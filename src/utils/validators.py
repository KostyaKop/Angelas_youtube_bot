"""YouTube URL validation and parsing utilities."""

import re

# Regex patterns for YouTube URLs
YOUTUBE_PATTERNS = [
    # Standard watch URLs
    r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
    # Short URLs
    r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})",
    # Shorts URLs
    r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
    # Live URLs
    r"(?:https?://)?(?:www\.)?youtube\.com/live/([a-zA-Z0-9_-]{11})",
    # Embed URLs
    r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
    # Mobile URLs
    r"(?:https?://)?m\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
]

# Combined pattern for URL detection
URL_DETECT_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.|m\.)?(?:youtube\.com|youtu\.be)/?(?:watch|shorts|live|embed)?"
)


def is_youtube_url(text: str) -> bool:
    """
    Check if text contains a YouTube URL.
    
    Args:
        text: Input text to check
        
    Returns:
        True if text contains a YouTube URL
    """
    if not text:
        return False
    return bool(URL_DETECT_PATTERN.search(text))


def extract_video_id(url: str) -> str | None:
    """
    Extract video ID from YouTube URL.
    
    Supports:
    - youtube.com/watch?v=VIDEO_ID
    - youtu.be/VIDEO_ID
    - youtube.com/shorts/VIDEO_ID
    - youtube.com/embed/VIDEO_ID
    
    Args:
        url: YouTube URL
        
    Returns:
        11-character video ID or None if not found
    """
    if not url:
        return None
    
    url = url.strip()
    
    for pattern in YOUTUBE_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # Try to extract from query string (for edge cases)
    if "v=" in url:
        match = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url)
        if match:
            return match.group(1)
    
    return None


def clean_url(url: str) -> str:
    """
    Clean and normalize YouTube URL.
    
    Args:
        url: Raw URL
        
    Returns:
        Normalized URL
    """
    url = url.strip()
    
    # Add https if missing
    if not url.startswith("http"):
        url = "https://" + url
    
    return url
