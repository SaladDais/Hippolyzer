import wx 
import pprint 



about_txt = """
This demos a login dialog to be used by generic sample scripts for pyogp""" 
class DataXferValidator(wx.PyValidator):   
    def __init__(self, data, key): 
        wx.PyValidator.__init__(self) 
        self.data = data 
        self.key = key 
    def Clone(self): 
        """ 
Declaring the validator 
Licensed to Lawson English <LEnglish5@cox.net>
Using validators to manage data in a dialog 287 
         Note that every validator must implement the Clone() method. 
         """ 
        return DataXferValidator(self.data, self.key) 
    def Validate(self, win):   
        textCtrl = self.GetWindow() 
        text = textCtrl.GetValue() 
        if ((len(text) == 0) & (self.key != "region")) : 
            wx.MessageBox("This field must contain some text!", "Error") 
            textCtrl.SetBackgroundColour("pink") 
            textCtrl.SetFocus() 
            textCtrl.Refresh() 
            return False 
        else: 
            textCtrl.SetBackgroundColour( 
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)) 
            textCtrl.Refresh() 
            return True 

    def TransferToWindow(self):   
        textCtrl = self.GetWindow() 
        textCtrl.SetValue(self.data.get(self.key, "")) 
        return True 
    def TransferFromWindow(self):   
        textCtrl = self.GetWindow() 
        self.data[self.key] = textCtrl.GetValue() 
        return True 

class MyDialog(wx.Dialog): 
    def __init__(self, data): 
        wx.Dialog.__init__(self, None, -1, "Validators: data transfer") 
        self.returnvalue = None
        about   = wx.StaticText(self, -1, about_txt) 
        first_name_l  = wx.StaticText(self, -1, "First Name:") 
        last_name_l = wx.StaticText(self, -1, "Last Name:") 
        password_l = wx.StaticText(self, -1, "Password:") 
        loginuri_l = wx.StaticText(self, -1, "loginuri:")
        region_l = wx.StaticText(self, -1, "region:")

        first_name  = wx.TextCtrl(self,   
                              validator=DataXferValidator(data, "First Name")) 
        last_name = wx.TextCtrl(self, 
                              validator=DataXferValidator(data, "Last Name")) 
        password = wx.TextCtrl(self, 
                              validator=DataXferValidator(data, "Password")) 
        loginuri = wx.TextCtrl(self, 
                      validator=DataXferValidator(data, "loginuri")) 
        region = wx.TextCtrl(self, 
                      validator=DataXferValidator(data, "region")) 
        okay   = wx.Button(self, wx.ID_OK) 
        okay.SetDefault() 
        cancel = wx.Button(self, wx.ID_CANCEL) 
        sizer = wx.BoxSizer(wx.VERTICAL) 
        sizer.Add(about, 0, wx.ALL, 5) 
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5) 

        fgs = wx.FlexGridSizer(3, 2, 5, 5) 
        fgs.Add(first_name_l, 0, wx.ALIGN_RIGHT) 
        fgs.Add(first_name, 0, wx.EXPAND) 
        fgs.Add(last_name_l, 0, wx.ALIGN_RIGHT) 
        fgs.Add(last_name, 0, wx.EXPAND) 
        fgs.Add(password_l, 0, wx.ALIGN_RIGHT) 
        fgs.Add(password, 0, wx.EXPAND) 
        fgs.Add(loginuri_l, 0, wx.ALIGN_RIGHT) 
        fgs.Add(loginuri, 0, wx.EXPAND) 
        fgs.Add(region_l, 0, wx.ALIGN_RIGHT) 
        fgs.Add(region, 0, wx.EXPAND) 
        fgs.AddGrowableCol(1) 
        sizer.Add(fgs, 0, wx.EXPAND|wx.ALL, 5) 
        btns = wx.StdDialogButtonSizer() 
        btns.AddButton(okay) 
        btns.AddButton(cancel) 
        btns.Realize() 
        sizer.Add(btns, 0, wx.EXPAND|wx.ALL, 5) 
        self.SetSizer(sizer) 
        sizer.Fit(self) 


def main():
    app = wx.PySimpleApp() 
    
    data = { "First Name" : "first", "Last Name" : "last", "Password":"secretsauce",
            "loginuri" : "https://login.aditi.lindenlab.com/cgi-bin/login.cgi",
            "region" : ""} 
    dlg = MyDialog(data) 
    dlg.ShowModal() 
    print dlg.GetReturnCode()
    dlg.Destroy() 
    wx.MessageBox("You entered these values:\n\n" + 
                  pprint.pformat(data)) 
    app.MainLoop() 



        

if __name__=="__main__":
    main()
