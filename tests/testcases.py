"""Testcases 
All testcases are functions which start with test_ by convention.
No testing framework like pytest is used as the tests work directly on the API functionalities which are in 
general hard to mock.
The functionality for clean up, evaluation and summarizing is done from the fusion_addin_framework.py
file which is the entry point for testing.
"""

from uuid import uuid4
import random

import adsk.fusion, adsk.core

from .. import fusion_addin_framework as faf


def test_hello_world_button_normal():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(ws)
    panel = faf.Panel(tab)
    button = faf.Control(panel)
    cmd = faf.AddinCommand(
        button,
        execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
            "hello world"
        ),
    )


def test_hello_world_button_dotted():
    addin = faf.FusionAddin()
    cmd = (
        addin.workspace()
        .tab()
        .panel()
        .control()
        .addinCommand(
            execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            ),
        )
    )


def test_hello_world_button_defaults():
    cmd = faf.AddinCommand(
        execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
            "hello world"
        )
    )


def test_checkbox_normal():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(ws)
    panel = faf.Panel(tab)
    checkbox = faf.Control(panel, controlType="checkbox")
    cmd = faf.AddinCommand(
        checkbox,
        execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
            "hello world"
        ),
    )


def test_checkbox_dotted():
    addin = faf.FusionAddin()
    cmd = (
        addin.workspace()
        .tab()
        .panel()
        .control(controlType="checkbox")
        .addinCommand(
            execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            ),
        )
    )


def test_checkbox_defaults():
    checkbox = faf.Control(controlType="checkbox")
    cmd = faf.AddinCommand(
        checkbox,
        execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
            "hello world"
        ),
    )


# region
# def test_list_normal():
#     addin = faf.FusionAddin()
#     ws = faf.Workspace(addin)
#     tab = faf.Tab(ws)
#     panel = faf.Panel(tab)
#     checkbox = faf.Control(panel, controlType="list")
#     cmd = faf.AddinCommand(
#         checkbox,
#         execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
#             "hello world"
#         ),
#     )

# def test_list_dotted():
#    faf.FusionAddin()
#     cmd = (
#         addin.workspace()
#         .tab()
#         .panel()
#         .control(controlType="list")
#         .addinCommand(
#             execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
#                 "hello world"
#             ),
#         )
#     )

# def test_list_defaults():
#     list_ctrl = faf.Control(controlType="list")
#     cmd = faf.AddinCommand(
#         list_ctrl,
#         execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
#             "hello world"
#         ),
#     )
# endregion


def test_standard_attrs_button():
    cmd = (
        faf.FusionAddin(debugToUi=True)
        .workspace(
            id="FusionSolidEnvironment",
            name="random",
            productType="DesignProductType",
            resourceFolder="lightbulb",
            toolClipFilename="lightbulb",
            tooltip="",
            tooltipDescription="",
        )
        .tab(
            id="default",
            name="random",
        )
        .panel(
            id="default",
            name="random",
            positionID="",
            isBefore=True,
        )
        .control(
            controlType="button",
            isVisible=True,
            isPromoted=True,
            isPromotedByDefault=True,
            positionID="",
            isBefore=True,
        )
        .addinCommand(
            id="random",
            name="random",
            resourceFolder="lightbulb",
            tooltip="",
            toolClipFileName=None,
            isEnabled=True,
            isVisible=True,
            isChecked=True,
            execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            ),
        )
    )


