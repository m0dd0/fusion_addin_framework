import logging
from pathlib import Path
from abc import ABC
from typing import Union, Callable

import adsk.core
import adsk.fusion

from . import defaults as dflts
from . import messages as msgs
from . import handlers

# TODO manage multiple parent
# TODO default parents
# TODO manage childre, seperation between fusion children and framework children
# TODO create empty panels, tabs, workspaces


class FusionApp:

    _ui_level = 0

    def __init__(self):
        # TODO more feaures (see old)
        self._created_elements = {}

    def stop(self):
        for level in reversed(sorted(list(self._created_elements.keys()))):
            elems = self._created_elements.pop(level)
            for elem in elems:
                elem.in_fusion.deleteMe()

    def register_element(self, elem, level=0):
        self._created_elements[level].append(elem)

    @property
    def ui_level(self):
        return self._ui_level


class _FusionWrapper(ABC):
    _parent = None
    _ident = None
    _in_fusion = None

    def __init__(self, parent):
        self._parent = parent
        self._ui_level = self.parent.ui_level + 1

    def _already_existing(self, not_setable):
        if not_setable:
            if self._in_fusion.isNative:
                logging.warning(
                    msgs.setting_on_native(self._ident, self.id, not_setable)
                )
            else:
                logging.warning(
                    msgs.already_existing(self._ident, self.id, not_setable)
                )
                # TODO option to overwrite with warning
        logging.info(msgs.using_exisitng(self._ident, self.id))

    def _created_new(self):
        self.get_app().register_element(self, self.ui_level)
        logging.info(msgs.created_new(self._ident, self.id))

    def get_app(self):
        return self.parent.get_app()

    @property
    def id(self):
        return self._in_fusion.id

    @property
    def in_fusion(self):
        return self._in_fusion

    @property
    def parent(self):
        return self._parent

    @property
    def ui_level(self):
        return self._ui_level


class Workspace(_FusionWrapper):

    _ident = "workspace"

    def __init__(
        self,
        parent: FusionApp,
        name: str = None,
        id: str = None,  # pylint:disable=redefined-builtin
        product_type: str = None,
        image: Union[str, Path] = None,
        tooltip_image: Union[str, Path] = None,
        tooltip_head: str = None,
        tooltip_text: str = None,
    ):
        super().__init__(parent)

        # get the names of all attributes that were passen to the init
        given_args = {k for k, v in locals().items() if v is not None and k != "self"}

        # this could be done in only two lines with a loop
        # but its more clear if all defaults are set explicitly
        id = dflts.evaluate(id, self._ident, "id")
        name = dflts.evaluate(name, self._ident, "name")
        product_type = dflts.evaluate(product_type, self._ident, "product_type")
        image = dflts.evaluate(image, self._ident, "image")
        tooltip_image = dflts.evaluate(tooltip_image, self._ident, "tooltip_image")
        tooltip_head = dflts.evaluate(tooltip_head, self._ident, "tooltip_head")
        tooltip_text = dflts.evaluate(tooltip_text, self._ident, "tooltip_text")

        # try to get an existing instance
        self._in_fusion = adsk.core.Application.get().userInterface.workspaces.itemById(
            id
        )

        # if there is an instance, modify it if its not natice, else warning message
        if self._in_fusion is not None:
            not_setable = given_args - {"id"}
            self._already_existing(not_setable)

        # create new workspace if there is no
        else:
            self._in_fusion = adsk.core.Application.get().userInterface.workspaces.add(
                product_type, id, name, image
            )
            self._in_fusion.toolClipFilename = tooltip_image
            self._in_fusion.tooltip = tooltip_head
            self._in_fusion.tooltipDescription = tooltip_head

            self._created_new()

    @property
    def is_active(self):
        return self._in_fusion.isActive

    @property
    def is_native(self):
        return self._in_fusion.isNative

    @property
    def is_valid(self):
        return self._in_fusion.isValid

    @property
    def name(self):
        return self._in_fusion.name

    @property
    def product_type(self):
        return self._in_fusion.productType

    @property
    def image(self):
        return self._in_fusion.resourceFolder

    @image.setter
    def image(self, new_image):
        if self.is_native:
            logging.warning(msgs.setting_on_native("workspace", new_image, "image"))
        else:
            new_image = dflts.evaluate(new_image, "workspace", "image")
            self._in_fusion.resourceFolder = new_image

    @property
    def children(self):
        return self._in_fusion.toolbarTabs

    @property
    def tooltip_image(self):
        return self._in_fusion.toolClipFilename

    @tooltip_image.setter
    def tooltip_image(self, new_tooltip_image):
        if self.is_native:
            logging.warning(
                msgs.setting_on_native("workspace", new_tooltip_image, "tooltip_image")
            )
        else:
            dflts.evaluate(new_tooltip_image, "workspace", "tooltip_image")

    @property
    def tooltip_head(self):
        return self._in_fusion.tooltip

    @tooltip_head.setter
    def tooltip_head(self, new_tooltip_head):
        if self.is_native:
            logging.warning(
                msgs.setting_on_native("workspace", new_tooltip_head, "tooltip_head")
            )
        else:
            dflts.evaluate(new_tooltip_head, "workspace", "tooltip_head")

    @property
    def tooltip_text(self):
        return self._in_fusion.tooltip_description

    @tooltip_text.setter
    def tooltip_text(self, new_tooltip_text):
        if self.is_native:
            logging.warning(
                msgs.setting_on_native("workspace", new_tooltip_text, "tooltip_text")
            )
        else:
            dflts.evaluate(new_tooltip_text, "workspace", "tooltip_text")

        return self._in_fusion.tooltipDescription

    def tab(self, name: str = None, id: str = None):  # pylint:disable=redefined-builtin
        return Tab(self, name, id)


