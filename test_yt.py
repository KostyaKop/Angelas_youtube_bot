from youtube_transcript_api import YouTubeTranscriptApi
import sys

video_id = "dQw4w9WgXcQ"
try:
    print(f"Testing video: {video_id}")
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'uk', 'ru'])
    print("Success! Transcript found.")
    print(transcript[:2])
except Exception as e:
    import traceback
    print(f"Error type: {type(e)}")
    print(f"Error message: {e}")
    traceback.print_exc()
