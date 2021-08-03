General information
===================


Introduction
------------
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

The easiest way to understand the usage of the framework is probably to checkout 
the :ref:`example section <examples>`. 
Please note that this documentation assumes that you are already somewhat familiar
with the Fusion API and covers only the use of the framework itself.


.. _installation:

Installation
------------
The easiest and recommended way to use this framework is to **clone  
the framework into the same directory where your addin code is located** 
(or use it as a git submodule) and use relative imports.
In this case your folder structure should look like this:

::

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

In the main-file of your addin (``<YourAddinName>.py``) you can then use 
``from .fusion_addin_framework import fusion_addin_framework as faf``
to import the framework and access its classes.

..
   However it is also possible to pip-install the framework from PyPI by executing 
   ``pip install fusion_addin_framework`` 
   and use an absolute imports import.
   If you go for this installation method you need to be aware that Fusion360 runs 
   addins in its 'own' python environment.
   This means that you need to install the package to Fusions python environment and
   not to your default python environment or an virtual environment.
   Besides this caveat Fusion will reset its python environment at every update 
   so your installed libraries, including this framework, are no longer available and 
   your will need to reinstall them manually.
   Because of the mentioned pitfalls **it is not recommended to install the framework via pip**.
   You can read more about this behavior in `this
   <https://forums.autodesk.com/t5/fusion-360-api-and-scripts/to-install-python-modules/td-p/5777176>`_ 
   forum thread.


Basic idea and concept
----------------------
This section tries to point out the concepts used in the frameowrk and how they 
differ from the native Fusion API.
This information is not necessarily needed to use the framework as the :ref:`examples <examples>` 
should make its functionality clear.

As mentioned before the framework provides wrapper classes around some of Fusions 
API classes.
Especially these are:

 - ``fusion_addin_framework.Workspace`` wraps around ``adsk.core.Workspace``
 - ``fusion_addin_framework.Panel`` wraps around ``adsk.core.ToolbarPanel``
 - ``fusion_addin_framework.Tab`` wraps around ``adsk.core.ToolbarTab``
 - ``fusion_addin_framework.Dropdown`` wraps around ``adsk.core.Dropdown``
 - ``fusion_addin_framework.Control`` wraps around ``adsk.core.ToolbarControl``
 - ``fusion_addin_framework.AddinCommand`` wraps around ``adsk.core.commandDefinition`` and ``adsk.core.ControlDefinition``

Besides the wrapper classes a ``fusion_addin_framework.FusionAddin`` class acts as an 
entry point and keeps track of all created and UI-related instances and enables you
to clean up your addin by simply calling ``addin.stop()`` in the ``stop(context)``
function of your addin.

Fusions Userinterface is hierachical structured:
A Workspace contains Panels, a Panel contains Tabs, a Tab contains controls and so on. 
This hirachy is contained in the wrapper classes as you can intantiate them with
an instance of a parental wrapper class.
The full hierachy (or possible parent-child-relation) are visualized in the image 
below.

.. image:: ./images/relationships.svg

In contrast to the API classes you can instantiate the wrapper classes by passing
a parent wrapper instance as ``parent`` attribute and other attributes that define their appearance.
This makes creating UI-related instance more declarative.
All attributes are optional. 
If you dont set them, a default value will be used.
This also applies for the ``parent`` attribute. 
So, for example, if you just create a tab without any parameters passed (``tab = faf.Tab()``)
it will be created as a child of a panel instance where only default parameters
were used. 

After one of the wrapper classes got instantiated you can use them as they would 
be "normal" instances of their corresponding class in the API. 
All attribute and function calls will be redirected to the wrapped object.

If an wrapper class is instantiated with an id that already existsts,
all other parameters provided to the init method are ignored.
You can still set these parameters after initiliazation by setting the corresponding 
attribute value.

When using the API without the frameowrk you create event handlers which you can 
connect to events.
If the event occurs the ``notify()`` method of the connected event handler will 
get called.
In most cases you do not change the event handlers at any time after you have connected
them for the first time.
Instead of using handlers which comes with boilerplate code, using the frameowrk, 
you can simply pass functions itself to ìnstances of the ``AddinCommand`` class.
These function will be called by the frameowrk internally from the notify function 
of generic event handlers.
To provide a function which will get called at the execute event, you instantiate 
the AddinCommand class with ``cmd = AddinCommand(execute=my_func)``.
``my_func`` will be used as the ``notify()`` of an ``CommandEventHandler``.
Therfore it must also accept the ``adsk.core.CommandEventArgs`` as the first and
only positional argument.
All events that are associated with Fusions `Command class
<https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-0550963a-ff63-4183-b0a7-a1bf0c99f821>`_
can be set at initialization of the ``AddinCommand`` class.


Default images
--------------
For some of the UI-classes you can provide the path to an image or image folder 
(called ``resourceFolder`` in the API) for customizing their appearance.
This framework provides some default images you can choose from.
Instead of providing a path you can simply pass the name of one of the default 
images.  
The following default images are available:

 - "addon"
 - "cad"
 - "cubes"
 - "gear"
 - "lightbulb"
 - "shapes"
 - "tools"
 - "transparent" 

Please note that no sepereate images are provided for the dark and disabled
image option so a button will look the same in every state.

All these default icons were made by Freepik from www.flaticon.com.
If you want to make your addin publicly available and use one of the default images 
from this framework you need to attribute the author of these images. 
See `this
<https://support.flaticon.com/hc/en-us/articles/207248209-How-I-must-insert-the-attribution->`_
article for more details. 


..
   Note on naming convention
   -------------------------
   For consistency with the Fusion API all interfaces of the wrapper classes are in camelCase.
   For all internal variables and utility function, the python naming convention 
   (snake_case for variabels and functions and UpperCamelCase for classes) is used. 


..
   API errors and undocumented behavior
   ------------------------------------
   The commandDefinition.tooltip property will alway return an empty string.
   Changes to the attribute will be reflected in the UI though.

   Changing the resourceFolder of an commandDefinition will first become visible If
   the button got unpinned and pinned again from the toolbar.