def test_very_custom_button():
    addin = faf.FusionAddin(debugToUi=True)
    ws = faf.Workspace(
        addin,
        id="FusionSolidEnvironment",
        name="my test name",
        productType="DesignProductType",
        resourceFolder=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/test_images/one",
        toolClipFilename=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one/32x32.png",
        tooltip="my test tooltip",
        tooltipDescription="my test tooltip description",
    )
    tab = faf.Tab(
        ws,
        id="my test tab id",
        name="my name",
    )
    panel = faf.Panel(
        tab,
        id="mytestpanelid",
        name="my panels name",
        positionID="",
        isBefore=True,
    )
    ctrl = faf.Control(
        panel,
        controlType="button",
        isVisible=True,
        isPromoted=True,
        isPromotedByDefault=True,
        positionID="",
        isBefore=True,
    )
    cmd = faf.AddinCommand(
        ctrl,
        id="mycustomcmdid",
        name="ma command",
        resourceFolder=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one",
        tooltip="my custom tooltip",
        toolClipFileName=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one/32x32.png",
        isEnabled=True,
        isVisible=True,
        isChecked=True,
        execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
            "hello world"
        ),
    )


def test_very_custom_checkbox():
    addin = faf.FusionAddin(debugToUi=True)
    ws = faf.Workspace(
        addin,
        id="FusionSolidEnvironment",
        name="my test name",
        productType="DesignProductType",
        resourceFolder=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one",
        toolClipFilename=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one/32x32.png",
        tooltip="my test tooltip",
        tooltipDescription="my test tooltip description",
    )
    tab = faf.Tab(
        ws,
        id="my test tab id",
        name="my name",
    )
    panel = faf.Panel(
        tab,
        id="mytestpanelid",
        name="my panels name",
        positionID="",
        isBefore=True,
    )
    ctrl = faf.Control(
        panel,
        controlType="checkbox",
        isVisible=True,
        isPromoted=False,
        isPromotedByDefault=False,
        positionID="",
        isBefore=True,
    )
    cmd = faf.AddinCommand(
        ctrl,
        id="mycustomcheckboxcmdid",
        name="ma command",
        resourceFolder=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one",
        tooltip="my custom tooltip",
        toolClipFileName=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one/32x32.png",
        isEnabled=True,
        isVisible=True,
        isChecked=True,
        execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
            "hello world"
        ),
    )


# region
# def test_very_custom_list():
#         addin = faf.FusionAddin(debugToUi=True)
#         ws = faf.Workspace(
#             addin,
#             id="FusionSolidEnvironment",
#             name="my test name",
#             productType="DesignProductType",
#             resourceFolder=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one",
#             toolClipFilename=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one/32x32.png",
#             tooltip="my test tooltip",
#             tooltipDescription="my test tooltip description",
#         )
#         tab = faf.Tab(
#             ws,
#             id="my test tab id",
#             name="my name",
#         )
#         panel = faf.Panel(
#             tab,
#             id="mytestpanelid",
#             name="my panels name",
#             positionID="",
#             isBefore=True,
#         )
#         ctrl = faf.Control(
#             panel,
#             controlType="list",
#             isVisible=True,
#             isPromoted=True,
#             isPromotedByDefault=True,
#             positionID="",
#             isBefore=True,
#         )
#         cmd = faf.AddinCommand(
#             ctrl,
#             id="mycustomlistcmdid",
#             name="ma command",
#             resourceFolder=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one",
#             tooltip="my custom tooltip",
#             toolClipFileName=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one/32x32.png",
#             isEnabled=True,
#             isVisible=True,
#             isChecked=True,
#             execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
#                 "hello world"
#             ),
#         )
# endregion


def test_addin_properties():
    addin = faf.FusionAddin(debugToUi=False)
    assert addin.debugToUi == False
    addin.debugToUi = True
    assert addin.debugToUi == True
    assert addin.uiLevel == 0


def test_workspace_properties():
    addin = faf.FusionAddin()
    ws = faf.Workspace(
        addin,
        id="FusionSolidEnvironment",  # TODO test custom ws with posix path
        name="my test name",
        productType="DesignProductType",
        resourceFolder=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one",
        toolClipFilename=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one/32x32.png",
        tooltip="my test tooltip",
        tooltipDescription="my test tooltip description",
    )
    print(ws.parent)
    print(ws.addin)
    assert ws.uiLevel == 1

    assert ws.id == "FusionSolidEnvironment"
    print(ws.isActive)
    assert ws.isNative == True
    assert ws.isValid == True
    print(ws.name)
    print(ws.objectType)
    assert ws.productType == "DesignProductType"
    print(ws.toolbarPanels)
    print(ws.toolbarTabs)
    print(ws.resourceFolder)
    print(ws.toolClipFilename)
    print(ws.tooltip)
    print(ws.tooltipDescription)
    # no setable attributes

    print(ws.activate)
    print(ws.deleteMe)
    print(ws.classType())


