import os
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()

client = Client(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    print("Listing models...")
    # The method might be models.list or similar. inspecting client.models
    # Based on error message: "Call ListModels to see the list of available models"
    # Let's try client.models.list()
    for model in client.models.list():
        print(model.name)
except Exception as e:
    print(f"Error listing models: {e}")
    import traceback
    traceback.print_exc()
