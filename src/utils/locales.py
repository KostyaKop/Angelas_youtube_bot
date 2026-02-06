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
        "current_language": "Українська",
        "language_selected": "✅ Мову змінено на Українську",
        # Neutral button labels without flags
        "language_btn_uk": "UKR",
        "language_btn_en": "ENG",
        "language_btn_ru": "RUS",
        "language_btn_es": "ESP",
        # Analysis headers
        "summary_header": "Головна думка",
        "topics_header": "Ключові теми",
        "positions_header": "Позиції учасників",
        "arguments_header": "Аргументи",
        "conclusions_header": "Практичні висновки",
        # New: action buttons
        "btn_shorter": "📝 Коротше",
        "btn_my_stats": "📊 Статистика",
        "btn_export": "📥 Експорт",
        "shorter_processing": "⏳ Роблю коротку версію...",
        "shorter_result": "<b>📝 Коротка версія:</b>\n\n{content}",
        # Keyboard buttons
        "kb_settings": "⚙️ Налаштування",
        "kb_help": "❓ Допомога",
        "kb_stats": "📊 Статистика",
        # Errors
        "error_no_credits": "💰 <b>Закінчились кредити</b>\n\nНа вашому рахунку немає кредитів для обробки відео.\nПерегляньте свою статистику: /mystats",
        "error_blocked": "🚫 <b>Доступ заблоковано</b>\n\nВаш обліковий запис заблоковано.",
        "error_context_expired": "Контекст застарів, надішліть відео знову",
        "error_shorter_failed": "Не вдалось створити коротку версію",
        # Voice
        "voice_processing": "🎤 Обробляю голосове повідомлення...",
        "voice_failed_recognition": "❌ Не вдалося розпізнати голосове повідомлення",
        "voice_question_transcribed": "🎤 <i>Питання:</i> {text}\n\n⏳ Аналізую...",
        "voice_error": "❌ Помилка обробки голосового повідомлення",
        # Help message
        "help_message": "<b>🎬 YouTube Аналізатор</b>\n\n<b>Що я вмію:</b>\n• Аналізувати відео з YouTube\n• Відповідати на запитання по відео\n• Створювати короткі версії аналізу\n• Працювати з голосовими повідомленнями\n\n<b>Як працювати:</b>\n1. Надішліть посилання на YouTube відео\n2. Отримайте детальний аналіз\n3. Задавайте питання (текстом або голосом)\n4. Натисніть \"Коротше\" для тез\n\n<b>Формати посилань:</b>\n• youtube.com/watch?v=...\n• youtu.be/...\n• youtube.com/shorts/...\n• youtube.com/live/...",
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
        "language_name": "English",
        "settings_title": "⚙️ <b>Settings</b>\n\nChoose your language:",
        "current_language": "English",
        "language_selected": "✅ Language changed to English",
        "language_btn_uk": "UKR",
        "language_btn_en": "ENG",
        "language_btn_ru": "RUS",
        "language_btn_es": "ESP",
        "summary_header": "Main Idea",
        "topics_header": "Key Topics",
        "positions_header": "Participant Positions",
        "arguments_header": "Arguments",
        "conclusions_header": "Practical Conclusions",
        "btn_shorter": "📝 Shorter",
        "btn_my_stats": "📊 Stats",
        "btn_export": "📥 Export",
        "shorter_processing": "⏳ Creating short version...",
        "shorter_result": "<b>📝 Short version:</b>\n\n{content}",
        "kb_settings": "⚙️ Settings",
        "kb_help": "❓ Help",
        "kb_stats": "📊 Stats",
        # Errors
        "error_no_credits": "💰 <b>Out of credits</b>\n\nYou have no credits left to process videos.\nCheck your stats: /mystats",
        "error_blocked": "🚫 <b>Access denied</b>\n\nYour account is blocked.",
        "error_context_expired": "Context expired, please send the video again",
        "error_shorter_failed": "Failed to create short version",
        # Voice
        "voice_processing": "🎤 Processing voice message...",
        "voice_failed_recognition": "❌ Failed to recognize voice message",
        "voice_question_transcribed": "🎤 <i>Question:</i> {text}\n\n⏳ Analyzing...",
        "voice_error": "❌ Error processing voice message",
        "help_message": "<b>🎬 YouTube Analyzer</b>\n\n<b>What I can do:</b>\n• Analyze YouTube videos\n• Answer questions about videos\n• Create short summaries\n• Work with voice messages\n\n<b>How to use:</b>\n1. Send a YouTube video link\n2. Get detailed analysis\n3. Ask questions (text or voice)\n4. Click \"Shorter\" for key points\n\n<b>Supported links:</b>\n• youtube.com/watch?v=...\n• youtu.be/...\n• youtube.com/shorts/...\n• youtube.com/live/...",
    },
    "ru": {
        "welcome": "Привет! Отправьте мне ссылку на YouTube видео, и я сделаю для вас детальный анализ (summary).\n\nТакже вы можете изменить язык в /settings.",
        "processing": "🔄 <b>Анализирую видео...</b>",
        "processing_with_title": "🔄 <b>Анализирую видео...</b>\n📺 {title}",
        "no_subtitles": "⚠️ <b>Не удалось получить субтитры.</b>\n\nВозможные причины:\n• Субтитры отключены автором\n• Видео слишком новое\n• Технические ограничения\n\nПопробуйте другое видео с доступными субтитрами.",
        "ai_error": "🚫 <b>Техническая ошибка</b>\n\nНе удалось обработить видео. Возможно:\n• Видео слишком длинное\n• Сбой AI-модели\n\nПопробуйте повторить запрос через минуту.",
        "invalid_url": "❌ <b>Невалидная ссылка</b>\n\nОтправьте ссылку на YouTube видео в формате:\n• youtube.com/watch?v=...\n• youtu.be/...",
        "no_context": "🤔 <b>У вас пока нет активного видео для обсуждения.</b>\n\n👇 Сначала отправьте ссылку на YouTube",
        "answer_failed": "🚫 <b>Не удалось ответить на вопрос.</b>\n\nПопробуйте еще раз или отправьте новое видео.",
        "footer_summary": "\n\n💬 <i>Задайте вопрос по видео или отправьте новую ссылку</i>",
        "footer_answer": "\n\n💬 <i>Можете задать еще вопрос или отправить новую ссылку</i>",
        "language_name": "русском",
        "settings_title": "⚙️ <b>Настройки</b>\n\nВыберите ваш язык:",
        "current_language": "Русский",
        "language_selected": "✅ Язык изменен на Русский",
        "language_btn_uk": "UKR",
        "language_btn_en": "ENG",
        "language_btn_ru": "RUS",
        "language_btn_es": "ESP",
        "summary_header": "Главная мысль",
        "topics_header": "Ключевые темы",
        "positions_header": "Позиции участников",
        "arguments_header": "Аргументы",
        "conclusions_header": "Практические выводы",
        "btn_shorter": "📝 Короче",
        "btn_my_stats": "📊 Статистика",
        "btn_export": "📥 Экспорт",
        "shorter_processing": "⏳ Делаю короткую версию...",
        "shorter_result": "<b>📝 Короткая версия:</b>\n\n{content}",
        "kb_settings": "⚙️ Настройки",
        "kb_help": "❓ Помощь",
        "kb_stats": "📊 Статистика",
        # Errors
        "error_no_credits": "💰 <b>Закончились кредиты</b>\n\nНа вашем счету нет кредитов для обработки видео.\nПроверьте свою статистику: /mystats",
        "error_blocked": "🚫 <b>Доступ заблокирован</b>\n\nВаш аккаунт заблокирован.",
        "error_context_expired": "Контекст устарел, отправьте видео снова",
        "error_shorter_failed": "Не удалось создать краткую версию",
        # Voice
        "voice_processing": "🎤 Обрабатываю голосовое сообщение...",
        "voice_failed_recognition": "❌ Не удалось распознать голосовое сообщени",
        "voice_question_transcribed": "🎤 <i>Вопрос:</i> {text}\n\n⏳ Анализирую...",
        "voice_error": "❌ Ошибка обработки голосового сообщения",
        "help_message": "<b>🎬 YouTube Анализатор</b>\n\n<b>Что я умею:</b>\n• Анализировать видео с YouTube\n• Отвечать на вопросы по видео\n• Создавать краткие версии\n• Работать с голосовыми\n\n<b>Как использовать:</b>\n1. Отправьте ссылку на YouTube\n2. Получите анализ\n3. Задавайте вопросы\n4. Нажмите \"Короче\" для тезисов",
    },
    "es": {
        "welcome": "¡Hola! Envíame un enlace de video de YouTube y crearé un análisis detallado (resumen) para ti.\n\nTambién puedes cambiar el idioma en /settings.",
        "processing": "🔄 <b>Analizando video...</b>",
        "processing_with_title": "🔄 <b>Analizando video...</b>\n📺 {title}",
        "no_subtitles": "⚠️ <b>No se pudieron obtener los subtítulos.</b>\n\nPosibles razones:\n• Subtítulos desactivados por el autor\n• El video es muy nuevo\n• Limitaciones técnicas\n\nPrueba con otro video con subtítulos disponibles.",
        "ai_error": "🚫 <b>Error técnico</b>\n\nNo se pudo procesar el video. Posiblemente:\n• El video es muy largo\n• Fallo del modelo AI\n\nIntenta de nuevo en un minuto.",
        "invalid_url": "❌ <b>Enlace inválido</b>\n\nEnvía un enlace de video de YouTube en formato:\n• youtube.com/watch?v=...\n• youtu.be/...",
        "no_context": "🤔 <b>Aún no tienes un video activo para discutir.</b>\n\n👇 Primero, envía un enlace de YouTube",
        "answer_failed": "🚫 <b>No se pudo responder la pregunta.</b>\n\nIntenta de nuevo o envía un nuevo video.",
        "footer_summary": "\n\n💬 <i>Haz una pregunta sobre el video o envía un nuevo enlace</i>",
        "footer_answer": "\n\n💬 <i>Puedes hacer más preguntas o enviar un nuevo enlace</i>",
        "language_name": "español",
        "settings_title": "⚙️ <b>Configuración</b>\n\nElige tu idioma:",
        "current_language": "Español",
        "language_selected": "✅ Idioma cambiado a Español",
        "language_btn_uk": "UKR",
        "language_btn_en": "ENG",
        "language_btn_ru": "RUS",
        "language_btn_es": "ESP",
        "summary_header": "Idea Principal",
        "topics_header": "Temas Clave",
        "positions_header": "Posiciones de Participantes",
        "arguments_header": "Argumentos",
        "conclusions_header": "Conclusiones Prácticas",
        "btn_shorter": "📝 Más corto",
        "btn_my_stats": "📊 Estadísticas",
        "btn_export": "📥 Exportar",
        "shorter_processing": "⏳ Creando versión corta...",
        "shorter_result": "<b>📝 Versión corta:</b>\n\n{content}",
        "kb_settings": "⚙️ Ajustes",
        "kb_help": "❓ Ayuda",
        "kb_stats": "📊 Estadísticas",
        # Errors
        "error_no_credits": "💰 <b>Sin créditos</b>\n\nNo tienes créditos para procesar videos.\nRevisa tus estadísticas: /mystats",
        "error_blocked": "🚫 <b>Acceso bloqueado</b>\n\nTu cuenta está bloqueada.",
        "error_context_expired": "Contexto expirado, envía el video nuevamente",
        "error_shorter_failed": "No se pudo crear la versión corta",
        # Voice
        "voice_processing": "🎤 Procesando mensaje de voz...",
        "voice_failed_recognition": "❌ No se pudo reconocer el mensaje de voz",
        "voice_question_transcribed": "🎤 <i>Pregunta:</i> {text}\n\n⏳ Analizando...",
        "voice_error": "❌ Error al procesar el mensaje de voz",
        "help_message": "<b>🎬 YouTube Analizador</b>\n\n<b>Qué puedo hacer:</b>\n• Analizar videos de YouTube\n• Responder preguntas sobre videos\n• Crear resúmenes cortos\n• Trabajar con mensajes de voz\n\n<b>Cómo usar:</b>\n1. Envía un enlace de YouTube\n2. Recibe un análisis\n3. Haz preguntas\n4. Presiona \"Más corto\" para puntos clave",
    }
}

