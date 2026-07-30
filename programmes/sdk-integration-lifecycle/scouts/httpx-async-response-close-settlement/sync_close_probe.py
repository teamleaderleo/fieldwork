import json
import sys

import httpx


class FailOnceSyncStream(httpx.SyncByteStream):
    def __init__(self) -> None:
        self.close_calls = 0
        self.cleaned = False

    def __iter__(self):
        return iter(())

    def close(self) -> None:
        self.close_calls += 1
        if self.close_calls == 1:
            raise RuntimeError("sync close failed")
        self.cleaned = True


def main() -> None:
    stream = FailOnceSyncStream()
    response = httpx.Response(200, stream=stream)
    first_error = None

    try:
        response.close()
    except RuntimeError as exc:
        first_error = f"{type(exc).__name__}: {exc}"

    result = {
        "python": sys.version.split()[0],
        "httpx": httpx.__version__,
        "after_first_failure": {
            "error": first_error,
            "response_is_closed": response.is_closed,
            "close_calls": stream.close_calls,
            "stream_cleaned": stream.cleaned,
        },
    }

    response.close()

    result["after_retry"] = {
        "response_is_closed": response.is_closed,
        "close_calls": stream.close_calls,
        "stream_cleaned": stream.cleaned,
    }

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
