from pathlib import Path
from functools import partial
import json
from uuid import uuid4
import random
import logging
from types import SimpleNamespace

from ..util import py_utils
from .. import messages as msgs

### LOADING JSONS ###

_standard_defaults_path = Path(__file__).with_name("standard_defaults.json").absolute()
_standard_defaults = py_utils.load_json_file(_standard_defaults_path)

_custom_defaults_path = Path(__file__).parents[2] / "settings" / "custom_defaults.json"
try:
    _custom_defaults = py_utils.load_json_file(_custom_defaults_path)
except json.JSONDecodeError:
    logging.warning(msgs.json_error_in_defaults())
    _custom_defaults = {}

_default_images_path = Path(__file__).with_name("default_images").absolute()
_default_pictures = {p.stem: p.absolute() for p in _default_images_path.iterdir()}

_random_names_path = Path(__file__).with_name("random_names.json").absolute()
_random_names = py_utils.load_json_file(_random_names_path)


### PARSING ###
# the input values are parsed so that special values like "random" are evaluated
# no validation happens here


def _random_uuid(value):
    if value == "random":
        return str(uuid4())
    return value


def _random_select(selection, value):
    if value == "random":
        return random.choice(selection)
    return value


def _image_parser(value):
    if value in _default_pictures:
        return str(_default_pictures[value])
    return str(value)


# alias because it is also needed fom outside for dummy creation
def image_parser(value):
    return _image_parser(value)


def _image_file_parser(value, ending):
    pass


def _do_nothing():
    pass


def _func_parser(value):
    # default value is also None since functions cant be json serialized
    if value is None:
        return _do_nothing
    return value


_default_parsers = {
    "app": {
        "name": lambda v: v,
        "author": lambda v: v,
        "debug_to_ui": lambda v: v,
    },
    "workspace": {
        "id": _random_uuid,  # random or arbitrary string
        # random, arbitraty string
        "name": partial(_random_select, _random_names["workspace"]),
        "product_type": lambda v: v,  # ['Designproducttype']
        "image": _image_parser,  # pfad, random, [<default_images>]
        "tooltip_image": _image_parser,  # pfad, random, [<default_images>] # TODO different parser sinc the full image path is needed and not only the containing directory
        "tooltip_head": lambda v: v,  # arbitrary string
        "tooltip_text": lambda v: v,  # arbitrary string
    },
    "tab": {
        "id": _random_uuid,  # random, arbitrary string
        # random, arbitraty string
        "name": partial(_random_select, _random_names["tab"]),
    },
    "panel": {
        "id": _random_uuid,  # random, arbitrary string
        # random, arbitraty string
        "name": partial(_random_select, _random_names["panel"]),
        "position_index": lambda v: v,  # arbitrary integer
    },
    "button_command": {
        "id": _random_uuid,  # random, arbitrary string
        # random, arbitraty string
        "name": partial(_random_select, _random_names["command"]),
        "tooltip": lambda v: v,
        "image_tooltip": _image_parser,
        "image": _image_parser,
        "position_index": lambda v: v,
        "is_visible": lambda v: v,
        "is_enabled": lambda v: v,
        "is_promoted": lambda v: v,
        "is_promoted_by_default": lambda v: v,
        "on_created": _func_parser,
        "on_input_changed": _func_parser,
        "on_preview": _func_parser,
        "on_execute": _func_parser,
        "on_destroy": _func_parser,
        "on_key_down": _func_parser,
    },
    "button": {
        "position_index": lambda v: v,
        "is_visible": lambda v: v,
        "is_enabled": lambda v: v,
        "is_promoted": lambda v: v,
        "is_promoted_by_default": lambda v: v,
    },
}


### synthetisize the effective defaults

# flatten the dicts to make live easier
_custom_defaults_flat = py_utils.flatten_dict(_custom_defaults)
_standard_defaults_flat = py_utils.flatten_dict(_standard_defaults)

# drop all settings whose keys is not in standard defaults
_unknown_custom_defaults = set(_custom_defaults_flat.keys()) - set(
    _standard_defaults_flat.keys()
)
if _unknown_custom_defaults:
    logging.warning(msgs.unknown_defaults(_unknown_custom_defaults))
_custom_defaults_flat = {
    k: v for k, v in _custom_defaults_flat.items() if k not in _unknown_custom_defaults
}

# create a dict with all settings, where cstm settings replace standards
_standard_defaults_flat.update(_custom_defaults_flat)
_effective_defaults_flat = _standard_defaults_flat


def evaluate_constructor_locals(param_locals):
    param_locals.pop("self")
    current_class = param_locals.pop("__class__")

    parameter_names = list(param_locals.keys())
    for param_name in parameter_names:
        if param_locals[param_name] is None:
            param_locals[param_name] = _effective_defaults_flat.get(
                (current_class, param_name), None
            )
        else:
            # input validation could be done here
            pass

    return SimpleNamespace(**param_locals)