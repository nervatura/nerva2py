# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
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

from gluon.http import redirect
from gluon.sqlhtml import SQLFORM, DIV, SPAN, A, INPUT, FORM
from gluon.html import BR, HR, SELECT, OPTION, P, IMG, TABLE, TR, TD
from gluon.validators import IS_NOT_EMPTY
from gluon.tools import Auth, Crud
from gluon.html import URL
from storage import Storage #@UnresolvedImport
import os

from nerva2py.nervastore import NervaStore
from nerva2py.tools import NervaTools
from nerva2py.ndi import Ndi
from nerva2py.localstore import setEngine

response.DEMO_MODE = False
    
def get_back_button(url,title= T('Back to Admin menu')):
  return A(SPAN(_class="icon leftarrow"), _style="padding-top: 8px;padding-bottom: 8px;font-size: 14px;", 
           _class="w2p_trap buttontext button", _title= title, _href=url)
  
def get_command_button(caption,title,color="444444",cmd="",_id="",_height="30px", _top="2px", _href=""):
  return INPUT(_type="button", _value=caption, _title=title, _id=_id,
               _style="height: "+_height+" !important;padding-top: "+_top+" !important;color: #"+color+";font-size: 16px;", _onclick= cmd)

def get_mobil_button(label, href, icon="forward", cformat="ui-btn-right", ajax="true", iconpos="left", 
  rel=None, target=None, style=None, onclick=None, theme=None, cmd_id=None, mini=None, 
  transition=None, position=None, title=None):
  cmd = A(SPAN(label), _href=href, _class=cformat)
  cmd["_data-role"] = "button"
  cmd["_data-icon"] = icon
  cmd["_data-ajax"] = ajax
  cmd["_data-iconpos"] = iconpos
  if title:
    cmd["_title"] = title
  if cformat:
    cmd["_class"] = cformat
  if rel:
    cmd["_data-rel"] = rel
  if target:
    cmd["_target"] = "_blank"
  if style:
    cmd["_style"] = style
  if onclick:
    cmd["_onclick"] = onclick
  if theme:
    cmd["_data-theme"] = theme
  if cmd_id:
    cmd["_id"] = cmd_id
  if mini:
    cmd["_data-mini"] = mini
  if transition:
    cmd["_data-transition"] = transition
  if position:
    cmd["_data-position-to"] = position
  return cmd

def set_counter_bug(form):
  counter = form.elements("div.web2py_counter")
  if len(counter)>0:
    if counter[0][0]==None:
      counter[0][0] = ""

def set_htmltable_style(table, tbl_id=None, priority="0", columntoggle=True):
  table["_data-role"] = "table"
  if tbl_id:
    table["_id"] = tbl_id
  table["_class"] = "ui-body-d ui-shadow table-stripe ui-responsive"
  table["_data-column-btn-theme"] = "a"
  if columntoggle:
    table["_data-mode"] = "columntoggle"
    table["_data-column-btn-text"] = T("Columns to display...")
    table["_data-column-popup-theme"] = "a"
  head = table[0][0]
  head["_class"] = "ui-bar-d"
  pnum=1
  for i in range(len(head)):
    if len(head[i])>0:
      try:
        str(priority).split(",").index(str(i))
      except Exception:
        head[i]["_data-priority"] = pnum
        pnum+=1

def delete_row(rowtype, row_id):
  db(db[rowtype].id==row_id).delete()
  db.commit()
  return True

def get_frm_type(ruri):
  if ruri.find("/edit/")>0:
    return "edit"
  elif ruri.find("/new/")>0:
    return "new"
  elif ruri.find("/delete/")>0:
    return "delete"
  else:
    return "view"
  
