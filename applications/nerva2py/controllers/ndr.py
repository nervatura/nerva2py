# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

if 0:
  global request; request = globals.Request()
  global response; response = globals.Response()
  global session; session = globals.Session()
  import gluon.languages.translator as T
  from gluon.sql import DAL
  global db; db = DAL()
  
import os
import base64

from pyamf.amf3 import Decoder, ByteArray
from gluon.http import redirect
from gluon.html import URL, XML
from gluon.fileutils import read_file
from gluon.html import TABLE, TR, TD, CENTER, IMG, HTML, TITLE, BODY, LINK, HEAD, DIV
from gluon.html import CODE

from nerva2py.nervastore import NervaStore
from nerva2py.tools import DataOutput, DatabaseTools

ns = NervaStore(request, session, T, db)
dbout = DataOutput(ns)
dbtool = DatabaseTools(ns)

def translate():
  return "jQuery(document).ready(function(){jQuery('body').translate('%s');});" % request.args(0).split('.')[0]

def getLogin(database, username, password):
  validator = {}
  validator["valid"] = False   
  validator["message"] = "OK"
  if ns.db==None:
    if ns.local.setEngine(database,True)==False:
      validator["valid"] = False
      if ns.error_message!="":
        validator["message"] = str(ns.error_message)
      else: 
        validator["message"] = str(T("Could not connect to the database: ")+database)
      return validator
  if ns.connect.setLogin(username, password)==False:
    validator["valid"] = False
    if ns.error_message!="":
      validator["message"] = str(ns.error_message)
    else: 
      validator["message"] = str(T("Invalid user: ")+username)
    return validator
  validator["valid"] = True   
  validator["message"] = "OK"
  return validator

def getAppl():
  if request.vars.appl:
    file_name = os.path.join(request.folder, 'static/resources/application', str(request.vars.appl))
    if not os.path.isfile(file_name):
      return "Missing application!"
    redirect(URL('static/resources/application', str(request.vars.appl)))
  else:
    return "Missing appl parameter!"
    
def getHelp():
  if not request.vars.appl:
    return "Missing appl parameter!"
  if request.vars.page:
    bfolder = 'static/resources/application/'+str(request.vars.appl)
    if request.vars.lang:
      lang = str(request.vars.lang).lower()
    else:
      lang = "en"
    if request.vars.folder:
      bfolder+="/"+str(request.vars.folder)
    else:
      bfolder+='/help'
    if request.vars.title:
      response.title = request.vars.title
    if request.vars.subtitle:
      response.subtitle = request.vars.subtitle  
    file_name = os.path.join(request.folder, bfolder+"/"+lang, str(request.vars.page)+'.html')
    if not os.path.isfile(file_name):
      file_name = os.path.join(request.folder, bfolder, str(request.vars.page)+'.html')
      if not os.path.isfile(file_name):
        file_name = os.path.join(request.folder, bfolder+"/"+lang, 'index.html')
        if not os.path.isfile(file_name):
          file_name = os.path.join(request.folder, bfolder+'/en', 'index.html')
          if not os.path.isfile(file_name):
            return "Missing index file!"
    response.view=file_name
    return dict()
  else:
    return "Missing page parameter!"

def getResource():  
  if request.vars.file_name:
    rdir = str(request.vars.file_name).split("/")[0]
    if rdir=="backup":
      file_name = os.path.join(request.folder, 'static', str(request.vars.file_name))
    elif rdir in("docs","download","report"):
      file_name = os.path.join(request.folder, 'static/resources', str(request.vars.file_name))
    else:
      return "Valid directories: docs, download, report"
    if request.vars.lang and session._language and session._language!="en":
      file_name+='_'+str(session._language)
    if request.vars.file_type:
      file_name+='.'+str(request.vars.file_type)
    else:
      file_name+='.html'
    if not os.path.isfile(file_name):
      if request.vars.lang and session._language and session._language!="en":
        file_name = str(file_name).replace('_'+str(session._language), "")
        if not os.path.isfile(file_name):
          return T('Missing file...')
      else:
        return T('Missing file...')
    if request.vars.content:
      if request.vars.content=="view":
        response.view="../"+file_name[file_name.find("static"):]
        return dict()
      elif request.vars.content=="xml":
        response.headers['Content-Type']='text/xml'
      else:
        response.headers['Content-Type']=request.vars.content
        if request.vars.file_type:
          response.headers['Content-Disposition'] = 'attachment;filename="'+str(request.vars.file_name).split('/')[len(str(request.vars.file_name).split('/'))-1]+'.'+str(request.vars.file_type)+'"'
    return read_file(file_name)
  else:
    return T('Missing document...')
    
