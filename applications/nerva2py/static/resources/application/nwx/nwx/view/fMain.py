# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2015, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import wx.aui
from nwx.utils.configobj import ConfigObj  # @UnresolvedImport
import webbrowser
import sqlite3
#import base64
#from pyamf.remoting.client import RemotingService

class dict2obj(dict):
  def __init__(self, dict_, tablename=None):
    super(dict2obj, self).__init__(dict_)
    for key in self:
      item = self[key]
      if isinstance(item, list):
        for idx, it in enumerate(item):
          if isinstance(it, dict):
            item[idx] = dict2obj(it)
      elif isinstance(item, dict):
        self[key] = dict2obj(item)
    if tablename:
      self["__tablename__"] = tablename
     
  def __getattr__(self, key):
    return self[key]
  
  def __setattr__(self, key, value):
    self[key] = value
  
class fMain(wx.aui.AuiMDIParentFrame):
  application = None
  locale = None
  sb = None
  
  def __init__(self, app):
    self.application = app
    self.locale = ConfigObj("locale/"+self.application.app_settings["locale"]+"/"+self.__class__.__name__+".properties")
    wx.aui.AuiMDIParentFrame.__init__(self, None, -1, title=str(self.application.app_config["application"]["name"])+" (v"+str(self.application.app_config["application"]["version"])+")", style=wx.DEFAULT_FRAME_STYLE)
    self.SetIcon(wx.Icon('assets/icon32_ntura.png', wx.BITMAP_TYPE_PNG , 16, 16))
    self.SetMenuBar(self.makeMenuBar())
    self.sb = self.CreateStatusBar()
    self.sb.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
    self.sb.SetFieldsCount(2)
    self.sb.SetStatusWidths([25, -1])
    self.sb.icon = wx.StaticBitmap(self.sb, -1, wx.Bitmap('assets/icon16_accept.png'))
    self.sb.Bind(wx.EVT_SIZE, self.setIconSize)
    self.SetStatusText('OK', 1)
    self.Maximize()
    self.setStatusState()
        
  def makeMenuBar(self):
    xmb = self.application.get_resources().LoadMenuBar("fMain_menu")
    mb = wx.MenuBar()
    mb.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
    for xmenu in xmb.GetMenus():
      menu = self.createMenu(xmenu[0])
      mb.Append(menu, str(self.locale[xmenu[1]].decode('utf-8').encode(self.application.app_settings["codepage"])))
    return mb
  
  def createMenu(self, xmenu):
    menu = wx.Menu()
    for xitem in xmenu.GetMenuItems():
      mid = xitem.GetItemLabel()
      if mid.startswith("_"):
        sxmenu = self.application.get_resources().LoadMenu(mid[1:])
        smenu = self.createMenu(sxmenu)
        menu.AppendSubMenu(smenu, str(self.locale[mid[1:]].decode('utf-8').encode(self.application.app_settings["codepage"])))
      elif mid=="":
        menu.AppendSeparator()
      else:
        mitem = wx.MenuItem(menu, -1, str(self.locale[mid].decode('utf-8').encode(self.application.app_settings["codepage"])))
        mitem.SetBitmap(xitem.GetBitmap())
        #mitem.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.Bind(wx.EVT_MENU, getattr(self, mid), mitem)
        menu.AppendItem(mitem)
    return menu    
  
  def setStatusState(self, state=0):
    if state==1:
      #show refresh state
      self.sb.icon.SetBitmap(wx.Bitmap('assets/icon16_page_refresh.png'))
      self.SetStatusText(self.locale["status_refresh"].decode('utf-8').encode(self.application.app_settings["codepage"]), 1)
      return
    if state==2:
      #show update state
      self.sb.icon.SetBitmap(wx.Bitmap('assets/icon16_save.png'))
      self.SetStatusText(self.locale["status_update"].decode('utf-8').encode(self.application.app_settings["codepage"]), 1)
      return
    #show ready state
    self.sb.icon.SetBitmap(wx.Bitmap('assets/icon16_accept.png'))
    self.SetStatusText(self.locale["status_ready"].decode('utf-8').encode(self.application.app_settings["codepage"]), 1)
  
  def setIconSize(self, event):
    rect = self.sb.GetFieldRect(0)
    if self.application.app_settings["os"] != "Windows":
      y = rect.y+3
    else:
      y = rect.y
    self.sb.icon.SetPosition((rect.x+3, y))
    
