"""[summary]
"""

from typing import Iterable
from functools import wraps
import json
import math

import adsk.core
import adsk.fusion
import adsk.cam

from .PythonUtils import trim_from_substring

custom_appearance_substring = '_custom_colored_r'


def apply_color(obj, r, g, b, o=255):
    # https://ekinssolutions.com/setting-colors-in-fusion-360/
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)

    base_appearance_name = trim_from_substring(obj.appearance.name,
                                               custom_appearance_substring)

    colored_appearance_base = app.materialLibraries.itemByName(
        'Fusion 360 Appearance Library').appearances.itemByName(
            base_appearance_name)

    colored_appearance_name = '{4}{5}{0}g{1}b{2}o{3}'.format(
        r, g, b, o, colored_appearance_base.name, custom_appearance_substring)

    colored_appearance = design.appearances.itemByName(colored_appearance_name)
    if colored_appearance is None:
        colored_appearance = design.appearances.addByCopy(
            colored_appearance_base, colored_appearance_name)
        colored_appearance.appearanceProperties.itemByName(
            'Color').value = adsk.core.Color.create(r, g, b, o)

    obj.appearance = colored_appearance
    return colored_appearance


def remove_custom_appearances():
    for appearance in adsk.fusion.Design.cast(
            adsk.core.Application.get().activeProduct).appearances:
        if appearance.name.find(custom_appearance_substring) != -1:
            try:
                appearance.deleteMe()
            except:
                pass


def change_material(obj, material_name):
    material = adsk.core.Application.get().materialLibraries.itemByName(
        'Fusion 360 Appearance Library').appearances.itemByName(material_name)
    obj.appearance = material
    return material


def clear_collection(collection):
    """[summary]

    Args:
        collection ([type]): [description]
    """
    while collection.count > 0:
        collection.item(0).deleteMe()


def orient_bounding_box(bounding_box):
    """[summary]

    Args:
        bounding_box ([type]): [description]

    Returns:
        [type]: [description]
    """
    # do not use numpy to have no third party dependencies on apper
    diagonal = [
        max_coord - min_coord for max_coord, min_coord in zip(
            bounding_box.minPoint.asArray(), bounding_box.maxPoint.asArray())
    ]
    center = [
        min_coord + dia_coord / 2 for min_coord, dia_coord in zip(
            bounding_box.minPoint.asArray(), diagonal)
    ]
    oriented_box = adsk.core.OrientedBoundingBox3D.create(
        adsk.core.Point3D.create(*center), adsk.core.Vector3D.create(1, 0, 0),
        adsk.core.Vector3D.create(0, 1, 0), abs(diagonal[0]), abs(diagonal[1]),
        abs(diagonal[2]))
    return oriented_box


def delete_all_graphics():
    """[summary]
    """
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    for comp in des.allComponents:
        clear_collection(comp.customGraphicsGroup)
    adsk.core.Application.get().activeViewport.refresh()


def with_direct_design(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        design = adsk.fusion.Design.cast(
            adsk.core.Application.get().activeProduct)
        old_design_type = design.designType
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        return_val = func(*args, **kwargs)
        design.designType = old_design_type
        return return_val

    return wrapped


def create_cube(center, side_length):
    return adsk.fusion.TemporaryBRepManager.get().createBox(
        adsk.core.OrientedBoundingBox3D.create(
            adsk.core.Point3D.create(*center),
            adsk.core.Vector3D.create(1, 0, 0),
            adsk.core.Vector3D.create(0, 1, 0), side_length, side_length,
            side_length))


def new_comp(name=None, parent=None):
    if parent is None:
        parent = adsk.fusion.Design.cast(
            adsk.core.Application.get().activeProduct).rootComponent
    comp = parent.occurrences.addNewComponent(
        adsk.core.Matrix3D.create()).component
    if name:
        comp.name = name
    return comp


def delete_comp(comp):
    for occ in adsk.fusion.Design.cast(adsk.core.Application.get(
    ).activeProduct).rootComponent.allOccurrencesByComponent(comp):
        occ.deleteMe()


def get_json_attr(obj, group_name, attr_name):
    attr_value = obj.attributes.itemByName(group_name, attr_name).value
    try:
        attr_value = json.loads(attr_value)
    except:
        print('couldnt load attribute as json object')
    return attr_value


def select_items_by_name(list_items: adsk.core.ListItems,
                         names: Iterable[str]):
    for item in list_items:
        if item.name in names:
            item.isSelected = True
        else:
            item.isSelected = False


def item_by_name(coll, name):
    for i in coll:
        if i.name == name:
            return i
    return None


def view_extents_by_measure(measure: float,
                            is_horizontal_measure: bool = True):
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
    return max(view_extents_by_measure(horizontal, True),
               view_extents_by_measure(vertical, False))


def make_comp_invisible(comp: adsk.fusion.Component):
    libghtbulbs = [
        'isBodiesFolderLightBulbOn', 'isConstructionFolderLightBulbOn',
        'isJointsFolderLightBulbOn', 'isOriginFolderLightBulbOn',
        'isSketchFolderLightBulbOn'
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