def set_input_form(form):
  form["_id"]="frm_input"
  form["_data-ajax"]="false"
  text_inputs = form.elements('input',_type='text')
  for i in range(len(text_inputs)):
    text_inputs[i]["_onkeydown"]="if (event.keyCode == 13) document.forms['frm_input'].submit();"
  text_inputs = form.elements('input',_type='password')
  for i in range(len(text_inputs)):
    text_inputs[i]["_onkeydown"]="if (event.keyCode == 13) document.forms['frm_input'].submit();"
  submit_row = form.element("#submit_record__row")
  submit_row[1][0] = get_mobil_button(label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="a",
        onclick= "document.forms[0].submit();")
  return form

def get_form(query,field_id,orderby,fields=None,headers={},frm_type="view",priority="0,1"):
  gform = SQLFORM.grid(query=query, field_id=field_id, fields=fields, headers=headers, 
                       orderby=orderby, paginate=20, maxtextlength=25,
                       searchable=False, csv=False, details=False, showbuttontext=False,
                       create=_editable, deletable=False, editable=True, selectable=False)
  if type(gform[1][0][0]).__name__!="TABLE":
    if frm_type in ("edit","new"):
      gform = set_input_form(gform)
      if frm_type == "edit":
        gform[1][0][0] = ""
  else:
    htable = gform.elements("div.web2py_htmltable")
    if len(htable)>0:
      set_htmltable_style(htable[0][0],"form_search",priority)
      htable[0][0]["_width"]="100%"
  set_counter_bug(gform)
  return gform

def login_methods(username, password):
  if session.alias!=None:
    auth.messages.invalid_login = T("The NWC and NAS at the same time can not be logged in!")
  return False

def login_onaccept(form):
  session.nas_login=True
  
def logout_onlogout(form):
  session.nas_login=None

def requires_login():
  if session.alias!=None:
    auth.messages.access_denied = T("The NWC and NAS at the same time can not be logged in!")
    auth.settings.on_failed_authorization = URL("user/login")
    return auth.requires(False)
  else:
    return auth.requires(True)
                                 
def create_menu():
  ns_menu = []
  ns_menu.append((T('User Accounts'), False, URL("accounts"), []))
  ns_menu.append((T('Customer Databases'), False, URL("databases"), []))
  ns_menu_dbs = (T('Database Management'), False, None, [])
  ns_menu.append(ns_menu_dbs)
  ns_menu.append((T('Server Settings'), False, URL("settings"), []))
  ns_menu.append((T('Change Password'), False, URL("nas/index", "change_password"), []))
  
  ns_menu_dbs[3].append((T('Database Creation'), False, URL("createDb"), []))
  ns_menu_dbs[3].append((T('Database Backup'), False, URL("createBackup"), []))
  ns_menu_dbs[3].append((T('Restore the Database'), False, URL("restoreBackup"), []))
  return ns_menu
  
auth = Auth(db, hmac_key=Auth.get_or_create_key(), controller="nas") 
crud = Crud(db)

auth.define_tables(username=True, migrate=False, fake_migrate=False) 
auth.settings.remember_me_form = False
auth.settings.reset_password_requires_verification = True
auth.settings.actions_disabled.append('request_reset_password')
auth.settings.register_next = URL('index')
auth.settings.change_password_next = URL('index')
auth.settings.formstyle = 'table3cols'
auth.settings.allow_basic_login=True
auth.messages.submit_button = T('Save')
auth.settings.login_methods.append(login_methods)
auth.settings.login_onaccept.append(login_onaccept)
auth.settings.logout_onlogout = logout_onlogout
auth.requires_login = requires_login
response.auth = auth

if db(db.auth_user.id > 0).count() > 0:
  auth.settings.actions_disabled.append('register')
    
ns = NervaStore(request, T, db)
ns.admin_user = True
dbfu = NervaTools()
response.title=T('NAS ADMIN')
response.cmd_menu = get_mobil_button(label=T("MENU"), href="#main-menu",
                                             icon="bars", cformat="ui-btn-left", ajax="true", iconpos="left")
response.cmd_exit = get_mobil_button(label=T("EXIT"), href=URL("nas/user", "logout"),
                                             icon="power", cformat="ui-btn-right", ajax="false", iconpos="left",
                                             style="color: red;margin:2px;")
