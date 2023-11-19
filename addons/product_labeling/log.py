import logging
import os

from logging import Logger, handlers



def get_log() -> Logger:

    console_formatter = logging.Formatter(
        '%(levelname)s -- %(filename)s -- %(message)s'
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger = logging.getLogger(__name__)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

    return logger


log = get_log()
