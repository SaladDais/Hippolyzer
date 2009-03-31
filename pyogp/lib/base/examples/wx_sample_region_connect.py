#!/usr/bin/python
"""
@file sample_agent_login.py
@date 2009-02-16
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""



# standard
import re
import getpass, sys, logging
from optparse import OptionParser

from eventlet import api

# wx
import wx, datetime, time

import testdialog
import user_config
import pprint 

# pyogp
from pyogp.lib.base.agent import Agent
from pyogp.lib.base.settings import Settings



class LoggerTextCntl(wx.TextCtrl):
    def write(self, text):
        """
        Write the text to the LoggerTextCntl instance
        If not called in the context of the gui thread then uses
        CallAfter to do the work there.
        """        

        if not wx.Thread_IsMain():
            wx.CallAfter(self.__write, text)
        else:
            self.__write(text)

    def __write(self, text):
        # helper function for actually writing the text.
        self.AppendText(text)

    def flush(self):
        pass

class TestFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(1200, 700))
        panel = wx.Panel(self)
        
        global not_closed_window
        not_closed_window = True  
        
        self.timertext  = LoggerTextCntl(panel, 1, "",
                                         style=wx.TE_MULTILINE|wx.TE_READONLY, size = (150,400))
        self.msgtext  = LoggerTextCntl(panel, 2, "",
                                       style=wx.TE_MULTILINE|wx.TE_READONLY, pos = (151,0),size = (1049,400))
        self.errtext  = LoggerTextCntl(panel, 3, "",
                                       style=wx.TE_MULTILINE|wx.TE_READONLY, pos = (151,401),size = (1049,200))
        self.mybutton = wx.Button(panel, 4, 'Pause/Resume', (10, 620))
        self.Login = wx.Button(panel, 5, 'Login', (10, 650))
        self.Bind(wx.EVT_BUTTON, self.OnPause, id=4)
        self.Bind(wx.EVT_BUTTON, self.OnLogin, id=5)
        self.Centre()
        self.eqg = None
        self.gotimer =True
        self.timer = wx.Timer(self)

        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)
        self.timer.Start(100)
        self.Show(True)


    def OnTimer(self, event):
        wx.GetApp().DoTimer(event)
    def OnPause(self, event):

        if self.gotimer == True:
            self.timer.Stop()
            self.gotimer = False
        else:
            self.timer.Start(100)
            self.gotimer = True
    def OnLogin(self,event):
        wx.MessageBox("Logging in", "OK") 

    def onCloseWindow(self,event):
        #self.timer.Stop()
        #self.eqg.contenew = False
        #wx.GetApp().avatar_obj.tearDown()
        sys.stdout = sys.stderr = wx.GetApp().savedstdio
        #i = 0
        #while i<20:
            #print i
            #print self.eqg
            #if not self.eqg.isAlive():break
            #time.sleep(1)
            #i +=1

        logging.shutdown()
        global not_closed_window
        not_closed_window = False
        self.Destroy()


def DoLoginDialog():
        data = { "First Name" : "First", "Last Name" : "Last", "Password":"secretsauce",
            "loginuri" : "https://login.aditi.lindenlab.com/cgi-bin/login.cgi",
            "region" : ""} 
        data = user_config.login_data().selected_login_data
        dlg = testdialog.MyDialog(data) 
        api.spawn(dlg.ShowModal)
        
        while True:
            api.sleep(0)
            code = dlg.GetReturnCode()
            if ((code == 5100 ) or  (code == 5101)): 
                break
        
        dlg.Destroy() 
        wx.MessageBox("You entered these values:\n\n" + 
                  pprint.pformat(data)) 
        return data

    
        
def login():
    """ login an to a login endpoint """ 
        
    
    logindata = DoLoginDialog()
    
    

    parser = OptionParser()

    logger = logging.getLogger("pyogp.lib.base.example")

    parser.add_option("-l", "--loginuri", dest="loginuri", default="https://login.aditi.lindenlab.com/cgi-bin/login.cgi",
                      help="specified the target loginuri")
    parser.add_option("-r", "--region", dest="region", default=None,
                      help="specifies the region to connect to")
#http://ec2-75-101-203-98.compute-1.amazonaws.com:9000
    parser.add_option("-q", "--quiet", dest="verbose", default=True, action="store_false",
                      help="enable verbose mode")


    (options, args) = parser.parse_args()

    if options.verbose:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG) # seems to be a no op, set it for the logger
        formatter = logging.Formatter('%(asctime)-30s%(name)-30s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        # setting the level for the handler above seems to be a no-op
        # it needs to be set for the logger, here the root logger
        # otherwise it is NOTSET(=0) which means to log nothing.
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        print "Attention: This script will print nothing if you use -q. So it might be boring to use it like that ;-)"

    # example from a pure agent perspective

    settings = Settings()

    #First, initialize the agent
    client = Agent(settings)

    # In this example, let's disable inventory handling
    client.settings.ENABLE_INVENTORY_MANAGEMENT = False

    # Now let's log it in
    #client.login(options.loginuri, args[0], args[1], password, start_location = options.region, connect_region = True)

    api.spawn(client.login, logindata["loginuri"], logindata["First Name"], logindata["Last Name"], logindata["Password"], start_location = options.region, connect_region = True)
    
    while client.handler == None:
        api.sleep(0)   #need to do this to keep print output below happy
    #client.login(loginuri, first, last, password, start_location = None, connect_region = True)

    print ''
    print ''
    print 'At this point, we have an Agent object, Inventory dirs, and with a Region attribute'
    print 'Agent attributes:'
    for attr in client.__dict__:
        print attr, ':\t\t\t',  client.__dict__[attr]
    print ''
    print ''
    print 'Region attributes:'
    for attr in client.region.__dict__:
        print attr, ':\t\t\t',  client.region.__dict__[attr]





class TestApp(wx.App):
    def OnInit(self):
        self.savedstdio = sys.stdout
        self.loginflag = False
        self.loginmethodindex=0
        self.place_avatarindex=0

        self.frame = TestFrame(None, -1, "TestIt")
        self.frame.Show(True)

        sys.stdout = sys.stderr = self.frame.errtext
        #logging setup could go here instead...
        




        console = logging.StreamHandler(self.frame.timertext)

        self.timerlogger = logging.getLogger("Timer")
        self.timerlogger.setLevel(logging.DEBUG)
        self.timerlogger.addHandler(console)

        self.SetTopWindow(self.frame)
        

        #registration.init()           #ZCA stuff?

        return True

    
    def DoTimer(self,event):
        if self.loginflag == False:
            api.spawn(login)
            self.loginflag = True
        else:
            api.sleep(0)




        self.timerlogger.info(  "time = " + str(datetime.datetime.now().microsecond))           






def wxmain():

    app = TestApp(None)

    api.spawn(app.MainLoop)
    while not_closed_window:
        api.sleep(0)

    return


def main():
    return wxmain()


#def main():
    #return login()    

if __name__=="__main__":
    main()
