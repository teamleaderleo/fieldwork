from __future__ import annotations

import pathlib
import sys

path = pathlib.Path(sys.argv[1])
source = path.read_text()

if "def test_fieldwork_retry_after_zero_consumes_header" in source:
    raise SystemExit("fieldwork regressions already present")

source += r'''


def _fieldwork_retry_with_backoff(**kwargs: object) -> Retry:
    retry = Retry(total=5, backoff_factor=1, **kwargs)
    retry = retry.increment(method="GET")
    retry = retry.increment(method="GET")
    assert retry.get_backoff_time() == 2.0
    return retry


def test_fieldwork_retry_after_zero_consumes_header() -> None:
    retry = _fieldwork_retry_with_backoff()
    response = HTTPResponse(status=503, headers={"Retry-After": "0"})
    with mock.patch("time.sleep") as sleep_mock:
        retry.sleep(response)
    sleep_mock.assert_not_called()


def test_fieldwork_retry_after_absent_uses_backoff() -> None:
    retry = _fieldwork_retry_with_backoff()
    response = HTTPResponse(status=503)
    with mock.patch("time.sleep") as sleep_mock:
        retry.sleep(response)
    sleep_mock.assert_called_once_with(2.0)


def test_fieldwork_retry_after_positive_owns_delay() -> None:
    retry = _fieldwork_retry_with_backoff()
    response = HTTPResponse(status=503, headers={"Retry-After": "1"})
    with mock.patch("time.sleep") as sleep_mock:
        retry.sleep(response)
    sleep_mock.assert_called_once_with(1)


def test_fieldwork_retry_after_past_date_consumes_header() -> None:
    retry = _fieldwork_retry_with_backoff()
    response = HTTPResponse(
        status=503, headers={"Retry-After": "Sun, 06 Nov 1994 08:49:37 GMT"}
    )
    with mock.patch("time.sleep") as sleep_mock:
        retry.sleep(response)
    sleep_mock.assert_not_called()


def test_fieldwork_retry_after_capped_to_zero_consumes_header() -> None:
    retry = _fieldwork_retry_with_backoff(retry_after_max=0)
    response = HTTPResponse(status=503, headers={"Retry-After": "10"})
    assert retry.get_retry_after(response) == 0
    with mock.patch("time.sleep") as sleep_mock:
        retry.sleep(response)
    sleep_mock.assert_not_called()


def test_fieldwork_retry_after_disabled_uses_backoff() -> None:
    retry = _fieldwork_retry_with_backoff(respect_retry_after_header=False)
    response = HTTPResponse(status=503, headers={"Retry-After": "1"})
    with mock.patch("time.sleep") as sleep_mock:
        retry.sleep(response)
    sleep_mock.assert_called_once_with(2.0)
'''

path.write_text(source)
