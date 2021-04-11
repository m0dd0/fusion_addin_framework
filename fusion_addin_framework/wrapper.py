import logging
from pathlib import Path
from abc import ABC
from typing import Union, Callable, Dict, List
from collections import defaultdict
from uuid import uuid4

import appdirs
import adsk.core
import adsk.fusion

from . import defaults as dflts
from . import messages as msgs
from . import handlers


# constructor arguments are evaluated by using the locals() function, therefore
# this error can be ignored
# pylint:disable=unused-argument


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
        """Base class for all Fusion UI wrapper classes.
        Sets the attributes app attribute of the wrapped instance by getting its
        parents app attribute.
        Sets the ui_level attribute by incrementing the parents ui_level attribute.

        Args:
            parent (Union[_FusionWrapper, FusionApp]): the parent ui object instance
                e.g.: the parent of a panel is always a tab.
        """
        self._parent = parent
        self._addin = self.parent.addin
        self._ui_level = self.parent.ui_level + 1

    def __getattr__(self, attr):
        # attr_str_coponents = attr.split('_')

        return getattr(self.in_fusion, attr)

    # simply override the properties to use individual docstrings
    # region
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
    def addin(self):
        """The app instance which manages this instance."""
        return self._addin

    # endregion


class FusionAddin:
    """Entry point to create all your elements that will appear in the user interface.

    It handles their creation and deletes them
    if the addin is deactivated (by closing Fusion or stopping the Addin
    manually).
    Additionally it provides directories for log, congig and user data.
    """

    _ui_level = 0

    def __init__(
        self,
        name: str = None,
        author: str = None,
        debug_to_ui: bool = False,
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

        # normaly theres no need to use properties since its ok to set these attributes arbitrarily
        # however, sphinx autosummary module will not recognize attributes (only properties)
        # https://stackoverflow.com/questions/29902483/how-can-i-get-sphinx-autosummary-to-display-the-docs-for-an-instance-attributes
        # therfore (and for consisteny) properties are used for all attributes
        # also the code doenst get messy if you provide long attribute docstrings
        self._name = name
        self._author = author
        self._debug_to_ui = debug_to_ui

        self._registered_elements = defaultdict(list)

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
                `unwrapped <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-974691b7-5ff6-4bec-8fbc-1683f7b33fe5>`_
            image (Union[str, Path], optional): Either the path to a directory
                containing images named 49X31.png and 98x62.png or one of the
                default picture names (currently only 'lightbulb'). Defaults to 'lightbulb.
                `unwrapped <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-19c3a0e8-7a55-4a03-8aa3-c8ca9b845e84>`_
            tooltip_image (Union[str, Path], optional): Either full filename of
                the image file (png) used for the tool clip or one of the
                default picture names (currently only 'lightbulb'). The tooltip image
                is the image shown when the user hovers the mouse over the workspace
                name in the workspace drop-down. If None no image will be set.
                `unwrapped <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-5C744005-AF96-4EEB-B060-FC246373B159>`_
            tooltip_head (str, optional):  The tooltip text displayed for the workspace.
                This is the first line of text shown when the user hovers over the
                workspace name in the Fusion 360 toolbar drop-down.
                Defaults to "" (empty string).
                `unwrapped <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-6AD46B6E-269C-4FC9-96BB-C6180BAA35ED>`_
            tooltip_text (str, optional): The tooltip description displayed for
                the workspace. The tooltip description is a longer description of
                the workspace and is only displayed when the user hovers over the
                workspace name in the Fusion 360 toolbar drop-down.
                Defaults to "" (empty string).
                `unwrapped <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-4FCC71F8-8087-4F07-AB3D-D9699DBF883C>`_

        Returns:
            Workspace: The newly created or accessed Workspace instance.
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
        for level in reversed(sorted(list(self._registered_elements.keys()))):
            elems = self._registered_elements.pop(level)
            for elem in elems:
                try:
                    elem.deleteMe()
                except:
                    # element is probably already deleted
                    pass

    def register_element(self, elem: _FusionWrapper, level: int = 0):
        """Registers a instance of a ui wrapper object to the addin.

        All wrapper objects that are registered will get deleted if the addin stops.
        The order of the deletion is determind by the level. Instances with a
        higher level will get deleted first.
        All elements that are created will be registered by the framework internally,
        so there is no need to use this method in noraml use of the framework.

        Args:
            elem (_FusionWrapper): The wrapper instance to register.
            level (int, optional): The Ui level of the element. Defaults to 0.
        """
        if isinstance(elem, _FusionWrapper):
            elem = elem.in_fusion
        self._registered_elements[level].append(elem)
        return self.addin

    # region
    @property
    def name(self) -> str:
        """str: The name of the addin. Used for user directories only."""
        return self._name

    @name.setter
    def name(self, new_name: str):
        self._name = new_name

    @property
    def author(self) -> str:
        """str: The author of the addin. Used for user directories only."""
        return self._author

    @author.setter
    def author(self, new_author: str):
        self._author = new_author

    @property
    def debug_to_ui(self) -> bool:
        """bool: Flag indicating if erorr messages are displayed in a `messageBox
        <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-1692a9a4-3be0-4474-9e15-02fac696b2b2>`_
        or not.
        """
        return self._debug_to_ui

    @debug_to_ui.setter
    def debug_to_ui(self, new_debug_to_ui: bool):
        self._debug_to_ui = new_debug_to_ui

    @property
    def user_state_dir(self) -> str:
        """str: Directory for saving user state data."""
        return appdirs.user_state_dir(self.name, self.author)

    @property
    def user_cache_dir(self) -> str:
        """str: Directory for saving user cache data."""
        return appdirs.user_cache_dir(self.name, self.author)

    @property
    def user_config_dir(self) -> str:
        """str: Directory for saving user config data."""
        return appdirs.user_config_dir(self.name, self.author)

    @property
    def user_data_dir(self) -> str:
        """str: Directory for saving user data."""
        return appdirs.user_data_dir(self.name, self.author)

    @property
    def user_log_dir(self) -> str:
        """str: Directory for saving user log data."""
        return appdirs.user_log_dir(self.name, self.author)

    @property
    def ui_level(self) -> int:
        """int: The ui level ot the app. (Always 0)"""
        return self._ui_level

    @property
    def addin(self):  # do not use typehint --> doc generation will craah
        """FusionApp: Itself. Kept for consistency with the other wrapper classses."""
        return self

    @property
    def created_elements(self):  # -> Dict[int, List[FusionApp]]:
        """Dict[int, List[FusionApp]]: A dictonary with all the created ui elemnts.
        Mapped by their level.
        """
        return self._registered_elements

    # endregion


class Workspace(_FusionWrapper):
    def __init__(
        self,
        parent: FusionAddin,
        id: str = "FusionSolidEnvironment",  # pylint:disable=redefined-builtin
        name: str = "random",
        product_type: str = "DesignProductType",
        image: Union[str, Path] = "lightbulb",
        tooltip_image: Union[str, Path] = "lightbulb",
        tooltip_head: str = "",
        tooltip_text: str = "",
    ):
        """[summary]

        Args:
            parent (FusionAddin): [description]
            id (str, optional): [description]. Defaults to None.
            product_type (str, optional): [description]. Defaults to None.
            image (Union[str, Path], optional): [description]. Defaults to None.
            tooltip_image (Union[str, Path], optional): [description]. Defaults to None.
            tooltip_head (str, optional): [description]. Defaults to None.
            tooltip_text (str, optional): [description]. Defaults to None.
        """
        super().__init__(parent)

        id = dflts.eval_id(id)
        name = dflts.eval_name(name, __class__)
        image = dflts.eval_image(image)
        tooltip_image = dflts.eval_image(tooltip_image)

        # try to get an existing instance
        self._in_fusion = adsk.core.Application.get().userInterface.workspaces.itemById(
            id
        )

        # if there is an instance, show warning message if there are more arguments
        # than necessary to get the workspace
        if self._in_fusion is not None:
            logging.getLogger(__name__).info(msgs.using_exisitng(__class__, id))

        # create new workspace if there is no
        else:
            self._in_fusion = adsk.core.Application.get().userInterface.workspaces.add(
                product_type, id, name, image
            )
            self._in_fusion.toolClipFilename = tooltip_image
            self._in_fusion.tooltip = tooltip_head
            self._in_fusion.tooltipDescription = tooltip_head

            self.addin.register_element(self, self.ui_level)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def tab(self):
        """[summary]

        Args:
            id (str, optional): [description]. Defaults to None.
            name (str, optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        return Tab(self)


class Tab(_FusionWrapper):
    def __init__(
        self,
        parent: Workspace,
        id: str = "ToolsTab",  # pylint:disable=redefined-builtin
        name: str = "random",
    ):
        super().__init__(parent)

        id = dflts.eval_id(id)
        name = dflts.eval_name(name, __class__)

        self._in_fusion = self.parent.toolbarTabs.itemById(id)

        if self.in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisitng(__class__, id))
        else:
            self._in_fusion = self.parent.toolbarTabs.add(id, name)
            # nothing else is setable

            self.addin.register_element(self, self.ui_level)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def panel(self):
        return Panel(self)


class Panel(_FusionWrapper):
    def __init__(
        self,
        parent: Tab,
        id: str = "random",  # pylint:disable=redefined-builtin
        name: str = "random",
    ):
        # TODO account for position
        super().__init__(parent)

        id = dflts.eval_id(id)
        name = dflts.eval_name(name, __class__)

        self._in_fusion = self.parent.toolbarPanels.itemById(id)

        if self._in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisitng(__class__, id))
        else:

            self._in_fusion = self.parent.toolbarPanels.add(id, name)

            self.addin.register_element(self, self.ui_level)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def button(self):
        return Button(self)


class Button(_FusionWrapper):
    def __init__(
        self,
        parent: Panel,
        is_visible: bool = True,
        is_enabled: bool = True,
        is_promoted: bool = True,
        is_promoted_by_default: bool = True,
    ):
        super().__init__(parent)
        # TODO account position

        # a button can always be created since it has no id

        dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
            str(uuid4()),
            "<empty button>",
            "",
            dflts.eval_image("transparent"),
        )
        dummy_cmd_def.controlDefinition.isVisible = is_visible
        dummy_cmd_def.controlDefinition.isEnabled = is_enabled
        dummy_cmd_def.controlDefinition.name = "<no command connected>"
        # do not connect a handler since its a dummy cmd_def

        self._in_fusion = self.parent.controls.addCommand(dummy_cmd_def)
        self._in_fusion.isPromoted = is_promoted
        self._in_fusion.isPromotedByDefault = is_promoted_by_default
        self._in_fusion.isVisible = is_visible

        self.addin.register_element(dummy_cmd_def, self.ui_level + 1)
        self.addin.register_element(self, self.ui_level)
        logging.getLogger(__name__).info(msgs.created_new(__class__, None))

        # self._connected_command = None

    # @property
    # def connected_command(self):
    #     return self.connected_command

    def command(self):
        return Command(self)


class Command(_FusionWrapper):
    def __init__(
        self,
        parent: Button,
        id: str = "random",  # cmd_def #pylint:disable=redefined-builtin
        name: str = "random",  # cmd_Def
        image: Union[str, Path] = "lighbulb",  # cmd_def
        tooltip: str = "",  # cmd_def
        tooltip_image: Union[str, Path] = "lighbulb",  # cmd_Def
        on_created: Callable = dflts.do_nothing,  # cmd_def
        on_input_changed: Callable = dflts.do_nothing,  # cmd_def
        on_preview: Callable = dflts.do_nothing,  # cmd_def
        on_execute: Callable = dflts.do_nothing,  # cmd_def
        on_destroy: Callable = dflts.do_nothing,  # cmd_def
        on_key_down: Callable = dflts.do_nothing,  # cmd_def
    ):
        super().__init__(parent)

        id = dflts.eval_id(id)
        name = dflts.eval_name(name, __class__)
        image = dflts.eval_image(image)
        tooltip_image = dflts.eval_image(tooltip_image)

        self._in_fusion = (
            adsk.core.Application.get().userInterface.commandDefinitions.itemById(id)
        )

        if self._in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisitng(__class__, id))
        else:
            # create definition
            self._in_fusion = adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
                id, name, tooltip, image
            )
            self._in_fusion.toolClipFilename = tooltip_image
            self._in_fusion.controlDefinition.isVisible = self.parent.is_visible
            self._in_fusion.controlDefinition.isEnabled = self.parent.is_enabled
            self._in_fusion.controlDefinition.name = name

            self._in_fusion.commandCreated.add(
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

            # create a new button
            cmd_ctrl = self.parent.parent.controls.addCommand(self._in_fusion)
            cmd_ctrl.isPromoted = self.parent.isPromoted
            cmd_ctrl.isPromotedByDefault = self.parent.isPromotedByDefault
            cmd_ctrl.isVisible = self.parent.isVisible

            self.parent.in_fusion.deleteMe()
            self.parent._in_fusion = cmd_ctrl

            self.addin.register_element(self, self.ui_level)
            self.addin.register_element(cmd_ctrl, self.ui_level - 1)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def __getattr__(self, attr):
        try:
            return getattr(self._cmd_def, attr)
        except:
            return getattr(self._cmd_ctrl, attr)