import asyncio
from collections import defaultdict
from contextlib import suppress

from fastapi import WebSocket
from pydantic import BaseModel


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections[user_id].add(websocket)

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            sockets = self._connections.get(user_id)
            if sockets is None:
                return
            sockets.discard(websocket)
            if not sockets:
                del self._connections[user_id]

    async def send_to_user(self, user_id: int, payload: BaseModel) -> None:
        async with self._lock:
            sockets = list(self._connections.get(user_id, ()))
        if not sockets:
            return
        data = payload.model_dump_json()

        for ws in sockets:
            with suppress(Exception):
                await ws.send_text(data)

    def is_connected(self, user_id: int) -> bool:
        return user_id in self._connections


manager = ConnectionManager()
