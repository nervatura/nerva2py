# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import wx
from pyamf.remoting.client import RemotingService  # @UnresolvedImport
from nwx.dataset.models import customer, link, fieldvalue, address, contact  # @UnresolvedImport
from datetime import date

class dsCustomer():
  
  def __init__(self, parentView):
    self.parentView = parentView
  
  def initDataSet(self, _iniId=-1):
    dataSet = {}
    
    customerRow = customer()
    customerRow.id = _iniId
    dataSet["customer"] = []
    dataSet["customer"].append(customerRow)
    
    dataSet["groups"] = []
    dataSet["deffield"] = []
    dataSet["deffield_prop"] = []
    dataSet["link"] = []
    dataSet["_link"] = []
    dataSet["fieldvalue"] = []
    dataSet["_fieldvalue"] = []
    dataSet["address"] = []
    dataSet["_address"] = []
    dataSet["contact"] = []
    dataSet["_contact"] = []
    dataSet["calendar_view"] = []
    
    dataSet["changeData"] = False
    dataSet["fieldvalueId"] = 0
    dataSet["addressId"] = 0
    dataSet["contactId"] = 0
    dataSet["linkId"] = 0
    dataSet["deletedFlag"] = False
    dataSet["newCustnumber"] = ""
    
    return dataSet
      
  def loadDataset(self, dataSet):
    dataSetInfo = []
    
    dataSetInfo.append({"infoName":"groups", "infoType":"table", "classAlias":"models.groups", 
                        "filterStr":"deleted=0 and groupname in ('customer', 'nervatype', 'fieldtype', 'logstate', 'custtype')", 
                        "orderStr":"groupname, groupvalue"})
    dataSetInfo.append({"infoName":"deffield", "infoType":"table", "classAlias":"models.deffield", 
                        "filterStr":"deleted=0 and nervatype = (select id from groups where groupname = 'nervatype' and groupvalue = 'customer')", 
                        "orderStr":"description"})
    dataSetInfo.append({"infoName":"fieldValues", "infoType":"table", "classAlias":"models.fieldvalue", 
                        "filterStr":"fieldname in('not_logical_delete', 'log_customer_update', 'log_customer_deleted', 'default_customer_report')", 
                        "orderStr":None})
    
    if dataSet["customer"][0].id!=-1:
      dataSetInfo.append({"infoName":"customer", "infoType":"table", "classAlias":"models.customer", 
                        "filterStr":"id="+str(dataSet["customer"][0].id), "orderStr":None})
      dataSetInfo.append({"infoName":"link", "infoType":"table", "classAlias":"models.link", 
                        "filterStr":"deleted=0 and nervatype_1 = (select id from groups where groupname = 'nervatype' and groupvalue = 'customer') " +
                        "and nervatype_2 = (select id from groups where groupname = 'nervatype' and groupvalue = 'groups') " +
                        "and ref_id_1="+str(dataSet["customer"][0].id), "orderStr":None})
      dataSetInfo.append({"infoName":"address", "infoType":"table", "classAlias":"models.address", 
                        "filterStr":"deleted = 0 and nervatype = (select id from groups where groupname = 'nervatype' and groupvalue = 'customer') " +
                        "and ref_id ="+str(dataSet["customer"][0].id), "orderStr":"id"})
      dataSetInfo.append({"infoName":"contact", "infoType":"table", "classAlias":"models.contact", 
                        "filterStr":"deleted = 0 and nervatype = (select id from groups where groupname = 'nervatype' and groupvalue = 'customer') " +
                        "and ref_id ="+str(dataSet["customer"][0].id), "orderStr":"id"})
      paramList = []
      paramList.append({"name":"@customer_id", "value":dataSet["customer"][0].id, "wheretype":"in", "type":"integer"})
      dataSetInfo.append({"infoName":"deffield_prop", "infoType":"view", "sqlKey":"fCustomer_getDeffieldProp",
                          "sqlStr":None, "whereStr":"", "havingStr":"", "paramList":paramList})
      dataSetInfo.append({"infoName":"fieldvalue", "infoType":"table", "classAlias":"models.fieldvalue", 
                        "filterStr":"deleted = 0 and fieldname in (select fieldname from deffield where nervatype = " +
                        "(select id from groups where groupname = 'nervatype' and groupvalue = 'customer')) " +
                        "and ref_id="+str(dataSet["customer"][0].id), "orderStr":None})
      paramList = []
      paramList.append({"name":"@customer_id", "value":dataSet["customer"][0].id, "wheretype":"in", "type":"integer"})
      dataSetInfo.append({"infoName":"calendar_view", "infoType":"view", "sqlKey":"fCustomer_getCalendarView",
                          "sqlStr":None, "whereStr":"", "havingStr":"", "paramList":paramList})
    else:
      dataSetInfo.append({"infoName":"custnumber", "infoType":"function", "functionName":"nextNumber",
                          "paramList":{"id":"customer_number", "step":False}})
    
    client = RemotingService(self.parentView.application.app_settings["url"]+"/"+self.parentView.application.app_config["connection"]["npi_service"])
    service = client.getService("default")
    
    resultSet = service.loadDataSet_amf(self.parentView.getCredentials(), dataSetInfo)
    if resultSet.__class__.__name__!="ArrayCollection": 
      wx.MessageBox(str(resultSet), "loadDataset", wx.OK | wx.ICON_ERROR)
      return
    for recordSetInfo in resultSet:
      if recordSetInfo.infoName=="groups":
        dataSet["groups"] = recordSetInfo.recordSet
        if dataSet["customer"][0].id==-1:
          dataSet["customer"][0].custtype =  self.parentView.getItemFromKey2_(dataSet["groups"], "groupname", "custtype", "groupvalue", "company").id
        continue
        
      if recordSetInfo.infoName=="fieldValues":
        for inivalue in recordSetInfo.recordSet:
          if inivalue.fieldname=="default_customer_report":
            pass
          elif inivalue.fieldname=="not_logical_delete":
            if inivalue.value=="true":
              dataSet["deletedFlag"] = True
          elif inivalue.fieldname=="log_customer_update":
            pass
        continue
      
      if recordSetInfo.infoName=="deffield":
        dataSet["deffield"] = recordSetInfo.recordSet
        continue
      
      if recordSetInfo.infoName=="deffield_prop":
        dataSet["deffield_prop"] = recordSetInfo.recordSet
      
      if recordSetInfo.infoName=="custnumber":
        dataSet["newCustnumber"] = recordSetInfo.recordSet
        dataSet["customer"][0].custnumber = dataSet["newCustnumber"]
        continue
      
      if recordSetInfo.infoName=="calendar_view":
        dataSet["calendar_view"] = recordSetInfo.recordSet
        continue
        
      if recordSetInfo.infoName=="link":
        dataSet["link"] = recordSetInfo.recordSet
        for item in recordSetInfo.recordSet:
          group = self.parentView.getItemFromKey_(dataSet["groups"], "id", item.ref_id_2)
          if group:
            item.description = group.groupvalue
          else:
            item.description = "???"
        dataSet["linkId"]=len(dataSet["link"])
        continue

      elif recordSetInfo.infoName=="fieldvalue":
        dataSet["fieldvalue"] = recordSetInfo.recordSet
        for item in dataSet["fieldvalue"]:
          item.fieldtype = self.parentView.getItemFromKey_(dataSet["groups"], "id", self.parentView.getItemFromKey_(dataSet["deffield"], "fieldname", item.fieldname).fieldtype).groupvalue
          item.description = self.parentView.getItemFromKey_(dataSet["deffield"], "fieldname", item.fieldname).description
          item.visible = bool(self.parentView.getItemFromKey_(dataSet["deffield"], "fieldname", item.fieldname).visible)
          item.readonly = bool(self.parentView.getItemFromKey_(dataSet["deffield"], "fieldname", item.fieldname).visible)
          if item.fieldtype=="valuelist":
            item.valuelist = self.parentView.getItemFromKey_(dataSet["deffield"], "fieldname", item.fieldname).valuelist
          if item.fieldtype in("customer","tool","trans","transitem","transmovement","transpayment","product","project","employee","place"):
            item.valuelist = self.parentView.getItemFromKey(dataSet["deffield_prop"], "id", item.fieldtype+"_"+item.value)["description"]
        dataSet["fieldvalueId"] = len(dataSet["fieldvalue"])
        continue
      
      elif recordSetInfo.infoName=="address":
        dataSet["address"] = recordSetInfo.recordSet
        dataSet["addressId"] = len(dataSet["address"])
        continue

      elif recordSetInfo.infoName=="contact":
        dataSet["contact"] = recordSetInfo.recordSet
        dataSet["contactId"] = len(dataSet["contact"])
        continue
      
      elif recordSetInfo.infoName=="customer":
        dataSet["customer"] = recordSetInfo.recordSet
        continue  
    dataSet["changeData"] = False
  
  def reloadData(self, dataSet):
    dataSetInfo = []
    dataSetInfo.append({"infoName":"groups", "infoType":"table", "classAlias":"models.groups", 
                        "filterStr":"deleted=0 and groupname in ('customer', 'nervatype', 'fieldtype', 'logstate', 'custtype')", 
                        "orderStr":"groupname, groupvalue"})
    paramList = []
    paramList.append({"name":"@customer_id", "value":dataSet["customer"][0].id, "wheretype":"in", "type":"integer"})
    dataSetInfo.append({"infoName":"calendar_view", "infoType":"view", "sqlKey":"fCustomer_getCalendarView",
                          "sqlStr":None, "whereStr":"", "havingStr":"", "paramList":paramList})
    
    client = RemotingService(self.parentView.application.app_settings["url"]+"/"+self.parentView.application.app_config["connection"]["npi_service"])
    service = client.getService("default")
    
    resultSet = service.loadDataSet_amf(self.parentView.getCredentials(), dataSetInfo)
    if resultSet.__class__.__name__!="list": 
      wx.MessageBox(str(resultSet), "loadDataset", wx.OK | wx.ICON_ERROR)
      return
    for recordSetInfo in resultSet:
      if recordSetInfo.infoName=="groups":
        dataSet["groups"] = recordSetInfo.recordSet
        continue
      elif recordSetInfo.infoName=="calendar_view":
        dataSet["calendar_view"] = recordSetInfo.recordSet
        continue
  
  def saveDataSet(self, dataSet, parent):
    try:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
      self.parentView.setStatusState(2)
      
      client = RemotingService(self.parentView.application.app_settings["url"]+"/"+self.parentView.application.app_config["connection"]["npi_service"])
      service = client.getService("default")
      
      if dataSet["customer"][0].custnumber!=dataSet["newCustnumber"]:
        #check customer no. to make unique
        filter = "custnumber='"+dataSet["customer"][0].custnumber+"'"  # @ReservedAssignment
        if dataSet["customer"][0].id>-1:
          filter += " and id <> " + str(dataSet["customer"][0].id)
        
        resultSet = service.loadTable_amf(self.parentView.getCredentials(), "models.customer", filter, None)
        if resultSet.__class__.__name__!="ArrayCollection": 
          wx.MessageBox(str(resultSet), "saveDataSet", wx.OK | wx.ICON_ERROR)
          return
        elif len(resultSet)>0:
          wx.MessageBox(parent.getLocale("alert_err_iscustnumber"), parent.getLocale("alert_warning_lb"), wx.OK | wx.ICON_ERROR )
          return
      else:
        #recall and step new customer no.
        resultSet = service.callFunction_amf(self.parentView.getCredentials(), "nextNumber", {"id":"customer_number", "step":True})
        if resultSet.__class__.__name__!="ArrayCollection": 
          wx.MessageBox(str(resultSet), "loadDataset", wx.OK | wx.ICON_ERROR)
          return
        else:
          if len(resultSet)>0:
            dataSet["customer"][0].custnumber = resultSet[0]
          else:
            wx.MessageBox("Error", "loadDataset", wx.OK | wx.ICON_ERROR)
            return
          
      #save head data
      resultSet = service.saveRecord_amf(self.parentView.getCredentials(), dataSet["customer"][0])
      if resultSet.__class__.__name__!="customer": 
        wx.MessageBox(str(resultSet), "saveDataSet", wx.OK | wx.ICON_ERROR)
        return
      if getattr(resultSet, "oid", None):
        #new customer, replace the temp id
        dataSet["customer"][0].id = resultSet.id
        for item in dataSet["address"]:
          item.ref_id = dataSet["customer"][0].id
        for item in dataSet["contact"]:
          item.ref_id = dataSet["customer"][0].id
        for item in dataSet["fieldvalue"]:
          item.ref_id = dataSet["customer"][0].id
        for item in dataSet["link"]:
          item.ref_id_1 = dataSet["customer"][0].id
          
      dataSetInfo = []
      dataSetInfo.append({"tableName":"link", "updateType":"delete", "recordSet":dataSet["_link"]})
      dataSetInfo.append({"tableName":"address", "updateType":"delete", "recordSet":dataSet["_address"]})
      dataSetInfo.append({"tableName":"contact", "updateType":"delete", "recordSet":dataSet["_contact"]})
      dataSetInfo.append({"tableName":"fieldvalue", "updateType":"delete", "recordSet":dataSet["_fieldvalue"]})
          
      dataSetInfo.append({"tableName":"link", "updateType":"update", "recordSet":dataSet["link"]})
      dataSetInfo.append({"tableName":"address", "updateType":"update", "recordSet":dataSet["address"]})
      dataSetInfo.append({"tableName":"contact", "updateType":"update", "recordSet":dataSet["contact"]})
      dataSetInfo.append({"tableName":"fieldvalue", "updateType":"update", "recordSet":dataSet["fieldvalue"]})
      
      #save rows
      resultSet = service.saveDataSet_amf(self.parentView.getCredentials(), dataSetInfo)
      if resultSet.__class__.__name__!="list":
        wx.MessageBox(str(resultSet), "saveDataSet", wx.OK | wx.ICON_ERROR)
        return
      for recordSetInfo in resultSet:
        for srow in recordSetInfo.recordSet:
          if getattr(srow, "oid", None):
            #new row, replace the temp id
            item = self.parentView.getItemFromKey_(dataSet[recordSetInfo.tableName], "id", srow.oid)
            if item:
              item.id = srow.id
      
      dataSet["_link"] = []
      dataSet["_address"] = []
      dataSet["_contact"] = []
      dataSet["_fieldvalue"] = []
      dataSet["changeData"] = False
                      
    except Exception, err:
      wx.MessageBox(str(err), "saveDataSet", wx.OK | wx.ICON_ERROR)
    finally:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
      self.parentView.setStatusState(0)
                
  def deleteDataSet(self, dataSet, parent):
    delOK = False
    try:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
      self.parentView.setStatusState(2)
      client = RemotingService(self.parentView.application.app_settings["url"]+"/"+self.parentView.application.app_config["connection"]["npi_service"])
      service = client.getService("default")
      
      paramList = []
      paramList.append({"name":"@customer_id", "value":dataSet["customer"][0].id, "wheretype":"in", "type":"integer"})
      resultSet = service.loadView_amf(self.parentView.getCredentials(), "fCustomer_getDeleteState", None, "", "", paramList)
      if str(resultSet).startswith("Error"):
        wx.MessageBox(str(resultSet), "deleteDataSet", wx.OK | wx.ICON_ERROR)
        return
      if resultSet[0]["sco"]>0:
        wx.MessageBox(parent.getLocale("alert_delete_err"), parent.getLocale("alert_warning_lb"), wx.OK | wx.ICON_ERROR)
        return
      paramList = []
      paramList.append({"name":"@customer_id", "value":dataSet["customer"][0].id, "wheretype":"in", "type":"integer"})
      if dataSet["deletedFlag"]==True:
        resultSet = service.executeSql_amf(self.parentView.getCredentials(),  "fCustomer_getDeleteSql_delete", None, paramList)
      else:
        resultSet = service.executeSql_amf(self.parentView.getCredentials(),  "fCustomer_getDeleteSql_update", None, paramList)
      if str(resultSet).startswith("Error"):
        wx.MessageBox(str(resultSet), "deleteDataSet", wx.OK | wx.ICON_ERROR)
        return
      delOK = True    
    except Exception, err:
      wx.MessageBox(str(err), "deleteDataSet", wx.OK | wx.ICON_ERROR)
    finally:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
      self.parentView.setStatusState(0)
      return delOK
      
  def addAddressRow(self, dataSet):
    addr = address()
    dataSet["addressId"] = dataSet["addressId"] + 1
    addr.id = -dataSet["addressId"]
    addr.nervatype = self.parentView.getItemFromKey2_(dataSet["groups"], "groupname", "nervatype", "groupvalue", "customer").id
    addr.ref_id = dataSet["customer"][0].id
    dataSet["address"].append(addr)
    dataSet["changeData"] = True
  
  def deleteAddressRow(self, dataSet, item):
    if item.id > 0:
      if dataSet["deletedFlag"]==True:
        dataSet["_address"].append(item)
        dataSet["address"].remove(item)
      else:
        item.deleted=1
    else:
      dataSet["address"].remove(item)
    dataSet["changeData"] = True
          
  def addContactRow(self, dataSet):
    cont = contact()
    dataSet["contactId"] = dataSet["contactId"] + 1
    cont.id = -dataSet["contactId"]
    cont.nervatype = self.parentView.getItemFromKey2_(dataSet["groups"], "groupname", "nervatype", "groupvalue", "customer").id
    cont.ref_id = dataSet["customer"][0].id
    dataSet["contact"].append(cont)
    dataSet["changeData"] = True
  
  def deleteContactRow(self, dataSet, item):
    if item.id > 0:
      if dataSet["deletedFlag"]==True:
        dataSet["_contact"].append(item)
        dataSet["contact"].remove(item)
      else:
        item.deleted=1
    else:
      dataSet["contact"].remove(item)
    dataSet["changeData"] = True
      
  def addFieldRow(self, dataSet, df, urlink = "", ct_id = 0, ct_desc = ""):
    
    fieldtype = self.parentView.getItemFromKey_(dataSet["groups"], "id", self.parentView.getItemFromKey_(dataSet["deffield"], "fieldname", df.fieldname).fieldtype).groupvalue
    if fieldtype in("urlink","notes","customer","tool","trans","transitem","transmovement","transpayment","product","project","employee","place"):
      wx.MessageBox("Sorry, but this fieldtype ("+fieldtype+") is not handled...", ":-(", wx.OK | wx.ICON_ERROR)
      return
    
    cf = fieldvalue()
    dataSet["fieldvalueId"] = dataSet["fieldvalueId"] + 1
    cf.id = -dataSet["fieldvalueId"]
    cf.fieldname = df.fieldname
    cf.ref_id = dataSet["customer"][0].id
    
    cf.fieldtype = self.parentView.getItemFromKey_(dataSet["groups"], "id", self.parentView.getItemFromKey_(dataSet["deffield"], "fieldname", df.fieldname).fieldtype).groupvalue
    cf.description = self.parentView.getItemFromKey_(dataSet["deffield"], "fieldname", df.fieldname).description
    cf.visible = bool(self.parentView.getItemFromKey_(dataSet["deffield"], "fieldname", df.fieldname).visible)
    cf.readonly = bool(self.parentView.getItemFromKey_(dataSet["deffield"], "fieldname", df.fieldname).visible)
    if cf.fieldtype=="bool":
      cf.value = "f"
    elif cf.fieldtype=="date":
      cf.value = date.strftime(date.today(),"%Y-%m-%d")
    elif cf.fieldtype in("integer", "float"):
      cf.value = "0"
    elif cf.fieldtype=="urlink":
      cf.value = urlink
    elif cf.fieldtype=="valuelist":
      cf.valuelist = self.parentView.getItemFromKey_(dataSet["deffield"], "fieldname", df.fieldname).valuelist
    elif cf.fieldtype in("customer","tool","trans","transitem","transmovement","transpayment","product","project","employee","place"):
      cf.value = str(ct_id)
      cf.valuelist = ct_desc       
    dataSet["fieldvalue"].append(cf)
    dataSet["changeData"] = True

  def deleteFieldRow(self, dataSet, item):
    if item.id > 0:
      if dataSet["deletedFlag"]==True:
        dataSet["_fieldvalue"].append(item)
        dataSet["fieldvalue"].remove(item)
      else:
        item.deleted=1
    else:
      dataSet["fieldvalue"].remove(item)
    dataSet["changeData"] = True
   
  def addCustomerGroups(self, dataSet, groups_id):
    for item in dataSet["link"]:
      if item.ref_id_2 == groups_id:
        return
    cg = link()
    dataSet["linkId"] = dataSet["linkId"] + 1
    cg.id = -dataSet["linkId"]
    cg.nervatype_1 = self.parentView.getItemFromKey2_(dataSet["groups"], "groupname", "nervatype", "groupvalue", "customer").id
    cg.ref_id_1 = dataSet["customer"][0].id
    cg.nervatype_2 = self.parentView.getItemFromKey2_(dataSet["groups"], "groupname", "nervatype", "groupvalue", "groups").id
    cg.ref_id_2 = groups_id
    cg.description = self.parentView.getItemFromKey_(dataSet["groups"], "id", groups_id).groupvalue
    dataSet["link"].append(cg)
    dataSet["changeData"] = True
  
  def deleteCustomerGroups(self, dataSet, item):
    if item.id > 0:
      if dataSet["deletedFlag"]==True:
        dataSet["_link"].append(item)
        dataSet["link"].remove(item)
      else:
        item.deleted=1
    else:
      dataSet["link"].remove(item)
    dataSet["changeData"] = True
    