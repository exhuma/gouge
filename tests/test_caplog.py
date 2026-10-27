import logging

import pytest

from gouge.colourcli import Simple


def test_caplog(caplog: pytest.LogCaptureFixture) -> None:
    """
    Using the pytest "caplog" fixture can cause trouble with the "Simple"
    formatter. This test uses the fixture, and should not cause any errors.
    """
    Simple.basicConfig(level=logging.DEBUG)
    logging.warning("Hello World")  # noqa: LOG015
    assert len(caplog.records) == 1
