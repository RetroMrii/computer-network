"""Static path validation and safe filesystem resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


ALLOWED_DIRECTORY_ROOTS = frozenset({"/", "/public", "/css", "/images"})
INDEX_URL_PATH = "/public/index.html"


@dataclass(frozen=True)
class PathValidationResult:
    status_code: int
    reason: str
    decoded_path: str
    filesystem_path: Path | None = None

    @property
    def is_allowed(self) -> bool:
        return self.status_code == 200 and self.filesystem_path is not None


def resolve_static_path(
    raw_url_path: str, static_root: str | Path
) -> PathValidationResult:
    path_without_query = _strip_query_and_fragment(raw_url_path)
    decoded_path = unquote(path_without_query)

    if not decoded_path.startswith("/"):
        return _bad_request(decoded_path)
    if _contains_traversal(decoded_path):
        return _bad_request(decoded_path)

    mapped_path = (
        INDEX_URL_PATH if decoded_path in {"/", "/index.html"} else decoded_path
    )
    if _directory_root(mapped_path) not in ALLOWED_DIRECTORY_ROOTS:
        return _forbidden(decoded_path)

    root_path = Path(static_root).resolve(strict=False)
    candidate_path = (root_path / mapped_path.lstrip("/")).resolve(strict=False)
    if not _is_inside_root(candidate_path, root_path):
        return _bad_request(decoded_path)

    return PathValidationResult(
        status_code=200,
        reason="OK",
        decoded_path=mapped_path,
        filesystem_path=candidate_path,
    )


def _strip_query_and_fragment(raw_url_path: str) -> str:
    return raw_url_path.split("?", 1)[0].split("#", 1)[0]


def _contains_traversal(decoded_path: str) -> bool:
    return ".." in decoded_path or "\\" in decoded_path


def _directory_root(decoded_path: str) -> str:
    if decoded_path == "/":
        return "/"
    first_segment = decoded_path.strip("/").split("/", 1)[0]
    return f"/{first_segment}" if first_segment else "/"


def _is_inside_root(candidate_path: Path, root_path: Path) -> bool:
    try:
        candidate_path.relative_to(root_path)
    except ValueError:
        return False
    return True


def _bad_request(decoded_path: str) -> PathValidationResult:
    return PathValidationResult(
        status_code=400,
        reason="Bad Request",
        decoded_path=decoded_path,
    )


def _forbidden(decoded_path: str) -> PathValidationResult:
    return PathValidationResult(
        status_code=403,
        reason="Forbidden",
        decoded_path=decoded_path,
    )
