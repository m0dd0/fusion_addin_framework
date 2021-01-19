import logging
from pathlib import Path
from abc import ABC
from typing import Union, Callable
import traceback
from collections import defaultdict
from uuid import uuid4

import adsk.core
import adsk.fusion

from . import defaults as dflts
from . import messages as msgs
from . import handlers

from .util.py_utils import create_default_logger
from .util import appdirs

# TODO manage multiple parent
# TODO default parents
# TODO manage childre, seperation between fusion children and framework children
# TODO create empty panels, tabs, workspaces


class FusionApp:

    _ui_level = 0
    _ident = "app"

    def __init__(self, logger=None, name=None, author=None, debug_to_ui=None):
        # no need ot use properties since its ok to set them
        self.name = self.eval_arg(name, self._ident, "name")
        self.author = self.eval_arg(author, self._ident, "author")
        self.debug_to_ui = self.eval_arg(debug_to_ui, self._ident, "debug_to_ui")

        self.user_state_dir = appdirs.user_state_dir(self.name, self.author)
        self.user_cache_dir = appdirs.user_cache_dir(self.name, self.author)
        self.user_config_dir = appdirs.user_config_dir(self.name, self.author)
        self.user_data_dir = appdirs.user_data_dir(self.name, self.author)
        self.user_log_dir = appdirs.user_log_dir(self.name, self.author)

        if logger is None:
            logger = create_default_logger(
                name="faf_logger",
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler(self.user_log_dir),
                ],
                message_format="{asctime} {levelname} {module}/{funcName}: {message}",
            )
        self.logger = logger

        self._created_elements = defaultdict(list)

        self._effective_defaults = dflts.get_effective_defaults(self.logger)
        self._default_parsers = dflts.get_default_parsers(self.logger)

    def eval_arg(self, value, *keys):
        key = tuple(keys)
        if value is None:
            value = self._effective_defaults[key]
        return self._default_parsers[key](value)

    def stop(self):
        for level in reversed(sorted(list(self._created_elements.keys()))):
            elems = self._created_elements.pop(level)
            for elem in elems:
                try:
                    elem.deleteMe()
                except:
                    # element is probably already deleted
                    # TODO catch only this error
                    pass

    def register_element(self, elem, level=0):
        if isinstance(elem, _FusionWrapper):
            elem = elem.in_fusion
        self._created_elements[level].append(elem)

    def workspace(
        self,
        id: str = None,  # pylint:disable=redefined-builtin
        name: str = None,
        product_type: str = None,
        image: Union[str, Path] = None,
        tooltip_image: Union[str, Path] = None,
        tooltip_head: str = None,
        tooltip_text: str = None,
    ):
        return Workspace(
            self,
            id,
            name,
            product_type,
            image,
            tooltip_image,
            tooltip_head,
            tooltip_text,
        )

    @property
    def ui_level(self):
        return self._ui_level


class _FusionWrapper(ABC):
    _parent = None
    _in_fusion = None

    def __init__(self, parent):
        self._parent = parent
        self._app = self.parent.app
        self._ui_level = self.parent.ui_level + 1

    def _given_args(self, locals):  # pylint:disable=redefined-builtin
        return {
            k: v
            for k, v in locals.items()
            if v is not None and k not in ["self", "__class__"]
        }

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

    @property
    def app(self):
        return self._app


