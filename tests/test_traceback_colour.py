"""
Golden tests for the colours of tracebacks emitted by the "Simple" formatter.
"""

import importlib.util
import logging
from collections.abc import Callable
from logging import LogRecord
from pathlib import Path
from types import TracebackType

import pytest

from gouge.colourcli import P_ANSI, Simple

RED = "\x1b[31m"
DIM_WHITE = "\x1b[37m\x1b[2m"
YELLOW = "\x1b[33m"
RESET = "\x1b[0m"

ExcInfo = tuple[type[BaseException], BaseException, TracebackType]

MODULE_SOURCE = """\
def inner():
    raise ValueError("bad {value}")


def outer():
    inner()
"""


def raise_from(module_file: Path) -> ExcInfo:
    """
    Write a small module to *module_file*, call into it and return the
    resulting exception info (with a real traceback).
    """
    module_file.parent.mkdir(parents=True, exist_ok=True)
    module_file.write_text(MODULE_SOURCE)
    spec = importlib.util.spec_from_file_location("raiser", module_file)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    outer: Callable[[], None] = module.outer
    try:
        outer()
    except ValueError as exc:
        assert exc.__traceback__ is not None
        return (type(exc), exc, exc.__traceback__)
    raise AssertionError("The module did not raise")


def traceback_lines(level: int, formatter: Simple, exc: ExcInfo) -> list[str]:
    """
    Format a record carrying *exc* and return only the traceback lines.
    """
    record = LogRecord("name", level, "path", 1, "message", None, exc)
    return formatter.format(record).splitlines()[1:]


@pytest.fixture
def no_src(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Run in an empty working directory, so no "./src" default applies.
    """
    workdir = tmp_path / "work"
    workdir.mkdir()
    monkeypatch.chdir(workdir)
    return tmp_path


@pytest.mark.parametrize(
    "level, colour",
    [
        (logging.DEBUG, DIM_WHITE),
        (logging.INFO, DIM_WHITE),
        (logging.WARNING, DIM_WHITE),
        (logging.ERROR, RED),
        (logging.CRITICAL, RED),
    ],
    ids=["debug", "info", "warning", "error", "critical"],
)
def test_every_traceback_line_is_coloured(
    no_src: Path, level: int, colour: str
) -> None:
    """
    Ensure each traceback line starts with the exception colour and ends
    with a reset, so the colour does not depend on the previous line.
    """
    exc = raise_from(no_src / "lib" / "raiser.py")
    formatter = Simple(show_exc=True)

    lines = traceback_lines(level, formatter, exc)

    assert lines[0] == f"{colour}Traceback (most recent call last):{RESET}"
    assert lines[-1] == f"{colour}ValueError: bad {{value}}{RESET}"
    assert all(
        line.startswith(colour) and line.endswith(RESET) for line in lines
    )
    assert YELLOW not in "".join(lines)


@pytest.mark.parametrize(
    "level, colour",
    [(logging.DEBUG, DIM_WHITE), (logging.ERROR, RED)],
    ids=["debug", "error"],
)
def test_highlighted_path_keeps_line_colour(
    no_src: Path, level: int, colour: str
) -> None:
    """
    Ensure the text around a highlighted file name has the exception colour,
    the file name itself is yellow, and the full colour is restored after it.
    """
    module_file = no_src / "lib" / "raiser.py"
    exc = raise_from(module_file)
    formatter = Simple(show_exc=True, highlighted_path=no_src / "lib")

    lines = traceback_lines(level, formatter, exc)

    expected_inner = (
        f'{colour}  File "{YELLOW}{module_file}{colour}", '
        f"line 2, in inner{RESET}"
    )
    expected_outer = (
        f'{colour}  File "{YELLOW}{module_file}{colour}", '
        f"line 6, in outer{RESET}"
    )
    assert expected_outer in lines
    assert expected_inner in lines
    test_frame = next(line for line in lines if __file__ in line)
    assert test_frame.startswith(f'{colour}  File "{__file__}", line ')
    assert test_frame.endswith(RESET)
    assert YELLOW not in test_frame


def test_src_directory_is_highlighted_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Ensure files below "./src" are highlighted when no path is given.
    """
    monkeypatch.chdir(tmp_path)
    module_file = tmp_path / "src" / "raiser.py"
    exc = raise_from(module_file)
    formatter = Simple(show_exc=True)

    lines = traceback_lines(logging.ERROR, formatter, exc)

    assert (
        f'{RED}  File "{YELLOW}{module_file}{RED}", line 2, in inner{RESET}'
        in lines
    )


def test_coloured_traceback_matches_plain_text(no_src: Path) -> None:
    """
    Ensure colouring only adds escape codes: without them, the output is the
    plain traceback, including literal braces.
    """
    exc = raise_from(no_src / "lib" / "raiser.py")
    formatter = Simple(show_exc=True, highlighted_path=no_src / "lib")
    plain = logging.Formatter().formatException(exc)

    lines = traceback_lines(logging.ERROR, formatter, exc)

    assert P_ANSI.sub("", "\n".join(lines)) == plain
    assert "{value}" in plain


def test_exc_text_stays_plain(no_src: Path) -> None:
    """
    Ensure the cached ``record.exc_text`` holds no escape codes, so other
    handlers formatting the same record get a plain traceback.
    """
    exc = raise_from(no_src / "lib" / "raiser.py")
    formatter = Simple(show_exc=True, highlighted_path=no_src / "lib")
    record = LogRecord("name", logging.ERROR, "path", 1, "message", None, exc)

    formatter.format(record)

    assert record.exc_text == logging.Formatter().formatException(exc)
    assert "\x1b" not in logging.Formatter().format(record)


def test_cached_exc_text_without_exc_info(no_src: Path) -> None:
    """
    Ensure a record carrying only ``exc_text`` (for example one received
    from another process) still gets a coloured traceback.
    """
    record = LogRecord("name", logging.ERROR, "path", 1, "message", None, None)
    record.exc_text = "Traceback (most recent call last):\nKeyError: '{x}'"
    formatter = Simple(show_exc=True)

    lines = formatter.format(record).splitlines()[1:]

    assert lines == [
        f"{RED}Traceback (most recent call last):{RESET}",
        f"{RED}KeyError: '{{x}}'{RESET}",
    ]


def test_format_exception_api(no_src: Path) -> None:
    """
    Ensure ``formatException`` returns the plain traceback without a colour
    and a coloured one when a colour is given.
    """
    exc = raise_from(no_src / "lib" / "raiser.py")
    formatter = Simple(show_exc=True)
    plain = logging.Formatter().formatException(exc)

    coloured = formatter.formatException(exc, RED)

    assert formatter.formatException(exc) == plain
    assert coloured.splitlines() == [
        f"{RED}{line}{RESET}" for line in plain.splitlines()
    ]
