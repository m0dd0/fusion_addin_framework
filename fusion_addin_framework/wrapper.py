# pylint:disable=redefined-builtin
# pylint:disable=unsubscriptable-object

import logging
from pathlib import Path
from abc import ABC
from typing import Union, Callable
from collections import defaultdict
from uuid import uuid4

try:
    import appdirs
except:
    logging.getLogger(__name__).warning(  # pylint:disable=logging-not-lazy
        "The appdirs package is not installed. Using path related attributes "
        + "(like ...) of the addin object will result in an Error. Consider "
        + "pip-installing (link) the fusion_addin_framework."
    )
import adsk.core
import adsk.fusion

from . import defaults as dflts
from . import messages as msgs
from . import handlers


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
        self._in_fusion = None
        self._parent = parent
        self._addin = self.parent.addin
        self._ui_level = self.parent.ui_level + 1

    def __getattr__(self, attr):
        # will only get called if the attribute is not expicitly contained in
        # the class instance
        return getattr(self._in_fusion, attr)

    def __setattr__(self, name, value):
        # avoid infinite recursion by using self.__dict__ instead of hasattr
        if "_in_fusion" in self.__dict__.keys() and hasattr(self._in_fusion, name):
            setattr(self._wrapped, name, value)
        else:
            super().__setattr__(name, value)

    # simply override the properties to use individual docstrings
    # region
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

    It handles their creation and deletes them if the addin is deactivated
    (by closing Fusion or stopping the Addin manually).
    Additionally it provides directories for logging, config and user data.
    """

    _ui_level = 0

    def __init__(
        self,
        name: str = None,
        author: str = None,
        debug_to_ui: bool = True,
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
        self._name = name
        self._author = author
        self._debug_to_ui = debug_to_ui

        self._registered_elements = defaultdict(list)

    def workspace(self, *args, **kwargs):
        """Creates a workspace as a child of this Adddin.

        Calling this method is the same as initialsing a :class:`.Workspace`
        with this addin instance as parent parameters. Therfore the same parameters
        are passed. See :class:`.Workspace` for a detailed description of the paramters.

        Returns:
            Workspace: The newly created or accessed Workspace instance.
        """
        return Workspace(self, *args, **kwargs)

    def stop(self):
        """Stops the addin and deletes all created ui elements.

        This methods needs to get called from the stop(context) function of the
        main file of your addin to ensure proper cleanup.
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
            elem = elem._in_fusion
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
        or only send to the module logger.
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
        productType: str = "DesignProductType",
        resourceFolder: Union[str, Path] = "lightbulb",
        toolClipFilename: Union[str, Path] = "lightbulb",
        tooltip: str = "",
        tooltipDescription: str = "",
    ):
        """[summary]

        Args:
            parent (FusionAddin): [description]
            id (str, optional): [description]. Defaults to "FusionSolidEnvironment".
            productType (str, optional): [description]. Defaults to "DesignProductType".
            resourceFolder (Union[str, Path], optional): [description]. Defaults to "lightbulb".
            toolClipFilename (Union[str, Path], optional): [description]. Defaults to "lightbulb".
            tooltip (str, optional): [description]. Defaults to "".
            tooltipDescription (str, optional): [description]. Defaults to "".
        """
        super().__init__(parent)

        id = dflts.eval_id(id)
        name = dflts.eval_name(name, __class__)
        resourceFolder = dflts.eval_image(resourceFolder)
        toolClipFilename = dflts.eval_image_path(toolClipFilename)

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
                productType, id, name, resourceFolder
            )
            self._in_fusion.toolClipFilename = toolClipFilename
            self._in_fusion.tooltip = tooltip
            self._in_fusion.tooltipDescription = tooltipDescription

            self.addin.register_element(self, self.ui_level)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def tab(self, *args, **kwargs):
        """[summary]

        Returns:
            [type]: [description]
        """
        return Tab(self, *args, **kwargs)


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

        if self._in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisitng(__class__, id))
        else:
            self._in_fusion = self.parent.toolbarTabs.add(id, name)
            # nothing else is setable

            self.addin.register_element(self, self.ui_level)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def panel(self, *args, **kwargs):
        return Panel(self, *args, **kwargs)


