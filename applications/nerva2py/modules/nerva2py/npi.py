# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

from nerva2py.tools import NervaTools

#Basic npi functions. Encoding independent

class Npi(object):
  ns = None
  tool = NervaTools(None)
    
  def __init__(self, NervaStore):
    self.ns = NervaStore
    self.tool = NervaTools(NervaStore)
  
  def getLogin(self, database, username, password):
    validator = {}
    if self.ns.db==None:
      if self.ns.local.setEngine(database)==False:
        validator["valid"] = False
        validator["message"] = str(self.ns.error_message)
        return validator
    if self.ns.connect.setLogin(username, password)==False:
      validator["valid"] = False
      if self.ns.error_message!="":
        validator["message"] = str(self.ns.error_message)
      else: 
        validator["message"] = str(self.ns.T("Invalid user: ")+username)
      return validator
    validator["valid"] = True   
    validator["message"] = "OK"
    return validator
  
  def loadView(self, login, sqlKey, sqlStr, whereStr, havingStr, paramList, simpleList=False, orderStr=""):
    if login.has_key("safe")!=True:
      validator = self.getLogin(login["database"], login["username"], login["password"])
      if validator["valid"]==False:
        raise NameError(validator["message"])
    try:
      if login.has_key("appl"):
        appl = login["appl"]
      else:
        appl = "nflex"
      sqlStr = self.ns.local.setSqlParams(sqlKey=sqlKey, sqlStr=sqlStr, whereStr=whereStr, havingStr=havingStr, 
                            paramList=paramList, rlimit=False, appl=appl)
      if simpleList==False:
        result = self.ns.db.executesql(sqlStr, as_dict=True)
      else:
        result = self.ns.db.executesql(sqlStr, as_dict=False)
    except Exception, err:
      raise RuntimeError(err)
    return result
  
  def loadTable(self, login, tableName, filterStr, orderStr):
    if login.has_key("safe")!=True:
      validator = self.getLogin(login["database"], login["username"], login["password"])
      if validator["valid"]==False:
        raise NameError(validator["message"])
    try:
      query = "select * from "+tableName
      if filterStr!="" and filterStr!=None:
        query += " where "+filterStr
      if orderStr!="" and orderStr!=None:
        query += " order by "+orderStr
      table = self.ns.db.executesql(query, as_dict=True)
    except Exception, err:
      raise RuntimeError(err)
    return table
  
  def executeSql(self, login, sqlKey, sqlStr, paramList):
    if login.has_key("safe")!=True:
      validator = self.getLogin(login["database"], login["username"], login["password"])
      if validator["valid"]==False:
        raise NameError(validator["message"])
    try:
      if login.has_key("appl"):
        appl = login["appl"]
      else:
        appl = "nflex"
      sqlStr = self.ns.local.setSqlParams(sqlKey=sqlKey, sqlStr=sqlStr, whereStr="", havingStr="", 
                            paramList=paramList, rlimit=False, appl=appl)
      self.ns.db.executesql(sqlStr)
    except Exception, err:
      #self.ns.db.rollback()
      raise RuntimeError(err)
    #self.ns.db.commit()
    return True
  
  def loadDataSet(self, login, dataSetInfo):
    validator = self.getLogin(login["database"], login["username"], login["password"])
    if validator["valid"]==False:
      raise NameError(validator["message"])
    login["safe"] = True
    dataSet=[]
    try:
      for recordSetInfo in dataSetInfo:
        if (recordSetInfo["infoType"] == "table"):
          tableName = recordSetInfo["classAlias"].replace("models.","") if recordSetInfo.has_key("classAlias") else recordSetInfo["tableName"]
          recordSet = self.loadTable(login, tableName, recordSetInfo["filterStr"], recordSetInfo["orderStr"])
        if (recordSetInfo["infoType"] == "view"):
          recordSet = self.loadView(login, recordSetInfo["sqlKey"], recordSetInfo["sqlStr"], recordSetInfo["whereStr"], 
                                    recordSetInfo["havingStr"], recordSetInfo["paramList"], False, "")
        if (recordSetInfo["infoType"] == "execute"):
          self.executeSql(login, recordSetInfo["sqlKey"], recordSetInfo["sqlStr"], recordSetInfo["paramList"])
        if (recordSetInfo["infoType"] == "function"):
          func = getattr(self.tool, recordSetInfo["functionName"], None)
          params = {}
          if callable(func):
            if (type(recordSetInfo["paramList"]) is list):
              for param in recordSetInfo["paramList"]:
                if str(param["value"]).startswith("select"):
                  recordSet = self.loadView(login, None, str(param["value"]), "", "", recordSetInfo["paramList"], False, "")
                  if recordSet!=None:
                    param["value"] = recordSet[0]["value"]
                params[param["name"]] = param["value"]
            else:
              params = recordSetInfo["paramList"]
            recordSet = func(params)
        infoSet = {}
        infoSet["infoName"] = recordSetInfo["infoName"]
        infoSet["recordSet"] = recordSet
        dataSet.append(infoSet)
    except Exception, err:
      raise RuntimeError(err)
    return dataSet

  def saveRecord(self, login, record, validate=False):
    def clearValues(tablename, values):
      table = getattr(self.ns.db, tablename)
      for key in values.keys():
        if values[key]==None or hasattr(table, key)==False:
          del values[key]
      return values
    if login.has_key("safe")!=True:
      validator = self.getLogin(login["database"], login["username"], login["password"])
      if validator["valid"]==False:
        raise NameError(validator["message"])
    if type(record) is dict:
      tablename = record["__tablename__"]
      values = clearValues(tablename, record)
    else:
      tablename = record.__tablename__
      values = clearValues(tablename, record.__dict__)
    row_id = self.ns.connect.updateData(tablename, values=values, validate=validate, insert_row=True)
    if not row_id:
      raise NameError(str(self.ns.error_message))
    elif type(record) is dict:
      record["id"] = row_id
    else:
      record.id = row_id
    return record
  
  def saveRecordSet(self, login, recordSet, validate=False):
    validator = self.getLogin(login["database"], login["username"], login["password"])
    if validator["valid"]==False:
      raise NameError(validator["message"])
    login["safe"] = True
    try:
      for record in recordSet:
        record = self.saveRecord(login, record, validate)
    except Exception, err:
      self.ns.db.rollback()
      raise RuntimeError(err)
    self.ns.db.commit()
    return recordSet
  
  def saveDataSet(self, login, dataSet, validate=False):
    validator = self.getLogin(login["database"], login["username"], login["password"])
    if validator["valid"]==False:
      raise NameError(validator["message"])
    login["safe"] = True
    try:
      for updateSetInfo in dataSet:
        if (updateSetInfo["updateType"] == "update"):
          for record in updateSetInfo["recordSet"]:
            record = self.saveRecord(login, record, validate)
        if (updateSetInfo["updateType"] == "delete"):
          for record in updateSetInfo["recordSet"]:
            self.deleteRecord(login, record)
        if (updateSetInfo["updateType"] == "function"):
          func = getattr(self.tool, updateSetInfo["functionName"], None)
          if callable(func):
            updateSetInfo["value"] = func(updateSetInfo["paramList"])
    except Exception, err:
      self.ns.db.rollback()
      raise RuntimeError(err)
    self.ns.db.commit()
    return dataSet
  
  def deleteRecord(self, login, record):
    if login.has_key("safe")!=True:
      validator = self.getLogin(login["database"], login["username"], login["password"])
      if validator["valid"]==False:
        raise NameError(validator["message"])
    if type(record) is dict:
      if not self.ns.connect.deleteData(nervatype=record["__tablename__"], ref_id=record["id"]):
        raise NameError(str(self.ns.error_message))
    else:
      if not self.ns.connect.deleteData(nervatype=record.__tablename__, ref_id=record.id):
        raise NameError(str(self.ns.error_message))
    return True
  
  def deleteRecordSet(self, login, recordSet):
    validator = self.getLogin(login["database"], login["username"], login["password"])
    if validator["valid"]==False:
      raise NameError(validator["message"])
    login["safe"] = True
    try:
      for record in recordSet:
        self.deleteRecord(login, record)
    except Exception, err:
      self.ns.db.rollback()
      raise RuntimeError(err)
    self.ns.db.commit()
    return True
  
  def callFunction(self, login, functionName, paramList):
    if login.has_key("safe")!=True:
      validator = self.getLogin(login["database"], login["username"], login["password"])
      if validator["valid"]==False:
        raise NameError(validator["message"])
    func = getattr(self.tool, functionName, None)
    if callable(func):
      try:
        retval = func(paramList)
      except Exception, err:
        raise RuntimeError(err)
      if type(retval) is not list:
        retval = [retval]
      return retval