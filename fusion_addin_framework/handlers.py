import logging

import adsk.core

from . import messages as msgs
import traceback

_handlers = []

# TODO all handlers
# TODO warning if handler functions have wrong number of arguments


def create(
    app, cmd_name, on_created, on_execute, on_preview, on_input_changed, on_key_down
):
    on_created_handler = _CommandCreatedHandler(
        app,
        cmd_name,
        "OnCommandCreated",
        on_created,
        on_execute,
        on_preview,
        on_input_changed,
        on_key_down,
    )
    _handlers.append(on_created_handler)
    return on_created_handler


# TODO (try) parent class
# class _GenericHandler(ABC):
#     def __init__(self, logger, cmd_name, type):
#         self.logger = logger
#         self.cmd_name = cmd_name
#         self.type = type


class _CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(
        self,
        app,
        cmd_name,
        handler_type,
        on_start,
        on_execute,
        on_preview,
        on_input_changed,
        on_key_down,
    ):
        super().__init__()

        self.app = app
        self.cmd_name = cmd_name
        self.handler_type = handler_type

        self.on_start = on_start
        self.on_execute = on_execute
        self.on_preview = on_preview
        self.on_input_changed = on_input_changed
        self.on_key_down = on_key_down

    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        logging.getLogger(__name__).info(
            msgs.starting_handler(self.handler_type, self.cmd_name)
        )

        cmd = args.command

        on_execute_handler = _CommandEventHandler(
            self.app, self.cmd_name, "OnExecute", self.on_execute
        )
        cmd.execute.add(on_execute_handler)
        _handlers.append(on_execute_handler)

        on_input_changed_handler = _InputChangedHandler(
            self.app, self.cmd_name, "OnInputChanged", self.on_input_changed
        )
        cmd.inputChanged.add(on_input_changed_handler)
        _handlers.append(on_input_changed_handler)

        on_destroy_handler = _CommandEventHandler(
            self.app, self.cmd_name, "OnDestroy", self.on_destroy
        )
        cmd.destroy.add(on_destroy_handler)
        _handlers.append(on_destroy_handler)

        on_execute_preview_handler = _CommandEventHandler(
            self.app, self.cmd_name, "OnPreview", self.on_preview
        )
        cmd.executePreview.add(on_execute_preview_handler)
        _handlers.append(on_execute_preview_handler)

        on_keydown_handler = _KeyboardHandler(
            self.app, self.cmd_name, "OnKeyDown", self.on_key_down
        )
        cmd.keyDown.add(on_keydown_handler)
        _handlers.append(on_keydown_handler)

        try:
            self.on_start(args)
        except:
            # no exception gets raised outside the handlers so this try, except
            # block is mandatory to prevent silent errors !!!!!!!
            msg = "Failed:\n{}".format(traceback.format_exc())  # TODO msgs
            logging.getLogger(__name__).error(msg)
            if self.addin.debug_to_ui:
                adsk.core.Application.get().userInterface.messageBox(msg)


class _CommandEventHandler(adsk.core.CommandEventHandler):
    def __init__(self, app, cmd_name, handler_type, action):
        super().__init__()

        self.app = app
        self.cmd_name = cmd_name
        self.handler_type = handler_type

        self.action = action

    def notify(self, args: adsk.core.CommandEventArgs):
        logging.getLogger(__name__).info(
            msgs.starting_handler(self.handler_type, self.cmd_name)
        )

        try:
            self.action(args)
        except:
            # no exception gets raised outside the handlers so this try, except
            # block is mandatory to prevent silent errors !!!!!!!
            msg = "Failed:\n{}".format(traceback.format_exc())  # TODO msgs
            logging.getLogger(__name__).error(msg)
            if self.app.debug_to_ui:
                adsk.core.Application.get().userInterface.messageBox(msg)


class _InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self, app, cmd_name, handler_type, action):
        super().__init__()

        self.app = app
        self.cmd_name = cmd_name
        self.handler_type = handler_type

        self.action = action

    def notify(self, args: adsk.core.InputChangedEventArgs):
        logging.getLogger(__name__).info(
            msgs.starting_handler(self.handler_type, self.cmd_name)
        )

        try:
            self.action(args)
        except:
            # no exception gets raised outside the handlers so this try, except
            # block is mandatory to prevent silent errors !!!!!!!
            msg = "Failed:\n{}".format(traceback.format_exc())  # TODO msgs
            logging.getLogger(__name__).error(msg)
            if self.app.debug_to_ui:
                adsk.core.Application.get().userInterface.messageBox(msg)


class _KeyboardHandler(adsk.core.KeyboardEventHandler):
    def __init__(self, app, cmd_name, handler_type, action):
        super().__init__()

        self.app = app
        self.cmd_name = cmd_name
        self.handler_type = handler_type

        self.action = action

    def notify(self, args):
        logging.getLogger(__name__).info(
            msgs.starting_handler(self.handler_type, self.cmd_name)
        )

        try:
            self.action(args)
        except:
            # no exception gets raised outside the handlers so this try, except
            # block is mandatory to prevent silent errors !!!!!!!
            msg = "Failed:\n{}".format(traceback.format_exc())  # TODO msgs
            logging.getLogger(__name__).error(msg)
            if self.app.debug_to_ui:
                adsk.core.Application.get().userInterface.messageBox(msg)


# TODO use custom commands
# class _CustomCommandEventHandler(adsk.core.CustomEventHandler):
#     def __init__(self, logger, cmd_name, type, action):
#         super().__init__()

#         self.logger = logger
#         self.cmd_name = cmd_name
#         self.type = type

#         try:
#     self.action(args)
# except:
#     self.logger.error("Failed:\n{}".format(traceback.format_exc()))
# no exception gets raised outside the handlers so this try, except
# block is mandatory to prevent silent errors !!!!!!!

#     def notify(self, args):
#         self.logger.info(msgs.starting_handler(self.type, self.cmd_name))

#         self.action(args)