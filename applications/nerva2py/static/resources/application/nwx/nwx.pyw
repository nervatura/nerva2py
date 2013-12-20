#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import sys, os, wx
from wx import xrc
from nwx.utils.configobj import ConfigObj  # @UnresolvedImport
      
class nwx(wx.App):
  app = wx.App()
  app_config = ConfigObj("config.ini")
  app_settings = {}
  app_xmlres = None
    
  def __init__(self):
    self.app.SetAppName(self.app_config["application"]["name"])
    
    from nwx.view.fLogin import fLogin
    _flogin = fLogin(self)
    _flogin.ShowModal()
    if _flogin.login_ok == True:
      _flogin.Destroy()
      from nwx.view.fMain import fMain
      _fmain = fMain(self)
      self.app.SetTopWindow(_fmain)
      _fmain.Bind(wx.EVT_CLOSE, self.onExit, _fmain)
      _fmain.Show()
      self.app.MainLoop()
  
  def __init_resources(self):
    self.app_xmlres = xrc.EmptyXmlResource()
    self.app_xmlres.Load("nwx/view/fLogin.xrc")
    self.app_xmlres.Load("nwx/view/fMain.xrc")
    self.app_xmlres.Load("nwx/view/fBrowser.xrc")
    self.app_xmlres.Load("nwx/view/fCustomer.xrc")
    
  def get_resources(self):
    if self.app_xmlres == None:
      self.__init_resources()
    return self.app_xmlres
  
  def onExit(self, evt):
    self.app.ExitMainLoop()

if __name__ == '__main__':
#  try:
#    import psyco
#    psyco.full()
#  except ImportError:
#    pass
  hpath = os.path.abspath(os.path.dirname(__file__))
  if hpath not in sys.path:
    sys.path.insert(0, hpath)
  reload(sys)
  sys.setdefaultencoding("utf-8") #@UndefinedVariable
  nwx()
  
