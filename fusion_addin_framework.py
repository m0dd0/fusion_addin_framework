"""
This addin definition is only for testing the framework itself.
It can be executed if the framework repository is put directly in the Addin
directory. In normal use this can be ignored and wont be recognized by Fuion360.
"""

import traceback
from pprint import pprint
import logging

import adsk.core, adsk.fusion, adsk.cam

# using reative imports because editable pip install doesnt work
from .tests import testcases
from . import fusion_addin_framework as faf

addins = []


def run(context):  # pylint:disable=unused-argument
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        faf.utils.create_logger(
            faf.__name__,
            [logging.StreamHandler(), faf.utils.TextPaletteLoggingHandler()],
        )

        logging.getLogger(faf.__name__).info(
            "started fusion_addin_framework testing addin"
        )

        all_testcases = [
            getattr(testcases, name)
            for name in dir(testcases)
            if name.startswith("test") and callable(getattr(testcases, name))
        ]

        global addins
        # results, addins = testcases.execute_cases(all_testcases)
        results, addins = testcases.execute_cases([testcases.test_custom_events])

        print("### RESULTS ###")
        pprint(dict(results))
        if all([r["passed"] for r in results.values()]):
            print("### PASSED ###")
        else:
            print("### FAILED ###")

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def stop(context):  # pylint:disable=unused-argument
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        global addins

        for addin in reversed(addins):
            if addin is not None:
                addin.stop()

        logging.getLogger(faf.__name__).info("stopped all addin instances")

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
