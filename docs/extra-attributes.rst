Extra attributes and correlation IDs
====================================

.. versionadded:: 2.3

Log calls can carry values as attributes of the record, passed with
``extra={...}``. A :class:`logging.Filter` can add attributes as well, for
example the ID of the request being handled. Set ``show_extra`` to append
them to the message as ``key=value`` pairs. On a terminal they are dimmed.

Show every extra attribute
--------------------------

With ``show_extra=True``, every attribute which is not a standard
:class:`~logging.LogRecord` attribute and does not start with ``_`` is
shown, sorted by name:

>>> import logging
>>> from gouge.colourcli import Simple
>>> handlers = Simple.basicConfig(
...     level=logging.INFO,
...     show_extra=True,
... )
>>> log = logging.getLogger("app")
>>> log.warning(
...     "Order created",
...     extra={"order.id": 42, "user": "ana"},
... )
2026-10-27 13:34:48,899 WARNING    [app] Order created order.id=42 user=ana

Values are rendered with :class:`str`. A value which is empty or contains
whitespace is quoted with :func:`repr`, so the pairs stay easy to parse:

>>> log.warning(
...     "Renamed", extra={"title": "Q3 report"}
... )
2026-10-27 13:34:48,899 WARNING    [app] Renamed title='Q3 report'

Show selected attributes
------------------------

Give a sequence of names to show only those, in that order. Names a record
does not have are skipped:

>>> handlers = Simple.basicConfig(
...     show_extra=["user", "order.id"]
... )
>>> log.warning(
...     "Order created",
...     extra={"order.id": 42, "user": "ana"},
... )
2026-10-27 13:34:48,899 WARNING    [app] Order created user=ana order.id=42
>>> log.warning(
...     "Logged out", extra={"user": "ana"}
... )
2026-10-27 13:34:48,899 WARNING    [app] Logged out user=ana

Add a correlation ID
--------------------

A correlation ID ties together the records written while handling one
request. Keep the current ID in a :class:`~contextvars.ContextVar` and copy
it onto every record with a filter on the handler:

>>> import contextvars
>>> request_id = contextvars.ContextVar(
...     "request_id", default="-"
... )
>>> class RequestIdFilter(logging.Filter):
...     def filter(self, record):
...         record.request_id = request_id.get()
...         return True
>>> handlers = Simple.basicConfig(
...     show_extra=["request_id"]
... )
>>> for handler in handlers:
...     handler.addFilter(RequestIdFilter())
>>> token = request_id.set("4bf92f35")
>>> log.info("Payment accepted")
2026-10-27 13:34:48,899 INFO       [app] Payment accepted request_id=4bf92f35
>>> request_id.reset(token)
>>> log.info("Idle")
2026-10-27 13:34:48,899 INFO       [app] Idle request_id=-

Set the ID where a request starts, for example in a web framework's
middleware, and reset it when the request ends.

Before 2.3, showing such a field meant subclassing
:class:`~gouge.colourcli.Simple` and overriding
:meth:`~gouge.colourcli.Simple.format` to append it. Replace such a
subclass with the filter and ``show_extra``. The filter also puts the ID
into :class:`~gouge.parseable.JSONLog` output, which writes every extra
attribute (see :doc:`structured-output`).

OpenTelemetry trace IDs
-----------------------

The `OpenTelemetry logging instrumentation
<https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/logging/logging.html>`_
sets ``otelTraceID`` and ``otelSpanID`` on every record. gouge shows them as
``trace_id`` and ``span_id`` while a span is active, and leaves them out
otherwise. ``show_extra=True`` includes them; name them to show only the
trace IDs:

>>> handlers = Simple.basicConfig(
...     show_extra=["trace_id", "span_id"]
... )
>>> log.info(
...     "Charged",
...     extra={
...         "otelTraceID": "0af7651916cd43dd",
...         "otelSpanID": "b7ad6b71",
...     },
... )
2026-10-27 13:34:48,899 INFO       [app] Charged trace_id=0af7651916cd43dd span_id=b7ad6b71
