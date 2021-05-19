"""
This module contains functions for evaluating the passed arguments to the wrapper
functions and supplies the evaluated default values. 
There is no need to use this module directly.
"""

from pathlib import Path
from uuid import uuid4
import random

# dictionairy which maps the available image ids ti the corresponding directory path
default_images_path = Path(__file__).with_name("default_images").absolute()
default_pictures = {p.stem: p.absolute() for p in default_images_path.iterdir()}

# the names for the ui instances if they are not provided by the user
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

# for some ui entities default ids are provided so no alway a newpanel/tab gets
# cretaed if no id is provided
default_ids = {
    "Workspace": {
        "FusionSolidEnvironment": "ToolsTab",
        "FusionRenderEnvironment": "RenderTab",
        "CAMEnvironment": "UtilitiesTab",
    },
    "Tab": {"ToolsTab": "SolidScriptsAddinsPanel"},
}


def eval_id(value: str, instance=None) -> str:
    """[summary]

    Args:
        value (str): [description]
        instance ([type], optional): [description]. Defaults to None.

    Returns:
        str: [description]
    """
    if instance is not None and value == "default":
        value = default_ids.get(instance.parent.__class__.__name__, {}).get(
            instance.parent.id
        )
        if value is None:
            value = "random"
            # logging.info(
            #     f"There is no default id defined for a {instance.__class__.__name__} "
            #     + f"in {instance.parent.id} {instance.parent.__class__.__name__}, "
            #     + f"so a new {instance.__class__.__name__} will be used."
            # )
    if value == "random":
        value = str(uuid4())
    return value


def eval_name(value: str, cls) -> str:
    if value == "random":
        value = random.choice(random_names[cls.__name__])
    return value


def eval_image(value: str) -> str:
    if value in default_pictures:
        value = str(default_pictures[value])
    return value


def eval_image_path(value: str) -> str:
    if value in default_pictures:
        value = str(default_pictures[value] / "32x32.png")
    return value


def do_nothing(*args, **kwargs):
    pass
