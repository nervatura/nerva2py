# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2015, Csaba Kappel
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

from gluon.sqlhtml import SQLFORM
from gluon.validators import IS_IN_DB, IS_IN_SET, IS_EMPTY_OR
from gluon.html import TBODY, THEAD, TH, TEXTAREA, CODE
from gluon.sql import Field

from nerva2py.nervastore import NervaStore
from nerva2py.tools import DatabaseTools, NervaTools
from nerva2py.nas import AdminUi
                                 
def create_menu():
  ns_menu = []
  ns_menu.append((T('User Accounts'), False, URL("accounts"), []))
  ns_menu.append((T('Customer Databases'), False, URL("databases"), []))
  ns_menu_dbs = (T('Database Management'), False, None, [])
  ns_menu.append(ns_menu_dbs)
  ns_menu.append((T('Report templates'), False, URL("reports"), []))
  ns_menu.append((T('Server Settings'), False, URL("settings"), []))
  ns_menu.append((T('Change Password'), False, URL("change_password"), []))
  
  ns_menu_dbs[3].append((T('Database Creation'), False, URL("create_db"), []))
  ns_menu_dbs[3].append((T('Database Backup'), False, URL("create_backup"), []))
  ns_menu_dbs[3].append((T('Restore the Database'), False, URL("restore_backup"), []))
  return ns_menu

ns = NervaStore(request, session, T, db)
ui = AdminUi('nas_admin',request, session, db)
dbtool = DatabaseTools(ns); ntool = NervaTools(ns);
response.title=T('NAS ADMIN')
   
auth = response.auth = ui.connect.auth_ini(controller="nas",use_username=True,reset_password=False,register=True)
if db(db.auth_user.id > 0).count() > 0:
  auth.settings.actions_disabled.append('register')

response.ns_menu = create_menu()
ui.control.create_cmd(response,T,"b")

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
              P(A("©2011-2015 Nervatura Framework", _href="http://www.nervatura.com", _target="_blank", 
                  _title="Nervatura", _style="font-weight: bold;")),
              _align="center", _style="padding-top:30px;")
  return dict(form=gform)

def login():
  if DEMO_MODE:
    return ui.connect.show_disabled(response.title)
  response.view='nas/login.html'
  form=auth()
  if type(form).__name__=="str" or type(form).__name__=="lazyT":
    if type(form).__name__=="str":
      session.flash = form
    form = auth.login()
  return dict(form=ui.control.set_input_form(form,submit_label=T("Login"),theme="b"))
  
def logout():
  auth.logout()
  
@auth.requires(session.alias=='nas_admin', requires_login=True)
def change_password():
  response.subtitle = T("Change Password")
  response.view='nas/index.html'
  return dict(form=ui.control.set_input_form(auth.change_password(),submit_label=T("Change password"), theme="b"))
              
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
          icon="back", cformat=None, ajax="false", theme="b", style="width: 100px;")
  else:
    response.cmd_new = ui.control.get_mobil_button(label=T("New"), 
          href=URL("accounts/new/auth_user",**{'user_signature': True}),
          icon="plus", cformat=None, ajax="false", theme="b", style="width: 100px;")
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
          icon="delete", iconpos="notext", ajax="false", theme="b",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this object?")
            +"')){ajax('"+URL('accounts/delete/auth_user'+"/"+str(row["id"]),**{'user_signature': True})
            +"',[],'');jQuery(this).closest('tr').remove();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}")
  else:
    db.auth_user.id.readable = db.auth_user.id.writable = False
  
  gform = ui.control.get_form(query=db.auth_user,field_id=db.auth_user.id,orderby=db.auth_user.username,
                   fields=fields,headers=headers,frm_type=frm_type,priority="0,1",create=_editable)
  return dict(form=gform)

