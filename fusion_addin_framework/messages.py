### FUSION WRAPPERS ###


def using_exisitng(cls, id):  # pylint:disable=redefined-builtin
    msg = (
        "Using existing {0} (id: {1})."
        # "All arguments except 'id' will be "
        # "ignored. If you want to change properties of this {0}, you can "
        # "access and set the attributes if its not a native {0}."
    ).format(cls.__name__, id)
    return msg


def created_new(cls, id):  # pylint:disable=redefined-builtin
    msg = f"Created a new {cls.__name__}. (id: {id})"
    return msg


### HANDLERS ###


def starting_handler(handler_type, cmd_name):
    msg = f"Executing {handler_type} handler of '{cmd_name}' command."
    return msg


def handler_error(handler_type, command_name, traceback):
    msg = f"Error in {handler_type} of {command_name} command:\n{traceback}"
    return msg


def doubled_callbacks(event_name):
    msg = (
        f"Two or more callback functions for the {event_name} event were provided. "
        + "Only the last one will get used."
    )
    return msg


### MISCELLANEOUS ###


def no_appdirs():
    msg = (
        "The appdirs package is not installed. Using path related attributes "
        + "(like addin.user_cache_dir) of the addin object will result in an Error. "
        + "Consider pip-installing the fusion_addin_framework."
    )
    return msg


def addin_exists():
    msg = "There have been already addin instances created. It is recommende to use only one addin instance"
    return msg