# utilities
from pyogp.lib.base.exc import NotImplemented

class DataManager(object):
    def __init__(self, agent, settings):
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
    
    
