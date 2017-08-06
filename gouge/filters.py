"""
This module contains generally useful filters.
"""
import logging
from warnings import warn


class ShiftingFilter:
    """
    This filter will shift the logging level of log records a certain number of
    log levels.

    :param shift_by: The number of levels to shift. Positive integers will
        increase the level, negative integers will decrease it.
    :param logger: This and all child loggers will be shifted.
    :param min: Don't shift below this level.
    :param max: Don't shift above this level.
    :param offset: An explicit, fine-grained offset value. This overrides
        *shift_by*!
    """
    def __init__(self, shift_by=0, logger='',
                 min=logging.NOTSET, max=logging.CRITICAL, offset=0):
        if offset and shift_by:
            warn('You specified both "offset" and "shift_by"! "shift_by" '
                 'will be ignored!', SyntaxWarning)

        if offset:
            self.offset = offset
        else:
            self.offset = 10 * shift_by
        self.logger = logger
        self.max = max
        self.min = min

    def filter(self, record):
        """
        Always returns *True* but will modify the logging level of *record* by
        the rules defined in this filter.

        See :py:meth:`logging.filters.Filter.filter`
        """
        if record.name.startswith(self.logger):
            new_value = record.levelno + self.offset
            new_levelno = min(self.max, max(self.min, new_value))
            record.levelname = logging.getLevelName(new_levelno)
            record.levelno = new_levelno
        return True
