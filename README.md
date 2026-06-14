# Computer Networks HTTP/1.0 Static Web Server

This repository contains a Computer Networks programming assignment project: a multi-threaded HTTP/1.0 static web server written from scratch in Python.

The goal is to demonstrate low-level TCP socket programming, manual HTTP request parsing, manual HTTP response construction, safe static file serving, directory traversal protection, stateless request handling, and one-thread-per-client concurrency.

Demo video: TODO: add demo video link

## What The Server Does

- Listens on a configurable host and port.
- Accepts TCP client connections with `socket.socket`.
- Starts one thread for each accepted client connection.
- Reads request bytes until the HTTP header terminator `\r\n\r\n`.
- Parses the HTTP request line manually.
- Serves static files from the configured `cna/` root.
- Supports only `GET` for static files.
- Builds HTTP/1.0 responses manually as bytes.
- Includes `Content-Length`, `Content-Type`, and `Connection: close` in every response.
- Returns generated HTML error pages for `400`, `403`, `404`, and `405`.
- Closes each client connection after one response.

## Architecture Overview

The project is split into small modules:

- `server.py` owns command-line parsing, socket setup, accept loop, threads, request handling, and shutdown.
- `http_parser.py` parses decoded HTTP request lines into structured request data.
- `security.py` URL-decodes and validates paths, blocks traversal, and enforces allowed directories.
- `mime_utils.py` resolves MIME types with Python's standard-library `mimetypes` module.
- `response_builder.py` builds raw HTTP/1.0 response bytes and generated error pages.
- `logger.py` prints request logs with timestamp, client address, request line, status, and byte count.
- `tests/test_server.py` starts the server as a subprocess and verifies behavior using standard-library clients.
- `cna/` contains the static Computer Networks Academy frontend.

## File Structure

```text
computer-network/
├── README.md
├── CONTEXT_ENGINEERING.md
├── HARNESS_ENGINEERING.md
├── PROJECT_GENERATION_PROMPT.md
├── AGENTS.md
├── server.py
├── http_parser.py
├── response_builder.py
├── security.py
├── mime_utils.py
├── logger.py
├── tests/
│   └── test_server.py
└── cna/
    ├── public/
    │   ├── index.html
    │   ├── academy.html
    │   ├── status-codes.html
    │   ├── concurrency.html
    │   └── app.js
    ├── css/
    │   ├── style.css
    │   └── game.css
    └── images/
        ├── network-map.svg
        └── http-flow.svg
```

## Requirements

- Python 3.14
- Windows PowerShell for the documented commands
- No external Python packages
- No Flask, FastAPI, Django, `http.server`, `socketserver`, `aiohttp`, `uvicorn`, `gunicorn`, or other server frameworks
- Static frontend only: HTML, CSS, SVG, and plain JavaScript

## Run On Windows PowerShell

Default command:

```powershell
python server.py
```

Explicit command:

```powershell
python server.py --host 127.0.0.1 --port 8081 --root cna
```

Expected startup message:

```text
Serving cna on http://127.0.0.1:8081
Press Ctrl+C to stop.
```

Stop the server with `Ctrl+C`.

## Command-Line Options

| Option | Default | Description |
|---|---:|---|
| `--host` | `127.0.0.1` | Address to bind the listening socket to |
| `--port` | `8081` | TCP port to listen on |
| `--root` | `cna` | Static file root directory |

## Supported Routes

| URL path | Served file |
|---|---|
| `/` | `cna/public/index.html` |
| `/public/index.html` | `cna/public/index.html` |
| `/public/academy.html` | `cna/public/academy.html` |
| `/public/status-codes.html` | `cna/public/status-codes.html` |
| `/public/concurrency.html` | `cna/public/concurrency.html` |
| `/public/app.js` | `cna/public/app.js` |
| `/css/style.css` | `cna/css/style.css` |
| `/css/game.css` | `cna/css/game.css` |
| `/images/network-map.svg` | `cna/images/network-map.svg` |
| `/images/http-flow.svg` | `cna/images/http-flow.svg` |

Allowed URL directory roots:

- `/`
- `/public`
- `/css`
- `/images`

Directory paths such as `/public/` do not generate directory listings. They return `404 Not Found`.

## Status-Code Behavior

| Status | When it is returned |
|---|---|
| `200 OK` | Existing file in an allowed static directory |
| `400 Bad Request` | Malformed request syntax or decoded directory traversal |
| `403 Forbidden` | Valid path syntax targeting a blocked directory root |
| `404 Not Found` | Missing files in allowed directories, or directory paths other than `/` |
| `405 Method Not Allowed` | Any syntactically valid non-GET method |

## Static Frontend

The frontend is named Computer Networks Academy. It is a local-only static site with no build step, no npm, no CDN, and no backend API calls.

Pages include:

- Home page explaining the custom socket server and proving HTML/CSS/JS/SVG serving.
- Academy page explaining TCP socket lifecycle and HTTP request/response flow.
- Status-code page with a small status-code challenge.
- Concurrency page with the main client-side simulator.

