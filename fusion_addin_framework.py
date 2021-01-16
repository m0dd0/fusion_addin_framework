import adsk.core, adsk.fusion, adsk.cam, traceback

_app = None
_ui = None
_root = None

_to_delete = []

_handlers = []


class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            print("created")
            args = adsk.core.CommandCreatedEventArgs.cast(args)
            cmd = args.command

            on_input_changed = MyInputChangedHandler()
            cmd.inputChanged.add(on_input_changed)
            _handlers.append(on_input_changed)

            on_execute_preview = MyCommandExecutePreviewHandler()
            cmd.executePreview.add(on_execute_preview)
            _handlers.append(on_execute_preview)

            on_execute = MyExecuteHandler()
            cmd.execute.add(on_execute)
            _handlers.append(on_execute)

            on_destroy = MyCommandDestroyHandler()
            cmd.destroy.add(on_destroy)
            _handlers.append(on_destroy)

            inputs = cmd.commandInputs
            inputs.addBoolValueInput("bool_input_id", "bool", True, "", False)

        except:
            print("Failed:\n{}".format(traceback.format_exc()))


class MyInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            args = adsk.core.InputChangedEventArgs.cast(args)
            print("input changed")

        except:
            print("Failed:\n{}".format(traceback.format_exc()))


class MyCommandExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            print("preview")
            args = adsk.core.CommandEventArgs.cast(args)

        except:
            print("Failed:\n{}".format(traceback.format_exc()))


class MyExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            print("execute")
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            _ui.messageBox("executing")

        except:
            print("Failed:\n{}".format(traceback.format_exc()))


class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            print("destroy")
            args = adsk.core.CommandEventArgs.cast(args)

        except:
            print("Failed:\n{}".format(traceback.format_exc()))


def run(context):
    global _app
    global _ui
    global _root
    global _to_delete
    try:
        print("run")

        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        _root = adsk.fusion.Design.cast(_app.activeProduct).rootComponent

        # creating the created handler for the command defintion
        on_command_created = MyCommandCreatedHandler()
        _handlers.append(on_command_created)

        # getting the position in the ui.
        ws = _ui.workspaces.itemById("FusionSolidEnvironment")
        tab = ws.toolbarTabs.itemById("ToolsTab")
        panel = tab.toolbarPanels.add("my_panel_id", "My Panel")
        panel2 = tab.toolbarPanels.add("my_panel2_id", "My Panel2")
        _to_delete.append(panel)

        cmd_def = _ui.commandDefinitions.addButtonDefinition(
            "button_cmd_def_id",
            "cmd_def_name",
            "tooltip",
            r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\fusion_addin_framework\fusion_addin_framework\src\defaults\default_images\lightbulb",
        )
        cmd_def.commandCreated.add(on_command_created)
        _to_delete.append(cmd_def)

        cmd_ctrl = panel.controls.addCommand(cmd_def)
        _to_delete.append(cmd_ctrl)
        cmd_ctrl2 = panel2.controls.addCommand(cmd_def)
        _to_delete.append(cmd_ctrl)

        print(panel.controls.itemById("button_cmd_def_id"))
        print(_ui.commandDefinitions.itemById("button_cmd_def_id"))
    except:
        print("Failed:\n{}".format(traceback.format_exc()))


def stop(context):
    try:
        print("stop")

        _to_delete.pop().deleteMe()
        for elem in reversed(_to_delete):
            elem.deleteMe()

    except:
        print("Failed:\n{}".format(traceback.format_exc()))
