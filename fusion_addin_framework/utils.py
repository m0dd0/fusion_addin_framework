"""This modules contains utility functions realted to the Fusion360 API."""
# pylint:disable=unspecified-encoding
# to avoid import error due to type hints if adsk.core not available
from __future__ import annotations
from ast import Call
from queue import Queue
from typing import Any, Callable, Iterable, Dict, List, Union, Tuple
import logging
import json
import enum
import math
import time
import threading
import os
from pathlib import Path
from functools import wraps

import adsk.core, adsk.fusion

from . import handlers


### LOGGING ###
# region
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


# endregion


### FRAMEWORK RELATED ###
# region
@enum.unique
class InputIdsBase(enum.Enum):
    """A Enum subclass which values are of type <name>_input_type.

    <name> is the name you name the value of the instance
    """

    def _generate_next_value_(
        name, start, count, last_values
    ):  # pylint:disable=no-self-argument,unused-argument
        return name + "_input_id"


def get_values(current_inputs: adsk.core.CommandInputs) -> Dict[str, Any]:
    """Extracts the command values from the given CommandInputs collections and maps
    them to the id of their command.

    Args:
        current_inputs (adsk.core.CommandInputs): A (arbitrary) command inputs group.
            In most cases this should be the inputGroup of the currentlly active command
            recieved in the inputChanged event.

    Returns:
        Dict[str, Any]: The values of the current command inputs mapped by their id. If multiple values
            can be selected a corresponding list is returned.
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


class AppObjects:
    """Collection allowing simplified access to frequtnly used API objects."""

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


# endregion


### COMPONENT RELATED ###
# region
def new_component(
    name: str = None, parent: adsk.fusion.Component = None
) -> adsk.fusion.Component:
    """Creates a new component.

    Args:
        name (str, optional): The name if the component. Defaults to the default name ("Component_xx").
        parent (adsk.fusion.Component, optional): A parent component. Defaults to thr root component.

    Returns:
        adsk.fusion.Component: The created component.
    """
    if parent is None:
        parent = adsk.fusion.Design.cast(
            adsk.core.Application.get().activeProduct
        ).rootComponent
    comp = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
    if name:
        comp.name = name
    return comp


def delete_component(component: adsk.fusion.Component):
    """Deletes a component by deleting all its occurrences in the design.

    Args:
        component (adsk.fusion.Component): The component to delete.
    """
    for occ in adsk.fusion.Design.cast(
        adsk.core.Application.get().activeProduct
    ).rootComponent.allOccurrencesByComponent(component):
        occ.deleteMe()


def make_comp_invisible(comp: adsk.fusion.Component):
    """Disables the visibility of all occurrences of the passed component.

    Args:
        comp (adsk.fusion.Component): The component to hide

    Returns:
        _type_: _description_
    """
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


# endregion


### COLLECTION RELATED ###
# region
def clear_collection(collection: adsk.core.ObjectCollection):
    """Safely clears a collection.

    Args:
        collection (adsk.core.ObjectCollection): The collection to clear.
    """
    while collection.count > 0:
        collection.item(0).deleteMe()


def items_by_attribute(
    collection: adsk.core.ObjectCollection, attribute_name: str, attribute_value: Any
) -> List[Any]:
    """Returns all objects of a collections whose attribute with the given name have the
    given value.

    Args:
        collection (adsk.core.ObjectCollection): The object collection to query.
        attribute_name (str): The name of the attribute for comparison.
        attribute_value (Any): The value of the attribute for comparison.

    Returns:
        List[Any]: The found objects which met the attribute condition.
    """

    found_items = []
    for item in collection:
        if getattr(item, attribute_name) == attribute_value:
            found_items.append(item)
    return found_items


# endregion


### HUB REALTED ###
# region
def get_data_folder(
    fusion_path: List[str], create_folders=False
) -> adsk.core.DataFolder:
    """Searches the data hub for a data folder at the given "fusion path". A "fusion path" is
    a list in the form [<project_name>,<folder>,<subfolder>,<subfolder>,...] which describes
    the position of the data folder.

    Args:
        fusion_path (List[str]): The path of the fusion data folder in the form [<project_name>,<folder>,<subfolder>,<subfolder>,...].
        create_folders (bool, optional): Indicates if new folders should be created if a folder
            in the "fusion path" doesnt exist. Defaults to False.

    Raises:
        FileNotFoundError: If create_folders is set to False and a folder in the passed
            "fusion path" doesnt exist.

    Returns:
        adsk.core.DataFolder: The queried data folder.
    """
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


def get_doc(fusion_path: List[str], tolerance_search=False) -> adsk.core.DataFile:
    """Searches the data hub for a document folder at the given "fusion path". A "fusion path" is
    a list in the form [<project_name>,<folder>,<subfolder>,<subfolder>,...,<file_name>] which describes
    the position of the file.

    Args:
        fusion_path (List[str]): The path of the fusion document in the form [<project_name>,<folder>,<subfolder>,<subfolder>,...,<file_name>].
        tolerance_search (bool, optional): If set to true file name is treated as not case
            sensitive and any whitespaces are ignored in the search. Defaults to False.

    Returns:
        adsk.core.DataFile: The queried fusion document.
    """
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

    raise FileNotFoundError(
        f"There is no file with the provided fusion path {fusion_path}"
    )


# endregion


### CAMERA ###
# region
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
    extent = math.pi * (radius**2)
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


def set_camera_viewarea(
    plane="xy",
    horizontal_borders=(0, 10),
    vertical_borders=(0, 10),
    camera: adsk.core.Camera = None,
) -> adsk.core.Camera:
    """Returns a camera which is condifured so that the vieport certainly displays the area
    defioned by the horizonal and vertical extent parameters. The viewport is set to the minimum
    area that will still display all the area.

    Args:
        plane (str, optional): The plane which shows the viewport. Defaults to "xy".
        horizontal_borders (tuple, optional): The horizontal dimension which is diaplayed. Defaults to (0, 10).
        vertical_borders (tuple, optional): The vertical dimension which is diaplayed. Defaults to (0, 10).
        camera (adsk.core.Camera, optional): A camera instance which gets adapted.
            Defaults to the currently active camera.

    Raises:
        ValueError: IF an invalid name of a plane is provided.

    Returns:
        adsk.core.Camera: The adapted camera instance.
    """

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

    if camera is None:
        camera = adsk.core.Application.get().activeViewport.camera

    camera.target = adsk.core.Point3D.create(*target)
    camera.eye = adsk.core.Point3D.create(*eye)
    camera.upVector = adsk.core.Vector3D.create(*up_vector)
    camera.viewExtents = view_extent_by_rectangle(horizontal_extent, vertical_extent)

    return camera


def set_camera_viewcube(
    view: Tuple[str], camera: adsk.core.Camera = None
) -> adsk.core.Camera:
    """Creates a camera which is oriented in the same way as a click on a edge or corner
    of the viewcube would do. The camera is builfd from the passed camera or the currently
    active viewport camera if no camera got passed. Modifies the "eye", "target", "upVector" and "isFitView"
    properties of the camera.

    Args:
        view (Tuple[str]): A Tuple containing one, two, or three unique keywords from
            {"back", "front", "right", "left", "top", "bottom"} describing the face, edge
            or corner of the viewcube
        camera (adsk.core.Camera, optional): A camera instance which gets adapted.
            Defaults to the currently active camera.

    Raises:
        ValueError: If the view arguments does not refer to a valid viewcue position.
            E.g.: ("top", "bottom"), or ("top", "top", "right") would be invalid.

    Returns:
        adsk.core.Camera: The adjusted camera.
    """
    side_eyes = {
        "back": adsk.core.Vector3D.create(0, 1, 0),
        "front": adsk.core.Vector3D.create(0, -1, 0),
        "right": adsk.core.Vector3D.create(1, 0, 0),
        "left": adsk.core.Vector3D.create(-1, 0, 0),
        "top": adsk.core.Vector3D.create(0, 0, 1),
        "bottom": adsk.core.Vector3D.create(0, 0, -1),
    }

    # input validaion to prevent hard to fix bugsx
    # if isinstance(view, str):
    #     view = view.lower()
    #     legal_words = "|".join(side_eyes.keys())
    #     if not re.fullmatch(f"({legal_words})+", view):
    #         raise ValueError("Invalid view argument.")
    #     view = re.findall(legal_words, view)  # convert to list

    if len(view) > len(set(view)):
        raise ValueError("Invalid view argument.")

    if camera is None:
        camera = adsk.core.Application.get().activeViewport.camera
    camera.isFitView = True
    # prevent bug by not setting to exactly 0
    camera.target = adsk.core.Point3D.create(0.00001, 0.00001, 0.00001)

    eye = adsk.core.Vector3D.create(0, 0, 0)
    i_vectors = 0
    for side in view:
        eye.add(side_eyes[side])
        i_vectors += 1

    if eye.length < 0.9:
        raise ValueError("Invalid view argument.")

    up_vector = adsk.core.Vector3D.create(0, 0, 1)
    if i_vectors == 1:
        if eye.z == 0:
            up_vector = adsk.core.Vector3D.create(0, 0, 1)
        else:
            up_vector = adsk.core.Vector3D.create(0, 1, 0)

    camera.upVector = up_vector

    eye.normalize()
    eye = eye.asPoint()
    camera.eye = eye

    return camera


def camera_zoom(factor: int, camera: adsk.core.Camera = None) -> adsk.core.Camera:
    """Adjusts the cameras viewWxtents by zooming. A zoom factor of n results in the viewport
    being zoomed in to show only 1/n th area of the previous area.

    Args:
        factor (int): The zoom factor
        camera (adsk.core.Camera, optional):A camera instance which gets adapted.
            Defaults to the currently active camera.

    Returns:
        adsk.core.Camera: The adjusted camera.
    """
    if camera is None:
        camera = adsk.core.Application.get().activeViewport.camera
    camera.viewExtents = camera.viewExtents / factor**2
    return camera


# endregion


### MISC ###
# region
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


def get_appearance(material_name: str) -> adsk.core.Appearance:
    """Gets the appearance with the passed name from the Fusion 360 Appearance Library.

    Args:
        material_name (str): The name of the apperance to fetch.

    Returns:
        adsk.core.Appearnce: The appearance.
    """
    material = (
        adsk.core.Application.get()
        .materialLibraries.itemByName("Fusion 360 Appearance Library")
        .appearances.itemByName(material_name)
    )
    return material


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
    """Deletes all custom grpahics in the design."""
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    for comp in des.allComponents:
        clear_collection(comp.customGraphicsGroup)
    adsk.core.Application.get().activeViewport.refresh()


def create_cube(
    center: Tuple[Union[float, int]], side_length: float
) -> adsk.fusion.BRepBody:
    """Creates a simple cube using the TemporaryBRepManager.

    Args:
        center (Tuple[Union[float, int]]): A (x,y,z)-tuple containing the cubes center coordinates.
        side_length (float): The side length of the cube.

    Returns:
        adsk.fusion.BRepBody: The transient instance of the created cube.
    """
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


def get_json_attribute(
    object_: adsk.core.Base, group_name: str, attribute_name: str
) -> Dict[str, Any]:
    """Gets the json loaded attributes of a object.

    Args:
        object_ (adsk.core.Base): The of the object in which attributs is looked for the attribute.
            (Trailing underscore to avoid redeining build in).
        group_name (str): The attribute group name of the wanted attribute.
        attribute_name (str): The name of the atribute.

    Returns:
        Dict[str, Any]: The json loaded attribute values.
    """
    return json.loads(object_.attributes.itemByName(group_name, attribute_name).value)


# endregion


### PYTHON ONLY ###
# region
def get_json_from_file(
    path: Union[str, Path], default_value: Union[Dict, List] = None
) -> Union[Dict, List]:
    """Gets the json decoded data from the file if the file exists and creates the file if
    its not exists. IF its not existing the default value is returned.

    Args:
        path (Union[str, Path]): The file path of the json file.
        default_value (Union[Dict, List], optional): The value which gets inserted into the
            newly created file and is returned in case the file doesnt exist. Defaults to None.

    Returns:
        Union[Dict, List]: The json decoded content of the file or the default value if the
            file hasnt existed yet.
    """
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


def make_ordinal(n: int) -> str:
    """Convert an integer into its ordinal representation.

    make_ordinal(0)   => '0th'
    make_ordinal(3)   => '3rd'
    make_ordinal(122) => '122nd'
    make_ordinal(213) => '213th'


    Args:
        n (int): The integer to convert.

    Returns:
        str: The resulting string.
    """
    n = int(n)
    suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    return str(n) + suffix


class AnnotatedTimer(threading.Timer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._execution_timestamp = None

    def start(self):
        self._execution_timestamp = time.perf_counter() + self.interval
        super().start()

    @property
    def execution_timestamp(self):
        return self._execution_timestamp


class PeriodicExecuter:
    def __init__(
        self,
        interval: int,
        action: Callable,
        wait_for_action: bool = False,
        initial_execution: bool = False,
    ):
        """Creates an executer which executes the passed action periodically.

        Args:
            interval (int): The time in milliseconds to wait between calls of action.
            action (Callable): The function to execute periodically. Must not accept any
                arguments.
            wait_for_action (bool, optional): Determines if the time which is needed to
                execute the action is included in the delay time or not. Defaults to False.
            initial_execution (bool, optional): Determines whether the first execution is
                executed directly after the first start call or if the interval time is waited.
        """
        self.interval = interval
        self.wait_for_func = wait_for_action
        self.action = action

        self._initial_delay = 0 if initial_execution else self.interval
        self._start_delay = self._initial_delay

        self._timer = None

    def _new_timer(self, delta):
        self._timer = AnnotatedTimer(delta, self._scheduled_action)
        self._timer.start()

    def _cancel_timer(self):
        self._timer.cancel()
        self._timer = None

    def _scheduled_action(self):
        if self.wait_for_func:
            self.action()
            self._new_timer(self.interval)
        else:
            self._new_timer(self.interval)
            self.action()

    def start(self):
        """Starts the periodic execution of the action."""
        if self._timer is None:
            self._new_timer(self._start_delay)

    def pause(self):
        """Pauses the periodic execution. This will NOT reset the delay time. So if half
        of the delay is already passed, only half of the delay will be executed after the
        executor is started again."""
        if self._timer is not None:  # only if we are currently running / not paused
            self._start_delay = self._timer.execution_timestamp - time.time()
            self._cancel_timer()

    def reset(self):
        """Resets the delay time to its maximum/interval time again indepent of the state of the executer."""
        self._start_delay = self._initial_delay
        if self._timer is not None:  # only if we are currently running / not paused
            self._cancel_timer()
            self.start()


# endregion

### THREAD / CUSTOM EVENT ###
# region
_custom_event_queues = {}  # {id:queue}


def create_custom_event(
    event_id: str, action: Call, debug_to_ui=False
) -> adsk.core.CustomEvent:
    """Creates and registers a custom event. The event is not associated with any command.
    The custom event gets removed and cleaned up when calling the addin.stop() method.
    If you dont instantiate a addin you need to clean up / unregister the event manually.

    Args:
        event_id (str): The id of the event.
        action (Call): The action which gets executed from the handler. Must accept one argument
            for eventArgs which might get passed.
        debug_to_ui (bool, optional): Whether any errors appearing during execution
                of the action are displayed in messageBox. Defaults to False.

    Returns:
        adsk.core.CustomEvent: The created CustomEvent.
    """
    custom_event = adsk.core.Application.get().registerCustomEvent(event_id)
    custom_handler = handlers.GenericCustomEventHandler(
        action, custom_event, debug_to_ui
    )
    custom_event.add(custom_handler)
    return custom_event


def _generic_custom_event_action(
    event_args: adsk.core.CustomEventArgs,  # pylint:disable=unused-argument
):
    """The generic handler function used in the thread event.
    Executes all actions which got stored in the corresponding queue.

    Args:
        event_args (adsk.core.CustomEventArgs): The eventArgs which get passed to the handler
            notify by Fusion. However they are ignored.
    """
    event_queue = _custom_event_queues[event_args.firingEvent.eventId]
    while not event_queue.empty():
        event_queue.get()()


def execute_as_event(
    to_execute: Callable, event_id: str = None, debug_to_ui: bool = False
):
    """Utility function which allows you to execute the passed Callable from witihn a
    custom event. This is needed when you want to trigger some Fusion related actions
    from a thread or other external non Fusion stimuli. The passed Callable must not accept any
    arguments.

    Args:
        to_execute (Callable): The argument free action to execute.
        debug_to_ui (bool, optional): Whether any errors appearing during execution
                of the action are displayed in messageBox. Defaults to False.
    """
    if event_id is None:
        event_id = "faf_utility_default_custom_event"

    if event_id not in _custom_event_queues.keys():
        create_custom_event(event_id, _generic_custom_event_action, debug_to_ui)
        _custom_event_queues[event_id] = Queue()

    _custom_event_queues[event_id].put(to_execute)
    adsk.core.Application.get().fireCustomEvent(event_id)


def execute_as_event_deco(event_id: str = None, debug_to_ui: bool = False):
    """Utility decorator which allows you to execute the passed Callable from witihn a
    custom event. This is needed when you want to trigger some Fusion related actions
    from a thread or other external non Fusion stimuli. You can also decorate functions
    which receive arguments (in contrast to the execute_as_event utility function).

    Args:
        debug_to_ui (bool, optional): Whether any errors appearing during execution
    """

    def decorator(to_decorate: Callable):
        @wraps(to_decorate)
        def decorated(*args, **kwargs):
            execute_as_event(
                lambda: to_decorate(*args, **kwargs),
                event_id=event_id,
                debug_to_ui=debug_to_ui,
            )

        return decorated

    return decorator


# def execute_from_command_execute_handler(to_execute: Callable):
#     if (handlers.last_activated_command.parentCommandDefinition.id
#         != adsk.core.Application.get().userInterface.activeCommand
#     ):
#         # handlers.last_activated_command = None
#         raise RuntimeError(msgs.)

#     handlers.last_activated_command_queue[1].put(to_execute)
#     handlers.last_activated_command.doExecute(False)


# endregion
