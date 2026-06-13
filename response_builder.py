"""Manual HTTP/1.0 response construction."""

from __future__ import annotations


CRLF = "\r\n"
ERROR_CONTENT_TYPE = "text/html; charset=utf-8"

STATUS_REASONS = {
    200: "OK",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
}

ERROR_DETAILS = {
    400: (
        "Request Line Repair",
        "The server could not understand the request syntax.",
        "Build a clean request line with exactly three parts: method, path, and HTTP version.",
        "GET /public/index.html HTTP/1.0",
    ),
    403: (
        "Access Gate",
        "The path is syntactically valid, but it points outside the approved public areas.",
        "Choose one allowed route root: /, /public, /css, or /images.",
        "/public/academy.html",
    ),
    404: (
        "Route Scout",
        "The route is allowed, but the requested file was not found.",
        "Find an existing academy file and request that exact path.",
        "/public/status-codes.html",
    ),
    405: (
        "Method Match",
        "This static server only serves files with the GET method.",
        "Switch the method to GET while keeping the target path unchanged.",
        "GET /public/index.html HTTP/1.0",
    ),
}


def build_response(
    status_code: int,
    reason: str,
    content_type: str,
    body: bytes,
) -> bytes:
    status_line = f"HTTP/1.0 {status_code} {reason}"
    header_lines = [
        status_line,
        f"Content-Length: {len(body)}",
        f"Content-Type: {content_type}",
        "Connection: close",
    ]
    headers = CRLF.join(header_lines).encode("ascii")
    return headers + CRLF.encode("ascii") + CRLF.encode("ascii") + body


def build_file_response(body: bytes, content_type: str) -> bytes:
    return build_response(
        status_code=200,
        reason=STATUS_REASONS[200],
        content_type=content_type,
        body=body,
    )


def build_error_response(status_code: int) -> bytes:
    reason = STATUS_REASONS.get(status_code)
    details = ERROR_DETAILS.get(status_code)
    if reason is None or details is None:
        raise ValueError(f"unsupported error status code: {status_code}")

    body = _error_page_html(status_code, reason, details).encode("utf-8")
    return build_response(
        status_code=status_code,
        reason=reason,
        content_type=ERROR_CONTENT_TYPE,
        body=body,
    )


def _error_page_html(
    status_code: int,
    reason: str,
    details: tuple[str, str, str, str],
) -> str:
    challenge_title, explanation, mission, example = details
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{status_code} {reason} - Computer Networks Academy</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172033;
      --muted: #526070;
      --line: #c9d4e5;
      --panel: #ffffff;
      --stage: #eef4fb;
      --accent: #0f766e;
      --accent-strong: #115e59;
      --warning: #b45309;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 32px 16px;
      background: var(--stage);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.5;
    }}
    main {{
      width: min(780px, 100%);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 28px;
      box-shadow: 0 16px 40px rgba(23, 32, 51, 0.12);
    }}
    .academy {{
      margin: 0 0 10px;
      color: var(--accent-strong);
      font-size: 0.85rem;
      font-weight: 700;
      letter-spacing: 0;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2rem, 5vw, 3.5rem);
      line-height: 1.05;
    }}
    .summary {{
      max-width: 62ch;
      margin: 16px 0 24px;
      color: var(--muted);
      font-size: 1.05rem;
    }}
    .challenge {{
      display: grid;
      gap: 16px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #f8fbff;
    }}
    .challenge h2 {{
      margin: 0;
      font-size: 1.2rem;
    }}
    .packet {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }}
    .packet span {{
      min-width: 0;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #ffffff;
      text-align: center;
      font-family: Consolas, Monaco, monospace;
      font-size: 0.92rem;
      overflow-wrap: anywhere;
    }}
    code {{
      display: block;
      padding: 12px;
      border-left: 4px solid var(--accent);
      background: #ecfdf5;
      color: #064e3b;
      font-family: Consolas, Monaco, monospace;
      overflow-wrap: anywhere;
    }}
    a {{
      display: inline-block;
      margin-top: 22px;
      color: var(--accent-strong);
      font-weight: 700;
      text-decoration: none;
    }}
    a:hover {{ text-decoration: underline; }}
    .hint {{
      margin: 0;
      color: var(--warning);
      font-weight: 700;
    }}
    @media (max-width: 560px) {{
      main {{ padding: 22px; }}
      .packet {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <p class="academy">Computer Networks Academy</p>
    <h1>{status_code} {reason}</h1>
    <p class="summary">{explanation}</p>
    <section class="challenge" aria-labelledby="challenge-title">
      <h2 id="challenge-title">{challenge_title}</h2>
      <p>{mission}</p>
      <div class="packet" aria-label="HTTP request-line parts">
        <span>METHOD</span>
        <span>PATH</span>
        <span>VERSION</span>
      </div>
      <p class="hint">Try this shape:</p>
      <code>{example}</code>
    </section>
    <a href="/">Return to the academy home page</a>
  </main>
</body>
</html>
"""
