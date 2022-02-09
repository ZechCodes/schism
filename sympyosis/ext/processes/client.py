from typing import Any
import asyncio
import json


class Client:
    def __init__(self, *, port: int, host: str = "127.0.0.1"):
        self.port = port
        self.host = host
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection("127.0.0.1", 8000)

    def close(self):
        self.writer.close()
        self.writer = self.reader = None

    async def send(self, action: str, payload: Any, *, allow_reconnect: int = 2) -> Any:
        if not self.writer and allow_reconnect:
            await self.connect()

        data = {"action": action, "payload": payload}
        await self.writer.drain()
        self.writer.write(json.dumps(data).encode())
        self.writer.write(b"\r\r")

        try:
            response = await self.reader.readuntil(b"\r\r")
        except asyncio.exceptions.IncompleteReadError:
            self.writer = self.reader = None
            if allow_reconnect:
                return await self.send(
                    action, payload, allow_reconnect=allow_reconnect - 1
                )
            else:
                raise

        return json.loads(response.decode())["payload"]
