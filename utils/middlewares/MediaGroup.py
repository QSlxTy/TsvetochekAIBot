from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import Any

    from aiogram.types import Message


import asyncio

from aiogram import BaseMiddleware

from cachetools import TTLCache


class AlbumMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.latency = 0.02
        self._cache: TTLCache[str, list] = TTLCache(
            maxsize=10_000,
            ttl=30,
        )

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            message: Message,
            data: dict[str, Any],
    ) -> Any | None:

        if not message.media_group_id:
            return await handler(message, data)

        if message.media_group_id not in self._cache:
            self._cache[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)
            data['_is_last'] = True
            data['album'] = self._cache[message.media_group_id]
            await handler(message, data)
        else:
            self._cache[message.media_group_id].append(message)
