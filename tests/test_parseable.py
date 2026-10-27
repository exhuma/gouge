"""
Tests for the machine-readable formatters.
"""

import csv
import io
import logging
from xml.dom.minidom import parseString

import pytest

from conftest import MakeRecord
from gouge.parseable import CSVLog, XMLLog


def test_csv_format_columns(make_record: MakeRecord) -> None:
    """
    Ensure a CSV row has the documented columns with the formatted message.
    """
    row = next(
        csv.reader(
            io.StringIO(
                CSVLog().format(
                    make_record("hello %s", ("world",), name="my.logger")
                )
            )
        )
    )
    assert len(row) == 17
    assert row[3] == "WARNING"
    assert row[4] == "30"
    assert row[5] == "7"
    assert row[8] == "my.logger"
    assert row[15] == "hello world"
    assert row[16] == ""


def test_csv_format_exception(make_record: MakeRecord) -> None:
    """
    Ensure the traceback text is placed in the last CSV column.
    """
    formatter = CSVLog()
    record = make_record(
        "hello %s", ("world",), name="my.logger", exc_info=True
    )
    row = next(csv.reader(io.StringIO(formatter.format(record))))
    assert "ValueError: boom" in row[16]
    assert "Traceback" in row[16]


def test_csv_is_stateless_between_records(make_record: MakeRecord) -> None:
    """
    Ensure consecutive records do not leak into each other.
    """
    formatter = CSVLog()
    formatter.format(make_record("hello %s", ("world",), name="my.logger"))
    output = formatter.format(
        make_record("hello %s", ("world",), name="my.logger")
    )
    assert len(list(csv.reader(io.StringIO(output)))) == 1


def test_xml_format_fields(make_record: MakeRecord) -> None:
    """
    Ensure the XML record contains the documented elements.
    """
    doc = parseString(
        XMLLog().format(make_record("hello %s", ("world",), name="my.logger"))
    )
    assert doc.documentElement is not None
    assert doc.documentElement.tagName == "record"

    def text(tag: str) -> str:
        node = doc.getElementsByTagName(tag)[0]
        return "".join(
            child.data for child in node.childNodes if hasattr(child, "data")
        )

    assert text("levelname") == "WARNING"
    assert text("levelno") == "30"
    assert text("name") == "my.logger"
    assert text("message") == "hello world"
    assert "Traceback" not in text("exc_text")


def test_xml_format_exception_is_escaped(make_record: MakeRecord) -> None:
    """
    Ensure the traceback text is included and is valid XML.
    """
    record = make_record(
        "hello %s", ("world",), name="my.logger", exc_info=True
    )
    record.msg = "a <b> & c"
    record.args = ()
    doc = parseString(XMLLog().format(record))
    exc_node = doc.getElementsByTagName("exc_text")[0]
    assert "ValueError: boom" in exc_node.firstChild.data  # type: ignore[union-attr]
    msg_node = doc.getElementsByTagName("message")[0]
    assert msg_node.firstChild.data == "a <b> & c"  # type: ignore[union-attr]


@pytest.mark.parametrize("cls", [CSVLog, XMLLog])
def test_basic_config(
    cls: type[CSVLog] | type[XMLLog], restore_root_logger: logging.Logger
) -> None:
    """
    Ensure basicConfig installs the formatter on the root handlers.
    """
    stream = io.StringIO()
    cls.basicConfig(stream=stream, force=True, level=logging.INFO)
    logging.getLogger("x").info("hi")
    assert all(
        isinstance(h.formatter, cls) for h in restore_root_logger.handlers
    )
    assert "hi" in stream.getvalue()