def test_tab_properties():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(
        ws,
        id="test_tab_properties_tab_id",
        name="my name",
    )
    print(tab.parent)
    print(tab.addin)
    assert tab.uiLevel == 2

    assert tab.id == "test_tab_properties_tab_id"
    print(tab.index)
    print(tab.isActive)
    assert tab.isNative == False
    assert tab.isValid == True
    print(tab.isVisible)
    assert tab.name == "my name"
    print(tab.objectType)
    print(tab.parentUserInterface)
    assert tab.productType == "DesignProductType"
    print(tab.toolbarPanels)
    # no setable attributes

    print(tab.activate)
    print(tab.deleteMe)
    print(tab.classType())


def test_panel_properties():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(ws)
    panel = faf.Panel(
        tab,
        id="test_panel_properties_panel_id",
        name="my panels name",
        positionID="",
        isBefore=True,
    )
    print(panel.parent)
    print(panel.addin)
    assert panel.uiLevel == 3

    print(panel.controls)
    assert panel.id == "test_panel_properties_panel_id"
    assert panel.isValid == True
    print(panel.isVisible)
    assert panel.name == "my panels name"
    print(panel.objectType)
    print(panel.parentUserInterface)
    assert panel.productType == "DesignProductType"
    print(panel.promotedControls)
    print(panel.relatedWorkspaces)
    # no setable attributes

    print(panel.classType())
    print(panel.deleteMe)
    print(panel.indexWithinTab)


def test_button_properties():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(ws)
    panel = faf.Panel(tab)
    button = faf.Control(
        panel,
        controlType="button",
        isVisible=True,
        isPromoted=True,
        isPromotedByDefault=True,
        positionID="",
        isBefore=True,
    )
    print(button.parent)
    print(button.addin)
    assert button.uiLevel == 4

    print(button.commandDefinition)
    print(button.id)
    assert button.isPromoted == True
    button.isPromoted = False
    assert button.isPromoted == False
    assert button.isPromotedByDefault == True
    button.isPromotedByDefault = False
    assert button.isPromotedByDefault == False
    assert button.isValid == True
    print(button.isVisible)
    print(button.objectType)
    print(button.parent)

    print(button.classType())
    print(button.deleteMe)

    assert (
        button.commandDefinition.controlDefinition.objectType
        == adsk.core.ButtonControlDefinition.classType()
    )


def test_checkbox_properties():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(ws)
    panel = faf.Panel(tab)
    checkbox = faf.Control(
        panel,
        controlType="checkbox",
        isVisible=True,
        isPromoted=True,
        isPromotedByDefault=True,
        positionID="",
        isBefore=True,
    )
    print(checkbox.parent)
    print(checkbox.addin)
    assert checkbox.uiLevel == 4

    print(checkbox.commandDefinition)
    print(checkbox.id)
    assert checkbox.isPromoted == True
    checkbox.isPromoted = False
    assert checkbox.isPromoted == False
    assert checkbox.isPromotedByDefault == True
    checkbox.isPromotedByDefault = False
    assert checkbox.isPromotedByDefault == False
    assert checkbox.isValid == True
    print(checkbox.isVisible)
    print(checkbox.objectType)
    print(checkbox.parent)

    print(checkbox.classType())
    print(checkbox.deleteMe)

    assert (
        checkbox.commandDefinition.controlDefinition.objectType
        == adsk.core.CheckBoxControlDefinition.classType()
    )


