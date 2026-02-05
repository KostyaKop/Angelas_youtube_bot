"""Localization strings for the bot."""

MESSAGES = {
    "uk": {
        "welcome": "Привіт! Надішліть мені посилання на YouTube відео, і я зроблю для вас детальний аналіз (summary).\n\nТакож ви можете змінити мову в /settings.",
        "processing": "🔄 <b>Аналізую відео...</b>",
        "processing_with_title": "🔄 <b>Аналізую відео...</b>\n📺 {title}",
        "no_subtitles": "⚠️ <b>Не вдалося отримати субтитри.</b>\n\nМожливі причини:\n• Субтитри вимкнені автором\n• Відео занадто нове\n• Технічні обмеження\n\nСпробуйте інше відео з доступними субтитрами.",
        "ai_error": "🚫 <b>Технічна помилка</b>\n\nНе вдалося обробити відео. Можливо:\n• Відео занадто довге\n• Збій AI-моделі\n\nСпробуйте повторити запит через хвилину.",
        "invalid_url": "❌ <b>Невалідне посилання</b>\n\nНадішліть посилання на YouTube відео у форматі:\n• youtube.com/watch?v=...\n• youtu.be/...",
        "no_context": "🤔 <b>У вас поки немає активного відео для обговорення.</b>\n\n👇 Спочатку надішліть посилання на YouTube",
        "answer_failed": "🚫 <b>Не вдалося відповісти на питання.</b>\n\nСпробуйте ще раз або надішліть нове відео.",
        "footer_summary": "\n\n💬 <i>Задайте питання по відео або надішліть нове посилання</i>",
        "footer_answer": "\n\n💬 <i>Можете задати ще питання або надіслати нове посилання</i>",
        "language_name": "українській",
        "settings_title": "⚙️ <b>Налаштування</b>\n\nОберіть вашу мову:",
        "current_language": "🇺🇦 Українська",
        "language_selected": "✅ Мову змінено на Українську",
        "language_btn_uk": "🇺🇦 Українська",
        "language_btn_en": "🇺🇸 English",
        "language_btn_ru": "🇷🇺 Русский",
        # Analysis headers
        "summary_header": "Головна думка",
        "topics_header": "Ключові теми",
        "positions_header": "Позиції учасників",
        "arguments_header": "Аргументи",
        "conclusions_header": "Практичні висновки",
    },
    "en": {
        "welcome": "Hi! Send me a YouTube video link, and I'll create a detailed analysis (summary) for you.\n\nYou can also change the language in /settings.",
        "processing": "🔄 <b>Analyzing video...</b>",
        "processing_with_title": "🔄 <b>Analyzing video...</b>\n📺 {title}",
        "no_subtitles": "⚠️ <b>Failed to get subtitles.</b>\n\nPossible reasons:\n• Subtitles disabled by author\n• Video is too new\n• Technical limitations\n\nTry another video with available subtitles.",
        "ai_error": "🚫 <b>Technical error</b>\n\nFailed to process video. Possibly:\n• Video is too long\n• AI model failure\n\nPlease try again in a minute.",
        "invalid_url": "❌ <b>Invalid link</b>\n\nPlease send a YouTube video link in format:\n• youtube.com/watch?v=...\n• youtu.be/...",
        "no_context": "🤔 <b>No active video for discussion yet.</b>\n\n👇 First, send a YouTube link",
        "answer_failed": "🚫 <b>Failed to answer the question.</b>\n\nTry again or send a new video.",
        "footer_summary": "\n\n💬 <i>Ask a question about the video or send a new link</i>",
        "footer_answer": "\n\n💬 <i>You can ask more questions or send a new link</i>",
        "language_name": "ENGLISH",
        "settings_title": "⚙️ <b>Settings</b>\n\nChoose your language:",
        "current_language": "🇺🇸 English",
        "language_selected": "✅ Language changed to English",
        "language_btn_uk": "🇺🇦 Українська",
        "language_btn_en": "🇺🇸 English",
        "language_btn_ru": "🇷🇺 Русский",
        # Analysis headers
        "summary_header": "Main Idea",
        "topics_header": "Key Topics",
        "positions_header": "Participant Positions",
        "arguments_header": "Arguments",
        "conclusions_header": "Practical Conclusions",
    },
    "ru": {
        "welcome": "Привет! Отправьте мне ссылку на YouTube видео, и я сделаю для вас детальный анализ (summary).\n\nТакже вы можете изменить язык в /settings.",
        "processing": "🔄 <b>Анализирую видео...</b>",
        "processing_with_title": "🔄 <b>Анализирую видео...</b>\n📺 {title}",
        "no_subtitles": "⚠️ <b>Не удалось получить субтитры.</b>\n\nВозможные причины:\n• Субтитры отключены автором\n• Видео слишком новое\n• Технические ограничения\n\nПопробуйте другое видео с доступными субтитрами.",
        "ai_error": "🚫 <b>Техническая ошибка</b>\n\nНе удалось обработать видео. Возможно:\n• Видео слишком длинное\n• Сбой AI-модели\n\nПопробуйте повторить запрос через минуту.",
        "invalid_url": "❌ <b>Невалидная ссылка</b>\n\nОтправьте ссылку на YouTube видео в формате:\n• youtube.com/watch?v=...\n• youtu.be/...",
        "no_context": "🤔 <b>У вас пока нет активного видео для обсуждения.</b>\n\n👇 Сначала отправьте ссылку на YouTube",
        "answer_failed": "🚫 <b>Не удалось ответить на вопрос.</b>\n\nПопробуйте еще раз или отправьте новое видео.",
        "footer_summary": "\n\n💬 <i>Задайте вопрос по видео или отправьте новую ссылку</i>",
        "footer_answer": "\n\n💬 <i>Можете задать еще вопрос или отправить новую ссылку</i>",
        "language_name": "русском",
        "settings_title": "⚙️ <b>Настройки</b>\n\nВыберите ваш язык:",
        "current_language": "🇷🇺 Русский",
        "language_selected": "✅ Язык изменен на Русский",
        "language_btn_uk": "🇺🇦 Українська",
        "language_btn_en": "🇺🇸 English",
        "language_btn_ru": "🇷🇺 Русский",
        # Analysis headers
        "summary_header": "Главная мысль",
        "topics_header": "Ключевые темы",
        "positions_header": "Позиции участников",
        "arguments_header": "Аргументы",
        "conclusions_header": "Практические выводы",
    }
}

DEFAULT_LANG = "uk"

def get_message(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """Get localized message."""
    lang_dict = MESSAGES.get(lang, MESSAGES[DEFAULT_LANG])
    msg = lang_dict.get(key, MESSAGES[DEFAULT_LANG].get(key, key))
    
    if kwargs:
        return msg.format(**kwargs)
    return msg
