Examples
========

Using this framework 
Creating a very simple command at the default location () with the default values.

.. code-block:: python 

    import fusion_addin_framework as faf
    import adsk.core, adsk.fusion

    cmd = None

    def say_hi():
        adsk.core.Application.get().userInterface.messageBox("hi")

    def run(context):
        global cmd
        cmd = faf.ButtonCommand(onExecute=say_hi)
        
    def stop(context):
        cmd.addin.stop()

Creating a button controlled command at a very specific location:

.. code-block:: python 

    import fusion_addin_framework as faf
    import adsk.core, adsk.fusion

    cmd = None

    def say_hi():
        adsk.core.Application.get().userInterface.messageBox("hi")

    def run(context):
        global cmd
        addin = Addin()
        ws = Workspace(parent=addin, id='')
        tab = Tab()
        cmd = faf.ButtonCommand(onExecute=say_hi)
        
    def stop(context):
        cmd.addin.stop()
