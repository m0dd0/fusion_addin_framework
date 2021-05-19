"""This modules contains utility functions."""

from typing import Iterable
import logging

import adsk.core, adsk.fusion


def create_logger(
    name: str,
    handlers: Iterable[logging.Handler],
    level: int = logging.DEBUG,
    message_format: str = "{asctime} {levelname} {module}/{funcName}: {message}",
) -> logging.Logger:
    """Sets up a logger instance with the provided settings.

    The given level and format will be set to all passed handlers.
    It will be ensured that all handlers are removed before the handlers are added.
    This can be useful because they will not always get deleted when restarting
    your addin.

    Args:
        name (str): The name of the logger.
        handlers (Iterable[logging.Handler]): A list of handlers to connect to the logger.
        level (int, optional): The logger level. Defaults to logging.DEBUG.
        message_format (str, optional): The format string for the handlers. Defaults to "{asctime} {levelname} {module}/{funcName}: {message}".

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)

    # logger always at lowest level set only handlers levels are set by level attribute
    logger.setLevel(logging.DEBUG)

    # delete allexisting handlers, to ensure no duplicated handler is added
    # when this method is called twice
    if logger.hasHandlers():
        logger.handlers.clear()

    # logging format (for all handlers)
    formatter = logging.Formatter(message_format, style="{")

    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)

    return logger


def get_input_values(event_args):
    """[summary]

    Args:
        event_args ([type]): [description]
    """
    pass
    # TODO implement


class TextPaletteLoggingHandler(logging.StreamHandler):
    """Logging Handler for python logging mechanism to use the textCommand Palett
    in the Fusion GUI to output logging messages.
    """

    def __init__(self):
        """Initialises the handler. TextCommand Paleete needs to be accessed manually"""
        super().__init__()
        self.textPalette = adsk.core.Application.get().userInterface.palettes.itemById(
            "TextCommands"
        )
        # self.textPalette.isVisible = True

    def emit(self, record):
        self.textPalette.writeText(self.format(record))
        # adsk.doEvents() # doesnt seem to be necessary


def ui_ids_dict():
    """Dumps the ids of the fusion user interface element to a hierachical dict.

    To dump the dict to a file use

    with open(Path(__file__).absolute().parent / "ui_ids.json", "w+") as f:
        json.dump(ui_ids_dict(), f, indent=4)
    """

    def get_controls(parent):
        controls = {}
        for ctrl in parent.controls:
            if ctrl.objectType == adsk.core.CommandControl.classType():
                cmd_def_id = None
                # for come controls the commnd defintion is not acceisble
                try:
                    cmd_def_id = ctrl.commandDefinition.id
                except:
                    pass
                controls[ctrl.id] = cmd_def_id
            elif ctrl.objectType == adsk.core.DropDownControl.classType():
                controls[ctrl.id] = get_controls(ctrl)
            elif ctrl.objectType == adsk.core.SplitButtonControl.classType():
                cmd_def_ids = []
                try:
                    cmd_def_ids.append(ctrl.defaultCommandDefinition.id)
                except:
                    cmd_def_ids.append(None)
                try:
                    for cmd_def in ctrl.additionalDefinitions:
                        cmd_def_id.append(cmd_def.id)
                except:
                    cmd_def_ids.append(None)

                controls[ctrl.id] = cmd_def_ids

        return controls

    def get_panels(tab):
        panels = {}
        # some panels collections contina None elements
        # these collections will also raise errors when iterating over it or using .item()
        # thererfore [] must be used for iterating over them
        for i in range(tab.toolbarPanels.count):
            panel = tab.toolbarPanels[i]
            if panel is not None:
                panels[panel.id] = get_controls(panel)
        return panels

    def get_tabs(ws):
        tabs = {}
        for tab in ws.toolbarTabs:
            tabs[tab.id] = get_panels(tab)
        return tabs

    def get_workspaces(ui):
        workspaces = {}
        for ws in ui.workspaces:
            # in this workspace attributes access results in error
            if ws.id != "DebugEnvironment":
                workspaces[ws.id] = get_tabs(ws)
        return workspaces

    def get_toolbars(ui):
        toolbars = {}
        for toolbar in ui.toolbars:
            toolbars[toolbar.id] = get_controls(toolbar)
        return toolbars

    def get_palettes(ui):
        paletts = []
        for pallet in ui.palettes:
            paletts.append(pallet.id)
        return paletts

    ui = adsk.core.Application.get().userInterface
    ui_dict = {}
    ui_dict["workspaces"] = get_workspaces(ui)
    ui_dict["toolbars"] = get_toolbars(ui)
    ui_dict["pallets"] = get_palettes(ui)

    return ui_dict
