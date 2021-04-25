"""
This addin definition is only for testing the framework itself.
It can be executed if the framework repository is put directly in the Addin
directory. In normal use this can be ignored and wont be recognized by Fuion360.
"""

import traceback
from pprint import pprint
import logging

import adsk.core, adsk.fusion, adsk.cam

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
        # TODO text command handler

        faf.test_logger()

        global addins

        # results, addins = testcases.execute_cases(
        #     [
        #         testcases.test_default_button,
        #         testcases.test_hello_world,
        #     ]
        # )

        # pprint(dict(results))

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

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