def exportToExcel():
  if not request.vars.code or not request.vars.sheet or not request.vars.view:
    return "Missing parameters!"
  if request.vars.code=="amf":
    sheet = base64.b64decode(request.vars.sheet)
    view = base64.b64decode(request.vars.view)
    sheet = Decoder(ByteArray(sheet)).readElement()
    view = Decoder(ByteArray(view)).readElement()
  else:
    sheet = eval(base64.urlsafe_b64decode(request.vars.sheet))
    view = eval(base64.urlsafe_b64decode(request.vars.view))
  login = view["login"]
  validator = getLogin(login["database"], login["username"], login["password"])
  if validator["valid"]==False:
    return validator["message"]
  response.headers['Content-Type'] = "application/vnd.ms-excel"
  response.headers['Content-Disposition'] = 'attachment;filename="NervaturaExport.xls"'
  return dbout.exportToExcel(sheet, view)

def exportToICalendar():
  if request.vars.code and request.vars.database and request.vars.username:
    if request.vars.code=="base64":
      if request.vars.password:
        password = base64.b64decode(request.vars.password)
      else:
        password = None
      validator = getLogin(base64.b64decode(request.vars.database), base64.b64decode(request.vars.username), password)
    else:
      if request.vars.password:
        password = request.vars.password
      else:
        password = None
      validator = getLogin(request.vars.database, request.vars.username, password)
    if validator["valid"]==False:
      return validator["message"]
  else:
    return T('Missing login parameter(s)!')
  
  if request.vars.calnumber:
    if request.vars.code=="base64":
      calnumber = base64.b64decode(request.vars.calnumber)
    else:
      calnumber = request.vars.calnumber
    events = ns.db(ns.db.event.calnumber==calnumber).select()
    if len(events)>0:
      event_id = events[0]["id"]
    else:
      return T('Missing calnumber: '+request.vars.calnumber)
  elif request.vars.event_id:
    if request.vars.code=="base64":
      event_id = base64.b64decode(request.vars.event_id)
    else:
      event_id = request.vars.event_id
  else:
    return T('Missing calnumber or event_id parameter!')
  if request.vars.alldata:
    export_fields = True
  else:
    export_fields = False
  response.headers['Content-Type'] = "text/ics"
  response.headers['Content-Disposition'] = 'attachment;filename="NervaturaEvents.ics"'
  return dbout.exportToICalendar(event_id, export_fields)

def getParamList(params):
  drows = []
  rows = params.split("||")
  for row in rows:
    drow = {}
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

def exportToReport():
  if request.vars.database and request.vars.username:
    if request.vars.code in("base64","base64all"):
      if request.vars.password:
        password = base64.b64decode(request.vars.password)
      else:
        password = None
      validator = getLogin(base64.b64decode(request.vars.database), base64.b64decode(request.vars.username), password)
    else:
      if request.vars.password:
        password = request.vars.password
      else:
        password = None
      validator = getLogin(request.vars.database, request.vars.username, password)
    if validator["valid"]==False:
      return validator["message"]
  else:
    return T('Missing login parameter(s)!')
  params={}
  filters={}
  if request.vars.reportcode:
    if request.vars.code in("base64","base64all"):
      params["reportcode"] = base64.b64decode(request.vars.reportcode)
    else:
      params["reportcode"] = request.vars.reportcode
  elif request.vars.report_id:
    if request.vars.code in("base64","base64all"):
      params["report_id"] = base64.b64decode(request.vars.report_id)
    else:
      params["report_id"] = request.vars.report_id
  else:
    return T('Missing reportcode or report_id parameter!')
  if request.vars.filters:
    if request.vars.code in("base64","base64all"):
      filters = getParamList(base64.b64decode(request.vars.filters))[0]
    else:
      filters = getParamList(request.vars.filters)[0]
  else:
    return T('Missing filters parameter!')
  
  if request.vars.output:
    if request.vars.code in("base64","base64all"):
      params["output"] = base64.b64decode(request.vars.output)
    else:
      params["output"] = request.vars.output
  else:
    params["output"] = "html"
  
  if request.vars.orientation:
    if request.vars.code in("base64","base64all"):
      params["orientation"] = base64.b64decode(request.vars.orientation)
    else:
      params["orientation"] = request.vars.orientation
  else:
    params["orientation"] = "P"
  
  if request.vars.size:
    if request.vars.code in("base64","base64all"):
      params["size"] = base64.b64decode(request.vars.size)
    else:
      params["size"] = request.vars.size
  else:
    params["size"] = "A4"
  
  if params["output"]=="printer":
    if not request.vars.printername:
      return T('Missing printername parameter!')
    printer_prop = dbout.check_printer(request.vars.printername)
    if printer_prop["state"]==False:
      return printer_prop["error_message"]
    params["output"] = "pdf"
    if request.vars.copies:
      try:
        copies = int(request.vars.copies)
      except:
        copies = 1
    else:
      copies = 1
  else:
    printer_prop = None
    
  report_tmp = dbout.getReport(params,filters)
  if type(report_tmp).__name__=="str":
    if report_tmp=="NODATA":
      return HTML(HEAD(TITLE("Nervatura Report"),
                   LINK(_rel="shortcut icon", _href=URL('static','favicon.ico'), _type="image/x-icon")),
              BODY(DIV(CENTER(TABLE(TR(TD(IMG(_src=URL('static','images/nodata.png'),
                                      _style="border: solid;border-color: #FFFFFF;"),
                            _style="text-align: center;vertical-align: middle;font-weight: bold;font-family: sans-serif;font-size: 20px;")),
                      _style="background-color:#FFFFFF;color:#444444;margin-top:200px;")),_style="width:100%;height:100%")),_style="background-color:#000000;")
    else:
      return report_tmp
  
  if printer_prop:
    print_item = dbout.printReport(printer_prop, report_tmp["template"], "Nervatura Report", copies, params["orientation"], params["size"])
    if print_item["state"]==False:
      return print_item["error_message"]
    return "OK"
  elif report_tmp["filetype"]=="fpdf":
    if params["output"]=="xml":
      response.headers['Content-Type']='text/xml'
    elif params["output"]=="pdf":
      response.headers['Content-Type']='application/pdf'
    if request.vars.code=="base64all":
      return base64.b64encode(report_tmp["template"])
    else:
      return report_tmp["template"]
  elif report_tmp["filetype"]=="xls":
    response.headers['Content-Type'] = "application/vnd.ms-excel"
    response.headers['Content-Disposition'] = 'attachment;filename="NervaturaReport.xls"'
    if request.vars.code=="base64all":
      return base64.b64encode(report_tmp["template"])
    else:
      return report_tmp["template"]
  elif report_tmp["filetype"]=="html":
    response.view = "default/report.html"
    response.title = report_tmp["data"]["title"]
    response.subtitle = ""
    import StringIO
    report_tmp["template"]=response.render(StringIO.StringIO(report_tmp["template"]),report_tmp["data"])
    return dict(template=XML(report_tmp["template"]))
  else:
    if request.vars.code=="base64all":
      return base64.b64encode(report_tmp["template"])
    else:
      return report_tmp["template"]

