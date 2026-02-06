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




from src.utils.locales import get_message

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
    
    # Get user language
    lang = await context_store.get_language(user_id)
    
    # Get context from Redis
    context = await context_store.get(user_id)
    if not context:
        await message.answer(get_message("no_context", lang))
        return
    
    # Send typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Get AI answer with context
        answer = await ai_analyzer.answer_followup(context, question, lang=lang)
        if not answer:
            await message.answer(get_message("answer_failed", lang))
            return
        
        # Format response
        full_response = answer + get_message("footer_answer", lang)
        
        # Send answer (split if too long)
        chunks = split_message(full_response)
        for chunk in chunks:
            await message.answer(chunk)
        
        logger.info(f"Answered followup question for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error answering followup: {e}")
        await message.answer(get_message("answer_failed", lang))
