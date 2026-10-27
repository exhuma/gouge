Running under uvicorn
=====================

.. versionadded:: 2.3

`uvicorn <https://www.uvicorn.org/>`_ installs its own handlers on its
loggers ``uvicorn``, ``uvicorn.error`` and ``uvicorn.access``, and stops
their records from reaching the root logger. A formatter configured on the
root logger therefore never sees them.
:func:`~gouge.uvicorn.capture_uvicorn` removes those handlers and lets the
records propagate. It does not import uvicorn.

Route uvicorn's records through gouge
-------------------------------------

Call :func:`~gouge.uvicorn.capture_uvicorn` *after* uvicorn has set up its
loggers, or uvicorn undoes it. A startup hook of the application is the
right place, for example a lifespan function:

>>> from contextlib import asynccontextmanager
>>> from gouge.uvicorn import capture_uvicorn
>>> @asynccontextmanager
... async def lifespan(app):
...     capture_uvicorn(level="INFO")
...     yield

Pass it to the application, for example ``FastAPI(lifespan=lifespan)`` or
``Starlette(lifespan=lifespan)``, and configure gouge as usual when the
program starts.

Alternatively, start uvicorn with ``log_config=None``. uvicorn then
installs no handlers, and only the propagation flags need to be fixed,
which :func:`~gouge.uvicorn.capture_uvicorn` does as well.

This example stands in for uvicorn. It sets up the access logger the way
uvicorn does, then captures it:

>>> import logging
>>> from gouge.colourcli import Simple
>>> handlers = Simple.basicConfig(
...     pre_formatters={
...         "uvicorn.access": [
...             "gouge.preformatters.uvicorn_access",
...         ],
...     },
... )
>>> access = logging.getLogger("uvicorn.access")
>>> access.addHandler(logging.NullHandler())
>>> access.propagate = False
>>> capture_uvicorn(level="INFO")
>>> access.info(
...     '%s - "%s %s HTTP/%s" %d',
...     "127.0.0.1:52341",
...     "GET", "/items", "1.1", 200,
... )
2026-10-27 13:34:48,899 INFO       [uvicorn.access] 127.0.0.1:52341 - "GET /items HTTP/1.1" 200

On a terminal, :func:`~gouge.preformatters.uvicorn_access` colours the
client address, method, path, HTTP version and status code (see
:doc:`pre-formatters`).

.. note::

   ``access_log=False`` makes uvicorn stop the propagation of
   ``uvicorn.access``. Calling :func:`~gouge.uvicorn.capture_uvicorn`
   afterwards turns it on again. To keep the access log off, pass only
   the other loggers:
   ``capture_uvicorn(loggers=["uvicorn", "uvicorn.error"])``.

Configure with dictConfig
-------------------------

When uvicorn reads a logging configuration file with ``--log-config``, it
uses that configuration instead of its own, so no capture is needed. Put
gouge's formatter and the uvicorn loggers in the file, as in the YAML
example in :doc:`configuring`.
