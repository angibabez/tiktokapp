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
    # Simple HTML wrap
    return render_template_string("<html><body><pre>{{ content }}</pre></body></html>", content=content)

@app.route('/terms')
def terms():
    content = read_md_file("terms_of_service.md")
    return render_template_string("<html><body><pre>{{ content }}</pre></body></html>", content=content)

# Placeholder for TikTok domain verification file if needed later
# @app.route('/tiktokxxxxx.html')
# def verify():
#     return "verification_code"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
