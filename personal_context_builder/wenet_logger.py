""" Logger for wenet project

use syslog

"""
import logging
import logging.handlers
from personal_context_builder import config
import sys


def create_logger(name="wenet-undefined"):
    """create a logger with the correct configuration"""

    logger = logging.getLogger(name)
    logger.setLevel(config.DEFAULT_LOGGER_LEVEL)
    formatter = logging.Formatter(config.DEFAULT_LOGGER_FORMAT)

    log_file = logging.handlers.WatchedFileHandler(config.DEFAULT_LOG_FILE)
    ch = logging.StreamHandler()

    log_file.formatter = formatter
    ch.formatter = formatter

    logger.addHandler(log_file)
    logger.addHandler(ch)
    return logger


def create_web_logger_config():
    """create a logger for the sanic app"""
    return dict(
        version=1,
        disable_existing_loggers=False,
        loggers={
            "sanic.root": {"level": "INFO", "handlers": ["console", "log_file_1"]},
            "sanic.error": {
                "level": "INFO",
                "handlers": ["error_console", "log_file_1"],
                "propagate": True,
                "qualname": "sanic.error",
            },
            "sanic.access": {
                "level": "INFO",
                "handlers": ["access_console", "log_file_0"],
                "propagate": True,
                "qualname": "sanic.access",
            },
        },
        handlers={
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": sys.stdout,
            },
            "error_console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": sys.stderr,
            },
            "access_console": {
                "class": "logging.StreamHandler",
                "formatter": "access",
                "stream": sys.stdout,
            },
            "log_file_0": {
                "class": "logging.handlers.WatchedFileHandler",
                "filename": config.DEFAULT_LOG_FILE,
                "formatter": "access",
            },
            "log_file_1": {
                "class": "logging.handlers.WatchedFileHandler",
                "filename": config.DEFAULT_LOG_FILE,
                "formatter": "generic",
            },
        },
        formatters={
            "generic": {
                "format": config.DEFAULT_LOGGER_FORMAT,
                "class": "logging.Formatter",
            },
            "access": {
                "format": config.DEFAULT_SANIC_LOGGER_FORMAT,
                "class": "logging.Formatter",
            },
        },
    )
