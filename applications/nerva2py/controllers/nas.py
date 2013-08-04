# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Project
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

from gluon.sqlhtml import SQLFORM, DIV, SPAN, A, UL, LI, INPUT, FORM
from gluon.html import H3, BR, HR, SELECT, OPTION, P
from gluon.validators import IS_NOT_EMPTY
from gluon.tools import Auth, Crud
from gluon.html import URL
from storage import Storage #@UnresolvedImport
import os

from nerva2py.nervastore import NervaStore
from nerva2py.tools import NervaTools
from nerva2py.ndi import Ndi
from nerva2py.localstore import setEngine
  
def get_back_button(url,title= T('Back to Admin menu')):
  return A(SPAN(_class="icon leftarrow"), _style="padding-top: 8px;padding-bottom: 8px;font-size: 14px;", 
           _class="w2p_trap buttontext button", _title= title, _href=url)
  
def get_command_button(caption,title,color="444444",cmd="",_id="",_height="30px", _top="2px", _href=""):
  return INPUT(_type="button", _value=caption, _title=title, _id=_id,
               _style="height: "+_height+" !important;padding-top: "+_top+" !important;color: #"+color+";font-size: 16px;", _onclick= cmd)

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
response.title=T('NAS ADMINISTRATION')
response.subtitle = get_command_button(caption=T("Logout"),title=T("Logout from NAS"), 
                      cmd="window.location ='"+URL("nas/user", "logout")+"'", color="006400")

if session.auth:
  if session.auth.user.username=="demo":
    _deletable=False
    if request.post_vars:
      request.post_vars = Storage()
      response.flash = T("Demo user: This action is not allowed!")
  else:
    _deletable =True
      
@auth.requires_login()
def index():
  response.frm_name = "admin"
  response.view='nas/index.html'
  response.frm_caption = T("Welcome")
  gform = H3(
             UL(
                LI(A(SPAN(T("User Accounts")),_href=URL("accounts"))),
                LI(A(SPAN(T("Customer Databases")),_href=URL("databases"))),
                LI(A(SPAN(T("Database Management")),_href=URL("management"))),
                LI(A(T("Server Settings"),_href=URL("settings"))),
                LI(A(T("Change Password"),_href=URL("nas/index", "change_password")))
                ), _style="font-weight: bold;"
             )
  if len(request.args)>0:        
    if request.args[0]=="change_password":
      response.frm_name = "user"
      response.frm_caption = SPAN(get_back_button(URL("index")),BR(),BR(),T('Change Password'))
      return dict(form=auth())
  return dict(form=gform)

@auth.requires_login()
def accounts():
  response.frm_name = "accounts"
  response.view='nas/index.html'
  response.frm_caption = SPAN(get_back_button(URL("index")), BR(),BR(), T('User Accounts'))
  fields = (db.auth_user.id, db.auth_user.username, db.auth_user.first_name, 
            db.auth_user.last_name, db.auth_user.email)
  headers = {'auth_user.username': T('Username'),
             'auth_user.first_name': T('First Name'), 'auth_user.last_name': T('Last Name'),
             'auth_user.email': T('Email') }
  db.auth_user.id.readable = db.auth_user.id.writable = False
  gform = SQLFORM.grid(query=db.auth_user, field_id=db.auth_user._id, fields=fields, headers=headers, 
                       orderby=db.auth_user.username, paginate=20, maxtextlength=25,
                       searchable=False, csv=False, details=False, showbuttontext=False,
                       create=True, deletable=_deletable, editable=True, selectable=False)
  return dict(form=gform)

@auth.requires_login()
def databases():
  response.frm_name = "databases"
  response.view='nas/index.html'
  response.frm_caption = SPAN(get_back_button(URL("index")), BR(),BR(), T('Customer Databases'))
  fields = (db.databases.id, db.databases.alias, db.databases.host, 
            db.databases.dbname)
  db.databases.id.readable = db.databases.id.writable = False
  if db(db.databases.id > 0).count() == 0:
    gform = crud.create(db.databases)
  else:
    gform = SQLFORM.grid(query=db.databases, field_id=db.databases._id, fields=fields, 
                       orderby=db.databases.alias, maxtextlength=25, paginate=25,
                       searchable=False, csv=False, details=False, showbuttontext=False,
                       create=True, deletable=_deletable, editable=True, selectable=False)
  return dict(form=gform)

