import re

from gouge.colourcli import clr

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
    A sample pre-formatter for the "uvicorn.access" logger
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
