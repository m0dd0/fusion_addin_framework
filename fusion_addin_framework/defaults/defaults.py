from pathlib import Path
from functools import partial
import logging
import json
from copy import deepcopy

from ..util import py_utils

### import and load jsons ###

default_pictures_path = Path(__file__).with_name("default_pictures")
default_pictures = {p.stem(): p.absolute() for p in default_pictures_path.iterdir()}

standard_defaults_path = Path(__file__).with_name("standard_defaults.json")
standard_defaults = json.loads(standard_defaults_path)


### checker functions ###


def picture_check(picture_type, value):
    sizes_by_type = {"workspace": {"49x31.png": False, "98x62.png": False}}

    # check if a default picure name was provided and set v to according path if so
    value = default_pictures.get(value, value)

    # parse value to string, should always work
    pic_dir = Path(str(value)).absolute()

    # check if path exists, return False if not
    if not pic_dir.exists():
        logging.warning(
            "The provided image path {0} for the {1} picture doesnt exist. This "
            "setting will be ignored.".format(pic_dir, picture_type)
        )
        return False

    # file names in the given pic_dir
    contained_files = [f.name for f in pic_dir.iterdir()]

    # check for all the pics that are needed
    for size, optional in sizes_by_type[picture_type].items():
        if size not in contained_files:
            if not optional:
                logging.warning(
                    "The provided image directory {0} for the {1} picture "
                    "doesnt contain the file '{2}'. This file is mandatory. "
                    "Therfore this setting will be ignored.".format(
                        pic_dir, picture_type, size
                    )
                )
                return False
            else:
                logging.warning(
                    "The provided image directory {0} for the {1} picture "
                    "doesnt contains the file '{2}'. Fusion will generate this "
                    "file automatically.".format(pic_dir, picture_type, size)
                )
        else:
            pass
            # TODO check for image size
            # (https://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib/9499976)

    # only if all non optional sizes are contained return true
    return True


### assign checker functions to every key/setting ###

default_checks = {
    "workspace": {
        "id": lambda v: isinstance(v, str),  # random, arbitrary string
        "name": lambda v: isinstance(v, str),  # random, arbitraty string
        "product_type": lambda v: v in ["DesignProducttype"],  # ['Designproducttype']
        # TODO check when pictures are optional # pfad, random, ['lighbulb']
        "picture": partial(
            picture_check, {"49x31.png": False, "98x62.png": False}, "workspace"
        ),
        "picture_tooltip": lambda v: isinstance(v, str),  # arbitrary string
        "tooltip_head": lambda v: isinstance(v, str),  # arbitrary string
        "tooltip_text": lambda v: isinstance(v, str),  # arbitrary string
    },
    "tab": {
        "id": lambda v: isinstance(v, str),  # random, arbitrary string
        "name": lambda v: isinstance(v, str),  # random, arbitraty string
        "position_index": lambda v: isinstance(v, int),  # arbitrary integer
        "is_visible": lambda v: isinstance(v, bool),  # arbitrary bool
    },
    "panel": {
        "id": lambda v: isinstance(v, str),  # random, arbitrary string
        "name": lambda v: isinstance(v, str),  # random, arbitraty string
        "position_index": lambda v: isinstance(v, int),  # arbitrary integer
        "is_visible": lambda v: isinstance(v, bool),  # arbitrary bool
    },
}


### calculate the default dict with inserted correct usr values ###


def effective_defaults(user_defaults_path):
    # try to load user defaults
    try:
        user_defaults = json.load(user_defaults_path)
    except json.JSONDecodeError:
        logging.warning(
            "Couldnt decode user default setting. Make sure to use proper "
            "json encoding. Standard default settings are used."
        )
        user_defaults = {}

    # flatten all the dict to make live easier,
    # abbreviation indicates flattened dict
    usr_dflts = py_utils.flatten_dict(user_defaults)
    std_dflts = py_utils.flatten_dict(standard_defaults)
    dflt_checks = py_utils.flatten_dict(default_checks)

    # drop all settings that whose keys is not in standard defaults
    unknown_user_settings = set(usr_dflts.keys()) - set(std_dflts.keys())
    if unknown_user_settings:
        logging.warning(
            "The following default setttings are not known and will be ignored: {0}. "
            "Check the Documentation for all available options".format(
                unknown_user_settings
            )
        )
    usr_dflts = {k: v for k, v in usr_dflts.items() if k not in unknown_user_settings}

    # drop all settings whose value didnt pass the check
    usr_dflts = {k: v for k, v in usr_dflts.items() if dflt_checks[k](v)}
    # usr_dflts = {k: v for k, v in usr_dflts.items() if dflt_checks[k + ("checks",)](v)}

    # create a dict with all settings, where usr settings replace standards
    eff_dflts = deepcopy(std_dflts)
    eff_dflts.update(usr_dflts)

    return eff_dflts
