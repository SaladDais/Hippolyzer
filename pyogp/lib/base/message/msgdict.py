from indra.base import llsd

class MessageDictionary(object):
    def __init__(self, message_details):
        if message_details == None:
            raise Exception('Details file null')
        #all the details of the file
        self.message_details = {}
        #only concerning messages
        self.message_dict = {}
        
        self.buildDictionary(message_details)

    def buildDictionary(self, message_details):
        self.message_details    = llsd.parse(message_details)   
        message_dict = self.message_details['messages']
        for message in message_dict:
            self.message_dict[message] = message_dict[message]
    
    def get_message(self, message_name):
        if message_name in self.message_dict:
            return self.message_dict[message_name]

        return None

    def get_message_flavor(self, message_name):
        message = self.get_message(message_name)
        if message == None:
            return None

        return message['flavor']

    def get_trusted_sender(self, message_name):
        message = self.get_message(message_name)
        if message == None:
            return None

        return message['trusted-sender']

    def __getitem__(self, i):
        return self.get_message(i)
