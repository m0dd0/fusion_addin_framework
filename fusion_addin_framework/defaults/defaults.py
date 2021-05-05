from pathlib import Path
from uuid import uuid4
import random

from ..util import py_utils

### LOADING JSONS ###


default_images_path = Path(__file__).with_name("default_images").absolute()
default_pictures = {p.stem: p.absolute() for p in default_images_path.iterdir()}

# random_names_path = Path(__file__).with_name("random_names.json").absolute()
# random_names = py_utils.load_json_file(random_names_path)


### PARSING ###
random_names = {
    "Workspace": [
        "wobbling workspace",
        "wonderful workspace",
        "wolfish workspace",
        "wounded workspace",
        "woozy workspace",
    ],
    "Tab": [
        "talky tab",
        "taxpaying tab",
        "tapered tab",
        "tasty tab",
        "tai tab",
    ],
    "Panel": [
        "pale panel",
        "painful panel",
        "pacifisitc panel",
        "pacific panel",
    ],
    "_CommandWrapper": [
        "comic command",
        "cometic command",
        "comfy command",
        "cozy command",
        "corned command",
    ],
}

default_ids = {
    "Workspace": {
        "DesignWorkspace": "ToolsTab",
        "RenderWorkspace": "",
    },
    "Tab": {"SolidTab": "Select"},
}


def eval_id(value, parent=None):
    if parent is not None and value == "default":
        value = default_ids.get(parent.__class__.__name__, {}).get(parent.id)
        if value is None:
            logging.info()
            value = "random"
    if value == "random":
        return str(uuid4())
    return value


def eval_name(value, cls):
    if value == "random":
        return random.choice(random_names[cls.__name__])
    return value


def eval_image(value):
    if value is None:
        return None
    if value in default_pictures:
        return str(default_pictures[value])
    return value


def eval_image_path(value):
    if value is None:
        return None
    if value in default_pictures:
        return str(default_pictures[value] / "32x32.png")
    return value


def do_nothing(*args, **kwargs):
    pass
