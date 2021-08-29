""" """

from collections import defaultdict
from time import perf_counter
import traceback
from typing import List, Callable
from uuid import uuid4
from datetime import datetime
import random
import time

import adsk.fusion, adsk.core

from .. import fusion_addin_framework as faf


def execute_cases(cases: List[Callable]):
    """Executes the passed functions in a controlled environment and logs some
        data about their axacution.

    Args:
        cases (List[Callable]): A list of the testfuctions to execute.

    Returns:
        dict: A dictionairy with the test resulte mapped to the function name.
        list: A list of addins which where created durin the execution of the tests.
    """
    results = defaultdict(dict)
    addins = []
    for case in cases:
        try:
            print(f"{f' {case.__name__} ':{'#'}^{60}}")
            start = perf_counter()
            addin = case()
            addins.append(addin)
            results[case.__name__]["elapsed_time"] = perf_counter() - start
            results[case.__name__]["passed"] = True
        except:
            results[case.__name__]["elapsed_time"] = -1
            results[case.__name__]["passed"] = False
            print(traceback.format_exc())

    return results, addins

    ### Testcases ###


def test_hello_world_button_normal():
    try:
        addin = faf.FusionAddin()
        ws = faf.Workspace(addin)
        tab = faf.Tab(ws)
        panel = faf.Panel(tab)
        button = faf.Control(panel)
        cmd = faf.AddinCommand(
            button,
            onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            ),
        )
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_hello_world_button_dotted():
    try:
        addin = faf.FusionAddin()
        cmd = (
            addin.workspace()
            .tab()
            .panel()
            .control()
            .addinCommand(
                onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                    "hello world"
                ),
            )
        )
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_hello_world_button_defaults():
    try:
        cmd = faf.AddinCommand(
            onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            )
        )
    except Exception as test_exception:
        cmd.addin.stop()
        raise test_exception
    return cmd.addin


def test_checkbox_normal():
    try:
        addin = faf.FusionAddin()
        ws = faf.Workspace(addin)
        tab = faf.Tab(ws)
        panel = faf.Panel(tab)
        checkbox = faf.Control(panel, controlType="checkbox")
        cmd = faf.AddinCommand(
            checkbox,
            onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            ),
        )
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_checkbox_dotted():
    try:
        addin = faf.FusionAddin()
        cmd = (
            addin.workspace()
            .tab()
            .panel()
            .control(controlType="checkbox")
            .addinCommand(
                onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                    "hello world"
                ),
            )
        )
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_checkbox_defaults():
    try:
        checkbox = faf.Control(controlType="checkbox")
        cmd = faf.AddinCommand(
            checkbox,
            onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            ),
        )
    except Exception as test_exception:
        checkbox.addin.stop()
        raise test_exception
    return checkbox.addin


# def test_list_normal():
#     try:
#         addin = faf.FusionAddin()
#         ws = faf.Workspace(addin)
#         tab = faf.Tab(ws)
#         panel = faf.Panel(tab)
#         checkbox = faf.Control(panel, controlType="list")
#         cmd = faf.AddinCommand(
#             checkbox,
#             onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
#                 "hello world"
#             ),
#         )
#     except Exception as test_exception:
#         addin.stop()
#         raise test_exception
#     return addin

# def test_list_dotted():
#     try:
#         addin = faf.FusionAddin()
#         cmd = (
#             addin.workspace()
#             .tab()
#             .panel()
#             .control(controlType="list")
#             .addinCommand(
#                 onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
#                     "hello world"
#                 ),
#             )
#         )
#     except Exception as test_exception:
#         addin.stop()
#         raise test_exception
#     return addin

# def test_list_defaults():
#     try:
#         list_ctrl = faf.Control(controlType="list")
#         cmd = faf.AddinCommand(
#             list_ctrl,
#             onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
#                 "hello world"
#             ),
#         )
#     except Exception as test_exception:
#         list_ctrl.addin.stop()
#         raise test_exception
#     return list_ctrl.addin


def test_standard_attrs_button():
    try:
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
                onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                    "hello world"
                ),
            )
        )
    except Exception as test_exception:
        cmd.addin.stop()
        raise test_exception
    return cmd.addin


