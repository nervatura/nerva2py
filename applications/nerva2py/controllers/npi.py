# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

if 0:
  from gluon.globals import Session
  global session; session = Session()
  global request; request = globals.Request()
  import gluon.languages.translator as T
  from gluon.sql import DAL
  global db; db = DAL()
  global response; response = globals.Response()

import pyamf
from pyamf.flex import ArrayCollection 
from gluon.tools import Service

from nerva2py.nervastore import NervaStore
from nerva2py.tools import NervaTools
from nerva2py.npi import Npi
import nerva2py.models

if request.env.http_origin:
  response.headers['Access-Control-Allow-Origin'] = request.env.http_origin
else:
  response.headers['Access-Control-Allow-Origin'] = "*"
response.headers['Access-Control-Allow-Credentials'] = 'true'
response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
response.headers['Access-Control-Max-Age'] = 86400

if request.env.request_method == 'OPTIONS':
  if request.env.http_access_control_request_method:
    response.headers['Access-Control-Allow-Methods'] = request.env.http_access_control_request_method
    if request.env.http_access_control_request_headers:
      response.headers['Access-Control-Allow-Headers'] = request.env.http_access_control_request_headers
                
ns = NervaStore(request, session, T, db)
npi = Npi(ns)
tool = NervaTools(ns)

service = Service()
        
def call():
  session.forget()
  return service()

def getVernum():
  return response.verNo

@service.jsonrpc
@service.jsonrpc2
def getLogin_json(database, username, password):
  validator = npi.getLogin(database, username, password)
  if validator["valid"]==True:
    validator["employee"] = ns.employee.as_dict(datetime_to_str=False)
    validator["audit"] = ns.db(ns.db.ui_audit.usergroup==ns.employee.usergroup).select()
    validator["groupinput"] = ns.db(ns.db.ui_groupinput.groups_id==ns.employee.usergroup).select()
    transfilter = ns.db((ns.db.link.ref_id_1==ns.employee.usergroup)&(ns.db.link.deleted==0)
                        &(ns.db.link.nervatype_2==ns.db((ns.db.groups.groupname=="nervatype")
                        &(ns.db.groups.groupvalue=="groups")).select()[0].id)).select()
    if len(transfilter)>0:
      validator["transfilter"] = transfilter[0].ref_id_2
    else:
      validator["transfilter"] = None
    validator["groups"] = ns.db(ns.db.groups.groupname.belongs(('usergroup', 'nervatype', 'transtype', 'inputfilter', 'transfilter', 'department', 'logstate', 'fieldtype'))).select()
    validator["menucmd"] = ns.db().select(ns.db.ui_menu.ALL)
    validator["menufields"] = ns.db().select(ns.db.ui_menufields.ALL, orderby=ns.db.ui_menufields.menu_id|ns.db.ui_menufields.orderby)
    userlogin = ns.db(ns.db.fieldvalue.fieldname=="log_userlogin").select()
    if len(userlogin)>0:
      validator["userlogin"] = userlogin[0].value
    else:
      validator["userlogin"] = "false"
  return validator

@service.amfrpc3("default")
def getLogin_amf(database, username, password, validdata=False):
  validator = npi.getLogin(database, username, password)
  pyamf.register_package(nerva2py.models, 'models')
  if validator["valid"]==True:
    validator["employee"] = ns.employee.as_dict(datetime_to_str=False)
    validator["audit"] = ArrayCollection(ns.db(ns.db.ui_audit.usergroup==ns.employee.usergroup).select().as_list(datetime_to_str=False))
    validator["groupinput"] = ArrayCollection(ns.db(ns.db.ui_groupinput.groups_id==ns.employee.usergroup).select().as_list(datetime_to_str=False))
    transfilter = ns.db((ns.db.link.ref_id_1==ns.employee.usergroup)
                        &(ns.db.link.nervatype_2==ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select()[0].id)
                        &(ns.db.link.ref_id_2.belongs(ns.db(ns.db.groups.groupname=="nervatype")._select(ns.db.groups.id)))).select()
    if len(transfilter)>0:
      validator["transfilter"] = transfilter[0].ref_id_2
    else:
      validator["transfilter"] = None
    validator["groups"] = ArrayCollection(ns.db(ns.db.groups.groupname.belongs(('usergroup', 'nervatype', 'transtype', 'inputfilter', 'transfilter', 'department', 'logstate', 'fieldtype'))).select().as_list(datetime_to_str=False))
    validator["menucmd"] = ArrayCollection(ns.db().select(ns.db.ui_menu.ALL).as_list(datetime_to_str=False))
    validator["menufields"] = ArrayCollection(ns.db().select(ns.db.ui_menufields.ALL, orderby=ns.db.ui_menufields.menu_id|ns.db.ui_menufields.orderby).as_list(datetime_to_str=False))
    userlogin = ns.db(ns.db.fieldvalue.fieldname=="log_userlogin").select()
    if len(userlogin)>0:
      validator["userlogin"] = userlogin[0].value
    else:
      validator["userlogin"] = "false"
  return validator

@service.jsonrpc
@service.jsonrpc2
def loadView_json(login, sqlKey, sqlStr, whereStr, havingStr, paramList, simpleList=False, orderStr=""):
  return npi.loadView(login, sqlKey, sqlStr, whereStr, havingStr, paramList, simpleList, orderStr)

@service.amfrpc3("default")
def loadView_amf(login, sqlKey, sqlStr, whereStr, havingStr, paramList, simpleList=False, orderStr=""):
  return ArrayCollection(npi.loadView(login, sqlKey, sqlStr, whereStr, havingStr, paramList, simpleList, orderStr))

