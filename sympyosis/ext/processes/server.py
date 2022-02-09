from typing import Any, Awaitable, Callable
import asyncio
import json


class Server:
    def __init__(self, *, port: int, host: str = "127.0.0.1"):
        self._port = port
        self._host = host
        self._actions = {}

    def add_action(self, action: str, callback: Callable[[Any], Awaitable[str]]):
        self._actions[action] = callback

    async def accept(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            while body := await reader.readuntil(b"\r\r"):
                response = await self.create_response(body[:-2].decode())
                await writer.drain()
                writer.write(json.dumps({"payload": response}).encode())
                writer.write(b"\r\r")
        except asyncio.exceptions.IncompleteReadError:
            pass

    async def create_response(self, body: str) -> Any:
        error = "An unknown error was encountered"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            error = "There was an error decoding the JSON"
        else:
            match data:
                case {"payload": payload, "action": action} if action in self._actions:
                    try:
                        return await self._actions[action](payload)
                    except Exception as e:
                        error = f"Action handler for {action} failed:\n   {type(e).__name__}: {e}"

                case {"action": action} if action not in self._actions:
                    error = "No handler was found for the requested action"

                case {"action": _}:
                    error = "No payload present in the request"

                case {"payload": _}:
                    error = "No action present in the request"

                case {}:
                    error = "No action or payload present in the request"

        return {"error": error}

    async def listen(self):
        server = await asyncio.start_server(self.accept, host=self._host, port=self._port)
        await server.serve_forever()
