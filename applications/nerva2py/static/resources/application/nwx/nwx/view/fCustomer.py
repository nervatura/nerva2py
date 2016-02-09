# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2015, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import wx.grid
from wx import xrc
from nwx.utils.dataValidator import dataValidator  # @UnresolvedImport
from nwx.dataset.dsCustomer import dsCustomer  # @UnresolvedImport
from nwx.view.fBase import fChildFrame  # @UnresolvedImport
from nwx.utils.gridTable import inputTable, fieldTable  # @UnresolvedImport

class fCustomer(fChildFrame):
  dataSet = None
  
  def __init__(self, parent, iniId):
    try:
      fChildFrame.__init__(self, parent)
      wx.SetCursor(wx.StockCursor(wx.CURSOR_WAIT)) 
      self.parent.setStatusState(1)
      self.SetTitle(self.getLocale(self.__class__.__name__+"_title"))          
      self.SetIcon(wx.Icon('assets/icon16_customer.png', wx.BITMAP_TYPE_PNG , 16, 16))
      self.SetBackgroundColour("#FFFFFF")
      self.Bind(wx.EVT_KEY_DOWN, self._key_down)
      self.Bind(wx.EVT_CLOSE, self._close)
      
      self.body = parent.application.get_resources().LoadPanel(self, "fCustomer") 
      self.body.Bind(wx.EVT_KEY_DOWN, self._key_down)
      xrc.XRCCTRL(self, 'command').SetBackgroundColour(self.parent.application.app_settings["panel_color"])
      
      self.cmd_help = xrc.XRCCTRL(self, 'cmd_help')
      self.cmd_help.SetForegroundColour(self.parent.application.app_settings["help_color"])
      self.cmd_help.name = "cmd_help"
      self.cmd_help.keycode = "[F1]"
      self.cmd_help.Bind(wx.EVT_BUTTON, self._cmd_help)
      self.cmd_help.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.cmd_close = xrc.XRCCTRL(self, 'cmd_close')
      self.cmd_close.SetForegroundColour(self.parent.application.app_settings["close_color"])
      self.cmd_close.name = "cmd_close"
      self.cmd_close.keycode = ""
      self.cmd_close.Bind(wx.EVT_BUTTON, self._cmd_close)
      self.cmd_close.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.cmd_save = xrc.XRCCTRL(self, 'cmd_save')
      self.cmd_save.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_save.name = "cmd_save"
      self.cmd_save.keycode = ""
      self.cmd_save.Bind(wx.EVT_BUTTON, self._cmd_save)
      self.cmd_save.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.cmd_trans = xrc.XRCCTRL(self, 'cmd_trans')
      self.cmd_trans.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_trans.name = "cmd_trans"
      self.cmd_trans.keycode = ""
      self.cmd_trans.Bind(wx.EVT_BUTTON, self._cmd_trans)
      self.cmd_trans.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.head_panel = xrc.XRCCTRL(self, 'head')
      xrc.XRCCTRL(self, 'head0').SetBackgroundColour(self.parent.application.app_settings["panel_color"])
      xrc.XRCCTRL(self, 'panel_custnumber').SetBackgroundColour(self.parent.application.app_settings["label_color"])  
      self.lb_custnumber = xrc.XRCCTRL(self, 'lb_custnumber')
      self.lb_custnumber.SetForegroundColour(self.parent.application.app_settings["color"])
      self.tb_custnumber = xrc.XRCCTRL(self, 'tb_custnumber')
      self.tb_custnumber.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.rb_custype = xrc.XRCCTRL(self, 'rb_custype')
      self.rb_custype.SetLabel(self.getLocale("lb_custype_label"))
      self.rb_custype.SetItemLabel(0, self.getLocale("rb_company_label"))
      self.rb_custype.SetItemLabel(1, self.getLocale("rb_private_label"))
      self.rb_custype.SetItemLabel(2, self.getLocale("rb_other_label"))
      self.rb_custype.SetForegroundColour(self.parent.application.app_settings["color"])
      self.rb_custype.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      xrc.XRCCTRL(self, 'panel_name').SetBackgroundColour(self.parent.application.app_settings["label_color"])  
      self.lb_name = xrc.XRCCTRL(self, 'lb_name')
      self.lb_name.SetForegroundColour(self.parent.application.app_settings["color"])
      self.tb_name = xrc.XRCCTRL(self, 'tb_name')
      self.tb_name.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      xrc.XRCCTRL(self, 'head1').SetBackgroundColour(self.parent.application.app_settings["panel_color"])
      xrc.XRCCTRL(self, 'panel_taxnumber').SetBackgroundColour(self.parent.application.app_settings["label_color"])  
      self.lb_taxnumber = xrc.XRCCTRL(self, 'lb_taxnumber')
      self.lb_taxnumber.SetForegroundColour(self.parent.application.app_settings["color"])
      self.tb_taxnumber = xrc.XRCCTRL(self, 'tb_taxnumber')
      self.tb_taxnumber.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      xrc.XRCCTRL(self, 'panel_account').SetBackgroundColour(self.parent.application.app_settings["label_color"])  
      self.lb_account = xrc.XRCCTRL(self, 'lb_account')
      self.lb_account.SetForegroundColour(self.parent.application.app_settings["color"])
      self.tb_account = xrc.XRCCTRL(self, 'tb_account')
      self.tb_account.Bind(wx.EVT_KEY_DOWN, self._key_down)
      self.cb_inactive = xrc.XRCCTRL(self, 'cb_inactive')
      self.cb_inactive.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cb_inactive.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      xrc.XRCCTRL(self, 'head2').SetBackgroundColour(self.parent.application.app_settings["panel_color"])
      xrc.XRCCTRL(self, 'panel_terms').SetBackgroundColour(self.parent.application.app_settings["label_color"])  
      self.lb_terms = xrc.XRCCTRL(self, 'lb_terms')
      self.lb_terms.SetForegroundColour(self.parent.application.app_settings["color"])
      self.tb_terms = xrc.XRCCTRL(self, 'tb_terms')
      self.tb_terms.Bind(wx.EVT_KEY_DOWN, self._key_down)
      xrc.XRCCTRL(self, 'panel_creditlimit').SetBackgroundColour(self.parent.application.app_settings["label_color"])  
      self.lb_creditlimit = xrc.XRCCTRL(self, 'lb_creditlimit')
      self.lb_creditlimit.SetForegroundColour(self.parent.application.app_settings["color"])
      self.tb_creditlimit = xrc.XRCCTRL(self, 'tb_creditlimit')
      self.tb_creditlimit.Bind(wx.EVT_KEY_DOWN, self._key_down)
      xrc.XRCCTRL(self, 'panel_discount').SetBackgroundColour(self.parent.application.app_settings["label_color"])  
      self.lb_discount = xrc.XRCCTRL(self, 'lb_discount')
      self.lb_discount.SetForegroundColour(self.parent.application.app_settings["color"])
      self.ns_discount = xrc.XRCCTRL(self, 'ns_discount')
      self.ns_discount.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      xrc.XRCCTRL(self, 'panel_group').SetBackgroundColour(self.parent.application.app_settings["label_color"])  
      self.lb_group = xrc.XRCCTRL(self, 'lb_group')
      self.lb_group.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmb_group = xrc.XRCCTRL(self, 'cmb_group')
      self.cmb_group.Bind(wx.EVT_KEY_DOWN, self._key_down)
      self.cmd_group_edit = xrc.XRCCTRL(self, 'cmd_group_edit')
      self.cmd_group_edit.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_group_edit.name = "cmd_group_edit"
      self.cmd_group_edit.keycode = ""
      #self.cmd_group_edit.Bind(wx.EVT_BUTTON, self.cmd_group_edit)
      self.cmd_group_edit.Bind(wx.EVT_KEY_DOWN, self._key_down)
      self.lst_customergroups = xrc.XRCCTRL(self, 'lst_customergroups')
      self.lst_customergroups.Bind(wx.EVT_KEY_DOWN, self._key_down)
      self.cmd_group_add = xrc.XRCCTRL(self, 'cmd_group_add')
      self.cmd_group_add.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_group_add.name = "cmd_group_add"
      self.cmd_group_add.keycode = ""
      self.cmd_group_add.Bind(wx.EVT_BUTTON, self._cmd_group_add)
      self.cmd_group_add.Bind(wx.EVT_KEY_DOWN, self._key_down)
      self.cmd_group_delete = xrc.XRCCTRL(self, 'cmd_group_delete')
      self.cmd_group_delete.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_group_delete.name = "cmd_group_delete"
      self.cmd_group_delete.keycode = ""
      self.cmd_group_delete.Bind(wx.EVT_BUTTON, self._cmd_group_delete)
      self.cmd_group_delete.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      xrc.XRCCTRL(self, 'panel_notes').SetBackgroundColour(self.parent.application.app_settings["label_color"])  
      self.lb_notes = xrc.XRCCTRL(self, 'lb_notes')
      self.lb_notes.SetForegroundColour(self.parent.application.app_settings["color"])
      xrc.XRCCTRL(self, 'panel_inactive').SetBackgroundColour(self.parent.application.app_settings["label_color"])
      self.tb_notes = xrc.XRCCTRL(self, 'tb_notes')
      self.tb_notes.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      xrc.XRCCTRL(self, 'hlabel').SetBackgroundColour(self.parent.application.app_settings["label_color"])
      self.lb_head = xrc.XRCCTRL(self, 'lb_head')
      self.lb_head.SetWindowStyle(wx.NO_BORDER)
      self.lb_head.SetBackgroundColour(self.parent.application.app_settings["label_color"])
      self.lb_head.SetVisitedColour(self.lb_head.GetNormalColour())
      self.lb_head.Bind(wx.EVT_HYPERLINK , self._lb_head)
      
      iml = wx.ImageList(16, 16)
      iml.AddIcon(wx.Icon('assets/icon16_address.png', wx.BITMAP_TYPE_PNG , 16, 16))
      iml.AddIcon(wx.Icon('assets/icon16_contact.png', wx.BITMAP_TYPE_PNG , 16, 16))
      iml.AddIcon(wx.Icon('assets/icon16_deffield.png', wx.BITMAP_TYPE_PNG , 16, 16))
      iml.AddIcon(wx.Icon('assets/icon16_calendar.png', wx.BITMAP_TYPE_PNG , 16, 16))
        
      self.tabSheets = wx.Notebook(self)
      self.tabSheets.AssignImageList(iml)
      self.tabSheets.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
      
      spn = wx.Panel(self.tabSheets, name="ts_fields")
      self.tabSheets.AddPage(spn, self.getLocale("ts_fields_label"), imageId=2)
      spn.SetBackgroundColour("#FFFFFF")
      cpn = wx.Panel(spn)
      bm = wx.StaticBitmap(cpn)
      bm.SetBitmap(wx.Bitmap('assets/icon16_select.png'))
      self.cmd_fields_menu = wx.Button(cpn, 2, self.getLocale("lb_popmenu_label"))
      self.cmd_fields_menu.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_fields_menu.Bind(wx.EVT_BUTTON, self._cmd_pmenu)
      self.cmd_fields_menu.Bind(wx.EVT_KEY_DOWN, self._key_down)
      self.cmb_fields = wx.ComboBox(cpn, style=wx.CB_DROPDOWN)
      self.cmb_fields.Bind(wx.EVT_KEY_DOWN, self._key_down)
      sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
      sizer.Add(bm, flag=wx.ALL|wx.ALIGN_CENTRE_VERTICAL, border=5)
      sizer.AddSpacer(3)
      sizer.Add(self.cmd_fields_menu, flag=wx.ALL)
      sizer.AddSpacer(5)
      sizer.Add(self.cmb_fields, flag=wx.ALL|wx.ALIGN_CENTRE_VERTICAL)
      cpn.SetSizer(sizer)
      self.dg_fields = wx.grid.Grid(spn, id=2)
      self.dg_fields.SetLabelFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
      self.dg_fields.SetDefaultCellFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      self.dg_fields.SetRowLabelSize(30) 
      self.dg_fields.SetMargins(0,0)
      self.dg_fields.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK , self._grid_menu)
      self.dg_fields.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self._grid_change)
      self.dg_fields.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._field_link)
      self.dg_fields.Bind(wx.EVT_KEY_DOWN, self._key_down)
      sizer = wx.FlexGridSizer(2, 1, 0, 0)
      sizer.AddGrowableRow(1)
      sizer.AddGrowableCol(0)
      sizer.Add(cpn, 1, wx.EXPAND)
      sizer.Add(self.dg_fields, 2, wx.EXPAND)
      spn.SetSizer(sizer)
      
      spn = wx.Panel(self.tabSheets, name="ts_address")
      self.tabSheets.AddPage(spn, self.getLocale("ts_address_label"), imageId=0)
      spn.SetBackgroundColour("#FFFFFF")
      cpn = wx.Panel(spn)
      bm = wx.StaticBitmap(cpn)
      bm.SetBitmap(wx.Bitmap('assets/icon16_select.png'))
      self.cmd_address_menu = wx.Button(cpn, 0, self.getLocale("lb_popmenu_label"))
      self.cmd_address_menu.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_address_menu.Bind(wx.EVT_BUTTON, self._cmd_pmenu)
      self.cmd_address_menu.Bind(wx.EVT_KEY_DOWN, self._key_down)
      sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
      sizer.Add(bm, flag=wx.ALL|wx.ALIGN_CENTRE_VERTICAL, border=5)
      sizer.AddSpacer(3)
      sizer.Add(self.cmd_address_menu, flag=wx.ALL)
      cpn.SetSizer(sizer)
      self.dg_address = wx.grid.Grid(spn, id=0)
      self.dg_address.SetLabelFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
      self.dg_address.SetDefaultCellFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      self.dg_address.SetRowLabelSize(30) 
      self.dg_address.SetMargins(0,0)
      self.dg_address.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK , self._grid_menu)
      self.dg_address.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self._grid_change)
      self.dg_address.Bind(wx.EVT_KEY_DOWN, self._key_down)
      sizer = wx.FlexGridSizer(2, 1, 0, 0)
      sizer.AddGrowableRow(1)
      sizer.AddGrowableCol(0)
      sizer.Add(cpn, 1, wx.EXPAND)
      sizer.Add(self.dg_address, 2, wx.EXPAND)
      spn.SetSizer(sizer)
      
      spn = wx.Panel(self.tabSheets, name="ts_contact")
      self.tabSheets.AddPage(spn, self.getLocale("ts_contact_label"), imageId=1)
      spn.SetBackgroundColour("#FFFFFF")
      cpn = wx.Panel(spn)
      bm = wx.StaticBitmap(cpn)
      bm.SetBitmap(wx.Bitmap('assets/icon16_select.png'))
      self.cmd_contact_menu = wx.Button(cpn, 1, self.getLocale("lb_popmenu_label"))
      self.cmd_contact_menu.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_contact_menu.Bind(wx.EVT_BUTTON, self._cmd_pmenu)
      self.cmd_contact_menu.Bind(wx.EVT_KEY_DOWN, self._key_down)
      sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
      sizer.Add(bm, flag=wx.ALL|wx.ALIGN_CENTRE_VERTICAL, border=5)
      sizer.AddSpacer(3)
      sizer.Add(self.cmd_contact_menu, flag=wx.ALL)
      cpn.SetSizer(sizer)
      self.dg_contact = wx.grid.Grid(spn, id=1)
      self.dg_contact.SetLabelFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
      self.dg_contact.SetDefaultCellFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      self.dg_contact.SetRowLabelSize(30) 
      self.dg_contact.SetMargins(0,0)
      self.dg_contact.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK , self._grid_menu)
      self.dg_contact.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self._grid_change)
      self.dg_contact.Bind(wx.EVT_KEY_DOWN, self._key_down)
      sizer = wx.FlexGridSizer(2, 1, 0, 0)
      sizer.AddGrowableRow(1)
      sizer.AddGrowableCol(0)
      sizer.Add(cpn, 1, wx.EXPAND)
      sizer.Add(self.dg_contact, 2, wx.EXPAND)
      spn.SetSizer(sizer)
      
      spn = wx.Panel(self.tabSheets, name="ts_events")
      self.tabSheets.AddPage(spn, self.getLocale("ts_events_label"), imageId=3)
      spn.SetBackgroundColour("#FFFFFF")
      cpn = wx.Panel(spn)
      bm = wx.StaticBitmap(cpn)
      bm.SetBitmap(wx.Bitmap('assets/icon16_select.png'))
      self.cmd_events_menu = wx.Button(cpn, 3, self.getLocale("lb_popmenu_label"))
      self.cmd_events_menu.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_events_menu.Bind(wx.EVT_BUTTON, self._cmd_pmenu)
      self.cmd_events_menu.Bind(wx.EVT_KEY_DOWN, self._key_down)
      sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
      sizer.Add(bm, flag=wx.ALL|wx.ALIGN_CENTRE_VERTICAL, border=5)
      sizer.AddSpacer(3)
      sizer.Add(self.cmd_events_menu, flag=wx.ALL)
      cpn.SetSizer(sizer)
      self.dg_events = wx.grid.Grid(spn, id=3)
      self.dg_events.SetLabelFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
      self.dg_events.SetDefaultCellFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      self.dg_events.EnableEditing(False)
      self.dg_events.SetRowLabelSize(30) 
      self.dg_events.SetMargins(0,0)
      self.dg_events.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK , self._grid_menu)
      self.dg_events.Bind(wx.EVT_KEY_DOWN, self._key_down)
      sizer = wx.FlexGridSizer(2, 1, 0, 0)
      sizer.AddGrowableRow(1)
      sizer.AddGrowableCol(0)
      sizer.Add(cpn, 1, wx.EXPAND)
      sizer.Add(self.dg_events, 2, wx.EXPAND)
      spn.SetSizer(sizer)
      
      sizer = wx.FlexGridSizer(2, 1, 0, 0)
      sizer.AddGrowableRow(1)
      sizer.Add(self.body, 1, wx.EXPAND)
      sizer.Add(self.tabSheets, 2, wx.EXPAND)
      self.SetSizer(sizer)
      self.SetAutoLayout(True)
      
      self.setLocale()
      self.iniId = iniId 
      self.ds = dsCustomer(parent)
      self.dataSet = self.ds.initDataSet(iniId)
      self.ds.loadDataset(self.dataSet)
      self.dataBind()
      self.TransferDataToWindow()
      self.setAddressTable()
      self.setContactTable()
      self.setFieldTable()
      self.setEventsTable()
      
      self.loadGroups()
      self.loadCustomerGroups()
      self.loadDeffield()
      if self.dataSet["customer"][0].id != -1:
        self.SetTitle(self.dataSet["customer"][0].custnumber)
      self.dataSet["changeData"]=False     
      
      wx.CallAfter(self.Layout)
      self.tb_custnumber.SetFocus()
    except Exception, err:
      wx.MessageBox(str(err), "__init__", wx.OK | wx.ICON_ERROR)
    finally:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
      self.parent.setStatusState(0)
  
  def getCusttypeValue(self):
    custtype_name = self.parent.getItemFromKey(self.dataSet["groups"], "id", self.dataSet["customer"][0].custtype).groupvalue
    if custtype_name=="private":
      return 1
    elif custtype_name=="other":
      return 2
    else:
      return 0
    
  def dataBind(self):
    self.tb_custnumber.SetValidator(dataValidator(wtype="textBox", data=self.dataSet["customer"][0], 
      field="custnumber", required=True, formatter=None, validationCB=self.dataValidation,
      changeCB=self.changeData))
    self.tb_name.SetValidator(dataValidator(wtype="textBox", data=self.dataSet["customer"][0], 
      field="custname", required=True, formatter=None, validationCB=self.dataValidation,
      changeCB=self.changeData))
    
    self.rb_custype.SetValidator(dataValidator(wtype="radioBox", data=self.dataSet["customer"][0], 
      field="custtype", required=False, formatter=None, validationCB=self.dataValidation, 
      changeCB=self.changeData))
    self.rb_custype.SetSelection(self.getCusttypeValue())
    
    self.tb_taxnumber.SetValidator(dataValidator(wtype="textBox", data=self.dataSet["customer"][0], 
      field="taxnumber", required=False, formatter=None, validationCB=self.dataValidation,
      changeCB=self.changeData))
    self.tb_account.SetValidator(dataValidator(wtype="textBox", data=self.dataSet["customer"][0], 
      field="account", required=False, formatter=None, validationCB=self.dataValidation,
      changeCB=self.changeData))
    self.cb_inactive.SetValidator(dataValidator(wtype="checkBox", data=self.dataSet["customer"][0], 
      field="inactive", required=False, formatter=None, validationCB=self.dataValidation,
      changeCB=self.changeData))
    self.tb_terms.SetValidator(dataValidator(wtype="spinBox", data=self.dataSet["customer"][0], 
      field="terms", required=False, formatter=None, validationCB=self.dataValidation,
      changeCB=self.changeData))
    self.tb_creditlimit.SetValidator(dataValidator(wtype="intBox", data=self.dataSet["customer"][0], 
      field="creditlimit", required=False, formatter=None, validationCB=self.dataValidation,
      changeCB=self.changeData, maxLength=9))
    self.ns_discount.SetValidator(dataValidator(wtype="spinBox", data=self.dataSet["customer"][0], 
      field="discount", required=False, formatter=None, validationCB=self.dataValidation,
      changeCB=self.changeData))
    self.tb_notes.SetValidator(dataValidator(wtype="textBox", data=self.dataSet["customer"][0], 
      field="notes", required=False, formatter=None, validationCB=self.dataValidation,
      changeCB=self.changeData))
  
  def address_filter(self,i):
    return not bool(self.dataSet["address"][i].deleted)
  
  def contact_filter(self,i):
    return not bool(self.dataSet["contact"][i].deleted)
  
  def fieldvalue_filter(self,i):
    return bool(self.dataSet["fieldvalue"][i].visible) and (not bool(self.dataSet["fieldvalue"][i].deleted))
  
  def link_filter(self,i):
    return not bool(self.dataSet["link"][i].deleted)
    
  def getDataRows(self, table, filter_func):
    ifilter = filter(filter_func, xrange(len(table)))
    restable=[]
    for i in ifilter:
      restable.append(table[i])
    return restable
  
  def setAddressTable(self):             
    dataField=["country", "state", "zipcode", "city", "street", "notes"] 
    headerText={"country":self.getLocale("address_country_headerText"),
                "state":self.getLocale("address_state_headerText"),
                "zipcode":self.getLocale("address_zipcode_headerText"),
                "city":self.getLocale("address_city_headerText"),
                "street":self.getLocale("address_street_headerText"),
                "notes":self.getLocale("address_notes_headerText")}       
    stable = inputTable(dataField, None, headerText, self.getDataRows(self.dataSet["address"],self.address_filter))
    self.dg_address.SetTable(stable, True)
    self.dg_address.AutoSizeColumns(False)
    self.dg_address.ForceRefresh()
  
  def setContactTable(self):            
    dataField=["firstname", "surname", "status", "phone", "fax", "mobil", "email", "notes"] 
    headerText={"firstname":self.getLocale("contact_firstname_headerText"),
                "surname":self.getLocale("contact_surname_headerText"),
                "status":self.getLocale("contact_status_headerText"),
                "phone":self.getLocale("contact_phone_headerText"),
                "fax":self.getLocale("contact_fax_headerText"),
                "mobil":self.getLocale("contact_mobil_headerText"),
                "email":self.getLocale("contact_email_headerText"),
                "notes":self.getLocale("contact_notes_headerText")}       
    stable = inputTable(dataField, None, headerText, self.getDataRows(self.dataSet["contact"],self.contact_filter))
    self.dg_contact.SetTable(stable, True)
    self.dg_contact.AutoSizeColumns(False)
    self.dg_contact.ForceRefresh()
  
  def setFieldTable(self):             
    dataField=["description", "value", "notes"] 
    headerText={"description":self.getLocale("fields_description_headerText"),
                "value":self.getLocale("fields_value_headerText"),
                "notes":self.getLocale("fields_notes_headerText")}
    stable = fieldTable(dataField, headerText, self.getDataRows(self.dataSet["fieldvalue"],self.fieldvalue_filter))
    self.dg_fields.SetTable(stable, True)
    self.dg_fields.AutoSizeColumns(False)
    self.dg_fields.ForceRefresh()
  
  def setEventsTable(self):            
    dataField=["calnumber", "vf_groups", "fromdate", "todate", "subject"] 
    headerText={"calnumber":self.getLocale("events_calnumber_headerText"),
                "vf_groups":self.getLocale("events_groups_headerText"),
                "fromdate":self.getLocale("events_fromdate_headerText"),
                "todate":self.getLocale("events_todate_headerText"),
                "subject":self.getLocale("events_subject_headerText")}
    dataType={"calnumber":wx.grid.GRID_VALUE_STRING, 
              "vf_groups":wx.grid.GRID_VALUE_STRING, 
              "fromdate":wx.grid.GRID_VALUE_DATETIME,
              "todate":wx.grid.GRID_VALUE_DATETIME,  
              "subject":wx.grid.GRID_VALUE_STRING}       
    stable = inputTable(dataField, dataType, headerText, self.dataSet["calendar_view"])
    self.dg_events.SetTable(stable, True)
    self.dg_events.AutoSizeColumns(False)
    self.dg_events.ForceRefresh()
              
  def dataValidation(self, data, field, value, required, flValid, validateError):
    if flValid==False:
      valErr = validateError.split("|")
      if valErr[0]=="required":
        if valErr[1]=="custnumber" or valErr[1]=="custname":
          wx.MessageBox(self.getLocale("alert_err_noname"),
            self.getLocale("alert_warning_lb"), wx.OK | wx.ICON_ERROR)
          return
  
  def changeData(self, win, oldValue, newValue, dataRecord, dataField):
    self.dataSet["changeData"] = True
    if dataField=="custtype":
      if newValue==2:
        self.dataSet["customer"][0].custtype = self.parent.getItemFromKey2(self.dataSet["groups"], "groupname", "custtype", "groupvalue", "other").id
      elif newValue==1:
        self.dataSet["customer"][0].custtype = self.parent.getItemFromKey2(self.dataSet["groups"], "groupname", "custtype", "groupvalue", "private").id
      else:
        self.dataSet["customer"][0].custtype = self.parent.getItemFromKey2(self.dataSet["groups"], "groupname", "custtype", "groupvalue", "company").id
  
  def loadCustomerGroups(self):
    self.lst_customergroups.Clear()
    for item in self.dataSet["link"]:
      if item.deleted==0:
        self.lst_customergroups.Append(item.description, item)
  
  def loadGroups(self):
    self.cmb_group.Clear()
    for item in self.dataSet["groups"]:
      if item.inactive==False and item.groupname == "customer":
        self.cmb_group.Append(item.groupvalue, item)
        
  def loadDeffield(self):
    self.cmb_fields.Clear()
    for item in self.dataSet["deffield"]:
      self.cmb_fields.Append(item.description, item)
        
