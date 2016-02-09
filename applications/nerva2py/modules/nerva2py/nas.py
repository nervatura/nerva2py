# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2015, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

from gluon.html import URL, CENTER, HTML, TITLE, BODY, LINK, HEAD
from gluon.sqlhtml import SQLFORM, DIV, SPAN, IMG, A
from gluon.html import TABLE, TR, TD
from gluon.tools import Auth
from gluon.validators import IS_NOT_EMPTY
from gluon.sql import Field

class AdminUiConnect(object):
  
  def __init__(self, ui):
    self.ui = ui
  
  def auth_ini(self, controller,use_username=True,reset_password=False,register=False):
    self.auth = Auth(self.ui.db, controller=controller, function="login")
    self.auth.settings.extra_fields[self.auth.settings.table_user_name]= [
      Field('agree','boolean', default=True,
        label='I agree to the Terms and Conditions',
        requires=IS_NOT_EMPTY(error_message='You must agree this!'))
    ]
    self.auth.define_tables(username=use_username, migrate=False, fake_migrate=False)
    self.auth.settings.remember_me_form = False
    self.auth.settings.reset_password_requires_verification = True
    if not reset_password:
      self.auth.settings.actions_disabled.append('request_reset_password')
    if not register:
      self.auth.settings.actions_disabled.append('register')
    self.auth.settings.register_next = URL('index',**{'user_signature': True})
    self.auth.settings.change_password_next = URL('index',**{'user_signature': True})
    self.auth.settings.formstyle = 'table3cols'
    self.auth.settings.allow_basic_login=True
    self.auth.settings.login_onaccept.append(self.login_onaccept)
    return self.auth
  
  def check_alias(self,alias):
    import re
    return re.sub(r'[^a-zA-Z0-9_]','', alias)
  
  def delete_data(self, table, ref_id=None, log_enabled=True):
    try:
      if self.ui.db[table].has_key("deleted"):
        self.ui.db(self.ui.db[table]["id"]==ref_id).update(**{"deleted":True})
      else:
        self.ui.db(self.ui.db[table].id==ref_id).delete()
      if log_enabled and self.ui.db.has_key("auth_event"):
        values={"time_stamp":self.ui.request.now, "client_ip":self.ui.request.client,
                "user_id":self.ui.session.auth.user.id, "origin":self.auth.settings.controller, 
                "description":"User "+str(self.ui.session.auth.user.id)+" deleted ("+str(table)+")"}
        self.ui.db.auth_event.insert(**values)
      self.ui.db.commit()
      return True
    except Exception, err:
      self.error_message = str(err)
      return False
      
  def login_onaccept(self, form):
    self.ui.session.alias=self.ui.alias
            
  def show_disabled(self,title):
    return HTML(HEAD(TITLE(title),
                   LINK(_rel="shortcut icon", _href=URL('static','favicon.ico'), _type="image/x-icon")),
              BODY(DIV(CENTER(TABLE(TR(TD(IMG(_src=URL('static','images/dataprotection_min.jpg'),
                                      _style="border: solid;border-color: #FFFFFF;"),
                            _style="text-align: center;vertical-align: middle;font-weight: bold;font-family: Arial, Helvetica,  sans-serif;font-size: 20px;")),
                      _style="background-color:#FFFFFF;color:#444444;margin-top:30px;")),_style="width:100%;height:100%;")),_style="background-color:#879FB7;")
    
  def update_data(self, table, values, log_enabled=True, validate=True):
    try:
      ref_id=None
      if values.has_key("id"):
        if values["id"]:
          ref_id = values["id"]
        del values["id"]
      if not ref_id:
        if validate:
          ret = self.ui.db[table].validate_and_insert(**values)
          if ret.errors:
            return {"id":None,"error":str(ret.errors.keys()[0])+": "+str(ret.errors.values()[0])}
          else:
            ref_id = ret.id
        else:
          try:
            ref_id = self.ui.db[table].insert(**values)
          except Exception, err:
            return {"id":None,"error":str(err)}
      else:
        if validate:
          ret = self.ui.db(self.ui.db[table].id==ref_id).validate_and_update(**values)
          if ret.errors:
            return {"id":None,"error":str(ret.errors.keys()[0])+": "+str(ret.errors.values()[0])}
        else:
          try:
            self.ui.db(self.ui.db[table].id==ref_id).update(**values)
          except Exception, err:
            return {"id":None,"error":str(err)}
    except Exception, err:
      return {"id":None,"error":str(err)}
    
    if log_enabled and self.ui.db.has_key("auth_event"):
      values={"time_stamp":self.ui.request.now, "client_ip":self.ui.request.client,
              "user_id":self.ui.session.auth.user.id, "origin":self.auth.settings.controller, 
              "description":"User "+str(self.ui.session.auth.user.id)+" updated ("+str(table)+")"}
      self.ui.db.auth_event.insert(**values)
    self.ui.db.commit()
    return {"id":ref_id,"error":None}
  