class Workspace(_FusionWrapper):

    _ident = "workspace"

    def __init__(
        self,
        parent: FusionApp,
        id: str = None,  # pylint:disable=redefined-builtin
        name: str = None,
        product_type: str = None,
        image: Union[str, Path] = None,
        tooltip_image: Union[str, Path] = None,
        tooltip_head: str = None,
        tooltip_text: str = None,
    ):
        super().__init__(parent)
        self.app = parent  # override

        # get the names of all attributes that were passen to the init
        given_args = self._given_args(locals())

        # this could be done in only two lines with a loop
        # but its more clear if all defaults are set explicitly
        id = self.app.eval_arg(id, self._ident, "id")
        name = self.app.eval_arg(name, self._ident, "name")
        product_type = self.app.eval_arg(product_type, self._ident, "product_type")
        image = self.app.eval_arg(image, self._ident, "image")
        tooltip_image = self.app.eval_arg(tooltip_image, self._ident, "tooltip_image")
        tooltip_head = self.app.eval_arg(tooltip_head, self._ident, "tooltip_head")
        tooltip_text = self.app.eval_arg(tooltip_text, self._ident, "tooltip_text")

        # try to get an existing instance
        self._in_fusion = adsk.core.Application.get().userInterface.workspaces.itemById(
            id
        )

        # if there is an instance, show warning message if there are more arguments
        # than necessary to get the workspace
        if self._in_fusion is not None:
            not_setable = given_args.keys() - {"id", "parent"}
            if not_setable:
                self.app.logger.warning(
                    msgs.already_existing(self._ident, id, not_setable)
                )
            self.app.logger.info(msgs.using_exisitng(self._ident, id))
            # print(msgs.using_exisitng(self._ident, id))

        # create new workspace if there is no
        else:
            self._in_fusion = adsk.core.Application.get().userInterface.workspaces.add(
                product_type, id, name, image
            )
            self._in_fusion.toolClipFilename = tooltip_image
            self._in_fusion.tooltip = tooltip_head
            self._in_fusion.tooltipDescription = tooltip_head

            self.app.register_element(self, self.ui_level)
            self.app.logger.info(msgs.created_new(self._ident, id))

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
            self.app.logger.warning(
                msgs.setting_on_native("workspace", new_image, "image")
            )
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
            self.app.logger.warning(
                msgs.setting_on_native("workspace", new_tooltip_image, "tooltip_image")
            )
        else:
            new_tooltip_image = dflts.evaluate(
                new_tooltip_image, "workspace", "tooltip_image"
            )
            self._in_fusion.toolClipFilename = new_tooltip_image

    @property
    def tooltip_head(self):
        return self._in_fusion.tooltip

    @tooltip_head.setter
    def tooltip_head(self, new_tooltip_head):
        if self.is_native:
            self.app.logger.warning(
                msgs.setting_on_native("workspace", new_tooltip_head, "tooltip_head")
            )
        else:
            new_tooltip_head = dflts.evaluate(
                new_tooltip_head, "workspace", "tooltip_head"
            )
            self._in_fusion.tooltip = new_tooltip_head

    @property
    def tooltip_text(self):
        return self._in_fusion.tooltip_description

    @tooltip_text.setter
    def tooltip_text(self, new_tooltip_text):
        if self.is_native:
            self.app.logger.warning(
                msgs.setting_on_native("workspace", new_tooltip_text, "tooltip_text")
            )
        else:
            new_tooltip_text = dflts.evaluate(
                new_tooltip_text, "workspace", "tooltip_text"
            )
            self._in_fusion.tooltipDescription = new_tooltip_text

    def tab(self, id: str = None, name: str = None):  # pylint:disable=redefined-builtin
        return Tab(self, id, name)


class Tab(_FusionWrapper):

    _ident = "tab"

    def __init__(
        self,
        parent: Workspace,
        id: str = None,  # pylint:disable=redefined-builtin
        name: str = None,
    ):
        super().__init__(parent)
        given_args = self._given_args(locals())

        name = self.app.eval_arg(name, self._ident, "name")
        id = self.app.eval_arg(id, self._ident, "id")

        self._in_fusion = self.parent.children.itemById(id)

        if self.in_fusion:
            not_setable = given_args.keys() - {"id", "parent"}
            if not_setable:
                self.app.logger.warning(
                    msgs.already_existing(self._ident, id, not_setable)
                )
            self.app.logger.info(msgs.using_exisitng(self._ident, id))
        else:
            self._in_fusion = self.parent.in_fusion.toolbarTabs.add(id, name)
            # nothing else is setable

            self.app.register_element(self, self.ui_level)
            self.app.logger.info(msgs.created_new(self._ident, id))

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
        id: str = None,  # pylint:disable=redefined-builtin
        name: str = None,
        position: int = None,
    ):
        return Panel(self, name, id, position)


