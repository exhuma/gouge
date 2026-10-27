"""
Tests for configuring the formatters from :py:func:`logging.config.dictConfig`
and for the helpers which make that practical.
"""

import io
import logging
import logging.config

import pytest

from conftest import MakeRecord
from gouge.colourcli import Simple
from gouge.preformatters import uvicorn_access

ACCESS = '127.0.0.1 - "GET /x HTTP/1.1" 200'


@pytest.mark.parametrize(
    "key,cls",
    [
        (key, cls)
        for key in ("class", "()")
        for cls in ("CSVLog", "XMLLog", "JSONLog")
    ],
)
def test_parseable_from_dictconfig(
    key: str,
    cls: str,
    restore_root_logger: logging.Logger,
    make_record: MakeRecord,
) -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {"f": {key: f"gouge.parseable.{cls}"}},
            "handlers": {
                "h": {"class": "logging.StreamHandler", "formatter": "f"}
            },
            "root": {"handlers": ["h"]},
        }
    )
    handler = logging.getLogger().handlers[0]
    assert type(handler.formatter).__name__ == cls
    assert "hello" in handler.format(
        make_record("hello", name="a", level=logging.INFO)
    )


def test_simple_from_dictconfig_with_dotted_pre_formatter(
    restore_root_logger: logging.Logger, make_record: MakeRecord
) -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "f": {
                    "()": "gouge.colourcli.Simple",
                    "pre_formatters": {
                        "uvicorn.access": ["gouge.preformatters.uvicorn_access"]
                    },
                }
            },
            "handlers": {
                "h": {"class": "logging.StreamHandler", "formatter": "f"}
            },
            "root": {"handlers": ["h"]},
        }
    )
    handler = logging.getLogger().handlers[0]
    assert isinstance(handler.formatter, Simple)
    assert handler.formatter.pre_formatters == {
        "uvicorn.access": [uvicorn_access]
    }
    assert "\x1b[34m127.0.0.1" in handler.format(
        make_record(ACCESS, name="uvicorn.access", level=logging.INFO)
    )


def test_pre_formatters_accept_callables_and_strings(
    make_record: MakeRecord,
) -> None:
    def upper(message: str) -> str:
        return message.upper()

    fmt = Simple(
        pre_formatters={"a": [upper, "gouge.preformatters.uvicorn_access"]}
    )
    assert fmt.pre_formatters == {"a": [upper, uvicorn_access]}
    assert "HI" in fmt.format(make_record("hi", name="a", level=logging.INFO))


def test_pre_formatter_accepts_colon_syntax() -> None:
    fmt = Simple(pre_formatters={"a": ["gouge.preformatters:uvicorn_access"]})
    assert fmt.pre_formatters == {"a": [uvicorn_access]}


@pytest.mark.parametrize(
    "spec,fragment",
    [
        ("nodots", "'nodots'"),
        ("no_such_module_xyz.func", "'no_such_module_xyz.func'"),
        ("gouge.preformatters.missing", "'gouge.preformatters.missing'"),
        ("gouge.preformatters.METHOD_COLORS.x", "'gouge.preformatters"),
        ("gouge.preformatters.P_UVICORN_ACCESS", "not callable"),
    ],
)
def test_bad_pre_formatter_names_the_string(spec: str, fragment: str) -> None:
    with pytest.raises(ValueError, match="(?i)pre-formatter") as info:
        Simple(pre_formatters={"a": [spec]})
    assert fragment in str(info.value)


def test_basic_config_forwards_pre_formatters(
    restore_root_logger: logging.Logger,
) -> None:
    stream = io.StringIO()
    stream.name = "<stderr>"
    handlers = Simple.basicConfig(
        stream=stream,
        force=True,
        pre_formatters={"a": ["gouge.preformatters.uvicorn_access"]},
    )
    formatter = handlers[0].formatter
    assert isinstance(formatter, Simple)
    assert formatter.pre_formatters == {"a": [uvicorn_access]}