# region
# def test_list_properties():
#         addin = faf.FusionAddin()
#         ws = faf.Workspace(addin)
#         tab = faf.Tab(ws)
#         panel = faf.Panel(tab)
#         list_ctrl = faf.Control(
#             panel,
#             controlType="list",
#             isVisible=True,
#             isPromoted=True,
#             isPromotedByDefault=True,
#             positionID="",
#             isBefore=True,
#         )
#         print(list_ctrl.parent)
#         print(list_ctrl.addin)
#         assert list_ctrl.uiLevel == 4

#         print(list_ctrl.commandDefinition)
#         print(list_ctrl.id)
#         assert list_ctrl.isPromoted == True
#         list_ctrl.isPromoted = False
#         assert list_ctrl.isPromoted == False
#         assert list_ctrl.isPromotedByDefault == True
#         list_ctrl.isPromotedByDefault = False
#         assert list_ctrl.isPromotedByDefault == False
#         assert list_ctrl.isValid == True
#         print(list_ctrl.isVisible)
#         print(list_ctrl.objectType)
#         print(list_ctrl.parent)

#         print(list_ctrl.classType())
#         print(list_ctrl.deleteMe)

#         assert (
#             list_ctrl.commandDefinition.controlDefinition.objectType
#             == adsk.core.ListControlDefinition.classType()
#         )
# endregion


def test_button_command_properties():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(ws)
    panel = faf.Panel(tab)
    button = faf.Control(panel)
    cmd = faf.AddinCommand(
        button,
        id="test_button_command_properties_cmd_id",
        name="ma command",
        resourceFolder=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one",
        tooltip="my custom tooltip",
        toolClipFileName=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one/32x32.png",
        isEnabled=True,
        isVisible=True,
        isChecked=True,
        execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
            "hello world"
        ),
    )
    print(cmd.parent)
    print(cmd.addin)
    assert cmd.uiLevel == 5

    # controlDefinition attributes
    print(cmd.controlDefinition)
    assert cmd.isEnabled == True
    cmd.isEnabled = False
    assert cmd.isEnabled == False

    assert cmd.isValid == True
    assert cmd.isVisible == True
    cmd.isVisible = False
    assert cmd.isVisible == False
    cmd.isVisible = True
    # assert cmd.name == "ma command"
    # cmd.name = "2"
    # assert cmd.name == "2"
    # print(cmd.objectType)

    # commandDefinition attributes
    assert cmd.id == "test_button_command_properties_cmd_id"
    assert cmd.isNative == False
    assert cmd.isValid == True
    assert cmd.name == "ma command"
    cmd.name = "2"
    assert cmd.name == "2"
    print(cmd.objectType)
    assert (
        cmd.resourceFolder
        == r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one"
    )
    cmd.resourceFolder = r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/two"
    assert (
        cmd.resourceFolder
        == r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/two"
    )
    assert (
        cmd.toolClipFilename
        == r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one/32x32.png"
    )
    cmd.toolClipFilename = r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/two/32x32.png"
    assert (
        cmd.toolClipFilename
        == r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/two/32x32.png"
    )
    # accessing the tooltip returns empty string. This is an error in the API.
    # print(cmd.tooltip)
    # assert cmd.tooltip == "my custom tooltip"
    cmd.tooltip = "my tooltip 2"
    # assert cmd.tooltip == "my tooltip 2"

    print(cmd.classType())
    print(cmd.deleteMe)
    print(cmd.execute)


