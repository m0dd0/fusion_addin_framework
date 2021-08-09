.. _examples:

Examples
========

The usage of this framework should be easy to understand by studying the examples below.

All the given examples assume that you cloned the `fusion_addin_framework
<https://github.com/m0dd0/fusion_addin_framework>`_ 
into the directory of your addin as explained :ref:`here<installation>` and the 
code is executed from the main-file of your addin.

`This repository
<https://github.com/m0dd0/SampleFusionAddin>`_ 
contains each of the shown examples in a seperate branch.


Simple addin
------------

The code below creates a very simple addin/command at the default location 
(Design workspace, Tools tab, Addin panel, button controlled).
The used workspace, panel and button are not explicitly defined and therefore the default 
values are used.
The next example will demonstrate how to specify the exact position of the control
which activates the command of your addin.
Note that the created button is not promoted by default and that a random
name will be used by default.

Instead of creating a execute command event handler we pass a function to the 
``AddinCommand`` class. This function will be executed by the framework as the notify
function of the commend event handler.
This concept will be demonstrated in more detail in another example.

.. code-block:: python 

    import adsk.core, adsk.fusion, adsk.cam, traceback
    from .fusion_addin_framework import fusion_addin_framework as faf


    cmd = None


    def say_hi(event_args: adsk.core.CommandEventArgs):
        adsk.core.Application.get().userInterface.messageBox("hi")


    def run(context):
        try:
            global cmd
            cmd = faf.AddinCommand(onExecute=say_hi)
        except:
            adsk.core.Application.get().userInterface.messageBox(
                "Failed:\n{}".format(traceback.format_exc())
            )


    def stop(context):
        try:
            cmd.addin.stop()
        except:
            adsk.core.Application.get().userInterface.messageBox(
                "Failed:\n{}".format(traceback.format_exc())
            )

Specify position of the addin
-----------------------------

To define the exact position of the command control in the userinterface you can 
use the wrapper classes as shown below.
By providing the Id of the already exisiting native Design Workspace, Solid Tab and Solid Panel
the control will be positioned correspondingly.
We set ``isPromoted=True`` so the control will appear in the Panel.

.. code-block:: python 

    import adsk.core, adsk.fusion, adsk.cam, traceback
    from .fusion_addin_framework import fusion_addin_framework as faf


    addin = None


    def say_hi(event_args: adsk.core.CommandEventArgs):
        adsk.core.Application.get().userInterface.messageBox("hi")


    def run(context):
        try:
            global addin
            addin = faf.FusionAddin()
            ws = faf.Workspace(parent=addin, id="FusionSolidEnvironment")
            tab = faf.Tab(parent=ws, id="SolidTab")
            panel = faf.Panel(parent=tab, id="SolidCreatePanel")
            control = faf.Control(parent=panel, isPromoted=True)
            cmd = faf.AddinCommand(parent=control, onExecute=say_hi, name="my command")
        except:
            adsk.core.Application.get().userInterface.messageBox(
                "Failed:\n{}".format(traceback.format_exc())
            )

    def stop(context):
        addin.stop()


As an alternative to the the notation above you can also use the following code which
internally results in exactly the same wrapper classes being instantiated.
This "dotted" style of creating the UI elements can be used in evry other example
as well as long as you dont need to add more than one child to a parent UI element.


.. code-block:: python

    import adsk.core, adsk.fusion, adsk.cam, traceback
    from .fusion_addin_framework import fusion_addin_framework as faf


    cmd = None


    def say_hi(event_args: adsk.core.CommandEventArgs):
        adsk.core.Application.get().userInterface.messageBox("hi")


    def run(context):
        try:
            global cmd
            cmd = (
                faf.FusionAddin()
                .workspace(id="FusionSolidEnvironment")
                .tab(id="SolidTab")
                .panel(id="SolidCreatePanel")
                .control(isPromoted=True)
                .addinCommand(onExecute=say_hi, name="my command")
            )
        except:
            adsk.core.Application.get().userInterface.messageBox(
                "Failed:\n{}".format(traceback.format_exc())
            )


    def stop(context):
        cmd.addin.stop()

