import os
from dotenv import load_dotenv
from pathlib import Path

# Determine the project root directory, assuming this file is in config/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env file from the project root
DOTENV_PATH = PROJECT_ROOT / '.env'
if DOTENV_PATH.exists():
    load_dotenv(DOTENV_PATH)
else:
    print(f"Warning: .env file not found at {DOTENV_PATH}. Using default or system environment variables.")

class AppConfig:
    """Application configuration class to load and store settings."""

    # Backend Configuration
    FLASK_APP: str = os.getenv("FLASK_APP", "backend/app.py")
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", 5000))
    DATABASE_URL: str | None = os.getenv("DATABASE_URL") # e.g., "sqlite:///backend/database.db"
    MODEL_PATH: str | None = os.getenv("MODEL_PATH") # e.g., "models/your_model.joblib"

    # Frontend Configuration
    STREAMLIT_SERVER_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", 8501))
    # If frontend needs to call backend, it should use this base URL
    # This is especially important if they run on different hosts/ports or in containers
    BACKEND_API_BASE_URL: str = os.getenv("BACKEND_API_BASE_URL", f"http://localhost:{BACKEND_PORT}")

    # Other shared configurations
    SECRET_KEY: str | None = os.getenv("SECRET_KEY")

    # Derived backend recommend URL
    @property
    def BACKEND_RECOMMEND_URL(self) -> str:
        return f"{self.BACKEND_API_BASE_URL}/recommend"

# Instantiate the config object for easy import elsewhere
app_config = AppConfig()

if __name__ == "__main__":
    # Example of how to access the config values
    print(f"Flask App: {app_config.FLASK_APP}")
    print(f"Flask Env: {app_config.FLASK_ENV}")
    print(f"Backend Port: {app_config.BACKEND_PORT}")
    print(f"Database URL: {app_config.DATABASE_URL}")
    print(f"Model Path: {app_config.MODEL_PATH}")
    print(f"Streamlit Port: {app_config.STREAMLIT_SERVER_PORT}")
    print(f"Backend API Base URL: {app_config.BACKEND_API_BASE_URL}")
    print(f"Backend Recommend URL: {app_config.BACKEND_RECOMMEND_URL}")
    print(f"Secret Key: {app_config.SECRET_KEY}") 