def test_checkbox_command_properties():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(ws)
    panel = faf.Panel(tab)
    checkbox = faf.Control(panel, controlType="checkbox")
    cmd = faf.AddinCommand(
        checkbox,
        id="test_checkbox_command_properties_cmd_id",
        name="ma command",
        resourceFolder=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one",
        tooltip="my custom tooltip",
        toolClipFileName=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one/32x32.png",
        isEnabled=True,
        isVisible=True,
        isChecked=True,
        execute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
            "hello world"
        ),
    )
    print(cmd.parent)
    print(cmd.addin)
    assert cmd.uiLevel == 5

    # controlDefinition attributes
    print(cmd.controlDefinition)
    assert cmd.isEnabled == True
    cmd.isEnabled = False
    assert cmd.isEnabled == False
    assert cmd.isChecked == True
    cmd.isChecked = False
    assert cmd.isChecked == False

    assert cmd.isValid == True
    assert cmd.isVisible == True
    cmd.isVisible = False
    assert cmd.isVisible == False
    cmd.isVisible = True
    # assert cmd.name == "ma command"
    # cmd.name = "2"
    # assert cmd.name == "2"
    # print(cmd.objectType)

    # commandDefinition attributes
    assert cmd.id == "test_checkbox_command_properties_cmd_id"
    assert cmd.isNative == False
    assert cmd.isValid == True
    assert cmd.name == "ma command"
    cmd.name = "2"
    assert cmd.name == "2"
    print(cmd.objectType)
    assert (
        cmd.resourceFolder
        == r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one"
    )
    cmd.resourceFolder = r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/two"
    assert (
        cmd.resourceFolder
        == r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/two"
    )
    assert (
        cmd.toolClipFilename
        == r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one/32x32.png"
    )
    cmd.toolClipFilename = r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/two/32x32.png"
    assert (
        cmd.toolClipFilename
        == r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/two/32x32.png"
    )
    # accessing the tooltip returns empty string. This is an error in the API.
    # print(cmd.tooltip)
    # assert cmd.tooltip == "my custom tooltip"
    cmd.tooltip = "my tooltip 2"
    # assert cmd.tooltip == "my tooltip 2"

    print(cmd.classType())
    print(cmd.deleteMe)
    print(cmd.execute)


def test_all_handlers_buttton():
    cmd = faf.AddinCommand(
        commandCreated=lambda args: args.command.commandInputs.addBoolValueInput(
            "customboolvalueinputid", "bool", False
        ),
        activate=lambda args: print("onActivate", args),
        deactivate=lambda args: print("onDeactivate", args),
        destroy=lambda args: print("onDestroy", args),
        execute=lambda args: print("onExecute", args),
        executePreview=lambda args: print("onExecutePreview", args),
        inputChanged=lambda args: print("onInputChanged", args),
        keyDown=lambda args: print("onKayDown", args),
        keyUp=lambda args: print("onKayUp", args),
        mouseClick=lambda args: print("onMouseClick", args),
        mouseDoubleClick=lambda args: print("onMouseDoubleClick", args),
        mouseDown=lambda args: print("onMouseDown", args),
        mouseDrag=lambda args: print("onMouseDrag", args),
        mouseDragBegin=lambda args: print("onMouseDrgaBegin", args),
        mouseDragEnd=lambda args: print("onMouseDragEnd", args),
        mouseUp=lambda args: print("onMouseUp", args),
        mouseWheel=lambda args: print("onMouseWheel", args),
        # onMouseMove=lambda args: print("onMouseMove", args),
        preSelect=lambda args: print("onPreSelect", args),
        preSelectEnd=lambda args: print("onPreSelectEnd", args),
        preSelectMouseMove=lambda args: print("onPreSelectMouseMove", args),
        select=lambda args: print("onSelect", args),
        unselect=lambda args: print("onUnselect", args),
        validateInputs=lambda args: print("onValidateInputs", args),
    )


def test_all_handlers_checkbox():
    checkbox = faf.Control(controlType="checkbox")
    cmd = faf.AddinCommand(
        checkbox,
        commandCreated=lambda args: args.command.commandInputs.addBoolValueInput(
            "customboolvalueinputid", "bool", False
        ),
        activate=lambda args: print("onActivate", args),
        deactivate=lambda args: print("onDeactivate", args),
        destroy=lambda args: print("onDestroy", args),
        execute=lambda args: print("onExecute", args),
        executePreview=lambda args: print("onExecutePreview", args),
        inputChanged=lambda args: print("onInputChanged", args),
        keyDown=lambda args: print("onKayDown", args),
        keyUp=lambda args: print("onKayUp", args),
        mouseClick=lambda args: print("onMouseClick", args),
        mouseDoubleClick=lambda args: print("onMouseDoubleClick", args),
        mouseDown=lambda args: print("onMouseDown", args),
        mouseDrag=lambda args: print("onMouseDrag", args),
        mouseDragBegin=lambda args: print("onMouseDrgaBegin", args),
        mouseDragEnd=lambda args: print("onMouseDragEnd", args),
        mouseUp=lambda args: print("onMouseUp", args),
        mouseWheel=lambda args: print("onMouseWheel", args),
        # onMouseMove=lambda args: print("onMouseMove", args),
        preSelect=lambda args: print("onPreSelect", args),
        preSelectEnd=lambda args: print("onPreSelectEnd", args),
        preSelectMouseMove=lambda args: print("onPreSelectMouseMove", args),
        select=lambda args: print("onSelect", args),
        unselect=lambda args: print("onUnselect", args),
        validateInputs=lambda args: print("onValidateInputs", args),
    )


