"""[summary]
"""

import traceback
import logging
import os
from datetime import datetime

import adsk.core

app = adsk.core.Application.cast(adsk.core.Application.get())
ui = app.userInterface

try:
    from .apper.apper.Utilities import create_default_logger
    from .apper.apper import FusionApp
    from .apper.apper.UiElements import Workspace, Toolbar, Tab, Panel  # pylint: disable = unused-import
    from .apper.apper.UiElements import Dropdown, CommandControl, SplitButtonControl  # pylint: disable = unused-import
    from .apper.apper.UiElements import ButtonDefinition, CheckBoxDefinition, ListDefinition  # pylint: disable = unused-import

    from .commands.CustomCommandDir import CustomCommand

    logfile = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'logs',
        datetime.now().strftime('%Y-%m-%d_%H-%M-%S_apper_addin2_log.txt'))
    logger = create_default_logger(
        name='apper_addin2_logger',
        handlers=[logging.StreamHandler(),
                  logging.FileHandler(logfile)],
        level=logging.DEBUG)

    my_addin = FusionApp(
        debug_to_ui=True,
        logger=logger,
    )

    my_addin.add_command(
        command_class=CustomCommand,
        positions=[
            [
                Workspace(),
                Tab(),
                Panel(),
                CommandControl(),
                ButtonDefinition(ui_id='custom_buton_definiton_1',
                                 name='custombuttonname1')
            ],
            # [
            # Toolbar(),
            # Workspace(),
            # Tab(),
            # Panel(),
            # CommandControl(),
            # ButtonDefinition(ui_id='custom_addin_command_custom_addinas',
            #                  name='cbsd')
            # ],
        ])

except:
    app = adsk.core.Application.get()
    ui = app.userInterface
    message = 'Initialization Failed: {0}'.format(traceback.format_exc())
    if ui:
        ui.messageBox(message)
    logger.error(message)


def run(context):  # pylint: disable = unused-argument
    """[summary]

    Args:
        context ([type]): [description]
    """
    my_addin.run_app()


def stop(context):  # pylint: disable = unused-argument
    """[summary]

    Args:
        context ([type]): [description]
    """
    my_addin.stop_app()
