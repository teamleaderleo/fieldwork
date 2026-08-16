#!/usr/bin/env python3
"""Model and installed-curl probe for a resume Content-Range boundary.

Exact source read: curl/curl master at
2c22d3069aef507d6a6876a6d20616fe5e50c6a3.

The model mirrors the relevant current lib/http.c state transition. The
optional live portion uses the locally installed curl binary against a tiny
stdlib TCP server. It is supplemental execution, not execution of the pinned
checkout.
"""

from __future__ import annotations

import pathlib
import socket
import subprocess
import tempfile
import threading
from dataclasses import dataclass


@dataclass(frozen=True)
class ParseResult:
    resume_from: int
    content_range: bool
    offset: int | None


def model_content_range(httpcode: int, resume_from: int, value: str) -> ParseResult:
    """Mirror the relevant current Curl_http_header Content-Range logic."""
    i = 0
    while i < len(value) and not value[i].isdigit() and value[i] != "*":
        i += 1

    content_range = False
    offset = None

    if i < len(value) and value[i].isdigit():
        j = i
        while j < len(value) and value[j].isdigit():
            j += 1
        offset = int(value[i:j])
        if resume_from == offset:
            content_range = True
    elif httpcode < 300:
        # Current source comment: "get everything".
        resume_from = 0

    return ParseResult(resume_from, content_range, offset)


def model_controls() -> None:
    matching = model_content_range(206, 5, "bytes 5-10/11")
    star = model_content_range(206, 5, "bytes */11")
    wrong = model_content_range(206, 5, "bytes 6-11/12")
    historical_416 = model_content_range(416, 5, "bytes */5")

    assert matching == ParseResult(5, True, 5)
    assert star == ParseResult(0, False, None)
    assert wrong == ParseResult(5, False, 6)
    assert historical_416 == ParseResult(5, False, None)

    print("model controls")
    print(f"206 matching numeric range -> {matching}")
    print(f"206 unsatisfied '*' range -> {star}")
    print(f"206 wrong numeric range -> {wrong}")
    print(f"416 unsatisfied '*' range -> {historical_416}")


def serve_once(status: int, content_range: str | None, body: bytes) -> tuple[int, bytes, str]:
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    port = listener.getsockname()[1]

    def server() -> None:
        conn, _ = listener.accept()
        with conn:
            request = b""
            while b"\r\n\r\n" not in request:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                request += chunk

            reason = {
                200: "OK",
                206: "Partial Content",
                416: "Requested Range Not Satisfiable",
            }[status]
            headers = [
                f"HTTP/1.1 {status} {reason}",
                f"Content-Length: {len(body)}",
                "Connection: close",
            ]
            if content_range is not None:
                headers.append(f"Content-Range: {content_range}")
            response = ("\r\n".join(headers) + "\r\n\r\n").encode() + body
            conn.sendall(response)
        listener.close()

    thread = threading.Thread(target=server)
    thread.start()

    with tempfile.TemporaryDirectory() as tmp:
        output = pathlib.Path(tmp) / "partial.bin"
        output.write_bytes(b"hello")
        completed = subprocess.run(
            [
                "curl",
                "-sS",
                "-C",
                "5",
                "-o",
                str(output),
                f"http://127.0.0.1:{port}/",
            ],
            capture_output=True,
            check=False,
        )
        result = (
            completed.returncode,
            output.read_bytes(),
            completed.stderr.decode(errors="replace"),
        )

    thread.join()
    return result


def installed_curl_controls() -> None:
    try:
        version = subprocess.run(
            ["curl", "-V"], capture_output=True, text=True, check=True
        ).stdout.splitlines()[0]
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("installed curl unavailable; model-only probe completed")
        return

    print(f"installed control: {version}")

    cases = [
        ("matching", 206, "bytes 5-10/11", b"WORLD!"),
        ("unsatisfied-star", 206, "bytes */11", b"WORLD!"),
        ("missing", 206, None, b"WORLD!"),
        ("wrong-offset", 206, "bytes 6-11/12", b"WORLD!"),
        ("historical-416", 416, "bytes */5", b""),
    ]

    observed: dict[str, tuple[int, bytes, str]] = {}
    for name, status, content_range, body in cases:
        observed[name] = serve_once(status, content_range, body)
        rc, data, stderr = observed[name]
        print(
            f"{name}: rc={rc} bytes={data!r} stderr={stderr.strip()!r}"
        )

    assert observed["matching"][0] == 0
    assert observed["matching"][1] == b"helloWORLD!"

    # The discriminator: '*' denotes an unsatisfied range, yet the current
    # installed control accepts the malformed 206 and appends its body.
    assert observed["unsatisfied-star"][0] == 0
    assert observed["unsatisfied-star"][1] == b"helloWORLD!"

    # Existing safety behavior when resume remains active.
    assert observed["missing"][0] == 33
    assert observed["missing"][1] == b"hello"
    assert observed["wrong-offset"][0] == 33
    assert observed["wrong-offset"][1] == b"hello"

    # Current 416 handling leaves the completed file alone.
    assert observed["historical-416"][0] == 0
    assert observed["historical-416"][1] == b"hello"


def main() -> None:
    model_controls()
    installed_curl_controls()


if __name__ == "__main__":
    main()
