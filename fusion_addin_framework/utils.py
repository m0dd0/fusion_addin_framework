"""This modules contains utility functions realted to the Fusion360 API."""

from typing import Iterable, Dict, List, Union
import logging
import json
import enum
import math
import traceback
import time
import threading
from functools import partial
import os
from pathlib import Path

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


class TextPaletteLoggingHandler(logging.StreamHandler):
    def __init__(self):
        """Logging handler utilizing Fusions text command pallete.

        Using this logging handler logging messages will be displayed in the
        text command palette in the Fusion GUI.
        The TextCommand palette needs to be accessed manually.
        """
        super().__init__()
        self.textPalette = adsk.core.Application.get().userInterface.palettes.itemById(
            "TextCommands"
        )
        # self.textPalette.isVisible = True

    def emit(self, record):
        self.textPalette.writeText(self.format(record))
        # adsk.doEvents() # doesnt seem to be necessary


def ui_ids_dict(out_file_path=None) -> Dict:
    """Dumps the ids of the fusion user interface element to a hierachical dict.

    To dump the dict to a file use

    .. code-block:: python

        with open(Path(__file__).absolute().parent / "ui_ids.json", "w+") as f:
            json.dump(ui_ids_dict(), f, indent=4)

    Returns:
        Dict: A dictionairy which represents the full user interface.
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

    if out_file_path is not None:
        with open(Path(out_file_path), "w+") as f:
            json.dump(ui_dict, f, indent=4)

    return ui_dict


@enum.unique
class InputIdsBase(enum.Enum):
    """A Enum subclass which values are of type <name>_input_type.

    <name> is the name you name the value of the instance
    """

    def _generate_next_value_(
        name, start, count, last_values
    ):  # pylint:disable=no-self-argument,unused-argument
        return name + "_input_id"


def get_values(current_inputs: adsk.core.CommandInputs) -> Dict:
    """Extracts the command values from the given CommandInputs collections and maps
    them to the id of their command.

    Args:
        current_inputs (adsk.core.CommandInputs): [description]

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

        input_values[command_input.id] = command_input

    return input_values


def change_material(
    obj: adsk.fusion.Occurrence, material_name: str
) -> adsk.core.Material:
    material = (
        adsk.core.Application.get()
        .materialLibraries.itemByName("Fusion 360 Appearance Library")
        .appearances.itemByName(material_name)
    )
    obj.appearance = material
    return material


def clear_collection(collection: adsk.core.ObjectCollection):
    """Safely clears a collection.

    Args:
        collection (adsk.core.ObjectCollection): The collection to clear.
    """
    while collection.count > 0:
        collection.item(0).deleteMe()


def orient_bounding_box(
    bounding_box: adsk.core.BoundingBox3D,
) -> adsk.core.OrientedBoundingBox3D:
    """Converts a bounding box into an oriented bounding box.

    Args:
        bounding_box (adsk.core.BoundingBox3D): The unoriented bounding box

    Returns:
        adsk.core.OrientedBoundingBox3D: The oriented bounding box.
    """
    # do not use numpy to have no third party dependencies on apper
    diagonal = [
        max_coord - min_coord
        for max_coord, min_coord in zip(
            bounding_box.minPoint.asArray(), bounding_box.maxPoint.asArray()
        )
    ]
    center = [
        min_coord + dia_coord / 2
        for min_coord, dia_coord in zip(bounding_box.minPoint.asArray(), diagonal)
    ]
    oriented_box = adsk.core.OrientedBoundingBox3D.create(
        adsk.core.Point3D.create(*center),
        adsk.core.Vector3D.create(1, 0, 0),
        adsk.core.Vector3D.create(0, 1, 0),
        abs(diagonal[0]),
        abs(diagonal[1]),
        abs(diagonal[2]),
    )
    return oriented_box


def delete_all_graphics():
    """Deletes all custom grpahics in the viewport."""
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    for comp in des.allComponents:
        clear_collection(comp.customGraphicsGroup)
    adsk.core.Application.get().activeViewport.refresh()


def create_cube(
    center: List[Union[float, int]], side_length: float
) -> adsk.fusion.BRepBody:
    return adsk.fusion.TemporaryBRepManager.get().createBox(
        adsk.core.OrientedBoundingBox3D.create(
            adsk.core.Point3D.create(*center),
            adsk.core.Vector3D.create(1, 0, 0),
            adsk.core.Vector3D.create(0, 1, 0),
            side_length,
            side_length,
            side_length,
        )
    )


def new_comp(name=None, parent=None):
    if parent is None:
        parent = adsk.fusion.Design.cast(
            adsk.core.Application.get().activeProduct
        ).rootComponent
    comp = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
    if name:
        comp.name = name
    return comp


