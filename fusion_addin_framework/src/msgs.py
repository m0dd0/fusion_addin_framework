def setting_on_native(type, id, not_setable):
    msg = (
        "The following arguments for the {0} (id: {1}) were ignored since "
        "they cant be manipulated on a native {0}: {2}"
    ).format(type, id, not_setable)
    return msg
