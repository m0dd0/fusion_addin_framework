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
    addin = faf.FusionAddin()
    try:
        ws = faf.Workspace(addin)
        tab = faf.Tab(ws)
        panel = faf.Panel(tab)
        button = faf.Control(
            panel,
        )
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
    addin = faf.FusionAddin()
    try:
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
        raise test_exception


def test_checkbox_normal():
    addin = faf.FusionAddin()
    try:
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
    addin = faf.FusionAddin()
    try:
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
        raise test_exception


def test_list_normal():
    addin = faf.FusionAddin()
    try:
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
    addin = faf.FusionAddin()
    try:
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
        checkbox = faf.Control(controlType="list")
        cmd = faf.AddinCommand(
            checkbox,
            onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            ),
        )
    except Exception as test_exception:
        raise test_exception


def test_very_custom_button():
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
            positionID=None,
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


def test_very_custom_checkbox():
    pass


def test_very_custom_list():
    pass


# TODO check also setability
# region access attributes
def test_addin_properties():
    pass
    # print(addin.name)
    # print(addin.author)
    # print(addin.debug_to_ui)
    # print(addin.user_state_dir)
    # print(addin.user_cache_dir)
    # print(addin.user_config_dir)
    # print(addin.user_data_dir)
    # print(addin.user_log_dir)
    # print(addin.ui_level)
    # print(addin.created_elements)


def test_workspace_properties():
    pass
    # print(workspace.parent)
    # print(workspace.addin)
    # print(workspace.ui_level)

    # print(workspace.id)
    # print(workspace.isActive)
    # print(workspace.isNative)
    # print(workspace.isValid)
    # print(workspace.name)
    # print(workspace.objectType)
    # print(workspace.productType)
    # print(workspace.resourceFolder)
    # print(workspace.toolbarPanels)
    # print(workspace.toolbarTabs)
    # print(workspace.toolClipFileName)
    # print(workspace.tooltip)
    # print(workspace.tooltipDescription)


def test_tab_properties():
    pass
    # print(tab.parent)
    # print(tab.addin)
    # print(tab.ui_level)

    # print(tab.id)
    # print(tab.index)
    # print(tab.isActive)
    # print(tab.isNative)
    # print(tab.isValid)
    # print(tab.isVisible)
    # print(tab.name)
    # print(tab.objectType)
    # print(tab.parenUserInterface)
    # print(tab.productType)
    # print(tab.toolbarPanels)


def test_panel_properties():
    pass
    # print(panel.parent)
    # print(panel.addin)
    # print(panel.ui_level)

    # print(panel.controls)
    # print(panel.id)
    # print(panel.index)
    # print(panel.isValid)
    # print(panel.isVisible)
    # print(panel.name)
    # print(panel.objectType)
    # print(panel.parenUserInterface)
    # print(panel.productType)
    # print(panel.promotedControls)
    # print(panel.relatedWorkspaces)


def test_button_properteis():
    pass


def test_checkbox_properties():
    pass


def test_list_properties():
    pass


def test_command_properties():
    pass


def test_all_handlers_buttton():
    pass


def test_multiple_controls():
    pass


def test_empty_control():
    pass