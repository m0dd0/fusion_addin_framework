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
            start = perf_counter()
            addin = case()
            addins.append(addin)
            results[case.__name__]["elapsed_time"] = perf_counter() - start
            results[case.__name__]["passed"] = True
        except:
            results[case.__name__]["elapsed_time"] = -1
            results[case.__name__]["passed"] = False
            print(case.__name__, "#################################")
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
        cmd = faf.Command(
            button,
            onExecute=lambda command_event_args: adsk.core.Application.get().userInterface.messageBox(
                "hello world"
            ),
        )
    except Exception as test_exception:
        addin.stop()
        raise test_exception
    return addin
