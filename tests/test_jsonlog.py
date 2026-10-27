"""
Tests for the JSON Lines formatter :py:class:`gouge.parseable.JSONLog`.
"""

import io
import json
import logging
import logging.config
from collections.abc import Iterator
from typing import Any

import pytest

from conftest import CREATED, MakeRecord
from gouge.colourcli import Simple
from gouge.parseable import JSONLog


def _parse(line: str) -> dict[str, Any]:
    assert "\n" not in line
    data: dict[str, Any] = json.loads(line)
    return data


class CorrelationFilter(logging.Filter):
    """
    A filter like the ones applications use to attach request IDs.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = "4bf92f35"
        record.trace_id = "0af7651916cd43dd8448eb211c80319c"
        return True


@pytest.fixture
def app_logger() -> Iterator[logging.Logger]:
    """
    A non-propagating logger without handlers, cleaned up afterwards.
    """
    logger = logging.getLogger("test_jsonlog.app")
    logger.propagate = False
    yield logger
    logger.handlers[:] = []
    logger.propagate = True


def test_core_keys_exact(make_record: MakeRecord) -> None:
    """
    Ensure a plain record renders exactly the core keys, in order, as one
    compact line.
    """
    output = JSONLog().format(
        make_record("hello %s", ("world",), created=CREATED)
    )
    assert output == (
        '{"timestamp":"2026-10-27T13:34:48.899+00:00","level":"WARNING",'
        '"logger":"app.orders","message":"hello world"}'
    )


def test_extras_are_top_level_and_sorted(make_record: MakeRecord) -> None:
    """
    Ensure extra attributes are added as top-level keys, sorted by name,
    after the core keys, and private names are skipped.
    """
    record = make_record(created=CREATED)
    record.zeta = 1
    record.__dict__["order.id"] = 42
    record._private = "hidden"
    data = _parse(JSONLog().format(record))
    assert list(data) == [
        "timestamp",
        "level",
        "logger",
        "message",
        "order.id",
        "zeta",
    ]
    assert data["order.id"] == 42
    assert data["zeta"] == 1


def test_json_types_are_kept(make_record: MakeRecord) -> None:
    """
    Ensure JSON-compatible values keep their type.
    """
    record = make_record(created=CREATED)
    record.flag = True
    record.ratio = 0.5
    record.nothing = None
    record.items = ["a", 1]
    data = _parse(JSONLog().format(record))
    assert data["flag"] is True
    assert data["ratio"] == 0.5
    assert data["nothing"] is None
    assert data["items"] == ["a", 1]


def test_unicode_is_written_as_is(make_record: MakeRecord) -> None:
    """
    Ensure non-ASCII text is not escaped and survives a round trip.
    """
    record = make_record("Bestellung für %s", ("Zoë",), created=CREATED)
    record.city = "Luxembourg-Ville ☃"
    output = JSONLog().format(record)
    assert "für Zoë" in output
    assert "☃" in output
    data = _parse(output)
    assert data["message"] == "Bestellung für Zoë"
    assert data["city"] == "Luxembourg-Ville ☃"


def test_newlines_are_escaped(make_record: MakeRecord) -> None:
    """
    Ensure multi-line messages stay on one output line.
    """
    output = JSONLog().format(make_record("first\nsecond", created=CREATED))
    assert _parse(output)["message"] == "first\nsecond"


def test_non_serialisable_value_uses_str(make_record: MakeRecord) -> None:
    """
    Ensure values JSON cannot represent are written as their ``str()``.
    """

    class Order:
        def __str__(self) -> str:
            return "Order#42"

    record = make_record(created=CREATED)
    record.order = Order()
    record.ids = {1, 2}
    data = _parse(JSONLog().format(record))
    assert data["order"] == "Order#42"
    assert data["ids"] == "{1, 2}"


def test_exception(make_record: MakeRecord) -> None:
    """
    Ensure the plain traceback is added as ``exc_text`` and cached on the
    record.
    """
    record = make_record(exc_info=True, created=CREATED)
    formatter = JSONLog()
    data = _parse(formatter.format(record))
    assert list(data)[-1] == "exc_text"
    assert data["exc_text"].startswith("Traceback (most recent call last):")
    assert data["exc_text"].endswith("ValueError: boom")
    assert "\x1b" not in data["exc_text"]
    assert record.exc_text == data["exc_text"]


def test_cached_exc_text_is_reused(make_record: MakeRecord) -> None:
    """
    Ensure an ``exc_text`` cached by another formatter is used as-is.
    """
    record = make_record(exc_info=True, created=CREATED)
    record.exc_text = "cached"
    assert _parse(JSONLog().format(record))["exc_text"] == "cached"


def test_stack_info(make_record: MakeRecord) -> None:
    """
    Ensure ``stack_info`` is added only when the record has one.
    """
    record = make_record(created=CREATED)
    assert "stack_info" not in _parse(JSONLog().format(record))
    record.stack_info = "Stack (most recent call last):\n  here"
    data = _parse(JSONLog().format(record))
    assert data["stack_info"] == "Stack (most recent call last):\n  here"


def test_extras_colliding_with_core_keys(make_record: MakeRecord) -> None:
    """
    Ensure extras named like core keys do not overwrite them but are kept
    under ``extra.<name>``, and an explicit ``extra.<name>`` wins.
    """
    record = make_record(created=CREATED)
    record.timestamp = "fake"
    record.level = "fake"
    record.logger = "fake"
    data = _parse(JSONLog().format(record))
    assert data["timestamp"] == "2026-10-27T13:34:48.899+00:00"
    assert data["level"] == "WARNING"
    assert data["logger"] == "app.orders"
    assert data["extra.timestamp"] == "fake"
    assert data["extra.level"] == "fake"
    assert data["extra.logger"] == "fake"

    record.__dict__["extra.level"] = "explicit"
    data = _parse(JSONLog().format(record))
    assert data["extra.level"] == "explicit"


def test_opentelemetry_ids(make_record: MakeRecord) -> None:
    """
    Ensure OpenTelemetry's record attributes become ``trace_id`` and
    ``span_id`` and the other ``otel*`` attributes are left out.
    """
    record = make_record(created=CREATED)
    record.otelTraceID = "0af7651916cd43dd8448eb211c80319c"
    record.otelSpanID = "b7ad6b7169203331"
    record.otelServiceName = "app"
    record.otelTraceSampled = True
    data = _parse(JSONLog().format(record))
    assert data["trace_id"] == "0af7651916cd43dd8448eb211c80319c"
    assert data["span_id"] == "b7ad6b7169203331"
    assert not [key for key in data if key.startswith("otel")]


def test_datefmt_is_applied_in_utc(make_record: MakeRecord) -> None:
    """
    Ensure *datefmt* formats the UTC time.
    """
    formatter = JSONLog(datefmt="%Y-%m-%dT%H:%M:%S%z")
    data = _parse(formatter.format(make_record(created=CREATED)))
    assert data["timestamp"] == "2026-10-27T13:34:48+0000"


def test_filter_attributes_in_both_formatters(
    app_logger: logging.Logger,
) -> None:
    """
    Ensure attributes set by a filter appear in the JSON and on the
    console line.
    """
    json_stream = io.StringIO()
    console_stream = io.StringIO()
    for stream, formatter in (
        (json_stream, JSONLog()),
        (console_stream, Simple(show_extra=True)),
    ):
        handler = logging.StreamHandler(stream)
        handler.addFilter(CorrelationFilter())
        handler.setFormatter(formatter)
        app_logger.addHandler(handler)

    app_logger.warning("Order created", extra={"order.id": 42})

    data = _parse(json_stream.getvalue().rstrip("\n"))
    assert data["correlation_id"] == "4bf92f35"
    assert data["trace_id"] == "0af7651916cd43dd8448eb211c80319c"
    assert data["order.id"] == 42
    console = console_stream.getvalue()
    assert "correlation_id=4bf92f35" in console
    assert "trace_id=0af7651916cd43dd8448eb211c80319c" in console


@pytest.mark.parametrize(
    "formatter_config",
    [
        {"()": "gouge.parseable.JSONLog"},
        {"()": "gouge.parseable.JSONLog", "format": "%(message)s"},
        {"class": "gouge.parseable.JSONLog"},
        {
            "class": "gouge.parseable.JSONLog",
            "format": "%(message)s",
            "datefmt": "%Y",
            "validate": True,
        },
    ],
)
def test_dict_config(
    formatter_config: dict[str, Any], app_logger: logging.Logger
) -> None:
    """
    Ensure the formatter can be set up with :py:func:`dictConfig`, both as
    a factory and as a class.
    """
    stream = io.StringIO()
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": formatter_config},
            "handlers": {
                "out": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": stream,
                }
            },
            "loggers": {
                app_logger.name: {"handlers": ["out"], "propagate": False}
            },
        }
    )
    app_logger.warning("hello", extra={"cid": "abc"})
    data = _parse(stream.getvalue().rstrip("\n"))
    assert data["message"] == "hello"
    assert data["cid"] == "abc"
    assert isinstance(app_logger.handlers[0].formatter, JSONLog)


def test_basic_config(restore_root_logger: logging.Logger) -> None:
    """
    Ensure ``basicConfig`` installs the formatter on the root handlers.
    """
    stream = io.StringIO()
    JSONLog.basicConfig(stream=stream, force=True, level=logging.INFO)
    logging.getLogger("x").info("hi", extra={"cid": "abc"})
    assert all(
        isinstance(h.formatter, JSONLog) for h in restore_root_logger.handlers
    )
    data = _parse(stream.getvalue().rstrip("\n"))
    assert data["message"] == "hi"
    assert data["cid"] == "abc"
