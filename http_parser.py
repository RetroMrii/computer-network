"""HTTP request-line parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_HTTP_VERSIONS = {"HTTP/1.0", "HTTP/1.1"}
TOKEN_SEPARATORS = set('()<>@,;:\\"/[]?={} \t')


@dataclass(frozen=True)
class HttpRequest:
    method: str
    path: str
    version: str
    request_line: str


class HttpParseError(ValueError):
    """Raised when the decoded HTTP request line is malformed."""


def parse_request(header_text: str) -> HttpRequest:
    """Parse the request line from decoded HTTP header text."""
    request_line = _first_header_line(header_text)
    return parse_request_line(request_line)


def parse_request_line(request_line: str) -> HttpRequest:
    parts = request_line.split()
    if len(parts) != 3:
        raise HttpParseError("request line must contain method, path, and version")

    method, path, version = parts
    if not _is_valid_method(method):
        raise HttpParseError("method token is malformed")
    if not path.startswith("/"):
        raise HttpParseError("path must start with /")
    if version not in SUPPORTED_HTTP_VERSIONS:
        raise HttpParseError("unsupported or malformed HTTP version")

    return HttpRequest(
        method=method,
        path=path,
        version=version,
        request_line=request_line,
    )


def _first_header_line(header_text: str) -> str:
    first_line = header_text.splitlines()[0] if header_text.splitlines() else ""
    if not first_line:
        raise HttpParseError("request line is empty")
    return first_line


def _is_valid_method(method: str) -> bool:
    return bool(method) and all(_is_token_char(character) for character in method)


def _is_token_char(character: str) -> bool:
    return character.isascii() and character.isprintable() and character not in TOKEN_SEPARATORS
