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
The use of the framework and its advantages can be demonstrated with some examples.
More examples can be found in the [documentation](https://fusion-addin-framework.readthedocs.io/en/latest/).

```python

```
