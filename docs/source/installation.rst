.. _installation:

Installation
============

The recommended way to use this framework is to **clone  
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
