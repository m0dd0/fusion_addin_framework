"""
This addin definition is only for testing the framework itself.
It can be executed if the framework repository is put directly in the Addin
directory. In normal use this can be ignored and wont be recognized by Fuion360.
"""

import traceback
from pprint import pprint

import adsk.core, adsk.fusion, adsk.cam

from .tests import testcases


def run(context):  # pylint:disable=unused-argument
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        results = testcases.execute_cases(
            [
                testcases.test_default_button,
            ]
        )

        # ui.messageBox(str(results))
        pprint(dict(results))

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def stop(context):  # pylint:disable=unused-argument
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
