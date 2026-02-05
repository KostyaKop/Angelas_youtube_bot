# YouTube Analysis Telegram Bot 🎬🤖

AI-асистент для глибокого аналізу YouTube відео з транскрипцією, детальним саммарі з тайм-кодами та можливістю діалогу.

## Features

- 📹 Аналіз YouTube відео з субтитрами
- 📝 Детальні саммарі з тайм-кодами
- 💬 Followup-питання по відео
- 🔄 AI fallback (Gemini → OpenAI)
- 📊 Логування в Google Sheets

## Tech Stack

| Component | Technology |
|-----------|------------|
| Bot Framework | aiogram 3.x |
| YouTube Transcripts | youtube-transcript-api |
| Primary AI | Gemini 2.0 Flash |
| Fallback AI | GPT-4o-mini |
| Context Storage | Upstash Redis |
| Logging | Google Sheets |
| Hosting | Railway |

## Quick Start

### 1. Clone & Install

```bash
git clone <repo-url>
cd youtube-bot
pip install -r requirements.txt
```

### 2. Environment Variables

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:
- `TELEGRAM_BOT_TOKEN` - from @BotFather
- `GEMINI_API_KEY` - from Google AI Studio
- `OPENAI_API_KEY` - from OpenAI Platform
- `UPSTASH_REDIS_URL` - from Upstash Console
- `GOOGLE_SHEETS_ID` - your spreadsheet ID
- `GOOGLE_SERVICE_ACCOUNT_JSON` - service account credentials

### 3. Run Locally

```bash
python -m src.main
```

### 4. Deploy to Railway

```bash
railway up
```

## Project Structure

```
src/
├── main.py              # Entry point
├── config.py            # Configuration
├── handlers/            # Telegram handlers
│   ├── commands.py      # /start, /help
│   ├── youtube.py       # Video processing
│   └── followup.py      # Q&A functionality
├── services/            # Business logic
│   ├── youtube.py       # Transcript extraction
│   ├── ai_analyzer.py   # Gemini/OpenAI analysis
│   ├── context_store.py # Redis context
│   └── sheets_logger.py # Google Sheets
└── utils/               # Utilities
    ├── validators.py    # URL validation
    ├── formatters.py    # HTML formatting
    └── chunker.py       # Message splitting
```

## Usage

1. Send YouTube link to the bot
2. Receive detailed analysis with timestamps
3. Ask followup questions about the video

### Supported URLs

- `youtube.com/watch?v=VIDEO_ID`
- `youtu.be/VIDEO_ID`
- `youtube.com/shorts/VIDEO_ID`

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Usage instructions |

## License

MIT
