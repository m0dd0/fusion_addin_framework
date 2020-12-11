"""[summary]
"""

import enum
from typing import Optional
import uuid
import traceback

import adsk.core
import adsk.fusion


# Class to quickly access Fusion Application Objects
class AppObjects(object):
    """The AppObjects class wraps many common application objects required when
     writing a Fusion 360 Addin."""
    def __init__(self):

        self.app = adsk.core.Application.cast(adsk.core.Application.get())

        # Get import manager
        self.import_manager = self.app.importManager

        # Get User Interface
        self.ui = self.app.userInterface

        self._document = self.document
        self._product = self.product
        self._design = self.design

    @property
    def document(self) -> Optional[adsk.core.Document]:
        """adsk.fusion.Design from the active document

        Returns: adsk.fusion.Design from the active document

        """
        document = None
        try:
            document = self.app.activeDocument
        except:
            pass

        if document is not None:
            return document
        else:
            return None

    @property
    def product(self) -> Optional[adsk.core.Product]:
        """adsk.fusion.Design from the active document

        Returns: adsk.fusion.Design from the active document

        """
        product = None
        try:
            product = self.app.activeProduct
        except:
            pass

        if product is not None:
            return product
        else:
            return None

    @property
    def design(self) -> Optional[adsk.fusion.Design]:
        """adsk.fusion.Design from the active document

        Returns: adsk.fusion.Design from the active document

        """
        design_ = None
        if self.document is not None:
            design_ = self.document.products.itemByProductType(
                'DesignProductType')

        if design_ is not None:
            return design_
        else:
            return None

    @property
    def cam(self) -> Optional[adsk.cam.CAM]:
        """adsk.cam.CAM from the active document

        Note if the document has never been activated in the CAM environment this will return None

        Returns: adsk.cam.CAM from the active document

        """
        cam_ = None
        if self.document is not None:
            cam_ = self.document.products.itemByProductType('CAMProductType')
        if cam_ is not None:
            return cam_
        else:
            return None

    @property
    def root_comp(self) -> Optional[adsk.fusion.Component]:
        """Every adsk.fusion.Design has exactly one Root Component

        It should also be noted that the Root Component in the Design does not
        have an associated Occurrence

        Returns: The Root Component of the adsk.fusion.Design

        """
        root_comp_ = None
        if self.product is not None:
            if self.product.productType == 'DesignProductType':
                root_comp_ = self.design.rootComponent

            if root_comp_ is not None:
                return root_comp_
            else:
                return None

    @property
    def temp_brep_mgr(self) -> adsk.fusion.TemporaryBRepManager:
        self.design.designType = adsk.fusion.DesignTypes.DirectDesignType
        return adsk.fusion.TemporaryBRepManager.get()

    @property
    def time_line(self) -> Optional[adsk.fusion.Timeline]:
        """adsk.fusion.Timeline from the active adsk.fusion.Design

        Returns: adsk.fusion.Timeline from the active adsk.fusion.Design

        """
        time_line_ = None
        if self.product is not None:
            if self.product.productType == 'DesignProductType':
                if self._design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
                    time_line_ = self.product.timeline

        if time_line_ is not None:
            return time_line_
        else:
            return None

    @property
    def units_manager(self) -> Optional[adsk.core.UnitsManager]:
        """adsk.core.UnitsManager from the active document

        If not in an active document with design workspace active, will return
     adsk.core.UnitsManager if possible

        Returns: adsk.fusion.FusionUnitsManager or adsk.core.UnitsManager if
    in a different workspace than design.
        """
        units_manager_ = None
        if self.product is not None:
            if self.product.productType == 'DesignProductType':
                units_manager_ = self._design.fusionUnitsManager
            else:
                try:
                    units_manager_ = self.product.unitsManager
                except:
                    pass
        if units_manager_ is not None:
            return units_manager_
        else:
            return None

    @property
    def f_units_manager(self) -> Optional[adsk.fusion.FusionUnitsManager]:
        """adsk.fusion.FusionUnitsManager from the active document.

        Only work in design environment.

        Returns: adsk.fusion.FusionUnitsManager or None if in a different workspace than design.
        """
        units_manager = None
        if self.product is not None:
            if self.product.productType == 'DesignProductType':
                units_manager = self._design.fusionUnitsManager
            else:
                units_manager = None

        if units_manager is not None:
            return units_manager
        else:
            return None

    @property
    def export_manager(self) -> Optional[adsk.fusion.ExportManager]:
        """adsk.fusion.ExportManager from the active document

        Returns: adsk.fusion.ExportManager from the active document

        """
        if self._design is not None:
            export_manager_ = self._design.exportManager
            return export_manager_
        else:
            return None


def get_values(current_inputs):
    """[summary]

    Args:
        current_inputs ([type]): [description]

    Returns:
        [type]: [description]
    """
    # value types have no special super class (like SliderCommandInput)
    # for consistency for all types lists are used
    value_types = [
        adsk.core.AngleValueCommandInput.classType(),
        adsk.core.BoolValueCommandInput.classType(),
        adsk.core.DistanceValueCommandInput.classType(),
        adsk.core.FloatSpinnerCommandInput.classType(),
        adsk.core.IntegerSpinnerCommandInput.classType(),
        adsk.core.ValueCommandInput.classType(),
        adsk.core.StringValueCommandInput.classType(),
        adsk.core.FloatSpinnerCommandInput.classType(),
        adsk.core.IntegerSpinnerCommandInput.classType(),
    ]

    slider_types = [
        adsk.core.FloatSliderCommandInput.classType(),
        adsk.core.IntegerSliderCommandInput.classType(),
    ]

    list_types = [
        adsk.core.ButtonRowCommandInput.classType(),
        adsk.core.DropDownCommandInput.classType(),
        adsk.core.RadioButtonGroupCommandInput.classType(),
    ]

    selection_types = [adsk.core.SelectionCommandInput.classType()]

    input_values = {}

    for command_input in current_inputs:

        if command_input.objectType in value_types:
            input_values[command_input.id] = command_input.value

        elif command_input.objectType in slider_types:
            val = command_input.valueOne
            if command_input.hasTwoSliders:
                val = (val, command_input.valueTwo)
            input_values[command_input.id] = val

        elif command_input.objectType in selection_types:
            input_values[command_input.id] = [
                command_input.selection(i).entity
                for i in range(command_input.selectionCount)
            ]

        elif command_input.objectType in list_types:
            input_values[command_input.id] = [
                item for item in command_input.listItems if item.isSelected
            ]

        input_values[command_input.id + '_input'] = command_input

    return input_values


@enum.unique
class InputIdsBase(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):  #pylint:disable=no-self-argument,unused-argument
        return name + '_input_id'


class CustomEventHandler(adsk.core.CustomEventHandler):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def notify(self, args):
        try:
            args = adsk.core.CustomEventArgs.cast(args)
            self.func()
        except:
            print('Custom event ({0}) failed: {1}'.format(
                self.func.__name__, traceback.format_exc()))


def do_with_custom_event(func):
    app = adsk.core.Application.get()
    event_id = str(uuid.uuid4())
    event = app.registerCustomEvent(event_id)
    handler = CustomEventHandler(func)
    event.add(handler)
    app.fireCustomEvent(event_id)
    app.unregisterCustomEvent(event_id)
