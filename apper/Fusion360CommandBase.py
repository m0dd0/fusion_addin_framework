""" Module providing the Fusion360 CommandBase.
"""

import sys
import os
from collections import deque
import traceback
from typing import List, Dict, Any
import logging
from abc import abstractmethod
import uuid

import adsk.core
import adsk.fusion

from .UiElements import UiItemFactory
from ..utilities import get_values


class HandlerState:
    def __init__(self):
        self.call_count = 0

    def reset(self):
        pass

    def get_changed(self):
        pass


class Fusion360CommandBase():
    """ Handles ui element creation and setting up handlers for a Command.

    This is used as an abstract base class. The child classes are implementing
    the command logic.
    """
    def __init__(
        self,
        fusion_app,
        positions: List[UiItemFactory],
        logger: logging.Logger,
        debug_to_ui: bool = True,
    ):
        self.fusion_app = fusion_app
        self.cmd_name = os.path.basename(
            sys.modules[self.__class__.__module__].__file__)
        self.cmd_path = os.path.dirname(
            os.path.abspath(sys.modules[self.__class__.__module__].__file__))
        self.cmd_uuid = str(uuid.uuid4())

        self.positions_info = positions
        # path elemts are stored as tuple, second value is inidcating
        # if element was created by addin
        self.position_paths = []

        self.debug_to_ui = debug_to_ui
        self.logger = logger

        self.on_command_created_handler = _CommandCreatedEventHandler(self)
        self.command_handlers = []
        self.custom_command_handlers = {}  # {event_id: customEventHandler}

        self.fusion_command = None  # needed sometimes for custom events

        self.log_info('initialised {0} command'.format(self.cmd_name))

    def show_error(self, message: str):
        """ Shows an error message according to the command settings.

        Args:
            message (str): the message to be displayed
        """
        self.logger.error('({0}) {1}'.format(self.cmd_name, message))
        if self.debug_to_ui:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox(message)

    def log_info(self, message: str):
        """ Logs an message according to the command settings.

        Args:
            message (str): the message to log
        """
        self.logger.info('({0}) {1}'.format(self.cmd_name, message))

    def register_custom_command_event(self, func):
        event_id = func.__name__ + self.cmd_uuid
        if event_id in self.custom_command_handlers.keys():
            self.log_info(
                'function \'{0}\' is already connected to a registered event'.
                format(func.__name__))
            return event_id
        custom_event = adsk.core.Application.get().registerCustomEvent(
            event_id)
        on_custom_event = _CustomCommandEventHandler(self, func)
        custom_event.add(on_custom_event)
        self.custom_command_handlers[event_id] = on_custom_event
        self.log_info(
            'connected function \'{0}\' to a registered event'.format(
                func.__name__))
        return event_id

    def fire_custom_command_event(self, func, args=''):
        adsk.core.Application.get().fireCustomEvent(
            func.__name__ + self.cmd_uuid, args)

    def on_run(self):
        """ Set up the ui elemnts and command definitons for the command.

        For each position factors in everx position list of the positions_info
        attribute, the in_fusion() method is run. The returned value is saved
        as parent and given to the next in_fusion() method. Command definitions
        are handled seperately.
        Also the 'resources' attribute of the factory are manipulated.
        The created/used ui elemnts are stored in the self.position_path attribute.
        There are no checks to validate the structure of the given structure.
        This should be done before.
        """
        for position_count, position_path_info in enumerate(
                self.positions_info):
            self.log_info('adding position {0}'.format(position_count + 1))

            for elem in position_path_info:
                if hasattr(elem, 'resources') and elem.resources != '':
                    if not os.path.isdir(elem.resources):
                        elem.resource = os.path.abspath(
                            os.path.join(
                                os.path.dirname(
                                    os.path.dirname(
                                        os.path.dirname(__file__))),
                                'resources', elem.resources))

            position_path_info = deque(position_path_info)
            this_position_path = []

            # second value will always indicate if element got created by addin
            last_ui_element = (adsk.core.Application.get().userInterface,
                               False)
            while len(position_path_info) > 2:
                new_ui_element = position_path_info.popleft().in_fusion(
                    last_ui_element[0])

                self.log_info('positioned into {0} \'{1}\' {2}'.format(
                    'newly created' if new_ui_element[1] else 'existing',
                    new_ui_element[0].id,
                    type(new_ui_element[0]).__name__))

                this_position_path.append(new_ui_element)

                last_ui_element = new_ui_element

            cmd_def = position_path_info.pop().in_fusion()
            cmd_def[0].commandCreated.add(self.on_command_created_handler)

            final_control = position_path_info.pop().in_fusion(
                last_ui_element[0], cmd_def[0])
            self.log_info('using {0} for command defintion \'{1}\''.format(
                final_control[0].objectType, cmd_def[0].id))

            this_position_path.append(final_control)
            this_position_path.append(cmd_def)

            self.position_paths.append(this_position_path)

    @abstractmethod
    def on_create(self, args: adsk.core.CommandEventArgs,
                  command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                  state: HandlerState):
        """ Executed when addin button is pressed.

        Create the needed input field here.

        Args:
            args (adsk.core.CommandEventArgs): the native commandEventArgs passed
                                                to the handler
            command (adsk.core.Command): reference to the command object
            inputs (adsk.core.CommandInputs): quick reference directly to the
                                                commandInputs object
        """
        pass

    @abstractmethod
    def on_preview(self, args: adsk.core.CommandEventArgs,
                   command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                   input_values: Dict[str, Any], state: HandlerState):
        """ Executed when any inputs have changed, will updated the graphic

        Code in this function will cause the graphics to refresh.
        Note if your addin is complex it may be useful to only preview a subset
        of the full operations

        Args:
            args (adsk.core.CommandEventArgs): the native commandEventArgs passed
                                                to the handler
            command (adsk.core.Command): reference to the command object
            inputs (adsk.core.CommandInputs): quick reference directly to the
                                                commandInputs object
            input_values (Dict[str,Any]): dictionary of the useful values a user
                                            entered.  The key is the command_id.
        """

        pass

    @abstractmethod
    def on_input_changed(self, args: adsk.core.InputChangedEventArgs,
                         command: adsk.core.Command,
                         inputs: adsk.core.CommandInputs,
                         input_values: Dict[str, Any],
                         changed_input: adsk.core.CommandInput,
                         state: HandlerState):
        """Executed when any inputs have changed.  Useful for updating command UI.

        When a user changes anything in the command dialog this method is executed.
        Typically used for making changes to the command dialog itself.

        Args:
            args (adsk.core.InputChangedEventArgs): the native commandEventArgs
                                                    passed to the handler
            command (adsk.core.Command): reference to the command object
            inputs (adsk.core.CommandInputs): quick reference directly to the
                                                commandInputs object
            input_values (Dict[str,Any]): dictionary of the useful values a user
                                         entered. The key is the command_id.
            changed_input (adsk.core.CommandInput): The specific commandInput
                                                     that was modified.
        """
        pass

    @abstractmethod
    def on_execute(self, args: adsk.core.CommandEventArgs,
                   command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                   input_values: Dict[str, Any], state: HandlerState):
        """Will be executed when user selects OK in command dialog.

        Args:
            args (adsk.core.CommandEventArgs): the native commandEventArgs
                passed to the handler.
            command (adsk.core.Command): reference to the command object
            inputs (adsk.core.CommandInputs): quick reference directly to the
                commandInputs object.
            input_values (Dict[str,Any]): dictionary of the useful values a user
                entered. The key is the command_id.
        """
        pass

    @abstractmethod
    def on_destroy(self, args: adsk.core.CommandEventArgs,
                   command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                   input_values: Dict[str, Any],
                   reason: adsk.core.CommandTerminationReason,
                   state: HandlerState):
        """ Executed when the command is done. Sometimes useful to check if a
        user hit cancel.

        You can use this to do any clean up that may otherwise be difficult until
        after the command has completed.
        Like firing a second command for example.

        Args:
            args (adsk.core.CommandEventArgs): the native commandEventArgs
                passed to the handler
            command (adsk.core.Command): reference to the command object
            inputs (adsk.core.CommandInputs): quick reference directly to the
                commandInputs object
            input_values (Dict[str,Any]): dictionary of the useful values a user
                entered.  The key is the command_id.
            reason (adsk.core.CommandTerminationReason): The reason the command
                was terminated. Enumerator defined in adsk.core.CommandTerminationReason
        """
        pass

    @abstractmethod
    def on_key_down(self, args: adsk.core.CommandEventArgs,
                    command: adsk.core.Command,
                    inputs: adsk.core.CommandInputs, input_values: Dict[str,
                                                                        Any],
                    keycode: int, state: HandlerState):
        """[summary]

        Args:
            args (adsk.core.CommandEventArgs): [description]
            command (adsk.core.Command): [description]
            inputs (adsk.core.CommandInputs): [description]
            input_values (Dict[str, Any]): [description]
            keycode (int): [description]
        """
        pass