class Panel(_FusionWrapper):
    def __init__(
        self,
        parent: Tab,
        id: str = "random",
        name: str = "random",
    ):
        # TODO account for position
        super().__init__(parent)

        id = dflts.eval_id(id)
        name = dflts.eval_name(name, __class__)

        self._in_fusion = self.parent.toolbarPanels.itemById(id)
        # TODO test what wil happen if ui.allToolbarpanels.itemById() already exists

        if self._in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisitng(__class__, id))
        else:

            self._in_fusion = self.parent.toolbarPanels.add(id, name)

            self.addin.register_element(self, self.ui_level)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def button(self, *args, **kwargs):
        return Button(self, *args, **kwargs)


class _CommandControlWrapper(_FusionWrapper):
    def __init__(
        self, parent, isBefore, positionID, isPromoted, isPromotedByDefault, isVisible
    ):
        super().__init__(parent)

        self._isBefore = isBefore
        self._positionID = positionID
        self._isPomoted = isPromoted
        self._isPromotedByDefault = isPromotedByDefault
        self._isVisible = isVisible

    def _create_control(self, cmd_def):
        if self._in_fusion is not None:
            self._in_fusion.deleteMe()

        if self._positionID is not None:
            self._in_fusion = self.parent.controls.addCommand(
                cmd_def, self._positionID, self._isBefore
            )
        else:
            self._in_fusion = self.parent.controls.addCommand(cmd_def)

        self._in_fusion.isPromoted = self._isPromoted
        self._in_fusion.isPromotedByDefault = self._isPromotedByDefault
        self._in_fusion.isVisible = self._isVisible

        self.addin.register_element(self, self.ui_level)


class Button(_CommandControlWrapper):
    def __init__(
        self,
        parent: Panel,
        isVisible: bool = True,
        isPromoted: bool = True,
        isPromotedByDefault: bool = True,
        positionID: str = None,
        isBefore: bool = True,
    ):
        """Wraps around Fusions CommandControl class <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-bb8d8c7b-3049-40c9-b7a5-76d24a462327>
        A dummy command definition with a button control definition is used to
        instantiate the control.

        Args:
            parent (Panel): [description]
            isVisible (bool, optional): [description]. Defaults to True.
            isPromoted (bool, optional): [description]. Defaults to True.
            isPromotedByDefault (bool, optional): [description]. Defaults to True.
        """
        super().__init__(parent, isBefore, positionID, isPromoted, isPromotedByDefault)

        # a button can always be created since it has no id

        # create a dummy cmd_def with a button_ctrl_def to instantiate the cmd_ctrl
        # itself. This will get overridden by the connected command later.
        dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
            str(uuid4()),
            "<empty button>",
            "",
            dflts.eval_image("transparent"),
        )
        dummy_cmd_def.controlDefinition.isVisible = True
        dummy_cmd_def.controlDefinition.isEnabled = True
        dummy_cmd_def.controlDefinition.name = "<no command connected>"
        # do not connect a handler since its a dummy cmd_def

        self.addin.register_element(dummy_cmd_def, self.ui_level + 1)
        # if positionID is not None:
        #     self._in_fusion = self.parent.controls.addCommand(
        #         dummy_cmd_def, positionID, isBefore
        #     )
        # else:
        #     self._in_fusion = self.parent.controls.addCommand(dummy_cmd_def)
        # self._in_fusion.isPromoted = isPromoted
        # self._in_fusion.isPromotedByDefault = isPromotedByDefault
        # self._in_fusion.isVisible = isVisible

        # self.addin.register_element(self, self.ui_level)
        self._create_control(dummy_cmd_def)
        logging.getLogger(__name__).info(msgs.created_new(__class__, None))

        # self._positionID = positionID
        # self._isBefore = isBefore
        # self._connected_command = None

    # @property
    # def connected_command(self):
    #     return self.connected_command

    def command(self, *args, **kwargs):
        return ButtonCommand(self, *args, **kwargs)


