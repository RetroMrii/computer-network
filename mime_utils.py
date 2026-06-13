"""MIME type helpers for static file responses."""

from __future__ import annotations

import mimetypes
from os import PathLike


DEFAULT_MIME_TYPE = "application/octet-stream"
JAVASCRIPT_MIME_TYPE = "application/javascript"


def guess_mime_type(path: str | PathLike[str]) -> str:
    mime_type, _encoding = mimetypes.guess_type(str(path))
    if str(path).lower().endswith(".js"):
        return JAVASCRIPT_MIME_TYPE
    return mime_type or DEFAULT_MIME_TYPE