@auth.requires_login()
def management():
  response.frm_name = "management"
  response.view='nas/index.html'
  response.frm_caption = SPAN(get_back_button(URL("index")), BR(),BR(), T('Database Management'))
  gform = H3(
             UL(
                LI(A(SPAN(T("Create a new Nervatura database")),_href=URL("createDb"))),
                LI(A(SPAN(T("Create a Database Backup")),_href=URL("createBackup"))),
                LI(A(SPAN(T("Restore the Database Data")),_href=URL("restoreBackup")))
                ), _style="font-weight: bold;"
             )
  return dict(form=gform)

@auth.requires_login()
def createDb():
  response.frm_name = "createDb"
  response.view='nas/index.html'
  response.frm_caption = SPAN(get_back_button(URL("management"),title=T('Back to Database Management')), BR(),BR(), T('Database Creation'))
  alias = db().select(db.databases.id,db.databases.alias,orderby=db.databases.alias).as_list()
  cmb_alias = SELECT(*[OPTION(field["alias"],_value=field["alias"]) for field in alias], _id="cmb_alias", _style="margin-top: 0px;")
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
             P(SPAN(T('Database alias:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_alias,
               SPAN("",_style="padding-left: 15px;"), A(SPAN(_class="icon loop")," ",SPAN(T("Start"), _style="font-weight: bold;"), 
                    _style="height: 20px;vertical-align: middle;", _class="w2p_trap buttontext button", 
                    _href="#", _onclick="createDatabase()", _title= ns.T('Start database creation')),
               _style="padding-top: 0px;"),
             P(SPAN(T('Starting the process?'), _id="msg_result",_style="padding-left: 15px;font-style: italic;")),
             HR()
             ,_style="font-weight: bold;")
  return dict(form=gform)

@auth.requires_login()
def createBackup():
  response.frm_name = "createBackup"
  response.view='nas/index.html'
  response.frm_caption = SPAN(get_back_button(URL("management"),title=T('Back to Database Management')), BR(),BR(), T('Create a Database Backup'))
  alias = db().select(db.databases.id,db.databases.alias,orderby=db.databases.alias).as_list()
  cmb_alias = SELECT(*[OPTION(field["alias"],_value=field["alias"]) for field in alias], _id="cmb_alias", _style="width: 400px;height: 25px;")
  cmb_btype = SELECT([OPTION(T("customer"), _value="customer"),OPTION(T("settings"), _value="settings")], _id="cmb_btype",_style="width: 100px;height: 25px;")
  cmb_format = SELECT([OPTION(T("backup"), _value="backup"),OPTION(T("XML"), _value="xml")], _id="cmb_format",_style="width: 100px;height: 25px;")
  cmb_filename = SELECT([OPTION(T("Alias"), _value=""),OPTION(T("Download"), _value="download"),
                         OPTION(T("Custom"), _value="custom")], _id="cmb_filename",_style="width: 100px;height: 25px;")
  cmb_nom = SELECT([OPTION(T("All"), _value=""),
                         OPTION(T("Custom"), _value="custom")], _id="cmb_nom",_style="width: 100px;height: 25px;")
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
             P(SPAN("",_style="padding-left: 15px;"), A(SPAN(_class="icon loop")," ",SPAN(T("Start"), _style="font-weight: bold;"), 
                    _style="height: 20px;vertical-align: middle;", _class="w2p_trap buttontext button", 
                    _href="#", _onclick="createDataBackup()", _title= ns.T('Start customer backup creation')),
               SPAN(T('Starting the process?'), _id="msg_result",_style="padding-left: 15px;font-style: italic;"), _style="padding-top: 5px;"),
               ),
             HR()
             ,_style="font-weight: bold;")
  return dict(form=gform)

