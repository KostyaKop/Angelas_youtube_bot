"""Text formatting utilities for Telegram messages."""

import re


def format_timestamp(seconds: float) -> str:
    """
    Format seconds as [MM:SS] or [HH:MM:SS].
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string
    """
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    if hours > 0:
        return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"
    return f"[{minutes:02d}:{secs:02d}]"


def escape_html(text: str) -> str:
    """
    Escape HTML special characters for Telegram.
    
    Args:
        text: Raw text
        
    Returns:
        HTML-escaped text
    """
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def clean_markdown_artifacts(text: str) -> str:
    """
    Remove markdown artifacts that AI might accidentally include.
    
    Converts markdown to HTML where possible.
    
    Args:
        text: Text that might contain markdown
        
    Returns:
        Cleaned text with HTML formatting
    """
    # Convert **bold** to <b>bold</b>
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    
    # Convert *italic* to <i>italic</i>
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    
    # Convert __underline__ to <u>underline</u>
    text = re.sub(r"__(.+?)__", r"<u>\1</u>", text)
    
    # Convert `code` to <code>code</code>
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    
    # Remove remaining markdown-style formatting
    text = text.replace("###", "")
    text = text.replace("##", "")
    text = text.replace("#", "")
    
    return text.strip()


def format_error_message(error_type: str, details: str = "") -> str:
    """
    Format error message for user.
    
    Args:
        error_type: Type of error
        details: Additional details
        
    Returns:
        Formatted error message
    """
    messages = {
        "no_subtitles": """
⚠️ <b>Не вдалося отримати субтитри.</b>

Можливі причини:
• Субтитри вимкнені автором
• Відео занадто нове
• Технічні обмеження

Спробуйте інше відео з доступними субтитрами.
""",
        "ai_error": """
🚫 <b>Технічна помилка</b>

Не вдалося обробити відео. Можливо:
• Відео занадто довге
• Збій AI-моделі

Спробуйте повторити запит через хвилину.
""",
        "no_context": """
🤔 <b>У вас поки немає активного відео для обговорення.</b>

👇 Спочатку надішліть посилання на YouTube
""",
        "invalid_url": """
❌ <b>Невалідне посилання</b>

Надішліть посилання на YouTube відео у форматі:
• youtube.com/watch?v=...
• youtu.be/...
""",
    }
    
    base_message = messages.get(error_type, "❌ Сталася помилка")
    
    if details:
        return f"{base_message.strip()}\n\n<i>{details}</i>"
    
    return base_message.strip()
