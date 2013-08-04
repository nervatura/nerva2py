# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Project
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import os

def setEngine(ns, database, check_ndi=False, created=False):
  arows = ns.lstore(ns.lstore.databases.alias == database).select()
  if len(arows)==0:  
    ns.error_message = ns.T("Unknown database name!")
    return False
  if arows[0].request_enabled_lst==None or arows[0].request_enabled_lst=="":
    pass
  else:
    if str(arows[0].request_enabled_lst).find(ns.request.client)==-1:
      ns.error_message = ns.T("Invalid client IP address!")
      return False
  if check_ndi==True:
    if arows[0].ndi_enabled==False:
      ns.error_message = ns.T("Disabled interface connection!")
      return False
    else:
      ns.md5_password = arows[0].ndi_md5_password
      ns.encrypt_data = arows[0].ndi_encrypt_data
      ns.encrypt_password = arows[0].ndi_encrypt_password
  erow = ns.lstore(ns.lstore.engine.id == arows[0].engine_id).select()[0]
  conStr = erow.connection
  ns.engine = erow.ename
  if str(arows[0].host).startswith("$"):
    if os.environ.has_key(str(arows[0].host)[1:]):
      arows[0].host = os.environ[str(arows[0].host)[1:]]
  if str(arows[0].port).startswith("$"):
    if os.environ.has_key(str(arows[0].port)[1:]):
      arows[0].port = os.environ[str(arows[0].port)[1:]]
  if erow.ename in("sqlite"):
    conStr = conStr.replace("database", arows[0].dbname)
  elif erow.ename=="google_sql":
    pass
  else:
    conStr = conStr.replace("database", arows[0].dbname)
    if arows[0].username==None or arows[0].username=="":
      conStr = conStr.replace("username:password@", "")
    else:
      conStr = conStr.replace("username", arows[0].username)
      conStr = conStr.replace("password", arows[0].password)
    if arows[0].port==0 or arows[0].port==None or arows[0].port=="":
      conStr = conStr.replace("localhost", arows[0].host)
    else:
      conStr = conStr.replace("localhost", arows[0].host+":"+str(arows[0].port))
  ns.setConnect(uri=conStr, pool_size=0)
  if ns.db!=None:
    if ns.defineTable(create=created)==False:
      return False
  else:
    ns.error_message = ns.T("Could not connect to the database: ")+database
    return False
  return True

def getSql(lstore, engine, sqlid, appl):
  sql = lstore((lstore[appl].sqlkey == sqlid)&(lstore[appl].engine == engine)).select()
  if len(sql)==0:
    sql = lstore((lstore[appl].sqlkey == sqlid)&(lstore[appl].engine == "all")).select()
  return sql[0].sqlstr

def setSqlParams(lstore, engine, sqlKey, sqlStr, whereStr, havingStr, paramList, rlimit=False, orderbyStr="", rowlimit=500, appl="nflex"):
  if (sqlStr == None): 
    sqlStr = getSql(lstore, engine, sqlKey, appl)
  else:
    sqlStr = str(sqlStr)
  if (paramList != None):
    for param in paramList:
      param["value"] = formatParamType(param["type"], param["value"])
      
      if (param["wheretype"]=="where"):
        whereStr = whereStr.replace(param["name"], str(param["value"]))
      if (param["wheretype"]=="having"):
        havingStr = havingStr.replace(param["name"], str(param["value"]))
      if (param["wheretype"]=="in"):
        sqlStr = sqlStr.replace(param["name"], str(param["value"]))
  sqlStr = sqlStr.replace("@where_str", str(whereStr))
  sqlStr = sqlStr.replace("@having_str", str(havingStr))
  sqlStr = sqlStr.replace("@orderby_str", str(orderbyStr))
  if (rlimit == True):
    sqlStr = sqlStr.replace(";", "")
    sqlStr = sqlStr + " limit " + str(rowlimit)
  return str(sqlStr)

def formatParamType(ptype, value):
  if ((ptype =="string") or (ptype =="date")):
    return "'"+value+"'"
  if ((ptype=="integer") or (ptype=="number") or (ptype=="boolean")):
    return value
