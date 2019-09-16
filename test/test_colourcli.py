"""
This module tests the log formatter which colorises messages
"""

import logging
from logging import LogRecord

from blessings import Terminal
from gouge.colourcli import Simple


def test_format_record_red_exception():
    """
    If the message level is higher or equal than "ERROR" we want to see the
    esception as red text. For lower levels we use another color.
    """
    record = LogRecord(
        'name',
        logging.ERROR,
        'path',
        42,
        'message',
        args={},
        exc_info=(ValueError, ValueError('foo'), None)
    )
    formatter = Simple(show_exc=True)
    terminal = Terminal(force_styling=True)
    formatter.term = terminal
    expected = terminal.red + 'ValueError'
    output = formatter.format(record)
    assert expected in output


def test_format_record_cyan_exception():
    """
    If the message level is higher or equal than "ERROR" we want to see the
    esception as red text. For lower levels we use cyan
    """
    record = LogRecord(
        'name',
        logging.DEBUG,
        'path',
        42,
        'message',
        args={},
        exc_info=(ValueError, ValueError('foo'), None)
    )
    formatter = Simple(show_exc=True)
    terminal = Terminal(force_styling=True)
    formatter.term = terminal
    expected = terminal.cyan + 'ValueError'
    output = formatter.format(record)
    assert expected in output
