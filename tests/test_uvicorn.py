"""
Tests for :py:mod:`gouge.uvicorn`.
"""

import logging
from collections.abc import Iterator
from typing import Any

import pytest

from gouge.uvicorn import capture_uvicorn


@pytest.fixture
def uvicorn_loggers() -> Iterator[list[logging.Logger]]:
    loggers = [
        logging.getLogger(n)
        for n in ("uvicorn", "uvicorn.error", "uvicorn.access", "other")
    ]
    saved: list[Any] = [
        (lg.handlers[:], lg.propagate, lg.level) for lg in loggers
    ]
    try:
        yield loggers
    finally:
        for lg, (handlers, propagate, level) in zip(
            loggers, saved, strict=True
        ):
            lg.handlers[:] = handlers
            lg.propagate = propagate
            lg.setLevel(level)


def test_capture_uvicorn(uvicorn_loggers: list[logging.Logger]) -> None:
    for logger in uvicorn_loggers:
        logger.addHandler(logging.NullHandler())
        logger.propagate = False
    capture_uvicorn(level="WARNING")
    for logger in uvicorn_loggers[:3]:
        assert logger.handlers == []
        assert logger.propagate is True
        assert logger.level == logging.WARNING
    other = uvicorn_loggers[3]
    assert len(other.handlers) == 1
    assert other.propagate is False


def test_capture_uvicorn_custom_loggers_keep_level(
    uvicorn_loggers: list[logging.Logger],
) -> None:
    other = uvicorn_loggers[3]
    other.propagate = False
    capture_uvicorn(loggers=["other"])
    assert other.propagate is True
    assert other.level == logging.NOTSET
