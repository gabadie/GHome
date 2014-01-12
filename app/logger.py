#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging
import traceback
from datetime import datetime


logger = logging.getLogger("ghome")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")

stream = logging.StreamHandler()
stream.setFormatter(formatter)
stream.setLevel(logging.INFO)
logger.addHandler(stream)

def add_file(logname):
    """
    Creates a log file and binds the logger with the output console and log file
    """
    dest_log = "{}.{}.log".format(logname, datetime.strftime(datetime.now(), "%Y-%m-%d_%Hh%Mm%Ss"))
    dest_dir = os.path.dirname(dest_log)

    if not os.path.exists(dest_dir):
        try:
            os.makedirs(os.path.dirname(dest_log))
        except:
            error("failed to add log " + dest_log + " : can't create directory " + dest_dir)
            return

    elif not os.path.isdir(dest_dir):
        error("failed to add log " + dest_log + " : " + dest_dir + " is not a directory")
        return

    hdlr = logging.FileHandler(dest_log)
    hdlr.setFormatter(formatter)
    hdlr.setLevel(logging.INFO)
    logger.addHandler(hdlr)

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
    logger.log(logging.ERROR, message)

def info(message):
    """
    Write an info message in the console and the log file
    """
    logger.log(logging.INFO, message)

def warning(message):
    """
    Write a warning message in the console and the log file
    """
    logger.log(logging.WARNING, message)
