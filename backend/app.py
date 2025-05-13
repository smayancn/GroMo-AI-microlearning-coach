from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
from typing import Dict, Any

# Assuming recommender.py and config.py are structured to be importable
# Adjust import path if your project structure is different or use PYTHONPATH
import sys
from pathlib import Path
# Add project root to sys.path to allow imports from config and backend
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.recommender import recommend_content, Recommendation
from config.config import app_config # Import app_config

app = Flask(__name__)

@app.route("/recommend", methods=["POST"])
def handle_recommend_request() -> Any:
    """
    Handles POST requests to /recommend endpoint.
    Expects a JSON body with "gp_id" and "product_type".
    Returns a JSON response with video, tip, and next_step.
    """
    try:
        data: Dict[str, str] = request.get_json()
        if not data:
            raise BadRequest("Request body must be JSON.")

        gp_id: str = data.get("gp_id")
        product_type: str = data.get("product_type")

        if not gp_id or not product_type:
            raise BadRequest("Missing 'gp_id' or 'product_type' in request body.")

        recommendation_data: Recommendation = recommend_content(gp_id, product_type)
        return jsonify(recommendation_data), 200 # Renamed variable to avoid conflict

    except BadRequest as e:
        app.logger.warning(f"Bad request to /recommend: {e.description} - Data: {request.data}")
        return jsonify({"error": str(e.description)}), 400
    except Exception as e:
        app.logger.error(f"Error in /recommend: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred."}), 500

if __name__ == "__main__":
    # Use port from app_config
    app.run(debug=(app_config.FLASK_ENV == 'development'), port=app_config.BACKEND_PORT, host='0.0.0.0') 