"""Raw-socket HTTP/1.0 static file server."""

from __future__ import annotations

import argparse
import socket
import threading
from pathlib import Path
from typing import Sequence

from http_parser import HttpParseError, HttpRequest, parse_request
from logger import log_request
from mime_utils import guess_mime_type
from response_builder import STATUS_REASONS, build_error_response, build_file_response
from security import resolve_static_path


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8081
DEFAULT_ROOT = "cna"
CLIENT_TIMEOUT_SECONDS = 10.0
MAX_HEADER_SIZE = 16384
RECV_SIZE = 4096
LISTEN_BACKLOG = 50
HEADER_TERMINATOR = b"\r\n\r\n"


class HeaderReadError(ValueError):
    pass


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Computer Networks HTTP/1.0 server.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--root", default=DEFAULT_ROOT)
    return parser.parse_args(argv)


def run_server(host: str, port: int, static_root: str | Path) -> None:
    root_path = Path(static_root)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(LISTEN_BACKLOG)

        print(f"Serving {root_path} on http://{host}:{port}")
        print("Press Ctrl+C to stop.")

        try:
            while True:
                client_socket, client_address = server_socket.accept()
                thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_address, root_path),
                    daemon=True,
                )
                thread.start()
        except KeyboardInterrupt:
            print("\nServer stopped.")


def handle_client(
    client_socket: socket.socket,
    client_address: tuple[str, int],
    static_root: Path,
) -> None:
    request_line: str | None = None
    status_code = 400
    reason = STATUS_REASONS[status_code]
    response = build_error_response(status_code)

    try:
        client_socket.settimeout(CLIENT_TIMEOUT_SECONDS)
        response, status_code, reason, request_line = _response_for_connection(
            client_socket,
            static_root,
        )
        try:
            client_socket.sendall(response)
        except OSError:
            pass
    finally:
        log_request(client_address, request_line, status_code, reason, len(response))
        _close_client(client_socket)


def _response_for_connection(
    client_socket: socket.socket,
    static_root: Path,
) -> tuple[bytes, int, str, str | None]:
    try:
        header_bytes = _read_http_header(client_socket)
        header_text = header_bytes.decode("iso-8859-1")
        request = parse_request(header_text)
    except (HeaderReadError, HttpParseError, OSError):
        return _error_response(400, None)

    if request.method != "GET":
        return _error_response(405, request.request_line)

    return _response_for_get(request, static_root)


def _response_for_get(
    request: HttpRequest,
    static_root: Path,
) -> tuple[bytes, int, str, str | None]:
    validation = resolve_static_path(request.path, static_root)
    if validation.status_code in {400, 403}:
        return _error_response(validation.status_code, request.request_line)

    filesystem_path = validation.filesystem_path
    if filesystem_path is None or not filesystem_path.is_file():
        return _error_response(404, request.request_line)

    try:
        body = filesystem_path.read_bytes()
    except OSError:
        return _error_response(404, request.request_line)

    response = build_file_response(body, guess_mime_type(filesystem_path))
    return response, 200, STATUS_REASONS[200], request.request_line


def _read_http_header(client_socket: socket.socket) -> bytes:
    buffer = bytearray()

    while True:
        terminator_index = buffer.find(HEADER_TERMINATOR)
        if terminator_index != -1:
            header_length = terminator_index + len(HEADER_TERMINATOR)
            if header_length > MAX_HEADER_SIZE:
                raise HeaderReadError("HTTP header is too large")
            return bytes(buffer[:header_length])

        if len(buffer) > MAX_HEADER_SIZE:
            raise HeaderReadError("HTTP header is too large")

        try:
            chunk = client_socket.recv(RECV_SIZE)
        except socket.timeout as exc:
            raise HeaderReadError("timed out while reading HTTP header") from exc

        if not chunk:
            raise HeaderReadError("client closed before sending a full HTTP header")
        buffer.extend(chunk)


def _error_response(status_code: int, request_line: str | None) -> tuple[bytes, int, str, str | None]:
    response = build_error_response(status_code)
    return response, status_code, STATUS_REASONS[status_code], request_line


def _close_client(client_socket: socket.socket) -> None:
    try:
        client_socket.close()
    except OSError:
        pass


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    run_server(args.host, args.port, args.root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
