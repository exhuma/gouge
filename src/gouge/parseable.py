"""
Machine-readable log formatters.

* :py:class:`CSVLog` writes one CSV row per record.
* :py:class:`XMLLog` writes one ``<record>`` element per record.
* :py:class:`JSONLog` writes one JSON object per line (JSON Lines),
  including the *extra* attributes of the record. This is the format to
  use for log aggregation.
"""

import csv
import io
import json
import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, Literal

from gouge._record import extra_attributes


class CSVLog(logging.Formatter):
    """
    CSV formatter for python loggers.

    The columns correspond to the following fields:

    * created
    * filename
    * funcName
    * levelname
    * levelno
    * lineno
    * module
    * msecs
    * name
    * pathname
    * process
    * processName
    * relativeCreated
    * thread
    * threadName
    * message
    * exc_text
    """

    @staticmethod
    def basicConfig(**kwargs: Any) -> None:
        logging.basicConfig(**kwargs)
        root = logging.getLogger()
        for handler in root.handlers:
            handler.setFormatter(CSVLog())

    def __init__(
        self, fmt: str | None = None, datefmt: str | None = None
    ) -> None:
        logging.Formatter.__init__(self, fmt, datefmt)
        self.buffer = io.StringIO()
        self.writer = csv.writer(self.buffer)

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            exc_text = getattr(record, "exc_text", "")
            if not exc_text:
                record.exc_text = self.formatException(record.exc_info)

        exc_text = getattr(record, "exc_text", "")
        message_items = [
            record.created,
            record.filename,
            record.funcName,
            record.levelname,
            record.levelno,
            record.lineno,
            record.module,
            record.msecs,
            record.name,
            record.pathname,
            record.process,
            record.processName,
            record.relativeCreated,
            record.thread,
            record.threadName,
            record.message,
            exc_text,
        ]

        self.writer.writerow(message_items)
        output = self.buffer.getvalue()
        self.buffer.seek(0)
        self.buffer.truncate()
        return output.strip()


class XMLLog(logging.Formatter):
    """
    XML formatter for python loggers.

    The records have the following schema::

        <record>
            <created />
            <filename />
            <funcName />
            <levelname />
            <levelno />
            <lineno />
            <module />
            <msecs />
            <name />
            <pathname />
            <process />
            <processName />
            <relativeCreated />
            <thread />
            <threadName />
            <message />
            <exc_text />
        </record>
    """

    @staticmethod
    def basicConfig(**kwargs: Any) -> None:
        logging.basicConfig(**kwargs)
        root = logging.getLogger()
        for handler in root.handlers:
            handler.setFormatter(XMLLog())

    def __init__(
        self, fmt: str | None = None, datefmt: str | None = None
    ) -> None:
        logging.Formatter.__init__(self, fmt, datefmt)
        from xml.dom.minidom import Document

        self.doc = Document()

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            exc_text = getattr(record, "exc_text", "")
            if not exc_text:
                record.exc_text = self.formatException(record.exc_info)

        exc_text = getattr(record, "exc_text", "")
        message_items = [
            ("created", record.created),
            ("filename", record.filename),
            ("funcName", record.funcName),
            ("levelname", record.levelname),
            ("levelno", record.levelno),
            ("lineno", record.lineno),
            ("module", record.module),
            ("msecs", record.msecs),
            ("name", record.name),
            ("pathname", record.pathname),
            ("process", record.process),
            ("processName", record.processName),
            ("relativeCreated", record.relativeCreated),
            ("thread", record.thread),
            ("threadName", record.threadName),
            ("message", record.message),
            ("exc_text", exc_text),
        ]

        element = self.doc.createElement("record")
        for tagname, value in message_items:
            subelement = self.doc.createElement(tagname)
            subelement.appendChild(self.doc.createTextNode(str(value)))
            element.appendChild(subelement)
        output: str = element.toxml()
        return output


