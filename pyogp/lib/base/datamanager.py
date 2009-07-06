# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import re

# pyogp messaging
from pyogp.lib.base.message.packets import *
from pyogp.lib.base.message.message_handler import MessageHandler

# utilities
from pyogp.lib.base.exc import NotImplemented

class DataManager(object):
    def __init__(self, settings, agent):
        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()
        self.agent = agent
    
    def enable_callbacks(self):
        """
        Implementing class would instantiate its message handlers here
        """
        raise NotImplemented("enable_callbacks")
    
    
