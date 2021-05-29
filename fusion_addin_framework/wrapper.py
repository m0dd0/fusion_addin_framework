""" This module contains the wrapper classes around the user interface elements
and command realted object. The main functionality of the framework is provided
by these wrapper classes."""

# pylint:disable=redefined-builtin
# pylint:disable=unsubscriptable-object

import logging
from pathlib import Path
from abc import ABC
from typing import Union, Callable, List
from collections import defaultdict
from uuid import uuid4

from . import messages as msgs

try:
    import appdirs

    # TODO remove appdirs functionalitites for cleaner usage
except:
    logging.getLogger(__name__).warning(msgs.no_appdirs())
import adsk.core
import adsk.fusion

from . import defaults as dflts
from . import handlers


# will stop also addins instaces from other addins do use only for debugging
# _addins = []
# def stop_all():
#     for a in _addins:
#         a.stop()


class _FusionWrapper(ABC):
    def __init__(
        self, parent, parent_class
    ):  # do NOT use for parent typehint --> docs generation will crash
        """Base class for all Fusion UI wrapper classes.

        Provides basic functionality used by the framework to handle the wrapper
        instances.
        Such as having a app attribute, which contains the controlling addin instance.
        Also sets the ui_level which is a atrtibute used by all wrapper classes.
        Defining class variables shared by all wrapper classes.
        Sets the attributes app attribute of the wrapped instance by getting its
        parents app attribute.
        Sets the ui_level attribute by incrementing the parents ui_level attribute.

        Args:
            parent (Union[_FusionWrapper, FusionApp]): the parent ui object instance
                e.g.: the parent of a panel is always a tab.
            parent_class: The class whihc is used to generate a default parent.
        """
        self._in_fusion = None

        # TODO save parents always as list internally
        if parent is None:
            parent = parent_class()
        self._parent = parent

        if isinstance(parent, list):
            self._addin = self.parent[0].addin
        else:
            self._addin = self.parent.addin

        self._ui_level = self.parent.ui_level + 1

    def __getattr__(self, attr):
        """[summary]

        Args:
            attr ([type]): [description]

        Returns:
            [type]: [description]
        """
        # will only get called if the attribute is not expicitly contained in
        # the class instance
        return getattr(self._in_fusion, attr)

    def __setattr__(self, name, value):
        """[summary]

        Args:
            name ([type]): [description]
            value ([type]): [description]
        """
        # avoid infinite recursion by using self.__dict__ instead of hasattr
        if "_in_fusion" in self.__dict__.keys() and hasattr(self._in_fusion, name):
            setattr(self._in_fusion, name, value)
        else:
            super().__setattr__(name, value)

    # simply override the properties to use individual docstrings
    # region
    @property
    def parent(self):
        """The wrapped parent instance of this object.

        Can be an List of object if multiple parents where provided
        """
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

    _ui_level = 0

    def __init__(
        self,
        name: str = None,
        author: str = None,
        debug_to_ui: bool = True,
    ):
        """Entry point to create all your elements that will appear in the user interface.

        It handles their creation and deletes them if the addin is deactivated
        (by closing Fusion or stopping the Addin manually).
        Additionally it provides directories for logging, config and user data.

        Args:
            name (str, optional): The name of the addin. Used to create app
                directories with meaningful names. Defaults to None.
            author (str, optional): The name of the addins author. Used to create
                app directories with meaningful names. Defaults to None.
            debug_to_ui (bool, optional): Flag indicating if erorr messages caused
                by errrors in the eventhandlers are displayed in a `messageBox
                <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-1692a9a4-3be0-4474-9e15-02fac696b2b2>`_
                or not. If not they will get logged anyways. Defaults to True.
        """
        self._name = name
        self._author = author
        self._debug_to_ui = debug_to_ui

        self._registered_elements = defaultdict(list)

        # addin instances from other addins are also dtected so dont use
        # if len(_addins) > 0:
        #     logging.getLogger(__name__).warning(msgs.addin_exists())
        # _addins.append(self)

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
            elem = elem._in_fusion  # pylint:disable=protected-access
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
        parent: FusionAddin = None,
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
        super().__init__(parent, FusionAddin)

        id = dflts.eval_id(id)
        name = dflts.eval_name(name, __class__)
        resourceFolder = dflts.eval_image(resourceFolder)
        toolClipFilename = dflts.eval_image(toolClipFilename, "32x32.png")

        self._in_fusion = adsk.core.Application.get().userInterface.workspaces.itemById(
            id
        )

        if self._in_fusion is not None:
            logging.getLogger(__name__).info(msgs.using_exisiting(__class__, id))

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
        parent: Workspace = None,  # TODO mulitple parents
        id: str = "default",
        name: str = "random",
    ):
        """[summary]

        Args:
            parent (Workspace, optional): [description]. Defaults to None.
            name (str, optional): [description]. Defaults to "random".
        """
        super().__init__(parent, Workspace)

        id = dflts.eval_id(id, self)
        name = dflts.eval_name(name, __class__)

        self._in_fusion = self.parent.toolbarTabs.itemById(id)

        if self._in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisiting(__class__, id))
        else:
            self._in_fusion = self.parent.toolbarTabs.add(id, name)

            self.addin.register_element(self, self.ui_level)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def panel(self, *args, **kwargs):
        return Panel(self, *args, **kwargs)


