import adsk.core

from . import messages as msgs

_handlers = []

# TODO all handlers


def create(
    logger, cmd_name, on_created, on_execute, on_preview, on_input_changed, on_key_down
):
    on_created = _CommandCreatedHandler(
        logger,
        cmd_name,
        "OnCommandCreated",
        on_created,
        on_execute,
        on_preview,
        on_input_changed,
        on_key_down,
    )
    _handlers.append(on_created)
    return on_created


# TODO (try) parent class
# class _GenericHandler(ABC):
#     def __init__(self, logger, cmd_name, type):
#         self.logger = logger
#         self.cmd_name = cmd_name
#         self.type = type


class _CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(
        self,
        logger,
        cmd_name,
        type,
        on_start,
        on_execute,
        on_preview,
        on_input_changed,
        on_key_down,
    ):
        super().__init__()

        self.logger = logger
        self.cmd_name = cmd_name
        self.type = type

        self.on_start = on_start
        self.on_execute = on_execute
        self.on_preview = on_preview
        self.on_input_changed = on_input_changed
        self.on_key_down = on_key_down

    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        self.logger.info(msgs.starting_handler(self.type, self.cmd_name))

        cmd = args.command

        on_execute_handler = _CommandEventHandler(
            self.logger, self.cmd_name, "OnExecute", self.on_execute
        )
        cmd.execute.add(on_execute_handler)
        _handlers.append(on_execute_handler)

        on_input_changed_handler = _InputChangedHandler(
            self.logger, self.cmd_name, "OnInputChanged", self.on_input_changed
        )
        cmd.inputChanged.add(on_input_changed_handler)
        _handlers.append(on_input_changed_handler)

        on_destroy_handler = _CommandEventHandler(
            self.logger, self.cmd_name, "OnDestroy", self.on_destroy
        )
        cmd.destroy.add(on_destroy_handler)
        _handlers.append(on_destroy_handler)

        on_execute_preview_handler = _CommandEventHandler(
            self.logger, self.cmd_name, "OnPreview", self.on_preview
        )
        cmd.executePreview.add(on_execute_preview_handler)
        _handlers.append(on_execute_preview_handler)

        on_keydown_handler = _KeyboardHandler(
            self.logger, self.cmd_name, "OnKeyDown", self.on_key_down
        )
        cmd.keyDown.add(on_keydown_handler)
        _handlers.append(on_keydown_handler)

        self.on_start(args)


class _CommandEventHandler(adsk.core.CommandEventHandler):
    def __init__(self, logger, cmd_name, type, action):
        super().__init__()

        self.logger = logger
        self.cmd_name = cmd_name
        self.type = type

        self.action = action

    def notify(self, args: adsk.core.CommandEventArgs):
        self.logger.info(msgs.starting_handler(type, self.cmd_name))

        self.action(args)


class _InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self, logger, cmd_name, type, action):
        super().__init__()

        self.logger = logger
        self.cmd_name = cmd_name
        self.type = type

        self.action = action

    def notify(self, args: adsk.core.InputChangedEventArgs):
        self.logger.info(msgs.starting_handler(self.type, self.cmd_name))

        self.action(args)


class _KeyboardHandler(adsk.core.KeyboardEventHandler):
    def __init__(self, logger, cmd_name, type, action):
        super().__init__()

        self.logger = logger
        self.cmd_name = cmd_name
        self.type = type

        self.action = action

    def notify(self, args):
        self.logger.info(msgs.starting_handler(self.type, self.cmd_name))

        self.action(args)


# TODO use custom commands
# class _CustomCommandEventHandler(adsk.core.CustomEventHandler):
#     def __init__(self, logger, cmd_name, type, action):
#         super().__init__()

#         self.logger = logger
#         self.cmd_name = cmd_name
#         self.type = type

#         self.action = action

#     def notify(self, args):
#         self.logger.info(msgs.starting_handler(self.type, self.cmd_name))

#         self.action(args)