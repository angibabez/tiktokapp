# Social Reposter Agent (YouTube First)

This agent automatically cross-posts your YouTube Shorts to Instagram Reels and TikTok, carrying over the custom thumbnail.

## How It Works

1. **Source**: The agent monitors your YouTube channel uploads via the YouTube Data API.
2. **Processing**: It detects new Shorts, downloads them using `yt-dlp`, and fetches the custom thumbnail.
3. **Instagram Reels**: 
   * It uploads the video to your Google Cloud Storage bucket (`socialrepost`) to create a signed URL.
   * It uses the Meta Graph API to post the Reel using that URL and the YouTube thumbnail as the cover.
4. **TikTok**:
   * Since the official API requires approval, it will use Playwright browser automation to upload the video to the TikTok web interface and set the custom cover image.

## Current Status

*   **YouTube**: Authenticated and ready.
*   **Instagram**: Authenticated and ready.
*   **GCS Storage**: Bucket `socialrepost` is ready.
*   **TikTok**: Script structure is ready, needs Playwright upload implementation.

## Configuration

Edit the `.env` file to update credentials.
Open `settings.html` in a browser to generate settings for `settings.json`.
