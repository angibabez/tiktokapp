import sys
import os
import urllib.parse
import json
import requests
import hashlib
import base64
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

# Redirect stdout and stderr to a file
sys.stdout = open('auth_tiktok_output.log', 'w', buffering=1)
sys.stderr = sys.stdout

load_dotenv()

CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080/"

def generate_pkce():
    code_verifier = secrets.token_urlsafe(32)
    m = hashlib.sha256()
    m.update(code_verifier.encode('utf-8'))
    code_challenge = base64.urlsafe_b64encode(m.digest()).decode('utf-8').replace('=', '')
    return code_verifier, code_challenge

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            code = params['code'][0]
            self.wfile.write(b"<h1>Success!</h1><p>You can close this window. The agent is processing the token.</p>")
            print(f"Received code: {code}")
            
            # Read verifier
            with open("pkce_verifier.txt", "r") as f:
                code_verifier = f.read()
            
            # Exchange code for token
            token_url = "https://open.tiktokapis.com/v2/oauth/token/"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "client_key": CLIENT_KEY,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
                "code_verifier": code_verifier
            }
            
            print("Exchanging code for token...")
            resp = requests.post(token_url, headers=headers, data=data)
            print(f"Token Response Status: {resp.status_code}")
            print(f"Token Response Body: {resp.text}")
            
            try:
                token_data = resp.json()
                if "access_token" in token_data:
                    with open("tiktok_token.json", "w") as f:
                        json.dump(token_data, f, indent=2)
                    print("Saved tiktok_token.json")
                else:
                    print("Failed to get access token from response.")
            except Exception as e:
                print(f"Error parsing token response: {e}")
                
        else:
            self.wfile.write(b"<h1>Error</h1><p>No code found in the URL.</p>")
            print("No code found in request.")
            
def main():
    print("Starting TikTok auth script...")
    
    code_verifier, code_challenge = generate_pkce()
    with open("pkce_verifier.txt", "w") as f:
        f.write(code_verifier)
        
    # Reduced scope to just basic info to test if it works without approval
    scope = "user.info.basic"
    state = "random_state_123"
    
    params = {
        "client_key": CLIENT_KEY,
        "scope": scope,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    
    auth_url = "https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode(params)
    
    print(f"Please visit this URL to authorize: {auth_url}", flush=True)
    
    server = HTTPServer(('localhost', 8080), OAuthHandler)
    print("Waiting for callback on http://localhost:8080/ ...", flush=True)
    server.handle_request()

if __name__ == "__main__":
    main()