@auth.requires_login()
def restoreBackup():
  response.frm_name = "restoreBackup"
  response.view='nas/index.html'
  response.frm_caption = SPAN(get_back_button(URL("management"),title=T('Back to Database Management')), BR(),BR(), T('Restore the Customer Data'))
  
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
  dfiles = os.listdir(os.path.join(ns.request.folder, 'static/backup'))
  files = []
  for dfile in dfiles:
    if str(dfile).endswith(".backup") or str(dfile).endswith(".xml"):
      files.append(dfile)
  files.sort()
  cmb_files = SELECT(*files, _id="cmb_files", _name="filename", _style="width: 400px;height: 25px;")
  gform = DIV(
              HR(),
              P(SPAN(T('It is recommended to create the database before restoring! See ')),
                A("Create a new Nervatura database",_href=URL("createDb"),_style="color:#0069D6;font-style: italic;")),
              FORM(
                   DIV(SPAN(T('Database alias:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_alias),
                   DIV(SPAN(T('Filename:') ,_style="padding-right: 15px;padding-left: 15px;"),cmb_files,
                       SPAN("",_style="padding-left: 15px;"), 
                       INPUT(_type="submit",_name="frm_filename", _title= ns.T('Start restore from local backup file'),
                             _value=T("Start restore"),_onclick="msg_result.innerHTML='"+T("Process started. Waiting for the server to respond ...")+"';"),
                       _style="padding-top: 8px;"),
                   DIV(SPAN(T('File:') ,_style="padding-right: 15px;padding-left: 15px;"),
                       INPUT(_type='file', _name='bfile', _id='bfile', _requires=IS_NOT_EMPTY()), SPAN("",_style="padding-left: 15px;"),
                       INPUT(_type="submit",_name="frm_file", _title= ns.T('Upload file and Start restore'),
                             _value=T("Upload and Start restore"),_onclick="msg_result.innerHTML='"+T("Process started. Waiting for the server to respond ...")+"';"),
                       _style="padding-top: 8px;"), 
                   _id="frm_upload_files",_name="frm_upload"),
              P(SPAN(msg_result, _id="msg_result",_style="padding-left: 15px;font-style: italic;")),
              HR()
              ,_style="font-weight: bold;")
  return dict(form=gform)

@auth.requires_login()
def restoreSetBk():
  response.frm_name = "restoreSetBk"
  response.view='nas/index.html'
  response.frm_caption = SPAN(get_back_button(URL("management"),title=T('Back to Database Management')), BR(),BR(), T('Restore the Settings Data'))
  gform = DIV()
  return dict(form=gform)
  
@auth.requires_login()
def createDatabase():
  if session.auth.user.username=="demo":
    return SPAN(T("Demo user: This action is not allowed!"),_style="color:red;")
  if request.vars.alias==None:
    return str(T("Error: Missing alias parameter!"))
  return dbfu.createDatabase(ns, request.vars.alias)

@auth.requires_login()
def createDataBackup():
  if request.vars.alias==None:
    return str(T("Error: Missing alias parameter!"))
  if request.vars.btype==None or request.vars.btype not in("customer","settings"):
    return str(T("Error: Missing backup type parameter!"))
  if request.vars.bformat:
    bformat = request.vars.bformat
  else:
    bformat = "backup"
  if request.vars.lst_nom:
    if request.vars.bformat:
      return str(T("Error: The setting is set, the backup only when all objects are allowed!!"))
    lst_nom = str(request.vars.lst_nom).split(",")
  else:
    lst_nom = []
  if setEngine(ns, request.vars.alias,True, False)==False:
    return str("Error: "+ns.error_message)
  ndi = Ndi(ns)
  retbc = dbfu.createDataBackup(ns, ndi, alias=request.vars.alias, btype=request.vars.btype, lst_nom=lst_nom, 
                                        bformat=bformat, filename=request.vars.filename)
  if request.vars.filename == "download":
    if (not str(retbc).startswith("<span")) and (not str(retbc).startswith("<div")):
      response.headers['Content-Type']='application/octet-stream'
      response.headers['Content-Disposition'] = 'attachment;filename="'+request.vars.alias+'.'+bformat+'"'
  return retbc
  
@auth.requires_login()
def settings():
  response.frm_name = "settings"
  response.view='nas/index.html'
  response.frm_caption = SPAN(get_back_button(URL("index")), BR(),BR(), T('Server Settings'))
  fields = (db.settings.id, db.settings.fieldname, db.settings.value, 
            db.settings.description)
  db.settings.id.readable = db.settings.id.writable = False
  gform = SQLFORM.grid(query=db.settings, field_id=db.settings._id, fields=fields, 
                       orderby=db.settings.fieldname, paginate=25, maxtextlength=25,
                       searchable=False, csv=False, details=False, showbuttontext=False,
                       create=True, deletable=_deletable, editable=True, selectable=False)
  return dict(form=gform)

def user():
  response.frm_name = "user"
  response.view='nas/index.html'
  response.subtitle=SPAN("Ver.No: "+response.verNo, _class="vernum")
  response.frm_caption = T("Login")
  return dict(form=auth())