# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

if 0:
  global response; response = globals.Response()
  global request; request = globals.Request()
  from gluon.globals import Session
  global session; session = Session()
  from gluon.sql import DAL
  global db; db = DAL()
  import gluon.languages.translator as T
  from db import DEMO_MODE

from gluon.http import redirect
from gluon.sqlhtml import DIV, SPAN, A, INPUT, FORM
from gluon.html import BR, HR, SELECT, OPTION, P, IMG, TABLE, TR, TD
from gluon.validators import IS_NOT_EMPTY
from gluon.html import URL
from gluon.storage import Storage 
import os

from nerva2py.nervastore import NervaStore
from nerva2py.tools import DatabaseTools
from nerva2py.nas import AdminUi
                                 
def create_menu():
  ns_menu = []
  ns_menu.append((T('User Accounts'), False, URL("accounts"), []))
  ns_menu.append((T('Customer Databases'), False, URL("databases"), []))
  ns_menu_dbs = (T('Database Management'), False, None, [])
  ns_menu.append(ns_menu_dbs)
  ns_menu.append((T('Server Settings'), False, URL("settings"), []))
  ns_menu.append((T('Change Password'), False, URL("change_password"), []))
  
  ns_menu_dbs[3].append((T('Database Creation'), False, URL("create_db"), []))
  ns_menu_dbs[3].append((T('Database Backup'), False, URL("create_backup"), []))
  ns_menu_dbs[3].append((T('Restore the Database'), False, URL("restore_backup"), []))
  return ns_menu

ns = NervaStore(request, session, T, db)
ui = AdminUi('nas_admin',request, session, db)
dbtool = DatabaseTools(ns)
response.title=T('NAS ADMIN')
   
auth = response.auth = ui.connect.auth_ini(controller="nas",use_username=True,reset_password=False,register=True)
if db(db.auth_user.id > 0).count() > 0:
  auth.settings.actions_disabled.append('register')

response.ns_menu = create_menu()
ui.control.create_cmd(response,T)

_editable =True
if session.auth:
  if session.auth.user.has_key("username"):
    if session.auth.user.username=="demo":
      _editable=False
      if request.post_vars:
        request.post_vars = Storage()
        response.flash = T("Demo user: This action is not allowed!")
  else:
    _editable =True
      
@auth.requires(session.alias=='nas_admin', requires_login=True)
def index():
  response.view='nas/index.html'
  response.subtitle = T("Home")
  gform = DIV(P("Nervatura NAS Admin",_style="font-weight: bold;"),
              P(SPAN(T("Username: "),_style="font-weight: bold;"),session.auth.user.username),
              P(SPAN("Ver.No: "+response.verNo,_class="vernum")),
              TABLE(TR(
                       TD(IMG(_style="vertical-align: bottom;", _src=URL('static','images/icon64_ntura_te.png')),
                          _style="width: 64px;padding-right: 0px;"),
                       TD("OPEN SOURCE",BR(),"BUSINESS",BR(),"MANAGEMENT",
                          _style="width: 120px;color: #616161;vertical-align: middle;font-size: 13px;"))),
              P(A("©2011-2014 Nervatura Framework", _href="http://www.nervatura.com", _target="_blank", 
                  _title="Nervatura", _style="font-weight: bold;")),
              _align="center", _style="padding-top:30px;")
  return dict(form=gform)

def login():
  if DEMO_MODE:
    return ui.connect.show_disabled(response.title)
  response.view='nas/login.html'
  form=auth()
  if type(form).__name__=="str":
    session.flash = form
    form = auth.login()
  return dict(form=ui.control.set_input_form(form,submit_label=T("Login")))
  
def logout():
  auth.logout()
  
@auth.requires(session.alias=='nas_admin', requires_login=True)
def change_password():
  response.subtitle = T("Change Password")
  response.view='nas/index.html'
  return dict(form=ui.control.set_input_form(auth.change_password(),submit_label=T("Change password")))
              
