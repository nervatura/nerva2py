# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import wx.aui
import webbrowser
from nwx.utils.configobj import ConfigObj  # @UnresolvedImport

class EvtHandler(wx.EvtHandler):
  def __init__(self, other):
    self.this = other.this
    self.thisown = 1
    del other.this
    self._setOORInfo(self)
    
class Frame(wx.Frame, EvtHandler):
  def __init__(self, other):
    EvtHandler.__init__(self, other)
    
class Dialog(wx.Dialog, EvtHandler):
  def __init__(self, other):
    EvtHandler.__init__(self, other)

class fChildFrame(wx.aui.AuiMDIChildFrame):
  def __init__(self, parent=None):
    wx.aui.AuiMDIChildFrame. __init__(self, parent, -1, "")
    self.parent = parent
    self.dirty = False
    self.fBrowser = None
    if parent!=None:
      self.locale = ConfigObj("locale/"+self.parent.application.app_settings["locale"]+"/"+self.__class__.__name__+".properties")
    #self.ds = None
    self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
    
  def getLocale(self, key):
    locStr = self.locale[key]
    if locStr.__class__.__name__ == "list":
      locStr_=""
      for lst in locStr:
        if locStr_!="":
          locStr_ = locStr_ +", "
        locStr_ = locStr_ + lst
      return locStr_.decode('utf-8').encode(self.parent.application.app_settings["codepage"])
    else:
      return locStr.decode('utf-8').encode(self.parent.application.app_settings["codepage"])
              
  def setLocale(self):
    for label_id in self.locale.keys():
      label = ""
      if self.locale[label_id].__class__.__name__ == "list":
        for lst in self.locale[label_id]:
          if label!="":
            label = label +", "
          label = label + lst
      else:
        label = self.locale[label_id]
      cl_id = str(label_id).replace("_label", "").replace("_title", "").replace("_headerText", "").replace("_toolTip", "")
      if self.__dict__.has_key(cl_id):
        if str(label_id).endswith("toolTip"):
          self.__dict__[cl_id].SetToolTip(wx.ToolTip(label.decode('utf-8').encode(self.parent.application.app_settings["codepage"])))
          continue
        if self.__dict__[cl_id].__class__.__name__=="StaticText" or self.__dict__[cl_id].__class__.__name__=="CheckBox" or \
          self.__dict__[cl_id].__class__.__name__=="HyperlinkCtrl" or self.__dict__[cl_id].__class__.__name__=="RadioButton":
          self.__dict__[cl_id].SetLabel(label.decode('utf-8').encode(self.parent.application.app_settings["codepage"]))
          continue
        if self.__dict__[cl_id].__class__.__name__=="Button":
          self.__dict__[cl_id].SetLabel(self.__dict__[cl_id].keycode+" "+label.decode('utf-8').encode(self.parent.application.app_settings["codepage"]))
          continue
  
  def showHead(self):
    if self.body.GetSizer().IsShown(self.head_panel)==True:
      show_filter=False
    else:
      show_filter=True
    self.head_panel.Show(show_filter)
    wx.CallAfter(self.Layout)
  
  def showPopMenu(self, menu, cmd=None, corY=0):
    pxmenu = self.parent.application.get_resources().LoadMenu(self.__class__.__name__+"_menu_"+menu)
    pmenu = wx.Menu()
    for pxitem in pxmenu.GetMenuItems():
      mid = pxitem.GetItemLabel()
      pitem = wx.MenuItem(pmenu, -1, str(self.getLocale(mid)))
      pitem.SetBitmap(pxitem.GetBitmap())
      pitem.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      self.Bind(wx.EVT_MENU, getattr(self, "_"+mid), pitem)
      pmenu.AppendItem(pitem)
    if cmd!=None:
      pos = cmd.GetPosition()
      pos[1] = pos[1]+cmd.GetSize()[1]+corY
      self.PopupMenu(pmenu, pos)
    else:
      self.PopupMenu(pmenu)
    pmenu.Destroy()
  
  def _field_link(self,  event=None):
    item = self.dg_fields.GetTable().GetRowData(event.GetRow())
    if item.fieldtype=="urlink":
      webbrowser.open(item.value)
      return
    if item.fieldtype=="customer":
      from nwx.view.fCustomer import fCustomer  # @UnresolvedImport
      fCustomer(self.parent, int(item.value)).Show()
      return
    if item.fieldtype in("tool","trans","transitem","transmovement","transpayment","product","project","employee","place"):
      return
              
  def _cmd_help(self, event=None):
    self.parent.getHelp(self.__class__.__name__)
  
  def _cmd_close(self, event=None):
    self.Close()
            
  def _close(self, event):
    if self.dataSet["changeData"]==True:
      dlg = wx.MessageDialog(self, self.getLocale("alert_dirty_ms"), self.getLocale("alert_warning_lb"),
        wx.YES_NO | wx.ICON_INFORMATION | wx.NO_DEFAULT)
      ms = dlg.ShowModal()
      dlg.Destroy()
      if ms==wx.ID_YES:
        event.Skip()
      else:
        return
    else:
      event.Skip()
    if self.fBrowser != None:
      self.fBrowser._closeShowWindow(self)     