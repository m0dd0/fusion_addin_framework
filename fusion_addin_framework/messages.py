"""This module contains message templates for logging messages the are send from
multiple plces in the code in some variation."""

### FUSION WRAPPERS ###


def using_exisiting(cls, id):  # pylint:disable=redefined-builtin
    msg = (
        f"Using existing {cls.__name__} (id: {id})."
        # "All arguments except 'id' will be "
        # "ignored. If you want to change properties of this {0}, you can "
        # "access and set the attributes if its not a native {0}."
    )
    return msg


def created_new(cls, id):  # pylint:disable=redefined-builtin
    msg = f"Created a new {cls.__name__}. (id: {id})"
    return msg


def invalid_control_type(control_type_name):
    msg = (
        f"'{control_type_name}' is no valid control type. Valid control types "
        + "are 'button', 'checkbox' or 'list'"
    )
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


def unknown_event_name(event_name):
    msg = (
        f"There is no event called '{event_name}'. The passed handler will be ignored."
    )
    return msg


def handler_execution_time(event_name, cmd_name, elapsed_time):
    msg = f"Executed {event_name} handler of '{cmd_name}' in {elapsed_time:.3f}s."
    return msg


### MISCELLANEOUS ###