#------------------------------------------------------------------------------------------      
#Main utils
#------------------------------------------------------------------------------------------    
  def getCredentials(self):
    return {"database": self.application.app_settings["database"], "username": self.application.app_settings["username"], "password": self.application.app_settings["password"]}
  
  def getHelp(self,page):
    url = self.application.app_settings["url"]+"/"+self.application.app_config["connection"]["ndr_service"]+"/getHelp"
    url += "?page="+page
    url += "&lang="+str(self.application.app_settings["locale"])[:2]
    url += "&appl=nwx"
    url += "&title=Nervatura WxDemo"
    url += "&subtitle=Ver.No: "+str(self.application.app_config["application"]["version"])
    webbrowser.open(url)
  
  def exportToICal(self, event_id):
    from pyamf.remoting.client import RemotingService  # @UnresolvedImport
    from icalendar import Calendar, Event, vDatetime  # @UnresolvedImport
    import uuid, os
    
    client = RemotingService(self.application.app_settings["url"]+"/"+self.application.app_config["connection"]["npi_service"])
    service = client.getService("default")
    
    events = service.loadTable_amf(self.getCredentials(), "models.event", "id="+str(event_id), None)
    if events.__class__.__name__!="ArrayCollection": 
      wx.MessageBox(str(events), "saveDataSet", wx.OK | wx.ICON_ERROR)
      return
    elif len(events)>0:
      event = events[0]
            
      cal = Calendar()
      cal.add('prodid', '-//nervatura.com/NONSGML Nervatura Calendar//EN')
      cal.add('version', '2.0')
      clevent = Event()
      if event["uid"]!=None:
        clevent['uid'] = event["uid"]
      else:
        clevent['uid'] = uuid.uuid4()
      if event["fromdate"]!=None:
        clevent['dtstart'] = vDatetime(event["fromdate"]).ical()
      if event["todate"]!=None:
        clevent['dtend'] = vDatetime(event["todate"]).ical()  
      if event["subject"]!=None:
        clevent['summary'] = event["subject"]
      if event["place"]!=None:
        clevent['location'] = event["place"]
      if event["eventgroup"]!=None:
        groups = service.loadTable_amf(self.getCredentials(), "models.groups", "id="+str(event["eventgroup"]), None)
        if groups.__class__.__name__=="ArrayCollection":
          if len(groups)>0:
            clevent['category'] = groups[0].groupvalue
      if event["description"]!=None:
        clevent['description'] = event["description"]  
      cal.add_component(clevent)
      
      wildcard = "iCal files (*.ical)|"     \
           "All files (*.*)|*.*"
      dlg = wx.FileDialog(
            self, message="Event export", 
            defaultDir=(os.getenv('USERPROFILE') or os.getenv('HOME')), 
            defaultFile=str(event["calnumber"]).replace("/", "_"), wildcard=wildcard, style=wx.SAVE)
      dlg.SetFilterIndex(0)
      if dlg.ShowModal() == wx.ID_OK:
        icalfile = open(dlg.GetPath()+".ical", 'w')
        icalfile.write(cal.as_string())
        icalfile.close()
      dlg.Destroy()
  
  def getItemFromKey(self, table, field, value):
    #from/return dict
    retval = None
    index = next((i for i in xrange(len(table)) if table[i][field] == value), None)
    if index is not None:
      retval = table[index]
    return retval
  
  def getItemFromKey_(self, table, field, value):
    #from/return object
    retval = None
    index = next((i for i in xrange(len(table)) if table[i].__dict__[field] == value), None)
    if index is not None:
      retval = table[index]
    return retval
  
  def getItemFromKey2(self, table, field1, value1, field2, value2):
    #from/return dict
    retval = None
    index = next((i for i in xrange(len(table)) if table[i][field1] == value1 and table[i][field2] == value2), None)
    if index is not None:
      retval = table[index]
    return retval
  
  def getItemFromKey2_(self, table, field1, value1, field2, value2):
    #from/return object
    retval = None
    index = next((i for i in xrange(len(table)) if table[i].__dict__[field1] == value1 and table[i].__dict__[field2] == value2), None)
    if index is not None:
      retval = table[index]
    return retval
  
  def getSql(self, sqlid):
    conn = sqlite3.connect('storage.db')  # @UndefinedVariable
    cur = conn.cursor()
    rows = cur.execute("select sqlstr from sql where sqlkey=? and engine=?", (sqlid, self.application.app_settings["engine"])).fetchall()
    if len(rows)==0:
      rows = cur.execute("select sqlstr from sql where sqlkey=? and engine='all'", (sqlid,)).fetchall()
    sql = rows[0][0]
    conn.close()
    return sql
  
  def dic2objList(self, table, tablename=None):
    retval = []
    for row in table:
      retval.append(dict2obj(row,tablename))
    return retval
#------------------------------------------------------------------------------------------      
#Menu events
#------------------------------------------------------------------------------------------    
  def main_base_customer_new(self, event):
    from nwx.view.fCustomer import fCustomer  # @UnresolvedImport
    child = fCustomer(self, -1)
    child.Show()
      
  def main_base_customer_browser(self, event):
    from nwx.view.fBrowser import fBrowser  # @UnresolvedImport
    child = fBrowser(self, "CustomerView", str(self.locale["main_base_customer_browser"].decode('utf-8').encode(self.application.app_settings["codepage"])))
    child.Show()
      
  def main_program_help(self, event):
    self.getHelp(self.__class__.__name__)
    
  def main_program_about(self, event):
    wx.MessageBox("Sample program using wxPython and NPI", "Nervatura WxDemo", wx.OK | wx.ICON_INFORMATION)
        
  def main_exit(self, event):
    self.Close()
          
    
      
      