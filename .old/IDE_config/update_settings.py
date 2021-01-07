"""
update_settings.py
=========================================================
File to permanently change the .vscode/settings.json file.

Every time the vscode editor is started from fusion to edit or debug a addin
the settings.json file normally gets overwritten by the file saved under
~/AppData/Roaming/Autodesk/Autodesk Fusion 360/APIP/ython/vscode/settings.json.
This file again gets overwritten every time Fusion starts.
So there is no direct way to change your vscode settings permanently, which can
be annoying if you want to use linting or custom IDE settings.

To overcome this issue you could make the file read only in windows. This again
has the downside that the python version fusion uses is not updated dynamically.
To solve all this problems you can use this script.
The script will overwrite the settings.json file in the .vscode directory of the
addin with the settings defined in a .json file in this directory named by a
name provided in SETTINGS_NAME variable of this scrip. Additionaly it makes the
settings file read-only so the settings are saved permanently.
Also it will automatically detect the current python instance and set the
"python.pythonPath" setting accordingly. It will also provide the .pylintrc
file in this directoy as linting parameter in the settings. So you can easily
customize your personal linting setings in this file without affecting the
settings.json file.
"""

import os
import json
import stat

SETTINGS_NAME = 'my_settings.json'
PYLINTRC_NAME = '.pylintrc'


def get_fusions_python():
    """
    gets the version of python which fusion is currently using
    """
    orig_settings_path = os.path.expanduser(
        r'~\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\Python\vscode\settings.json'
    )
    with open(orig_settings_path, 'r') as f:
        orig_settings = json.load(f)
    fusion_python_path = orig_settings['python.pythonPath']
    return fusion_python_path


def updateSettings():
    """
    Updates the IDE settings dynamically and permanently.
    For details see script docstring.
    """

    this_dir_path = os.path.realpath(os.path.dirname(__file__))
    settings_to_apply_path = os.path.join(this_dir_path, SETTINGS_NAME)
    pylintrc_path = os.path.join(this_dir_path, PYLINTRC_NAME)
    vscode_settings_path = os.path.realpath(
        os.path.join(this_dir_path, '../../.vscode/settings.json'))

    with open(settings_to_apply_path, 'r') as f:
        settings_to_apply = json.load(f)

    settings_to_apply['python.pythonPath'] = get_fusions_python()
    settings_to_apply['python.linting.pylintArgs'].append(
        r'--rcfile={0}'.format(pylintrc_path.replace('\\', '/')))
    settings_to_apply['python.autoComplete.extraPaths'][0] = os.path.abspath(
        os.path.expanduser(
            settings_to_apply['python.autoComplete.extraPaths'][0])).replace(
                '\\', '/')

    os.chmod(vscode_settings_path, stat.S_IWRITE)
    with open(vscode_settings_path, 'w') as f:
        json.dump(settings_to_apply, f, indent=4)
    os.chmod(vscode_settings_path, stat.S_IREAD)


if __name__ == '__main__':
    updateSettings()
    print('UPDATED SETTINGS')
