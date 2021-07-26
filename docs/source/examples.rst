Examples
========

The usage of this framework should be easy to unnderstand by having a look at at 
the examples below.

All the given xamples assume that you cloned the `fusion_addin_framework<>`_ into
the directory of your addin as explained `here<>_`.


Simplest possible addin
-----------------------

Creating a very simple command at the default location () with only on the default values.

.. code-block:: python 

    import fusion_addin_framework as faf
    import adsk.core, adsk.fusion

    cmd = None

    def say_hi():
        adsk.core.Application.get().userInterface.messageBox("hi")

    def run(context):
        global cmd
        cmd = faf.AddinCommand(onExecute=say_hi)
        
    def stop(context):
        cmd.addin.stop()

Specify position of the addin
-----------------------------

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

Alternativly to the the notation above xou could also use the following code which
results in exactly the same wrapper 
This "dotted" style of creating the UI elements could be used in evry other example
as well as long as you dont need to add more than one child to a parent UI element.

Addin at a very custom position
-------------------------------

Addin with many connected handlers
----------------------------------

Checkbox controlled addin
-------------------------

Addin with multiple controls
----------------------------

Addin using dropdowns
---------------------