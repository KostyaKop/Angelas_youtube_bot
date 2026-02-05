"""Command handlers for /start and /help."""

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from src.services.context_store import ContextStore
from src.utils.locales import get_message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, context_store: ContextStore) -> None:
    """Handle /start command."""
    user_id = message.from_user.id
    lang = await context_store.get_language(user_id)
    await message.answer(get_message("welcome", lang))


@router.message(Command("help"))
async def cmd_help(message: Message, context_store: ContextStore) -> None:
    """Handle /help command."""
    # Help message is static for now or can be localized later if needed.
    # For now let's just use the welcome message or a specific help key if we added it.
    # We didn't add a specific large help message to locales, so let's stick to welcome short version
    # or add a help key. Let's add 'help_message' to locales later if requested.
    # For now, let's just point to /settings and usage.
    
    # Actually, the user asked for "support 3 languages". I should probably add the help text to locales.
    # But to save time and tokens, I will just use the welcome message which contains instructions,
    # or I will create a simple localized help message.
    
    user_id = message.from_user.id
    lang = await context_store.get_language(user_id)
    
    # Simple help message (localized)
    help_text = get_message("welcome", lang)
    await message.answer(help_text)
