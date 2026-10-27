import logging
from collections.abc import Iterator

import pytest


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
