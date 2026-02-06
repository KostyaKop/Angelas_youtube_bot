"""Admin commands handler."""

import logging
from io import BytesIO

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from src.config import Config
from src.services.database import DatabaseService

router = Router()
logger = logging.getLogger(__name__)


def admin_only(handler):
    """Decorator to restrict access to admin only."""
    async def wrapper(message: Message, config: Config, **kwargs):
        if config.admin_user_id and message.from_user.id != config.admin_user_id:
            await message.answer("❌ Доступ заборонено")
            return
        return await handler(message, config=config, **kwargs)
    return wrapper


@router.message(Command("admin"))
async def cmd_admin(message: Message, config: Config, db: DatabaseService) -> None:
    """Show admin panel."""
    if config.admin_user_id and message.from_user.id != config.admin_user_id:
        await message.answer("❌ Доступ заборонено")
        return
    
    stats = await db.get_total_stats()
    
    text = f"""
<b>🔧 Адмін-панель</b>

<b>📊 Статистика:</b>
• Всього користувачів: <b>{stats['total_users']}</b>
• Активні (7 днів): <b>{stats['active_users_7d']}</b>
• Преміум: <b>{stats['premium_users']}</b>
• Всього відео: <b>{stats['total_videos']}</b>
• Відео сьогодні: <b>{stats['videos_today']}</b>

<b>⌨️ Команди:</b>
/users — Список користувачів
/addcredits &lt;user_id&gt; &lt;кількість&gt; — Додати кредити
/setpremium &lt;user_id&gt; — Зробити преміум
/block &lt;user_id&gt; — Заблокувати
/unblock &lt;user_id&gt; — Розблокувати
""".strip()
    
    await message.answer(text)


@router.message(Command("users"))
async def cmd_users(message: Message, config: Config, db: DatabaseService) -> None:
    """List all users."""
    if config.admin_user_id and message.from_user.id != config.admin_user_id:
        return
    
    users = await db.get_all_users_stats(limit=50)
    
    if not users:
        await message.answer("Немає користувачів.")
        return
    
    lines = ["<b>👥 Користувачі (останні 50):</b>\n"]
    
    for u in users:
        premium = "⭐" if u["is_premium"] else ""
        blocked = "🚫" if u["is_blocked"] else ""
        name = u["username"] or u["first_name"] or "—"
        lines.append(
            f"{premium}{blocked}<code>{u['user_id']}</code> @{name} — "
            f"💰{u['credits']} 📹{u['total_videos']}"
        )
    
    await message.answer("\n".join(lines))


@router.message(Command("addcredits"))
async def cmd_addcredits(message: Message, config: Config, db: DatabaseService) -> None:
    """Add credits to user."""
    if config.admin_user_id and message.from_user.id != config.admin_user_id:
        return
    
    args = message.text.split()[1:]
    
    if len(args) != 2:
        await message.answer("❌ Формат: /addcredits &lt;user_id&gt; &lt;кількість&gt;")
        return
    
    # Clean arguments from common formatting characters like < > [ ]
    def clean_arg(arg: str) -> str:
        return arg.strip().replace("<", "").replace(">", "").replace("[", "").replace("]", "")

    try:
        user_id = int(clean_arg(args[0]))
        amount = int(clean_arg(args[1]))
    except (ValueError, IndexError):
        await message.answer("❌ Невірний формат. user_id та кількість мають бути числами.")
        return
    
    success = await db.add_credits(user_id, amount)
    
    if success:
        await message.answer(f"✅ Додано <b>{amount}</b> кредитів користувачу <code>{user_id}</code>")
    else:
        await message.answer(f"❌ Користувача <code>{user_id}</code> не знайдено")


@router.message(Command("setpremium"))
async def cmd_setpremium(message: Message, config: Config, db: DatabaseService) -> None:
    """Set user as premium."""
    if config.admin_user_id and message.from_user.id != config.admin_user_id:
        return
    
    args = message.text.split()[1:]
    
    if len(args) != 1:
        await message.answer("❌ Формат: /setpremium &lt;user_id&gt;")
        return
    
    def clean_arg(arg: str) -> str:
        return arg.strip().replace("<", "").replace(">", "").replace("[", "").replace("]", "")

    try:
        user_id = int(clean_arg(args[0]))
    except (ValueError, IndexError):
        await message.answer("❌ Невірний user_id")
        return
    
    success = await db.set_premium(user_id, True)
    
    if success:
        await message.answer(f"✅ Користувач <code>{user_id}</code> тепер преміум ⭐")
    else:
        await message.answer(f"❌ Користувача <code>{user_id}</code> не знайдено")


@router.message(Command("block"))
async def cmd_block(message: Message, config: Config, db: DatabaseService) -> None:
    """Block user."""
    if config.admin_user_id and message.from_user.id != config.admin_user_id:
        return
    
    args = message.text.split()[1:]
    
    if len(args) != 1:
        await message.answer("❌ Формат: /block &lt;user_id&gt;")
        return
    
    def clean_arg(arg: str) -> str:
        return arg.strip().replace("<", "").replace(">", "").replace("[", "").replace("]", "")

    try:
        user_id = int(clean_arg(args[0]))
    except (ValueError, IndexError):
        await message.answer("❌ Невірний user_id")
        return
    
    success = await db.block_user(user_id, True)
    
    if success:
        await message.answer(f"🚫 Користувача <code>{user_id}</code> заблоковано")
    else:
        await message.answer(f"❌ Користувача <code>{user_id}</code> не знайдено")


@router.message(Command("unblock"))
async def cmd_unblock(message: Message, config: Config, db: DatabaseService) -> None:
    """Unblock user."""
    if config.admin_user_id and message.from_user.id != config.admin_user_id:
        return
    
    args = message.text.split()[1:]
    
    if len(args) != 1:
        await message.answer("❌ Формат: /unblock &lt;user_id&gt;")
        return
    
    def clean_arg(arg: str) -> str:
        return arg.strip().replace("<", "").replace(">", "").replace("[", "").replace("]", "")

    try:
        user_id = int(clean_arg(args[0]))
    except (ValueError, IndexError):
        await message.answer("❌ Невірний user_id")
        return
    
    success = await db.block_user(user_id, False)
    
    if success:
        await message.answer(f"✅ Користувача <code>{user_id}</code> розблоковано")
    else:
        await message.answer(f"❌ Користувача <code>{user_id}</code> не знайдено")
