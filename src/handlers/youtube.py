"""YouTube URL processing handler."""

import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message

from src.services.youtube import YouTubeService
from src.services.ai_analyzer import AIAnalyzer
from src.services.context_store import ContextStore
from src.services.sheets_logger import SheetsLogger
from src.utils.validators import is_youtube_url, extract_video_id
from src.utils.chunker import split_message

router = Router()
logger = logging.getLogger(__name__)

ERROR_NO_SUBTITLES = """
⚠️ <b>Не вдалося отримати субтитри.</b>

Можливі причини:
• Субтитри вимкнені автором
• Відео занадто нове
• Технічні обмеження

Спробуйте інше відео з доступними субтитрами.
""".strip()

ERROR_AI_FAILED = """
🚫 <b>Технічна помилка</b>

Не вдалося обробити відео. Можливо:
• Відео занадто довге
• Збій AI-моделі

Спробуйте повторити запит через хвилину.
""".strip()

ERROR_INVALID_URL = """
❌ <b>Невалідне посилання</b>

Надішліть посилання на YouTube відео у форматі:
• youtube.com/watch?v=...
• youtu.be/...
""".strip()


@router.message(F.text.func(is_youtube_url))
async def handle_youtube_url(
    message: Message,
    youtube_service: YouTubeService,
    ai_analyzer: AIAnalyzer,
    context_store: ContextStore,
    sheets_logger: SheetsLogger,
) -> None:
    """Process YouTube URL and generate analysis."""
    
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    url = message.text.strip()
    
    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        await message.answer(ERROR_INVALID_URL)
        return
    
    # Send processing indicator
    processing_msg = await message.answer("🔄 <b>Аналізую відео...</b>")
    
    try:
        # Get video info
        video_info = await youtube_service.get_video_info(video_id)
        title = video_info.get("title", "Untitled Video") if video_info else "Untitled Video"
        
        await processing_msg.edit_text(f"🔄 <b>Аналізую відео...</b>\n📺 {title}")
        
        # Get transcript
        transcript = await youtube_service.get_transcript(video_id)
        if not transcript:
            await processing_msg.edit_text(ERROR_NO_SUBTITLES)
            return
        
        # Format transcript with timestamps
        formatted_transcript = youtube_service.format_transcript_with_timestamps(transcript)
        
        # Analyze with AI
        summary = await ai_analyzer.analyze_video(title, formatted_transcript)
        if not summary:
            await processing_msg.edit_text(ERROR_AI_FAILED)
            return
        
        # Delete processing message
        await processing_msg.delete()
        
        # Send summary (split if too long)
        header = f"<b>📺 {title}</b>\n\n"
        full_response = header + summary + "\n\n💬 <i>Задайте питання по відео або надішліть нове посилання</i>"
        
        chunks = split_message(full_response)
        for chunk in chunks:
            await message.answer(chunk)
        
        # Save context to Redis
        await context_store.save(user_id, {
            "video_url": url,
            "video_id": video_id,
            "video_title": title,
            "transcript": formatted_transcript,
            "summary": summary,
            "created_at": datetime.utcnow().isoformat(),
        })
        
        # Log to Google Sheets
        summary_preview = summary[:200] + "..." if len(summary) > 200 else summary
        await sheets_logger.log_request(
            user_id=user_id,
            username=username,
            video_url=url,
            video_title=title,
            summary_preview=summary_preview
        )
        
        logger.info(f"Processed video {video_id} for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        await processing_msg.edit_text(ERROR_AI_FAILED)
