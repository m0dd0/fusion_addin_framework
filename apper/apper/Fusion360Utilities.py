"""[summary]
"""

from typing import Optional

import adsk.core
import adsk.fusion
import adsk.cam


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

    # @property
    # def time_line(self) -> Optional[adsk.fusion.Timeline]:
    #     """adsk.fusion.Timeline from the active adsk.fusion.Design

    #     Returns: adsk.fusion.Timeline from the active adsk.fusion.Design

    #     """
    #     time_line_ = None
    #     if self.product is not None:
    #         if self.product.productType == 'DesignProductType':
    #             if self._design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
    #                 time_line_ = self.product.timeline

    #     if time_line_ is not None:
    #         return time_line_
    #     else:
    #         return None

    # @property
    # def units_manager(self) -> Optional[adsk.core.UnitsManager]:
    #     """adsk.core.UnitsManager from the active document

    #     If not in an active document with design workspace active, will return
    #  adsk.core.UnitsManager if possible

    #     Returns: adsk.fusion.FusionUnitsManager or adsk.core.UnitsManager if
    # in a different workspace than design.
    #     """
    #     units_manager_ = None
    #     if self.product is not None:
    #         if self.product.productType == 'DesignProductType':
    #             units_manager_ = self._design.fusionUnitsManager
    #         else:
    #             try:
    #                 units_manager_ = self.product.unitsManager
    #             except:
    #                 pass
    #     if units_manager_ is not None:
    #         return units_manager_
    #     else:
    #         return None

    # @property
    # def f_units_manager(self) -> Optional[adsk.fusion.FusionUnitsManager]:
    #     """adsk.fusion.FusionUnitsManager from the active document.

    #     Only work in design environment.

    #     Returns: adsk.fusion.FusionUnitsManager or None if in a different workspace than design.
    #     """
    #     units_manager = None
    #     if self.product is not None:
    #         if self.product.productType == 'DesignProductType':
    #             units_manager = self._design.fusionUnitsManager
    #         else:
    #             units_manager = None

    #     if units_manager is not None:
    #         return units_manager
    #     else:
    #         return None

    # @property
    # def export_manager(self) -> Optional[adsk.fusion.ExportManager]:
    #     """adsk.fusion.ExportManager from the active document

    #     Returns: adsk.fusion.ExportManager from the active document

    #     """
    #     if self._design is not None:
    #         export_manager_ = self._design.exportManager
    #         return export_manager_
    #     else:
    #         return None


def apply_appearance(obj,
                     r: int,
                     g: int,
                     b: int,
                     o=255,
                     appearance_name='ABS (White)'):
    """[summary]

    Args:
        obj ([type]): [description]
        r (int): [description]
        g (int): [description]
        b (int): [description]
        o (int, optional): [description]. Defaults to 255.
        appearance_name (str, optional): [description]. Defaults to 'ABS (White)'.

    Raises:
        ValueError: [description]
        ValueError: [description]
    """
    # https://ekinssolutions.com/setting-colors-in-fusion-360/
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)

    custom_appearance_base = app.materialLibraries.itemByName(
        'Fusion 360 Appearance Library').appearances.itemByName(
            appearance_name)

    if custom_appearance_base is None:
        raise ValueError(
            '{0} is not contained in the Fusion 360 Appearance Library'.format(
                appearance_name))
    if custom_appearance_base.appearanceProperties.itemByName('Color') is None:
        raise ValueError(
            '{0} has no Color Property'.format(custom_appearance_base))

    new_appearance_name = 'CustomAppearanceByApper_{0}_{1}_{2}_{3}_modified_{4}'.format(
        r, g, b, o, custom_appearance_base.name)

    custom_appearance = design.appearances.itemByName(new_appearance_name)
    if custom_appearance is None:
        custom_appearance = design.appearances.addByCopy(
            custom_appearance_base, new_appearance_name)
        custom_appearance.appearanceProperties.itemByName(
            'Color').value = adsk.core.Color.create(r, g, b, o)

    obj.appearance = custom_appearance


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
    # min_arr = np.array(bounding_box.minPoint.asArray())
    # max_arr = np.array(bounding_box.maxPoint.asArray())
    # diagonal = max_arr - min_arr
    # center = min_arr + diagonal/2
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
