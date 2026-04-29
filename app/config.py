from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(alias="BOT_TOKEN")
    db_url: str = Field(default="sqlite+aiosqlite:///./data/bot.sqlite3", alias="DB_URL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # High-conversion links (can be updated anytime via .env)
    groups_url: str = Field(default="https://t.me/", alias="GROUPS_URL")
    app_url: str = Field(default="https://example.com/download", alias="APP_URL")
    official_bot_url: str = Field(default="https://t.me/", alias="OFFICIAL_BOT_URL")
    support_url: str = Field(default="https://t.me/", alias="SUPPORT_URL")
    comment_url: str = Field(default="https://t.me/", alias="COMMENT_URL")
    conversion_url: str = Field(default="https://example.com/convert", alias="CONVERSION_URL")

    # Anti-spam uniqueness (for broadcasts)
    broadcast_unique_suffix: bool = Field(default=True, alias="BROADCAST_UNIQUE_SUFFIX")

    # Admin / broadcast controls
    admin_ids: str = Field(default="", alias="ADMIN_IDS")
    broadcast_rps: int = Field(default=30, alias="BROADCAST_RPS")

    # Gemini Flash translation
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")

    @property
    def admin_id_set(self) -> set[int]:
        raw = (self.admin_ids or "").strip()
        if not raw:
            return set()
        out: set[int] = set()
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                out.add(int(part))
            except ValueError:
                continue
        return out


def load_settings() -> Settings:
    return Settings()

