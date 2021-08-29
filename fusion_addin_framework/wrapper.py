""" This module contains the wrapper classes around the user interface elements
and command realted object. The main functionality of the framework is provided
by these wrapper classes."""

# pylint:disable=redefined-builtin
# pylint:disable=unsubscriptable-object

import logging
from pathlib import Path
from abc import ABC
from typing import Union, Callable, List, Any, Dict
from collections import defaultdict
from uuid import uuid4

import adsk.core
import adsk.fusion

from . import messages as msgs
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
        Also sets the uiLevel which is a atrtibute used by all wrapper classes.
        Defining class variables shared by all wrapper classes.
        Sets the attributes app attribute of the wrapped instance by getting its
        parents app attribute.
        Sets the uiLevel attribute by incrementing the parents uiLevel attribute.

        Args:
            parent (Union[_FusionWrapper, FusionApp]): the parent ui object instance
                e.g.: the parent of a panel is always a tab.
            parent_class: The class whihc is used to generate a default parent.
        """
        self._in_fusion = None

        if parent is None:
            parent = parent_class()
        self._parent = parent

        # for now this is only the case for addincommand class
        if isinstance(self._parent, list):
            self._addin = self._parent[0].addin
            self._ui_level = self._parent[0].uiLevel + 1
        else:
            self._addin = self._parent.addin
            self._ui_level = self._parent.uiLevel + 1

    def __getattr__(self, attr: str) -> Any:
        """Tries to find and return the attribute with the given name in the fusion-object
        on which the wrapper is wrapped around. This will only get called if no
        attribute with the given name is found on the wrapper object itself.

        Args:
            attr (str): The attribute name.

        Returns:
            Any: The attribute value.
        """
        # will only get called if the attribute is not expicitly contained in
        # the class instance
        return getattr(self._in_fusion, attr)

    def __setattr__(self, name, value):
        """Tries to set an attribute with the given on the fusion-onject on which
        this wrapper is wrapped around.

        Args:
            name: The name of the attribute to set.
            value: The value of the attribute to set.
        """
        # avoid infinite recursion by using self.__dict__ instead of self.hasattr
        if "_in_fusion" in self.__dict__.keys() and hasattr(self._in_fusion, name):
            setattr(self._in_fusion, name, value)
        else:
            super().__setattr__(name, value)

    # simply override the properties to use individual docstrings
    @property
    def parent(self):
        """The parent wrapper-instance of this wrapper-instance.

        Can be an List of wrapper-instances if multiple parents were provided
        (only for addincommand instances for now).
        """
        return self._parent

    @property
    def uiLevel(self):
        """The level this instance is in the user interface hierachy.

        For Example: Workspace is always level 1, Tab always level 2, ...
        """
        return self._ui_level

    @property
    def addin(self):
        """The addin instance which manages this instance."""
        return self._addin


class FusionAddin:

    _ui_level = 0

    def __init__(
        self,
        debugToUi: bool = True,
    ):
        """Entry point to create all your elements that will appear in the user interface.

        Handles the creation of UI elements and deletes them (by calling the stop method).

        Args:
            debug_to_ui (bool, optional): Flag indicating if erorr messages caused
                by errors in the eventhandlers are displayed in a `messageBox
                <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-1692a9a4-3be0-4474-9e15-02fac696b2b2>`_
                or not. Regardless of this flag all messages will get logged by
                the module logger. Defaults to True.
        """
        self._debug_to_ui = debugToUi

        self._registered_elements = defaultdict(list)

        # addin instances from other addins are also dtected so dont use
        # if len(_addins) > 0:
        #     logging.getLogger(__name__).warning(msgs.addin_exists())
        # _addins.append(self)

    def workspace(self, *args, **kwargs):
        """Creates a :class:`.Workspace` as a child of this Adddin.

        Calling this method is the same as initialsing a :class:`.Workspace`
        with this addin instance as parent parameters. Therfore the same parameters
        are passed. See :class:`.Workspace` for a detailed description of the paramters.

        Returns:
            Workspace: The newly created or accessed Workspace instance.
        """
        return Workspace(self, *args, **kwargs)

    def stop(self):
        """Stops the addin and deletes all created command and user interface
        related elements.

        This methods needs to get called from the stop(context) function of the
        main file of your addin to ensure proper cleanup.
        If you dont call it, strange thigs can happen the next time you run the addin.
        """
        for event, handler in handlers._custom_events_and_handlers:
            event.remove(handler)
            adsk.core.Application.get().unregisterCustomEvent(event.eventId)

        for level in reversed(sorted(list(self._registered_elements.keys()))):
            elems = self._registered_elements.pop(level)
            for elem in elems:
                try:
                    elem.deleteMe()
                except:
                    # element is probably already deleted
                    pass

    def registerElement(self, elem: _FusionWrapper, level: int = 0):
        """Registers an instance of a :class:`._FusionWrapper` to the addin.

        All wrapper objects that are registered will get deleted if the addin stops.
        The order of the deletion is determind by the level. Instances with a
        higher level will get deleted first.
        All elements that are created will be registered by the framework internally,
        so THERE IS NO NEED TO USE THIS METHOD in noraml use of the framework.

        Args:
            elem (_FusionWrapper): The wrapper instance to register.
            level (int, optional): The Ui level of the element. Defaults to 0.
        """
        if isinstance(elem, _FusionWrapper):  # TODO check if still necessary
            elem = elem._in_fusion  # pylint:disable=protected-access
        self._registered_elements[level].append(elem)

    # region
    @property
    def debugToUi(self) -> bool:
        """bool: Flag indicating if erorr messages are displayed in a `messageBox
        <http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-1692a9a4-3be0-4474-9e15-02fac696b2b2>`_
        or only send to the module logger.
        """
        return self._debug_to_ui

    @debugToUi.setter
    def debugToUi(self, new_debug_to_ui: bool):
        self._debug_to_ui = new_debug_to_ui

    @property
    def uiLevel(self) -> int:
        """int: The ui level ot the app. (Always 0)"""
        return self._ui_level

    @property
    def addin(self):  # do not use typehint --> doc generation will craah
        """FusionApp: Itself. Kept for consistency with the other wrapper classes."""
        return self

    @property
    def createdElements(self):  # -> Dict[int, List[FusionApp]]:
        """Dict[int, List[FusionApp]]: A dictonary with all the created ui elemnts mapped by their ui level."""
        return self._registered_elements

    # endregion


class Workspace(_FusionWrapper):
    def __init__(
        self,
        parent: FusionAddin = None,
        id: str = "FusionSolidEnvironment",
        name: str = "random",
        productType: str = "DesignProductType",
        resourceFolder: Union[str, Path] = "lightbulb",
        toolClipFilename: Union[str, Path] = "lightbulb",
        tooltip: str = "",
        tooltipDescription: str = "",
    ):
        """Wraps around Fusions `Workspace
        <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-33f9ed37-e5c7-4153-ba85-c3254a199dd1>`_
        object.
        Besides the documented attributes and methods on this page all
        attributes and methods of the wrapped class can be accessed with the same
        attribute and method names as in the wrapped class.

        If an Id of an existing workspace is provided, all parameters except
        `parent` and `id` will be ignored.

        It is currently not possible to create a custom workspace via
        the API. This seems like a bug in Fusion360s API.
        Therfore you need to use a ID of an native workspace.
        If you have any information on this please answer `this
        <https://forums.autodesk.com/t5/fusion-360-api-and-scripts/custom-workspace-is-not-visible/m-p/10278987>`_
        forum post.

        Args:
            parent (FusionAddin): The parental addin instance. Defaults to an addin with
                the default values.
            id (str, optional): The id of the workspace. Defaults to "FusionSolidEnvironment".
            productType (str, optional): The name of the product this workspace
                is associated with. Defaults to "DesignProductType".
            resourceFolder (Union[str, Path], optional): The resource folder
                should contain two files; 49X31.png and 98x62.png. The larger is
                used for the Apple Retina display. Alternatively you can provide
                the name of one of the available default images. Defaults to "lightbulb".
            toolClipFilename (Union[str, Path], optional): The full filename of
                the image file (png) used for the tool clip. The tool clip is the
                image shown when the user hovers the mouse over the workspace name
                in the workspace drop-down. Alternatively you can provide
                the name of one of the available default images. Defaults to "lightbulb".
            tooltip (str, optional): Tooltip text displayed for the workspace.
                This is the first line of text shown when the user hovers over the
                workspace name in the Fusion 360 toolbar drop-down. Defaults to "".
            tooltipDescription (str, optional): The tooltip description displayed
                for the workspace. The tooltip description is a longer description
                of the workspace and is only displayed when the user hovers over
                the workspace name in the Fusion 360 toolbar drop-down. Defaults to "".
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

            self.addin.registerElement(self, self.uiLevel)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def tab(self, *args, **kwargs):
        """Creates a :class:`.Tab` as a child of this workspace.

        Calling this method is the same as initialsing a :class:`.Tab`
        with this workspace instance as parent parameters. Therefore the same
        parameters are passed. See :class:`.Tab` for a detailed description
        of the paramters.

        Returns:
            Tab: The newly created or accessed tab instance.
        """
        return Tab(self, *args, **kwargs)


