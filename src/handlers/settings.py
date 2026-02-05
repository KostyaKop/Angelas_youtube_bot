"""Settings handler for language selection and user stats."""

import logging
from io import BytesIO

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile

from src.services.context_store import ContextStore
from src.services.database import DatabaseService
from src.utils.locales import get_message

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("settings"))
async def show_settings(message: Message, context_store: ContextStore, db: DatabaseService) -> None:
    """Show settings menu."""
    user_id = message.from_user.id
    lang = await context_store.get_language(user_id)
    
    # Ensure user exists in database
    await db.get_or_create_user(
        user_id, 
        message.from_user.username, 
        message.from_user.first_name
    )
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_message("language_btn_uk", lang), callback_data="set_lang_uk"),
            InlineKeyboardButton(text=get_message("language_btn_en", lang), callback_data="set_lang_en"),
            InlineKeyboardButton(text=get_message("language_btn_ru", lang), callback_data="set_lang_ru"),
            InlineKeyboardButton(text=get_message("language_btn_es", lang), callback_data="set_lang_es"),
        ],
        [
            InlineKeyboardButton(text=get_message("btn_my_stats", lang), callback_data="my_stats"),
            InlineKeyboardButton(text=get_message("btn_export", lang), callback_data="export_history"),
        ]
    ])
    
    await message.answer(
        text=get_message("settings_title", lang),
        reply_markup=markup
    )


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: CallbackQuery, context_store: ContextStore, db: DatabaseService) -> None:
    """Handle language selection."""
    lang_code = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    
    # Save preference to both Redis and database
    await context_store.set_language(user_id, lang_code)
    await db.set_language(user_id, lang_code)
    
    # Confirm change in new language
    await callback.message.edit_text(
        text=get_message("language_selected", lang_code)
    )
    await callback.answer()


@router.callback_query(F.data == "my_stats")
async def show_my_stats(callback: CallbackQuery, db: DatabaseService, context_store: ContextStore) -> None:
    """Show user's own statistics."""
    user_id = callback.from_user.id
    lang = await context_store.get_language(user_id)
    
    stats = await db.get_user_stats(user_id)
    
    if not stats:
        await callback.answer("Статистика недоступна")
        return
    
    premium = "⭐ Преміум" if stats["is_premium"] else ""
    credits = "∞" if stats["is_premium"] else stats["credits"]
    
    text = f"""
<b>📊 Ваша статистика</b> {premium}

💰 Залишилось кредитів: <b>{credits}</b>
📹 Відео оброблено: <b>{stats['total_videos']}</b>
📅 Зареєстровано: {stats['created_at'][:10] if stats['created_at'] else '—'}
""".strip()
    
    await callback.message.edit_text(text)
    await callback.answer()


@router.callback_query(F.data == "export_history")
async def export_history(callback: CallbackQuery, db: DatabaseService) -> None:
    """Export user's history as CSV."""
    user_id = callback.from_user.id
    
    csv_content = await db.export_history_csv(user_id)
    
    if not csv_content:
        await callback.answer("Історія порожня")
        return
    
    # Send as file
    file = BufferedInputFile(
        csv_content.encode('utf-8'),
        filename=f"history_{user_id}.csv"
    )
    
    await callback.message.answer_document(
        file,
        caption="📥 Ваша історія відео"
    )
    await callback.answer("Файл відправлено!")


@router.message(Command("mystats"))
async def cmd_mystats(message: Message, db: DatabaseService, context_store: ContextStore) -> None:
    """Show user's statistics via command."""
    user_id = message.from_user.id
    
    # Ensure user exists
    await db.get_or_create_user(
        user_id,
        message.from_user.username,
        message.from_user.first_name
    )
    
    stats = await db.get_user_stats(user_id)
    
    if not stats:
        await message.answer("Статистика недоступна")
        return
    
    premium = "⭐ Преміум" if stats["is_premium"] else ""
    credits = "∞" if stats["is_premium"] else stats["credits"]
    
    text = f"""
<b>📊 Ваша статистика</b> {premium}

💰 Залишилось кредитів: <b>{credits}</b>
📹 Відео оброблено: <b>{stats['total_videos']}</b>
📅 Зареєстровано: {stats['created_at'][:10] if stats['created_at'] else '—'}
""".strip()
    
    await message.answer(text)

