from pyogp.lib.base.data import msg_tmpl
from pyogp.lib.base.message_types import MsgFrequency

class TemplateDictionary():
    def __init__(self, template_list):
        if template_list == None:
            raise Exception('Template list null')
        #maps name to template
        self.message_templates = {}
        #maps (freq,num) to template
        self.message_dict = {}

        self.buildDictionaries(template_list)

    def buildDictionaries(self, template_list):
        for template in template_list:
            self.message_templates[template.name] = template

            #do a mapping of type to a string for easier reference
            frequency_str = ''
            if template.frequency == MsgFrequency.FIXED_FREQUENCY_MESSAGE:
                frequency_str = "Fixed"
            elif template.frequency == MsgFrequency.LOW_FREQUENCY_MESSAGE:
                frequency_str = "Low"
            elif template.frequency == MsgFrequency.MEDIUM_FREQUENCY_MESSAGE:
                frequency_str = "Medium"
            elif template.frequency == MsgFrequency.HIGH_FREQUENCY_MESSAGE:
                frequency_str = "High"
                
            self.message_dict[(frequency_str, \
                               template.msg_num)] = template

    def get_template(self, template_name):
        return self.message_templates[template_name]
    
    def get_template_by_pair(self, frequency, num):
        return self.message_dict[(frequency, num)]

    def __getitem__(self, i):
        return self.get_template(i)
