""" Logger for wenet project

use syslog

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,


"""
import logging
import logging.handlers
import sys

from personal_context_builder import config


def create_logger(name="wenet-undefined"):
    """create a logger with the correct configuration"""

    logger = logging.getLogger(name)
    logger.setLevel(config.PCB_LOGGER_LEVEL)
    formatter = logging.Formatter(config.PCB_LOGGER_FORMAT)

    log_file = logging.handlers.WatchedFileHandler(config.PCB_LOG_FILE)
    ch = logging.StreamHandler()

    log_file.formatter = formatter
    ch.formatter = formatter

    logger.addHandler(log_file)
    logger.addHandler(ch)
    return logger
