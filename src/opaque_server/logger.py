import logging
import os
import sys

_RESET = "\033[0m"
_DIM = "\033[2m"
_LEVEL_COLORS = {
    logging.DEBUG: "\033[36m",       # cyan
    logging.INFO: "\033[32m",        # green
    logging.WARNING: "\033[33m",     # yellow
    logging.ERROR: "\033[31m",       # red
    logging.CRITICAL: "\033[1;41m",  # bold on red background
}


class TerminalFormatter(logging.Formatter):
    def __init__(self, use_color: bool):
        super().__init__(datefmt="%H:%M:%S")
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        time = self.formatTime(record, self.datefmt)
        level = f"{record.levelname:<8}"
        name = record.name

        if self.use_color:
            time = f"{_DIM}{time}{_RESET}"
            level = f"{_LEVEL_COLORS.get(record.levelno, '')}{level}{_RESET}"
            name = f"{_DIM}{name}{_RESET}"

        line = f"{time} | {level} | {name.upper()} | {record.getMessage()}"
        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)
        return line


def configure_logger(debug = True) -> None:
    use_color = sys.stderr.isatty() and "NO_COLOR" not in os.environ

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(TerminalFormatter(use_color))

    root = logging.getLogger()
    root.setLevel(logging.DEBUG if debug else logging.INFO)
    root.handlers = [handler]