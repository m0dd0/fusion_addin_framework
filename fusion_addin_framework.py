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
from .fusion_addin_framework import py_utils
from .fusion_addin_framework import fusion_utils

addins = []


def run(context):  # pylint:disable=unused-argument
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        py_utils.create_logger(
            faf.__name__,
            [logging.StreamHandler(), fusion_utils.TextPaletteLoggingHandler()],
        )

        logging.getLogger(faf.__name__).info(
            "started fusion_addin_framework testing addin"
        )

        global addins

        results, addins = testcases.execute_cases(
            [
                testcases.test_default_button,
                testcases.test_hello_world,
                # testcases.test_addin_properties,
                # testcases.test_custom_workspace,
            ]
        )

        pprint(dict(results))

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
            addin.stop()

        logging.getLogger(faf.__name__).info("stopped all addin instances")

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
