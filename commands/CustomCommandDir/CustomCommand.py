# pylint: disable = missing-module-docstring
# pylint: disable = unused-import
# pylint: disable = unused-argument

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
    def on_create(self, args, command, inputs):
        pass

    def on_preview(self, args, command, inputs, input_values):
        pass

    def on_input_changed(self, args, command, inputs, input_values,
                         changed_input):
        pass

    def on_execute(self, args, command, inputs, input_values):
        ao.ui.messageBox('executed')

    def on_destroy(self, args, command, inputs, input_values, reason):
        pass
