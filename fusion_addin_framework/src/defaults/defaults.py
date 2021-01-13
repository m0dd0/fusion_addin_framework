from pathlib import Path
from functools import partial
import logging
import json
from copy import deepcopy
from uuid import uuid4
import random

from ..util import py_utils

### LOADING JSONS ###

_standard_defaults_path = Path(__file__).with_name("standard_defaults.json").absolute()
_standard_defaults = json.loads(_standard_defaults_path)

_custom_defaults_path = (
    Path(__file__).joinpath("../../settings/standard_defaults.json").absolute()
)
_custom_defaults = json.loads(_custom_defaults_path)

_default_images_path = Path(__file__).with_name("default_images").absolute()
_default_pictures = {p.stem(): p.absolute() for p in _default_images_path.iterdir()}

_random_names_path = Path(__file__).with_name("random_names.json").absolute()
_random_names = json.loads(_random_names_path)


### PARSING ###
# the input values are parsed so that special values like "random" are evaluated
# no validation happens here


def _random_uuid(value):
    if value == "random":
        return uuid4()
    return value


def _random_select(selection, value):
    if value == "random":
        return random.choice(selection)
    return value


def _image_parser(value):
    if value in _default_pictures:
        return str(_default_pictures[value])
    return str(value)


default_parsers = {
    "workspace": {
        "id": _random_uuid,  # random or arbitrary string
        # random, arbitraty string
        "name": partial(_random_select, _random_names["workspace"]),
        "product_type": lambda v: v,  # ['Designproducttype']
        "picture": _image_parser,  # pfad, random, [<default_images>]
        "picture_tooltip": lambda v: v,  # arbitrary string
        "tooltip_head": lambda v: v,  # arbitrary string
        "tooltip_text": lambda v: v,  # arbitrary string
    },
    "tab": {
        "id": _random_uuid,  # random, arbitrary string
        "name": partial(
            _random_select, _random_names["tab"]
        ),  # random, arbitraty string
        "position_index": lambda v: v,  # arbitrary integer
        "is_visible": lambda v: v,  # arbitrary bool
    },
    "panel": {
        "id": _random_uuid,  # random, arbitrary string
        # random, arbitraty string
        "name": partial(_random_select, _random_names["panel"]),
        "position_index": lambda v: v,  # arbitrary integer
        "is_visible": lambda v: v,  # arbitrary bool
    },
}


### COMPOSE DEFAULT DICT ###

# try to load custom defaults
try:
    _custom_defaults = json.load(_custom_defaults_path)
except json.JSONDecodeError:
    logging.warning(
        "Couldnt decode custom default setting. Make sure to use proper "
        "json encoding. Standard default settings are used."
    )
    _custom_defaults = {}

# flatten all the dict to make live easier, abbreviation indicates flattened dict
_cstm_dflts = py_utils.flatten_dict(_custom_defaults)
_std_dflts = py_utils.flatten_dict(_standard_defaults)

# drop all settings whose keys is not in standard defaults
_unknown_custom_settings = set(_cstm_dflts.keys()) - set(_std_dflts.keys())
if _unknown_custom_settings:
    logging.warning(
        "The following default setttings are not known and will be ignored: {0}. "
        "Check the Documentation for all available options".format(
            _unknown_custom_settings
        )
    )
_cstm_dflts = {
    k: v for k, v in _cstm_dflts.items() if k not in _unknown_custom_settings
}

# create a dict with all settings, where cstm settings replace standards
eff_dflts = deepcopy(_std_dflts)
eff_dflts.update(_cstm_dflts)


def evaluate(value, *keys):
    key = tuple(keys)
    if value is None:
        value = eff_dflts[key]
    return default_parsers[key](value)
