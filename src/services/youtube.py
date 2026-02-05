"""YouTube transcript and metadata extraction service."""

import logging
import asyncio
import re
from concurrent.futures import ThreadPoolExecutor

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

logger = logging.getLogger(__name__)

# Thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=3)


class YouTubeService:
    """Service for extracting YouTube video transcripts and metadata."""
    
    # Supported languages in order of preference
    LANGUAGES = ["uk", "ru", "en", "auto"]
    
    async def get_transcript(self, video_id: str) -> list[dict] | None:
        """
        Get transcript with timestamps for a YouTube video.
        
        Returns list of segments: [{'text': '...', 'start': 12.5, 'duration': 3.2}]
        Returns None if no transcript available.
        """
        try:
            loop = asyncio.get_event_loop()
            transcript = await loop.run_in_executor(
                executor,
                self._fetch_transcript,
                video_id
            )
            return transcript
        except Exception as e:
            logger.error(f"Failed to get transcript for {video_id}: {e}")
            return None
    
    def _fetch_transcript(self, video_id: str) -> list[dict] | None:
        """Sync method to fetch transcript (runs in thread pool)."""
        try:
            # Try to get transcript in preferred languages
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=self.LANGUAGES
            )
            return transcript
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.warning(f"No transcript available for {video_id}: {e}")
            return None
        except Exception as e:
            # Try to get any available transcript
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript = transcript_list.find_generated_transcript(["en", "uk", "ru"])
                return transcript.fetch()
            except Exception:
                logger.error(f"Failed to fetch any transcript for {video_id}: {e}")
                return None
    
    async def get_video_info(self, video_id: str) -> dict | None:
        """
        Get basic video info (title, duration).
        
        Note: Uses oEmbed API which doesn't require API key.
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
        """
        Format transcript with timestamps for AI analysis.
        
        Input: [{'text': '...', 'start': 12.5, 'duration': 3.2}]
        Output: "[00:12] Text here\n[00:15] Next segment..."
        """
        lines = []
        
        for segment in transcript:
            start = segment.get("start", 0)
            text = segment.get("text", "").strip()
            
            if not text:
                continue
            
            timestamp = self._format_timestamp(start)
            lines.append(f"[{timestamp}] {text}")
        
        return "\n".join(lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as MM:SS or HH:MM:SS."""
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
