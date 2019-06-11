""" Logger for wenet project

use syslog

"""
import logging
import logging.handlers
import config
import sys


def create_logger(name="wenet-undefined"):
    """ create a logger with the correct configuration
    """

    logger = logging.getLogger(name)
    logger.setLevel(config.DEFAULT_LOGGER_LEVEL)
    formatter = logging.Formatter(config.DEFAULT_LOGGER_FORMAT)

    syslog = logging.handlers.SysLogHandler("/dev/log")
    ch = logging.StreamHandler()

    syslog.formatter = formatter
    ch.formatter = formatter

    logger.addHandler(syslog)
    logger.addHandler(ch)
    return logger


def create_web_logger_config():
    """ create a logger for the sanic app
    """
    return dict(
        version=1,
        disable_existing_loggers=False,
        loggers={
            "sanic.root": {"level": "INFO", "handlers": ["console", "sys-logger1"]},
            "sanic.error": {
                "level": "INFO",
                "handlers": ["error_console", "sys-logger1"],
                "propagate": True,
                "qualname": "sanic.error",
            },
            "sanic.access": {
                "level": "INFO",
                "handlers": ["access_console", "sys-logger0"],
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
            "sys-logger0": {
                "class": "logging.handlers.SysLogHandler",
                "address": "/dev/log",
                "facility": "user",
                "formatter": "access",
            },
            "sys-logger1": {
                "class": "logging.handlers.SysLogHandler",
                "address": "/dev/log",
                "facility": "user",
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
