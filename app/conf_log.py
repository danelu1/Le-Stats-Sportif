'''
Module used to configure the logging of the webserver.
'''
import logging
from logging.handlers import RotatingFileHandler
import time

def conf_logging(webserver):
    '''
    Method used to configure the logging of the webserver.
    '''
    webserver.logger = logging.getLogger('webserver.log')
    webserver.logger.setLevel(logging.INFO)

    logging.Formatter.converter = time.gmtime
    formatter = logging.Formatter('%(asctime)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S GMT')

    file_handler = RotatingFileHandler('webserver.log',
                                    maxBytes=10000,
                                    backupCount=1)
    file_handler.setFormatter(formatter)

    webserver.logger.addHandler(file_handler)