class _CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self, cmd_obj):
        super().__init__()
        self.cmd_obj = cmd_obj
        self.cmd_obj.log_info('initialized CommandCreatedEventHAndler')
        self.state = HandlerState()

    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        """ Gets called if the CommandCreatedEvent is raised.

        Args:
            args (adsk.core.CommandCreatedEventArgs): according event aruments
        """
        try:
            self.state.call_count += 1
            cmd = args.command

            self.cmd_obj.fusion_command = cmd

            on_execute_handler = _CommandExecuteHandler(self.cmd_obj)
            cmd.execute.add(on_execute_handler)
            self.cmd_obj.command_handlers.append(on_execute_handler)

            on_input_changed_handler = _InputChangedHandler(self.cmd_obj)
            cmd.inputChanged.add(on_input_changed_handler)
            self.cmd_obj.command_handlers.append(on_input_changed_handler)

            on_destroy_handler = _DestroyHandler(self.cmd_obj)
            cmd.destroy.add(on_destroy_handler)
            self.cmd_obj.command_handlers.append(on_destroy_handler)

            on_execute_preview_handler = _PreviewHandler(self.cmd_obj)
            cmd.executePreview.add(on_execute_preview_handler)
            self.cmd_obj.command_handlers.append(on_execute_preview_handler)

            on_keydown_handler = _KeyDownHandler(self.cmd_obj)
            cmd.keyDown.add(on_keydown_handler)
            self.cmd_obj.command_handlers.append(on_keydown_handler)

            self.cmd_obj.log_info('executing CommandCreatedEventHAndler')
            # TODO add more args wrapper when needed
            self.cmd_obj.on_create(args, cmd, cmd.commandInputs, self.state)

        except:
            self.cmd_obj.show_error('Command created failed: {0}'.format(
                traceback.format_exc()))