def delete_comp(comp):
    for occ in adsk.fusion.Design.cast(
        adsk.core.Application.get().activeProduct
    ).rootComponent.allOccurrencesByComponent(comp):
        occ.deleteMe()


def get_json_attr(obj, group_name, attr_name):
    return json.loads(obj.attributes.itemByName(group_name, attr_name).value)


def view_extents_by_measure(measure: float, is_horizontal_measure: bool = True):
    """Returns the viewExtents parameter so the given model measure fits exactly
    into the viewport.

    Args:
        measure (float): measure of the model to diplay
        is_horizontal_measure (bool, optional): if the given measure is describing
            horizontal or vertical distance. Defaults to True.

    Returns:
        float: the viewExtents parameter to apply
    """
    viewport = adsk.core.Application.get().activeViewport
    is_horizontal_viewport = viewport.width > viewport.height

    if is_horizontal_viewport and is_horizontal_measure:
        factor = viewport.height / viewport.width
    elif not is_horizontal_viewport and not is_horizontal_measure:
        factor = viewport.width / viewport.height
    else:
        factor = 1

    radius = factor * measure * 0.5
    extent = math.pi * (radius ** 2)
    return extent


def view_extent_by_rectangle(horizontal: float, vertical: float):
    """Returns theviewExtens parameter so that a rectangle ith the given design
    measures will fit into the viewport.

    Args:
        horizontal (float): horizontal dimension of the model to fit
        vertical (float): vertical dimension of the model to fit

    Returns:
        float: the viewExtents parameter to apply
    """
    return max(
        view_extents_by_measure(horizontal, True),
        view_extents_by_measure(vertical, False),
    )


def set_camera(
    plane="xy",
    horizontal_borders=(0, 10),
    vertical_borders=(0, 10),
    smooth_transition=False,
):

    horizontal_extent = horizontal_borders[1] - horizontal_borders[0]
    vertical_extent = vertical_borders[1] - vertical_borders[0]

    horizontal_center = horizontal_borders[0] + horizontal_extent / 2
    vertical_center = vertical_borders[0] + vertical_extent / 2

    # being to close leads to wrong appearance in orthographic mode
    eye_distance = max(horizontal_extent, vertical_extent) * 2

    # for some weird reason the camera will result in a very strange optic
    # if the eye is exactly on a axis with the target
    # therefore a little factor needs to be added to the eye coordinates
    # or maybe not --> try this first if errors occur
    # eye_factor = 1

    if plane == "xz" or plane == "front":
        target = (horizontal_center, 0, vertical_center)
        eye = (horizontal_center, eye_distance, vertical_center)
        up_vector = (0, 0, 1)
    if plane == "xy" or plane == "top":
        target = (horizontal_center, vertical_center, 0)
        eye = (horizontal_center, vertical_center, eye_distance)
        up_vector = (0, 1, 0)
    elif plane == "yz" or plane == "right":
        target = (0, horizontal_center, vertical_center)
        eye = (eye_distance, horizontal_center, vertical_center)
        up_vector = (0, 0, 1)
    else:
        raise ValueError("Provided invalid plane.")

    camera = adsk.core.Application.get().activeViewport.camera

    camera.target = adsk.core.Point3D.create(*target)
    camera.eye = adsk.core.Point3D.create(*eye)
    camera.upVector = adsk.core.Vector3D.create(*up_vector)
    camera.isSmoothTransition = smooth_transition
    camera.viewExtents = view_extent_by_rectangle(horizontal_extent, vertical_extent)
    adsk.core.Application.get().activeViewport.camera = camera


def make_comp_invisible(comp: adsk.fusion.Component):
    libghtbulbs = [
        "isBodiesFolderLightBulbOn",
        "isConstructionFolderLightBulbOn",
        "isJointsFolderLightBulbOn",
        "isOriginFolderLightBulbOn",
        "isSketchFolderLightBulbOn",
    ]
    active_lightbulbs = [attr for attr in libghtbulbs if getattr(comp, attr)]
    for libghtbulb_attr in active_lightbulbs:
        setattr(comp, libghtbulb_attr, False)

    visible_occs = []
    for occ in comp.occurrences:
        if occ.isLightBulbOn:
            occ.isLightBulbOn = False
            visible_occs.append(occ)

    return (active_lightbulbs, visible_occs)


def unmute_errors(to_ui=True):
    # TODO test
    def decorator(func):
        def wrapped(*args, **kwargs):
            try:
                val = func(*args, **kwargs)
            except:
                msg = "Failed:\n{}".format(traceback.format_exc())
                if to_ui:
                    adsk.core.Application.get().userInterface.messageBox(msg)
                else:
                    print(msg)
            return val

        return wrapped

    return decorator


