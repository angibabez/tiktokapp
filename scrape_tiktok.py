import sys
import os
from playwright.sync_api import sync_playwright

def scrape_latest_video(username):
    url = f"https://www.tiktok.com/@{username}"
    print(f"Navigating to {url}...")
    
    with sync_playwright() as p:
        # Use a Mobile User Agent
        user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="networkidle") 
            
            print("Waiting for videos to load...")
            # On mobile, the selector might be different. Let's wait for any link with /video/
            page.wait_for_selector('a[href*="/video/"]', timeout=15000)
            
            latest_video_link = page.query_selector('a[href*="/video/"]')
            video_url = latest_video_link.get_attribute("href")
            print(f"Found Video URL: {video_url}")
            
            img = latest_video_link.query_selector('img')
            cover_url = img.get_attribute("src") if img else None
            print(f"Found Cover URL: {cover_url}")
            
            return video_url, cover_url
            
        except Exception as e:
            print(f"Error during scrape: {e}")
            page.screenshot(path="tiktok_error.png")
            print("Saved debug screenshot to tiktok_error.png")
            raise e
        finally:
            browser.close()

def main():
    username = "appsandfrappes"
    try:
        video_url, cover_url = scrape_latest_video(username)
        print(f"\nResult:\nVideo: {video_url}\nCover: {cover_url}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    main()
