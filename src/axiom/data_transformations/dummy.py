import logging

logger = logging.getLogger(__name__)

def dummy(val):
    logger.info('djifisd')
    return f'hello {val}'