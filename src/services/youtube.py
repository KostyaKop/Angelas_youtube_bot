"""YouTube transcript and metadata extraction service using Apify."""

import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from apify_client import ApifyClient

logger = logging.getLogger(__name__)

# Thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=3)


class YouTubeService:
    """Service for extracting YouTube video transcripts using Apify."""
    
    def __init__(self, api_key: str):
        """Initialize Apify client."""
        self.client = ApifyClient(api_key)
        # Using a reliable transcript scraper found in user history
        self.actor_id = "pintostudio/youtube-transcript-scraper"
    
    async def get_transcript(self, video_id: str) -> list[dict] | None:
        """
        Get transcript with timestamps for a YouTube video using Apify.
        
        Returns list of segments: [{'text': '...', 'start': 12.5}]
        """
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        try:
            loop = asyncio.get_event_loop()
            transcript = await loop.run_in_executor(
                executor,
                self._run_apify_actor,
                video_url
            )
            return transcript
        except Exception as e:
            logger.error(f"Apify failed to get transcript for {video_id}: {e}")
            return None
    
    def _run_apify_actor(self, video_url: str) -> list[dict] | None:
        """Sync method to run Apify actor."""
        try:
            # Prepare the Actor input for pintostudio/youtube-transcript-scraper
            run_input = {
                "videoUrl": video_url,
                "targetLanguage": "uk" # Primary language preference
            }

            # Run the Actor and wait for it to finish
            run = self.client.actor(self.actor_id).call(run_input=run_input)

            # Fetch and return Actor results from the run's default dataset
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                # For pintostudio/youtube-transcript-scraper, results are in 'data' field
                transcript_data = item.get("data", [])
                if transcript_data:
                    return transcript_data
            
            return None
        except Exception as e:
            logger.error(f"Apify Actor execution error: {e}")
            return None
    
    async def get_video_info(self, video_id: str) -> dict | None:
        """
        Get basic video info (title, author).
        Uses oEmbed API (no key required).
        """
        import aiohttp
        
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "title": data.get("title", ""),
                            "author": data.get("author_name", ""),
                        }
        except Exception as e:
            logger.error(f"Failed to get video info for {video_id}: {e}")
        
        return None
    
    def format_transcript_with_timestamps(self, transcript: list[dict]) -> str:
        """Format transcript for AI analysis."""
        lines = []
        for segment in transcript:
            # Apify segments usually have 'text' and 'start' (in seconds or as string)
            start = segment.get("start", 0)
            text = segment.get("text", "").strip()
            
            if not text:
                continue
            
            # Convert start to float if it's a string like "0:12"
            if isinstance(start, str):
                start = self._parse_time_str(start)
            
            timestamp = self._format_timestamp(start)
            lines.append(f"[{timestamp}] {text}")
        
        return "\n".join(lines)
    
    def _parse_time_str(self, time_str: str) -> float:
        """Parse MM:SS or HH:MM:SS to seconds."""
        parts = time_str.split(":")
        try:
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            return float(time_str)
        except ValueError:
            return 0.0

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as MM:SS or HH:MM:SS."""
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