response.cmd_home = get_mobil_button(label=T("HOME"), href=URL('index'),
                                             icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
response.cmd_close = get_mobil_button(label=T("Close"), href="#",
                                          icon="delete", cformat="ui-btn-right", ajax="true", iconpos="notext", 
                                          rel="close")
response.ns_menu = create_menu()

if session.auth:
  if session.auth.user.username=="demo":
    _editable=False
    if request.post_vars:
      request.post_vars = Storage()
      response.flash = T("Demo user: This action is not allowed!")
  else:
    _editable =True
      
@auth.requires_login()
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
              P(A("©2011-2013 Nervatura Framework", _href="http://www.nervatura.com", _target="_blank", 
                  _title="Nervatura", _style="font-weight: bold;")),
              _align="center", _style="padding-top:30px;")
  if len(request.args)>0:        
    if request.args[0]=="change_password":
      response.subtitle = T("Change Password")
      return dict(form=set_input_form(auth()))
  return dict(form=gform)
              
@auth.requires_login()
def accounts():
  response.subtitle = T("User Accounts")
  response.view='nas/index.html'
  ruri = request.wsgi.environ["REQUEST_URI"]
  frm_type = get_frm_type(ruri)
  
  if frm_type=="delete":
    rid = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if delete_row("auth_user",rid):
      redirect(URL('accounts'))
      
  if frm_type in("edit","new"):
    response.cmd_back = get_mobil_button(label=T("BACK"), href=URL("accounts"),
          icon="back", ajax="false", theme="a")
  else:
    response.cmd_new = get_mobil_button(label=T("New"), 
          href=URL("accounts/new/auth_user",**{'user_signature': True}),
          icon="plus", ajax="false", theme="a")
  fields = (db.auth_user.id, db.auth_user.username, db.auth_user.first_name, 
            db.auth_user.last_name, db.auth_user.email)
  headers = {'auth_user.username': T('Username'),
             'auth_user.first_name': T('First Name'), 'auth_user.last_name': T('Last Name'),
             'auth_user.email': T('Email') }

  if _editable:
    db.auth_user.username.represent = lambda value,row: get_mobil_button(value, 
        href=URL("accounts/edit/auth_user/"+str(row["id"]),**{'user_signature': True}), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    db.auth_user.id.label=T("Delete")
    db.auth_user.id.represent = lambda value,row: get_mobil_button(T("Delete"), href="#", cformat=None, 
          icon="delete", iconpos="notext", ajax="false", theme="d",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this object?")
            +"')){ajax('"+URL('accounts/delete/auth_user'+"/"+str(row["id"]),**{'user_signature': True})
            +"',[],'');window.location.reload();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}")
  else:
    db.auth_user.id.readable = db.auth_user.id.writable = False
  
  gform = get_form(query=db.auth_user,field_id=db.auth_user.id,orderby=db.auth_user.username,
                   fields=fields,headers=headers,frm_type=frm_type,priority="0,1")
  return dict(form=gform)

@auth.requires_login()
def databases():
  response.subtitle = T("Customer Databases")
  response.view='nas/index.html'
  ruri = request.wsgi.environ["REQUEST_URI"]
  frm_type = get_frm_type(ruri)
    
  if frm_type=="delete":
    rid = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if delete_row("databases",rid):
      redirect(URL('databases'))
      
  if frm_type in("edit","new"):
    response.cmd_back = get_mobil_button(label=T("BACK"), href=URL("databases"),
          icon="back", ajax="false", theme="a")
  else:
    response.cmd_new = get_mobil_button(label=T("New"), 
          href=URL("databases/new/databases",**{'user_signature': True}),
          icon="plus", ajax="false", theme="a")
  
  fields = (db.databases.id, db.databases.alias, db.databases.host, 
            db.databases.dbname)
  
  if _editable:
    db.databases.alias.represent = lambda value,row: get_mobil_button(value, 
        href=URL("databases/edit/databases/"+str(row["id"]),**{'user_signature': True}), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    db.databases.id.label=T("Delete")
    db.databases.id.represent = lambda value,row: get_mobil_button(T("Delete"), href="#", cformat=None, 
          icon="delete", iconpos="notext", ajax="false", theme="d",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this object?")
            +"')){ajax('"+URL('databases/delete/databases'+"/"+str(row["id"]),**{'user_signature': True})
            +"',[],'');window.location.reload();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}")
  else:
    db.databases.id.readable = db.databases.id.writable = False
  
  gform = get_form(query=db.databases,field_id=db.databases.id,orderby=db.databases.alias,
                   fields=fields,headers={},frm_type=frm_type,priority="0,1")
  return dict(form=gform)

@auth.requires_login()
def createDb():
  response.subtitle = T("Database Creation")
  response.view='nas/index.html'
  alias = db().select(db.databases.id,db.databases.alias,orderby=db.databases.alias).as_list()
  cmb_alias = SELECT(*[OPTION(field["alias"],_value=field["alias"]) for field in alias], _id="cmb_alias", _style="margin-top: 0px;")
  if len(cmb_alias)==0:
    cmb_alias.insert(0, OPTION("", _value=""))
  gform = DIV(
             HR(),
             P(SPAN(T('1. Create a new database alias. See ')),A("Customer Databases",_href=URL("databases"),_style="color:#0069D6;font-style: italic;"),
               BR(),
               SPAN(T('2. The sqlite databases are created automatically.')),
               BR(),
               SPAN(T('3. Other types of databases must be created manually before.')),
               BR(),
               SPAN(T('4. Please select an alias, and start the creation:'))
               ,_style="font-style: italic;"),
             DIV(SPAN(T('Database alias:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_alias,
               P(get_mobil_button(label=T("Start"), href="#", onclick="createDatabase();", icon="check", theme="a"),
                 SPAN(T('Starting the process?'), _id="msg_result",_style="padding-left: 15px;font-style: italic;"),
               _style="padding-top: 0px;")),
             HR()
             ,_style="font-weight: bold;", _align="left")
  return dict(form=gform)

@auth.requires_login()
def createBackup():
  response.subtitle = T("Create a Backup")
  response.view='nas/index.html'
  alias = db().select(db.databases.id,db.databases.alias,orderby=db.databases.alias).as_list()
  cmb_alias = SELECT(*[OPTION(field["alias"],_value=field["alias"]) for field in alias], _id="cmb_alias", _style="width: 400px;height: 25px;")
  if len(cmb_alias)==0:
    cmb_alias.insert(0, OPTION("", _value=""))
  cmb_btype = SELECT([OPTION(T("customer"), _value="customer"),OPTION(T("settings"), _value="settings")], _id="cmb_btype",_style="width: 100px;height: 25px;")
  if len(cmb_btype)==0:
    cmb_btype.insert(0, OPTION("", _value=""))
  cmb_format = SELECT([OPTION(T("backup"), _value="backup"),OPTION(T("XML"), _value="xml")], _id="cmb_format",_style="width: 100px;height: 25px;")
  if len(cmb_format)==0:
    cmb_format.insert(0, OPTION("", _value=""))
  cmb_filename = SELECT([OPTION(T("Alias"), _value=""),OPTION(T("Download"), _value="download"),
                         OPTION(T("Custom"), _value="custom")], _id="cmb_filename",_style="width: 100px;height: 25px;")
  if len(cmb_filename)==0:
    cmb_filename.insert(0, OPTION("", _value=""))
  cmb_nom = SELECT([OPTION(T("All"), _value=""),
                         OPTION(T("Custom"), _value="custom")], _id="cmb_nom",_style="width: 100px;height: 25px;")
  if len(cmb_nom)==0:
    cmb_nom.insert(0, OPTION("", _value=""))
  gform = DIV(
             HR(),
             P(SPAN(T('Customer backup: '), _style="color:brown;"),BR(),
               SPAN(T('NOM objects: '), _style="color:green;"),SPAN("address, barcode, contact, currency, customer, deffield, employee, event, groups, item, link, \
               movement, numberdef, pattern, payment, place, price, product, project, rate, tax, tool, trans, setting"),BR(),
              SPAN(T('Not included: '), _style="color:red;"),SPAN("log, user interface objects (starting with the ui_) and deleted rows (deleted flag)"),BR(),BR(),
              SPAN(T('Settings backup: '), _style="color:brown;"),BR(),
              SPAN(T('Settings objects: '), _style="color:green;"),SPAN("ui_audit, ui_applview, ui_filter, ui_groupinput, ui_language, \
                ui_locale, ui_menu, ui_menufields, ui_message, ui_numtotext, ui_report, ui_reportfields, \
                ui_reportsources, ui_userconfig, ui_viewfields, ui_zipcatalog"),BR(),
              SPAN(T('Not included: '), _style="color:red;"),SPAN("ui_printqueue and other NOM objects"),BR(),BR(),
              SPAN(T("Independent from the database type and version of the NAS server."),_style="font-style: italic;")),
             DIV(
               DIV(SPAN(T('Database alias:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_alias),
               DIV(SPAN(T('Filename:') ,_style="padding-right: 15px;padding-left: 15px;"),cmb_filename, SPAN(" "),
               INPUT(_type="text",_value="",_id="cust_filename",_style="width: 327px;height: 12px;"), _style="padding-top: 10px;"),
               DIV(SPAN(T('NOM objects:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_nom, SPAN(" "),
               INPUT(_type="text",_value="",_id="cust_nom",_style="width: 300px;height: 10px;"),_style="padding-top: 10px;"), 
               DIV(SPAN(T('Backup type:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_btype,
                   SPAN(T('Backup format:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_format, _style="padding-top: 10px;"),
             P(SPAN(get_mobil_button(label=T("Start"), href="#", onclick="createDataBackup();", icon="check", theme="a",
                                 title=ns.T('Start customer backup creation')),
                    SPAN(T('Starting the process?'),_style="padding-left: 15px;", _id="msg_result"),_style="font-style: italic;"),
               _style="padding-top: 5px;"),
               ),
             HR()
             ,_style="font-weight: bold;", _align="left")
  return dict(form=gform)

@auth.requires_login()
def restoreBackup():
  response.subtitle = T("Restore the Customer Data")
  response.view='nas/index.html'
  
  msg_result = T('Starting the process?')
  if request.post_vars:
    if request.post_vars.alias==None or request.post_vars.alias=="":
      msg_result = T("Error: Missing alias parameter!")
    ndi = Ndi(ns)
    if setEngine(ns, request.vars.alias,True, False)==False:
      msg_result = str("Error: "+ns.error_message)
    elif request.post_vars.has_key("frm_file"):
      if request.post_vars.bfile=="":
        msg_result = T("Error: Missing upload file!")
      else:
        msg_result = dbfu.loadBackupData(ns, ndi, bfile=request.post_vars.bfile)
    else:
      if request.post_vars.filename=="":
        msg_result = T("Error: Missing upload filename!")
      else:
        msg_result = dbfu.loadBackupData(ns, ndi, filename=request.post_vars.filename)
    request.post_vars = None
  
  alias = db().select(db.databases.id,db.databases.alias,orderby=db.databases.alias).as_list()
  cmb_alias = SELECT(*[OPTION(field["alias"],_value=field["alias"]) for field in alias], _name="alias", _id="cmb_alias", _style="width: 362px;height: 25px;")
  if len(cmb_alias)==0:
    cmb_alias.insert(0, OPTION("", _value=""))
  dfiles = os.listdir(os.path.join(ns.request.folder, 'static/backup'))
  files = []
  for dfile in dfiles:
    if str(dfile).endswith(".backup") or str(dfile).endswith(".xml"):
      files.append(dfile)
  files.sort()
  cmb_files = SELECT(*files, _id="cmb_files", _name="filename", _style="width: 400px;height: 25px;")
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
  gform = DIV(
              HR(),
              P(SPAN(T('It is recommended to create the database before restoring! See ')),
                A("Create a new Nervatura database",_href=URL("createDb"),_style="color:#0069D6;font-style: italic;")),
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
  
@auth.requires_login()
def createDatabase():
  if session.auth.user.username=="demo":
    return P(SPAN(T("Demo user: This action is not allowed!"),_style="color:red;"))
  if request.vars.alias==None:
    return str(T("Error: Missing alias parameter!"))
  return P(dbfu.createDatabase(ns, request.vars.alias))

@auth.requires_login()
def createDataBackup():
  if request.vars.alias==None:
    return P(str(T("Error: Missing alias parameter!")))
  if request.vars.btype==None or request.vars.btype not in("customer","settings"):
    return P(str(T("Error: Missing backup type parameter!")))
  if request.vars.bformat:
    bformat = request.vars.bformat
  else:
    bformat = "backup"
  if request.vars.lst_nom:
    if request.vars.bformat:
      return P(str(T("Error: The setting is set, the backup only when all objects are allowed!!")))
    lst_nom = str(request.vars.lst_nom).split(",")
  else:
    lst_nom = []
  if setEngine(ns, request.vars.alias,True, False)==False:
    return P(str("Error: "+ns.error_message))
  ndi = Ndi(ns)
  retbc = dbfu.createDataBackup(ns, ndi, alias=request.vars.alias, btype=request.vars.btype, lst_nom=lst_nom, 
                                        bformat=bformat, filename=request.vars.filename,verNo=response.verNo)
  if request.vars.filename == "download":
    if (not str(retbc).startswith("<span")) and (not str(retbc).startswith("<div")):
      response.headers['Content-Type']='application/octet-stream'
      response.headers['Content-Disposition'] = 'attachment;filename="'+request.vars.alias+'.'+bformat+'"'
  return P(retbc)
  
@auth.requires_login()
def settings():
  response.subtitle = T("Server Settings")
  response.view='nas/index.html'
  
  ruri = request.wsgi.environ["REQUEST_URI"]
  frm_type = get_frm_type(ruri)
    
  if frm_type=="delete":
    rid = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if delete_row("settings",rid):
      redirect(URL('settings'))
      
  if frm_type in("edit","new"):
    response.cmd_back = get_mobil_button(label=T("BACK"), href=URL("settings"),
          icon="back", ajax="false", theme="a")
  else:
    response.cmd_new = get_mobil_button(label=T("New"), 
          href=URL("settings/new/settings",**{'user_signature': True}),
          icon="plus", ajax="false", theme="a")
    
  fields = (db.settings.id, db.settings.fieldname, db.settings.value, 
            db.settings.description)
  
  if _editable:
    db.settings.fieldname.represent = lambda value,row: get_mobil_button(value, 
        href=URL("settings/edit/settings/"+str(row["id"]),**{'user_signature': True}), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    db.settings.id.label=T("Delete")
    db.settings.id.represent = lambda value,row: get_mobil_button(T("Delete"), href="#", cformat=None, 
          icon="delete", iconpos="notext", ajax="false", theme="d",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this object?")
            +"')){ajax('"+URL('settings/delete/settings'+"/"+str(row["id"]),**{'user_signature': True})
            +"',[],'');window.location.reload();;};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}")
  else:
    db.settings.id.readable = db.settings.id.writable = False
  
  gform = get_form(query=db.settings,field_id=db.settings.id,orderby=db.settings.fieldname,
                   fields=fields,headers={},frm_type=frm_type,priority="0,1,2")
  return dict(form=gform)

def user():
  response.view='nas/index.html'
  return dict(form=set_input_form(auth()))