class Panel(_FusionWrapper):
    def __init__(
        self,
        parent: Tab = None,  # TODO multiple parents
        id: str = "default",
        name: str = "random",
        positionID: str = "",
        isBefore: bool = True,
    ):
        """[summary]

        Args:
            parent (Tab, optional): [description]. Defaults to None.
            name (str, optional): [description]. Defaults to "random".
            positionID (str, optional): [description]. Defaults to "".
            isBefore (bool, optional): [description]. Defaults to True.
        """
        super().__init__(parent, Tab)

        id = dflts.eval_id(id, self)
        name = dflts.eval_name(name, __class__)

        self._in_fusion = self.parent.toolbarPanels.itemById(id)
        # TODO test what wil happen if ui.allToolbarpanels.itemById() already exists

        if self._in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisiting(__class__, id))
        else:

            self._in_fusion = self.parent.toolbarPanels.add(
                id, name, positionID, isBefore
            )

            self.addin.register_element(self, self.ui_level)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def button(self, *args, **kwargs):
        """[summary]

        Returns:
            [type]: [description]
        """
        return Button(self, *args, **kwargs)

    def checkbox(self, *args, **kwargs):
        """[summary]

        Returns:
            [type]: [description]
        """
        return Checkbox(self, *args, **kwargs)

    def list_control(self, *args, **kwargs):
        """[summary]

        Returns:
            [type]: [description]
        """
        return ListControl(self, *args, **kwargs)

    def control(self, *args, **kwargs):
        """[summary]

        Returns:
            [type]: [description]
        """
        return CommandControl(self, *args, **kwargs)


class CommandControl(_FusionWrapper):
    def __init__(
        self,
        parent: Panel = None,
        control_type: str = "button",
        isVisible: bool = True,
        isPromoted: bool = True,
        isPromotedByDefault: bool = True,
        positionID: int = None,
        isBefore: bool = True,
    ):
        """[summary]

        Args:
            parent (Panel): [description]
            isVisible (bool): [description]
            isPromoted (bool): [description]
            isPromotedByDefault (bool): [description]
            positionID (int): [description]
            isBefore (bool): [description]
        """
        super().__init__(parent, Panel)

        self._isVisible = isVisible
        self._isPromoted = isPromoted
        self._isPromotedByDefault = isPromotedByDefault
        self._positionID = positionID
        self._isBefore = isBefore

        if control_type == "button":
            dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
                str(uuid4()),
                "<no command connected>",
                "",
                dflts.eval_image("transparent"),
            )
        elif control_type == "checkbox":
            dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addCheckBoxDefinition(
                str(uuid4()),
                "<no command connected>",
                "",
                False,
            )
            dummy_cmd_def.controlDefinition.isChecked = False
        elif control_type == "list":
            dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addListDefinition(
                str(uuid4()),
                "<no command connected>",
                adsk.core.ListControlDisplayTypes.RadioButtonlistType,
            )
            dummy_cmd_def.controlDefinition.listItems.add("<empty list>", False)

        dummy_cmd_def.controlDefinition.isVisible = True
        dummy_cmd_def.controlDefinition.isEnabled = True
        dummy_cmd_def.controlDefinition.name = "<no command connected>"
        # do not connect a handler since its a dummy cmd_def

        self.addin.register_element(dummy_cmd_def, self.ui_level + 1)

        self._create_control(dummy_cmd_def)

        logging.getLogger(__name__).info(msgs.created_new(__class__, None))

    def _create_control(self, cmd_def):
        """[summary]

        Args:
            cmd_def ([type]): [description]
        """
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

    def addin_command(self, *args, **kwargs):
        """[summary]

        Returns:
            [type]: [description]
        """
        return AddinCommand(self, *args, **kwargs)