def create_preview_img(ptype,keyname,title):
  if ptype=="button":
    cmd_preview = ui.control.get_mobil_button(T("Preview"), 
      href="#"+keyname.replace("/", "_"), cformat=None, icon="info", 
      title=title, theme="a", rel="popup", position="window", transition="fade")
    ipath = 'static/resources/report'
  else:
    cmd_preview = A(IMG(_src=URL('static/resources/application/images', keyname+'_min.png'), _title=title, _alt=title),
               _href="#"+keyname.replace("/", "_"))
    cmd_preview["_data-rel"] = "popup"
    cmd_preview["_data-position-to"] = "window"
    cmd_preview["_data-transition"] = "fade"
    ipath = 'static/resources/application/images'
  cmd_close = A(T("Close"), _href="#", _class="ui-btn-right")
  cmd_close["_data-rel"] = "back"
  cmd_close["_data-role"] = "button"
  cmd_close["_data-theme"] = "b"
  cmd_close["_data-icon"] = "delete"
  cmd_close["_data-iconpos"] = "notext"
  pop = DIV(cmd_close,
            DIV(title,_style="font-weight: bold;padding-bottom:4px;", _align="center"),
            IMG(_src=URL(ipath, keyname+'.png'), _title=title, _alt=title),
            _id=keyname.replace("/", "_"), _style="padding:10px;padding-top:5px;")
  pop["_data-role"] = "popup"
  pop["_data-overlay-theme"] = "b"
  pop["_data-theme"] = "b"
  pop["_data-corners"] = "true"
  return DIV(cmd_preview,pop, _style="padding-right:5px;")

@auth.requires(session.alias=='nas_admin', requires_login=True)
def report_template():
  response.subtitle = T("Edit report template")
  response.view='nas/template.html'
  #response.cmd_menu = None
  response.cmd_labels = ui.control.get_mobil_button(label=T("Labels"), href="#", 
        cformat=None, style="text-align: left;", icon="edit", ajax="true", theme="d",
        onclick= "document.getElementById('edit_label').style.display = 'block';"
        +"document.getElementById('edit_label_update').style.display = 'block';"
        +"document.getElementById('edit_template_update').style.display = 'none';"
        +"document.getElementById('view_template').style.display = 'none';"
        +"document.getElementById('edit_template').style.display = 'none';return true;")
  response.cmd_view = ui.control.get_mobil_button(label=T("View XML"), href="#", 
        cformat=None, style="text-align: left;", icon="page", ajax="true", theme="d",
        onclick= "document.getElementById('edit_label').style.display = 'none';"
        +"document.getElementById('edit_label_update').style.display = 'none';"
        +"document.getElementById('edit_template_update').style.display = 'none';"
        +"document.getElementById('view_template').style.display = 'block';"
        +"document.getElementById('edit_template').style.display = 'none';return true;")
  response.cmd_edit = ui.control.get_mobil_button(label=T("Edit XML"), href="#", 
        cformat=None, style="text-align: left;", icon="edit", ajax="true", theme="d",
        onclick= "document.getElementById('edit_label').style.display = 'none';"
        +"document.getElementById('edit_label_update').style.display = 'none';"
        +"document.getElementById('edit_template_update').style.display = 'block';"
        +"document.getElementById('view_template').style.display = 'none';"
        +"document.getElementById('edit_template').style.display = 'block';return true;")
  response.cmd_labels_update = ui.control.get_mobil_button(label=T("Save"), href="#", 
      cformat=None, style="text-align: left;", icon="check", ajax="false", theme="a",
      onclick= "document.forms['frm_labels'].submit();")
  response.frm_report_update = ui.control.get_mobil_button(label=T("Save"), href="#", 
      cformat=None, style="text-align: left;", icon="check", ajax="false", theme="a",
      onclick= "document.forms['frm_report'].submit();")
  labels,tmp_view,tmp_edit="","",""
  response.report_name=""
  
  if ns.local.setEngine(database=db.databases(id=request.vars["database"]).alias, check_ndi=False, created=False, createdb=False):
    
    
    if request.post_vars.has_key("update_labels"):
      for label_id in request.post_vars.keys():
        if label_id not in("update_labels"):
          row_id = ns.connect.updateData("ui_message", 
                     values={"id":label_id,"msg":request.post_vars[label_id]}, validate=False, insert_row=False)
          if not row_id:
            response.flash = str(ns.error_message)
      ns.db.commit()
    
    if request.post_vars.has_key("report_template"):
      row_id = ns.connect.updateData("ui_report", 
                  values={"id":ns.db.ui_report(reportkey=request.vars["reportkey"])["id"],"report":request.post_vars["report_template"]}, validate=False, insert_row=False)
      if not row_id:
        response.flash = str(ns.error_message)
      ns.db.commit()
    
    report = ns.db.ui_report(reportkey=request.vars["reportkey"])
    if report:
      response.report_name = report["repname"]
      tmp_view = CODE(report["report"])
      tmp_edit = TEXTAREA(_name="report_template", value=report["report"], 
        _style="height: auto!important;overflow-y: scroll;", _rows=20)
      response.update_labels = INPUT(_name="update_labels", _type="hidden", _value="yes")
      
      ui_message = ns.db((ns.db.ui_message.secname.like(report["reportkey"]+"%"))).select(orderby=ns.db.ui_message.secname|ns.db.ui_message.fieldname)
      labels = TABLE(_style="width: 100%;",_cellpadding="0px;", _cellspacing="0px;")
      ridlen = len(str(report["reportkey"]).split("_"))
      for message in ui_message:
        labels.append(TR(
                         TD(DIV(str(message["secname"]).split("_")[ridlen],_class="label"),_style="padding-right:10px;"),
                         TD(DIV(message["fieldname"],_class="label"),_style="padding-right:10px;"),
                         TD(INPUT(_name=message["id"], _type="text", _value=message["msg"],_style="width: 100%;"),_style="width: 100%;")))
    
  else:
    response.flash = str(ns.error_message)
      
  return dict(labels=labels, tmp_view=tmp_view, tmp_edit=tmp_edit)

