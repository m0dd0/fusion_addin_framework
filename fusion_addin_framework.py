# import adsk.core, adsk.fusion, adsk.cam, traceback

# def run(context):
#     ui = None
#     try:
#         app = adsk.core.Application.get()
#         ui  = app.userInterface
#         ui.messageBox('Hello addin')

#     except:
#         if ui:
#             ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# def stop(context):
#     ui = None
#     try:
#         app = adsk.core.Application.get()
#         ui  = app.userInterface
#         ui.messageBox('Stop addin')

#     except:
#         if ui:
#             ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

from . import fusion_addin_framework as faf

global ws


def run(context):
    try:
        ws = faf.Workspace(id="Design")
        tab = faf.Tab(parent_workspace=ws)

    except:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox("Stop addin")

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
