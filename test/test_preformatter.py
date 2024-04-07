import logging
from logging import LogRecord

import pytest

from gouge import preformatters as pf
from gouge.colourcli import Simple


def _dummy_preformatter(message: str) -> str:
    return "modified-message"


def test_preformatter():
    record = LogRecord(
        "the.logger",
        logging.INFO,
        "the-file",
        42,
        "the-message",
        None,
        None,
        None,
        None,
    )
    instance = Simple(pre_formatters={"the.logger": [_dummy_preformatter]})
    result = instance.format(record)
    assert "modified-message" in result


@pytest.mark.parametrize("status_code", ["100", "200", "300", "400", "500"])
def test_uvicorn_access(status_code: str):
    result = pf.uvicorn_access(
        f'127.0.0.1:43522 - "GET /foo/bar HTTP/1.1" {status_code}'
    )
    assert "127.0.0.1:43522" in result
    assert "-" in result
    assert "GET" in result
    assert "/foo/bar" in result
    assert "HTTP/1.1" in result
    assert str(status_code) in result


def test_uvicorn_access_default():
    result = pf.uvicorn_access("invalid-line-format")
    assert result == "invalid-line-format"
