# Comprehensive Project Demo Guide

This guide provides detailed step-by-step instructions to set up and run the project from scratch, suitable for anyone who has just downloaded this directory.

## 0. Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **Python**: Version 3.7 or higher.
    *   You can check by opening a terminal and typing `python --version` or `python3 --version`.
    *   If not installed, download it from [python.org](https://www.python.org/downloads/).
2.  **pip**: Python's package installer. It usually comes with Python.
    *   You can check by typing `pip --version` or `pip3 --version`.
3.  **Git**: For cloning the repository (if you haven't already).
    *   Download from [git-scm.com](https://git-scm.com/downloads).
4.  **Terminal/Command Prompt**: You will need a terminal (like Command Prompt on Windows, Terminal on macOS/Linux) to execute commands.

## 1. Clone the Repository & Navigate to Project Directory

If you haven't already, clone the project repository to your local machine and navigate into the project's root directory.

```bash
git clone <your-repository-url>  # Replace <your-repository-url> with the actual URL
cd <your-repository-name>      # Replace <your-repository-name> with the directory name
```
All subsequent commands assume you are starting from the project's root directory (`GroMo-AI-microlearning-coach`).

## 2. Create and Configure the Environment File (`.env`)

This project uses an `.env` file in the **project root directory** to manage configuration settings.

a.  **Create the file**: In the project's root directory (e.g., `GroMo-AI-microlearning-coach/`), create a file named `.env`.

b.  **Populate the `.env` file**: Add the following content. These values are based on defaults in `config/config.py`. Uncomment and modify lines as needed (e.g., for `DATABASE_URL`, `MODEL_PATH`, `SECRET_KEY`).

    ```env
    # Project Root .env file

    # Backend Configuration
    FLASK_APP=backend/app.py
    FLASK_ENV=development  # Set to 'production' for deployment
    BACKEND_PORT=5000
    # DATABASE_URL=sqlite:///backend/database.db # Example: Uncomment and set your database URL if used
    # MODEL_PATH=models/your_model.joblib      # Example: Uncomment and set your ML model path if used

    # Frontend Configuration
    STREAMLIT_SERVER_PORT=8501
    # BACKEND_API_BASE_URL=http://localhost:5000 # This is usually derived from BACKEND_PORT by config.py
                                               # Only set this if you need to override the default.

    # Other shared configurations
    # SECRET_KEY=your_very_strong_unique_secret_key # Example: Uncomment and set a strong secret key if your app needs it
    ```
    Your `config/config.py` will load these variables.

## 3. Set Up and Run the Backend Server

The backend provides the API for the frontend. **You'll need one terminal window for the backend.**

a.  **Navigate to the backend directory:**
    From the project root:
    ```bash
    cd backend
    ```

b.  **(Highly Recommended) Create and activate a Python virtual environment:** This isolates dependencies for this part of the project.
    ```bash
    python -m venv venv  # Create a virtual environment named 'venv'
    ```
    Activate it:
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    Your terminal prompt should change to indicate the virtual environment is active (e.g., `(venv) ...`).

c.  **Install backend dependencies:**
    While in the `backend` directory with the virtual environment active:
    ```bash
    pip install -r requirements.txt
    ```

d.  **Run the Backend Flask Server:**
    Still in the `backend` directory with the virtual environment active:
    ```bash
    python app.py
    ```
    You should see output indicating the Flask server is running, including lines like:
    ```
     * Running on http://127.0.0.1:5000
     * Running on http://<your_local_ip_address>:5000 
    ```
    (The port number will match `BACKEND_PORT` from your `.env` file).
    **Keep this terminal window open and the backend server running.**

## 4. Set Up and Run the Frontend Application

The frontend is a Streamlit dashboard. **Open a NEW terminal window/tab for the frontend.** This is separate from the backend terminal.

a.  **Navigate to the frontend directory:**
    From the project root (ensure you are in the project root, not still in `backend`):
    ```bash
    cd frontend
    ```

b.  **(Highly Recommended) Create and activate a Python virtual environment (separate from the backend's):**
    ```bash
    python -m venv venv  # Create a virtual environment named 'venv'
    ```
    Activate it:
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    Your terminal prompt should change.

c.  **Install frontend dependencies:**
    While in the `frontend` directory with its virtual environment active:
    ```bash
    pip install -r requirements.txt
    ```

d.  **Run the Frontend Streamlit Application:**
    Still in the `frontend` directory with its virtual environment active:
    ```bash
    streamlit run dashboard.py
    ```
    Streamlit will typically provide output like:
    ```
    You can now view your Streamlit app in your browser.

    Local URL: http://localhost:8501
    Network URL: http://<your_local_ip_address>:8501
    ```
    (The port number will match `STREAMLIT_SERVER_PORT` from your `.env` file).
    It should automatically open the application in your default web browser. If not, manually open one of the URLs provided.

## 5. Using the Application

1.  Ensure the **Backend Server** (from Step 3) is running in its terminal.
2.  Ensure the **Frontend Application** (from Step 4) is running in its terminal and open in your browser.
3.  Interact with the Streamlit dashboard in your browser. Enter a GP ID, select a product, and click "Get Recommendation". The frontend will communicate with the backend to fetch and display the results.

## Troubleshooting Tips

*   **`command not found` (e.g., `python`, `pip`, `streamlit`):**
    *   Ensure Python (and pip) are installed and their installation directories are added to your system's PATH environment variable.
    *   If virtual environments are active, these commands should point to the venv's versions.
    *   `streamlit` is installed via `pip install -r requirements.txt` in the frontend's venv.
*   **Port Conflicts**: If an application fails to start because a port is "already in use":
    *   Stop the other process using that port.
    *   Or, change the port in your `.env` file (`BACKEND_PORT` or `STREAMLIT_SERVER_PORT`) and restart the respective server. Remember to update the `BACKEND_API_BASE_URL` in `.env` or ensure `config.py` correctly picks up the new backend port if you change `BACKEND_PORT`.
*   **Dependency Issues**: If `pip install` fails, check error messages. You might be missing system-level libraries or have network issues. Ensure your virtual environment is active.
*   **Frontend Can't Connect to Backend (`Connection Error`)**:
    *   Verify the backend server is running (check its terminal).
    *   Verify the `BACKEND_API_BASE_URL` (derived or set in `.env`, and used in `frontend/dashboard.py` via `app_config`) correctly points to where your backend is running (host and port).
    *   Check for firewall issues that might be blocking the connection.
    *   Look for CORS (Cross-Origin Resource Sharing) errors in the browser's developer console (F12). If the frontend and backend run on different ports (they do by default: 8501 and 5000), the Flask backend (`backend/app.py`) might need the `Flask-CORS` extension if you encounter CORS issues, although `requests` from Streamlit to Flask usually don't have preflight issues that browsers enforce strictly.
*   **`.env` file not found warning**: Ensure the `.env` file is in the **project root directory** and is named exactly `.env`.

This more detailed guide should help anyone get your project up and running smoothly. Good luck with your demo! 