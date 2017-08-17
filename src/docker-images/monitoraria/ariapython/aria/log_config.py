from __future__ import absolute_import
import time
from threading import RLock
from logging import getLogger, handlers
import logging

class AriaLog(object):
    aria_log = getLogger("aria")
    aria_log_lock = RLock()
            
class LogConfiguration(object):
    was_init_once = False
    def __init__(self, log_level = logging.ERROR
                 , file_prefix = 'aria.log'
                 , file_max_size = 1024   # KB
                 , backup_count = 1024
                 , formatter = logging.Formatter("%(asctime)s [%(name)s][%(thread)d][%(process)d]:[%(levelname)s] %(filename)s:%(lineno)d %(message)s")
                 , file_handler = handlers.RotatingFileHandler):
        LogConfiguration.was_init_once = True
        self.fileHandler = file_handler
        self.file_name = file_prefix
        self.log_level = log_level
        self.file_name += time.strftime("%d_%m_%Y_%H_%M")
        self.formatter = formatter
        self.file_max_size =  file_max_size * 1024  # In B
        self.backup_count = backup_count
        self.file_handler = file_handler

def init_log(logConf):
    from logging import handlers
    import logging
    if logConf.file_handler == handlers.RotatingFileHandler:
        logConf.fileHandler = handlers.RotatingFileHandler(logConf.file_name, maxBytes=logConf.file_max_size, backupCount=logConf.backup_count)
        logConf.fileHandler.setFormatter(logConf.formatter)
    AriaLog.aria_log.addHandler(logConf.fileHandler)
    AriaLog.aria_log.setLevel(logConf.log_level)
