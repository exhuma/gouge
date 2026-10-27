"""
Helpers for running gouge's formatters under uvicorn.

This module is named ``uvicorn`` but never imports the uvicorn package (all
imports in gouge are absolute, so ``import uvicorn`` elsewhere still finds
the real one).
"""

import logging
from collections.abc import Sequence

#: The loggers :py:func:`capture_uvicorn` redirects by default.
UVICORN_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access")


def capture_uvicorn(
    level: int | str | None = None,
    loggers: Sequence[str] = UVICORN_LOGGERS,
) -> None:
    """
    Route uvicorn's log records through the root handlers.

    uvicorn installs its own handlers on its loggers and stops them from
    propagating, so the formatter configured on the root logger (for
    example with :py:meth:`Simple.basicConfig`) never sees them. This
    removes the handlers of *loggers* and enables propagation. uvicorn is
    not imported.

    Call it **after** uvicorn configured its loggers, or uvicorn's setup
    undoes it: either call it in a startup hook of the application (for
    example the FastAPI lifespan), or start uvicorn with ``log_config=None``
    so uvicorn does not install handlers in the first place (then only the
    ``propagate`` flags matter). Note that ``access_log=False`` makes
    uvicorn disable propagation of ``uvicorn.access``; calling this
    afterwards enables it again.

    :param level: Optional level to set on *loggers*.
    :param loggers: Names of the loggers to redirect. Defaults to
        ``uvicorn``, ``uvicorn.error`` and ``uvicorn.access``.
    """
    for name in loggers:
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.propagate = True
        if level is not None:
            logger.setLevel(level)
