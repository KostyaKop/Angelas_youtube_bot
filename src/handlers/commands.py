"""Command handlers for /start and /help."""

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()

WELCOME_MESSAGE = """
👋 <b>Ласкаво просимо!</b>

Я — AI-асистент для глибокого аналізу YouTube відео.

<b>Що я вмію:</b>
🔹 Створюю розгорнуті саммарі з ключовими думками
🔹 Виділяю позиції авторів та аргументи
🔹 Додаю тайм-коди до кожної тези
🔹 Відповідаю на питання по відео

<b>Як використовувати:</b>
1️⃣ Надішліть посилання на YouTube відео
2️⃣ Отримайте детальний аналіз
3️⃣ Задавайте уточнюючі питання

👇 <b>Надішліть посилання, щоб почати</b>
""".strip()

HELP_MESSAGE = """
📖 <b>Інструкція з використання</b>

<b>Підтримувані формати посилань:</b>
• youtube.com/watch?v=VIDEO_ID
• youtu.be/VIDEO_ID
• youtube.com/shorts/VIDEO_ID

<b>Важливо:</b>
⚠️ Відео має мати субтитри (автоматичні або мануальні)
⚠️ Підтримуються відео до 2 годин

<b>Після аналізу ви можете:</b>
• Задати уточнюючі питання по відео
• Попросити розкрити конкретну тему детальніше
• Надіслати нове посилання (попередній контекст буде замінено)

💬 <b>Приклади питань:</b>
• "Розкажи детальніше про другу тему"
• "Які аргументи наводить автор?"
• "Дай більше прикладів з 15:30"
""".strip()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer(WELCOME_MESSAGE)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    await message.answer(HELP_MESSAGE)
