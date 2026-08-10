from __future__ import annotations

import pathlib
import sys

path = pathlib.Path(sys.argv[1])
source = path.read_text()

if "def test_fieldwork_unknown_content_encoding_chain_stays_opaque" in source:
    raise SystemExit("fieldwork regressions already present")

source += r'''


def test_fieldwork_unknown_content_encoding_chain_stays_opaque() -> None:
    msg = b"fieldwork-unknown-chain"

    cases = [
        ("x-fieldwork", zlib.compress(msg), zlib.compress(msg)),
        (
            "gzip, x-fieldwork",
            zlib.compress(gzip.compress(msg)),
            zlib.compress(gzip.compress(msg)),
        ),
        (
            "x-fieldwork, gzip",
            gzip.compress(zlib.compress(msg)),
            gzip.compress(zlib.compress(msg)),
        ),
        ("gzip,", zlib.compress(gzip.compress(msg)), zlib.compress(gzip.compress(msg))),
    ]

    for content_encoding, wire, expected in cases:
        response = HTTPResponse(
            BytesIO(wire),
            headers={"content-encoding": content_encoding},
            preload_content=False,
        )
        assert response.read() == expected


def test_fieldwork_supported_content_encoding_chains_still_decode() -> None:
    msg = b"fieldwork-supported-chain"

    gzip_deflate = HTTPResponse(
        BytesIO(zlib.compress(gzip.compress(msg))),
        headers={"content-encoding": "gzip, deflate"},
        preload_content=False,
    )
    assert gzip_deflate.read() == msg

    deflate_deflate = HTTPResponse(
        BytesIO(zlib.compress(zlib.compress(msg))),
        headers={"content-encoding": "deflate, deflate"},
        preload_content=False,
    )
    assert deflate_deflate.read() == msg
'''

path.write_text(source)
