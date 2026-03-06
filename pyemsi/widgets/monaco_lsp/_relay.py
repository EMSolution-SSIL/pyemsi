from __future__ import annotations

import argparse
import asyncio
import json
import logging
from collections.abc import Sequence

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
except Exception as exc:  # pragma: no cover - import failure surfaced at runtime
    raise RuntimeError("The 'websockets' package is required for Monaco LSP relay") from exc


LOGGER = logging.getLogger(__name__)


class StdioJsonRpcClient:
    def __init__(self, command: Sequence[str]):
        self._command = list(command)
        self._proc: asyncio.subprocess.Process | None = None
        self._write_lock = asyncio.Lock()

    async def start(self) -> None:
        self._proc = await asyncio.create_subprocess_exec(
            *self._command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )

    @property
    def alive(self) -> bool:
        return self._proc is not None and self._proc.returncode is None

    async def write(self, payload: dict) -> None:
        if self._proc is None or self._proc.stdin is None:
            raise RuntimeError("LSP process stdin is not available")

        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        frame = b"Content-Length: " + str(len(body)).encode("ascii") + b"\r\n\r\n" + body

        async with self._write_lock:
            self._proc.stdin.write(frame)
            await self._proc.stdin.drain()

    async def read(self) -> dict:
        if self._proc is None or self._proc.stdout is None:
            raise RuntimeError("LSP process stdout is not available")

        header = await self._proc.stdout.readuntil(b"\r\n\r\n")
        content_length = _extract_content_length(header)
        body = await self._proc.stdout.readexactly(content_length)
        return json.loads(body.decode("utf-8"))

    async def stop(self) -> None:
        if self._proc is None:
            return
        if self._proc.returncode is None:
            self._proc.terminate()
            try:
                await asyncio.wait_for(self._proc.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                self._proc.kill()
                await self._proc.wait()


class WsLspRelay:
    def __init__(self, host: str, port: int, upstream_command: Sequence[str]):
        self._host = host
        self._port = port
        self._upstream = StdioJsonRpcClient(upstream_command)
        self._clients: set[WebSocketServerProtocol] = set()
        self._broadcast_task: asyncio.Task | None = None

    async def run(self) -> None:
        await self._upstream.start()
        self._broadcast_task = asyncio.create_task(self._broadcast_from_upstream())
        async with websockets.serve(self._handle_client, self._host, self._port):
            LOGGER.info("Monaco relay listening on ws://%s:%s", self._host, self._port)
            await self._broadcast_task

    async def _handle_client(self, websocket: WebSocketServerProtocol) -> None:
        self._clients.add(websocket)
        try:
            async for raw in websocket:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                payload = json.loads(raw)
                await self._upstream.write(payload)
        except asyncio.CancelledError:
            raise
        except Exception:
            LOGGER.debug("Client relay loop ended", exc_info=True)
        finally:
            self._clients.discard(websocket)

    async def _broadcast_from_upstream(self) -> None:
        try:
            while self._upstream.alive:
                payload = await self._upstream.read()
                if not self._clients:
                    continue
                message = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
                dead_clients: list[WebSocketServerProtocol] = []
                for client in self._clients:
                    try:
                        await client.send(message)
                    except Exception:
                        dead_clients.append(client)
                for client in dead_clients:
                    self._clients.discard(client)
        finally:
            await self._upstream.stop()


def _extract_content_length(header: bytes) -> int:
    for line in header.split(b"\r\n"):
        if line.lower().startswith(b"content-length:"):
            value = line.split(b":", 1)[1].strip()
            return int(value.decode("ascii"))
    raise ValueError("Missing Content-Length header in upstream LSP response")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monaco WebSocket to stdio LSP relay")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--ws-port", required=True, type=int)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("upstream", nargs=argparse.REMAINDER)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if not args.upstream:
        raise SystemExit("Expected upstream command after '--' (for example basedpyright-langserver --stdio)")

    upstream = list(args.upstream)
    if upstream and upstream[0] == "--":
        upstream = upstream[1:]
    if not upstream:
        raise SystemExit("Expected upstream command after '--'")

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.ERROR,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    relay = WsLspRelay(args.host, args.ws_port, upstream)
    asyncio.run(relay.run())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