class Tab(_FusionWrapper):

    _ident = "tab"

    def __init__(
        self,
        parent: Workspace,
        name: str = None,
        id: str = None,  # pylint:disable=redefined-builtin
    ):
        super().__init__(parent)
        given_args = {k for k, v in locals().items() if v is not None and k != "self"}

        name = dflts.evaluate(name, self._ident, "name")
        id = dflts.evaluate(id, self._ident, "id")

        self._in_fusion = self.parent.children.itemById(id)

        if self.in_fusion:
            not_setable = given_args - {"id"}
            self._already_existing(not_setable)

        else:
            self._in_fusion = self.parent.in_fusion.toolbarTabs.add(id, name)
            # nothing else is setable

            self._created_new()

    @property
    def position(self):
        return self._in_fusion.index

    @property
    def is_active(self):
        return self._in_fusion.isActive

    @property
    def is_native(self):
        return self._in_fusion.isNative

    @property
    def is_visible(self):
        return self._in_fusion.isVisible

    @property
    def is_valid(self):
        return self._in_fusion.isValid

    @property
    def name(self):
        return self._in_fusion.name

    @property
    def children(self):
        return self._in_fusion.toolbarPanels

    def panel(
        self,
        name: str = None,
        id: str = None,  # pylint:disable=redefined-builtin
        position: int = None,
    ):
        return Panel(self, name, id, position)


class Panel(_FusionWrapper):

    _ident = "panel"

    def __init__(
        self,
        parent: Tab,
        name: str = None,
        id: str = None,  # pylint:disable=redefined-builtin
        position: int = None,
    ):
        super().__init__(parent)
        given_args = {k for k, v in locals().items() if v is not None and k != "self"}

        name = dflts.evaluate(name, self._ident, "name")
        id = dflts.evaluate(id, self._ident, "id")
        position = dflts.evaluate(position, self._ident, "position")

        self._in_fusion = self.parent.children.itemById(id)

        if self._in_fusion:
            not_setable = given_args - {"id"}
            self._already_existing(not_setable)

        else:
            # TODO position
            # panel_order = {p.indexWithinTab(): p.id for p in self.parent.children}
            # for i in sorted(list(panel_order.keys())):  # + [math.inf]:
            #     if i > position:
            #         comes_before_id = panel_order[i]
            #         break
            self._in_fusion = self.parent.in_fusion.children.add(
                id, name  # , comes_before_id, True
            )
            # nothing else to set
            # TODO related workspaces

            self._created_new()

    @property
    def position(self):
        return self._in_fusion.indexWithinTab()

    @property
    def children(self):
        return self._in_fusion.controls

    @property
    def index(self):
        return self._in_fusion.index

    @property
    def is_valid(self):
        return self._in_fusion.isValid

    @property
    def is_visible(self):
        return self._in_fusion.isVisible

    @property
    def name(self):
        return self._in_fusion.name

    @property
    def promoted_controls(self):
        return self._in_fusion.promotedControls


