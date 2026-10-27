"""
Tests for the NO_COLOR / FORCE_COLOR handling.
"""

import io
import logging

import colorama as clr
import pytest

from conftest import MakeRecord
from gouge.colourcli import P_ANSI, Simple, _colour_decision
from gouge.preformatters import uvicorn_access

ACCESS_LINE = '1.2.3.4 - "GET /x HTTP/1.1" 200'
BOOM = (ValueError, ValueError("boom"), None)


def _access(make_record: MakeRecord, exc: bool = False) -> logging.LogRecord:
    return make_record(
        ACCESS_LINE,
        name="uvicorn.access",
        level=logging.ERROR,
        exc_info=BOOM if exc else None,
        extras={"cid": "abc"},
    )


def _formatter(**kwargs: object) -> Simple:
    return Simple(
        datefmt="T",
        show_exc=True,
        show_extra=True,
        highlighted_path=None,
        pre_formatters={"uvicorn.access": [uvicorn_access]},
        **kwargs,  # type: ignore[arg-type]
    )


@pytest.mark.parametrize(
    "force,env,expected",
    [
        (False, {}, None),
        (False, {"NO_COLOR": ""}, None),
        (False, {"FORCE_COLOR": ""}, None),
        (False, {"NO_COLOR": "1"}, False),
        (False, {"FORCE_COLOR": "1"}, True),
        (False, {"NO_COLOR": "1", "FORCE_COLOR": "1"}, True),
        (False, {"NO_COLOR": "1", "FORCE_COLOR": ""}, False),
        (True, {}, True),
        (True, {"NO_COLOR": "1"}, True),
    ],
)
def test_precedence(
    monkeypatch: pytest.MonkeyPatch,
    force: bool,
    env: dict[str, str],
    expected: bool | None,
) -> None:
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    assert _colour_decision(force) is expected
    assert Simple(force_styling=force)._colour is expected


def test_default_output_is_unchanged(make_record: MakeRecord) -> None:
    assert _formatter().format(_access(make_record, exc=True)) == (
        "\x1b[32mT\x1b[0m \x1b[1m\x1b[31mERROR     \x1b[0m "
        "\x1b[1m[uvicorn.access]\x1b[0m \x1b[34m1.2.3.4\x1b[0m - "
        '"\x1b[32mGET\x1b[0m \x1b[1m\x1b[37m/x\x1b[0m '
        '\x1b[36mHTTP/1.1\x1b[0m" \x1b[32m200\x1b[0m '
        "\x1b[2mcid=abc\x1b[0m\n\x1b[31mValueError: boom\x1b[0m"
    )


def test_no_color_output_is_plain(
    monkeypatch: pytest.MonkeyPatch, make_record: MakeRecord
) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    assert _formatter().format(_access(make_record, exc=True)) == (
        'T ERROR      [uvicorn.access] 1.2.3.4 - "GET /x HTTP/1.1" 200 '
        "cid=abc\nValueError: boom"
    )


def test_no_color_highlighted_path_is_plain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    try:
        raise ValueError("x")
    except ValueError:
        import sys

        record = logging.LogRecord(
            "a", logging.ERROR, "p", 1, "m", (), sys.exc_info()
        )
    from pathlib import Path

    output = Simple(
        show_exc=True, highlighted_path=Path(__file__).parent
    ).format(record)
    assert "test_no_color.py" in output
    assert not P_ANSI.search(output)


def test_force_color_env_wins_over_nothing(
    monkeypatch: pytest.MonkeyPatch, make_record: MakeRecord
) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")
    assert "\x1b[" in _formatter().format(_access(make_record))


def test_force_styling_beats_no_color(
    monkeypatch: pytest.MonkeyPatch, make_record: MakeRecord
) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    assert "\x1b[" in _formatter(force_styling=True).format(
        _access(make_record)
    )


def test_empty_no_color_is_ignored(
    monkeypatch: pytest.MonkeyPatch, make_record: MakeRecord
) -> None:
    monkeypatch.setenv("NO_COLOR", "")
    assert "\x1b[" in _formatter().format(_access(make_record))


@pytest.mark.parametrize(
    "force,env,strip",
    [
        (False, {}, None),
        (True, {}, False),
        (False, {"FORCE_COLOR": "1"}, False),
        (False, {"NO_COLOR": "1"}, True),
        (True, {"NO_COLOR": "1"}, False),
    ],
)
def test_basic_config_colorama_strip(
    monkeypatch: pytest.MonkeyPatch,
    restore_root_logger: logging.Logger,
    force: bool,
    env: dict[str, str],
    strip: bool | None,
) -> None:
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    calls: list[object] = []
    monkeypatch.setattr(clr, "init", lambda **kw: calls.append(kw["strip"]))
    stream = io.StringIO()
    stream.name = "<stderr>"
    Simple.basicConfig(force_styling=force, stream=stream, force=True)
    assert calls == [strip]
