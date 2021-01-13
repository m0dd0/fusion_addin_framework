import logging
from pathlib import Path
from abc import ABC
from typing import Union

import adsk.core
import adsk.fusion

from . import defaults as dflts
from . import messages as msgs

# TODO manage multiple parent
# TODO default parents
# TODO manage childre, seperation between fusion children and framework children


class FusionApp:
    def __init__(self):
        # TODO more feaures (see old)
        self._created_elements = {}

    def stop(self):
        for level in reversed(sorted(list(self._created_elements.keys()))):
            elems = self._created_elements.pop(level)
            for elem in elems:
                elem.in_fusion.deleteMe()

    def register_child(self, elem, level=0):
        self._created_elements[level].append(elem)


class _FusionWrapper(ABC):
    _parent = None
    _ident = None
    _in_fusion = None

    def __init__(self, parent):
        self._parent = parent

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

    def _register_child(self, child, level=0):
        self.parent._register_child(child, level + 1)  # pylint:disable=protected-access

    def _created_new(self):
        self.parent._register_child(self, 0)  # pylint:disable=protected-access
        logging.info(msgs.created_new(self._ident, self.id))

    @property
    def id(self):
        return self._in_fusion.id

    @property
    def in_fusion(self):
        return self._in_fusion

    @property
    def parent(self):
        return self._parent


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
        given_args = [k for k, v in locals().items() if v is not None and k != "self"]

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
            not_setable = set(given_args) - {"id"}
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
        given_args = [k for k, v in locals().items() if v is not None and k != "self"]

        name = dflts.evaluate(name, self._ident, "name")
        id = dflts.evaluate(id, self._ident, "id")

        self._in_fusion = self.parent.children.itemById(id)

        if self.in_fusion:
            not_setable = set(given_args.keys()) - {"id"}
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
        given_args = [k for k, v in locals().items() if v is not None and k != "self"]

        name = dflts.evaluate(name, self._ident, "name")
        id = dflts.evaluate(id, self._ident, "id")
        position = dflts.evaluate(position, self._ident, "position")

        self._in_fusion = self.parent.children.itemById(id)

        if self._in_fusion:
            not_setable = set(given_args.keys()) - {"id"}
            self._already_existing(not_setable)

        else:
            panel_order = {p.indexWithinTab(): p.id for p in self.parent.children}
            for i in sorted(list(panel_order.keys())):  # + [math.inf]:
                if i > position:
                    comes_before_id = panel_order[i]
                    break
            self._in_fusion = self.parent.in_fusion.toolbarPanels.add(
                id, name, comes_before_id, True
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
