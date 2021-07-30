# 0. BEFORE SCRIPT EXECUTION: activate venv
# 1. reinstall the addin framework itself to the venv
pip install --upgrade --force-reinstall $PSScriptRoot/../
# 3. delete autogenerated files
Remove-Item $PSScriptRoot/source/_autosummary/* -Force -Confirm:$false 
# 4. make clean
cmd.exe /C "`"$PSScriptRoot\make.bat`" clean" 
# 5. make html
cmd.exe /C "`"$PSScriptRoot\make.bat`" html" 