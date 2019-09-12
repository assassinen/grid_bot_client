import logging

def setup_custom_logger(name):
    logger = logging.getLogger(name)
    log_format = '%(asctime)s - %(name)s - %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)

    return logger