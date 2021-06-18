"""
This module contains functions for evaluating the passed arguments and supplies 
the random names names and default images.
"""

from pathlib import Path
from uuid import uuid4
import random

# dictionairy which maps the available image ids ti the corresponding directory path
default_images = {
    p.stem: p.absolute() for p in Path(__file__).with_name("default_images").iterdir()
}

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
    "AddinCommand": [
        "comic command",
        "cometic command",
        "comfy command",
        "cozy command",
        "corned command",
    ],
    "Dropdown": [
        "dusty dropdown",
        "demo dropdown",
        "dracula dropdown",
        "dominant dropdown",
        "dummy dropdown",
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
    """Evaluates the id argument of the wrapper classes.

    If the "random" keyword is passed a random uuid will be returned.
    If the instance attribute is given and the id is "default" the according
    default value will be looked up in the default_ids dict.

    Args:
        value (str): The provided id.
        instance ([type], optional): The wrapper instace from which this function
            is called. Defaults to None.

    Returns:
        str: The ultimately used id.
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
    """Returns a random name if value=="random".

    Args:
        value (str): The passed name.
        cls: The class of the instance for which the random name is intended.

    Returns:
        str: The ultimately used name.
    """
    if value == "random":
        value = random.choice(random_names.get(cls.__name__, ["Unnamed"]))
    return value


def eval_image(value: str, size=None) -> str:
    """Gets the path to an image directory or image path if the name is contained
    in the default image path directory.

    Args:
        value (str): Path or name of a default image.
        size ([type], optional): Size of the image. If None the path to the directory
            will be returned. Defaults to None.

    Returns:
        str: The path to the image or image directory.
    """
    if value in default_images:
        if size is not None:
            value = default_images[value] / size
        else:
            value = default_images[value]
    if isinstance(value, Path):
        value = value.as_posix()
    return value