class _PreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self, cmd_obj):
        super().__init__()
        self.cmd_obj = cmd_obj
        self.cmd_obj.log_info('initialized PreviewHandler')
        self.state = HandlerState()

    def notify(self, args: adsk.core.CommandEventArgs):
        """ Gets called if the CommandPreviewEvent is raised.

        Args:
            args (adsk.core.CommandEventArgs): according event aruments
        """
        try:
            self.state.call_count += 1
            cmd = args.firingEvent.sender

            self.cmd_obj.log_info('executing PreviewHandler')
            # TODO add more args wrapper when needed
            self.cmd_obj.on_preview(args, cmd, cmd.commandInputs,
                                    get_values(cmd.commandInputs), self.state)
        except:
            self.cmd_obj.show_error('Preview event failed: {}'.format(
                traceback.format_exc()))


class _InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self, cmd_obj):
        super().__init__()
        self.cmd_obj = cmd_obj
        self.cmd_obj.log_info('initialized InputChangedHandler')
        self.state = HandlerState()

    def notify(self, args: adsk.core.InputChangedEventArgs):
        """ Gets called if the InputChangedEvent is raised.

        Args:
            args (adsk.core.InputChangedEventArgs): according event aruments
        """
        try:
            self.state.call_count += 1
            cmd = args.firingEvent.sender

            self.cmd_obj.log_info('executing InputCHangedHandler')
            # TODO add more args wrapper when needed
            self.cmd_obj.on_input_changed(args, cmd, cmd.commandInputs,
                                          get_values(cmd.commandInputs),
                                          args.input, self.state)

        except:
            self.cmd_obj.show_error('Input changed event failed: {}'.format(
                traceback.format_exc()))


