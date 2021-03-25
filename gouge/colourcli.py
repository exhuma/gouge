"""
This module contains everything needed to emit colourful messages on the CLI
"""
import logging
from logging import Handler, LogRecord
from typing import Any, List, Optional

import colorama as clr


class Simple(logging.Formatter):
    """
    Fancy, colorised log output adding ANSI escape codes to the log output.

    :params show_threads: Whether to display thread names or not.
    :params show_exc: Whether to display tracebacks or not.

    .. note:: This formatter *suppresses* tracebacks by default! Remember that
        is is meant to give a concise, readable output. If you need to see
        tracebacks on the console, you can override this setting using
        *show_exc*.
    """

    @staticmethod
    def basicConfig(
        show_exc=True, show_threads=False, force_styling=False, show_pid=False, **kwargs
    ):
        # type: (bool, bool, bool, bool, Any) -> List[Handler]
        """
        Convenience method to have a one-liner set-up.

        *show_exc*, *show_threads*, *show_pid* and *force_styling* are directly
        passed to :py:class:`~.Simple`. The remaining *kwargs* are passed on to
        :py:func:`logging.basicConfig`.

        After returning from :py:func:`logging.basicConfig`, it will fetch the
        *stderr* and *stdout* handlers and replace the formatter.

        The function also returns a list of all handlers which have been
        modified. This is useful if you want to modify the handlers any further
        (for example using :py:class:`~gouge.filters.ShiftingFilter`).
        """
        clr.init(strip=(False if force_styling else None))
        logging.basicConfig(**kwargs)
        root = logging.getLogger()
        output = []
        for handler in root.handlers:
            stream = getattr(handler, "stream", None)
            if not stream:
                continue

            stream_name = getattr(stream, "name", None)
            if stream_name not in ("<stderr>", "<stdout>"):
                continue

            handler.setFormatter(Simple(show_exc, show_threads, show_pid=show_pid))
            output.append(handler)
        return output

    def __init__(
        self,
        show_exc=False,
        show_threads=False,
        fmt=None,
        datefmt=None,
        force_styling=False,
        show_pid=False,
    ):
        # type: (bool, bool, Optional[str], Optional[str], bool, bool) -> None
        logging.Formatter.__init__(self, fmt, datefmt)
        self.show_threads = show_threads
        self.show_exc = show_exc
        self.force_styling = force_styling
        self.show_pid = show_pid

    def colorised_exception(self, level, exc_text):
        # type: (int, str) -> str
        """
        Colorises the exception text based on log level
        """
        if level >= logging.ERROR:
            output = "\n{f.RED}{exc_text}{s.RESET_ALL}"
        else:
            output = "\n{f.WHITE}{s.DIM}{exc_text}{s.RESET_ALL}"
        return output

    def format(self, record):
        # type: (LogRecord) -> str
        if record.levelno <= logging.DEBUG:
            colorize = clr.Style.BRIGHT + clr.Fore.BLACK
        elif record.levelno <= logging.INFO:
            colorize = clr.Fore.CYAN
        elif record.levelno <= logging.WARNING:
            colorize = clr.Fore.YELLOW
        elif record.levelno <= logging.ERROR:
            colorize = clr.Style.BRIGHT + clr.Fore.RED
        else:
            colorize = clr.Style.BRIGHT + clr.Fore.YELLOW + clr.Back.RED

        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt or "")

        message_items = [
            "{f.GREEN}{asctime}{s.RESET_ALL}",
            "{levelcolor}{levelname:<10}{s.RESET_ALL}",
            "{s.BRIGHT}[{name}]{s.RESET_ALL}",
            "{message}",
        ]
        if self.show_threads:
            message_items.insert(0, "{threadName:<10}")

        if self.show_pid:
            message_items.insert(0, "{s.BRIGHT}[PID: {process:<5}]{s.RESET_ALL}")

        message_template = " ".join(message_items)

        if self.show_exc:
            if record.exc_info:
                # Cache the traceback text to avoid converting it multiple times
                # (it's constant anyway)
                exc_text = getattr(record, "exc_text", "")
                if not exc_text:
                    record.exc_text = self.formatException(  # type: ignore
                        record.exc_info
                    )

            exc_text = getattr(record, "exc_text", "")
            if exc_text:
                message_template += self.colorised_exception(record.levelno, exc_text)

        return message_template.format(
            levelcolor=colorize, f=clr.Fore, s=clr.Style, **vars(record)
        )
