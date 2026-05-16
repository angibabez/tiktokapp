import os
from flask import Flask, render_template_string

app = Flask(__name__)

def read_md_file(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return f.read()
    return "File not found."

@app.route('/')
def home():
    return "<h1>Social Reposter Backend</h1><p>This app hosts the legal documents for TikTok approval.</p>"

@app.route('/privacy')
def privacy():
    content = read_md_file("privacy_policy.md")
    return render_template_string("<html><body><pre>{{ content }}</pre></body></html>", content=content)

@app.route('/terms')
def terms():
    content = read_md_file("terms_of_service.md")
    return render_template_string("<html><body><pre>{{ content }}</pre></body></html>", content=content)

# TikTok Verification
@app.route('/tiktokuTRNwzZNzLrb05vvrnCfhNYJB5M28tsp.txt')
def verify():
    return "tiktok-developers-site-verification=uTRNwzZNzLrb05vvrnCfhNYJB5M28tsp"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
