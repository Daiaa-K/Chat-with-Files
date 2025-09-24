import logging
import os
from logging.handlers import RotatingFileHandler
from config.settings import settings

def logger_setup():
    
    # create logger
    logger = logging.getLogger(settings.APP_NAME)
    logger.setLevel(settings.LOG_LEVEL)

    # log file path
    log_path = os.path.join(settings.LOGS_DIR, settings.LOG_FILE)
    
    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # file handler
    file_handler = RotatingFileHandler(
        log_path, maxBytes=10*1024*1024, backupCount=5
    )
    
    file_handler.setFormatter(formatter)
    
    #console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = logger_setup()