@auth.requires(session.alias=='nas_admin', requires_login=True)
def accounts():
  response.subtitle = T("User Accounts")
  response.view='nas/index.html'
  ruri = request.wsgi.environ["REQUEST_URI"]
  frm_type = ui.control.get_frm_type(ruri)
  
  if frm_type=="delete":
    rid = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ui.connect.delete_data("auth_user",rid):
      redirect(URL('accounts'))
      
  if frm_type in("edit","new"):
    response.cmd_back = ui.control.get_mobil_button(label=T("BACK"), href=URL("accounts"),
          icon="back", ajax="false", theme="a")
  else:
    response.cmd_new = ui.control.get_mobil_button(label=T("New"), 
          href=URL("accounts/new/auth_user",**{'user_signature': True}),
          icon="plus", ajax="false", theme="a")
  fields = (db.auth_user.id, db.auth_user.username, db.auth_user.first_name, 
            db.auth_user.last_name, db.auth_user.email)
  headers = {'auth_user.username': T('Username'),
             'auth_user.first_name': T('First Name'), 'auth_user.last_name': T('Last Name'),
             'auth_user.email': T('Email') }

  if _editable:
    db.auth_user.username.represent = lambda value,row: ui.control.get_mobil_button(value, 
        href=URL("accounts/edit/auth_user/"+str(row["id"]),**{'user_signature': True}), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    db.auth_user.id.label=T("Delete")
    db.auth_user.id.represent = lambda value,row: ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, 
          icon="delete", iconpos="notext", ajax="false", theme="d",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this object?")
            +"')){ajax('"+URL('accounts/delete/auth_user'+"/"+str(row["id"]),**{'user_signature': True})
            +"',[],'');jQuery(this).closest('tr').remove();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}")
  else:
    db.auth_user.id.readable = db.auth_user.id.writable = False
  
  gform = ui.control.get_form(query=db.auth_user,field_id=db.auth_user.id,orderby=db.auth_user.username,
                   fields=fields,headers=headers,frm_type=frm_type,priority="0,1",create=_editable)
  return dict(form=gform)

@auth.requires(session.alias=='nas_admin', requires_login=True)
def databases():
  response.subtitle = T("Customer Databases")
  response.view='nas/index.html'
  ruri = request.wsgi.environ["REQUEST_URI"]
  frm_type = ui.control.get_frm_type(ruri)
    
  if frm_type=="delete":
    rid = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ui.connect.delete_data("databases",rid):
      redirect(URL('databases'))
      
  if frm_type in("edit","new"):
    response.cmd_back = ui.control.get_mobil_button(label=T("BACK"), href=URL("databases"),
          icon="back", ajax="false", theme="a")
  else:
    response.cmd_new = ui.control.get_mobil_button(label=T("New"), 
          href=URL("databases/new/databases",**{'user_signature': True}),
          icon="plus", ajax="false", theme="a")
  
  fields = (db.databases.id, db.databases.alias, db.databases.host, 
            db.databases.dbname)
  query = ((db.databases.deleted==False))
  
  if _editable:
    db.databases.alias.represent = lambda value,row: ui.control.get_mobil_button(value, 
        href=URL("databases/edit/databases/"+str(row["id"]),**{'user_signature': True}), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    db.databases.id.label=T("Delete")
    db.databases.id.represent = lambda value,row: ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, 
          icon="delete", iconpos="notext", ajax="false", theme="d",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this object?")
            +"')){ajax('"+URL('databases/delete/databases'+"/"+str(row["id"]),**{'user_signature': True})
            +"',[],'');jQuery(this).closest('tr').remove();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}")
  else:
    db.databases.id.readable = db.databases.id.writable = False
  
  db.databases.user_id.default=session.auth.user.id
  gform = ui.control.get_form(query=query,field_id=db.databases.id,orderby=db.databases.alias,
                   fields=fields,headers={},frm_type=frm_type,priority="0,1",create=_editable)
  return dict(form=gform)

