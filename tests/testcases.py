""" """

from collections import defaultdict
from time import perf_counter
import traceback
from typing import List, Callable

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


def test_list_normal():
    try:
        addin = faf.FusionAddin()
        ws = faf.Workspace(addin)
        tab = faf.Tab(ws)
        panel = faf.Panel(tab)
        checkbox = faf.Control(panel, controlType="list")
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


def test_list_dotted():
    try:
        addin = faf.FusionAddin()
        cmd = (
            addin.workspace()
            .tab()
            .panel()
            .control(controlType="list")
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


def test_list_defaults():
    try:
        list_ctrl = faf.Control(controlType="list")
        cmd = faf.AddinCommand(
            list_ctrl,
            onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            ),
        )
    except Exception as test_exception:
        list_ctrl.addin.stop()
        raise test_exception
    return list_ctrl.addin


def test_standard_attrs_button():
    try:
        cmd = (
            faf.FusionAddin(debug_to_ui=True)
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
        addin = faf.FusionAddin(debug_to_ui=True)
        ws = faf.Workspace(
            addin,
            id="FusionSolidEnvironment",
            name="my test name",
            productType="DesignProductType",
            resourceFolder=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images",
            toolClipFilename=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images\32x32.png",
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
            resourceFolder=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images",
            tooltip="my custom tooltip",
            toolClipFileName=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images\32x32.png",
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
        addin = faf.FusionAddin(debug_to_ui=True)
        ws = faf.Workspace(
            addin,
            id="FusionSolidEnvironment",
            name="my test name",
            productType="DesignProductType",
            resourceFolder=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images",
            toolClipFilename=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images\32x32.png",
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
            isPromoted=True,
            isPromotedByDefault=True,
            positionID="",
            isBefore=True,
        )
        cmd = faf.AddinCommand(
            ctrl,
            id="mycustomcheckboxcmdid",
            name="ma command",
            resourceFolder=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images",
            tooltip="my custom tooltip",
            toolClipFileName=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images\32x32.png",
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


def test_very_custom_list():
    try:
        addin = faf.FusionAddin(debug_to_ui=True)
        ws = faf.Workspace(
            addin,
            id="FusionSolidEnvironment",
            name="my test name",
            productType="DesignProductType",
            resourceFolder=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images",
            toolClipFilename=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images\32x32.png",
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
            controlType="list",
            isVisible=True,
            isPromoted=True,
            isPromotedByDefault=True,
            positionID="",
            isBefore=True,
        )
        cmd = faf.AddinCommand(
            ctrl,
            id="mycustomlistcmdid",
            name="ma command",
            resourceFolder=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images",
            tooltip="my custom tooltip",
            toolClipFileName=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images\32x32.png",
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


def test_addin_properties():
    try:
        addin = faf.FusionAddin(debug_to_ui=False)
        assert addin.debug_to_ui == False
        addin.debug_to_ui = True
        assert addin.debug_to_ui == True
        assert addin.ui_level == 0
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_workspace_properties():
    try:
        addin = faf.FusionAddin()
        ws = faf.Workspace(
            addin,
            id="FusionSolidEnvironment",
            name="my test name",
            productType="DesignProductType",
            resourceFolder=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images",
            toolClipFilename=r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\tests\test_images\32x32.png",
            tooltip="my test tooltip",
            tooltipDescription="my test tooltip description",
        )
        print(ws.parent)
        print(ws.addin)
        assert ws.ui_level == 1

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
        assert tab.ui_level == 2

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
        print(tab.parent)
        print(tab.addin)
        assert tab.ui_level == 3

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
        print(panel.indexWithinTab())

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_button_properteis():
    try:
        addin = faf.FusionAddin()
        ws = faf.Workspace(addin)
        tab = faf.Tab(ws)
        panel = faf.Panel(tab)
        button = faf.Control(panel)

    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin

    # def test_checkbox_properties():
    #     try:
    #         addin = faf.FusionAddin()
    #         ws = faf.Workspace(addin)
    #         tab = faf.Tab(ws)
    #         panel = faf.Panel(tab)
    #         button = faf.Control(panel)

    #     except Exception as test_exception:
    #         addin.stop()
    #         raise test_exception
    #     return addin

    # def test_list_properties():
    #     try:
    #         addin = faf.FusionAddin()
    #         ws = faf.Workspace(addin)
    #         tab = faf.Tab(ws)
    #         panel = faf.Panel(tab)
    #         button = faf.Control(panel)

    #     except Exception as test_exception:
    #         addin.stop()
    #         raise test_exception
    #     return addin

    # def test_command_properties():
    #     try:
    #         addin = faf.FusionAddin()
    #         ws = faf.Workspace(addin)
    #         tab = faf.Tab(ws)
    #         panel = faf.Panel(tab)
    #         button = faf.Control(panel)
    #         cmd = faf.AddinCommand(
    #             button,
    #             onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
    #                 "hello world"
    #             ),
    #         )
    #     except Exception as test_exception:
    #         addin.stop()
    #         raise test_exception
    #     return addin

    # def test_all_handlers_buttton():
    #     pass

    # def test_multiple_controls():
    #     pass

    # def test_empty_control():
    pass