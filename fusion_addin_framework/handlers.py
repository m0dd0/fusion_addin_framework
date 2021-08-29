"""
This module contains code to create a abstraction layer on the handler concept of 
the Fusion API. This module is utilized by the Command Wrapper.
"""

import logging
import traceback
from typing import Callable, Dict
import time

import adsk.core

from . import messages as msgs

# for typehints only
# do not use because it will cause an circular import error in sphinx
# from .wrapper import FusionAddin

# keep all handlers referenced
_handlers = []
_custom_events_and_handlers = []

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


def _notify_routine(addin, cmd_name: str, event_name: str, action: Callable, args):
    """Executes the handler action and ensures proper logging.

    Args:
        addin(FusionAddin): The addin instance of the parent command.
        cmd_name (str): The command name.
        event_name (str): The name of the event.
        action (Callable): The notify function of the event to execute.
        args ([type]): The arguments passed to the notify function.
    """
    logging.getLogger(__name__).info(msgs.starting_handler(event_name, cmd_name))
    try:
        start = time.perf_counter()
        action(args)
        logging.getLogger(__name__).info(
            msgs.handler_execution_time(
                event_name, cmd_name, time.perf_counter() - start
            )
        )
    except:
        # no exception gets raised outside the handlers so this try, except
        # block is mandatory to prevent silent errors !!!!!!!
        msg = msgs.handler_error(event_name, cmd_name, traceback.format_exc())
        logging.getLogger(__name__).error(msg)
        if addin.debugToUi:
            adsk.core.Application.get().userInterface.messageBox(msg)


class _CustomEventHandler(adsk.core.CustomEventHandler):
    def __init__(self, addin, cmd_name, event, action):
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event = event
        self.action = action

        _custom_events_and_handlers.append((event, self))

    def notify(self, args: adsk.core.CommandEventArgs):
        _notify_routine(
            self.addin,
            self.cmd_name,
            self.event.eventId + " (custom event)",
            self.action,
            args,
        )


class _InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self, addin, cmd_name: str, event_name: str, action: Callable):
        """Generic version of a InputChangedHandler class.

        All other handler classes behave the same but due to the mro it is not much
        easier to use a common base class.

        Args:
            addin (FusionAddin): The addin instance of the parent command.
            cmd_name ([type]): The command name.
            event_name (str): The name of the event.
            action (Callable): The notify function of the event to execute.
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
    "commandCreated": None,
}


def do_nothing(*args, **kwargs):  # pylint:disable=unused-argument
    pass


class _CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(
        self,
        addin,
        cmd_name: str,
        handler_dict: Dict[str, Callable],
    ):
        """Initialiszed the command created event handler and creates and
        connects all handlers according to the handler dict.

        Args:
            addin (FusionAddin): The addin instance of the parent command.
            cmd_name (str):  The command name.
            handler_dict (Dict[str, Callable]): A dictionairy which maps the
                event names to callables which are executet if the event id fired.
                Instead of the blank event name it can also be provided with an
                "on"-prefix.
        """
        super().__init__()

        self.handler_dict = {}
        # sanitize the dict to allow on-prefix
        allowed_prefix = "on"
        for event_name, handler_callable in handler_dict.items():
            if event_name.lower().startswith(allowed_prefix):
                event_name = event_name[len(allowed_prefix) :]
            event_name = event_name[0].lower() + event_name[1:]
            if event_name in self.handler_dict:
                logging.getLogger(__name__).warning(msgs.doubled_callbacks(event_name))
            if event_name not in handler_type_mapping:
                # raising an (custom) error would result in a silent error and crash
                # the further adding of handlers so use logging instead
                logging.getLogger(__name__).warning(msgs.unknown_event_name(event_name))
            else:
                self.handler_dict[event_name] = handler_callable

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = "commandCreated"
        self.action = self.handler_dict.pop(self.event_name, do_nothing)

        _handlers.append(self)

    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        cmd = args.command

        # create handlers for all events in the handler dict and connect them to
        # the correct event
        for event_name, handler_callable in self.handler_dict.items():
            handler_class = handler_type_mapping.get(event_name)
            if handler_class is None:
                # shouldnt happened
                # just in case sanitation in init hasnt worked properly
                logging.getLogger(__name__).warning(msgs.unknown_event_name(event_name))
            else:
                handler = handler_class(
                    self.addin,
                    self.cmd_name,
                    event_name,
                    handler_callable,
                )
                getattr(cmd, event_name).add(handler)
                _handlers.append(handler)

        _notify_routine(self.addin, self.cmd_name, self.event_name, self.action, args)
