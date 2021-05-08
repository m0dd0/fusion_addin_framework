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
                testcases.test_hello_world_button,
                testcases.test_hello_world_button_dotted,
                testcases.test_hello_world_button_no_parents,
                testcases.test_hello_world_checkbox,
                testcases.test_hello_world_checkbox_dotted,
                testcases.test_hello_world_checkbox_no_parents,
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

        faf.stop_all()
        # for addin in reversed(addins):
        #     if addin is not None:
        #         addin.stop()

        logging.getLogger(faf.__name__).info("stopped all addin instances")

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
