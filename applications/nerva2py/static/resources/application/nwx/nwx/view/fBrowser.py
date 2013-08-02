# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Project
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import os
from wx import xrc
from nwx.view.fBase import fChildFrame  # @UnresolvedImport
from nwx.dataset.dsBrowser import dsBrowser  # @UnresolvedImport

import wx.grid
import  wx.lib.gridmovers
from nwx.utils.gridTable import browserTable, filterTable  # @UnresolvedImport
import xlwt  # @UnresolvedImport

class fBrowser(fChildFrame):
  mainView = ""
  sectionView = ""
  _lst_selcol = []
  _lst_filter = []
  filter_type = {}
  sorting = {}
  dg_result = None
  defCfvalue = 100
  
  def __init__(self, parent, mainView, title=""):
    try:
      fChildFrame.__init__(self, parent)
      wx.SetCursor(wx.StockCursor(wx.CURSOR_WAIT)) 
      self.parent.setStatusState(1)
      self.SetTitle(self.getLocale(self.__class__.__name__+"_title"))   
      self.SetIcon(wx.Icon('assets/icon16_browser.png', wx.BITMAP_TYPE_PNG , 16, 16))
      self.SetBackgroundColour("#FFFFFF")
      self.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.body = parent.application.get_resources().LoadPanel(self, "fBrowser")
      self.head_panel = xrc.XRCCTRL(self, 'filter')
      self.body.Bind(wx.EVT_KEY_DOWN, self._key_down)
      xrc.XRCCTRL(self, 'command').SetBackgroundColour(self.parent.application.app_settings["panel_color"])
      xrc.XRCCTRL(self, 'filter0').SetBackgroundColour(self.parent.application.app_settings["panel_color"])
      xrc.XRCCTRL(self, 'filter1').SetBackgroundColour(self.parent.application.app_settings["panel_color"])
      xrc.XRCCTRL(self, 'filter2').SetBackgroundColour(self.parent.application.app_settings["panel_color"])
      
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
      
      self.cmd_load = xrc.XRCCTRL(self, 'cmd_load')
      self.cmd_load.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_load.name = "cmd_load"
      self.cmd_load.keycode = ""
      self.cmd_load.Bind(wx.EVT_BUTTON, self._cmd_load)
      self.cmd_load.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.cmd_view = xrc.XRCCTRL(self, 'cmd_view')
      self.cmd_view.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_view.name = "cmd_view"
      self.cmd_view.keycode = ""
      self.cmd_view.Bind(wx.EVT_BUTTON, self._cmd_view)
      self.cmd_view.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.cmd_trans = xrc.XRCCTRL(self, 'cmd_trans')
      self.cmd_trans.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_trans.name = "cmd_trans"
      self.cmd_trans.keycode = ""
      self.cmd_trans.Bind(wx.EVT_BUTTON, self._cmd_trans)
      self.cmd_trans.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.cmd_export = xrc.XRCCTRL(self, 'cmd_export')
      self.cmd_export.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_export.name = "cmd_export"
      self.cmd_export.keycode = ""
      self.cmd_export.Bind(wx.EVT_BUTTON, self._cmd_export)
      self.cmd_export.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      xrc.XRCCTRL(self, 'panel_viewlist').SetBackgroundColour(self.parent.application.app_settings["label_color"])  
      self.lb_viewlist = xrc.XRCCTRL(self, 'lb_viewlist')
      self.lb_viewlist.SetForegroundColour(self.parent.application.app_settings["color"])
      
      self.lst_view = xrc.XRCCTRL(self, 'lst_view')
      self.lst_view.Bind(wx.EVT_LISTBOX , self._lst_view)
      self.lst_view.Bind(wx.EVT_KEY_DOWN, self._key_down)
      xrc.XRCCTRL(self, 'panel_autocol').SetBackgroundColour(self.parent.application.app_settings["label_color"])
      self.cb_autocol = xrc.XRCCTRL(self, 'cb_autocol')
      self.cb_autocol.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cb_autocol.Bind(wx.EVT_CHECKBOX , self._cb_autocol)
      self.cb_autocol.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.cmd_total = xrc.XRCCTRL(self, 'cmd_total')
      self.cmd_total.Bind(wx.EVT_BUTTON , self._cmd_total)
      self.cmd_total.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.cmd_save = xrc.XRCCTRL(self, 'cmd_save')
      self.cmd_save.Bind(wx.EVT_BUTTON , self._cmd_save)
      self.cmd_save.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      xrc.XRCCTRL(self, 'panel_selcol').SetBackgroundColour(self.parent.application.app_settings["label_color"])
      self.lb_selcol = xrc.XRCCTRL(self, 'lb_selcol')
      self.lb_selcol.SetForegroundColour(self.parent.application.app_settings["color"])
      
      self.cmd_selcol_all = xrc.XRCCTRL(self, 'cmd_selcol_all')
      self.cmd_selcol_all.Bind(wx.EVT_BUTTON , self._cmd_selcol_all)
      self.cmd_selcol_all.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.cmd_selcol_none = xrc.XRCCTRL(self, 'cmd_selcol_none')
      self.cmd_selcol_none.Bind(wx.EVT_BUTTON , self._cmd_selcol_none)
      self.cmd_selcol_none.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.lst_selcol = xrc.XRCCTRL(self, 'lst_selcol')
      self.lst_selcol.Bind(wx.EVT_CHECKLISTBOX, self._lst_selcol)
      self.lst_selcol.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      xrc.XRCCTRL(self, 'panel_filterlist').SetBackgroundColour(self.parent.application.app_settings["label_color"])
      self.lb_filterlist = xrc.XRCCTRL(self, 'lb_filterlist')
      self.lb_filterlist.SetForegroundColour(self.parent.application.app_settings["color"])
      self.lst_filter = xrc.XRCCTRL(self, 'lst_filter')
      xrc.XRCCTRL(self, 'panel_filter').SetBackgroundColour(self.parent.application.app_settings["label_color"])
      self.lb_filter = xrc.XRCCTRL(self, 'lb_filter')
      self.lb_filter.SetForegroundColour(self.parent.application.app_settings["color"])
      self.cmd_filter = xrc.XRCCTRL(self, 'cmd_filter')
      
      self.cmd_filter_add = xrc.XRCCTRL(self, 'cmd_filter_add')
      self.cmd_filter_add.Bind(wx.EVT_BUTTON , self._cmd_filter_add)
      self.cmd_filter_add.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.cmd_filter_delete = xrc.XRCCTRL(self, 'cmd_filter_delete')
      self.cmd_filter_delete.Bind(wx.EVT_BUTTON , self._cmd_filter_delete)
      self.cmd_filter_delete.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.dg_filters = xrc.XRCCTRL(self, 'dg_filters')
      self.dg_filters.SetLabelFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
      self.dg_filters.SetDefaultCellFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      self.dg_filters.SetDefaultRowSize(22)
      self.dg_filters.SetRowLabelSize(30) 
      self.dg_filters.SetMargins(0,0)
      self.dg_filters.Bind(wx.EVT_KEY_DOWN, self._key_down)
      self.dg_filters.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self._dg_filters)
      
      #self.ns_fixcol = xrc.XRCCTRL(self, 'ns_fixcol')
      xrc.XRCCTRL(self, 'data').SetBackgroundColour(self.parent.application.app_settings["label_color"])
      self.lb_datagrid = xrc.XRCCTRL(self, 'lb_datagrid')
      self.lb_datagrid.SetBackgroundColour(self.parent.application.app_settings["label_color"])
      self.lb_datagrid.SetVisitedColour(self.lb_datagrid.GetNormalColour())
      self.lb_datagrid.Bind(wx.EVT_HYPERLINK , self._lb_datagrid) 
      
      self.dg_result = wx.grid.Grid(self)
      self.dg_result.EnableEditing(False)
      self.dg_result.SetLabelFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
      self.dg_result.SetDefaultCellFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      self.dg_result.SetDefaultRowSize(22)
      self.dg_result.SetRowLabelSize(30) 
      self.dg_result.SetMargins(0,0)
      self.dg_result.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK , self._dg_result_sort)
      self.dg_result.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK , self._dg_result_menu)
      self.dg_result.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK , self._dg_result_dbl)
      self.dg_result.Bind(wx.EVT_KEY_DOWN, self._key_down)
      
      self.dg_result.Bind(wx.grid.EVT_GRID_COL_SIZE, self._dg_result_col_size)
      wx.lib.gridmovers.GridColMover(self.dg_result)
      self.dg_result.Bind(wx.lib.gridmovers.EVT_GRID_COL_MOVE, self._dg_result_col_move)
      wx.lib.gridmovers.GridRowMover(self.dg_result)
      self.dg_result.Bind(wx.lib.gridmovers.EVT_GRID_ROW_MOVE, self._dg_result_row_move)
      
      self.dg_total = wx.grid.Grid(self)
      self.dg_total.CreateGrid(0,1)
      self.dg_total.SetColSize(0, 120)
      self.dg_total.SetColLabelValue(0, self.getLocale("dg_total_headerText"))
      self.dg_total.EnableEditing(False)
      self.dg_total.SetLabelFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
      self.dg_total.SetDefaultCellFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      self.dg_total.SetRowLabelSize(0) 
      self.dg_total.SetMargins(0,0)
      self.dg_total.Bind(wx.EVT_KEY_DOWN, self._key_down)
      self.dg_total.Hide()
      
      sizer = wx.FlexGridSizer(2, 1, 0, 0)
      sizer.AddGrowableRow(1)
      sizer.Add(self.body, 1, wx.EXPAND)
      sizer2 = wx.FlexGridSizer(1, 2, 0, 0)
      sizer2.AddGrowableRow(0)
      sizer2.Add(self.dg_total, 1, wx.EXPAND)
      sizer2.Add(self.dg_result, 2, wx.EXPAND)
      sizer.Add(sizer2, 2, wx.EXPAND)
      self.SetSizer(sizer)
      
      self.setLocale()
      self.mainView = mainView 
      self.ds = dsBrowser(parent)
      self.dataSet = self.ds.initDataSet()
      self.dataSet["mainView"]=mainView
      self.ds.loadDataset(self.dataSet)
      self.loadViewList()
      self.setResultData()     
      wx.CallAfter(self.Layout)
    except Exception, err:
      wx.MessageBox(str(err), "__init__", wx.OK | wx.ICON_ERROR)
    finally:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
      self.parent.setStatusState(0)
  
  def loadViewList(self):
    for item in self.dataSet["applviews"]:
      self.lst_view.Append(item["langname"], item)
    self.lst_view.Select(0)
            
    for item in self.dataSet["viewfields"]:
      if item["fieldtype"] == "checkbox":
        self.lst_filter.Append(item["langname"])
        self._lst_filter.append(item)
      
    config = self.ds.getConfig(self.dataSet, "browserConfig", "autoBrowserCol", None)
    if (len(config)>0):
      if (config[0].cfvalue == "true") or (config[0].cfvalue == "True") or (config[0].cfvalue == "t"):
        self.cb_autocol.SetValue(True)
      else:
        self.cb_autocol.SetValue(False)
    
    config = self.ds.getConfig(self.dataSet, "browserConfig", "showTotal", None)
    if (len(config)>0):
      if (config[0].cfvalue == "true") or (config[0].cfvalue == "True") or (config[0].cfvalue == "t"):
        self.dg_total.Show()
      else:
        self.dg_total.Hide()
    
    self.loadSectionView(self.mainView)  
  
  def loadSectionView(self, viewName):
    self.sectionView = viewName
    self.dataSet["result"] = []
    self.sorting = {}
    self.lb_datagrid.SetLabel(self.getLocale("lb_datagrid_label"))
    
    self.lst_selcol.Clear()
    self._lst_selcol = []
    lst_selcol = []
    for item in self.dataSet["viewfields"]:
      if item["viewname"] == viewName and item["fieldtype"] != "checkbox" and item["fieldtype"] != "filter":
        lst_selcol.append(item)
    lst_selcol.sort(cmp=None, key=lambda item: item["orderby"], reverse=False)
    
    self.filter_type = {"dateLabel":": ", "dateField":[], 
                        "numberLabel":": ", "numberField":[], "boolLabel":": ", "boolField":[],
                        "stringLabel":": ", "stringField":[]}
    for item in lst_selcol:
      lst_idx = self.lst_selcol.Append(item["langname"])
      self._lst_selcol.append(item)
      colConfig = self.ds.getConfig(self.dataSet, viewName, item["fieldname"], self.mainView)
      if len(colConfig)>0:
        self.lst_selcol.Check(lst_idx, True)
      else:
        self.lst_selcol.Check(lst_idx, False)
        
      if item.fieldtype=="date":
        self.filter_type["dateField"].append(item.fieldname)
        if self.filter_type["dateLabel"]==": ":
          self.filter_type["dateLabel"] = ": "+item.langname
        else:
          self.filter_type["dateLabel"] = self.filter_type["dateLabel"]+", "+item.langname
      elif item.fieldtype=="float" or item.fieldtype=="integer":
        self.filter_type["numberField"].append(item.fieldname)
        if self.filter_type["numberLabel"]==": ":
          self.filter_type["numberLabel"] = ": "+item.langname
        else:
          self.filter_type["numberLabel"] = self.filter_type["numberLabel"]+", "+item.langname
      elif item.fieldtype=="bool":
        self.filter_type["boolField"].append(item.fieldname)
        if self.filter_type["boolLabel"]==": ":
          self.filter_type["boolLabel"] = ": "+item.langname
        else:
          self.filter_type["boolLabel"] = self.filter_type["boolLabel"]+", "+item.langname
      else:
        self.filter_type["stringField"].append(item.fieldname)
        if self.filter_type["stringLabel"]==": ":
          self.filter_type["stringLabel"] = ": "+item.langname
        else:
          self.filter_type["stringLabel"] = self.filter_type["stringLabel"]+", "+item.langname
    
    self.cmd_filter.Clear()
    if self.filter_type["stringLabel"]!=": ": 
      self.cmd_filter.Append(self.getLocale("browser_filter_text"), "browser_filter_text")
    if self.filter_type["numberLabel"]!=": ":
      self.cmd_filter.Append(self.getLocale("browser_filter_number"), "browser_filter_number")
    if self.filter_type["dateLabel"]!=": ":
      self.cmd_filter.Append(self.getLocale("browser_filter_date"), "browser_filter_date")
    if self.filter_type["boolLabel"]!=": ":
      self.cmd_filter.Append(self.getLocale("browser_filter_boolean"), "browser_filter_boolean")       

    self.setFilterData()      
    self.setResultData()  
  
  
  def setFilterData(self):            
    self.dg_filters.ClearGrid()
    dataField=["fieldlabel", "ftype", "fvalue"] 
    headerText={"fieldlabel":self.getLocale("filter_fieldname_headerText"),
                "ftype":self.getLocale("filter_ftype_headerText"),
                "fvalue":self.getLocale("filter_fvalue_headerText")} 
    
    filter_table = [] 
    for fitem in self.dataSet["filter"]:
      if fitem.viewname == self.sectionView:
        filter_table.append(fitem)
    filter_table.sort(cmp=None, key=lambda item: item.id, reverse=False)
    
    stable = filterTable(dataField, headerText, self.filter_type, filter_table)
    self.dg_filters.SetTable(stable, True)
    self.dg_filters.SetColSize(0, 150)
    self.dg_filters.SetColSize(1, 50)
    self.dg_filters.SetColSize(2, 160)
    self.dg_filters.ForceRefresh()
      
  def setResultData(self):
    self.dg_result.ClearGrid()
    self.lsrow = None
    dataField=[] 
    headerText={} 
    dataType={}
    view_table = self.ds.getConfig(self.dataSet, self.sectionView, None, None) 
    if len(view_table)>0:
      view_table.sort(cmp=None, key=lambda item: item.orderby, reverse=False)
      for col in view_table:
        selcol =  self.parent.getItemFromKey(self._lst_selcol, "fieldname", col.cfname)
        if selcol:
          dataField.append(selcol["fieldname"])
          headerText[selcol["fieldname"]] = selcol["langname"]
          dataType[selcol["fieldname"]] = self.getGTypeFromFType(selcol["fieldtype"])
    else:
      dlg = wx.MessageDialog(self, self.getLocale("alert_nocol_ms"),self.getLocale("alert_warning_lb"),
                             wx.YES_NO | wx.ICON_INFORMATION)
      ms = dlg.ShowModal()
      dlg.Destroy()
      if ms==wx.ID_YES:
        for icol in range(len(self._lst_selcol)):
          dataField.append(self._lst_selcol[icol]["fieldname"])
          headerText[self._lst_selcol[icol]["fieldname"]] = self._lst_selcol[icol]["langname"]
          dataType[self._lst_selcol[icol]["fieldname"]] = self.getGTypeFromFType(self._lst_selcol[icol]["fieldtype"])
          self.ds.setConfig(self.dataSet, self.sectionView, self._lst_selcol[icol]["fieldname"], self.defCfvalue, icol, self.mainView)
          self.lst_selcol.Check(icol, True)
        
    stable = browserTable(dataField, dataType, headerText, self.dataSet["result"], self.sorting)
    self.dg_result.SetTable(stable, True)
    if self.cb_autocol.IsChecked():
      self.dg_result.AutoSizeColumns(False)
    else:
      self.setUserColSize()
    self.dg_result.ForceRefresh()
    
    self.createTotalRow()
    label = self.getLocale("lb_datagrid_label")
    if len(self.dataSet["result"])>0:
      label = label+" ("+str(len(self.dataSet["result"]))+")"
    self.lb_datagrid.SetLabel(label)
    self.lb_datagrid.Refresh()
    wx.CallAfter(self.Layout)  
  
  def loadData(self):
    self.dataSet["result"] = []
    self.sorting = {}
    param = {}
    param["WhereString"] = ""
    param["HavingString"] = ""
    param["paramList"] = []
    self.setWhereString(param);
    self.ds.loadResult(self.dataSet, self.dataSet["applviews"][self.lst_view.GetSelection()]["sqlstr"], param);
    self.setResultData()
    wx.CallAfter(self.Layout)
    
  def setUserColSize(self):
    for col in range(self.dg_result.GetNumberCols()):
      colConfig = self.ds.getConfig(self.dataSet, self.sectionView , self.dg_result.GetTable().GetColId(col), self.mainView)[0]
      self.dg_result.SetColSize(col, int(colConfig.cfvalue))
      
  def updateColConfig(self):
    for col in range(self.dg_result.GetNumberCols()):
      self.ds.setConfig(self.dataSet, self.sectionView, self.dg_result.GetTable().GetColId(col), self.dg_result.GetColSize(col), col, self.mainView)
      
  def getGTypeFromFType(self, ftype):
    if ftype=="bool":
      return wx.grid.GRID_VALUE_BOOL
    elif ftype=="date":
      return wx.grid.GRID_VALUE_DATETIME
    elif ftype=="integer":
      #return wx.grid.GRID_VALUE_LONG
      return wx.grid.GRID_VALUE_NUMBER
    elif ftype=="float":
      #return wx.grid.GRID_VALUE_FLOAT
      return wx.grid.GRID_VALUE_NUMBER
    elif ftype=="notes":
      return wx.grid.GRID_VALUE_TEXT
    else:
      return wx.grid.GRID_VALUE_STRING
  
  def createViewMenu(self):
    pmenu = wx.Menu()
    for col in range(self.lst_view.GetCount()):
      view = self.lst_view.GetClientData(col)
      pitem = wx.MenuItem(pmenu, col, view["langname"])
      pitem.SetBitmap(wx.Bitmap("assets/icon16_select.png", wx.BITMAP_TYPE_PNG))
      pitem.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      self.Bind(wx.EVT_MENU, getattr(self, "_browser_select_view"), pitem)
      pmenu.AppendItem(pitem)
    pos = self.cmd_view.GetPosition()
    pos[1] = pos[1]+self.cmd_view.GetSize()[1]
    self.PopupMenu(pmenu, pos)
    pmenu.Destroy()  
      
  def createTotalRow(self):
    if self.dg_total.IsShown()==False:
      return
    if self.dg_total.GetTable().GetNumberRows()>0:
      self.dg_total.DeleteRows(0, self.dg_total.GetTable().GetNumberRows())
    if len(self.dataSet["result"])==0:
      return
    tgrow=0
    for gcol in range(self.dg_result.GetTable().GetNumberCols()):
      fieldname = self.dg_result.GetTable().GetColId(gcol)
      viewfield =  self.parent.getItemFromKey2(self.dataSet["viewfields"], 
        "viewname", self.sectionView, "fieldname", fieldname)
      if viewfield["aggretype"] != None and viewfield["aggretype"] != "" and viewfield["aggretype"] != "<>" and (viewfield["fieldtype"] == "float" or viewfield["fieldtype"] == "integer"):
        tvalue=0 
        tcount=0
        for grow in self.dataSet["result"]:
          if grow[fieldname]!=None or grow[fieldname]!="":
            if viewfield["aggretype"]=="count":
              tvalue = tvalue + 1
            elif viewfield["aggretype"]=="sum":
              tvalue = tvalue + grow[fieldname]
            elif viewfield["aggretype"]=="avg":
              tcount = tcount + 1
              tvalue = tvalue + grow[fieldname]
        if viewfield["aggretype"] == "avg": 
          tvalue = tvalue / tcount
        self.dg_total.AppendRows()
        self.dg_total.SetCellAlignment(tgrow, 0, wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
        self.dg_total.SetCellValue(tgrow, 0, viewfield["langname"])
        tgrow = tgrow + 1
        self.dg_total.AppendRows()
        self.dg_total.SetCellAlignment(tgrow, 0, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.dg_total.SetCellValue(tgrow, 0, str(tvalue))
        tgrow = tgrow + 1 

  def setWhereString(self, param):
    param["WhereString"] = ""
    param["HavingString"] = ""
    
    view_filters = self.dg_filters.GetTable().__dict__["data"]
    fin = 0
    for filter in view_filters:  # @ReservedAssignment
      fin = fin + 1
      if getattr(filter, "wheretype")=="where":
        if getattr(filter, "fieldtype")=="string":
          sval = getattr(filter, "fvalue")
          if (getattr(filter, "fvalue") == "" or getattr(filter, "fvalue") == None):
            sval = ""
          else:
            sval = sval + "%"
          param["paramList"].append({"name":"@filter"+str(fin), "value":sval, "wheretype":"where", "type":"string"})
          if getattr(filter, "ftype") == "==":
            param["WhereString"] = param["WhereString"] + " and lower(" + getattr(filter, "sqlstr") + ") like lower(@filter"+str(fin)+")"
            continue        
          if getattr(filter, "ftype") == "=N":
            param["WhereString"] = param["WhereString"] + " and (lower(" + getattr(filter, "sqlstr") + ") like lower(@filter"+str(fin)+") or (" + getattr(filter, "sqlstr") + " is null))"
            continue
          if getattr(filter, "ftype") == "!=":
            param["WhereString"] = param["WhereString"] + " and lower(" + getattr(filter, "sqlstr") + ") not like lower(@filter"+str(fin)+")"
            continue
        
        if getattr(filter, "fieldtype")=="date":
          param["paramList"].append({"name":"@filter"+str(fin), "value":getattr(filter, "fvalue"), "wheretype":"where", "type":"date"})
          if getattr(filter, "ftype") == "==":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " = @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == "=N":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " is null"
            continue
          if getattr(filter, "ftype") == "!=":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " <> @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == ">=":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " >= @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == "<=":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " <= @filter"+str(fin)
            continue
          
        if getattr(filter, "fieldtype")=="float":#from nwx.dataset.models import userconfig
          param["paramList"].append({"name":"@filter"+str(fin), "value":getattr(filter, "fvalue"), "wheretype":"where", "type":"number"})
          if getattr(filter, "ftype") == "==":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " = @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == "=N":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " is null"
            continue
          if getattr(filter, "ftype") == "!=":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " <> @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == ">=":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " >= @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == "<=":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " <= @filter"+str(fin)
            continue
        
        if getattr(filter, "fieldtype")=="integer":
          param["paramList"].append({"name":"@filter"+str(fin), "value":getattr(filter, "fvalue"), "wheretype":"where", "type":"number"})
          if getattr(filter, "ftype") == "==":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " = @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == "=N":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " is null"
            continue
          if getattr(filter, "ftype") == "!=":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " <> @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == ">=":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " >= @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == "<=":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " <= @filter"+str(fin)
            continue
        
        if getattr(filter, "fieldtype")=="bool":
          bval = False
          if getattr(filter, "fvalue") == "t":
            bval = True
          else:
            bval = False
          param["paramList"].append({"name":"@filter"+str(fin), "value":bval, "wheretype":"where", "type":"boolean"})
          if getattr(filter, "ftype") == "==":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr")  + " = @filter"+str(fin)
            continue        
          if getattr(filter, "ftype") == "=N":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " is null "
            continue
          if getattr(filter, "ftype") == "!=":
            param["WhereString"] = param["WhereString"] + " and " + getattr(filter, "sqlstr") + " <> @filter"+str(fin)
            continue
        
      if getattr(filter, "wheretype")=="having":
        if getattr(filter, "fieldtype")=="string":
          sval = getattr(filter, "fvalue")
          if (getattr(filter, "fvalue") == "" or getattr(filter, "fvalue") == None):
            sval = ""
          else:
            sval = sval + "%"
          param["paramList"].append({"name":"@filter"+str(fin), "value":sval, "wheretype":"where", "type":"string"})
          if getattr(filter, "ftype") == "==":
            param["HavingString"] = param["HavingString"] + " and lower(" + getattr(filter, "sqlstr") + ") like lower(@filter"+str(fin)+")"
            continue        
          if getattr(filter, "ftype") == "=N":
            param["HavingString"] = param["HavingString"] + " and (lower(" + getattr(filter, "sqlstr") + ") like lower(@filter"+str(fin)+") or (" + getattr(filter, "sqlstr") + " is null))"
            continue
          if getattr(filter, "ftype") == "!=":
            param["HavingString"] = param["HavingString"] + " and lower(" + getattr(filter, "sqlstr") + ") not like lower(@filter"+str(fin)+")"
            continue
        
        if getattr(filter, "fieldtype")=="date":
          param["paramList"].append({"name":"@filter"+str(fin), "value":getattr(filter, "fvalue"), "wheretype":"where", "type":"date"})
          if getattr(filter, "ftype") == "==":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " = @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == "=N":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " is null"
            continue
          if getattr(filter, "ftype") == "!=":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " <> @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == ">=":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " >= @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == "<=":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " <= @filter"+str(fin)
            continue
        
        if getattr(filter, "fieldtype")=="float":
          param["paramList"].append({"name":"@filter"+str(fin), "value":getattr(filter, "fvalue"), "wheretype":"where", "type":"number"})
          if getattr(filter, "ftype") == "==":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " = @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == "=N":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " is null"
            continue
          if getattr(filter, "ftype") == "!=":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " <> @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == ">=":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " >= @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == "<=":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " <= @filter"+str(fin)
            continue
        
        if getattr(filter, "fieldtype")=="integer":
          param["paramList"].append({"name":"@filter"+str(fin), "value":getattr(filter, "fvalue"), "wheretype":"where", "type":"number"})
          if getattr(filter, "ftype") == "==":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " = @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == "=N":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " is null"
            continue
          if getattr(filter, "ftype") == "!=":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " <> @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == ">=":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " >= @filter"+str(fin)
            continue
          if getattr(filter, "ftype") == "<=":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " <= @filter"+str(fin)
            continue
        
        if getattr(filter, "fieldtype")=="bool":
          bval = False
          if getattr(filter, "fvalue") == "t":
            bval = True
          else:
            bval = False
          param["paramList"].append({"name":"@filter"+str(fin), "value":bval, "wheretype":"where", "type":"boolean"})
          if getattr(filter, "ftype") == "==":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr")  + " = @filter"+str(fin)
            continue        
          if getattr(filter, "ftype") == "=N":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " is null "
            continue
          if getattr(filter, "ftype") == "!=":
            param["HavingString"] = param["HavingString"] + " and " + getattr(filter, "sqlstr") + " <> @filter"+str(fin)
            continue
    
    for cbcol in range(self.lst_filter.GetCount()):
      if self.lst_filter.IsChecked(cbcol)==True:
        param["WhereString"] = param["WhereString"] + self._lst_filter[cbcol]["sqlstr"]
        
    if self.parent.application.app_settings["transfilter"]==0:
      #no filter
      pass
    if self.parent.application.app_settings["transfilter"]==1:
      #only their department
      if self.parent.application.app_settings["department_id"]!=None:
        table = self.dataSet["viewfields"]
        index = next((i for i in xrange(len(table)) if table[i]["viewname"] == self.sectionView and table[i]["fieldtype"] == "filter" and table[i]["fieldname"] == "fl_department"), None)
        if index is not None:
          param["WhereString"] = param["WhereString"] + " and " + table[index]["sqlstr"]
          param["paramList"].append({"name":"@department_id", "value":self.parent.application.app_settings["department_id"], "wheretype":"where", "type":"integer"})
    if self.parent.application.app_settings["transfilter"]==2:
      #only their own transactions
      table = self.dataSet["viewfields"]
      index = next((i for i in xrange(len(table)) if table[i]["viewname"] == self.sectionView and table[i]["fieldtype"] == "filter" and table[i]["fieldname"] == "fl_usename"), None)
      if index is not None:
        param["WhereString"] = param["WhereString"] + " and " + table[index]["sqlstr"]
        param["paramList"].append({"name":"@usename", "value":self.parent.application.app_settings["username"], "wheretype":"where", "type":"string"})

  def clipData(self):
    try:
      if self.dg_result.GetNumberRows()==0:
        return
      wx.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
      self.parent.setStatusState(1)
      cldata = ""
      for row in range(self.dg_result.GetNumberRows()):
        clrow = ""
        for col in range(self.dg_result.GetNumberCols()):
          if clrow!="":
            clrow = clrow + "\t"
          clrow = clrow + self.dg_result.GetCellValue(row, col)
        cldata = cldata + clrow + "\n"
      if cldata != "" and wx.TheClipboard.IsOpened()==False:
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(wx.TextDataObject(cldata))
        wx.TheClipboard.Close()
    except Exception, err:
      wx.MessageBox(str(err), "clipData", wx.OK | wx.ICON_ERROR)
    finally:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
      self.parent.setStatusState(0)
  
  def exportToExcel(self):
    try:
      if self.dg_result.GetNumberRows()==0:
        return
        
      wildcard = "Excel files (*.xls)|*.xls|"     \
           "All files (*.*)|*.*"
      dlg = wx.FileDialog(
            self, message=str(self.getLocale("browser_grid_export_excel")), 
            defaultDir=(os.getenv('USERPROFILE') or os.getenv('HOME')), 
            defaultFile="NervaturaExport", wildcard=wildcard, style=wx.SAVE)
      dlg.SetFilterIndex(0)
      if dlg.ShowModal() == wx.ID_OK:
        wx.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        self.parent.setStatusState(1)
        book = xlwt.Workbook(encoding='utf-8')
        styles = {
          'header': xlwt.easyxf(
            'font: bold true, height 160;'
            'alignment: horizontal left, vertical center;'
            'pattern: back_colour gray25;'
            'borders: left thin, right thin, top thin, bottom thin;'),
          'float': xlwt.easyxf(
            'alignment: horizontal right, vertical center;'
            'borders: left thin, right thin, top thin, bottom thin;',
            num_format_str='# ### ##0.00'),
          'integer': xlwt.easyxf(
            'alignment: horizontal right, vertical center;'
            'borders: left thin, right thin, top thin, bottom thin;',
            num_format_str='# ### ##0'),
          'date': xlwt.easyxf(
            'alignment: horizontal center, vertical center;'
            'borders: left thin, right thin, top thin, bottom thin;',
            num_format_str='yyyy.mm.dd'),
          'bool': xlwt.easyxf(
            'alignment: horizontal center, vertical center;'
            'borders: left thin, right thin, top thin, bottom thin;'),
          'string': xlwt.easyxf(
            'alignment: horizontal left, vertical center;'
            'borders: left thin, right thin, top thin, bottom thin;')}
      
        sheet1 = book.add_sheet(self.lst_view.GetClientData(self.lst_view.GetSelection())["langname"])     
        for col in range(self.dg_result.GetNumberCols()):
          sheet1.write(0, col, self.dg_result.GetColLabelValue(col), styles["header"])
        
        for row in range(self.dg_result.GetNumberRows()):
          for col in range(self.dg_result.GetNumberCols()):
            if self.dg_result.GetTable().GetTypeName(row, col)==wx.grid.GRID_VALUE_FLOAT:
              sheet1.write(row+1, col, self.dg_result.GetCellValue(row, col), styles["float"])
            if self.dg_result.GetTable().GetTypeName(row, col)==wx.grid.GRID_VALUE_LONG:
              sheet1.write(row+1, col, self.dg_result.GetCellValue(row, col), styles["integer"])
            if self.dg_result.GetTable().GetTypeName(row, col)==wx.grid.GRID_VALUE_DATETIME:
              sheet1.write(row+1, col, self.dg_result.GetCellValue(row, col), styles["date"])
            if self.dg_result.GetTable().GetTypeName(row, col)==wx.grid.GRID_VALUE_BOOL:
              if self.dg_result.GetCellValue(row, col)=="1":
                sheet1.write(row+1, col, True, styles["bool"])
              else:
                sheet1.write(row+1, col, False, styles["bool"])
            if self.dg_result.GetTable().GetTypeName(row, col)==wx.grid.GRID_VALUE_STRING or self.dg_result.GetTable().GetTypeName(row, col)==wx.grid.GRID_VALUE_TEXT:
              sheet1.write(row+1, col, self.dg_result.GetCellValue(row, col), styles["string"])
                        
        book.save(dlg.GetPath()+".xls")
      dlg.Destroy()
    except Exception, err:
      wx.MessageBox(str(err), "exportToExcel", wx.OK | wx.ICON_ERROR)
    finally:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
      self.parent.setStatusState(0)
      
  def exportToCSV(self):
    try:
      if self.dg_result.GetNumberRows()==0:
        return
      wildcard = "CSV files (*.csv)|*.csv|"     \
           "All files (*.*)|*.*"
      dlg = wx.FileDialog(
            self, message=str(self.getLocale("browser_grid_export_csv")), 
            defaultDir=(os.getenv('USERPROFILE') or os.getenv('HOME')), 
            defaultFile="NervaturaExport", wildcard=wildcard, style=wx.SAVE)
      dlg.SetFilterIndex(0)
      if dlg.ShowModal() == wx.ID_OK:
        wx.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        self.parent.setStatusState(1)
        csvfile = open(dlg.GetPath()+".csv", 'w')
        for row in range(self.dg_result.GetNumberRows()):
          clrow = ""
          for col in range(self.dg_result.GetNumberCols()):
            if clrow!="":
              clrow = clrow + ";"
            clrow = clrow + self.dg_result.GetCellValue(row, col).decode('utf-8').encode(self.parent.application.app_settings["codepage"])
          csvfile.write(clrow+"\n" )
        csvfile.close()
      dlg.Destroy()
    except Exception, err:
      wx.MessageBox(str(err), "exportToCSV", wx.OK | wx.ICON_ERROR)
    finally:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
      self.parent.setStatusState(0)  
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
      self._cmd_load()
    if event.ControlDown() ==True and keycode == 51:
      #[Ctrl][3]
      self._cmd_trans()
    event.Skip()
    
  def _cmd_load(self, event=None):
    self.loadData()
      
  def _cmd_view(self, event=None):
    self.createViewMenu()
  
  def _cmd_trans(self, event=None):
    menu = self.lst_view.GetClientData(self.lst_view.GetSelection())["menu"]
    if menu!=None or menu!="":
      self.showPopMenu(menu, self.cmd_trans)
      
  def _cmd_export(self, event=None):
    self.showPopMenu("export", self.cmd_export)
  
  def _cmd_save(self, event=None):
    self.ds.saveDataSet(self.dataSet)
  
  def _cmd_total(self, event=None):
    if self.dg_total.IsShown():
      self.dg_total.Hide()
      self.ds.setConfig(self.dataSet, "browserConfig", "showTotal", False, None, None)
    else:
      self.dg_total.Show()
      self.createTotalRow()
      self.ds.setConfig(self.dataSet, "browserConfig", "showTotal", True, None, None)
    wx.CallAfter(self.Layout)
  
  def _lst_view(self, event=None):
    if self.lst_view.GetClientData(self.lst_view.GetSelection())!=None:
      self.loadSectionView(self.lst_view.GetClientData(self.lst_view.GetSelection())["viewname"])
  
  def _cmd_selcol_all(self, event=None):
    ncol = self.dg_result.GetNumberCols()
    for selcol in range(self.lst_selcol.GetCount()):
      if self.lst_selcol.IsChecked(selcol)==False:
        fieldname = self._lst_selcol[selcol]["fieldname"]
        self.ds.setConfig(self.dataSet, self.sectionView, fieldname, self.defCfvalue, ncol, self.mainView)
        self.lst_selcol.Check(selcol, True)
        ncol = ncol+1
    self.setResultData()
  
  def _cmd_selcol_none(self, event=None):
    for selcol in range(self.lst_selcol.GetCount()):
      fieldname = self._lst_selcol[selcol]["fieldname"]
      if self.lst_selcol.IsChecked(selcol):
        self.ds.setConfig(self.dataSet, self.sectionView, fieldname, None, None, self.mainView, True)
      self.lst_selcol.Check(selcol, False)
    self.setResultData()  
  
  def _cmd_filter_add(self, event=None):
    if self.cmd_filter.GetSelection()>-1:
      self.cmd_filter.GetClientData(self.cmd_filter.GetSelection())
      self.ds.addFilterRow(self.dataSet, self.cmd_filter.GetClientData(self.cmd_filter.GetSelection()), self.sectionView, self.filter_type)
      self.setFilterData()
      
  def _cmd_filter_delete(self, event=None):
    delRows = []
    for srow in self.dg_filters.GetSelectedRows():
      delRows.append(self.dg_filters.GetTable().GetRowData(srow))
      for drow in delRows:
        self.ds.deleteFilterRow(self.dataSet, drow)
    self.setFilterData()  
  
  def _dg_filters(self, event=None):
    if event.GetCol()==0:
      frow = self.dg_filters.GetTable().GetRowData(event.GetRow())
      viewfield =  self.parent.getItemFromKey2(self.dataSet["viewfields"], 
            "viewname", self.sectionView, "langname", getattr(frow, "fieldlabel").strip())
      setattr(frow, "fieldname", viewfield["fieldname"])
      setattr(frow, "fieldlabel", viewfield["langname"])
      setattr(frow, "fieldtype", viewfield["fieldtype"])
      setattr(frow, "wheretype", viewfield["wheretype"])
      setattr(frow, "sqlstr", viewfield["sqlstr"])
        
  def _lst_selcol(self, event=None):
    selcol = event.GetSelection()
    fieldname = self._lst_selcol[selcol]["fieldname"]
    if self.lst_selcol.IsChecked(selcol):
      self.ds.setConfig(self.dataSet, self.sectionView, fieldname, self.defCfvalue, self.dg_result.GetNumberCols(), self.mainView)
    else:
      ncol=0
      for col in range(self.dg_result.GetNumberCols()):
        if self.dg_result.GetTable().GetColId(col)==fieldname:
          self.ds.setConfig(self.dataSet, self.sectionView, fieldname, None, None, self.mainView, True)
        else:
          self.ds.setConfig(self.dataSet, self.sectionView, self.dg_result.GetTable().GetColId(col), self.dg_result.GetColSize(col), ncol, self.mainView)
          ncol = ncol+1
    self.setResultData()
  
  def _cb_autocol(self, event=None):
    self.ds.setConfig(self.dataSet, "browserConfig", "autoBrowserCol", event.IsChecked())
  
  def _lb_datagrid(self, event=None):
    self.showHead()
    event.StopPropagation()
  
  def _dg_result_menu(self,evt):
    self.lsrow = evt.GetRow()
    menu = self.lst_view.GetClientData(self.lst_view.GetSelection())["menu"]
    if menu!=None or menu!="":
      self.showPopMenu(menu)
      
  def _dg_result_sort(self,evt):
    id = self.dg_result.GetTable().GetColId(evt.GetCol())  # @ReservedAssignment
    if len(self.sorting)>0:
      if self.sorting.has_key(id):
        if self.sorting[id]=="asc":
          self.sorting = {id:"desc"}
          self.dataSet["result"].sort(cmp=None, key=lambda item: item[id], reverse=True)
        else:
          self.sorting = {id:"asc"}
          self.dataSet["result"].sort(cmp=None, key=lambda item: item[id], reverse=False)
      else:
        self.sorting = {id:"asc"}
        self.dataSet["result"].sort(cmp=None, key=lambda item: item[id], reverse=False)
    else:
      self.sorting = {id:"asc"}
      self.dataSet["result"].sort(cmp=None, key=lambda item: item[id], reverse=False)
    self.setResultData()
  
  def _dg_result_col_size(self,evt):
    self.ds.setConfig(self.dataSet, self.sectionView, self.dg_result.GetTable().GetColId(evt.GetRowOrCol()), self.dg_result.GetColSize(evt.GetRowOrCol()), evt.GetRowOrCol(), self.mainView)
  
  def _dg_result_col_move(self,evt):
    frm = evt.GetMoveColumn()
    to = evt.GetBeforeColumn()
    self.dg_result.GetTable().MoveColumn(frm,to)
    if self.cb_autocol.IsChecked():
      self.dg_result.AutoSizeColumns(False)
    else:
      self.setUserColSize()
    self.updateColConfig()
    
  def _dg_result_row_move(self,evt):
    frm = evt.GetMoveRow()
    to = evt.GetBeforeRow()
    self.dg_result.GetTable().MoveRow(frm,to)
    if self.cb_autocol.IsChecked():
      self.dg_result.AutoSizeColumns(False)
    else:
      self.setUserColSize()
    self.updateColConfig()
  
  def _dg_result_dbl(self,evt):
    menu = self.lst_view.GetClientData(self.lst_view.GetSelection())["menuitem"]
    if menu!=None or menu!="":
      func = getattr(self, "_"+menu, None)
      if callable(func):
        func(evt)
        
  def _closeShowWindow(self,win):
    if win.dirty == True:
      dlg = wx.MessageDialog(self, win.GetTitle()+" "+self.getLocale("alert_dirty_ms"), self.getLocale("alert_warning_lb"),
        wx.YES_NO | wx.ICON_INFORMATION | wx.NO_DEFAULT)
      ms = dlg.ShowModal()
      dlg.Destroy()
      if ms==wx.ID_YES:
        self.loadData()
  
#------------------------------------------------------------------------------------------      
#Menu events
#------------------------------------------------------------------------------------------    
  def _browser_select_view(self, event):
    self.lst_view.SetSelection(event.GetId())
    self.loadSectionView(self.lst_view.GetClientData(self.lst_view.GetSelection())["viewname"])
  
  def _browser_grid_copy(self, event):
    self.clipData()
  
  def _browser_grid_export_excel(self, event):
    self.exportToExcel()
  
  def _browser_grid_export_csv(self, event):
    self.exportToCSV()
  
  def _browser_customer_new(self, event):
    from nwx.view.fCustomer import fCustomer  # @UnresolvedImport
    child = fCustomer(self.parent, -1)
    child.fBrowser = self
    child.Show()
  
  def getSelectedRowId(self, event):
    if hasattr(event, "GetRow"):
      return event.GetRow()
    elif len(self.dg_result.GetSelectedRows())>0:
      return self.dg_result.GetSelectedRows()[0]
    elif self.lsrow!=None:
      return self.lsrow
    else:
      return None
  
  def _browser_customer_edit(self, event):
    rowid = self.getSelectedRowId(event)
    if rowid!=None:
      id = self.dg_result.GetTable().__dict__["data"][rowid]["id"]  # @ReservedAssignment
      from nwx.view.fCustomer import fCustomer  # @UnresolvedImport
      child = fCustomer(self.parent,id)
      child.fBrowser = self
      child.Show()
    else:
      wx.MessageBox("Please select an entire row!", "Nervatura WxDemo", wx.OK | wx.ICON_INFORMATION)
  
  def _browser_event_edit(self, event):
    wx.MessageBox("Edit Event...", ":-)", wx.OK | wx.ICON_INFORMATION)
  
  def _browser_event_export(self, event):
    rowid = self.getSelectedRowId(event)
    if rowid!=None:
      id = self.dg_result.GetTable().__dict__["data"][rowid]["id"]  # @ReservedAssignment
      self.parent.exportToICal(id)
    else:
      wx.MessageBox("Please select an entire row!", "Nervatura WxDemo", wx.OK | wx.ICON_INFORMATION)
            