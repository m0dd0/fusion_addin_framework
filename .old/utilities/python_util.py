"""[summary]
"""

import logging
from typing import Iterable
import threading
from functools import partial, wraps
import time
import os
from pathlib import Path
import json


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


class PeriodicExecuter(threading.Thread):
    def __init__(self, interval, func, args=[], kwargs={}):
        self.interval = interval
        self.func = partial(func, *args, **kwargs)

        self.thread_active = True
        threading.Thread.__init__(self)
        self.daemon = True

        self.start_time = time.perf_counter()
        self.running = False

        super().start()  # start the thread itself (not the 'timer')

    def run(self):
        elapsed_time = 0
        while self.thread_active:
            current_time = time.perf_counter()
            if self.running:
                elapsed_time = current_time - self.start_time
                if elapsed_time > self.interval:
                    self.func()
                    self.start_time = current_time
            else:
                self.start_time = current_time - elapsed_time

    def pause(self):
        self.running = False

    def start(self):
        self.running = True

    def reset(self):
        self.start_time = time.perf_counter()

    def kill(self):
        self.thread_active = False
        self.join()


def with_time_printed(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        start = time.perf_counter()
        return_val = func(*args, **kwargs)
        print('{0:<30} : {1}'.format(func.__name__,
                                     time.perf_counter() - start))
        return return_val

    return wrapped


def remove_suffix(s, suffix):
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    return s


def trim_from_substring(s, sub):
    index = s.find(sub)
    if index != -1:
        return s[0:index]
    return s


def get_json_from_file(  # pylint:disable = dangerous-default-value
        path, default_value={}):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    if not os.path.exists(path):
        with open(path, 'w+') as f:
            json.dump(default_value, f)  # do not add indent !!!
    with open(path, 'r+') as f:
        json_data = json.load(f)
    return json_data


def make_ordinal(n):
    '''
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    '''
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix
