"""Util functions to declare/define a robust logger + respective handlers/formatter"""
# Docs: https://docs.python.org/3/howto/logging-cookbook.html

import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

from meteoswiss_retriever.constants import LOG_DIR

# Log record format (with millisecond precision)
LOG_RECORD_MS_PRECISION_FMT: str = (
    "[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s] %(message)s"
)

# Log record format (with microsecond precision)
LOG_RECORD_US_PRECISION_FMT: str = (
    "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
)

# Date format for log record (asctime)
DATE_FMT: str = "%Y-%m-%dT%H:%M:%S"

# Common formatter definition
DEFAULT_FORMATTER = logging.Formatter(
    fmt=LOG_RECORD_MS_PRECISION_FMT,
    datefmt=DATE_FMT,
)
# TODO: Add JSON format later

# TODO: Add logstach (elastic)


class MicrosecondFormatter(logging.Formatter):
    """
    Logging formatter enabling microsecond formatting
    (overloading of built-in `logging.Formatter`)
    """

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        """
        Function to format time
        (overloading of logging.Formatter.formatTime(...))
        :param record: Log record
        :type record: logging.LogRecord
        :param datefmt: Date format (if specified)
        :type datefmt: str | None
        :return: Formatted time for a given log record instance
        :rtype: str
        """
        dt = datetime.fromtimestamp(record.created)
        if datefmt and isinstance(datefmt, str):
            return dt.strftime(datefmt)
        return dt.isoformat(timespec="microseconds")


def get_formatter() -> logging.Formatter:
    """
    Function to build a valid logging formatter
    :return: Formatter object
    :rtype: logging.Formatter
    """
    return MicrosecondFormatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    )
    # return DEFAULT_FORMATTER


def get_stream_handler() -> logging.Handler:
    """
    Function to build a valid logging stream handler
    (stdout/stderr)
    :return: Stream handler
    :rtype: logging.Handler
    """
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(get_formatter())
    return handler


def _get_file_handler_pathname() -> str:
    """
    Function to get valid pathname for a given file handler
    :return: Valid pathname
    :rtype: str
    """
    log_dir: Path = LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "main.log"
    return str(log_file)


def get_file_handler() -> logging.Handler:
    """
    Function to build a valid file handler
    :return: File handler
    :rtype: FileHandler
    """
    handler = logging.FileHandler(
        filename=_get_file_handler_pathname(), encoding="utf-8"
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(get_formatter())
    return handler


def get_time_rotating_file_handler() -> logging.Handler:
    """
    Function to build a valid timed rotating file handler
    :return: Timed rotating file handler
    :rtype: TimedRotatingFileHandler
    """
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=_get_file_handler_pathname(),
        when="midnight",  # daily rotation
        interval=1,
        backupCount=60,  # keep ~2 months
        encoding="utf-8",
        delay=False,
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(get_formatter())
    return handler


def setup_logger() -> None:
    """
    Function to set up a valid root (meteoswiss_retriever) logger
    This function **must** only be called on project's entry points
    It also disables external packages logging
    :return: Nothing
    :rtype: None
    """
    configure_external_logging()
    # print("Setup logger")

    # Root logger (meteoswiss_retriever)
    root_logger = logging.getLogger("meteoswiss_retriever")
    root_logger.setLevel(logging.DEBUG)  # Setting up DEBUG level to capture all logs
    root_logger.propagate = False

    # Cleaning existing handlers if necessary
    if root_logger.hasHandlers():
        return

    # Adding handlers
    root_logger.addHandler(get_stream_handler())
    root_logger.addHandler(get_file_handler())


def get_logger(name: str) -> logging.Logger:
    """
    Function to get a valid logger instance
    :param name: Logger name
    :type name: str
    :return: Valid logger instance
    :rtype: logging.Logger
    """
    if not name or name == "__main__":
        return logging.getLogger("meteoswiss_retriever")

    if not name.startswith("meteoswiss_retriever"):
        name = f"meteoswiss_retriever.{name}"
    # print(name)
    return logging.getLogger(name)


def configure_external_logging(log_level: int = logging.WARNING) -> None:
    """
    Function to configure external logging
    :return: Nothing
    :rtype: None
    """
    # Silencing all other loggers

    # Uvicorn
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.error").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(log_level)

    # SQLAlchemy
    logging.getLogger("sqlalchemy").setLevel(log_level)
    logging.getLogger("sqlalchemy.engine").setLevel(log_level)
    logging.getLogger("sqlalchemy.pool").setLevel(log_level)

    # HTTP libs
    logging.getLogger("urllib3").setLevel(log_level)
    logging.getLogger("httpx").setLevel(log_level)

    # Async noise
    logging.getLogger("asyncio").setLevel(log_level)

    return None
