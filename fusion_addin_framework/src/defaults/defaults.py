from pathlib import Path
from functools import partial
import logging
import json
from copy import deepcopy
from uuid import uuid4
import random

# from ..util import py_utils

# ### import and load jsons ###

standard_defaults_path = Path(__file__).with_name("standard_defaults.json").absolute()
standard_defaults = json.loads(standard_defaults_path)

# custom_defaults_path = (
#     Path(__file__).joinpath("../../settings/standard_defaults.json").absolute()
# )

# default_pictures_path = Path(__file__).with_name("default_pictures").absolute()
# default_pictures = {p.stem(): p.absolute() for p in default_pictures_path.iterdir()}


# ### checker functions ###


# def picture_check(picture_type, value):
#     # TODO check when pictures are optional
#     # TODO load from extern (?)
#     sizes_by_type = {"workspace": {"49x31.png": False, "98x62.png": False}}

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


# def random_uuid(v):
#     if v == "random":
#         return uuid4()
#     return v


# def random_select(selection, v):
#     if v == "random":
#         return random.choice(selection)
#     return v


# def picture_parser(v):
#     if v in default_pictures:
#         return str(default_pictures[v])
#     return str(v)


# default_parsers = {
#     "workspace": {
#         "id": random_uuid,  # random, arbitrary string
#         "name": partial(
#             random_select, ["water workspace"]
#         ),  # random, arbitraty string # TODO laod from extern
#         "product_type": lambda v: v,  # ['Designproducttype']
#         "picture": picture_parser,  # pfad, random, ['lighbulb']
#         "picture_tooltip": lambda v: v,  # arbitrary string
#         "tooltip_head": lambda v: v,  # arbitrary string
#         "tooltip_text": lambda v: v,  # arbitrary string
#     },
#     "tab": {
#         "id": random_uuid,  # random, arbitrary string
#         "name": partial(random_select, ["toller tab"]),  # random, arbitraty string
#         "position_index": lambda v: v,  # arbitrary integer
#         "is_visible": lambda v: v,  # arbitrary bool
#     },
#     "panel": {
#         "id": random_uuid,  # random, arbitrary string
#         "name": partial(random_select, ["papa panel"]),  # random, arbitraty string
#         "position_index": lambda v: v,  # arbitrary integer
#         "is_visible": lambda v: v,  # arbitrary bool
#     },
# }


# ### calculate the default dict with inserted correct usr values ###

# # try to load custom defaults
# try:
#     custom_defaults = json.load(custom_defaults_path)
# except json.JSONDecodeError:
#     logging.warning(
#         "Couldnt decode custom default setting. Make sure to use proper "
#         "json encoding. Standard default settings are used."
#     )
#     custom_defaults = {}

# # flatten all the dict to make live easier,
# # abbreviation indicates flattened dict
# cstm_dflts = py_utils.flatten_dict(custom_defaults)
# std_dflts = py_utils.flatten_dict(standard_defaults)
# dflt_checks = py_utils.flatten_dict(default_checks)

# # drop all settings that whose keys is not in standard defaults
# unknown_custom_settings = set(cstm_dflts.keys()) - set(std_dflts.keys())
# if unknown_custom_settings:
#     logging.warning(
#         "The following default setttings are not known and will be ignored: {0}. "
#         "Check the Documentation for all available options".format(
#             unknown_custom_settings
#         )
#     )
# cstm_dflts = {k: v for k, v in cstm_dflts.items() if k not in unknown_custom_settings}

# # drop all settings whose value didnt pass the check
# for k, v in deepcopy(cstm_dflts).items():
#     if not dflt_checks[k](v):
#         logging.warning(
#             "The setting {0} is invalid and will be ignored. See the "
#             "documentation for information on custom default settings.".format(k)
#         )
#         cstm_dflts.pop(k)
# # cstm_dflts = {k: v for k, v in cstm_dflts.items() if dflt_checks[k + ("checks",)](v)}

# # create a dict with all settings, where cstm settings replace standards
# eff_dflts = deepcopy(std_dflts)
# eff_dflts.update(cstm_dflts)


# def get_default(*keys):
#     key = tuple(keys)
#     return default_parsers[key](eff_dflts[key])


# # def get_all_defaults(*keys):
# #     d = standard_defaults
# #     for k in keys:
# #         d = d[k]
# #     flat_keys = [tuple(keys + k) for k in d.keys()]
# #     return {k[-1]: get_default(*k) for k in flat_keys}


# def fill_args(args, cls_name):
#     given_args = {k: v for k, v in args.items() if k is not None}
#     args = {k: get_default(cls_name, k) for k in args if k is None}
#     return (args, given_args)

# # def fill_attrs(instance):
# #     type(instance).__name__.lower()

# def evaluate(inst, args):
#     given_args = {k: v for k, v in args.items() if k is not None}
#     args = {k: get_default(cls_name, k) for k in args if k is None}
#     return (args, given_args)


# random_names = {"workspace": ["www"], "tab": ["ttt"], "panel": ["ppp"]}

# default_pictures = {"lighbulb": ""}


# def name(val, choices_list, dflt):
#     if val is None:
#         val = dflt
#     if val == "random":
#         return random.choice(random_names[choices_list])
#     return val


# def id(val, dflt):
#     if val is None:
#         val = dflt
#     if val == "random":
#         return str(uuid4())
#     return val


# def picture(val, dflt):
#     if val is None:
#         val = dflt
#     if val in default_pictures:
#         return str(default_pictures[val])
#     return str(val)


# def no_parse(val, dflt):
#     if val is None:
#         val = dflt
#     return val

def evaluate(val, cls, attr):