class Checkbox(_CommandControlWrapper):
    def __init__(self, parent):
        super().__init__(parent)

        dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addCheckboxDefinition(
            str(uuid4()),
            "<no Command>",
            "",
            False,
        )
        dummy_cmd_def.controlDefinition.isVisible = True
        dummy_cmd_def.controlDefinition.isEnabled = True
        dummy_cmd_def.controlDefinition.name = "<no command connected>"
        dummy_cmd_def.controlDefinition.isChecked = isChecked
        # do not connect a handler since its a dummy cmd_def

        # if positionID is not None:
        #     self._in_fusion = self.parent.controls.addCommand(
        #         dummy_cmd_def, positionID, isBefore
        #     )
        # else:
        #     self._in_fusion = self.parent.controls.addCommand(dummy_cmd_def)
        # self._in_fusion.isPromoted = isPromoted
        # self._in_fusion.isPromotedByDefault = isPromotedByDefault
        # self._in_fusion.isVisible = isVisible

        self.addin.register_element(dummy_cmd_def, self.ui_level + 1)
        # self.addin.register_element(self, self.ui_level)
        logging.getLogger(__name__).info(msgs.created_new(__class__, None))

        # self._positionID = positionID
        # self._isBefore = isBefore


class Command(_FusionWrapper):
    def __init__(
        self,
        parent: Button,
        id: str = "random",
        name: str = "random",
        resourceFolder: Union[str, Path] = "lightbulb",
        tooltip: str = "",
        toolClipFileName: Union[str, Path] = "lightbulb",  # TODO no picture option
        isEnabled: bool = True,
        onCreated: Callable = dflts.do_nothing,
        onInputChanged: Callable = dflts.do_nothing,
        onPreview: Callable = dflts.do_nothing,
        onExecute: Callable = dflts.do_nothing,
        onDestroy: Callable = dflts.do_nothing,
        onKeyDown: Callable = dflts.do_nothing,
    ):
        super().__init__(parent)

        id = dflts.eval_id(id)
        name = dflts.eval_name(name, __class__)
        resourceFolder = dflts.eval_image(resourceFolder)
        toolClipFileName = dflts.eval_image_path(toolClipFileName)

        self._in_fusion = (
            adsk.core.Application.get().userInterface.commandDefinitions.itemById(id)
        )

        if self._in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisitng(__class__, id))

            # if self._in_fusion not isinstance parent:
            # rasise Error
        else:
            # create definition
            self._in_fusion = adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
                id, name, tooltip, resourceFolder
            )
            self._in_fusion.toolClipFilename = toolClipFileName
            self._in_fusion.controlDefinition.isEnabled = isEnabled
            self._in_fusion.controlDefinition.isVisible = (
                isVisible  # self.parent.isVisible
            )
            self._in_fusion.controlDefinition.name = name

            # ! if there is some error (typo) etc. fusion will break instantanious !
            self._in_fusion.commandCreated.add(
                handlers._CommandCreatedHandler(
                    self.addin,
                    name,
                    onCreated,
                    onExecute,
                    onPreview,
                    onInputChanged,
                )
            )
            self.addin.register_element(self, self.ui_level)

        self.parent._create_control(self._in_fusion)
        # create a new button
        # if self.parent._positionID:
        #     cmd_ctrl = self.parent.parent.controls.addCommand(
        #         self._in_fusion, self.parent._positionID, self.parent._isBefore
        #     )
        # else:
        #     cmd_ctrl = self.parent.parent.controls.addCommand(self._in_fusion)
        # cmd_ctrl.isPromoted = self.parent.isPromoted
        # cmd_ctrl.isPromotedByDefault = self.parent.isPromotedByDefault
        # cmd_ctrl.isVisible = self.parent.isVisible

        # self.parent._in_fusion.deleteMe()
        # self.parent._in_fusion = cmd_ctrl

        # self.addin.register_element(cmd_ctrl, self.ui_level - 1)

        logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def __getattr__(self, attr):
        try:
            return getattr(self._in_fusion, attr)
        except:
            return getattr(self._in_fusion.controlDefinition, attr)
        # finally:
        #     raise
        # TODO setattr
