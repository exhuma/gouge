"""
This module contains generally useful filters.
"""
import logging
from typing import Set
from warnings import warn


class ShiftingFilter:
    """
    This filter will shift the logging level of log records a certain number of
    log levels.

    For example:

    ``ShiftingFilter(1)`` will convert a message with level ``INFO`` to
    ``WARNING``, and ``ShiftingFilter(-1)`` will do the reverse.

    An example use-case is controlling log levels of libraries: It is possible
    that a library emits error-messages, but in the context of your application
    you would like to see those as *warning* messages only. If you have no
    control over that library your hands are tied and the only thing you can do
    is suppress these messages by changing the level of the associated logger.
    By modifying the log level using this filter still allows you to see the
    messages, albeit with another level which is more appropriate to your
    application.

    .. note::
        Filters can either be attached to handlers or loggers. But be aware that
        when attaching to loggers, they will only trigger on the exact logger
        they were attached to. Not in the parent hierarchy! See
        :py:meth:`logging.Filter.filter` for details. To simplify attaching to
        loggers, this class offers the method
        :py:meth:`~.ShiftingFilter.inject`.

    :param shift_by: The number of levels to shift. Positive integers will
        increase the level, negative integers will decrease it.
    :param logger: This and all child loggers will be shifted.
    :param min: Don't shift below this level.
    :param max: Don't shift above this level.
    :param offset: An explicit, fine-grained offset value. This overrides
        *shift_by*!
    """

    def __init__(
        self, shift_by=0, logger="", min=logging.NOTSET, max=logging.CRITICAL, offset=0
    ):
        # type: (int, str, int, int, int) -> None
        if offset and shift_by:
            warn(
                'You specified both "offset" and "shift_by"! "shift_by" '
                "will be ignored!",
                SyntaxWarning,
            )

        if offset:
            self.offset = offset
        else:
            self.offset = 10 * shift_by
        self.logger = logger
        self.max = max
        self.min = min
        self.injected_loggers = set()  # type: Set[logging.Logger]

    def inject(self, parent):
        # type: (str) -> None
        """
        Loop over each known logger and attach this filter.

        You can remove the attached filters again using
        :py:meth:`~.ShiftingFilter.cleanup`.

        .. note::
            This will only attach the filter to loggers which already exist! If
            you see that something is not working as expected, make sure the
            logger exists before calling this! You can look at all the existing
            loggers using ``logging.Logger.manager.loggerDict``.

        :param parent: Attach the filter to this and all descendant loggers.
        """
        if not isinstance(parent, str):
            parent = parent.name
        items = logging.Logger.manager.loggerDict.items()  # type: ignore
        for name, logger in items:
            if name.startswith(parent) and not isinstance(logger, logging.PlaceHolder):
                logger.addFilter(self)
                self.injected_loggers.add(logger)

    def cleanup(self):
        # type: () -> None
        """
        Remove all filters applied via :py:meth:`~.ShiftingFilter.inject`.
        """
        for logger in self.injected_loggers:
            logger.removeFilter(self)  # type: ignore

    def filter(self, record):
        # type: (logging.LogRecord) -> bool
        """
        Always returns *True* but will modify the logging level of *record* by
        the rules defined in this filter.

        See :py:meth:`logging.Filter.filter`
        """
        if record.name.startswith(self.logger):
            new_value = record.levelno + self.offset
            new_levelno = min(self.max, max(self.min, new_value))
            record.levelname = logging.getLevelName(new_levelno)
            record.levelno = new_levelno
        return True
