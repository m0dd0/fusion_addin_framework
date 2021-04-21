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

addins = None


def run(context):  # pylint:disable=unused-argument
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # print([logging.getLogger(name) for name in logging.root.manager.loggerDict])

        logger = logging.getLogger(faf.__name__)  # .setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        # create formatter and add it to the handler
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        # add the handler to the logger
        logger.addHandler(handler)
        # logging.basi

        global addins

        results, addins = testcases.execute_cases(
            [
                # testcases.test_default_button,
                testcases.test_hello_world,
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

        for addin in addins:
            addin.stop()

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
