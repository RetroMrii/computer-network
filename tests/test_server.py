"""Automated harness for the raw-socket HTTP server."""

from __future__ import annotations

import concurrent.futures
import http.client
import os
from dataclasses import dataclass
from pathlib import Path
import socket
import subprocess
import sys
import time
import unittest


HOST = "127.0.0.1"
SERVER_READY_TIMEOUT = 8.0
CLIENT_TIMEOUT = 5.0


@dataclass(frozen=True)
class HttpResult:
    status: int
    reason: str
    headers: dict[str, str]
    body: bytes


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, 0))
        return int(sock.getsockname()[1])


def raw_http_request(port: int, payload: bytes) -> bytes:
    with socket.create_connection((HOST, port), timeout=CLIENT_TIMEOUT) as sock:
        sock.settimeout(CLIENT_TIMEOUT)
        sock.sendall(payload)
        chunks: list[bytes] = []
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)


def split_headers_and_body(response: bytes) -> tuple[bytes, bytes]:
    return response.split(b"\r\n\r\n", 1)


def parse_status_line(response: bytes) -> tuple[str, int, str]:
    status_line = response.split(b"\r\n", 1)[0].decode("iso-8859-1")
    version, code, reason = status_line.split(" ", 2)
    return version, int(code), reason


def parse_headers(response: bytes) -> dict[str, str]:
    header_bytes, _body = split_headers_and_body(response)
    lines = header_bytes.decode("iso-8859-1").split("\r\n")[1:]
    headers: dict[str, str] = {}
    for line in lines:
        name, value = line.split(":", 1)
        headers[name.lower()] = value.strip()
    return headers


class WebServerHarnessTests(unittest.TestCase):
    server_process: subprocess.Popen[bytes]
    port: int
    repo_root: Path

    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.port = find_free_port()
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"
        cls.server_process = subprocess.Popen(
            [
                sys.executable,
                "-B",
                "server.py",
                "--host",
                HOST,
                "--port",
                str(cls.port),
                "--root",
                "cna",
            ],
            cwd=cls.repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
        cls._wait_for_server()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.server_process.poll() is None:
            cls.server_process.terminate()
            try:
                cls.server_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                cls.server_process.kill()
                cls.server_process.wait(timeout=3)

    @classmethod
    def _wait_for_server(cls) -> None:
        deadline = time.time() + SERVER_READY_TIMEOUT
        while time.time() < deadline:
            if cls.server_process.poll() is not None:
                raise RuntimeError("server process exited before accepting connections")
            try:
                with socket.create_connection((HOST, cls.port), timeout=0.25):
                    return
            except OSError:
                time.sleep(0.05)
        raise RuntimeError("server did not start before timeout")

    def http_request(self, method: str, path: str) -> HttpResult:
        connection = http.client.HTTPConnection(HOST, self.port, timeout=CLIENT_TIMEOUT)
        try:
            connection.request(method, path)
            response = connection.getresponse()
            body = response.read()
            return HttpResult(
                status=response.status,
                reason=response.reason,
                headers={name.lower(): value for name, value in response.getheaders()},
                body=body,
            )
        finally:
            connection.close()

    def assert_required_headers(self, result: HttpResult) -> None:
        self.assertIn("content-length", result.headers)
        self.assertIn("content-type", result.headers)
        self.assertEqual(int(result.headers["content-length"]), len(result.body))

    def test_root_returns_200(self) -> None:
        result = self.http_request("GET", "/")
        self.assertEqual(result.status, 200)
        self.assertEqual(result.reason, "OK")
        self.assertIn(b"Computer Networks Academy", result.body)
        self.assert_required_headers(result)

    def test_public_index_returns_200(self) -> None:
        result = self.http_request("GET", "/public/index.html")
        self.assertEqual(result.status, 200)
        self.assertEqual(result.reason, "OK")
        self.assertIn("text/html", result.headers["content-type"])
        self.assert_required_headers(result)

    def test_css_returns_200(self) -> None:
        result = self.http_request("GET", "/css/style.css")
        self.assertEqual(result.status, 200)
        self.assertEqual(result.reason, "OK")
        self.assertIn("text/css", result.headers["content-type"])
        self.assert_required_headers(result)

    def test_svg_returns_200(self) -> None:
        result = self.http_request("GET", "/images/network-map.svg")
        self.assertEqual(result.status, 200)
        self.assertEqual(result.reason, "OK")
        self.assertIn("image/svg+xml", result.headers["content-type"])
        self.assert_required_headers(result)

    def test_missing_file_returns_404(self) -> None:
        result = self.http_request("GET", "/public/missing.html")
        self.assertEqual(result.status, 404)
        self.assertEqual(result.reason, "Not Found")
        self.assert_required_headers(result)

    def test_blocked_directory_returns_403(self) -> None:
        result = self.http_request("GET", "/private/secret.html")
        self.assertEqual(result.status, 403)
        self.assertEqual(result.reason, "Forbidden")
        self.assert_required_headers(result)

    def test_directory_traversal_returns_400(self) -> None:
        response = raw_http_request(
            self.port,
            b"GET /../../etc/passwd HTTP/1.0\r\nHost: localhost\r\n\r\n",
        )
        version, status, reason = parse_status_line(response)
        headers = parse_headers(response)
        _header_bytes, body = split_headers_and_body(response)
        self.assertEqual(version, "HTTP/1.0")
        self.assertEqual(status, 400)
        self.assertEqual(reason, "Bad Request")
        self.assertIn("content-length", headers)
        self.assertIn("content-type", headers)
        self.assertEqual(int(headers["content-length"]), len(body))

    def test_post_returns_405(self) -> None:
        result = self.http_request("POST", "/public/index.html")
        self.assertEqual(result.status, 405)
        self.assertEqual(result.reason, "Method Not Allowed")
        self.assert_required_headers(result)

    def test_malformed_raw_request_returns_400(self) -> None:
        response = raw_http_request(self.port, b"BADREQUEST\r\n\r\n")
        _version, status, reason = parse_status_line(response)
        self.assertEqual(status, 400)
        self.assertEqual(reason, "Bad Request")

    def test_partial_header_read_returns_200(self) -> None:
        with socket.create_connection((HOST, self.port), timeout=CLIENT_TIMEOUT) as sock:
            sock.settimeout(CLIENT_TIMEOUT)
            sock.sendall(b"GET /public/index.html HTTP/1.0\r\n")
            time.sleep(0.1)
            sock.sendall(b"Host: localhost\r\n")
            time.sleep(0.1)
            sock.sendall(b"\r\n")
            chunks: list[bytes] = []
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)

        response = b"".join(chunks)
        _version, status, reason = parse_status_line(response)
        self.assertEqual(status, 200)
        self.assertEqual(reason, "OK")
        self.assertIn(b"Computer Networks Academy", response)

    def test_25_concurrent_clients_receive_200(self) -> None:
        paths = [
            "/",
            "/public/index.html",
            "/public/academy.html",
            "/public/status-codes.html",
            "/public/concurrency.html",
            "/css/style.css",
            "/images/network-map.svg",
        ]

        def request_path(index: int) -> int:
            result = self.http_request("GET", paths[index % len(paths)])
            return result.status

        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            statuses = list(executor.map(request_path, range(25)))

        self.assertEqual(statuses, [200] * 25)

    def test_success_responses_include_required_headers(self) -> None:
        result = self.http_request("GET", "/public/index.html")
        self.assert_required_headers(result)

    def test_error_responses_include_required_headers(self) -> None:
        result = self.http_request("GET", "/public/missing.html")
        self.assert_required_headers(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
