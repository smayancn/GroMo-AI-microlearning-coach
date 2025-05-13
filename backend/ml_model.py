import pandas as pd
import joblib
from pathlib import Path
from typing import Dict, Any, List, Optional

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

# Add project root to sys.path to allow imports from config
import sys
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from config.config import app_config

# Define feature columns and target column
CATEGORICAL_FEATURES = ["product_type"]
NUMERICAL_FEATURES = ["attempts", "successes"]
TARGET_COLUMN = "last_weak_topic"

# Default path for the model, relative to project root
DEFAULT_MODEL_FILENAME = "weakness_classifier.joblib"
DEFAULT_MODEL_DIR = project_root / "models"
DEFAULT_MODEL_PATH = DEFAULT_MODEL_DIR / DEFAULT_MODEL_FILENAME

def create_pipeline(class_labels: Optional[List[str]] = None) -> Pipeline:
    """
    Creates a scikit-learn pipeline for preprocessing and classification.

    Args:
        class_labels (Optional[List[str]]): A list of unique class labels for the target variable.
                                            Required if the target encoder needs to be fitted.

    Returns:
        Pipeline: The scikit-learn pipeline.
    """
    numerical_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )

    # RandomForestClassifier chosen as per user initial prompt
    model_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(random_state=42, class_weight='balanced')),
        ]
    )
    return model_pipeline

def train_model(
    data_path: Path,
    model_save_path: Path = DEFAULT_MODEL_PATH,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Optional[Pipeline]:
    """
    Trains the weakness detection model and saves it.

    Args:
        data_path (Path): Path to the CSV file containing training data.
        model_save_path (Path): Path where the trained model should be saved.
        test_size (float): Proportion of the dataset to include in the test split.
        random_state (int): Random seed for reproducibility.

    Returns:
        Optional[Pipeline]: The trained pipeline if successful, else None.
    """
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: Training data file not found at {data_path}")
        return None
    except Exception as e:
        print(f"Error loading training data: {e}")
        return None

    if df.empty:
        print("Error: Training data is empty.")
        return None

    # Ensure all required columns are present
    required_cols = CATEGORICAL_FEATURES + NUMERICAL_FEATURES + [TARGET_COLUMN]
    if not all(col in df.columns for col in required_cols):
        print(f"Error: Missing one or more required columns in training data: {required_cols}")
        return None
    
    df = df.dropna(subset=required_cols) # Drop rows with NaNs in essential columns
    if len(df) < 10: # Arbitrary small number for meaningful training
        print(f"Error: Not enough valid data rows ({len(df)}) for training after NaN drop.")
        return None

    # Encode the target variable
    target_encoder = LabelEncoder()
    df[TARGET_COLUMN] = target_encoder.fit_transform(df[TARGET_COLUMN])
    class_labels = list(target_encoder.classes_) # Get original string labels

    X = df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
    y = df[TARGET_COLUMN]

    if X.empty or y.empty:
        print("Error: Features or target variable is empty after processing.")
        return None

    # ---- DEBUG: Print value counts of y before split ----
    print("Value counts of encoded target variable (y) before train_test_split:")
    print(pd.Series(y).value_counts())
    # ---- END DEBUG ----

    # Stratification is disabled (stratify=None) due to the very small size of the dummy dataset.
    # With few samples per class (e.g., 3), stratification can lead to splits where the training set
    # (or folds within cross-validation used by the classifier) has only 1 sample for some classes,
    # causing errors in scikit-learn components that require at least 2 samples per class.
    # For a production system with a larger, more representative dataset, stratification (stratify=y) is recommended.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=None
    )

    model_pipeline = create_pipeline(class_labels=class_labels)

    print(f"Training model with {len(X_train)} samples...")
    model_pipeline.fit(X_train, y_train)

    # Save the trained model and the target encoder's classes
    model_save_path.parent.mkdir(parents=True, exist_ok=True)
    
    model_artifacts = {
        'pipeline': model_pipeline,
        'target_encoder_classes': class_labels
    }
    joblib.dump(model_artifacts, model_save_path)
    print(f"Model trained and saved to {model_save_path}")

    # Evaluate model (optional, but good practice)
    y_pred_encoded = model_pipeline.predict(X_test)
    # To get string labels for classification report:
    # y_pred_labels = target_encoder.inverse_transform(y_pred_encoded)
    # y_test_labels = target_encoder.inverse_transform(y_test)
    # print("\nClassification Report on Test Set:")
    # print(classification_report(y_test_labels, y_pred_labels, zero_division=0))
    # For encoded labels:
    print("\nClassification Report on Test Set (Encoded Labels):")
    print(classification_report(y_test, y_pred_encoded, zero_division=0, labels=range(len(class_labels)), target_names=class_labels))


    return model_pipeline

