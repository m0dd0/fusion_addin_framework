### FUSION WRAPPERS ###


def using_exisitng(cls, id):  # pylint:disable=redefined-builtin
    msg = (
        "Using existing {0} (id: {1}). All arguments except 'id' will be "
        "ignored. If you want to change properties of this {0}, you can "
        "access and set the attributes if its not a native {0}."
    ).format(cls.__name__, id)
    return msg


def created_new(cls, id):  # pylint:disable=redefined-builtin
    msg = f"Created a new {cls.__name__}. (id: {id})"
    return msg


### HANDLERS ###


def starting_handler(handler_type, cmd_name):
    msg = f"Executing {handler_type} handler of '{cmd_name}' command."
    return msg