#------------------------------------------------------------------------------------------      
#Events
#------------------------------------------------------------------------------------------  
  def _key_down(self, event):
    keycode = event.GetKeyCode()
    if keycode == wx.WXK_F1:
      self._cmd_help()
    if event.ControlDown() ==True and keycode == 49:
      #[Ctrl][1]
      self.Close()
    if event.ControlDown() ==True and keycode == 50:
      #[Ctrl][2]
      self._cmd_save()
    if event.ControlDown() ==True and keycode == 51:
      #[Ctrl][3]
      pass
      #self._cmd_trans()
    event.Skip()
    
  def _cmd_save(self, event=None):
    if self.Validate():
      self.TransferDataFromWindow()
      self.ds.saveDataSet(self.dataSet, self)
      self.TransferDataToWindow()
      self.SetTitle(self.dataSet["customer"][0].custnumber)
      self.dirty = True
  
  def _cmd_trans(self, event=None):
    self.showPopMenu("trans", self.cmd_trans)
  
  def _cmd_group_add(self, event=None):
    if self.cmb_group.GetSelection()!=wx.NOT_FOUND:
      item = self.cmb_group.GetClientData(self.cmb_group.GetSelection())
      self.ds.addCustomerGroups(self.dataSet, item.id)
      self.loadCustomerGroups()
  
  def _cmd_group_delete(self, event=None):
    if self.lst_customergroups.GetSelection()!=wx.NOT_FOUND:
      item = self.lst_customergroups.GetClientData(self.lst_customergroups.GetSelection())
      self.ds.deleteCustomerGroups(self.dataSet, item)
      self.loadCustomerGroups()
      
  def _lb_head(self, event=None):
    self.showHead()
    event.StopPropagation()

  def _grid_menu(self, event=None):
    if event.GetId()==0 or event.GetId()==1:
      self.showPopMenu("datarow")
    elif event.GetId()==2:
      self.showPopMenu("fieldrow")
    elif event.GetId()==3:
      self.showPopMenu("eventrow")
      
  def _cmd_pmenu(self, event=None):
    corY = self.tabSheets.GetPosition()[1]+30
    if event.GetId()==0 or event.GetId()==1:
      self.showPopMenu("datarow", self.cmd_address_menu, corY)
    elif event.GetId()==2:
      self.showPopMenu("fieldrow", self.cmd_address_menu, corY)
    elif event.GetId()==3:
      self.showPopMenu("eventrow", self.cmd_address_menu, corY)
      
  def _grid_change(self,  event=None):
    self.dataSet["changeData"]=True
     
