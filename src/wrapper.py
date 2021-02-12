import logging
from pathlib import Path
from abc import ABC
from typing import Union, Callable, Any, List, Dict
from collections import defaultdict
from uuid import uuid4

import adsk.core
import adsk.fusion

from . import defaults as dflts
from . import messages as msgs
from . import handlers

from .util.py_utils import create_default_logger
from .util import appdirs


class _FusionWrapper(ABC):
    """Base class for all Fusion UI wrapper classes.

    Provides basic functionality used by the framework to handle the wrapper instances.
    Such as having a app attribute, which contains the controlling addin instance.
    Also sets the ui_level which is a atrtibute used by all wrapper classes.
    Defining class variables shared by all wrapper classes.
    """

    _parent = None
    _in_fusion = None

    def __init__(
        self, parent
    ):  # do NOT use for parent typehint --> docs generation will crash
        """
        Sets the attributes app attribute of the wrapped instance by getting its
        parents app attribute.
        Sets the ui_level attribute by incrementing the parents ui_level attribute.

        Args:
            parent (Union[_FusionWrapper, FusionApp]): the parent ui object instance
                e.g.: the parent of a panel is always a tab.
        """
        self._parent = parent
        self._app = self.parent.app
        self._ui_level = self.parent.ui_level + 1

    # def _given_args(self, locals: Dict):  # pylint:disable=redefined-builtin
    #     """Removes None and unwanted entries from the locals dict.

    #     To get a dictionairy containing only the values passed to a method, the
    #     dictionairy returned by locals() called in a method needs to be cleaned.
    #     When calling locals() inside a method, 'self' and '__class__' will always be
    #     included in the locals()-dict. They are dropped.
    #     Also all pairs having a None value are dropped.

    #     Args:
    #         locals (Dict): The dictionairy returned by a locals() call at the beginning
    #             of a method

    #     Returns:
    #         Dict: The cleaned dict, containing only the passed values.
    #     """
    #     return {
    #         k: v
    #         for k, v in locals.items()
    #         if v is not None and k not in ["self", "__class__"]
    #     }

    # simply override the properties to use individual docstrings

    @property
    def id(self):
        """Id of the wrapped instance."""
        return self._in_fusion.id

    @property
    def in_fusion(self):
        """The instance, this object is wrapped around."""
        return self._in_fusion

    @property
    def parent(self):
        """The wrapped parent instance of this object."""
        return self._parent

    @property
    def ui_level(self):
        """The level this instance is in the user interface hierachy.

        For Example: Workspace is always level 1, Tab always level 2
        """
        return self._ui_level

    @property
    def app(self):
        """The app instance which manages this instance."""
        return self._app


