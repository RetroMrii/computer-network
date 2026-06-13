"""Request logging helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any


ClientAddress = tuple[Any, ...] | None


def log_request(
    client_address: ClientAddress,
    request_line: str | None,
    status_code: int,
    reason: str,
    response_byte_count: int,
) -> None:
    try:
        print(
            format_request_log(
                client_address,
                request_line,
                status_code,
                reason,
                response_byte_count,
            ),
            flush=True,
        )
    except OSError:
        pass


def format_request_log(
    client_address: ClientAddress,
    request_line: str | None,
    status_code: int,
    reason: str,
    response_byte_count: int,
) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client = _format_client_address(client_address)
    safe_request_line = _clean_request_line(request_line)
    safe_reason = _clean_text(reason) or "-"
    safe_byte_count = max(0, response_byte_count)
    return (
        f'[{timestamp}] {client} "{safe_request_line}" '
        f"{status_code} {safe_reason} {safe_byte_count} bytes"
    )


def _format_client_address(client_address: ClientAddress) -> str:
    if not client_address or len(client_address) < 2:
        return "unknown:0"
    host = _clean_text(client_address[0]) or "unknown"
    port = _clean_text(client_address[1]) or "0"
    return f"{host}:{port}"


def _clean_request_line(request_line: str | None) -> str:
    return _clean_text(request_line) or "-"


def _clean_text(value: object) -> str:
    text = str(value) if value is not None else ""
    return " ".join(text.replace('"', "'").split())
