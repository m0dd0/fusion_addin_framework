"""[summary]
"""

# pylint: disable = unused-import
# pylint: disable = unused-argument

from typing import Dict, Any

import adsk.core
import adsk.fusion

from ...apper.apper import Fusion360CommandBase
from ...apper.apper import Utilities
from ...apper.apper import Fusion360Utilities
from ...apper.apper.Fusion360Utilities import AppObjects

ao = AppObjects()


# Class for a Fusion 360 Command
# Place your program logic here
class CustomCommand(Fusion360CommandBase):
    """[summary]

    Args:
        Fusion360CommandBase ([type]): [description]
    """
    def on_create(self, args: adsk.core.CommandEventArgs,
                  command: adsk.core.Command, inputs: adsk.core.CommandInputs):
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
        ao.ui.messageBox('executed')

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
