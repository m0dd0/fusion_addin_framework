"""[summary]
"""

import logging
from typing import Iterable


def unique_string(all_strings: Iterable[str],
                  not_unique: str,
                  template: str = '{0}_{1}',
                  start: int = 1):
    """[summary]

    Args:
        all_strings (Iterable[str]): [description]
        not_unique (str): [description]
        template (str, optional): [description]. Defaults to '{0}_{1}'.
        start (int, optional): [description]. Defaults to 1.

    Returns:
        [type]: [description]
    """
    if not_unique not in all_strings:
        return not_unique
    while template.format(not_unique, start) in all_strings:
        start += 1
    return template.format(not_unique, start)


def create_default_logger(
    name: str,
    handlers: Iterable[logging.Handler],
    level: int = logging.DEBUG,
    message_format:
    str = '{asctime} {levelname} {module}/{funcName}: {message}',
):
    """[summary]

    Args:
        name (str): [description]
        handlers (Iterable[logging.Handler]): [description]
        level (int, optional): [description]. Defaults to logging.DEBUG.
        message_format (str, optional): [description].
            Defaults to '{asctime} {levelname} {module}/{funcName}: {message}'.

    Returns:
        [type]: [description]
    """

    logger = logging.getLogger(name)

    # logger always at lowest level set only handlers levels are set by level attribute
    logger.setLevel(logging.DEBUG)

    # delete allexisting handlers, to ensure no duplicated handler is added
    # when this method is called twice
    if logger.hasHandlers():
        logger.handlers.clear()

    # logging format (for all handlers)
    formatter = logging.Formatter(message_format, style='{')

    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)

    return logger
