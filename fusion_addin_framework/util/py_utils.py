"""[summary]

Returns:
    [type]: [description]
"""

from typing import Iterable
import logging
import json


def flatten_dict(d):
    """[summary]

    Args:
        d ([type]): [description]

    Returns:
        [type]: [description]
    """
    flattened = {}

    def _traverse_dict(d, upper_keys):
        for k, v in d.items():
            if isinstance(v, dict):
                _traverse_dict(d[k], upper_keys + [k])
            else:
                flattened[tuple(upper_keys + [k])] = v

    _traverse_dict(d, [])
    return flattened


def create_logger(
    name: str,
    handlers: Iterable[logging.Handler],
    level: int = logging.DEBUG,
    message_format: str = "{asctime} {levelname} {module}/{funcName}: {message}",
):
    """[summary]

    Args:
        name (str): [description]
        handlers (Iterable[logging.Handler]): [description]
        level (int, optional): [description]. Defaults to logging.DEBUG.
        message_format (str, optional): [description]. Defaults to "{asctime} {levelname} {module}/{funcName}: {message}".

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
    formatter = logging.Formatter(message_format, style="{")

    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)

    return logger


def load_json_file(path):
    """[summary]

    Args:
        path ([type]): [description]

    Returns:
        [type]: [description]
    """
    with open(path) as json_file:
        json_data = json.load(json_file)
    return json_data