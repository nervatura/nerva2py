# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2015, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import wx
from nwx.utils.adapter import npiAdapter  # @UnresolvedImport
from nwx.view.fMain import dict2obj  # @UnresolvedImport
from datetime import date

class dsCustomer():
  
  def __init__(self, parentView):
    self.parentView = parentView
  
  def initDataSet(self, _iniId=-1):
    dataSet = {}
    
    customerRow = dict2obj({"id":None, "custtype":None, "custnumber":None, "custname":None, 
      "taxnumber":None,"account":None, "notax":0, "terms":0, "creditlimit":0, "discount":0, 
      "notes":None, "inactive":0, "deleted":0}, "customer")
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
    
    dataSetInfo.append({"infoName":"groups", "infoType":"table", "classAlias":"groups", 
                        "filterStr":"deleted=0 and groupname in ('customer', 'nervatype', 'fieldtype', 'logstate', 'custtype')", 
                        "orderStr":"groupname, groupvalue"})
    dataSetInfo.append({"infoName":"deffield", "infoType":"table", "classAlias":"deffield", 
                        "filterStr":"deleted=0 and nervatype = (select id from groups where groupname = 'nervatype' and groupvalue = 'customer')", 
                        "orderStr":"description"})
    dataSetInfo.append({"infoName":"fieldValues", "infoType":"table", "classAlias":"fieldvalue", 
                        "filterStr":"fieldname in('not_logical_delete', 'log_customer_update', 'log_customer_deleted', 'default_customer_report')", 
                        "orderStr":None})
    
    if dataSet["customer"][0].id!=-1:
      dataSetInfo.append({"infoName":"customer", "infoType":"table", "classAlias":"customer", 
                        "filterStr":"id="+str(dataSet["customer"][0].id), "orderStr":None})
      dataSetInfo.append({"infoName":"link", "infoType":"table", "classAlias":"link", 
                        "filterStr":"deleted=0 and nervatype_1 = (select id from groups where groupname = 'nervatype' and groupvalue = 'customer') " +
                        "and nervatype_2 = (select id from groups where groupname = 'nervatype' and groupvalue = 'groups') " +
                        "and ref_id_1="+str(dataSet["customer"][0].id), "orderStr":None})
      dataSetInfo.append({"infoName":"address", "infoType":"table", "classAlias":"address", 
                        "filterStr":"deleted = 0 and nervatype = (select id from groups where groupname = 'nervatype' and groupvalue = 'customer') " +
                        "and ref_id ="+str(dataSet["customer"][0].id), "orderStr":"id"})
      dataSetInfo.append({"infoName":"contact", "infoType":"table", "classAlias":"contact", 
                        "filterStr":"deleted = 0 and nervatype = (select id from groups where groupname = 'nervatype' and groupvalue = 'customer') " +
                        "and ref_id ="+str(dataSet["customer"][0].id), "orderStr":"id"})
      paramList = []
      paramList.append({"name":"@customer_id", "value":dataSet["customer"][0].id, "wheretype":"in", "type":"integer"})
      sqlStr = self.parentView.getSql("fCustomer_getDeffieldProp")
      dataSetInfo.append({"infoName":"deffield_prop", "infoType":"view", "sqlKey":None,
                          "sqlStr":sqlStr, "whereStr":"", "havingStr":"", "paramList":paramList})
      dataSetInfo.append({"infoName":"fieldvalue", "infoType":"table", "classAlias":"fieldvalue", 
                        "filterStr":"deleted = 0 and fieldname in (select fieldname from deffield where nervatype = " +
                        "(select id from groups where groupname = 'nervatype' and groupvalue = 'customer')) " +
                        "and ref_id="+str(dataSet["customer"][0].id), "orderStr":None})
      paramList = []
      paramList.append({"name":"@customer_id", "value":dataSet["customer"][0].id, "wheretype":"in", "type":"integer"})
      sqlStr = self.parentView.getSql("fCustomer_getCalendarView")
      dataSetInfo.append({"infoName":"calendar_view", "infoType":"view", "sqlKey":None,
                          "sqlStr":sqlStr, "whereStr":"", "havingStr":"", "paramList":paramList})
    else:
      dataSetInfo.append({"infoName":"custnumber", "infoType":"function", "functionName":"nextNumber",
                          "paramList":{"numberkey":"custnumber", "step":False}})
    
    conn = npiAdapter(self.parentView.application.app_settings["url"]+"/"+
      self.parentView.application.app_config["connection"]["npi_service"])
    response = conn.loadDataSet(self.parentView.getCredentials(), dataSetInfo)
    if response=="error":
      return
    else:
      resultSet = response
    
    for recordSetInfo in resultSet:
      if recordSetInfo["infoName"]=="groups":
        dataSet["groups"] = self.parentView.dic2objList(recordSetInfo["recordSet"],recordSetInfo["infoName"])
        if dataSet["customer"][0].id==-1:
          dataSet["customer"][0].custtype =  self.parentView.getItemFromKey2(dataSet["groups"], "groupname", "custtype", "groupvalue", "company").id
        continue
        
      if recordSetInfo["infoName"]=="fieldValues":
        for inivalue in recordSetInfo["recordSet"]:
          if inivalue["fieldname"]=="default_customer_report":
            pass
          elif inivalue["fieldname"]=="not_logical_delete":
            if inivalue["value"]=="true":
              dataSet["deletedFlag"] = True
          elif inivalue["fieldname"]=="log_customer_update":
            pass
        continue
      
      if recordSetInfo["infoName"]=="deffield":
        dataSet["deffield"] = self.parentView.dic2objList(recordSetInfo["recordSet"],recordSetInfo["infoName"])
        continue
      
      if recordSetInfo["infoName"]=="deffield_prop":
        dataSet["deffield_prop"] = self.parentView.dic2objList(recordSetInfo["recordSet"],recordSetInfo["infoName"])
      
      if recordSetInfo["infoName"]=="custnumber":
        dataSet["newCustnumber"] = recordSetInfo["recordSet"]
        dataSet["customer"][0].custnumber = dataSet["newCustnumber"]
        continue
      
      if recordSetInfo["infoName"]=="calendar_view":
        dataSet["calendar_view"] = self.parentView.dic2objList(recordSetInfo["recordSet"],recordSetInfo["infoName"])
        continue
        
      if recordSetInfo["infoName"]=="link":
        dataSet["link"] = self.parentView.dic2objList(recordSetInfo["recordSet"],recordSetInfo["infoName"])
        for item in recordSetInfo["recordSet"]:
          group = self.parentView.getItemFromKey(dataSet["groups"], "id", item.ref_id_2)
          if group:
            item.description = group.groupvalue
          else:
            item.description = "???"
        dataSet["linkId"]=len(dataSet["link"])
        continue

      elif recordSetInfo["infoName"]=="fieldvalue":
        dataSet["fieldvalue"] = self.parentView.dic2objList(recordSetInfo["recordSet"],recordSetInfo["infoName"])
        for item in dataSet["fieldvalue"]:
          item.fieldtype = self.parentView.getItemFromKey(dataSet["groups"], "id", self.parentView.getItemFromKey(dataSet["deffield"], "fieldname", item.fieldname).fieldtype).groupvalue
          item.description = self.parentView.getItemFromKey(dataSet["deffield"], "fieldname", item.fieldname).description
          item.visible = bool(self.parentView.getItemFromKey(dataSet["deffield"], "fieldname", item.fieldname).visible)
          item.readonly = bool(self.parentView.getItemFromKey(dataSet["deffield"], "fieldname", item.fieldname).visible)
          if item.fieldtype=="valuelist":
            item.valuelist = self.parentView.getItemFromKey(dataSet["deffield"], "fieldname", item.fieldname).valuelist
          if item.fieldtype in("customer","tool","trans","transitem","transmovement","transpayment","product","project","employee","place"):
            item.valuelist = self.parentView.getItemFromKey(dataSet["deffield_prop"], "id", item.fieldtype+"_"+item.value)["description"]
        dataSet["fieldvalueId"] = len(dataSet["fieldvalue"])
        continue
      
      elif recordSetInfo["infoName"]=="address":
        dataSet["address"] = self.parentView.dic2objList(recordSetInfo["recordSet"],recordSetInfo["infoName"])
        dataSet["addressId"] = len(dataSet["address"])
        continue

      elif recordSetInfo["infoName"]=="contact":
        dataSet["contact"] = self.parentView.dic2objList(recordSetInfo["recordSet"],recordSetInfo["infoName"])
        dataSet["contactId"] = len(dataSet["contact"])
        continue
      
      elif recordSetInfo["infoName"]=="customer":
        dataSet["customer"] = self.parentView.dic2objList(recordSetInfo["recordSet"],recordSetInfo["infoName"])
        continue  
    dataSet["changeData"] = False
  
  def reloadData(self, dataSet):
    dataSetInfo = []
    dataSetInfo.append({"infoName":"groups", "infoType":"table", "classAlias":"models.groups", 
                        "filterStr":"deleted=0 and groupname in ('customer', 'nervatype', 'fieldtype', 'logstate', 'custtype')", 
                        "orderStr":"groupname, groupvalue"})
    paramList = []
    paramList.append({"name":"@customer_id", "value":dataSet["customer"][0].id, "wheretype":"in", "type":"integer"})
    sqlStr = self.parentView.getSql("fCustomer_getCalendarView")
    dataSetInfo.append({"infoName":"calendar_view", "infoType":"view", "sqlKey":None,
                          "sqlStr":sqlStr, "whereStr":"", "havingStr":"", "paramList":paramList})
    
    conn = npiAdapter(self.parentView.application.app_settings["url"]+"/"+
      self.parentView.application.app_config["connection"]["npi_service"])
    response = conn.loadDataSet(self.parentView.getCredentials(), dataSetInfo)
    if response=="error":
      return
    else:
      resultSet = response
      
    if resultSet.__class__.__name__!="list": 
      wx.MessageBox(str(resultSet), "loadDataset", wx.OK | wx.ICON_ERROR)
      return
    for recordSetInfo in resultSet:
      if recordSetInfo["infoName"]=="groups":
        dataSet["groups"] = self.parentView.dic2objList(recordSetInfo["recordSet"],recordSetInfo["infoName"])
        continue
      elif recordSetInfo["infoName"]=="calendar_view":
        dataSet["calendar_view"] = self.parentView.dic2objList(recordSetInfo["recordSet"],recordSetInfo["infoName"])
        continue
  
  def saveDataSet(self, dataSet, parent):
    try:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
      self.parentView.setStatusState(2)
      
      if dataSet["customer"][0].custnumber!=dataSet["newCustnumber"]:
        #check customer no. to make unique
        filter = "custnumber='"+dataSet["customer"][0].custnumber+"'"  # @ReservedAssignment
        if dataSet["customer"][0].id>-1:
          filter += " and id <> " + str(dataSet["customer"][0].id)
        
        conn = npiAdapter(self.parentView.application.app_settings["url"]+"/"+
          self.parentView.application.app_config["connection"]["npi_service"])
        response = conn.loadTable(self.parentView.getCredentials(), "customer", filter)
        if response=="error":
          return
        elif len(response)>0:
          wx.MessageBox(parent.getLocale("alert_err_iscustnumber"), parent.getLocale("alert_warning_lb"), 
                        wx.OK | wx.ICON_ERROR )
          return
      else:
        #recall and step new customer no.
        conn = npiAdapter(self.parentView.application.app_settings["url"]+"/"+
          self.parentView.application.app_config["connection"]["npi_service"])
        response = conn.callFunction(self.parentView.getCredentials(), 
          "nextNumber", {"numberkey":"custnumber", "step":True})
        if response=="error":
          return
        else:
          if len(response)>0:
            dataSet["customer"][0].custnumber = response[0]
          else:
            wx.MessageBox("Error", "loadDataset", wx.OK | wx.ICON_ERROR)
            return
          
      #save head data
      conn = npiAdapter(self.parentView.application.app_settings["url"]+"/"+
        self.parentView.application.app_config["connection"]["npi_service"])
      response = conn.saveRecord(self.parentView.getCredentials(), dataSet["customer"][0])
      if response=="error":
        return

      if dataSet["customer"][0].id==-1:
        #new customer, replace the temp id
        dataSet["customer"][0].id = response["id"]
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
      conn = npiAdapter(self.parentView.application.app_settings["url"]+"/"+
        self.parentView.application.app_config["connection"]["npi_service"])
      response = conn.saveDataSet(self.parentView.getCredentials(), dataSetInfo)
      if response=="error":
        return
      else:
        dataSet["_link"] = []
        dataSet["_address"] = []
        dataSet["_contact"] = []
        dataSet["_fieldvalue"] = []
        dataSet["changeData"] = False
        self.loadDataset(dataSet)
                      
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
      conn = npiAdapter(self.parentView.application.app_settings["url"]+"/"+
        self.parentView.application.app_config["connection"]["npi_service"])
      
      paramList = []
      paramList.append({"name":"@customer_id", "value":dataSet["customer"][0].id, "wheretype":"in", "type":"integer"})
      sqlStr = self.parentView.getSql("fCustomer_getDeleteState")
      response = conn.loadView(self.parentView.getCredentials(), None, sqlStr, "", "", paramList)
      if response=="error":
        return
      elif response[0]["sco"]>0:
        wx.MessageBox(parent.getLocale("alert_delete_err"), parent.getLocale("alert_warning_lb"), wx.OK | wx.ICON_ERROR)
        return
      paramList = []
      paramList.append({"name":"@customer_id", "value":dataSet["customer"][0].id, "wheretype":"in", "type":"integer"})
      if dataSet["deletedFlag"]==True:
        sqlStr = self.parentView.getSql("fCustomer_getDeleteSql_delete")
      else:
        sqlStr = self.parentView.getSql("fCustomer_getDeleteSql_update")
      response = conn.executeSql(self.parentView.getCredentials(), None, sqlStr, paramList)
      if response=="error":
        delOK = False
      else:
        delOK = True    
    except Exception, err:
      wx.MessageBox(str(err), "deleteDataSet", wx.OK | wx.ICON_ERROR)
    finally:
      wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
      self.parentView.setStatusState(0)
      return delOK
      
  def addAddressRow(self, dataSet):
    addr = dict2obj({"id":None, "nervatype":None, "ref_id":None, "country":None, "state":None,
      "zipcode":None, "city":None, "street":None, "notes":None, "deleted":0},"address")
    dataSet["addressId"] = dataSet["addressId"] + 1
    addr.id = -dataSet["addressId"]
    addr.nervatype = self.parentView.getItemFromKey2(dataSet["groups"], "groupname", "nervatype", "groupvalue", "customer").id
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
    cont = dict2obj({"id":None, "nervatype":None, "ref_id":None, "firstname":None, "surname":None,
      "status":None, "phone":None, "fax":None, "mobil":None, "email":None, "notes":None, 
      "deleted":0},"contact")
    dataSet["contactId"] = dataSet["contactId"] + 1
    cont.id = -dataSet["contactId"]
    cont.nervatype = self.parentView.getItemFromKey2(dataSet["groups"], "groupname", "nervatype", "groupvalue", "customer").id
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
    
    fieldtype = self.parentView.getItemFromKey(dataSet["groups"], "id", self.parentView.getItemFromKey(dataSet["deffield"], "fieldname", df.fieldname).fieldtype).groupvalue
    if fieldtype in("urlink","notes","customer","tool","trans","transitem","transmovement","transpayment","product","project","employee","place"):
      wx.MessageBox("Sorry, but this fieldtype ("+fieldtype+") is not handled...", ":-(", wx.OK | wx.ICON_ERROR)
      return
    
    cf = dict2obj({"id":None, "fieldname":None, "ref_id":None, "value":None, 
                   "notes":None, "deleted":0},"fieldvalue")
    dataSet["fieldvalueId"] = dataSet["fieldvalueId"] + 1
    cf.id = -dataSet["fieldvalueId"]
    cf.fieldname = df.fieldname
    cf.ref_id = dataSet["customer"][0].id
    
    cf.fieldtype = self.parentView.getItemFromKey(dataSet["groups"], "id", self.parentView.getItemFromKey(dataSet["deffield"], "fieldname", df.fieldname).fieldtype).groupvalue
    cf.description = self.parentView.getItemFromKey(dataSet["deffield"], "fieldname", df.fieldname).description
    cf.visible = bool(self.parentView.getItemFromKey(dataSet["deffield"], "fieldname", df.fieldname).visible)
    cf.readonly = bool(self.parentView.getItemFromKey(dataSet["deffield"], "fieldname", df.fieldname).visible)
    if cf.fieldtype=="bool":
      cf.value = "f"
    elif cf.fieldtype=="date":
      cf.value = date.strftime(date.today(),"%Y-%m-%d")
    elif cf.fieldtype in("integer", "float"):
      cf.value = "0"
    elif cf.fieldtype=="urlink":
      cf.value = urlink
    elif cf.fieldtype=="valuelist":
      cf.valuelist = self.parentView.getItemFromKey(dataSet["deffield"], "fieldname", df.fieldname).valuelist
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
    cg = dict2obj({"id":None, "nervatype_1":None, "ref_id_1":None, "nervatype_2":None, 
      "ref_id_2":None, "linktype":0, "deleted":0},"link")
    dataSet["linkId"] = dataSet["linkId"] + 1
    cg.id = -dataSet["linkId"]
    cg.nervatype_1 = self.parentView.getItemFromKey2(dataSet["groups"], "groupname", "nervatype", "groupvalue", "customer").id
    cg.ref_id_1 = dataSet["customer"][0].id
    cg.nervatype_2 = self.parentView.getItemFromKey2(dataSet["groups"], "groupname", "nervatype", "groupvalue", "groups").id
    cg.ref_id_2 = groups_id
    cg.description = self.parentView.getItemFromKey(dataSet["groups"], "id", groups_id).groupvalue
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
    