class ButtonCommand(_FusionWrapper):

    _ident = "button"

    def __init__(
        self,
        parent: Panel,
        id: str = None,  # cmd_def #pylint:disable=redefined-builtin
        name: str = None,  # cmd_Def
        tooltip: str = None,  # cmd_def
        image_tooltip: Union[str, Path] = None,  # cmd_Def
        image: Union[str, Path] = None,  # cmd_def
        position: int = None,  # cmd_ctrl
        is_visible: bool = None,  # cmd_ctrl, ctrl_def
        is_enabled: bool = None,  # ctrl_def
        is_promoted: bool = True,  # cmd_ctrl
        is_promoted_by_default: bool = True,  # cmd_ctrl
        on_created: Callable = None,  # cmd_def
        on_input_changed: Callable = None,  # cmd_def
        on_preview: Callable = None,  # cmd_def
        on_execute: Callable = None,  # cmd_def
        on_destroy: Callable = None,  # cmd_def
    ):
        super().__init__(parent)
        given_args = {k for k, v in locals().items() if v is not None and k != "self"}

        id = dflts.evaluate(id, self._ident, "id")
        name = dflts.evaluate(name, self._ident, "name")
        tooltip = dflts.evaluate(tooltip, self._ident, "tooltip")
        image_tooltip = dflts.evaluate(image_tooltip, self._ident, "image_tooltip")
        image = dflts.evaluate(image, self._ident, "image")
        position = dflts.evaluate(position, self._ident, "position")
        is_visible = dflts.evaluate(is_visible, self._ident, "is_visible")
        is_enabled = dflts.evaluate(is_enabled, self._ident, "is_enabled")
        is_promoted = dflts.evaluate(is_promoted, self._ident, "is_promoted")
        is_promoted_by_default = dflts.evaluate(
            is_promoted_by_default, self._ident, "is_promoted_by_defualt"
        )
        on_created = dflts.evaluate(on_created, self._ident, "on_created")
        on_input_changed = dflts.evaluate(
            on_input_changed, self._ident, "on_input_changed"
        )
        on_preview = dflts.evaluate(on_preview, self._ident, "on_preview")
        on_execute = dflts.evaluate(on_execute, self._ident, "on_execute")
        on_destroy = dflts.evaluate(on_destroy, self._ident, "on_destroy")

        cmd_ctrl = self.parent.children.itemById(id)
        cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.itemById(
            id
        )

        if cmd_ctrl or cmd_def:
            # TODO implement handling
            raise ValueError()

        else:
            cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
                id, name, tooltip, image
            )
            cmd_def.toolClipFilename = image_tooltip
            cmd_def.controlDefinition.isVisible = is_visible
            cmd_def.controlDefinition.isEnabled = is_enabled
            cmd_def.controlDefinition.name = name

            # TODO all handlers
            cmd_def.commandCreated.add(
                handlers.create(on_created, on_execute, on_preview, on_input_changed)
            )

            # TODO parse position
            cmd_ctrl = self.parent.children.addCommand(cmd_def)  # , position, True)
            cmd_ctrl.isPromoted = is_promoted
            cmd_ctrl.isPromotedByDefault = is_promoted_by_default
            cmd_ctrl.isVisible = is_visible

            self._in_fusion = cmd_ctrl

            self._created_new()

        # TODO properties


# class Button(_FusionWrapper):
#     def __init__(self, parent: Panel, position):
#         pass


# class Command(_FusionWrapper):
#     def __init__(self):
#         pass