class Tab(_FusionWrapper):
    def __init__(
        self,
        parent: Workspace = None,  # TODO mulitple parents
        id: str = "default",
        name: str = "random",
    ):
        """Wraps around Fusions `Tab
        <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-7AF58337-178C-467C-831F-285B0FB02D56>`_
        object.
        Besides the documented attributes and methods on this page all
        attributes and methods of the wrapped class can be accessed with the same
        attribute and method names as in the wrapped class.

        If an Id of an existing Tab is provided, all parameters except `parent` and
        `id` will be ignored.

        Args:
            parent (Workspace, optional): The parent workspace which contains this
                tab. Defaults to a Workspace with the default parameters.
            id (str, optional): The id of the Tab. Defaults to "ToolsTab" in DesignWorkspace,
                to "UtilitiesTab" in CAMWorkspace and "RenderTab" in RenderWorkspace.
            name (str, optional): The name of the tab as seen in the user interface.
                Defaults to a random name.
        """
        super().__init__(parent, Workspace)

        id = dflts.eval_id(id, self)
        name = dflts.eval_name(name, __class__)

        self._in_fusion = self.parent.toolbarTabs.itemById(id)

        if self._in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisiting(__class__, id))
        else:
            self._in_fusion = self.parent.toolbarTabs.add(id, name)

            self.addin.registerElement(self, self.uiLevel)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def panel(self, *args, **kwargs):
        """Creates a :class:`.Panel` as a child of this tab.

        Calling this method is the same as initialsing a :class:`.Panel`
        with this tab instance as parent parameters. Therefore the same
        parameters are passed. See :class:`.Panel` for a detailed description
        of the paramters.

        Returns:
            Panel: The newly created or accessed panel instance.
        """
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
        """Wraps around the `Panel
        <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-0ca48ac9-da95-4623-bf87-150f3729717a>`_
        object.
        Besides the documented attributes and methods on this page all
        attributes and methods of the wrapped class can be accessed with the same
        attribute and method names as in the wrapped class.

        If an Id of an existing Panel is provided, all parameters except `parent` and
        `id` will be ignored.

        Args:
            parent (Tab, optional): The parent tab which contains this
                panel. Defaults to a panel with the default parameters.
            name (str, optional): The name of the tab as seen in the user interface.
                Defaults to a random name.
            positionID (str, optional): Specifies the id of the panel to position
                this panel relative to. Not setting this value indicates that the
                panel will be created at the end of all other panels. The isBefore
                parameter specifies whether to place the panel before or after this
                panel. Defaults to "".
            isBefore (bool, optional): Specifies whether to place the panel before
                or after the panel specified by the positionID argument. This
                argument is ignored is positionID is not specified. Defaults to True.
        """
        super().__init__(parent, Tab)

        id = dflts.eval_id(id, self)
        name = dflts.eval_name(name, __class__)

        # TODO test what wil happen if ui.allToolbarpanels.itemById() already exists
        self._in_fusion = self.parent.toolbarPanels.itemById(id)

        if self._in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisiting(__class__, id))
        else:
            self._in_fusion = self.parent.toolbarPanels.add(
                id, name, positionID, isBefore
            )

            self.addin.registerElement(self, self.uiLevel)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    # region
    # def button(self, *args, **kwargs):
    #     """[summary]

    #     Returns:
    #         [type]: [description]
    #     """
    #     return Button(self, *args, **kwargs)

    # def checkbox(self, *args, **kwargs):
    #     """[summary]

    #     Returns:
    #         [type]: [description]
    #     """
    #     return Checkbox(self, *args, **kwargs)

    # def list_control(self, *args, **kwargs):
    #     """[summary]

    #     Returns:
    #         [type]: [description]
    #     """
    #     return ListControl(self, *args, **kwargs)
    # endregion

    def control(self, *args, **kwargs):
        """Creates a :class:`.Control` as a child of this panel.

        Calling this method is the same as initialsing a :class:`.Control`
        with this panel instance as parent parameter. Therefore the same
        parameters are passed. See :class:`.Control` for a detailed description
        of the paramters.

        Returns:
            Control: The newly created or accessed Control instance.
        """
        return Control(self, *args, **kwargs)

    def dropdown(self, *args, **kwargs):
        """Creates a :class:`.Dropdown` as a child of this panel.

        Calling this method is the same as initialsing a :class:`.Dropdown`
        with this panel instance as parent parameter. Therefore the same
        parameters are passed. See :class:`.Dropdown` for a detailed description
        of the paramters.

        Returns:
            Dropdown: The newly created or accessed Dropdown instance.
        """
        return Dropdown(self, *args, **kwargs)