def test_very_custom_button():
    try:
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
            onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            ),
        )
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_very_custom_checkbox():
    try:
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
            onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            ),
        )
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


# def test_very_custom_list():
#     try:
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
#             onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
#                 "hello world"
#             ),
#         )
#     except Exception as test_exception:
#         addin.stop()
#         raise test_exception
#     return addin


def test_addin_properties():
    try:
        addin = faf.FusionAddin(debugToUi=False)
        assert addin.debugToUi == False
        addin.debugToUi = True
        assert addin.debugToUi == True
        assert addin.uiLevel == 0
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_workspace_properties():
    try:
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
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_tab_properties():
    try:
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

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_panel_properties():
    try:
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

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_button_properties():
    try:
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

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_checkbox_properties():
    try:
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

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


# def test_list_properties():
#     try:
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

#     except Exception as test_exception:
#         addin.stop()
#         raise test_exception
#     return addin


def test_button_command_properties():
    try:
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
            onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
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

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_checkbox_command_properties():
    try:
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
            onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
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

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_all_on_handlers_buttton():
    try:
        cmd = faf.AddinCommand(
            onCommandCreated=lambda args: args.command.commandInputs.addBoolValueInput(
                "customboolvalueinputid", "bool", False
            ),
            onActivate=lambda args: print("onActivate", args),
            onDeactivate=lambda args: print("onDeactivate", args),
            onDestroy=lambda args: print("onDestroy", args),
            onExecute=lambda args: print("onExecute", args),
            onExecutePreview=lambda args: print("onExecutePreview", args),
            onInputChanged=lambda args: print("onInputChanged", args),
            onKeyDown=lambda args: print("onKayDown", args),
            onKeyUp=lambda args: print("onKayUp", args),
            onMouseClick=lambda args: print("onMouseClick", args),
            onMouseDoubleClick=lambda args: print("onMouseDoubleClick", args),
            onMouseDown=lambda args: print("onMouseDown", args),
            onMouseDrag=lambda args: print("onMouseDrag", args),
            onMouseDragBegin=lambda args: print("onMouseDrgaBegin", args),
            onMouseDragEnd=lambda args: print("onMouseDragEnd", args),
            onMouseUp=lambda args: print("onMouseUp", args),
            onMouseWheel=lambda args: print("onMouseWheel", args),
            # onMouseMove=lambda args: print("onMouseMove", args),
            onPreSelect=lambda args: print("onPreSelect", args),
            onPreSelectEnd=lambda args: print("onPreSelectEnd", args),
            onPreSelectMouseMove=lambda args: print("onPreSelectMouseMove", args),
            onSelect=lambda args: print("onSelect", args),
            onUnselect=lambda args: print("onUnselect", args),
            onValidateInputs=lambda args: print("onValidateInputs", args),
        )
    except Exception as test_exception:
        cmd.addin.stop()
        raise test_exception
    return cmd.addin


def test_all_on_handlers_checkbox():
    try:
        checkbox = faf.Control(controlType="checkbox")
        cmd = faf.AddinCommand(
            checkbox,
            onCommandCreated=lambda args: args.command.commandInputs.addBoolValueInput(
                "customboolvalueinputid", "bool", False
            ),
            onActivate=lambda args: print("onActivate", args),
            onDeactivate=lambda args: print("onDeactivate", args),
            onDestroy=lambda args: print("onDestroy", args),
            onExecute=lambda args: print("onExecute", args),
            onExecutePreview=lambda args: print("onExecutePreview", args),
            onInputChanged=lambda args: print("onInputChanged", args),
            onKeyDown=lambda args: print("onKayDown", args),
            onKeyUp=lambda args: print("onKayUp", args),
            onMouseClick=lambda args: print("onMouseClick", args),
            onMouseDoubleClick=lambda args: print("onMouseDoubleClick", args),
            onMouseDown=lambda args: print("onMouseDown", args),
            onMouseDrag=lambda args: print("onMouseDrag", args),
            onMouseDragBegin=lambda args: print("onMouseDrgaBegin", args),
            onMouseDragEnd=lambda args: print("onMouseDragEnd", args),
            onMouseUp=lambda args: print("onMouseUp", args),
            onMouseWheel=lambda args: print("onMouseWheel", args),
            # onMouseMove=lambda args: print("onMouseMove", args),
            onPreSelect=lambda args: print("onPreSelect", args),
            onPreSelectEnd=lambda args: print("onPreSelectEnd", args),
            onPreSelectMouseMove=lambda args: print("onPreSelectMouseMove", args),
            onSelect=lambda args: print("onSelect", args),
            onUnselect=lambda args: print("onUnselect", args),
            onValidateInputs=lambda args: print("onValidateInputs", args),
        )
    except Exception as test_exception:
        cmd.addin.stop()
        raise test_exception
    return cmd.addin