.. _hirachy_example:

Command at a very custom position
---------------------------------
In the example above we positioned the control into an already existing panel.
Using the framework it is very simple to position the command control into a custom
panel or even into a custom tab.

To create a custom tab or panel you only need to pass a new unique id to the corresponding
wrapper class. 
If you pass "random" as id, a random id will be genreated and used.
In this example mostly the default values are used. However you can specify every 
other aspect by setting the arguments at initialization of the wrapper class.

In this example we also use one of included image "cubes" instead of the default "lightbulb"
image. 


.. code-block:: python

    import adsk.core, adsk.fusion, adsk.cam, traceback
    import logging

    from .fusion_addin_framework import fusion_addin_framework as faf


    addin = None


    def say_hi(event_args: adsk.core.CommandEventArgs):
        adsk.core.Application.get().userInterface.messageBox("hi")


    def run(context):
        try:
            global addin
            addin = faf.FusionAddin()
            ws = faf.Workspace(parent=addin, id="FusionSolidEnvironment")
            # passing the "random" as an id will generate an UUID, it would be also possible
            # to use a custom id like "MySuperCustomId1234"
            tab = faf.Tab(parent=ws, id="random", name="my tab")
            panel = faf.Panel(parent=tab, id="random", name="my panel")
            control = faf.Control(parent=panel, isPromoted=True, isPromotedByDefault=True)
            cmd = faf.AddinCommand(
                parent=control, onExecute=say_hi, name="my command", resourceFolder="cubes"
            )
        except:
            adsk.core.Application.get().userInterface.messageBox(
                "Failed:\n{}".format(traceback.format_exc())
            )


    def stop(context):
        addin.stop()

.. _handler_example:

Command with multiple connected handlers
----------------------------------------
In the previous examples we only used the execute event handler to simulate a 
very basic addin.
All other event handlers that can be connected to Fusions `Command
<https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-0550963a-ff63-4183-b0a7-a1bf0c99f821>`_ 
class are supported by the framework as well.
You can pass the corresponding notify-function as an argument to the ``faf.AddinCommand`` class.
Use the name of the event as attribute name. Optionally you can add an "on"-prefix 
to the attribute name.
``AddincComman(onExecute=my_func)`` is the same as ``AddinCommand(execute=my_func)``.

In the example below we use a subset of the possible event handlers to demonstrate
the usage of functions instead of command handlers.

As in the first example the addin will be positioned at the default position (Addin Panel).

.. code-block:: python

    import adsk.core, adsk.fusion, adsk.cam, traceback
    from .fusion_addin_framework import fusion_addin_framework as faf

    cmd = None


    def create_inputs(event_args: adsk.core.CommandCreatedEventArgs):
        event_args.command.commandInputs.addBoolValueInput("boolInputId", "my input", True)


    def say_hi(event_args: adsk.core.CommandEventArgs):
        adsk.core.Application.get().userInterface.messageBox("hi")


    def say_changed(event_args: adsk.core.InputChangedEventArgs):
        adsk.core.Application.get().userInterface.messageBox("input changed")


    def say_by(event_args: adsk.core.CommandCreatedEventArgs):
        adsk.core.Application.get().userInterface.messageBox("by")


    def run(context):
        try:
            global cmd
            cmd = faf.AddinCommand(
                name="my command",
                onExecute=say_hi,
                onCommandCreated=create_inputs,
                onInputChanged=say_changed,
                onDestroy=say_by,
            )
            # it is not necessary to use the "on"-prefix, the code below is equivalent
            # cmd = faf.AddinCommand(
            #     name="my command",
            #     execute=say_hi,
            #     commandCreated=create_inputs,
            #     inputChanged=say_changed,
            #     destroy=say_by,
            # )

        except:
            adsk.core.Application.get().userInterface.messageBox(
                "Failed:\n{}".format(traceback.format_exc())
            )


    def stop(context):
        cmd.addin.stop()



