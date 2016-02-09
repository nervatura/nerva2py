# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2015, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import wx, os, locale
from wx import xrc
import webbrowser
from nwx.utils.configobj import ConfigObj  # @UnresolvedImport
from nwx.view.fBase import Dialog  # @UnresolvedImport
from nwx.utils.adapter import npiAdapter  # @UnresolvedImport

class fLogin(Dialog):
  application = None
  login_ok = False
  user_config = ConfigObj()
  locale = ConfigObj()

  def init_config(self):
    home = os.getenv('USERPROFILE') or os.getenv('HOME')
    if os.path.exists(home+os.sep+".nervatura"+os.sep+"nervatura.ini")==False:
      if os.path.exists(home+os.sep+".nervatura")==False:
        os.makedirs(home+os.sep+".nervatura")
      self.user_config = ConfigObj()
      self.user_config.filename = home+os.sep+".nervatura"+os.sep+"nervatura.ini"
      self.user_config.write()
    else:
      self.user_config = ConfigObj(home+os.sep+".nervatura"+os.sep+"nervatura.ini")
    
    if self.user_config.has_key("locale")==True:
      self.application.app_settings["locale"] = str(self.user_config["locale"])
    else:
      self.application.app_settings["locale"] = str(self.application.app_config["default"]["locale"])
    self.locale = ConfigObj("locale/"+self.application.app_settings["locale"]+"/"+self.__class__.__name__+".properties")
    self.application.app_settings["codepage"] = locale.getdefaultlocale()[1]
      
    if self.user_config.has_key("url")==True:
      self.application.app_settings["url"] = str(self.user_config["url"])
    else:
      self.application.app_settings["url"] = str(self.application.app_config["connection"]["default_url"])
    
    if self.user_config.has_key("database")==True:
      self.application.app_settings["database"] = str(self.user_config["database"])
    else:
      self.application.app_settings["database"] = ""
    if self.user_config.has_key("username")==True:
      self.application.app_settings["username"] = str(self.user_config["username"])
    else:
      self.application.app_settings["username"] = ""
    self.application.app_settings["password"] = ""
    #self.application.app_settings["usergroup"] = str(self.application.app_config["default"]["usergroup"])
    self.application.app_settings["transfilter"] = int(self.application.app_config["default"]["transfilter"])
    self.application.app_settings["department"] = None
    self.application.app_settings["department_id"] = None
    
    self.application.app_settings["color"] = self.application.app_config["default"]["color"]
    self.application.app_settings["label_color"] = self.application.app_config["default"]["label_color"]
    self.application.app_settings["panel_color"] = self.application.app_config["default"]["panel_color"]
    self.application.app_settings["help_color"] = self.application.app_config["default"]["help_color"]
    self.application.app_settings["close_color"] = self.application.app_config["default"]["close_color"]
    
    self.application.app_settings["os"] = str(wx.GetOsDescription()).split(" ")[0]
    self.application.app_settings["engine"] = "sqlite"
      
  def __init__(self, app, parent = None):
    self.application = app
    
    self.init_config()
    Dialog.__init__(self, app.get_resources().LoadDialog(parent, self.__class__.__name__))
    #self.SetBackgroundColour(self.application.app_settings["panel_color"])
    #xrc.XRCCTRL(self, 'panel_body').SetBackgroundColour(self.application.app_settings["panel_color"])    
    self.Fit()
    self.SetAutoLayout(True)
    
    self.lb_database = xrc.XRCCTRL(self, 'lb_database')
    xrc.XRCCTRL(self, 'panel_database').SetBackgroundColour(self.application.app_settings["label_color"])
    self.lb_database.SetForegroundColour(self.application.app_settings["color"])
    self.tb_database = xrc.XRCCTRL(self, 'tb_database')
    self.tb_database.name = "database"
    self.tb_database.SetValue(self.application.app_settings["database"])
    self.tb_database.Bind(wx.EVT_TEXT, self.onTextChange)
    self.tb_database.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
    
    self.lb_username = xrc.XRCCTRL(self, 'lb_username')
    xrc.XRCCTRL(self, 'panel_username').SetBackgroundColour(self.application.app_settings["label_color"])
    self.lb_username.SetForegroundColour(self.application.app_settings["color"])
    self.tb_username = xrc.XRCCTRL(self, 'tb_username')
    self.tb_username.name = "username"
    self.tb_username.SetValue(self.application.app_settings["username"])
    self.tb_username.Bind(wx.EVT_TEXT, self.onTextChange)
    self.tb_username.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
    
    self.lb_password = xrc.XRCCTRL(self, 'lb_password')
    xrc.XRCCTRL(self, 'panel_password').SetBackgroundColour(self.application.app_settings["label_color"])
    self.lb_password.SetForegroundColour(self.application.app_settings["color"])
    self.tb_password = xrc.XRCCTRL(self, 'tb_password')
    self.tb_password.name = "password"
    self.tb_password.SetValue(self.application.app_settings["password"])
    self.tb_password.Bind(wx.EVT_TEXT, self.onTextChange)
    self.tb_password.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
    self.tb_password.SetFocus()    
    
    self.lb_language = xrc.XRCCTRL(self, 'lb_language')
    xrc.XRCCTRL(self, 'panel_language').SetBackgroundColour(self.application.app_settings["label_color"])
    self.lb_language.SetForegroundColour(self.application.app_settings["color"])
    self.tb_password = xrc.XRCCTRL(self, 'tb_password')
    self.cmb_language = xrc.XRCCTRL(self, 'cmb_language')
    self.cmb_language.name = "locale"
    for lcode in self.application.app_config["locale"].keys():
      self.cmb_language.Append(self.application.app_config["locale"][lcode].decode('utf-8').encode(self.application.app_settings["codepage"]), lcode)
      if str(self.application.app_settings["locale"])==str(lcode):
        self.cmb_language.SetStringSelection(self.application.app_config["locale"][lcode].decode('utf-8').encode(self.application.app_settings["codepage"]))
    self.cmb_language.Bind(wx.EVT_COMBOBOX, self.onSelectionChange)
    self.cmb_language.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
    
    self.lb_url = xrc.XRCCTRL(self, 'lb_url')
    xrc.XRCCTRL(self, 'panel_url').SetBackgroundColour(self.application.app_settings["label_color"])
    self.lb_url.SetForegroundColour(self.application.app_settings["color"])
    self.tb_url = xrc.XRCCTRL(self, 'tb_url')
    self.tb_url.name = "url"
    self.tb_url.SetValue(self.application.app_settings["url"])
    self.tb_url.Bind(wx.EVT_TEXT, self.onTextChange)
    self.tb_url.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
    
    self.cmd_login = xrc.XRCCTRL(self, 'cmd_login')
    self.cmd_login.name = "cmd_login"
    self.cmd_login.keycode = ""
    self.cmd_login.Bind(wx.EVT_BUTTON, self._cmd_login)
    self.cmd_login.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
    
    self.cmd_help = xrc.XRCCTRL(self, 'cmd_help')
    self.cmd_help.SetForegroundColour(self.application.app_settings["help_color"])
    self.cmd_help.name = "cmd_help"
    self.cmd_help.keycode = "[F1]"
    self.cmd_help.Bind(wx.EVT_BUTTON, self._cmd_help)
    self.cmd_help.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
    
    self.cmd_cancel = xrc.XRCCTRL(self, 'cmd_cancel')
    self.cmd_cancel.SetForegroundColour(self.application.app_settings["close_color"])
    self.cmd_cancel.name = "cmd_cancel"
    self.cmd_cancel.keycode = ""
    self.cmd_cancel.Bind(wx.EVT_BUTTON, self._cmd_cancel)
    self.cmd_cancel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
    
    self.set_locale(self.application.app_settings["locale"])
  
  def set_locale(self, lc_code):
    if self.application.app_settings["locale"]!=lc_code or self.locale==None:
      self.application.app_settings["locale"] = lc_code
      self.locale = ConfigObj("locale/"+self.application.app_settings["locale"]+"/"+self.__class__.__name__+".properties")
      self.application.app_settings["codepage"] = locale.getdefaultlocale()[1]
    for label_id in self.locale.keys():
      label = ""
      if self.locale[label_id].__class__.__name__ == "list":
        for lst in self.locale[label_id]:
          label = label + lst
      else:
        label = self.locale[label_id]
      cl_id = str(label_id).replace("_label", "").replace("_title", "").replace("_headerText", "")
      if cl_id == self.__class__.__name__:
        self.SetTitle(label.decode('utf-8').encode(self.application.app_settings["codepage"])+" (v"+str(self.application.app_config["application"]["version"])+")")
      if self.__dict__.has_key(cl_id):
        if self.__dict__[cl_id].__class__.__name__=="StaticText":
          self.__dict__[cl_id].SetLabel(label.decode('utf-8').encode(self.application.app_settings["codepage"]))
        elif self.__dict__[cl_id].__class__.__name__=="Button":
          self.__dict__[cl_id].SetLabel(self.__dict__[cl_id].keycode+" "+label.decode('utf-8').encode(self.application.app_settings["codepage"]))
        else:
          pass
  
  def OnKeyDown(self, event):
    keycode = event.GetKeyCode()
    if keycode == wx.WXK_F1:
      self.callHelp()
    event.Skip()
  
  def onSelectionChange(self, event):
    if self.application.app_settings[event.GetEventObject().name]!=str(event.GetEventObject().GetClientData(self.cmb_language.GetSelection())):
      self.set_locale(event.GetEventObject().GetClientData(self.cmb_language.GetSelection()))
          
  def onTextChange(self, event):
    if self.application.app_settings[event.GetEventObject().name]!=str(event.GetString()):
      self.application.app_settings[event.GetEventObject().name]=str(event.GetString())
  
  def _cmd_login(self, event=None):
    self.callLogin() 
  def _cmd_help(self, event=None):
    self.callHelp()
  def _cmd_cancel(self, event=None):
    self.Close()
      
  def callLogin(self):
    try:
      conn = npiAdapter(self.application.app_settings["url"]+"/"+
          self.application.app_config["connection"]["npi_service"])
      login = conn.getLogin(self.application.app_settings["database"], 
                            self.application.app_settings["username"], 
                            self.application.app_settings["password"])
      if login=="error":
        return
      elif login["valid"]==True:
        self.user_config["locale"] = self.application.app_settings["locale"]
        self.user_config["url"] = self.application.app_settings["url"]
        self.user_config["database"] = self.application.app_settings["database"]
        self.user_config["username"] = self.application.app_settings["username"]
        self.user_config.write()
        self.application.app_settings["employee_id"] = login["employee"]["id"]
        self.application.app_settings["engine"] = login["engine"]
        self.login_ok = True
        self.Close()
      else:
        wx.MessageBox(str(login["message"]), str(self.application.app_config["application"]["name"]), wx.OK | wx.ICON_ERROR)
    except Exception, err:
      wx.MessageBox(str(err), "callLogin", wx.OK | wx.ICON_ERROR)
  
  def callHelp(self):
    url = self.application.app_settings["url"]+"/"+self.application.app_config["connection"]["ndr_service"]+"/getHelp"
    url += "?page="+self.__class__.__name__
    url += "&lang="+str(self.application.app_settings["locale"])[:2]
    url += "&appl=nwx"
    url += "&title=Nervatura WxDemo"
    url += "&subtitle=Ver.No: "+str(self.application.app_config["application"]["version"])
    webbrowser.open(url)

