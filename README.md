# Computer Networks HTTP/1.0 Static Web Server

Computer Networks HTTP/1.0 Static Web Server is a multi-threaded static web server written from scratch in Python.

The project demonstrates how a web server transforms raw bytes received over a TCP socket into HTTP request data, validates the requested path, reads static files from disk, and returns manually constructed HTTP/1.0 responses.

The main purpose of this project is to apply core Computer Networks course concepts in code:

* TCP socket lifecycle
* process-to-process communication through ports
* HTTP request parsing
* HTTP response formatting
* static file serving
* directory traversal protection
* stateless request handling
* concurrent client handling

The server uses Python's low-level `socket` API directly. It does not use Flask, FastAPI, Django, `http.server`, `socketserver`, or any other web framework or high-level server library.

---

## Table of Contents

* [Project Overview](#project-overview)
* [Course Concepts Demonstrated](#course-concepts-demonstrated)
* [Main Features](#main-features)
* [Tech Stack](#tech-stack)
* [Project Structure](#project-structure)
* [Architecture](#architecture)
* [HTTP Behavior](#http-behavior)
* [Supported Routes](#supported-routes)
* [Status Codes](#status-codes)
* [Security Rules](#security-rules)
* [Concurrency Model](#concurrency-model)
* [Static Frontend](#static-frontend)
* [Installation and Setup](#installation-and-setup)
* [Running the Server](#running-the-server)
* [Usage Flow](#usage-flow)
* [Automated Tests](#automated-tests)
* [Manual Testing](#manual-testing)
* [Browser and DevTools Verification](#browser-and-devtools-verification)
* [Demo Checklist](#demo-checklist)
* [Known Limitations](#known-limitations)
* [Recommended Git Ignore Rules](#recommended-git-ignore-rules)
* [Future Improvements](#future-improvements)
* [Author](#author)

---

## Project Overview

This project implements a functional HTTP/1.0 static web server.

When a client connects, the server:

1. Accepts a TCP connection.
2. Starts a worker thread for that client.
3. Reads raw bytes from the socket.
4. Buffers incoming data until the HTTP header terminator `\r\n\r\n` is found.
5. Parses the HTTP request line.
6. Validates the requested method, path, and HTTP version.
7. Maps the URL path to a static file under the configured root directory.
8. Prevents directory traversal and blocked-directory access.
9. Builds an HTTP/1.0 response manually.
10. Sends the response bytes to the client.
11. Closes the connection.

The server is intentionally simple and stateless. It serves static files only and does not implement application routing, sessions, cookies, authentication, databases, templates, or backend APIs.

---

## Demo Video

Demo video:

```txt
TODO: add demo video link
```

---

## Course Concepts Demonstrated

This project connects directly to the course's application-layer and transport-layer topics.

### Application Layer

The server manually implements the application-layer behavior of HTTP.

It defines and handles:

* request-line parsing
* HTTP methods
* URL paths
* HTTP versions
* response status lines
* response headers
* MIME types
* response bodies
* status-code semantics

The project focuses on HTTP as a text-based request-response protocol.

### Client-Server Model

The project follows a classic client-server architecture.

* The browser, curl, or test harness acts as the client.
* The Python program acts as the server.
* The client initiates communication.
* The server listens on a host and port.
* The server accepts incoming connections and replies to requests.

### Transport Layer

The server uses TCP sockets.

TCP provides reliable, ordered byte delivery. The server does not manually implement TCP sequence numbers, acknowledgements, retransmissions, flow control, or congestion control. Those mechanisms are handled by the operating system and TCP stack.

The application code receives the TCP byte stream and interprets it as HTTP.

### Process-to-Process Communication

The server binds to a host and port. Clients connect to that socket endpoint.

Example:

```txt
127.0.0.1:8081
```

The IP address identifies the host. The port identifies the server process.

### HTTP Statelessness

Each request is handled independently.

The server does not remember previous clients and does not maintain session state between requests.

### Layer Separation

This project focuses on the application layer above TCP sockets.

The server does not manually implement:

* DNS
* IP routing
* ARP
* Ethernet framing
* physical-layer transmission
* TCP reliability internals

Those lower-layer responsibilities are handled by the operating system and network stack.

---

## Main Features

### Low-Level Socket Server

* Uses Python's standard-library `socket` module.
* Creates a TCP socket manually.
* Binds to a configurable host and port.
* Listens for incoming connections.
* Accepts client sockets.
* Sends and receives raw bytes.
* Closes each client connection after one response.

### Manual HTTP Parsing

* Reads HTTP request bytes from the socket.
* Buffers dynamically until `\r\n\r\n`.
* Does not assume the full header arrives in one `recv()` call.
* Decodes the request as ASCII-compatible HTTP text.
* Parses the request line into:

```txt
METHOD PATH VERSION
```

Example:

```http
GET /public/index.html HTTP/1.0
```

### Static File Serving

* Serves static files from the configured `cna/` root.
* Supports HTML, CSS, JavaScript, and SVG files.
* Uses MIME type detection.
* Sends file bytes as the response body.
* Includes `Content-Length`.
* Includes `Content-Type`.
* Includes `Connection: close`.

### Security Protection

* Blocks directory traversal attempts.
* Decodes URL paths before validation.
* Rejects paths containing `..`.
* Ensures resolved file paths remain inside the static root.
* Allows only specific public URL roots.
* Blocks access to unsupported directory roots.

### Error Handling

The server returns generated HTML error pages for:

* `400 Bad Request`
* `403 Forbidden`
* `404 Not Found`
* `405 Method Not Allowed`

### Concurrency

* Uses one Python thread per accepted client connection.
* Allows multiple clients to be handled simultaneously.
* Prevents one slow client from blocking all other clients.
* Includes automated tests for concurrent requests.

### Frontend

The static frontend is named Computer Networks Academy.

It includes:

* home page
* academy page
* status-code challenge page
* concurrency simulator page
* dark mode by default
* light/dark theme toggle in the navbar
* responsive layout
* HTML, CSS, JavaScript, and SVG assets

---

## Tech Stack

### Backend

* Python 3.14
* Python standard library only
* `socket`
* `threading`
* `pathlib`
* `urllib.parse`
* `mimetypes`
* `argparse`
* `datetime`

### Frontend

* HTML
* CSS
* Plain JavaScript
* SVG images
* No npm
* No build step
* No external CDN
* No frontend framework

### Testing

* Python `unittest`
* Python `socket`
* Python `http.client`
* Python `subprocess`
* Browser manual testing
* `curl.exe -v`

### Development Tools

* Windows PowerShell
* VS Code
* Git
* Browser Developer Tools

---

## Project Structure

```txt
computer-network/
├── README.md
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

---

## Architecture

The project is split into small modules.

### `server.py`

Owns the main server lifecycle.

Responsibilities:

* parse command-line arguments
* create the listening socket
* bind host and port
* listen for incoming TCP clients
* accept client connections
* create one thread per client
* read request bytes
* send response bytes
* close client sockets
* handle shutdown

### `http_parser.py`

Parses HTTP request data.

Responsibilities:

* validate the request line
* extract method
* extract path
* extract HTTP version
* reject malformed request syntax

### `security.py`

Validates and resolves requested URL paths.

Responsibilities:

* URL-decode paths
* reject traversal attempts
* map `/` to the homepage
* enforce allowed directory roots
* block unsupported directory roots
* resolve safe filesystem paths under the static root

### `mime_utils.py`

Resolves content types for static files.

Examples:

```txt
.html -> text/html
.css  -> text/css
.js   -> application/javascript
.svg  -> image/svg+xml
```

### `response_builder.py`

Builds HTTP/1.0 response bytes.

Responsibilities:

* construct status line
* construct headers
* include blank CRLF separator
* attach body bytes
* generate HTML error pages

### `logger.py`

Prints request logs.

A log entry includes:

* timestamp
* client address
* request line
* status code
* byte count

### `tests/test_server.py`

Runs automated verification.

Responsibilities:

* start server as a subprocess
* wait for readiness
* send normal HTTP requests
* send raw malformed requests
* test partial header reads
* test traversal blocking
* test blocked directories
* test missing files
* test unsupported methods
* test concurrent clients
* shut down the test server

---

## HTTP Behavior

### Request Format

The server expects the HTTP request to begin with a request line:

```http
GET /public/index.html HTTP/1.0
```

The request line contains:

```txt
METHOD PATH VERSION
```

The server reads until the header terminator:

```txt
\r\n\r\n
```

This is important because TCP is a byte stream. The server cannot assume that a full HTTP header arrives in a single `recv()` call.

### Response Format

The server manually builds an HTTP response with this structure:

```http
HTTP/1.0 200 OK
Content-Length: 1234
Content-Type: text/html
Connection: close

<body bytes>
```

Every response includes:

* status line
* `Content-Length`
* `Content-Type`
* `Connection: close`
* blank line
* body bytes

### HTTP Version

The server returns HTTP/1.0 responses.

The server closes the connection after sending one response.

This matches HTTP/1.0-style non-persistent behavior. It does not implement HTTP/1.1 keep-alive or pipelining.

---

## Supported Routes

| URL path                    | Served file                    |
| --------------------------- | ------------------------------ |
| `/`                         | `cna/public/index.html`        |
| `/index.html`               | `cna/public/index.html`        |
| `/public/index.html`        | `cna/public/index.html`        |
| `/public/academy.html`      | `cna/public/academy.html`      |
| `/public/status-codes.html` | `cna/public/status-codes.html` |
| `/public/concurrency.html`  | `cna/public/concurrency.html`  |
| `/public/app.js`            | `cna/public/app.js`            |
| `/css/style.css`            | `cna/css/style.css`            |
| `/css/game.css`             | `cna/css/game.css`             |
| `/images/network-map.svg`   | `cna/images/network-map.svg`   |
| `/images/http-flow.svg`     | `cna/images/http-flow.svg`     |

Allowed URL directory roots:

```txt
/
 /public
 /css
 /images
```

Directory paths such as `/public/` do not generate directory listings. They return `404 Not Found`.

---

## Status Codes

| Status                   | Meaning            | When it is returned                                  |
| ------------------------ | ------------------ | ---------------------------------------------------- |
| `200 OK`                 | Success            | Existing file in an allowed static directory         |
| `400 Bad Request`        | Invalid request    | Malformed syntax or decoded traversal attempt        |
| `403 Forbidden`          | Blocked path       | Valid path syntax targeting a blocked directory root |
| `404 Not Found`          | Missing resource   | Missing file in an allowed directory                 |
| `405 Method Not Allowed` | Unsupported method | Valid request line using a method other than `GET`   |

---

## Security Rules

The server serves files only from the configured static root.

Default root:

```txt
cna
```

Path safety rules:

* URL paths are decoded before validation.
* Paths containing traversal attempts such as `..` are rejected.
* Normalized filesystem paths must remain inside the static root.
* Only selected URL roots are allowed.
* Blocked directory roots return `403 Forbidden`.
* Missing allowed files return `404 Not Found`.

Traversal example:

```http
GET /public/%2e%2e/%2e%2e/etc/passwd HTTP/1.0
Host: localhost
```

Expected result:

```txt
HTTP/1.0 400 Bad Request
```

The path is decoded before validation, so encoded traversal is still rejected.

---

## Concurrency Model

The server uses one Python thread per accepted client connection.

Each worker thread:

1. Receives a client socket.
2. Sets a client timeout.
3. Reads request bytes until `\r\n\r\n`.
4. Parses the HTTP request.
5. Validates the path.
6. Builds one HTTP response.
7. Sends the response.
8. Closes the client socket.

This allows multiple clients to be processed at the same time.

The server does not use:

* thread pools
* async I/O
* event loops
* persistent connections

The chosen model is simple and directly demonstrates multi-threaded server behavior.

---

## Static Frontend

The frontend is named Computer Networks Academy.

It is a local static site served by the Python socket server.

Pages include:

* Home page explaining the custom HTTP server.
* Academy page explaining TCP socket lifecycle and HTTP request-response flow.
* Status-code page with an interactive status-code challenge.
* Concurrency page with a visual client/server/thread simulator.

The frontend uses dark mode by default and includes a navbar toggle for switching between dark and light themes.

The Concurrency Simulator visually shows several clients opening TCP connections, sending HTTP requests, being handled by server threads, and receiving HTTP/1.0 responses.

The simulator is an educational client-side visualization. It is not a live measurement of actual Python threads. Real server concurrency is verified by the automated test harness.

---

## Installation and Setup

### 1. Clone or open the project

```powershell
cd C:\path\to\computer-network
```

### 2. Verify Python

```powershell
python --version
```

Expected:

```txt
Python 3.14.x
```

### 3. Confirm there are no required external packages

The project uses the Python standard library only.

No installation command is required.

Do not install Flask, FastAPI, Django, or other web frameworks for this project.

---

## Running the Server

### Default command

```powershell
python server.py
```

### Explicit command

```powershell
python server.py --host 127.0.0.1 --port 8081 --root cna
```

Expected output:

```txt
Serving cna on http://127.0.0.1:8081
Press Ctrl+C to stop.
```

Server URL:

```txt
http://127.0.0.1:8081
```

Stop the server with:

```txt
Ctrl+C
```

---

## Command-Line Options

| Option   |     Default | Description                             |
| -------- | ----------: | --------------------------------------- |
| `--host` | `127.0.0.1` | Address to bind the listening socket to |
| `--port` |      `8081` | TCP port to listen on                   |
| `--root` |       `cna` | Static file root directory              |

Example:

```powershell
python server.py --host 127.0.0.1 --port 8081 --root cna
```

---

## Usage Flow

1. Start the server from the project root.
2. Open a browser.
3. Navigate to `http://localhost:8081/`.
4. Open the Academy page.
5. Open the Status Codes page.
6. Open the Concurrency page.
7. Run the visual simulator.
8. Use the theme toggle to test dark and light mode.
9. Open browser Developer Tools.
10. Inspect the Network tab.
11. Confirm that HTML, CSS, JavaScript, and SVG files are served separately.
12. Use `curl.exe -v` to inspect raw response headers.
13. Run the automated test suite.

---

## Automated Tests

Run the automated test harness from the repository root:

```powershell
python -m unittest tests.test_server -v
```

The test file starts the server as a subprocess on `127.0.0.1` using a free test port, waits for readiness, runs checks, and shuts the subprocess down.

The automated test suite verifies:

* homepage response
* static HTML serving
* CSS serving
* JavaScript serving
* SVG serving
* missing file behavior
* blocked directory behavior
* directory traversal blocking
* malformed request handling
* non-GET method handling
* partial-read behavior
* concurrent clients
* required response headers

Expected result:

```txt
Ran 13 tests

OK
```

---

## Manual Testing

Start the server first:

```powershell
python server.py --host 127.0.0.1 --port 8081 --root cna
```

### Root route

```powershell
curl.exe -v http://localhost:8081/
```

Expected:

```txt
HTTP/1.0 200 OK
```

### Index route

```powershell
curl.exe -v http://localhost:8081/index.html
```

Expected:

```txt
HTTP/1.0 200 OK
```

### Static HTML file

```powershell
curl.exe -v http://localhost:8081/public/index.html
```

Expected:

```txt
HTTP/1.0 200 OK
Content-Type: text/html
```

### CSS file

```powershell
curl.exe -v http://localhost:8081/css/style.css
```

Expected:

```txt
HTTP/1.0 200 OK
Content-Type: text/css
```

### JavaScript file

```powershell
curl.exe -v http://localhost:8081/public/app.js
```

Expected:

```txt
HTTP/1.0 200 OK
```

### SVG image

```powershell
curl.exe -v http://localhost:8081/images/network-map.svg
```

Expected:

```txt
HTTP/1.0 200 OK
Content-Type: image/svg+xml
```

### Missing file

```powershell
curl.exe -v http://localhost:8081/public/missing.html
```

Expected:

```txt
HTTP/1.0 404 Not Found
```

### Blocked directory

```powershell
curl.exe -v http://localhost:8081/private/secret.txt
```

Expected:

```txt
HTTP/1.0 403 Forbidden
```

### Unsupported method

```powershell
curl.exe -v -X POST http://localhost:8081/public/index.html
```

Expected:

```txt
HTTP/1.0 405 Method Not Allowed
```

---

## Raw Socket Testing

Some invalid paths are best tested with raw sockets because browsers and curl may normalize paths before sending them.

The automated test harness sends raw requests such as:

```http
GET /../../etc/passwd HTTP/1.0
Host: localhost

```

Expected response:

```txt
HTTP/1.0 400 Bad Request
```

This confirms that traversal attempts are rejected by the server.

---

## Browser and DevTools Verification

Open these pages while the server is running:

```txt
http://localhost:8081/
http://localhost:8081/index.html
http://localhost:8081/public/index.html
http://localhost:8081/public/academy.html
http://localhost:8081/public/status-codes.html
http://localhost:8081/public/concurrency.html
```

To inspect HTTP behavior:

1. Open Developer Tools.
2. Go to the Network tab.
3. Reload the page.
4. Click a request.
5. Check the method.
6. Check the status code.
7. Check response headers.
8. Confirm `Content-Length`.
9. Confirm `Content-Type`.
10. Confirm that CSS, JavaScript, and SVG files are loaded as separate static resources.

---

## Demo Checklist

Before recording or presenting the project, verify:

* Server starts successfully.
* Browser can load the home page.
* `/index.html` loads the same home page.
* Static HTML files load.
* CSS file loads.
* JavaScript file loads.
* SVG images load.
* Dark mode is the default.
* Theme toggle switches between dark and light mode.
* Academy page explains the server behavior.
* Status-code challenge works.
* Concurrency simulator runs visually.
* Explanation panel appears after the simulator completes.
* `curl.exe -v` shows valid HTTP/1.0 response headers.
* Missing file returns `404 Not Found`.
* Blocked directory returns `403 Forbidden`.
* Traversal attempt returns `400 Bad Request`.
* Unsupported method returns `405 Method Not Allowed`.
* Automated tests pass.
* Server terminal shows request logs.
* Demo video link is added to this README before submission.

## Known Limitations

The project intentionally does not implement:

* HTTP request bodies
* dynamic backend routes
* templates
* databases
* authentication
* cookies
* sessions
* persistent connections
* HTTP keep-alive
* HTTP pipelining
* HTTP/2
* HTTPS/TLS
* WebSockets
* directory listings
* file uploads
* CDN caching
* compression
* range requests
* production-grade logging
* production-grade security hardening

The frontend simulator is a visual teaching tool, not a live measurement of server threads.

The server is designed for local course demonstration, not for public internet deployment.

---

## Assignment Compliance Checklist

| Assignment requirement         | Project evidence                                                            |
| ------------------------------ | --------------------------------------------------------------------------- |
| Use low-level networking API   | `server.py` uses Python's `socket` module directly                          |
| No high-level web framework    | No Flask, FastAPI, Django, `http.server`, `socketserver`, or routing engine |
| Socket initialization          | Server binds to a host and port and listens for TCP connections             |
| Accept TCP clients             | Server accepts incoming client sockets                                      |
| Robust stream reading          | Server buffers bytes until `\r\n\r\n`                                       |
| No single-recv assumption      | Partial header behavior is covered by automated tests                       |
| Manual HTTP parsing            | `http_parser.py` parses method, path, and version                           |
| Serve static files             | Files are served from the configured `cna/` root                            |
| GET only                       | Non-GET methods return `405 Method Not Allowed`                             |
| Static files in subdirectories | HTML, CSS, JS, and SVG files exist under `public`, `css`, and `images`      |
| Allowed subdirectories         | `/`, `/public`, `/css`, and `/images` are allowed                           |
| Block other subdirectories     | Paths such as `/private/secret.txt` return `403 Forbidden`                  |
| Directory traversal prevention | Decoded traversal attempts return `400 Bad Request`                         |
| Valid HTTP response format     | Responses include status line, headers, blank line, and body                |
| Content-Length header          | Included in responses                                                       |
| Content-Type header            | Included in responses                                                       |
| 200 OK                         | Returned for existing allowed files                                         |
| 400 Bad Request                | Returned for malformed syntax and traversal attempts                        |
| 404 Not Found                  | Returned for missing allowed files                                          |
| Stateless execution            | No persistent connections, cookies, or session memory                       |
| Concurrency                    | Server starts one thread per accepted client connection                     |
| Concurrent verification        | `tests/test_server.py` covers 25 concurrent clients                         |
| Browser verification           | Static frontend can be loaded in Chrome or Firefox                          |
| curl verification              | Manual `curl.exe -v` commands are documented                                |
| DevTools verification          | README documents Network tab inspection                                     |
| Demo video                     | Link must be added before submission                                        |

---

## Build and Syntax Checks

### Python syntax check

Run:

```powershell
python -m py_compile server.py http_parser.py response_builder.py security.py mime_utils.py logger.py tests/test_server.py
```

Expected result:

```txt
No output
```

No output means the files passed syntax checking.

### Automated test check

Run:

```powershell
python -m unittest tests.test_server -v
```

Expected result:

```txt
OK
```

---

## Recommended Git Ignore Rules

Root `.gitignore` should include:

```gitignore
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/
.env
.DS_Store
Thumbs.db
.vscode/
```

If submitting a ZIP file, avoid including:

```txt
.git/
__pycache__/
.pytest_cache/
```

A clean ZIP can be created from Git with:

```powershell
git archive --format=zip --output computer-network-clean.zip HEAD
```

---

## Future Improvements

Possible future improvements include:

* add a thread pool option
* add request header parsing beyond the request line
* add `HEAD` method support
* add access-log file output
* add configurable allowed directory roots
* add configurable timeout and max header size
* add more MIME type tests
* add a small benchmark script
* add a richer DevTools walkthrough page
* add optional HTTP/1.1 keep-alive as a separate learning extension
* add optional HTTPS through a reverse proxy for demonstration

These improvements are intentionally outside the current assignment scope.

---

## Author

This project was built as a Computer Networks programming assignment.

The project focuses on practical understanding of HTTP, TCP sockets, static file serving, request parsing, response formatting, security validation, and concurrent client handling.
