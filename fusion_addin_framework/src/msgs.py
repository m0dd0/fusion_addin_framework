def setting_on_native(type, id, not_setable):
    msg = (
        "The following arguments for the {0} (id: {1}) were ignored since "
        "they cant be manipulated on a native {0}: {2}"
    ).format(type, id, not_setable)
    return msg


def already_exisiting(type, id, not_setable):
    msg = (
        "A {0} with this id ({1}) already exists. Therefore the following "
        "arguments will be ignored: {2}. If you want to change these properties, "
        "set them manually after creation"
    ).format(type, id, not_setable)
    return msg