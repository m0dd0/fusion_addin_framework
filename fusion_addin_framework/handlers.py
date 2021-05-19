"""
This module contains code to create a abstraction layer on the handler concept of the Fusion API
Thi module will be utilized by the Command Wrappers and doesnt need to be accessed directly.
"""

import logging
import traceback
from typing import Callable, Dict

import adsk.core

from . import messages as msgs
from . import defaults as dflts

# keep all handlers referenced
_handlers = []


# doesnt make live much easier so generic class is not used
# from abc import ABC
# class _GenericHandler(ABC):
#     event_name = None
#     cmd_name = None
#     action = None
#     addin = None

#     def notify(self, args):
#         logging.getLogger(__name__).info(
#             msgs.starting_handler(self.event_name, self.cmd_name)
#         )

#         try:
#             self.action(args)
#         except:
#             # no exception gets raised outside the handlers so this try, except
#             # block is mandatory to prevent silent errors !!!!!!!
#             msg = msgs.handler_error(
#                 self.event_name, self.cmd_name, traceback.format_exc()
#             )
#             logging.getLogger(__name__).error(msg)
#             if self.addin.debug_to_ui:
#                 adsk.core.Application.get().userInterface.messageBox(msg)


# pylint:disable=arguments-differ


def _notify_routine(addin, cmd_name, event_name, action, args):
    """Executs the handler action and ensures proper logging.

    Args:
        addin ([type]): [description]
        cmd_name ([type]): [description]
        event_name ([type]): [description]
        action ([type]): [description]
        args ([type]): [description]
    """
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
    """[summary]

    All other handler classes behave the same but due to the mro it is not much
    easier to use a common base class.

    Args:
        adsk ([type]): [description]
    """

    def __init__(self, addin, cmd_name, event_name, action):
        """[summary]

        Args:
            addin ([type]): [description]
            cmd_name ([type]): [description]
            event_name ([type]): [description]
            action ([type]): [description]
        """
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


# maps each available event of the commad to thier associated handler type
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
        cmd_name: str,
        handler_dict: Dict[str, Callable],
    ):
        """Initialiszed the command created and creates and connects all handlers
        acoording to the handler dict.

        Args:
            addin (Addin): The parent addin instace to determine if errors will get logged to the ui.
            cmd_name ([type]): [description]
            handler_dict ([type]): [description]
        """
        super().__init__()

        self.handler_dict = {}
        # sanitize the dict to allow on-prefix
        for event_name, handler_callable in handler_dict.items():
            if event_name.lower().startswith("on"):
                event_name = event_name[2:]
            event_name = event_name[0].lower() + event_name[1:]
            if event_name in self.handler_dict:
                logging.warning(msgs.doubled_callbacks(event_name))
            self.handler_dict[event_name] = handler_callable

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = "commandCreated"
        self.action = self.handler_dict.pop(self.event_name, dflts.do_nothing)

        _handlers.append(self)

    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        cmd = args.command

        #
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
