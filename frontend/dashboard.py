import streamlit as st
import requests
from typing import Dict, Any

# Adjust import path for config
import sys
from pathlib import Path
# Add project root to sys.path to allow imports from config
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from config.config import app_config # Import app_config

# Use the derived URL from app_config
BACKEND_API_URL = app_config.BACKEND_RECOMMEND_URL

def get_recommendation(gp_id: str, product_type: str) -> Dict[str, Any] | None:
    """Fetches recommendation from the backend API."""
    payload = {"gp_id": gp_id, "product_type": product_type}
    try:
        response = requests.post(BACKEND_API_URL, json=payload)
        response.raise_for_status()  # Raises an exception for HTTP errors
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Connection Error: Could not connect to the backend at {BACKEND_API_URL}. Please ensure the backend server is running.")
        return None
    except requests.exceptions.Timeout:
        st.error(f"Timeout: The request to {BACKEND_API_URL} timed out.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e.response.status_code} - {e.response.reason}. Check backend logs for details.")
        # Attempt to parse error message from backend if available
        try:
            error_details = e.response.json()
            if "error" in error_details:
                st.error(f"Backend message: {error_details['error']}")
        except ValueError:
            pass # No JSON error body from backend
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the backend: {e}")
        return None
    except Exception as e: # Catch any other unexpected errors
        st.error(f"An unexpected error occurred while fetching recommendation: {e}")
        return None

st.set_page_config(layout="wide", page_title="GroMo AI Microlearning Coach")

st.title("🚀 GroMo AI Microlearning Coach")
st.markdown("Get personalized tips and video recommendations to boost your sales!")

# --- Input Section ---
st.header("Get Personalized Help")

PRODUCT_TYPES = ["Loan", "Insurance", "Credit Card"] # Can be dynamic later

col1, col2 = st.columns(2)

with col1:
    gp_id_input = st.text_input("Enter your GroMo Partner ID (e.g., GP001):", key="gp_id_input_key") # Changed key

with col2:
    product_type_input = st.selectbox(
        "Select a product you'd like help with:",
        PRODUCT_TYPES,
        key="product_type_input_key" # Changed key
    )

if st.button("💡 Get Recommendation", key="get_recommendation_button_key", use_container_width=True): # Changed key
    if not gp_id_input:
        st.warning("Please enter your GP ID.")
    elif not product_type_input:
        st.warning("Please select a product type.")
    else:
        with st.spinner("Fetching your personalized recommendation..."):
            recommendation = get_recommendation(gp_id_input, product_type_input.lower())

        if recommendation:
            if recommendation.get("error"):
                # This specific check might be redundant if get_recommendation handles backend errors well
                st.error(f"Backend Error: {recommendation.get('error')}")
            else:
                st.success("Here is your personalized recommendation!")
                
                video_url = recommendation.get("video")
                tip = recommendation.get("tip")
                next_step = recommendation.get("next_step")

                if video_url:
                    st.subheader("🎬 Watch this short video:")
                    if "youtube.com" in video_url or "youtu.be" in video_url:
                        st.video(video_url)
                    else:
                        st.markdown(f"[Watch Video]({video_url})")
                else:
                    st.info("No video available for this recommendation.")

                if tip:
                    st.subheader("💡 Sales Tip:")
                    st.markdown(f"> {tip}")
                
                if next_step:
                    st.subheader("🎯 Next Step:")
                    st.markdown(f"**{next_step}**")
        # If recommendation is None, get_recommendation already showed an error

else:
    st.info("Enter your ID and select a product to get started.")

# --- Footer or additional sections (optional) ---
st.markdown("---_Developed for GroMo Partners_---")

# To run this Streamlit app:
# 1. Ensure you have an .env file in the project root (see .env.example)
# 2. Run the backend: python backend/app.py (or however you run your Flask app)
# 3. Run this frontend: streamlit run frontend/dashboard.py --server.port <YourStreamlitPortFromEnv> 