class Button(CommandControl):
    def __init__(
        self,
        parent: Panel = None,
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
        super().__init__(
            parent,
            "button",
            isVisible,
            isPromoted,
            isPromotedByDefault,
            positionID,
            isBefore,
        )

        # # create a dummy cmd_def with a button_ctrl_def to instantiate the cmd_ctrl
        # # itself. This will get overridden by the connected command later.
        # dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
        #     str(uuid4()),
        #     "<no command connected>",
        #     "",
        #     dflts.eval_image("transparent"),
        # )
        # # TODO put in super class
        # dummy_cmd_def.controlDefinition.isVisible = True
        # dummy_cmd_def.controlDefinition.isEnabled = True
        # dummy_cmd_def.controlDefinition.name = "<no command connected>"
        # # do not connect a handler since its a dummy cmd_def

        # self.addin.register_element(dummy_cmd_def, self.ui_level + 1)

        # self._create_control(dummy_cmd_def)

        # logging.getLogger(__name__).info(msgs.created_new(__class__, None))

    # def buttonCommand(self, *args, **kwargs):
    #     """[summary]

    #     Returns:
    #         [type]: [description]
    #     """
    #     return ButtonCommand(self, *args, **kwargs)


class Checkbox(CommandControl):
    def __init__(
        self,
        parent: Panel = None,
        isVisible: bool = True,
        isPromoted: bool = True,
        isPromotedByDefault: bool = True,
        positionID: str = None,
        isBefore: bool = True,
    ):
        """[summary]

        Args:
            parent (Panel, optional): [description]. Defaults to None.
            isVisible (bool, optional): [description]. Defaults to True.
            isPromoted (bool, optional): [description]. Defaults to True.
            isPromotedByDefault (bool, optional): [description]. Defaults to True.
            positionID (str, optional): [description]. Defaults to None.
            isBefore (bool, optional): [description]. Defaults to True.
        """
        super().__init__(
            parent,
            "checkbox",
            isVisible,
            isPromoted,
            isPromotedByDefault,
            positionID,
            isBefore,
        )

        # dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addCheckBoxDefinition(
        #     str(uuid4()),
        #     "<no command connected>",
        #     "",
        #     False,
        # )
        # # TODO put in super class
        # dummy_cmd_def.controlDefinition.isVisible = True
        # dummy_cmd_def.controlDefinition.isEnabled = True
        # dummy_cmd_def.controlDefinition.name = "<no command connected>"

        # dummy_cmd_def.controlDefinition.isChecked = False
        # # do not connect a handler since its a dummy cmd_def

        # self.addin.register_element(dummy_cmd_def, self.ui_level + 1)

        # self._create_control(dummy_cmd_def)

        # logging.getLogger(__name__).info(msgs.created_new(__class__, None))

    # def checkboxCommand(self, *args, **kwargs):
    #     return CheckboxCommand(self, *args, **kwargs)


class ListControl(CommandControl):
    def __init__(
        self,
        parent: Panel = None,
        isVisible: bool = True,
        isPromoted: bool = True,
        isPromotedByDefault: bool = True,
        positionID: str = None,
        isBefore: bool = True,
    ):
        """[summary]

        Args:
            parent (Panel, optional): [description]. Defaults to None.
            isVisible (bool, optional): [description]. Defaults to True.
            isPromoted (bool, optional): [description]. Defaults to True.
            isPromotedByDefault (bool, optional): [description]. Defaults to True.
            positionID (str, optional): [description]. Defaults to None.
            isBefore (bool, optional): [description]. Defaults to True.
        """
        super().__init__(
            parent,
            "list",
            isVisible,
            isPromoted,
            isPromotedByDefault,
            positionID,
            isBefore,
        )

        # dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addListDefinition(
        #     str(uuid4()),
        #     "<no command connected>",
        #     adsk.core.ListControlDisplayTypes.RadioButtonlistType,
        # )
        # # TODO put in super class
        # dummy_cmd_def.controlDefinition.isVisible = True
        # dummy_cmd_def.controlDefinition.isEnabled = True
        # dummy_cmd_def.controlDefinition.name = "<no command connected>"
        # dummy_cmd_def.controlDefinition.listItems.add("<empty list>", False)
        # # do not connect a handler since its a dummy cmd_def

        # self.addin.register_element(dummy_cmd_def, self.ui_level + 1)

        # self._create_control(dummy_cmd_def)

        # logging.getLogger(__name__).info(msgs.created_new(__class__, None))

    # def listCommand(self, *args, **kwargs):
    #     """[summary]

    #     Returns:
    #         [type]: [description]
    #     """
    #     return ListCommand(self, *args, **kwargs)


# TODO unify commands


class AddinCommand(_FusionWrapper):
    def __init__(
        self,
        parent: Union[
            List[Button],
            Button,
            List[Checkbox],
            Checkbox,
            List[ListControl],
            ListControl,
        ] = None,
        id: str = "random",
        name: str = "random",
        resourceFolder: Union[str, Path] = "lightbulb",
        tooltip: str = "",
        toolClipFileName: Union[str, Path] = None,
        isEnabled: bool = True,
        isVisible: bool = True,
        isChecked: bool = True,  # only checkbox
        listControlDisplayType=adsk.core.ListControlDisplayTypes.RadioButtonlistType,  # only list
        **event_handlers: Callable,
    ):
        """[summary]

        Args:
            parent (Union[ List[Button], Button, List[Checkbox], Checkbox, List[ListControl], ListControl, ], optional): [description]. Defaults to None.
            id (str, optional): [description]. Defaults to "random".
            name (str, optional): [description]. Defaults to "random".
            resourceFolder (Union[str, Path], optional): [description]. Defaults to "lightbulb".
            tooltip (str, optional): [description]. Defaults to "".
            toolClipFileName (Union[str, Path], optional): [description]. Defaults to None.
            isEnabled (bool, optional): [description]. Defaults to True.
            isVisible (bool, optional): [description]. Defaults to True.
            isChecked (bool, optional): [description]. Defaults to True.
        """
        super().__init__(parent, Button)

        id = dflts.eval_id(id)
        name = dflts.eval_name(name, __class__.__bases__[0])
        resourceFolder = dflts.eval_image(resourceFolder)
        toolClipFileName = dflts.eval_image(toolClipFileName, "32x32.png")

        # TODO unify mulitple parent routine
        if not isinstance(self.parent, list):
            parent = [self.parent]

        self._in_fusion = (
            adsk.core.Application.get().userInterface.commandDefinitions.itemById(id)
        )

        if self._in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisiting(__class__, id))
        else:
            # create definition depending on the parent(s) control type
            # (TODO helper for generc dmf_def creation avoid code duplication in command control class)
            if (  # if parent.control_type == "button":
                parent.commandDefinition.controlDefinition.objectType
                == adsk.core.ButtonControlDefinition.classType()
            ):
                self._in_fusion = adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
                    id,
                    name,
                    tooltip,
                    resourceFolder,
                )
            elif (  # if parent.control_type == "checkbox":
                parent.commandDefinition.controlDefinition.objectType
                == adsk.core.CheckBoxControlDefinition.classType()
            ):
                self._in_fusion = adsk.core.Application.get().userInterface.commandDefinitions.addCheckBoxDefinition(
                    id,
                    name,
                    tooltip,
                    isChecked,
                )
            elif (  # if parent.control_type == "list":
                parent.commandDefinition.controlDefinition.objectType
                == adsk.core.ListControlDefinition.classType()
            ):
                self._in_fusion = adsk.core.Application.get().userInterface.commandDefinitions.addCListDefinition(
                    id,
                    name,
                    listControlDisplayType,
                    resourceFolder,
                )

            if toolClipFileName is not None:
                self._in_fusion.toolClipFilename = toolClipFileName
            self._in_fusion.tooltip = tooltip
            self._in_fusion.resourceFolder = resourceFolder
            self._in_fusion.controlDefinition.isEnabled = isEnabled
            self._in_fusion.controlDefinition.isVisible = isVisible
            self._in_fusion.controlDefinition.name = name

            # ! if there is some error (typo) etc. fusion will break instantanious !
            self._in_fusion.commandCreated.add(
                handlers._CommandCreatedHandler(  # pylint:disable=protected-access
                    self.addin, name, event_handlers
                )
            )

            self.addin.register_element(self, self.ui_level)

        for p in parent:
            p._create_control(self._in_fusion)  # pylint:disable=protected-access

        logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def add_parent_control(self, parent):
        """[summary]

        Args:
            parent ([type]): [description]
        """
        parent._create_control(self._in_fusion)  # pylint:disable=protected-access
        self.parent.append(parent)

    def __getattr__(self, attr):
        try:
            return getattr(self._in_fusion.controlDefinition, attr)
        except:
            return getattr(self._in_fusion, attr)

    def __setattr__(self, name, value):
        # avoid infinite recursion by using self.__dict__ instead of hasattr
        if "_in_fusion" in self.__dict__.keys() and hasattr(self._in_fusion, name):
            try:
                setattr(self._in_fusion.controlDefinition, name, value)
            except:
                setattr(self._in_fusion, name, value)
        else:
            super().__setattr__(name, value)


