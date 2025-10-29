import logging
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Initialize logger
logger = logging.getLogger("debug_script")
logger.setLevel(logging.DEBUG)

# Create a file handler for logging
file_handler = logging.FileHandler("debug_script.log")
file_handler.setLevel(logging.DEBUG)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Print to terminal as well
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Test Supabase connection
def test_supabase_connection():
    try:
        logger.info("Testing Supabase connection...")
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase URL or Key is not set in environment variables.")

        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Test query
        response = supabase.table("audio_transcriptions").select("*").limit(1).execute()
        logger.info("Supabase connection successful. Response: %s", response.data)
    except Exception as e:
        logger.error("Supabase connection failed. Error: %s", str(e))

import random

# ... existing code ...

# Test API endpoint
def test_api_endpoint():
    try:
        logger.info("Testing /api/auth/register endpoint...")
        url = "http://localhost:8000/api/auth/register"
        
        # Generate a random user for each test run
        random_int = random.randint(1000, 9999)
        email = f"testuser{random_int}@testdomain.com"
        username = f"testuser{random_int}"

        payload = {
            "email": email,
            "password": "securepassword",
            "username": username
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        logger.info("API Response Status: %s", response.status_code)
        logger.info("API Response Body: %s", response.text)

        if response.status_code != 200:
            logger.error("API test failed with status code %s", response.status_code)
    except Exception as e:
        logger.error("API test failed. Error: %s", str(e))

if __name__ == "__main__":
    logger.info("Starting debug script...")
    test_supabase_connection()
    test_api_endpoint()
    logger.info("Debug script completed.")