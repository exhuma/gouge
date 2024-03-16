from logging import LogRecord
import logging
from gouge.colourcli import Simple


def _dummy_preformatter(message: str) -> str:
    return "modified-message"


def test_preformatter():
    record = LogRecord(
        "the.logger",
        logging.INFO,
        "the-file",
        42,
        "the-message",
        None,
        None,
        None,
        None,
    )
    instance = Simple(pre_formatters={"the.logger": [_dummy_preformatter]})
    result = instance.format(record)
    assert "modified-message" in result
