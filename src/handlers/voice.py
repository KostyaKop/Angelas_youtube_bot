"""Voice message handler using OpenAI Whisper for transcription."""

import logging
import os
import tempfile

from aiogram import Router, F, Bot
from aiogram.types import Message

from src.services.context_store import ContextStore
from src.services.ai_analyzer import AIAnalyzer
from src.services.database import DatabaseService
from src.utils.locales import get_message
from src.utils.chunker import split_message

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.voice)
async def handle_voice_message(
    message: Message,
    bot: Bot,
    context_store: ContextStore,
    ai_analyzer: AIAnalyzer,
    db: DatabaseService,
) -> None:
    """
    Handle voice messages by transcribing with Whisper and processing as followup question.
    """
    user_id = message.from_user.id
    lang = await context_store.get_language(user_id)
    
    # Ensure user exists
    user = await db.get_or_create_user(
        user_id,
        message.from_user.username,
        message.from_user.first_name
    )
    
    # Check if user is blocked
    if user.is_blocked:
        await message.answer("🚫 <b>Доступ заблоковано</b>")
        return
    
    # Get context - voice messages are only for followup questions
    context = await context_store.get(user_id)
    if not context:
        await message.answer(get_message("no_context", lang))
        return
    
    # Download voice file
    processing_msg = await message.answer("🎤 Обробляю голосове повідомлення...")
    
    try:
        # Get file from Telegram
        file = await bot.get_file(message.voice.file_id)
        
        # Create temp file for audio
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Download file
        await bot.download_file(file.file_path, temp_path)
        
        # Transcribe with Whisper
        transcribed_text = await ai_analyzer.transcribe_audio(temp_path)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        if not transcribed_text:
            await processing_msg.edit_text("❌ Не вдалося розпізнати голосове повідомлення")
            return
        
        # Show what was transcribed
        await processing_msg.edit_text(f"🎤 <i>Питання:</i> {transcribed_text}\n\n⏳ Аналізую...")
        
        # Process as followup question
        answer = await ai_analyzer.answer_followup(context, transcribed_text, lang=lang)
        
        if answer:
            # Delete processing message
            try:
                await processing_msg.delete()
            except Exception:
                pass
            
            # Send response
            full_response = answer + get_message("footer_answer", lang)
            chunks = split_message(full_response)
            
            for chunk in chunks:
                await message.answer(chunk)
            
            logger.info(f"Answered voice followup for user {user_id}")
        else:
            await processing_msg.edit_text(get_message("answer_failed", lang))
    
    except Exception as e:
        logger.error(f"Voice message error: {e}")
        try:
            await processing_msg.edit_text("❌ Помилка обробки голосового повідомлення")
        except Exception:
            await message.answer("❌ Помилка обробки голосового повідомлення")
