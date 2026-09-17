from __future__ import annotations

import pathlib
import sys

path = pathlib.Path(sys.argv[1])
source = path.read_text()

old = '''        if self.respect_retry_after_header and response:
            slept = self.sleep_for_retry(response)
            if slept:
                return

        self._sleep_backoff()
'''

new = '''        if self.respect_retry_after_header and response:
            slept = self.sleep_for_retry(response)
            if slept:
                return
            if self.get_retry_after(response) == 0:
                return

        self._sleep_backoff()
'''

if source.count(old) != 1:
    raise SystemExit("expected exact Retry.sleep baseline block once")

path.write_text(source.replace(old, new, 1))
