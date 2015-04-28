# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2015, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""
import wx
import json, requests  # @UnresolvedImport

class npiAdapter():
  
  def __init__(self, host_address):
    self.host_address = host_address
  
  def initData(self, pid, method):
    return {"id":pid, "method":method, "params":{}, "jsonrpc":"2.0"}
  
  def postData(self, data):
    response = requests.post(self.host_address, 
      data=json.dumps(data), headers={'content-type': 'application/json'}).json()
    if response.has_key("error"):
      wx.MessageBox(str(response["error"]["message"])+": "+str(response["error"]["data"]), 
        "Nervatura", wx.OK | wx.ICON_ERROR)
      return "error"
    else:
      return response["result"]
  
  def getLogin (self, database, username, password):
    data = self.initData(1, "getLogin_json")
    data["params"]["database"] = database 
    data["params"]["username"] = username 
    data["params"]["password"] = password
    return self.postData(data)
  
  def loadView(self, login, sqlKey=None, sqlStr=None, whereStr="", havingStr="", 
               paramList=[], simpleList=False, orderStr=""):
    data = self.initData(2, "loadView_json")
    data["params"]["login"] = login 
    data["params"]["sqlKey"] = sqlKey 
    data["params"]["sqlStr"] = sqlStr
    data["params"]["whereStr"] = whereStr 
    data["params"]["havingStr"] = havingStr 
    data["params"]["paramList"] = paramList
    data["params"]["simpleList"] = simpleList 
    data["params"]["orderStr"] = orderStr;
    return self.postData(data)

  def loadTable(self, login, classAlias, filterStr="", orderStr=""):
    data = self.initData(3, "loadTable_json")
    data["params"]["login"] = login 
    data["params"]["classAlias"] = classAlias 
    data["params"]["filterStr"] = filterStr
    data["params"]["orderStr"] = orderStr
    return self.postData(data)

  def loadDataSet(self, login, dataSetInfo):
    data = self.initData(4, "loadDataSet_json")
    data["params"]["login"] = login 
    data["params"]["dataSetInfo"] = dataSetInfo;
    return self.postData(data)

  def executeSql(self, login, sqlKey, sqlStr, paramList=[]):
    data = self.initData(5, "executeSql_json")
    data["params"]["login"] = login 
    data["params"]["sqlKey"] = sqlKey 
    data["params"]["sqlStr"] = sqlStr
    data["params"]["paramList"] = paramList
    return self.postData(data)

  def saveRecord(self, login, record):
    data = self.initData(6, "saveRecord_json")
    data["params"]["login"] = login 
    data["params"]["record"] = record
    return self.postData(data)

  def saveRecordSet(self, login, recordSet):
    data = self.initData(7, "saveRecordSet_json")
    data["params"]["login"] = login 
    data["params"]["recordSet"] = recordSet;
    return self.postData(data)

  def saveDataSet(self, login, dataSet):
    data = self.initData(8, "saveDataSet_json")
    data["params"]["login"] = login 
    data["params"]["dataSet"] = dataSet
    return self.postData(data)

  def deleteRecord(self, login, record):
    data = self.initData(9, "deleteRecord_json")
    data["params"]["login"] = login 
    data["params"]["record"] = record;
    return self.postData(data)

  def deleteRecordSet(self, login, recordSet):
    data = self.initData(10, "deleteRecordSet_json")
    data["params"]["login"] = login 
    data["params"]["recordSet"] = recordSet
    return self.postData(data)

  def callFunction(self, login, functionName, paramList=[]):
    data = self.initData(11, "callFunction_json")
    data["params"]["login"] = login 
    data["params"]["functionName"] = functionName 
    data["params"]["paramList"] = paramList
    return self.postData(data)
    
    