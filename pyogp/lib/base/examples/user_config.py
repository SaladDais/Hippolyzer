#! /usr/bin/python
#
# This file bears no copyright and is placed in the Public Domain by its author.
#

import os
import sys

about_txt = """
Grabs the user's config data from ~/.pyogp/*
This currently only handles ~/.pyogp/login_data.py
Load in other config files and extend instance variables to suit.""" 

class login_data():
    def __init__(self): 
        default_data = {"Description"      : "Default login data",
                        "First Name"       : "First",
                        "Last Name"        : "Last",
                        "Password"         : "secretsauce",
                        "loginuri"         : "https://login.aditi.lindenlab.com/cgi-bin/login.cgi",
                        "region"           : ""}
        config = {'logins' : None, 'default_login': None}
        logins_config_file = os.environ["HOME"] + '/.pyogp/login_data.py'
        if os.path.exists(logins_config_file):
            try:
                execfile(logins_config_file, {}, config)
            except Exception, e:
                print "Configuration file %s is not valid Python, fix it -->  %s" % (logins_config_file, str(e))
                sys.exit(2)
        else:
            config = {'logins' : [default_data], 'default_login': 0}
        self.logins = config['logins']
        self.selected_login_number = config['default_login']
        self.selected_login_data = self.logins[self.selected_login_number]

def main():
    print login_data().selected_login_data

if __name__ == "__main__":
    main()