Checkbox controlled addin
-------------------------
Instead of a button you can also use a checkbox to activate your command.
You onyl need to specify ``control_type='checkbox'`` at the instantiation of the 
Control wrapper.

.. code-block:: python

    import adsk.core, adsk.fusion, adsk.cam, traceback
    from .fusion_addin_framework import fusion_addin_framework as faf


    addin = None


    def say_hi(even_args: adsk.core.CommandEventArgs):
        adsk.core.Application.get().userInterface.messageBox("hi")


    def run(context):
        try:
            global addin
            addin = faf.FusionAddin()
            workspace = faf.Workspace(addin)
            tab = faf.Tab(workspace, id="ToolsTab")
            panel = faf.Panel(tab, id="SolidScriptsAddinsPanel")
            # use a checkbox instead of a button
            control = faf.Control(panel, controlType="checkbox")
            cmd = faf.AddinCommand(control, name="my checkbox command", execute=say_hi)
        except:
            adsk.core.Application.get().userInterface.messageBox(
                "Failed:\n{}".format(traceback.format_exc())
            )


    def stop(context):
        addin.stop()


Addin with multiple controls
----------------------------
In some cases you might want to activate your command with different controls from
different locations in the UI.
You can achieve this by providing a list of parental controls to the ``faf.AddinCommand``
class.
All controls will share the same image and name.
The example belwo results in two buttons (in the addin panel and solid panel) which
both activate the same command.

.. code-block:: python

    import adsk.core, adsk.fusion, adsk.cam, traceback
    from .fusion_addin_framework import fusion_addin_framework as faf

    addin = None


    def say_hi(event_args: adsk.core.CommandEventArgs):
        adsk.core.Application.get().userInterface.messageBox("hi")


    def run(context):
        try:
            global addin
            addin = faf.FusionAddin()
            ws = faf.Workspace(parent=addin, id="FusionSolidEnvironment")

            solid_tab = faf.Tab(parent=ws, id="SolidTab")
            tools_tab = faf.Tab(parent=ws, id="ToolsTab")

            solid_panel = faf.Panel(parent=solid_tab, id="SolidCreatePanel")
            addin_panel = faf.Panel(parent=tools_tab, id="SolidScriptsAddinsPanel")

            control_1 = faf.Control(parent=solid_panel, isPromoted=True)
            control_2 = faf.Control(parent=addin_panel, isPromoted=True)

            # this command has two parental controls and can therfore be acticated from
            # different postions in the UI
            cmd = faf.AddinCommand(
                parent=[control_1, control_2], onExecute=say_hi, name="my command"
            )
        except:
            adsk.core.Application.get().userInterface.messageBox(
                "Failed:\n{}".format(traceback.format_exc())
            )


    def stop(context):
        addin.stop()


Accessing attributes
--------------------
The examples above set all attributes at initialization of the wrapper class.
With the instantiated wrapper instances you can acess and set **all** attributes 
that the corresponding wrapped instance owns.
These attributes are not documented in the reference of this framework but can be
looked up in the API documentation of the wrapped class.   

