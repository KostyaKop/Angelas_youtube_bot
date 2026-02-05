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


def clean_text_for_telegram(text: str) -> str:
    """
    Sanitize text for Telegram HTML format.
    
    1. Removes unsupported tags like <br>, <div>, <p>
    2. Converts lists (<ul>, <ol>, <li>) to bullet points
    3. Closes unclosed tags
    4. Converts Markdown shortcuts to HTML
    """
    if not text:
        return ""

    # 1. Remove unsupported block tags, replacing them with newlines if needed
    for tag in ["<br>", "<br/>", "<br />", "<p>", "<div>", "<h1>", "<h2>", "<h3>"]:
        text = text.replace(tag, "\n")
    
    # 2. Handle lists - convert <li> to bullet points
    text = text.replace("<li>", "• ")
    
    # 3. Strip closing tags and container tags
    for tag in ["</p>", "</div>", "<html>", "</html>", "<body>", "</body>", 
                "<ul>", "</ul>", "<ol>", "</ol>", "</li>", "</h1>", "</h2>", "</h3>"]:
        text = text.replace(tag, "")
        
    # 4. Remove tags we explicitly don't want (underlines, code blocks if AI ignored instructions)
    # We want to keep <b>, <i>, <a>, but remove others.
    # Simple strip for <u> and <code>
    text = text.replace("<u>", "").replace("</u>", "")
    text = text.replace("<code>", "").replace("</code>", "")

    # 5. Convert common Markdown to HTML
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Code - if any left in markdown format, strip backticks
    text = re.sub(r"`(.+?)`", r"\1", text)
    
    # 6. Final cleanup
    text = text.replace("###", "").replace("##", "")
    
    # Remove multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    
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
