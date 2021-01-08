import adsk.core


class _CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            print("created")
            args = adsk.core.CommandCreatedEventArgs.cast(args)
            cmd = args.command

            on_execute = _ExecuteHandler()
            cmd.execute.add(on_execute)
            _handlers.append(on_execute)

            inputs = cmd.commandInputs
            inputs.addBoolValueInput("bool_input_id", "bool", True, "", False)

        except:
            print("Failed:\n{}".format(traceback.format_exc()))


class _ExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            _ui.messageBox("executing")

        except:
            print("Failed:\n{}".format(traceback.format_exc()))
