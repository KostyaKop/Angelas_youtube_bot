"""Command handlers for /start and /help."""

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from src.services.context_store import ContextStore
from src.services.database import DatabaseService
from src.utils.locales import get_message, detect_language

router = Router()


def get_main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Create main reply keyboard with localized buttons."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_message("kb_settings", lang)),
                KeyboardButton(text=get_message("kb_help", lang)),
                KeyboardButton(text=get_message("kb_stats", lang)),
            ]
        ],
        resize_keyboard=True,
        is_persistent=True
    )


@router.message(CommandStart())
async def cmd_start(message: Message, context_store: ContextStore, db: DatabaseService) -> None:
    """Handle /start command."""
    user_id = message.from_user.id
    
    # Check if user already has a language set
    existing_lang = await context_store.get_language(user_id)
    
    # For new users, auto-detect from Telegram settings
    if existing_lang == "uk":  # Default means might be new user
        user = await db.get_or_create_user(
            user_id,
            message.from_user.username,
            message.from_user.first_name
        )
        
        # If user is brand new (just created), detect language
        detected_lang = detect_language(message.from_user.language_code)
        if detected_lang != existing_lang:
            await context_store.set_language(user_id, detected_lang)
            await db.set_language(user_id, detected_lang)
            existing_lang = detected_lang
    else:
        # Ensure user exists in database
        await db.get_or_create_user(
            user_id,
            message.from_user.username,
            message.from_user.first_name
        )
    
    # Send welcome with persistent keyboard
    keyboard = get_main_keyboard(existing_lang)
    await message.answer(get_message("welcome", existing_lang), reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: Message, context_store: ContextStore) -> None:
    """Handle /help command."""
    user_id = message.from_user.id
    lang = await context_store.get_language(user_id)
    
    help_text = get_message("help_message", lang)
    await message.answer(help_text)


# Keyboard button text handlers (for persistent keyboard buttons)
# Note: These match the exact button text from locales

# Settings button - all language variants
SETTINGS_BUTTONS = ["⚙️ Налаштування", "⚙️ Settings", "⚙️ Настройки", "⚙️ Ajustes"]

@router.message(lambda msg: msg.text in SETTINGS_BUTTONS)
async def handle_settings_button(message: Message, context_store: ContextStore, db: DatabaseService) -> None:
    """Handle settings keyboard button press."""
    # Import here to avoid circular dependency
    from src.handlers.settings import show_settings
    # Forward to settings handler
    await show_settings(message, context_store, db)


# Help button - all language variants
HELP_BUTTONS = ["❓ Допомога", "❓ Help", "❓ Помощь", "❓ Ayuda"]

@router.message(lambda msg: msg.text in HELP_BUTTONS)
async def handle_help_button(message: Message, context_store: ContextStore) -> None:
    """Handle help keyboard button press."""
    user_id = message.from_user.id
    lang = await context_store.get_language(user_id)
    help_text = get_message("help_message", lang)
    await message.answer(help_text)


# Stats button - all language variants
STATS_BUTTONS = ["📊 Статистика", "📊 Stats", "📊 Estadísticas"]

@router.message(lambda msg: msg.text in STATS_BUTTONS)
async def handle_stats_button(message: Message, context_store: ContextStore, db: DatabaseService) -> None:
    """Handle stats keyboard button press."""
    from src.handlers.settings import cmd_mystats
    await cmd_mystats(message, db, context_store)
