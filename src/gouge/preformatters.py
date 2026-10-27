"""
Pre-formatters: functions which rewrite the message of a record before
:py:class:`~gouge.colourcli.Simple` formats it.

A pre-formatter takes the message text and returns the new text. Map
logger names to pre-formatters with the *pre_formatters* option of
:py:class:`~gouge.colourcli.Simple`.
"""

import re

import colorama as clr

P_UVICORN_ACCESS = re.compile(
    r'^(?P<remote_host>\S+) - "'
    r"(?P<method>GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) "
    r'(?P<path>\S+) (?P<http>\S+)" (?P<status>\d+)'
)
METHOD_COLORS = {
    "GET": clr.Fore.GREEN,
    "POST": clr.Fore.YELLOW,
    "PUT": clr.Fore.YELLOW,
    "DELETE": clr.Fore.RED,
    "PATCH": clr.Fore.YELLOW,
    "HEAD": clr.Fore.GREEN,
    "OPTIONS": clr.Fore.GREEN,
}


def uvicorn_access(message: str) -> str:
    """
    Colour the access log lines of the ``uvicorn.access`` logger.

    The client address is blue, the method green, yellow or red, the path
    bright white, the HTTP version cyan, and the status code coloured by its
    class (2xx green, 3xx yellow, 4xx blue, 5xx yellow on red). A message
    in any other form is returned unchanged.

    :param message: The message of the record, with its arguments merged.
    :returns: The message with ANSI colour codes added.
    """
    match = P_UVICORN_ACCESS.match(message)
    if match:
        remote_host, method, path, http_version, status_code = match.groups()
        if int(status_code) >= 500:
            status_color = f"{clr.Back.RED}{clr.Fore.YELLOW}"
        elif int(status_code) >= 400:
            status_color = clr.Fore.BLUE
        elif int(status_code) >= 300:
            status_color = clr.Fore.YELLOW
        else:
            status_color = clr.Fore.GREEN
        method_color = METHOD_COLORS.get(method, clr.Fore.YELLOW)
        return (
            f"{clr.Fore.BLUE}{remote_host}{clr.Style.RESET_ALL}"
            ' - "'
            f"{method_color}{method}{clr.Style.RESET_ALL} "
            f"{clr.Style.BRIGHT}{clr.Fore.WHITE}{path}{clr.Style.RESET_ALL} "
            f"{clr.Fore.CYAN}{http_version}{clr.Style.RESET_ALL}"
            '" '
            f"{status_color}{status_code}{clr.Style.RESET_ALL}"
        )
    return message
