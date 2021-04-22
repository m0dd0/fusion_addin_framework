# This script determines the current location of the python instance which is
# used by Fusion360. The path changes at each update. During the update it can 
# happen that there are multiple python instances which will cause the script
# to fail. In this case simply restart Fusion360 which will delete the unused
# instancess of Fusion360 automatically.  
# This scriot will not work on Mac.

&(Get-ChildItem $env:LOCALAPPDATA\Autodesk\webdeploy\production\*\Python\python.exe) $args