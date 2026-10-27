import logging
from logging import LogRecord

import pytest

from gouge import preformatters as pf
from gouge.colourcli import Simple


def _dummy_preformatter(message: str) -> str:
    return "modified-message"


def test_preformatter() -> None:
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
def test_uvicorn_access(status_code: str) -> None:
    result = pf.uvicorn_access(
        f'127.0.0.1:43522 - "GET /foo/bar HTTP/1.1" {status_code}'
    )
    assert "127.0.0.1:43522" in result
    assert "-" in result
    assert "GET" in result
    assert "/foo/bar" in result
    assert "HTTP/1.1" in result
    assert str(status_code) in result


def test_uvicorn_access_default() -> None:
    result = pf.uvicorn_access("invalid-line-format")
    assert result == "invalid-line-format"


def test_single_pre_formatter_needs_no_list() -> None:
    """
    Ensure a bare dotted path or callable is a one-element list, not
    iterated character by character.
    """
    from gouge.preformatters import uvicorn_access

    by_path = Simple(pre_formatters={"x": "gouge.preformatters.uvicorn_access"})
    by_callable = Simple(pre_formatters={"x": str.upper})
    assert by_path.pre_formatters == {"x": [uvicorn_access]}
    assert by_callable.pre_formatters == {"x": [str.upper]}
