Structured output
=================

The formatters in :mod:`gouge.parseable` write records for machines rather
than people: :class:`~gouge.parseable.JSONLog` writes JSON Lines,
:class:`~gouge.parseable.CSVLog` CSV and :class:`~gouge.parseable.XMLLog`
XML. They never add colour.

JSON Lines
----------

.. versionadded:: 2.3

:class:`~gouge.parseable.JSONLog` writes one compact JSON object per line.
This is the format to use when logs are collected by a log aggregator:

>>> import logging
>>> from gouge.parseable import JSONLog
>>> JSONLog.basicConfig(level=logging.INFO)
>>> log = logging.getLogger("app")
>>> log.info(
...     "Order created",
...     extra={"order.id": 42},
... )
{"timestamp":"2026-10-27T13:34:48.899+00:00","level":"INFO","logger":"app","message":"Order created","order.id":42}

The keys are, in this order:

``timestamp``
   The creation time of the record in UTC, as ISO 8601 with milliseconds.
   Pass ``datefmt`` to use another format.

``level``, ``logger`` and ``message``
   The level name, the logger name and the message with its arguments
   merged in.

Extra attributes
   Every attribute passed with ``extra={...}`` or set by a filter, sorted
   by name, as for ``show_extra=True`` in
   :class:`~gouge.colourcli.Simple` (see :doc:`extra-attributes`). Numbers,
   booleans, lists and dictionaries keep their JSON type; other values are
   written as their :class:`str`.

``exc_text`` and ``stack_info``
   The plain traceback and the stack, only if the record has them.

An extra attribute named like one of the other keys is written as
``extra.<name>``, so it cannot overwrite them:

>>> log.info("Saved", extra={"level": "admin"})
{"timestamp":"2026-10-27T13:34:48.899+00:00","level":"INFO","logger":"app","message":"Saved","extra.level":"admin"}

Tracebacks stay on the same line, with the line breaks escaped:

>>> try:
...     1 / 0
... except ZeroDivisionError:
...     log.exception("Failed")
{"timestamp":...,"message":"Failed","exc_text":"Traceback (most recent call last):\n ... division by zero"}

CSV and XML
-----------

:class:`~gouge.parseable.CSVLog` writes one row per record, and
:class:`~gouge.parseable.XMLLog` one ``<record>`` element. Both write the
same fields: the standard attributes of :class:`~logging.LogRecord`
followed by the message and the traceback. They do not write extra
attributes.

>>> from gouge.parseable import CSVLog, XMLLog
>>> handler = logging.StreamHandler()
>>> handler.setFormatter(CSVLog())
>>> jobs = logging.getLogger("jobs")
>>> jobs.addHandler(handler)
>>> jobs.propagate = False
>>> jobs.warning("Retrying")
1793108088.899,...,WARNING,30,...,jobs,...,Retrying,
>>> handler.setFormatter(XMLLog())
>>> jobs.warning("Retrying")
<record><created>1793108088.899</created>...<message>Retrying</message><exc_text>None</exc_text></record>

Configure with dictConfig
-------------------------

Use the formatter classes like any other formatter, either with ``"()"``
or with ``"class"``:

>>> import logging.config
>>> logging.config.dictConfig({
...     "version": 1,
...     "disable_existing_loggers": False,
...     "formatters": {
...         "json": {
...             "class": "gouge.parseable.JSONLog",
...         },
...     },
...     "handlers": {
...         "console": {
...             "class": "logging.StreamHandler",
...             "formatter": "json",
...         },
...     },
...     "root": {
...         "handlers": ["console"],
...         "level": "INFO",
...     },
... })
>>> logging.getLogger("app").info("Ready")
{"timestamp":"2026-10-27T13:34:48.899+00:00","level":"INFO","logger":"app","message":"Ready"}
