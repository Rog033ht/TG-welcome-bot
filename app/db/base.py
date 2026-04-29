from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserUpsert:
    uid: int
    username: str | None
    full_name: str
    join_date: datetime
    language_code: str = "en"


class Database(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def init_schema(self) -> None: ...

    @abstractmethod
    async def upsert_user(self, user: UserUpsert) -> None: ...

    # Button click stats
    @abstractmethod
    async def log_button_click(
        self,
        *,
        uid: int,
        button_id: str,
        chat_id: int | None,
        message_id: int | None,
        created_at: datetime,
        payload: str | None = None,
    ) -> None: ...

    # Auto follow-ups
    @abstractmethod
    async def enqueue_followup(
        self,
        *,
        uid: int,
        template: str,
        due_at: datetime,
        created_at: datetime,
    ) -> bool: ...

    @abstractmethod
    async def fetch_due_followups(
        self,
        *,
        now: datetime,
        limit: int = 100,
    ) -> list[dict]: ...

    @abstractmethod
    async def mark_followup_sent(
        self,
        *,
        followup_id: int,
        sent_at: datetime,
    ) -> None: ...

    # Broadcast
    @abstractmethod
    async def save_asset(
        self,
        *,
        name: str,
        file_id: str,
        file_type: str,
        created_at: datetime,
    ) -> None: ...

    @abstractmethod
    async def get_asset(self, *, name: str) -> dict | None: ...

    @abstractmethod
    async def create_broadcast(
        self,
        *,
        asset_name: str,
        caption: str,
        created_at: datetime,
    ) -> int: ...

    @abstractmethod
    async def get_broadcast(self, *, broadcast_id: int) -> dict | None: ...

    @abstractmethod
    async def update_broadcast_progress(
        self,
        *,
        broadcast_id: int,
        status: str,
        last_uid: int,
        sent_count: int,
        fail_count: int,
        updated_at: datetime,
    ) -> None: ...

    @abstractmethod
    async def list_users_after(self, *, after_uid: int, limit: int) -> list[int]: ...

    @abstractmethod
    async def get_user_language(self, *, uid: int) -> str: ...

    # Campaign template (caption + buttons)
    @abstractmethod
    async def save_campaign_template(
        self,
        *,
        name: str,
        button_rows: list[list[dict]],
        created_at: datetime,
    ) -> None: ...

    @abstractmethod
    async def get_campaign_template(self, *, name: str) -> dict | None: ...

    @abstractmethod
    async def list_campaign_templates(self, *, limit: int = 20) -> list[dict]: ...

    @abstractmethod
    async def delete_campaign_template(self, *, name: str) -> bool: ...

    # Smart polls
    @abstractmethod
    async def save_smart_poll(
        self,
        *,
        poll_id: str,
        asset_name: str | None,
        question: str,
        option_a: str,
        option_b: str,
        base_a: int,
        base_b: int,
        created_at: datetime,
    ) -> None: ...

    @abstractmethod
    async def get_smart_poll(self, *, poll_id: str) -> dict | None: ...

    @abstractmethod
    async def upsert_smart_poll_vote(
        self,
        *,
        poll_id: str,
        uid: int,
        option: str,
        created_at: datetime,
    ) -> None: ...

    @abstractmethod
    async def get_smart_poll_results(self, *, poll_id: str) -> dict | None: ...

