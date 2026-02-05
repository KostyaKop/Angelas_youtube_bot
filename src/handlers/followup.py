"""Followup question handler for contextual Q&A."""

import logging

from aiogram import Router
from aiogram.types import Message

from src.services.ai_analyzer import AIAnalyzer
from src.services.context_store import ContextStore
from src.utils.validators import is_youtube_url
from src.utils.chunker import split_message

router = Router()
logger = logging.getLogger(__name__)

ERROR_NO_CONTEXT = """
🤔 <b>У вас поки немає активного відео для обговорення.</b>

👇 Спочатку надішліть посилання на YouTube
""".strip()

ERROR_ANSWER_FAILED = """
🚫 <b>Не вдалося відповісти на питання.</b>

Спробуйте ще раз або надішліть нове відео.
""".strip()


@router.message()
async def handle_followup(
    message: Message,
    ai_analyzer: AIAnalyzer,
    context_store: ContextStore,
) -> None:
    """Handle followup questions using stored context."""
    
    # Skip if it's a YouTube URL (handled by youtube.py)
    if message.text and is_youtube_url(message.text):
        return
    
    # Skip commands
    if message.text and message.text.startswith("/"):
        return
    
    user_id = message.from_user.id
    question = message.text or ""
    
    if not question.strip():
        return
    
    # Get context from Redis
    context = await context_store.get(user_id)
    if not context:
        await message.answer(ERROR_NO_CONTEXT)
        return
    
    # Send typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Get AI answer with context
        answer = await ai_analyzer.answer_followup(context, question)
        if not answer:
            await message.answer(ERROR_ANSWER_FAILED)
            return
        
        # Format response
        full_response = answer + "\n\n💬 <i>Можете задати ще питання або надіслати нове посилання</i>"
        
        # Send answer (split if too long)
        chunks = split_message(full_response)
        for chunk in chunks:
            await message.answer(chunk)
        
        logger.info(f"Answered followup question for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error answering followup: {e}")
        await message.answer(ERROR_ANSWER_FAILED)
