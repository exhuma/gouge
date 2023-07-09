import io
import logging
from functools import partial

import pytest

from gouge.filters import ShiftingFilter

SimpleRecord = partial(
    logging.LogRecord, pathname="", lineno=0, msg="", args={}, exc_info=None
)


@pytest.fixture
def reset_logging():
    try:
        yield
    finally:
        logging.shutdown()
        for logger in logging.Logger.manager.loggerDict.values():
            if isinstance(logger, logging.PlaceHolder):
                continue
            del logger.handlers[:]
            del logger.filters[:]


def test_noshift():
    """
    A default instance should not shift anything
    """
    record = SimpleRecord(name="a.b.c", level=logging.DEBUG)
    filter_ = ShiftingFilter()
    filter_.filter(record)
    assert record.levelno == logging.DEBUG


def test_noshift_unmatching():
    """
    If the name does not match, no shifting should occur.
    """
    filter_ = ShiftingFilter(1, "foo.bar")
    record = SimpleRecord(name="a.b.c", level=logging.DEBUG)
    filter_.filter(record)
    assert record.levelno == logging.DEBUG


def test_noshift_parent():
    """
    Parent nodes should not be shifted.
    """
    filter_ = ShiftingFilter(1, "a.b.c")
    record = SimpleRecord(name="a.b", level=logging.DEBUG)
    filter_.filter(record)
    assert record.levelno == logging.DEBUG


def test_shift_fullmatch():
    """
    If the name matches exactly, we should shift
    """
    filter_ = ShiftingFilter(1, "a.b.c")
    record = SimpleRecord(name="a.b.c", level=logging.DEBUG)
    filter_.filter(record)
    assert record.levelno == logging.INFO


def test_shift_child():
    """
    Child nodes should be shifted
    """
    filter_ = ShiftingFilter(1, "a.b.c")
    record = SimpleRecord(name="a.b.c.d.e", level=logging.DEBUG)
    filter_.filter(record)
    assert record.levelno == logging.INFO


def test_shift_reversed():
    """
    We should also allow shifting in reverse.
    """
    filter_ = ShiftingFilter(-1)
    record = SimpleRecord(name="a.b.c", level=logging.INFO)
    filter_.filter(record)
    assert record.levelno == logging.DEBUG


def test_shift_fine_grained():
    """
    Instead of shifting by levels, the user should be allowed to shift by an
    exact offset.
    """
    filter_ = ShiftingFilter(offset=2)
    record = SimpleRecord(name="a.b.c", level=logging.NOTSET)
    filter_.filter(record)
    assert record.levelno == 2


def test_shift_min():
    """
    We should never go below level.NOTSET
    """
    filter_ = ShiftingFilter(-1)
    record = SimpleRecord(name="a.b.c", level=logging.NOTSET)
    filter_.filter(record)
    assert record.levelno == logging.NOTSET


def test_shift_max():
    """
    We also stop above logging.CRITICAL
    """
    filter_ = ShiftingFilter(1)
    record = SimpleRecord(name="a.b.c", level=logging.CRITICAL)
    filter_.filter(record)
    assert record.levelno == logging.CRITICAL


def test_shift_custom_min():
    """
    The user should have the option to refuse shifting below a certain
    level.
    """
    filter_ = ShiftingFilter(-1, min=logging.INFO)
    record = SimpleRecord(name="a.b.c", level=logging.INFO)
    filter_.filter(record)
    assert record.levelno == logging.INFO


def test_shift_custom_max():
    """
    The user should have the option to refuse shifting above a certain
    level.
    """
    filter_ = ShiftingFilter(1, max=logging.ERROR)
    record = SimpleRecord(name="a.b.c", level=logging.ERROR)
    filter_.filter(record)
    assert record.levelno == logging.ERROR


def test_shift_custom_min_outside_bounds():
    """
    We allow specifying a custom min value outside of the "standard" bounds.
    """
    filter_ = ShiftingFilter(-1, min=-10)
    record = SimpleRecord(name="a.b.c", level=logging.NOTSET)
    filter_.filter(record)
    assert record.levelno == -10


def test_shift_custom_max_outside_bounds():
    """
    We allow specifying a custom max value outside of the "standard" bounds.
    """
    filter_ = ShiftingFilter(1, max=60)
    record = SimpleRecord(name="a.b.c", level=logging.CRITICAL)
    filter_.filter(record)
    assert record.levelno == 60


def test_attached_to_handler(reset_logging):
    blob = io.StringIO()
    handler = logging.StreamHandler(blob)
    handler.setFormatter(logging.Formatter("%(levelno)s %(levelname)s %(msg)s"))
    handler.addFilter(ShiftingFilter(-1))
    logger_c = logging.getLogger("a.b.c")
    logger_d = logging.getLogger("a.b.d")
    logger_parent = logging.getLogger("a")
    logger_parent.setLevel(logging.DEBUG)
    logger_parent.addHandler(handler)

    logger_c.error("error - c")
    logger_d.info("info - d")
    logger_d.debug("debug - d")

    lines = blob.getvalue().splitlines()

    expected = [
        "30 WARNING error - c",
        "10 DEBUG info - d",
        "0 NOTSET debug - d",
    ]
    assert lines == expected


def test_attached_to_logger(reset_logging):
    blob = io.StringIO()
    handler = logging.StreamHandler(blob)
    handler.setFormatter(logging.Formatter("%(levelno)s %(levelname)s %(msg)s"))

    logger_c = logging.getLogger("a.b.c")
    logger_d = logging.getLogger("a.b.d")
    logger_parent = logging.getLogger("a")
    logger_parent.setLevel(logging.DEBUG)
    logger_parent.addHandler(handler)

    filter = ShiftingFilter(-1)
    filter.inject("a")

    logger_c.error("error - c")
    logger_d.info("info - d")
    logger_d.debug("debug - d")

    filter.cleanup()

    lines = blob.getvalue().splitlines()

    expected = [
        "30 WARNING error - c",
        "10 DEBUG info - d",
        "0 NOTSET debug - d",
    ]
    assert lines == expected