# class _CommandWrapper(_FusionWrapper):
#     def __init__(self, parent, parent_class):
#         """[summary]

#         Args:
#             parent ([type]): [description]
#             parent_class ([type]): [description]
#         """
#         super().__init__(parent, parent_class)

#     def _setup_routine(
#         self,
#         id,
#         name,
#         toolClipFileName,
#         tooltip,
#         resourceFolder,
#         isEnabled,
#         isVisible,
#         event_handlers,
#         subclass,
#         adding_method,
#     ):
#         """[summary]

#         Args:
#             id ([type]): [description]
#             name ([type]): [description]
#             toolClipFileName ([type]): [description]
#             tooltip ([type]): [description]
#             resourceFolder ([type]): [description]
#             isEnabled (bool): [description]
#             isVisible (bool): [description]
#             event_handlers ([type]): [description]
#             subclass ([type]): [description]
#             adding_method ([type]): [description]
#         """
#         self._in_fusion = (
#             adsk.core.Application.get().userInterface.commandDefinitions.itemById(id)
#         )

#         if self._in_fusion:
#             logging.getLogger(__name__).info(msgs.using_exisiting(subclass, id))
#         else:
#             # create definition
#             self._in_fusion = adding_method()

#             if toolClipFileName is not None:
#                 self._in_fusion.toolClipFilename = toolClipFileName
#             self._in_fusion.tooltip = tooltip
#             self._in_fusion.resourceFolder = resourceFolder
#             self._in_fusion.controlDefinition.isEnabled = isEnabled
#             self._in_fusion.controlDefinition.isVisible = isVisible
#             self._in_fusion.controlDefinition.name = name