class Dropdown(_FusionWrapper):
    def __init__(
        self,
        parent: Union["Dropdown", Panel] = None,
        id: str = "random",
        text: str = "random",
        resourceFolder: str = "lightbulb",
        positionID: str = "",
        isBefore: str = True,
        isVisible: bool = True,
    ):
        """Wraps around Fusions `Dropdown
        <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-47de53a5-90f0-4d3c-9eee-3fc16d794014>`_
        object.
        Besides the documented attributes and methods on this page all
        attributes and methods of the wrapped class can be accessed with the same
        attribute and method names as in the wrapped class.

        If an Id of an existing Dropdown is provided, all parameters except `parent`
        and `id` will be ignored.

        Args:
            parent (Union[Dropdown, Panel], optional): The parent panel or dropdown
                where this dropdoen is added to. Defaults to None.
            id (str, optional): The id of this dropdwown. Defaults to a random id.
            text (str, optional): The text displayed for the drop-down in a menu.
                For a drop-down in a toolbar this argument is ignored because an
                icon is used. Defaults to a random text.
            resourceFolder (str, optional): The resource folder containing the
                image used for the icon when the drop-down is in a toolbar.
                Defaults to "lightbulb".
            positionID (str, optional): Specifies the reference id of the control
                to position this control relative to. Not setting this value indicates
                that the control will be created at the end of all other controls
                in toolbar. The isBefore parameter specifies whether to place the
                control before or after the reference control.
            isBefore (str, optional): Specifies whether to place the control before
                or after the reference control specified by the positionID parameter.
                This argument is ignored is positionID is not specified. Defaults to True.
            isVisible (bool, optional): Sets if this dropdown is currently visible.
                Defaults to True.
        """
        super().__init__(parent, Panel)

        id = dflts.eval_id(id)
        text = dflts.eval_name(text, __class__)
        resourceFolder = dflts.eval_image(resourceFolder)

        self._in_fusion = self.parent.controls.itemById(id)

        if self._in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisiting(__class__, id))
        else:
            self._in_fusion = self.parent.controls.addDropDown(
                text, resourceFolder, id, positionID, isBefore
            )
            self._in_fusion.isVisible = isVisible
            self.addin.registerElement(self, self.uiLevel)
            logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def control(self, *args, **kwargs):
        """Creates a :class:`.Control` as a child of this workspace.

        Calling this method is the same as initialsing a :class:`.Control`
        with this panel instance as parent parameter. Therefore the same
        parameters are passed. See :class:`.Control` for a detailed description
        of the paramters.

        Returns:
            Control: The newly created or accessed Control instance.
        """
        return Control(self, *args, **kwargs)

    def dropdown(self, *args, **kwargs):
        """Creates a :class:`.Dropdown` as a child of this panel.

        Calling this method is the same as initialsing a :class:`.Dropdown`
        with this panel instance as parent parameter. Therefore the same
        parameters are passed. See :class:`.Dropdown` for a detailed description
        of the paramters.

        Returns:
            Dropdown: The newly created or accessed Dropdown instance.
        """
        return Dropdown(self, *args, **kwargs)