def show_codefile():
  fpath = request.vars.fpath if request.vars.fpath else "controllers"
  lang = request.vars.language if request.vars.fpath else "python"
  if request.vars.fname:
    return CODE(read_file(os.path.join(request.folder, fpath, request.vars.fname)), language=lang).xml()
  else:
    return "Missing file..."
    
def createDataBackup():
  if request.vars.database and request.vars.username:
    if request.vars.code=="base64":
      if request.vars.password:
        password = base64.b64decode(request.vars.password)
      else:
        password = ""
      username = base64.b64decode(request.vars.username)
      database = base64.b64decode(request.vars.database)
    else:
      if request.vars.password:
        password = request.vars.password
      else:
        password = None
      username = request.vars.username
      database = request.vars.database
    if not ns.db:
      if not ns.local.setEngine(database,True):
        if ns.error_message!="":
          return str(ns.error_message)
        else: 
          return str(ns.T("Could not connect to the database: "))+str(database)
    if not ns.connect.setLogin(username, password):
      if ns.error_message!="":
        return str(ns.error_message)
      else: 
        return str(ns.T("Invalid user: "))+str(username)
  else:
    return T('Error: Missing login parameter(s)!')
  if request.vars.bformat:
    bformat = request.vars.bformat
  else:
    bformat = "backup"

  retbc = dbtool.createDataBackup(alias=request.vars.database, bformat=bformat, filename=request.vars.filename,verNo=response.verNo)
  if request.vars.filename == "download":
    if (not str(retbc).startswith("<span")) and (not str(retbc).startswith("<div")):
      response.headers['Content-Type']='application/octet-stream'
      response.headers['Content-Disposition'] = 'attachment;filename="'+request.vars.database+'.'+bformat+'"'
  return retbc

def restoreDataBackup():
  if request.vars.database and request.vars.username:
    if request.vars.code=="base64":
      if request.vars.password:
        password = base64.b64decode(request.vars.password)
      else:
        password = ""
      username = base64.b64decode(request.vars.username)
      database = base64.b64decode(request.vars.database)
    else:
      if request.vars.password:
        password = request.vars.password
      else:
        password = None
      username = request.vars.username
      database = request.vars.database
    if not ns.db:
      if not ns.local.setEngine(database,True):
        if ns.error_message!="":
          return str(ns.error_message)
        else: 
          return str(ns.T("Could not connect to the database: "))+str(database)
    if not ns.connect.setLogin(username, password):
      if ns.error_message!="":
        return str(ns.error_message)
      else: 
        return str(ns.T("Invalid user: "))+str(username)
  else:
    return T('Missing login parameter(s)!')
  if (request.vars.bfile==None or request.vars.bfile=="") and (request.vars.filename==None or request.vars.filename==""):
    return T('Missing file parameter(s)!')
  if request.vars.filename:
    if request.vars.filename!="":
      return dbtool.loadBackupData(alias=database, filename=request.vars.filename)
  return dbtool.loadBackupData(alias=database, bfile=request.vars.bfile)
