import logging
from typing import List, Union, Callable
from pathlib import Path
from uuid import uuid4

import adsk.core
import adsk.fusion

from . import defaults as dflts
from . import handlers
from . import msgs
from .util.py_utils import comes_after

# from .defaults import

# ws = Workspace(id="Solid")
# tab = Tab(id="Tools", parent_workspace=ws)
# panel = Panel(id="Addin", parent_tab=tab)
# button = Button(id="faf_button_id", parent_panel=panel)
# cmd = Command(id="faf_command_id", parent_button=button)

# cmd = Command(Button(Panel(Tab(Workspace))))

# class FusionWrapper():
#     def __init__(
#         self,
# all properties of a fusion ui element that can be set
# ...
# ):
# get the given properties
# given_args = get_given_args(locals())

# parse all properties (externally) and save them as attributes (?)
# self.property = parse(property)

# app = adsk.core.Application.get()
# paretn_coll = app.userInterface.workspaces

# self.in_fusion = parent_coll.itemById(self.id)
# if self.in_fusion:
#     if self.in_fusion.isNative:
#     not_setable = set(given_args.keys()) - {"id"}
#     if not_setable:
#         show_warning()
# else:
#     overwrite

# create new workspace
# else:
#     self.in_fusion = app.userInterface.workspaces.add(
#         self.product_type, self.id, self.name, self.picture
#     )
#     self.in_fusion.toolClipFilename = self.picture_tooltip
#     self.in_fusion.tooltip = self.tooltip_head
#     self.in_fusion.tooltipDescription = self.tooltip_head


class Workspace:
    def __init__(
        self,
        name: str = None,  # add
        id: str = None,  # add
        product_type: str = None,  # add
        picture: Union[str, Path] = None,  # add
        picture_tooltip: Union[str, Path] = None,
        tooltip_head: str = None,
        tooltip_text: str = None,
    ):
        given_args = {k: v for k, v in locals().items() if v is not None}
        self.id = dflts.id(id, "random")
        self.name = dflts.name(name, "workspace", "random")
        self.product_type = dflts.no_parse(product_type, "DesignProductType")
        self.picture = dflts.picture(picture, "lighbulb")
        self.picture_tooltip = dflts.picture(picture_tooltip, "")
        self.tooltip_head = dflts.no_parse(tooltip_head, "")
        self.tooltip_text = dflts.no_parse(tooltip_text, "")

        app = adsk.core.Application.get()
        ws_coll = app.userInterface.workspaces

        self.in_fusion = ws_coll.itemById(self.id)
        if self.in_fusion:
            if self.in_fusion.isNative:
                not_setable = set(given_args.keys()) - {"id", "self"}
                if not_setable:
                    logging.warning(
                        msgs.setting_on_native("workspace", self.id, not_setable)
                    )
                self.name = self.in_fusion.name
                self.product_type = self.in_fusion.productType
                self.picture = self.in_fusion.resourceFolder
                self.picture_tooltip = self.in_fusion.toolClipFilename
                self.tooltip_head = self.in_fusion.tooltip
                self.tooltip_text = self.in_fusion.tooltipDescription
            else:
                pass

        # create new workspace
        else:
            self.in_fusion = app.userInterface.workspaces.add(
                self.product_type, self.id, self.name, self.picture
            )
            self.in_fusion.toolClipFilename = self.picture_tooltip
            self.in_fusion.tooltip = self.tooltip_head
            self.in_fusion.tooltipDescription = self.tooltip_head


class Tab:
    def __init__(
        self,
        parent_workspace: Workspace,
        name: str = None,  # add
        id: str = None,  # add
        # position_index: int = None,
        # is_visible: bool = None,
    ):
        given_args = {k: v for k, v in locals().items() if v is not None}
        self.parent_workspace = parent_workspace
        self.name = dflts.name(name, "tab", "random")
        self.id = dflts.id(id, "random")
        # self.position_index = dflts.no_parse(position_index, -1)
        # self.is_visible = dflts.no_parse(is_visible, True)

        logging.warning(
            "Its currently not supported by Fusion360 to set the position of a tab within a workspace."
        )

        self.in_fusion = parent_workspace.in_fusion.toolbarTabs.itemById(self.id)
        if self.in_fusion:
            if self.in_fusion.isNative:
                not_setable = set(given_args.keys()) - {"id"}
                if not_setable:
                    logging.warning(msgs.setting_on_native("tab", self.id, not_setable))
            else:
                # TODO implement if app managemnt is created
                pass
        # create new tab
        else:
            self.in_fusion = parent_workspace.in_fusion.toolbarTabs.add(
                self.id, self.name
            )

        self.index = self.in_fusion.position_index
        self.isVisible = self.in_fusion.is_visible

        # @property
        # def position_index(self):


class Panel:
    def __init__(
        self,
        parent_tab: Tab,
        name: str = None,
        id: str = None,
        position_index: int = None,
        is_visible: bool = None,
    ):
        given_args = {k: v for k, v in locals().items() if v is not None}
        dflts.fill
        self.parent_tab = parent_tab
        self.name = dflts.name(name, "panel", "random")
        self.id = dflts.id(id, "random")
        self.position_index = dflts.no_parse(position_index, -1)
        self.is_visible = dflts.no_parse(is_visible, True)

        self.in_fusion = parent_tab.in_fusion.toolbarPanels.itemById(self.id)

        if self.in_fusion:
            if self.in_fusion.isNative:
                not_setable = set(given_args.keys()) - {"id"}
                if not_setable:
                    logging.warning(
                        msgs.setting_on_native("panel", self.id, not_setable)
                    )
            else:
                # TODO implement if app managemnt is created
                pass
        # create new tab
        else:
            panel_order = {
                p.indexWithinTab(): p.id
                for p in self.parent_tab.in_fusion.toolbarPanels
            }
            before_id = panel_order[
                comes_after(list(panel_order.keys()), self.position_index)
            ]
            self.in_fusion = parent_tab.in_fusion.toolbarPanels.add(
                self.id, self.name, before_id, True
            )
            self.in_fusion.isVisible = is_visible


# class Button:
#     def __init__(self, parent_panel: Panel, id=None, position=None, is_promoted=None):
#         self.parent_panel = parent_panel
#         self.id = id
#         self.position = position
#         self.is_promoted = is_promoted
#         self.in_fusion = self.create_control()

#     def create_control(
#         self,
#         name="<unused button>",
#         tooltip="this button was created but no command has been connected to it yet",
#         image="",
#     ):
#         return adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
#             self.id, name, tooltip, image  # TODO button image
#         )


# class Command:
#     def __init__(
#         self,
#         name: str = None,
#         id: str = None,
#         parent_button: Button = None,
#         tooltip: str = None,
#         image: Path = None,
#         on_created: Callable = None,
#         on_input_changed: Callable = None,
#         on_preview: Callable = None,
#         on_execute: Callable = None,
#         on_destroy: Callable = None,
#     ):
#         button.in_fusion.deleteMe()
#         button.create_control(name, tooltip, image)
#         self.in_fusion = button.cmd-
#         button.cmd_def.commandCreated.add(
#             handlers._CommandCreatedHandler(
#                 on_created, on_input_changed, on_execute, on_destroy
#             )
#         )

#     def add_control(self):
#         pass

#     def remove_control(self, control):
#         pass