class Control(_FusionWrapper):
    def __init__(
        self,
        parent: Union[Panel, Dropdown] = None,  # TODO allow multiple parents ?!
        controlType: str = "button",
        isVisible: bool = True,
        isPromoted: bool = False,
        isPromotedByDefault: bool = False,
        positionID: int = "",
        isBefore: bool = True,
    ):
        """Wraps around Fusions `CommandControl
        <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-bb8d8c7b-3049-40c9-b7a5-76d24a462327>`_
        object.
        Besides the documented attributes and methods on this page all
        attributes and methods of the wrapped class can be accessed with the same
        attribute and method names as in the wrapped class.

        Note that in contrast to the usage of the 'orignal' API a commandDefintion
        is *not* needed to initialize the commandControl. Instead a commandDefintion
        can be added as a children of the commandControl by using the :class:`.AddinCommand`
        wrapper. If no commandDefintion is provided a dummy defintion is used
        which doesnt have any functionality connected to its command.
        Depending on the passed `controlType` attribute the ControlDefinition of
        the commandDefintion child will be determined.

        Args:
            parent (Union[Panel, Dropdown], optional): The parent panel or dropdown which
                contains this control. Defaults to a Panel with the default properties.
            controlType (str, optional): The kind of control which is used to activate the
                associated command. Possible options are "button", "checkbox" or "list".
                Only "button" control type can be used in the panel directly.
                Therefore you should set the isPromoted and isPromotedByDefault
                to False ff you use a checkbox or list. Otherwise an additional
                button which has no functionality will be created.
                This is caused by the somewhat misleading behavior of the Fusion API.
                Defaults to "button".
            isVisible (bool, optional): Sets if this control is currently visible. Defaults to True.
            isPromoted (bool, optional): Sets if this command has been promoted to the parent panel.
                This property is ignored in the case where this controls parent isn't a panel.
                Defaults to False.
            isPromotedByDefault (bool, optional): Sets if this command is a default command in the panel.
                This defines the default state of the panel if the UI is reset.
                This property is ignored in the case where this control isn't in a panel.
                Defaults to False.
            positionID (int, optional): Specifies the reference id of the control to position this
                control relative to. Not setting this value indicates that the
                control will be created at the end of all other controls in toolbar.
                The isBefore parameter specifies whether to place the control before
                or after the reference control.
            isBefore (bool, optional): Specifies whether to place the control before or after
                the reference control specified by the positionID parameter. This
                argument is ignored is positionID is not specified. Defaults to True.
        """
        super().__init__(parent, Panel)

        self._isVisible = isVisible
        # if controlType != "button" or isinstance(parent, Dropdown):
        #     isPromoted = False
        #     isPromotedByDefault = False
        self._isPromoted = isPromoted
        self._isPromotedByDefault = isPromotedByDefault
        self._positionID = positionID
        self._isBefore = isBefore

        # create a dummy control so a control is displayed in the UI even if no
        # command was created
        if controlType == "button":
            dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
                str(uuid4()),
                "<no command connected>",
                "",
                dflts.eval_image("transparent"),
            )
        elif controlType == "checkbox":
            dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addCheckBoxDefinition(
                str(uuid4()),
                "<no command connected>",
                "",
                False,
            )
            dummy_cmd_def.controlDefinition.isChecked = False
        elif controlType == "list":
            dummy_cmd_def = adsk.core.Application.get().userInterface.commandDefinitions.addListDefinition(
                str(uuid4()),
                "<no command connected>",
                adsk.core.ListControlDisplayTypes.RadioButtonlistType,
            )
            dummy_cmd_def.controlDefinition.listItems.add("<empty list>", False)
        else:
            raise ValueError(msgs.invalid_control_type(controlType))

        dummy_cmd_def.controlDefinition.isVisible = True
        dummy_cmd_def.controlDefinition.isEnabled = True
        dummy_cmd_def.controlDefinition.name = "<no command connected>"
        # do not connect a handler since its a dummy cmd_def

        self.addin.registerElement(dummy_cmd_def, self.uiLevel + 1)

        self._create_control(dummy_cmd_def)

        logging.getLogger(__name__).info(msgs.created_new(__class__, None))

    def _create_control(self, cmd_def):
        """Creates a control with the properties that are passed at the initialization
        of the class and the given command defintion.
        If a control already has been created (like the dummy command defintion control)
        the previous control will be deleted first.
        The control will be (re)registered to the parent addin instance.

        Args:
            cmd_def (adsk.fusion.CommandDefinition): The command definition object for
                which will be used to create the control in the user interface.
        """
        # to delete the control created by the dummy definition
        if self._in_fusion is not None:
            self._in_fusion.deleteMe()

        # create the control itself with the passed cmd def and the attributs from
        # the init call
        self._in_fusion = self.parent.controls.addCommand(
            cmd_def, self._positionID, self._isBefore
        )

        self._in_fusion.isPromoted = self._isPromoted
        self._in_fusion.isPromotedByDefault = self._isPromotedByDefault
        self._in_fusion.isVisible = self._isVisible

        self.addin.registerElement(self, self.uiLevel)

    def addinCommand(self, *args, **kwargs):
        """Creates a :class:`.AddinCommand` as a child of this Control.

        Calling this method is the same as initialsing a :class:`.AddinCommand`
        with this Control instance as parent parameter. Therefore the same
        parameters are passed. See :class:`.AddinCommand` for a detailed description
        of the paramters.

        Returns:
            AddinCommand: The newly created or accessed AddinCommand instance.
        """
        return AddinCommand(self, *args, **kwargs)


