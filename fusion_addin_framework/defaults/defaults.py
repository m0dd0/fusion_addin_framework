from pathlib import Path
from uuid import uuid4
import random

from ..util import py_utils

### LOADING JSONS ###


default_images_path = Path(__file__).with_name("default_images").absolute()
default_pictures = {p.stem: p.absolute() for p in default_images_path.iterdir()}

random_names_path = Path(__file__).with_name("random_names.json").absolute()
random_names = py_utils.load_json_file(random_names_path)


### PARSING ###


def eval_id(value):
    if value == "random":
        return str(uuid4())
    return value


def eval_name(value, cls):
    if value == "random":
        return random.choice(random_names[cls.__name__])
    return value


def eval_image(value):
    if value in default_pictures:
        return str(default_pictures[value])
    return str(value)


def do_nothing():
    pass
