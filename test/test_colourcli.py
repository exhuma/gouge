"""
This module tests the log formatter which colorises messages
"""

import logging
import re
from logging import LogRecord

from gouge.colourcli import Simple


def test_format_record_red_exception():
    """
    If the message level is higher or equal than "ERROR" we want to see the
    esception as red text. For lower levels we use another color.
    """
    record = LogRecord(
        "name",
        logging.ERROR,
        "path",
        42,
        "message",
        args={},
        exc_info=(ValueError, ValueError("foo"), None),
    )
    formatter = Simple(show_exc=True)
    needle = "\x1b[31mValueError"
    output = formatter.format(record)
    assert needle in output


def test_format_record_grey_exception():
    """
    If the message level is higher or equal than "ERROR" we want to see the
    esception as red text. For lower levels we use grey
    """
    record = LogRecord(
        "name",
        logging.DEBUG,
        "path",
        42,
        "message",
        args={},
        exc_info=(ValueError, ValueError("foo"), None),
    )
    formatter = Simple(show_exc=True)
    needle = "\x1b[37m\x1b[2mValueError"
    output = formatter.format(record)
    assert needle in output


def test_show_pid():
    """
    Ensure the PID is visible if requested
    """
    record = LogRecord(
        "name", logging.DEBUG, "path", 42, "message", args={}, exc_info=None
    )
    formatter = Simple(show_pid=True)
    output = formatter.format(record)
    assert re.search(r"\[PID: \d+\s*\]", output)