# region
# class Button(CommandControl):
#     def __init__(
#         self,
#         parent: Panel = None,
#         isVisible: bool = True,
#         isPromoted: bool = True,
#         isPromotedByDefault: bool = True,
#         positionID: str = None,
#         isBefore: bool = True,
#     ):
#         """[summary]

#         Args:
#             parent (Panel, optional): [description]. Defaults to None.
#             isVisible (bool, optional): [description]. Defaults to True.
#             isPromoted (bool, optional): [description]. Defaults to True.
#             isPromotedByDefault (bool, optional): [description]. Defaults to True.
#             positionID (str, optional): [description]. Defaults to None.
#             isBefore (bool, optional): [description]. Defaults to True.
#         """
#         super().__init__(
#             parent,
#             "button",
#             isVisible,
#             isPromoted,
#             isPromotedByDefault,
#             positionID,
#             isBefore,
#         )


# class Checkbox(CommandControl):
#     def __init__(
#         self,
#         parent: Panel = None,
#         isVisible: bool = True,
#         isPromoted: bool = True,
#         isPromotedByDefault: bool = True,
#         positionID: str = None,
#         isBefore: bool = True,
#     ):
#         """[summary]

#         Args:
#             parent (Panel, optional): [description]. Defaults to None.
#             isVisible (bool, optional): [description]. Defaults to True.
#             isPromoted (bool, optional): [description]. Defaults to True.
#             isPromotedByDefault (bool, optional): [description]. Defaults to True.
#             positionID (str, optional): [description]. Defaults to None.
#             isBefore (bool, optional): [description]. Defaults to True.
#         """
#         super().__init__(
#             parent,
#             "checkbox",
#             isVisible,
#             isPromoted,
#             isPromotedByDefault,
#             positionID,
#             isBefore,
#         )


