from __future__ import annotations

import fcntl
import hashlib
from pathlib import Path


class ProcessLock:
    def __init__(self, *, key: str, base_dir: str = "/tmp") -> None:
        digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
        self._path = Path(base_dir) / f"tg-bot-{digest}.lock"
        self._fp = None

    def acquire(self) -> bool:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._fp = self._path.open("w")
        try:
            fcntl.flock(self._fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._fp.write(str(self._path))
            self._fp.flush()
            return True
        except BlockingIOError:
            self._fp.close()
            self._fp = None
            return False

    def release(self) -> None:
        if not self._fp:
            return
        try:
            fcntl.flock(self._fp.fileno(), fcntl.LOCK_UN)
        finally:
            self._fp.close()
            self._fp = None

