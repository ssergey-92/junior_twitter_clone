"""Module for creation project logger."""

from os import path as os_path, environ as os_environ
from pathlib import Path
from logging import DEBUG, Formatter, Logger, StreamHandler, getLogger
from logging.handlers import RotatingFileHandler


def get_logs_dir_path() -> str:
    """Get logs saving path.

    Returns:
        abs_path (str): logs saving abs path

    """
    log_path = os_environ.get("LOGS_PATH")
    if os_environ.get("PYTEST_LOGS"):
        log_path = os_path.join(
            os_path.dirname(os_path.realpath(__file__)), log_path,
        )

    return os_path.abspath(log_path)


def get_stream_handler() -> StreamHandler:
    """Create stream handler for project logger.

    Returns:
        StreamHandler : stream handler

    """
    stream_handler = StreamHandler()
    stream_handler.setLevel(DEBUG)
    formatter = Formatter(
        "*** "
        "%(asctime)s | %(name)s | %(funcName)s | %(levelname)s | %(message)s",
    )
    stream_handler.setFormatter(formatter)
    return stream_handler


def get_rotating_file_handler() -> RotatingFileHandler:
    """Create rotating file handler for project logger.

    Returns:
        RotatingFileHandler : rotating file handler

    """
    logs_path = get_logs_dir_path()
    create_directory(logs_path)
    logs_file_path = os_path.join(logs_path, "logs.log")
    rotating_file_handler = RotatingFileHandler(
        filename=logs_file_path,
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8",
    )
    rotating_file_handler.setLevel(DEBUG)
    formatter = Formatter(
        "%(asctime)s|%(name)s|%(funcName)s|%(levelname)s|%(message)s",
    )
    rotating_file_handler.setFormatter(formatter)
    return rotating_file_handler


def create_directory(abs_path: str) -> None:
    """Create path if it is not existed.

    Args:
        abs_path (str): abs path

    """
    Path(abs_path).mkdir(parents=True, exist_ok=True)


def get_project_logger(logger_name: str) -> Logger:
    """Create logger for project.

    Args:
        logger_name (str): name of logger

    Returns:
        Logger : instance of Logger
    """
    logger = getLogger(logger_name)
    logger.handlers.clear()
    for i_handler in (get_stream_handler(), get_rotating_file_handler()):
        logger.addHandler(i_handler)
    logger.setLevel(DEBUG)
    return logger


project_logger = get_project_logger("junior_twitter_clone")

