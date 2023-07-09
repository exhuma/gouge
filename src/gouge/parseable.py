import csv
import io
import logging
from typing import Any, Optional


class CSVLog(logging.Formatter):
    """
    CSV formatter for python loggers.

    The columns correspond to the following fields:

    * created
    * filename
    * funcName
    * levelname
    * levelno
    * lineno
    * module
    * msecs
    * name
    * pathname
    * process
    * processName
    * relativeCreated
    * thread
    * threadName
    * message
    * exc_text
    """

    @staticmethod
    def basicConfig(**kwargs):
        # type: (Any) -> None
        logging.basicConfig(**kwargs)
        root = logging.getLogger()
        for handler in root.handlers:
            handler.setFormatter(CSVLog())

    def __init__(self, fmt=None, datefmt=None):
        # type: (Optional[str], Optional[str]) -> None
        logging.Formatter.__init__(self, fmt, datefmt)
        self.buffer = io.StringIO()
        self.writer = csv.writer(self.buffer)

    def format(self, record):
        # type: (logging.LogRecord) -> str

        record.message = record.getMessage()

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            exc_text = getattr(record, "exc_text", "")
            if not exc_text:
                record.exc_text = self.formatException(record.exc_info)  # type: ignore

        exc_text = getattr(record, "exc_text", "")
        message_items = [
            record.created,
            record.filename,
            record.funcName,
            record.levelname,
            record.levelno,
            record.lineno,
            record.module,
            record.msecs,
            record.name,
            record.pathname,
            record.process,
            record.processName,
            record.relativeCreated,
            record.thread,
            record.threadName,
            record.message,
            exc_text,
        ]

        self.writer.writerow(message_items)
        output = self.buffer.getvalue()
        self.buffer.seek(0)
        self.buffer.truncate()
        return output.strip()


class XMLLog(logging.Formatter):
    """
    XML formatter for python loggers.

    The records have the following schema::

        <record>
            <created />
            <filename />
            <funcName />
            <levelname />
            <levelno />
            <lineno />
            <module />
            <msecs />
            <name />
            <pathname />
            <process />
            <processName />
            <relativeCreated />
            <thread />
            <threadName />
            <message />
            <exc_text />
        </record>
    """

    @staticmethod
    def basicConfig(**kwargs):
        # type: (Any) -> None
        logging.basicConfig(**kwargs)
        root = logging.getLogger()
        for handler in root.handlers:
            handler.setFormatter(XMLLog())

    def __init__(self, fmt=None, datefmt=None):
        # type: (Optional[str], Optional[str]) -> None
        logging.Formatter.__init__(self, fmt, datefmt)
        from xml.dom.minidom import Document  # type: ignore

        self.doc = Document()

    def format(self, record):
        # type: (logging.LogRecord) -> str

        record.message = record.getMessage()

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            exc_text = getattr(record, "exc_text", "")
            if not exc_text:
                record.exc_text = self.formatException(record.exc_info)  # type: ignore

        exc_text = getattr(record, "exc_text", "")
        message_items = [
            ("created", record.created),
            ("filename", record.filename),
            ("funcName", record.funcName),
            ("levelname", record.levelname),
            ("levelno", record.levelno),
            ("lineno", record.lineno),
            ("module", record.module),
            ("msecs", record.msecs),
            ("name", record.name),
            ("pathname", record.pathname),
            ("process", record.process),
            ("processName", record.processName),
            ("relativeCreated", record.relativeCreated),
            ("thread", record.thread),
            ("threadName", record.threadName),
            ("message", record.message),
            ("exc_text", exc_text),
        ]

        element = self.doc.createElement("record")
        for tagname, value in message_items:
            subelement = self.doc.createElement(tagname)
            subelement.appendChild(self.doc.createTextNode(str(value)))
            element.appendChild(subelement)
        output = element.toxml()  # type: str
        return output
