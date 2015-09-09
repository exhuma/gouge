import logging

from blessings import Terminal


class Simple(logging.Formatter):
    """
    Fancy, colorised log output adding ANSI escape codes to the log output.

    :params show_threads: Whether to display thread names or not.
    """

    @staticmethod
    def basicConfig(*args, **kwargs):
        logging.basicConfig(*args, **kwargs)
        root = logging.getLogger()
        for handler in root.handlers:
            handler.setFormatter(Simple())

    def __init__(self, show_threads=False, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)
        self.show_threads = show_threads
        self.term = Terminal()

    def format(self, record):
        if record.levelno <= logging.DEBUG:
            colorize = self.term.bold_blue
        elif record.levelno <= logging.INFO:
            colorize = self.term.bold_magenta
        elif record.levelno <= logging.WARNING:
            colorize = self.term.bold_yellow
        elif record.levelno <= logging.ERROR:
            colorize = self.term.bold_cyan
        else:
            colorize = self.term.bold_yellow_on_red

        if self.show_threads:
            msg = '{} - '.format(record.threadName)
        else:
            msg = ''

        return msg + '{} - {} - [{}] - {}'.format(
            self.term.green(self.formatTime(record, self.datefmt)),
            colorize(record.levelname),
            record.name,
            record.getMessage()
        )
