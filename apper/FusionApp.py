"""[summary]
"""

import traceback
from collections import defaultdict
from itertools import zip_longest
from typing import List
import os
import logging

import adsk.core

from . import Fusion360CommandBase
from .UiElements import UiItemFactory, child_type, CommandDefinition

from ..utilities import appdirs


class FusionApp:
    """Base class for creating a Fusion 360 Add-in

    Args:
        name: The name of the addin
        company: the name of your company or organization
        debug: set this flag as True to enable more interactive feedback when developing.
    """
    def __init__(self,
                 name,
                 logger: logging.Logger,
                 debug_to_ui: bool = True,
                 author=None):
        self.name = name
        self.author = author if author is not None else self.name

        self.user_state_dir = appdirs.user_state_dir(self.name, self.author)
        self.user_cache_dir = appdirs.user_cache_dir(self.name, self.author)
        self.user_config_dir = appdirs.user_config_dir(self.name, self.author)
        self.user_data_dir = appdirs.user_data_dir(self.name, self.author)
        self.user_log_dir = appdirs.user_log_dir(self.name, self.author)

        self.default_resources = os.path.abspath(
            os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         'default_resources'))
        self.resources = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'resources'))

        self.debug_to_ui = debug_to_ui
        self.commands = []
        # self.events = []
        self.created_ui_elements = defaultdict(list)

        self.logger = logger

    def _show_error(self, message):
        self.logger.error(message)
        if self.debug_to_ui:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox(message)

    def add_command(self, command_class: Fusion360CommandBase,
                    positions: List[List[UiItemFactory]]):
        """[summary]

        Args:
            command_class (Fusion360CommandBase): [description]
            positions (List[List[UiItemFactory]]): [description]
        """

        try:
            for position in positions:
                if not isinstance(position[-1], CommandDefinition):
                    raise ValueError(
                        'You need to provide a Command Definition at the end of'
                        'every position. Not a {0}.'.format(
                            type(position[-1].__name__)))
                parent = adsk.core.UserInterface
                for elem in position:
                    if not isinstance(elem, child_type[parent]):
                        raise ValueError(
                            'You can not place a {0} into a {1}. {2} exspected.'
                            .format(
                                type(elem).__name__, parent.__name__,
                                ' or '.join(
                                    [t.__name__ for t in child_type[parent]])))
                    parent = type(elem)

            command = command_class(self, positions, self.logger,
                                    self.debug_to_ui)

            self.commands.append(command)

        except:
            self._show_error('Apper Add Command failed: {}'.format(
                traceback.format_exc()))

    def run_app(self):
        """[summary]
        """

        try:
            for run_command in self.commands:
                run_command.on_run()
        except:
            self._show_error('Running App failed: {0}'.format(
                traceback.format_exc()))

    def stop_app(self):
        """Stops the Addin and cleans up all of the created UI elements"""
        try:

            all_position_paths = []
            for stop_command in self.commands:
                all_position_paths.extend(stop_command.position_paths)

            for level in reversed(list(zip_longest(*all_position_paths))):
                for elem in level:
                    if elem[1]:
                        self.logger.info('deleting {0} {1}'.format(
                            elem[0].objectType, elem[0].id))
                        elem[0].deleteMe()

            # for event in self.events:
            #     event.on_stop()

        except:
            self._show_error('AddIn Stop Failed: {0}'.format(
                traceback.format_exc()))

    # def add_document_event(self, event_id: str,
    #                        event_type: adsk.core.DocumentEvent,
    #                        event_class: Any):
    #     """Register a document event that can respond to various document actions

    #     Args:
    #         event_id: A unique identifier for the event
    #         event_type: Any document event in the current application
    #         event_class: Your subclass of apper.Fusion360DocumentEvent
    #     """
    #     doc_event = event_class(event_id, event_type)
    #     doc_event.fusion_app = self
    #     self.events.append(doc_event)

    # def add_custom_event(self, event_id: str, event_class: Any):
    #     """Register a custom event to respond to a function running in a new thread

    #     Args:
    #         event_id: A unique identifier for the event
    #         event_class: Your subclass of apper.Fusion360CustomThread
    #     """

    #     custom_event = event_class(event_id)
    #     custom_event.fusion_app = self
    #     self.events.append(custom_event)

    # def add_custom_event_no_thread(self, event_id: str, event_class: Any):
    #     """Register a custom event

    #     Args:
    #         event_id: A unique identifier for the event
    #         event_class: Your subclass of apper.Fusion360CustomThread
    #     """

    #     custom_event = event_class(event_id)
    #     custom_event.fusion_app = self
    #     self.events.append(custom_event)

    # def add_workspace_event(self, event_id: str, workspace_name: str,
    #                         event_class: Any):
    #     """Register a workspace event that can respond to various workspace actions

    #     Args:
    #         event_id: A unique identifier for the event
    #         workspace_name: name of the workspace (i.e.
    #         event_class: Your subclass of apper.Fusion360WorkspaceEvent
    #     """
    #     workspace_event = event_class(event_id, workspace_name)
    #     workspace_event.fusion_app = self
    #     self.events.append(workspace_event)

    # def add_command_event(self, event_id: str, event_type: Any,
    #                       event_class: Any):
    #     """Register a workspace event that can respond to various workspace actions

    #     Args:
    #         event_id: A unique identifier for the event
    #         event_type: One of [UserInterface.commandCreated,
    #         UserInterface.commandStarting, UserInterface.commandTerminated]
    #         event_class: Your subclass of apper.Fusion360CommandEvent class
    #     """
    #     command_event = event_class(event_id, event_type)
    #     command_event.fusion_app = self
    #     self.events.append(command_event)

    # def add_web_request_event(self, event_id: str,
    #                           event_type: adsk.core.WebRequestEvent,
    #                           event_class: Any):
    #     """Register a workspace event that can respond to various workspace actions

    #     Args:
    #         event_id: A unique identifier for the event
    #         event_class: Your subclass of apper.Fusion360WebRequestEvent
    #         event_type: Opened or Inserting from URL event type such as (app.openedFromURL)
    #     """
    #     web_request_event = event_class(event_id, event_type)
    #     web_request_event.fusion_app = self
    #     self.events.append(web_request_event)
