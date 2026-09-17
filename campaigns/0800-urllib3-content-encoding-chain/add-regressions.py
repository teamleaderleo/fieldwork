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
        ("x-fieldwork", zlib.compress(msg)),
        ("gzip, x-fieldwork", zlib.compress(gzip.compress(msg))),
        ("x-fieldwork, gzip", gzip.compress(zlib.compress(msg))),
    ]

    for content_encoding, wire in cases:
        response = HTTPResponse(
            BytesIO(wire),
            headers={"content-encoding": content_encoding},
            preload_content=False,
        )
        assert response.read() == wire


def test_fieldwork_supported_content_encoding_chains_still_decode() -> None:
    msg = b"fieldwork-supported-chain"

    cases = [
        ("gzip, deflate", zlib.compress(gzip.compress(msg))),
        ("deflate, deflate", zlib.compress(zlib.compress(msg))),
        ("gzip,", gzip.compress(msg)),
        (", gzip", gzip.compress(msg)),
        ("gzip, , deflate", zlib.compress(gzip.compress(msg))),
    ]

    for content_encoding, wire in cases:
        response = HTTPResponse(
            BytesIO(wire),
            headers={"content-encoding": content_encoding},
            preload_content=False,
        )
        assert response.read() == msg


def test_fieldwork_content_encoding_chain_keeps_link_limit() -> None:
    response = HTTPResponse(
        BytesIO(b""),
        headers={"content-encoding": ",".join(["gzip"] * 6)},
        preload_content=False,
    )
    with pytest.raises(DecodeError, match="Too many content encodings in the chain"):
        response.read()
'''

path.write_text(source)
