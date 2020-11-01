""" Module providing the Fusion360 CommandBase.
"""

import sys
import os
from collections import deque
import traceback
from typing import List, Dict, Any
import logging

import adsk.core
import adsk.fusion

from .UiElements import UiItemFactory


class Fusion360CommandBase():
    """ Handles ui element creation and setting up handlers for a Command.

    This is used as an abstract base class. The child classes are implementing
    the command logic.
    """
    def __init__(
        self,
        positions: List[UiItemFactory],
        logger: logging.Logger,
        debug_to_ui: bool = True,
    ):
        self.cmd_name = os.path.basename(
            sys.modules[self.__class__.__module__].__file__)
        self.resources_path = os.path.join(
            os.path.dirname(
                os.path.abspath(
                    sys.modules[self.__class__.__module__].__file__)),
            'resources')

        self.positions_info = positions
        # path elemts are stored as tuple, second value is inidcating
        # if element was created by addin
        self.position_paths = []

        self.debug_to_ui = debug_to_ui
        self.logger = logger

        self.on_command_created_handler = _CommandCreatedEventHandler(self)
        self.command_handlers = []

        self.log_info('initialised {0} command'.format(self.cmd_name))

    def show_error(self, message: str):
        """ Shows an error message according to the command settings.

        Args:
            message (str): the message to be displayed
        """
        if self.debug_to_ui:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox(message)
        self.logger.error('({0}) {1}'.format(self.cmd_name, message))

    def log_info(self, message: str):
        """ Logs an message according to the command settings.

        Args:
            message (str): the message to log
        """
        self.logger.info('({0}) {1}'.format(self.cmd_name, message))

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
                if hasattr(elem, 'resources'):
                    elem.resources = os.path.join(self.resources_path,
                                                  elem.resources)

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

    def on_preview(self, args: adsk.core.CommandEventArgs,
                   command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                   input_values: Dict[str, Any]):
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

    def on_input_changed(self, args: adsk.core.InputChangedEventArgs,
                         command: adsk.core.Command,
                         inputs: adsk.core.CommandInputs,
                         input_values: Dict[str, Any],
                         changed_input: adsk.core.CommandInput):
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

    def on_execute(self, args: adsk.core.CommandEventArgs,
                   command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                   input_values: Dict[str, Any]):
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

    def on_destroy(self, args: adsk.core.CommandEventArgs,
                   command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                   input_values: Dict[str, Any],
                   reason: adsk.core.CommandTerminationReason):
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


class _CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self, cmd_obj):
        super().__init__()
        self.cmd_obj = cmd_obj
        self.cmd_obj.log_info('initialized CommandCreatedEventHAndler')

    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        """ Gets called if the CommandCreatedEvent is raised.

        Args:
            args (adsk.core.CommandCreatedEventArgs): according event aruments
        """
        try:
            cmd = args.command

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

            self.cmd_obj.log_info('executing CommandCreatedEventHAndler')
            # TODO add more args wrapper when needed
            self.cmd_obj.on_create(args, cmd, cmd.commandInputs)

        except:
            self.cmd_obj.show_error('Command created failed: {0}'.format(
                traceback.format_exc()))


class _PreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self, cmd_obj):
        super().__init__()
        self.cmd_obj = cmd_obj
        self.cmd_obj.log_info('initialized PreviewHandler')

    def notify(self, args: adsk.core.CommandEventArgs):
        """ Gets called if the CommandPreviewEvent is raised.

        Args:
            args (adsk.core.CommandEventArgs): according event aruments
        """
        try:
            cmd = args.firingEvent.sender

            self.cmd_obj.log_info('executing PreviewHandler')
            # TODO add more args wrapper when needed
            self.cmd_obj.on_preview(args, cmd, cmd.commandInputs,
                                    get_values(cmd.commandInputs))
        except:
            self.cmd_obj.show_error('Preview event failed: {}'.format(
                traceback.format_exc()))


class _InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self, cmd_obj):
        super().__init__()
        self.cmd_obj = cmd_obj
        self.cmd_obj.log_info('initialized InputChangedHandler')

    def notify(self, args: adsk.core.InputChangedEventArgs):
        """ Gets called if the InputChangedEvent is raised.

        Args:
            args (adsk.core.InputChangedEventArgs): according event aruments
        """
        try:
            cmd = args.firingEvent.sender

            self.cmd_obj.log_info('executing InputCHangedHandler')
            # TODO add more args wrapper when needed
            self.cmd_obj.on_input_changed(args, cmd, cmd.commandInputs,
                                          get_values(cmd.commandInputs),
                                          args.input)

        except:
            self.cmd_obj.show_error('Input changed event failed: {}'.format(
                traceback.format_exc()))


