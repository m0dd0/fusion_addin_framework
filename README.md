# Fusion Addin Framework

Fusion360 is a great CAD Software and also provides a pretty extensive API for customizing the software to your needs.
The API is written in C++ and ported to Python. For this reason as a python developer some concept might feel a bit overcomplicated and not very "pythonic" overall.
This framework aims at simplifying the creation of Fusion360 Addins by wrapping around some of the classes in the API. 
You can find the documentation for the framework [here](https://fusion-addin-framework.readthedocs.io/en/stable/).
T

## installation
Fusion360 uses and manages it own python instance which will be reset at every update of Fusion360. Therfore it is *not* recommended to simply pip install this package to Fusions python instance. 
There are two options to use the package.

The first option is to dynamically install the package from within the addin itself (if it hasnt been installed already). This can be achieved by using the following code for "importing" the package.

The second option is to simply clone this repo into your addin folder and use relative imports. Note that you need to impoer the subfolder to actually access


 


## basic example
The code below is a very basic sample which prints a message if you press a custom button in a custom panel. 