#             # ! if there is some error (typo) etc. fusion will break instantanious !
#             self._in_fusion.commandCreated.add(
#                 handlers._CommandCreatedHandler(  # pylint:disable=protected-access
#                     self.addin, name, event_handlers
#                 )
#             )

#             self.addin.register_element(self, self.ui_level)

#         if not isinstance(self.parent, list):
#             parent = [self.parent]
#         for p in parent:
#             p._create_control(self._in_fusion)  # pylint:disable=protected-access

#         logging.getLogger(__name__).info(msgs.created_new(subclass, id))

#     def add_parent_control(self, parent):
#         """[summary]

#         Args:
#             parent ([type]): [description]
#         """
#         parent._create_control(self._in_fusion)  # pylint:disable=protected-access
#         self.parent.append(parent)

#     def __getattr__(self, attr):
#         try:
#             return getattr(self._in_fusion.controlDefinition, attr)
#         except:
#             return getattr(self._in_fusion, attr)

#     def __setattr__(self, name, value):
#         # avoid infinite recursion by using self.__dict__ instead of hasattr
#         if "_in_fusion" in self.__dict__.keys() and hasattr(self._in_fusion, name):
#             try:
#                 setattr(self._in_fusion.controlDefinition, name, value)
#             except:
#                 setattr(self._in_fusion, name, value)
#         else:
#             super().__setattr__(name, value)


# class ButtonCommand(_CommandWrapper):
#     def __init__(
#         self,
#         parent: Union[List[Button], Button] = None,
#         id: str = "random",
#         name: str = "random",
#         resourceFolder: Union[str, Path] = "lightbulb",
#         tooltip: str = "",
#         toolClipFileName: Union[str, Path] = None,
#         isEnabled: bool = True,
#         isVisible: bool = True,
#         **event_handlers: Callable,
#     ):
#         """[summary]

#         Args:
#             parent (Union[List[Button], Button], optional): [description]. Defaults to None.
#             id (str, optional): [description]. Defaults to "random".
#             name (str, optional): [description]. Defaults to "random".
#             resourceFolder (Union[str, Path], optional): [description]. Defaults to "lightbulb".
#             tooltip (str, optional): [description]. Defaults to "".
#             toolClipFileName (Union[str, Path], optional): [description]. Defaults to None.
#             isEnabled (bool, optional): [description]. Defaults to True.
#             isVisible (bool, optional): [description]. Defaults to True.
#         """
#         super().__init__(parent, Button)

