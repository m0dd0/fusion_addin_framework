import logging
from typing import List, Union, Callable
from pathlib import Path
from uuid import uuid4

import adsk.core
import adsk.fusion

from .defaults import fill_args
from .util.py_utils import comes_after
from . import handlers


ws = Workspace(id="Solid")
tab = Tab(id="Tools", parent_workspace=ws)
panel = Panel(id="Addin", parent_tab=tab)
button = Button(id="faf_button_id", parent_panel=panel)
cmd = Command(id="faf_command_id", parent_button=button)

cmd = Command(Button(Panel(Tab(Workspace))))

# class FusionWrapper:
#     def __init__(self):
#         pass

#     @classmethod
#     def create_from_fusion(cls, fusion_obj):
#         pass


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
        args, given_args = fill_args(locals(), "workspace")
        for name, value in args.items():
            setattr(self, name, value)

        app = adsk.core.Application.get()
        ws_coll = app.userInterface.workspaces

        self.in_fusion = ws_coll.itemById(args["id"])
        if self.in_fusion:
            if self.in_fusion.isNative:
                not_setable = set(given_args.keys()) - {"id", "children"}
                if not_setable:
                    logging.warning(
                        "The following arguments for the workspace (id: {0}) "
                        "were ignored since they cant be manipulated on a "
                        "native Workspace: {1}".format(args["id"], not_setable)
                    )
            else:
                pass
                # TODO implement if app managemnt is created

        # create new workspace
        else:
            self.in_fusion = app.userInterface.workspaces.add(
                args["product_type"], args["id"], args["name"], args["picture"]
            )
            self.in_fusion.toolClipFilename = args["picture_tooltip"]
            self.in_fusion.tooltip = args["tooltip_head"]
            self.in_fusion.tooltipDescription = args["tooltip_text"]


class Tab:
    def __init__(
        self,
        parent_workspace: Workspace,  # TODO support ultiple parents, TODO default
        name: str = None,  # add
        id: str = None,  # add
        position_index: int = None,
        is_visible: bool = None,
    ):
        args, given_args = fill_args(locals(), "tab")

        self.in_fusion = parent_workspace.in_fusion.toolbarTabs.itemById(args["id"])
        if self.in_fusion:
            if self.in_fusion.isNative:
                not_setable = set(given_args.keys()) - {"id", "children"}
                if not_setable:
                    logging.warning(
                        "The following arguments for the tab (id: {0}) "
                        "were ignored since they cant be manipulated on a "
                        "native tab: {1}".format(args["id"], not_setable)
                    )
            else:
                # TODO implement if app managemnt is created
                pass
        # create new tab
        else:
            self.in_fusion = parent_workspace.in_fusion.toolbarTabs.add(
                args["id"], args["name"]
            )
            self.in_fusion.index = args["position_index"]
            self.in_fusion.isVisible = args["is_visible"]


class Panel:
    def __init__(
        self,
        parent_tab: Tab,  # TODO default
        name: str,
        id: str,
        position_index: int,
        is_visible: bool,
    ):
        args, given_args = fill_args(locals(), "panel")

        self.in_fusion = parent_tab.in_fusion.toolbarPanels.itemById(args["id"])

        if self.in_fusion:
            if self.in_fusion.isNative:
                not_setable = set(given_args.keys()) - {"id", "children"}
                if not_setable:
                    logging.warning(
                        "The following arguments for the panel (id: {0}) "
                        "were ignored since they cant be manipulated on a "
                        "native panel: {1}".format(args["id"], not_setable)
                    )
            else:
                # TODO implement if app managemnt is created
                pass
        # create new tab
        else:
            # TODO check behaviour of related workspaces etc.
            # TODO warning or similar
            panel_order = {p.index: p.id for p in parent_tab.in_fusion.toolbarPanels}
            before_id = panel_order[
                comes_after(list(panel_order.keys()), args["position_index"])
            ]
            self.in_fusion = parent_tab.in_fusion.toolbarPanels.add(
                args["id"], args["name"], before_id, True
            )


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
