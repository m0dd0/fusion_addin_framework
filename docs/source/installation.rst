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

A ready to use cookiecutter template can be found `here`_
.. _here: https://github.com/m0dd0/FusionAddinCookiecutter