class _CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self, cmd_obj):
        super().__init__()
        self.cmd_obj = cmd_obj
        self.cmd_obj.log_info('initialized CommandExecuteHandler')

    def notify(self, args: adsk.core.CommandEventArgs):
        """ Gets called if the CommandExecuteEvent is raised.

        Args:
            args (adsk.core.CommandEventArgs): according event aruments
        """
        try:
            cmd = args.firingEvent.sender

            self.cmd_obj.log_info('executing CommandExecuteHandler')
            # TODO add more args wrapper when needed
            self.cmd_obj.on_execute(args, cmd, cmd.commandInputs,
                                    get_values(cmd.commandInputs))

        except:
            self.cmd_obj.show_error('Command execute event failed: {}'.format(
                traceback.format_exc()))


class _DestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self, cmd_obj):
        super().__init__()
        self.cmd_obj = cmd_obj
        self.cmd_obj.log_info('initialized DestroyHandler')

    def notify(self, args: adsk.core.CommandEventArgs):
        """ Gets called if the CommandDestroyEvent is raised.

        Args:
            args (adsk.core.CommandEventArgs): according event aruments
        """
        try:
            cmd = args.firingEvent.sender

            self.cmd_obj.log_info('executing DestroyHandler')
            # TODO add more args wrapper when needed
            self.cmd_obj.on_destroy(args, cmd, cmd.commandInputs,
                                    get_values(cmd.commandInputs),
                                    args.terminationReason)

        except:
            self.cmd_obj.show_error('Destoy event failed: {}'.format(
                traceback.format_exc()))


def get_values(current_inputs):
    """ Returns a dictionary with all input VALUES as values. 
    Input Ids are the keys.
    """
    return current_inputs

    # TODO validate and imporve function
    # value_types = [
    #     adsk.core.BoolValueCommandInput.classType(),
    #     adsk.core.DistanceValueCommandInput.classType(),
    #     adsk.core.FloatSpinnerCommandInput.classType(),
    #     adsk.core.IntegerSpinnerCommandInput.classType(),
    #     adsk.core.ValueCommandInput.classType(),
    #     adsk.core.StringValueCommandInput.classType()
    # ]

    # slider_types = [
    #     adsk.core.FloatSliderCommandInput.classType(),
    #     adsk.core.IntegerSliderCommandInput.classType()
    # ]

    # list_types = [
    #     adsk.core.ButtonRowCommandInput.classType(),
    #     adsk.core.DropDownCommandInput.classType(),
    #     adsk.core.RadioButtonGroupCommandInput.classType()
    # ]

    # selection_types = [adsk.core.SelectionCommandInput.classType()]

    # input_values = {}
    # input_values.clear()

    # for command_input in current_inputs:

    #     # If the input type is in this list the value of the input is returned
    #     if command_input.objectType in value_types:
    #         input_values[command_input.id] = command_input.value
    #         input_values[command_input.id + '_input'] = command_input

    #     elif command_input.objectType in slider_types:
    #         input_values[command_input.id] = command_input.valueOne
    #         input_values[command_input.id + '_input'] = command_input

    #     # TODO need to account for radio and button multi select also
    #     # If the input type is in this list the name of the selected list item is returned
    #     elif command_input.objectType in list_types:
    #         if command_input.objectType == adsk.core.DropDownCommandInput.classType(
    #         ):
    #             if command_input.dropDownStyle == adsk.core.DropDownStyles.CheckBoxDropDownStyle:
    #                 input_values[command_input.id] = command_input.listItems
    #                 input_values[command_input.id + '_input'] = command_input

    #             else:
    #                 if command_input.selectedItem is not None:
    #                     input_values[
    #                         command_input.id] = command_input.selectedItem.name
    #                     input_values[command_input.id +
    #                                  '_input'] = command_input
    #         else:
    #             if command_input.selectedItem is not None:
    #                 input_values[
    #                     command_input.id] = command_input.selectedItem.name
    #             else:
    #                 input_values[command_input.id] = None
    #             input_values[command_input.id + '_input'] = command_input

    #     # If the input type is a selection an array of entities is returned
    #     elif command_input.objectType in selection_types:
    #         selections = []
    #         if command_input.selectionCount > 0:
    #             for i in range(0, command_input.selectionCount):
    #                 selections.append(command_input.selection(i).entity)

    #         input_values[command_input.id] = selections
    #         input_values[command_input.id + '_input'] = command_input

    #     else:
    #         input_values[command_input.id] = command_input.name
    #         input_values[command_input.id + '_input'] = command_input

    # return input_values