class JSONLog(logging.Formatter):
    """
    JSON Lines formatter for python loggers.

    Each record becomes one compact JSON object on a single line (newlines
    in values are escaped). Non-ASCII text is written as-is. The keys are,
    in this order:

    * ``timestamp``: the creation time of the record in UTC, as ISO 8601
      with milliseconds, for example ``2026-10-27T13:34:48.899+00:00``.
      UTC avoids ambiguous local times around daylight-saving changes.
    * ``level``: the level name, for example ``INFO``.
    * ``logger``: the logger name.
    * ``message``: the message with its arguments merged in.
    * every *extra* attribute of the record, sorted by name. Extra
      attributes are those passed with ``extra={...}`` to a log call or set
      by a filter; standard :py:class:`logging.LogRecord` attributes and
      names starting with ``_`` are left out. The OpenTelemetry IDs
      ``otelTraceID`` and ``otelSpanID`` become ``trace_id`` and
      ``span_id`` when a span is active.
    * ``exc_text``: the plain traceback, only if the record has exception
      information. Like the standard formatter, it is cached on the
      record.
    * ``stack_info``: the stack, only if the record has one.

    The keys above always win: an extra attribute with the same name as
    one of them is written as ``extra.<name>`` instead (and dropped if that
    name is taken as well). Values which JSON cannot represent are written
    as their :py:func:`str`.

    :param fmt: Ignored. Accepted so the formatter can be configured like
        any :py:class:`logging.Formatter`.
    :param datefmt: An optional :py:meth:`~datetime.datetime.strftime`
        format for ``timestamp``. It is applied to the UTC time, so ``%z``
        renders as ``+0000``.
    :param style: Passed on to :py:class:`logging.Formatter`.
    :param validate: Passed on to :py:class:`logging.Formatter`.
    :param defaults: Passed on to :py:class:`logging.Formatter`.

    Example, with a correlation ID which a filter put on the records:

    .. code-block:: python

        import logging

        from gouge.parseable import JSONLog


        class CorrelationFilter(logging.Filter):
            def filter(self, record: logging.LogRecord) -> bool:
                record.correlation_id = "4bf92f35"
                return True


        handler = logging.StreamHandler()
        handler.addFilter(CorrelationFilter())
        handler.setFormatter(JSONLog())
        logging.getLogger().addHandler(handler)
        logging.getLogger("app").warning(
            "Order created", extra={"order.id": 42}
        )
        # {"timestamp":"2026-10-27T13:34:48.899+00:00","level":"WARNING",
        #  "logger":"app","message":"Order created",
        #  "correlation_id":"4bf92f35","order.id":42}  (one line)

    With :py:func:`logging.config.dictConfig`, use either
    ``{"()": "gouge.parseable.JSONLog"}`` or
    ``{"class": "gouge.parseable.JSONLog"}`` as the formatter.
    """

    #: The keys :py:class:`JSONLog` writes itself.
    CORE_KEYS = frozenset(
        {"timestamp", "level", "logger", "message", "exc_text", "stack_info"}
    )

    @staticmethod
    def basicConfig(**kwargs: Any) -> None:
        """
        Convenience method to have a one-liner set-up.

        Call :py:func:`logging.basicConfig` with *kwargs*, then set a
        :py:class:`JSONLog` formatter on every handler of the root logger.

        :param kwargs: Passed on to :py:func:`logging.basicConfig`.
        """
        logging.basicConfig(**kwargs)
        root = logging.getLogger()
        for handler in root.handlers:
            handler.setFormatter(JSONLog())

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        validate: bool = True,
        *,
        defaults: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            fmt, datefmt, style, validate=validate, defaults=defaults
        )

    def formatTime(
        self, record: logging.LogRecord, datefmt: str | None = None
    ) -> str:
        """
        Return the creation time of *record* in UTC.

        :param record: The record to format.
        :param datefmt: An optional
            :py:meth:`~datetime.datetime.strftime` format. Without it, the
            time is ISO 8601 with milliseconds and UTC offset.
        :returns: The formatted time.
        """
        created = datetime.fromtimestamp(record.created, tz=UTC)
        if datefmt:
            return created.strftime(datefmt)
        return created.isoformat(timespec="milliseconds")

    def format(self, record: logging.LogRecord) -> str:
        """
        Format *record* as one line of JSON.

        :param record: The record to format.
        :returns: The JSON object, without a trailing newline.
        """
        record.message = record.getMessage()
        payload: dict[str, object] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.message,
        }
        for key, value in extra_attributes(record).items():
            if key in self.CORE_KEYS:
                key = f"extra.{key}"
            payload.setdefault(key, value)

        if record.exc_info and not record.exc_text:
            # Cache the plain traceback, like the standard formatter does.
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            payload["exc_text"] = record.exc_text
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(
            payload, ensure_ascii=False, default=str, separators=(",", ":")
        )