class FusionApp:
    """
    An App object is the entry point to create all your elements that will
    appear in the user interface. It handles their creation and deletes them
    if the addin is deactivated (by closing Fusion or stopping the Addin
    manually).
    """

    _ui_level = 0
    _ident = "app"

    def __init__(
        self,
        # logger: logging.Logger = None,
        name: str = None,
        author: str = None,
        debug_to_ui: bool = None,
    ):
        """
        Args:
            name (str, optional): The name of the addin. Used to create app
                directories with meaningful names. Defaults to None.
            author (str, optional): The name of the addins author. Used to create
                app directories with meaningful names. Defaults to None.
            debug_to_ui (bool, optional): Flag indicating if erorr messages caused
                by errrors in the callbacks are displayed in a `messageBox
                <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-1692a9a4-3be0-4474-9e15-02fac696b2b2>`_
                or not. If not they will get logged anyways. Defaults to True.
        """

        # no need ot use properties since its ok to set them
        self.name = self.eval_arg(name, [self._ident, "name"])
        self.author = self.eval_arg(author, [self._ident, "author"])
        self.debug_to_ui = self.eval_arg(debug_to_ui, [self._ident, "debug_to_ui"])

        self.user_state_dir = appdirs.user_state_dir(self.name, self.author)
        self.user_cache_dir = appdirs.user_cache_dir(self.name, self.author)
        self.user_config_dir = appdirs.user_config_dir(self.name, self.author)
        self.user_data_dir = appdirs.user_data_dir(self.name, self.author)
        self.user_log_dir = appdirs.user_log_dir(self.name, self.author)

        self._created_elements = defaultdict(list)

    def workspace(
        self,
        id: str = None,  # pylint:disable=redefined-builtin
        name: str = None,
        product_type: str = None,
        image: Union[str, Path] = None,  # pylint:disable=unsubscriptable-object
        tooltip_image: Union[str, Path] = None,  # pylint:disable=unsubscriptable-object
        tooltip_head: str = None,
        tooltip_text: str = None,
    ):
        """Creates a workspace as a child of this Adddin.

        Calling this method is the same as initialsing a :class:`.Workspace`
        with this addin instance as parent parameters. Therfore the same parameters
        are passed. See :class:`.Workspace` for details.

        Args:
            id (str, optional): The id of the :class:`.Workspace`. If 'random' is passed a
                random uuid will be used. If you provide an id of a native workspace
                the other arguments will be ignored. Defaults to 'FusionSolidEnvironment'.
                `unwrapped <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-33f9ed37-e5c7-4153-ba85-c3254a199dd1>`_
            name (str, optional): The name of the Workspace as seen in the user
                interface. If 'random' is passed a random name will be choosen.
                Defaults to 'random'.
                `unwrapped <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-144afd36-e125-4e28-8821-79a0134f207e>`_
            product_type (str, optional): The name of the product the workspace
                is associated with. Defaults to 'DesignProductType'.
                `unwrapped <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-974691b7-5ff6-4bec-8fbc-1683f7b33fe5>_`
            image (Union[str, Path], optional): Either the path to a directory
                containing images named 49X31.png and 98x62.png or one of the
                default picture names (currently only 'lightbulb'). Defaults to 'lightbulb.
                `unwrapped <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-19c3a0e8-7a55-4a03-8aa3-c8ca9b845e84>_`
            tooltip_image (Union[str, Path], optional): Either full filename of
                the image file (png) used for the tool clip or one of the
                default picture names (currently only 'lightbulb'). The tooltip image
                is the image shown when the user hovers the mouse over the workspace
                name in the workspace drop-down. If None no image will be set.
                `unwrapped <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-5C744005-AF96-4EEB-B060-FC246373B159>_`
            tooltip_head (str, optional):  The tooltip text displayed for the workspace.
                This is the first line of text shown when the user hovers over the
                workspace name in the Fusion 360 toolbar drop-down.
                Defaults to "" (empty string).
                `unwrapped <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-6AD46B6E-269C-4FC9-96BB-C6180BAA35ED>_`
            tooltip_text (str, optional): The tooltip description displayed for
                the workspace. The tooltip description is a longer description of
                the workspace and is only displayed when the user hovers over the
                workspace name in the Fusion 360 toolbar drop-down.
                Defaults to None. `unwrapped <>_`

        Returns:
            [type]: [description]
        """
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

    def stop(self):
        """Stops the addin and deletes all created ui elements.

        This methods needs to get called from the stop(context) function of the
        main file of your addin o ensure proper cleanup.
        If you dont call it, strange thigs can happen the next time you want to
        run the addin.
        """
        for level in reversed(sorted(list(self._created_elements.keys()))):
            elems = self._created_elements.pop(level)
            for elem in elems:
                try:
                    elem.deleteMe()
                except:
                    # element is probably already deleted
                    pass

    def eval_arg(self, value: Any, keys: List[str]):
        """Evaluates a given arguments with the parser at keys position.

        The value argument can be any argument that you can pass to one of the
        initalising methodes of any ui wrapper class.
        The method returns the result of the input validation of this value with
        the parser of the position defined by the keys.
        For example if you provide the value "lightbulb" and ["workspace", "image"]
        as key, the parser will return a string representing the full path of the
        source of the lighbulb image.
        This method is not needed in the regular use. However, you can use it with
        None as value to quickly check the defualt parameter for a class initialisation
        or for debugging purpose.

        Args:
            value (Any): The initialsation argument to evaluate
            keys (List[str]): The "position" of the parser which is used to evaluate
                the value

        Returns:
            Any: The reult of evaluating the given value
        """
        key = tuple(keys)
        if value is None:
            value = self._effective_defaults[key]
        return self._default_parsers[key](value)

    def register_element(self, elem: _FusionWrapper, level: int = 0):
        """Registers a instance of a ui wrapper object to the addin.

        All wrapper objects that are registered will get deleted if the addin stops.
        The order of the deletion is determind by the level. Instances with a
        higher level will get deleted first.
        All elements that are created will be registered by the framework internally,
        so there is no need to use this method in noraml use og the framework.

        Args:
            elem (_FusionWrapper): The wrapper instance to register.
            level (int, optional): The Ui level of the element. Defaults to 0.
        """
        if isinstance(elem, _FusionWrapper):
            elem = elem.in_fusion
        self._created_elements[level].append(elem)

    @property
    def ui_level(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._ui_level

    @property
    def app(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self


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
        """[summary]

        Args:
            parent (FusionApp): [description]
            id (str, optional): [description]. Defaults to None.
            product_type (str, optional): [description]. Defaults to None.
            image (Union[str, Path], optional): [description]. Defaults to None.
            tooltip_image (Union[str, Path], optional): [description]. Defaults to None.
            tooltip_head (str, optional): [description]. Defaults to None.
            tooltip_text (str, optional): [description]. Defaults to None.
        """
        super().__init__(parent)

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
    def id(self):
        """Id of the workspace."""
        return self._in_fusion.id

    @property
    def is_active(self):
        """ "Gets if the workspace is currently active - i.e. displayed"
        (Read only, `source <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-fed83f5e-f240-4fa6-9149-d4ffb25cdf41>`_)
        """
        return self._in_fusion.isActive

    @property
    def is_native(self):
        """ "Gets if this workspace is native to Fusion 360 or was created via the API."
        (Read only, `source <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-6463695c-156a-49dd-ae4e-7ba0bdc3a86e>`_)
        """
        return self._in_fusion.isNative

    @property
    def is_valid(self):
        """ "Indicates if this object is still valid, i.e. hasn't been deleted or some other action done to invalidate the reference."
        (Read only, `source <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-3bd18973-0b8a-40a3-9fc8-b40658b730a9>`_)
        """
        return self._in_fusion.isValid

    @property
    def name(self):
        """ "Gets the visible name of the workspace as seen in the user interface. This is the localized name."
        (Read only `source <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-144afd36-e125-4e28-8821-79a0134f207e>`_)
        """
        return self._in_fusion.name

    @property
    def product_type(self):
        """ "Returns the name of the product this workspace is associated with."
        (Read only, `source <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-974691b7-5ff6-4bec-8fbc-1683f7b33fe5>`_)
        """
        return self._in_fusion.productType

    @property
    def image(self):
        """The directory path with the images used by the workspace.
        (`source <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-19c3a0e8-7a55-4a03-8aa3-c8ca9b845e84>`_)
        Can be set with the same values you can pass to the construcor (image name or path)
        """
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
    def child_tabs(self):
        """ "Gets the collection containing the tabs associated with this workspace."
        (Read only, `source <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-99D28385-358B-4A86-9E25-24454EEF5671>`_)
        """
        return self._in_fusion.toolbarTabs

    @property
    def tooltip_image(self):
        """ "Gets or sets the full filename of the image file (png) used for the tool clip.
        The tool clip is the image shown when the user hovers the mouse over the workspace name in the workspace drop-down."
        Can be set with the same values you can pass to the construcor (image name or path)
        (`source <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-5C744005-AF96-4EEB-B060-FC246373B159>`_)
        """
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
        """ "Gets or sets the tooltip text displayed for the workspace.
        This is the first line of text shown when the user hovers over the workspace
        name in the Fusion 360 toolbar drop-down. This is typically the name of
        the workspace. This is different from the name in the that the name is a
        short name shown in the drop-down. The tooltip is only shown when the user
        hovers over the name and box appears providing more information about the
        workspace. For example, the name of the model workspace is "Model" and the
        tooltip is "Model Workspace"."
        (source `<http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-6AD46B6E-269C-4FC9-96BB-C6180BAA35ED>`_)
        """
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
        """[summary]

        Returns:
            [type]: [description]
        """
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
        """[summary]

        Args:
            id (str, optional): [description]. Defaults to None.
            name (str, optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
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

        self._in_fusion = self.parent.child_tabs.itemById(id)

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

    def panel(
        self,
        id: str = None,  # pylint:disable=redefined-builtin
        name: str = None,
        position: int = None,
    ):
        return Panel(self, name, id, position)

    @property
    def position(self):
        """ "Gets the position this tab is in within the toolbar. The first tab is
        at position 0. This value is with respect to the complete list of tabs so
        this value could be outside of the expected range if you have a collection
        of tabs associated with a workspace, which is a subset of the entire list of tabs."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-DA16E678-F571-422B-A42F-D964C092B49C>_`)
        """
        return self._in_fusion.index

    @property
    def is_active(self):
        """ "Gets if this toolbar tab is currently active - i.e. displayed."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-B54F2692-F167-4950-B465-4330379B9B3D>_`)
        """
        return self._in_fusion.isActive

    @property
    def is_native(self):
        """ "Gets if this tab is native to Fusion 360 or was created via the API."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-F5DE1649-C025-46DB-8F2E-AA9B7852BB4A>_`)
        """
        return self._in_fusion.isNative

    @property
    def is_visible(self):
        """ "Gets whether this tab is currently being displayed in the user interface."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-0DA0535A-EC20-450F-B4E0-6DAA7F21B022>_`)
        """
        return self._in_fusion.isVisible

    @property
    def is_valid(self):
        """ "Indicates if this object is still valid, i.e. hasn't been deleted or
        some other action done to invalidate the reference."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-3B2DC592-EA8D-4A7D-B147-1E5E8897A0E5>_`)
        """
        return self._in_fusion.isValid

    @property
    def name(self):
        """ "Gets the name of the tab as seen in the user interface."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-BF03BCDB-32F3-4066-A9EE-B32599DDC27D>_`)
        """
        return self._in_fusion.name

    @property
    def child_panels(self):
        """ "Gets the collection containing the panels associated with this tab.
        It's through this collection that you can add new toolbar panels."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-DE74300B-BA9D-433C-9A08-69218005E8BA>_`)
        """
        return self._in_fusion.toolbarPanels


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

        self._in_fusion = self.parent.child_panels.itemById(id)

        if self._in_fusion:
            not_setable = given_args.keys() - {"id", "parent"}
            if not_setable:
                self.app.logger.warning(
                    msgs.already_existing(self._ident, id, not_setable)
                )
            self.app.logger.info(msgs.using_exisitng(self._ident, id))
        else:
            panel_order = {p.indexWithinTab(): p.id for p in self.parent.child_panels}
            sorted_indices = sorted(list(panel_order.keys()))
            comes_before_id = None
            for i in sorted_indices:
                if i > position:
                    comes_before_id = panel_order[i]
                    break
            # check if index is greater than highest existing index
            comes_before_flag = True
            if not comes_before_id:
                comes_before_id = sorted_indices[-1]
                comes_before_flag = False

            self._in_fusion = self.parent.child_panels.add(
                id, name, comes_before_id, comes_before_flag
            )
            # nothing else to set

            self.app.register_element(self, self.ui_level)
            self.app.logger.info(msgs.created_new(self._ident, id))

    def button(
        self,
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

    @property
    def position(self):
        """ "Gets the position this panel is in within the toolbar tab. The first
        panel in the tab is at position 0."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-148C2831-F0E3-4DF9-8ED2-AC1F0B561B77>_`)
        """
        return self._in_fusion.indexWithinTab()

    @property
    def child_controls(self):
        """ "Gets the controls associated with this panel. These are all in the
        panel's drop-down (assuming their visible property is true) and are
        selectively shown within the panel."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-34d0c84b-302d-4bbf-819d-c92beb3db4ff>_`)
        """
        return self._in_fusion.controls

    @property
    def index(self):
        """ "Gets the position this panel is in within the toolbar. The first panel
        is at position 0. This value is with respect to the complete list of panels
        so this value could be outside of the expected range if you have a collection
        of panels associated with a workspace, which is a subset of the entire list of panels."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-2aa563c4-93bf-4c8b-8c66-ec204e405716>_`)
        """
        return self._in_fusion.index

    @property
    def is_valid(self):
        """ "Indicates if this object is still valid, i.e. hasn't been deleted or
        some other action done to invalidate the reference."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-43d2846d-6a4f-448d-a494-f46e77dbfc96>_`)
        """
        return self._in_fusion.isValid

    @property
    def is_visible(self):
        """ ""
        (Read only, `official docs <>_`)
        """
        return self._in_fusion.isVisible

    @property
    def name(self):
        """ "Gets whether this panel is currently being displayed in the user interface.
        Visibility of a panel is controlled by it being associated with the currently
        active workspace."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-f660e4f0-bdd5-469b-9d7e-eb2a8be38050>_`)
        """
        return self._in_fusion.name

    @property
    def promoted_controls(self):
        """ "Gets the controls in the panel that have been promoted.
        Promoted controls are the controls that are displayed within the panel."
        (Read only, `official docs <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-234ef3f2-7c5c-4daf-a6e8-94ea423dd2d8>_`)
        """
        return self._in_fusion.promotedControls


class Button(_FusionWrapper):

    _ident = "button"

    def __init__(
        self,
        parent: Panel,
        position_index: int = None,
        is_visible: bool = None,
        is_enabled: bool = None,
        is_promoted: bool = True,
        is_promoted_by_default: bool = True,
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
        cmd_ctrl = self.parent.child_controls.addCommand(
            dummy_cmd_def
        )  # , position, True)
        cmd_ctrl.isPromoted = is_promoted
        cmd_ctrl.isPromotedByDefault = is_promoted_by_default
        cmd_ctrl.isVisible = is_visible

        self._in_fusion = cmd_ctrl

        self.app.register(dummy_cmd_def, self.ui_level)
        self.app.register_element(self, self.ui_level + 1)
        self.app.logger.info(msgs.created_new(self._ident, None))

        self._connected_command = None

    @property
    def connected_command(self):
        return self.connected_command

    def command(
        self,
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