#------------------------------------------------------------------------------------------      
#Menu events
#------------------------------------------------------------------------------------------ 
  def _customer_print(self, event):
    wx.MessageBox("Print Customer data...", ":-)", wx.OK | wx.ICON_INFORMATION)
  
  def _customer_delete(self, event):
    dlg = wx.MessageDialog(self, self.getLocale("alert_delete_ms"), self.getLocale("alert_warning_lb"),
        wx.YES_NO | wx.ICON_INFORMATION | wx.NO_DEFAULT)
    ms = dlg.ShowModal()
    dlg.Destroy()
    if ms==wx.ID_NO:
        return
    if self.dataSet["customer"][0].id==-1:
      self.dataSet["changeData"]=False
      self.Close()
    else:
      if self.ds.deleteDataSet(self.dataSet, self):
        self.dataSet["changeData"]=False
        self.dirty = True
        self.Close()
      
  def _datarow_new(self, event):
    if self.tabSheets.GetCurrentPage().GetName()=="ts_address":
      self.ds.addAddressRow(self.dataSet)
      self.setAddressTable()
    if self.tabSheets.GetCurrentPage().GetName()=="ts_contact":
      self.ds.addContactRow(self.dataSet)
      self.setContactTable()
  
  def _datarow_delete(self, event):
    if self.tabSheets.GetCurrentPage().GetName()=="ts_address":
      delRows = []
      for srow in self.dg_address.GetSelectedRows():
        delRows.append(self.dg_address.GetTable().GetRowData(srow))
      for drow in delRows:
        self.ds.deleteAddressRow(self.dataSet, drow)
      self.setAddressTable()
    if self.tabSheets.GetCurrentPage().GetName()=="ts_contact":
      delRows = []
      for srow in self.dg_contact.GetSelectedRows():
        delRows.append(self.dg_contact.GetTable().GetRowData(srow))
      for drow in delRows:
        self.ds.deleteContactRow(self.dataSet, drow)
      self.setContactTable()
  
  def _field_new(self, event):
    if self.cmb_fields.GetSelection()!=wx.NOT_FOUND:
      dfitem = self.cmb_fields.GetClientData(self.cmb_fields.GetSelection())
      self.ds.addFieldRow(self.dataSet, dfitem)
      self.setFieldTable()
      
  def _field_delete(self, event):
    delRows = []
    for srow in self.dg_fields.GetSelectedRows():
      delRows.append(self.dg_fields.GetTable().GetRowData(srow))
    for drow in delRows:
      self.ds.deleteFieldRow(self.dataSet, drow)
    self.setFieldTable()
  
  def _event_new(self, event):
    wx.MessageBox("New Event...", ":-)", wx.OK | wx.ICON_INFORMATION)
  
  def _event_edit(self, event):
    wx.MessageBox("Edit Event...", ":-)", wx.OK | wx.ICON_INFORMATION)
  
  def _event_export(self, event):
    if hasattr(event, "GetRow"):
      row = event.GetRow()
    elif len(self.dg_events.GetSelectedRows())>0:
      row = self.dg_events.GetSelectedRows()[0]
    else:
      wx.MessageBox("Please select an entire row!", "Nervatura WxDemo", wx.OK | wx.ICON_INFORMATION)
      return
    id = self.dg_events.GetTable().__dict__["data"][row]["id"]  # @ReservedAssignment
    self.parent.exportToICal(id)
      