class Panel(_FusionWrapper):

    _ident = "panel"

    def __init__(
        self,
        parent: Tab,
        id: str = None,  # pylint:disable=redefined-builtin
        name: str = None,
        position_index: int = None,
    ):
        super().__init__(parent)
        given_args = self._given_args(locals())

        name = self.app.eval_arg(name, self._ident, "name")
        id = self.app.eval_arg(id, self._ident, "id")
        position_index = self.app.eval_arg(
            position_index, self._ident, "position_index"
        )

        self._in_fusion = self.parent.children.itemById(id)

        if self._in_fusion:
            not_setable = given_args.keys() - {"id", "parent"}
            if not_setable:
                self.app.logger.warning(
                    msgs.already_existing(self._ident, id, not_setable)
                )
            self.app.logger.info(msgs.using_exisitng(self._ident, id))
        else:
            # TODO position
            # panel_order = {p.indexWithinTab(): p.id for p in self.parent.children}
            # for i in sorted(list(panel_order.keys())):  # + [math.inf]:
            #     if i > position:
            #         comes_before_id = panel_order[i]
            #         break
            self._in_fusion = self.parent.children.add(
                id, name  # , comes_before_id, True
            )
            # nothing else to set
            # TODO related workspaces

            self.app.register_element(self, self.ui_level)
            self.app.logger.info(msgs.created_new(self._ident, id))

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

    def button(
        self,
        parent: Panel,
        position_index: int = None,
        is_visible: bool = None,
        is_enabled: bool = None,
        is_promoted: bool = True,
        is_promoted_by_default: bool = True,
    ):
        return Button(
            self,
            position_index,
            is_visible,
            is_enabled,
            is_promoted,
            is_promoted_by_default,
        )


class Button(_FusionWrapper):

    _ident = "button"

    def __init__(
        self,
        parent: Panel,
        position_index: int = None,  # cmd_ctrl
        is_visible: bool = None,  # cmd_ctrl, ctrl_def
        is_enabled: bool = None,  # ctrl_def
        is_promoted: bool = True,  # cmd_ctrl
        is_promoted_by_default: bool = True,  # cmd_ctrl
    ):
        super().__init__(parent)
        given_args = self._given_args(locals())

        position_index = self.app.eval_arg(
            position_index, self._ident, "position_index"
        )
        is_visible = self.app.eval_arg(is_visible, self._ident, "is_visible")
        is_enabled = self.app.eval_arg(is_enabled, self._ident, "is_enabled")
        is_promoted = self.app.eval_arg(is_promoted, self._ident, "is_promoted")
        is_promoted_by_default = self.app.eval_arg(
            is_promoted_by_default, self._ident, "is_promoted_by_default"
        )

        # a button can always be created since it has no id

        dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
            str(uuid4()),
            "<no command connected>",
            "",
            dflts.image_parser("transparent"),
        )
        dummy_cmd_def.controlDefinition.isVisible = is_visible
        dummy_cmd_def.controlDefinition.isEnabled = is_enabled
        dummy_cmd_def.controlDefinition.name = "<no command connected>"
        # do not connect a handler since its a dummy cmd_def

        # TODO parse position
        cmd_ctrl = self.parent.children.addCommand(dummy_cmd_def)  # , position, True)
        cmd_ctrl.isPromoted = is_promoted
        cmd_ctrl.isPromotedByDefault = is_promoted_by_default
        cmd_ctrl.isVisible = is_visible

        self._in_fusion = cmd_ctrl

        self.app.register(dummy_cmd_def, self.ui_level)
        self.app.register_element(self, self.ui_level + 1)
        self.app.logger.info(msgs.created_new(self._ident, None))

        self._is_dummy = True  # TODO better solution

    @property
    def is_dummy(self):
        return self._is_dummy

    def command(
        self,
        parent: Button,
        id: str = None,  # pylint:disable=redefined-builtin
        name: str = None,
        image: Union[str, Path] = None,
        tooltip: str = None,
        tooltip_image: Union[str, Path] = None,
        on_created: Callable = None,
        on_input_changed: Callable = None,
        on_preview: Callable = None,
        on_execute: Callable = None,
        on_destroy: Callable = None,
        on_key_down: Callable = None,
    ):
        return Command(self, id, name, image, tooltip, tooltip_image)

    # TODO properties


