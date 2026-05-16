import sys
import os
from dotenv import load_dotenv
import google_auth_oauthlib.flow
import pickle

# Redirect stdout and stderr to a file in the workspace
sys.stdout = open('auth_output.log', 'w', buffering=1)
sys.stderr = sys.stdout

load_dotenv()

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    print("Starting auth script...")
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
        client_config, SCOPES
    )
    
    # Use a fixed port so we can whitelist it in GCP
    print("Please visit the URL printed below to authorize the application.")
    credentials = flow.run_local_server(port=8080, open_browser=False)
    
    # Save the credentials for the next run
    with open("token.pickle", "wb") as token:
        pickle.dump(credentials, token)
    
    print("Authorization successful! Saved token.pickle")

if __name__ == "__main__":
    main()
