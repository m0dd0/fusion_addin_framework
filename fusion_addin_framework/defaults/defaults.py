from pathlib import Path
from uuid import uuid4
import random

default_images_path = Path(__file__).with_name("default_images").absolute()
default_pictures = {p.stem: p.absolute() for p in default_images_path.iterdir()}

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
        "FusionSolidEnvironment": "ToolsTab",
        "FusionRenderEnvironment": "RenderTab",
        "CAMEnvironment": "UtilitiesTab",
    },
    "Tab": {"ToolsTab": "SolidScriptsAddinsPanel"},
}


def eval_id(value, instance=None):
    if instance is not None and value == "default":
        value = default_ids.get(instance.parent.__class__.__name__, {}).get(
            instance.parent.id
        )
        if value is None:
            # logging.info(
            #     f"There is no default id defined for a {instance.__class__.__name__} "
            #     + f"in {instance.parent.id} {instance.parent.__class__.__name__}, "
            #     + f"so a new {instance.__class__.__name__} will be used."
            # )
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
