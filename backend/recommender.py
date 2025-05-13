import random
import pandas as pd # Added for reading GP performance data
from pathlib import Path # Added for path handling
from typing import Dict, List, TypedDict, Optional, Any # Optional, Any added

# Add project root to sys.path to allow imports
import sys
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from config.config import app_config
# Conditional import for ml_model, handling case where it might not be fully ready
try:
    from backend.ml_model import load_model_artifacts, predict_weakness, DEFAULT_MODEL_PATH
    ML_MODEL_LOADED = True
except ImportError as e:
    print(f"Warning: Could not import ml_model components: {e}. Recommender will use fallback logic.")
    ML_MODEL_LOADED = False
    DEFAULT_MODEL_PATH = None # Define for type safety if import fails
    def load_model_artifacts(model_load_path: Any) -> Any: return None # Dummy function
    def predict_weakness(model_artifacts: Any, product_type: Any, attempts: Any, successes: Any) -> Any: return None # Dummy function

class Recommendation(TypedDict):
    video: str
    tip: str
    next_step: str

# Hardcoded data for MVP - will be replaced by ML model and database later
# Keys should ideally match the possible outputs of the ML model (weak_topic)
DUMMY_CONTENT_DATA: Dict[str, List[Dict[str, str]]] = {
    # Assuming these keys match potential 'last_weak_topic' values from gps_performance.csv
    "loan_closing_technique": [
        {
            "video": "https://www.youtube.com/watch?v=loan_closing_video",
            "tip": "Master the art of closing loan deals with these proven techniques.",
            "next_step": "Practice these closing questions with a colleague.",
        }
    ],
    "insurance_objection_handling": [
        {
            "video": "https://www.youtube.com/watch?v=insurance_objection_video",
            "tip": "Learn to effectively handle common objections when selling insurance.",
            "next_step": "Role-play an objection scenario for an insurance product.",
        }
    ],
    "credit_card_benefits_explaining": [
        {
            "video": "https://www.youtube.com/watch?v=cc_benefits_video",
            "tip": "Clearly articulate the unique benefits of our credit card offers.",
            "next_step": "List 3 key benefits for each credit card you offer.",
        }
    ],
    "loan_application_process": [
        {
            "video": "https://www.youtube.com/watch?v=loan_application_video",
            "tip": "Guide clients smoothly through the loan application process.",
            "next_step": "Create a checklist for the loan application steps.",
        }
    ],
    "insurance_policy_comparison": [
        {
            "video": "https://www.youtube.com/watch?v=insurance_compare_video",
            "tip": "Help clients compare insurance policies to find the best fit.",
            "next_step": "Compare two similar insurance policies and highlight differences.",
        }
    ],
    "insurance_product_knowledge": [
         {
            "video": "https://www.youtube.com/watch?v=insurance_knowledge_video",
            "tip": "Deepen your understanding of our insurance product details.",
            "next_step": "Study the product brochure for a new insurance policy.",
        }
    ],
    "credit_card_sales_pitch": [
        {
            "video": "https://www.youtube.com/watch?v=cc_pitch_video",
            "tip": "Craft a compelling sales pitch for credit cards.",
            "next_step": "Record yourself delivering a credit card sales pitch.",
        }
    ],
    "loan_eligibility_criteria": [
        {
            "video": "https://www.youtube.com/watch?v=loan_eligibility_video",
            "tip": "Understand and explain loan eligibility criteria accurately.",
            "next_step": "Review the eligibility criteria for three different loan products.",
        }
    ],
    "insurance_claim_process": [
        {
            "video": "https://www.youtube.com/watch?v=insurance_claim_video",
            "tip": "Assist clients efficiently through the insurance claim process.",
            "next_step": "Outline the steps for a typical insurance claim.",
        }
    ],
    "loan_negotiation_skills": [
        {
            "video": "https://www.youtube.com/watch?v=loan_negotiation_video",
            "tip": "Improve your negotiation skills for loan terms and conditions.",
            "next_step": "Identify three negotiation points for a loan scenario.",
        }
    ],
    "default": [
        {
            "video": "https://www.youtube.com/watch?v=dummy_generic_video",
            "tip": "Always listen to your customer's needs first.",
            "next_step": "Practice active listening in your next conversation.",
        }
    ]
}

# Load GP performance data (simulating a database for now)
GP_PERFORMANCE_DATA_PATH = project_root / "data" / "gps_performance.csv"
gp_performance_df: Optional[pd.DataFrame] = None
try:
    gp_performance_df = pd.read_csv(GP_PERFORMANCE_DATA_PATH)
except FileNotFoundError:
    print(f"Warning: GP performance data file not found at {GP_PERFORMANCE_DATA_PATH}. ML-based recommendations will be limited.")
except Exception as e:
    print(f"Warning: Error loading GP performance data: {e}. ML-based recommendations will be limited.")