class _CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self, cmd_obj):
        super().__init__()
        self.cmd_obj = cmd_obj
        self.cmd_obj.log_info('initialized CommandExecuteHandler')
        self.state = HandlerState()

    def notify(self, args: adsk.core.CommandEventArgs):
        """ Gets called if the CommandExecuteEvent is raised.

        Args:
            args (adsk.core.CommandEventArgs): according event aruments
        """
        try:
            self.state.call_count += 1
            cmd = args.firingEvent.sender

            self.cmd_obj.log_info('executing CommandExecuteHandler')
            # TODO add more args wrapper when needed
            self.cmd_obj.on_execute(args, cmd, cmd.commandInputs,
                                    get_values(cmd.commandInputs), self.state)

        except:
            self.cmd_obj.show_error('Command execute event failed: {}'.format(
                traceback.format_exc()))


class _DestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self, cmd_obj):
        super().__init__()
        self.cmd_obj = cmd_obj
        self.cmd_obj.log_info('initialized DestroyHandler')
        self.state = HandlerState()

    def notify(self, args: adsk.core.CommandEventArgs):
        """ Gets called if the CommandDestroyEvent is raised.

        Args:
            args (adsk.core.CommandEventArgs): according event aruments
        """
        try:
            self.state.call_count += 1
            cmd = args.firingEvent.sender

            self.cmd_obj.log_info('executing DestroyHandler')
            # TODO add more args wrapper when needed
            self.cmd_obj.on_destroy(args, cmd, cmd.commandInputs,
                                    get_values(cmd.commandInputs),
                                    args.terminationReason, self.state)

            for event_id in set(self.cmd_obj.custom_command_handlers.keys()):
                adsk.core.Application.get().unregisterCustomEvent(event_id)
            self.cmd_obj.custom_command_handlers.clear()
        except:
            self.cmd_obj.show_error('Destoy event failed: {}'.format(
                traceback.format_exc()))


class _KeyDownHandler(adsk.core.KeyboardEventHandler):
    def __init__(self, cmd_obj):
        super().__init__()
        self.cmd_obj = cmd_obj
        self.cmd_obj.log_info('initialized KeyboardHandler')
        self.state = HandlerState()

    def notify(self, args: adsk.core.KeyboardEventArgs):
        try:
            self.state.call_count += 1
            cmd = args.firingEvent.sender

            self.cmd_obj.log_info('executing KeyDownHandler')
            self.cmd_obj.on_key_down(args, cmd, cmd.commandInputs,
                                     get_values(cmd.commandInputs),
                                     args.keyCode, self.state)
        except:
            self.cmd_obj.show_error('Key Down event failed: {}'.format(
                traceback.format_exc()))


class _CustomCommandEventHandler(adsk.core.CustomEventHandler):
    def __init__(self, cmd_obj, notify_func):
        super().__init__()
        self.state = HandlerState()

        self.cmd_obj = cmd_obj
        self.notify_func = notify_func

    def notify(self, args):
        try:
            self.state.call_count += 1
            self.cmd_obj.log_info(
                'executing CustomEventHandler \'{0}\''.format(
                    self.notify_func.__name__))
            self.notify_func(args, self.cmd_obj.fusion_command, self.state)
        except:
            self.cmd_obj.show_error(
                'Custom Command event \'{0}\' failed: {1}'.format(
                    self.notify_func.__name__, traceback.format_exc()))
