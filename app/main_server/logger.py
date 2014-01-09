#!/usr/bin/env python

"""
@file    Logger.py
@author  Remi Domingues
@date    30/07/2013

This file contains a logger class definition.
"""

import sys
import logging
import traceback

class Logger:    
    LOGGER_ID = "mainServer"
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
    INIT_TIMESTAMP = datetime.now()
    LOG_FILE_PATH = LOG_DIRECTORY + "/mainServer.log.{}.log".format(datetime.strftime(INIT_TIMESTAMP, "%d-%m-%Y_%Hh%Mm%Ss"))

    """
    Logger used in order to write error, warning and info messages
    in the user console and a log file
    """
    logger = logging.getLogger(LOGGER_ID)
    
    @staticmethod
    def init_logger():
        """
        Creates a log file and binds the logger with the output console and log file
        """
        hdlr = logging.FileHandler(LOG_FILE_PATH)
        formatter = logging.Formatter(LOG_FORMAT)
        hdlr.setFormatter(formatter)
        Logger.logger.addHandler(hdlr)
        Logger.logger.setLevel(LOG_LEVEL)
        
    @staticmethod
    def exception(e):
        """
        Write an exception stacktrace in the console and the log file
        """
        Logger.logger.exception(e)
        traceback.print_exc()

    @staticmethod
    def error(message):
        """
        Write an error message in the console and the log file
        """
        Logger.log_file(logging.ERROR, message)
        Logger.log_console(logging.ERROR, message)
    
    @staticmethod
    def info(message):
        """
        Write an info message in the console and the log file
        """
        Logger.log_file(logging.INFO, message)
        Logger.log_console(logging.INFO, message)

    @staticmethod
    def warning(message):
        """
        Write a warning message in the console and the log file
        """
        Logger.log_file(logging.WARNING, message)
        Logger.log_console(logging.WARNING, message)
        
    @staticmethod
    def info_file(message):
        """
        Write an info message in the log file
        """
        Logger.log_file(logging.INFO, message)
        
    @staticmethod
    def exception_file(e):
        """
        Write an exception stacktrace in the log file
        """
        Logger.logger.exception(e)

    @staticmethod
    def log_file(level, message):
        """
        Write a warning, error or info message in the log file
        """
        Logger.logger.log(level, message)
            
    @staticmethod
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
