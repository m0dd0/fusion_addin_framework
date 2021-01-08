import logging
from typing import List, Union, Callable
from pathlib import Path
from uuid import uuid4

import adsk.core
import adsk.fusion

from .defaults import fill_args
from .util.py_utils import comes_after


class FusionWrapper:
    def __init__(self):
        pass


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
        # children: List[Tab] = None,
    ):
        args, given_args = fill_args(locals(), "workspace")

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

        # self.children = []
        #     for tab in children:
        #         fusion_tab = fusion_ws.toolbarTabs.itemById(tab.id)
        #         if fusion_tab:
        #             if
        #         else:
        #             fusion_tab = fusion_ws.toolbarTabs.add(tab.id, tab.name)
        #             tab.parents.append(self)

    # def tab(
    #     self,
    #     name: str = None,  # add
    #     id: str = None,  # add
    #     position_index: int = None,
    #     is_visible: bool = None,
    #     # children: List[Panel] = None,
    # ):
    #     new_tab = Tab(name, id, position_index, is_visible, [self])
    #     self.children.append(new_tab)
    #     return new_tab

    # def toolbar(self):
    #     pass

    # @classmethod
    # def create_from_fusion(cls, fusion_obj):
    #     pass


class Tab:
    def __init__(
        self,
        parent_workspace: Workspace,  # TODO support ultiple parents, TODO default
        name: str = None,  # add
        id: str = None,  # add
        position_index: int = None,
        is_visible: bool = None,
        # children: List[Panel] = None,
        # parents: Union[List[Workspace], Workspace] = None,
    ):
        args, given_args = fill_args(locals(), "tab")

        # if not isinstance(parents, List):
        #     parents = [parents]
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
        # children: List[Control],
        # parents, # TODO support multiple parents
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


dummy_button = (
    adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
        uuid4(),
        "unused button",
        "this button was createdbut has no connected command",
        "",
    )
)


class Button:
    def __init__(self, position, parent: Panel):
        self.cmd_def = parent.in_fusion.controls.addCommand(
            dummy_button, position, True
        )


class Command:
    def __init__(self, button: Button):
        button.cmd_def.commandCreated


class Control:
    def __init__(self, parent, command):
        self.connected_command = None

    def conncect_command(
        self,
        name,
        id,
        on_created: Callable = None,
        on_input_changed: Callable = None,
        on_preview: Callable = None,
        on_execute: Callable = None,
        on_destroy: Callable = None,
    ):
        if self.connected_command:
            self.connected_command.remove_control(self)
            self.connected_command = None
            print("WARNING")
        self.connected_command = Command(
            self, on_created, on_input_changed, on_preview, on_execute, on_destroy
        )


class Command:
    def __init__(
        self,
        name: str = None,
        id: str = None,
        controlls: Union[List[Control], Control] = None,
        on_created: Callable = None,
        on_input_changed: Callable = None,
        on_preview: Callable = None,
        on_execute: Callable = None,
        on_destroy: Callable = None,
        command_class=None,
    ):
        pass

    def add_control(self):
        pass

    def remove_control(self, control):
        pass
