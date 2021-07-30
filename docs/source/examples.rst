.. _examples:

Examples
========

The usage of this framework should be easy to unnderstand by having a look at at 
the examples below.

All the given examples assume that you cloned the `fusion_addin_framework
<https://github.com/m0dd0/fusion_addin_framework>`_ 
into the directory of your addin as explained :ref:`here<installation>` and the 
code is executed from the main-file of your addin.


Simplest possible addin
-----------------------

Creating a very simple addin/command at the default location 
(Design-workspace, Tools-tab, Addin-panel, button controlled).
The Workspace, Panel and Button are not explicitly defined and therefore the default 
values are used.
The next example will demonstrate how to specify the exact position of the Control
which activates the command of your addin.
Note that the created button is not promoted by default.

When clicking 

.. code-block:: python 

    import adsk.core, adsk.fusion
    from .fusion_addin_framework import  as faf

    cmd = None

    def say_hi(cmd_args: adsk.core.):
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

Using the module logger
-----------------------