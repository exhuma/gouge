import logging
import sys
from collections.abc import Callable, Iterator
from typing import Any

import colorama as clr
import pytest

#: Signature of the ``make_record`` fixture.
MakeRecord = Callable[..., logging.LogRecord]

#: 2026-10-27T13:34:48.899 UTC
CREATED = 1793108088.899


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """
    Isolate every test from ``NO_COLOR`` / ``FORCE_COLOR`` in the developer's
    environment, and undo colorama's global initialisation afterwards.
    """
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    yield
    clr.deinit()


@pytest.fixture
def restore_root_logger() -> Iterator[logging.Logger]:
    """
    Save the root logger's handlers and level and restore them afterwards.
    """
    root = logging.getLogger()
    handlers = root.handlers[:]
    level = root.level
    root.handlers[:] = []
    try:
        yield root
    finally:
        root.handlers[:] = handlers
        root.setLevel(level)
        clr.deinit()


@pytest.fixture
def make_record() -> MakeRecord:
    """
    Return a factory for :py:class:`logging.LogRecord` objects.

    ``exc_info=True`` raises and captures a real ``ValueError("boom")``;
    an exception tuple is used as given. *extras* are set as attributes on
    the record, like ``extra={...}`` would do. *created* and *func* override
    the creation time and function name.
    """

    def factory(
        msg: str = "Order created",
        args: tuple[object, ...] | None = None,
        *,
        name: str = "app.orders",
        level: int = logging.WARNING,
        exc_info: Any = None,
        extras: dict[str, object] | None = None,
        created: float | None = None,
        func: str | None = None,
    ) -> logging.LogRecord:
        if exc_info is True:
            try:
                raise ValueError("boom")
            except ValueError:
                exc_info = sys.exc_info()
        record = logging.LogRecord(
            name,
            level,
            "/src/app.py",
            7,
            msg,
            args,
            exc_info or None,
            func=func,
        )
        if created is not None:
            record.created = created
        for key, value in (extras or {}).items():
            setattr(record, key, value)
        return record

    return factory
