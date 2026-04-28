from __future__ import annotations

import secrets
from datetime import datetime, timezone


_INVISIBLE_POOL = [
    "\u200b",  # ZERO WIDTH SPACE
    "\u200c",  # ZERO WIDTH NON-JOINER
    "\u2060",  # WORD JOINER
]


def append_unique_suffix(text: str, *, enabled: bool = True, add_timestamp: bool = True) -> str:
    """
    Telegram anti-spam uniqueness helper:
    - Appends a tiny invisible character + random nibble
    - Optionally adds a short timestamp (visible only if user copies)
    """
    if not enabled:
        return text

    inv = secrets.choice(_INVISIBLE_POOL)
    rnd = secrets.token_hex(1)  # 2 hex chars
    suffix = f"{inv}{rnd}"
    if add_timestamp:
        ts = datetime.now(tz=timezone.utc).strftime("%H%M%S")
        suffix += f"{inv}{ts}"
    return text + suffix

