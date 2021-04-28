import logging
import traceback

import adsk.core

from . import messages as msgs
from . import defaults as dflts

_handlers = []

# TODO use (ttest) parent class
def _notify_routine(addin, cmd_name, event_name, action, args):
    logging.getLogger(__name__).info(msgs.starting_handler(event_name, cmd_name))

    try:
        action(args)
    except:
        # no exception gets raised outside the handlers so this try, except
        # block is mandatory to prevent silent errors !!!!!!!
        msg = msgs.handler_error(event_name, cmd_name, traceback.format_exc())
        logging.getLogger(__name__).error(msg)
        if addin.debug_to_ui:
            adsk.core.Application.get().userInterface.messageBox(msg)


class _InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self, addin, cmd_name, event_name, action):
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = event_name
        self.action = action

    def notify(self, args: adsk.core.InputChangedEventArgs):
        _notify_routine(self.addin, self.cmd_name, self.event_name, self.action, args)


class _CommandEventHandler(adsk.core.CommandEventHandler):
    def __init__(self, addin, cmd_name, event_name, action):
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = event_name
        self.action = action

    def notify(self, args: adsk.core.CommandEventArgs):
        _notify_routine(self.addin, self.cmd_name, self.event_name, self.action, args)


class _ValidateInputsEventHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self, addin, cmd_name, event_name, action):
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = event_name
        self.action = action

    def notify(self, args: adsk.core.ValidateInputsEventArgs):
        _notify_routine(self.addin, self.cmd_name, self.event_name, self.action, args)


class _SelectionEventHandler(adsk.core.SelectionEventHandler):
    def __init__(self, addin, cmd_name, event_name, action):
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = event_name
        self.action = action

    def notify(self, args: adsk.core.SelectionEventArgs):
        _notify_routine(self.addin, self.cmd_name, self.event_name, self.action, args)


class _MouseEventHandler(adsk.core.MouseEventHandler):
    def __init__(self, addin, cmd_name, event_name, action):
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = event_name
        self.action = action

    def notify(self, args: adsk.core.MouseEventArgs):
        _notify_routine(self.addin, self.cmd_name, self.event_name, self.action, args)


class _KeyboardEvenHandler(adsk.core.KeyboardEventHandler):
    def __init__(self, addin, cmd_name, event_name, action):
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = event_name
        self.action = action

    def notify(self, args: adsk.core.KeyboardEventArgs):
        _notify_routine(self.addin, self.cmd_name, self.event_name, self.action, args)


handler_type_mapping = {
    "activate": _CommandEventHandler,
    "deactivate": _CommandEventHandler,
    "destroy": _CommandEventHandler,
    "execute": _CommandEventHandler,
    "executePreview": _CommandEventHandler,
    "inputChanged": _InputChangedHandler,
    "keyDown": _KeyboardEvenHandler,
    "keyUp": _KeyboardEvenHandler,
    "mouseClick": _MouseEventHandler,
    "mouseDoubleClick": _MouseEventHandler,
    "mouseDown": _MouseEventHandler,
    "mouseDrag": _MouseEventHandler,
    "mouseDragBegin": _MouseEventHandler,
    "mouseDragEnd": _MouseEventHandler,
    "mouseMove": _MouseEventHandler,
    "mouseUp": _MouseEventHandler,
    "mouseWheel": _MouseEventHandler,
    "preSelect": _SelectionEventHandler,
    "preSelectEnd": _SelectionEventHandler,
    "preSelectMouseMove": _SelectionEventHandler,
    "select": _SelectionEventHandler,
    "unselect": _SelectionEventHandler,
    "validateInputs": _ValidateInputsEventHandler,
}


class _CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(
        self,
        addin,
        cmd_name,
        handler_dict,
    ):
        super().__init__()

        self.handler_dict = {}
        # sanitize the dict to allow on-prefix
        for event_name, handler_callable in handler_dict.items():
            if event_name.lower().startswith("on"):
                event_name = event_name[2:]
            event_name = event_name[0].lower() + event_name[1:]
            if event_name in self.handler_dict:
                logging.warning(
                    f"Two or more callback functions for the {event_name} event were provided. "
                    + "Only the last one will get used."
                )
            self.handler_dict[event_name] = handler_callable

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = "commandCreated"
        self.action = self.handler_dict.pop(self.event_name, dflts.do_nothing)

        _handlers.append(self)

    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        cmd = args.command

        for event_name, handler_callable in self.handler_dict.items():
            handler = handler_type_mapping[event_name](
                self.addin,
                self.cmd_name,
                event_name,
                handler_callable,
            )
            getattr(cmd, event_name).add(handler)
            _handlers.append(handler)

        _notify_routine(self.addin, self.cmd_name, self.event_name, self.action, args)
