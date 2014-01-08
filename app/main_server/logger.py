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
    def initLogger():
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
        Logger.logFile(logging.ERROR, message)
        Logger.logConsole(logging.ERROR, message)
    
    @staticmethod
    def info(message):
        """
        Write an info message in the console and the log file
        """
        Logger.logFile(logging.INFO, message)
        Logger.logConsole(logging.INFO, message)

    @staticmethod
    def warning(message):
        """
        Write a warning message in the console and the log file
        """
        Logger.logFile(logging.WARNING, message)
        Logger.logConsole(logging.WARNING, message)
        
    @staticmethod
    def infoFile(message):
        """
        Write an info message in the log file
        """
        Logger.logFile(logging.INFO, message)
        
    @staticmethod
    def exceptionFile(e):
        """
        Write an exception stacktrace in the log file
        """
        Logger.logger.exception(e)

    @staticmethod
    def logFile(level, message):
        """
        Write a warning, error or info message in the log file
        """
        Logger.logger.log(level, message)
            
    @staticmethod
    def logConsole(level, message):
        """
        Write a warning, error or info message in the console
        """
        if level == logging.INFO:
            print message
        if level == logging.WARNING:
            print "WARNING : " + message
        elif level == logging.ERROR:
            sys.stderr.write(message + '\n')
