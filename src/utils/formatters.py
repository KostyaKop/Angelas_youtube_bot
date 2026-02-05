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
    Comprehensive sanitization for Telegram HTML format.
    
    Handles:
    1. Problematic Unicode characters (zero-width, direction marks, etc.)
    2. Unsupported HTML tags
    3. Markdown to HTML conversion
    4. HTML entity encoding for special characters
    5. Unclosed/malformed tags
    6. Control characters
    """
    if not text:
        return ""

    # ========== 1. Remove problematic Unicode characters ==========
    
    # Zero-width and invisible characters
    invisible_chars = [
        '\u200b',  # Zero-width space
        '\u200c',  # Zero-width non-joiner
        '\u200d',  # Zero-width joiner
        '\u200e',  # Left-to-right mark
        '\u200f',  # Right-to-left mark
        '\u2060',  # Word joiner
        '\u2061',  # Function application
        '\u2062',  # Invisible times
        '\u2063',  # Invisible separator
        '\u2064',  # Invisible plus
        '\ufeff',  # Byte order mark
        '\u00ad',  # Soft hyphen
        '\u034f',  # Combining grapheme joiner
    ]
    for char in invisible_chars:
        text = text.replace(char, '')
    
    # Remove control characters (except newline, tab)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # ========== 2. Escape special HTML characters FIRST ==========
    # But preserve existing valid HTML tags we want to keep
    
    # Temporarily protect valid tags
    protected_tags = {}
    tag_counter = 0
    
    # Protect allowed tags: <b>, </b>, <i>, </i>, <a href="...">, </a>
    def protect_tag(match):
        nonlocal tag_counter
        placeholder = f"__TAG_{tag_counter}__"
        protected_tags[placeholder] = match.group(0)
        tag_counter += 1
        return placeholder
    
    # Protect valid opening/closing tags
    text = re.sub(r'<(/?)(b|i|a)(\s[^>]*)?>',  protect_tag, text, flags=re.IGNORECASE)
    
    # Escape remaining < and > that aren't part of valid tags
    text = text.replace('&', '&amp;')  # Must be first
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    # Restore protected tags
    for placeholder, tag in protected_tags.items():
        text = text.replace(placeholder, tag)
    
    # ========== 3. Remove unsupported HTML tags ==========
    
    # Block tags - replace with newlines
    for tag in ['<br>', '<br/>', '<br />', '<p>', '<div>', '<h1>', '<h2>', '<h3>', '<h4>', '<h5>', '<h6>']:
        text = text.replace(tag, '\n')
        text = re.sub(rf'{re.escape(tag)}', '\n', text, flags=re.IGNORECASE)
    
    # Handle lists - convert <li> to bullet points
    text = re.sub(r'<li[^>]*>', '• ', text, flags=re.IGNORECASE)
    
    # Strip these closing/container tags
    tags_to_remove = [
        '</p>', '</div>', '<html>', '</html>', '<body>', '</body>',
        '<ul>', '</ul>', '<ol>', '</ol>', '</li>',
        '</h1>', '</h2>', '</h3>', '</h4>', '</h5>', '</h6>',
        '<u>', '</u>', '<code>', '</code>', '<pre>', '</pre>',
        '<span>', '</span>', '<strong>', '</strong>', '<em>', '</em>',
        '<blockquote>', '</blockquote>', '<hr>', '<hr/>', '<hr />',
    ]
    for tag in tags_to_remove:
        text = re.sub(rf'{re.escape(tag)}', '', text, flags=re.IGNORECASE)
    
    # Convert <strong> to <b> and <em> to <i> (before removal above)
    text = re.sub(r'<strong[^>]*>', '<b>', text, flags=re.IGNORECASE)
    text = re.sub(r'</strong>', '</b>', text, flags=re.IGNORECASE)
    text = re.sub(r'<em[^>]*>', '<i>', text, flags=re.IGNORECASE)
    text = re.sub(r'</em>', '</i>', text, flags=re.IGNORECASE)
    
    # ========== 4. Convert Markdown to HTML ==========
    
    # Code fences - remove entirely
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)  # Inline code - just keep text
    
    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    
    # Italic: *text* or _text_ (be careful not to match already converted)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<i>\1</i>', text)
    
    # Strikethrough ~~text~~ - not supported in Telegram, just remove markers
    text = re.sub(r'~~(.+?)~~', r'\1', text)
    
    # Headers (# ## ###) - just remove the markers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Horizontal rules
    text = re.sub(r'^[\-\*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    # ========== 5. Fix common AI output issues ==========
    
    # Remove "Here is..." / "Вот..." intro phrases (common AI pattern)
    intro_patterns = [
        r'^(Here is|Here\'s|Вот|Ось)[^:]*:\s*\n*',
        r'^(Below is|Нижче)[^:]*:\s*\n*',
    ]
    for pattern in intro_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Fix doubled tags like <b><b>text</b></b>
    text = re.sub(r'(<b>\s*)+', '<b>', text)
    text = re.sub(r'(\s*</b>)+', '</b>', text)
    text = re.sub(r'(<i>\s*)+', '<i>', text)
    text = re.sub(r'(\s*</i>)+', '</i>', text)
    
    # ========== 6. Balance unclosed tags ==========
    
    # Count open/close tags and add missing closers
    for tag in ['b', 'i']:
        open_count = len(re.findall(rf'<{tag}>', text, re.IGNORECASE))
        close_count = len(re.findall(rf'</{tag}>', text, re.IGNORECASE))
        
        if open_count > close_count:
            text += f'</{tag}>' * (open_count - close_count)
        elif close_count > open_count:
            # Remove extra closing tags from the end
            for _ in range(close_count - open_count):
                text = re.sub(rf'</{tag}>(?!.*</{tag}>)', '', text, count=1, flags=re.IGNORECASE)
    
    # ========== 7. Final cleanup ==========
    
    # Remove multiple consecutive newlines (max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove trailing whitespace from lines
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text



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
