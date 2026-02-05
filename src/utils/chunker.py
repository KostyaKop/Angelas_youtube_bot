"""Message chunking for Telegram's character limit."""


def split_message(text: str, max_length: int = 4000) -> list[str]:
    """
    Split long message into chunks respecting Telegram's limit.
    
    Tries to split at natural breakpoints:
    1. Double newlines (paragraphs)
    2. Single newlines
    3. Sentences
    4. Hard cut if nothing else works
    
    Args:
        text: Full message text
        max_length: Maximum chunk length (default 4000 to leave margin)
        
    Returns:
        List of message chunks
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    remaining = text
    
    while len(remaining) > max_length:
        chunk = remaining[:max_length]
        
        # Try to find natural break point
        split_pos = find_split_position(chunk)
        
        if split_pos > 0:
            chunks.append(remaining[:split_pos].rstrip())
            remaining = remaining[split_pos:].lstrip()
        else:
            # Hard cut if no break point found
            chunks.append(remaining[:max_length])
            remaining = remaining[max_length:]
    
    if remaining.strip():
        chunks.append(remaining.strip())
    
    return chunks


def find_split_position(text: str) -> int:
    """
    Find best position to split text.
    
    Priority:
    1. Last double newline (paragraph break)
    2. Last single newline
    3. Last sentence end (. ! ?)
    4. Last space
    
    Args:
        text: Text chunk to find split position in
        
    Returns:
        Position to split at, or 0 if none found
    """
    # Try double newline first
    pos = text.rfind("\n\n")
    if pos > len(text) * 0.3:  # Only if not too early
        return pos + 1
    
    # Try single newline
    pos = text.rfind("\n")
    if pos > len(text) * 0.3:
        return pos + 1
    
    # Try sentence end
    for punct in [". ", "! ", "? "]:
        pos = text.rfind(punct)
        if pos > len(text) * 0.3:
            return pos + 1
    
    # Try space
    pos = text.rfind(" ")
    if pos > len(text) * 0.2:
        return pos + 1
    
    return 0