class Command(_FusionWrapper):

    _ident = "command"

    def __init__(
        self,
        parent: Button,
        id: str = None,  # cmd_def #pylint:disable=redefined-builtin
        name: str = None,  # cmd_Def
        image: Union[str, Path] = None,  # cmd_def
        tooltip: str = None,  # cmd_def
        tooltip_image: Union[str, Path] = None,  # cmd_Def
        on_created: Callable = None,  # cmd_def
        on_input_changed: Callable = None,  # cmd_def
        on_preview: Callable = None,  # cmd_def
        on_execute: Callable = None,  # cmd_def
        on_destroy: Callable = None,  # cmd_def
        on_key_down: Callable = None,  # cmd_def
    ):
        super().__init__(parent)
        given_args = self._given_args(locals())

        id = self.app.eval_arg(id, self._ident, "id")
        name = self.app.eval_arg(name, self._ident, "name")
        tooltip = self.app.eval_arg(tooltip, self._ident, "tooltip")
        tooltip_image = self.app.eval_arg(tooltip_image, self._ident, "image_tooltip")
        image = self.app.eval_arg(image, self._ident, "image")
        on_created = self.app.eval_arg(on_created, self._ident, "on_created")
        on_input_changed = self.app.eval_arg(
            on_input_changed, self._ident, "on_input_changed"
        )
        on_preview = self.app.eval_arg(on_preview, self._ident, "on_preview")
        on_execute = self.app.eval_arg(on_execute, self._ident, "on_execute")
        on_destroy = self.app.eval_arg(on_destroy, self._ident, "on_destroy")

        cmd_ctrl = self.parent.children.itemById(id)
        cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.itemById(
            id
        )

        if not self.parent.is_dummy:
            raise ValueError(msgs.button_not_empty(self.parent.child.id))

        if cmd_ctrl:
            not_setable = given_args.keys() - {"id", "parent"}
            self.app.logger.warning(msgs.already_existing(self._ident, id, not_setable))
        elif cmd_def:
            # TODO parse position
            cmd_ctrl = self.parent.parent.children.addCommand(
                cmd_def
            )  # , position, True)
            cmd_ctrl.isPromoted = self.parent.is_promoted
            cmd_ctrl.isPromotedByDefault = self.parent.is_promoted_by_default
            cmd_ctrl.isVisible = self.parent.is_visible

        else:
            # create definition and recreate control
            cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
                id, name, tooltip, image
            )
            cmd_def.toolClipFilename = tooltip_image
            cmd_def.controlDefinition.isVisible = self.parent.is_visible
            cmd_def.controlDefinition.isEnabled = self.parent.is_enabled
            cmd_def.controlDefinition.name = name

            # TODO all handlers
            cmd_def.commandCreated.add(
                handlers.create(
                    self.app,
                    name,
                    on_created,
                    on_execute,
                    on_preview,
                    on_input_changed,
                    on_key_down,
                )
            )

            # TODO parse position
            cmd_ctrl = self.parent.parent.children.addCommand(
                cmd_def
            )  # , position, True)
            cmd_ctrl.isPromoted = self.parent.is_promoted
            cmd_ctrl.isPromotedByDefault = self.parent.is_promoted_by_default
            cmd_ctrl.isVisible = self.parent.is_visible

            # delete dummy if existing
            if self.parent.dummy is not None:
                self.parent.in_fusion.deleteMe()

            self._in_fusion = cmd_ctrl

            self.app
            self.app.register_element(self, self.ui_level)
            # self.app.register_element() # TODO dregister also cmd_def for deletion somehow
            self.app.logger.info(msgs.created_new(self._ident, id))

        # TODO properties
