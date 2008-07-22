from pyogp.lib.base.data import msg_tmpl

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
            self.message_templates[template.get_name()] = template
            self.message_dict[(template.get_frequency(), \
                               template.get_message_number())] = template

    def get_template(self, template_name):
        return self.message_templates[template_name]

    def get_template_by_pair(self, frequency, num):
        return self.message_dict[(frequency, num)]

    def __getitem__(self, i):
        return self.get_template(i)
