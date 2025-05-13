# GroMo AI Microlearning Coach

## Overview

The GroMo AI Microlearning Coach is a system designed to provide personalized, bite-sized training content to GroMo Partners (GPs). It aims to help GPs improve their sales performance for financial products like loans, insurance, and credit cards by:
1.  Identifying a GP's weak skill area using a machine learning model based on their past performance.
2.  Recommending targeted microlearning materials (videos, tips, next steps).

This project is currently in its initial development phase, with a functional prototype that includes an ML-driven recommendation engine.
🎥 [Click here to watch the demo video](https://github.com/smayancn/GroMo-AI-microlearning-coach/blob/main/demo.mp4)

## Current Features

*   **ML-Powered Weakness Detection**: 
    *   A scikit-learn (RandomForestClassifier) model is trained on dummy GP performance data (`data/gps_performance.csv`) to predict a `last_weak_topic`.
    *   The model considers `product_type`, `attempts`, and `successes` as features.
    *   The training script (`backend/ml_model.py`) can be run to generate/update the model file (`models/weakness_classifier.joblib`).
*   **Recommendation Engine**: 
    *   Given a `gp_id` and `product_type`, the system attempts to fetch the GP's performance data.
    *   It uses the loaded ML model to predict the GP's weak topic for that product type.
    *   Based on the predicted topic (or `product_type` as a fallback), it recommends:
        *   A short video URL.
        *   A concise sales tip.
        *   A next-step action prompt.
    *   Content is currently sourced from a hardcoded dictionary in `backend/recommender.py`, keyed by weak topics.
*   **Backend API**: A Flask-based REST API endpoint (`POST /recommend`) that accepts a `gp_id` and `product_type` in JSON, returning the personalized recommendation.
*   **Frontend Dashboard (MVP)**: A Streamlit web application where GPs can:
    *   Enter their GP ID.
    *   Select a product type they need help with.
    *   Receive and view the recommended video, tip, and next step, now potentially influenced by the ML model.
*   **Configuration Management**: Settings (ports, API URLs, model path) are managed via a `.env` file and a central `config/config.py` module.

## Project Structure

```
.
├── backend/
│   ├── app.py                 # Flask API entry point
│   ├── ml_model.py            # ML model training, loading, prediction logic
│   ├── recommender.py         # Recommendation logic (integrates ML model)
│   └── requirements.txt       # Backend Python dependencies
├── config/
│   └── config.py              # Environment variable parsing and config management
├── data/
│   └── gps_performance.csv    # Dummy GP sales log data for training
├── frontend/
│   ├── dashboard.py           # Streamlit MVP interface
│   └── requirements.txt       # Frontend Python dependencies
├── models/
│   ├── .gitkeep               # Placeholder for trained model files
│   └── weakness_classifier.joblib # Trained ML model (after running ml_model.py)
├── .env.example             # Example environment variable structure
└── README.md                # This file
```

## Setup and Running the Application (Detailed)

### Prerequisites

*   Python 3.9+
*   pip (Python package installer)
*   Git (for cloning, if applicable)

### 1. Clone the Repository (if you haven't already)

```bash
# If you have the project files, skip this step
git clone <repository_url>
cd <repository_name>
```

### 2. Create and Configure Environment Variables (`.env` file)

*   In the project root directory, copy the `.env.example` file to a new file named `.env`:
    ```bash
    cp .env.example .env
    ```
*   **Open the `.env` file and review/edit the variables:**
    *   `FLASK_APP`: Should be `backend/app.py` (usually no change needed).
    *   `FLASK_ENV`: Set to `development` for debug features, or `production`.
    *   `BACKEND_PORT`: Port for the Flask backend (default: `5000`).
    *   `MODEL_PATH`: **Important for the ML model.**
        *   If you want to use the default path and filename (`models/weakness_classifier.joblib`), you can leave this line commented out or remove it from `.env`.
        *   If you want to specify a different path or filename for your model, uncomment this line and set the path (e.g., `MODEL_PATH=models/my_custom_model.joblib`). The path should be relative to the project root or an absolute path.
    *   `STREAMLIT_SERVER_PORT`: Port for the Streamlit frontend (default: `8501`).
    *   `BACKEND_API_BASE_URL`: Base URL for the backend, used by the frontend. If backend and frontend run on the same machine with default ports, `http://localhost:5000` (or `http://127.0.0.1:5000`) is typical.

### 3. Install Dependencies

*   Ensure your terminal is in the **project root directory**.
*   **Backend Dependencies**:
    ```bash
    pip install -r backend/requirements.txt
    ```
*   **Frontend Dependencies**:
    ```bash
    pip install -r frontend/requirements.txt
    ```

### 4. Train the ML Model (Important First Step for ML Features)

*   The system uses an ML model to predict GP weaknesses. You need to train this model at least once.
*   Ensure your terminal is in the **project root directory**.
*   Run the ML model training script:
    ```bash
    python backend/ml_model.py
    ```
*   **Expected Output**:
    *   You'll see messages about loading data, training progress.
    *   A line saying `Model trained and saved to <...>/models/weakness_classifier.joblib` (or your custom path if set in `.env`).
    *   A classification report (its quality will depend on the dummy data).
    *   Some sample predictions.
*   **Verification**: After running, check that the `models/weakness_classifier.joblib` file has been created (or your custom model file).
*   **Note**: The current dummy data is very small. Stratification during training is disabled to prevent errors with this small dataset. For a real system, a larger and more representative dataset would be crucial, and stratification should be enabled.

### 5. Run the Backend Server (Flask API)

*   Ensure your terminal is in the **project root directory**.
*   Start the Flask backend server:
    ```bash
    python backend/app.py
    ```
*   **Expected Output**:
    *   Messages indicating the Flask server is running, typically something like:
        `* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)` or `* Running on all addresses. Use http://<your_local_ip>:5000/`
    *   You should also see output from the `recommender.py` module indicating whether it successfully loaded the ML model (e.g., `Recommender attempting to load model from: ...` followed by success or failure messages).
*   Keep this terminal window open. This is your backend server.

### 6. Run the Frontend Application (Streamlit Dashboard)

*   Open a **new terminal window** (leave the backend server running in its own terminal).
*   Ensure this new terminal is also in the **project root directory**.
*   Start the Streamlit frontend application:
    ```bash
    streamlit run frontend/dashboard.py
    ```
*   **Expected Output**:
    *   Streamlit will typically provide URLs, such as:
        `You can now view your Streamlit app in your browser.`
        `  Local URL: http://localhost:8501`
        `  Network URL: http://<your_local_ip>:8501`
    *   Your default web browser should automatically open to the local URL.

## How to Use and Test the Application

### A. Using the Streamlit Frontend Dashboard

1.  **Open the Dashboard**: If it didn't open automatically, navigate to `http://localhost:8501` (or the port you configured) in your web browser.
2.  **Enter GP ID**: In the "Enter your GroMo Partner ID" field, type a GP ID. 
    *   To test ML-driven recommendations, use IDs present in `data/gps_performance.csv` (e.g., `GP001`, `GP002`, ..., `GP030`).
    *   To test fallback (non-ML), use an ID not in the CSV (e.g., `GP_Unknown`).
3.  **Select Product Type**: Choose a product from the dropdown (e.g., "Loan", "Insurance", "Credit Card").
4.  **Get Recommendation**: Click the "💡 Get Recommendation" button.
5.  **View Results**: The dashboard will display:
    *   An embedded video (if a YouTube URL is provided).
    *   A sales tip.
    *   A next-step prompt.
6.  **Check Backend Logs**: Look at the terminal window where `python backend/app.py` is running. You should see log messages for each request to `/recommend`. These logs will indicate:
    *   If the ML model was used (`ML predicted weak topic for ...`).
    *   What the predicted topic was.
    *   If it fell back to product-type based recommendations and why (e.g., GP data not found, ML model not loaded, prediction failed).

### B. Testing the Backend API Directly (e.g., using curl)

You can also test the `/recommend` endpoint directly. This is useful for debugging or integration testing.

1.  Ensure the backend Flask server (`python backend/app.py`) is running.
2.  Open a new terminal (different from the backend server and Streamlit frontend terminals).
3.  Use a command-line tool like `curl` (available on Linux, macOS, and Windows PowerShell/WSL) or a GUI tool like Postman.

    **Example using `curl`:**

    *   **Test with a GP known in `gps_performance.csv` (e.g., GP001, loan):**
        ```bash
        curl -X POST -H "Content-Type: application/json" -d "{\"gp_id\": \"GP001\", \"product_type\": \"loan\"}" http://localhost:5000/recommend
        ```
        *(For Windows CMD, you might need to escape the double quotes differently or use a file for the JSON payload.)*

    *   **Test with a GP not in `gps_performance.csv` (e.g., GP_NonExistent, insurance):**
        ```bash
        curl -X POST -H "Content-Type: application/json" -d "{\"gp_id\": \"GP_NonExistent\", \"product_type\": \"insurance\"}" http://localhost:5000/recommend
        ```

4.  **Examine the Output**: `curl` will print the JSON response from the API directly to your terminal. It should look like:
    ```json
    {
      "video": "some_url",
      "tip": "some_tip",
      "next_step": "some_next_step"
    }
    ```
5.  **Again, check the backend server logs** to see how the recommendation was derived (ML prediction or fallback).

---

This README will be further updated as more features like Dockerization and formal testing are implemented. 
