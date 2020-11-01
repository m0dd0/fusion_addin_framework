"""[summary]
"""

import subprocess
import os
import json

TO_EXECUTE = [('pip', 'install', 'pylint'), ('pip', 'install', 'rope'),
              ('pip', 'install', 'yapf')]


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


if __name__ == '__main__':
    fusions_python_path = get_fusions_python()

    for command in TO_EXECUTE:
        try:
            subprocess.run([fusions_python_path, '-m', *command], check=True)
        except:
            print('couldnt execute \'{0}\'.'.format(' '.join(command)))