# class ListControl(CommandControl):
#     def __init__(
#         self,
#         parent: Panel = None,
#         isVisible: bool = True,
#         isPromoted: bool = True,
#         isPromotedByDefault: bool = True,
#         positionID: str = None,
#         isBefore: bool = True,
#     ):
#         """[summary]

#         Args:
#             parent (Panel, optional): [description]. Defaults to None.
#             isVisible (bool, optional): [description]. Defaults to True.
#             isPromoted (bool, optional): [description]. Defaults to True.
#             isPromotedByDefault (bool, optional): [description]. Defaults to True.
#             positionID (str, optional): [description]. Defaults to None.
#             isBefore (bool, optional): [description]. Defaults to True.
#         """
#         super().__init__(
#             parent,
#             "list",
#             isVisible,
#             isPromoted,
#             isPromotedByDefault,
#             positionID,
#             isBefore,
#         )
# endregion


class AddinCommand(_FusionWrapper):
    def __init__(
        self,
        parent: Union[Control, List[Control]] = None,
        id: str = "random",
        name: str = "random",
        resourceFolder: Union[str, Path] = "lightbulb",
        tooltip: str = "",
        toolClipFileName: Union[str, Path] = None,
        isEnabled: bool = True,
        isVisible: bool = True,
        isChecked: bool = True,  # only checkbox
        listControlDisplayType: int = adsk.core.ListControlDisplayTypes.RadioButtonlistType,  # only list
        customEventHandlers: Dict[str, Callable] = None,
        **eventHandlers: Callable,
    ):
        """Wraps around Fusions `CommandDefinition
        <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-5e5a72e2-0869-4f85-936f-eab4ebd4aced>`_
        object and its `ControlDefintion
        <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-f4282920-9484-49db-bcdd-b46f6506543d>`_
        attribute.
        Besides the documented attributes and methods on this page all
        attributes and methods of the wrapped classes can be accessed with the same
        attribute and method names as in the wrapped classes.
        The atributes of the commandDefintion object will be looked up first.

        This class does NOT wrap around Fusions `Command
        <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-0550963a-ff63-4183-b0a7-a1bf0c99f821>`_
        class.
        (Thats why its called 'AddinCommand' and not 'Command' only.)

        If an Id of an existing CommandDefintion is provided, all parameters except
        `parent` and `id` will be ignored.

        This class also encapsulates the concepts of the `event handlers
        <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID->`_
        of the Fusion API.
        Using this class you do not need to connect a handler to the `created event
        <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-895ee146-8697-4ba0-98e7-4f72b74edb4f>`_
        of the commandDefintion.
        Instead of connecting handlers, you simply pass a function as an arguments
        to this wrapper class.
        The argument name must correspond to a event name of Fusions `Command
        <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-0550963a-ff63-4183-b0a7-a1bf0c99f821>`_
        class or 'commandCreated' for the `commandCreatedEventHandler`.
        The passed function will get executed as the notify method of the corresponding
        handler. Also the same argument will get passed to this function
        (e.g. `CommandCreatedEventArgs
        <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-97617dc7-d815-4b05-ac50-8880afe8937b>`_
        for a function passed to the argument `onCommandCreated`).
        Therfore the signature of the passed (notify-)functions must accept exactly
        one positional argument (which can be used within the fucntion).

        See the example section for some use cases.
        Checking out the examples should make the concept od using function-arguments
        instead of handlers understandable in no time.

        Args:
            parent (Union[Control, List[Control]], optional): The parent Control
                this command is connected to. You can also pass a list of controls.
                In this case the same command/functionality getx connected to multiple
                controls. If a list of controls is passed you must ensure that all
                controls are of the same controlType and that all of them are in
                distinct panels. Defaults to a ComanndControl with the default
                properties.
            id (str, optional): The unique id of the commandDefintion with respect
                to all other existing commandDefintions. Defaults to a random id.
            name (str, optional): The visible name of the command as seen in the
                user interface. This will also be set as the name of the controlDefintione
                attribute. Defaults to a random name.
            resourceFolder (Union[str, Path], optional): Directory that contains
                any additional files associated with this command. These are
                typically the image files that will be used for a button and the
                HTML files for a tool clip or helps and tips. Alternatively you
                can provide the name of one of the available default images.
                Defaults to "lightbulb".
            tooltip (str, optional): The tooltip string. This is always shown
                for commands. If the tooltip description and/or tool clip are also
                specified then the tooltip will progressively display more information
                as the user hovers the mouse over the control. Defaults to "".
            toolClipFileName (Union[str, Path], optional): The full filename of
                the image file (PNG) used for the tool clip. The tooltip is always
                shown but as the user hovers over the control it will progressively
                display the tool clip along with the tooltip text. Alternatively you
                can provide the name of one of the available default images.
                Defaults to None (no toolclip image is used).
            isEnabled (bool, optional): Sets if this ControlDefinition is enabled
                or not. This has the effect of enabling and disabling any
                associated (parental) controls. Defaults to True.
            isVisible (bool, optional): Sets if this ControlDefinition is visible
                or not. This has the effect of making any associated (parental)
                controls visible or invisible in the user interface. Defaults to True.
            isChecked (bool, optional): Will be ignored if controlType of the parental
                Control is not 'checkbox'. Sets whether the check box of the parental
                controlDefintions is checked. Changing this will result in changing
                any associated (parental) controls and will execute the associated
                command. Defaults to True.
            listControlDisplayType (int, optional): Will be ignored if the controlType
                of the paerntal Control is not 'list'. Sets how the parental list
                control will be displayed; as a standard list, a list of check boxes,
                or a list of radio buttons. Possible Values can be found in
                the `ListControlDisplayType
                <https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-3b2f79e4-2b1b-4bc9-8632-d3b6fe1fc421>`_
                enumerator. Defaults to RadioButtonListType (1).
        """
        super().__init__(parent, Control)

        if not isinstance(self._parent, list):
            parent_list = [self._parent]
        else:
            parent_list = self._parent

        if customEventHandlers is None:
            customEventHandlers = {}

        id = dflts.eval_id(id)
        name = dflts.eval_name(name, __class__)
        resourceFolder = dflts.eval_image(resourceFolder)
        toolClipFileName = dflts.eval_image(toolClipFileName, "32x32.png")

        self._in_fusion = (
            adsk.core.Application.get().userInterface.commandDefinitions.itemById(id)
        )

        if self._in_fusion:
            logging.getLogger(__name__).info(msgs.using_exisiting(__class__, id))

        else:
            # create definition depending on the parent(s) control type
            parent_control_type = parent_list[
                0
            ].commandDefinition.controlDefinition.objectType

            if parent_control_type == adsk.core.ButtonControlDefinition.classType():
                self._in_fusion = adsk.core.Application.get().userInterface.commandDefinitions.addButtonDefinition(
                    id,
                    name,
                    tooltip,
                    resourceFolder,
                )
            elif parent_control_type == adsk.core.CheckBoxControlDefinition.classType():
                self._in_fusion = adsk.core.Application.get().userInterface.commandDefinitions.addCheckBoxDefinition(
                    id,
                    name,
                    tooltip,
                    isChecked,
                )
            elif parent_control_type == adsk.core.ListControlDefinition.classType():
                self._in_fusion = adsk.core.Application.get().userInterface.commandDefinitions.addListDefinition(
                    id,
                    name,
                    listControlDisplayType,
                    resourceFolder,
                )
            else:
                raise ValueError(msgs.invalid_control_type(parent_control_type))

            if toolClipFileName is not None:
                self._in_fusion.toolClipFilename = toolClipFileName
            self._in_fusion.tooltip = tooltip
            self._in_fusion.resourceFolder = resourceFolder
            self._in_fusion.controlDefinition.isEnabled = isEnabled
            self._in_fusion.controlDefinition.isVisible = isVisible
            self._in_fusion.controlDefinition.name = name

            # maybe move handler dict sanitation here
            # not done yet because handler type mapping in handlers.py
            # move when reconnecting handlers is implemented

            # ! if there is some error (typo) etc. fusion will break instantanious !
            self._in_fusion.commandCreated.add(
                handlers._CommandCreatedHandler(  # pylint:disable=protected-access
                    self.addin, name, eventHandlers
                )
            )

            # register custom events
            for event_id, handler_notify in customEventHandlers.items():
                custom_event = adsk.core.Application.get().registerCustomEvent(event_id)
                custom_handler = handlers._CustomEventHandler(
                    self.addin, name, custom_event, handler_notify
                )
                custom_event.add(custom_handler)

            self.addin.registerElement(self, self.uiLevel)

        for p in parent_list:
            p._create_control(self._in_fusion)  # pylint:disable=protected-access

        logging.getLogger(__name__).info(msgs.created_new(__class__, id))

    def addParentControl(self, parentControl):
        """Adds an additional control for acticvating this command.

        The control should be of the same control type as the other controls of
        this command.

        Args:
            parent (Control): The additional control for the command.
        """
        parentControl._create_control(  # pylint:disable=protected-access
            self._in_fusion
        )
        if not isinstance(self._parent, list):
            self._parent = [self._parent]
        self._parent.append(parentControl)

    def __getattr__(self, attr):
        """Tries to find the attribute in the commandDefintion object first and
        in the commandDefintion.controlDefintion object second on which this class
        is wrapped around.
        This will only get called if no attribute is found in the AddinCommand
        wrapper object itself.

        Args:
            attr: The attribute name.

        Returns:
            Any: The attribute value.
        """
        if hasattr(self._in_fusion, attr):
            return getattr(self._in_fusion, attr)
        else:  # hasattr(self._in_fusion.controlDefinition, attr):
            return getattr(self._in_fusion.controlDefinition, attr)

    def __setattr__(self, name, value):
        """Tries to set an attribute on the commandDefintion first and on the
        commandDefintion.controlDefintion object second on which this wrapper is
        wrapped around.
        If the attribute is not found it will be set on the wrapper object.

        Args:
            name: The name of the attribute to set.
            value: The value of the attribute to set.
        """
        # avoid infinite recursion by using self.__dict__ instead of self.hasattr
        if "_in_fusion" in self.__dict__.keys() and self._in_fusion is not None:
            if hasattr(self._in_fusion, name):
                setattr(self._in_fusion, name, value)
            elif hasattr(self._in_fusion.controlDefinition, name):
                setattr(self._in_fusion.controlDefinition, name, value)
            else:
                super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)
