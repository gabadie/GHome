#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@file    py
@author  Remi Domingues
@date    30/07/2013

This file contains a logger class definition.
"""

import sys
import os
import logging
import traceback
from datetime import datetime

LOGGER_ID = "mainServer"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
INIT_TIMESTAMP = datetime.now()
LOG_DIRECTORY = "log"
LOG_FILE_PATH = LOG_DIRECTORY + "/mainServer.{}.log".format(datetime.strftime(INIT_TIMESTAMP, "%d-%m-%Y_%Hh%Mm%Ss"))

"""
used in order to write error, warning and info messages
in the user console and a log file
"""
logger = logging.getLOGGER_ID)

def init_logger():
    """
    Creates a log file and binds the logger with the output console and log file
    """
    hdlr = logging.FileHandler(LOG_FILE_PATH)
    formatter = logging.Formatter(LOG_FORMAT)
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(LOG_LEVEL)

def exception(e):
    """
    Write an exception stacktrace in the console and the log file
    """
    logger.exception(e)
    traceback.print_exc()

def error(message):
    """
    Write an error message in the console and the log file
    """
    log_file(logging.ERROR, message)
    log_console(logging.ERROR, message)

def info(message):
    """
    Write an info message in the console and the log file
    """
    log_file(logging.INFO, message)
    log_console(logging.INFO, message)

def warning(message):
    """
    Write a warning message in the console and the log file
    """
    log_file(logging.WARNING, message)
    log_console(logging.WARNING, message)

def info_file(message):
    """
    Write an info message in the log file
    """
    log_file(logging.INFO, message)

def exception_file(e):
    """
    Write an exception stacktrace in the log file
    """
    logger.exception(e)

def log_file(level, message):
    """
    Write a warning, error or info message in the log file
    """
    logger.log(level, message)

def log_console(level, message):
    """
    Write a warning, error or info message in the console
    """
    if level == logging.INFO:
        print message
    if level == logging.WARNING:
        print "WARNING : " + message
    elif level == logging.ERROR:
        sys.stderr.write(message + '\n')