@auth.requires(session.alias=='nas_admin', requires_login=True)
def reports():
  response.subtitle = T("Report templates")
  response.view='nas/reports.html'
  response.cmd_back = ui.control.get_mobil_button(label=T("Account"), href=URL("account",**{'user_signature': True}),
        icon="back", ajax="false", theme="a", mini="true")
  nas_reports= ntool.getReportFiles(os.path.join(ns.request.folder,'static/resources/report'))
  frm_filter = SQLFORM.factory(
    Field('database', db.databases, requires = IS_IN_DB(db((db.databases.deleted==False)), 
      db.databases.id, '%(alias)s'), label=T('Database')),
    Field('reptype', "string", label=T('Rep.type'), 
      requires = IS_EMPTY_OR(IS_IN_SET(nas_reports["types"]))),
    Field('label', "string", label=T('Group'), 
      requires = IS_EMPTY_OR(IS_IN_SET(nas_reports["labels"]))),
    Field('repname', type='string', length=50, label=T('Name/Description')),
    Field('install', type='boolean', label=T('Installed')),
    submit_button=T("Load"), table_name="filter", _id="frm_filter"
  )
  
  if request.post_vars.has_key("report_labels"):
    if ns.local.setEngine(database=db.databases(id=request.post_vars["database"]).alias, check_ndi=False, created=False, createdb=False):
      for label_id in request.post_vars.keys():
        if label_id not in("report_labels","database"):
          row_id = ns.connect.updateData("ui_message", 
                     values={"id":label_id,"msg":request.post_vars[label_id]}, validate=False, insert_row=False)
          if not row_id:
            response.flash = str(ns.error_message)
      ns.db.commit()
      if session.frm_filter:
        frm_filter.vars = session.frm_filter
    else:
      response.flash = str(ns.error_message)
      
  if request.post_vars.has_key("ins_cmd"):
    if ns.local.setEngine(database=db.databases(id=request.post_vars["ins_database"]).alias, check_ndi=False, created=False, createdb=False):
      if request.post_vars["ins_cmd"]=="delete":
        try:
          report_id = ns.db.ui_report(reportkey=request.post_vars["ins_reportkey"])["id"]
          ns.db(ns.db.ui_reportfields.report_id==report_id).delete()
          ns.db(ns.db.ui_reportsources.report_id==report_id).delete()
          ns.db((ns.db.ui_message.secname.like(request.post_vars["ins_reportkey"]+"%"))).delete()
          ns.db(ns.db.ui_report.id==report_id).delete()
          ns.db.commit()
        except Exception, err:
          response.flash = str(err)
      else:
        load = dbtool.loadReport(fileName=request.post_vars["ins_reportkey"]+".xml")
        if load != "OK":
          response.flash = load
      if session.frm_filter:
        frm_filter.vars = session.frm_filter
    else:
      response.flash = str(ns.error_message)
  
  flash=response.flash
  frm_filter.process(keepvalues=True,onfailure=None)
  frm_filter.errors.clear()
  response.flash = flash
  frm_filter.custom.submit = ui.control.get_mobil_button(label=T("Search"), href="#", 
        cformat=None, style="text-align: left;", icon="search", ajax="false", theme="a",
        onclick= "document.forms['frm_filter'].submit();", cmd_id="filter_submit")
  frm_filter.custom.widget.repname["_onkeydown"]="if (event.keyCode == 13) document.getElementById('filter_submit').click()"
  if not request.post_vars.has_key("ins_cmd"):
    session.frm_filter = frm_filter.vars
      
  dbs_reports=None
  if frm_filter.vars.database and frm_filter.vars.database!="":
    if ns.local.setEngine(database=db.databases(id=frm_filter.vars.database).alias, check_ndi=False, created=False, createdb=False):
      query = (ns.db.ui_report.id>0) 
      dbs_reports = []
      if frm_filter.vars.repname and frm_filter.vars.repname!="":
        query = query & ((ns.db.ui_report.repname.lower().like("%"+str(request.post_vars.repname).lower()+"%"))|
                         (ns.db.ui_report.description.lower().like("%"+str(request.post_vars.repname).lower()+"%")))
      if frm_filter.vars.label and frm_filter.vars.label!="":
        groups_id=ns.valid.get_groups_id('nervatype', frm_filter.vars.label)
        if groups_id:
          query = query & ((ns.db.ui_report.nervatype==groups_id))
        else:
          query = query & ((ns.db.ui_report.transtype==ns.valid.get_groups_id('transtype', frm_filter.vars.label)))
      reportkey_rows = ns.db(query).select(ns.db.ui_report.reportkey,orderby=ns.db.ui_report.repname)
      [dbs_reports.append(row.reportkey) for row in reportkey_rows]
    else:
      response.flash = str(ns.error_message)
  
  htmltable = TABLE(THEAD(TR(TH(),TH(),TH(),TH(T("Name")+"/"+T("Description")))))
  tbody = TBODY()
  numrec=0
  for row in nas_reports["reports"]:
    cmd_edit = INPUT(_value=T("Edit template"), _disabled="", _type="button")
    def filter_row():
      if frm_filter.vars.repname and frm_filter.vars.repname!="":
        if str(row["repname"].lower()).find(frm_filter.vars.repname.lower())==-1 and str(row["description"].lower()).find(frm_filter.vars.repname.lower())==-1:
          return False
      if frm_filter.vars.label and frm_filter.vars.label!="":
        if str(row["label"]).find(frm_filter.vars.label)==-1:
          return False
      if frm_filter.vars.reptype and frm_filter.vars.reptype!="":
        if str(row["reptype"]).find(frm_filter.vars.reptype)==-1:
          return False
      return True
    if filter_row():
      numrec+=1
      if not row.has_key("preview"):
        cmd_preview = INPUT(_value=T("Preview"), _disabled="", _type="button")
      else:
        cmd_preview = create_preview_img("button",row["preview"],row["repname"])
      if dbs_reports==None:
        cmd_install = INPUT(_value=T("Install"), _disabled="", _type="button")
      else:
        try:
          dbs_reports.index(row["reportkey"])
          dbs_reports.remove(row["reportkey"])
          cmd_install = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="delete", 
                title=T("Delete from the database..."), style="color:#FF7F50;", theme="b", 
                onclick="document.getElementById('ins_cmd').value='delete';document.getElementById('ins_reportkey').value='"
                +row["reportkey"]+"';document.getElementById('ins_database').value='"+str(frm_filter.vars.database)
                +"';document.forms['frm_install'].submit();")
          if len(ns.db((ns.db.ui_message.secname.like(row["reportkey"]+"%"))).select())>0:
            cmd_edit = ui.control.get_mobil_button(T("Edit template"), 
              href=URL("report_template",vars={"database":frm_filter.vars.database,"reportkey":row["reportkey"]}
                       ,**{'user_signature': True}), 
              cformat=None, icon="edit", 
              title=T('Edit report template'), theme="a")
        except Exception:
          cmd_install = ui.control.get_mobil_button(T("Install"), href="#", cformat=None, icon="plus", 
                title=T("Install to the database..."), style="color:#8FBC8F;", theme="b",
                onclick="document.getElementById('ins_cmd').value='install';document.getElementById('ins_reportkey').value='"
                +row["reportkey"]+"';document.getElementById('ins_database').value='"+str(frm_filter.vars.database)
                +"';document.forms['frm_install'].submit();")
      tbody.append(
        TR(TD(cmd_install), TD(cmd_preview), TD(cmd_edit), TD(SPAN(row["repname"],_style="font-weight: bold;"),BR(),row["description"])))
    else:
      try:
        dbs_reports.remove(row["reportkey"])
      except Exception:
        pass
  if dbs_reports:
    for reportkey in dbs_reports:
      cmd_preview = INPUT(_value=T("Preview"), _disabled="", _type="button")
      cmd_install = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="delete", 
                title=T("Delete from the database..."), style="color:#FF7F50;", theme="b",
                onclick="document.getElementById('ins_cmd').value='delete';document.getElementById('ins_reportkey').value='"
              +reportkey+"';document.getElementById('ins_database').value='"+str(frm_filter.vars.database)
              +"';document.forms['frm_install'].submit();")
      report = ns.db.ui_report(reportkey=reportkey)
      if len(ns.db((ns.db.ui_message.secname.like(reportkey+"%"))).select())>0:
        cmd_edit = ui.control.get_mobil_button(T("Edit template"), target="blank", 
              href=URL("report_template",vars={"database":frm_filter.vars.database,"reportkey":reportkey},
                       **{'user_signature': True}), cformat=None, icon="edit", 
              title=T('Edit report template'), theme="a")
      else:
        cmd_edit = INPUT(_value=T("Edit template"), _disabled="", _type="button")
      tbody.append(
        TR(TD(cmd_install), TD(cmd_preview), TD(cmd_edit), TD(SPAN(report["repname"],_style="font-weight: bold;"),BR(),report["description"])))
  htmltable.append(tbody)
  ui.control.set_htmltable_style(htmltable,"tbl_reports","0,1,2",columntoggle=False)
  
  return dict(form=frm_filter, repgrid=htmltable)

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
          icon="back", cformat=None, ajax="false", theme="b", style="width: 100px;")
  else:
    response.cmd_new = ui.control.get_mobil_button(label=T("New"), 
          href=URL("databases/new/databases",**{'user_signature': True}),
          icon="plus", cformat=None, ajax="false", theme="b", style="width: 100px;")
  
  fields = (db.databases.id, db.databases.alias, db.databases.host, 
            db.databases.dbname)
  query = ((db.databases.deleted==False))
  
  if _editable:
    db.databases.alias.represent = lambda value,row: ui.control.get_mobil_button(value, 
        href=URL("databases/edit/databases/"+str(row["id"]),**{'user_signature': True}), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    db.databases.id.label=T("Delete")
    db.databases.id.represent = lambda value,row: ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, 
          icon="delete", iconpos="notext", ajax="false", theme="b",
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
               P(SPAN(T('Starting the process?'), _id="msg_result",_style="font-style: italic;"),
                 ui.control.get_mobil_button(label=T("Start"), href="#", onclick="createDatabase();", 
                 cformat=None, icon="check", theme="b", style="width: 100px;"),
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
              SPAN(T('Settings objects: '), _style="color:green;"),SPAN("ui_audit, ui_language, \
                ui_menu, ui_menufields, ui_message, ui_report, ui_reportfields, \
                ui_reportsources, ui_userconfig"),BR(),
              SPAN(T('Not included: '), _style="color:red;"),SPAN("ui_printqueue"),BR(),BR(),
              SPAN(T("Independent from the database type and version of the NAS server."),_style="font-style: italic;")),
             DIV(
               DIV(SPAN(T('Database alias:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_alias),
               DIV(SPAN(T('Filename:') ,_style="padding-right: 15px;padding-left: 15px;"),cmb_filename, SPAN(" "),
               cust_filename, _style="padding-top: 10px;"), 
               DIV(SPAN(T('Backup format:'),_style="padding-right: 15px;padding-left: 15px;"),cmb_format, _style="padding-top: 10px;"),
             P(
                SPAN(T('Starting the process?'), _id="msg_result",_style="font-style: italic;"),
                ui.control.get_mobil_button(label=T("Start"), href="#", onclick="createDataBackup();", 
                  cformat=None, icon="check", theme="b", style="width: 100px;",
                  title=ns.T('Start customer backup creation')),
               _style="padding-top: 5px;")),
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
  cmd_filename["_data-theme"] = "b"
  cmd_filename["_data-icon"] = "check"
  cmd_file=INPUT(_type="submit",_name="frm_file", _title= ns.T('Upload file and Start restore'),
    _value=T("Upload and Start restore"),
    _onclick="msg_result.innerHTML='"+T("Process started. Waiting for the server to respond ...")+"';")
  cmd_file["_data-theme"] = "b"
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
      cformat=None, icon="back", ajax="false", theme="b", style="width: 100px;")
  else:
    response.cmd_new = ui.control.get_mobil_button(label=T("New"), 
      href=URL("settings/new/settings",**{'user_signature': True}),
      cformat=None, icon="back", ajax="false", theme="b", style="width: 100px;")
    
  fields = (db.settings.id, db.settings.fieldname, db.settings.value, 
            db.settings.description)
  
  if _editable:
    db.settings.fieldname.represent = lambda value,row: ui.control.get_mobil_button(value, 
        href=URL("settings/edit/settings/"+str(row["id"]),**{'user_signature': True}), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    db.settings.id.label=T("Delete")
    db.settings.id.represent = lambda value,row: ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, 
          icon="delete", iconpos="notext", ajax="false", theme="b",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this object?")
            +"')){ajax('"+URL('settings/delete/settings'+"/"+str(row["id"]),**{'user_signature': True})
            +"',[],'');jQuery(this).closest('tr').remove();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}")
  else:
    db.settings.id.readable = db.settings.id.writable = False
  
  gform = ui.control.get_form(query=db.settings,field_id=db.settings.id,orderby=db.settings.fieldname,
                   fields=fields,headers={},frm_type=frm_type,priority="0,1,2",create=_editable)
  return dict(form=gform)