def load_model_artifacts(model_load_path: Path = DEFAULT_MODEL_PATH) -> Optional[Dict[str, Any]]:
    """
    Loads the trained model pipeline and target encoder classes.

    Args:
        model_load_path (Path): Path from where to load the model artifacts.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing 'pipeline' and 'target_encoder_classes',
                                or None if loading fails.
    """
    if not model_load_path.exists():
        print(f"Error: Model file not found at {model_load_path}")
        return None
    try:
        model_artifacts = joblib.load(model_load_path)
        if 'pipeline' not in model_artifacts or 'target_encoder_classes' not in model_artifacts:
            print("Error: Model artifacts are corrupted or missing key components.")
            return None
        print(f"Model artifacts loaded successfully from {model_load_path}")
        return model_artifacts
    except Exception as e:
        print(f"Error loading model artifacts: {e}")
        return None

def predict_weakness(
    model_artifacts: Dict[str, Any],
    product_type: str,
    attempts: int,
    successes: int
) -> Optional[str]:
    """
    Predicts the weak skill area based on input features using the loaded model.

    Args:
        model_artifacts (Dict[str, Any]): Loaded model pipeline and target encoder classes.
        product_type (str): The product type.
        attempts (int): Number of attempts for this product type.
        successes (int): Number of successes for this product type.

    Returns:
        Optional[str]: The predicted weak topic (string label), or None if prediction fails.
    """
    try:
        pipeline = model_artifacts['pipeline']
        target_encoder_classes = model_artifacts['target_encoder_classes']
        
        # Create a DataFrame for the input features
        # Ensure the order of columns matches how the preprocessor was trained
        input_df = pd.DataFrame({
            "product_type": [product_type],
            "attempts": [attempts],
            "successes": [successes]
        })
        
        # Reorder columns to match training order if necessary
        # This is crucial if ColumnTransformer relies on specific column order for NUMERICAL_FEATURES and CATEGORICAL_FEATURES
        # However, ColumnTransformer uses column names, so order in input_df might not be an issue as long as names are correct.
        # For safety, one could enforce: input_df = input_df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
        # But this depends on the structure. Given the current create_pipeline, named selection should work.

        predicted_encoded_label = pipeline.predict(input_df)
        
        # Convert encoded label back to original string label
        if predicted_encoded_label is not None and len(predicted_encoded_label) > 0:
            # Ensure target_encoder_classes is a list or array for indexing
            if isinstance(target_encoder_classes, (list, pd.Series)):
                 predicted_weakness_str = target_encoder_classes[predicted_encoded_label[0]]
                 return predicted_weakness_str
            else:
                 print(f"Error: target_encoder_classes is not an indexable list or array. Type: {type(target_encoder_classes)}")
                 return None
        else:
            print("Error: Model prediction was empty or None.")
            return None
            
    except KeyError as e:
        print(f"Error during prediction: Missing feature in input data or model: {e}")
        return None
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None

if __name__ == "__main__":
    print("Attempting to train the ML model...")
    # Determine data path relative to this file or project root
    csv_data_path = project_root / "data" / "gps_performance.csv"
    
    # Use model path from config if available, else use default
    model_path_to_save = Path(app_config.MODEL_PATH) if app_config.MODEL_PATH else DEFAULT_MODEL_PATH
    
    if not csv_data_path.exists():
        print(f"CRITICAL: Training data CSV not found at {csv_data_path}. Please ensure it exists.")
    else:
        print(f"Using training data from: {csv_data_path}")
        print(f"Model will be saved to: {model_path_to_save}")
        
        trained_pipeline = train_model(data_path=csv_data_path, model_save_path=model_path_to_save)

        if trained_pipeline:
            print("\n--- Testing model loading and prediction --- ")
            loaded_artifacts = load_model_artifacts(model_load_path=model_path_to_save)
            if loaded_artifacts:
                # Example prediction (use actual data for meaningful test)
                sample_prediction = predict_weakness(
                    model_artifacts=loaded_artifacts,
                    product_type="loan", 
                    attempts=10, 
                    successes=2
                )
                print(f"Sample prediction for (loan, 10 attempts, 2 successes): {sample_prediction}")
                
                sample_prediction_2 = predict_weakness(
                    model_artifacts=loaded_artifacts,
                    product_type="insurance", 
                    attempts=15, 
                    successes=5
                )
                print(f"Sample prediction for (insurance, 15 attempts, 5 successes): {sample_prediction_2}")
            else:
                print("Could not test prediction as model loading failed.")
        else:
            print("Model training failed. Cannot test prediction.") 