The Concurrency Simulator visually shows several clients opening TCP connections, sending HTTP requests, being handled by server threads, and receiving HTTP/1.0 responses. This simulator is educational and client-side only; real server concurrency is verified by the automated test harness.

## Concurrency Model

The server uses one Python thread per accepted client connection.

Each worker thread:

1. Sets a client timeout.
2. Reads the request header until `\r\n\r\n`.
3. Parses and validates the request.
4. Sends exactly one response.
5. Closes the connection.

The server does not implement persistent connections, sessions, cookies, shared user state, databases, templates, or backend APIs.

## Security Behavior

The server serves files only from the configured static root, normally `cna/`.

Path safety rules:

- URL paths are decoded with `urllib.parse.unquote`.
- Traversal is checked after decoding.
- Paths containing traversal attempts such as `..` are rejected with `400 Bad Request`.
- Normalized filesystem paths must remain inside the static root.
- Blocked directory roots such as `/private` return `403 Forbidden`.
- Missing allowed files return `404 Not Found`.

Example:

```text
GET /public/%2e%2e/%2e%2e/etc/passwd HTTP/1.0
```

This is decoded before validation and rejected as `400 Bad Request`.

## Automated Tests

Run the automated harness from the repository root:

```powershell
python -m unittest tests.test_server -v
```

The test file starts the server as a subprocess on `127.0.0.1` using a free test port, waits for readiness, runs the checks, and shuts the subprocess down.

The automated suite was run successfully in this workspace with:

```powershell
python -B -m unittest tests.test_server -v
```

Result:

```text
Ran 13 tests

OK
```

## Manual Curl Verification

Start the server first:

```powershell
python server.py --host 127.0.0.1 --port 8081 --root cna
```

Successful file:

```powershell
curl.exe -v http://localhost:8081/public/index.html
```

Root route:

```powershell
curl.exe -v http://localhost:8081/
```

Missing file:

```powershell
curl.exe -v http://localhost:8081/public/missing.html
```

Blocked directory:

```powershell
curl.exe -v http://localhost:8081/private/secret.txt
```

Non-GET method:

```powershell
curl.exe -v -X POST http://localhost:8081/public/index.html
```

Traversal attempts are best verified with raw sockets because browsers and curl may normalize paths before sending them. The automated test harness sends this exact raw request:

```http
GET /../../etc/passwd HTTP/1.0
Host: localhost
```

Expected response: `HTTP/1.0 400 Bad Request`.

## Browser Demo URLs

Open these while the server is running:

- `http://localhost:8081/`
- `http://localhost:8081/public/index.html`
- `http://localhost:8081/public/academy.html`
- `http://localhost:8081/public/status-codes.html`
- `http://localhost:8081/public/concurrency.html`
- `http://localhost:8081/css/style.css`
- `http://localhost:8081/public/app.js`
- `http://localhost:8081/images/network-map.svg`

## Known Limitations

- Supports only static `GET` file serving.
- Does not implement HTTP request bodies.
- Does not implement persistent connections or keep-alive.
- Does not implement directory indexes.
- Does not implement HTTPS/TLS.
- Does not implement routing engines, templates, cookies, sessions, authentication, databases, or backend APIs.
- The frontend simulator is a visual teaching tool, not a live measurement of server threads.
- Error pages are generated by the server and use inline styling rather than shared CSS files.

## Grading Checklist

| Assignment requirement | Project evidence |
|---|---|
| Use raw TCP sockets | `server.py` uses `socket.socket`, `bind`, `listen`, `accept`, `recv`, `sendall`, and `close` |
| No high-level web framework/server | No Flask, FastAPI, Django, `http.server`, `socketserver`, or similar libraries |
| Manual HTTP parsing | `http_parser.py` parses the request line into method, path, and version |
| Dynamic header buffering | `server.py` reads until `\r\n\r\n` and does not assume one `recv()` call |
| Maximum header size | `server.py` enforces a `16384` byte header limit |
| Client timeout | `server.py` sets a 10 second client socket timeout |
| HTTP/1.0 responses | `response_builder.py` writes `HTTP/1.0 <code> <reason>` status lines |
| Required response headers | Responses include `Content-Length`, `Content-Type`, and `Connection: close` |
| Static root only | `security.py` resolves files under the configured `cna/` root |
| Allowed directories only | `/`, `/public`, `/css`, and `/images` are allowed roots |
| Root route | `/` maps to `cna/public/index.html` |
| Directory traversal blocked | Decoded traversal attempts return `400 Bad Request` |
| Blocked subdirectories | Paths such as `/private/secret.txt` return `403 Forbidden` |
| Missing files | Missing allowed files return `404 Not Found` |
| Non-GET methods | Valid non-GET request lines return `405 Method Not Allowed` |
| Static frontend | `cna/` contains HTML, CSS, JavaScript, and SVG files |
| Concurrency | Server starts one thread per accepted client connection |
| 25 concurrent clients | Covered by `tests/test_server.py` |
| Partial-read behavior | Covered by `tests/test_server.py` |
| Standard library only | Server and tests use Python standard-library modules |
| Demo video placeholder | `TODO: add demo video link` is included above |
