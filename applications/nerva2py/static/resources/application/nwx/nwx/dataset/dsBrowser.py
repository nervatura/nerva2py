# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Project
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import wx
from datetime import date
from pyamf.remoting.client import RemotingService  # @UnresolvedImport
from nwx.dataset.models import filter, userconfig  # @UnresolvedImport

class dsBrowser():
  
  def __init__(self, parentView):
    self.parentView = parentView    
  
  def initDataSet(self):
    dataSet = {}
    
    dataSet["userconfig"] = []
    dataSet["_userconfig"] = []
    dataSet["filter"] = []
    dataSet["_filter"] = []
      
    dataSet["applviews"] = []
    dataSet["viewfields"] = []
    dataSet["result"] = []
    
    dataSet["mainView"] = ""
    dataSet["changeData"] = False
    dataSet["filterId"] = 0

    return dataSet
      
  def loadDataset(self, dataSet):
    dataSetInfo = []
    paramList = []
    
    paramList.append({"name":"@parent", "value": dataSet["mainView"], "wheretype":"in", "type":"string"})
    paramList.append({"name":"@lang", "value":str(self.parentView.application.app_settings["locale"][:2]).lower(), 
      "wheretype":"in", "type":"string"})
    dataSetInfo.append({"infoName":"applviews", "infoType":"view", "sqlKey":"fBrowser_getApplViews",
                          "sqlStr":None, "whereStr":"", "havingStr":"", "paramList":paramList})    
    
    paramList = []
    paramList.append({"name":"@parent", "value": dataSet["mainView"], "wheretype":"in", "type":"string"})
    paramList.append({"name":"@lang", "value":str(self.parentView.application.app_settings["locale"][:2]).lower(), 
      "wheretype":"in", "type":"string"})
    dataSetInfo.append({"infoName":"viewfields", "infoType":"view", "sqlKey":"fBrowser_getViewFields",
                          "sqlStr":None, "whereStr":"", "havingStr":"", "paramList":paramList})
    
    paramList = []
    dataSetInfo.append({"infoName":"userconfig", "infoType":"table", "classAlias":"models.ui_userconfig", 
                        "filterStr":"employee_id="+str(self.parentView.application.app_settings["employee_id"])+" and (cfgroup='browserConfig' or section='"+dataSet["mainView"]+"') ", 
                        "orderStr":None})            
    dataSetInfo.append({"infoName":"filter", "infoType":"table", "classAlias":"models.ui_filter", 
                        "filterStr":"employee_id="+str(self.parentView.application.app_settings["employee_id"])+" and parentview='"+dataSet["mainView"]+"' ", 
                        "orderStr":None})
            
    client = RemotingService(self.parentView.application.app_settings["url"]+"/"+self.parentView.application.app_config["connection"]["npi_service"])
    service = client.getService("default")
    
    resultSet = service.loadDataSet_amf(self.parentView.getCredentials(), dataSetInfo)  
    if resultSet.__class__.__name__!="ArrayCollection":
      wx.MessageBox(str(resultSet), "loadDataset", wx.OK | wx.ICON_ERROR)
      return
    for recordSetInfo in resultSet:
      if recordSetInfo.infoName=="applviews":
        dataSet["applviews"] = recordSetInfo.recordSet
        continue
      elif recordSetInfo.infoName=="viewfields":
        dataSet["viewfields"] = recordSetInfo.recordSet
        continue
      elif recordSetInfo.infoName=="userconfig":
        dataSet["userconfig"] = recordSetInfo.recordSet
        continue
      elif recordSetInfo.infoName=="filter":
        dataSet["filter"] = recordSetInfo.recordSet
        for item in dataSet["filter"]:
          viewfield =  self.parentView.getItemFromKey2(dataSet["viewfields"], 
            "viewname", item.viewname, "fieldname", item.fieldname)
          item.fieldlabel = viewfield["langname"]
          item.fieldtype = viewfield["fieldtype"]
          item.wheretype = viewfield["wheretype"]
          item.sqlstr = viewfield["sqlstr"]
        dataSet["filterId"] = len(dataSet["filter"])
        continue
    dataSet["changeData"] = False
  
  def loadResult(self, dataSet, sqlstr, param):
    try:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
      self.parentView.setStatusState(1)
      client = RemotingService(self.parentView.application.app_settings["url"]+"/"+self.parentView.application.app_config["connection"]["npi_service"])
      service = client.getService("default")
      
      resultSet = service.loadView_amf(self.parentView.getCredentials(), None, 
        sqlstr, param["WhereString"], param["HavingString"], param["paramList"])  
      if resultSet.__class__.__name__!="ArrayCollection":
        wx.MessageBox(str(resultSet), "loadResult", wx.OK | wx.ICON_ERROR)
        return
      dataSet["result"] = resultSet
        
    except Exception, err:
      wx.MessageBox(str(err), "loadResult", wx.OK | wx.ICON_ERROR)
    finally:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
      self.parentView.setStatusState(0)
  
  def saveDataSet(self, dataSet):
    try:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
      self.parentView.setStatusState(2)
      client = RemotingService(self.parentView.application.app_settings["url"]+"/"+self.parentView.application.app_config["connection"]["npi_service"])
      service = client.getService("default")
        
      dataSetPy = []
      dataSetPy.append({"tableName":"userconfig", "updateType":"delete", "recordSet":dataSet["_userconfig"]})
      dataSetPy.append({"tableName":"filter", "updateType":"delete", "recordSet":dataSet["_filter"]})
      dataSetPy.append({"tableName":"userconfig", "updateType":"update", "recordSet":dataSet["userconfig"]})
      dataSetPy.append({"tableName":"filter", "updateType":"update", "recordSet":dataSet["filter"]})
      
      resultSet = service.saveDataSet_amf(self.parentView.getCredentials(), dataSetPy)  
      if resultSet.__class__.__name__!="list":
        wx.MessageBox(str(resultSet), "saveDataSet", wx.OK | wx.ICON_ERROR)
        return
      for recordSetInfo in resultSet:
        for srow in recordSetInfo.recordSet:
          if getattr(srow, "oid", None):
            item = self.parentView.getItemFromKey_(dataSet[recordSetInfo.tableName], "id", srow.oid)
            if item:
              item.id = srow.id
          
      dataSet["_userconfig"] = []
      dataSet["_filter"] = []
      dataSet["changeData"] = False
        
    except Exception, err:
      wx.MessageBox(str(err), "saveDataSet", wx.OK | wx.ICON_ERROR)
    finally:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
      self.parentView.setStatusState(0)

  def addFilterRow(self, dataSet, ftype, sectionView, filter_type):
      frow = filter()
      dataSet["filterId"] = dataSet["filterId"] + 1
      frow.id = -dataSet["filterId"]
      frow.employee_id = self.parentView.application.app_settings["employee_id"]
      frow.parentview = dataSet["mainView"]
      frow.viewname = sectionView
      frow.ftype = "=="
      fname = ""
      if ftype=="browser_filter_text":
        frow.fvalue = ""
        fname = filter_type["stringField"][0]
      elif ftype=="browser_filter_number":
        frow.fvalue = "0"
        fname = filter_type["numberField"][0]
      elif ftype=="browser_filter_date":
        frow.fvalue = date.strftime(date.today(),"%Y-%m-%d")
        fname = filter_type["dateField"][0]
      elif ftype=="browser_filter_boolean":
        frow.fvalue = "t"
        fname = filter_type["boolField"][0]
      viewfield =  self.parentView.getItemFromKey2(dataSet["viewfields"], 
              "viewname", sectionView, "fieldname", fname)
      frow.fieldname = fname
      frow.fieldlabel = viewfield["langname"]
      frow.fieldtype = viewfield["fieldtype"]
      frow.wheretype = viewfield["wheretype"]
      frow.sqlstr = viewfield["sqlstr"]
        
      dataSet["filter"].append(frow)
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
    config = userconfig()
    config.employee_id = self.parentView.application.app_settings["employee_id"] 
    config.section = isection 
    config.cfgroup = icfgroup 
    config.cfname = icfname 
    config.cfvalue = ivalue 
    config.orderby = iorderby
    dataSet["userconfig"].append(config)   
        