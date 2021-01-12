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

# picture_dependencies_path = (
#     Path(__file__).with_name("picture_dependencies.json").absolute()
# )
# picture_dependencies = json.loads(picture_dependencies_path)

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

# TODO use subfunctions
# try to load custom defaults
try:
    _custom_defaults = json.load(_custom_defaults_path)
except json.JSONDecodeError:
    logging.warning(
        "Couldnt decode custom default setting. Make sure to use proper "
        "json encoding. Standard default settings are used."
    )
    _custom_defaults = {}

# flatten all the dict to make live easier,
# abbreviation indicates flattened dict
_cstm_dflts = py_utils.flatten_dict(_custom_defaults)
_std_dflts = py_utils.flatten_dict(_standard_defaults)
# dflt_checks = py_utils.flatten_dict(default_checks)

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

# drop all settings whose value didnt pass the check
# for k, v in deepcopy(cstm_dflts).items():
#     if not dflt_checks[k](v):
#         logging.warning(
#             "The setting {0} is invalid and will be ignored. See the "
#             "documentation for information on custom default settings.".format(k)
#         )
#         cstm_dflts.pop(k)

# create a dict with all settings, where cstm settings replace standards
eff_dflts = deepcopy(_std_dflts)
eff_dflts.update(_cstm_dflts)


def evaluate(value, *keys):
    key = tuple(keys)
    if value is None:
        value = eff_dflts[key]
    return default_parsers[key](value)


# TODO implement atribute checking
# ### checker functions ###


# def picture_check(picture_type, value):
#     # check if a default picure name was provided and set v to according path if so
#     value = default_pictures.get(value, value)

#     # parse value to string, should always work
#     pic_dir = Path(str(value)).absolute()

#     # check if path exists, return False if not
#     if not pic_dir.exists():
#         logging.warning(
#             "The provided image path {0} for the {1} picture doesnt exist".format(
#                 pic_dir, picture_type
#             )
#         )
#         return False

#     # file names in the given pic_dir
#     contained_files = [f.name for f in pic_dir.iterdir()]

#     # check for all the pics that are needed
#     for size, optional in sizes_by_type[picture_type].items():
#         if size not in contained_files:
#             if not optional:
#                 logging.warning(
#                     "The provided image directory {0} for the {1} picture "
#                     "doesnt contain the file '{2}'. This file is mandatory.".format(
#                         pic_dir, picture_type, size
#                     )
#                 )
#                 return False
#             else:
#                 logging.warning(
#                     "The provided image directory {0} for the {1} picture "
#                     "doesnt contains the file '{2}'. Fusion will generate this "
#                     "file automatically.".format(pic_dir, picture_type, size)
#                 )
#         else:
#             pass
#             # TODO check for image size
#             # (https://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib/9499976)

#     # only if all non optional sizes are contained return true
#     return True


# ### assign checker functions to every key/setting ###

# default_checks = {
#     "workspace": {
#         "id": lambda v: isinstance(v, str),  # random, arbitrary string
#         "name": lambda v: isinstance(v, str),  # random, arbitraty string
#         "product_type": lambda v: v in ["DesignProducttype"],  # ['Designproducttype']
#         "picture": partial(picture_check, "workspace"),  # pfad, random, ['lighbulb']
#         "picture_tooltip": lambda v: isinstance(v, str),  # arbitrary string
#         "tooltip_head": lambda v: isinstance(v, str),  # arbitrary string
#         "tooltip_text": lambda v: isinstance(v, str),  # arbitrary string
#     },
#     "tab": {
#         "id": lambda v: isinstance(v, str),  # random, arbitrary string
#         "name": lambda v: isinstance(v, str),  # random, arbitraty string
#         "position_index": lambda v: isinstance(v, int),  # arbitrary integer
#         "is_visible": lambda v: isinstance(v, bool),  # arbitrary bool
#     },
#     "panel": {
#         "id": lambda v: isinstance(v, str),  # random, arbitrary string
#         "name": lambda v: isinstance(v, str),  # random, arbitraty string
#         "position_index": lambda v: isinstance(v, int),  # arbitrary integer
#         "is_visible": lambda v: isinstance(v, bool),  # arbitrary bool
#     },
# }
