import logging
from datetime import datetime
import os

def setup_custom_logger(name, log_level=logging.INFO):
    os.environ['TZ'] = 'Europe/Moscow'
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - key:%(name)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(handler)

    date = datetime.today().strftime("%Y%m%d_%H")
    file_handler = logging.FileHandler('{}.log'.format(date))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
