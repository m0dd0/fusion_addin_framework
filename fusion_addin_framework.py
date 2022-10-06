"""
This addin definition is only for testing the framework itself.
It can be executed if the framework repository is put directly in the Addin
directory. In normal use this can be ignored and wont be recognized by Fuion360.
"""

import traceback
import logging
from collections import defaultdict
from time import perf_counter
from typing import Dict, Union

import adsk.core, adsk.fusion, adsk.cam

from .tests import testcases
from . import fusion_addin_framework as faf

# a list or a single test function to test
# if a single testfunction is testes the addin.stop method is called at leaving addin
# if multiple testfunctions are provided we stop the addin immideately after the test
# which created it got executed.
TESTCASES = testcases.ALL_CASES
# TESTCASES = [testcases.test_thread_event_decorator]


def format_results(result_dict: Dict[str, Dict[str, Union[str, float]]]) -> str:
    """Gives a nice summarizing string of the results of the tests.

    Args:
        result_dict (Dict): The  dict containing all restults of the test mapped by their names.

    Returns:
        str: The formatted string.
    """
    # pprint(dict(results), width=200)
    formatted_str = "### RESULTS ###"

    formatted_str += f"\n{'test name':<50}{'elapsed time':<15}exception"
    for test_name, test_result in result_dict.items():
        formatted_str += f"\n{test_name:<50}"
        formatted_str += f"{str(round(test_result['elapsed_time'],5)):<15}"
        formatted_str += f"{type(test_result['exception']).__name__}"

    if all([r["exception"] is None for r in result_dict.values()]):
        formatted_str += "\n### PASSED ###"
    else:
        formatted_str += "\n### FAILED ###"

    return formatted_str


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

        results = defaultdict(dict)

        for case in TESTCASES:
            print(f"{f' {case.__name__} ':{'#'}^{60}}")

            start = perf_counter()

            thrown_exception = None
            formatted_traceback = None

            try:
                case()
            except Exception as test_exception:
                thrown_exception = test_exception
                formatted_traceback = traceback.format_exc()

            results[case.__name__]["elapsed_time"] = perf_counter() - start
            results[case.__name__]["exception"] = thrown_exception
            results[case.__name__]["traceback"] = formatted_traceback

            if formatted_traceback is not None:
                print(formatted_traceback)

            # if we only had one testcase we mostly want to analyse the result in fusion
            # and therfore we shouldnt stop the addin directly after the test
            if len(TESTCASES) > 1:
                faf.stop()

        print(format_results(results))

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def stop(context):  # pylint:disable=unused-argument
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        faf.stop()

        logging.getLogger(faf.__name__).info("stopped all addin instances")

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
