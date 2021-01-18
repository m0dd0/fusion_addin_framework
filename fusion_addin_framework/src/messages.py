### FUSION WRAPPERS ###

# TODO use in setters
# def setting_on_native(type, id, not_setable):  # pylint:disable=redefined-builtin
#     msg = (
#         "The following arguments for the {0} (id: {1}) were ignored since "
#         "they cant be manipulated on a native {0}: {2}"
#     ).format(type, id, not_setable)
#     return msg


def already_existing(type, id, not_setable):  # pylint:disable=redefined-builtin
    msg = (
        "A {0} with this id ({1}) already exists. Therefore the following "
        "arguments will be ignored: {2}. If you want to change these properties, "
        "you can set them manually after creation if its not a native {0}."
    ).format(type, id, not_setable)
    return msg


def using_exisitng(type, id):  # pylint:disable=redefined-builtin
    msg = "Using existing {0}. (id: {1})".format(type, id)
    return msg


def created_new(type, id):  # pylint:disable=redefined-builtin
    msg = "Created a new {0}. (id: {1})".format(type, id)
    return msg


def button_not_empty(cmd_id):
    msg = "There is already a command {0} connected to this button.".format(cmd_id)
    return msg


### DEFAULTS ###


def unknown_defaults(unknown_custom_defaults):
    msg = (
        "The following custom defaults are not known and will be ignored: {0}. "
        "Check the Documentation for all available options."
    ).format(unknown_custom_defaults)
    return msg


def json_error_in_defaults():
    msg = (
        "Couldnt decode custom default setting. Make sure to use proper json "
        "encoding. Standard default settings are used."
    )
    return msg


### HANDLERS ###


def starting_handler(handler_type, cmd_name):
    msg = "Executing {0} handler of '{1}' command.".format(handler_type, cmd_name)
    return msg


### FRAMEWORK ERRORS ###


def default_evaluating_error(keys, value):
    msg = "Error while evaluating {0} defualt. Returning value {1}. SORRY THIS SHOULDNT HAPPEN.".format(
        keys, value
    )
    return msg