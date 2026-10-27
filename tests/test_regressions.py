"""
Regression tests for bugs fixed in the 2.3 line.
"""

import io
import logging
import warnings
from typing import Any
from pathlib import Path

import pytest

from conftest import MakeRecord
from gouge.colourcli import P_ANSI, Simple
from gouge.filters import ShiftingFilter


def test_explicit_highlighted_path_wins_over_src(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Ensure an explicit *highlighted_path* beats the ``<cwd>/src`` default.
    """
    (tmp_path / "src").mkdir()
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(tmp_path)
    assert Simple(highlighted_path=other).highlighted_path == other.absolute()


def test_src_is_default_highlighted_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Ensure ``<cwd>/src`` is used when no path is given.
    """
    (tmp_path / "src").mkdir()
    monkeypatch.chdir(tmp_path)
    assert Simple().highlighted_path == (tmp_path / "src").absolute()


def test_no_highlighted_path_without_src(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Ensure nothing is highlighted without argument and without ``src``.
    """
    monkeypatch.chdir(tmp_path)
    assert Simple().highlighted_path is None


@pytest.mark.parametrize("force", [True, False])
def test_basic_config_forwards_force_styling(
    force: bool,
    restore_root_logger: logging.Logger,
    monkeypatch: pytest.MonkeyPatch,
    make_record: MakeRecord,
) -> None:
    """
    Ensure *force_styling* reaches the created formatter: it overrides
    ``NO_COLOR``, and without it the output is plain.
    """
    monkeypatch.setenv("NO_COLOR", "1")
    stream = io.StringIO()
    stream.name = "<stderr>"
    handlers = Simple.basicConfig(
        force_styling=force, stream=stream, force=True
    )
    assert handlers
    for handler in handlers:
        output = handler.format(make_record())
        assert bool(P_ANSI.search(output)) is force


def test_basic_config_with_stringio_stream(
    restore_root_logger: logging.Logger,
) -> None:
    """
    Ensure streams without a ``name`` (e.g. mocks) do not crash (issue #2).
    """
    restore_root_logger.handlers[:] = [logging.StreamHandler(io.StringIO())]
    assert Simple.basicConfig() == []


def test_basic_config_with_streamless_handler(
    restore_root_logger: logging.Logger,
) -> None:
    """
    Ensure handlers without a stream are skipped.
    """
    restore_root_logger.handlers[:] = [logging.NullHandler()]
    assert Simple.basicConfig() == []


@pytest.mark.parametrize("as_logger", [False, True])
def test_inject_accepts_name_or_logger(as_logger: bool) -> None:
    """
    Ensure ``inject`` works with a logger name and a logger instance.
    """
    child = logging.getLogger("gouge_test_inject.child")
    parent = logging.getLogger("gouge_test_inject")
    flt = ShiftingFilter(1)
    flt.inject(parent if as_logger else "gouge_test_inject")
    try:
        assert flt in child.filters
        assert flt in parent.filters
    finally:
        flt.cleanup()
    assert flt not in child.filters


def test_conflicting_arguments_warn_at_caller() -> None:
    """
    Ensure the warning keeps its category and points at the caller.
    """
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        ShiftingFilter(shift_by=1, offset=5)
    assert len(caught) == 1
    assert caught[0].category is SyntaxWarning
    assert caught[0].filename == __file__


@pytest.mark.parametrize("name", ["s", "f", "levelcolor"])
def test_extra_named_like_template_helper(name: str) -> None:
    """
    Ensure an extra attribute named like a template helper does not break
    formatting and does not change the output.
    """
    record = logging.LogRecord(
        "name", logging.INFO, "path", 1, "hello", None, None
    )
    expected = Simple().format(record)
    setattr(record, name, "boom")
    assert Simple().format(record) == expected


def test_old_style_format_exception_override_still_works(
    make_record: MakeRecord,
) -> None:
    """
    Ensure a 2.2.5 subclass with a required *exc_color* argument is only
    called with two arguments, and that ``exc_text`` stays plain.
    """

    class OldStyle(Simple):
        def formatException(  # type: ignore[override]
            self, exc_info: Any, exc_color: str
        ) -> str:
            return f"CUSTOM[{exc_color!r}] {exc_info[1]}"

    record = make_record(level=logging.ERROR, exc_info=True)
    output = OldStyle(show_exc=True, force_styling=True).format(record)
    assert "CUSTOM[" in output
    assert "boom" in output
    assert record.exc_text is not None
    assert "CUSTOM" not in record.exc_text
    assert not P_ANSI.search(record.exc_text)
    assert "Traceback" in record.exc_text
