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