DEFAULT_LANG = "uk"

# Mapping from Telegram language codes to our language codes
TELEGRAM_LANG_MAP = {
    "uk": "uk",
    "ru": "ru",
    "es": "es",
    "en": "en",
    # Common variations
    "uk-UA": "uk",
    "ru-RU": "ru",
    "es-ES": "es",
    "es-MX": "es",
    "en-US": "en",
    "en-GB": "en",
}


def detect_language(telegram_lang_code: str | None) -> str:
    """
    Detect language from Telegram language code.
    Falls back to Ukrainian if unknown.
    """
    if not telegram_lang_code:
        return DEFAULT_LANG
    
    # Try exact match
    if telegram_lang_code in TELEGRAM_LANG_MAP:
        return TELEGRAM_LANG_MAP[telegram_lang_code]
    
    # Try prefix match (e.g., "en-AU" -> "en")
    prefix = telegram_lang_code.split("-")[0].lower()
    if prefix in TELEGRAM_LANG_MAP:
        return TELEGRAM_LANG_MAP[prefix]
    
    # Default to English for unknown languages (international fallback)
    return "en"


def get_message(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """Get localized message."""
    lang_dict = MESSAGES.get(lang, MESSAGES[DEFAULT_LANG])
    msg = lang_dict.get(key, MESSAGES[DEFAULT_LANG].get(key, key))
    
    if kwargs:
        return msg.format(**kwargs)
    return msg

