"""
Tests for rendering the extra attributes of a record in
:py:class:`gouge.colourcli.Simple`.
"""

import io
import logging
import sys

import colorama as clr
import pytest

from conftest import MakeRecord
from gouge.colourcli import Simple

DIM = clr.Style.DIM
RESET = clr.Style.RESET_ALL


def _tail(pairs: str) -> str:
    return f" {DIM}{pairs}{RESET}"


class CorrelationFilter(logging.Filter):
    """
    A filter like the ones applications use to attach request IDs.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = "4bf92f35"
        record.trace_id = "0af7651916cd43dd8448eb211c80319c"
        return True


def test_default_output_unchanged(make_record: MakeRecord) -> None:
    """
    Ensure extra attributes are not shown by default.
    """
    record = make_record(name="app", level=logging.INFO, func="run")
    expected = Simple().format(record)
    record.correlation_id = "abc"
    assert Simple().format(record) == expected
    assert Simple(show_extra=False).format(record) == expected


def test_show_all_extras_sorted(make_record: MakeRecord) -> None:
    """
    Ensure ``show_extra=True`` appends every extra attribute, sorted by
    name, as a dim tail.
    """
    record = make_record(name="app", level=logging.INFO, func="run")
    expected = Simple().format(record)
    record.zeta = 1
    record.alpha = "x"
    record.__dict__["order.id"] = 42
    output = Simple(show_extra=True).format(record)
    assert output == expected + _tail("alpha=x order.id=42 zeta=1")


def test_show_all_without_extras_has_no_tail(make_record: MakeRecord) -> None:
    """
    Ensure nothing is appended when a record has no extra attributes.
    """
    record = make_record(name="app", level=logging.INFO, func="run")
    assert Simple(show_extra=True).format(record) == Simple().format(record)


def test_private_and_standard_attributes_hidden(
    make_record: MakeRecord,
) -> None:
    """
    Ensure standard record attributes, attributes set while formatting and
    names starting with ``_`` are not treated as extras.
    """
    record = make_record(name="app", level=logging.INFO, func="run")
    expected = Simple().format(record)
    record._private = "hidden"
    record.stack_info = "stack"
    assert Simple(show_extra=True).format(record) == expected


def test_show_selected_extras_in_order(make_record: MakeRecord) -> None:
    """
    Ensure a sequence of names shows only those, in that order, skipping
    absent ones; standard attributes may be selected too.
    """
    record = make_record(name="app", level=logging.INFO, func="run")
    expected = Simple().format(record)
    record.b = 2
    record.a = 1
    record.c = 3
    formatter = Simple(show_extra=["c", "missing", "a", "funcName"])
    assert formatter.format(record) == expected + _tail("c=3 a=1 funcName=run")


def test_show_extra_single_string_is_one_name(make_record: MakeRecord) -> None:
    """
    Ensure a bare string selects one attribute, not its characters.
    """
    record = make_record(name="app", level=logging.INFO, func="run")
    expected = Simple().format(record)
    record.cid = "x1"
    record.c = "no"
    output = Simple(show_extra="cid").format(record)
    assert output == expected + _tail("cid=x1")


@pytest.mark.parametrize(
    ("value", "rendered"),
    [
        ("plain", "plain"),
        (42, "42"),
        (None, "None"),
        ("", "''"),
        ("two words", "'two words'"),
        ("line\nbreak", "'line\\nbreak'"),
        ("tab\there", "'tab\\there'"),
        (["a", "b"], "\"['a', 'b']\""),
    ],
)
def test_value_rendering(
    value: object, rendered: str, make_record: MakeRecord
) -> None:
    """
    Ensure values use ``str()``, falling back to ``repr()`` of that string
    when it is empty or contains whitespace.
    """
    record = make_record(name="app", level=logging.INFO, func="run")
    expected = Simple().format(record)
    record.key = value
    output = Simple(show_extra=True).format(record)
    assert output == expected + _tail(f"key={rendered}")


def test_braces_are_safe(make_record: MakeRecord) -> None:
    """
    Ensure braces in values, names and the message are output verbatim.
    """
    record = make_record(
        "Got {} and {0}", name="app", level=logging.INFO, func="run"
    )
    expected = Simple().format(record)
    record.tpl = "{levelname}{0}{"
    record.__dict__["{odd}"] = "}"
    output = Simple(show_extra=True).format(record)
    assert output == expected + _tail("tpl={levelname}{0}{ {odd}=}")
    assert "Got {} and {0}" in output


def test_no_escape_codes_leak_into_record(make_record: MakeRecord) -> None:
    """
    Ensure formatting does not store ANSI escape codes on the record, so
    other handlers can reuse it.
    """
    record = make_record(name="app", level=logging.INFO, func="run")
    record.cid = "abc"
    before = dict(vars(record))
    Simple(show_extra=True).format(record)
    assert vars(record)["cid"] == "abc"
    assert {
        key: value
        for key, value in vars(record).items()
        if key not in ("message", "asctime")
    } == before
    assert "\x1b" not in record.message
    assert "\x1b" not in record.asctime


def test_extras_precede_traceback() -> None:
    """
    Ensure the extras tail stays on the message line, before a traceback.
    """
    try:
        raise ValueError("boom")
    except ValueError:
        exc_info = sys.exc_info()
    record = logging.LogRecord(
        "app", logging.ERROR, "p", 1, "failed", None, exc_info
    )
    record.cid = "abc"
    output = Simple(show_extra=True, show_exc=True).format(record)
    first_line, rest = output.split("\n", 1)
    assert first_line.endswith(_tail("cid=abc"))
    assert "ValueError: boom" in rest


def test_opentelemetry_ids(make_record: MakeRecord) -> None:
    """
    Ensure OpenTelemetry's record attributes are shown as ``trace_id`` and
    ``span_id``, and the service name and sampling flag are hidden.
    """
    record = make_record(name="app", level=logging.INFO, func="run")
    expected = Simple().format(record)
    record.otelTraceID = "0af7651916cd43dd8448eb211c80319c"
    record.otelSpanID = "b7ad6b7169203331"
    record.otelServiceName = "app"
    record.otelTraceSampled = True
    output = Simple(show_extra=True).format(record)
    assert output == expected + _tail(
        "span_id=b7ad6b7169203331 trace_id=0af7651916cd43dd8448eb211c80319c"
    )
    selected = Simple(show_extra=["trace_id"]).format(record)
    assert selected == expected + _tail(
        "trace_id=0af7651916cd43dd8448eb211c80319c"
    )


def test_opentelemetry_ids_without_span(make_record: MakeRecord) -> None:
    """
    Ensure the "no active span" ID ``"0"`` is not shown.
    """
    record = make_record(name="app", level=logging.INFO, func="run")
    expected = Simple().format(record)
    record.otelTraceID = "0"
    record.otelSpanID = "0"
    assert Simple(show_extra=True).format(record) == expected


def test_explicit_trace_id_wins_over_opentelemetry(
    make_record: MakeRecord,
) -> None:
    """
    Ensure an explicitly set ``trace_id`` is not replaced by the
    OpenTelemetry attribute.
    """
    record = make_record(name="app", level=logging.INFO, func="run")
    expected = Simple().format(record)
    record.trace_id = "explicit"
    record.otelTraceID = "from-otel"
    output = Simple(show_extra=True).format(record)
    assert output == expected + _tail("trace_id=explicit")


def test_filter_attributes_are_shown() -> None:
    """
    Ensure attributes set by a filter appear on the logged line.
    """
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.addFilter(CorrelationFilter())
    handler.setFormatter(Simple(show_extra=["correlation_id", "trace_id"]))
    logger = logging.getLogger("test_show_extra.filter")
    logger.propagate = False
    logger.addHandler(handler)
    try:
        logger.warning("Order created", extra={"order.id": 42})
    finally:
        logger.removeHandler(handler)
    assert stream.getvalue().endswith(
        "Order created"
        + _tail(
            "correlation_id=4bf92f35 trace_id=0af7651916cd43dd8448eb211c80319c"
        )
        + "\n"
    )


def test_basic_config_passes_show_extra(
    restore_root_logger: logging.Logger,
) -> None:
    """
    Ensure ``basicConfig`` passes *show_extra* on to the formatter.
    """
    stream = io.StringIO()
    stream.name = "<stderr>"
    handlers = Simple.basicConfig(show_extra=["cid"], stream=stream, force=True)
    assert handlers
    for handler in handlers:
        assert isinstance(handler.formatter, Simple)
        assert handler.formatter.show_extra == ("cid",)
