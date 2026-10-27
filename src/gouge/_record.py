"""
Private helpers to tell the standard attributes of a log record apart from
the *extra* attributes an application attached to it.

Extra attributes come from the ``extra`` argument of a log call, or from a
:class:`logging.Filter` which sets attributes on the record (for example a
correlation or trace ID).
"""

import logging
from collections.abc import Iterable

#: Attributes set by OpenTelemetry's logging instrumentation, mapped to the
#: field names used in the output.
_OTEL_RENAMED = {"otelTraceID": "trace_id", "otelSpanID": "span_id"}

#: The value OpenTelemetry uses for the IDs when no span is active.
_OTEL_INVALID_ID = "0"

#: Attributes which are not extras: everything a fresh record has, the
#: attributes set while formatting, and the OpenTelemetry attributes (the IDs
#: are emitted under their own names instead).
STANDARD_ATTRIBUTES = frozenset(
    vars(logging.LogRecord("", logging.NOTSET, "", 0, "", None, None))
) | {
    "message",
    "asctime",
    "otelTraceID",
    "otelSpanID",
    "otelServiceName",
    "otelTraceSampled",
}


def extra_attributes(record: logging.LogRecord) -> dict[str, object]:
    """
    Return the extra attributes of *record*, sorted by name.

    Names starting with ``_`` are left out. The OpenTelemetry IDs
    ``otelTraceID`` and ``otelSpanID`` are returned as ``trace_id`` and
    ``span_id``, unless the record already has attributes of that name or
    the ID is the "no active span" value ``"0"``.

    :param record: The record to inspect.
    :returns: A new dictionary of attribute names to values.
    """
    output = {
        key: value
        for key, value in vars(record).items()
        if key not in STANDARD_ATTRIBUTES and not key.startswith("_")
    }
    for otel_name, name in _OTEL_RENAMED.items():
        value = getattr(record, otel_name, None)
        if value is not None and value != _OTEL_INVALID_ID:
            output.setdefault(name, value)
    return dict(sorted(output.items()))


def selected_attributes(
    record: logging.LogRecord, names: Iterable[str]
) -> dict[str, object]:
    """
    Return the attributes *names* of *record*, in the given order.

    A name is looked up in :py:func:`extra_attributes` first (so
    ``trace_id`` also finds the OpenTelemetry ID), then on the record
    itself. Names which are found in neither place are skipped.

    :param record: The record to inspect.
    :param names: The attribute names to return.
    :returns: A new dictionary of attribute names to values.
    """
    extras = extra_attributes(record)
    output: dict[str, object] = {}
    for name in names:
        if name in extras:
            output[name] = extras[name]
        elif hasattr(record, name):
            output[name] = getattr(record, name)
    return output


def cache_exc_text(
    record: logging.LogRecord, formatter: logging.Formatter
) -> None:
    """
    Cache the plain traceback of *record* in ``record.exc_text``.

    Like :py:meth:`logging.Formatter.format` does, the text is only created
    if the record has exception information and no text yet. It is created
    with ``formatter.formatException(record.exc_info)``, so it never
    contains escape codes: other handlers may reuse it.

    :param record: The record to update.
    :param formatter: The formatter used to render the traceback.
    """
    if record.exc_info and not record.exc_text:
        record.exc_text = formatter.formatException(record.exc_info)
