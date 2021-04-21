from collections import defaultdict
from time import perf_counter
import traceback

from .. import fusion_addin_framework as faf


def execute_cases(cases):
    results = defaultdict(dict)
    for case in cases:
        try:
            start = perf_counter()
            case()
            results[case.__name__]["elapsed_time"] = perf_counter() - start
            results[case.__name__]["passed"] = True
            results[case.__name__]["traceback"] = ""
        except:
            results[case.__name__]["elapsed_time"] = -1
            results[case.__name__]["passed"] = False
            print(case.__name__, "#################################")
            print(traceback.format_exc())
            # results[case.__name__]["traceback"] = "".join(traceback.format_exc())

    return results


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