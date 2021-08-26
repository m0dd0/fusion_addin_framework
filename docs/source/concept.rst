Concept
=======

This section tries to point out the concepts used in the framework and how they 
differ from the native Fusion API.
These information are not necessarily needed to use the framework as the :ref:`examples <examples>` 
should make its functionality understandable already.

The framework provides wrapper classes around some of Fusions 
API classes to simplify the access to the corresponding wrapped instance.
Especially these wrapper classes are:

 - ``fusion_addin_framework.Workspace`` which wraps around ``adsk.core.Workspace``
 - ``fusion_addin_framework.Panel`` which wraps around ``adsk.core.ToolbarPanel``
 - ``fusion_addin_framework.Tab`` which wraps around ``adsk.core.ToolbarTab``
 - ``fusion_addin_framework.Dropdown`` which wraps around ``adsk.core.Dropdown``
 - ``fusion_addin_framework.Control`` which wraps around ``adsk.core.ToolbarControl``
 - ``fusion_addin_framework.AddinCommand`` which wraps around ``adsk.core.CommandDefinition`` and ``adsk.core.ControlDefinition``

Besides the listed wrapper classes a ``fusion_addin_framework.FusionAddin`` class acts as an 
entry point and keeps track of all created UI-related instances and enables you
to clean up your addin by simply calling ``addin.stop()`` in the ``stop(context)``
function of your addin (instead of deleting each created instacne seperately).

Fusions Userinterface is hierachical structured:
A Workspace contains Panels, a Panel contains Tabs, a Tab contains controls and so on. 
This hirachy is represented by the wrapper classes as you can intantiate them with
an instance of a parental wrapper class.
The full hierachy (or possible parent-child-relation) are visualized in the image 
below.

.. image:: ./images/relationships.svg

In contrast to the native API classes you can instantiate the wrapper classes by passing
a parent wrapper instance as ``parent`` attribute and other attributes which define their appearance.
This makes creating UI-related instance more declarative.
All attributes are optional. 
If you dont set them, a default value will be used.
This also applies for the ``parent`` attribute. 
So, for example, if you just create a tab without any parameters passed (``tab = faf.Tab()``)
it will be created as a child of a panel instance where only default parameters
were used. 

See :ref:`this example <_hirachy_example>` for a better understanding of the discussed concept.

After a wrapper class got instantiated you can use the instance as they would 
be "normal" instances of their corresponding class in the ntaive API. 
All attribute accesses and method calls will be redirected to the wrapped object 
(if such a method or attribute exists).

If an wrapper class is instantiated with an ``id`` that already existsts,
all other parameters provided to the ```__init__`` method are ignored.
You can still set these parameters after initiliazation by setting the corresponding 
attribute value.

When using the API without the frameowrk you create event handlers which you can 
connect to events.
If the event occurs the ``notify()`` method of the connected event handler will 
get called.
In most cases you do not change the event handlers at any time after you have connected
them for the first time.
Instead of using handlers which comes with boilerplate code, using the frameowrk, 
you can simply pass functions to an instance of the ``fusion_addin_framework.AddinCommand`` class.
These function will get called by the frameowrk internally as the notify function 
of generic event handlers.
To provide a function which will get called at the execute event, you instantiate 
the AddinCommand class with ``cmd = AddinCommand(execute=my_func)``.
``my_func`` will be used as the ``notify()`` of an ``CommandEventHandler``.
Therfore it must also accept the ``adsk.core.CommandEventArgs`` as the first and
only positional argument.
All events that are associated with Fusions `Command class
<https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-0550963a-ff63-4183-b0a7-a1bf0c99f821>`_
can be set at initialization of the ``AddinCommand`` class.

See :ref:`this example <_handler_example>` for more information.


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