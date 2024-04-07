"""
This module contains everything needed to emit colourful messages on the CLI
"""

import logging
import re
import sys
from logging import Handler, LogRecord
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional

import colorama as clr

P_FILENAME = re.compile(r"File \"([^\"]+)\", line (\d+), in ([^\s]+)")


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

    pre_formatters: Dict[str, List[Callable[[str], str]]]

    @staticmethod
    def basicConfig(
        show_exc: bool = True,
        show_threads: bool = False,
        force_styling: bool = False,
        show_pid: bool = False,
        highlighted_path: Optional[Path] = None,
        **kwargs: Any,
    ) -> List[Handler]:
        """
        Convenience method to have a one-liner set-up.

        *show_exc*, *show_threads*, *show_pid* and *force_styling* are directly
        passed to :py:class:`~.Simple`. The remaining *kwargs* are passed on to
        :py:func:`logging.basicConfig`.

        If *highlighted_path* is set, it will highlight local filenames in
        tracebacks. This is useful if you want to highlight the current working
        directory. If a "src" directory exists in the current working directory,
        it will be used as the default.

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

            handler.setFormatter(
                Simple(
                    show_exc=show_exc,
                    show_threads=show_threads,
                    show_pid=show_pid,
                    highlighted_path=highlighted_path,
                )
            )
            output.append(handler)
        return output

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = "%",
        validate: bool = True,
        *,
        defaults: Optional[Mapping[str, Any]] = None,
        show_exc: bool = False,
        show_threads: bool = False,
        force_styling: bool = False,
        show_pid: bool = False,
        pre_formatters: Optional[Dict[str, List[Callable[[str], str]]]] = None,
        highlighted_path: Optional[Path] = None,
    ):
        python_310_args = {"defaults": defaults, "validate": validate}
        if sys.version_info < (3, 10):
            python_310_args.pop("defaults")
        if sys.version_info < (3, 8):
            python_310_args.pop("validate")
        super().__init__(fmt, datefmt, style, **python_310_args)
        self.show_threads = show_threads
        self.show_exc = show_exc
        self.force_styling = force_styling
        self.show_pid = show_pid
        self.pre_formatters = pre_formatters or {}
        self.highlighted_path = highlighted_path
        if (Path.cwd() / "src").exists():
            self.highlighted_path = Path.cwd() / "src"
        else:
            self.highlighted_path = None

    def format(self, record: LogRecord) -> str:
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

        message = record.getMessage()
        for pre_formatter in self.pre_formatters.get(record.name, []):
            message = pre_formatter(message)
        record.message = message
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
            message_items.insert(
                0, "{s.BRIGHT}[PID: {process:<5}]{s.RESET_ALL}"
            )

        message_template = " ".join(message_items)

        if self.show_exc:
            if record.exc_info:
                # Cache the traceback text to avoid converting it multiple times
                # (it's constant anyway)
                exc_text = getattr(record, "exc_text", "")
                if not exc_text:
                    record.exc_text = self.formatException(record.exc_info)

            exc_text = getattr(record, "exc_text", "")
            if exc_text:
                if record.levelno >= logging.ERROR:
                    message_template += "\n{f.RED}"
                else:
                    message_template += "\n{f.WHITE}{s.DIM}"
                message_template += self.formatException(record.exc_info)
                message_template += "{s.RESET_ALL}"

        return message_template.format(
            levelcolor=colorize, f=clr.Fore, s=clr.Style, **vars(record)
        )

    def formatException(self, exc_info: tuple) -> str:
        exc_text = super().formatException(exc_info)
        if "{" in exc_text or "}" in exc_text:
            exc_text = exc_text.replace("{", "{{").replace("}", "}}")
        if self.highlighted_path is None:
            return exc_text

        pth = self.highlighted_path

        def highlight_local_filenames(match: re.Match) -> str:
            filename = Path(match.group(1))
            if filename.is_relative_to(pth):
                return match.group(0).replace(
                    match.group(1),
                    f"{clr.Fore.YELLOW}{match.group(1)}{clr.Fore.RED}",
                )
            return match.group(0)

        exc_text = P_FILENAME.sub(highlight_local_filenames, exc_text)
        return exc_text
