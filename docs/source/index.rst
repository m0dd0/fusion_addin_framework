Introduction
============

Fusion360 is a great CAE software and also provides an comprehensive API for 
customizing and extending the software to your needs.
While automating your tasks with the Fusion API with scripts is mostly 
straightforward, turning these scripts into addins which can be executed via 
the GUI requires an considerable amount of boilerplate code.
This framework aims at simplifying the creation of addins by providing wrapper 
classes around Fusions GUI-related API classes like ``adsk.core.Workspace``, ``adsk.coreToolbarTab``, ``adsk.core.ToolbarPanel`` etc.
Using this approach no functionalities of the 'original' API gets lost while some 
additions allow a much cleaner and inutitiv creation of addins (at least in my 
oppinion).  
Also the event handler concept is substituated. Using the framework you can simply 
pass a python functions to a Command class. This further simlifies the creation 
of addins without sacrifying any flexibility.

The easiest way to understand the usage of the framework is probably to checkout 
the :ref:`example section <examples>`. 
Please note that this documentation assumes that you are already somewhat familiar
with the Fusion API and covers only the use of the framework itself.


.. toctree::
   :hidden:

   self
   installation
   concept
   examples
   reference
   indices

