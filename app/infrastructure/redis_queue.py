from __future__ import annotations

import json
import logging

import redis

from app.settings import get_settings

log = logging.getLogger(__name__)
QUEUE_KEY = "oficina:execution:queue"


class ExecutionQueue:
    def __init__(self, url: str | None = None) -> None:
        self._url = url or get_settings().redis_url
        self._client: redis.Redis | None = None

    def _redis(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.Redis.from_url(self._url, decode_responses=True)
        return self._client

    def enqueue(self, os_id: int, correlation_id: str | None = None) -> None:
        try:
            self._redis().zadd(QUEUE_KEY, {json.dumps({"os_id": os_id, "correlation_id": correlation_id}): os_id})
        except Exception:  # noqa: BLE001
            log.warning("redis indisponível; fila em memória ignorada")

    def peek(self, limit: int = 20) -> list[dict]:
        try:
            items = self._redis().zrange(QUEUE_KEY, 0, limit - 1)
            return [json.loads(x) for x in items]
        except Exception:  # noqa: BLE001
            return []

    def ping(self) -> bool:
        try:
            return bool(self._redis().ping())
        except Exception:  # noqa: BLE001
            return False