@service.jsonrpc
@service.jsonrpc2
def loadTable_json(login, classAlias, filterStr, orderStr):
  return npi.loadTable(login, classAlias, filterStr, orderStr)

@service.amfrpc3("default")
def loadTable_amf(login, classAlias, filterStr, orderStr):
  table = npi.loadTable(login, classAlias.replace("models.",""), filterStr, orderStr)
  tl = []
  for row in table:
    trow = pyamf.load_class(classAlias).createInstance()
    trow.__dict__ = row
    tl.append(trow)
  return ArrayCollection(tl)

@service.jsonrpc
@service.jsonrpc2  
def loadDataSet_json(login, dataSetInfo):
  validator = getLogin_json(login["database"], login["username"], login["password"])
  if validator["valid"]==False:
    raise NameError(validator["message"])
  login["safe"] = True
  dataSet=[]
  try:
    for recordSetInfo in dataSetInfo:
      if (recordSetInfo["infoType"] == "table"): 
        recordSet = loadTable_json(login, recordSetInfo["classAlias"], recordSetInfo["filterStr"], recordSetInfo["orderStr"])
      if (recordSetInfo["infoType"] == "view"):
        recordSet = loadView_json(login, recordSetInfo["sqlKey"], recordSetInfo["sqlStr"], recordSetInfo["whereStr"], 
                                  recordSetInfo["havingStr"], recordSetInfo["paramList"], False, "")
      if (recordSetInfo["infoType"] == "execute"):
        executeSql_json(login, recordSetInfo["sqlKey"], recordSetInfo["sqlStr"], recordSetInfo["paramList"])
      if (recordSetInfo["infoType"] == "function"):
        func = getattr(tool, recordSetInfo["functionName"], None)
        params = {}
        if callable(func):
          if (type(recordSetInfo["paramList"]) is list):
            for param in recordSetInfo["paramList"]:
              if str(param["value"]).startswith("select"):
                recordSet = loadView_json(login, None, str(param["value"]), "", "", recordSetInfo["paramList"], False, "")
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

@service.amfrpc3("default")  
def loadDataSet_amf(login, dataSetInfo):
  validator = getLogin_amf(login["database"], login["username"], login["password"])
  if validator["valid"]==False:
    raise NameError(validator["message"])
  login["safe"] = True
  dataSet=[]
  try:
    for recordSetInfo in dataSetInfo:
      if (recordSetInfo["infoType"] == "table"): 
        recordSet = loadTable_amf(login, recordSetInfo["classAlias"], recordSetInfo["filterStr"], recordSetInfo["orderStr"])
      if (recordSetInfo["infoType"] == "view"):
        recordSet = loadView_amf(login, recordSetInfo["sqlKey"], recordSetInfo["sqlStr"], recordSetInfo["whereStr"], 
                                  recordSetInfo["havingStr"], recordSetInfo["paramList"], False, "")
      if (recordSetInfo["infoType"] == "execute"):
        executeSql_amf(login, recordSetInfo["sqlKey"], recordSetInfo["sqlStr"], recordSetInfo["paramList"])
      if (recordSetInfo["infoType"] == "function"):
        func = getattr(tool, recordSetInfo["functionName"], None)
        params = {}
        if callable(func):
          if (type(recordSetInfo["paramList"]) is list) or (type(recordSetInfo["paramList"]) is ArrayCollection):
            for param in recordSetInfo["paramList"]:
              if str(param["value"]).startswith("select"):
                recordSet = loadView_amf(login, None, str(param["value"]), "", "", recordSetInfo["paramList"], False, "")
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
  return ArrayCollection(dataSet)

@service.jsonrpc
@service.jsonrpc2
def executeSql_json(login, sqlKey, sqlStr, paramList):
  return npi.executeSql(login, sqlKey, sqlStr, paramList)

@service.amfrpc3("default")
def executeSql_amf(login, sqlKey, sqlStr, paramList):
  return npi.executeSql(login, sqlKey, sqlStr, paramList)

@service.jsonrpc
@service.jsonrpc2
def saveRecord_json(login, record, validate=False):
  return npi.saveRecord(login, record, validate)

@service.amfrpc3("default")
def saveRecord_amf(login, record, validate=False):
  return npi.saveRecord(login, record, validate)

@service.jsonrpc
@service.jsonrpc2
def saveRecordSet_json(login, recordSet, validate=False):
  return npi.saveRecordSet(login, recordSet, validate)

@service.amfrpc3("default")
def saveRecordSet_amf(login, recordSet, validate=False):
  return npi.saveRecordSet(login, recordSet, validate)

@service.jsonrpc
@service.jsonrpc2
def saveDataSet_json(login, dataSet, validate=False):
  return npi.saveDataSet(login, dataSet, validate)

@service.amfrpc3("default")
def saveDataSet_amf(login, dataSet, validate=False):
  return npi.saveDataSet(login, dataSet, validate)

@service.jsonrpc
@service.jsonrpc2
def deleteRecord_json(login, record):
  return npi.deleteRecord(login, record)

@service.amfrpc3("default")
def deleteRecord_amf(login, record):
  return npi.deleteRecord(login, record)

@service.jsonrpc
@service.jsonrpc2
def deleteRecordSet_json(login, recordSet):
  return npi.deleteRecordSet(login, recordSet)

@service.amfrpc3("default")
def deleteRecordSet_amf(login, recordSet):
  return npi.deleteRecordSet(login, recordSet)

@service.jsonrpc
@service.jsonrpc2
def callFunction_json(login, functionName, paramList):
  return npi.callFunction(login, functionName, paramList)

@service.amfrpc3("default")
def callFunction_amf(login, functionName, paramList):
  return ArrayCollection(npi.callFunction(login, functionName, paramList))
