from __future__ import annotations

import pathlib
import sys

path = pathlib.Path(sys.argv[1])
source = path.read_text()

old = '''        if self._decoder is None:
            if content_encoding in self.CONTENT_DECODERS:
                self._decoder = _get_decoder(content_encoding)
            elif "," in content_encoding:
                encodings = [
                    e.strip()
                    for e in content_encoding.split(",")
                    if e.strip() in self.CONTENT_DECODERS
                ]
                if encodings:
                    self._decoder = _get_decoder(content_encoding)
'''

new = '''        if self._decoder is None:
            if content_encoding in self.CONTENT_DECODERS:
                self._decoder = _get_decoder(content_encoding)
            elif "," in content_encoding:
                encodings = [
                    e.strip()
                    for e in content_encoding.split(",")
                    if e.strip()
                ]
                if encodings and all(
                    encoding in self.CONTENT_DECODERS for encoding in encodings
                ):
                    self._decoder = _get_decoder(",".join(encodings))
'''

if source.count(old) != 1:
    raise SystemExit("expected exact _init_decoder baseline block once")

path.write_text(source.replace(old, new, 1))
