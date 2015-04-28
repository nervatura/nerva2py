# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2015, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import wx, sqlite3, time, json
from nwx.utils.adapter import npiAdapter  # @UnresolvedImport
from datetime import date
from nwx.view.fMain import dict2obj  # @UnresolvedImport

class dsBrowser():
  
  def __init__(self, parentView):
    self.parentView = parentView    
  
  def initDataSet(self):
    dataSet = {}
    
    dataSet["userconfig"] = []
    dataSet["_userconfig"] = []
      
    dataSet["applviews"] = []
    dataSet["viewfields"] = []
    dataSet["result"] = []
    
    dataSet["mainView"] = ""
    dataSet["changeData"] = False
    dataSet["filterId"] = 0

    return dataSet
      
  def loadDataset(self, dataSet):
    
    conn = sqlite3.connect('storage.db')  # @UndefinedVariable
    conn.row_factory = sqlite3.Row  # @UndefinedVariable
    
    cur = conn.cursor()
    sqlStr = self.parentView.getSql("fBrowser_getApplViews")
    for row in cur.execute(sqlStr, (dataSet["mainView"],)):
      item = {}; fields = row.keys()
      for index in range(len(fields)):
        item[fields[index]] = row[index]
      dataSet["applviews"].append(dict2obj(item))
    
    sqlStr = self.parentView.getSql("fBrowser_getViewFields")
    for row in cur.execute(sqlStr, (dataSet["mainView"],)):
      item = {}; fields = row.keys()
      for index in range(len(fields)):
        item[fields[index]] = row[index]
      dataSet["viewfields"].append(dict2obj(item))
    
    dataSet["userconfig"] = []
    conn.close()
    
    dataSetInfo = [{"infoName":"userconfig", "infoType":"table", "classAlias":"ui_userconfig", 
       "filterStr":"employee_id="+str(self.parentView.application.app_settings["employee_id"])+
       " and (cfgroup='browserConfig' or section='"+dataSet["mainView"]+"') ", 
       "orderStr":None}]
    
    conn = npiAdapter(self.parentView.application.app_settings["url"]+"/"+
      self.parentView.application.app_config["connection"]["npi_service"])
    response = conn.loadDataSet(self.parentView.getCredentials(), dataSetInfo)
    if response=="error":
      return
    else:
      for recordSetInfo in response:
        for record in recordSetInfo["recordSet"]:
          dataSet[recordSetInfo["infoName"]].append(dict2obj(record,"ui_"+recordSetInfo["infoName"]))

    dataSet["changeData"] = False
  
  def loadResult(self, dataSet, sqlstr, param):
    try:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
      self.parentView.setStatusState(1)
      
      conn = npiAdapter(self.parentView.application.app_settings["url"]+"/"+
        self.parentView.application.app_config["connection"]["npi_service"])
      response = conn.loadView(self.parentView.getCredentials(), None, sqlstr, param["WhereString"], 
        param["HavingString"], param["paramList"])
      if response=="error":
        return
      else:
        dataSet["result"] = response
        
    except Exception, err:
      wx.MessageBox(str(err), "loadResult", wx.OK | wx.ICON_ERROR)
    finally:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
      self.parentView.setStatusState(0)
  
  def saveDataSet(self, dataSet):
    try:      
      wx.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
      self.parentView.setStatusState(2)
        
      dataSetPy = []
      dataSetPy.append({"tableName":"ui_userconfig", "updateType":"delete", "recordSet":dataSet["_userconfig"]})
      dataSetPy.append({"tableName":"ui_userconfig", "updateType":"update", "recordSet":dataSet["userconfig"]})
      
      conn = npiAdapter(self.parentView.application.app_settings["url"]+"/"+
        self.parentView.application.app_config["connection"]["npi_service"])
      response = conn.saveDataSet(self.parentView.getCredentials(), dataSetPy)
      if response=="error":
        return
      else:
        dataSet["_userconfig"] = []
        dataSet["changeData"] = False
        self.loadDataset(dataSet)
        
    except Exception, err:
      wx.MessageBox(str(err), "saveDataSet", wx.OK | wx.ICON_ERROR)
    finally:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
      self.parentView.setStatusState(0)

  def addFilterRow(self, dataSet, ftype, sectionView, filter_type):
      frow = {"ftype":"=="}
      fname = ""
      if ftype=="browser_filter_text":
        frow["fvalue"] = ""
        fname = filter_type["stringField"][0]
      elif ftype=="browser_filter_number":
        frow["fvalue"] = "0"
        fname = filter_type["numberField"][0]
      elif ftype=="browser_filter_date":
        frow["fvalue"] = date.strftime(date.today(),"%Y-%m-%d")
        fname = filter_type["dateField"][0]
      elif ftype=="browser_filter_boolean":
        frow["fvalue"] = "t"
        fname = filter_type["boolField"][0]
      viewfield =  self.parentView.getItemFromKey2(dataSet["viewfields"], 
        "viewname", sectionView, "fieldname", fname)
      frow["fieldname"] = fname
      frow["fieldlabel"] = viewfield["langname"]
      frow["fieldtype"] = viewfield["fieldtype"]
      frow["wheretype"] = viewfield["wheretype"]
      frow["sqlstr"] = viewfield["sqlstr"]
      
      self.setConfig(dataSet, sectionView, "filter_"+str(time.time()), json.dumps(frow), None, dataSet["mainView"])
      dataSet["changeData"] = True
   
  def deleteFilterRow(self, dataSet, item):
      if item.id > 0:
        dataSet["_filter"].append(item)  
      dataSet["filter"].remove(item);
      dataSet["changeData"] = True
  
  def getConfig(self, dataSet, cfgroup, cfname, section=None):
    retVal = []
    for config in dataSet["userconfig"]:
      if ((section == None or section == config.section) and 
        (cfgroup == None or cfgroup == config.cfgroup) and 
        (cfname == None or cfname == config.cfname)):
        retVal.append(config) 
    return retVal
  
  def setConfig(self, dataSet, icfgroup, icfname, ivalue, iorderby=None, isection=None, deleteRow=False):
    for config in dataSet["userconfig"]:
      if config.section==isection and config.cfgroup==icfgroup and config.cfname==icfname:
        if deleteRow==False:
          config.cfvalue = ivalue
          config.orderby = iorderby
        else:
          dataSet["userconfig"].remove(config)
          dataSet["_userconfig"].append(config)
        return
    config = dict2obj({},"ui_userconfig")
    config.employee_id = self.parentView.application.app_settings["employee_id"] 
    config.section = isection 
    config.cfgroup = icfgroup 
    config.cfname = icfname 
    config.cfvalue = ivalue 
    config.orderby = iorderby
    dataSet["userconfig"].append(config)   
        