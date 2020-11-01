"""[summary]

"""

from dataclasses import dataclass
from typing import Union

import adsk.core

from .Enums import ProductTypes, Workspaces, Tabs, Panels, Toolbars

# TODO use values abstract base classes


@dataclass
class UiItemFactory:
    """[summary]
    """
    pass


# Structures ################################################################
@dataclass
class Structure(UiItemFactory):
    """[summary]
    """
    pass


# http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-33f9ed37-e5c7-4153-ba85-c3254a199dd1
@dataclass
class Workspace(Structure):
    """[summary]

    Args:
        Structure ([type]): [description]

    Returns:
        [type]: [description]
    """
    ui_id: str = Workspaces.Solid
    name: str = 'Custom WS'
    resources: str = 'workspace'
    product_type: str = ProductTypes.Design
    tooltip: str = 'workspace tooltip'
    tooltip_description: str = 'workspace tooltip description'
    toolclip_resource_name: str = 'toolclip.png'

    def in_fusion(self, parent: adsk.core.UserInterface):
        """[summary]

        Args:
            parent (adsk.core.UserInterface): [description]

        Returns:
            [type]: [description]
        """
        workspace = parent.workspaces.itemById(self.ui_id)
        if workspace is None:
            workspace = parent.workspaces.add(self.product_type, self.ui_id,
                                              self.name, self.resources)
            return workspace, True
        return workspace, False


# http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-7AF58337-178C-467C-831F-285B0FB02D56
@dataclass
class Tab(Structure):
    """[summary]

    Args:
        Structure ([type]): [description]

    Returns:
        [type]: [description]
    """
    ui_id: str = Tabs.ToolsTab
    name: str = 'Custom Tab'
    is_visible: bool = True

    def in_fusion(self, parent: adsk.core.Workspace):
        """[summary]

        Args:
            parent (adsk.core.Workspace): [description]

        Returns:
            [type]: [description]
        """
        tab = parent.toolbarTabs.itemById(self.ui_id)
        if tab is None:
            tab = parent.toolbarTabs.add(self.ui_id, self.name)
            return tab, True
        return tab, False


# http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-0ca48ac9-da95-4623-bf87-150f3729717a
@dataclass
class Panel(Structure):
    """[summary]

    Args:
        Structure ([type]): [description]

    Returns:
        [type]: [description]
    """
    ui_id: str = Panels.AddIns
    name: str = 'Custom Panel'
    position_id: str = ''
    is_before: bool = True
    is_visible: bool = True

    def in_fusion(self, parent: adsk.core.ToolbarTab):
        """[summary]

        Args:
            parent (adsk.core.ToolbarTab): [description]

        Returns:
            [type]: [description]
        """
        panel = parent.toolbarPanels.itemById(self.ui_id)
        if panel is None:
            panel = parent.toolbarPanels.add(self.ui_id, self.name,
                                             self.position_id, self.is_before)
            return panel, True
        return panel, False


# http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-065bceb3-eb13-4f4f-9ed1-1ba843e51f5c
@dataclass
class Toolbar(Structure):
    """[summary]

    Args:
        Structure ([type]): [description]

    Raises:
        ValueError: [description]

    Returns:
        [type]: [description]
    """
    ui_id: str = Toolbars.QAT

    def in_fusion(self, parent: adsk.core.UserInterface):
        """[summary]

        Args:
            parent (adsk.core.UserInterface): [description]

        Raises:
            ValueError: [description]

        Returns:
            [type]: [description]
        """
        toolbar = parent.toolbars.itemById(self.ui_id)
        if toolbar is None:
            raise ValueError('{0} is no existing toolbar id.'
                             'You cant add custom toolbars.'.format(
                                 self.ui_id))
        return toolbar, False


# Controls ################################################################
@dataclass
class Control(UiItemFactory):
    """[summary]

    Args:
        UiItemFactory ([type]): [description]
    """
    pass


# http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-e02e6471-48e3-4f01-8fa8-fc1d808421e4
@dataclass
class Dropdown(Control):
    """[summary]

    Args:
        Control ([type]): [description]

    Returns:
        [type]: [description]
    """
    ui_id: str
    text: str = 'CustomDropdown'
    resources: str = 'dropdown'
    position_id: str = ''
    is_before: bool = True
    is_visible: bool = True

    def in_fusion(self, parent: Union[adsk.core.ToolbarPanel,
                                      adsk.core.DropDownControl]):
        """[summary]

        Args:
            parent (Union[adsk.core.ToolbarPanel,adsk.core.DropDownControl]): [description]

        Returns:
            [type]: [description]
        """
        dropdown_control = parent.controls.itemById(self.ui_id)
        if dropdown_control is None:
            dropdown_control = parent.controls.add(self.text, self.resources,
                                                   self.ui_id,
                                                   self.position_id,
                                                   self.is_before)
            return dropdown_control, True
        return dropdown_control, False


