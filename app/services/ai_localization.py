from __future__ import annotations

import asyncio
import json
import re
import time
from typing import Iterable

from google import genai
from google.genai import types as genai_types
from google.genai.errors import ClientError
from loguru import logger


LANG_NAME = {
    "en": "English",
    "ph": "Taglish (Philippines)",
    "vi": "Vietnamese",
    "es": "Spanish (LATAM)",
    "tr": "Turkish",
}

# Slightly looser thresholds so promo/marketing copy is less likely to come back empty / English-only.
_GEMINI_SAFETY = [
    genai_types.SafetySetting(
        category=genai_types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=genai_types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    genai_types.SafetySetting(
        category=genai_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=genai_types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    genai_types.SafetySetting(
        category=genai_types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=genai_types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    genai_types.SafetySetting(
        category=genai_types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=genai_types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
]

# Space out sequential fallback calls (free tier RPM is tiny).
_SEQUENTIAL_GAP_SEC = 4.0


def _build_prompt(english_text: str, target_lang: str) -> str:
    lang_label = LANG_NAME.get(target_lang, target_lang)
    return (
        "You are a professional marketing localizer (compliance-aware tone).\n"
        f"Translate the following English HTML into **{lang_label}** only.\n"
        "Rules:\n"
        "- The **entire** visible copy must be in the target language (no English paragraphs left untranslated).\n"
        "- Preserve all HTML tags and attributes exactly (<b>, <i>, <a href=\"...\">, line breaks).\n"
        "- Keep numbers, promo codes, and brand-style words if they are normally kept untranslated in that market.\n"
        "- Return **only** the translated HTML/text, no preamble or quotes.\n\n"
        f"Target language again: **{lang_label}**\n\n"
        f"English source:\n{english_text}"
    )


def _build_batch_prompt(english_text: str, keys: tuple[str, ...]) -> str:
    key_list = ", ".join(f'"{k}"' for k in keys)
    return (
        "Translate the English HTML below into multiple marketing variants.\n"
        f"Return **only** valid JSON with exactly these string keys: {key_list}.\n"
        "Values must be the full translated HTML for each locale:\n"
        '- "ph": Taglish (Philippines English–Filipino mix)\n'
        '- "vi": Vietnamese\n'
        '- "tr": Turkish\n'
        '- "es": Latin American Spanish\n\n'
        "Rules:\n"
        "- Preserve ALL HTML tags and attributes exactly.\n"
        "- Translate all visible user-facing text in each value.\n"
        "- Keep promo codes / numbers unless locals normally keep them in Latin script unchanged.\n"
        "- No markdown code fences, no commentary, no extra keys — JSON object only.\n\n"
        f"English source:\n{english_text}"
    )


def _extract_text(resp: genai_types.GenerateContentResponse) -> str:
    raw = (getattr(resp, "text", None) or "").strip()
    if raw:
        return raw
    try:
        cands = resp.candidates or []
        if not cands or not cands[0].content or not cands[0].content.parts:
            return ""
        chunks: list[str] = []
        for part in cands[0].content.parts:
            if isinstance(part.text, str) and part.text:
                chunks.append(part.text)
        return "".join(chunks).strip()
    except Exception:
        return ""


def _log_blocked_response(resp: genai_types.GenerateContentResponse, target_lang: str) -> None:
    try:
        cands = resp.candidates or []
        if not cands:
            pf = getattr(resp, "prompt_feedback", None)
            logger.warning("Gemini returned no candidates (lang=%s) prompt_feedback=%s", target_lang, pf)
            return
        fr = getattr(cands[0], "finish_reason", None)
        if fr is not None and "SAFETY" in str(fr).upper():
            logger.warning("Gemini finish_reason=%s for lang=%s — output may be empty", fr, target_lang)
    except Exception:
        pass


def _parse_batch_json(text: str, keys: tuple[str, ...]) -> dict[str, str] | None:
    t = (text or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.I)
        t = re.sub(r"\s*```\s*$", "", t)
    try:
        obj = json.loads(t)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    out: dict[str, str] = {}
    for k in keys:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            out[k] = v.strip()
    if len(out) != len(keys):
        return None
    return out


def _retry_delay_from_429(exc: BaseException) -> float:
    msg = str(exc)
    m = re.search(r"retry in ([\d.]+)s", msg, re.I)
    if m:
        return min(65.0, float(m.group(1)) + 2.0)
    return 15.0


def _normalize_model_id(model: str) -> str:
    m = (model or "").strip()
    if not m:
        return "gemini-2.0-flash"
    if m.startswith("models/") or m.startswith("tunedModels/"):
        return m
    return m


def _generate_sync(english_text: str, target_lang: str, api_key: str, model: str) -> str:
    key = (api_key or "").strip()
    if not key:
        return english_text
    model_id = _normalize_model_id(model)
    try:
        client = genai.Client(api_key=key)
        config = genai_types.GenerateContentConfig(safety_settings=_GEMINI_SAFETY)
        resp = client.models.generate_content(
            model=model_id,
            contents=_build_prompt(english_text, target_lang),
            config=config,
        )
        text = _extract_text(resp)
        if not text:
            _log_blocked_response(resp, target_lang)
            return english_text
        return text
    except ClientError as e:
        if getattr(e, "code", None) == 429:
            logger.warning("Gemini 429 single-lang (lang=%s): %s", target_lang, e.message or e)
        else:
            logger.exception("Gemini ClientError (lang=%s model=%s)", target_lang, model_id)
        return english_text
    except Exception:
        logger.exception("Gemini localization failed (lang=%s model=%s)", target_lang, model_id)
        return english_text


def _generate_batch_sync(english_text: str, api_key: str, model: str, keys: tuple[str, ...]) -> dict[str, str] | None:
    """One API call returning JSON for all locales — avoids free-tier RPM bursts from 4 back-to-back calls."""
    key = (api_key or "").strip()
    if not key:
        return None
    model_id = _normalize_model_id(model)
    client = genai.Client(api_key=key)
    config = genai_types.GenerateContentConfig(safety_settings=_GEMINI_SAFETY)
    contents = _build_batch_prompt(english_text, keys)
    max_attempts = 1
    for attempt in range(max_attempts):
        try:
            resp = client.models.generate_content(model=model_id, contents=contents, config=config)
            text = _extract_text(resp)
            parsed = _parse_batch_json(text, keys) if text else None
            if parsed:
                return parsed
            logger.warning(
                "Gemini batch: missing/invalid JSON (attempt %s/%s) preview=%r",
                attempt + 1,
                max_attempts,
                (text or "")[:240],
            )
        except ClientError as e:
            if getattr(e, "code", None) == 429:
                logger.warning("Gemini 429 on batch translate; fast-fail to fallback (no wait)")
                return None
            logger.warning("Gemini batch ClientError: %s", e.message or e)
            return None
        except Exception:
            logger.exception("Gemini batch failed (model=%s)", model_id)
            return None
    return None


def _generate_sequential_sync(english_text: str, api_key: str, model: str, keys: Iterable[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for i, code in enumerate(keys):
        if i > 0:
            time.sleep(_SEQUENTIAL_GAP_SEC)
        out[code] = _generate_sync(english_text, code, api_key, model)
    return out


async def generate_localized_content(
    english_text: str,
    target_lang: str,
    *,
    api_key: str,
    model: str,
) -> str:
    if not (api_key or "").strip():
        return english_text
    return await asyncio.to_thread(_generate_sync, english_text, target_lang, api_key, model)


async def generate_campaign_translations(
    english_text: str,
    *,
    locale_codes: tuple[str, ...],
    api_key: str,
    model: str,
) -> dict[str, str]:
    """
    Fill locale_codes (e.g. ph,vi,tr,es) using one batched Gemini call when possible,
    else slower sequential calls with spacing (free-tier friendly).
    """
    if not (api_key or "").strip():
        return {c: english_text for c in locale_codes}
    keys = tuple(locale_codes)
    batch = await asyncio.to_thread(_generate_batch_sync, english_text, api_key, model, keys)
    if batch:
        return batch
    logger.info("Gemini batch failed; falling back to sequential translations with %ss gap", _SEQUENTIAL_GAP_SEC)
    return await asyncio.to_thread(_generate_sequential_sync, english_text, api_key, model, keys)


def non_en_locales_match_english(translations: dict[str, str]) -> bool:
    """True if every non-EN preview string equals EN — no key, API failure, quota, or safety."""
    en = (translations.get("en") or "").strip()
    for code in ("ph", "vi", "tr", "es"):
        if (translations.get(code) or "").strip() != en:
            return False
    return True