#         id = dflts.eval_id(id)
#         name = dflts.eval_name(name, __class__.__bases__[0])
#         resourceFolder = dflts.eval_image(resourceFolder)
#         toolClipFileName = dflts.eval_image(toolClipFileName, "32x32.png")

#         adding_method = partial(
#             adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition,
#             id,
#             name,
#             tooltip,
#             resourceFolder,
#         )

#         self._setup_routine(
#             id,
#             name,
#             toolClipFileName,
#             tooltip,
#             resourceFolder,
#             isEnabled,
#             isVisible,
#             event_handlers,
#             __class__,
#             adding_method,
#         )


# class CheckboxCommand(_CommandWrapper):
#     def __init__(
#         self,
#         parent: Union[List[Checkbox], Checkbox] = None,
#         id: str = "random",
#         name: str = "random",
#         tooltip: str = "",
#         toolClipFileName: Union[str, Path] = None,
#         resourceFolder: str = "lightbulb",
#         isEnabled: bool = True,
#         isVisible: bool = True,
#         isChecked: bool = False,
#         **event_handlers: Callable,
#     ):
#         """[summary]

#         Args:
#             parent (Union[List[Checkbox], Checkbox], optional): [description]. Defaults to None.
#             id (str, optional): [description]. Defaults to "random".
#             name (str, optional): [description]. Defaults to "random".
#             tooltip (str, optional): [description]. Defaults to "".
#             toolClipFileName (Union[str, Path], optional): [description]. Defaults to None.
#             resourceFolder (str, optional): [description]. Defaults to "lightbulb".
#             isEnabled (bool, optional): [description]. Defaults to True.
#             isVisible (bool, optional): [description]. Defaults to True.
#             isChecked (bool, optional): [description]. Defaults to False.
#         """
#         super().__init__(parent, Checkbox)

#         id = dflts.eval_id(id)
#         name = dflts.eval_name(name, __class__.__bases__[0])
#         resourceFolder = dflts.eval_image(resourceFolder)
#         toolClipFileName = dflts.eval_image(toolClipFileName, "32x32.png")

#         adding_method = partial(
#             adsk.core.Application.get().userInterface.commandDefinitions.addCheckBoxDefinition,
#             id,
#             name,
#             tooltip,
#             isChecked,
#         )

#         self._setup_routine(
#             id,
#             name,
#             toolClipFileName,
#             tooltip,
#             resourceFolder,
#             isEnabled,
#             isVisible,
#             event_handlers,
#             __class__,
#             adding_method,
#         )


# class ListCommand(_CommandWrapper):
#     def __init__(
#         self,
#         parent: Union[List[ListControl], ListControl] = None,
#         id: str = "random",
#         name: str = "random",
#         resourceFolder: Union[str, Path] = "lightbulb",
#         tooltip: str = "",
#         toolClipFileName: Union[str, Path] = None,
#         isEnabled: bool = True,
#         isVisible: bool = True,
#         listControlDisplayType=adsk.core.ListControlDisplayTypes.RadioButtonlistType,
#         **event_handlers: Callable,
#     ):
#         """[summary]

#         Args:
#             parent (Union[List[ListControl], ListControl], optional): [description]. Defaults to None.
#             id (str, optional): [description]. Defaults to "random".
#             name (str, optional): [description]. Defaults to "random".
#             resourceFolder (Union[str, Path], optional): [description]. Defaults to "lightbulb".
#             tooltip (str, optional): [description]. Defaults to "".
#             toolClipFileName (Union[str, Path], optional): [description]. Defaults to None.
#             isEnabled (bool, optional): [description]. Defaults to True.
#             isVisible (bool, optional): [description]. Defaults to True.
#             listControlDisplayType ([type], optional): [description]. Defaults to adsk.core.ListControlDisplayTypes.RadioButtonlistType.
#         """
#         super().__init__(parent, ListControl)

#         id = dflts.eval_id(id)
#         name = dflts.eval_name(name, __class__.__bases__[0])
#         resourceFolder = dflts.eval_image(resourceFolder)
#         toolClipFileName = dflts.eval_image(toolClipFileName, "32x32.png")

#         adding_method = partial(
#             adsk.core.Application.get().userInterface.commandDefinitions.addCListDefinition,
#             id,
#             name,
#             listControlDisplayType,
#             resourceFolder,
#         )

#         self._setup_routine(
#             id,
#             name,
#             toolClipFileName,
#             tooltip,
#             resourceFolder,
#             isEnabled,
#             isVisible,
#             event_handlers,
#             __class__,
#             adding_method,
#         )
