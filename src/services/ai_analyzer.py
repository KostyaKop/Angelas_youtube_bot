"""AI analysis service with Gemini primary and OpenAI fallback."""

import logging
import google.generativeai as genai
from openai import AsyncOpenAI
from src.utils.formatters import clean_text_for_telegram

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI service for video analysis with fallback support."""
    
    # Analysis prompt template
    analysis_prompt_template = """ROLE: Senior Research Analyst
TASK: Create comprehensive video analysis in {language_name}

VIDEO TITLE: {title}
TRANSCRIPT WITH TIMESTAMPS:
{transcript}

OUTPUT FORMAT (STRICT TELEGRAM HTML):

<b>🎯 {summary_header}</b>
[2-3 sentences with the main idea]

<b>📌 {topics_header}</b>
• <b>Topic 1</b>: explanation [12:34]
• <b>Topic 2</b>: explanation [18:45]

<b>👤 {positions_header}</b>
• <b>Name/Role</b>: position with arguments [05:20]

<b>⚖️ {arguments_header}</b>
• <b>Thesis</b> — for: ... [15:30] / against: ... [16:45]

<b>💡 {conclusions_header}</b>
• Conclusion 1 [30:15]
• Conclusion 2 [32:40]

CRITICAL RULES:
1. Add timestamp [MM:SS] after EACH thesis
2. Use ONLY HTML tags: <b>, <i>
3. DO NOT use <ul>, <ol>, <li>, <u>, <code>, <br>, <p>, <div>
4. Use "• " for bullet points
5. NEVER USE MARKDOWN (*, _, **, ```)
6. Language: {language_name} (write ALL text in this language)
7. Detailed analysis (not brief)
8. NO intro phrases like "Here is...", "Вот анализ..."
9. Provide specific examples and quotes from the video"""

    followup_prompt_template = """CONTEXT:
Video Title: {title}
Previous Summary: {summary}
Full Transcript: {transcript}

USER QUESTION: {question}

Provide a detailed answer in {language_name} using the video context.
Include relevant timestamps [MM:SS] when referencing specific parts.

RULES:
1. Use ONLY HTML tags: <b>, <i>
2. DO NOT use <ul>, <ol>, <li>, <u>, <code>
3. Use "• " for bullet points
4. NEVER USE MARKDOWN
5. Answer directly, no intro phrases
6. Reference specific parts with timestamps
7. Language: {language_name} (write ALL text in this language)"""

    # ... (init method follows)

    def __init__(self, gemini_api_key: str, openai_api_key: str):
        """Initialize AI clients."""
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Configure OpenAI
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
    
    async def analyze_video(self, title: str, transcript: str, lang: str = "uk") -> str | None:
        """
        Analyze video transcript and generate summary.
        Uses Gemini as primary, OpenAI as fallback.
        """
        # Get localized prompt parameters
        from src.utils.locales import get_message
        
        prompt = self.analysis_prompt_template.format(
            title=title,
            transcript=transcript,
            language_name=get_message("language_name", lang),
            summary_header=get_message("summary_header", lang),
            topics_header=get_message("topics_header", lang),
            positions_header=get_message("positions_header", lang),
            arguments_header=get_message("arguments_header", lang),
            conclusions_header=get_message("conclusions_header", lang)
        )
        
        # Truncate transcript if too long (for token limits)
        if len(prompt) > 100000:
            # Keep first ~80% of transcript
            truncated_transcript = transcript[:int(len(transcript) * 0.8)]
            prompt = self.analysis_prompt_template.format(
                title=title,
                transcript=truncated_transcript,
                language_name=get_message("language_name", lang),
                summary_header=get_message("summary_header", lang),
                topics_header=get_message("topics_header", lang),
                positions_header=get_message("positions_header", lang),
                arguments_header=get_message("arguments_header", lang),
                conclusions_header=get_message("conclusions_header", lang)
            )
            logger.warning(f"Truncated transcript for analysis (original: {len(transcript)} chars)")
        
        # Try Gemini first
        result = await self._try_gemini(prompt)
        if result:
            logger.info("Analysis completed with Gemini")
            return result
        
        # Fallback to OpenAI
        logger.warning("Gemini failed, falling back to OpenAI")
        result = await self._try_openai(prompt)
        if result:
            logger.info("Analysis completed with OpenAI (fallback)")
            return result
        
        logger.error("Both AI providers failed")
        return None
    
    async def answer_followup(self, context: dict, question: str, lang: str = "uk") -> str | None:
        """
        Answer followup question using stored context.
        """
        from src.utils.locales import get_message
        
        prompt = self.followup_prompt_template.format(
            title=context.get("video_title", ""),
            summary=context.get("summary", ""),
            transcript=context.get("transcript", ""),
            question=question,
            language_name=get_message("language_name", lang)
        )
        
        # Truncate if needed
        if len(prompt) > 100000:
            # Reduce transcript in context
            reduced_transcript = context.get("transcript", "")[:50000]
            prompt = self.followup_prompt_template.format(
                title=context.get("video_title", ""),
                summary=context.get("summary", ""),
                transcript=reduced_transcript,
                question=question,
                language_name=get_message("language_name", lang)
            )
        
        # Try Gemini first
        result = await self._try_gemini(prompt)
        if result:
            return result
        
        # Fallback to OpenAI
        logger.warning("Gemini failed for followup, using OpenAI")
        return await self._try_openai(prompt)
    
    async def _try_gemini(self, prompt: str) -> str | None:
        """Try to generate response with Gemini."""
        try:
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                return clean_text_for_telegram(response.text)
            
            return None
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return None
    
    async def _try_openai(self, prompt: str) -> str | None:
        """Try to generate response with OpenAI (fallback)."""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a video analysis assistant. Output in Russian using HTML formatting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            if response.choices:
                return clean_text_for_telegram(response.choices[0].message.content)
            
            return None
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return None
