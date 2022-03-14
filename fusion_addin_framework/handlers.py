"""
This module contains code to create a abstraction layer on the handler concept of 
the Fusion API. This module is utilized by the Command Wrapper.
"""
# pylint:disable=invalid-name

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
handlers = []
custom_events_and_handlers = []

# region
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
# endregion


class GenericCustomEventHandler(adsk.core.CustomEventHandler):
    def __init__(self, action: Callable, event: adsk.core.Event, debug_to_ui=False):
        """Generic version of a CustomEventHAndler  which executes the passed action as its
        notify method. This handler is NOT associated to any command and is used from the
        utility functions.

        Args:
            action (Callable): The action to execute from the custom event.
            event (adsk.core.Event): The associated event.
            debug_to_ui (bool, optional): Whether any errors appearing during execution
                of the action are displayed in messageBox. Defaults to False.
        """
        super().__init__()

        self.action = action
        self.event = event
        self.debug_to_ui = debug_to_ui

        custom_events_and_handlers.append((event, self))

    def notify(self, eventArgs: adsk.core.CommandEventArgs):
        logging.getLogger(__name__).info(
            msgs.starting_handler(
                f"{self.event.eventId} (custom event)", "<no_command>"
            )
        )
        try:
            start = time.perf_counter()
            self.action(eventArgs)
            logging.getLogger(__name__).info(
                msgs.handler_execution_time(
                    f"{self.event.id} (custom event)",
                    "<no_command>",
                    time.perf_counter() - start,
                )
            )
        except:
            # no exception gets raised outside the handlers so this try, except
            # block is mandatory to prevent silent errors !!!!!!!
            msg = msgs.handler_error(
                f"{self.event.id} (custom event)",
                "<no_command>",
                traceback.format_exc(),
            )
            logging.getLogger(__name__).error(msg)
            if self.debug_to_ui:
                adsk.core.Application.get().userInterface.messageBox(msg)


def _notify_routine(
    addin,
    cmd_name: str,
    event_name: str,
    action: Callable,
    event_args: adsk.core.CommandEventArgs,
):
    """Executes the handler action and ensures proper logging.

    Args:
        addin(FusionAddin): The addin instance of the parent command.
        cmd_name (str): The command name.
        event_name (str): The name of the event.
        action (Callable): The notify function of the event to execute.
        args (adsk.core.CommandEventArgs): The arguments passed to the notify function.
    """
    logging.getLogger(__name__).info(msgs.starting_handler(event_name, cmd_name))
    try:
        start = time.perf_counter()
        action(event_args)
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


# region
# class CustomEventHandler_(adsk.core.CustomEventHandler):
#     def __init__(self, addin, cmd_name: str, event: adsk.core.Event, action: Callable):
#         """Generic custom event handlers which is associated with a certain command.

#         Args:
#             addin (FusionAddin): _description_
#             cmd_name (str): The command name.
#             event (adsk.core.Event): The associated event.
#             action (Callable): The notify function of the event to execute.
#         """
#         super().__init__()

#         self.addin = addin
#         self.cmd_name = cmd_name
#         self.event = event
#         self.action = action

#         custom_events_and_handlers.append((event, self))

#     def notify(self, eventArgs: adsk.core.CommandEventArgs):
#         _notify_routine(
#             self.addin,
#             self.cmd_name,
#             self.event.eventId + " (custom event)",
#             self.action,
#             eventArgs,
#         )
# endregion


class InputChangedHandler_(adsk.core.InputChangedEventHandler):
    def __init__(self, addin, cmd_name: str, event_name: str, action: Callable):
        """Generic version of a InputChangedHandler class.

        All other handler classes behave the same but due to the mro it is not much
        easier to use a common base class.

        Args:
            addin (FusionAddin): The addin instance of the parent command.
            cmd_name (str): The command name.
            event_name (str): The name of the event.
            action (Callable): The notify function of the event to execute.
        """
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = event_name
        self.action = action

    def notify(self, eventArgs: adsk.core.InputChangedEventArgs):
        _notify_routine(
            self.addin, self.cmd_name, self.event_name, self.action, eventArgs
        )


