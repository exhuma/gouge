"""
Colourful, human-readable log output for the console.
"""

import logging
import os
import pkgutil
import re
from collections.abc import Callable, Mapping, Sequence
from logging import Handler, LogRecord
from pathlib import Path
from typing import Any, Literal

import colorama as clr

from gouge._record import (
    cache_exc_text,
    extra_attributes,
    selected_attributes,
)

P_FILENAME = re.compile(r"File \"([^\"]+)\", line (\d+), in ([^\s]+)")
P_ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def _colour_decision(force_styling: bool = False) -> bool | None:
    """
    Decide whether output is coloured. This is the single place where that
    decision is taken; the environment is read at the time of the call.

    In order of precedence:

    1. *force_styling* is true: colour (``True``).
    2. Environment variable ``FORCE_COLOR`` set and not empty: colour.
    3. Environment variable ``NO_COLOR`` set and not empty: no colour
       (``False``), see https://no-color.org.
    4. Otherwise ``None``: the legacy behaviour. :py:class:`Simple` emits
       colour codes, and :py:meth:`Simple.basicConfig` lets colorama strip
       them if the stream is not a terminal.
    """
    if force_styling or os.environ.get("FORCE_COLOR"):
        return True
    if os.environ.get("NO_COLOR"):
        return False
    return None


def _resolve_pre_formatter(
    spec: Callable[[str], str] | str,
) -> Callable[[str], str]:
    """
    Return *spec* if it is callable, otherwise resolve it with
    :py:func:`pkgutil.resolve_name`. Both ``"package.module.function"`` and
    ``"package.module:function"`` are accepted.

    :raises ValueError: If a string cannot be resolved to a callable.
    """
    if not isinstance(spec, str):
        return spec
    try:
        resolved = pkgutil.resolve_name(spec)
    except (ValueError, ImportError, AttributeError) as exc:
        raise ValueError(
            f"Cannot import pre-formatter {spec!r}: {exc}"
        ) from exc
    if not callable(resolved):
        raise ValueError(f"Pre-formatter {spec!r} is not callable")
    result: Callable[[str], str] = resolved
    return result


#: Colour of the level name, by the highest level it applies to. Anything
#: above the last entry uses :py:data:`_CRITICAL_COLOUR`.
_LEVEL_COLOURS = (
    (logging.DEBUG, clr.Style.BRIGHT + clr.Fore.BLACK),
    (logging.INFO, clr.Fore.CYAN),
    (logging.WARNING, clr.Fore.YELLOW),
    (logging.ERROR, clr.Style.BRIGHT + clr.Fore.RED),
)
_CRITICAL_COLOUR = clr.Style.BRIGHT + clr.Fore.YELLOW + clr.Back.RED


def _level_colour(levelno: int) -> str:
    """
    Return the ANSI sequence used to colour the level name of a record.
    """
    for maximum, colour in _LEVEL_COLOURS:
        if levelno <= maximum:
            return colour
    return _CRITICAL_COLOUR