# Load ML model artifacts
loaded_ml_model_artifacts: Optional[Dict[str, Any]] = None
if ML_MODEL_LOADED:
    model_path_from_config = app_config.MODEL_PATH
    actual_model_path = Path(model_path_from_config) if model_path_from_config else DEFAULT_MODEL_PATH
    if actual_model_path:
        print(f"Recommender attempting to load model from: {actual_model_path}")
        loaded_ml_model_artifacts = load_model_artifacts(actual_model_path)
        if not loaded_ml_model_artifacts:
            print(f"Warning: Recommender failed to load ML model from {actual_model_path}. Using fallback logic.")
    else:
        print("Warning: MODEL_PATH not configured and no default path for ML model. Recommender will use fallback logic.")

def get_gp_performance(gp_id: str, product_type: str) -> Optional[pd.Series]:
    """Fetches the latest performance data for a GP and product type from the CSV."""
    if gp_performance_df is None:
        return None
    # Normalize product_type for comparison, assuming CSV also has lowercase or consistent case
    # For simplicity, this finds the first match. In a real DB, you'd get the most recent or aggregate.
    # This also assumes gp_id and product_type uniquely identify a row or we take the first.
    # A more robust solution would handle multiple entries, perhaps by taking the latest or averaging.
    filtered_data = gp_performance_df[
        (gp_performance_df['gp_id'] == gp_id) &
        (gp_performance_df['product_type'].str.lower() == product_type.lower())
    ]
    if not filtered_data.empty:
        return filtered_data.iloc[-1] # Get the last entry for this GP and product
    return None

def recommend_content(gp_id: str, product_type: str) -> Recommendation:
    """
    Recommends microlearning content. 
    Uses ML model to predict weakness if available, otherwise falls back to product type.
    """
    predicted_topic: Optional[str] = None
    
    if loaded_ml_model_artifacts and gp_performance_df is not None:
        gp_data = get_gp_performance(gp_id, product_type)
        if gp_data is not None and "attempts" in gp_data and "successes" in gp_data:
            try:
                attempts = int(gp_data["attempts"])
                successes = int(gp_data["successes"])
                # The product_type for prediction should match what the model was trained on (e.g. lowercase)
                predicted_topic = predict_weakness(
                    loaded_ml_model_artifacts, 
                    product_type.lower(), # Ensure consistent casing with training data
                    attempts, 
                    successes
                )
                if predicted_topic:
                    print(f"ML predicted weak topic for {gp_id} ({product_type}): {predicted_topic}")
                else:
                    print(f"ML prediction returned None for {gp_id} ({product_type}). Using fallback.")
            except ValueError:
                print(f"Warning: Could not convert attempts/successes to int for {gp_id}. Using fallback.")
            except Exception as e:
                print(f"Warning: Error during ML prediction for {gp_id}: {e}. Using fallback.")
        else:
            print(f"No performance data found for {gp_id} ({product_type}) or missing attempts/successes. Using fallback.")
    else:
        if not ML_MODEL_LOADED:
            print("ML model components not available.")
        if gp_performance_df is None:
            print("GP performance data not loaded.")
        if not loaded_ml_model_artifacts:
             print("ML model artifacts not loaded.")
        print("Using fallback logic for recommendation.")

    # Determine which content list to use
    content_source_key = product_type.lower() # Default to product type if no/failed prediction
    if predicted_topic and predicted_topic in DUMMY_CONTENT_DATA:
        content_source_key = predicted_topic
        print(f"Using ML predicted topic '{predicted_topic}' for content.")
    elif predicted_topic:
        print(f"Predicted topic '{predicted_topic}' not in DUMMY_CONTENT_DATA. Falling back to product type '{product_type.lower()}'.")
    else:
        print(f"No ML prediction. Using product type '{product_type.lower()}' for content.")
        
    content_list = DUMMY_CONTENT_DATA.get(content_source_key, DUMMY_CONTENT_DATA["default"])
    
    selected_content = random.choice(content_list)

    return {
        "video": selected_content["video"],
        "tip": selected_content["tip"],
        "next_step": selected_content["next_step"],
    }

if __name__ == "__main__":
    print("Testing recommender with potential ML integration:")
    # Ensure you have run ml_model.py to generate the model file first.
    # Also, ensure .env is set up if MODEL_PATH is defined there.

    # Test case 1: GP001, loan (should have data in gps_performance.csv)
    print("\n--- Test Case 1: GP001, loan ---")
    gp1_loan_rec = recommend_content("GP001", "loan")
    print(f"Recommendation for GP001 (Loan): {gp1_loan_rec}")

    # Test case 2: GP004, insurance (should have data)
    print("\n--- Test Case 2: GP004, insurance ---")
    gp2_insurance_rec = recommend_content("GP004", "insurance")
    print(f"Recommendation for GP004 (Insurance): {gp2_insurance_rec}")

    # Test case 3: GP_Unknown, loan (no specific performance data, should use fallback)
    print("\n--- Test Case 3: GP_Unknown, loan ---")
    gp_unknown_loan_rec = recommend_content("GP_Unknown", "loan")
    print(f"Recommendation for GP_Unknown (Loan): {gp_unknown_loan_rec}")
    
    # Test case 4: GP001, unknown_product (should use default content)
    print("\n--- Test Case 4: GP001, unknown_product ---")
    gp1_unknown_prod_rec = recommend_content("GP001", "unknown_product")
    print(f"Recommendation for GP001 (Unknown Product): {gp1_unknown_prod_rec}") 