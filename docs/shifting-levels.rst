Shifting log levels
===================

.. versionadded:: 1.2

A library may log at a level that does not suit your application, for
example an ``ERROR`` for a failure it recovers from. Raising the level of
its logger hides those records altogether.
:class:`~gouge.filters.ShiftingFilter` keeps them but changes their level.

Shift the records of a library
------------------------------

``ShiftingFilter(shift_by, logger)`` moves the level of every record of
``logger`` and its children by ``shift_by`` steps. ``-1`` turns ``ERROR``
into ``WARNING``, ``1`` turns ``INFO`` into ``WARNING``. Attach it to a
handler, so it sees the records of every logger:

>>> import logging
>>> from gouge.colourcli import Simple
>>> from gouge.filters import ShiftingFilter
>>> handlers = Simple.basicConfig()
>>> for handler in handlers:
...     handler.addFilter(
...         ShiftingFilter(-1, logger="noisy")
...     )
>>> logging.getLogger("noisy.client").error(
...     "Connection reset, retrying"
... )
2026-10-27 13:34:48,899 WARNING    [noisy.client] Connection reset, retrying
>>> log = logging.getLogger("app")
>>> log.error("Payment failed")
2026-10-27 13:34:48,899 ERROR      [app] Payment failed

Levels are checked before filters run: a record must pass the level of its
logger and of the handler before the filter changes it. Shifting up
therefore cannot bring back records that these levels drop.

``min`` and ``max`` limit the result, and ``offset`` shifts by a number of
level values instead of steps (a step is 10):

>>> limited = ShiftingFilter(
...     2, max=logging.WARNING
... )

Attach to loggers
-----------------

A filter on a logger only sees records logged on exactly that logger, not
those of its children. :meth:`~gouge.filters.ShiftingFilter.inject`
attaches the filter to a logger and every existing descendant;
:meth:`~gouge.filters.ShiftingFilter.cleanup` removes it again:

>>> lib = logging.getLogger("lib")
>>> lib_db = logging.getLogger("lib.db")
>>> quiet = ShiftingFilter(-2)
>>> quiet.inject("lib")
>>> lib_db.error("Deadlock, retrying")
2026-10-27 13:34:48,899 INFO       [lib.db] Deadlock, retrying
>>> quiet.cleanup()

Loggers created after :meth:`~gouge.filters.ShiftingFilter.inject` do not
get the filter.
