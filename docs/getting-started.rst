Console output
==============

:class:`~gouge.colourcli.Simple` is the console formatter. Each line holds
the time, the level name padded to ten characters, the logger name in
brackets, and the message.

The examples on these pages show the output without colour. On a terminal,
the time is green, the level is coloured by severity, and the logger name
is bold.

Set up logging in one call
--------------------------

:meth:`Simple.basicConfig <gouge.colourcli.Simple.basicConfig>` calls
:func:`logging.basicConfig` and puts a :class:`~gouge.colourcli.Simple`
formatter on the handlers that write to standard error or standard output.
Keyword arguments that are not options of gouge go to
:func:`logging.basicConfig`:

>>> import logging
>>> from gouge.colourcli import Simple
>>> handlers = Simple.basicConfig(
...     level=logging.DEBUG
... )
>>> logging.getLogger("app").debug("Loading")
2026-10-27 13:34:48,899 DEBUG      [app] Loading

It returns the handlers it changed, so you can add filters to them:

>>> handlers
[<StreamHandler <stderr> (NOTSET)>]

Call it once, at the start of the program. Like
:func:`logging.basicConfig`, it only adds a handler if the root logger has
none, but it replaces the formatter of every console handler of the root
logger on each call.

Tracebacks
----------

:meth:`~gouge.colourcli.Simple.basicConfig` shows tracebacks by default.
Records of level ``ERROR`` and above get a red traceback, lower levels a
dimmed one:

>>> log = logging.getLogger("app")
>>> try:
...     1 / 0
... except ZeroDivisionError:
...     log.exception("Cannot compute")
2026-10-27 13:34:48,899 ERROR      [app] Cannot compute
Traceback (most recent call last):
  ...
ZeroDivisionError: division by zero

File names below ``highlighted_path`` are shown in yellow, so your own
frames stand out between those of libraries. It defaults to the ``src``
directory of the current working directory, if there is one. Set it
explicitly when your code lives elsewhere:

>>> from pathlib import Path
>>> handlers = Simple.basicConfig(
...     highlighted_path=Path("app")
... )

Pass ``show_exc=False`` to leave tracebacks out.

Process and thread
------------------

``show_pid`` and ``show_threads`` prefix each line with the process ID and
the thread name:

>>> handlers = Simple.basicConfig(
...     show_threads=True,
... )
>>> log.info("Polling")
MainThread 2026-10-27 13:34:48,899 INFO       [app] Polling

Add a handler yourself
----------------------

To keep other handlers untouched, create the formatter and attach it to a
handler of your choice. A formatter created this way does not show
tracebacks unless you pass ``show_exc=True``:

>>> handler = logging.StreamHandler()
>>> handler.setFormatter(Simple(show_exc=True))
>>> worker = logging.getLogger("worker")
>>> worker.addHandler(handler)
>>> worker.propagate = False
>>> worker.warning("Queue is empty")
2026-10-27 13:34:48,899 WARNING    [worker] Queue is empty

A formatter created directly emits colour codes even when the output is not
a terminal. :doc:`colour` explains how to control that.
