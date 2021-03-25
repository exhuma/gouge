import logging
from logging import LogRecord

import pytest

from gouge.colourcli import Simple


@pytest.mark.parametrize(
    "level,color_code",
    [
        (logging.DEBUG, "\x1b[30mDEBUG"),
        (logging.INFO, "\x1b[36mINFO"),
        (logging.WARNING, "\x1b[33mWARNING"),
        (logging.ERROR, "\x1b[31mERROR"),
        (logging.CRITICAL, "\x1b[41mCRITICAL"),
    ],
)
def test_debug(level, color_code):
    fmt = Simple(force_styling=True)
    record = LogRecord("name", level, "pathname", 1, "msg", (), None)
    result = fmt.format(record)
    assert color_code in result
    assert "msg" in result
