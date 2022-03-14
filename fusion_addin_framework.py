"""
This addin definition is only for testing the framework itself.
It can be executed if the framework repository is put directly in the Addin
directory. In normal use this can be ignored and wont be recognized by Fuion360.
"""

import traceback
from pprint import pprint
import logging
from collections import defaultdict
from time import perf_counter

import adsk.core, adsk.fusion, adsk.cam

from .tests import testcases
from . import fusion_addin_framework as faf

# a list or a single test function to test
# if a single testfunction is testes the addin.stop method is called at leaving addin
# if multiple testfunctions are provided we stop the addin immideately after the test
# which created it got executed.
# TESTCASES = testcases.ALL_CASES
TESTCASES = [testcases.test_custom_event]


addin = None


def run(context):  # pylint:disable=unused-argument
    ui = None
    try:
        global addin
        app = adsk.core.Application.get()
        ui = app.userInterface

        faf.utils.create_logger(
            faf.__name__,
            [logging.StreamHandler(), faf.utils.TextPaletteLoggingHandler()],
        )

        logging.getLogger(faf.__name__).info(
            "started fusion_addin_framework testing addin"
        )

        results = defaultdict(dict)
        for case in TESTCASES:
            try:
                print(f"{f' {case.__name__} ':{'#'}^{60}}")
                start = perf_counter()
                addin = case()
                results[case.__name__]["elapsed_time"] = perf_counter() - start
                results[case.__name__]["passed"] = True
            except:
                results[case.__name__]["elapsed_time"] = -1
                results[case.__name__]["passed"] = False
                print(traceback.format_exc())
            try:
                if len(TESTCASES) > 1:
                    addin.stop()
                    addin = None
            except:
                pass

        print("### RESULTS ###")
        pprint(dict(results), width=200)
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

        if addin is not None:
            addin.stop()

        logging.getLogger(faf.__name__).info("stopped all addin instances")

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
