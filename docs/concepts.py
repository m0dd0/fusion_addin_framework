# ### VERERBUNG ###


# class MyCommand(faf.CommandBase):
#     pass


# cmd = MyCommand()
# cmd.controls = []


# ### HTML STYLE ###


# faf.Workspace(
#     id="Solid",
#     children=[
#         faf.Tab(
#             id="Tools",
#             children=[
#                 faf.Panel(
#                     id="Addin",
#                     children=[
#                         faf.Command(),
#                     ],
#                 ),
#             ],
#         ),
#     ],
# ### CHAINED STYLE ###

# faf.Workspace(id="Solid").tab(id="Tools").panel(id="Addin").buttondefintion(
#     id="asdfasdfasdfasdfasdf"
# ).addCommand()


# ### COMMAND CENTERED ###

# cmd = faf.Command(controls=[])


# ### ORIGINAL ###

# import traceback
# import adsk.core
# import adsk.fusion

# handlers = []


# class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
#     def __init__(self):
#         super().__init__()

#     def notify(self, args):
#         try:
#             args = adsk.core.CommandCreatedEventArgs.cast(args)
#             cmd = args.command

#             on_execute = MyExecuteHandler()
#             cmd.execute.add(on_execute)
#             handlers.append(on_execute)

#             inputs = cmd.commandInputs
#             inputs.addBoolValueInput("bool_input_id", "bool", True, "", False)
#         except:
#             print("Failed:\n{}".format(traceback.format_exc()))


# class MyExecuteHandler(adsk.core.CommandEventHandler):
#     def __init__(self):
#         super().__init__()

#     def notify(self, args):
#         try:
#             args = adsk.core.CommandEventArgs.cast(args)

#         except:
#             print("Failed:\n{}".format(traceback.format_exc()))


# def run():
#     app = adsk.core.Application.get()
#     ui = app.userInterface

#     on_command_created = MyCommandCreatedHandler()
#     handlers.append(on_command_created)

#     workspace = ui.workspaces.itemById("Solid")
#     tab = workspace.toolbarTabs.itemById("Tools")
#     panel = tab.toolbarPanels.itemById("Addins")

#     cmd_def = ui.commandDefinitions.addButtonDefinition(
#         "cmd_def_id", "cmd name", "tooltip"
#     )
#     cmd_def.commandCreated.add(on_command_created)

#     # cmd_def.controlDefinition # specifying control more accurately

#     panel.controls.addCommand(cmd_def)


# def stop():
#     pass