# http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-bb8d8c7b-3049-40c9-b7a5-76d24a462327
@dataclass
class CommandControl(Control):
    """[summary]

    Args:
        Control ([type]): [description]

    Returns:
        [type]: [description]
    """
    # ui_id: str not setable (in constructor) ???
    position_id: str = ''
    is_before: bool = True
    is_promoted: bool = True
    is_visible: bool = True
    is_promoted_by_default: bool = True

    def in_fusion(self, parent: Union[adsk.core.ToolbarPanel,
                                      adsk.core.Toolbar],
                  cmd_def: adsk.core.CommandDefinition):
        """[summary]

        Args:
            parent (Union[adsk.core.ToolbarPanel, adsk.core,Toolbar]): [description]
            cmd_def (adsk.core.CommandDefinition): [description]

        Returns:
            [type]: [description]
        """
        # commandControl needs no id in constructor
        # id will be set automatically unique, so no need to check id
        command_control = parent.controls.addCommand(cmd_def, self.position_id,
                                                     self.is_before)
        if isinstance(parent, adsk.core.ToolbarPanel
                      ):  # TODO check if also useable in dropdown
            command_control.isPromoted = self.is_promoted
            command_control.isVisible = self.is_visible
            command_control.isPromotedByDefault = self.is_promoted_by_default
        return command_control, True


# http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-717b6ac8-6e27-4246-ab55-b00c239b32f0
@dataclass
class SplitButtonControl(Control):
    """[summary]

    Args:
        Control ([type]): [description]

    Returns:
        [type]: [description]
    """
    ui_id: str
    show_last_used: bool = False
    position_id: str = ''
    is_before: bool = True
    is_visible: bool = True

    def in_fusion(self, parent: adsk.core.Toolbar,
                  cmd_def: adsk.core.CommandDefinition):
        """[summary]

        Args:
            parent (adsk.core.Toolbar): [description]
            cmd_def (adsk.core.CommandDefinition): [description]

        Returns:
            [type]: [description]
        """
        split_control = parent.controls.itemById(self.ui_id)
        if split_control is None:
            split_control = parent.controls.addSplitButton(
                cmd_def, [], self.show_last_used, self.ui_id, self.position_id,
                self.is_before)
            return split_control, True

        additional_definitions = split_control.additionalDefinitions
        additional_definitions.append(cmd_def)
        split_control.additional_definitions = additional_definitions
        return split_control, False


# CommandDefinitions ########################################################
@dataclass
class CommandDefinition(UiItemFactory):
    """[summary]

    Args:
        UiItemFactory ([type]): [description]
    """
    pass


# http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-ff5016c5-0a01-4895-8875-2df3f82cb3dd
@dataclass
class ButtonDefinition(CommandDefinition):
    """[summary]

    Args:
        CommandDefinition ([type]): [description]

    Returns:
        [type]: [description]
    """
    ui_id: str
    name: str = 'CustomButtonDefinition'
    tooltip: str = ''
    resources: str = 'button'
    is_enabled: bool = True

    def in_fusion(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        ui = adsk.core.Application.get().userInterface
        # TODO check if definiton can be used at two controls (probably not)
        # if so throw error id defintioin exists
        cmd_def = ui.commandDefinitions.itemById(self.ui_id)
        # TODO check if commanddefinition has same type as self
        if cmd_def is None:
            cmd_def = ui.commandDefinitions.addButtonDefinition(
                self.ui_id, self.name, self.tooltip, self.resources)
            return cmd_def, True
        return cmd_def, False


# http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-78da93a5-4333-49be-a172-732ca537a359
@dataclass
class CheckBoxDefinition(CommandDefinition):
    """[summary]

    Args:
        CommandDefinition ([type]): [description]

    Returns:
        [type]: [description]
    """
    ui_id: str
    name: str = 'CustomCheckBoxDefinition'
    tooltip: str = ''
    is_checked: bool = False
    is_enabled: bool = True

    def in_fusion(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        ui = adsk.core.Application.get().userInterface
        # TODO check if definiton can be used at two controls (probably not)
        # if so throw error id defintioin exists
        cmd_def = ui.commandDefinitions.itemById(self.ui_id)
        # TODO check if commanddefinition has same type as self
        if cmd_def is None:
            cmd_def = ui.commandDefinitions.addCheckBoxDefinition(
                self.ui_id, self.name, self.tooltip, self.is_checked)
            return cmd_def, True
        return cmd_def, False


# http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-bd75eda6-1d13-4274-9703-d66af434a92f
@dataclass
class ListDefinition(CommandDefinition):
    """[summary]

    Args:
        CommandDefinition ([type]): [description]

    Returns:
        [type]: [description]
    """
    ui_id: str
    name: str = 'CustomListDefiniton'
    list_control_type: int = adsk.core.ListControlDisplayTypes.CheckBoxListType
    is_enabled: bool = True
    is_visible: bool = True
    resources: str = 'button'

    def in_fusion(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        ui = adsk.core.Application.get().userInterface
        # TODO check if definiton can be used at two controls (probably not)
        # if so throw error id defintioin exists
        cmd_def = ui.commandDefinitions.itemById(self.ui_id)
        # TODO check if commanddefinition has same type as self
        if cmd_def is None:
            cmd_def = ui.commandDefintions.addListDefinition(
                self.ui_id, self.name, self.list_control_type, self.resources)
            return cmd_def, True
        return cmd_def, False


child_type = {
    adsk.core.UserInterface: (Workspace, Toolbar),
    Workspace: (Tab),
    Toolbar: (SplitButtonControl, CommandControl, Dropdown),
    SplitButtonControl: (CheckBoxDefinition, ListDefinition, ButtonDefinition),
    CommandControl: (CheckBoxDefinition, ListDefinition, ButtonDefinition),
    Tab: (Panel),
    Panel: (Dropdown, CommandControl),
    Dropdown: (Dropdown, CommandControl),
}
