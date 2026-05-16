import os
import json
import time
import pickle
import requests
import subprocess
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from google.cloud import storage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

STATE_FILE = "posted_videos.json"
SETTINGS_FILE = "settings.json"
BUCKET_NAME = "socialrepost"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"posted_videos": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {
        "pipelines": {"youtube_to_instagram": True, "youtube_to_tiktok": True},
        "filters": {"include_hashtags": [], "exclude_hashtags": []},
        "hashtag_mappings": []
    }

def get_youtube_service():
    if not os.path.exists("token.pickle"):
        print("YouTube token.pickle not found. Please run auth_youtube.py first.")
        return None
        
    with open("token.pickle", "rb") as token:
        credentials = pickle.load(token)
        
    return build("youtube", "v3", credentials=credentials)

def get_latest_youtube_video(youtube):
    """Fetches the latest video from the authenticated user's channel."""
    print("Fetching latest YouTube video...")
    try:
        # Get the uploads playlist ID
        channels_response = youtube.channels().list(mine=True, part="contentDetails").execute()
        uploads_playlist_id = channels_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Get the latest video in the uploads playlist
        playlist_items_response = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part="snippet",
            maxResults=1
        ).execute()
        
        if not playlist_items_response["items"]:
            print("No videos found in channel.")
            return None
            
        item = playlist_items_response["items"][0]
        video_id = item["snippet"]["resourceId"]["videoId"]
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        
        # Get the high resolution thumbnail
        thumbnails = item["snippet"]["thumbnails"]
        thumb_url = thumbnails.get("maxres", thumbnails.get("high", {})).get("url")
        
        return {
            "id": video_id,
            "title": title,
            "description": description,
            "thumbnail_url": thumb_url,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        }
    except Exception as e:
        print(f"Failed to fetch YouTube video: {e}")
        return None

def download_youtube_video(video_url, dest_path):
    """Downloads a YouTube video using yt-dlp."""
    print(f"Downloading YouTube video from {video_url}...")
    try:
        # Call yt-dlp via subprocess
        subprocess.run([
            "yt-dlp", 
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", 
            "-o", dest_path, 
            video_url
        ], check=True)
        print("Download complete.")
        return True
    except Exception as e:
        print(f"Failed to download video: {e}")
        return False

def upload_to_gcs(local_path, filename):
    """Uploads a file to GCS and returns a signed URL."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_filename(local_path)
    
    url = blob.generate_signed_url(version="v4", expiration=3600, method="GET")
    return url

def post_to_instagram_reels(video_url, cover_url, caption):
    """Posts a video to Instagram Reels."""
    print("Posting to Instagram Reels...")
    # Implementation remains the same as before (omitted for brevity but assumed present)
    # ...
    return True

def upload_to_tiktok_via_browser(video_path, cover_path, caption):
    """Automates the upload to TikTok web interface."""
    print("Uploading to TikTok via browser automation...")
    # This will require Playwright to log in or use saved cookies
    # And fill the upload form
    print("Placeholder: TikTok web upload automation.")
    return True

def main():
    state = load_state()
    settings = load_settings()
    
    youtube = get_youtube_service()
    if not youtube:
        return
        
    video_data = get_latest_youtube_video(youtube)
    if not video_data:
        return
        
    video_id = video_data["id"]
    if video_id in state["posted_videos"]:
        print("Latest video has already been processed.")
        return
        
    print(f"New video detected: {video_data['title']} ({video_id})")
    
    # Download video and thumbnail
    video_path = f"{video_id}.mp4"
    thumb_path = f"{video_id}.jpg"
    
    if not download_youtube_video(video_data["url"], video_path):
        return
        
    if video_data["thumbnail_url"]:
        download_file(video_data["thumbnail_url"], thumb_path) # Reuse download_file helper
        
    # Apply filters based on hashtags in title/description
    # ... (similar to previous filter logic)
    
    # Upload to Instagram
    if settings["pipelines"].get("youtube_to_instagram", True):
        gcs_url = upload_to_gcs(video_path, f"{video_id}.mp4")
        post_to_instagram_reels(gcs_url, video_data["thumbnail_url"], video_data["title"])
        
    # Upload to TikTok
    if settings["pipelines"].get("youtube_to_tiktok", True):
        upload_to_tiktok_via_browser(video_path, thumb_path, video_data["title"])
        
    # Update state
    state["posted_videos"].append(video_id)
    save_state(state)
    
    # Cleanup local files
    if os.path.exists(video_path):
        os.remove(video_path)
    if os.path.exists(thumb_path):
        os.remove(thumb_path)
        
    print("Done.")

if __name__ == "__main__":
    main()