.. code-block:: python

    import adsk.core, adsk.fusion, adsk.cam, traceback
    from .fusion_addin_framework import fusion_addin_framework as faf

    addin = None


    def say_hi(event_args: adsk.core.CommandEventArgs):
        adsk.core.Application.get().userInterface.messageBox("hi")


    def run(context):
        try:
            global addin
            addin = faf.FusionAddin()

            # access the attributes and methods of the workspace instance
            ws = faf.Workspace(parent=addin, id="FusionSolidEnvironment")
            print(ws.parent)
            print(ws.addin)
            print(ws.isActive)
            print(ws.name)
            print(ws.objectType)
            print(ws.productType)
            print(ws.resourceFolder)
            print(ws.toolClipFilename)
            ws.activate()
            # ...

            tab = faf.Tab(parent=ws, id="SolidTab")
            print(tab.parent)
            print(tab.id)
            print(tab.index)
            print(tab.isActive)
            print(tab.name)
            print(tab.objectType)
            tab.activate()
            # ...

            panel = faf.Panel(parent=tab, id="SolidCreatePanel")
            print(panel.parent)
            print(panel.controls)
            print(panel.id)
            print(panel.isValid)
            print(panel.isVisible)
            print(panel.name)
            print(panel.indexWithinTab("SolidTab"))
            # ...

            button = faf.Control(parent=panel, isPromoted=True)
            print(button.parent)
            print(button.commandDefinition)
            print(button.id)
            print(button.isPromoted)
            button.isPromoted = False
            button.isPromotedByDefault = False
            print(button.isVisible)
            print(button.objectType)
            print(button.parent)
            # ...

            cmd = faf.AddinCommand(parent=button, onExecute=say_hi, name="my command")
            print(cmd.parent)
            print(cmd.controlDefinition)
            print(cmd.isVisible)
            print(cmd.id)
            print(cmd.isNative)
            print(cmd.resourceFolder)
            # ...
        except:
            adsk.core.Application.get().userInterface.messageBox(
                "Failed:\n{}".format(traceback.format_exc())
            )
            

    def stop(context):
        addin.stop()


Addin with dropdowns
--------------------
The creation and use of (arbitrarily deeply nested) dropdowns is also supported by the 
framework.
A Dropdown follow the same parent-child relationship as the other wrapper classes do.
The only difference is that a dropdown can be a child of another dropdown instance.

In this exampled we use the "dotted" notation to create 4 nested dropdowns.

.. code-block:: python

    import adsk.core, adsk.fusion, adsk.cam, traceback
    from .fusion_addin_framework import fusion_addin_framework as faf

    cmd = None


    def say_hi(event_args: adsk.core.CommandEventArgs):
        adsk.core.Application.get().userInterface.messageBox("hi")


    def run(context):
        try:
            global cmd
            cmd = (
                faf.Workspace()
                .tab()
                .panel()
                .dropdown()
                .dropdown()
                .dropdown()
                .dropdown()
                .control()
                .addinCommand(execute=say_hi)
            )
        except:
            adsk.core.Application.get().userInterface.messageBox(
                "Failed:\n{}".format(traceback.format_exc())
            )


    def stop(context):
        cmd.addin.stop()


Using the module logger
-----------------------
The frameworks contains its own logger which logs different informations on the 
creation of addins/commands and the execution of handlers.
These information can be very useful if you are debugging your addin.
The example below shows how to use the logger.
Additionaly the framework provides a logging handler which outputs the logged data
to Fusions integrated text pallette.


.. code-block:: python

    import adsk.core, adsk.fusion, adsk.cam, traceback
    from .fusion_addin_framework import fusion_addin_framework as faf

    import logging

    addin = None


    def say_hi(event_args: adsk.core.CommandEventArgs):
        adsk.core.Application.get().userInterface.messageBox("hi")


    def run(context):
        try:
            logger = logging.getLogger(faf.__name__)
            logger.setLevel(logging.DEBUG)
            stream_handler = logging.StreamHandler()
            logger.addHandler(stream_handler)
            palette_handler = faf.utils.TextPaletteLoggingHandler()
            logger.addHandler(palette_handler)

            # alternativly you can use this utiltiy function
            # faf.utils.create_logger(
            #     faf.__name__,
            #     [logging.StreamHandler(), faf.utils.TextPaletteLoggingHandler()],
            # )

            global addin
            addin = faf.FusionAddin()
            ws = faf.Workspace(parent=addin, id="FusionSolidEnvironment")
            tab = faf.Tab(parent=ws, id="SolidTab")
            panel = faf.Panel(parent=tab, id="SolidCreatePanel")
            control = faf.Control(parent=panel, isPromoted=True)
            cmd = faf.AddinCommand(parent=control, onExecute=say_hi, name="my command")
        except:
            adsk.core.Application.get().userInterface.messageBox(
                "Failed:\n{}".format(traceback.format_exc())
            )


    def stop(context):
        addin.stop()
