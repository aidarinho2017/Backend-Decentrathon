# diet/services.py
import requests
from django.conf import settings

def generate_diet_plan(user_data):
    # Define the endpoint and headers for the API request
    url = "https://your-ai-endpoint-url/v1/predict"  # Replace with actual URL
    headers = {
        "Authorization": f"Bearer {settings.API_KEY}",
        "Content-Type": "application/json"
    }

    # Prepare the input data for the AI model
    payload = {
        "height": user_data["height"],
        "weight": user_data["weight"],
        "sex": user_data["sex"],
        "diseases": user_data["diseases"],
        "preferences": user_data["preferences"]
    }

    # Send the request to the AI model endpoint
    response = requests.post(url, json=payload, headers=headers)

    # Handle the response and return the diet plan
    if response.status_code == 200:
        return response.json().get("diet_plan", "No plan available")
    else:
        raise Exception(f"Failed to generate diet plan: {response.text}")
