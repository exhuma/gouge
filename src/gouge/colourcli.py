"""
This module contains everything needed to emit colourful messages on the CLI
"""

import logging
import re
from collections.abc import Callable, Mapping
from logging import Handler, LogRecord
from pathlib import Path
from typing import Any, Literal

import colorama as clr

P_FILENAME = re.compile(r"File \"([^\"]+)\", line (\d+), in ([^\s]+)")


class Simple(logging.Formatter):
    """
    Fancy, colorised log output adding ANSI escape codes to the log output.

    :params show_threads: Whether to display thread names or not.
    :params show_exc: Whether to display tracebacks or not.
    :params highlighted_path: Local filenames below this path are highlighted
        in tracebacks. An explicitly given path always wins. If it is not
        given, ``<cwd>/src`` is used as the default when that directory
        exists, otherwise nothing is highlighted.

    .. note:: This formatter *suppresses* tracebacks by default! Remember that
        is is meant to give a concise, readable output. If you need to see
        tracebacks on the console, you can override this setting using
        *show_exc*.
    """

    pre_formatters: dict[str, list[Callable[[str], str]]]

    @staticmethod
    def basicConfig(
        show_exc: bool = True,
        show_threads: bool = False,
        force_styling: bool = False,
        show_pid: bool = False,
        highlighted_path: Path | None = None,
        **kwargs: Any,
    ) -> list[Handler]:
        """
        Convenience method to have a one-liner set-up.

        *show_exc*, *show_threads*, *show_pid* and *force_styling* are directly
        passed to :py:class:`~.Simple`. The remaining *kwargs* are passed on to
        :py:func:`logging.basicConfig`.

        If *highlighted_path* is set, it will highlight local filenames in
        tracebacks. This is useful if you want to highlight the current working
        directory. An explicitly given *highlighted_path* always wins. Only if
        it is not given and a "src" directory exists in the current working
        directory, that directory is used as the default.

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
                    force_styling=force_styling,
                    highlighted_path=highlighted_path,
                )
            )
            output.append(handler)
        return output

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        validate: bool = True,
        *,
        defaults: Mapping[str, Any] | None = None,
        show_exc: bool = False,
        show_threads: bool = False,
        force_styling: bool = False,
        show_pid: bool = False,
        pre_formatters: dict[str, list[Callable[[str], str]]] | None = None,
        highlighted_path: Path | None = None,
    ) -> None:
        super().__init__(
            fmt, datefmt, style, validate=validate, defaults=defaults
        )
        self.show_threads = show_threads
        self.show_exc = show_exc
        self.force_styling = force_styling
        self.show_pid = show_pid
        self.pre_formatters = pre_formatters or {}
        self.highlighted_path: Path | None
        if highlighted_path is not None:
            self.highlighted_path = highlighted_path.absolute()
        elif (Path.cwd() / "src").exists():
            self.highlighted_path = (Path.cwd() / "src").absolute()
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
        # The record goes first: an extra attribute named like one of the
        # template helpers must not break formatting.
        output = message_template.format_map(
            {
                **vars(record),
                "levelcolor": colorize,
                "f": clr.Fore,
                "s": clr.Style,
            }
        )

        if self.show_exc:
            if record.exc_info and not record.exc_text:
                # Cache the *plain* traceback, like the stdlib formatter
                # does. Other handlers may reuse ``record.exc_text``, so it
                # must not contain any escape codes.
                record.exc_text = self.formatException(record.exc_info)
            if record.exc_text:
                exc_color = (
                    clr.Fore.RED
                    if record.levelno >= logging.ERROR
                    else clr.Fore.WHITE + clr.Style.DIM
                )
                output += "\n" + self._colourise_traceback(
                    record.exc_text, exc_color
                )

        return output

    def formatException(self, exc_info: Any, exc_color: str = "") -> str:
        """
        Format the exception in *exc_info* as traceback text.

        Without *exc_color* the plain traceback is returned, exactly as
        :py:meth:`logging.Formatter.formatException` does. Otherwise each
        line is wrapped in *exc_color* and file names below
        *highlighted_path* are shown in yellow.

        :param exc_info: The exception tuple as returned by
            :py:func:`sys.exc_info`.
        :param exc_color: The ANSI escape sequence used for the traceback.
        """
        exc_text = super().formatException(exc_info)
        if not exc_color:
            return exc_text
        return self._colourise_traceback(exc_text, exc_color)

    def _colourise_traceback(self, exc_text: str, exc_color: str) -> str:
        """
        Colour every line of *exc_text* with *exc_color*.

        Each line starts with the colour and ends with a reset, so the
        colour survives viewers which reset the attributes per line.
        Highlighted file names are followed by *exc_color* again to
        restore the full traceback colour (foreground and style).
        """
        pth = self.highlighted_path

        def highlight_local_filenames(match: re.Match[str]) -> str:
            filename = Path(match.group(1)).absolute()
            if pth is not None and filename.is_relative_to(pth):
                return match.group(0).replace(
                    match.group(1),
                    f"{clr.Fore.YELLOW}{match.group(1)}{exc_color}",
                )
            return match.group(0)

        lines = []
        for line in exc_text.splitlines():
            if line:
                line = P_FILENAME.sub(highlight_local_filenames, line)
                line = f"{exc_color}{line}{clr.Style.RESET_ALL}"
            lines.append(line)
        return "\n".join(lines)
