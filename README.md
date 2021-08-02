# Fusion Addin Framework
Fusion360 is a great CAE software and also provides an comprehensive API for 
customizing and extending the software to your needs.
While automating your tasks with the Fusion API by coding scripts is mostly 
straightforward, turning these scripts into addins which can be executed via 
the GUI requires an considerable amount of boilerplate code.
This framework aims at simplifying the creation of addins by providing wrapper 
classes around Fusions GUI related API classes like workspace, tab, panel etc.
Using this approach no functionalities of the 'original' API gets lost while some 
additions allow a much cleaner and inutitiv creation of addins (at least in my 
oppinion).  
Also the event handler concept is substituated and python functions as first 
level object are used instead to further simlify the creation of addins without
sacrifying any flexibility.

Checkout the [documentation](https://fusion-addin-framework.readthedocs.io/en/latest/) for more information.


## Installation
The easiest and recommended way to use this framework is to **clone  
the framework into the same directory where your addin code is located** 
(or use it as a git submodule) and use relative imports.
In this case your folder structure should look like this:
```
Addins/
├─ <YourAddinName>/
│  ├─ .vscode/
│  ├─ .env
│  ├─ <YourAddinName>.py
│  ├─ <YourAddinName>.manifest
│  ├─ fusion_addin_framework/
|  |  ├─ setup.py
|  |  ├─ ...
|  |  ├─ fusion_addin_framework/
├─ ...
```
In the main-file of your addin (`<YourAddinName>.py`) you can then use 
`from .fusion_addin_framework import fusion_addin_framework as faf`
to import the framework and access its classes.

## Examples
The use of the framework and its advantages can be demonstrated with a example.
More examples can be found in the [documentation](https://fusion-addin-framework.readthedocs.io/en/latest/).

The code below creates a button in the Solid Panel by using wrapper classes.
Instead of using event handlers the notify function of the execute-event is passed
to the `AddinCommand` class.
```python

import adsk.core, adsk.fusion, adsk.cam, traceback

from .fusion_addin_framework import fusion_addin_framework as faf


# specify position of addin
addin = None


def say_hi(event_args: adsk.core.CommandEventArgs):
    adsk.core.Application.get().userInterface.messageBox("hi")


def run(context):
    global addin
    addin = faf.FusionAddin()
    ws = faf.Workspace(parent=addin, id="FusionSolidEnvironment")
    tab = faf.Tab(parent=ws, id="SolidTab")
    panel = faf.Panel(parent=tab, id="SolidCreatePanel")
    control = faf.Control(parent=panel, isPromoted=True)
    cmd = faf.AddinCommand(parent=control, onExecute=say_hi, name="my command")


def stop(context):
    addin.stop()
```

The wrapper classes can also be used to create a button in a custom panel and tab:

```python
import adsk.core, adsk.fusion, adsk.cam, traceback

from .fusion_addin_framework import fusion_addin_framework as faf


# Addin at a very custom position
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
```