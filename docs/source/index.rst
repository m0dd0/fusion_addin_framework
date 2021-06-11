Introduction
============
Here will be some introduction to the frameowrk describing it purpose etc.

Installation
------------
The recommended 
Fusion360 runs addins in its own python environment.
If your addins relies on additional libraries (like this framework) you could 
simply pip-install these libraries to this environment.
However, Fusion will reset this environment at every update so your libraries 
are no longer available and your addin will crash.
There are two ways to work around this issue:

Fusion360 runs addin in ist own python instance which is managed by Fusion360 and will be reset at every update of Fusion. On Windows this instance is located at …. Therefore some extra attention needs to be given to the installation process of any dependency (including this framework) your addin relies on.

The framework is available on PyPi and can therefore easily be installed by executing pip install fusion_Addin_framework from fusions python instance. However for the named reason you need to reinstall it after every Fusion360 Update. You can automate this reinstalling process by using:
…
As the import routine in our  addin.

A second option to use this framework is to simply link the git repository as a submodule to your Addin. You can do this by using:

Your folder structure should look like this in that case.
If you choose this option you need to use relative imports since the package is not installed to your python instance.
So instead of import fusion_addin_framework you will need to type from .fusion_addin_framework import fusion_addin_framework to access the functionalities of the framework.

Basic idea and concept
----------------------
The idea of this framework is to simplify the creation of Fusion360 Addin by 
providing wrapper classes which represent the 
Especially the concept of the handler classes is substituted by simply using
After these classes got instantiated you can use them as they would be "normal"
instances. All attribute and function calls will be redirected to the undelying object.
In addition to the originally implementation default values for all parameters 
where provided 

The best way to understand this concept and the usage of this addin in general 
is to checkout the exmaples. 

Note on naming convention
-------------------------
For consistency with the Fusion API all interfaces of the wrapper classes are in camelCase.
For all internal variables and utility function, the python naming convention 
(snake_case for variabels and functions and UpperCamelCase for classes) is used. 

Default images
--------------
For some of the UI-classes in the Fusion360-API you can provide the path to an image 
or image folder (called "resourceFolder" in the API) for customizing their appearance.
This framework provides some default images you can choose from.
Instead of providing a path you simply pass the name of one of the images  
The following default images are available:

Please note that no sepereate images are provided for the dark and disabled
image option.

All these default icons were made by Freepik from www.flaticon.com.
If you want to make your addin pulicly available you need to attribute the author
of these images. See https://support.flaticon.com/hc/en-us/articles/207248209-How-I-must-insert-the-attribution-
for more details. 



.. toctree::
   :hidden:

   self
   examples
   reference
   indices