class Simple(logging.Formatter):
    """
    Console formatter which colours the level, logger name and traceback of
    each record with ANSI escape codes.

    Each line holds the time, the level name, the logger name in brackets
    and the message, optionally preceded by the process ID and thread name
    and followed by *extra* attributes.

    :param fmt: Passed on to :py:class:`logging.Formatter`.
    :param datefmt: Passed on to :py:class:`logging.Formatter`.
    :param style: Passed on to :py:class:`logging.Formatter`.
    :param validate: Passed on to :py:class:`logging.Formatter`.
    :param defaults: Passed on to :py:class:`logging.Formatter`.
    :param show_exc: Whether to append tracebacks to the message.
    :param show_threads: Whether to prefix each line with the thread name.
    :param force_styling: Emit colour codes even if ``NO_COLOR`` is set (see
        below).
    :param show_pid: Whether to prefix each line with the process ID.
    :param pre_formatters: Functions which rewrite the message of records
        of a given logger, as a mapping of logger name to a sequence of
        functions. Each item is either a callable taking and returning a
        :py:class:`str`, or a dotted path to one, such as
        ``"gouge.preformatters.uvicorn_access"``. Paths are imported once
        when the formatter is created, which makes this option usable from
        :py:func:`logging.config.dictConfig` and YAML files. Paths are
        resolved with :py:func:`pkgutil.resolve_name`, so both
        ``"package.module.function"`` and ``"package.module:function"``
        work. An invalid path raises :py:class:`ValueError` naming it. The
        ``pre_formatters`` attribute always holds callables.
    :param highlighted_path: Local filenames below this path are highlighted
        in tracebacks. An explicitly given path always wins. If it is not
        given, ``<cwd>/src`` is used as the default when that directory
        exists, otherwise nothing is highlighted.
    :param show_extra: Which *extra* attributes of a record to append to the
        message, as dimmed ``key=value`` pairs. Extra attributes are those
        passed with ``extra={...}`` to a log call or set by a filter.
        ``False`` (the default) shows none. ``True`` shows every attribute
        which is not a standard :py:class:`logging.LogRecord` attribute and
        does not start with ``_``, sorted by name. A sequence of names shows
        only those, in that order, and skips names the record does not have
        (a single string is taken as one name). Values are rendered with
        :py:class:`str`, or with :py:func:`repr` if that is empty or contains
        whitespace, so the pairs stay easy to parse. The OpenTelemetry IDs
        ``otelTraceID`` and ``otelSpanID`` are shown as ``trace_id`` and
        ``span_id`` when a span is active.

    Example, showing a correlation ID which a filter put on the records:

    >>> import logging
    >>> from gouge.colourcli import Simple
    >>> class CorrelationFilter(logging.Filter):
    ...     def filter(self, record):
    ...         record.correlation_id = "4bf92f35"
    ...         return True
    >>> handler = logging.StreamHandler()
    >>> handler.addFilter(CorrelationFilter())
    >>> handler.setFormatter(Simple(show_extra=True))
    >>> logging.getLogger().addHandler(handler)
    >>> logging.getLogger("app").warning(
    ...     "Order created", extra={"order.id": 42}
    ... )  # doctest: +NORMALIZE_WHITESPACE
    2026-10-27 13:34:48,899 WARNING    [app] Order created
    correlation_id=4bf92f35 order.id=42

    **Colour.** Whether colour codes are emitted is decided once, when the
    formatter is created (the environment is read at that point), in this
    order:

    1. *force_styling* is true: colour.
    2. Environment variable ``FORCE_COLOR`` set and not empty: colour.
    3. Environment variable ``NO_COLOR`` set and not empty
       (https://no-color.org): no colour. The output then contains no ANSI
       escape sequences at all, including those emitted by pre-formatters.
    4. Otherwise a directly created formatter emits colour codes, as it
       cannot know where its output goes. :py:meth:`basicConfig` lets
       colorama strip them when the stream is not a terminal.

    With :py:func:`logging.config.dictConfig`, use for example
    ``{"()": "gouge.colourcli.Simple", "pre_formatters":
    {"uvicorn.access": ["gouge.preformatters.uvicorn_access"]}}``.

    .. note::

        This formatter *suppresses* tracebacks by default, to keep the
        output concise. Pass ``show_exc=True`` to show them.
        :py:meth:`basicConfig` shows them by default.
    """

    pre_formatters: dict[str, list[Callable[[str], str]]]

    @staticmethod
    def basicConfig(
        show_exc: bool = True,
        show_threads: bool = False,
        force_styling: bool = False,
        show_pid: bool = False,
        highlighted_path: Path | None = None,
        *,
        show_extra: bool | Sequence[str] = False,
        pre_formatters: (
            Mapping[str, Sequence[Callable[[str], str] | str]] | None
        ) = None,
        **kwargs: Any,
    ) -> list[Handler]:
        """
        Configure logging with :py:func:`logging.basicConfig` and a
        :py:class:`Simple` formatter, in one call.

        *show_exc*, *show_threads*, *show_pid*, *force_styling*,
        *show_extra* and *pre_formatters* are directly passed to
        :py:class:`Simple`. The remaining *kwargs* are passed on to
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

        Colour follows the rules described in :py:class:`Simple`:
        *force_styling* or ``FORCE_COLOR`` switch colorama's stripping off,
        ``NO_COLOR`` makes it strip everything, and otherwise colorama strips
        the codes if the stream is not a terminal.

        :returns: The handlers whose formatter was replaced.
        """
        decision = _colour_decision(force_styling)
        clr.init(strip=(None if decision is None else not decision))
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
                    show_extra=show_extra,
                    pre_formatters=pre_formatters,
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
        pre_formatters: (
            Mapping[str, Sequence[Callable[[str], str] | str]] | None
        ) = None,
        highlighted_path: Path | None = None,
        show_extra: bool | Sequence[str] = False,
    ) -> None:
        super().__init__(
            fmt, datefmt, style, validate=validate, defaults=defaults
        )
        self.show_threads = show_threads
        self.show_exc = show_exc
        self.force_styling = force_styling
        self.show_pid = show_pid
        self._strip_colour = _colour_decision(force_styling) is False
        self.pre_formatters = {
            name: [_resolve_pre_formatter(item) for item in items]
            for name, items in (pre_formatters or {}).items()
        }
        self.show_extra: bool | tuple[str, ...]
        if isinstance(show_extra, str):
            self.show_extra = (show_extra,)
        elif isinstance(show_extra, bool):
            self.show_extra = show_extra
        else:
            self.show_extra = tuple(show_extra)
        self.highlighted_path: Path | None
        if highlighted_path is not None:
            self.highlighted_path = highlighted_path.absolute()
        elif (Path.cwd() / "src").exists():
            self.highlighted_path = (Path.cwd() / "src").absolute()
        else:
            self.highlighted_path = None

    def format(self, record: LogRecord) -> str:
        """
        Format *record* as one coloured line, followed by its traceback if
        *show_exc* is set.

        :param record: The record to format.
        :returns: The formatted text.
        """
        output = self._format(record)
        if self._strip_colour:
            output = P_ANSI.sub("", output)
        return output

    def _format(self, record: LogRecord) -> str:
        colorize = _level_colour(record.levelno)

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
        extras = self._format_extras(record)
        if extras:
            output += f" {clr.Style.DIM}{extras}{clr.Style.RESET_ALL}"

        if self.show_exc:
            output = self._append_traceback(output, record)

        return output

    def _append_traceback(self, output: str, record: LogRecord) -> str:
        """
        Return *output* followed by the coloured traceback of *record*, if
        it has one.
        """
        # Cache the *plain* traceback, like the stdlib formatter does.
        # Other handlers may reuse ``record.exc_text``, so it must not
        # contain any escape codes.
        cache_exc_text(record, self)
        if not record.exc_text:
            return output
        exc_color = (
            clr.Fore.RED
            if record.levelno >= logging.ERROR
            else clr.Fore.WHITE + clr.Style.DIM
        )
        if record.exc_info:
            # Go through the public hook, so subclasses overriding
            # formatException() change the console traceback (as in 2.2.5).
            traceback = self.formatException(record.exc_info, exc_color)
        else:
            traceback = self._colourise_traceback(record.exc_text, exc_color)
        return f"{output}\n{traceback}"

    def _format_extras(self, record: LogRecord) -> str:
        """
        Render the extra attributes selected by *show_extra* as
        space-separated ``key=value`` pairs.
        """
        if self.show_extra is False:
            return ""
        if self.show_extra is True:
            attributes = extra_attributes(record)
        else:
            attributes = selected_attributes(record, self.show_extra)
        return " ".join(
            f"{key}={_format_value(value)}" for key, value in attributes.items()
        )

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


def _format_value(value: object) -> str:
    """
    Render *value* for a ``key=value`` pair: :py:class:`str`, unless that is
    empty or contains whitespace, then :py:func:`repr` of that string.
    """
    text = str(value)
    if not text or any(char.isspace() for char in text):
        return repr(text)
    return text
