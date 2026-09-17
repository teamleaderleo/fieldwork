"""Synthetic discriminators for the urllib3 foundational-systems scout.

Evidence class: model-executed when run against an installed urllib3 release.
The scout report separately pins and source-reads the upstream revision.
"""

from __future__ import annotations

import gzip
import io
import zlib
from unittest.mock import patch

import urllib3
from urllib3.response import HTTPResponse
from urllib3.util import Retry


def mixed_content_encoding_probe() -> None:
    payload = b"fieldwork-urllib3-mixed-encoding"
    # HTTP Content-Encoding "gzip, deflate" means gzip was applied first,
    # then deflate. Decoders therefore run in reverse order.
    wire = zlib.compress(gzip.compress(payload))

    def read(encoding: str) -> bytes:
        response = HTTPResponse(
            io.BytesIO(wire),
            headers={"Content-Encoding": encoding},
            preload_content=False,
        )
        return response.read()

    unknown_only = read("x-fieldwork")
    mixed_unknown = read("gzip, x-fieldwork")
    known_control = read("gzip, deflate")

    print("[mixed-content-encoding]")
    print(f"unknown-only preserved raw bytes: {unknown_only == wire}")
    print(f"known+unknown decoded to payload: {mixed_unknown == payload}")
    print(f"known control decoded to payload: {known_control == payload}")

    assert unknown_only == wire
    assert mixed_unknown == payload
    assert known_control == payload


def retry_after_zero_probe() -> None:
    retry = Retry(total=5, backoff_factor=1)
    retry = retry.increment(method="GET")
    retry = retry.increment(method="GET")
    assert retry.get_backoff_time() == 2.0

    observed: dict[str, list[object]] = {}
    cases = {
        "absent": {},
        "zero": {"Retry-After": "0"},
        "one": {"Retry-After": "1"},
    }

    for name, headers in cases.items():
        response = HTTPResponse(status=503, headers=headers)
        with patch("time.sleep") as sleeper:
            retry.sleep(response)
            observed[name] = list(sleeper.call_args_list)

    print("[retry-after-zero]")
    print(f"configured exponential backoff: {retry.get_backoff_time()}")
    for name, calls in observed.items():
        print(f"{name}: {calls}")

    assert observed["absent"] == observed["zero"]
    assert str(observed["zero"][0]) == "call(2.0)"
    assert str(observed["one"][0]) == "call(1)"


def retry_total_none_probe() -> None:
    retry = Retry(total=None, status=2, respect_retry_after_header=True)
    implicit = retry.is_retry("GET", 429, has_retry_after=True)
    forced = Retry(
        total=None,
        status=2,
        status_forcelist={429},
        respect_retry_after_header=True,
    ).is_retry("GET", 429, has_retry_after=True)

    print("[retry-total-none]")
    print(f"implicit Retry-After 429 retried: {implicit}")
    print(f"status-forcelist 429 retried: {forced}")

    assert implicit is False
    assert forced is True


def main() -> None:
    print(f"urllib3={urllib3.__version__}")
    mixed_content_encoding_probe()
    retry_after_zero_probe()
    retry_total_none_probe()


if __name__ == "__main__":
    main()
