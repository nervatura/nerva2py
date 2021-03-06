# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2015, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

if 0:
  global request; request = globals.Request()
  from gluon.globals import Session
  global session; session = Session()
  global response; response = globals.Response()
  import gluon.languages.translator as T
  from gluon.sql import DAL
  global db; db = DAL()

from nerva2py.nervastore import NervaStore
from nerva2py.ndi import Ndi
from nerva2py.ordereddict import OrderedDict
import base64
from gluon.tools import Service

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
ndi = Ndi(ns)

service = Service()
        
def call():
  session.forget()
  return service()  
#----------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------

def getHost():
  return request.env.remote_addr

def getEncoding():
  import sys
  return sys.getdefaultencoding()
  
def getVernum():
  return response.verNo

@service.jsonrpc
@service.jsonrpc2
def updateData_json(params, data):
  if params==None or data==None:
    return "Error|Missing parameters: params,data"
  return decodeData("update","json",params,data)

def updateData():
  if request.vars.code==None or request.vars.params==None or request.vars.data==None:
    return "Error|Missing parameters: code,params,data"
  return decodeData("update",request.vars.code,request.vars.params,request.vars.data)

@service.jsonrpc
@service.jsonrpc2
def deleteData_json(params, data):
  if params==None or data==None:
    return "Error|Missing parameters: params,data"
  return decodeData("delete","json",params,data)

def deleteData():
  if request.vars.code==None or request.vars.params==None or request.vars.data==None:
    return "Error|Missing parameters: code,params,data"
  return decodeData("delete",request.vars.code,request.vars.params,request.vars.data)

@service.jsonrpc
@service.jsonrpc2
def getData_json(params, filters):
  if params==None or filters==None:
    return "Error|Missing parameters: params,filters"
  return decodeData("get","json",params,filters)

def getData():
  if request.vars.code==None or request.vars.params==None or request.vars.filters==None:
    return "Error|Missing parameters: code,params,filters"
  return decodeData("get",request.vars.code,request.vars.params,request.vars.filters)

def getParamList(params):
  drows = []
  rows = params.split("||")
  for row in rows:
    drow = OrderedDict()
    fields = row.split("|")
    for field in fields:
      if field.find("=")==-1:
        key = field
        value = True
      else:
        key = field[:field.find("=")]
        value = field[field.find("=")+1:]
      drow[key] = value
    if len(drow)>0:
      drows.append(drow)
  return drows
  
def getDecrypt(data):
  return data

def decode_base64(data):
  try:
    return base64.decodestring(data)
  except:
    bdata =data+ "=" * ((4 - len(data) % 4) % 4)
    return base64.decodestring(bdata)
  
def decodeData(ftype,code,params,data):
  if type(code) is list: code = code[0] 
  if not params or params=="":
    return setRetvalue("Error|Missing parameter: params", code)
  else:
    if type(params) is list: params = params[0]
  if ftype!="get" and (not data or data==""):
    return setRetvalue("Error|Missing parameter: data", code)
  if ftype=="get" and (type(data) is list): data = data[0]
  if code=="json":
    param = params
    items = data
  else:
    if code=="base64" or code=="base64all":
      param = getParamList(decode_base64(params))[0]
      data = decode_base64(data)
    else:
      param = getParamList(params)[0]
    items = getParamList(data)
#     if ns.encrypt_data:
#       param = getDecrypt(param)
#       items = getDecrypt(items)
  validator = ndi.getLogin(param)
  if validator["valid"]==False:
    return setRetvalue(validator["message"],code)
  
  if param.has_key("datatype")==False:
    return setRetvalue("Error|Missing parameter: datatype",code)
  
  output="text"
  if ftype=="get": 
    if type(items) is list:
      items = items[0]
    if items.has_key("output"):
      output = items["output"]
  if code=="json" and output not in("json","text","html"):
    output = "json"
    if items.has_key("output"):
      items["output"] = output
  
  return setRetvalue(ndi.callNdiFunc(ftype+"_"+param["datatype"],param,items),code,output)

def setRetvalue(retvalue, code, output="text"):
  if not str(retvalue).startswith("OK") and not str(retvalue).startswith("Error"):
    if output.startswith("xml"):
      response.headers['Content-Type'] = "text/xml"
    elif output=="excel":
      response.headers['Content-Type'] = "application/vnd.ms-excel"
      response.headers['Content-Disposition'] = 'attachment;filename="NervaturaExport.xls"'
    elif output=="json":
      response.headers['Content-Type'] = "text/json"
      if code!="json":
        from gluon.serializers import json
        try:
          retvalue = json(retvalue)
        except:
          retvalue = "json error"
  if code=="base64all" and output=="text":
    retvalue = base64.b64encode(retvalue)
  return retvalue

