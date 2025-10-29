from dotenv import load_dotenv
import os
from termcolor import colored

# Load environment variables from .env file
load_dotenv()

# List of required environment variables
required_env_vars = [
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "HF_TOKEN",
    "GEMINI_API_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "GROQ_API_KEY",
    "ELEVEN_LABS_API",
    "LANGCHAIN_API_KEY",
    "TAVILY_API_KEY",
    "supabase_password",
    "ASSEMBLYAI_API_KEY",
    "JWT_SECRET",
    "JWT_ALGORITHM",
    "JWT_EXPIRATION_MINUTES",
    "MAX_UPLOAD_SIZE",
    "UPLOAD_DIR"
]

# Check and print all environment variables
print("\nChecking environment variables:\n")
all_vars_present = True
for var in required_env_vars:
    value = os.getenv(var)
    if value:
        print(colored(f"[✔] {var} is set.", "green"))
    else:
        print(colored(f"[✘] {var} is NOT set.", "red"))
        all_vars_present = False

if all_vars_present:
    print(colored("\nAll required environment variables are set!", "green"))
else:
    print(colored("\nSome required environment variables are missing. Please check your .env file.", "red"))