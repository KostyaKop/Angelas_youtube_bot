"""YouTube URL processing handler."""

import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from src.services.youtube import YouTubeService
from src.services.ai_analyzer import AIAnalyzer
from src.services.context_store import ContextStore
from src.services.sheets_logger import SheetsLogger
from src.services.database import DatabaseService
from src.utils.validators import is_youtube_url, extract_video_id
from src.utils.chunker import split_message
from src.utils.locales import get_message

router = Router()
logger = logging.getLogger(__name__)




from src.config import Config

@router.message(F.text.func(is_youtube_url))
async def handle_youtube_url(
    message: Message,
    youtube_service: YouTubeService,
    ai_analyzer: AIAnalyzer,
    context_store: ContextStore,
    sheets_logger: SheetsLogger,
    db: DatabaseService,
    config: Config,
) -> None:
    """Process YouTube URL and generate analysis."""
    
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    url = message.text.strip()
    
    # Get user language
    lang = await context_store.get_language(user_id)
    
    # Ensure user exists in database
    user = await db.get_or_create_user(
        user_id,
        message.from_user.username,
        message.from_user.first_name
    )
    
    # Check if user is blocked
    if user.is_blocked:
        await message.answer(get_message("error_blocked", lang))
        return
    
    # Check credits
    has_credits, remaining = await db.check_credits(user_id)
    if not has_credits:
        await message.answer(get_message("error_no_credits", lang))
        return
    
    try:
        # Extract video ID
        video_id = extract_video_id(url)
        if not video_id:
            logger.warning(f"Failed to extract video ID from: {url}")
            await message.answer(get_message("invalid_url", lang))
            if config.admin_user_id:
                try:
                    await message.bot.send_message(
                        config.admin_user_id, 
                        f"⚠️ <b>Невдала спроба (URL)</b>\n👤 {username}\n🔗 {url}\n❌ Невірне посилання"
                    )
                except Exception:
                    pass
            return
        
        # Send processing indicator
        processing_msg = await message.answer(get_message("processing", lang))
        
        # Get video info
        video_info = await youtube_service.get_video_info(video_id)
        title = video_info.get("title", "Untitled Video") if video_info else "Untitled Video"
        
        await processing_msg.edit_text(get_message("processing_with_title", lang, title=title))
        
        # Get transcript
        transcript = await youtube_service.get_transcript(video_id)
        if not transcript:
            await processing_msg.edit_text(get_message("no_subtitles", lang))
            if config.admin_user_id:
                try:
                    await message.bot.send_message(
                        config.admin_user_id, 
                        f"⚠️ <b>Невдала спроба (Субтитри)</b>\n👤 {username}\n📺 {title}\n🔗 {url}\n❌ Немає субтитрів"
                    )
                except Exception:
                    pass
            return
        
        # Format transcript with timestamps
        formatted_transcript = youtube_service.format_transcript_with_timestamps(transcript)
        
        # Analyze with AI
        summary = await ai_analyzer.analyze_video(title, formatted_transcript, lang=lang)
        if not summary:
            await processing_msg.edit_text(get_message("ai_error", lang))
            return
        
        # Use credit and log to database
        await db.use_credit(user_id, video_id, title, url)
        
        # Delete processing message
        try:
            await processing_msg.delete()
        except Exception:
            pass
        
        # Send summary (split if too long)
        header = f"<b>📺 {title}</b>\n\n"
        full_response = header + summary + get_message("footer_summary", lang)
        
        chunks = split_message(full_response)
        
        # Add "Shorter" button on the last chunk
        shorter_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_message("btn_shorter", lang), callback_data=f"shorter_{video_id}")]
        ])
        
        for i, chunk in enumerate(chunks):
            if i == len(chunks) - 1:  # Last chunk
                await message.answer(chunk, reply_markup=shorter_keyboard)
            else:
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
        
        # Log to Google Sheets (still used for admin logging)
        summary_preview = summary[:200] + "..." if len(summary) > 200 else summary
        await sheets_logger.log_request(
            user_id=user_id,
            username=username,
            video_url=url,
            video_title=title,
            summary_preview=summary_preview
        )
        
        logger.info(f"Processed video {video_id} for user {user_id}")
        
        # Admin Notification (Success)
        if config.admin_user_id:
            try:
                credits_info = f"💰 Залишилось: {remaining - 1}" if remaining > 0 else "⭐ Premium"
                msg = f"✅ <b>Нове відео оброблено</b>\n\n👤 Користувач: {username} (`{user_id}`)\n📺 Відео: {title}\n🔗 {url}\n{credits_info}"
                await message.bot.send_message(config.admin_user_id, msg)
            except Exception as e:
                logger.error(f"Failed to send admin notification: {e}")

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        try:
            await processing_msg.edit_text(get_message("ai_error", lang))
        except Exception:
            await message.answer(get_message("ai_error", lang))
        
        # Admin Notification (Error)
        if config.admin_user_id:
            try:
                msg = f"❌ <b>Помилка обробки</b>\n\n👤 Користувач: {username} (`{user_id}`)\n🔗 {url}\n\n⚠️ Помилка: {str(e)}"
                await message.bot.send_message(config.admin_user_id, msg)
            except Exception:
                pass


@router.callback_query(F.data.startswith("shorter_"))
async def handle_shorter(
    callback: CallbackQuery,
    context_store: ContextStore,
    ai_analyzer: AIAnalyzer,
) -> None:
    """Generate a shorter version of the video analysis."""
    user_id = callback.from_user.id
    video_id = callback.data.split("_", 1)[1]
    
    lang = await context_store.get_language(user_id)
    
    # Get context from Redis
    context = await context_store.get(user_id)
    if not context or context.get("video_id") != video_id:
        await callback.answer(get_message("error_context_expired", lang))
        return
    
    await callback.answer(get_message("shorter_processing", lang))
    
    # Generate shorter version
    shorter = await ai_analyzer.make_shorter(context, lang)
    
    if shorter:
        result = get_message("shorter_result", lang, content=shorter)
        await callback.message.answer(result)
    else:
        await callback.answer(get_message("error_shorter_failed", lang))
