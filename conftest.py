"""
Fixtures for the doctests in the documentation pages and the README.

Every page runs in the same process, so each one gets a clean slate: the
logging configuration, colorama's stream wrappers and the colour
environment variables are restored once the page has run.

So that the expected output in the pages is stable:

* ``NO_COLOR`` is set, so the output holds no escape codes. Pages which
  show colour codes set ``FORCE_COLOR`` or ``force_styling`` themselves.
* Log records get a fixed creation time, 2026-10-27 13:34:48.899 UTC, and
  :class:`~gouge.colourcli.Simple` renders times in UTC.
* A page runs in its own directory, so it can open files next to it.
* :data:`sys.stderr`, where :func:`logging.basicConfig` sends records by
  default, writes to the doctest's captured standard output, and the root
  logger starts without handlers.
"""

import logging
import sys
import time
from collections.abc import Generator, Iterator
from typing import Any

import colorama as clr
import pytest

#: The creation time of every record in a doctest.
CREATED = 1793108088.899


class _StderrToStdout:
    """
    Stand-in for :data:`sys.stderr` which writes to the current
    :data:`sys.stdout`, the stream doctest compares with the expected
    output. Its name is ``<stderr>``, like the real stream, so
    ``basicConfig`` helpers recognise the handler writing to it.
    """

    name = "<stderr>"
    closed = False

    def write(self, text: str) -> int:
        return sys.stdout.write(text)

    def flush(self) -> None:
        sys.stdout.flush()

    def isatty(self) -> bool:
        return False


def _logger_state(logger: logging.Logger) -> dict[str, Any]:
    return {
        "handlers": logger.handlers[:],
        "filters": logger.filters[:],
        "level": logger.level,
        "propagate": logger.propagate,
        "disabled": logger.disabled,
    }


def _restore_logging(saved: dict[str, dict[str, Any]]) -> None:
    """
    Restore the loggers in *saved* and reset every logger created since.
    """
    loggers: list[logging.Logger] = [logging.getLogger()]
    loggers += [
        item
        for item in logging.Logger.manager.loggerDict.values()
        if isinstance(item, logging.Logger)
    ]
    for logger in loggers:
        state = saved.get(
            logger.name,
            {
                "handlers": [],
                "filters": [],
                "level": logging.NOTSET,
                "propagate": True,
                "disabled": False,
            },
        )
        logger.handlers[:] = state["handlers"]
        logger.filters[:] = state["filters"]
        logger.setLevel(state["level"])
        logger.propagate = state["propagate"]
        logger.disabled = state["disabled"]


@pytest.fixture(autouse=True)
def doctest_environment(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> Iterator[None]:
    """
    Give every doctest page a clean, deterministic logging set-up.
    """
    if not isinstance(request.node, pytest.DoctestItem):
        yield
        return

    saved = {
        logger.name: _logger_state(logger)
        for logger in [logging.getLogger()]
        + [
            item
            for item in logging.Logger.manager.loggerDict.values()
            if isinstance(item, logging.Logger)
        ]
    }
    stdout, stderr = sys.stdout, sys.stderr
    factory = logging.getLogRecordFactory()

    def fixed_time_record(*args: Any, **kwargs: Any) -> logging.LogRecord:
        record = factory(*args, **kwargs)
        record.created = CREATED
        record.msecs = 899.0
        return record

    if request.node.path.suffix == ".rst":
        # Pages open files relative to themselves.
        monkeypatch.chdir(request.node.path.parent)
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setattr(logging.Formatter, "converter", time.gmtime)
    logging.setLogRecordFactory(fixed_time_record)
    try:
        yield
    finally:
        clr.deinit()
        sys.stdout, sys.stderr = stdout, stderr
        logging.setLogRecordFactory(factory)
        _restore_logging(saved)


@pytest.hookimpl(wrapper=True, trylast=True)
def pytest_runtest_call(item: pytest.Item) -> Generator[None, None, None]:
    """
    Run a doctest page with :data:`sys.stderr` sent to the doctest output
    and without handlers on the root logger, as in a fresh interpreter.

    This runs inside pytest's own capturing and log capturing, which
    replace :data:`sys.stderr` and add handlers to the root logger for
    every test phase.
    """
    if not isinstance(item, pytest.DoctestItem):
        return (yield)
    root = logging.getLogger()
    handlers = root.handlers[:]
    stdout, stderr = sys.stdout, sys.stderr
    root.handlers[:] = []
    sys.stderr = _StderrToStdout()  # type: ignore[assignment]
    try:
        return (yield)
    finally:
        # Undo colorama's stream wrappers, then put pytest's streams back:
        # deinit() restores whatever streams colorama last wrapped.
        clr.deinit()
        sys.stdout, sys.stderr = stdout, stderr
        root.handlers[:] = handlers
