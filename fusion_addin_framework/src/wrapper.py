import logging
from pathlib import Path
from abc import ABC
from typing import Union

import adsk.core
import adsk.fusion

from . import defaults as dflts
from . import msgs
from .util.py_utils import comes_after


class FusionApp:
    def __init__(self):
        # TODO more feaures (see old)
        self._created_elements = {}

    def stop(self):
        def delete_elem(elem):
            for child in elem.children:
                delete_elem(child)
            if not elem.is_native:
                elem.in_fusion.deleteMe()

        for level in reversed(sorted(list(self._created_elements.keys()))):
            elems = self._created_elements.pop(level)
            for elem in elems:
                elem.in_fusion.deleteMe()

    def register_child(self, elem, level=0):
        self._created_elements[level].append(elem)


class _FusionWrapper(ABC):
    parent = None
    _in_fusion = None

    def __init__(self):
        pass

    def _already_existing(self, not_setable, type: str, id: str):
        if not_setable:
            if self._in_fusion.isNative:
                logging.warning(msgs.setting_on_native(type, id, not_setable))
            else:
                logging.warning(msgs.already_existing("workspace", id, not_setable))
                # TODO option to overwrite with warning

    def _register_child(self, child, level=0):
        self.parent.register_child(child, level + 1)

    @property
    def id(self):
        return self._in_fusion.id

    @property
    def in_fusion(self):
        return self._in_fusion


class Workspace(_FusionWrapper):
    def __init__(
        self,
        parent: FusionApp,
        name: str = None,
        id: str = None,
        product_type: str = None,
        image: Union[str, Path] = None,
        tooltip_image: Union[str, Path] = None,
        tooltip_head: str = None,
        tooltip_text: str = None,
    ):
        super().__init__()

        # get the names of all attributes that were passen to the init
        given_args = [k for k, v in locals().items() if v is not None and k != "self"]

        # this could be done in only two lines with a loop
        # but its more clear if all defaults are set explicitly
        id = dflts.evaluate(id, "workspace", "id")
        name = dflts.evaluate(name, "workspace", "name")
        product_type = dflts.evaluate(product_type, "workspace", "product_type")
        image = dflts.evaluate(image, "workspace", "image")
        tooltip_image = dflts.evaluate(tooltip_image, "workspace", "tooltip_image")
        tooltip_head = dflts.evaluate(tooltip_head, "workspace", "tooltip_head")
        tooltip_text = dflts.evaluate(tooltip_text, "workspace", "tooltip_text")

        # parent is needed to be saved to register children
        self.parent = parent

        # try to get an existing instance
        self._in_fusion = adsk.core.Application.get().userInterface.workspaces.itemById(
            id
        )

        # if there is an instance, modify it if its not natice, else warning message
        if self._in_fusion is not None:
            not_setable = set(given_args) - {"id"}
            self._already_existing(not_setable, "workspace", id)

        # create new workspace if there is no
        else:
            self._in_fusion = adsk.core.Application.get().userInterface.workspaces.add(
                product_type, id, name, image
            )
            self._in_fusion.toolClipFilename = tooltip_image
            self._in_fusion.tooltip = tooltip_head
            self._in_fusion.tooltipDescription = tooltip_head

            self.parent._register_child(self)

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

    def tab(self, name: str = None, id: str = None, position_index: int = None):
        return Tab(self, name, id, position_index)


class Tab(_FusionWrapper):
    def __init__(
        self,
        parent: Workspace,
        name: str = None,  # add
        id: str = None,  # add
    ):
        super().__init__()

        given_args = [k for k, v in locals().items() if v is not None and k != "self"]

        name = dflts.evaluate(name, "tab", "name")
        id = dflts.evaluate(id, "tab", "id")

        self.parent = parent

        self._in_fusion = parent.children.itemById(self.id)

        if self.in_fusion:
            not_setable = set(given_args.keys()) - {"id"}
            self._already_existing(not_setable, "tab", id)

        else:
            self._in_fusion = parent.in_fusion.toolbarTabs.add(id, name)
            # nothing else is setable

        @property
        def position_index(self):


class Panel:
    def __init__(
        self,
        parent_tab: Tab,
        name: str = None,
        id: str = None,
        position_index: int = None,
        is_visible: bool = None,
    ):
        given_args = {k: v for k, v in locals().items() if v is not None}
        dflts.fill
        self.parent_tab = parent_tab
        self.name = dflts.name(name, "panel", "random")
        self.id = dflts.id(id, "random")
        self.position_index = dflts.no_parse(position_index, -1)
        self.is_visible = dflts.no_parse(is_visible, True)

        self.in_fusion = parent_tab._in_fusion.toolbarPanels.itemById(self.id)

        if self.in_fusion:
            if self.in_fusion.isNative:
                not_setable = set(given_args.keys()) - {"id"}
                if not_setable:
                    logging.warning(
                        msgs.setting_on_native("panel", self.id, not_setable)
                    )
            else:
                # TODO implement if app managemnt is created
                pass
        # create new tab
        else:
            panel_order = {
                p.indexWithinTab(): p.id
                for p in self.parent_tab._in_fusion.toolbarPanels
            }
            before_id = panel_order[
                comes_after(list(panel_order.keys()), self.position_index)
            ]
            self.in_fusion = parent_tab._in_fusion.toolbarPanels.add(
                self.id, self.name, before_id, True
            )
            self.in_fusion.isVisible = is_visible


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
