### VERERBUNG ###


class MyCommand(faf.CommandBase):
    pass


cmd = MyCommand()
cmd.controls = []
### HTML STYLE ###

import fusion_addin_framework as faf

faf.Workspace(
    id="Solid",
    children=[
        faf.Tab(
            id="Tools",
            children=[
                faf.Panel(
                    id="Addin",
                    children=[
                        faf.Command(),
                    ],
                ),
            ],
        ),
    ],
)


### CHAINED STYLE ###

faf.Workspace(id="Solid").tab(id="Tools").panel(id="Addin").buttondefintion(
    id="asdfasdfasdfasdfasdf"
).addCommand()


### COMMAND CENTERED ###

cmd = faf.Command(controls=[])


###
from typing import List, Callable, Union
from pathlib import Path
from uuid import uuid4
import logging
import json
import random

from .defaults import get_default


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
        children: List[Tab] = None,
    ):
        args = locals()
        given_args = {k: v for k, v in args.items() if k is not None}
        args = {k: get_default("workspace", k) for k in args if k is None}

        app = adsk.core.Application.get()
        ws_coll = app.userInterface.workspaces

        fusion_ws = ws_coll.itemById(args["id"])
        if fusion_ws:
            if fusion_ws.isNative:
                not_setable = set(given_args.keys()) - {"id", "children"}
                if not_setable is not None:
                    logging.warning(
                        "The following arguments for the workspace (id: {0}) "
                        "were ignored since they cant be manipulated on a "
                        "native Workspace: {1}".format(id, not_setable)
                    )
            else:
                pass
                # TODO implement if app managemnt is created

        # create new workspace
        else:

            if name is None:
                dflt = get_default("workspace", "name")
                if dflt == "random":
                    name = random.choice(random_names["workspace"])
                else:
                    name = str(dflt)  # in case defaults json has no string

            if product_type is None:
                product_type = get_default("workspace", "name")
                if product_type not in app.supportedProductTypes:
                    product_type = get_by_multiindex("workspace", "product_type")
                    logging.warning(
                        "The provided producttype for the workspace {0} is not "
                        "supported. Therefore the default product type {1} was "
                        "used.".format(id, product_type)
                    )

            if picture is None:
                dflt = get_default("workspace", "picture")
            #     if dflt == default_pictures

            # fusion_ws = ws_coll.add(
            #     product_type,
            #     id,
            #     name,
            # )

    def panel(self):
        # create panel if not exists and reuten newly created or existing panel
        pass

    def toolbar(self):
        pass


class Tab:
    def __init__(
        self,
        name: str = None,  # add
        id: str = None,  # add
        position_index: int = None,
        is_visible: bool = None,
        children: List[Panel] = None,
        parents=None,
    ):
        pass


class Panel:
    def __init__(
        self,
        name: str,
        id: str,
        position_index: int,
        is_visible: bool,
        children: List[Control],
        parents,
    ):
        pass


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


class Button(Control):
    def __init__(self, parent, command):
        super().__init__(parent, command)


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


### ORIGINAL ###

import traceback
import adsk.core
import adsk.fusion

handlers = []


class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            args = adsk.core.CommandCreatedEventArgs.cast(args)
            cmd = args.command

            on_execute = MyExecuteHandler()
            cmd.execute.add(on_execute)
            handlers.append(on_execute)

            inputs = cmd.commandInputs
            inputs.addBoolValueInput("bool_input_id", "bool", True, "", False)
        except:
            print("Failed:\n{}".format(traceback.format_exc()))


class MyExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            args = adsk.core.CommandEventArgs.cast(args)

        except:
            print("Failed:\n{}".format(traceback.format_exc()))


def run():
    app = adsk.core.Application.get()
    ui = app.userInterface

    on_command_created = MyCommandCreatedHandler()
    handlers.append(on_command_created)

    workspace = ui.workspaces.itemById("Solid")
    tab = workspace.toolbarTabs.itemById("Tools")
    panel = tab.toolbarPanels.itemById("Addins")

    cmd_def = ui.commandDefinitions.addButtonDefinition(
        "cmd_def_id", "cmd name", "tooltip"
    )
    cmd_def.commandCreated.add(on_command_created)

    # cmd_def.controlDefinition # specifying control more accurately

    panel.controls.addCommand(cmd_def)


def stop():
    pass
