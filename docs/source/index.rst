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

Basic idea and concept
----------------------
The idea of this framework is to simplify the creation of Fusion360 Addin by 
providing wrapper classes which represent the 
After these classes got instantiated you can use them as they would be "normal"
instances. All attribute and function calls will be redirected to the undelying object.
In addition to the originally implementation default values for all parameters 
where provided 

The best way to understand this concept is to checkout the exmaples. 

.. toctree::
   :hidden:

   self
   examples
   reference
   indices