def test_error_handlers_passed_buttton():
    raised = False
    try:
        cmd = faf.AddinCommand(asdasd=lambda args: print("error"))
    except Exception:
        raised = True
    if not raised:
        raise ValueError("Invalid handler name not detected by addin.")


def test_error_in_handler():
    def raise_error(args):
        print("start")
        raise ValueError()
        print("end")

    cmd = faf.AddinCommand(execute=raise_error)
    cmd.addin.debugToUi = False
    assert cmd.addin.debugToUi == False


def test_multiple_controls():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(ws)

    panel = faf.Panel(tab)
    button_1 = faf.Control(panel)
    # two buttons in one panel is not allowed
    # button_2 = faf.Control(panel)
    panel_2 = faf.Panel(tab, "random")
    button_3 = faf.Control(panel_2)
    cmd = faf.AddinCommand([button_1, button_3])

    tab_2 = faf.Tab(ws, "random")
    panel_3 = faf.Panel(tab_2)
    button_5 = faf.Control(panel_3)
    cmd.addParentControl(button_5)


def test_multiple_controls_2():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(ws)

    panel = faf.Panel(tab)
    button_1 = faf.Control(panel)
    # button_2 = faf.Control(panel)
    panel_2 = faf.Panel(tab, "random")
    button_3 = faf.Control(panel_2)
    # button_4 = faf.control(panel_2)
    cmd = faf.AddinCommand(button_1)

    # cmd.addParentControl(button_2)
    cmd.addParentControl(button_3)
    # cmd.addParentControl(button_4)

    tab_2 = faf.Tab(ws, "random")
    panel_3 = faf.Panel(tab_2)
    button_5 = faf.Control(panel_3)
    cmd.addParentControl(button_5)


def test_multiple_controls_3():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(ws)

    panel = faf.Panel(tab)
    button_1 = faf.Control(panel)
    panel_2 = faf.Panel(tab, "random")
    button_3 = faf.Control(panel_2)
    cmd = faf.AddinCommand([button_1])

    cmd.addParentControl(button_3)

    tab_2 = faf.Tab(ws, "random")
    panel_3 = faf.Panel(tab_2)
    button_5 = faf.Control(panel_3)
    cmd.addParentControl(button_5)


def test_multiple_controls_different_type():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(ws)

    panel = faf.Panel(tab)
    checkbox = faf.Control(panel, controlType="checkbox")
    panel_2 = faf.Panel(tab, "random")
    button_3 = faf.Control(panel_2)
    cmd = faf.AddinCommand([checkbox, button_3])


def test_dropdown_normal():
    addin = faf.FusionAddin()
    ws = faf.Workspace(addin)
    tab = faf.Tab(ws, id="random")
    panel = faf.Panel(tab)
    dd = faf.Dropdown(panel)
    ctrl = faf.Control(dd, isPromoted=False, isPromotedByDefault=False)
    ctrl_2 = faf.Control(dd)
    cmd = faf.AddinCommand(ctrl)


def test_dropdown_default():
    dd = faf.Dropdown()
    ctrl = faf.Control(dd)


def test_dropdown_dotted():
    ctrl = faf.Workspace().tab().panel().dropdown().control()