def test_all_handlers_buttton():
    try:
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
            # mouseMove=lambda args: print("onMouseMove", args),
            preSelect=lambda args: print("onPreSelect", args),
            preSelectEnd=lambda args: print("onPreSelectEnd", args),
            preSelectMouseMove=lambda args: print("onPreSelectMouseMove", args),
            select=lambda args: print("onSelect", args),
            unselect=lambda args: print("onUnselect", args),
            validateInputs=lambda args: print("onValidateInputs", args),
        )
    except Exception as test_exception:
        cmd.addin.stop()
        raise test_exception
    return cmd.addin


def test_error_handlers_passed_buttton():
    try:
        cmd = faf.AddinCommand(
            execute=lambda args: print("onExecute", args),
            onExecute=lambda args: print("onExecute DOUBLE", args),
            asdasd=lambda args: print("error"),
        )
    except Exception as test_exception:
        cmd.addin.stop()
        raise test_exception
    return cmd.addin


def test_error_in_handler():
    def raise_error(args):
        print("start")
        raise ValueError
        print("end")

    try:
        cmd = faf.AddinCommand(
            execute=raise_error,  # print("onExecute", args),
        )
        cmd.addin.debugToUi = False
        assert cmd.addin.debugToUi == False
    except Exception as test_exception:
        cmd.addin.stop()
        raise test_exception
    return cmd.addin


def test_multiple_controls():
    try:
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

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_multiple_controls_2():
    try:
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

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_multiple_controls_3():
    try:
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

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_multiple_controls_different_type():
    try:
        addin = faf.FusionAddin()
        ws = faf.Workspace(addin)
        tab = faf.Tab(ws)

        panel = faf.Panel(tab)
        checkbox = faf.Control(panel, controlType="checkbox")
        panel_2 = faf.Panel(tab, "random")
        button_3 = faf.Control(panel_2)
        cmd = faf.AddinCommand([checkbox, button_3])

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_dropdown_normal():
    try:
        addin = faf.FusionAddin()
        ws = faf.Workspace(addin)
        tab = faf.Tab(ws, id="random")
        panel = faf.Panel(tab)
        dd = faf.Dropdown(panel)
        ctrl = faf.Control(dd, isPromoted=False, isPromotedByDefault=False)
        ctrl_2 = faf.Control(dd)
        cmd = faf.AddinCommand(ctrl)

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_dropdown_default():
    try:
        dd = faf.Dropdown()
        ctrl = faf.Control(dd)

    except Exception as test_exception:
        dd.addin.stop()
        raise test_exception
    return dd.addin


def test_dropdown_dotted():
    try:
        ctrl = faf.Workspace().tab().panel().dropdown().control()

    except Exception as test_exception:
        ctrl.addin.stop()
        raise test_exception
    return ctrl.addin


def test_dropdown_nested():
    try:
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

    except Exception as test_exception:
        ctrl.addin.stop()
        raise test_exception
    return ctrl.addin


def test_dropdown_properties():
    try:
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

    except Exception as test_exception:
        dd.addin.stop()
        raise test_exception
    return dd.addin


def test_custom_events():
    try:
        custom_event_id = str(uuid4())
        cmd = faf.AddinCommand(
            customEventHandlers={
                custom_event_id: lambda args: adsk.core.Application.get().userInterface.messageBox(
                    args.additionalInfo
                )
            }
        )

        thread = faf.utils.PeriodicExecuter(
            5,
            lambda: adsk.core.Application.get().fireCustomEvent(
                custom_event_id, str(random.randint(0, 100))
            ),
        )
        thread.start()
        # time.sleep(20)
        # thread.kill()
    except Exception as test_exception:
        cmd.addin.stop()
        raise test_exception
    return cmd.addin