@auth.requires(session.alias=='nas_admin', requires_login=True)
def create_db():
  response.subtitle = T("Database Creation")
  response.view='nas/index.html'
  alias = db((db.databases.deleted==False)).select(db.databases.id,db.databases.alias,orderby=db.databases.alias)
  cmb_alias = SELECT(*[OPTION(field["alias"],_value=field["alias"]) for field in alias], _id="cmb_alias", _style="margin-top: 0px;")
  if len(cmb_alias)==0:
    cmb_alias.insert(0, OPTION("", _value=""))
  gform = DIV(
             HR(),
             P(SPAN(T('1. Create a new database alias. See ')),A("Customer Databases",_href=URL("databases"),_style="color:#0069D6;font-style: italic;"),
               BR(),
               SPAN(T('2. The sqlite and Google SQL databases are created automatically.')),
               BR(),
               SPAN(T('3. Other types of databases must be created manually before.')),
               BR(),
               SPAN(T('4. Please select an alias, and start the creation:'))
               ,_style="font-style: italic;"),
             DIV(SPAN(T('Database alias:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_alias,
               P(ui.control.get_mobil_button(label=T("Start"), href="#", onclick="createDatabase();", icon="check", theme="a"),
                 SPAN(T('Starting the process?'), _id="msg_result",_style="padding-left: 15px;font-style: italic;"),
               _style="padding-top: 0px;")),
             HR()
             ,_style="font-weight: bold;", _align="left")
  return dict(form=gform)

@auth.requires(session.alias=='nas_admin', requires_login=True)
def create_backup():
  response.subtitle = T("Create a Backup")
  response.view='nas/index.html'
  alias = db((db.databases.deleted==False)).select(db.databases.id,db.databases.alias,orderby=db.databases.alias)
  cmb_alias = SELECT(*[OPTION(field["alias"],_value=field["alias"]) for field in alias], _id="cmb_alias")
  if len(cmb_alias)==0:
    cmb_alias.insert(0, OPTION("", _value=""))
  cmb_format = SELECT([OPTION(T("backup"), _value="backup"),OPTION(T("XML"), _value="xml")], _id="cmb_format")
  if len(cmb_format)==0:
    cmb_format.insert(0, OPTION("", _value=""))
  cmb_filename = SELECT([OPTION(T("Alias"), _value=""),OPTION(T("Download"), _value="download"),
                         OPTION(T("Custom"), _value="custom")], _id="cmb_filename")
  if request.env.web2py_runtime_gae:
    cmb_filename = SELECT([OPTION(T("Download"), _value="download")], _id="cmb_filename")
    cust_filename = ""
  else:
    cust_filename = INPUT(_type="text",_value="",_id="cust_filename")
  gform = DIV(
             HR(),
             P(SPAN(T('Nervatura backup: '), _style="color:brown;"),BR(),
               SPAN(T('NOM objects: '), _style="color:green;"),SPAN("address, barcode, contact, currency, customer, deffield, employee, event, fieldvalue, groups, item, link, \
               log, movement, numberdef, pattern, payment, place, price, product, project, rate, tax, tool, trans"),BR(),
              SPAN(T('Settings objects: '), _style="color:green;"),SPAN("ui_audit, ui_applview, ui_filter, ui_groupinput, ui_language, \
                ui_locale, ui_menu, ui_menufields, ui_message, ui_numtotext, ui_report, ui_reportfields, \
                ui_reportsources, ui_userconfig, ui_viewfields, ui_zipcatalog"),BR(),
              SPAN(T('Not included: '), _style="color:red;"),SPAN("ui_printqueue"),BR(),BR(),
              SPAN(T("Independent from the database type and version of the NAS server."),_style="font-style: italic;")),
             DIV(
               DIV(SPAN(T('Database alias:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_alias),
               DIV(SPAN(T('Filename:') ,_style="padding-right: 15px;padding-left: 15px;"),cmb_filename, SPAN(" "),
               cust_filename, _style="padding-top: 10px;"), 
               DIV(SPAN(T('Backup format:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_format, _style="padding-top: 10px;"),
             P(SPAN(ui.control.get_mobil_button(label=T("Start"), href="#", onclick="createDataBackup();", icon="check", theme="a",
                                 title=ns.T('Start customer backup creation')),
                    SPAN(T('Starting the process?'),_style="padding-left: 15px;", _id="msg_result"),_style="font-style: italic;"),
               _style="padding-top: 5px;"),
               ),
             HR()
             ,_style="font-weight: bold;", _align="left")
  return dict(form=gform)

@auth.requires(session.alias=='nas_admin', requires_login=True)
def restore_backup():
  response.subtitle = T("Restore the Customer Data")
  response.view='nas/index.html'
  
  msg_result = T('Starting the process?')
  if request.post_vars:
    if request.post_vars.alias==None or request.post_vars.alias=="":
      msg_result = T("Error: Missing alias parameter!")
    if request.post_vars.has_key("frm_file"):
      if request.post_vars.bfile=="":
        msg_result = T("Error: Missing upload file!")
      else:
        msg_result = dbtool.loadBackupData(alias=request.vars.alias, bfile=request.post_vars.bfile)
    else:
      if request.post_vars.filename=="":
        msg_result = T("Error: Missing upload filename!")
      else:
        msg_result = dbtool.loadBackupData(alias=request.vars.alias, filename=request.post_vars.filename)
    request.post_vars = None
  
  alias = db((db.databases.deleted==False)).select(db.databases.id,db.databases.alias,orderby=db.databases.alias)
  cmb_alias = SELECT(*[OPTION(field["alias"],_value=field["alias"]) for field in alias], _name="alias", _id="cmb_alias")
  if len(cmb_alias)==0:
    cmb_alias.insert(0, OPTION("", _value=""))
  dfiles = os.listdir(os.path.join(ns.request.folder, 'static/backup'))
  files = []
  for dfile in dfiles:
    if str(dfile).endswith(".backup") or str(dfile).endswith(".xml"):
      files.append(dfile)
  files.sort()
  cmb_files = SELECT(*files, _id="cmb_files", _name="filename")
  if len(cmb_files)==0:
    cmb_files.insert(0, OPTION("", _value=""))
  cmd_filename=INPUT(_type="submit",_name="frm_filename", _title= ns.T('Start restore from local backup file'),
                             _value=T("Start restore"),_onclick="msg_result.innerHTML='"+T("Process started. Waiting for the server to respond ...")+"';")
  cmd_filename["_data-theme"] = "a"
  cmd_filename["_data-icon"] = "check"
  cmd_file=INPUT(_type="submit",_name="frm_file", _title= ns.T('Upload file and Start restore'),
                             _value=T("Upload and Start restore"),_onclick="msg_result.innerHTML='"+T("Process started. Waiting for the server to respond ...")+"';")
  cmd_file["_data-theme"] = "a"
  cmd_file["_data-icon"] = "check"
  cmd_file["_data-ajax"] = "false"
  if request.env.web2py_runtime_gae:
    gform = DIV(
              HR(),
              P(SPAN(T('The sqlite and Google SQL databases are created automatically. Other types of databases must be created manually before.'))),
              FORM(
                   DIV(SPAN(T('Database alias:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_alias),
                   DIV(SPAN(T('File:') ,_style="padding-right: 15px;padding-left: 15px;"),
                       INPUT(_type='file', _name='bfile', _id='bfile', _requires=IS_NOT_EMPTY()), SPAN("",_style="padding-left: 15px;"),
                       cmd_file,
                       _style="padding-top: 8px;"), 
                   _id="frm_upload_files",_name="frm_upload", **{"_data-ajax":"false"}),
              P(SPAN(msg_result, _id="msg_result",_style="padding-left: 15px;font-style: italic;padding-top: 5px;")),
              HR()
              ,_style="font-weight: bold;", _align="left")
  else:
    gform = DIV(
              HR(),
              P(SPAN(T('The sqlite and Google SQL databases are created automatically. Other types of databases must be created manually before.'))),
              FORM(
                   DIV(SPAN(T('Database alias:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_alias),
                   DIV(SPAN(T('Filename:') ,_style="padding-right: 15px;padding-left: 15px;"),cmb_files,
                       SPAN("",_style="padding-left: 15px;"), 
                       cmd_filename,
                       _style="padding-top: 8px;"),
                   DIV(SPAN(T('File:') ,_style="padding-right: 15px;padding-left: 15px;"),
                       INPUT(_type='file', _name='bfile', _id='bfile', _requires=IS_NOT_EMPTY()), SPAN("",_style="padding-left: 15px;"),
                       cmd_file,
                       _style="padding-top: 8px;"), 
                   _id="frm_upload_files",_name="frm_upload", **{"_data-ajax":"false"}),
              P(SPAN(msg_result, _id="msg_result",_style="padding-left: 15px;font-style: italic;padding-top: 5px;")),
              HR()
              ,_style="font-weight: bold;", _align="left")
  return dict(form=gform)
  
@auth.requires(session.alias=='nas_admin', requires_login=True)
def createDatabase():
  if session.auth.user.username=="demo":
    return P(SPAN(T("Demo user: This action is not allowed!"),_style="color:red;"))
  if request.vars.alias==None:
    return str(T("Error: Missing alias parameter!"))
  return P(dbtool.createDatabase(request.vars.alias))

@auth.requires(session.alias=='nas_admin', requires_login=True)
def createDataBackup():
  if request.vars.alias==None:
    return P(str(T("Error: Missing alias parameter!")))
  if request.vars.bformat:
    bformat = str(request.vars.bformat)
  else:
    bformat = "backup"
  if ns.local.setEngine(request.vars.alias,True, False)==False:
    if request.vars.filename == "download":
      session.flash = str(ns.error_message)
      redirect(URL("create_backup"))
    else:
      return P("Error: "+str(ns.error_message))
  retbc = dbtool.createDataBackup(alias=request.vars.alias, bformat=bformat, filename=request.vars.filename,verNo=response.verNo)
  if request.vars.filename == "download":
    if (not str(retbc).startswith("<span")) and (not str(retbc).startswith("<div")):
      import time
      response.headers['Content-Type']='application/octet-stream'
      response.headers['Content-Disposition'] = 'attachment;filename="'+str(request.vars.alias)+'_'+time.strftime("%Y%m%d_%H%M")+'.'+bformat+'"'
      return retbc
    else:
      session.flash = str(retbc)
      redirect(URL("create_backup"))
  return P(retbc)
  
@auth.requires(session.alias=='nas_admin', requires_login=True)
def settings():
  response.subtitle = T("Server Settings")
  response.view='nas/index.html'
  
  ruri = request.wsgi.environ["REQUEST_URI"]
  frm_type = ui.control.get_frm_type(ruri)
    
  if frm_type=="delete":
    rid = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ui.connect.delete_data("settings",rid):
      redirect(URL('settings'))
      
  if frm_type in("edit","new"):
    response.cmd_back = ui.control.get_mobil_button(label=T("BACK"), href=URL("settings"),
          icon="back", ajax="false", theme="a")
  else:
    response.cmd_new = ui.control.get_mobil_button(label=T("New"), 
          href=URL("settings/new/settings",**{'user_signature': True}),
          icon="plus", ajax="false", theme="a")
    
  fields = (db.settings.id, db.settings.fieldname, db.settings.value, 
            db.settings.description)
  
  if _editable:
    db.settings.fieldname.represent = lambda value,row: ui.control.get_mobil_button(value, 
        href=URL("settings/edit/settings/"+str(row["id"]),**{'user_signature': True}), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    db.settings.id.label=T("Delete")
    db.settings.id.represent = lambda value,row: ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, 
          icon="delete", iconpos="notext", ajax="false", theme="d",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this object?")
            +"')){ajax('"+URL('settings/delete/settings'+"/"+str(row["id"]),**{'user_signature': True})
            +"',[],'');jQuery(this).closest('tr').remove();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}")
  else:
    db.settings.id.readable = db.settings.id.writable = False
  
  gform = ui.control.get_form(query=db.settings,field_id=db.settings.id,orderby=db.settings.fieldname,
                   fields=fields,headers={},frm_type=frm_type,priority="0,1,2",create=_editable)
  return dict(form=gform)