def test_dropdown_nested():
    ctrl = (
        faf.Workspace()
        .tab()
        .panel()
        .dropdown()
        .dropdown()
        .dropdown()
        .dropdown()
        .control()
    )


def test_dropdown_properties():
    dd = faf.Dropdown(
        id="test_dropdown_properties_id",
        text="dd_name",
        resourceFolder=r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one",
        isVisible=True,
    )
    ctrl = faf.Control(dd)

    assert dd.uiLevel == 4
    print(dd.controls)
    assert dd.id == "test_dropdown_properties_id"
    print(dd.index)
    assert dd.isValid == True
    print(dd.isVisible)
    assert dd.name == "dd_name"
    print(dd.objectType)
    print(dd.parent)
    assert (
        dd.resourceFolder
        == r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one"
    )


def test_custom_event():
    event_id = str(uuid4())
    addin = faf.FusionAddin()
    faf.utils.create_custom_event(
        event_id,
        lambda event_arg: adsk.core.Application.get().userInterface.messageBox(
            str(random.randint(0, 100))
        ),
    )
    adsk.core.Application.get().fireCustomEvent(event_id)


def test_execute_as_event():
    addin = faf.FusionAddin()
    faf.utils.execute_as_event(
        lambda: adsk.core.Application.get().userInterface.messageBox("42")
    )


def test_thread_event_utility():
    try:
        addin = faf.FusionAddin()
        thread = faf.utils.PeriodicExecuter(
            5,
            lambda: faf.utils.execute_as_event(
                lambda: adsk.core.Application.get().userInterface.messageBox(
                    str(random.randint(0, 100))
                )
            ),
        )
        thread.start()
    except Exception as test_exception:
        try:
            thread.pause()
        except:
            pass
        raise test_exception


@faf.utils.execute_as_event_deco()
def decorated_action(show="42"):
    adsk.core.Application.get().userInterface.messageBox(show)


def test_execute_as_event_decorator():
    addin = faf.FusionAddin()
    decorated_action("42")


def test_thread_event_decorator():
    try:
        addin = faf.FusionAddin()
        thread = faf.utils.PeriodicExecuter(5, decorated_action)
        thread.start()
    except Exception as test_exception:
        try:
            thread.pause()
        except:
            pass
        raise test_exception


class MyCommand(faf.AddinCommandBase):
    def execute(self, eventArgs):
        print("execute")

    def commandCreated(self, eventArgs: adsk.core.CommandEventArgs):
        print("commandCreated")

    def inputChanged(self, eventArgs: adsk.core.CommandEventArgs):
        print("input changed")


def test_subclass_pattern():
    cmd = MyCommand()


ALL_CASES = [
    test_hello_world_button_normal,
    test_hello_world_button_dotted,
    test_hello_world_button_defaults,
    test_checkbox_normal,
    test_checkbox_dotted,
    test_checkbox_defaults,
    test_standard_attrs_button,
    test_very_custom_button,
    test_very_custom_checkbox,
    test_addin_properties,
    test_workspace_properties,
    test_tab_properties,
    test_panel_properties,
    test_button_properties,
    test_checkbox_properties,
    test_button_command_properties,
    test_checkbox_command_properties,
    test_all_handlers_buttton,
    test_all_handlers_checkbox,
    # onyl testabel as single test as addin gets instantiated but does not return reference and therefore cant be deleted later
    # test_error_handlers_passed_buttton,
    test_error_in_handler,
    test_multiple_controls,
    test_multiple_controls_2,
    test_multiple_controls_3,
    test_multiple_controls_different_type,
    test_dropdown_normal,
    test_dropdown_default,
    test_dropdown_dotted,
    test_dropdown_nested,
    test_dropdown_properties,
    test_custom_event,
    test_execute_as_event,
    # pops up a window every few seconds and therefore no included in main test suite
    # test_thread_event_utility,
    # test_thread_event_decorator,
    test_execute_as_event_decorator,
    test_subclass_pattern,
]
