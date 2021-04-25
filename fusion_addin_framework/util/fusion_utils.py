import logging

import adsk, adsk.core


def get_input_values(event_args):
    pass
    # TODO implement


class TextPaletteLoggingHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self.textPalette = adsk.core.Application.get().userInterface.palettes.itemById(
            "TextCommands"
        )
        # self.textPalette.isVisible = True

    def emit(self, record):
        self.textPalette.writeText(self.format(record))
        # adsk.doEvents() # doesnt seem to be necessary