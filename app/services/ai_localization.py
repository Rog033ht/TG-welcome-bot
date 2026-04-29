from __future__ import annotations

import asyncio

from google import genai
from loguru import logger


LANG_NAME = {
    "en": "English",
    "ph": "Taglish (Philippines)",
    "vi": "Vietnamese",
    "es": "Spanish (LATAM)",
    "tr": "Turkish",
}


def _build_prompt(english_text: str, target_lang: str) -> str:
    lang_label = LANG_NAME.get(target_lang, target_lang)
    return (
        "You are an expert iGaming marketer. "
        f"Translate this English text into {lang_label} using 'Old Driver' (underground) slang. "
        "Keep the tone catchy and aggressive. "
        "DO NOT change the HTML tags like <b> or <a>. "
        "Return only the translated text.\n\n"
        f"English text:\n{english_text}"
    )


def _generate_sync(english_text: str, target_lang: str, api_key: str, model: str) -> str:
    if not api_key.strip():
        return english_text
    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model=model,
            contents=_build_prompt(english_text, target_lang),
        )
        text = (getattr(resp, "text", None) or "").strip()
        return text or english_text
    except Exception:
        logger.exception("Gemini localization failed; falling back to English")
        return english_text


async def generate_localized_content(
    english_text: str,
    target_lang: str,
    *,
    api_key: str,
    model: str,
) -> str:
    if not api_key:
        return english_text
    return await asyncio.to_thread(_generate_sync, english_text, target_lang, api_key, model)

