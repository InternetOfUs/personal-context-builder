""" Logger for wenet project

use syslog

"""
import logging
import logging.handlers
import config


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


def create_web_logger(name="wenet-App"):
    """ create a logger for the sanic app
    """
    logger = logging.getLogger(name)
    logger.setLevel(config.DEFAULT_LOGGER_LEVEL)
    formatter = logging.Formatter(config.DEFAULT_SANIC_LOGGER_FORMAT)

    syslog = logging.handlers.SysLogHandler("/dev/log")
    ch = logging.StreamHandler()

    syslog.formatter = formatter
    ch.formatter = formatter

    logger.addHandler(syslog)
    logger.addHandler(ch)
    return logger
