# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from logging import DEBUG, INFO
from logging import Formatter, StreamHandler, getLogger, getLoggerClass

from sys import stdout
from pprint import PrettyPrinter



def create_logger(app):

    Logger = getLoggerClass()

    class DebugLogger(Logger):
        def getEffectiveLevel(x):
            if x.level == 0 and app.debug:
                return DEBUG
            return Logger.getEffectiveLevel(x)

    class DebugHandler(StreamHandler):

        def emit(x, record):
            pp = PrettyPrinter(indent=2)
            record.msg = pp.pformat(record.msg)
            StreamHandler.emit(x, record) if app.debug else None

    handler = DebugHandler()
    handler.setLevel(DEBUG)
    handler.setFormatter(Formatter(app.debug_log_format))
    logger = getLogger(app.logger_name)
    del logger.handlers[:]
    logger.__class__ = DebugLogger
    logger.addHandler(handler)
    logger.setLevel(DEBUG)

    return logger
