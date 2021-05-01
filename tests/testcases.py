from collections import defaultdict
from time import perf_counter
import traceback

import adsk.fusion, adsk.core

from .. import fusion_addin_framework as faf


def execute_cases(cases):
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


def test_default_button():
    addin = faf.FusionAddin()
    try:
        ws = faf.Workspace(addin)
        tab = faf.Tab(ws)
        panel = faf.Panel(tab)
        button = faf.Button(panel)
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_hello_world():
    addin = faf.FusionAddin()
    try:
        ws = faf.Workspace(addin)
        tab = faf.Tab(ws)
        panel = faf.Panel(tab)
        button = faf.Button(
            panel,
        )
        cmd = faf.ButtonCommand(
            button,
            onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            ),
        )
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def access_all_addin_properties(addin):
    print(addin.name)
    print(addin.author)
    print(addin.debug_to_ui)
    print(addin.user_state_dir)
    print(addin.user_cache_dir)
    print(addin.user_config_dir)
    print(addin.user_data_dir)
    print(addin.user_log_dir)
    print(addin.ui_level)
    print(addin.created_elements)


def access_all_workspace_properties(workspace):
    print(workspace.parent)
    print(workspace.addin)
    print(workspace.ui_level)

    print(workspace.id)
    print(workspace.isActive)
    print(workspace.isNative)
    print(workspace.isValid)
    print(workspace.name)
    print(workspace.objectType)
    print(workspace.productType)
    print(workspace.resourceFolder)
    print(workspace.toolbarPanels)
    print(workspace.toolbarTabs)
    print(workspace.toolClipFileName)
    print(workspace.tooltip)
    print(workspace.tooltipDescription)


def access_all_tab_properties(tab):
    print(tab.parent)
    print(tab.addin)
    print(tab.ui_level)

    print(tab.id)
    print(tab.index)
    print(tab.isActive)
    print(tab.isNative)
    print(tab.isValid)
    print(tab.isVisible)
    print(tab.name)
    print(tab.objectType)
    print(tab.parenUserInterface)
    print(tab.productType)
    print(tab.toolbarPanels)


def access_all_panel_properties(panel):
    print(panel.parent)
    print(panel.addin)
    print(panel.ui_level)

    print(panel.controls)
    print(panel.id)
    print(panel.index)
    print(panel.isValid)
    print(panel.isVisible)
    print(panel.name)
    print(panel.objectType)
    print(panel.parenUserInterface)
    print(panel.productType)
    print(panel.promotedControls)
    print(panel.relatedWorkspaces)


def test_addin_properties():
    addin = faf.FusionAddin("my_addin", "Moritz", True)
    try:
        access_all_addin_properties(addin)
        assert addin.name == "my_addin"
        assert addin.author == "Moritz"
        assert addin.debug_to_ui == True
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_custom_workspace():
    addin = faf.FusionAddin()
    try:
        ws = faf.Workspace(addin, "MyWorkspaceCustomID")
        tab = faf.Tab(ws)
        panel = faf.Panel(tab)
        button = faf.Button(panel)
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin


def test_custom_tab():
    pass


def test_custom_panel():
    pass


def test_connect_multiple_commands():
    pass


def test_all_handlers():
    pass