class CommandEventHandler_(adsk.core.CommandEventHandler):
    def __init__(self, addin, cmd_name: str, event_name: str, action: Callable):
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = event_name
        self.action = action

    def notify(self, eventArgs: adsk.core.CommandEventArgs):
        _notify_routine(
            self.addin, self.cmd_name, self.event_name, self.action, eventArgs
        )


class ValidateInputsEventHandler_(adsk.core.ValidateInputsEventHandler):
    def __init__(self, addin, cmd_name: str, event_name: str, action: Callable):
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = event_name
        self.action = action

    def notify(self, eventArgs: adsk.core.ValidateInputsEventArgs):
        _notify_routine(
            self.addin, self.cmd_name, self.event_name, self.action, eventArgs
        )


class SelectionEventHandler_(adsk.core.SelectionEventHandler):
    def __init__(self, addin, cmd_name: str, event_name: str, action: Callable):
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = event_name
        self.action = action

    def notify(self, eventArgs: adsk.core.SelectionEventArgs):
        _notify_routine(
            self.addin, self.cmd_name, self.event_name, self.action, eventArgs
        )


class MouseEventHandler_(adsk.core.MouseEventHandler):
    def __init__(self, addin, cmd_name: str, event_name: str, action: Callable):
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = event_name
        self.action = action

    def notify(self, eventArgs: adsk.core.MouseEventArgs):
        _notify_routine(
            self.addin, self.cmd_name, self.event_name, self.action, eventArgs
        )


class KeyboardEvenHandler_(adsk.core.KeyboardEventHandler):
    def __init__(self, addin, cmd_name: str, event_name: str, action: Callable):
        super().__init__()

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = event_name
        self.action = action

    def notify(self, eventArgs: adsk.core.KeyboardEventArgs):
        _notify_routine(
            self.addin, self.cmd_name, self.event_name, self.action, eventArgs
        )


# maps each available event of the commad to thier associated handler type
handler_type_mapping = {
    "activate": CommandEventHandler_,
    "deactivate": CommandEventHandler_,
    "destroy": CommandEventHandler_,
    "execute": CommandEventHandler_,
    "executePreview": CommandEventHandler_,
    "inputChanged": InputChangedHandler_,
    "keyDown": KeyboardEvenHandler_,
    "keyUp": KeyboardEvenHandler_,
    "mouseClick": MouseEventHandler_,
    "mouseDoubleClick": MouseEventHandler_,
    "mouseDown": MouseEventHandler_,
    "mouseDrag": MouseEventHandler_,
    "mouseDragBegin": MouseEventHandler_,
    "mouseDragEnd": MouseEventHandler_,
    "mouseMove": MouseEventHandler_,
    "mouseUp": MouseEventHandler_,
    "mouseWheel": MouseEventHandler_,
    "preSelect": SelectionEventHandler_,
    "preSelectEnd": SelectionEventHandler_,
    "preSelectMouseMove": SelectionEventHandler_,
    "select": SelectionEventHandler_,
    "unselect": SelectionEventHandler_,
    "validateInputs": ValidateInputsEventHandler_,
    "commandCreated": None,
}


def do_nothing(*args, **kwargs):  # pylint:disable=unused-argument
    pass


class CommandCreatedHandler_(adsk.core.CommandCreatedEventHandler):
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

        self.handler_dict = handler_dict

        self.addin = addin
        self.cmd_name = cmd_name
        self.event_name = "commandCreated"
        self.action = self.handler_dict.pop(self.event_name, do_nothing)

        handlers.append(self)

    def notify(self, eventArgs: adsk.core.CommandCreatedEventArgs):
        cmd = eventArgs.command

        # create handlers for all events in the handler dict and connect them to
        # the correct event
        for event_name, handler_callable in self.handler_dict.items():
            handler_class = handler_type_mapping.get(event_name)
            if handler_class is None:
                # shouldnt happened
                # just in case sanitation in AddinCommand hasnt worked properly
                logging.getLogger(__name__).warning(msgs.unknown_event_name(event_name))
            else:
                handler = handler_class(
                    self.addin,
                    self.cmd_name,
                    event_name,
                    handler_callable,
                )
                getattr(cmd, event_name).add(handler)
                handlers.append(handler)

        _notify_routine(
            self.addin, self.cmd_name, self.event_name, self.action, eventArgs
        )
