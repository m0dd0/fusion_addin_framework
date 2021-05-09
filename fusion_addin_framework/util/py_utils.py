"""This modules contains general utility function for working with python."""

from typing import Iterable, Dict
import logging


def flatten_dict(d: Dict) -> Dict:
    """Flattens a nested dictonairy. Keys will be tuples of keys from the nested dicts.

    Args:
        d (Dict): The dictionairy to flatten.

    Returns:
        Dict: The flattened dictionairy.
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
) -> logging.Logger:
    """Sets up a logger instance with the provided settings.

    The given level and format will be set to all passed handlers.
    It will be ensured that all handlers are removed before the handlers are added.
    This can be useful because they will not always get deleted when restarting
    your addin.

    Args:
        name (str): The name of the logger.
        handlers (Iterable[logging.Handler]): A list of handlers to connect to the logger.
        level (int, optional): The logger level. Defaults to logging.DEBUG.
        message_format (str, optional): The format string for the handlers. Defaults to "{asctime} {levelname} {module}/{funcName}: {message}".

    Returns:
        logging.Logger: The configured logger instance.
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