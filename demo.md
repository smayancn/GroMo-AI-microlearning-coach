# Project Demo Guide

This guide provides step-by-step instructions to set up and run the project for a demonstration.

## Prerequisites

1.  **Python Installed**: Ensure you have Python 3.7+ installed on your system.
2.  **Git Installed**: For cloning the repository (if you haven't already).
3.  **Terminal/Command Prompt**: You will need a terminal to execute commands.
4.  **(Optional but Recommended) Virtual Environments**: To keep dependencies isolated, it's highly recommended to use virtual environments (e.g., `venv` or `conda`).

## Setup Instructions

### 1. Clone the Repository (if you haven't already)

```bash
git clone <your-repository-url>
cd <your-repository-name>
```

### 2. Set Up the Backend

The backend provides the core logic and API.

a.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

b.  **(Recommended) Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

c.  **Install backend dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install Flask, pandas, scikit-learn, and other necessary libraries.

d.  **(Optional) Configure Environment Variables:**
    If your backend requires a `.env` file for configuration (e.g., API keys, database URLs), create a `.env` file in the `backend` directory and populate it with the necessary variables. The `python-dotenv` library will automatically load it. Example:
    ```env
    # backend/.env
    FLASK_ENV=development
    DEBUG=True
    # Add other necessary variables
    ```

e.  **Run the Backend Server:**
    Open `backend/app.py` and check how it's started. Typically, for a Flask app, you would run:
    ```bash
    python app.py
    ```
    Alternatively, you might use:
    ```bash
    flask run
    ```
    (You might need to set `FLASK_APP=app.py` as an environment variable if you use `flask run` and it's not automatically detected: `export FLASK_APP=app.py` or `set FLASK_APP=app.py` on Windows).

    The backend server will likely start on `http://127.0.0.1:5000` (or another port if specified in `app.py`). Note the port it's running on.

### 3. Set Up the Frontend

The frontend provides the user interface (dashboard).

a.  **Open a new terminal window/tab.** It's important to keep the backend server running in its own terminal.

b.  **Navigate to the project's root directory** (if you are in the `backend` directory, go one level up `cd ..`), then navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```

c.  **(Recommended) Create and activate a virtual environment (separate from the backend's):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

d.  **Install frontend dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install Streamlit, requests, and other necessary libraries.

e.  **(Optional) Configure Environment Variables:**
    If your frontend requires a `.env` file for configuration (e.g., the URL of the backend API if it's not hardcoded), create a `.env` file in the `frontend` directory.
    Example:
    ```env
    # frontend/.env
    BACKEND_API_URL=http://127.0.0.1:5000/api 
    # (Adjust if your backend runs on a different port or has a different API prefix)
    ```
    Your `dashboard.py` would need to be written to load this using `python-dotenv` and use it when making requests.

f.  **Run the Frontend Application:**
    ```bash
    streamlit run dashboard.py
    ```
    Streamlit will typically open the application automatically in your web browser. If not, it will provide a URL (usually `http://localhost:8501`).

## Running the Demo

1.  **Start the Backend**: Ensure your backend server (from `backend/app.py`) is running. Check its terminal output for any errors and to confirm the URL it's serving on (e.g., `http://127.0.0.1:5000`).
2.  **Start the Frontend**: Ensure your Streamlit frontend (`frontend/dashboard.py`) is running. It should open in your browser or provide a URL (e.g., `http://localhost:8501`).
3.  **Interact with the Frontend**: Open the Streamlit URL in your browser. Perform the actions you want to showcase in your demo. The frontend will make requests to the backend API.

## Demo Flow Suggestions

*   **Introduction**: Briefly introduce the project and its purpose.
*   **Backend Check**: (Optional, for technical demos) Briefly show the backend terminal running and indicate it's ready.
*   **Frontend Walkthrough**:
    *   Open the Streamlit app in the browser.
    *   Showcase the main features of the dashboard.
    *   If there's data input, demonstrate that.
    *   Show any outputs, visualizations, or recommendations generated.
    *   Explain what's happening in the background (how the frontend interacts with the backend ML model/recommender).
*   **Conclusion**: Summarize the key features shown.

## Troubleshooting Tips

*   **Port Conflicts**: If an application fails to start due to a port already being in use, you may need to stop the other process using that port or configure your application to use a different port.
    *   In `backend/app.py` (Flask), you can specify a port: `app.run(port=5001)`
    *   For `streamlit run`, you can use: `streamlit run dashboard.py --server.port 8502`
*   **Dependency Issues**: If `pip install` fails, ensure your Python/pip setup is correct and that the `requirements.txt` files are accurate. Check for error messages indicating missing system libraries.
*   **API Connection Issues**: If the frontend cannot connect to the backend:
    *   Verify the backend is running and accessible.
    *   Check the URL the frontend is trying to reach (it might be hardcoded in `dashboard.py` or configured via an environment variable).
    *   Look for CORS errors in the browser's developer console (if the frontend and backend are on different ports, CORS headers might be needed on the Flask backend).
*   **Environment Variables**: Ensure `.env` files are correctly placed and loaded if your application relies on them.

Good luck with your demo recording! 