class PeriodicExecuter(threading.Thread):
    def __init__(self, interval, func, args=None, kwargs=None, wait_for_func=False):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        self.interval = interval
        self.func = partial(func, *args, **kwargs)

        self.wait_for_func = wait_for_func

        self.thread_active = True
        threading.Thread.__init__(self)
        self.daemon = True

        self.start_time = time.perf_counter()
        self.running = False

        super().start()  # start the thread itself (not the 'timer')

    def run(self):
        elapsed_time = 0
        while self.thread_active:
            current_time = time.perf_counter()
            if self.running:
                elapsed_time = current_time - self.start_time
                if elapsed_time > self.interval:
                    self.func()
                    if self.wait_for_func:
                        current_time = time.perf_counter()
                    self.start_time = current_time
            else:
                self.start_time = current_time - elapsed_time

    def pause(self):
        self.running = False

    def start(self):
        self.running = True

    def reset(self):
        self.start_time = time.perf_counter()

    def kill(self):
        self.thread_active = False
        self.join()


def get_json_from_file(path, default_value=None):
    if default_value is None:
        default_value = {}

    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    if not os.path.exists(path):
        with open(path, "w+") as f:
            json.dump(default_value, f)  # do not add indent !!!
    with open(path, "r+") as f:
        json_data = json.load(f)
    return json_data


def make_ordinal(n):
    """Convert an integer into its ordinal representation.

    make_ordinal(0)   => '0th'
    make_ordinal(3)   => '3rd'
    make_ordinal(122) => '122nd'
    make_ordinal(213) => '213th'
    """
    n = int(n)
    suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    return str(n) + suffix


class AppObjects:
    def __init__(self):
        self._app = None
        self.reload_app()

    def reload_app(self):
        self._app = adsk.core.Application.cast(adsk.core.Application.get())

    @property
    def app(self):
        return self._app

    @property
    def rootComponent(self):
        return self._app.activeDocument.design.rootComponent

    @property
    def userInterface(self):
        return self._app.userInterface

    @property
    def design(self):
        return self._app.activeDocument.design

    @property
    def commandDefinitions(self):
        return self._app.userInterface.commandDefinitions

    @property
    def workspaces(self):
        return self._app.userInterface.workspaces

    @property
    def activeViewport(self):
        return self._app.activeViewport


def get_data_folder(fusion_path, create_folders=False) -> adsk.core.DataFolder:
    app = adsk.core.Application.get()

    project_name = fusion_path[0]
    folders = fusion_path[1:]

    project = None
    for p in app.data.dataProjects:
        if p.name == project_name:
            project = p
            break
    if project is None:
        raise FileNotFoundError(f"There is no {project_name} Fusion project.")

    folder = project.rootFolder
    for sub_folder in folders:
        folder = folder.dataFolders.itemByName(sub_folder)
        if folder is None:
            if create_folders:
                folder = folder.dataFolder.add(sub_folder)
            else:
                raise FileNotFoundError(
                    f"There is no file with the provided fusion path {fusion_path}"
                )

    return folder


def get_doc(
    fusion_path, tolerance_search=False, raise_exception=True
) -> adsk.core.DataFile:
    doc_name = fusion_path[-1]
    folder = get_data_folder(fusion_path[:-1])

    if tolerance_search:
        for doc in folder.dataFiles:
            if doc_name.strip().lower() in doc.name.strip().lower():
                return doc
    else:
        for doc in folder.dataFiles:
            if doc.name == doc_name:
                return doc

    if raise_exception:
        raise FileNotFoundError(
            f"There is no file with the provided fusion path {fusion_path}"
        )
    else:
        return None


def execute_from_cmd(target_func, cmd, execution_queue):
    execution_queue.put(target_func)
    cmd.doExecute()


def execute_with_custom_event(target_func, event_id, execution_queue):
    execution_queue.put(target_func)
    adsk.core.Application.get().fireCustomEvent(event_id)


def items_by_attribute(collection, attribute_name, attribute_value):
    found_items = []
    for item in collection:
        if getattr(item, attribute_name) == attribute_value:
            found_items.append(item)
    return found_items


def item_by_attribute(collection, attribute_name, attribute_value):
    items = items_by_attribute(collection, attribute_name, attribute_value)
    if len(items) > 1:
        raise ValueError(
            f"There are multiple elemnts in the colletction which meet the condition {attribute_name}={attribute_value}."
        )
    if len(items) == 0:
        return None
    else:
        return items[0]
