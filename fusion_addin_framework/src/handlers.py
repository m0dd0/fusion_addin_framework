import adsk.core

_handlers = []  # TODO use app (maybe)

# TODO all handlers


def create(on_created, on_execute, on_preview, on_input_changed, on_key_down):
    on_created = _CommandCreatedHandler(
        on_created, on_execute, on_preview, on_input_changed, on_key_down
    )
    _handlers.append(on_created)
    return on_created


class _CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self, on_start, on_execute, on_preview, on_input_changed, on_key_down):
        super().__init__()
        self.on_start = on_start
        self.on_execute = on_execute
        self.on_preview = on_preview
        self.on_input_changed = on_input_changed
        self.on_key_down = on_key_down

    def notify(self, args: adsk.core.CommandCreatedEventArgs):

        cmd = args.command

        on_execute_handler = _CommandEventHandler(self.on_execute)
        cmd.execute.add(on_execute_handler)
        _handlers.append(on_execute_handler)

        on_input_changed_handler = _InputChangedHandler(self.on_input_changed)
        cmd.inputChanged.add(on_input_changed_handler)
        _handlers.append(on_input_changed_handler)

        on_destroy_handler = _CommandEventHandler(self.on_destroy)
        cmd.destroy.add(on_destroy_handler)
        _handlers.append(on_destroy_handler)

        on_execute_preview_handler = _CommandEventHandler(self.on_preview)
        cmd.executePreview.add(on_execute_preview_handler)
        _handlers.append(on_execute_preview_handler)

        on_keydown_handler = _KeyboardHandler(self.on_key_down)
        cmd.keyDown.add(on_keydown_handler)
        _handlers.append(on_keydown_handler)

        self.on_start(args)


class _CommandEventHandler(adsk.core.CommandEventHandler):
    def __init__(self, action):
        super().__init__()
        self.action = action

    def notify(self, args: adsk.core.CommandEventArgs):
        self.action(args)


class _InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self, action):
        super().__init__()
        self.action = action

    def notify(self, args: adsk.core.InputChangedEventArgs):
        self.action(args)


class _KeyboardHandler(adsk.core.KeyboardEventHandler):
    def __init__(self, action):
        super().__init__()
        self.action = action

    def notify(self, args):
        self.action(args)


class _CustomCommandEventHandler(adsk.core.CustomEventHandler):
    def __init__(self, action):
        super().__init__()
        self.action = action

    def notify(self, args):
        self.action(args)