class AdminUiControl(object):
  
  def __init__(self, ui):
    self.ui = ui
  
  def create_cmd(self,response,T,theme="a"):
    response.cmd_menu = self.get_mobil_button(label=T("MENU"), href="#main-menu", style="color: #FFD700;",
                          icon="bars", cformat="ui-btn-left", ajax="true", iconpos="left", theme=theme, mini="true")
    response.cmd_exit = self.get_mobil_button(label=T("EXIT"), href=URL("logout",**{'user_signature': True}),
                          icon="power", cformat="ui-btn-right", ajax="false", iconpos="left",
                          style="color: red;margin:2px;", theme=theme, mini="true")
    response.cmd_home = self.get_mobil_button(label=T("HOME"), href=URL('index',**{'user_signature': True}),
                          icon="home", cformat="ui-btn-left", ajax="false", iconpos="left", theme=theme, mini="true")
    response.cmd_close = self.get_mobil_button(label=T("Close"), href="#",
                          icon="delete", cformat="ui-btn-right", ajax="true", iconpos="notext", rel="close")
  
  def get_form(self, query,field_id,orderby,fields=None,headers={},frm_type="view",priority="0,1",create=True):
    gform = SQLFORM.grid(query=query, field_id=field_id, fields=fields, headers=headers, 
                         orderby=orderby, paginate=20, maxtextlength=25,
                         searchable=False, csv=False, details=False, showbuttontext=False,
                         create=create, deletable=False, editable=True, selectable=False,
                         ignore_common_filters=False)
    if type(gform[1][0][0]).__name__!="TABLE":
      if frm_type in ("edit","new"):
        gform = self.set_input_form(gform)
        if frm_type == "edit":
          gform[1][0][0] = ""
    else:
      htable = gform.elements("div.web2py_htmltable")
      if len(htable)>0:
        self.set_htmltable_style(htable[0][0],"form_search",priority)
        htable[0][0]["_width"]="100%"
    counter = gform.elements("div.web2py_counter")
    if len(counter)>0:
      if counter[0][0]==None:
        counter[0][0] = ""
    if gform[len(gform)-1]["_class"].startswith("web2py_paginator"):
      pages = gform[len(gform)-1].elements("a")
      for i in range(len(pages)):
        pages[i]["_data-ajax"] = "false"
    return gform

  def get_frm_type(self, ruri):
    if ruri.find("/edit/")>0:
      return "edit"
    elif ruri.find("/new/")>0:
      return "new"
    elif ruri.find("/delete/")>0:
      return "delete"
    else:
      return "view"
  
  def get_mobil_button(self, label, href, icon="forward", cformat="ui-btn-right", ajax="true", iconpos="left", 
                       rel=None, target=None, style=None, onclick=None, theme=None, cmd_id=None,mini=None,
                       transition=None, position=None, title=None):
    cmd = A(SPAN(label), _href=href, _class=cformat)
    cmd["_data-role"] = "button"
    cmd["_data-icon"] = icon
    cmd["_data-ajax"] = ajax
    cmd["_data-iconpos"] = iconpos
    if title: cmd["_title"] = title
    if cformat: cmd["_class"] = cformat
    if rel: cmd["_data-rel"] = rel
    if target: cmd["_target"] ="_blank"
    if style: cmd["_style"] = style
    if onclick: cmd["_onclick"] = onclick
    if theme: cmd["_data-theme"] = theme
    if cmd_id: cmd["_id"] = cmd_id
    if mini: cmd["_data-mini"] = mini
    if transition: cmd["_data-transition"] = transition
    if position: cmd["_data-position-to"] = position
    return cmd

  def set_htmltable_style(self, table, tbl_id=None, priority="0", columntoggle=True):
    table["_data-role"] = "table"
    if tbl_id:
      table["_id"] = tbl_id
    table["_class"] = "ui-body-d ui-shadow table-stripe ui-responsive"
    table["_data-column-btn-theme"] = "b"
    if columntoggle:
      table["_data-mode"] = "columntoggle"
      table["_data-column-btn-text"] = "Columns to display..."
      table["_data-column-popup-theme"] = "b"
    thead = table.elements("thead")
    if len(thead)>0:
      head = thead[0][0]
    else:
      colgroup = table.elements("col")
      if len(colgroup)==0:    
        head = table[0][0]
      else:
        head = table[1][0]
    head["_class"] = "ui-bar-d"
    pnum=1
    for i in range(len(head)):
      if len(head[i])>0:
        try:
          str(priority).split(",").index(str(i))
        except Exception:
          head[i]["_data-priority"] = pnum
          pnum+=1
  
  def set_input_form(self, form, submit_label="Save", theme="b"):
    form["_id"]="frm_input"
    form["_data-ajax"]="false"
    text_inputs = form.elements('input',_type='text')
    for i in range(len(text_inputs)):
      text_inputs[i]["_onkeydown"]="if (event.keyCode == 13) document.forms['frm_input'].submit();"
    text_inputs = form.elements('input',_type='password')
    for i in range(len(text_inputs)):
      text_inputs[i]["_onkeydown"]="if (event.keyCode == 13) document.forms['frm_input'].submit();"
    submit_row = form.element("#submit_record__row")
    submit_row[1][0] = self.get_mobil_button(label=submit_label, href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="false", theme=theme,
          onclick= "document.forms[0].submit();")
    return form
    
class AdminUi(object):
  control = AdminUiControl(None)
  connect = AdminUiConnect(None)
  
  def __init__(self, alias, request, session, db):
    self.alias = alias
    self.request = request
    self.session = session
    self.db = db
    self.control = AdminUiControl(self)
    self.connect = AdminUiConnect(self)



