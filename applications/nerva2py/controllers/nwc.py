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
  from gluon.globals import Session
  global session; session = Session()
  global response; response = globals.Response()
  import gluon.languages.translator as T
  from gluon.sql import DAL
  global db; db = DAL()

from gluon.html import URL
from gluon.http import redirect
from gluon.tools import Auth
from gluon.sql import Field
from gluon.validators import IS_IN_DB, IS_NOT_EMPTY, IS_IN_SET, IS_EMPTY_OR
from gluon.html import INPUT, CENTER, HTML, TITLE, BODY, LINK, HEAD, H1, UL, LI, H3, P, STRONG
from gluon.sqlhtml import SQLFORM, DIV, SPAN, IMG, A
from gluon.html import SELECT, OPTION, XML
from gluon.html import TABLE, TR, TD, TBODY, THEAD, TH
from gluon.utils import web2py_uuid
import gluon.contrib.simplejson as json

from gluon.storage import Storage

from nerva2py.nervastore import NervaStore
from nerva2py.tools import auth_ini
from nerva2py.simplegrid import SimpleGrid
from nerva2py.te import JqueryTeWidget
from nerva2py.nwc import WebUi

import os, datetime, math, base64, re

DEMO_MODE = False
ns = NervaStore(request,session,T,db)
ui = WebUi(ns,response,"nerva2py","nwc")

ns_auth=auth_ini(session,URL('frm_login'))
if session.alias!=None:
  if session.auth:
    if getattr(session.auth.user, "alias",None) != session.alias:
      session.alias=None
      redirect(URL('frm_login'))
  if ns.local.setEngine(session.alias):
    response.alias = session.alias
    ns_auth = Auth(ns.db, hmac_key=Auth.get_or_create_key(), controller=ui.controller, function="frm_login")
    ns_auth.define_tables(username=True, migrate=False, fake_migrate=False)
    if session.auth!=None:
      session.auth.user.alias = session.alias
      response.username = session.auth.user.username
      if session.auth.user.username=="demo" and session.alias=="demo":
        DEMO_MODE = True
  ui.menu.create_menu()
        
@ns_auth.requires_login()
def index():
  response.view=ui.dir_view+'/index.html'
  response.footer_enabled = True
  if session.mobile:
    response.title=T("Nervatura Mobile")
  else:
    if session.welcome==True:
      session.welcome=False
      response.flash = T('Welcome to Nervatura Web Client!')
    response.subtitle=T('START PAGE')
    response.titleicon = URL(ui.dir_images,'icon16_home.png')
  return dict()

def frm_login():
  response.view=ui.dir_view+'/login.html'
  if request.vars.has_key("alias"):
    last_alias = request.vars["alias"]
  elif request.cookies.has_key('last_alias'):
    last_alias = request.cookies['last_alias'].value
  elif DEMO_MODE:
    last_alias = "demo"
  else:
    last_alias = ""
  if request.vars.has_key("user"):
    last_username = request.vars["user"]
  elif request.cookies.has_key('last_username'):
    last_username = request.cookies['last_username'].value
  elif DEMO_MODE:
    last_username = "demo"
  else:
    last_username = ""
  form = SQLFORM.factory(
    Field('alias', type='string', length=50, requires=IS_NOT_EMPTY(), label=T('Database'), default=last_alias),
    Field('username', type='string', length=50, requires=IS_NOT_EMPTY(), label=T('Username'), default=last_username),
    Field('password', type='password', length=50, label=T('Password')),
    submit_button=T("Login"), table_name="login", _id="frm_login", **{"_data-ajax":"false"}
  )
  if session.mobile:
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=login'),
                                             icon="info", iconpos="notext", target="blank")
    response.cmd_desktop = ui.control.get_mobil_button(label=T("Desktop"), href=URL("index",vars={"desktop":"true"}),
                                             icon="calendar", iconpos="notext", title=T('Nervatura Web Client'), ajax="false")
    form.custom.submit = ui.control.get_mobil_button(label=T("Login"), href="#", 
        cformat=None, style="text-align: center;width: 60%;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_login'].submit();")
  else:
    response.cmd_help =A(SPAN(XML("&nbsp;")),IMG(_src=URL(ui.dir_images, 'icon16_help.png'),_style="padding-top:2px;"),
                         SPAN(XML("&nbsp;")), 
                         _style="padding-top:3px;padding-bottom:2px;", 
                         _target="_blank", _class="w2p_trap buttontext button", _href=URL('cmd_go_help?page=login'), 
                         _title=T('Help'))
    response.cmd_mobil = A(IMG(_src=URL(ui.dir_images, 'icon16_phone.png'),_style="padding-top:2px;"),
                           SPAN(T("Mobile"),_style="font-weight: bold;"), 
                           _style="padding-top:3px;padding-bottom:2px;", 
                           _class="w2p_trap buttontext button", _href=URL("index",vars={"mobile":"true"}), 
                           _title=T('Nervatura Mobile Client'), _onclick="#")
    form.custom.submit = A(SPAN(_class="icon lock"),
                           SPAN(T("Login"),_style="font-weight: bold;"), 
                           _style="padding:5px;width:120px;", 
                           _class="w2p_trap buttontext button", _href="#", 
                           _title=T('Nervatura Login'), _onclick="document.forms['frm_login'].submit();")
  #Opera and IE hack
  if request.vars.has_key("alias") and request.vars.has_key("username") and request.vars.has_key("password") and not request.vars.has_key("_formname"):
    request.vars["_formname"] = "login/create"
  if form.accepts(request.vars) and session.nas_login==None:
    if ns.local.setEngine(form.vars.alias):
      session.alias = form.vars.alias
      ns_auth = Auth(ns.db, hmac_key=Auth.get_or_create_key(), controller=ui.controller, function="frm_login")
      
      ns_auth.settings.table_user_name = 'employee'
      ns_auth.settings.login_next = URL('index')
      ns_auth.settings.logout_next = URL('frm_login')
      ns_auth.settings.login_methods = [ui.login_methods]
      
      ns_auth.settings.expiration = 3600  # seconds
      ns_auth.settings.long_expiration = 3600*24*30 # one month
  
      ns_auth.define_tables(username=True, migrate=False, fake_migrate=False)
      
      if form.vars.password=="":
        form.vars.password=None
      if ns.connect.setLogin(form.vars.username, form.vars.password):
        ns_auth.user = Storage({"id":ns.employee["id"], "username":ns.employee["username"], 
                                "password":ns.employee["password"], "alias":session.alias})
        session.auth = Storage(user=ns_auth.user, last_visit=request.now,
                               expiration=ns_auth.settings.expiration,
                               hmac_key = web2py_uuid())
        session.welcome=True
        response.cookies['last_alias'] = form.vars.alias
        #response.cookies['last_alias']['expires'] = 24 * 3600
        response.cookies['last_alias']['path'] = '/'
        response.cookies['last_username'] = form.vars.username
        response.cookies['last_username']['path'] = '/'
        ns.connect.insertLog("login")
        ui.nwc_ini()
        redirect(URL('index'))
      else:
        response.flash = str(ns.error_message)
        
    else:
      response.flash = str(ns.error_message)
  elif session.nas_login!=None:
    response.flash = T("The NWC and NAS at the same time can not be logged in!")
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  return dict(form=form)

def frm_logout():
  session.alias=None
  mobile = session.mobile
  try:
    ns_auth.logout(next=URL('frm_login'),log=None)
    session.mobile = mobile
    redirect(URL('frm_login'))
  except Exception:
    session.mobile = mobile
    redirect(URL('frm_login'))
    
@ns_auth.requires_login()
def cmd_add_queue():
  if request.vars.qty=="":
    copy=1
  else:
    copy=request.vars.qty
  values = {"nervatype":request.vars.nervatype, "ref_id":request.vars.ref_id, "qty":copy, 
            "employee_id":session.auth.user.id, "report_id":request.vars.template, "crdate":datetime.datetime.now().date()}
  ns.connect.updateData("ui_printqueue", values=values, validate=False, insert_row=True)

def cmd_export_ical():
  response.headers['Content-Type'] = "text/ics"
  response.headers['Content-Disposition'] = 'attachment;filename="NervaturaEvents.ics"'
  return ui.dbout.exportToICalendar(request.vars.id)

@ns_auth.requires_login()
def cmd_get_formula():
  if request.vars.production_id:
    production = ns.db.trans(id=request.vars.production_id)
    production_qty = ns.db((ns.db.movement.trans_id==production.id)&(ns.db.movement.shared==1)&(ns.db.movement.deleted==0)).select()[0].qty
  else:
    return T("Missing production!")
  if request.vars.formula_id:
    formula = ns.db.trans(id=request.vars.formula_id)
    movetype_head = ns.valid.get_groups_id("movetype", "head")
    movetype_plan = ns.valid.get_groups_id("movetype", "plan")
    formula_qty = ns.db((ns.db.movement.trans_id==formula.id)&(ns.db.movement.movetype==movetype_head)
                        &(ns.db.movement.deleted==0)).select()[0].qty
    items = ns.db((ns.db.movement.trans_id==formula.id)&(ns.db.movement.deleted==0)
                  &(ns.db.movement.movetype==movetype_plan)).select()
  else:
    return T("Missing formula!")
  movetype_inventory = ns.valid.get_groups_id("movetype", "inventory")
  movements = ns.db((ns.db.movement.trans_id==production.id)&(ns.db.movement.shared==0)).select(ns.db.movement.id)
  for movement in movements:
    ns.connect.deleteData("movement", ref_id=movement.id)          
  for item in items:
    if item.shared==1:
      qty = -math.ceil(production_qty/formula_qty)
    else:
      qty = -(production_qty/formula_qty)*item.qty
    if item.place_id:
      place_id=item.place_id
    else:
      place_id=production.place_id
    values = {"trans_id":production.id,"shippingdate":production.transdate,"movetype":movetype_inventory, 
              "product_id":item.product_id, "qty":qty,"place_id":place_id}
    ns.connect.updateData("movement", values=values, validate=False, insert_row=True)  
  return "OK"

@ns_auth.requires_login()
def cmd_get_price():
  if request.vars.has_key("trans_id") and request.vars.has_key("product_id"):
    trans = ns.db(ns.db.trans.id==request.vars.trans_id).select().as_list()
    if len(trans)>0:
      params = {}
      params["product_id"]=request.vars.product_id
      trans = trans[0]
      direction = ns.db.groups(id=ns.db.trans(id=trans["id"]).direction).groupvalue
      if direction=="out":
        params["vendorprice"]=0
      else:
        params["vendorprice"]=1
      params["posdate"]=trans["transdate"]
      params["curr"]=trans["curr"]
      params["customer_id"]=trans["customer_id"]
      if request.vars.has_key("qty"):
        params["qty"]=request.vars.qty
      else:
        params["qty"]=1
      return ui.tool.getPriceValueDal(params)
    else:    
      return 0
  else:
    return 0

@ns_auth.requires_login()
def cmd_get_report():
  ruri = request.wsgi.environ["REQUEST_URI"]
  formkey = ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1]
  if session[formkey]:
    return ui.report.show_report(session[formkey].params["output"],
                                 ui.dbout.getReport(session[formkey].params,session[formkey].filters))
  else:
    return HTML(HEAD(TITLE(response.title),
                   LINK(_rel="shortcut icon", _href=URL('static','favicon.ico'), _type="image/x-icon")),
              BODY(DIV(CENTER(TABLE(TR(TD(IMG(_src=URL('static','images/nodata.png'),
                                      _style="border: solid;border-color: #FFFFFF;"),
                            _style="text-align: center;vertical-align: middle;font-weight: bold;font-family: Arial, Helvetica,  sans-serif;font-size: 20px;")),
                      _style="background-color:#FFFFFF;color:#444444;margin-top:200px;")),
                       _style="width:100%;height:100%")),_style="background-color:#000000;")

def cmd_go_help():
  if DEMO_MODE:
    redirect("http://www.nervatura.com")
  elif request.vars.page:
    lang = session._language if session._language else "en"
    file_name = os.path.join(request.folder, ui.dir_help, lang, str(request.vars.page)+'.html')
    if not os.path.isfile(file_name):
      file_name = os.path.join(request.folder, ui.dir_help, lang, 'index.html')
      if not os.path.isfile(file_name):
        file_name = os.path.join(request.folder, ui.dir_help, 'en', 'index.html')
        if not os.path.isfile(file_name):
          return "Missing index file!"
    response.view=file_name
    response.title = T("Nervatura Web Client")
    response.subtitle = "Ver.No: "+response.verNo
    return dict()
  else:
    return "Missing page parameter!"

@ns_auth.requires_login()
def cmd_trans_cancel():
  if request.vars.trans_id:
    try:
      return ui.connect.create_trans(request.vars.trans_id,"cancellation")
    except Exception, err:
      return "err|-1|"+str(err)
  else:
    return "err|-1|"+T("Missing trans id!")
  
@ns_auth.requires_login()
def cmd_trans_copy():
  if request.vars.trans_id:
    try:
      return ui.connect.create_trans(request.vars.trans_id)
    except Exception, err:
      return "err|-1|"+str(err)
  else:
    return "err|-1|"+T("Missing trans id!")

@ns_auth.requires_login()
def cmd_trans_corr():
  if request.vars.trans_id:
    try:
      return ui.connect.create_trans(request.vars.trans_id,"amendment")
    except Exception, err:
      return "err|-1|"+str(err)
  else:
    return "err|-1|"+T("Missing trans id!")

@ns_auth.requires_login()
def dlg_create():
  if request.vars.trans_id and request.vars.new_transtype and request.vars.new_direction and request.vars.from_inventory and request.vars.netto_qty:
    try:
      _from_inventory = (request.vars.from_inventory=='1')
      _netto_qty = (request.vars.netto_qty=='1')
      return ui.connect.create_trans(request.vars.trans_id,transcast="normal",new_transtype=request.vars.new_transtype,
                          new_direction=request.vars.new_direction,from_inventory=_from_inventory,netto_qty=_netto_qty)
    except Exception, err:
      return "err|-1|"+str(err)
  else:
    return "err|-1|"+T("Missing parameters!")

@ns_auth.requires_login()
def dlg_customer():
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.custtype!=ns.valid.get_groups_id("custtype", "own")))
  if session.mobile:
    fields = [ns.db.customer.id, ns.db.customer.custnumber, ns.db.customer.custname]
    ns.db.customer.id.label = T('Select')  
    ns.db.customer.id.represent = lambda value,row: ui.control.get_select_button(onclick='set_customer_value("'+str(row.id)+'", "'+str(row.custnumber)+'", "'+str(row.custname)+'")')
    ns.db.customer.custname.represent = lambda value,row: A(SPAN(value),
                     _href=URL(r=request, f="frm_customer/view/customer/"+str(row.id)), _target="_blank")
    left,links=None,None
  else:
    nervatype_customer = ns.valid.get_groups_id("nervatype", "customer")  
    primary_address = ((ns.db.address.id.belongs(ns.db((ns.db.address.deleted==0)&(ns.db.address.nervatype==nervatype_customer)).select(ns.db.address.id.min().with_alias('id'), groupby=ns.db.address.ref_id))))
    fields = [ns.db.customer.id, ns.db.customer.custnumber, ns.db.customer.custname, ns.db.address.city, ns.db.address.street]
    left = (ns.db.address.on((ns.db.customer.id==ns.db.address.ref_id) & primary_address))
    links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href="#", _title=T("Select Item"), 
                         _onclick='set_customer_value("'+str(row.customer.id)+'", "'+
                         str(row.customer.custnumber)+'", "'+str(row.customer.custname)+'");jQuery(this).parents(".ui-dialog-content").dialog("close");return true;')]
  return DIV(ui.select.find_data("customer",query,fields,ns.db.customer.custname,10,25,links,left), _id="dlg_filter")

@ns_auth.requires_login()
def dlg_employee():
  query = ((ns.db.employee.deleted==0)&(ns.db.employee.usergroup==ns.db.groups.id))
  left = None
  if session.mobile:
    fields = [ns.db.employee.id, ns.db.employee.empnumber, ns.db.groups.groupvalue, ns.db.employee.username]
    ns.db.employee.id.label = T('Select')  
    ns.db.employee.id.represent = lambda value,row: ui.control.get_select_button(onclick='set_employee_value("'+str(row.employee.id)+'", "'+str(row.employee.empnumber)+'", "'+str(row.employee.username)+'");')
    ns.db.employee.empnumber.represent = lambda value,row: A(SPAN(value),
                       _href=URL(r=request, f="frm_employee/view/employee/"+str(row.employee.id)), _target="_blank")
    links=None
  else:
    fields = [ns.db.employee.id, ns.db.employee.empnumber, ns.db.groups.groupvalue, ns.db.employee.username] 
    links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href="#", _title=T("Select Item"), 
                         _onclick='set_employee_value("'+str(row.employee.id)+'", "'+str(row.employee.empnumber)+'", "'
                         +str(row.employee.username)+'");jQuery(this).parents(".ui-dialog-content").dialog("close");return true;')]
  return DIV(ui.select.find_data("employee",query,fields,ns.db.employee.empnumber,10,25,links,left), _id="dlg_filter")

def dlg_payment(transtype=None):
  query = ((ns.db.trans.deleted==0)&(ns.db.trans.id==ns.db.payment.trans_id)&(ns.db.payment.deleted==0)&(ns.db.trans.place_id==ns.db.place.id))
  if transtype:
    transtype_id = ns.valid.get_groups_id("transtype", transtype)
    query = query & ((ns.db.trans.transtype==transtype_id))
    href=URL("dlg_payment_"+transtype)
  else:
    href=URL("dlg_payment_all")
  fields = [ns.db.payment.id, ns.db.trans.transnumber, ns.db.trans.transtype, #ns.db.fieldvalue.value, 
            ns.db.payment.paiddate, ns.db.trans.place_id, ns.db.place.curr, ns.db.payment.amount]
  left = None #[(ns.db.fieldvalue.on((ns.db.trans.id==ns.db.fieldvalue.ref_id)&(ns.db.fieldvalue.fieldname=='trans_transcast')&(ns.db.fieldvalue.deleted==0)))]
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
    
  #set transfilter
  query = ui.select.set_transfilter(query)
  
  ns.db.groups.groupvalue.label = T("Doc.Type")
  if session.mobile:
    ns.db.payment.id.label = T('Select')  
    ns.db.payment.id.represent = lambda value,row: ui.control.get_select_button(onclick='set_payment_value("'+str(row.payment.id)+'", "'+str(row.trans.transnumber)+'", "'
                         +str(row.trans.transtype)+'", "'+str(row.place.curr)+'", '+str(row.payment.amount)
                         +');jQuery(this).parents(".dialog").hide();return true;;')
    links = None
  else:
    links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href="#", _title=T("Select Item"), 
                         _onclick='set_payment_value("'+str(row.payment.id)+'", "'+str(row.trans.transnumber)+'", "'
                         +str(row.trans.transtype)+'", "'+str(row.place.curr)+'", '+str(row.payment.amount)
                         +');jQuery(this).parents(".ui-dialog-content").dialog("close");return true;')]
  return DIV(ui.select.find_data("payment",query,fields,ns.db.trans.transnumber,10,25,links,left,page_url=href), _id="dlg_filter")

@ns_auth.requires_login()
def dlg_payment_all():
  return dlg_payment()

def dlg_place(placetype=None,fnum=""):
  if session.mobile:
    ns.db.place.id.label = T('Select')  
    ns.db.place.id.represent = lambda value,row: ui.control.get_select_button(onclick='set_place_value'+fnum+'("'+str(row.place.id)+'", "'+str(row.place.planumber)+'", "'+str(row.place.description)
                           +'", "'+str(row.place.curr)
                           +'");')
    ns.db.place.planumber.represent = lambda value,row: A(SPAN(value),
                       _href=URL(r=request, f="frm_place/view/place/"+str(row.place.id)), _target="_blank")
    links = None
  else:
    links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href="#", _title=T("Select Item"), 
                         _onclick='set_place_value'+fnum+'("'+str(row.place.id)+'", "'+str(row.place.planumber)+'", "'+str(row.place.description)
                         +'", "'+str(row.place.curr)
                         +'");jQuery(this).parents(".ui-dialog-content").dialog("close");return true;')]
  query = ((ns.db.place.deleted==0)&(ns.db.place.placetype==ns.db.groups.id))
  if placetype:
    placetype_id = ns.valid.get_groups_id("placetype", placetype)
    query = query & ((ns.db.place.placetype==placetype_id))
    href=URL("dlg_place_"+placetype+fnum)
  else:
    href=URL("dlg_place_all")
  ns.db.groups.groupvalue.label=T("Type")
  left = None
  fields = [ns.db.place.id, ns.db.place.planumber, ns.db.groups.groupvalue, ns.db.place.description, ns.db.place.curr]
  return DIV(ui.select.find_data("place",query,fields,ns.db.place.planumber,10,25,links,left,page_url=href), _id="dlg_filter")

@ns_auth.requires_login()
def dlg_place_all():
  return dlg_place()

@ns_auth.requires_login()
def dlg_place_bank():
  return dlg_place("bank")

@ns_auth.requires_login()
def dlg_place_cash():
  return dlg_place("cash")

@ns_auth.requires_login()
def dlg_place_store():
  return dlg_place("store")

@ns_auth.requires_login()
def dlg_place_warehouse():
  return dlg_place("warehouse")

@ns_auth.requires_login()
def dlg_place_warehouse2():
  return dlg_place("warehouse","2")

def dlg_product(protype="all"):
  query = ((ns.db.product.deleted==0)&(ns.db.product.protype==ns.db.groups.id))
  left = None
  if protype!="all":
    protype_id = ns.valid.get_groups_id("protype", protype)
    query = query & ((ns.db.product.protype==protype_id))
    href=URL("dlg_product_"+protype)
  else:
    href=URL("dlg_product_all")
  if session.mobile:
    fields = [ns.db.product.id, ns.db.product.partnumber, ns.db.product.description, ns.db.product.unit, ns.db.product.tax_id]
    ns.db.product.id.label = T('Select')  
    ns.db.product.id.represent = lambda value,row: ui.control.get_select_button(onclick='set_product_value("'+str(row.id)+'", "'+str(row.partnumber)+'", "'+str(row.description)+'", "'+str(row.unit)+'", "'+str(row.tax_id)+'");')
    ns.db.product.partnumber.represent = lambda value,row: A(SPAN(value),
                       _href=URL(r=request, f="frm_product/view/product/"+str(row.id)), _target="_blank")
    links=None
  else:
    fields = [ns.db.product.id, ns.db.product.partnumber, ns.db.product.description, ns.db.product.unit, ns.db.product.tax_id]
    links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href="#", _title=T("Select Item"), 
                         _onclick='set_product_value("'+str(row.id)+'", "'+str(row.partnumber)+'", "'+str(row.description)+'", "'
                         +str(row.unit)+'", "'+str(row.tax_id)+'");jQuery(this).parents(".ui-dialog-content").dialog("close");return true;')]
  return DIV(ui.select.find_data("product",query,fields,ns.db.product.description,10,25,links,left,page_url=href), _id="dlg_filter")

@ns_auth.requires_login()
def dlg_product_all():
  return dlg_product("all")

@ns_auth.requires_login()
def dlg_product_item():
  return dlg_product("item")

@ns_auth.requires_login()
def dlg_product_service():
  return dlg_product("service")

@ns_auth.requires_login()
def dlg_product_stock():
  ruri = request.wsgi.environ["REQUEST_URI"]
  product_id = ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1]
  try:
    product_id = int(product_id)
  except Exception:
    product_id = None
  movetype_inventory_id = ns.valid.get_groups_id("movetype", "inventory")
  join = [(ns.db.product.on((ns.db.movement.product_id==ns.db.product.id))),
          (ns.db.trans.on((ns.db.movement.trans_id==ns.db.trans.id)&(ns.db.trans.deleted==0))),
          (ns.db.place.on((ns.db.movement.place_id==ns.db.place.id)))]
  left = None
  
  query = ((ns.db.movement.deleted==0)&(ns.db.movement.movetype==movetype_inventory_id))
  if product_id:
    query = query &(ns.db.movement.product_id==product_id)
    groupfields=[ns.db.movement.place_id,ns.db.place.planumber, ns.db.place.description, ns.db.product.unit, ns.db.movement.notes,
               ns.db.movement.qty.sum().with_alias('qty'),ns.db.movement.shippingdate.max().with_alias('shippingdate')]
    groupby=[ns.db.movement.place_id|ns.db.place.planumber|ns.db.place.description|ns.db.product.unit|ns.db.movement.notes]
    if session.mobile:
      fields = [ns.db.place.description, ns.db.movement.notes,
            ns.db.movement.qty, ns.db.movement.shippingdate]
      ns.db.place.planumber.represent = lambda value,row: ui.control.get_select_button(onclick='set_place_value("'+str(row.movement.place_id)+'", "'+str(row.place.planumber)
          +'");return true;',label=value,title=T("Select warehous"))
    else:
      fields = [ns.db.place.planumber, ns.db.place.description, ns.db.product.unit, ns.db.movement.notes,
            ns.db.movement.qty, ns.db.movement.shippingdate]
  else:
    fields = [ns.db.movement.place_id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes,
            ns.db.movement.qty, ns.db.movement.shippingdate]
    groupfields=[ns.db.movement.place_id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes,
               ns.db.movement.qty.sum().with_alias('qty'),ns.db.movement.shippingdate.max().with_alias('shippingdate')]
    groupby=[ns.db.movement.place_id|ns.db.product.partnumber|ns.db.movement.product_id|ns.db.product.unit|ns.db.movement.notes]
  
  ns.db.movement.place_id.label = T("Warehouse No.")
  ns.db.movement.qty.label = T("Stock")
  ns.db.place.description.label = T("Warehouse")
  ns.db.movement.shippingdate.label = T("LastDate")
  ns.db.movement.shippingdate.represent = lambda value,row: ui.control.format_value("date",row["shippingdate"])  

  if session.mobile:
    links = None
  else:
    links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href="#", _title=T("Select Warehouse"), 
                         _onclick='set_place_value("'+str(row.movement.place_id)+'", "'+str(row.place.planumber)+'");jQuery(this).parents(".ui-dialog-content").dialog("close");return true;')]
  
  form = SimpleGrid.grid(query=query, field_id=ns.db.movement.place_id, 
             fields=fields, groupfields=groupfields, groupby=groupby, left=left, having=None, join=join,
             orderby=ns.db.movement.place_id, sortable=False, paginate=None, maxtextlength=25,
             showbuttontext=False, editable=False, links=links)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if len(table)==0:
      form = ""
    elif type(table[0][0][0]).__name__!="TABLE":
      form = ""
    else:
      table[0][0][0]["_width"]="100%"
      table[0][0][0]["_cellpadding"]="3px;"
      ui.control.set_htmltable_style(table[0][0][0],"inventory_page","1,2")
    form.__delitem__(0)
    title = H1(ns.db.product(id=product_id).partnumber+" - "+ns.db.product(id=product_id).description,
               _style="color: #FFFFFF;font-size: small;margin:0px;padding:8px;")
    return DIV(title, form, _id="dlg_filter", _style="background-color: #222222;margin:0px;")
  else:
    return DIV(form, _id="dlg_filter")

@ns_auth.requires_login()
def dlg_project():
  query = ((ns.db.project.deleted==0))
  if session.mobile:
    fields = [ns.db.project.id, ns.db.project.pronumber, ns.db.project.description, ns.db.project.startdate]
    ns.db.project.startdate.represent = lambda value,row: ui.control.format_value("date",row.startdate)
    ns.db.project.id.label = T('Select')  
    ns.db.project.id.represent = lambda value,row: ui.control.get_select_button(onclick='set_project_value("'+str(row.id)+'", "'+str(row.pronumber)+'", "'+str(row.description)+'");')
    ns.db.project.pronumber.represent = lambda value,row: A(SPAN(value),
                       _href=URL(r=request, f="frm_project/view/project/"+str(row.id)), _target="_blank")
    left,links=None,None
  else:
    fields = [ns.db.project.id, ns.db.project.pronumber, ns.db.project.description, ns.db.project.startdate, ns.db.project.enddate, ns.db.customer.custname]
    left = (ns.db.customer.on(ns.db.project.customer_id==ns.db.customer.id))
    ns.db.project.startdate.represent = lambda value,row: ui.control.format_value("date",row.project["startdate"])
    ns.db.project.enddate.represent = lambda value,row: ui.control.format_value("date",row.project["enddate"])
    links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href="#", _title=T("Select Item"), 
                         _onclick='set_project_value("'+str(row.project.id)+'", "'+str(row.project.pronumber)+'", "'
                         +str(row.project.description)+'");jQuery(this).parents(".ui-dialog-content").dialog("close");return true;')]
  return DIV(ui.select.find_data("project",query,fields,ns.db.project.pronumber,10,25,links,left), _id="dlg_filter")

@ns_auth.requires_login()
def dlg_tool():
  query = ((ns.db.tool.deleted==0))
  if session.mobile:
    fields = [ns.db.tool.id, ns.db.tool.serial, ns.db.tool.description]
    ns.db.tool.id.label = T('Select')  
    ns.db.tool.id.represent = lambda value,row: ui.control.get_select_button(onclick='set_tool_value("'+str(row.id)+'", "'+str(row.serial)+'", "'+str(row.description)+'");')
    ns.db.tool.serial.represent = lambda value,row: A(SPAN(value),
                       _href=URL(r=request, f="frm_tool/view/tool/"+str(row.id)), _target="_blank")
    left,links=None,None
  else:
    fields = [ns.db.tool.id, ns.db.tool.serial, ns.db.tool.description, ns.db.groups.groupvalue]
    left = (ns.db.groups.on(ns.db.tool.toolgroup==ns.db.groups.id))
    links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href="#", _title=T("Select Item"), 
                         _onclick='set_tool_value("'+str(row.tool.id)+'", "'+str(row.tool.serial)+'", "'
                         +str(row.tool.description)+'");jQuery(this).parents(".ui-dialog-content").dialog("close");return true;')]
  return DIV(ui.select.find_data("tool",query,fields,ns.db.tool.serial,10,25,links,left), _id="dlg_filter")

def dlg_transitem(transtype=None):
  query = ((ns.db.trans.deleted==0)
           &(ns.db.trans.transtype==ns.db.groups.id))
  ns.db.groups.groupvalue.label = T("Doc.Type")
  if transtype:
    transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue.belongs(transtype.split(",")))).select(ns.db.groups.id)
    query = query & ((ns.db.trans.transtype.belongs(transtype_id)))
    href=URL("dlg_transitem_"+transtype.split(",")[0])
  else:
    query = query & (ns.db.groups.groupvalue.belongs(("invoice","receipt","order","offer","worksheet","rent")))
    href=URL("dlg_transitem_all")
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = ui.select.set_transfilter(query)
  
  if session.mobile:
    fields = [ns.db.trans.id, ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, ns.db.trans.curr]
    ns.db.trans.id.label = T('Select')  
    ns.db.trans.id.represent = lambda value,row: ui.control.get_select_button(onclick='set_transitem_value("'+str(row.id)+'", "'+str(row.transnumber)+'", "'
                           +str(row.transtype)+'", "'+str(row.direction)+'", "'+str(row.curr)
                           +'");')
    ns.db.trans.transnumber.represent = lambda value,row: A(SPAN(value),
                       _href=URL(r=request, f="frm_trans/view/trans/"+str(row.id)), _target="_blank")
    left,links = None,None
  else:
    fields = [ns.db.trans.id, ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, ns.db.trans.customer_id, ns.db.trans.transdate, ns.db.trans.curr]
    left = [(ns.db.customer.on((ns.db.customer.id==ns.db.trans.customer_id)))]  
    ns.db.trans.transdate.label = T("Date")
    links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href="#", _title=T("Select Item"), 
                         _onclick='set_transitem_value("'+str(row.id)+'", "'+str(row.transnumber)+'", "'
                         +str(row.transtype)+'", "'+str(row.direction)+'", "'+str(row.curr)
                         +'");jQuery(this).parents(".ui-dialog-content").dialog("close");return true;')]
  return DIV(ui.select.find_data("trans",query,fields,ns.db.trans.transnumber,10,25,links,left,page_url=href), _id="dlg_filter")

@ns_auth.requires_login()
def dlg_transitem_all():
  return dlg_transitem()

@ns_auth.requires_login()
def dlg_transitem_invoice():
  return dlg_transitem("invoice,receipt")

def dlg_transmovement(transtype=None):
  query = ((ns.db.trans.deleted==0)
           &(ns.db.trans.transtype==ns.db.groups.id))
  left = None
  if transtype:
    transtype_id = ns.valid.get_groups_id("transtype", transtype)
    query = query & ((ns.db.trans.transtype==transtype_id))
    href=URL("dlg_transmovement_"+transtype)
  else:
    query = query & (ns.db.groups.groupvalue.belongs(("inventory","delivery","production","waybill","formula")))
    href=URL("dlg_transmovement_all")
    
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = ui.select.set_transfilter(query)
  
  fields = [ns.db.trans.id, ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction]
    
  ns.db.groups.groupvalue.label = T("Doc.Type")
  if session.mobile:
    ns.db.trans.id.label = T('Select')  
    ns.db.trans.id.represent = lambda value,row: ui.control.get_select_button(onclick='set_transmovement_value("'+str(row.id)+'", "'+str(row.transnumber)+'", "'
                           +str(row.transtype)+'", "'+str(row.direction)+'");')
    ns.db.trans.transnumber.represent = lambda value,row: A(SPAN(value),
                       _href=URL(r=request, f="frm_trans/view/trans/"+str(row.id)), _target="_blank")
    links = None
  else:
    links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href="#", _title=T("Select Item"), 
                         _onclick='set_transmovement_value("'+str(row.id)+'", "'+str(row.transnumber)+'", "'
                         +str(row.transtype)+'", "'+str(row.direction)
                         +'");jQuery(this).parents(".ui-dialog-content").dialog("close");return true;')]
  return DIV(ui.select.find_data("trans",query,fields,ns.db.trans.transnumber,10,25,links,left,page_url=href), _id="dlg_filter") 

@ns_auth.requires_login()
def dlg_transmovement_all():
  return dlg_transmovement()

def dlg_transpayment(transtype=None):
  query = ((ns.db.trans.deleted==0)
           &(ns.db.trans.transtype==ns.db.groups.id)
           &(ns.db.trans.place_id==ns.db.place.id))
  left = None
  if transtype:
    transtype_id = ns.valid.get_groups_id("transtype", transtype)
    query = query & ((ns.db.trans.transtype==transtype_id))
    href=URL("dlg_transpayment_"+transtype)
  else:
    query = query & (ns.db.groups.groupvalue.belongs(("bank","cash")))
    href=URL("dlg_transpayment_all")
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
      
  #set transfilter
  query = ui.select.set_transfilter(query)
  
  if session.mobile:
    ns.db.trans.id.label = T('Select')  
    ns.db.trans.id.represent = lambda value,row: ui.control.get_select_button(onclick='set_transpayment_value("'+str(row.trans.id)+'", "'+str(row.trans.transnumber)+'", "'
                           +str(row.trans.transtype)+'", "'+str(row.place.curr)
                           +'");')
    ns.db.trans.transnumber.represent = lambda value,row: A(SPAN(value),
                       _href=URL(r=request, f="frm_trans/view/trans/"+str(row.trans.id)), _target="_blank")
    links = None
  else:
    links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href="#", _title=T("Select Item"), 
                         _onclick='set_transpayment_value("'+str(row.trans.id)+'", "'+str(row.trans.transnumber)+'", "'
                         +str(row.trans.transtype)+'", "'+str(row.place.curr)
                         +'");jQuery(this).parents(".ui-dialog-content").dialog("close");return true;')]
    
  fields = [ns.db.trans.id, ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, ns.db.place.planumber, ns.db.place.curr]
  ns.db.groups.groupvalue.label = T("Doc.Type")
  ns.db.place.planumber.label = T("Bank/Ch.")
  return DIV(ui.select.find_data("trans",query,fields,ns.db.trans.transnumber,10,25,links,left,page_url=href), _id="dlg_filter")

@ns_auth.requires_login()
def dlg_transpayment_all():
  return dlg_transpayment()

@ns_auth.requires_login()
def dlg_transpayment_bank():
  return dlg_transpayment("bank")

@ns_auth.requires_login()
def dlg_transpayment_cash():
  return dlg_transpayment("cash")

@ns_auth.requires_login()
def find_customer_address():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.customer_address_filter=None
    redirect(URL("find_customer_address"))
  
  if ruri.find("new")>0:
    redirect(URL('frm_customer/new/customer'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_customer"+ruri[ruri.find("find_customer_address")+21:]
    redirect(URL(ruri))
  
  response.browsertype=T('Customer Browser')
  response.subtitle=T('Addresses')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_customer_address","find_customer_address/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_customer_address","find_customer_address/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_address.png')
    response.export_excel = ruri.replace("find_customer_address","find_customer_address/excel")
    response.export_csv = ruri.replace("find_customer_address","find_customer_address/csv")
  ui.menu.set_find_customer_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="customer_address_filter",
    state_fields=None,bool_fields=None,date_fields=None,number_fields=None,
    data_fields={"data_fields_name":["htab_customer_custnumber", "htab_customer_custname", ns.db.address.country.name, 
                                     ns.db.address.state.name, ns.db.address.zipcode.name, ns.db.address.city.name, 
                                     ns.db.address.street.name, ns.db.address.notes.name],
                 "data_fields_label":[ns.db.customer.custnumber.label, ns.db.customer.custname.label, ns.db.address.country.label, 
                                      ns.db.address.state.label, ns.db.address.zipcode.label, ns.db.address.city.label, 
                                      ns.db.address.street.label, ns.db.address.notes.label]})
  
  nervatype_customer = ns.valid.get_groups_id("nervatype", "customer")
  join = [(ns.db.address.on((ns.db.customer.id==ns.db.address.ref_id)&(ns.db.address.nervatype==nervatype_customer)&(ns.db.address.deleted==0)))]
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.custtype!=ns.valid.get_groups_id("custtype", "own")))
  
  where = ui.select.get_filter_query(sfilter=session.customer_address_filter,table="customer",query=query)
  query = where["query"]
  
  fields = [ns.db.address.id,ns.db.customer.custname,ns.db.address.country,ns.db.address.state,
            ns.db.address.zipcode,ns.db.address.city,ns.db.address.street,ns.db.address.notes]
  left = None
  if ruri.find("find_customer_address/excel")>0:
    return ui.report.export_excel("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  if ruri.find("find_customer_address/csv")>0:
    return ui.report.export_csv("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_address_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.customer.id==-1))
  
  ns.db.address.id.label = T("Address No.")
  if session.mobile:
    ns.db.address.id.represent = lambda value,row: ui.control.get_mobil_button(ns.valid.show_refnumber("refnumber","address", value), href=URL("frm_customer/edit/customer/"+str(row.customer["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    ns.db.address.id.represent = lambda value,row: SPAN(ns.valid.show_refnumber("refnumber","address", value))
    editable=True
  form = SimpleGrid.grid(query=query, field_id=ns.db.customer.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.customer.custname, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_customer","0,5,6")
  return dict(form=form)

@ns_auth.requires_login()
def find_customer_contact():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.customer_contact_filter=None
    redirect(URL("find_customer_contact"))
  
  if ruri.find("new")>0:
    redirect(URL('frm_customer/new/customer'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_customer"+ruri[ruri.find("find_customer_contact")+21:]
    redirect(URL(ruri))
    
  response.browsertype=T('Customer Browser')
  response.subtitle=T('Contact persons')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_customer_contact","find_customer_contact/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_customer_contact","find_customer_contact/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_user.png')
    response.export_excel = ruri.replace("find_customer_contact","find_customer_contact/excel")
    response.export_csv = ruri.replace("find_customer_contact","find_customer_contact/csv")
  ui.menu.set_find_customer_menu()
  response.filter_form = ui.select.create_filter_form(sfilter_name="customer_contact_filter",
    state_fields=None,bool_fields=None,date_fields=None,number_fields=None,
    data_fields={"data_fields_name":["htab_customer_custnumber", "htab_customer_custname", ns.db.contact.firstname.name, 
                                     ns.db.contact.surname.name, ns.db.contact.status.name, ns.db.contact.phone.name, 
                                     ns.db.contact.fax.name, ns.db.contact.mobil.name, ns.db.contact.email.name, 
                                     ns.db.contact.notes.name],
                 "data_fields_label":[ns.db.customer.custnumber.label, ns.db.customer.custname.label, ns.db.contact.firstname.label, 
                                      ns.db.contact.surname.label, ns.db.contact.status.label, ns.db.contact.phone.label, 
                                      ns.db.contact.fax.label, ns.db.contact.mobil.label, ns.db.contact.email.label, 
                                      ns.db.contact.notes.label]})
  nervatype_customer = ns.valid.get_groups_id("nervatype", "customer")
  
  join = [(ns.db.contact.on((ns.db.customer.id==ns.db.contact.ref_id)&(ns.db.contact.nervatype==nervatype_customer)&(ns.db.contact.deleted==0)))]
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.custtype!=ns.valid.get_groups_id("custtype", "own")))
  
  where = ui.select.get_filter_query(sfilter=session.customer_contact_filter,table="contact",query=query)
  query = where["query"]
  
  fields = [ns.db.contact.id, ns.db.customer.custname, ns.db.contact.firstname,ns.db.contact.surname,
            ns.db.contact.status,ns.db.contact.phone,ns.db.contact.fax,ns.db.contact.mobil,ns.db.contact.email,ns.db.contact.notes]
  left = None
  
  if ruri.find("find_customer_contact/excel")>0:
    return ui.report.export_excel("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  if ruri.find("find_customer_contact/csv")>0:
    return ui.report.export_csv("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_contact_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.customer.id==-1))
  
  ns.db.contact.id.label = T("Contact No.")
  if session.mobile:
    ns.db.contact.id.represent = lambda value,row: ui.control.get_mobil_button(ns.valid.show_refnumber("refnumber","contact", value), href=URL("frm_customer/edit/customer/"+str(row.customer["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    ns.db.contact.id.represent = lambda value,row: SPAN(ns.valid.show_refnumber("refnumber","contact", value))
    editable=True
  form = SimpleGrid.grid(query=query, field_id=ns.db.customer.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.customer.custname, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_customer","0,2,3")
  return dict(form=form)

@ns_auth.requires_login()
def find_customer_customer():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.customer_customer_filter=None
    redirect(URL("find_customer_customer"))
    
  if ruri.find("new")>0:
    redirect(URL('frm_customer/new/customer'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_customer"+ruri[ruri.find("find_customer_customer")+22:]
    redirect(URL(ruri))
  
  response.browsertype=T('Customer Browser')
  response.subtitle=T('Customer Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_customer_customer","find_customer_customer/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_customer_customer","find_customer_customer/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_customer.png')
    response.export_excel = ruri.replace("find_customer_customer","find_customer_customer/excel")
    response.export_csv = ruri.replace("find_customer_customer","find_customer_customer/csv")
  ui.menu.set_find_customer_menu()
  response.filter_form = ui.select.create_filter_form(sfilter_name="customer_customer_filter",state_fields=None,
    bool_fields={"bool_fields_name":[ns.db.customer.notax.name, ns.db.customer.inactive.name],
                 "bool_fields_label":[ns.db.customer.notax.label, ns.db.customer.inactive.label]},
    number_fields={"number_fields_name":[ns.db.customer.terms.name, ns.db.customer.creditlimit.name, ns.db.customer.discount.name],
                   "number_fields_label":[ns.db.customer.terms.label, ns.db.customer.creditlimit.label, ns.db.customer.discount.label]},
    date_fields=None,
    data_fields={"data_fields_name":[ns.db.customer.custnumber.name, ns.db.customer.custname.name, ns.db.customer.taxnumber.name, 
                                     ns.db.customer.custtype.name, ns.db.customer.account.name, ns.db.customer.notes.name, 
                                     "htab_address_city", "htab_address_street"],
                 "data_fields_label":[ns.db.customer.custnumber.label, ns.db.customer.custname.label, ns.db.customer.taxnumber.label, 
                                      ns.db.customer.custtype.label, ns.db.customer.account.label, ns.db.customer.notes.label, 
                                      ns.db.address.city.label, ns.db.address.street.label]})

  nervatype_customer = ns.valid.get_groups_id("nervatype", "customer")
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.custtype!=ns.valid.get_groups_id("custtype", "own")))  
  where = ui.select.get_filter_query(sfilter=session.customer_customer_filter,table="customer",query=query)
  query = where["query"]
  
  fields = [ns.db.customer.custnumber, ns.db.customer.custname, ns.db.customer.taxnumber, ns.db.customer.custtype, 
            ns.db.customer.account, ns.db.customer.notax, ns.db.customer.terms, ns.db.customer.creditlimit, ns.db.customer.discount,
            ns.db.customer.notes, ns.db.address.city, ns.db.address.street, ns.db.customer.inactive]
  pa_list = ns.db((ns.db.address.deleted==0)&(ns.db.address.nervatype==nervatype_customer)).select(ns.db.address.id.min().with_alias('id'), groupby=ns.db.address.ref_id)
  if len(pa_list)>0:
    left = (ns.db.address.on((ns.db.customer.id==ns.db.address.ref_id) & (ns.db.address.id.belongs(pa_list))))
  else:
    left = (ns.db.address.on((ns.db.customer.id==ns.db.address.ref_id)))
  
  if ruri.find("find_customer_customer/excel")>0:
    return ui.report.export_excel("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords)
  if ruri.find("find_customer_customer/csv")>0:
    return ui.report.export_csv("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_customer_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.customer.id==-1))
  
  if session.mobile:
    ns.db.customer.custnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_customer/edit/customer/"+str(row.customer["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable=False
  else:
    editable=True
  form = SimpleGrid.grid(query=query, field_id=ns.db.customer.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=None,
             orderby=ns.db.customer.custname, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, create=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_customer","0,1")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_customer_event():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.customer_event_filter=None
    redirect(URL("find_customer_event"))
  
  if ruri.find("new")>0:
    redirect(URL('frm_customer/new/customer'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_event"+ruri[ruri.find("find_customer_event")+19:]
    redirect(URL(ruri))
  response.browsertype=T('Customer Browser')
  response.subtitle=T('Events')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_customer_event","find_customer_event/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_customer_event","find_customer_event/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
    response.export_excel = ruri.replace("find_customer_event","find_customer_event/excel")
    response.export_csv = ruri.replace("find_customer_event","find_customer_event/csv")
  ui.menu.set_find_customer_menu()
  response.filter_form = ui.select.create_filter_form(sfilter_name="customer_event_filter",state_fields=None,bool_fields=None,
    date_fields={"date_fields_name":[ns.db.event.fromdate.name,ns.db.event.todate.name],
                 "date_fields_label":[ns.db.event.fromdate.label,ns.db.event.todate.label]},
    number_fields=None,
    data_fields={"data_fields_name":[ns.db.event.calnumber.name, "htab_customer_custnumber", "htab_customer_custname", 
                                     ns.db.event.eventgroup.name, ns.db.event.subject.name, ns.db.event.place.name, 
                                     ns.db.event.description.name],
                 "data_fields_label":[ns.db.event.calnumber.label, ns.db.customer.custnumber.label, ns.db.customer.custname.label, 
                                      ns.db.event.eventgroup.label, ns.db.event.subject.label, ns.db.event.place.label, 
                                      ns.db.event.description.label]},
    more_data={"title":"Event Additional Data","caption":"Additional Data","url":URL('find_customer_event_fields')})
  
  ns.db.event.ref_id.represent = lambda value,row: A(SPAN(ns.db.customer(id=int(value))["custname"]),
                     _href=URL(r=request, f="frm_customer/view/customer/"+str(value)), _target="_blank")
  ns.db.event.ref_id.label=T('Customer')
  nervatype_customer = ns.valid.get_groups_id("nervatype", "customer")
  
  join = [(ns.db.event.on((ns.db.customer.id==ns.db.event.ref_id)&(ns.db.event.nervatype==nervatype_customer)&(ns.db.event.deleted==0)))]
  left = [(ns.db.groups.on((ns.db.event.eventgroup==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.custtype!=ns.valid.get_groups_id("custtype", "own")))
  where = ui.select.get_filter_query(sfilter=session.customer_event_filter,table="event",query=query)
  query = where["query"]
  
  fields = [ns.db.event.calnumber,ns.db.customer.custnumber, ns.db.event.ref_id, ns.db.event.eventgroup,
            ns.db.event.fromdate,ns.db.event.todate,ns.db.event.subject,ns.db.event.place,ns.db.event.description]
  
  if ruri.find("find_customer_event/excel")>0:
    return ui.report.export_excel("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  if ruri.find("find_customer_event/csv")>0:
    return ui.report.export_csv("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_event_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.customer.id==-1))
  
  if session.mobile:
    ns.db.event.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_event/edit/event/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    links = None
    editable=False
  else:
    links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("cmd_export_ical?id="+str(row.event.id)), _target="_blank", _title=T("Export Item"))]
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=ns.db.event.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.customer.custname, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=links)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_event","0,1,6")
  return dict(form=form)

@ns_auth.requires_login()
def find_customer_event_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.customer_event_fields_filter=None
    redirect(URL("find_customer_event_fields"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_event"+ruri[ruri.find("find_customer_event_fields")+26:]
    redirect(URL(ruri))
  
  response.browsertype=T('Customer Browser')
  response.subtitle=T('Event Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_customer_event_fields","find_customer_event_fields/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_customer_event_fields","find_customer_event_fields/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
    response.export_excel = ruri.replace("find_customer_event_fields","find_customer_event_fields/excel")
    response.export_csv = ruri.replace("find_customer_event_fields","find_customer_event_fields/csv")
  ui.menu.set_find_customer_menu()
  nervatype_event = ns.valid.get_groups_id("nervatype", "event")
  nervatype_customer = ns.valid.get_groups_id("nervatype", "customer")
  response.filter_form = ui.select.get_fields_filter("event","customer_event_fields_filter")
  
  htab = ns.db.event.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(htab.nervatype==nervatype_customer))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_event)))]
  query = (ns.db.fieldvalue.deleted==0)
  where = ui.select.get_filter_query(sfilter=session.customer_event_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.calnumber,htab.subject,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_customer_event_fields/excel")>0:
    return ui.report.export_excel("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  if ruri.find("find_customer_event_fields/csv")>0:
    return ui.report.export_csv("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_event_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
  
  if session.mobile:
    htab.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_event/edit/event/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.calnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_event","0,1,2")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_customer_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.customer_fields_filter=None
    redirect(URL("find_customer_fields"))

  if ruri.find("new")>0:
    redirect(URL('frm_customer/new/customer'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_customer"+ruri[ruri.find("find_customer_fields")+20:]
    redirect(URL(ruri))
  
  response.browsertype=T('Customer Browser')
  response.subtitle=T('Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_customer_fields","find_customer_fields/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_customer_fields","find_customer_fields/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_customer.png')
    response.export_excel = ruri.replace("find_customer_fields","find_customer_fields/excel")
    response.export_csv = ruri.replace("find_customer_fields","find_customer_fields/csv")
  ui.menu.set_find_customer_menu()
  nervatype_customer = ns.valid.get_groups_id("nervatype", "customer")
  response.filter_form = ui.select.get_fields_filter("customer","customer_fields_filter")
  
  htab = ns.db.customer.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(htab.custtype!=ns.valid.get_groups_id("custtype", "own")))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_customer)))]
  query = (ns.db.fieldvalue.deleted==0)
  where = ui.select.get_filter_query(sfilter=session.customer_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.custnumber,htab.custname,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None

  if ruri.find("find_customer_fields/excel")>0:
    return ui.report.export_excel("customer",query,left,fields,htab.custname,request.vars.keywords,join=join)
  if ruri.find("find_customer_fields/csv")>0:
    return ui.report.export_csv("customer",query,left,fields,htab.custname,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
  
  if session.mobile:
    htab.custnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_customer/edit/customer/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.custname, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, create=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_customer","0,2,3")
  return dict(form=form)

@ns_auth.requires_login()
def find_customer_groups():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.customer_groups_filter=None
    redirect(URL("find_customer_groups"))
    
  if ruri.find("new")>0:
    redirect(URL('frm_customer/new/customer'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_customer"+ruri[ruri.find("find_customer_groups")+20:]
    redirect(URL(ruri))
  
  response.browsertype=T('Customer Browser')
  response.subtitle=T('Groups')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_customer_groups","find_customer_groups/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_customer_groups","find_customer_groups/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_customer.png')
    response.export_excel = ruri.replace("find_customer_groups","find_customer_groups/excel")
    response.export_csv = ruri.replace("find_customer_groups","find_customer_groups/csv")
  ui.menu.set_find_customer_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="customer_groups_filter",state_fields=None,
    bool_fields=None, date_fields=None, number_fields=None,
    data_fields={"data_fields_name":["htab_customer_custnumber","htab_customer_custname",ns.db.groups.groupvalue.name,
                                     ns.db.groups.description.name],
                 "data_fields_label":[ns.db.customer.custnumber.label,ns.db.customer.custname.label,ns.db.groups.groupvalue.label,
                                      ns.db.groups.description.label]})
  
  nervatype_customer = ns.valid.get_groups_id("nervatype", "customer")
  nervatype_groups = ns.valid.get_groups_id("nervatype", "groups")
  join = [(ns.db.link.on((ns.db.customer.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_customer)&(ns.db.link.deleted==0))),
          (ns.db.groups.on((ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.ref_id_2==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.custtype!=ns.valid.get_groups_id("custtype", "own")))
  where = ui.select.get_filter_query(sfilter=session.customer_groups_filter,table="groups",query=query)
  query = where["query"]
  
  fields = [ns.db.customer.custnumber, ns.db.customer.custname,ns.db.groups.groupvalue,ns.db.groups.description]
  left = None
  
  if ruri.find("find_customer_groups/excel")>0:
    return ui.report.export_excel("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  if ruri.find("find_customer_groups/csv")>0:
    return ui.report.export_csv("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_groups_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.customer.id==-1))
  
  if session.mobile:
    ns.db.customer.custnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_customer/edit/customer/"+str(row.customer["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=ns.db.customer.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.customer.custname, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_customer","0,2,3")
  return dict(form=form)

@ns_auth.requires_login()
def find_employee_employee():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.employee_employee_filter=None
    redirect(URL("find_employee_employee"))
    
  if ruri.find("new")>0:
    redirect(URL('frm_employee/new/employee'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_employee"+ruri[ruri.find("find_employee_employee")+22:]
    redirect(URL(ruri))
  response.browsertype=T('Employee Browser')
  response.subtitle=T('Employee Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_employee_employee","find_employee_employee/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_employee_employee","find_employee_employee/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_user.png')
    response.export_excel = ruri.replace("find_employee_employee","find_employee_employee/excel")
    response.export_csv = ruri.replace("find_employee_employee","find_employee_employee/csv")
  ui.menu.set_find_employee_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="employee_employee_filter",state_fields=None,
    bool_fields={"bool_fields_name":[ns.db.employee.inactive.name],
                 "bool_fields_label":[ns.db.employee.inactive.label]},
    number_fields=None,
    date_fields={"date_fields_name":[ns.db.employee.startdate.name, ns.db.employee.enddate.name],
                 "date_fields_label":[ns.db.employee.startdate.label, ns.db.employee.enddate.label]},
    data_fields={"data_fields_name":[ns.db.employee.empnumber.name, "htab_contact_firstname", "htab_contact_surname", 
                                     ns.db.employee.username.name, ns.db.employee.usergroup.name,ns.db.employee.department.name, 
                                     "htab_contact_status", "htab_contact_phone", "htab_contact_mobil", "htab_contact_email", 
                                     "htab_contact_notes"],
                 "data_fields_label":[ns.db.employee.empnumber.label, ns.db.contact.firstname.label, ns.db.contact.surname.label, 
                                      ns.db.employee.username.label, ns.db.employee.usergroup.label, ns.db.employee.department.label, 
                                      ns.db.contact.status.label, ns.db.contact.phone.label, ns.db.contact.mobil.label,
                                      ns.db.contact.email.label, ns.db.contact.notes.label]})
  
  nervatype_employee = ns.valid.get_groups_id("nervatype", "employee")
  query = ((ns.db.employee.deleted==0)&(ns.db.employee.usergroup==ns.db.groups.id))
  where = ui.select.get_filter_query(sfilter=session.employee_employee_filter,table="employee",query=query)
  query = where["query"]
  
  department = ns.db.groups.with_alias('department')
  department.groupvalue.label=T("Department")
  fields = [ns.db.employee.empnumber, ns.db.contact.firstname, ns.db.contact.surname, ns.db.employee.username, ns.db.employee.usergroup,
            department.groupvalue, ns.db.employee.startdate, ns.db.employee.enddate, ns.db.contact.status, ns.db.contact.phone, ns.db.contact.mobil,
            ns.db.contact.email, ns.db.contact.notes, ns.db.employee.inactive]
  left = ([ns.db.contact.on((ns.db.employee.id==ns.db.contact.ref_id)&(ns.db.contact.nervatype==nervatype_employee)&(ns.db.contact.deleted==0)),
          department.on((ns.db.employee.department==department.id)&(department.deleted==0))])
  
  if ruri.find("find_employee_employee/excel")>0:
    return ui.report.export_excel("employee",query,left,fields,ns.db.employee.empnumber,request.vars.keywords)
  if ruri.find("find_employee_employee/csv")>0:
    return ui.report.export_csv("employee",query,left,fields,ns.db.employee.empnumber,request.vars.keywords)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.employee_employee_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.employee.id==-1))
  
  if session.mobile:
    ns.db.employee.empnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_employee/edit/employee/"+str(row.employee["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True
  form = SimpleGrid.grid(query=query, field_id=ns.db.employee.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=None,
             orderby=ns.db.employee.empnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, create=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_employee","0,1,2,3")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_employee_event():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.employee_event_filter=None
    redirect(URL("find_employee_event"))
  
  if ruri.find("new")>0:
    redirect(URL('frm_employee/new/employee'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_event"+ruri[ruri.find("find_employee_event")+19:]
    redirect(URL(ruri))
  response.browsertype=T('Employee Browser')
  response.subtitle=T('Events')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_employee_event","find_employee_event/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_employee_event","find_employee_event/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
    response.export_excel = ruri.replace("find_employee_event","find_employee_event/excel")
    response.export_csv = ruri.replace("find_employee_event","find_employee_event/csv")
  ui.menu.set_find_employee_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="employee_event_filter",state_fields=None,bool_fields=None,
    date_fields={"date_fields_name":[ns.db.event.fromdate.name,ns.db.event.todate.name],
                 "date_fields_label":[ns.db.event.fromdate.label,ns.db.event.todate.label]},
    number_fields=None,
    data_fields={"data_fields_name":[ns.db.event.calnumber.name, "htab_employee_empnumber", "htab_employee_username", 
                                     ns.db.event.eventgroup.name, ns.db.event.subject.name, ns.db.event.place.name, 
                                     ns.db.event.description.name],
                 "data_fields_label":[ns.db.event.calnumber.label, ns.db.employee.empnumber.label, ns.db.employee.username.label, 
                                      ns.db.event.eventgroup.label, ns.db.event.subject.label, ns.db.event.place.label, 
                                      ns.db.event.description.label]},
    more_data={"title":"Event Additional Data","caption":"Additional Data","url":URL('find_employee_event_fields')})
  
  ns.db.event.ref_id.represent = lambda value,row: A(SPAN(ns.db.employee(id=int(value))["empnumber"]),
                     _href=URL(r=request, f="frm_employee/view/employee/"+str(value)), _target="_blank")
  ns.db.event.ref_id.label=T('Employee No.')
  nervatype_employee = ns.valid.get_groups_id("nervatype", "employee")

  join = [(ns.db.event.on((ns.db.employee.id==ns.db.event.ref_id)&(ns.db.event.nervatype==nervatype_employee)&(ns.db.event.deleted==0)))]
  left = [(ns.db.groups.on((ns.db.event.eventgroup==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  query = (ns.db.employee.deleted==0)  
  where = ui.select.get_filter_query(sfilter=session.employee_event_filter,table="event",query=query)
  query = where["query"]
  
  fields = [ns.db.event.calnumber,ns.db.event.ref_id, ns.db.employee.username, ns.db.event.eventgroup,
            ns.db.event.fromdate,ns.db.event.todate,ns.db.event.subject,ns.db.event.place,ns.db.event.description]
  if ruri.find("find_employee_event/excel")>0:
    return ui.report.export_excel("employee",query,left,fields,ns.db.employee.empnumber,request.vars.keywords,join=join)
  if ruri.find("find_employee_event/csv")>0:
    return ui.report.export_csv("employee",query,left,fields,ns.db.employee.empnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.employee_event_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.employee.id==-1))
    
  if session.mobile:
    links = None
    ns.db.event.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_event/edit/event/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable=False
  else:
    links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("cmd_export_ical?id="+str(row.event.id)), _target="_blank", _title=T("Export Item"))]
    editable=True
  form = SimpleGrid.grid(query=query, field_id=ns.db.event.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.employee.empnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=links)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_event","0,1,6")
  return dict(form=form)

@ns_auth.requires_login()
def find_employee_event_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.employee_event_fields_filter=None
    redirect(URL("find_employee_event_fields"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_event"+ruri[ruri.find("find_employee_event_fields")+26:]
    redirect(URL(ruri))
  
  response.browsertype=T('Employee Browser')
  response.subtitle=T('Event Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_employee_event_fields","find_employee_event_fields/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_employee_event_fields","find_employee_event_fields/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
    response.export_excel = ruri.replace("find_employee_event_fields","find_employee_event_fields/excel")
    response.export_csv = ruri.replace("find_employee_event_fields","find_employee_event_fields/csv")
  ui.menu.set_find_employee_menu()
  nervatype_event = ns.valid.get_groups_id("nervatype", "event")
  nervatype_employee = ns.valid.get_groups_id("nervatype", "employee")
  response.filter_form = ui.select.get_fields_filter("event","employee_event_fields_filter")
  
  htab = ns.db.event.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(htab.nervatype==nervatype_employee))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_event)))]
  query = (ns.db.fieldvalue.deleted==0)
  where = ui.select.get_filter_query(sfilter=session.employee_event_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.calnumber,htab.subject,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_employee_event_fields/excel")>0:
    return ui.report.export_excel("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  if ruri.find("find_employee_event_fields/csv")>0:
    return ui.report.export_csv("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.employee_event_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  if session.mobile:
    htab.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_event/edit/event/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.calnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_event","0,1,2")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_employee_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.employee_fields_filter=None
    redirect(URL("find_employee_fields"))
  
  if ruri.find("new")>0:
    redirect(URL('frm_employee/new/employee'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_employee"+ruri[ruri.find("find_employee_fields")+20:]
    redirect(URL(ruri))
    
  response.browsertype=T('Employee Browser')
  response.subtitle=T('Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_employee_fields","find_employee_fields/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_employee_fields","find_employee_fields/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_user.png')
    response.export_excel = ruri.replace("find_employee_fields","find_employee_fields/excel")
    response.export_csv = ruri.replace("find_employee_fields","find_employee_fields/csv")
  ui.menu.set_find_employee_menu()
  nervatype_employee = ns.valid.get_groups_id("nervatype", "employee")
  response.filter_form = ui.select.get_fields_filter("employee","employee_fields_filter")
  
  htab = ns.db.employee.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_employee)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = ui.select.get_filter_query(sfilter=session.employee_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.empnumber,htab.username,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_employee_fields/excel")>0:
    return ui.report.export_excel("employee",query,left,fields,htab.empnumber,request.vars.keywords,join=join)
  if ruri.find("find_employee_fields/csv")>0:
    return ui.report.export_csv("employee",query,left,fields,htab.empnumber,request.vars.keywords,join=join)
    
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.employee_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
  
  if session.mobile:
    htab.empnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_employee/edit/employee/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.empnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, create=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_employee","0,2,3")
  return dict(form=form)

@ns_auth.requires_login()
def find_log():
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.log_filter=None
    redirect(URL("find_log"))
  
  response.lo_menu = []  
  response.browsertype=T('Log Browser')
  response.subtitle=T('Database Logs')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_log","find_log/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_log","find_log/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_book_edit.png')
    response.export_excel = ruri.replace("find_log","find_log/excel")
    response.export_csv = ruri.replace("find_log","find_log/csv")

  response.filter_form = ui.select.create_filter_form(sfilter_name="log_filter",state_fields=["logstate","nervatype"],
    bool_fields=None,
    date_fields={"date_fields_name":[ns.db.log.crdate.name],
                 "date_fields_label":[ns.db.log.crdate.label]},
    number_fields=None,
    data_fields={"data_fields_name":[ns.db.log.employee_id.name],
                 "data_fields_label":[ns.db.log.employee_id.label]})
  
  join = None
  left = None
  query = (ns.db.log.id>0)
  where = ui.select.get_filter_query(sfilter=session.log_filter,table="log",query=query)
  query = where["query"]
  
  fields = [ns.db.log.logstate,ns.db.log.employee_id,ns.db.log.crdate,ns.db.log.nervatype,ns.db.log.ref_id]
  if ruri.find("find_log/excel")>0:
    return ui.report.export_excel("log",query,left,fields,ns.db.log.crdate,request.vars.keywords,join=join)
  if ruri.find("find_log/csv")>0:
    return ui.report.export_csv("log",query,left,fields,ns.db.log.crdate,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.log_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.log.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.log.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=None,
             orderby=ns.db.log.crdate, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_log","0,1,2")
  return dict(form=form)

@ns_auth.requires_login()
def find_movement_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.movement_fields_filter=None
    redirect(URL("find_movement_fields"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_movement_fields")+20:]
    redirect(URL(ruri))
  
  response.browsertype=T('Stock Browser')
  response.subtitle=T('Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_movement_fields","find_movement_fields/excel"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_movement_fields","find_movement_fields/csv"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_lorry.png')
    response.export_excel = ruri.replace("find_movement_fields","find_movement_fields/excel")
    response.export_csv = ruri.replace("find_movement_fields","find_movement_fields/csv")
  ui.menu.set_find_movement_menu()
  response.filter_form = ui.select.get_fields_filter("trans","movement_fields_filter",["invtype","direction","transtate"])
  
  nervatype_trans = ns.valid.get_groups_id("nervatype", "trans")
  htab = ns.db.trans.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(ns.db.fieldvalue.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_trans)))]
  query = (ns.db.fieldvalue.deleted==0)
  query = query & ((htab.deleted==0))
  where = ui.select.get_filter_query(sfilter=session.movement_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  #set transtype
  query = query & (htab.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("delivery","inventory","waybill","production","formula"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~htab.transtype.belongs(audit))
  
  #set transfilter
  query = ui.select.set_transfilter(query,htab)
        
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id, htab.transnumber, ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  if ruri.find("find_movement_fields/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,htab.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_movement_fields/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,htab.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.movement_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
  
  if session.mobile:
    htab.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
    field_id=htab.id
  else:
    editable=True
    field_id=ns.db.fieldvalue.id
  form = SimpleGrid.grid(query=query, field_id=field_id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,2,3")
  return dict(form=form)

@ns_auth.requires_login()
def find_movement_formula():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.movement_formula_filter=None
    redirect(URL("find_movement_formula"))
  
  if ruri.find("new")>0:
    redirect(URL('frm_trans/new/trans/formula/transfer'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_movement_formula")+21:]
    redirect(URL(ruri))
            
  response.browsertype=T('Stock Browser')
  response.subtitle=T('Formula')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_movement_formula","find_movement_formula/excel"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_movement_formula","find_movement_formula/csv"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_formula.png')
    response.export_excel = ruri.replace("find_movement_formula","find_movement_formula/excel")
    response.export_csv = ruri.replace("find_movement_formula","find_movement_formula/csv")
  ui.menu.set_find_movement_menu()
  
  if session.mobile:
    fields = [ns.db.trans.transnumber, ns.db.movement.movetype, ns.db.product.partnumber, 
            ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.qty, ns.db.movement.notes,
            ns.db.movement.place_id, ns.db.movement.shared]
  else:
    fields = [ns.db.movement.trans_id, ns.db.movement.movetype, ns.db.product.partnumber, 
            ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.qty, ns.db.movement.notes,
            ns.db.movement.place_id, ns.db.movement.shared]
  join = [(ns.db.product.on((ns.db.movement.product_id==ns.db.product.id))),
          (ns.db.trans.on((ns.db.movement.trans_id==ns.db.trans.id)&(ns.db.trans.deleted==0)))]
  left = None 
    
  transtype_formula = ns.valid.get_groups_id("transtype", "formula")
  query = ((ns.db.movement.deleted==0)&(ns.db.trans.transtype==transtype_formula))
  
  ui.select.init_sfilter("movement_formula_filter")
  where = ui.select.get_filter_query(sfilter=session.movement_formula_filter,table="movement",query=query)
  query = where["query"]
  having = where["having"] 
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = ui.select.set_transfilter(query)
  
  ns.db.movement.place_id.label = T("Warehouse No.")
  ns.db.movement.movetype.label = T("Type")
  ns.db.movement.movetype.represent = lambda value,row: T("in") if ns.db.groups(id=value).groupvalue=="head" else T("out")
  
  if ruri.find("find_movement_formula/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,ns.db.product.partnumber,request.vars.keywords,
                        join=join,groupfields=None,groupby=None,having=having)
  if ruri.find("find_movement_formula/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,ns.db.product.partnumber,request.vars.keywords,
                        join=join,groupfields=None,groupby=None,having=having)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.movement_formula_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.movement.id==-1))
  
  quick_total={"qty":0}
  total_rows = ns.db(query).select(*[ns.db.movement.qty.sum().with_alias('qty')],
                      join=join,left=left,groupby=None,having=having).as_list()
  for row in total_rows:
    if row["qty"]:
      quick_total["qty"]+=row["qty"]
  response.filter_form = ui.select.create_filter_form(
    sfilter_name="movement_formula_filter",state_fields=["headtype","transtate"],
    bool_fields={"bool_fields_name":[ns.db.movement.shared.name],
                 "bool_fields_label":[ns.db.movement.shared.label]},
    date_fields=None,
    number_fields={"number_fields_name":[ns.db.movement.qty.name],
                   "number_fields_label":[ns.db.movement.qty.label]},
    data_fields={"data_fields_name":[ns.db.movement.trans_id.name, ns.db.movement.place_id.name, ns.db.product.partnumber.name, 
                                     ns.db.movement.product_id.name, ns.db.product.unit.name, ns.db.movement.notes.name],
                 "data_fields_label":[ns.db.movement.trans_id.label, ns.db.movement.place_id.label, ns.db.product.partnumber.label, 
                                      ns.db.movement.product_id.label, ns.db.product.unit.label, ns.db.movement.notes.label]},
    quick_total=quick_total)
  
  if session.mobile:
    ns.db.trans.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.trans["id"])), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=having, join=join,
             orderby=ns.db.movement.id, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, create=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,1,2")
  return dict(form=form)

@ns_auth.requires_login()
def find_movement_groups():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.movement_groups_filter=None
    redirect(URL("find_movement_groups"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_movement_groups")+20:]
    redirect(URL(ruri))
  
  response.browsertype=T('Stock Browser')
  response.subtitle=T('Groups')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_movement_groups","find_movement_groups/excel"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_movement_groups","find_movement_groups/csv"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_lorry.png')
    response.export_excel = ruri.replace("find_movement_groups","find_movement_groups/excel")
    response.export_csv = ruri.replace("find_movement_groups","find_movement_groups/csv")
  ui.menu.set_find_movement_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="movement_groups_filter",state_fields=["invtype","direction"],
    bool_fields=None, date_fields=None, number_fields=None,
    data_fields={"data_fields_label":[ns.db.trans.transnumber.label,ns.db.groups.groupvalue.label,ns.db.groups.description.label],
                 "data_fields_name":["htab_trans_transnumber",ns.db.groups.groupvalue.name,ns.db.groups.description.name]})
  
  nervatype_trans = ns.valid.get_groups_id("nervatype", "trans")
  nervatype_groups = ns.valid.get_groups_id("nervatype", "groups")
  join = [(ns.db.link.on((ns.db.trans.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0))),
          (ns.db.groups.on((ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.ref_id_2==ns.db.groups.id)))]
  query = ((ns.db.trans.deleted==0)&(ns.db.groups.deleted==0))
  where = ui.select.get_filter_query(sfilter=session.movement_groups_filter,table="groups",query=query)
  query = where["query"]
  
  #set transtype
  query = query & (ns.db.trans.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("delivery","inventory","waybill","production","formula"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = ui.select.set_transfilter(query)
      
  fields = [ns.db.trans.transnumber,ns.db.groups.groupvalue,ns.db.groups.description]
  left = None
  if ruri.find("find_movement_groups/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_movement_groups/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.movement_groups_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
  
  if session.mobile:
    ns.db.trans.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.trans["id"])), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.trans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,1")
  return dict(form=form)

@ns_auth.requires_login()
def find_movement_inventory():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.movement_inventory_filter=None
    redirect(URL("find_movement_inventory"))
          
  response.browsertype=T('Stock Browser')
  response.subtitle=T('Inventory')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_movement_inventory","find_movement_inventory/excel"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_movement_inventory","find_movement_inventory/csv"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_lorry.png')
    response.export_excel = ruri.replace("find_movement_inventory","find_movement_inventory/excel")
    response.export_csv = ruri.replace("find_movement_inventory","find_movement_inventory/csv")
  ui.menu.set_find_movement_menu()
  
  movetype_inventory_id = ns.valid.get_groups_id("movetype", "inventory")
  fields = [ns.db.movement.place_id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes,
            ns.db.movement.qty, ns.db.movement.shippingdate]
  join = [(ns.db.product.on((ns.db.movement.product_id==ns.db.product.id))),
          (ns.db.trans.on((ns.db.movement.trans_id==ns.db.trans.id)&(ns.db.trans.deleted==0)))]
  left = None
  query = ((ns.db.movement.deleted==0)&(ns.db.movement.movetype==movetype_inventory_id))
  
  ui.select.init_sfilter("movement_inventory_filter")
  where = ui.select.get_filter_query(sfilter=session.movement_inventory_filter,table="movement",query=query)
  query = where["query"]
  having = (ns.db.movement.qty.sum()!=0)
  if where["having"]:
    having = having & where["having"]
  
  order = ns.db.movement.place_id
  if request.vars.order:
    if request.vars.order in("movement.qty","movement.shippingdate"):
      order = str(request.vars.order).split(".")[1]
    else:
      order = request.vars.order  
  
  ns.db.movement.place_id.label = T("Warehouse No.")
  ns.db.movement.qty.label = T("Stock")
  ns.db.movement.shippingdate.label = T("PosDate")
  ns.db.movement.shippingdate.represent = lambda value,row: ui.control.format_value("date",row["shippingdate"])  
  
  groupfields=[ns.db.movement.place_id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes,
               ns.db.movement.qty.sum().with_alias('qty'),ns.db.movement.shippingdate.max().with_alias('shippingdate')]
  groupby=[ns.db.movement.place_id|ns.db.product.partnumber|ns.db.movement.product_id|ns.db.product.unit|ns.db.movement.notes]  
  
  if ruri.find("find_movement_inventory/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,ns.db.product.partnumber,request.vars.keywords,
                        join=join,groupfields=groupfields,groupby=groupby,having=having)
  if ruri.find("find_movement_inventory/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,ns.db.product.partnumber,request.vars.keywords,
                        join=join,groupfields=groupfields,groupby=groupby,having=having)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.movement_inventory_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.movement.id==-1))
  quick_total={"qty":0}
  total_rows = ns.db(query).select(*[ns.db.movement.qty.sum().with_alias('qty')],
                      join=join,left=left,groupby=groupby,having=having).as_list()
  for row in total_rows:
    if row["qty"]:
      quick_total["qty"]+=row["qty"]
#   response.filter_form = get_find_movement_inventory_filter(quick_total)
  response.filter_form = ui.select.create_filter_form(
    sfilter_name="movement_inventory_filter",state_fields=["invtype","transtate"], bool_fields=None,
    date_fields={"date_fields_name":[ns.db.movement.shippingdate.name],
                 "date_fields_label":[ns.db.movement.shippingdate.label]},
    number_fields={"number_fields_name":["sqty"],
                   "number_fields_label":[ns.db.movement.qty.label]},
    data_fields={"data_fields_name":[ns.db.movement.place_id.name, ns.db.product.partnumber.name, ns.db.movement.product_id.name, 
                                     ns.db.product.unit.name, ns.db.movement.notes.name],
                 "data_fields_label":[ns.db.movement.place_id.label, ns.db.product.partnumber.label, ns.db.movement.product_id.label, 
                                      ns.db.product.unit.label, ns.db.movement.notes.label]},
    quick_total=quick_total)
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.movement.place_id, 
             fields=fields, groupfields=groupfields, groupby=groupby, left=left, having=having, join=join,
             orderby=order, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,1,2,3")
    
  return dict(form=form)

@ns_auth.requires_login()
def find_movement_product():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.movement_product_filter=None
    redirect(URL("find_movement_product"))
  
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_movement_product")+21:]
    redirect(URL(ruri))
            
  response.browsertype=T('Stock Browser')
  response.subtitle=T('Product Movement')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_movement_product","find_movement_product/excel"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_movement_product","find_movement_product/csv"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_lorry.png')
    response.export_excel = ruri.replace("find_movement_product","find_movement_product/excel")
    response.export_csv = ruri.replace("find_movement_product","find_movement_product/csv")
  ui.menu.set_find_movement_menu()
    
  iln = ns.db.link.with_alias('iln')
  itrn = ns.db.trans.with_alias('itrn')
  
  if session.mobile:
    fields = [ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, 
            ns.db.movement.shippingdate, ns.db.movement.place_id, ns.db.product.partnumber, 
            ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes, ns.db.movement.qty,
            ns.db.item.trans_id, itrn.customer_id]
  else:
    fields = [ns.db.trans.transtype, ns.db.trans.direction, ns.db.movement.trans_id, 
            ns.db.movement.shippingdate, ns.db.movement.place_id, ns.db.product.partnumber, 
            ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes, ns.db.movement.qty,
            ns.db.item.trans_id, itrn.customer_id]
  join = [(ns.db.product.on((ns.db.movement.product_id==ns.db.product.id))),
          (ns.db.trans.on((ns.db.movement.trans_id==ns.db.trans.id)&(ns.db.trans.deleted==0)))]
  
  nervatype_movement_id = ns.valid.get_groups_id("nervatype", "movement")
  nervatype_item_id = ns.valid.get_groups_id("nervatype", "item")
  left = [(iln.on((ns.db.movement.id==iln.ref_id_1)&(iln.nervatype_1==nervatype_movement_id)&(iln.deleted==0))),
          (ns.db.item.on((iln.nervatype_2==nervatype_item_id)&(iln.ref_id_2==ns.db.item.id))),
          (itrn.on((ns.db.item.trans_id==itrn.id)&(itrn.deleted==0)))]
  movetype_inventory_id = ns.valid.get_groups_id("movetype", "inventory")
  query = ((ns.db.movement.deleted==0)&(ns.db.movement.movetype==movetype_inventory_id))
  
  ui.select.init_sfilter("movement_product_filter")
  where = ui.select.get_filter_query(sfilter=session.movement_product_filter,table="movement",query=query)
  query = where["query"]
  having = where["having"] 
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = ui.select.set_transfilter(query)
  
  ns.db.movement.place_id.label = T("Warehouse No.")
  ns.db.movement.shippingdate.represent = lambda value,row: ui.control.format_value("date",row["shippingdate"])
  ns.db.item.trans_id.label = T("Ref.No.")    
  itrn.customer_id.label = T("Ref.Customer")
  
  if ruri.find("find_movement_product/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,ns.db.product.partnumber,request.vars.keywords,
                        join=join,groupfields=None,groupby=None,having=having)
  if ruri.find("find_movement_product/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,ns.db.product.partnumber,request.vars.keywords,
                        join=join,groupfields=None,groupby=None,having=having)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.movement_product_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.movement.id==-1))
  
  quick_total={"qty":0}
  total_rows = ns.db(query).select(*[ns.db.movement.qty.sum().with_alias('qty')],
                      join=join,left=left,groupby=None,having=having).as_list()
  for row in total_rows:
    if row["qty"]:
      quick_total["qty"]+=row["qty"]
#   response.filter_form = get_find_movement_product_filter(quick_total)
  response.filter_form = ui.select.create_filter_form(
    sfilter_name="movement_product_filter",state_fields=["invtype","direction","transtate"], bool_fields=None,
    date_fields={"date_fields_name":[ns.db.movement.shippingdate.name],
                 "date_fields_label":[ns.db.movement.shippingdate.label]},
    number_fields={"number_fields_name":[ns.db.movement.qty.name],
                   "number_fields_label":[ns.db.movement.qty.label]},
    data_fields={"data_fields_name":[ns.db.movement.trans_id.name, ns.db.movement.place_id.name, ns.db.product.partnumber.name, 
                                     ns.db.movement.product_id.name, ns.db.product.unit.name, ns.db.movement.notes.name,
                                     "refnumber", "refcust"],
                 "data_fields_label":[ns.db.movement.trans_id.label, ns.db.movement.place_id.label, ns.db.product.partnumber.label, 
                                      ns.db.movement.product_id.label, ns.db.product.unit.label, ns.db.movement.notes.label,
                                      ns.db.item.trans_id.label, itrn.customer_id.label]},
    quick_total=quick_total)
    
  if session.mobile:
    ns.db.trans.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.trans["id"])), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable=False
  else:
    editable=True
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=having, join=join,
             orderby=ns.db.movement.id, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,1,2,3")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_movement_tool():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.movement_tool_filter=None
    redirect(URL("find_movement_tool"))
    
  if ruri.find("new")>0:
    redirect(URL('frm_trans/new/trans/waybill/out'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_movement_tool")+18:]
    redirect(URL(ruri))
  response.browsertype=T('Stock Browser')
  response.subtitle=T('Tool Movement')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_movement_tool","find_movement_tool/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_movement_tool","find_movement_tool/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_wrench_page.png')
    response.export_excel = ruri.replace("find_movement_tool","find_movement_tool/excel")
    response.export_csv = ruri.replace("find_movement_tool","find_movement_tool/csv")
  ui.menu.set_find_movement_menu()
  
  ns.db.movement.notes.label = T('Additional info')
  ns.db.link.ref_id_2.label=T('Ref.No.')
  reftab = ns.db.trans.with_alias('reftab')
  
  response.filter_form = ui.select.create_filter_form(
    sfilter_name="movement_tool_filter",state_fields=["direction","transtate"], 
    bool_fields={"bool_fields_name":[ns.db.trans.closed.name],
                 "bool_fields_label":[ns.db.trans.closed.label]},
    date_fields={"date_fields_name":[ns.db.trans.crdate.name,ns.db.movement.shippingdate.name],
                 "date_fields_label":[ns.db.trans.crdate.label,ns.db.movement.shippingdate.label]},
    number_fields=None,
    data_fields={"data_fields_name":[ns.db.trans.transnumber.name, "htab_reftab_transnumber", "htab_customer_custname", 
                                     "htab_employee_empnumber", "htab_tool_serial", "htab_tool_description", 
                                     "htab_movement_notes", ns.db.trans.notes.name, ns.db.trans.intnotes.name],
                 "data_fields_label":[ns.db.trans.transnumber.label, ns.db.link.ref_id_2.label, ns.db.trans.customer_id.label, 
                                      ns.db.trans.employee_id.label, ns.db.movement.tool_id.label, ns.db.tool.description.label, 
                                      ns.db.movement.notes.label, ns.db.trans.notes.label, ns.db.trans.intnotes.label]})
  
  nervatype_trans = ns.valid.get_groups_id("nervatype", "trans")
  transtype_waybill = ns.valid.get_groups_id("transtype", "waybill")
  ns.db.link.ref_id_2.represent = lambda value,row: A(SPAN(ns.db.trans(id=int(value))["transnumber"]),
                     _href=URL(r=request, f="frm_trans/view/trans/"+str(value)), _target="_blank")
  join = [ns.db.movement.on((ns.db.trans.id==ns.db.movement.trans_id)&(ns.db.movement.deleted==0)),
          ns.db.tool.on((ns.db.movement.tool_id==ns.db.tool.id))]
  left = [ns.db.link.on((ns.db.trans.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0)
           &(ns.db.link.nervatype_2==nervatype_trans)),
          reftab.on((ns.db.link.ref_id_2==reftab.id)),
          ns.db.customer.on((ns.db.trans.customer_id==ns.db.customer.id)),
          ns.db.employee.on((ns.db.trans.employee_id==ns.db.employee.id))]
  query = ((ns.db.trans.deleted==0)&(ns.db.trans.transtype==transtype_waybill))
  where = ui.select.get_filter_query(sfilter=session.movement_tool_filter,table="trans",query=query)
  query = where["query"]
  
  #set transfilter
  query = ui.select.set_transfilter(query)
  
  fields = [ns.db.trans.transnumber, ns.db.trans.crdate,ns.db.trans.direction,ns.db.link.ref_id_2,ns.db.trans.customer_id,ns.db.trans.employee_id,
            ns.db.movement.shippingdate,ns.db.movement.tool_id,ns.db.tool.description,ns.db.movement.notes,
            ns.db.trans.transtate,ns.db.trans.closed,ns.db.trans.notes,ns.db.trans.intnotes]
  
  if ruri.find("find_movement_tool/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_movement_tool/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.movement_tool_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
  
  if session.mobile:
    ns.db.trans.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.trans["id"])), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.trans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, create=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,1,2")
      
  return dict(form=form)

@ns_auth.requires_login()
def find_payment_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.payment_fields_filter=None
    redirect(URL("find_payment_fields"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_payment_fields")+19:]
    redirect(URL(ruri))
  
  response.browsertype=T('Payment Browser')
  response.subtitle=T('Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_payment_fields","find_payment_fields/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_payment_fields","find_payment_fields/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
    response.export_excel = ruri.replace("find_payment_fields","find_payment_fields/excel")
    response.export_csv = ruri.replace("find_payment_fields","find_payment_fields/csv")
  ui.menu.set_find_payment_menu()
  response.filter_form = ui.select.get_fields_filter("trans","payment_fields_filter",["paymtype","direction","transtate","transcast"])
  
  nervatype_trans = ns.valid.get_groups_id("nervatype", "trans")
  transtype_cash_id = ns.valid.get_groups_id("transtype", "cash")
  htab = ns.db.trans.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(ns.db.fieldvalue.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_trans)))]
  query = (ns.db.fieldvalue.deleted==0)
  query = query & ((htab.deleted==0)|(htab.transtype==transtype_cash_id))
  where = ui.select.get_filter_query(sfilter=session.payment_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  #set transtype
  query = query & (htab.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("bank","cash"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~htab.transtype.belongs(audit))
    
  #set transfilter
  query = ui.select.set_transfilter(query,htab)
        
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id, htab.transnumber, ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  if ruri.find("find_payment_fields/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,htab.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_payment_fields/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,htab.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.payment_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
  
  if session.mobile:
    htab.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable = False
    field_id=htab.id
  else:
    editable = True
    field_id=ns.db.fieldvalue.id
      
  form = SimpleGrid.grid(query=query, field_id=field_id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,2,3")
    
  return dict(form=form)

@ns_auth.requires_login()
def find_payment_groups():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.payment_groups_filter=None
    redirect(URL("find_payment_groups"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_payment_groups")+19:]
    redirect(URL(ruri))
  
  response.browsertype=T('Payment Browser')
  response.subtitle=T('Groups')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_payment_groups","find_payment_groups/excel"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_payment_groups","find_payment_groups/csv"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
    response.export_excel = ruri.replace("find_payment_groups","find_payment_groups/excel")
    response.export_csv = ruri.replace("find_payment_groups","find_payment_groups/csv")
  ui.menu.set_find_payment_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="payment_groups_filter",state_fields=["paymtype","direction"],
    bool_fields=None, date_fields=None, number_fields=None,
    data_fields={"data_fields_name":["htab_trans_transnumber",ns.db.groups.groupvalue.name,ns.db.groups.description.name],
                 "data_fields_label":[ns.db.trans.transnumber.label,ns.db.groups.groupvalue.label,ns.db.groups.description.label]})
  
  nervatype_trans = ns.valid.get_groups_id("nervatype", "trans")
  nervatype_groups = ns.valid.get_groups_id("nervatype", "groups")
  transtype_cash_id = ns.valid.get_groups_id("transtype", "cash")
  join = [(ns.db.link.on((ns.db.trans.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0))),
          (ns.db.groups.on((ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.ref_id_2==ns.db.groups.id)))]
  query = ((ns.db.trans.deleted==0)|((ns.db.trans.transtype==transtype_cash_id)))
  where = ui.select.get_filter_query(sfilter=session.payment_groups_filter,table="groups",query=query)
  query = where["query"]
  
  #set transtype
  query = query & (ns.db.trans.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("cash","bank"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
    
  #set transfilter
  query = ui.select.set_transfilter(query)
      
  fields = [ns.db.trans.transnumber,ns.db.groups.groupvalue,ns.db.groups.description]
  left = None
  if ruri.find("find_payment_groups/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_payment_groups/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.payment_groups_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
  
  if session.mobile:
    ns.db.trans.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.trans["id"])), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True
      
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.trans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,1")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_payment_invoice():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.payment_invoice_filter=None
    redirect(URL("find_payment_invoice"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_payment_invoice")+20:]
    redirect(URL(ruri))
  
  response.browsertype=T('Payment Browser')
  response.subtitle=T('Invoice assignments')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_payment_invoice","find_payment_invoice/excel"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_payment_invoice","find_payment_invoice/csv"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_invoice.png')
    response.export_excel = ruri.replace("find_payment_invoice","find_payment_invoice/excel")
    response.export_csv = ruri.replace("find_payment_invoice","find_payment_invoice/csv")
  ui.menu.set_find_payment_menu()
  
  ptrans = ns.db.trans.with_alias('ptrans')
  itrans = ns.db.trans.with_alias('itrans')
  link_qty = ns.db.fieldvalue.with_alias('link_qty')
  link_rate = ns.db.fieldvalue.with_alias('link_rate')
  
  ptrans.place_id.label = T('BankAcc/Checkout')
  itrans.transnumber.label = T('Invoice No.')
  itrans.curr.label = T('Inv.Curr')
  link_qty.value.label = T('Amount')
  link_qty.value.represent = lambda value,row: ui.control.format_value("number",row["link_qty"]["value"])
  link_rate.value.label = T('Rate')
  link_rate.value.represent = lambda value,row: ui.control.format_value("number",row["link_rate"]["value"])
  
  nervatype_trans = ns.valid.get_groups_id("nervatype", "trans")
  nervatype_payment = ns.valid.get_groups_id("nervatype", "payment")
  transtype_cash_id = ns.valid.get_groups_id("transtype", "cash")
  
  join = [(ns.db.payment.on((ns.db.link.ref_id_1==ns.db.payment.id)&(ns.db.payment.deleted==0))),
          (ptrans.on((ns.db.payment.trans_id==ptrans.id)&((ptrans.deleted==0)|(ptrans.transtype==transtype_cash_id)))),
          (ns.db.place.on((ptrans.place_id==ns.db.place.id)&(ns.db.place.deleted==0))),
          (itrans.on((ns.db.link.ref_id_2==itrans.id)&(itrans.deleted==0))),
          (link_qty.on((ns.db.link.id==link_qty.ref_id)&(link_qty.fieldname=="link_qty")&(link_qty.deleted==0))),
          (link_rate.on((ns.db.link.id==link_rate.ref_id)&(link_rate.fieldname=="link_rate")&(link_rate.deleted==0)))]
  query = ((ns.db.link.deleted==0)&(ns.db.link.nervatype_1==nervatype_payment)&(ns.db.link.nervatype_2==nervatype_trans))
  
  ui.select.init_sfilter("payment_invoice_filter")
  where = ui.select.get_filter_query(sfilter=session.payment_invoice_filter,table="payment_invoice",query=query)
  query = where["query"]
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.ptrans.transtype.belongs(audit))
    
  #set transfilter
  query = ui.select.set_transfilter(query,ptrans)
  
  if session.mobile:
    fields = [ptrans.transnumber, ptrans.transtype, ptrans.direction, ns.db.payment.paiddate, ptrans.place_id,
            ns.db.place.curr, link_qty.value, link_rate.value, itrans.transnumber, itrans.curr]
  else:      
    fields = [ptrans.transtype, ptrans.direction, ns.db.payment.paiddate, ptrans.place_id, ptrans.transnumber,
            ns.db.place.curr, link_qty.value, link_rate.value, itrans.transnumber, itrans.curr]
  left = None
  if ruri.find("find_payment_invoice/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,ptrans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_payment_invoice/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,ptrans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.payment_invoice_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.payment.id==-1))
  
  quick_total={"amount":0}
  total_rows = ns.db(query).select(*[("sum(cast(link_qty.value as real))")],
                      join=join,left=left,groupby=None,having=None).as_list()
  if len(total_rows)>0:
    quick_total={"amount":total_rows[0].values()[0].values()[0]}
#   response.filter_form = get_find_payment_invoice_filter(quick_total)
  response.filter_form = ui.select.create_filter_form(sfilter_name="payment_invoice_filter",
    state_fields=["paymtype","direction","transtate"], bool_fields=None,
    date_fields={"date_fields_name":[ns.db.payment.paiddate.name],
                 "date_fields_label":[ns.db.payment.paiddate.label]},
    number_fields={"number_fields_name":["link_qty","link_rate"],
                   "number_fields_label":[link_qty.value.label, link_rate.value.label]},
    data_fields={"data_fields_name":["place", "docnumber", "doc_curr", "invnumber", "inv_curr"],
                 "data_fields_label":[ptrans.place_id.label, ptrans.transnumber.label, ns.db.place.curr.label, 
                                      itrans.transnumber.label, itrans.curr.label]},
    quick_total=quick_total)
  
  if session.mobile:
    ptrans.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.ptrans["id"])), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True
      
  form = SimpleGrid.grid(query=query, field_id=ptrans.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ptrans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,1")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_payment_payment():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.payment_payment_filter=None
    redirect(URL("find_payment_payment"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_payment_payment")+20:]
    redirect(URL(ruri))
    
  response.browsertype=T('Payment Browser')
  response.subtitle=T('Payments Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_payment_payment","find_payment_payment/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_payment_payment","find_payment_payment/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_money.png')
    response.export_excel = ruri.replace("find_payment_payment","find_payment_payment/excel")
    response.export_csv = ruri.replace("find_payment_payment","find_payment_payment/csv")
  ui.menu.set_find_payment_menu()
    
  transtype_cash_id = ns.valid.get_groups_id("transtype", "cash")
  join = [(ns.db.payment.on((ns.db.trans.id==ns.db.payment.trans_id)&(ns.db.payment.deleted==0))),
          (ns.db.place.on((ns.db.trans.place_id==ns.db.place.id)))]
  query = ((ns.db.trans.deleted==0)|(ns.db.trans.transtype==transtype_cash_id))
  ui.select.init_sfilter("payment_payment_filter")
  where = ui.select.get_filter_query(sfilter=session.payment_payment_filter,table="trans",query=query)
  query = where["query"]
  left = [(ns.db.fieldvalue.on((ns.db.trans.id==ns.db.fieldvalue.ref_id)&(ns.db.fieldvalue.fieldname=='trans_transcast')&(ns.db.fieldvalue.deleted==0)))]
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
    
  #set transfilter
  query = ui.select.set_transfilter(query)
      
  if session.mobile:
    fields = [ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, ns.db.fieldvalue.value, ns.db.trans.ref_transnumber, 
            ns.db.trans.crdate, ns.db.payment.paiddate, ns.db.trans.place_id, ns.db.place.curr, ns.db.payment.amount,
            ns.db.payment.notes, ns.db.trans.employee_id, ns.db.trans.transtate, ns.db.trans.closed, ns.db.trans.deleted, ns.db.trans.notes]
  else:
    fields = [ns.db.trans.transtype, ns.db.trans.direction, ns.db.fieldvalue.value, ns.db.payment.trans_id, ns.db.trans.ref_transnumber, 
            ns.db.trans.crdate, ns.db.payment.paiddate, ns.db.trans.place_id, ns.db.place.curr, ns.db.payment.amount,
            ns.db.payment.notes, ns.db.trans.employee_id, ns.db.trans.transtate, ns.db.trans.closed, ns.db.trans.deleted, ns.db.trans.notes]
  
  if ruri.find("find_payment_payment/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_payment_payment/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.payment_payment_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
  
  quick_total={"amount":0}
  total_rows = ns.db(query).select(*[ns.db.payment.amount.sum().with_alias('amount')],
                      join=join,left=left,groupby=None,having=None).as_list()
  if len(total_rows)>0:
    if total_rows[0]["amount"]:
      quick_total={"amount":total_rows[0]["amount"]}
#   response.filter_form = get_find_payment_payment_filter(quick_total)
  response.filter_form = ui.select.create_filter_form(sfilter_name="payment_payment_filter",
    state_fields=["paymtype","direction","transtate","transcast"],
    bool_fields={"bool_fields_name":[ns.db.trans.closed.name, ns.db.trans.deleted.name],
                 "bool_fields_label":[ns.db.trans.closed.label, ns.db.trans.deleted.label]},
    date_fields={"date_fields_name":[ns.db.trans.crdate.name, ns.db.payment.paiddate.name],
                 "date_fields_label":[ns.db.trans.crdate.label, ns.db.payment.paiddate.label]},
    number_fields={"number_fields_name":["paidamount"],
                   "number_fields_label":[ns.db.payment.amount.label]},
    data_fields={"data_fields_name":["transnumber", ns.db.trans.ref_transnumber.name, ns.db.trans.place_id.name, "place_curr", 
                                     "payment_description", ns.db.trans.employee_id.name, ns.db.trans.notes.name],
                 "data_fields_label":[ns.db.payment.trans_id.label, ns.db.trans.ref_transnumber.label, ns.db.trans.place_id.label, 
                                      ns.db.place.curr.label, ns.db.payment.notes.label, ns.db.trans.employee_id.label, 
                                      ns.db.trans.notes.label]},
    quick_total=quick_total)
  
  ns.db.fieldvalue.value.label = T('Doc.State')
  ns.db.trans.crdate.label = T('Date')
  ns.db.trans.place_id.label = T('BankAcc/Checkout')
  
  if session.mobile:
    ns.db.trans.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.trans["id"])), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable = False
  else:
    editable = True
      
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.trans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,1,2,3")
    
  return dict(form=form)

@ns_auth.requires_login()
def find_product_barcode():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.product_barcode_filter=None
    redirect(URL("find_product_barcode"))
    
  if ruri.find("new")>0:
    redirect(URL('frm_product/new/product'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_product"+ruri[ruri.find("find_product_barcode")+20:]
    redirect(URL(ruri))
  response.browsertype=T('Product Browser')
  response.subtitle=T('Barcodes')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_product_barcode","find_product_barcode/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_product_barcode","find_product_barcode/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_barcode.png')
    response.export_excel = ruri.replace("find_product_barcode","find_product_barcode/excel")
    response.export_csv = ruri.replace("find_product_barcode","find_product_barcode/csv")
  ui.menu.set_find_product_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="product_barcode_filter",state_fields=None,
    bool_fields={"bool_fields_name":[ns.db.barcode.defcode.name],
                 "bool_fields_label":[ns.db.barcode.defcode.label]},
    number_fields={"number_fields_name":[ns.db.barcode.qty.name],
                   "number_fields_label":[ns.db.barcode.qty.label]}, 
    date_fields=None,
    data_fields={"data_fields_name":["htab_product_partnumber","htab_product_description", ns.db.barcode.code.name, 
                                     ns.db.barcode.description.name, "htab_groups_groupvalue"],
                 "data_fields_label":[ns.db.product.partnumber.label, ns.db.product.description.label, ns.db.barcode.code.label, 
                                      ns.db.barcode.description.label, ns.db.barcode.barcodetype.label]})
  join = [ns.db.barcode.on((ns.db.barcode.product_id==ns.db.product.id)),
          ns.db.groups.on((ns.db.groups.id==ns.db.barcode.barcodetype))]
  left = None
  query = ((ns.db.product.deleted==0))
  where = ui.select.get_filter_query(sfilter=session.product_barcode_filter,table="barcode",query=query)
  query = where["query"]
  
  fields = [ns.db.product.partnumber, ns.db.barcode.product_id, ns.db.barcode.code,ns.db.barcode.description,
            ns.db.barcode.barcodetype,ns.db.barcode.qty,ns.db.barcode.defcode]
  
  if ruri.find("find_product_barcode/excel")>0:
    return ui.report.export_excel("product",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  if ruri.find("find_product_barcode/csv")>0:
    return ui.report.export_csv("product",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_barcode_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.product.id==-1))
  
  if session.mobile:
    ns.db.product.partnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_product/edit/product/"+str(row.product["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=ns.db.product.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.product.description, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_product","0,2,3")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_product_discount():
  audit_filter = ui.connect.get_audit_filter("price", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.product_discount_filter=None
    redirect(URL("find_product_discount"))
  
  product_id=None
  try:
    product_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if not ns.db.product(id=product_id):
      product_id=None
  except Exception:
    pass
  
  if ruri.find("edit/price")>0 or ruri.find("view/price")>0:
    price_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    product_id = ns.db.price(id=price_id).product_id
    redirect(URL('find_product_discount/view/product/'+str(product_id)))
    
  if ruri.find("delete/price")>0:
    price_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    product_id = ns.db.price(id=price_id).product_id
    if ns.connect.deleteData("price", ref_id=price_id): 
      redirect(URL('find_product_discount/view/product/'+str(product_id)))
  
  nervatype_price = ns.valid.get_groups_id("nervatype", "price")
  nervatype_customer = ns.valid.get_groups_id("nervatype", "customer")
  nervatype_groups = ns.valid.get_groups_id("nervatype", "groups")
  
  if request.post_vars["_formname"]=="price/create":
    ui.connect.clear_post_vars()
    if not request.post_vars.has_key("vendorprice"):
      request.post_vars["vendorprice"]=0
    else:
      request.post_vars["vendorprice"]=1
    customer_id = None
    if request.post_vars["customer_id"]!="":
      customer_id = request.post_vars["customer_id"]
    del request.post_vars["customer_id"]
    group_id = None
    if request.post_vars["group_id"]!="":
      group_id = request.post_vars["group_id"]
    del request.post_vars["group_id"]
    
    price_id = ns.connect.updateData("price", values=request.post_vars, validate=False, insert_row=True)
    if price_id:
      customer_links = ns.db((ns.db.link.ref_id_1==price_id)&(ns.db.link.nervatype_1==nervatype_price)
                      &(ns.db.link.nervatype_2==nervatype_customer)&(ns.db.link.deleted==0)).select()
      if customer_id:
        values = {"nervatype_1":nervatype_price, "ref_id_1":price_id, 
                  "nervatype_2":nervatype_customer, "ref_id_2":customer_id}
        if len(customer_links)>0: values["id"]=customer_links[0]["id"]
        link_id = ns.connect.updateData("link", values=values, validate=False, insert_row=True)
        if not link_id:
          response.flash = str(ns.error_message)
      else:
        for link in customer_links:
          ns.connect.deleteData("link", ref_id=link["id"])
      
      groups_links = ns.db((ns.db.link.ref_id_1==price_id)&(ns.db.link.nervatype_1==nervatype_price)
                      &(ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.deleted==0)).select()
      if group_id:
        values = {"nervatype_1":nervatype_price, "ref_id_1":price_id, 
                  "nervatype_2":nervatype_groups, "ref_id_2":group_id}
        if len(groups_links)>0: values["id"]=groups_links[0]["id"]
        link_id = ns.connect.updateData("link", values=values, validate=False, insert_row=True)
        if not link_id:
          response.flash = str(ns.error_message)
      else:
        for link in groups_links:
          ns.connect.deleteData("link", ref_id=link["id"])
          
      redirect()
    else:
      response.flash = str(ns.error_message)
  
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_product_discount","find_product_discount/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_product_discount","find_product_discount/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=price'),
                                             cformat=None, icon="info", iconpos="left", target="blank",
                                             style="margin:5px;")
  else:      
    response.titleicon = URL(ui.dir_images,'icon16_money.png')
    response.export_excel = ruri.replace("find_product_discount","find_product_discount/excel")
    response.export_csv = ruri.replace("find_product_discount","find_product_discount/csv")
  response.view=ui.dir_view+'/browser.html'
  
  custlink = ns.db.link.with_alias('custlink')
  ns.db.customer.id.represent = lambda value,row: A(SPAN(ns.db.customer(id=int(value))["custname"]),
                     _href=URL(r=request, f="frm_customer/view/customer/"+str(value)), _target="_blank")
  ns.db.customer.id.label=T('Customer')
  grouplink = ns.db.link.with_alias('grouplink')
  calcmode = ns.db.groups.with_alias('calcmode')
  ns.db.price.pricevalue.label = T("Limit")
    
  join = [ns.db.price.on((ns.db.price.product_id==ns.db.product.id)&(ns.db.price.deleted==0)&(ns.db.price.discount!=None)),
          calcmode.on((ns.db.price.calcmode==calcmode.id))]
  
  left = [custlink.on((ns.db.price.id==custlink.ref_id_1)&(custlink.nervatype_1==nervatype_price)
                            &(custlink.nervatype_2==nervatype_customer)&(custlink.deleted==0)),
          ns.db.customer.on((custlink.ref_id_2==ns.db.customer.id)&(ns.db.customer.deleted==0)),
          grouplink.on((ns.db.price.id==grouplink.ref_id_1)&(grouplink.nervatype_1==nervatype_price)
                            &(grouplink.nervatype_2==nervatype_groups)&(grouplink.deleted==0)),
          ns.db.groups.on((grouplink.ref_id_2==ns.db.groups.id)&(ns.db.groups.deleted==0))]
  
  if product_id:
    response.browsertype=T('DISCOUNT')
    response.lo_menu = []
    response.subtitle= ns.db.product(id=product_id).partnumber +" - "+ ns.db.product(id=product_id).description
    query = (ns.db.product.id==product_id)
    _sortable = False
    _orderby=ns.db.price.validfrom
    ns.db.groups.id.readable = False
    ns.db.customer.custname.readable = False
    response.edit_title = T("DISCOUNT")
    response.edit_form = SQLFORM(ns.db.price, submit_button=T("Save"),_id="frm_edit")
    response.edit_form.process()
    _field_id=ns.db.price.id
    def_calcmode = ns.valid.get_groups_id("calcmode", "amo")
    response.edit_id = INPUT(_name="id", _type="hidden", _value="", _id="edit_id")
    cust_groups = ns.db((ns.db.groups.groupname=="customer")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.groupvalue)
    response.cmb_groups = SELECT(*[OPTION(group.groupvalue, _value=group.id) for group in cust_groups], _id="price_group_id", _name="group_id")
    response.cmb_groups.insert(0, OPTION("", _value=""))
    if session.mobile:
      response.cmd_back = ui.control.get_mobil_button(label=T("PRODUCT"), href=URL("frm_product/view/product/"+str(product_id)), icon="back", 
                                           cformat="ui-btn-left", ajax="false")
      fields = [ns.db.price.id, ns.db.customer.id, ns.db.customer.custname, ns.db.groups.id, ns.db.groups.groupvalue, ns.db.price.validfrom,
              ns.db.price.validto,ns.db.price.calcmode,ns.db.price.curr, ns.db.price.qty, ns.db.price.pricevalue,
              ns.db.price.discount,ns.db.price.vendorprice]
      _links= None
      ns.db.price.id.label = T("*")
      ns.db.price.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, 
        icon="edit", style="text-align: left;", title=T("Edit Discount"),
        onclick="set_price("
         +str(row["price"]["id"])+",'"
         +str(row["price"]["validfrom"])+"','"
         +str(row["price"]["validto"])+"','"
         +str(row["price"]["curr"])+"',"
         +str(row["price"]["qty"])+","
         +str(row["price"]["pricevalue"])+","
         +str(row["price"]["discount"])+","
         +str(row["price"]["calcmode"])+","
         +str(row["price"]["vendorprice"])+",'"
         +str(row["groups"]["id"])+"','"
         +str(row["customer"]["id"])+"','"
         +str(row["customer"]["custname"])+"','"
         +json.dumps(str(T("Edit value")))[1:-1]+"')", theme="d")
      response.cmd_edit_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
        icon="back", ajax="true", theme="a",  
        onclick= "show_page('view_page');", rel="close")
      response.edit_items = TABLE(
                                  TR(TD(DIV(response.edit_form.custom.label.validfrom, _class="label")),
                                   TD(response.edit_form.custom.widget.validfrom)
                                   ),
                                TR(TD(DIV(response.edit_form.custom.label.validto, _class="label")),
                                   TD(response.edit_form.custom.widget.validto)
                                   ),
                                TR(TD(
                                      TABLE(TR(TD(DIV(response.edit_form.custom.label.curr, _class="label")),
                                               TD(response.edit_form.custom.widget.curr, _style="padding-left:10px;padding-right:10px;"),
                                               TD(DIV(response.edit_form.custom.label.vendorprice, _class="label")),
                                               TD(response.edit_form.custom.widget.vendorprice, _class="td_checkbox")
                                               ),
                                            _style="width: 100%;",_cellpadding="0px;", _cellspacing="0px;"),
                                      _colspan="2")),
                                TR(TD(DIV(response.edit_form.custom.label.qty, _class="label")),
                                   TD(response.edit_form.custom.widget.qty)
                                   ),
                                TR(TD(DIV(response.edit_form.custom.label.pricevalue, _class="label")),
                                   TD(response.edit_form.custom.widget.pricevalue)
                                   ),
                                TR(TD(DIV(T("Group"), _class="label")),
                                   TD(response.cmb_groups,
                                      INPUT(_name="product_id", _type="hidden", _value=product_id, _id="price_product_id"))
                                   ),
                                TR(TD(DIV(T("Customer"), _class="label"), _colspan="2")
                                   ),
                                TR(TD(INPUT(_name="customer_id", _type="hidden", _value="", _id="customer_id"),
                                      ui.select.get_customer_selector("")
                                      , _colspan="2")
                                   ),
                                TR(TD(DIV(response.edit_form.custom.label.calcmode, _class="label")),
                                   TD(response.edit_form.custom.widget.calcmode)
                                   ),
                                TR(TD(DIV(response.edit_form.custom.label.discount, _class="label")),
                                   TD(response.edit_form.custom.widget.discount)
                                   ),
                                _style="width: 100%;",_cellpadding="5px;", _cellspacing="0px;")
    else:
      response.cmd_back = ui.control.get_back_button(URL("frm_product/view/product/"+str(product_id)))
      fields = [ns.db.customer.id, ns.db.customer.custname, ns.db.groups.id, ns.db.groups.groupvalue, ns.db.price.validfrom,
              ns.db.price.validto,ns.db.price.calcmode,ns.db.price.curr, ns.db.price.qty, ns.db.price.pricevalue,
              ns.db.price.discount,ns.db.price.vendorprice]
      _links=[lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_price("
                           +str(row["price"]["id"])+",'"
                           +str(row["price"]["validfrom"])+"','"
                           +str(row["price"]["validto"])+"','"
                           +str(row["price"]["curr"])+"',"
                           +str(row["price"]["qty"])+","
                           +str(row["price"]["pricevalue"])+","
                           +str(row["price"]["discount"])+","
                           +str(row["price"]["calcmode"])+","
                           +str(row["price"]["vendorprice"])+",'"
                           +str(row["groups"]["id"])+"','"
                           +str(row["customer"]["id"])+"','"
                           +str(row["customer"]["custname"])+"','"
                           +json.dumps(str(T("Edit value")))[1:-1]+"')",
                           _title=T("Edit Discount")),
           lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this price?')+
                              "')){window.location ='"+URL("find_product_discount/delete/price/"+str(row["price"]["id"]))+"';};return false;", 
                         _title=T("Delete Price"))]
      response.edit_icon = URL(ui.dir_images,'icon16_money.png')
      response.cmd_edit_cancel = A(SPAN(_class="icon cross"), _id="cmd_edit_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_form').style.display = 'none';return true;")
      response.edit_items = DIV(
                            TABLE(TR(
                                 TD(DIV(response.edit_form.custom.label.validfrom, _class="label"),
                                    _style="padding: 8px 0px 2px 10px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.validfrom,
                                    _style="padding: 8px 10px 2px 15px;width: 80px;"),
                                 TD(DIV(response.edit_form.custom.label.validto, _class="label"),
                                    _style="padding: 8px 0px 2px 5px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.validto,
                                    _style="padding: 8px 10px 2px 15px;width: 80px;"),
                                 TD(DIV(response.edit_form.custom.label.curr, _class="label"),
                                    _style="padding: 8px 10px 2px 5px;width: 60px;"),
                                 TD(response.edit_form.custom.widget.curr,
                                    _style="padding: 8px 0px 2px 5px;width: 60px;"),
                                 TD(DIV(response.edit_form.custom.label.qty, _class="label"),
                                    _style="padding: 8px 10px 2px 5px;width: 60px;"),
                                 TD(response.edit_form.custom.widget.qty,
                                    _style="padding: 8px 0px 2px 5px;width: 60px;"),
                                 TD(DIV(response.edit_form.custom.label.pricevalue, _class="label"),
                                    _style="padding: 8px 10px 2px 15px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.pricevalue,
                                    _style="padding: 8px 15px 2px 5px;")
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;"),
                            TABLE(TR(
                                 TD(DIV(T("Group"),_style="width: 80px;", _class="label"),
                                    _style="padding: 8px 0px 2px 10px;width: 80px;"),
                                 TD(response.cmb_groups,
                                    INPUT(_name="product_id", _type="hidden", _value=product_id, _id="price_product_id"),
                                    _style="padding: 6px 5px 2px 5px;width: 175px;"),
                                 TD(DIV(T("Customer"),_style="width: 80px;", _class="label"),
                                    _style="padding: 8px 0px 2px 0px;width: 80px;"),
                                 TD(INPUT(_name="customer_id", _type="hidden", _value="", _id="customer_id"),ui.select.get_customer_selector(""),
                                    _style="padding: 6px 5px 2px 5px;"),
                                 TD(DIV(response.edit_form.custom.label.vendorprice,_style="width: 80px;", _class="label"),
                                    _style="padding: 7px 0px 5px 10px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.vendorprice,
                                    _style="padding: 3px 5px 9px 0px;width: 10px;")
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;"),
                            TABLE(TR(
                                 TD(DIV(response.edit_form.custom.label.calcmode, _class="label"),
                                    _style="padding: 8px 5px 10px 10px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.calcmode,
                                    _style="padding: 3px 5px 5px 10px;width: 175px;"),
                                 TD(DIV(response.edit_form.custom.label.discount, _class="label"),
                                    _style="padding: 8px 5px 10px 0px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.discount,
                                    _style="padding: 3px 5px 5px 10px;width: 135px;"),
                                 TD(DIV())
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;")
                            )
    
    if audit_filter!="readonly":
      if session.mobile:
        response.cmd_edit_update = ui.control.get_mobil_button(label=T("Save Discount"), href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="true", theme="b",
          onclick= "price_update();return true;")
      else:
        response.cmd_edit_update = ui.control.get_command_button(caption=T("Save"),title=T("Update price data"),color="008B00", _id="cmd_edit_submit",
                              cmd="price_update();return true;")
    
    if audit_filter=="all":
      if session.mobile:
        response.cmd_edit_delete = ui.control.get_mobil_button(label=T("Delete Discount"), href="#", 
          cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to delete this price?')+
                              "')){if(document.getElementById('edit_id').value>-1){window.location = '"
            +URL("find_product_discount")+"/delete/price/'+document.getElementById('edit_id').value;} else {show_page('view_page');}}")
        response.cmd_edit_new = ui.control.get_mobil_button(label=T("New Discount"), href="#", 
          cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
          onclick= "set_price(-1,'"+str(datetime.datetime.now().date())+"','','"+ns.connect.getSetting("default_currency")+"',0,0,0,"+str(def_calcmode)+",0,'','','','"+json.dumps(str(T("New value")))[1:-1]+"');", rel="close")
      else:
        response.cmd_edit_new = A(SPAN(_class="icon plus"), _id="cmd_edit_new", 
          _style="height: 15px;",
          _class="w2p_trap buttontext button", _href="#", _title=T('New Discount'), 
          _onclick= "set_price(-1,'"+str(datetime.datetime.now().date())+"','','"+ns.connect.getSetting("default_currency")+"',0,0,0,"+str(def_calcmode)+",0,'','','','"+json.dumps(str(T("New value")))[1:-1]+"');")
    else:
      response.cmd_edit_delete = ""
      response.cmd_edit_new = ""
    priority = "0,3,5,7"
  else:
    response.browsertype=T('Product Browser')
    response.subtitle=T('Discount')
    ui.menu.set_find_product_menu()
    response.filter_form = ui.select.create_filter_form(sfilter_name="product_discount_filter",state_fields=["pricetype"],
      bool_fields={"bool_fields_name":[ns.db.price.vendorprice.name],
                   "bool_fields_label":[ns.db.price.vendorprice.label]},
      number_fields={"number_fields_name":[ns.db.price.qty.name, ns.db.price.pricevalue.name, ns.db.price.discount.name],
                     "number_fields_label":[ns.db.price.qty.label, ns.db.price.pricevalue.label, ns.db.price.discount.label]}, 
      date_fields={"date_fields_name":[ns.db.price.validfrom.name, ns.db.price.validto.name],
                   "date_fields_label":[ns.db.price.validfrom.label, ns.db.price.validto.label]},
      data_fields={"data_fields_name":["htab_product_partnumber", "htab_product_description", "htab_product_unit", 
                                       "htab_customer_custname", "htab_groups_groupvalue", "htab_calcmode_groupvalue", 
                                       ns.db.price.curr.name],
                   "data_fields_label":[ns.db.product.partnumber.label, ns.db.product.description.label, ns.db.product.unit.label, 
                                        ns.db.customer.id.label, ns.db.groups.groupvalue.label, ns.db.price.calcmode.label, 
                                        ns.db.price.curr.label]})
    query = (ns.db.product.deleted==0)
    where = ui.select.get_filter_query(sfilter=session.product_discount_filter,table="price",query=query)
    query = where["query"]
    _sortable = True
    _orderby=ns.db.product.description
    if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_discount_filter)==0 and len(request.post_vars)==0:
      query = (query&(ns.db.product.id==-1))
    fields = [ns.db.product.partnumber, ns.db.price.product_id, ns.db.product.unit,ns.db.customer.id, ns.db.groups.groupvalue,
            ns.db.price.validfrom,ns.db.price.validto,
            ns.db.price.calcmode,ns.db.price.curr, ns.db.price.qty, ns.db.price.pricevalue,ns.db.price.discount,ns.db.price.vendorprice]
    _field_id=ns.db.product.id
    _links=None
    priority = "0,2,3"
    
  if ruri.find("find_product_discount/excel")>0:
    return ui.report.export_excel("price",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  if ruri.find("find_product_discount/csv")>0:
    return ui.report.export_csv("price",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  
  if session.mobile:
    ns.db.product.partnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("find_product_discount/edit/product/"+str(row.product["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    _sortable = True
    editable = False
  else:
    editable = _sortable
  form = SimpleGrid.grid(query=query, field_id=_field_id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.product.description, sortable=_sortable, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=_links)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_price",priority)
  return dict(form=form)

@ns_auth.requires_login()
def find_product_event():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.product_event_filter=None
    redirect(URL("find_product_event"))
  
  if ruri.find("new")>0:
    redirect(URL('frm_product/new/product'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_event"+ruri[ruri.find("find_product_event")+18:]
    redirect(URL(ruri))
  response.browsertype=T('Product Browser')
  response.subtitle=T('Events')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_product_event","find_product_event/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_product_event","find_product_event/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
    response.export_excel = ruri.replace("find_product_event","find_product_event/excel")
    response.export_csv = ruri.replace("find_product_event","find_product_event/csv")
  ui.menu.set_find_product_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="product_event_filter",state_fields=None,bool_fields=None,
    date_fields={"date_fields_name":[ns.db.event.fromdate.name,ns.db.event.todate.name],
                 "date_fields_label":[ns.db.event.fromdate.label,ns.db.event.todate.label]},
    number_fields=None,
    data_fields={"data_fields_name":[ns.db.event.calnumber.name, "htab_product_partnumber", "htab_product_description", 
                                     ns.db.event.eventgroup.name, ns.db.event.subject.name, ns.db.event.place.name, 
                                     ns.db.event.description.name],
                 "data_fields_label":[ns.db.event.calnumber.label, ns.db.product.partnumber.label, ns.db.product.description.label, 
                                      ns.db.event.eventgroup.label, ns.db.event.subject.label, ns.db.event.place.label, 
                                      ns.db.event.description.label]},
    more_data={"title":"Event Additional Data","caption":"Additional Data","url":URL('find_product_event_fields')})
  
  ns.db.event.ref_id.represent = lambda value,row: A(SPAN(ns.db.product(id=int(value))["description"]),
                     _href=URL(r=request, f="frm_product/view/product/"+str(value)), _target="_blank")
  ns.db.event.ref_id.label=T('Product')
  nervatype_product = ns.valid.get_groups_id("nervatype", "product")
  join = [(ns.db.event.on((ns.db.product.id==ns.db.event.ref_id)&(ns.db.event.nervatype==nervatype_product)&(ns.db.event.deleted==0)))]
  left = [(ns.db.groups.on((ns.db.event.eventgroup==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  query = ((ns.db.product.deleted==0))
  where = ui.select.get_filter_query(sfilter=session.product_event_filter,table="event",query=query)
  query = where["query"]
  
  fields = [ns.db.event.calnumber,ns.db.product.partnumber, ns.db.event.ref_id, ns.db.event.eventgroup,
            ns.db.event.fromdate,ns.db.event.todate,ns.db.event.subject,ns.db.event.place,ns.db.event.description]
  
  if ruri.find("find_product_event/excel")>0:
    return ui.report.export_excel("product",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  if ruri.find("find_product_event/csv")>0:
    return ui.report.export_csv("product",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_event_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.product.id==-1))
    
  if session.mobile:
    links = None
    ns.db.event.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_event/edit/event/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable = False
  else:
    links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("cmd_export_ical?id="+str(row.event.id)), _target="_blank", _title=T("Export Item"))]
    editable = True
  form = SimpleGrid.grid(query=query, field_id=ns.db.event.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.product.description, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=links)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_event","0,1,6")
  return dict(form=form)

@ns_auth.requires_login()
def find_product_event_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.product_event_fields_filter=None
    redirect(URL("find_product_event_fields"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_event"+ruri[ruri.find("find_product_event_fields")+25:]
    redirect(URL(ruri))
  
  response.browsertype=T('Product Browser')
  response.subtitle=T('Event Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_product_event_fields","find_product_event_fields/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_product_event_fields","find_product_event_fields/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
    response.export_excel = ruri.replace("find_product_event_fields","find_product_event_fields/excel")
    response.export_csv = ruri.replace("find_product_event_fields","find_product_event_fields/csv")
  ui.menu.set_find_product_menu()
  nervatype_event = ns.valid.get_groups_id("nervatype", "event")
  nervatype_product = ns.valid.get_groups_id("nervatype", "product")
  response.filter_form = ui.select.get_fields_filter("event","product_event_fields_filter")
  
  htab = ns.db.event.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(htab.nervatype==nervatype_product))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_event)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = ui.select.get_filter_query(sfilter=session.product_event_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.calnumber,htab.subject,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_product_event_fields/excel")>0:
    return ui.report.export_excel("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  if ruri.find("find_product_event_fields/csv")>0:
    return ui.report.export_csv("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_event_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
  
  if session.mobile:
    htab.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_event/edit/event/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.calnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_event","0,1,2")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_product_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.product_fields_filter=None
    redirect(URL("find_product_fields"))
  
  if ruri.find("new")>0:
    redirect(URL('frm_product/new/product'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_product"+ruri[ruri.find("find_product_fields")+19:]
    redirect(URL(ruri))
  response.browsertype=T('Product Browser')
  response.subtitle=T('Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_product_fields","find_product_fields/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_product_fields","find_product_fields/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_parts.png')
    response.export_excel = ruri.replace("find_product_fields","find_product_fields/excel")
    response.export_csv = ruri.replace("find_product_fields","find_product_fields/csv")
  ui.menu.set_find_product_menu()
  nervatype_product = ns.valid.get_groups_id("nervatype", "product")
  response.filter_form = ui.select.get_fields_filter("product","product_fields_filter")
  
  htab = ns.db.product.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_product)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = ui.select.get_filter_query(sfilter=session.product_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.partnumber,htab.description,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_product_fields/excel")>0:
    return ui.report.export_excel("product",query,left,fields,htab.description,request.vars.keywords,join=join)
  if ruri.find("find_product_fields/csv")>0:
    return ui.report.export_csv("product",query,left,fields,htab.description,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
  
  if session.mobile:
    htab.partnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_product/edit/product/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.description, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, create=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_product","0,2,3")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_product_groups():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.product_groups_filter=None
    redirect(URL("find_product_groups"))
  
  if ruri.find("new")>0:
    redirect(URL('frm_product/new/product'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_product"+ruri[ruri.find("find_product_groups")+19:]
    redirect(URL(ruri))
    
  response.browsertype=T('Product Browser')
  response.subtitle=T('Groups')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_product_groups","find_product_groups/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_product_groups","find_product_groups/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_parts.png')
    response.export_excel = ruri.replace("find_product_groups","find_product_groups/excel")
    response.export_csv = ruri.replace("find_product_groups","find_product_groups/csv")
  ui.menu.set_find_product_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="product_groups_filter",
    state_fields=None, bool_fields=None, date_fields=None, number_fields=None,
    data_fields={"data_fields_name":["htab_product_partnumber","htab_product_description",ns.db.groups.groupvalue.name,
                                     ns.db.groups.description.name],
                 "data_fields_label":[ns.db.product.partnumber.label,ns.db.product.description.label,ns.db.groups.groupvalue.label,
                                      ns.db.groups.description.label]})
  
  nervatype_product = ns.valid.get_groups_id("nervatype", "product")
  nervatype_groups = ns.valid.get_groups_id("nervatype", "groups")  
  join = [(ns.db.link.on((ns.db.product.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_product)&(ns.db.link.deleted==0))),
          (ns.db.groups.on((ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.ref_id_2==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  query = (ns.db.product.deleted==0)
  where = ui.select.get_filter_query(sfilter=session.product_groups_filter,table="groups",query=query)
  query = where["query"]
  fields = [ns.db.product.partnumber, ns.db.product.description,ns.db.groups.groupvalue,ns.db.groups.description]
  left = None
  
  if ruri.find("find_product_groups/excel")>0:
    return ui.report.export_excel("product",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  if ruri.find("find_product_groups/csv")>0:
    return ui.report.export_csv("product",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_groups_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.product.id==-1))
  
  if session.mobile:
    ns.db.product.partnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_product/edit/product/"+str(row.product["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=ns.db.product.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.product.description, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_product","0,2,3")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_product_price():
  audit_filter = ui.connect.get_audit_filter("price", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.product_price_filter=None
    redirect(URL("find_product_price"))
  
  product_id=None
  try:
    product_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if not ns.db.product(id=product_id):
      product_id=None
  except Exception:
    pass
  
  if ruri.find("edit/price")>0 or ruri.find("view/price")>0:
    price_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    product_id = ns.db.price(id=price_id).product_id
    redirect(URL('find_product_price/view/product/'+str(product_id)))
    
  if ruri.find("delete/price")>0:
    price_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    product_id = ns.db.price(id=price_id).product_id
    if ns.connect.deleteData("price", ref_id=price_id): 
      redirect(URL('find_product_price/view/product/'+str(product_id)))
  
  nervatype_price = ns.valid.get_groups_id("nervatype", "price")
  nervatype_customer = ns.valid.get_groups_id("nervatype", "customer")
  nervatype_groups = ns.valid.get_groups_id("nervatype", "groups")
        
  if request.post_vars["_formname"]=="price/create":
    ui.connect.clear_post_vars()
    if not request.post_vars.has_key("vendorprice"):
      request.post_vars["vendorprice"]=0
    else:
      request.post_vars["vendorprice"]=1
    customer_id = None
    if request.post_vars["customer_id"]!="":
      customer_id = request.post_vars["customer_id"]
    del request.post_vars["customer_id"]
    group_id = None
    if request.post_vars["group_id"]!="":
      group_id = request.post_vars["group_id"]
    del request.post_vars["group_id"]
    
    price_id = ns.connect.updateData("price", values=request.post_vars, validate=False, insert_row=True)
    if price_id:
      customer_links = ns.db((ns.db.link.ref_id_1==price_id)&(ns.db.link.nervatype_1==nervatype_price)
                      &(ns.db.link.nervatype_2==nervatype_customer)&(ns.db.link.deleted==0)).select()
      if customer_id:
        values = {"nervatype_1":nervatype_price, "ref_id_1":price_id, 
                  "nervatype_2":nervatype_customer, "ref_id_2":customer_id}
        if len(customer_links)>0: values["id"]=customer_links[0]["id"]
        link_id = ns.connect.updateData("link", values=values, validate=False, insert_row=True)
        if not link_id:
          response.flash = str(ns.error_message)
      else:
        for link in customer_links:
          ns.connect.deleteData("link", ref_id=link["id"])
      
      groups_links = ns.db((ns.db.link.ref_id_1==price_id)&(ns.db.link.nervatype_1==nervatype_price)
                      &(ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.deleted==0)).select()
      if group_id:
        values = {"nervatype_1":nervatype_price, "ref_id_1":price_id, 
                  "nervatype_2":nervatype_groups, "ref_id_2":group_id}
        if len(groups_links)>0: values["id"]=groups_links[0]["id"]
        link_id = ns.connect.updateData("link", values=values, validate=False, insert_row=True)
        if not link_id:
          response.flash = str(ns.error_message)
      else:
        for link in groups_links:
          ns.connect.deleteData("link", ref_id=link["id"])
          
      redirect()
    else:
      response.flash = str(ns.error_message)
    
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_product_price","find_product_price/excel"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_product_price","find_product_price/csv"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=price'),
                                               cformat=None, icon="info", iconpos="left", target="blank",
                                               style="margin:5px;")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_money.png')
    response.export_excel = ruri.replace("find_product_price","find_product_price/excel")
    response.export_csv = ruri.replace("find_product_price","find_product_price/csv")
  response.view=ui.dir_view+'/browser.html'
  
  custlink = ns.db.link.with_alias('custlink')
  ns.db.customer.id.represent = lambda value,row: A(SPAN(ns.db.customer(id=int(value))["custname"]),
                     _href=URL(r=request, f="frm_customer/view/customer/"+str(value)), _target="_blank")
  ns.db.customer.id.label=T('Customer')
  grouplink = ns.db.link.with_alias('grouplink')
  
  if product_id:
    response.browsertype=T('PRICE')
    response.lo_menu = []
    response.subtitle= ns.db.product(id=product_id).partnumber +" - "+ ns.db.product(id=product_id).description
    query = (ns.db.product.id==product_id)
    _sortable = False
    _orderby=ns.db.price.validfrom
    ns.db.groups.id.readable = False
    ns.db.customer.custname.readable = False
    def_calcmode = ns.valid.get_groups_id("calcmode", "amo")
    response.edit_title = T("PRICE")
    response.edit_form = SQLFORM(ns.db.price, submit_button=T("Save"),_id="frm_edit")
    response.edit_form.process()
    _field_id=ns.db.price.id
    response.edit_id = INPUT(_name="id", _type="hidden", _value="", _id="edit_id")
    cust_groups = ns.db((ns.db.groups.groupname=="customer")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.groupvalue)
    response.cmb_groups = SELECT(*[OPTION(group.groupvalue, _value=group.id) for group in cust_groups], _id="price_group_id", _name="group_id")
    response.cmb_groups.insert(0, OPTION("", _value=""))
    if session.mobile:
      response.cmd_back = ui.control.get_mobil_button(label=T("PRODUCT"), href=URL("frm_product/view/product/"+str(product_id)), icon="back", 
                                           cformat="ui-btn-left", ajax="false")
      fields = [ns.db.price.id, ns.db.customer.id, ns.db.customer.custname, ns.db.groups.id, ns.db.groups.groupvalue, ns.db.price.validfrom,ns.db.price.validto,ns.db.price.curr, 
              ns.db.price.qty, ns.db.price.pricevalue,ns.db.price.vendorprice]
      ns.db.price.id.label = T("*")
      ns.db.price.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, 
        icon="edit", style="text-align: left;", title=T("Edit Price"),
        onclick="set_price("
         +str(row["price"]["id"])+",'"
         +str(row["price"]["validfrom"])+"','"
         +str(row["price"]["validto"])+"','"
         +str(row["price"]["curr"])+"',"
         +str(row["price"]["qty"])+","
         +str(row["price"]["pricevalue"])+",'',"+str(def_calcmode)+","
         +str(row["price"]["vendorprice"])+",'"
         +str(row["groups"]["id"])+"','"
         +str(row["customer"]["id"])+"','"
         +str(row["customer"]["custname"])+"','"
         +json.dumps(str(T("Edit value")))[1:-1]+"')", theme="d")
      _links=None
      response.cmd_edit_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
        icon="back", ajax="true", theme="a",  
        onclick= "show_page('view_page');", rel="close")
      response.edit_items = TABLE(TR(TD(DIV(response.edit_form.custom.label.validfrom, _class="label")),
                                   TD(response.edit_form.custom.widget.validfrom)
                                   ),
                                TR(TD(DIV(response.edit_form.custom.label.validto, _class="label")),
                                   TD(response.edit_form.custom.widget.validto)
                                   ),
                                TR(TD(
                                      TABLE(TR(TD(DIV(response.edit_form.custom.label.curr, _class="label")),
                                               TD(response.edit_form.custom.widget.curr, _style="padding-left:10px;padding-right:10px;"),
                                               TD(DIV(response.edit_form.custom.label.vendorprice, _class="label")),
                                               TD(response.edit_form.custom.widget.vendorprice, _class="td_checkbox")
                                               ),
                                            _style="width: 100%;",_cellpadding="0px;", _cellspacing="0px;"),
                                      _colspan="2")),
                                TR(TD(DIV(response.edit_form.custom.label.qty, _class="label")),
                                   TD(response.edit_form.custom.widget.qty)
                                   ),
                                TR(TD(DIV(response.edit_form.custom.label.pricevalue, _class="label")),
                                   TD(response.edit_form.custom.widget.pricevalue)
                                   ),
                                TR(TD(DIV(T("Group"), _class="label")),
                                   TD(response.cmb_groups,
                                      INPUT(_name="product_id", _type="hidden", _value=product_id, _id="price_product_id"),
                                      INPUT(_name="calcmode", _type="hidden", _value=def_calcmode, _id="price_calcmode"),
                                      INPUT(_name="discount", _type="hidden", _value="", _id="price_discount"))
                                   ),
                                TR(TD(DIV(T("Customer"), _class="label"), _colspan="2")
                                   ),
                                TR(TD(INPUT(_name="customer_id", _type="hidden", _value="", _id="customer_id"),
                                      ui.select.get_customer_selector("")
                                      , _colspan="2")
                                   ),
                                _style="width: 100%;",_cellpadding="5px;", _cellspacing="0px;")
    else:
      response.cmd_back = ui.control.get_back_button(URL("frm_product/view/product/"+str(product_id)))
      fields = [ns.db.customer.id, ns.db.customer.custname, ns.db.groups.id, ns.db.groups.groupvalue, ns.db.price.validfrom,ns.db.price.validto,ns.db.price.curr, 
              ns.db.price.qty, ns.db.price.pricevalue,ns.db.price.vendorprice]
      _links=[lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_price("
                           +str(row["price"]["id"])+",'"
                           +str(row["price"]["validfrom"])+"','"
                           +str(row["price"]["validto"])+"','"
                           +str(row["price"]["curr"])+"',"
                           +str(row["price"]["qty"])+","
                           +str(row["price"]["pricevalue"])+",'',"+str(def_calcmode)+","
                           +str(row["price"]["vendorprice"])+",'"
                           +str(row["groups"]["id"])+"','"
                           +str(row["customer"]["id"])+"','"
                           +str(row["customer"]["custname"])+"','"
                           +json.dumps(str(T("Edit value")))[1:-1]+"')",
                           _title=T("Edit Price")),
           lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this price?')+
                              "')){window.location ='"+URL("find_product_price/delete/price/"+str(row["price"]["id"]))+"';};return false;", 
                         _title=T("Delete Price"))]
      response.edit_icon = URL(ui.dir_images,'icon16_money.png')
      response.cmd_edit_cancel = A(SPAN(_class="icon cross"), _id="cmd_edit_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_form').style.display = 'none';return true;")
      response.edit_items = DIV(
                            TABLE(TR(
                                 TD(DIV(response.edit_form.custom.label.validfrom, _class="label"),
                                    _style="padding: 8px 0px 2px 10px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.validfrom,
                                    _style="padding: 8px 10px 2px 15px;width: 80px;"),
                                 TD(DIV(response.edit_form.custom.label.validto, _class="label"),
                                    _style="padding: 8px 0px 2px 5px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.validto,
                                    _style="padding: 8px 10px 2px 15px;width: 80px;"),
                                 TD(DIV(response.edit_form.custom.label.curr, _class="label"),
                                    _style="padding: 8px 10px 2px 5px;width: 60px;"),
                                 TD(response.edit_form.custom.widget.curr,
                                    _style="padding: 8px 0px 2px 5px;width: 60px;"),
                                 TD(DIV(response.edit_form.custom.label.qty, _class="label"),
                                    _style="padding: 8px 10px 2px 5px;width: 60px;"),
                                 TD(response.edit_form.custom.widget.qty,
                                    _style="padding: 8px 0px 2px 5px;width: 60px;"),
                                 TD(DIV(response.edit_form.custom.label.pricevalue, _class="label"),
                                    _style="padding: 8px 10px 2px 15px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.pricevalue,
                                    _style="padding: 8px 15px 2px 5px;")
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;"),
                            TABLE(TR(
                                 TD(DIV(T("Group"),_style="width: 80px;", _class="label"),
                                    _style="padding: 8px 0px 10px 10px;width: 80px;"),
                                 TD(response.cmb_groups,
                                    INPUT(_name="product_id", _type="hidden", _value=product_id, _id="price_product_id"),
                                    INPUT(_name="calcmode", _type="hidden", _value=def_calcmode, _id="price_calcmode"),
                                    INPUT(_name="discount", _type="hidden", _value="", _id="price_discount"),
                                    _style="padding: 3px 5px 5px 5px;width: 175px;"),
                                 TD(DIV(T("Customer"),_style="width: 80px;", _class="label"),
                                    _style="padding: 8px 0px 10px 0px;width: 80px;"),
                                 TD(INPUT(_name="customer_id", _type="hidden", _value="", _id="customer_id"),ui.select.get_customer_selector(""),
                                    _style="padding: 3px 5px 5px 5px;"),
                                 TD(DIV(response.edit_form.custom.label.vendorprice,_style="width: 80px;", _class="label"),
                                    _style="padding: 8px 0px 10px 10px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.vendorprice,
                                    _style="padding: 3px 5px 9px 0px;width: 10px;")
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;")
                            )
    
    if audit_filter!="readonly":
      if session.mobile:
        response.cmd_edit_update = ui.control.get_mobil_button(label=T("Save Price"), href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="true", theme="b",
          onclick= "price_update();return true;")
      else:
        response.cmd_edit_update = ui.control.get_command_button(caption=T("Save"),title=T("Update price data"),color="008B00", _id="cmd_edit_submit",
                              cmd="price_update();return true;")
    if audit_filter=="all":
      if session.mobile:
        response.cmd_edit_delete = ui.control.get_mobil_button(label=T("Delete Price"), href="#", 
          cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to delete this price?')+
                              "')){if(document.getElementById('edit_id').value>-1){window.location = '"
            +URL("find_product_price")+"/delete/price/'+document.getElementById('edit_id').value;} else {show_page('view_page');}}")
        response.cmd_edit_new = ui.control.get_mobil_button(label=T("New Price"), href="#", 
          cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
          onclick= "set_price(-1,'"+str(datetime.datetime.now().date())+"','','"+ns.connect.getSetting("default_currency")+"',0,0,'',"+str(def_calcmode)+",0,'','','','"+json.dumps(str(T("New price")))[1:-1]+"');", rel="close")
      else:
        response.cmd_edit_new = A(SPAN(_class="icon plus"), _id="cmd_edit_new", 
          _style="height: 15px;",
          _class="w2p_trap buttontext button", _href="#", _title=T('New Price'), 
          _onclick= "set_price(-1,'"+str(datetime.datetime.now().date())+"','','"+ns.connect.getSetting("default_currency")+"',0,0,'',"+str(def_calcmode)+",0,'','','','"+json.dumps(str(T("New value")))[1:-1]+"');")
    else:
      response.cmd_edit_delete = ""
      response.cmd_edit_new = ""
    priority = "0,3,5,7"
  else:
    response.browsertype=T('Product Browser')
    response.subtitle=T('Price')
    ui.menu.set_find_product_menu()
    response.filter_form = ui.select.create_filter_form(sfilter_name="product_price_filter",state_fields=["pricetype"],
      bool_fields={"bool_fields_name":[ns.db.price.vendorprice.name],
                   "bool_fields_label":[ns.db.price.vendorprice.label]},
      number_fields={"number_fields_name":[ns.db.price.qty.name, ns.db.price.pricevalue.name],
                     "number_fields_label":[ns.db.price.qty.label, ns.db.price.pricevalue.label]}, 
      date_fields={"date_fields_name":[ns.db.price.validfrom.name, ns.db.price.validto.name],
                   "date_fields_label":[ns.db.price.validfrom.label, ns.db.price.validto.label]},
      data_fields={"data_fields_name":["htab_product_partnumber", "htab_product_description", "htab_product_unit", 
                                       "htab_customer_custname", "htab_groups_groupvalue", ns.db.price.curr.name],
                   "data_fields_label":[ns.db.product.partnumber.label, ns.db.product.description.label, ns.db.product.unit.label, 
                                        ns.db.customer.id.label, ns.db.groups.groupvalue.label, ns.db.price.curr.label]})
    query = (ns.db.product.deleted==0)
    where = ui.select.get_filter_query(sfilter=session.product_price_filter,table="price",query=query)
    query = where["query"]
    _sortable = True
    _orderby=ns.db.product.description
    if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_price_filter)==0 and len(request.post_vars)==0:
      query = (query&(ns.db.product.id==-1))
    fields = [ns.db.product.partnumber, ns.db.price.product_id, ns.db.product.unit, ns.db.customer.id, ns.db.groups.groupvalue,
            ns.db.price.validfrom,ns.db.price.validto,ns.db.price.curr, ns.db.price.qty, ns.db.price.pricevalue,ns.db.price.vendorprice]
    _field_id=ns.db.product.id
    _links=None
    priority = "0,2,3"
  
  join = [ns.db.price.on((ns.db.price.product_id==ns.db.product.id)&(ns.db.price.deleted==0)&(ns.db.price.discount==None))]
  
  left = [custlink.on((ns.db.price.id==custlink.ref_id_1)&(custlink.nervatype_1==nervatype_price)
                            &(custlink.nervatype_2==nervatype_customer)&(custlink.deleted==0)),
          ns.db.customer.on((custlink.ref_id_2==ns.db.customer.id)&(ns.db.customer.deleted==0)),
          grouplink.on((ns.db.price.id==grouplink.ref_id_1)&(grouplink.nervatype_1==nervatype_price)
                            &(grouplink.nervatype_2==nervatype_groups)&(grouplink.deleted==0)),
          ns.db.groups.on((grouplink.ref_id_2==ns.db.groups.id)&(ns.db.groups.deleted==0))]
  
  if ruri.find("find_product_price/excel")>0:
    return ui.report.export_excel("price",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  if ruri.find("find_product_price/csv")>0:
    return ui.report.export_csv("price",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  
  if session.mobile:
    ns.db.product.partnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("find_product_price/edit/product/"+str(row.product["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    _sortable = True
    editable = False
  else:
    editable = _sortable
  form = SimpleGrid.grid(query=query, field_id=_field_id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.product.description, sortable=_sortable, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=_links)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_price",priority)
  return dict(form=form)

@ns_auth.requires_login()
def find_product_product():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.product_product_filter=None
    redirect(URL("find_product_product"))
    
  if ruri.find("new")>0:
    redirect(URL('frm_product/new/product'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_product"+ruri[ruri.find("find_product_product")+20:]
    redirect(URL(ruri))
  response.browsertype=T('Product Browser')
  response.subtitle=T('Product Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_product_product","find_product_product/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_product_product","find_product_product/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_parts.png')
    response.export_excel = ruri.replace("find_product_product","find_product_product/excel")
    response.export_csv = ruri.replace("find_product_product","find_product_product/csv")
  ui.menu.set_find_product_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="product_product_filter",state_fields=None,
    bool_fields={"bool_fields_name":[ns.db.product.webitem.name, ns.db.product.inactive.name],
                 "bool_fields_label":[ns.db.product.webitem.label, ns.db.product.inactive.label]},
    number_fields=None, date_fields=None,
    data_fields={"data_fields_name":[ns.db.product.partnumber.name, ns.db.product.protype.name, ns.db.product.description.name, 
                                     ns.db.product.unit.name, ns.db.product.tax_id.name, ns.db.product.notes.name],
                 "data_fields_label":[ns.db.product.partnumber.label, ns.db.product.protype.label, ns.db.product.description.label, 
                                      ns.db.product.unit.label, ns.db.product.tax_id.label, ns.db.product.notes.label]})
  query = (ns.db.product.deleted==0)
  fields = [ns.db.product.partnumber, ns.db.product.protype, ns.db.product.description, ns.db.product.unit, 
            ns.db.product.tax_id, ns.db.product.notes, ns.db.product.webitem, ns.db.product.inactive]
  left = None
  where = ui.select.get_filter_query(sfilter=session.product_product_filter,table="product",query=query)
  query = where["query"]
  
  if ruri.find("find_product_product/excel")>0:
    return ui.report.export_excel("product",query,left,fields,ns.db.product.description,request.vars.keywords)
  if ruri.find("find_product_product/csv")>0:
    return ui.report.export_csv("product",query,left,fields,ns.db.product.description,request.vars.keywords)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_product_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.product.id==-1))
  
  if session.mobile:
    ns.db.product.partnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_product/edit/product/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True
  form = SimpleGrid.grid(query=query, field_id=ns.db.product.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=None,
             orderby=ns.db.product.description, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, create=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_product","0,2")
  return dict(form=form)

@ns_auth.requires_login()
def find_project_address():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.project_address_filter=None
    redirect(URL("find_project_address"))
    
  if ruri.find("new")>0:
    redirect(URL('frm_project/new/project'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_project"+ruri[ruri.find("find_project_address")+20:]
    redirect(URL(ruri))
  
  response.browsertype=T('Project Browser')
  response.subtitle=T('Addresses')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_project_address","find_project_address/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_project_address","find_project_address/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_address.png')
    response.export_excel = ruri.replace("find_project_address","find_project_address/excel")
    response.export_csv = ruri.replace("find_project_address","find_project_address/csv")
  ui.menu.set_find_project_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="project_address_filter",
    state_fields=None,bool_fields=None,date_fields=None,number_fields=None,
    data_fields={"data_fields_name":["htab_project_pronumber", "htab_project_description", ns.db.address.country.name, 
                                     ns.db.address.state.name, ns.db.address.zipcode.name, ns.db.address.city.name, 
                                     ns.db.address.street.name, ns.db.address.notes.name],
                 "data_fields_label":[ns.db.project.pronumber.label, ns.db.project.description.label, ns.db.address.country.label, 
                                      ns.db.address.state.label, ns.db.address.zipcode.label, ns.db.address.city.label, 
                                      ns.db.address.street.label, ns.db.address.notes.label]})
  
  nervatype_project = ns.valid.get_groups_id("nervatype", "project")
  join = [(ns.db.address.on((ns.db.project.id==ns.db.address.ref_id)&(ns.db.address.nervatype==nervatype_project)&(ns.db.address.deleted==0)))]
  query = (ns.db.project.deleted==0)
  where = ui.select.get_filter_query(sfilter=session.project_address_filter,table="address",query=query)
  query = where["query"]
  
  fields = [ns.db.address.id, ns.db.project.description,ns.db.address.country,ns.db.address.state,
            ns.db.address.zipcode,ns.db.address.city,ns.db.address.street,ns.db.address.notes]
  left = None
  if ruri.find("find_project_address/excel")>0:
    return ui.report.export_excel("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords,join=join)
  if ruri.find("find_project_address/csv")>0:
    return ui.report.export_csv("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.project_address_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.project.id==-1))
  
  ns.db.address.id.label = T("Address No.")
  if session.mobile:
    ns.db.address.id.represent = lambda value,row: ui.control.get_mobil_button(ns.valid.show_refnumber("refnumber","address", value), href=URL("frm_project/edit/project/"+str(row.project["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    ns.db.address.id.represent = lambda value,row: SPAN(ns.valid.show_refnumber("refnumber","address", value))  
    editable=True
  form = SimpleGrid.grid(query=query, field_id=ns.db.project.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.project.pronumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_project","0,5,6")
  return dict(form=form)

@ns_auth.requires_login()
def find_project_contact():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.project_contact_filter=None
    redirect(URL("find_project_contact"))
    
  if ruri.find("new")>0:
    redirect(URL('frm_project/new/project'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_project"+ruri[ruri.find("find_project_contact")+20:]
    redirect(URL(ruri))
  
  response.browsertype=T('Project Browser')
  response.subtitle=T('Contact persons')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_project_contact","find_project_contact/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_project_contact","find_project_contact/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_user.png')
    response.export_excel = ruri.replace("find_project_contact","find_project_contact/excel")
    response.export_csv = ruri.replace("find_project_contact","find_project_contact/csv")
  ui.menu.set_find_project_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="project_contact_filter",
    state_fields=None,bool_fields=None,date_fields=None,number_fields=None,
    data_fields={"data_fields_name":["htab_project_pronumber", "htab_project_description", ns.db.contact.firstname.name, 
                                     ns.db.contact.surname.name, ns.db.contact.status.name, ns.db.contact.phone.name, 
                                     ns.db.contact.fax.name, ns.db.contact.mobil.name, ns.db.contact.email.name, 
                                     ns.db.contact.notes.name],
                 "data_fields_label":[ns.db.project.pronumber.label, ns.db.project.description.label, ns.db.contact.firstname.label, 
                                      ns.db.contact.surname.label, ns.db.contact.status.label, ns.db.contact.phone.label, 
                                      ns.db.contact.fax.label, ns.db.contact.mobil.label, ns.db.contact.email.label, 
                                      ns.db.contact.notes.label]})
  
  nervatype_project = ns.valid.get_groups_id("nervatype", "project")
  join = [(ns.db.contact.on((ns.db.project.id==ns.db.contact.ref_id)&(ns.db.contact.nervatype==nervatype_project)&(ns.db.contact.deleted==0)))]
  query = (ns.db.project.deleted==0)
  where = ui.select.get_filter_query(sfilter=session.project_contact_filter,table="contact",query=query)
  query = where["query"]
  
  fields = [ns.db.contact.id, ns.db.project.description, ns.db.contact.firstname,ns.db.contact.surname,
            ns.db.contact.status,ns.db.contact.phone,ns.db.contact.fax,ns.db.contact.mobil,ns.db.contact.email,ns.db.contact.notes]
  left = None
  
  if ruri.find("find_project_contact/excel")>0:
    return ui.report.export_excel("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords,join=join)
  if ruri.find("find_project_contact/csv")>0:
    return ui.report.export_csv("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.project_contact_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.project.id==-1))
  
  ns.db.contact.id.label = T("Contact No.")
  if session.mobile:
    ns.db.contact.id.represent = lambda value,row: ui.control.get_mobil_button(ns.valid.show_refnumber("refnumber","contact", value), href=URL("frm_project/edit/project/"+str(row.project["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    ns.db.contact.id.represent = lambda value,row: SPAN(ns.valid.show_refnumber("refnumber","contact", value))  
    editable=True
  form = SimpleGrid.grid(query=query, field_id=ns.db.project.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.project.pronumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_project","0,2,3")
  
  return dict(form=form)
  
@ns_auth.requires_login()
def find_project_event():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.project_event_filter=None
    redirect(URL("find_project_event"))
    
  if ruri.find("new")>0:
    redirect(URL('frm_project/new/project'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_event"+ruri[ruri.find("find_project_event")+18:]
    redirect(URL(ruri))
    
  response.browsertype=T('Project Browser')
  response.subtitle=T('Events')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_project_event","find_project_event/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_project_event","find_project_event/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
    response.export_excel = ruri.replace("find_project_event","find_project_event/excel")
    response.export_csv = ruri.replace("find_project_event","find_project_event/csv")
  ui.menu.set_find_project_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="project_event_filter",state_fields=None,bool_fields=None,
    date_fields={"date_fields_name":[ns.db.event.fromdate.name,ns.db.event.todate.name],
                 "date_fields_label":[ns.db.event.fromdate.label,ns.db.event.todate.label]},
    number_fields=None,
    data_fields={"data_fields_name":[ns.db.event.calnumber.name, "htab_project_pronumber", "htab_project_description", 
                        ns.db.event.eventgroup.name, ns.db.event.subject.name, ns.db.event.place.name, ns.db.event.description.name],
                 "data_fields_label":[ns.db.event.calnumber.label, ns.db.project.pronumber.label, ns.db.project.description.label, 
                        ns.db.event.eventgroup.label, ns.db.event.subject.label, ns.db.event.place.label, ns.db.event.description.label]},
    more_data={"title":"Event Additional Data","caption":"Additional Data","url":URL('find_project_event_fields')})
  
  ns.db.event.ref_id.represent = lambda value,row: A(SPAN(ns.db.project(id=int(value))["pronumber"]),
                     _href=URL(r=request, f="frm_project/view/project/"+str(value)), _target="_blank")
  ns.db.event.ref_id.label=T('Project No.')
  nervatype_project = ns.valid.get_groups_id("nervatype", "project")
  
  join = [(ns.db.event.on((ns.db.project.id==ns.db.event.ref_id)&(ns.db.event.nervatype==nervatype_project)&(ns.db.event.deleted==0)))]
  left = [(ns.db.groups.on((ns.db.event.eventgroup==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  query = (ns.db.project.deleted==0)
  where = ui.select.get_filter_query(sfilter=session.project_event_filter,table="event",query=query)
  query = where["query"]
  
  fields = [ns.db.event.calnumber,ns.db.event.ref_id, ns.db.project.description, ns.db.event.eventgroup,
            ns.db.event.fromdate,ns.db.event.todate,ns.db.event.subject,ns.db.event.place,ns.db.event.description]
  if ruri.find("find_project_event/excel")>0:
    return ui.report.export_excel("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords,join=join)
  if ruri.find("find_project_event/csv")>0:
    return ui.report.export_csv("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.project_event_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.project.id==-1))
    
  if session.mobile:
    links = None
    ns.db.event.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_event/edit/event/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable=False
  else:
    links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("cmd_export_ical?id="+str(row.event.id)), _target="_blank", _title=T("Export Item"))]
    editable=True
  form = SimpleGrid.grid(query=query, field_id=ns.db.event.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.project.pronumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=links)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_event","0,1,6")
  return dict(form=form)

@ns_auth.requires_login()
def find_project_event_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.project_event_fields_filter=None
    redirect(URL("find_project_event_fields"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_event"+ruri[ruri.find("find_project_event_fields")+25:]
    redirect(URL(ruri))
  
  response.browsertype=T('Project Browser')
  response.subtitle=T('Event Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_project_event_fields","find_project_event_fields/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_project_event_fields","find_project_event_fields/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
    response.export_excel = ruri.replace("find_project_event_fields","find_project_event_fields/excel")
    response.export_csv = ruri.replace("find_project_event_fields","find_project_event_fields/csv")
  ui.menu.set_find_project_menu()
  nervatype_event = ns.valid.get_groups_id("nervatype", "event")
  nervatype_project = ns.valid.get_groups_id("nervatype", "project")
  response.filter_form = ui.select.get_fields_filter("event","project_event_fields_filter")
  
  htab = ns.db.event.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(htab.nervatype==nervatype_project))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_event)))]
  query = (ns.db.fieldvalue.deleted==0)
  where = ui.select.get_filter_query(sfilter=session.project_event_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.calnumber,htab.subject,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_project_event_fields/excel")>0:
    return ui.report.export_excel("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  if ruri.find("find_project_event_fields/csv")>0:
    return ui.report.export_csv("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.project_event_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
  
  if session.mobile:
    htab.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_event/edit/event/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.calnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_event","0,1,2")
  return dict(form=form)

@ns_auth.requires_login()
def find_project_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.project_fields_filter=None
    redirect(URL("find_project_fields"))
    
  if ruri.find("new")>0:
    redirect(URL('frm_project/new/project'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_project"+ruri[ruri.find("find_project_fields")+19:]
    redirect(URL(ruri))
  
  response.browsertype=T('Project Browser')
  response.subtitle=T('Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_project_fields","find_project_fields/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_project_fields","find_project_fields/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_date_edit.png')
    response.export_excel = ruri.replace("find_project_fields","find_project_fields/excel")
    response.export_csv = ruri.replace("find_project_fields","find_project_fields/csv")
  ui.menu.set_find_project_menu()
  nervatype_project = ns.valid.get_groups_id("nervatype", "project")
  response.filter_form = ui.select.get_fields_filter("project","project_fields_filter")
  
  htab = ns.db.project.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_project)))]
  query = (ns.db.fieldvalue.deleted==0)
  where = ui.select.get_filter_query(sfilter=session.project_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.pronumber,htab.description,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_project_fields/excel")>0:
    return ui.report.export_excel("project",query,left,fields,htab.pronumber,request.vars.keywords,join=join)
  if ruri.find("find_project_fields/csv")>0:
    return ui.report.export_csv("project",query,left,fields,htab.pronumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.project_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
  
  if session.mobile:
    htab.pronumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_project/edit/project/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.pronumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, create=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_pronumber","0,2,3")
  return dict(form=form)

@ns_auth.requires_login()
def find_project_project():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.project_project_filter=None
    redirect(URL("find_project_project"))
    
  if ruri.find("new")>0:
    redirect(URL('frm_project/new/project'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_project"+ruri[ruri.find("find_project_project")+20:]
    redirect(URL(ruri))
    
  response.browsertype=T('Project Browser')
  response.subtitle=T('Project Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_project_project","find_project_project/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_project_project","find_project_project/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_date_edit.png')
    response.export_excel = ruri.replace("find_project_project","find_project_project/excel")
    response.export_csv = ruri.replace("find_project_project","find_project_project/csv")
  ui.menu.set_find_project_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="project_project_filter",state_fields=None,
    bool_fields={"bool_fields_name":[ns.db.project.inactive.name],
                 "bool_fields_label":[ns.db.project.inactive.label]},
    date_fields={"date_fields_name":[ns.db.project.startdate.name, ns.db.project.enddate.name],
                 "date_fields_label":[ns.db.project.startdate.label, ns.db.project.enddate.label]},
    number_fields=None,
    data_fields={"data_fields_name":[ns.db.project.pronumber.name, ns.db.project.description.name, ns.db.project.customer_id.name, 
                                     ns.db.project.notes.name],
                 "data_fields_label":[ns.db.project.pronumber.label, ns.db.project.description.label, ns.db.project.customer_id.label, 
                                      ns.db.project.notes.label]})
  
  query = ((ns.db.project.deleted==0))
  where = ui.select.get_filter_query(sfilter=session.project_project_filter,table="project",query=query)
  query = where["query"]
  
  fields = [ns.db.project.pronumber, ns.db.project.description, ns.db.project.customer_id, ns.db.project.startdate, 
            ns.db.project.enddate, ns.db.project.inactive, ns.db.project.notes]
  left = None
  if ruri.find("find_project_project/excel")>0:
    return ui.report.export_excel("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords)
  if ruri.find("find_project_project/csv")>0:
    return ui.report.export_csv("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.project_project_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.project.id==-1))
  
  if session.mobile:
    ns.db.project.pronumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_project/edit/project/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True
  form = SimpleGrid.grid(query=query, field_id=ns.db.project.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=None,
             orderby=ns.db.project.pronumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, create=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_project","0,1,2,4")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_rate():
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.rate_filter=None
    redirect(URL("find_rate"))
  
  if ruri.find("edit/rate")>0 or ruri.find("view/rate")>0:
    redirect(URL('find_rate'))
    
  if ruri.find("delete/rate")>0:
    rate_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ns.connect.deleteData("rate", ref_id=rate_id):
      redirect(URL('find_rate'))
        
  if request.post_vars["_formname"]=="rate/create":
    ui.connect.clear_post_vars()
    row_id = ns.connect.updateData("rate", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      redirect()
        
  response.browsertype=T('Rate Browser')
  response.subtitle=T('Interest and Exchange Rate')
  response.view=ui.dir_view+'/browser.html'
  response.lo_menu = []
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_rate","find_rate/excel"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_rate","find_rate/csv"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=rate'),
                                               cformat=None, icon="info", iconpos="left", target="blank",
                                               style="margin:5px;")
    response.cmd_edit_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
        icon="back", ajax="true", theme="a",  
        onclick= "show_page('view_page');", rel="close")
    fields = [ns.db.rate.id, ns.db.rate.ratetype,ns.db.rate.ratedate,ns.db.rate.curr,ns.db.rate.ratevalue,ns.db.rate.rategroup,ns.db.rate.place_id]
    links = None
    ns.db.rate.id.label = T("*")
    ns.db.rate.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, 
      icon="edit", style="text-align: left;", title=T("Edit Rate"),
      onclick="set_rate("+str(row["id"])+","
                         +str(row["ratetype"])+",'"
                         +str(row["ratedate"])+"','"
                         +str(row["curr"])+"','"
                         +str(row["place_id"])+"','"
                         +str(row["rategroup"])+"',"
                         +str(row["ratevalue"])+",'"
                         +json.dumps(str(T("Edit value")))[1:-1]+"')", theme="d")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_percent.png')
    response.export_excel = ruri.replace("find_rate","find_rate/excel")
    response.export_csv = ruri.replace("find_rate","find_rate/csv")
    response.edit_icon = URL(ui.dir_images,'icon16_percent.png')
    response.cmd_edit_cancel = A(SPAN(_class="icon cross"), _id="cmd_edit_cancel", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_form').style.display = 'none';document.getElementById('filter_div').style.display = 'block';return true;")
    fields = [ns.db.rate.ratetype,ns.db.rate.ratedate,ns.db.rate.curr,ns.db.rate.ratevalue,ns.db.rate.rategroup,ns.db.rate.place_id]
    links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_rate("
                           +str(row["id"])+","
                           +str(row["ratetype"])+",'"
                           +str(row["ratedate"])+"','"
                           +str(row["curr"])+"','"
                           +str(row["place_id"])+"','"
                           +str(row["rategroup"])+"',"
                           +str(row["ratevalue"])+",'"
                           +json.dumps(str(T("Edit value")))[1:-1]+"')",
                           _title=T("Edit Rate"))]
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="rate_filter",state_fields=["ratetype"],bool_fields=None,
    date_fields={"date_fields_name":[ns.db.rate.ratedate.name],
                 "date_fields_label":[ns.db.rate.ratedate.label]},
    number_fields={"number_fields_name":[ns.db.rate.ratevalue.name],
                   "number_fields_label":[ns.db.rate.ratevalue.label]},
    data_fields={"data_fields_name":[ns.db.rate.curr.name,ns.db.rate.rategroup.name,ns.db.rate.place_id.name],
                 "data_fields_label":[ns.db.rate.curr.label,ns.db.rate.rategroup.label,ns.db.rate.place_id.label]})
  join = None
  left = None
  query = (ns.db.rate.deleted==0)
  where = ui.select.get_filter_query(sfilter=session.rate_filter,table="rate",query=query)
  query = where["query"]
  
  if ruri.find("find_rate/excel")>0:
    return ui.report.export_excel("rate",query,left,fields,ns.db.rate.ratedate,request.vars.keywords,join=join)
  if ruri.find("find_rate/csv")>0:
    return ui.report.export_csv("rate",query,left,fields,ns.db.rate.ratedate,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.rate_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.rate.id==-1))
  
  if audit_filter!="readonly":
    if session.mobile:
      response.cmd_edit_update = ui.control.get_mobil_button(label=T("Save Rate"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="true", theme="b",
        onclick= "rate_update();return true;")
    else:
      response.cmd_edit_update = ui.control.get_command_button(caption=T("Save"),title=T("Update rate data"),color="008B00", _id="cmd_edit_submit",
                              cmd="rate_update();return true;")
  else:
    response.cmd_edit_update = ""  
  if audit_filter=="all":
    if session.mobile:
      response.cmd_edit_delete = ui.control.get_mobil_button(label=T("Delete Rate"), href="#", 
        cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
        onclick= "if(confirm('"+T('Are you sure you want to delete this rate?')+
                            "')){if(document.getElementById('edit_id').value>-1){window.location = '"
          +URL("find_rate")+"/delete/rate/'+document.getElementById('edit_id').value;} else {show_page('view_page');}}")
      response.cmd_edit_new = ui.control.get_mobil_button(label=T("New Rate"), href="#", 
        cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
        onclick= "set_rate(-1,'','"+str(datetime.datetime.now().date())+"','"+ns.connect.getSetting("default_currency")+"','','',0,'"+json.dumps(str(T("New value")))[1:-1]+"');", rel="close")
    else:
      links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this rate?')+
                              "')){window.location ='"+URL("find_rate/delete/rate/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Rate")))
      response.cmd_edit_new = A(SPAN(_class="icon plus"), _id="cmd_edit_new", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('New Rate'), 
        _onclick= "set_rate(-1,'','"+str(datetime.datetime.now().date())+"','"+ns.connect.getSetting("default_currency")+"','','',0,'"+json.dumps(str(T("New value")))[1:-1]+"');")
  else:
    response.cmd_edit_new = ""
    response.cmd_edit_delete = ""
  
  response.edit_form = SQLFORM(ns.db.rate, submit_button=T("Save"),_id="frm_edit")
  response.edit_form.process()
  response.edit_title = T("RATE")
  response.edit_id = INPUT(_name="id", _type="hidden", _value="", _id="edit_id")
  if session.mobile:
    response.edit_items = DIV(
                            TABLE(
                                  TR(TD(DIV(response.edit_form.custom.label.ratetype, _class="label")),
                                     TD(response.edit_form.custom.widget.ratetype)),
                                  TR(TD(DIV(response.edit_form.custom.label.ratedate, _class="label")),
                                     TD(response.edit_form.custom.widget.ratedate)),
                                  TR(TD(DIV(response.edit_form.custom.label.curr,_class="label")),
                                     TD(response.edit_form.custom.widget.curr)),
                                  TR(TD(DIV(response.edit_form.custom.label.ratevalue,_class="label")),
                                     TD(response.edit_form.custom.widget.ratevalue)),
                              _style="padding: 0px;margin: 0px;width: 100%;"),
                            TABLE(
                                  TR(TD(DIV(response.edit_form.custom.label.rategroup, _class="label")),
                                     TD(response.edit_form.custom.widget.rategroup)),
                                  TR(TD(DIV(response.edit_form.custom.label.place_id,_style="width: 120px;", _class="label")),
                                     TD(response.edit_form.custom.widget.place_id)),
                              _style="padding: 0px;margin: 0px;width: 100%;")
                            )
  else:
    response.edit_items = DIV(
                            TABLE(TR(
                                 TD(DIV(response.edit_form.custom.label.ratetype, _class="label"),
                                    _style="padding: 8px 5px 2px 10px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.ratetype,
                                    _style="padding: 8px 0px 2px 10px;width: 100px;"),
                                 TD(DIV(response.edit_form.custom.label.ratedate, _class="label"),
                                    _style="padding: 8px 5px 2px 5px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.ratedate,
                                    _style="padding: 8px 10px 2px 10px;width: 90px;"),
                                 TD(DIV(response.edit_form.custom.label.curr, _class="label"),
                                    _style="padding: 8px 5px 2px 5px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.curr,
                                    _style="padding: 8px 0px 2px 10px;width: 80px;"),
                                 TD(DIV(response.edit_form.custom.label.ratevalue, _class="label"),
                                    _style="padding: 8px 5px 2px 5px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.ratevalue,
                                    _style="padding: 8px 20px 2px 10px;")
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;"),
                            TABLE(TR(
                                 TD(DIV(response.edit_form.custom.label.rategroup, _class="label"),
                                    _style="padding: 8px 5px 10px 10px;width: 80px;"),
                                 TD(response.edit_form.custom.widget.rategroup,
                                    _style="padding: 8px 0px 10px 10px;width: 275px;"),
                                 TD(ui.control.get_goprop_button(title=T("Edit Groups"), url=URL("frm_groups_rategroup?back=1")),
                                    _style="padding: 8px 0px 10px 5px;width: 12px;"),
                                 TD(DIV(response.edit_form.custom.label.place_id, _class="label"),
                                    _style="padding: 8px 5px 10px 0px;width: 120px;"),
                                 TD(response.edit_form.custom.widget.place_id,
                                    _style="padding: 8px 20px 10px 10px;")
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;")
                            )
      
  form = SimpleGrid.grid(query=query, field_id=ns.db.rate.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=None,
             orderby=ns.db.rate.ratedate, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=False, deletable=False, links=links)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_rate","0,1,2,3")
  return dict(form=form)

@ns_auth.requires_login()
def find_tool_event():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.tool_event_filter=None
    redirect(URL("find_tool_event"))
  
  if ruri.find("new")>0:
    redirect(URL('frm_tool/new/tool'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_event"+ruri[ruri.find("find_tool_event")+15:]
    redirect(URL(ruri))
  
  response.browsertype=T('Tool Browser')
  response.subtitle=T('Events')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_tool_event","find_tool_event/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_tool_event","find_tool_event/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
    response.export_excel = ruri.replace("find_tool_event","find_tool_event/excel")
    response.export_csv = ruri.replace("find_tool_event","find_tool_event/csv")
  ui.menu.set_find_tool_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="tool_event_filter",state_fields=None,bool_fields=None,
    date_fields={"date_fields_name":[ns.db.event.fromdate.name,ns.db.event.todate.name],
                 "date_fields_label":[ns.db.event.fromdate.label,ns.db.event.todate.label]},
    number_fields=None,
    data_fields={"data_fields_name":[ns.db.event.calnumber.name, "htab_tool_serial", "htab_tool_description", 
                                     ns.db.event.eventgroup.name, ns.db.event.subject.name, ns.db.event.place.name, 
                                     ns.db.event.description.name],
                 "data_fields_label":[ns.db.event.calnumber.label, ns.db.tool.serial.label, ns.db.tool.description.label, 
                                      ns.db.event.eventgroup.label, ns.db.event.subject.label, ns.db.event.place.label, 
                                      ns.db.event.description.label]},
    more_data={"title":"Event Additional Data","caption":"Additional Data","url":URL('find_tool_event_fields')})
  
  ns.db.event.ref_id.represent = lambda value,row: A(SPAN(ns.db.tool(id=int(value))["serial"]),
                     _href=URL(r=request, f="frm_tool/view/tool/"+str(value)), _target="_blank")
  ns.db.event.ref_id.label=T('Serial')
  nervatype_tool = ns.valid.get_groups_id("nervatype", "tool")
  join = [(ns.db.event.on((ns.db.tool.id==ns.db.event.ref_id)&(ns.db.event.nervatype==nervatype_tool)&(ns.db.event.deleted==0)))]
  left = [(ns.db.groups.on((ns.db.event.eventgroup==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  if ns.connect.getSetting("printer_in_tool")!="true":
    printer_groups_id = ns.db((ns.db.groups.groupname=="toolgroup")&(ns.db.groups.groupvalue=='printer')).select(ns.db.groups.id)  
    query = ((ns.db.tool.deleted==0)&(~ns.db.tool.toolgroup.belongs(printer_groups_id) | (ns.db.tool.toolgroup==None)))
  else:
    query = (ns.db.tool.deleted==0)
  
  where = ui.select.get_filter_query(sfilter=session.tool_event_filter,table="event",query=query)
  query = where["query"]
  
  fields = [ns.db.event.calnumber,ns.db.event.ref_id, ns.db.tool.description, ns.db.event.eventgroup,
            ns.db.event.fromdate,ns.db.event.todate,ns.db.event.subject,ns.db.event.place,ns.db.event.description]
  if ruri.find("find_tool_event/excel")>0:
    return ui.report.export_excel("tool",query,left,fields,ns.db.tool.serial,request.vars.keywords,join=join)
  if ruri.find("find_tool_event/csv")>0:
    return ui.report.export_csv("tool",query,left,fields,ns.db.tool.serial,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.tool_event_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.tool.id==-1))
    
  if session.mobile:
    ns.db.event.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_event/edit/event/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable=False
    links = None
  else:
    editable=True
    links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("cmd_export_ical?id="+str(row.event.id)), _target="_blank", _title=T("Export Item"))]
  form = SimpleGrid.grid(query=query, field_id=ns.db.event.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.tool.serial, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=links)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_event","0,1,6")
  return dict(form=form)

@ns_auth.requires_login()
def find_tool_event_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.tool_event_fields_filter=None
    redirect(URL("find_tool_event_fields"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_event"+ruri[ruri.find("find_tool_event_fields")+22:]
    redirect(URL(ruri))
  
  response.browsertype=T('Tool Browser')
  response.subtitle=T('Event Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_tool_event_fields","find_tool_event_fields/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_tool_event_fields","find_tool_event_fields/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
    response.export_excel = ruri.replace("find_tool_event_fields","find_tool_event_fields/excel")
    response.export_csv = ruri.replace("find_tool_event_fields","find_tool_event_fields/csv")
  ui.menu.set_find_tool_menu()
  nervatype_event = ns.valid.get_groups_id("nervatype", "event")
  nervatype_tool = ns.valid.get_groups_id("nervatype", "tool")
  response.filter_form = ui.select.get_fields_filter("event","tool_event_fields_filter")
  
  htab = ns.db.event.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(htab.nervatype==nervatype_tool))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_event)))]
  query = (ns.db.fieldvalue.deleted==0)
  where = ui.select.get_filter_query(sfilter=session.tool_event_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.calnumber,htab.subject,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_tool_event_fields/excel")>0:
    return ui.report.export_excel("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  if ruri.find("find_tool_event_fields/csv")>0:
    return ui.report.export_csv("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.tool_event_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
  
  if session.mobile:
    htab.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_event/edit/event/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.calnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_event","0,1,2")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_tool_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.tool_fields_filter=None
    redirect(URL("find_tool_fields"))
  
  if ruri.find("new")>0:
    redirect(URL('frm_tool/new/tool'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_tool"+ruri[ruri.find("find_tool_fields")+16:]
    redirect(URL(ruri))
    
  response.browsertype=T('Tool Browser')
  response.subtitle=T('Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_tool_fields","find_tool_fields/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_tool_fields","find_tool_fields/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_wrench.png')
    response.export_excel = ruri.replace("find_tool_fields","find_tool_fields/excel")
    response.export_csv = ruri.replace("find_tool_fields","find_tool_fields/csv")
  ui.menu.set_find_tool_menu()
  nervatype_tool = ns.valid.get_groups_id("nervatype", "tool")
  response.filter_form = ui.select.get_fields_filter("tool","tool_fields_filter")
  
  htab = ns.db.tool.with_alias('htab')
  if ns.connect.getSetting("printer_in_tool")!="true":
    printer_groups_id = ns.db((ns.db.groups.groupname=="toolgroup")&(ns.db.groups.groupvalue=='printer')).select(ns.db.groups.id)  
    join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(~htab.toolgroup.belongs(printer_groups_id) | (htab.toolgroup==None)))),
            (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
             &(ns.db.deffield.nervatype==nervatype_tool)))]
  else:
    join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_tool)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = ui.select.get_filter_query(sfilter=session.tool_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  htab.description.label = T('Tool description')
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.serial,htab.description,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_tool_fields/excel")>0:
    return ui.report.export_excel("tool",query,left,fields,htab.serial,request.vars.keywords,join=join)
  if ruri.find("find_tool_fields/csv")>0:
    return ui.report.export_csv("tool",query,left,fields,htab.serial,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.tool_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
  
  if session.mobile:
    htab.serial.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_tool/edit/tool/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True  
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.serial, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, create=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_tool","0,2,3")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_tool_tool():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.tool_tool_filter=None
    redirect(URL("find_tool_tool"))
    
  if ruri.find("new")>0:
    redirect(URL('frm_tool/new/tool'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_tool"+ruri[ruri.find("find_tool_tool")+14:]
    redirect(URL(ruri))
  response.browsertype=T('Tool Browser')
  response.subtitle=T('Tool Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_tool_tool","find_tool_tool/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_tool_tool","find_tool_tool/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_wrench.png')
    response.export_excel = ruri.replace("find_tool_tool","find_tool_tool/excel")
    response.export_csv = ruri.replace("find_tool_tool","find_tool_tool/csv")
  ui.menu.set_find_tool_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="tool_tool_filter",state_fields=None,
    bool_fields={"bool_fields_name":[ns.db.tool.inactive.name],
                 "bool_fields_label":[ns.db.tool.inactive.label]},
    number_fields=None, date_fields=None,
    data_fields={"data_fields_name":[ns.db.tool.serial.name, ns.db.tool.description.name, ns.db.tool.product_id.name, 
                                     ns.db.tool.toolgroup.name, ns.db.tool.notes.name],
                 "data_fields_label":[ns.db.tool.serial.label, ns.db.tool.description.label, ns.db.tool.product_id.label, 
                                      ns.db.tool.toolgroup.label, ns.db.tool.notes.label]})
  if ns.connect.getSetting("printer_in_tool")!="true":
    printer_groups_id = ns.db((ns.db.groups.groupname=="toolgroup")&(ns.db.groups.groupvalue=='printer')).select(ns.db.groups.id)  
    query = ((ns.db.tool.deleted==0)&(~ns.db.tool.toolgroup.belongs(printer_groups_id) | (ns.db.tool.toolgroup==None)))  
  else:
    query = (ns.db.tool.deleted==0)
  where = ui.select.get_filter_query(sfilter=session.tool_tool_filter,table="tool",query=query)
  query = where["query"]
  join = [(ns.db.product.on((ns.db.product.id==ns.db.tool.product_id)&(ns.db.product.deleted==0)))]
  left = (ns.db.groups.on((ns.db.tool.toolgroup==ns.db.groups.id)))
  
  fields = [ns.db.tool.serial, ns.db.tool.description, ns.db.tool.product_id, ns.db.groups.groupvalue, 
            ns.db.tool.notes, ns.db.tool.inactive]
  
  if ruri.find("find_tool_tool/excel")>0:
    return ui.report.export_excel("tool",query,left,fields,ns.db.tool.serial,request.vars.keywords,join=join)
  if ruri.find("find_tool_tool/csv")>0:
    return ui.report.export_csv("tool",query,left,fields,ns.db.tool.serial,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.tool_tool_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.tool.id==-1))
  
  if session.mobile:
    ns.db.tool.serial.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_tool/edit/tool/"+str(row.tool["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    editable=True
  form = SimpleGrid.grid(query=query, field_id=ns.db.tool.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.tool.serial, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, create=False, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_tool","0,1")
  
  return dict(form=form)

@ns_auth.requires_login()
def find_transitem_fields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.transitem_fields_filter=None
    redirect(URL("find_transitem_fields"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_transitem_fields")+21:]
    redirect(URL(ruri))
  
  response.browsertype=T('Documents Browser')
  response.subtitle=T('Additional Data')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_transitem_fields","find_transitem_fields/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_transitem_fields","find_transitem_fields/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
    response.export_excel = ruri.replace("find_transitem_fields","find_transitem_fields/excel")
    response.export_csv = ruri.replace("find_transitem_fields","find_transitem_fields/csv")
  ui.menu.set_find_transitem_menu()
  response.filter_form = ui.select.get_fields_filter("trans","transitem_fields_filter",["transtype","direction","transtate","transcast"])
  
  nervatype_trans = ns.valid.get_groups_id("nervatype", "trans")
  transtype_invoice_id = ns.valid.get_groups_id("transtype", "invoice")
  transtype_receipt_id = ns.valid.get_groups_id("transtype", "receipt")
  direction_out_id = ns.valid.get_groups_id("direction", "out")
  
  htab = ns.db.trans.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(ns.db.fieldvalue.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
                             &((ns.db.deffield.visible==1) | ns.db.deffield.fieldname.belongs((
                               'trans_reholiday', 'trans_rebadtool', 'trans_reother', 'trans_rentnote', 
                               'trans_wsdistance', 'trans_wsrepair', 'trans_wstotal','trans_wsnote')))
           &(ns.db.deffield.nervatype==nervatype_trans)))]
  query = (ns.db.fieldvalue.deleted==0)
  query = query & ((htab.deleted==0)|((htab.transtype==transtype_invoice_id)&(htab.direction==direction_out_id))
           |((htab.transtype==transtype_receipt_id)&(htab.direction==direction_out_id)))
  
  where = ui.select.get_filter_query(sfilter=session.transitem_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  #set transtype
  query = query & (htab.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("offer","order","worksheet","rent","invoice","receipt"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~htab.transtype.belongs(audit))
  
  #set transfilter
  query = ui.select.set_transfilter(query,htab)
        
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id, htab.transnumber, ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  if ruri.find("find_transitem_fields/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,htab.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_transitem_fields/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,htab.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.transitem_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
  
  if session.mobile:
    htab.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.htab["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable = False
  else:
    editable = True
    
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,2,3")
    
  return dict(form=form)

@ns_auth.requires_login()
def find_transitem_groups():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.transitem_groups_filter=None
    redirect(URL("find_transitem_groups"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_transitem_groups")+21:]
    redirect(URL(ruri))
  
  response.browsertype=T('Documents Browser')
  response.subtitle=T('Groups')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_transitem_groups","find_transitem_groups/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_transitem_groups","find_transitem_groups/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
    response.export_excel = ruri.replace("find_transitem_groups","find_transitem_groups/excel")
    response.export_csv = ruri.replace("find_transitem_groups","find_transitem_groups/csv")
  ui.menu.set_find_transitem_menu()
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="transitem_groups_filter",
    state_fields=["transtype","direction"], bool_fields=None, date_fields=None, number_fields=None,
    data_fields={"data_fields_name":["htab_trans_transnumber",ns.db.groups.groupvalue.name,ns.db.groups.description.name],
                 "data_fields_label":[ns.db.trans.transnumber.label,ns.db.groups.groupvalue.label,ns.db.groups.description.label]})
  
  nervatype_trans = ns.valid.get_groups_id("nervatype", "trans")
  nervatype_groups = ns.valid.get_groups_id("nervatype", "groups")
  transtype_invoice_id = ns.valid.get_groups_id("transtype", "invoice")
  transtype_receipt_id = ns.valid.get_groups_id("transtype", "receipt")
  transtype_cash_id = ns.valid.get_groups_id("transtype", "cash")
  direction_out_id = ns.valid.get_groups_id("direction", "out")
  
  join = [(ns.db.link.on((ns.db.trans.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0))),
          (ns.db.groups.on((ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.ref_id_2==ns.db.groups.id)))]
  
  query = ((ns.db.trans.deleted==0)|((ns.db.trans.transtype==transtype_invoice_id)&(ns.db.trans.direction==direction_out_id))
           |((ns.db.trans.transtype==transtype_receipt_id)&(ns.db.trans.direction==direction_out_id)&(ns.db.groups.deleted==0))
           |((ns.db.trans.transtype==transtype_cash_id)))
  
  where = ui.select.get_filter_query(sfilter=session.transitem_groups_filter,table="groups",query=query)
  query = where["query"]
  
  #set transtype
  query = query & (ns.db.trans.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("offer","order","worksheet","rent","invoice","receipt"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = ui.select.set_transfilter(query)
      
  fields = [ns.db.trans.transnumber,ns.db.groups.groupvalue,ns.db.groups.description]
  left = None
  if ruri.find("find_transitem_groups/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_transitem_groups/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.transitem_groups_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
  
  if session.mobile:
    ns.db.trans.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.trans["id"])), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable = False
  else:
    editable = True
      
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.trans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,1")
      
  return dict(form=form)

@ns_auth.requires_login()
def find_transitem_item():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.transitem_item_filter=None
    redirect(URL("find_transitem_item"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_transitem_item")+19:]
    redirect(URL(ruri))
  
  response.browsertype=T('Documents Browser')
  response.subtitle=T('Document rows')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_transitem_item","find_transitem_item/excel"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_transitem_item","find_transitem_item/csv"), 
                          cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_corrected.png')
    response.export_excel = ruri.replace("find_transitem_item","find_transitem_item/excel")
    response.export_csv = ruri.replace("find_transitem_item","find_transitem_item/csv")
  ui.menu.set_find_transitem_menu()
  
  transtype_invoice_id = ns.valid.get_groups_id("transtype", "invoice")
  transtype_receipt_id = ns.valid.get_groups_id("transtype", "receipt")
  direction_out_id = ns.valid.get_groups_id("direction", "out")  
  join = [(ns.db.item.on((ns.db.trans.id==ns.db.item.trans_id)&(ns.db.item.deleted==0)))]
  query = ((ns.db.trans.deleted==0)|((ns.db.trans.transtype==transtype_invoice_id)&(ns.db.trans.direction==direction_out_id))
           |((ns.db.trans.transtype==transtype_receipt_id)&(ns.db.trans.direction==direction_out_id)))
  
  ui.select.init_sfilter("transitem_item_filter")
  where = ui.select.get_filter_query(sfilter=session.transitem_item_filter,table="item",query=query)
  query = where["query"]
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = ui.select.set_transfilter(query)
  
  if session.mobile:
    fields = [ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, ns.db.trans.transdate, 
            ns.db.trans.curr, ns.db.item.product_id, ns.db.item.description, ns.db.item.unit, ns.db.item.qty, ns.db.item.fxprice,
            ns.db.item.netamount, ns.db.item.discount, ns.db.item.tax_id, ns.db.item.vatamount, ns.db.item.amount,
            ns.db.item.deposit, ns.db.item.actionprice, ns.db.item.ownstock]
  else:    
    fields = [ns.db.trans.transtype, ns.db.trans.direction, ns.db.item.trans_id, ns.db.trans.transdate, 
            ns.db.trans.curr, ns.db.item.product_id, ns.db.item.description, ns.db.item.unit, ns.db.item.qty, ns.db.item.fxprice,
            ns.db.item.netamount, ns.db.item.discount, ns.db.item.tax_id, ns.db.item.vatamount, ns.db.item.amount,
            ns.db.item.deposit, ns.db.item.actionprice, ns.db.item.ownstock]
  left = None
  
  ns.db.item.deposit.label = T('Deposit/Option')
  
  if ruri.find("find_transitem_item/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_transitem_item/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.transitem_item_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
  
  quick_total={"netamount":0,"vatamount":0,"amount":0}
  total_rows = ns.db(query).select(*[ns.db.item.netamount.sum().with_alias('netamount'),ns.db.item.vatamount.sum().with_alias('vatamount'),ns.db.item.amount.sum().with_alias('amount')],
                      join=join,left=left,groupby=None,having=None).as_list()
  if len(total_rows)>0:
    if total_rows[0]["netamount"]:
      quick_total={"netamount":total_rows[0]["netamount"],"vatamount":total_rows[0]["vatamount"],"amount":total_rows[0]["amount"]}
  response.filter_form = ui.select.create_filter_form(sfilter_name="transitem_item_filter",
    state_fields=["transtype","direction","transtate","transcast"],
    bool_fields={"bool_fields_name":[ns.db.item.deposit.name, ns.db.item.actionprice.name, ns.db.item.ownstock.name],
                 "bool_fields_label":[ns.db.item.deposit.label, ns.db.item.actionprice.label, ns.db.item.ownstock.label]},
    date_fields={"date_fields_name":[ns.db.trans.transdate.name],
                 "date_fields_label":[ns.db.trans.transdate.label]},
    number_fields={"number_fields_name":[ns.db.item.qty.name, ns.db.item.fxprice.name,ns.db.item.netamount.name, 
                                         ns.db.item.discount.name,ns.db.item.vatamount.name, ns.db.item.amount.name],
                   "number_fields_label":[ns.db.item.qty.label, ns.db.item.fxprice.label,ns.db.item.netamount.label, 
                                          ns.db.item.discount.label,ns.db.item.vatamount.label, ns.db.item.amount.label]},
    data_fields={"data_fields_name":[ns.db.item.trans_id.name, "htab_trans_curr", ns.db.item.product_id.name, 
                                     ns.db.item.description.name, ns.db.item.unit.name, ns.db.item.tax_id.name],
                 "data_fields_label":[ns.db.item.trans_id.label, ns.db.trans.curr.label, ns.db.item.product_id.label, 
                                      ns.db.item.description.label, ns.db.item.unit.label, ns.db.item.tax_id.label]},
    quick_total=quick_total)
  
  if session.mobile:
    ns.db.trans.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.trans["id"])), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    editable = False
  else:
    editable = True
  
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.trans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,1")
      
  return dict(form=form)

@ns_auth.requires_login()
def find_transitem_trans():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.transitem_trans_filter=None
    redirect(URL("find_transitem_trans"))
    
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_transitem_trans")+20:]
    redirect(URL(ruri))
          
  response.browsertype=T('Documents Browser')
  response.subtitle=T('Documents')
  response.view=ui.dir_view+'/browser.html'
  if session.mobile:
    response.cmd_excel = ui.control.get_mobil_button(T('Export to Excel'), href=ruri.replace("find_transitem_trans","find_transitem_trans/excel"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
    response.cmd_csv = ui.control.get_mobil_button(T('Export to csv file'), href=ruri.replace("find_transitem_trans","find_transitem_trans/csv"), 
                            cformat=None, style="text-align: left;", theme="b", target="true")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
    response.export_excel = ruri.replace("find_transitem_trans","find_transitem_trans/excel")
    response.export_csv = ruri.replace("find_transitem_trans","find_transitem_trans/csv")
  ui.menu.set_find_transitem_menu()
  
  transtype_invoice_id = ns.valid.get_groups_id("transtype", "invoice")
  transtype_receipt_id = ns.valid.get_groups_id("transtype", "receipt")
  direction_out_id = ns.valid.get_groups_id("direction", "out")
  
  left = [(ns.db.item.on((ns.db.trans.id==ns.db.item.trans_id)&(ns.db.item.deleted==0))),
          (ns.db.fieldvalue.on((ns.db.trans.id==ns.db.fieldvalue.ref_id)&(ns.db.fieldvalue.fieldname=='trans_transcast')&(ns.db.fieldvalue.deleted==0)))]
  join = None
  
  query = ((ns.db.trans.deleted==0)|((ns.db.trans.transtype==transtype_invoice_id)&(ns.db.trans.direction==direction_out_id))
           |((ns.db.trans.transtype==transtype_receipt_id)&(ns.db.trans.direction==direction_out_id)))
  
  ui.select.init_sfilter("transitem_trans_filter")
  where = ui.select.get_filter_query(sfilter=session.transitem_trans_filter,table="trans",query=query)
  query = where["query"]
  having = where["having"]
  
  order = ns.db.trans.crdate
  if request.vars.order:
    if request.vars.order in("item.netamount","item.vatamount","item.amount"):
      order = str(request.vars.order).split(".")[1]
    else:
      order = request.vars.order
      
  #set transtype
  query = query & (ns.db.trans.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("offer","order","worksheet","rent","invoice","receipt"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = ui.select.set_transfilter(query)
    
  ns.db.fieldvalue.value.label = T('Doc.State')
  ns.db.trans.crdate.label = T('Date')
  ns.db.trans.transdate.label = T('TransDate/ StartDate')
  ns.db.trans.duedate.label = T('DueDate/ EndDate')
  
  groupfields=[ns.db.trans.id,ns.db.trans.transtype,ns.db.trans.direction,ns.db.fieldvalue.value,ns.db.trans.id,ns.db.trans.transnumber,
               ns.db.trans.ref_transnumber,ns.db.trans.crdate,ns.db.trans.transdate,ns.db.trans.duedate,ns.db.trans.customer_id,ns.db.trans.employee_id,
               ns.db.trans.department,ns.db.trans.project_id,ns.db.trans.paidtype,ns.db.trans.curr,
               ns.db.item.netamount.sum().with_alias('netamount'),ns.db.item.vatamount.sum().with_alias('vatamount'),ns.db.item.amount.sum().with_alias('amount'),
               ns.db.trans.paid,ns.db.trans.acrate,ns.db.trans.notes,ns.db.trans.intnotes,ns.db.trans.transtate,ns.db.trans.closed,ns.db.trans.deleted]
  groupby=[ns.db.trans.id|ns.db.trans.transtype|ns.db.trans.direction|ns.db.fieldvalue.value|ns.db.trans.id|ns.db.trans.transnumber|
               ns.db.trans.ref_transnumber|ns.db.trans.crdate|ns.db.trans.transdate|ns.db.trans.duedate|ns.db.trans.customer_id|ns.db.trans.employee_id|
               ns.db.trans.department|ns.db.trans.project_id|ns.db.trans.paidtype|ns.db.trans.curr|
               ns.db.trans.paid|ns.db.trans.acrate|ns.db.trans.notes|ns.db.trans.intnotes|ns.db.trans.transtate|ns.db.trans.closed|ns.db.trans.deleted]  
  
  if session.mobile:
    fields = [ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, ns.db.fieldvalue.value, ns.db.trans.ref_transnumber,
            ns.db.trans.crdate, ns.db.trans.transdate, ns.db.trans.duedate, ns.db.trans.customer_id, ns.db.trans.employee_id, ns.db.trans.department,
            ns.db.trans.project_id, ns.db.trans.paidtype, ns.db.trans.curr,
            ns.db.item.netamount, ns.db.item.vatamount, ns.db.item.amount,
            ns.db.trans.paid, ns.db.trans.acrate, ns.db.trans.notes, ns.db.trans.intnotes, ns.db.trans.transtate, ns.db.trans.closed, ns.db.trans.deleted]
    ns.db.trans.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_trans/edit/trans/"+str(row.trans["id"])), 
        cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")  
    editable=False
  else:
    fields = [ns.db.trans.transtype, ns.db.trans.direction, ns.db.fieldvalue.value, ns.db.trans.transnumber, ns.db.trans.ref_transnumber,
            ns.db.trans.crdate, ns.db.trans.transdate, ns.db.trans.duedate, ns.db.trans.customer_id, ns.db.trans.employee_id, ns.db.trans.department,
            ns.db.trans.project_id, ns.db.trans.paidtype, ns.db.trans.curr,
            ns.db.item.netamount, ns.db.item.vatamount, ns.db.item.amount,
            ns.db.trans.paid, ns.db.trans.acrate, ns.db.trans.notes, ns.db.trans.intnotes, ns.db.trans.transtate, ns.db.trans.closed, ns.db.trans.deleted]
    editable=True
    
  if ruri.find("find_transitem_trans/excel")>0:
    return ui.report.export_excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,
                        join=join,groupfields=groupfields,groupby=groupby,having=having)
  if ruri.find("find_transitem_trans/csv")>0:
    return ui.report.export_csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,
                        join=join,groupfields=groupfields,groupby=groupby,having=having)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.transitem_trans_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
  
  quick_total={"netamount":0,"vatamount":0,"amount":0}
  total_rows = ns.db(query).select(*[ns.db.item.netamount.sum().with_alias('netamount'),ns.db.item.vatamount.sum().with_alias('vatamount'),ns.db.item.amount.sum().with_alias('amount')],
                      join=join,left=left,groupby=groupby,having=having).as_list()
  for row in total_rows:
    if row["netamount"]:
      quick_total["netamount"]+=row["netamount"]
    if row["vatamount"]:
      quick_total["vatamount"]+=row["vatamount"]
    if row["amount"]:
      quick_total["amount"]+=row["amount"]
  
  response.filter_form = ui.select.create_filter_form(sfilter_name="transitem_trans_filter",
    state_fields=["transtype","direction","transtate","transcast"],
    bool_fields={"bool_fields_name":[ns.db.trans.paid.name,ns.db.trans.closed.name],
                 "bool_fields_label":[ns.db.trans.paid.label,ns.db.trans.closed.label]},
    date_fields={"date_fields_name":[ns.db.trans.crdate.name,ns.db.trans.transdate.name,ns.db.trans.duedate.name],
                 "date_fields_label":[ns.db.trans.crdate.label,ns.db.trans.transdate.label,ns.db.trans.duedate.label]},
    number_fields={"number_fields_name":[ns.db.item.netamount.name,ns.db.item.vatamount.name,ns.db.item.amount.name,ns.db.trans.acrate.name],
                   "number_fields_label":[ns.db.item.netamount.label,ns.db.item.vatamount.label,ns.db.item.amount.label,ns.db.trans.acrate.label]},
    data_fields={"data_fields_name":[ns.db.trans.transnumber.name, ns.db.trans.ref_transnumber.name, ns.db.trans.customer_id.name, 
                                     ns.db.trans.employee_id.name, ns.db.trans.department.name, ns.db.trans.project_id.name, 
                                     ns.db.trans.paidtype.name, ns.db.trans.curr.name, ns.db.trans.notes.name, ns.db.trans.intnotes.name],
                 "data_fields_label":[ns.db.trans.transnumber.label, ns.db.trans.ref_transnumber.label, ns.db.trans.customer_id.label, 
                                      ns.db.trans.employee_id.label, ns.db.trans.department.label, ns.db.trans.project_id.label, 
                                      ns.db.trans.paidtype.label, ns.db.trans.curr.label, ns.db.trans.notes.label, 
                                      ns.db.trans.intnotes.label]},
    quick_total=quick_total)
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=groupfields, groupby=groupby, left=left, having=having, join=join,
             orderby=order, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=editable, links=None)
  if session.mobile:
    table = form.elements("div.web2py_table")
    if type(table[0][0][0]).__name__=="TABLE":
      ui.control.set_htmltable_style(table[0][0][0],"find_trans","0,1,2,3")
  
  return dict(form=form)

def frm_audit():
  audit_filter_setting = ui.connect.get_audit_filter("setting", None)[0]
  audit_filter_audit = ui.connect.get_audit_filter("audit", None)[0]
  if audit_filter_setting=="disabled" or audit_filter_audit=="disabled":
    audit_filter="disabled"
  elif audit_filter_setting=="readonly" or audit_filter_audit=="readonly":
    audit_filter="readonly"
  elif audit_filter_setting=="update" or audit_filter_audit=="update":
    audit_filter="update"
  else:
    audit_filter="all"
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  response.title=T('SETTINGS')
  response.view=ui.dir_view+'/audit.html'
  if session.mobile:
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=audit'),
                                         cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_key.png')
    response.cmd_help = ui.control.get_help_button("audit")
    response.margin_top = "20px"
  
  if str(ruri).find("delete/usergroup")>0:
    usergroup_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if not ns.connect.deleteData("groups", ref_id=usergroup_id):
      session.flash = str(ns.error_message)
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(URL('frm_groups_usergroup'))
    redirect(URL('frm_groups_usergroup'))
  
  if str(ruri).find("delete/ui_audit")>0:
    audit_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    usergroup_id = ns.db.ui_audit(id=audit_id).usergroup
    ns.connect.deleteData("ui_audit", ref_id=audit_id)
    redirect(URL('frm_audit/view/usergroup/'+str(usergroup_id)))
  
  if str(ruri).find("edit/ui_audit")>0 or str(ruri).find("view/ui_audit")>0 or str(ruri).find("new/ui_audit")>0:
    response.prm_input = True
    ns.db.ui_audit.supervisor.readable = ns.db.ui_audit.supervisor.writable = False
    response.cmd_delete = ""          
    if str(ruri).find("new/ui_audit")>0:
      audit_id=-1
      usergroup_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      ns.db.ui_audit.nervatype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('nervatype')
                                                      &ns.db.groups.groupvalue.belongs(("audit","customer","product","price","employee","tool","project","event","setting","trans","menu","report"))), 
                                                ns.db.groups.id, '%(groupvalue)s')
      ns.db.ui_audit.subtype.readable = ns.db.ui_audit.subtype.writable = False
      response.subtitle=T('New access right')
      form = SQLFORM(ns.db.ui_audit, submit_button=T("Save"),_id="frm_audit")
      form.vars.inputfilter = ns.valid.get_groups_id("inputfilter", "all")
    else:
      audit_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      usergroup_id = ns.db.ui_audit(id=audit_id).usergroup
      nervatype_name = ns.db.groups(id=ns.db.ui_audit(id=audit_id).nervatype).groupvalue
      ns.db.ui_audit.nervatype.writable = False
      response.nervatype = nervatype_name
      if nervatype_name=="trans":
        ns.db.ui_audit.supervisor.readable = ns.db.ui_audit.supervisor.writable = True
        ns.db.ui_audit.subtype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('transtype')
                                                      &ns.db.groups.groupvalue.belongs(("offer","order","worksheet","rent","invoice","delivery","inventory","waybill","production","formula","bank","cash"))), 
                                                ns.db.groups.id, '%(groupvalue)s')
      elif nervatype_name=="report":
        ns.db.ui_audit.subtype.requires = IS_IN_DB(ns.db, ns.db.ui_report.id, '%(reportkey)s')
        ns.db.ui_audit.inputfilter.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('inputfilter')
                                                      &ns.db.groups.groupvalue.belongs(("all","disabled"))), 
                                                ns.db.groups.id, '%(groupvalue)s')
      elif nervatype_name=="menu":
        ns.db.ui_audit.subtype.requires = IS_IN_DB(ns.db, ns.db.ui_menu.id, '%(menukey)s')
        ns.db.ui_audit.inputfilter.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('inputfilter')
                                                      &ns.db.groups.groupvalue.belongs(("all","disabled"))), 
                                                ns.db.groups.id, '%(groupvalue)s')
      else:
        ns.db.ui_audit.subtype.readable = ns.db.ui_audit.subtype.writable = False
      response.subtitle=T('Edit access right')
      form = SQLFORM(ns.db.ui_audit, record = audit_id, submit_button=T("Save"),_id="frm_audit")
      if audit_filter=="all" and session.mobile:
        response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
                                            onclick="if(confirm('"+T('Are you sure you want to delete this access right?')+
                              "')){window.location ='"+URL("frm_audit/delete/ui_audit/"+str(audit_id))+"';};return false;", theme="b")

    if session.mobile:
      response.cmd_audit_close = ui.control.get_mobil_button(label=T("BACK"), href=URL('frm_audit/view/usergroup/'+str(usergroup_id)),
        icon="back", theme="a", ajax="false")
      response.cmd_home = ui.control.get_mobil_button(label=T("GROUPS"), href=URL('frm_groups_usergroup'),
                                             icon="search", cformat="ui-btn-left", ajax="false", iconpos="left")
    else:
      response.cmd_back = ui.control.get_back_button(URL('frm_audit/view/usergroup/'+str(usergroup_id)))
    
    if request.post_vars:
      request.post_vars.usergroup = usergroup_id
    if form.validate(keepvalues=True):
      if audit_id>-1: form.vars.id = audit_id
      row_id = ns.connect.updateData("ui_audit", values=dict(form.vars), validate=False, insert_row=True)
      if not row_id:
        response.flash = str(ns.error_message)
      else:
        if str(ruri).find("new/ui_audit")>0:
          redirect(URL('frm_audit/view/ui_audit/'+str(row_id)))
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    form.custom.widget.supervisor = ui.control.get_bool_input(audit_id,"ui_audit","supervisor")
    if audit_filter=="readonly":
      form.custom.submit = ""
    elif DEMO_MODE:
      form.custom.submit = DIV(SPAN(T('DEMO MODE')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
    elif session.mobile:
      form.custom.submit = ui.control.get_mobil_button(label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_audit'].submit();")
    return dict(form=form,view_audit="")
  
  if str(ruri).find("edit/usergroup")>0 or str(ruri).find("view/usergroup")>0: 
    usergroup_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])   
    response.subtitle=T('Edit user group')
    form = SQLFORM(ns.db.groups, record = usergroup_id, submit_button=T("Save"),_id="frm_audit")
    if audit_filter=="all" and not DEMO_MODE:
      if session.mobile:
        response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
                                            onclick="if(confirm('"+T('Are you sure you want to delete this group?')+
                              "')){window.location ='"+URL("frm_audit/delete/usergroup/"+str(usergroup_id))+"';};return false;", theme="b")
      else:
        response.cmd_delete = INPUT(_type="button", _value=T("Delete"),
                                _style="height: 28px !important;padding-top: 4px !important;color: #A52A2A;width: 100%;", 
                                _onclick="javascript:if(confirm(w2p_ajax_confirm_message||'"+T('Are you sure you want to delete this group?')
                                  +"')){window.location ='"+URL("frm_audit/delete/usergroup/"+str(usergroup_id))+"';};return false;")
    else:
      response.cmd_delete = ""
    audit = ((ns.db.ui_audit.usergroup==usergroup_id))
    ns.db.ui_audit.usergroup.readable = ns.db.ui_audit.usergroup.writable = False
    if session.mobile:
      ns.db.ui_audit.id.label = T("*")
      ns.db.ui_audit.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), 
                          href=URL("frm_audit/edit/ui_audit/"+str(row["id"])), 
                          cformat=None, icon="edit", style="text-align: left;", ajax="false")
      deletable,editable=False,False
    else:
      ns.db.ui_audit.id.readable = ns.db.ui_audit.id.writable = False
      deletable=(audit_filter=="all")
      editable=True
    
    view_audit = ui.select.get_tab_grid(_query=audit, _field_id=ns.db.ui_audit.id, _fields=None, _deletable=deletable, links=None, _editable=editable,
                             multi_page="audit_page", rpl_1="/frm_audit", rpl_2="/frm_audit/view/usergroup/"+str(usergroup_id),_priority="0,1,2,3")    
  else:
    usergroup_id=-1
    form = SQLFORM(ns.db.groups, submit_button=T("Save"),_id="frm_audit")
    response.subtitle=T('New user group')
    response.cmd_delete = ""
    view_audit=""
  
  if audit_filter=="readonly":
    form.custom.submit = ""
  elif DEMO_MODE:
    form.custom.submit = DIV(SPAN(T('DEMO MODE')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
  elif session.mobile:
    form.custom.submit = ui.control.get_mobil_button(label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_audit'].submit();")
        
  if request.post_vars:
    request.post_vars.groupname = "usergroup"
  groups_nervatype_id = ns.valid.get_groups_id("nervatype", "groups")  
  if form.validate(keepvalues=True):
    group = ns.db((ns.db.groups.id!=usergroup_id)&(ns.db.groups.groupname=="usergroup")&(ns.db.groups.groupvalue==form.vars.groupvalue)).select().as_list()
    if len(group)==0:
      if usergroup_id>-1: form.vars.id = usergroup_id
      row_id = ns.connect.updateData("groups", values=dict(form.vars), validate=False, insert_row=True)
      if row_id:
        values = {"nervatype_1":groups_nervatype_id, "ref_id_1":row_id, 
                  "nervatype_2":groups_nervatype_id, "ref_id_2":int(request.post_vars.transfilter_id)}
        filterlink = ns.db((ns.db.link.ref_id_1==usergroup_id)&(ns.db.link.nervatype_1==groups_nervatype_id)
                  &(ns.db.link.nervatype_2==groups_nervatype_id)&(ns.db.link.deleted==0)).select().as_list()
        if len(filterlink)>0:
          values["id"]=filterlink[0]["id"]
        link_id = ns.connect.updateData("link", values=values, validate=False, insert_row=True)
        if not link_id:
          response.flash = str(ns.error_message)
        else:
          if str(ruri).find("new/usergroup")>0:
            redirect(URL('frm_audit/view/usergroup/'+str(row_id)))
      else:
        response.flash = str(ns.error_message)
    else:
      form.errors["groupvalue"] = T('The group name already exists!')
      response.flash = T('Error: ')+str(T('The group name already exists!'))
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  form.custom.widget.inactive = ui.control.get_bool_input(usergroup_id,"groups","inactive")
  filterlink = ns.db((ns.db.link.ref_id_1==usergroup_id)&(ns.db.link.nervatype_1==groups_nervatype_id)
                  &(ns.db.link.nervatype_2==groups_nervatype_id)&(ns.db.link.deleted==0)).select().as_list()
  if len(filterlink)>0:
    filterlink = filterlink[0]["ref_id_2"]
  else:
    filterlink = ns.valid.get_groups_id("transfilter", "all")
  transfilter = ns.db((ns.db.groups.groupname=="transfilter")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.id).as_list()
  response.cmb_transfilter = SELECT(*[OPTION(field["groupvalue"], _value=field["id"], 
                                             _selected=(field["id"]==filterlink)) for field in transfilter], _id="cmb_transfilter",
                                    _onchange="document.getElementById('transfilter_id').value=this.value")
  response.transfilter_id = INPUT(_name="transfilter_id", _type="hidden", _value=filterlink, _id="transfilter_id")
  
  if session.mobile:
    response.cmd_groups_close = ui.control.get_mobil_button(label=T("BACK"), href=URL('frm_groups_usergroup'),
        icon="back", theme="a", ajax="false")
  else:
    response.cmd_back = ui.control.get_back_button(URL('frm_groups_usergroup'))
  if usergroup_id>-1:
    if session.mobile:
      response.cmd_add_audit = ui.control.get_mobil_button(
        label=T("Add access right"), href=URL('frm_audit/new/ui_audit/'+str(usergroup_id)), 
        cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
    else:
      response.cmd_add_audit = A(SPAN(_class="icon plus"), _style="height: 18px;vertical-align: middle;padding-top: 2px;padding-bottom: 4px;", 
               _class="w2p_trap buttontext button", 
             _href=URL('frm_audit/new/ui_audit/'+str(usergroup_id)), _title=T("Add access right"))
  else:
    response.cmd_add_audit = ""
  
  return dict(form=form,view_audit=view_audit)

def frm_currency():
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  if str(ruri).find("delete/currency")>0:
    currency_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if not ns.connect.deleteData("currency", ref_id=currency_id):
      session.flash = str(ns.error_message)
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(URL('frm_currency'))
    redirect(URL('frm_currency'))

  response.view=ui.dir_view+'/currency.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Currency')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_money.png')
    response.cmd_back = ui.control.get_back_button(session.back_url)
  ns.db.currency.id.readable = ns.db.currency.id.writable = False
  ns.db.currency.curr.label = T('Currency')
  if str(ruri).find("new/currency")>0 or str(ruri).find("edit/currency")>0:
    response.edit = True
    sform = None
    if str(ruri).find("edit/currency")>0:
      currency_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      response.subtitle=T('Edit currency')
      form = SQLFORM(ns.db.currency, record=currency_id, submit_button=T("Save"), comments = False, formstyle = 'divs', _id="frm_currency")
    else:
      currency_id = -1
      response.subtitle=T('New currency')
      form = SQLFORM(ns.db.currency, submit_button=T("Save"), comments = False, formstyle = 'divs', _id="frm_currency")
    
    if form.validate(keepvalues=True):
      if currency_id>-1: form.vars.id = currency_id
      row_id = ns.connect.updateData("currency", values=dict(form.vars), validate=False, insert_row=True)
      if not row_id:
        response.flash = str(ns.error_message)
      else:
        if str(ruri).find("new/currency")>0:
          redirect(URL('frm_currency'))
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    if session.mobile:
      response.cmd_currency_close = ui.control.get_mobil_button(label=T("BACK"), href=URL('frm_currency'),
        icon="back", theme="a", ajax="false")
    else:
      response.cmd_back = ui.control.get_back_button(URL('frm_currency'))
    if audit_filter=="readonly":
      form.custom.submit = ""
    elif session.mobile:
      form.custom.submit = ui.control.get_mobil_button(label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_currency'].submit();")
  else:
    if session.mobile:
      ns.db.currency.curr.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_currency/edit/currency/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
      deletable = False
    else:
      response.margin_top = "20px"
      deletable = False #(audit_filter=="all")
    fields = [ns.db.currency.curr,ns.db.currency.description,ns.db.currency.digit,ns.db.currency.defrate, ns.db.currency.cround]
    
    sform = DIV(ui.select.create_search_form(URL("frm_currency")),
                _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
    form = ui.select.find_data(table="currency",query=ns.db.currency,fields=fields,orderby=ns.db.currency.curr,
                       paginate=10,maxtextlength=25,links=None,left=None,page_url=None,
                       sortable=True,priority="0,1",deletable=deletable,fullrow=True)
  return dict(form=DIV(form, _id="dlg_frm"),sform=sform)

@ns_auth.requires_login()
def frm_custom_menu():
  ruri = request.wsgi.environ["REQUEST_URI"]
  menukey = ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1]
  menucmd = ns.db.ui_menu(menukey=menukey)
  response.subtitle = menucmd.description
  response.view=ui.dir_view+'/custom.html'
  if session.mobile:
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=menucmd'),
      cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
    response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
      icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
  else:
    response.cmd_help = ui.control.get_help_button("menucmd")
    if menucmd.url==0 and session.back_url:
      response.cmd_back = ui.control.get_back_button(session.back_url)
    else:
      response.cmd_back = ui.control.get_home_button()
    if menucmd.icon==None:
      response.titleicon = URL(ui.dir_images,'icon16_world_link.png')
    else:
      response.titleicon = URL(ui.dir_images,'icon16_'+str(menucmd.icon)+'.png')
  response.description=T(menucmd.description)
  menufields = ns.db(ns.db.ui_menufields.menu_id==menucmd.id).select(orderby=ns.db.ui_menufields.menu_id|ns.db.ui_menufields.orderby).as_list()
  form=""
  if request.post_vars or len(menufields)==0:
    if menucmd.address==None:
      url = "http://"+request.wsgi.environ["HTTP_HOST"]
    else:
      url = menucmd.address
    if menucmd.url==1:
      if menucmd.funcname!=None:
        url+="/"+menucmd.funcname
      prm=""
      for pname in dict(request.post_vars).keys():
        prm+="&"+pname+"="+str(dict(request.post_vars)[pname])
      if prm!="":
        url+="?"+prm[1:]
      redirect(url)
    else:
      func = getattr(ui.tool, menucmd.funcname, None)
      if callable(func):
        response.return_value = func(dict(request.post_vars))
      else:
        response.return_value =T('Missing menu function!')
  else:
    if menucmd.url==0 and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    tfields=[]
    for field in menufields:
      if ns.db.groups(id=field["fieldtype"]).groupvalue=="bool":
        tfield = Field(field["fieldname"], 'boolean', label=field["description"])
        tfield.default = False
          
      elif ns.db.groups(id=field["fieldtype"]).groupvalue=="date":
        tfield = Field(field["fieldname"], 'date', label=field["description"])
        tfield.default = datetime.datetime.now().date()
          
      elif ns.db.groups(id=field["fieldtype"]).groupvalue=="integer":
        tfield = Field(field["fieldname"], 'integer', label=field["description"])
        tfield.default = 0
          
      elif ns.db.groups(id=field["fieldtype"]).groupvalue=="float":
        tfield = Field(field["fieldname"], 'double', label=field["description"])
        tfield.default = 0
          
      else:
        tfield = Field(field["fieldname"], 'string', label=field["description"])
      tfields.append(tfield)
    form = SQLFORM.factory(*tfields, submit_button=T("Call"), comments=False, **{"_data-ajax":"false"}) 
    
  return dict(form=form)

@ns_auth.requires_login()
def frm_customer():
  customer_audit_filter = ui.connect.get_audit_filter("customer", None)[0]
  setting_audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  
  if customer_audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    customer_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["customer_page_"+str(customer_id)] = "fieldvalue_page"
    redirect(URL('frm_customer/view/customer/'+str(customer_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    customer_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["customer_page_"+str(customer_id)] = "fieldvalue_page"
    if ns.connect.deleteData("fieldvalue", ref_id=fieldvalue_id):
      redirect(URL('frm_customer/view/customer/'+str(customer_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    ui.connect.clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    row_id = ns.connect.updateData("fieldvalue", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["customer_page_"+str(request.post_vars["ref_id"])] = "fieldvalue_page"
      redirect()
   
  if ruri.find("edit/address")>0 or ruri.find("view/address")>0:
    address_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    customer_id = ns.db.address(id=address_id).ref_id
    session["customer_page_"+str(customer_id)] = "address_page"
    redirect(URL('frm_customer/view/customer/'+str(customer_id)))
    
  if ruri.find("delete/address")>0:
    address_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    customer_id = ns.db.address(id=address_id).ref_id
    session["customer_page_"+str(customer_id)] = "address_page"
    if ns.connect.deleteData("address", ref_id=address_id):
      redirect(URL('frm_customer/view/customer/'+str(customer_id)))
        
  if request.post_vars["_formname"]=="address/create":
    ui.connect.clear_post_vars()
    row_id = ns.connect.updateData("address", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["customer_page_"+str(request.post_vars["ref_id"])] = "address_page"
      redirect()
  
  if ruri.find("edit/contact")>0 or ruri.find("view/contact")>0:
    contact_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    customer_id = ns.db.contact(id=contact_id).ref_id
    session["customer_page_"+str(customer_id)] = "contact_page"
    redirect(URL('frm_customer/view/customer/'+str(customer_id)))
    
  if ruri.find("delete/contact")>0:
    contact_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    customer_id = ns.db.contact(id=contact_id).ref_id
    session["customer_page_"+str(customer_id)] = "contact_page"
    if ns.connect.deleteData("contact", ref_id=contact_id):
      redirect(URL('frm_customer/view/customer/'+str(customer_id)))
        
  if request.post_vars["_formname"]=="contact/create":
    ui.connect.clear_post_vars()
    row_id = ns.connect.updateData("contact", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["customer_page_"+str(request.post_vars["ref_id"])] = "contact_page"
      redirect()
  
  if ruri.find("event")>0:
    ruri = "frm_event/view"+ruri[ruri.find("frm_customer/edit")+17:]
    redirect(URL(ruri))
  
  if ruri.find("new/link")>0:
    customer_id = int(request.vars.refnumber)
    cust_nervatype = ns.valid.get_groups_id("nervatype", "customer")
    groups_id = int(request.vars.groups_id)
    groups_nervatype = ns.valid.get_groups_id("nervatype", "groups")
    glink = ns.db((ns.db.link.ref_id_1==customer_id)&(ns.db.link.nervatype_1==cust_nervatype)&(ns.db.link.deleted==0)
              &(ns.db.link.nervatype_2==groups_nervatype)&(ns.db.link.ref_id_2==groups_id)).select().as_list()
    if len(glink)==0:
      values = {"nervatype_1":cust_nervatype, "ref_id_1":customer_id, "nervatype_2":groups_nervatype, "ref_id_2":groups_id}
      ns.connect.updateData("link", values=values, validate=False, insert_row=True)
    session["customer_page_"+str(customer_id)] = "groups_page"
    redirect(URL('frm_customer/view/customer/'+str(customer_id)))
    
  if ruri.find("delete/link")>0:
    link_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ns.connect.deleteData("link", ref_id=link_id):
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(ruri[:ruri.find("delete/link")-1])
  
  if ruri.find("new/customer")>0:
    customer_id = -1
  else:
    customer_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ns.db.customer(id=customer_id).deleted==1:
      return ui.connect.show_disabled(response.title)
      
  if ruri.find("delete/customer")>0:
    if not ns.connect.deleteData("customer", ref_id=customer_id):
      session.flash = str(ns.error_message)
      redirect(URL('frm_customer/view/customer/'+str(customer_id)))
    else:
      redirect(URL('find_customer_customer'))
      
  response.view=ui.dir_view+'/customer.html'
  response.custnumber = ""
  if not session.mobile:
    response.titleicon = URL(ui.dir_images,'icon16_customer.png')
    response.icon_deffield = IMG(_src=URL(ui.dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_address = IMG(_src=URL(ui.dir_images,'icon16_address.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_contact = IMG(_src=URL(ui.dir_images,'icon16_contact.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_calendar = IMG(_src=URL(ui.dir_images,'icon16_calendar.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.lo_menu = []
  nervatype_customer = ns.valid.get_groups_id("nervatype", "customer")
  nervatype_groups = ns.valid.get_groups_id("nervatype", "groups")
  
  #basic customer data
  ns.db.customer.id.readable = ns.db.customer.id.writable = False
  ns.db.customer.deleted.readable = ns.db.customer.deleted.writable = False
  own_customer = False
  if customer_id>0:
    company = ns.valid.get_own_customer()    
    if customer_id==company.id:
      response.home,own_customer = True,True
      response.subtitle=T('COMPANY')
      response.custnumber=""
      ns.db.customer.custname.label = T('Company Name')
      response.titleicon = URL(ui.dir_images,'icon16_home.png')
      customer_audit_filter = setting_audit_filter
      if len(request.post_vars)>0:
        request.post_vars.custtype = company.custtype
        request.post_vars.custnumber = company.custnumber
        request.post_vars.terms = company.terms
        request.post_vars.creditlimit = company.creditlimit
        request.post_vars.discount = company.discount
    else:
      response.subtitle=T('CUSTOMER')
      response.custnumber=ns.db.customer(id=customer_id).custnumber
      ns.db.customer.custtype.requires = IS_IN_DB(ns.db((ns.db.groups.groupname.like('custtype'))&(ns.db.groups.groupvalue!="own")), ns.db.groups.id, '%(groupvalue)s')
    form = SQLFORM(ns.db.customer, record = customer_id, submit_button=T("Save"),_id="frm_customer")
    if customer_audit_filter!="disabled":
      response.cmd_report = ui.control.get_report_button(nervatype="customer", title=T('Customer Reports'), ref_id=customer_id,
                                              label=response.custnumber)
    else:
      response.cmd_report = ""
    if customer_audit_filter=="all" and customer_id>0 and not own_customer:
      if session.mobile:
        response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
                                            onclick="if(confirm('"+T('Are you sure you want to delete this customer?')+
                                            "')){window.location ='"+URL("frm_customer/delete/customer/"+str(customer_id))+"';};return false;", theme="b")
      else:
        response.cmd_delete = ui.control.get_command_button(_id="cmd_delete", caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this customer?')+
                              "')){window.location ='"+URL("frm_customer/delete/customer/"+str(customer_id))+"';};return false;")
    else:
      response.cmd_delete = ""
  else:
    form = SQLFORM(ns.db.customer, submit_button=T("Save"),_id="frm_customer")
    form.vars.custnumber = ns.connect.nextNumber("custnumber",False)
    form.vars.custtype = ns.valid.get_groups_id("custtype", "company")
    response.subtitle=T('NEW CUSTOMER')
    response.custnumber = ""
    response.cmd_report = ""
    response.cmd_delete = ""
  
  if session.mobile:
    if own_customer:
      response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
                                               icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
    else:
      if customer_audit_filter in ("disabled"):
        response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
                                               icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
      else:
        response.cmd_back = ui.control.get_mobil_button(label=T("SEARCH"), href=URL("frm_quick_customer"), icon="search", cformat="ui-btn-left", ajax="false") 
  
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=customer'),
                                           cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:
    if own_customer:
      response.cmd_back = ui.control.get_home_button()
    else:
      if customer_audit_filter in ("disabled"):
        response.cmd_back = ui.control.get_home_button()
      else:
        response.cmd_back = ui.control.get_back_button(URL("find_customer_customer")) 
    response.cmd_help = ui.control.get_help_button("customer")
  
  if (not own_customer and (customer_audit_filter in ("readonly","disabled"))) or (own_customer and (setting_audit_filter in ("readonly","disabled"))):
    form.custom.submit = ""
  elif session.mobile:
    form.custom.submit = ui.control.get_mobil_button(cmd_id="cmd_customer_update",
        label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_customer'].submit();")      
  if form.validate(keepvalues=True):
    if customer_id==-1:
      nextnumber = ns.connect.nextNumber("custnumber",False)
      if form.vars.custnumber == nextnumber:
        form.vars.custnumber = ns.connect.nextNumber("custnumber")
    else:
      form.vars.id = customer_id
    row_id = ns.connect.updateData("customer", values=dict(form.vars), validate=False, insert_row=True)  
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      redirect(URL('frm_customer/view/customer/'+str(row_id)))
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      if str(ns.db.customer.fields).find(error)>0:
        flash+=ns.db.customer[error].label+": "+form.errors[error]+", "
      else:
        flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  form.custom.widget.notax = ui.control.get_bool_input(customer_id,"customer","notax")
  form.custom.widget.inactive = ui.control.get_bool_input(customer_id,"customer","inactive")

  if session.mobile:
    if session["customer_page_"+str(customer_id)]:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value=session["customer_page_"+str(customer_id)])
      session["customer_page_"+str(customer_id)]="customer_page"
    else:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value="customer_page")
      
    response.menu_customer = ui.control.get_mobil_button(T("Customer Data"), href="#", 
        cformat=None, icon="edit", style="text-align: left;",
        onclick= "show_page('customer_page');", theme="a", rel="close")

  #show customer groups list
  if customer_id>-1:
    customer_groups = ((ns.db.link.ref_id_1==customer_id)&(ns.db.link.nervatype_1==nervatype_customer)&
            (ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.deleted==0))
    ns.db.link.ref_id_2.represent = lambda value,row: ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")
    ns.db.link.nervatype_1.readable = ns.db.link.ref_id_1.readable = ns.db.link.nervatype_2.readable = ns.db.link.linktype.readable = ns.db.link.deleted.readable = False
    ns.db.link.ref_id_2.label = T('Groups')
    
    if session.mobile:
      groups_count = ns.db(customer_groups).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
      response.menu_groups = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Customer Groups"),groups_count), href="#", cformat=None, icon="star", style="text-align: left;",
        onclick= "show_page('groups_page');",
        theme="a", rel="close")
      if customer_audit_filter not in ("readonly","disabled"):
        ns.db.link.id.label=T("Delete")
        ns.db.link.id.represent = lambda value,row: ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="delete", iconpos="notext",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this object?")
            +"')){ajax('"+URL('frm_customer/delete/link')+"/"+str(row["id"])
            +"',[],'');jQuery(this).closest('tr').remove();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}", 
          theme="d")
      else:
        ns.db.link.id.readable = ns.db.link.id.writable = False
      deletable = False
    else:
      ns.db.link.id.readable = ns.db.link.id.writable = False
      deletable = customer_audit_filter not in ("readonly","disabled")
    response.view_customer_groups = ui.select.get_tab_grid(customer_groups, ns.db.link.id, _fields=None, _editable=False,
                                       _deletable=deletable, links=None, 
                                      multi_page="groups_page", rpl_1="/frm_customer", rpl_2="/frm_customer/view/customer/"+str(customer_id))
    
    #show add/remove customer groups combo and setting button
    if customer_audit_filter not in ("readonly","disabled"):
      response.cmb_groups = ui.control.get_cmb_groups("customer")
      if session.mobile:
        response.cmd_groups_add = ui.control.get_mobil_button(label=T("Add to Group"), href="#", 
          icon="plus", cformat=None, ajax="true", theme="b",
          onclick= "var group_id = document.getElementById('cmb_groups').value;if(group_id!=''){window.location ='"+URL("frm_customer/new/link")
           +"?refnumber="+str(customer_id)+"&groups_id='+group_id;} else {alert('"+T('Missing Customer Group!')+"');return false;}")
        response.cmd_groups = ui.control.get_mobil_button(label=T("Edit Groups"), href="#", 
          icon="gear", cformat=None, ajax="true", theme="b", rel="close",
          onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
              +"')){window.location ='"+URL("frm_groups_customer?back=1")+"';};return false;")
      else:
        response.cmd_groups_add = ui.control.get_icon_button(T('Add to Group'),"cmd_groups_add", 
          cmd="var group_id = document.getElementById('cmb_groups').value;if(group_id!=''){window.location ='"+URL("frm_customer/new/link")
          +"?refnumber="+str(customer_id)+"&groups_id='+group_id;} else {alert('"+T('Missing Transaction Group!')+"');return false;}")                          
        response.cmd_groups = ui.control.get_goprop_button(title=T("Edit Customer Groups"), url=URL("frm_groups_customer?back=1"))
    else:
      response.cmd_groups_add = ""
      response.cmb_groups = ""
      response.cmd_groups = ""
  else:
    response.menu_groups = ""
      
  setting_audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if setting_audit_filter=="disabled":
    response.cmd_groups = ""
                
  #additional fields data
  if customer_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_customer)&(ns.db.fieldvalue.ref_id==customer_id))
    editable = not customer_audit_filter in ("readonly","disabled")
    ui.select.set_view_fields("customer", nervatype_customer, 0, editable, fieldvalue, customer_id, "/frm_customer", "/frm_customer/view/customer/"+str(customer_id))   
  else:
    response.menu_fields = ""
    
  #address data
  if customer_id>-1:
    address = ((ns.db.address.ref_id==customer_id)&(ns.db.address.nervatype==nervatype_customer)&(ns.db.address.deleted==0))
    address_count = ns.db(address).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if session.mobile:
      links = None
      response.menu_address = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Address Data"),address_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('address_page');", theme="a", rel="close")
      ns.db.address.id.label = T("*")
      ns.db.address.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, icon="edit", style="text-align: left;",
                            onclick="set_address("
                             +str(row["id"])+",'"
                             +json.dumps(str(row["country"]))[1:-1]+"','"
                             +json.dumps(str(row["state"]))[1:-1]+"','"
                             +json.dumps(str(row["zipcode"]))[1:-1]+"','"
                             +json.dumps(str(row["city"]))[1:-1]+"','"
                             +json.dumps(str(row["street"]))[1:-1]+"','"
                             +json.dumps(str(row["notes"]))[1:-1]+"')", theme="d")
    else:
      ns.db.address.id.label = T("No.")
      ns.db.address.id.represent = lambda value,row: ui.control.format_value("integer",row["id"])
      links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_address("
                           +str(row["id"])+",'"
                           +json.dumps(str(row["country"]))[1:-1]+"','"
                           +json.dumps(str(row["state"]))[1:-1]+"','"
                           +json.dumps(str(row["zipcode"]))[1:-1]+"','"
                           +json.dumps(str(row["city"]))[1:-1]+"','"
                           +json.dumps(str(row["street"]))[1:-1]+"','"
                           +json.dumps(str(row["notes"]))[1:-1]+"')",
                           _title=T("Edit Address"))]
    ns.db.address.nervatype.readable = ns.db.address.ref_id.readable = ns.db.address.deleted.readable = False
    ns.db.address.street.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
    
    if (not own_customer and customer_audit_filter in ("readonly","disabled")) or (own_customer and setting_audit_filter in ("readonly","disabled")):
      if session.mobile:
        response.cmd_address_new = ""
      else:
        response.cmd_address_new = SPAN(" ",SPAN(str(address_count), _class="detail_count"))
      response.cmd_address_update = ""
      response.cmd_address_delete = ""
    else:
      if session.mobile:
        response.cmd_address_update = ui.control.get_mobil_button(cmd_id="cmd_address_update",
          label=T("Save Address"), href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
          onclick= "document.forms['frm_address'].submit();")
        response.cmd_address_delete = ui.control.get_mobil_button(cmd_id="cmd_address_delete",
          label=T("Delete Address"), href="#", 
          cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to delete this data?')+
                              "')){if(document.getElementById('address_id').value>-1){window.location = '"
            +URL("frm_customer")+"/delete/address/'+document.getElementById('address_id').value;} else {show_page('address_page');}}")
        response.cmd_address_new = ui.control.get_mobil_button(cmd_id="cmd_address_new",
          label=T("New Address"), href="#", 
          cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
          onclick= "set_address(-1,'','','','','','');", rel="close")
        response.cmd_address_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
          icon="back", ajax="true", theme="a",  
          onclick= "show_page('address_page');", rel="close")
      else:
        links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this address?')+
                              "')){window.location ='"+URL("frm_customer/delete/address/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Address")))
        response.cmd_address_update = ui.control.get_command_button(caption=T("Save"),title=T("Update address data"),color="008B00", _id="cmd_address_submit",
                              cmd="address_update();return true;")
        response.cmd_address_new = ui.control.get_tabnew_button(address_count,T('New Address'),cmd_id="cmd_address_new",
                                cmd = "$('#tabs').tabs({ active: 1 });set_address(-1,'','','','','','')")
  
    response.view_address = ui.select.get_tab_grid(_query=address, _field_id=ns.db.address.id, _fields=None, _deletable=False, _editable=False, links=links, 
                               multi_page="address_page", rpl_1="/frm_customer", rpl_2="/frm_customer/view/customer/"+str(customer_id),_priority="0,4,5")
    
    response.address_form = SQLFORM(ns.db.address, submit_button=T("Save"),_id="frm_address")
    response.address_form.process()
    if not session.mobile:
      response.address_icon = URL(ui.dir_images,'icon16_address.png')
      response.cmd_address_cancel = A(SPAN(_class="icon cross"), _id="cmd_address_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_address').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.address_id = INPUT(_name="id", _type="hidden", _value="", _id="address_id")
    response.address_ref_id = INPUT(_name="ref_id", _type="hidden", _value=customer_id, _id="address_ref_id")
    response.address_nervatype = INPUT(_name="nervatype", _type="hidden", _value=nervatype_customer, _id="address_nervatype")
  else:
    response.menu_address = ""
      
  #contact data
  if customer_id>-1:
    contact = ((ns.db.contact.ref_id==customer_id)&(ns.db.contact.nervatype==nervatype_customer)&(ns.db.contact.deleted==0))
    contact_count = ns.db(contact).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if session.mobile:
      links = None
      response.menu_contact = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Contact Info"),contact_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('contact_page');",
        theme="a", rel="close")
      ns.db.contact.id.label = T("*")
      ns.db.contact.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, icon="edit", style="text-align: left;",
                            onclick="set_contact("
                             +str(row["id"])+",'"
                             +json.dumps(str(row["firstname"]))[1:-1]+"','"
                             +json.dumps(str(row["surname"]))[1:-1]+"','"
                             +json.dumps(str(row["status"]))[1:-1]+"','"
                             +json.dumps(str(row["phone"]))[1:-1]+"','"
                             +json.dumps(str(row["fax"]))[1:-1]+"','"
                             +json.dumps(str(row["mobil"]))[1:-1]+"','"
                             +json.dumps(str(row["email"]))[1:-1]+"','"
                             +json.dumps(str(row["notes"]))[1:-1]+"')")
    else:
      ns.db.contact.id.label = T("No.")
      ns.db.contact.id.represent = lambda value,row: ui.control.format_value("integer",row["id"])
      links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                             _class="w2p_trap buttontext button", _href="#", _onclick="set_contact("
                             +str(row["id"])+",'"
                             +json.dumps(str(row["firstname"]))[1:-1]+"','"
                             +json.dumps(str(row["surname"]))[1:-1]+"','"
                             +json.dumps(str(row["status"]))[1:-1]+"','"
                             +json.dumps(str(row["phone"]))[1:-1]+"','"
                             +json.dumps(str(row["fax"]))[1:-1]+"','"
                             +json.dumps(str(row["mobil"]))[1:-1]+"','"
                             +json.dumps(str(row["email"]))[1:-1]+"','"
                             +json.dumps(str(row["notes"]))[1:-1]+"')",
                             _title=T("Edit Contact"))]
    ns.db.contact.nervatype.readable = ns.db.contact.ref_id.readable = ns.db.contact.deleted.readable = False
    
    if (not own_customer and customer_audit_filter in ("readonly","disabled")) or (own_customer and setting_audit_filter in ("readonly","disabled")):
      if session.mobile:
        response.cmd_contact_new = ""
      else:
        response.cmd_contact_new = SPAN(" ",SPAN(str(contact_count), _class="detail_count"))
      response.cmd_contact_update = ""
      response.cmd_contact_delete = ""
    else:
      if session.mobile:
        response.cmd_contact_update = ui.control.get_mobil_button(cmd_id="cmd_contact_update",
          label=T("Save Contact"), href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
          onclick= "document.forms['frm_contact'].submit();")
        response.cmd_contact_delete = ui.control.get_mobil_button(cmd_id="cmd_contact_delete",
          label=T("Delete Contact"), href="#", 
          cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to delete this data?')+
                              "')){if(document.getElementById('contact_id').value>-1){window.location = '"
            +URL("frm_customer")+"/delete/contact/'+document.getElementById('contact_id').value;} else {show_page('contact_page');}}")
        response.cmd_contact_new = ui.control.get_mobil_button(cmd_id="cmd_contact_new",
          label=T("New Contact"), href="#", 
          cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
          onclick= "set_contact(-1,'','','','','','','','');", rel="close")
        response.cmd_contact_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
          icon="back", ajax="true", theme="a",  
          onclick= "show_page('contact_page');", rel="close")
      else:
        links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this contact?')+
                                "')){window.location ='"+URL("frm_customer/delete/contact/"+str(row.id))+"';};return false;", 
                           _title=T("Delete Contact")))
        response.cmd_contact_update = ui.control.get_command_button(caption=T("Save"),title=T("Update contact data"),color="008B00", _id="cmd_contact_submit",
                                cmd="contact_update();return true;")
        response.cmd_contact_new = ui.control.get_tabnew_button(contact_count,T('New Contact'),cmd_id="cmd_contact_new",
                                  cmd = "$('#tabs').tabs({ active: 2 });set_contact(-1,'','','','','','','','')")
  
    response.view_contact = ui.select.get_tab_grid(_query=contact, _field_id=ns.db.contact.id, _fields=None, _deletable=False, _editable=False, links=links, 
                               multi_page="contact_page", rpl_1="/frm_customer", rpl_2="/frm_customer/view/customer/"+str(customer_id),_priority="0,1,2")
    
    response.contact_form = SQLFORM(ns.db.contact, submit_button=T("Save"),_id="frm_contact")
    response.contact_form.process()
    if not session.mobile:
      response.contact_icon = URL(ui.dir_images,'icon16_contact.png')
      response.cmd_contact_cancel = A(SPAN(_class="icon cross"), _id="cmd_contact_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_contact').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.contact_id = INPUT(_name="id", _type="hidden", _value="", _id="contact_id")
    response.contact_ref_id = INPUT(_name="ref_id", _type="hidden", _value=customer_id, _id="contact_ref_id")
    response.contact_nervatype = INPUT(_name="nervatype", _type="hidden", _value=nervatype_customer, _id="contact_nervatype")
  else:
    response.menu_contact = ""
        
  #event data  
  event_audit_filter = ui.connect.get_audit_filter("event", None)[0]
  if event_audit_filter!="disabled" and customer_id>-1:
    event = ((ns.db.event.ref_id==customer_id)&(ns.db.event.nervatype==nervatype_customer)&(ns.db.event.deleted==0))
    event_count = ns.db(event).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if session.mobile:
      editable = False
      links = None
      blabel = T("Company Events") if own_customer else T("Customer Events")
      response.menu_event = ui.control.get_mobil_button(ui.control.get_bubble_label(blabel,event_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('event_page');",
        theme="a", rel="close")
      ns.db.event.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL('frm_customer/edit/event/')+str(row["id"]), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    else:
      editable = True
      links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("cmd_export_ical?id="+str(row.id)), _target="_blank", _title=T("Export Item"))]
    ns.db.event.id.readable = ns.db.event.id.writable = False
    ns.db.event.nervatype.readable = ns.db.event.ref_id.readable = ns.db.event.uid.readable = ns.db.event.deleted.readable = False
    
    if (not own_customer and customer_audit_filter in ("readonly","disabled")) or (own_customer and setting_audit_filter in ("readonly","disabled")) or (event_audit_filter in ("readonly","disabled")):
      gdeleted = False
      if session.mobile:
        response.cmd_event_new = ""
      else:
        response.cmd_event_new = SPAN(" ",SPAN(str(event_count), _class="detail_count"))
    else:
      if session.mobile:
        gdeleted = False
        response.cmd_event_new = ui.control.get_mobil_button(cmd_id="cmd_event_new",
          label=T("New Event"), href=URL("frm_event/new/event")+"?refnumber="+form.formname, 
          cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
      else:
        gdeleted = True
        response.cmd_event_new = ui.control.get_tabnew_button(event_count,T('New Event'),cmd_id="tabs-events",url=URL("frm_event/new/event")+"?refnumber="+form.formname)

    response.view_event = ui.select.get_tab_grid(_query=event, _field_id=ns.db.event.id, _fields=None, _deletable=gdeleted, links=links, _editable=editable,
                             multi_page="event_page", rpl_1="/frm_customer", rpl_2="/frm_customer/view/customer/"+str(customer_id),_priority="0,4")
  else:
    response.view_event = ""
    response.event_disabled=True
    response.menu_event = ""
      
  return dict(form=form)

def frm_deffield(nervatype,subtype=None):
  ruri = request.wsgi.environ["REQUEST_URI"]
  response.view=ui.dir_view+'/deffield.html'
  if nervatype!="all":
    nervatype_id = ns.valid.get_groups_id("nervatype", nervatype)
  else:
    ns.db.deffield.nervatype.label = T("N.Type")
    nervatype_id = None
  if subtype!=None:
    subtype_id = ns.valid.get_groups_id("transtype", subtype)
  else:
    subtype_id = None
  
  if str(ruri).find("delete/deffield")>0:
    deffield_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    ns.connect.deleteData("deffield", ref_id=deffield_id)
    redirect(URL('frm_deffield_'+nervatype))
  
  ns.db.deffield.fieldtype.requires = IS_IN_DB(ns.db((ns.db.groups.groupname.like('fieldtype'))&(ns.db.groups.groupvalue!="filter")&(ns.db.groups.groupvalue!="checkbox")&(ns.db.groups.groupvalue!="trans")), ns.db.groups.id, '%(groupvalue)s')
  ns.db.deffield.subtype.readable = ns.db.deffield.subtype.writable = False
  ns.db.deffield.deleted.readable = ns.db.deffield.deleted.writable = False
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  
  if (audit_filter=="all"):
    if session.mobile:
      response.cmd_deffield_new = ui.control.get_mobil_button(cmd_id="cmd_deffield_new",
        label=T("New Additional Data"), href=URL("frm_deffield_"+nervatype+"/new/deffield")+"?back=1", 
        cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
    else:
      response.cmd_deffield_new = ui.control.get_new_button(URL("frm_deffield_"+nervatype+"/new/deffield")+"?back=1")
  else:
    response.cmd_deffield_new = ""
    
  if session.mobile:
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=deffield'),
                                         cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:
    response.cmd_help = ui.control.get_help_button("deffield")
    ns.db.deffield.id.readable = ns.db.deffield.id.writable = False
  
  if str(ruri).find("new/deffield")>0 or str(ruri).find("edit/deffield")>0 or str(ruri).find("view/groups")>0:
    response.prm_input = True
    if session.mobile:
      response.cmd_deffield_close = ui.control.get_mobil_button(label=T("BACK"), href=URL('frm_deffield_'+nervatype),
        icon="back", theme="a", ajax="false")
    else:
      response.cmd_back = ui.control.get_back_button(URL('frm_deffield_'+nervatype))
    
    ns.db.deffield.fieldname.writable = False
    ns.db.deffield.description.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
    if str(ruri).find("edit/deffield")>0 or str(ruri).find("view/groups")>0:
      ns.db.deffield.nervatype.writable = False
      ns.db.deffield.fieldtype.writable = False
      deffield_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      valuelist_id = ns.valid.get_groups_id("fieldtype", "valuelist")
      if ns.db.deffield(id=deffield_id)["fieldtype"]==valuelist_id:
        ns.db.deffield.valuelist.widget=lambda field,value: SQLFORM.widgets.text.widget(field,value, _rows=3)
      else:
        ns.db.deffield.valuelist.readable = ns.db.deffield.valuelist.writable = False
    else:
      ns.db.deffield.valuelist.readable = ns.db.deffield.valuelist.writable = False
      ns.db.deffield.nervatype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('nervatype')
        &ns.db.groups.groupvalue.belongs(('address','barcode','contact','currency','customer','employee','event','formula','groups',
                                          'item','link','log','movement','numberdef','pattern','payment','place','price','product',
                                          'project','rate','tax','tool','trans','setting','report'))), ns.db.groups.id, '%(groupvalue)s')
    ns.db.deffield.fieldname.label = T("Data UID")
    ns.db.deffield.fieldtype.label = T("Type")
    ns.db.deffield.valuelist.label = T("Value list (row separator: | sign)")
    ns.db.deffield.addnew.label = T("Auto create")
    if str(ruri).find("edit/deffield")>0:
      if ns.db.deffield(id=deffield_id).deleted==1:
        return ui.connect.show_disabled(response.title)
      form = SQLFORM(ns.db.deffield, record=deffield_id, submit_button=T("Save"), comments = False, _id="frm_deffield")
      if audit_filter=="all":
        if session.mobile:
          response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
                                            onclick="if(confirm('"+T('Are you sure you want to delete this data?')+
                              "')){window.location ='"+URL("frm_deffield_"+nervatype+"/delete/deffield/"+str(deffield_id))+"';};return false;", theme="b")
        else:
          response.cmd_delete = ui.control.get_command_button(caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this data?')+
                              "')){window.location ='"+URL("frm_deffield_"+nervatype+"/delete/deffield/"+str(deffield_id))+"';};return false;")
      else:
        response.cmd_delete = ""
    else:
      deffield_id = -1
      form = SQLFORM(ns.db.deffield, submit_button=T("Save"), comments = False, _id="frm_deffield")
      form.vars.nervatype = nervatype_id
      response.cmd_delete = ""
      
    if request.post_vars:
      form.vars.subtype = subtype
      if deffield_id == -1:
        form.vars.fieldname = web2py_uuid()
    if form.validate(keepvalues=True):
      if deffield_id>0: form.vars.id = deffield_id
      row_id = ns.connect.updateData("deffield", values=form.vars, validate=False, insert_row=True)  
      if not row_id:
        response.flash = str(ns.error_message)
      else:
        if deffield_id==-1:
          redirect(URL('frm_deffield_'+nervatype+'/edit/deffield/'+str(row_id)))
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        if str(ns.db.deffield.fields).find(error)>0:
          flash+=ns.db.deffield[error].label+": "+form.errors[error]+", "
        else:
          flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    form.custom.widget.addnew = ui.control.get_bool_input(deffield_id,"deffield","addnew")
    form.custom.widget.visible = ui.control.get_bool_input(deffield_id,"deffield","visible")
    form.custom.widget.readonly = ui.control.get_bool_input(deffield_id,"deffield","readonly")
    if audit_filter=="readonly":
      form.custom.submit = ""
    elif session.mobile:
      form.custom.submit = ui.control.get_mobil_button(cmd_id="cmd_deffield_update",
        label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_deffield'].submit();")
  else:
    ns.db.deffield.fieldname.readable = ns.db.deffield.fieldname.writable = False
    ns.db.deffield.valuelist.readable = ns.db.deffield.valuelist.writable = False
    ns.db.deffield.addnew.readable = ns.db.deffield.addnew.writable = False
    ns.db.deffield.visible.readable = ns.db.deffield.visible.writable = False
    ns.db.deffield.readonly.readable = ns.db.deffield.readonly.writable = False
    ns.db.groups.groupvalue.label = T("N.Type")
    
    if session.mobile:
      if nervatype!="all":
        fields=[ns.db.deffield.id,ns.db.deffield.description,ns.db.deffield.fieldtype]
        deffield = ((ns.db.deffield.nervatype==nervatype_id)&(ns.db.deffield.subtype==subtype_id)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1))
      else:
        fields=[ns.db.deffield.id,ns.db.deffield.description,ns.db.groups.groupvalue,ns.db.deffield.fieldtype]
        deffield = ((ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==ns.db.groups.id))
      
      if (audit_filter=="all"):
        ns.db.deffield.id.label=T("Delete")
        if nervatype!="all":
          ns.db.deffield.id.represent = lambda value,row: ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="delete", iconpos="notext",
            onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this data?")
              +"')){ajax('"+URL("frm_deffield_"+nervatype+"/delete/deffield/"+str(row["id"]))
              +"',[],'');jQuery(this).closest('tr').remove();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}", 
            theme="d")
          ns.db.deffield.description.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_deffield_"+nervatype+"/edit/deffield/"+str(row["id"])), 
                            cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
        else:
          ns.db.deffield.id.represent = lambda value,row: ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="delete", iconpos="notext",
            onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this data?")
              +"')){ajax('"+URL("frm_deffield_"+nervatype+"/delete/deffield/"+str(row.deffield["id"]))
              +"',[],'');jQuery(this).closest('tr').remove();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}", 
            theme="d")
          ns.db.deffield.description.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_deffield_"+nervatype+"/edit/deffield/"+str(row.deffield["id"])), 
                            cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
      else:
        ns.db.deffield.id.readable = ns.db.deffield.id.writable = False
    else:
      response.cmd_back = ui.control.get_back_button(session.back_url)
      response.margin_top = "20px"
    
      if nervatype!="all":
        fields=[ns.db.deffield.description,ns.db.deffield.fieldtype]
        deffield = ((ns.db.deffield.nervatype==nervatype_id)&(ns.db.deffield.subtype==subtype_id)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1))
      else:
        fields=[ns.db.groups.groupvalue,ns.db.deffield.description]
        deffield = ((ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==ns.db.groups.id))
      
    form = ui.select.find_data(table="deffield",query=deffield,fields=fields,orderby=ns.db.deffield.description,
                       paginate=10,maxtextlength=50,links=None,left=None,page_url=None,
                       sortable=True,priority="0,1",deletable=False,fullrow=True)
  return form

@ns_auth.requires_login()
def frm_deffield_all():
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  response.title=T('SETTINGS')
  response.subtitle=T('Additional Data')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_deffield.png')
  response.sform = ui.select.create_search_form(URL("frm_deffield_all"))
  return dict(form=frm_deffield("all"))

@ns_auth.requires_login()
def frm_deffield_customer():
  response.title=T('CUSTOMER')
  response.subtitle=T('Additional Data')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_customer.png')
  response.sform = ui.select.create_search_form(URL("frm_deffield_customer"))
  return dict(form=frm_deffield("customer"))

@ns_auth.requires_login()
def frm_deffield_employee():
  response.title=T('EMPLOYEE')
  response.subtitle=T('Additional Data')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_user.png')
  response.sform = ui.select.create_search_form(URL("frm_deffield_employee"))
  return dict(form=frm_deffield("employee"))

@ns_auth.requires_login()
def frm_deffield_event():
  response.title=T('EVENT')
  response.subtitle=T('Additional Data')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
  response.sform = ui.select.create_search_form(URL("frm_deffield_event"))
  return dict(form=frm_deffield("event"))

@ns_auth.requires_login()
def frm_deffield_groups():
  response.title=T('GROUPS')
  response.subtitle=T('Additional Data')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_edit.png')
  response.sform = ui.select.create_search_form(URL("frm_deffield_groups"))
  return dict(form=frm_deffield("groups"))

@ns_auth.requires_login()
def frm_deffield_place():
  response.title=T('PLACE')
  response.subtitle=T('Additional Data')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_book.png')
  response.sform = ui.select.create_search_form(URL("frm_deffield_place"))
  return dict(form=frm_deffield("place"))

@ns_auth.requires_login()
def frm_deffield_product():
  response.title=T('PRODUCT')
  response.subtitle=T('Additional Data')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_parts.png')
  response.sform = ui.select.create_search_form(URL("frm_deffield_product"))
  return dict(form=frm_deffield("product"))

@ns_auth.requires_login()
def frm_deffield_project():
  response.title=T('PROJECT')
  response.subtitle=T('Additional Data')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_date_edit.png')
  response.sform = ui.select.create_search_form(URL("frm_deffield_project"))
  return dict(form=frm_deffield("project"))

@ns_auth.requires_login()
def frm_deffield_setting():
  response.title=T('SETTINGS')
  response.subtitle=T('Database Settings')
  if not session.mobile:
    if request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_numberdef.png')
  response.sform = ui.select.create_search_form(URL("frm_deffield_setting"))
  return dict(form=frm_deffield("setting"))

@ns_auth.requires_login()
def frm_deffield_tool():
  response.title=T('TOOL')
  response.subtitle=T('Additional Data')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_wrench.png')
  response.sform = ui.select.create_search_form(URL("frm_deffield_tool"))
  return dict(form=frm_deffield("tool"))

@ns_auth.requires_login()
def frm_deffield_trans():
  response.title=T('TRANSACTION')
  response.subtitle=T('Additional Data')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_deffield.png')
  response.sform = ui.select.create_search_form(URL("frm_deffield_trans"))
  return dict(form=frm_deffield("trans"))

@ns_auth.requires_login()
def frm_employee():
  audit_filter = ui.connect.get_audit_filter("employee", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    employee_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["employee_page_"+str(employee_id)] = "fieldvalue_page"
    redirect(URL('frm_employee/view/employee/'+str(employee_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    employee_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["employee_page_"+str(employee_id)] = "fieldvalue_page"
    if ns.connect.deleteData("fieldvalue", ref_id=fieldvalue_id):
      redirect(URL('frm_employee/view/employee/'+str(employee_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    ui.connect.clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    row_id = ns.connect.updateData("fieldvalue", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["employee_page_"+str(request.post_vars["ref_id"])] = "fieldvalue_page"
      redirect()
  
  if ruri.find("event")>0:
    ruri = "frm_event/view"+ruri[ruri.find("frm_employee/edit")+17:]
    redirect(URL(ruri))
  
  if ruri.find("new/employee")>0:
    employee_id = -1
  else:
    employee_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ns.db.employee(id=employee_id).deleted==1:
      return ui.connect.show_disabled(response.title)
      
  if ruri.find("delete/employee")>0:
    if not ns.connect.deleteData("employee", ref_id=employee_id):
      session.flash = str(ns.error_message)
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(URL('find_employee_employee'))
    redirect(URL('find_employee_employee'))  
  
  response.view=ui.dir_view+'/employee.html'
  if not session.mobile:
    response.titleicon = URL(ui.dir_images,'icon16_user.png')
    response.icon_deffield = IMG(_src=URL(ui.dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_calendar = IMG(_src=URL(ui.dir_images,'icon16_calendar.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.lo_menu = []
  
  nervatype_employee = ns.valid.get_groups_id("nervatype", "employee")
  employee_audit_filter = ui.connect.get_audit_filter("employee", None)[0]
  setting_audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  
  #basic employee data
  ns.db.employee.deleted.readable = ns.db.employee.deleted.writable = False
  ns.db.address.street.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
  if employee_id>0:
    employee = ns.db.employee(id=employee_id)
    contact = ns.db((ns.db.contact.ref_id==employee_id)&(ns.db.contact.nervatype==nervatype_employee)
                    &(ns.db.contact.deleted==0)).select()
    contact = contact[0] if len(contact)>0 else None
    address = ns.db((ns.db.address.ref_id==employee_id)&(ns.db.address.nervatype==nervatype_employee)
                    &(ns.db.address.deleted==0)).select()
    address = address[0] if len(address)>0 else None
    response.subtitle=T('EMPLOYEE')
    response.empnumber = ns.db.employee(id=employee_id).empnumber
    if employee_audit_filter!="disabled":
      response.cmd_report = ui.control.get_report_button(nervatype="employee", title=T('Employee Reports'), ref_id=employee_id,
                                              label=response.empnumber)
    else:
      response.cmd_report = ""
    if employee_audit_filter=="all":
      if session.mobile:
        response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
                                            onclick="if(confirm('"+T('Are you sure you want to delete this employee?')+
                                            "')){window.location ='"+URL("frm_employee/delete/employee/"+str(employee_id))+"';};return false;", theme="b")
      else:
        response.cmd_delete = ui.control.get_command_button(_id="cmd_delete", caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this employee?')+
                              "')){window.location ='"+URL("frm_employee/delete/employee/"+str(employee_id))+"';};return false;")
    else:
      response.cmd_delete = ""
    if employee_audit_filter not in ("readonly","disabled"):
      if session.mobile:
        response.cmd_password = ui.control.get_mobil_button(T("Change password"), href="#", cformat=None, icon="lock", style="text-align: left;",
                                            onclick="if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
                                  +"')){window.location ='"+URL("frm_password/"+str(employee_id))+"';};return false;", theme="b")
      else:
        response.cmd_password = ui.control.get_command_button(_id="cmd_password", caption=T("Change password"),title=T("Change password"),color="483D8B",
                              _height="30px", _top= "4px",
                              cmd="if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
                                  +"')){window.location ='"+URL("frm_password/"+str(employee_id))+"';};return false;")
    else:
      response.cmd_password = ""
  else:
    employee=None
    contact=None
    address=None
    response.subtitle=T('NEW EMPLOYEE')
    response.empnumber = ""
    response.cmd_report = ""
    response.cmd_delete = ""
    response.cmd_password = ""
  
  fvalues={}
  fields=[]
  for fname in ns.db.employee.fields:
    if employee==None:
      fvalues[fname]=None
    else:
      fvalues[fname]=employee[fname]
    fields.append(ns.db.employee[fname])
  for fname in ns.db.contact.fields:
    if fvalues.has_key(fname)==False and fname!="nervatype" and fname!="ref_id":
      if contact==None:
        fvalues[fname]=None
      else:
        fvalues[fname]=contact[fname]
      fields.append(ns.db.contact[fname])
  for fname in ns.db.address.fields:
    if fvalues.has_key(fname)==False and fname!="nervatype" and fname!="ref_id":
      if address==None:
        fvalues[fname]=None
      else:
        fvalues[fname]=address[fname]
      fields.append(ns.db.address[fname])
  form = SQLFORM.factory(*fields,submit_button=T("Save"),table_name="employee",_id="frm_employee")
  if employee==None:
    form.vars.empnumber = ns.connect.nextNumber("empnumber",False)
    form.vars.usergroup = ns.valid.get_groups_id("usergroup", "admin")
  else:
    for fvalue in fvalues.items():
      if fvalue[1]!=None:
        form.vars[fvalue[0]]=fvalue[1]
  form.process(keepvalues=True,onfailure=None)
  form.errors.clear()
  
  if session.mobile:
    if employee_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
                                             icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
    else:
      response.cmd_back = ui.control.get_mobil_button(label=T("SEARCH"), href=URL("frm_quick_employee"), icon="search", cformat="ui-btn-left", ajax="false") 
  
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=employee'),
                                           cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:
    if employee_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_home_button()
    else:
      response.cmd_back = ui.control.get_back_button(URL("find_employee_employee"))
    response.cmd_help = ui.control.get_help_button("employee")
  
  if employee_audit_filter in ("readonly","disabled"):
    form.custom.submit = "" 
  elif session.mobile:
    form.custom.submit = ui.control.get_mobil_button(cmd_id="cmd_employee_update",
        label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_employee'].submit();")
      
  if len(request.post_vars)>0:
    employee_values={}
    contact_values={}
    address_values={}
    for value_key in form.vars.keys():
      if value_key!="id":
        if ns.db.employee.has_key(value_key):
          employee_values[value_key]=form.vars[value_key]
        elif ns.db.contact.has_key(value_key):
          contact_values[value_key]=form.vars[value_key]
        elif ns.db.address.has_key(value_key):
          address_values[value_key]=form.vars[value_key]
    if employee_id==-1:
      empnumber = ns.connect.nextNumber("empnumber",False)
      if employee_values.has_key("empnumber"):
        if employee_values["empnumber"] == empnumber:
          employee_values["empnumber"] = ns.connect.nextNumber("empnumber")
      if employee_values.has_key("username"):
        if employee_values["username"]=="":
          del employee_values["username"]
    else:
      employee_values["id"] = employee_id
   
    row_id = ns.connect.updateData("employee", values=employee_values, validate=False, insert_row=True)  
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      address_values["ref_id"]=row_id
      address_values["nervatype"]=nervatype_employee
      address = ns.db((ns.db.address.ref_id==row_id)&(ns.db.address.nervatype==nervatype_employee)
                      &(ns.db.address.deleted==0)).select()
      if len(address)>0: address_values["id"]=address[0]["id"]
      address_id = ns.connect.updateData("address", values=address_values, validate=False, insert_row=True)  
      if not address_id:
        response.flash = str(ns.error_message)

      contact_values["ref_id"]=row_id
      contact_values["nervatype"]=nervatype_employee
      contact = ns.db((ns.db.contact.ref_id==row_id)&(ns.db.contact.nervatype==nervatype_employee)
                      &(ns.db.contact.deleted==0)).select()
      if len(contact)>0: contact_values["id"]=contact[0]["id"]
      contact_id = ns.connect.updateData("contact", values=contact_values, validate=False, insert_row=True)  
      if not contact_id:
        response.flash = str(ns.error_message)  
      redirect(URL('frm_employee/view/employee/'+str(row_id)))
  
  form.custom.widget.inactive = ui.control.get_bool_input(employee_id,"employee","inactive")                            
  
  if (employee_audit_filter in ("readonly","disabled")) or (setting_audit_filter in ("disabled")):
    response.cmd_department = ""
    response.cmd_usergroup = ""
  else:
    if session.mobile:
      response.cmd_department = ui.control.get_mobil_button(label=T("Edit Departments"), href="#", 
        icon="gear", cformat=None, ajax="true", theme="b", rel="close",
        onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
            +"')){window.location ='"+URL("frm_groups_department?back=1")+"';};return false;")
      response.cmd_usergroup = ui.control.get_mobil_button(label=T("Edit Usergroups"), href="#", 
        icon="gear", cformat=None, ajax="true", theme="b", rel="close",
        onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
            +"')){window.location ='"+URL("frm_groups_usergroup?back=1")+"';};return false;")
    else:
      response.cmd_department = ui.control.get_goprop_button(title=T("Edit Departments"), url=URL("frm_groups_department?back=1"))
      response.cmd_usergroup = ui.control.get_goprop_button(title=T("Edit Usergroups"), url=URL("frm_groups_usergroup?back=1"))
  
  if session.mobile:
    if session["employee_page_"+str(employee_id)]:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value=session["employee_page_"+str(employee_id)])
      session["employee_page_"+str(employee_id)]="employee_page"
    else:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value="employee_page")
    response.menu_employee = ui.control.get_mobil_button(T("Employee Data"), href="#", cformat=None, icon="edit", style="text-align: left;",
        onclick= "show_page('employee_page');",
        theme="a", rel="close")
    
  #additional fields data
  if employee_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_employee)&(ns.db.fieldvalue.ref_id==employee_id))
    editable = not employee_audit_filter in ("readonly","disabled")
    ui.select.set_view_fields("employee", nervatype_employee, 0, editable, fieldvalue, employee_id, "/frm_employee", "/frm_employee/view/employee/"+str(employee_id))
  else:
    response.menu_fields = ""
    
  #event data
  event_audit_filter = ui.connect.get_audit_filter("event", None)[0]
  if event_audit_filter!="disabled" and employee_id>-1:
    event = ((ns.db.event.ref_id==employee_id)&(ns.db.event.nervatype==nervatype_employee)&(ns.db.event.deleted==0))
    ns.db.event.id.readable = ns.db.event.id.writable = False
    ns.db.event.nervatype.readable = ns.db.event.ref_id.readable = ns.db.event.uid.readable = False
    event_count = ns.db(event).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if session.mobile:
      links = None
      editable = False
      response.menu_event = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Employee Events"),event_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('event_page');",
        theme="a", rel="close")
      ns.db.event.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL('frm_employee/edit/event/')+str(row["id"]), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    else:
      editable = True
      links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("cmd_export_ical?id="+str(row.id)), _target="_blank", _title=T("Export Item"))]
    
    if employee_audit_filter in ("readonly","disabled") or event_audit_filter in ("readonly","disabled"):
      gdeleted = False
      if session.mobile:
        response.cmd_event_new = ""
      else:
        response.cmd_event_new = SPAN(" ",SPAN(str(event_count), _class="detail_count"))
    else:
      if session.mobile:
        gdeleted = False
        response.cmd_event_new = ui.control.get_mobil_button(cmd_id="cmd_event_new",
          label=T("New Event"), href=URL("frm_event/new/event")+"?refnumber="+form.formname, 
          cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
      else:
        gdeleted = True
        response.cmd_event_new = ui.control.get_tabnew_button(event_count,T('New Event'),cmd_id="tabs-event",url=URL("frm_event/new/event")+"?refnumber=employee/"+str(employee_id))
    
    response.view_event = ui.select.get_tab_grid(_query=event, _field_id=ns.db.event.id, _fields=None, _deletable=gdeleted, links=links, _editable=editable,
                             multi_page="event_page", rpl_1="/frm_employee", rpl_2="/frm_employee/view/employee/"+str(employee_id),_priority="0,4")
  else:
    response.view_event = ""
    response.event_disabled=True
    response.menu_event = ""
      
  return dict(form=form)

@ns_auth.requires_login()
def frm_event():
  audit_filter = ui.connect.get_audit_filter("event", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    event_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["event_page_"+str(event_id)] = "fieldvalue_page"
    redirect(URL('frm_event/view/event/'+str(event_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    event_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["event_page_"+str(event_id)] = "fieldvalue_page"
    if ns.connect.deleteData("fieldvalue", ref_id=fieldvalue_id):
      redirect(URL('frm_event/view/event/'+str(event_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    ui.connect.clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    row_id = ns.connect.updateData("fieldvalue", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["event_page_"+str(request.post_vars["ref_id"])] = "fieldvalue_page"
      redirect()
    
  if ruri.find("new")>0:
    event_id = -1
    nervatype_name = str(request.vars.refnumber).split("/")[0]
    ref_id = int(str(request.vars.refnumber).split("?")[0].split("/")[1])
  else:
    event_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    nervatype_name = ns.db.groups(id=ns.db.event(id=event_id).nervatype).groupvalue
    ref_id = ns.db.event(id=event_id).ref_id
    if ns.db.event(id=event_id).deleted==1:
      return ui.connect.show_disabled(response.title)
  
  if ruri.find("delete/event")>0:
    if not ns.connect.deleteData("event", ref_id=event_id):
      session.flash = str(ns.error_message)
      redirect(URL('frm_event/view/event/'+str(event_id)))
    else:
      redirect(URL("frm_"+nervatype_name+"/view/"+nervatype_name+"/"+str(ref_id)))
  
  response.view=ui.dir_view+'/event.html'
  if not session.mobile:
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
    response.icon_deffield = IMG(_src=URL(ui.dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_note = IMG(_src=URL(ui.dir_images,'icon16_note.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.from_title = ns.valid.show_refnumber("refnumber", nervatype_name, ref_id)
  ns.db.event.nervatype.writable = False
  ns.db.event.ref_id.writable = False
  if event_id>0:
    form = SQLFORM(ns.db.event, record = event_id, submit_button=T("Save"),_id="frm_event")
    response.subtitle=T('EVENT')
    if session.mobile:
      response.cmd_export = ui.control.get_mobil_button(cmd_id="cmd_event_export",
        label=T("Export to iCal"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "window.open('"+URL("cmd_export_ical")+"?id="+str(event_id)+"', '_blank');")
      if audit_filter=="all":
        response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
                                              onclick="if(confirm('"+T('Are you sure you want to delete this event?')+
                                              "')){window.location ='"+URL("frm_event/delete/event/"+str(event_id))+"';};return false;", theme="b")
      else:
        response.cmd_delete = ""
    else:
      response.cmd_export = ui.control.get_command_button(caption=T("Export"), title=T("Export to iCal"), 
                                             cmd = "window.open('"+URL("cmd_export_ical")+"?id="+str(event_id)+"', '_blank');")
  else:
    form = SQLFORM(ns.db.event, submit_button=T("Save"),_id="frm_event")
    form.vars.nervatype =  ns.valid.get_groups_id("nervatype", nervatype_name)
    form.vars.ref_id = ref_id
    form.vars.calnumber = ns.connect.nextNumber("calnumber",False)
    response.subtitle=T('NEW EVENT')
    response.cmd_export = ""
  if session.mobile:
    form.custom.submit = ui.control.get_mobil_button(cmd_id="cmd_event_update",
        label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_event'].submit();")
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=event'),
                                         cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:
    form.custom.submit = ui.control.get_command_button(caption=T("Save"), title=T("Save event data"), 
                                            color="008B00", cmd = "event_update();")
    response.cmd_help = ui.control.get_help_button("event")
  nervatype_audit_filter = ui.connect.get_audit_filter(nervatype_name, None)[0]
  event_audit_filter = ui.connect.get_audit_filter("event", None)[0]
  setting_audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if (nervatype_audit_filter in ("disabled")) or (event_audit_filter in ("disabled")):
    if session.mobile:
      response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
                                             icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
    else:
      response.cmd_back = ui.control.get_home_button()
  else:
    if session.mobile:
      response.cmd_back = ui.control.get_mobil_button(label=T(str(nervatype_name).upper()), href=URL("frm_"+nervatype_name+"/view/"+nervatype_name+"/"+str(ref_id)), 
                                           icon="back", cformat="ui-btn-left", ajax="false")
    else:
      response.cmd_back = ui.control.get_back_button(URL("frm_"+nervatype_name+"/view/"+nervatype_name+"/"+str(ref_id))) 
                
  if (nervatype_audit_filter in ("readonly","disabled")) or (event_audit_filter in ("readonly","disabled")):
    form.custom.submit = ""
    response.cmd_new = ""
  else:
    if session.mobile:
      response.cmd_new = ui.control.get_mobil_button(cmd_id="cmd_event_new",
        label=T("New Event"), href=URL('frm_event/new/event')+'?refnumber='+nervatype_name+"/"+str(ref_id), 
        cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
    else:
      response.cmd_new = ui.control.get_new_button(URL('frm_event/new/event')+'?refnumber='+nervatype_name+"/"+str(ref_id))  
  
  if form.validate(keepvalues=True):
    if event_id==-1:
      nextnumber = ns.connect.nextNumber("calnumber",False)
      if form.vars.calnumber == nextnumber:
        form.vars.calnumber = ns.connect.nextNumber("calnumber")
    else:
      form.vars.id = event_id    
    row_id = ns.connect.updateData("event", values=form.vars, validate=False, insert_row=True)  
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      redirect(URL('frm_event/view/event/'+str(row_id)))
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  if session.mobile:
    if session["event_page_"+str(event_id)]:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value=session["event_page_"+str(event_id)])
      session["event_page_"+str(event_id)]="event_page"
    else:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value="event_page")
    response.menu_event = ui.control.get_mobil_button(T("Event Data"), href="#", cformat=None, icon="edit", style="text-align: left;",
      onclick= "show_page('event_page');",
      theme="a", rel="close")
  
  #additional fields data
  nervatype_event = ns.valid.get_groups_id("nervatype", "event")
  if event_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_event)&(ns.db.fieldvalue.ref_id==event_id))
    editable = not (nervatype_audit_filter in ("readonly","disabled")) or (event_audit_filter in ("readonly","disabled"))
    ui.select.set_view_fields(nervatype_name="event", nervatype_id=nervatype_event, tab_index=1, editable=editable, query=fieldvalue,
                    ref_id=event_id, rpl_1="/frm_event", rpl_2="/frm_event/view/event/"+str(event_id), add_view_fields=True)
  else:
    response.menu_fields = ""
    
  if (nervatype_audit_filter in ("readonly","disabled")) or (event_audit_filter in ("readonly","disabled")) or (setting_audit_filter in ("disabled")):
    response.cmd_groups = ""
  else:
    if session.mobile:
      response.cmd_groups = ui.control.get_mobil_button(label=T("Edit Groups"), href="#", 
        icon="gear", cformat=None, ajax="true", theme="b", rel="close",
        onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
            +"')){window.location ='"+URL("frm_groups_eventgroup?back=1")+"';};return false;")
    else:
      response.cmd_groups = ui.control.get_goprop_button(title=T("Edit Event Groups"), url=URL("frm_groups_eventgroup?back=1")) 
  
  return dict(form=form)

def frm_groups(groupname, cmd_lnk=None, audit_filter=None):
  ruri = request.wsgi.environ["REQUEST_URI"]
  response.view=ui.dir_view+'/groups.html'
  if not audit_filter:
    audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  
  if session.mobile:
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=groups'),
                                         cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:
    response.cmd_help = ui.control.get_help_button("groups")
  
  if (audit_filter=="all"):
    if session.mobile:
      response.cmd_groups_new = ui.control.get_mobil_button(cmd_id="cmd_groups_new",
          label=T("New Group"), href=URL("frm_groups_"+groupname+"/new/groups")+"?back=1", 
          cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
    else:
      response.cmd_groups_new = ui.control.get_new_button(URL("frm_groups_"+groupname+"/new/groups")+"?back=1")
  else:
    response.cmd_groups_new = ""
      
  if str(ruri).find("delete/groups")>0:
    group_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if not ns.connect.deleteData("groups", ref_id=group_id):
      session.flash = str(ns.error_message)
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(URL('frm_groups_'+groupname))
    redirect(URL('frm_groups_'+groupname))
  
  ns.db.groups.groupname.label = T("G.Type")
  if str(ruri).find("new/groups")>0 or str(ruri).find("edit/groups")>0 or str(ruri).find("view/groups")>0:
    response.prm_input = True
    if session.mobile:
      response.cmd_groups_close = ui.control.get_mobil_button(label=T("BACK"), href=URL('frm_groups_'+groupname),
        icon="back", theme="a", ajax="false")
    else:
      response.cmd_back = ui.control.get_back_button(URL('frm_groups_'+groupname))
    
    if str(ruri).find("new/groups")>0:
      groups_id=-1
      ns.db.groups.groupname.requires = IS_IN_SET(("customer","department","eventgroup","paidtype","product","toolgroup","trans","rategroup"))
      form = SQLFORM(ns.db.groups, submit_button=T("Save"),_id="frm_groups")
      if groupname!="all":
        form.vars.groupname=groupname
      response.subtitle=T('New value')
      response.cmd_delete = ""
    else: 
      groups_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      if ns.db.groups(id=groups_id).deleted==1:
        return ui.connect.show_disabled(response.title)
      ns.db.groups.groupname.writable = False
      response.subtitle=T('Edit value')
      form = SQLFORM(ns.db.groups, record = groups_id, submit_button=T("Save"),_id="frm_groups")
      if audit_filter=="all":
        if session.mobile:
          response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
                                            onclick="if(confirm('"+T('Are you sure you want to delete this group?')+
                              "')){window.location ='"+URL("frm_groups_"+groupname+"/delete/groups/"+str(groups_id))+"';};return false;", theme="b")
        else:
          response.cmd_delete = ui.control.get_command_button(caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this group?')+
                              "')){window.location ='"+URL("frm_groups_"+groupname+"/delete/groups/"+str(groups_id))+"';};return false;")
      else:
        response.cmd_delete = ""
      
    if form.validate(keepvalues=True):
      group = ns.db((ns.db.groups.id!=groups_id)&(ns.db.groups.groupname==request.post_vars.groupname)&(ns.db.groups.groupvalue==form.vars.groupvalue)).select().as_list()
      if len(group)==0:        
        if groups_id>0: form.vars.id = groups_id
        row_id = ns.connect.updateData("groups", values=form.vars, validate=False, insert_row=True)  
        if not row_id:
          response.flash = str(ns.error_message)
        else:
          if groups_id==-1:
            redirect(URL('frm_groups_'+groupname+'/view/groups/'+str(row_id)))
      else:
        form.errors["groupvalue"] = T('The group name already exists!')
        response.flash = T('Error: ')+str(T('The group name already exists!'))
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        if str(ns.db.groups.fields).find(error)>0:
          flash+=ns.db.groups[error].label+": "+form.errors[error]+", "
        else:
          flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    form.custom.widget.inactive = ui.control.get_bool_input(groups_id,"groups","inactive")
    if audit_filter=="readonly":
      form.custom.submit = ""
    elif session.mobile:
      form.custom.submit = ui.control.get_mobil_button(cmd_id="cmd_groups_update",
        label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_groups'].submit();")
  else:
    ns.db.groups.deleted.readable = ns.db.groups.deleted.writable = False
    if groupname!="all":
      groups = ((ns.db.groups.groupname==groupname)&(ns.db.groups.deleted==0))
      ns.db.groups.groupname.readable = ns.db.groups.groupname.writable = False
    else:
      groups = ((ns.db.groups.groupname.belongs(("customer","department","eventgroup","paidtype","product","toolgroup","trans","rategroup")))&(ns.db.groups.deleted==0))

    if session.mobile:
      if ns.db.groups.groupname.readable:
        fields = [ns.db.groups.id, ns.db.groups.groupvalue,ns.db.groups.groupname,ns.db.groups.description,ns.db.groups.inactive]
      else:
        fields = [ns.db.groups.id, ns.db.groups.groupvalue,ns.db.groups.description,ns.db.groups.inactive]
      
      if (cmd_lnk==None) and (audit_filter=="all"):
        ns.db.groups.id.label=T("Delete")
        ns.db.groups.id.represent = lambda value,row: ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="delete", iconpos="notext",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this group?")
            +"')){ajax('"+URL("frm_groups_"+groupname+"/delete/groups/"+str(row["id"]))
            +"',[],'');jQuery(this).closest('tr').remove();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}", 
          theme="d")
      else:
        ns.db.groups.id.readable = ns.db.groups.id.writable = False
      
      if (cmd_lnk==None):
        ns.db.groups.groupvalue.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_groups_"+groupname+"/edit/groups/"+str(row["id"])), 
                            cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
      else:
        cmd_lnk=None
      deletable = False
    else:
      response.cmd_back = ui.control.get_back_button(session.back_url)
      response.margin_top = "20px"
      ns.db.groups.id.readable = ns.db.groups.id.writable = False         
      if ns.db.groups.groupname.readable:
        fields = [ns.db.groups.groupname,ns.db.groups.groupvalue,ns.db.groups.description,ns.db.groups.inactive]
      else:
        fields = [ns.db.groups.groupvalue,ns.db.groups.description,ns.db.groups.inactive]
      deletable=((cmd_lnk==None) and (audit_filter=="all"))
        
    form = ui.select.find_data(table="groups",query=groups,fields=fields,orderby=ns.db.groups.groupvalue,
                       paginate=10,maxtextlength=25,links=cmd_lnk,left=None,page_url=None,
                       sortable=True,priority="0,1",deletable=deletable,fullrow=True)
  return form

@ns_auth.requires_login()
def frm_groups_all():
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  response.title=T('SETTINGS')
  response.subtitle=T('Groups')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_edit.png')
  response.sform = ui.select.create_search_form(URL("frm_groups_all"))
  return dict(form=frm_groups("all"))

@ns_auth.requires_login()
def frm_groups_customer():
  response.title=T('CUSTOMER')
  response.subtitle=T('Groups')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_customer.png')
  response.sform = ui.select.create_search_form(URL("frm_groups_customer"))
  return dict(form=frm_groups("customer"))

@ns_auth.requires_login()
def frm_groups_department():
  response.title=T('SETTINGS')
  response.subtitle=T('Departments')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_user.png')
  response.sform = ui.select.create_search_form(URL("frm_groups_department"))
  return dict(form=frm_groups("department"))

@ns_auth.requires_login()
def frm_groups_eventgroup():
  response.title=T('EVENT')
  response.subtitle=T('Groups')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_calendar.png')
  response.sform = ui.select.create_search_form(URL("frm_groups_eventgroup"))
  return dict(form=frm_groups("eventgroup"))

@ns_auth.requires_login()
def frm_groups_paidtype():
  response.title=T('SETTINGS')
  response.subtitle=T('Payment types')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_money.png')
  response.sform = ui.select.create_search_form(URL("frm_groups_paidtype"))
  return dict(form=frm_groups("paidtype"))

@ns_auth.requires_login()
def frm_groups_product():
  response.title=T('PRODUCT')
  response.subtitle=T('Groups')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_parts.png')
  response.sform = ui.select.create_search_form(URL("frm_groups_product"))
  return dict(form=frm_groups("product"))

@ns_auth.requires_login()
def frm_groups_rategroup():
  response.title=T('RATE')
  response.subtitle=T('Groups')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_percent.png')
  response.sform = ui.select.create_search_form(URL("frm_groups_rategroup"))
  return dict(form=frm_groups("rategroup"))

@ns_auth.requires_login()
def frm_groups_toolgroup():
  response.title=T('TOOL')
  response.subtitle=T('Groups')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_wrench.png')
  response.sform = ui.select.create_search_form(URL("frm_groups_toolgroup"))
  return dict(form=frm_groups("toolgroup"))

@ns_auth.requires_login()
def frm_groups_trans():
  response.title=T('TRANSACTION')
  response.subtitle=T('Groups')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_edit.png')
  response.sform = ui.select.create_search_form(URL("frm_groups_trans"))
  return dict(form=frm_groups("trans"))

@ns_auth.requires_login()
def frm_groups_usergroup():
  audit_filter_setting = ui.connect.get_audit_filter("setting", None)[0]
  audit_filter_audit = ui.connect.get_audit_filter("audit", None)[0]
  if audit_filter_setting=="disabled" or audit_filter_audit=="disabled":
    audit_filter="disabled"
  elif audit_filter_setting=="readonly" or audit_filter_audit=="readonly":
    audit_filter="readonly"
  elif audit_filter_setting=="update" or audit_filter_audit=="update":
    audit_filter="update"
  else:
    audit_filter="all"
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  response.title=T('SETTINGS')
  response.subtitle=T('User groups and access rights')
  ruri = request.wsgi.environ["REQUEST_URI"]
  if str(ruri).find("new/groups")>0:
    redirect(URL('frm_audit/new/usergroup'))
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL('index')
    response.titleicon = URL(ui.dir_images,'icon16_user.png')
    cmd_lnk = [lambda row: A(SPAN(_class="icon key"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("frm_audit/view/usergroup/"+str(row.id)), _title=T("Access rights"))]
  else:
    cmd_lnk = True
    ns.db.groups.groupvalue.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_audit/view/usergroup/"+str(row.id)), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
  response.sform = ui.select.create_search_form(URL("frm_groups_usergroup"))
  return dict(form=frm_groups("usergroup",cmd_lnk,audit_filter))

def frm_menucmd():
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  response.title=T('SETTINGS')
  response.view=ui.dir_view+'/menucmd.html'
  if session.mobile:
    response.cmd_menucmd_close = ui.control.get_mobil_button(label=T("BACK"), href=URL('frm_quick_menucmd'),
        icon="back", theme="a", ajax="false")
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=menucmd'),
                                             cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_world_link.png')
    response.cmd_help = ui.control.get_help_button("menucmd")
  
  if str(ruri).find("delete/ui_menufields")>0:
    menufields_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    menu_id = ns.db.ui_menufields(id=menufields_id).menu_id
    ns.connect.deleteData("ui_menufields", ref_id=menufields_id)
    redirect(URL('frm_menucmd/view/ui_menu/'+str(menu_id)))
    
  if str(ruri).find("delete/ui_menu")>0:
    menu_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    
    menufields = ns.db(ns.db.ui_menufields.menu_id==menu_id).select(ns.db.ui_menufields.id)
    for menufields_id in menufields:
      ns.connect.deleteData("ui_menufields", ref_id=menufields_id)
    ns.connect.deleteData("ui_menu", ref_id=menu_id)
    redirect(URL('frm_quick_menucmd'))
  
  if str(ruri).find("edit/ui_menufields")>0 or str(ruri).find("view/ui_menufields")>0 or str(ruri).find("new/ui_menufields")>0:
    response.prm_input = True
    if str(ruri).find("new/ui_menufields")>0:
      menufields_id=-1
      menu_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      response.subtitle=T('New parameter')
      form = SQLFORM(ns.db.ui_menufields, submit_button=T("Save"), _id="frm_menufields")
      form.vars.fieldtype = ns.valid.get_groups_id("fieldtype", "string")
    else:
      menufields_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      menu_id = ns.db.ui_menufields(id=menufields_id).menu_id
      response.subtitle=T('Edit parameter')
      form = SQLFORM(ns.db.ui_menufields, record = menufields_id, submit_button=T("Save"), _id="frm_menufields")
    
    if session.mobile:
      response.cmd_delete_menufields = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
          onclick="javascript:if(confirm(w2p_ajax_confirm_message||'"+T('Are you sure you want to delete this field?')
            +"')){window.location ='"+URL("frm_menucmd/delete/ui_menufields/"+str(menufields_id))+"';};return false;", theme="b")
      response.cmd_menufields_close = ui.control.get_mobil_button(label=T("BACK"), href=URL('frm_menucmd/view/ui_menu/'+str(menu_id)),
          icon="back", theme="a", ajax="false")
    else:
      response.cmd_back = ui.control.get_back_button(URL('frm_menucmd/view/ui_menu/'+str(menu_id)))
    
    if request.post_vars:
      request.post_vars.menu_id = menu_id
    if form.validate(keepvalues=True):      
      if menufields_id>0: form.vars.id = menufields_id
      row_id = ns.connect.updateData("ui_menufields", values=form.vars, validate=False, insert_row=True)  
      if not row_id:
        response.flash = str(ns.error_message)
      else:
        if menufields_id==-1:
          redirect(URL('frm_menucmd/view/ui_menufields/'+str(row_id)))
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    if audit_filter=="readonly":
      form.custom.submit=""
    elif session.mobile:
      form.custom.submit = ui.control.get_mobil_button(label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_menufields'].submit();")
    return dict(form=form,view_menufields="")
  
  ns.db.ui_menu.address.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
  if str(ruri).find("edit/ui_menu")>0 or str(ruri).find("view/ui_menu")>0: 
    menu_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])   
    response.subtitle=T('Edit shortcut')
    form = SQLFORM(ns.db.ui_menu, record = menu_id, submit_button=T("Save"), _id="frm_menu")
    if session.mobile:
      response.cmd_delete_menu = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
          onclick="javascript:if(confirm(w2p_ajax_confirm_message||'"+T('Are you sure you want to delete this shortcut?')
          +"')){window.location ='"+URL("frm_menucmd/delete/ui_menu/"+str(menu_id))+"';};return false;", theme="b")
      ns.db.ui_menufields.fieldname.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_menucmd/edit/ui_menufields/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
      deletable = False
    else:
      response.cmd_delete = INPUT(_type="button", _value=T("Delete"),
                                _style="height: 25px !important;padding-top: 2px !important;color: #A52A2A;width: 100%;", 
                                _onclick="javascript:if(confirm(w2p_ajax_confirm_message||'"+T('Are you sure you want to delete this shortcut?')
                                  +"')){window.location ='"+URL("frm_menucmd/delete/ui_menu/"+str(menu_id))+"';};return false;")
      deletable = (audit_filter=="all")
  
    menufields = ((ns.db.ui_menufields.menu_id==menu_id))
    ns.db.ui_menufields.id.readable = ns.db.ui_menufields.id.writable = False
    ns.db.ui_menufields.menu_id.readable = ns.db.ui_menufields.menu_id.writable = False
    
    view_menufields = ui.select.find_data(table="ui_menufields",query=menufields,fields=None,orderby=ns.db.ui_menufields.id,
                      paginate=None,maxtextlength=20,left=None,sortable=False,page_url=None,deletable=deletable,fullrow=True)
  else:
    menu_id=-1
    form = SQLFORM(ns.db.ui_menu, submit_button=T("Save"), _id="frm_menu")
    response.subtitle=T('New shortcut')
    response.cmd_add_field = ""
    response.cmd_delete = ""
    view_menufields=""
    response.cmd_delete_menu = ""
    
  if form.validate(keepvalues=True):
    if menu_id>0: form.vars.id = menu_id
    row_id = ns.connect.updateData("ui_menu", values=form.vars, validate=False, insert_row=True)  
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      if menu_id==-1:
        redirect(URL('frm_menucmd/view/ui_menu/'+str(row_id)))
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  if not session.mobile:
    response.cmd_back = ui.control.get_back_button(URL('frm_quick_menucmd'))
  if menu_id>-1:
    if session.mobile:
      response.cmd_add_menufields = ui.control.get_mobil_button(
        label=T("Add paramater"), href=URL('frm_menucmd/new/ui_menufields/'+str(menu_id)), 
        cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
    else:
      response.cmd_add_field = A(SPAN(_class="icon plus"), _style="height: 15px;vertical-align: middle;padding-top: 2px;padding-bottom: 4px;", 
               _class="w2p_trap buttontext button", 
             _href=URL('frm_menucmd/new/ui_menufields/'+str(menu_id)), _title=T("Add paramater"))
  else:
    response.cmd_add_field = ""
  form.custom.widget.url = ui.control.get_bool_input(menu_id,"ui_menu","url")
  if audit_filter=="readonly":
    form.custom.submit=""
  elif session.mobile:
    form.custom.submit = ui.control.get_mobil_button(label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_menu'].submit();")
  return dict(form=form,view_menufields=view_menufields)

def frm_numberdef():
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  response.view=ui.dir_view+'/numberdef.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Transaction Numbering')
  if session.mobile:
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=numberdef'),
      cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_numberdef.png')
    response.cmd_help = ui.control.get_help_button("numberdef")
  
  ns.db.numberdef.id.readable = ns.db.numberdef.id.writable = False
  ns.db.numberdef.visible.readable = ns.db.numberdef.visible.writable = False
  ns.db.numberdef.readonly.readable = ns.db.numberdef.readonly.writable = False
  ns.db.numberdef.orderby.readable = ns.db.numberdef.orderby.writable = False
  ns.db.numberdef.numberkey.writable = False
  ns.db.numberdef.description.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
  if str(ruri).find("edit/numberdef")>0:
    response.edit = True
    sform=None
    response.subtitle=T('Edit value')
    if session.mobile:
      response.cmd_numberdef_close = ui.control.get_mobil_button(label=T("BACK"), href=URL('frm_numberdef'),
        icon="back", theme="a", ajax="false")
    else:
      response.cmd_back = ui.control.get_back_button(URL('frm_numberdef'))
    numberdef_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    form = SQLFORM(ns.db.numberdef, record=numberdef_id, submit_button=T("Save"), comments = False, formstyle = 'divs', _id="frm_numberdef")
    if form.validate(keepvalues=True):
      form.vars.id = numberdef_id
      row_id = ns.connect.updateData("numberdef", values=form.vars, validate=False, insert_row=True)  
      if not row_id:
        response.flash = str(ns.error_message)
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    form.custom.widget.isyear = ui.control.get_bool_input(numberdef_id,"numberdef","isyear")
    response.readonly = ns.db.numberdef(id=numberdef_id)["readonly"]
    if audit_filter=="readonly":
      form.custom.submit=""
    elif session.mobile:
      form.custom.submit = ui.control.get_mobil_button(label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_numberdef'].submit();")
  else:
    if session.mobile:
      ns.db.numberdef.numberkey.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_numberdef/edit/numberdef/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    else:
      response.margin_top = "20px"
      response.cmd_back = ui.control.get_home_button()
    numberdef = ((ns.db.numberdef.visible==1))
    fields = [ns.db.numberdef.numberkey,ns.db.numberdef.prefix,ns.db.numberdef.curvalue,ns.db.numberdef.isyear,ns.db.numberdef.sep,
              ns.db.numberdef.len,ns.db.numberdef.description]
    
    sform = DIV(ui.select.create_search_form(URL("frm_numberdef")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
    form = ui.select.find_data(table="numberdef",query=numberdef,fields=fields,orderby=ns.db.numberdef.numberkey,
                      paginate=10,maxtextlength=20,left=None,sortable=True,page_url=None,deletable=False,fullrow=True)
  
  return dict(form=DIV(form, _id="dlg_frm"),sform=sform)

@ns_auth.requires_login()
def frm_password():
  ruri = request.wsgi.environ["REQUEST_URI"]
  employee_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  employee = ns.db.employee(id=employee_id)
  if session.mobile:
    response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'), icon="home", cformat="ui-btn-left", ajax="false")
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=index'),
                                               cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
    if request.wsgi.environ.has_key("HTTP_REFERER"):
      if request.wsgi.environ["HTTP_REFERER"].find("frm_password")>-1:
        response.cmd_back = ui.control.get_mobil_button(label=T("EMPLOYEE"), 
          href=URL('frm_employee/view/employee/'+str(employee_id)), icon="back", cformat="ui-btn-left", ajax="false")
      else:
        response.cmd_back = ui.control.get_mobil_button(label=T("BACK"), 
          href=request.wsgi.environ["HTTP_REFERER"], icon="back", cformat="ui-btn-left", ajax="false")
    if DEMO_MODE:
      response.cmd_update = DIV(SPAN(T('DEMO MODE')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding:9px;")
    else:
      response.cmd_update = ui.control.get_mobil_button(cmd_id="cmd_update",
        label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_password'].submit();")
  else:
    if request.wsgi.environ.has_key("HTTP_REFERER"):
      if request.wsgi.environ["HTTP_REFERER"].find("frm_password")>-1:
        response.back_url = URL('frm_employee/view/employee/'+str(employee_id))
      else:
        response.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      response.back_url = URL('index')
    response.titleicon = URL(ui.dir_images,'icon16_key.png')
  response.view=ui.dir_view+'/password.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Changing the password')
  if employee["username"]==None or employee["username"]=="":
    response.enabled = False
    response.username = "Missing username!"
  else:
    response.enabled = True
    response.username = employee["username"]
  form = SQLFORM.factory(
    Field('password_1', type='password', length=50, label=T('New password')),
    Field('password_2', type='password', length=50, label=T('Verify password')),
    submit_button=T("Save"), table_name="change", _id="frm_password"
  )
  if form.process().accepted:
    if form.vars.password_1!=form.vars.password_2:
      form.errors["password_2"]="Password fields don't match"
      response.flash = T("Form has errors: Password fields don't match")
    else:
      if form.vars.password_1=="":
        password=None
      else:
        password = ns.valid.get_md5_value(form.vars.password_1)
      row_id = ns.connect.updateData(nervatype="employee", values={"id":employee_id,"password":password}, validate=False)
      if not row_id:
        response.flash = "Error|"+str(ns.error_message)
  if DEMO_MODE:
    form.custom.submit = DIV(SPAN(T('DEMO MODE')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
  return dict(form=form)

@ns_auth.requires_login()
def frm_place():
  place_audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if place_audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    place_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["place_page_"+str(place_id)] = "fieldvalue_page"
    redirect(URL('frm_place/view/place/'+str(place_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    place_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["place_page_"+str(place_id)] = "fieldvalue_page"
    if ns.connect.deleteData("fieldvalue", ref_id=fieldvalue_id):
      redirect(URL('frm_place/view/place/'+str(place_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    ui.connect.clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    row_id = ns.connect.updateData("fieldvalue", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["place_page_"+str(request.post_vars["ref_id"])] = "fieldvalue_page"
      redirect()
  
  if ruri.find("edit/contact")>0 or ruri.find("view/contact")>0:
    contact_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    place_id = ns.db.contact(id=contact_id).ref_id
    session["place_page_"+str(place_id)] = "contact_page"
    redirect(URL('frm_place/view/place/'+str(place_id)))
    
  if ruri.find("delete/contact")>0:
    contact_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    place_id = ns.db.contact(id=contact_id).ref_id
    session["place_page_"+str(place_id)] = "contact_page"
    if ns.connect.deleteData("contact", ref_id=contact_id):
      redirect(URL('frm_place/view/place/'+str(place_id)))
        
  if request.post_vars["_formname"]=="contact/create":
    ui.connect.clear_post_vars()
    row_id = ns.connect.updateData("contact", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["place_page_"+str(request.post_vars["ref_id"])] = "contact_page"
      redirect()
  
  if ruri.find("new/place")>0:
    place_id = -1
    placetype=""
  else:
    place_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    placetype= ns.db((ns.db.groups.id==ns.db.place(id=place_id).placetype)).select().as_list()[0]["groupvalue"]
    if ns.db.place(id=place_id).deleted==1:
      return ui.connect.show_disabled(response.title)
      
  if ruri.find("delete/place")>0:
    if not ns.connect.deleteData("place", ref_id=place_id):
      session.flash = str(ns.error_message)
      redirect(URL('frm_place/view/place/'+str(place_id)))
    else:
      redirect(URL('frm_quick_place'))
  
  response.view=ui.dir_view+'/place.html'
  response.title=T("PLACE")
  response.lo_menu = []
  if not session.mobile:
    response.titleicon = URL(ui.dir_images,'icon16_book.png')
    response.icon_deffield = IMG(_src=URL(ui.dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_contact = IMG(_src=URL(ui.dir_images,'icon16_contact.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  nervatype_place = ns.valid.get_groups_id("nervatype", "place")
  
  #basic place data
  if placetype not in ("bank", "cash"):
    ns.db.place.curr.readable = ns.db.place.curr.writable = False
  else:
    ns.db.place.curr.requires = IS_IN_DB(ns.db(ns.db.currency), ns.db.currency.curr, '%(curr)s')
  ns.db.place.deleted.readable = ns.db.place.deleted.writable = False
  ns.db.place.description.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
  if place_id>0:
    ns.db.place.placetype.writable = False
    form = SQLFORM(ns.db.place, record = place_id, submit_button=T("Save"), _id="frm_place")
    response.subtitle=ns.db.place(id=place_id).planumber
    if place_audit_filter!="disabled":
      response.cmd_report = ui.control.get_report_button(nervatype="place", title=T('Place Reports'), ref_id=place_id,
                                              label=response.subtitle)
    else:
      response.cmd_report = ""
    if place_audit_filter=="all":
      if session.mobile:
        response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
                                            onclick="if(confirm('"+T('Are you sure you want to delete this place?')+
                                            "')){window.location ='"+URL("frm_place/delete/place/"+str(place_id))+"';};return false;", theme="b")
      else:
        response.cmd_delete = ui.control.get_command_button(_id="cmd_delete", caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this place?')+
                              "')){window.location ='"+URL("frm_place/delete/place/"+str(place_id))+"';};return false;")
    else:
      response.cmd_delete = ""
    address = ns.db((ns.db.address.deleted==0)&(ns.db.address.nervatype==nervatype_place)&(ns.db.address.ref_id==place_id)).select()
    if len(address)>0:
      address_id = address[0].id
    else:
      address_id = ns.connect.updateData("address", values={"nervatype":nervatype_place,"ref_id":place_id}, 
                                         validate=False, insert_row=True)
  else:
    form = SQLFORM(ns.db.place, submit_button=T("Save"), _id="frm_place")
    form.vars.planumber = ns.connect.nextNumber("planumber",False)
    form.vars.placetype = ns.valid.get_groups_id("placetype", "bank")
    response.subtitle=T('New place')
    response.serial=""
    response.cmd_report = ""
    response.cmd_delete = ""
    address_id=None
  
  if session.mobile:
    if place_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
                                               icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
    else:
      response.cmd_back = ui.control.get_mobil_button(label=T("SEARCH"), href=URL("frm_quick_place"), icon="search", cformat="ui-btn-left", ajax="false") 
  
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=place'),
                                           cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:    
    if place_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_home_button()
    else:
      response.cmd_back = ui.control.get_back_button(URL("frm_quick_place")) 
    response.cmd_help = ui.control.get_help_button("place")
  
  if place_audit_filter in ("readonly","disabled"):
    form.custom.submit = ""
  elif session.mobile:
    form.custom.submit = ui.control.get_mobil_button(label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_place'].submit();")
  
  if form.validate(keepvalues=True):   
    if place_id==-1:
      nextnumber = ns.connect.nextNumber("planumber",False)
      if form.vars.planumber == nextnumber:
        form.vars.planumber = ns.connect.nextNumber("planumber")
    else:
      form.vars.id = place_id
    row_id = ns.connect.updateData("place", values=form.vars, validate=False, insert_row=True)  
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      values = {"nervatype":nervatype_place,"ref_id":row_id,"zipcode":request.post_vars.zipcode,
                "city":request.post_vars.city,"street":request.post_vars.street}
      address = ns.db((ns.db.address.ref_id==row_id)&(ns.db.address.nervatype==nervatype_place)
                      &(ns.db.address.deleted==0)).select()
      if len(address)>0: values["id"]=address[0]["id"]
      address_id = ns.connect.updateData("address", values=values, validate=False, insert_row=True)  
      if not address_id:
        response.flash = str(ns.error_message)
      redirect(URL('frm_place/view/place/'+str(row_id)))
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      if str(ns.db.place.fields).find(error)>0:
        flash+=ns.db.place[error].label+": "+form.errors[error]+", "
      else:
        flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  else:
    pass
    
  form.custom.widget.inactive = ui.control.get_bool_input(place_id,"place","inactive")
  if address_id:
    response.zipcode = INPUT(_name="zipcode", _type="text", _value=str(ns.db.address(id=address_id).zipcode), _id="address_zipcode", _class="string")
    response.city = INPUT(_name="city", _type="text", _value=str(ns.db.address(id=address_id).city), _id="address_city", _class="string")
    response.street = INPUT(_name="street", _type="text", _value=str(ns.db.address(id=address_id).street), _id="address_street", _class="string")
  else:
    response.zipcode = INPUT(_name="zipcode", _type="text", _value="", _id="address_zipcode", _class="string")
    response.city = INPUT(_name="city", _type="text", _value="", _id="address_city", _class="string")
    response.street = INPUT(_name="street", _type="text", _value="", _id="address_street", _class="string")
  
  if session.mobile:
    if session["place_page_"+str(place_id)]:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value=session["place_page_"+str(place_id)])
      session["place_page_"+str(place_id)]="place_page"
    else:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value="place_page")
      
    response.menu_place = ui.control.get_mobil_button(T("Place Data"), href="#", 
        cformat=None, icon="edit", style="text-align: left;",
        onclick= "show_page('place_page');", theme="a", rel="close")
  
  #additional fields data
  if place_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_place)&(ns.db.fieldvalue.ref_id==place_id))
    editable = not (place_audit_filter in ("readonly","disabled"))
    ui.select.set_view_fields("place", nervatype_place, 0, editable, fieldvalue, place_id, "/frm_place", "/frm_place/view/place/"+str(place_id))
  else:
    response.menu_fields = ""
  
  #contact data
  if place_id>-1:
    contact = ((ns.db.contact.ref_id==place_id)&(ns.db.contact.nervatype==nervatype_place)&(ns.db.contact.deleted==0))
    contact_count = ns.db(contact).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if session.mobile:
      links = None
      response.menu_contact = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Contact Info"),contact_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('contact_page');",
        theme="a", rel="close")
      ns.db.contact.id.label = T("*")
      ns.db.contact.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, icon="edit", style="text-align: left;",
                            onclick="set_contact("
                             +str(row["id"])+",'"
                             +json.dumps(str(row["firstname"]))[1:-1]+"','"
                             +json.dumps(str(row["surname"]))[1:-1]+"','"
                             +json.dumps(str(row["status"]))[1:-1]+"','"
                             +json.dumps(str(row["phone"]))[1:-1]+"','"
                             +json.dumps(str(row["fax"]))[1:-1]+"','"
                             +json.dumps(str(row["mobil"]))[1:-1]+"','"
                             +json.dumps(str(row["email"]))[1:-1]+"','"
                             +json.dumps(str(row["notes"]))[1:-1]+"')")
    else:
      ns.db.contact.id.label = T("No.")
      ns.db.contact.id.represent = lambda value,row: ui.control.format_value("integer",row["id"])
      links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                             _class="w2p_trap buttontext button", _href="#", _onclick="set_contact("
                             +str(row["id"])+",'"
                             +json.dumps(str(row["firstname"]))[1:-1]+"','"
                             +json.dumps(str(row["surname"]))[1:-1]+"','"
                             +json.dumps(str(row["status"]))[1:-1]+"','"
                             +json.dumps(str(row["phone"]))[1:-1]+"','"
                             +json.dumps(str(row["fax"]))[1:-1]+"','"
                             +json.dumps(str(row["mobil"]))[1:-1]+"','"
                             +json.dumps(str(row["email"]))[1:-1]+"','"
                             +json.dumps(str(row["notes"]))[1:-1]+"')",
                             _title=T("Edit Contact"))]
    ns.db.contact.nervatype.readable = ns.db.contact.ref_id.readable = ns.db.contact.deleted.readable = False
    
    if place_audit_filter in ("readonly","disabled"):
      if session.mobile:
        response.cmd_contact_new = ""
      else:
        response.cmd_contact_new = SPAN(" ",SPAN(str(contact_count), _class="detail_count"))
      response.cmd_contact_update = ""
      response.cmd_contact_delete = ""
    else:
      if session.mobile:
        response.cmd_contact_update = ui.control.get_mobil_button(cmd_id="cmd_contact_update",
          label=T("Save Contact"), href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
          onclick= "document.forms['frm_contact'].submit();")
        response.cmd_contact_delete = ui.control.get_mobil_button(cmd_id="cmd_contact_delete",
          label=T("Delete Contact"), href="#", 
          cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to delete this data?')+
                              "')){if(document.getElementById('contact_id').value>-1){window.location = '"
            +URL("frm_place")+"/delete/contact/'+document.getElementById('contact_id').value;} else {show_page('contact_page');}}")
        response.cmd_contact_new = ui.control.get_mobil_button(cmd_id="cmd_contact_new",
          label=T("New Contact"), href="#", 
          cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
          onclick= "set_contact(-1,'','','','','','','','');", rel="close")
        response.cmd_contact_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
          icon="back", ajax="true", theme="a",  
          onclick= "show_page('contact_page');", rel="close")
      else:
        links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this contact?')+
                                "')){window.location ='"+URL("frm_place/delete/contact/"+str(row.id))+"';};return false;", 
                           _title=T("Delete Contact")))
        response.cmd_contact_update = ui.control.get_command_button(caption=T("Save"),title=T("Update contact data"),color="008B00", _id="cmd_contact_submit",
                                cmd="contact_update();return true;")
        response.cmd_contact_new = ui.control.get_tabnew_button(contact_count,T('New Contact'),cmd_id="cmd_contact_new",
                                  cmd = "$('#tabs').tabs({ active: 2 });set_contact(-1,'','','','','','','','')")
  
    response.view_contact = ui.select.get_tab_grid(_query=contact, _field_id=ns.db.contact.id, _fields=None, _deletable=False, _editable=False, links=links, 
                               multi_page="contact_page", rpl_1="/frm_place", rpl_2="/frm_place/view/place/"+str(place_id),_priority="0,1,2")
    
    response.contact_form = SQLFORM(ns.db.contact, submit_button=T("Save"),_id="frm_contact")
    response.contact_form.process()
    if not session.mobile:
      response.contact_icon = URL(ui.dir_images,'icon16_contact.png')
      response.cmd_contact_cancel = A(SPAN(_class="icon cross"), _id="cmd_contact_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_contact').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.contact_id = INPUT(_name="id", _type="hidden", _value="", _id="contact_id")
    response.contact_ref_id = INPUT(_name="ref_id", _type="hidden", _value=place_id, _id="contact_ref_id")
    response.contact_nervatype = INPUT(_name="nervatype", _type="hidden", _value=nervatype_place, _id="contact_nervatype")
  else:
    response.menu_contact = ""
              
  return dict(form=form)

@ns_auth.requires_login()
def frm_printqueue():
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if request.vars.has_key("get_report"):
    params, filters = {}, {}
    params["report_id"]=request.vars.report_id
    params["output"]="pdf"
    params["orientation"]=request.vars.orientation
    params["size"]=request.vars.size
    filters["@id"]=request.vars.ref_id
    return base64.b64encode(ui.dbout.getReport(params, filters)["template"])
  
  if request.vars.has_key("delete_rows"):
    if request.vars.has_key("rows"):
      rows = request.vars.rows.split("|")
      for row in rows:
        row = row.split(",")
        ns.connect.deleteData("ui_printqueue", ref_id=row[0])
    return "OK"
      
  if ruri.find("delete/ui_printqueue")>0:
    queue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    ns.connect.deleteData("ui_printqueue", ref_id=queue_id)
    redirect(URL('frm_printqueue'))
    
  filter_form = SQLFORM.factory(
    Field('nervatype', "string", label=T('Type'), 
              requires = IS_EMPTY_OR(IS_IN_SET(["customer","product","employee","tool","project","order","offer","invoice",
                                                "receipt","rent","worksheet","delivery","inventory","waybill","production",
                                                "formula","bank","cash"]))),
    Field('transnumber', type='string', length=50, label=T('Doc.No.'), default=""),
    Field('fromdate', type='date', label=T('From Date')),
    Field('enddate', type='date', label=T('End Date')),
    Field('username', type='string', length=50, label=T('Username'), default=""),
    submit_button=T("Filter"), table_name="filter", _id="frm_print_filter", **{"_data-ajax":"false"}
  )
  
  errors={}
  query = (ns.db.ui_printqueue.id>0)
  if len(request.post_vars)>0:
    if request.post_vars.nervatype and request.post_vars.nervatype!="":
      if request.post_vars.nervatype in("order","offer","invoice","receipt","rent","worksheet","delivery","inventory","waybill","production","formula","bank","cash"):
        nervatype_id = ns.valid.get_groups_id("nervatype", "trans")
        transtype_id = ns.valid.get_groups_id("transtype", request.post_vars.nervatype)
        query= query&(ns.db.ui_printqueue.nervatype==nervatype_id)&(ns.db.ui_printqueue.ref_id==ns.db.trans.id)&(ns.db.trans.transtype==transtype_id)
      else:
        nervatype_id = ns.valid.get_groups_id("nervatype", request.post_vars.nervatype)
        query= query&(ns.db.ui_printqueue.nervatype==nervatype_id)
      filter_form.vars.nervatype=request.post_vars.nervatype
    if request.post_vars.transnumber and request.post_vars.transnumber!="":
      if request.post_vars.nervatype=="":
        errors["nervatype"]="Missing type!"
        response.flash = T("Form has errors: Doc.No.filter, but missing type!")
      else:
        if request.post_vars.nervatype in("order","offer","invoice","receipt","rent","worksheet","delivery","inventory","waybill","production","formula","bank","cash"):
          query= query&(ns.db.trans.transnumber.lower().like("%"+str(request.post_vars.transnumber).lower()+"%"))
        elif request.post_vars.nervatype=="customer":
          query= query&(ns.db.ui_printqueue.ref_id==ns.db.customer.id)&(ns.db.customer.custname.lower().like("%"+str(request.post_vars.transnumber).lower()+"%"))
        elif request.post_vars.nervatype=="product":
          query= query&(ns.db.ui_printqueue.ref_id==ns.db.product.id)&(ns.db.product.description.lower().like("%"+str(request.post_vars.transnumber).lower()+"%"))
        elif request.post_vars.nervatype=="employee":
          query= query&(ns.db.ui_printqueue.ref_id==ns.db.employee.id)&(ns.db.employee.empnumber.lower().like("%"+str(request.post_vars.transnumber).lower()+"%"))
        elif request.post_vars.nervatype=="tool":
          query= query&(ns.db.ui_printqueue.ref_id==ns.db.tool.id)&(ns.db.tool.serial.lower().like("%"+str(request.post_vars.transnumber).lower()+"%"))
        elif request.post_vars.nervatype=="project":
          query= query&(ns.db.ui_printqueue.ref_id==ns.db.project.id)&(ns.db.project.pronumber.lower().like("%"+str(request.post_vars.transnumber).lower()+"%"))
      filter_form.vars.transnumber=request.post_vars.transnumber
    if request.post_vars.fromdate and request.post_vars.fromdate!="":
      query= query&(ns.db.ui_printqueue.crdate>=datetime.datetime.strptime(request.post_vars.fromdate, str('%Y-%m-%d')))
      filter_form.vars.fromdate=request.post_vars.fromdate
    if request.post_vars.enddate and request.post_vars.enddate!="":
      query= query&(ns.db.ui_printqueue.crdate<=datetime.datetime.strptime(request.post_vars.enddate, str('%Y-%m-%d')))
      filter_form.vars.enddate=request.post_vars.enddate
    if request.post_vars.username and request.post_vars.username!="":
      query= query&(ns.db.ui_printqueue.employee_id==ns.db.employee.id)&(ns.db.employee.username==request.post_vars.username)
      filter_form.vars.username=request.post_vars.username
  
  #set transfilter
  query = ui.select.set_transfilter(query,ns.db.ui_printqueue,"employee_id")
    
  if request.vars.has_key("print_selected"):
    if request.vars.selected_row!=None:
      if request.vars.printer_type in("local","export"):
        print_selected = []
        [print_selected.append(int(id_row)) for id_row in request.vars.selected_row]
        print_filter = ns.db(ns.db.ui_printqueue.id.belongs(print_selected)).select()
        print_selected = []
        [print_selected.append([int(id_row.id),int(id_row.report_id),int(id_row.ref_id),int(id_row.qty),
                                re.sub(r'[^0-9a-zA-Z]+','_',ns.valid.show_refnumber("refnumber", ns.db.groups(id=id_row.nervatype).groupvalue, id_row.ref_id))]
                               ) for id_row in print_filter]
        return str(print_selected)[1:-1].replace("], [", "|").replace("[", "").replace("]", "").replace(" ", "")
      print_result = ui.dbout.printQueue(request.vars.printer, request.vars.selected_row, request.vars.orientation, request.vars.size)
      if not print_result["state"]:
        response.flash = print_result["error_message"]
    else:
      if request.vars.printer_type in("local","export"):
        return ""
  elif request.vars.has_key("print_filter"):
    print_filter = ns.db(query).select()
    print_selected = []
    if request.vars.printer_type in("local","export"):
      [print_selected.append([int(id_row.id),int(id_row.report_id),int(id_row.ref_id),int(id_row.qty),
                              re.sub(r'[^0-9a-zA-Z]+','_',ns.valid.show_refnumber("refnumber", ns.db.groups(id=id_row.nervatype).groupvalue, id_row.ref_id))]
                             ) for id_row in print_filter]
      return str(print_selected)[1:-1].replace("], [", "|").replace("[", "").replace("]", "").replace(" ", "")
    [print_selected.append(id_row.id) for id_row in print_filter]
    print_result = ui.dbout.printQueue(request.vars.printer, print_selected, request.vars.orientation, request.vars.size)
    if not print_result["state"]:
      response.flash = print_result["error_message"]
  else:
    if filter_form.validate(keepvalues=True, onsuccess=None):
      pass
    for error in errors.keys():
      filter_form.errors[error] = errors[error]
  
  printer_clienthost = ns.connect.getSetting("printer_clienthost")
  response.subtitle=T('PRINTER QUEUE')
  response.view=ui.dir_view+'/printqueue.html'
  if session.mobile:
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=printqueue'),
      cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
    response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
      icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
    response.cmd_filter_pop = ui.control.get_popup_cmd(pop_id="popup_filter",label=T("Filter data"),theme="b",inline=False,mini=False, picon="search")
    response.cmd_print_pop = ui.control.get_popup_cmd(pop_id="popup_print",label=T("Print/Export"),theme="b",inline=False,mini=False, picon="page")
    
    response.cmd_filter = ui.control.get_mobil_button(label=T("Filter data"), href="#", 
          cformat=None, style="text-align: left;", icon="search", ajax="false", theme="b",
          onclick= "set_filter_values();document.forms['frm_print_filter'].submit();")
    response.cmd_print_selected = ui.control.get_mobil_button(
          label=T("Print all selected items"), href="#", 
          cformat=None, style="text-align: left;", icon="page", ajax="false", theme="b",
          onclick= "set_filter_values();print_items('print_selected','"+printer_clienthost+"');")
    response.cmd_print_filter = ui.control.get_mobil_button(
          label=T("Print all filtered items"), href="#", 
          cformat=None, style="text-align: left;", icon="page", ajax="false", theme="b",
          onclick= "set_filter_values();print_items('print_filter','"+printer_clienthost+"');")
    fields = [ns.db.ui_printqueue.id, ns.db.ui_printqueue.ref_id, ns.db.ui_printqueue.qty, ns.db.ui_printqueue.nervatype,  
              ns.db.ui_printqueue.crdate, ns.db.ui_printqueue.employee_id, ns.db.ui_printqueue.report_id]
    links = [lambda row: INPUT(_type='checkbox', _name='selected_row', _value=row.id)]
    
    ns.db.ui_printqueue.id.label=T("?")
    ns.db.ui_printqueue.id.represent = lambda value,row: ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", iconpos="notext",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this object?")
            +"')){ajax('"+URL('frm_printqueue/delete/ui_printqueue')+"/"+str(row["id"])
            +"',[],'');jQuery(this).closest('tr').remove();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}", 
          theme="d")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_printer.png')
    response.cmd_back = ui.control.get_home_button()
    response.cmd_help = ui.control.get_help_button("printqueue")
    response.lo_menu = []
    response.cmd_print_selected = A(SPAN(_class="icon check")+SPAN(T("Selected Print"),_style="color: #4682B4;font-weight: bold;padding-right: 0px;padding-left: 3px;"), 
                                    _id="cmd_print_selected", 
                                       _style="width: 100%;padding: 0px;padding-left: 6px;padding-right: 3px;height: 22px;padding-top: 3px;", 
                                       _class="w2p_trap buttontext button", _href="#null", _title=T("Print all selected items"), 
                                       _onclick="print_items('print_selected','"+printer_clienthost+"');")
    response.cmd_print_filter = A(SPAN(_class="icon magnifier")+SPAN(T("Filter Print"),_style="color: #191970;font-weight: bold;padding-right: 0px;padding-left: 3px;"), 
                                    _id="cmd_print_filter", 
                                       _style="width: 100%;padding: 0px;padding-left: 6px;padding-right: 3px;height: 22px;padding-top: 3px;", 
                                       _class="w2p_trap buttontext button", _href="#null", _title=T("Print all filtered items"), 
                                       _onclick="print_items('print_filter','"+printer_clienthost+"');")
    ns.db.ui_printqueue.id.readable = ns.db.ui_printqueue.id.writable = False
    fields = [ns.db.ui_printqueue.id, ns.db.ui_printqueue.nervatype, ns.db.ui_printqueue.ref_id, ns.db.ui_printqueue.qty, 
              ns.db.ui_printqueue.crdate, ns.db.ui_printqueue.employee_id, ns.db.ui_printqueue.report_id]
    links = [lambda row: INPUT(_type='checkbox', _name='selected_row', _value=row.id)]
  
  printers = ns.db((ns.db.tool.deleted==0)&(ns.db.product.id==ns.db.tool.product_id)&(ns.db.product.deleted==0)
           &(ns.db.tool.inactive==0)&(ns.db.tool.toolgroup==ns.db.groups.id)
           &(ns.db.groups.groupvalue=='printer')).select(ns.db.tool.serial,orderby=ns.db.tool.id).as_list()
  response.cmb_printers = SELECT(*[OPTION(field["serial"], _value=field["serial"], 
                                          _selected=(field["serial"]==ns.connect.getSetting("default_printer"))) for field in printers], 
                                 _id="cmb_printers", _name="printer",_style="width: 100%;height: 28px;")
  
  if len(response.cmb_printers)==0:
    response.cmb_printers.insert(0, OPTION("", _value=""))
  response.cmb_printer_type = SELECT([OPTION(T("Server"), _value="server", _selected=(len(printers)>0)),
                                      OPTION(T("Local"), _value="local", _selected=(len(printers)==0)),
                                      OPTION(T("Export"), _value="export", _selected=False)], 
                                     _id="cmb_printer_type", _name="printer_type",_style="width: 100%;height: 28px;")
  
  orientation = ns.db((ns.db.groups.groupname=="orientation")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.id)
  response.cmb_orientation = SELECT(*[OPTION(T(ori["description"]), _value=ori["groupvalue"]) for ori in orientation], 
                             _id="cmb_orientation", _name="orientation",_style="width: 100%;height: 28px;")
  size = ns.db((ns.db.groups.groupname=="papersize")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.id)
  response.cmb_size = SELECT(*[OPTION(psize["description"], _value=psize["groupvalue"]) for psize in size], 
                             _id="cmb_size", _name="size",_style="width: 100%;height: 28px;")
  response.cmb_size[1]["_selected"]=["selected"]
  
  view_printqueue = SQLFORM.grid(query=query, field_id=ns.db.ui_printqueue.id, fields=fields, #headers=headers,
                 orderby=ns.db.ui_printqueue.id, sortable=True, paginate=25, maxtextlength=25,
                 searchable=False, csv=False, details=False, showbuttontext=False,
                 create=False, deletable=True, editable=False, selectable=False, links=links, user_signature=False,
                 buttons_placement = 'left', links_placement = 'left')
  if type(view_printqueue[1][0][0]).__name__!="TABLE":
    view_printqueue[1][0][0] = ""
  else:
    if session.mobile:
      htable = view_printqueue.elements("div.web2py_htmltable")
      if len(htable)>0:
        ui.control.set_htmltable_style(htable[0][0],"ui_printqueue_search","0,1,2")
        htable[0][0]["_width"]="100%"
      if view_printqueue[len(view_printqueue)-1]["_class"].startswith("web2py_paginator"):
        pages = view_printqueue[len(view_printqueue)-1].elements("a")
        for i in range(len(pages)):
          pages[i]["_data-ajax"] = "false"
  return dict(form=filter_form, view_printqueue=view_printqueue)

@ns_auth.requires_login()
def frm_product():
  audit_filter = ui.connect.get_audit_filter("product", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if request.vars.has_key("check_barcode"):
    if request.vars.barcode_id and request.vars.code:
      barcode = ns.db((ns.db.barcode.code==request.vars.code)&(ns.db.barcode.id!=request.vars.barcode_id)).select()
      if len(barcode)>0:
        return T("The barcode already exists!")
      else:
        return "OK"
    else:  
      return T("Missing parameters!")
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    product_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["product_page_"+str(product_id)] = "fieldvalue_page"
    redirect(URL('frm_product/view/product/'+str(product_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    product_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["product_page_"+str(product_id)] = "fieldvalue_page"
    if ns.connect.deleteData("fieldvalue", ref_id=fieldvalue_id):
      redirect(URL('frm_product/view/product/'+str(product_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    ui.connect.clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    row_id = ns.connect.updateData("fieldvalue", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["product_page_"+str(request.post_vars["ref_id"])] = "fieldvalue_page"
      redirect()
    
  if ruri.find("edit/barcode")>0 or ruri.find("view/barcode")>0:
    barcode_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    product_id = ns.db.barcode(id=barcode_id).product_id
    session["product_page_"+str(product_id)] = "barcode_page"
    redirect(URL('frm_product/view/product/'+str(product_id)))
    
  if ruri.find("delete/barcode")>0:
    barcode_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    product_id = ns.db.barcode(id=barcode_id).product_id
    session["product_page_"+str(product_id)] = "barcode_page"
    if ns.connect.deleteData("barcode", ref_id=barcode_id):
      redirect(URL('frm_product/view/product/'+str(product_id)))
        
  if request.post_vars["_formname"]=="barcode/create":
    ui.connect.clear_post_vars()
    if not request.post_vars.has_key("defcode"):
      request.post_vars["defcode"]=0
    else:
      request.post_vars["defcode"]=1
    if len(ns.db((ns.db.barcode.product_id==request.post_vars["product_id"])&(ns.db.barcode.defcode==1)).select())==0:
      request.post_vars["defcode"]=1
    else:
      if request.post_vars["defcode"]==1:
        barcodes = ns.db((ns.db.barcode.product_id==request.post_vars["product_id"])
                         &(ns.db.barcode.defcode==1)).select(ns.db.barcode.id)
        for barcode_id in barcodes:
          ns.connect.updateData("barcode", values={"id":barcode_id, "defcode":0}, validate=False, insert_row=True)
    row_id = ns.connect.updateData("barcode", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["product_page_"+str(request.post_vars["product_id"])] = "barcode_page"
      redirect()
  
  if ruri.find("event")>0:
    ruri = "frm_event/view"+ruri[ruri.find("frm_product/edit")+16:]
    redirect(URL(ruri))
  
  if ruri.find("new/link")>0:
    product_id = int(request.vars.refnumber)
    product_nervatype = ns.valid.get_groups_id("nervatype", "product")
    groups_id = int(request.vars.groups_id)
    groups_nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
    glink = ns.db((ns.db.link.ref_id_1==product_id)&(ns.db.link.nervatype_1==product_nervatype)&(ns.db.link.deleted==0)
              &(ns.db.link.nervatype_2==groups_nervatype)&(ns.db.link.ref_id_2==groups_id)).select().as_list()
    if len(glink)==0:
      values = {"nervatype_1":product_nervatype, "ref_id_1":product_id, "nervatype_2":groups_nervatype, "ref_id_2":groups_id}
      ns.connect.updateData("link", values=values, validate=False, insert_row=True)
    session["product_page_"+str(product_id)] = "groups_page"
    redirect(URL('frm_product/view/product/'+str(product_id)))
    
  if ruri.find("delete/link")>0:
    link_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ns.connect.deleteData("link", ref_id=link_id):
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(ruri[:ruri.find("delete/link")-1])
  
  if ruri.find("new/product")>0:
    product_id = -1
  else:
    product_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ns.db.product(id=product_id).deleted==1:
      return ui.connect.show_disabled(response.title)
      
  if ruri.find("delete/product")>0:
    if not ns.connect.deleteData("product", ref_id=product_id):
      session.flash = str(ns.error_message)
      redirect(URL('frm_product/view/product/'+str(product_id)))
    else:
      redirect(URL('find_product_product'))  
  
  response.view=ui.dir_view+'/product.html'
  if not session.mobile:
    response.titleicon = URL(ui.dir_images,'icon16_parts.png')
    response.icon_deffield = IMG(_src=URL(ui.dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_barcode = IMG(_src=URL(ui.dir_images,'icon16_barcode.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_calendar = IMG(_src=URL(ui.dir_images,'icon16_calendar.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.lo_menu = []
  
  nervatype_product = ns.valid.get_groups_id("nervatype", "product")
  nervatype_groups = ns.valid.get_groups_id("nervatype", "groups")  
  product_audit_filter = ui.connect.get_audit_filter("product", None)[0]
  price_audit_filter = ui.connect.get_audit_filter("price", None)[0]
  
  #basic product data
  ns.db.product.id.readable = ns.db.product.id.writable = False
  ns.db.product.deleted.readable = ns.db.product.deleted.writable = False
  if product_id>0:
    ns.db.product.protype.writable = False
    form = SQLFORM(ns.db.product, record = product_id, submit_button=T("Save"), _id="frm_product")
    response.subtitle=T("PRODUCT")
    response.partnumber=ns.db.product(id=product_id).partnumber
    if product_audit_filter!="disabled":
      response.cmd_report = ui.control.get_report_button(nervatype="product", title=T('Product Reports'), ref_id=product_id,
                                              label=response.partnumber)
    else:
      response.cmd_report = ""
    if product_audit_filter=="all":
      if session.mobile:
        response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
                                            onclick="if(confirm('"+T('Are you sure you want to delete this product?')+
                                            "')){window.location ='"+URL("frm_product/delete/product/"+str(product_id))+"';};return false;", theme="b")
      else:
        response.cmd_delete = ui.control.get_command_button(_id="cmd_delete", caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this product?')+
                              "')){window.location ='"+URL("frm_product/delete/product/"+str(product_id))+"';};return false;")
    else:
      response.cmd_delete = ""
    if price_audit_filter!="disabled":
      if session.mobile:
        response.cmd_price = ui.control.get_mobil_button(T("Price"), href="#", cformat=None, icon="dollar", style="text-align: left;",
                                            onclick="if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
                                  +"')){window.location ='"+URL('find_product_price/view/product/'+str(product_id))+"';};return false;", theme="b")
        response.cmd_discount = ui.control.get_mobil_button(T("Discount"), href="#", cformat=None, icon="dollar", style="text-align: left;",
                                            onclick="if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
                                  +"')){window.location ='"+URL("find_product_discount/"+str(product_id))+"';};return false;", theme="b")
      else:
        response.cmd_price = ui.control.get_command_button(_id="cmd_price", caption=T("Price"),title=T("Show Price"),color="483D8B",
                              _height="30px", _top="4px",
                              cmd="if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
                                  +"')){window.location ='"+URL('find_product_price/view/product/'+str(product_id))+"';};return false;")
        response.cmd_discount = ui.control.get_command_button(_id="cmd_discount", caption=T("Discount"),title=T("Show Discount"),color="483D8B",
                              _height="30px", _top="4px",
                              cmd="if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
                                  +"')){window.location ='"+URL("find_product_discount/"+str(product_id))+"';};return false;")
    else:
      response.cmd_price = ""
      response.cmd_discount = ""
  else:
    form = SQLFORM(ns.db.product, submit_button=T("Save"), _id="frm_product")
    form.vars.partnumber = ns.connect.nextNumber("partnumber",False)
    form.vars.protype = ns.valid.get_groups_id("protype", "item")
    if len(ns.db(ns.db.fieldvalue.fieldname=="default_unit").select().as_list())>0:
      form.vars.unit = ns.db.fieldvalue(fieldname="default_unit").value
    if len(ns.db(ns.db.fieldvalue.fieldname=="default_taxcode").select().as_list())>0:
      if len(ns.db(ns.db.tax.taxcode==ns.db.fieldvalue(fieldname="default_taxcode").value).select().as_list())>0:
        form.vars.tax_id = ns.db.tax(taxcode=ns.db.fieldvalue(fieldname="default_taxcode").value).id
      else:
        if len(ns.db(ns.db.tax.inactive==0).select().as_list())>0:
          form.vars.tax_id = ns.db(ns.db.tax.inactive==0).select().as_list()[0]["id"]
    else:
      form.vars.tax_id = ns.db(ns.db.tax.inactive==0).select().as_list()[0]["id"]
    response.subtitle=T('NEW PRODUCT')
    response.partnumber=""
    response.cmd_report = ""
    response.cmd_delete = ""
    response.cmd_price = ""
    response.cmd_discount = ""
  
  if session.mobile:
    if product_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
                                             icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
    else:
      response.cmd_back = ui.control.get_mobil_button(label=T("SEARCH"), href=URL("frm_quick_product"), icon="search", cformat="ui-btn-left", ajax="false")
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=product'),
                                         cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:
    if product_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_home_button()
    else:
      response.cmd_back = ui.control.get_back_button(URL("find_product_product")) 
    response.cmd_help = ui.control.get_help_button("product")
  
  if product_audit_filter in ("readonly","disabled"):
    form.custom.submit = "" 
  elif session.mobile:
    form.custom.submit = ui.control.get_mobil_button(label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_product'].submit();") 
            
  if form.validate(keepvalues=True):      
    if product_id==-1:
      nextnumber = ns.connect.nextNumber("partnumber",False)
      if form.vars.partnumber == nextnumber:
        form.vars.partnumber = ns.connect.nextNumber("partnumber")
    else:
      form.vars.id = product_id    
    row_id = ns.connect.updateData("product", values=form.vars, validate=False, insert_row=True)  
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      redirect(URL('frm_product/view/product/'+str(row_id)))
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      if str(ns.db.product.fields).find(error)>0:
        flash+=ns.db.product[error].label+": "+form.errors[error]+", "
      else:
        flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  form.custom.widget.webitem = ui.control.get_bool_input(product_id,"product","webitem")
  form.custom.widget.inactive = ui.control.get_bool_input(product_id,"product","inactive")
  
  if session.mobile:
    if session["product_page_"+str(product_id)]:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value=session["product_page_"+str(product_id)])
      session["product_page_"+str(product_id)]="product_page"
    else:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value="product_page")
    response.menu_product = ui.control.get_mobil_button(T("Product Data"), href="#", 
        cformat=None, icon="edit", style="text-align: left;",
        onclick= "show_page('product_page');", theme="a", rel="close")
  
  #show product groups list
  if product_id>-1:
    product_groups = ((ns.db.link.ref_id_1==product_id)&(ns.db.link.nervatype_1==nervatype_product)&
            (ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.deleted==0))
    ns.db.link.ref_id_2.represent = lambda value,row: ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")
    ns.db.link.nervatype_1.readable = ns.db.link.ref_id_1.readable = ns.db.link.nervatype_2.readable = ns.db.link.linktype.readable = ns.db.link.deleted.readable = False
    ns.db.link.ref_id_2.label = T('Groups')
    if session.mobile:
      groups_count = ns.db(product_groups).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
      response.menu_groups = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Product Groups"),groups_count), href="#", cformat=None, icon="star", style="text-align: left;",
        onclick= "show_page('groups_page');",
        theme="a", rel="close")
      if product_audit_filter not in ("readonly","disabled"):
        ns.db.link.id.label=T("Delete")
        ns.db.link.id.represent = lambda value,row: ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="delete", iconpos="notext",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this object?")
            +"')){ajax('"+URL('frm_product/delete/link')+"/"+str(row["id"])
            +"',[],'');jQuery(this).closest('tr').remove();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}", 
          theme="d")
      else:
        ns.db.link.id.readable = ns.db.link.id.writable = False
      deletable = False
    else:
      ns.db.link.id.readable = ns.db.link.id.writable = False
      deletable=(product_audit_filter not in ("readonly","disabled"))
    
    response.view_product_groups = ui.select.get_tab_grid(product_groups, ns.db.link.id, _fields=None, _editable=False, _deletable=deletable, links=None, 
                                    multi_page="groups_page", rpl_1="/frm_product", rpl_2="/frm_product/view/product/"+str(product_id))
    
    #show add/remove product groups combo and setting button
    if product_audit_filter not in ("readonly","disabled"):
      response.cmb_groups = ui.control.get_cmb_groups("product")
      if session.mobile:
        response.cmd_groups_add = ui.control.get_mobil_button(label=T("Add to Group"), href="#", 
          icon="plus", cformat=None, ajax="true", theme="b",
          onclick= "var group_id = document.getElementById('cmb_groups').value;if(group_id!=''){window.location ='"+URL("frm_product/new/link")
           +"?refnumber="+str(product_id)+"&groups_id='+group_id;} else {alert('"+T('Missing Product Group!')+"');return false;}")
        response.cmd_groups = ui.control.get_mobil_button(label=T("Edit Groups"), href="#", 
          icon="gear", cformat=None, ajax="true", theme="b", rel="close",
          onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
              +"')){window.location ='"+URL("frm_groups_product?back=1")+"';};return false;")
      else:                          
        response.cmd_groups_add = ui.control.get_icon_button(T('Add to Group'),"cmd_groups_add", 
          cmd="var group_id = document.getElementById('cmb_groups').value;if(group_id!=''){window.location ='"+URL("frm_product/new/link")
          +"?refnumber="+str(product_id)+"&groups_id='+group_id;} else {alert('"+T('Missing Transaction Group!')+"');return false;}")
        response.cmd_groups = ui.control.get_goprop_button(title=T("Edit Product Groups"), url=URL("frm_groups_product?back=1"))
    else:
      response.cmb_groups = ""
      response.cmd_groups = ""
      response.cmd_groups_add = ""
  else:
    response.menu_groups = ""
    
  setting_audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if setting_audit_filter=="disabled":
    response.cmd_groups = ""
    
  #additional fields data
  if product_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_product)&(ns.db.fieldvalue.ref_id==product_id))
    editable = not product_audit_filter in ("readonly","disabled")
    ui.select.set_view_fields("product", nervatype_product, 0, editable, fieldvalue, product_id, "/frm_product", "/frm_product/view/product/"+str(product_id))
  else:
    response.menu_fields = ""
      
  #barcode data
  if product_id>-1:
    barcode = ((ns.db.barcode.product_id==product_id))
    barcode_count = ns.db(barcode).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    ns.db.barcode.product_id.readable = ns.db.barcode.product_id.writable = False
    if session.mobile:
      links = None
      response.menu_barcode = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Barcodes"),barcode_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('barcode_page');",
        theme="a", rel="close")
      ns.db.barcode.id.label = T("*")
      ns.db.barcode.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, icon="edit", style="text-align: left;",
                            onclick="set_barcode("
                             +str(row["id"])+",'"
                             +json.dumps(str(row["code"]))[1:-1]+"','"
                             +json.dumps(str(row["description"]))[1:-1]+"',"
                             +str(row["barcodetype"])+","
                             +str(row["qty"])+","
                             +str(row["defcode"])+")", theme="d")
    else:
      ns.db.barcode.id.readable = ns.db.barcode.id.writable = False
      links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_barcode("
                           +str(row["id"])+",'"
                           +json.dumps(str(row["code"]))[1:-1]+"','"
                           +json.dumps(str(row["description"]))[1:-1]+"',"
                           +str(row["barcodetype"])+","
                           +str(row["qty"])+","
                           +str(row["defcode"])+")",
                           _title=T("Edit Barcode"))]
    
    if product_audit_filter not in ("readonly","disabled"):
      if session.mobile:
        response.cmd_barcode_update = ui.control.get_mobil_button(label=T("Save Barcode"), href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="true", theme="b",
          onclick= "barcode_update();return true;")
        response.cmd_barcode_delete = ui.control.get_mobil_button(label=T("Delete Barcode"), href="#", 
          cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to delete this data?')+
                              "')){if(document.getElementById('barcode_id').value>-1){window.location = '"
            +URL("frm_product")+"/delete/barcode/'+document.getElementById('barcode_id').value;} else {show_page('barcode_page');}}")
        response.cmd_barcode_new = ui.control.get_mobil_button(label=T("New Barcode"), href="#", 
          cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
          onclick= "set_barcode(-1,'','','',0,'');", rel="close")
        response.cmd_barcode_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
          icon="back", ajax="true", theme="a",  
          onclick= "show_page('barcode_page');", rel="close")
      else:
        links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this barcode?')+
                              "')){window.location ='"+URL("frm_product/delete/barcode/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Barcode")))
        response.cmd_barcode_update = ui.control.get_command_button(caption=T("Save"),title=T("Update barcode data"),color="008B00", _id="cmd_barcode_submit",
                              cmd="barcode_update();return true;")
        response.cmd_barcode_new = ui.control.get_tabnew_button(barcode_count,T('New Barcode'),cmd_id="cmd_barcode_new",
                                cmd = "$('#tabs').tabs({ active: 1 });set_barcode(-1,'','','',0,'')") 
    else:
      response.cmd_barcode_update = ""
      response.cmd_barcode_delete = ""
      if session.mobile:
        response.cmd_barcode_new = ""
      else:
        response.cmd_barcode_new = SPAN(" ",SPAN(str(barcode_count), _class="detail_count"))
    
    fields=[ns.db.barcode.id,ns.db.barcode.product_id,ns.db.barcode.defcode,ns.db.barcode.code,ns.db.barcode.barcodetype,
            ns.db.barcode.qty,ns.db.barcode.description]
    response.view_barcode = ui.select.get_tab_grid(_query=barcode, _field_id=ns.db.barcode.id, _fields=fields, _deletable=False, 
                                         _editable=False ,links=links, multi_page="barcode_page", 
                                         rpl_1="/frm_product", rpl_2="/frm_product/view/product/"+str(product_id),_priority="0,2,5")
    
    response.barcode_form = SQLFORM(ns.db.barcode, submit_button=T("Save"),_id="frm_barcode")
    response.barcode_form.process()
    if not session.mobile:
      response.barcode_icon = URL(ui.dir_images,'icon16_barcode.png')
      response.cmd_barcode_cancel = A(SPAN(_class="icon cross"), _id="cmd_barcode_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_barcode').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.barcode_id = INPUT(_name="id", _type="hidden", _value="", _id="barcode_id")
    response.barcode_product_id = INPUT(_name="product_id", _type="hidden", _value=product_id, _id="barcode_ref_id")    
  else:
    response.menu_barcode = ""
    
  #event data
  event_audit_filter = ui.connect.get_audit_filter("event", None)[0]
  if event_audit_filter!="disabled" and product_id>-1:
    event = ((ns.db.event.ref_id==product_id)&(ns.db.event.nervatype==nervatype_product)&(ns.db.event.deleted==0))
    event_count = ns.db(event).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    ns.db.event.id.readable = ns.db.event.id.writable = False
    ns.db.event.nervatype.readable = ns.db.event.ref_id.readable = ns.db.event.uid.readable = False
    if session.mobile:
      links = None
      editable = False
      response.menu_event = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Poduct Events"),event_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('event_page');",
        theme="a", rel="close")
      ns.db.event.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL('frm_product/edit/event/')+str(row["id"]), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    else:
      editable = True
      links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("cmd_export_ical?id="+str(row.id)), _target="_blank", _title=T("Export Item"))]
    
    if (product_audit_filter in ("readonly","disabled")) or (event_audit_filter in ("readonly","disabled")):
      gdeleted = False
      if session.mobile:
        response.cmd_event_new = ""
      else:
        response.cmd_event_new = SPAN(" ",SPAN(str(event_count), _class="detail_count"))
    else:
      if session.mobile:
        gdeleted = False
        response.cmd_event_new = ui.control.get_mobil_button(cmd_id="cmd_event_new",
          label=T("New Event"), href=URL("frm_event/new/event")+"?refnumber="+form.formname, 
          cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
      else:
        gdeleted = True
        response.cmd_event_new = ui.control.get_tabnew_button(event_count,T('New Event'),cmd_id="tabs-event",url=URL("frm_event/new/event"+"?refnumber="+form.formname))

    response.view_event = ui.select.get_tab_grid(_query=event, _field_id=ns.db.event.id, _fields=None, _deletable=gdeleted, links=links, _editable=editable,
                             multi_page="event_page", rpl_1="/frm_product", rpl_2="/frm_product/view/product/"+str(product_id),_priority="0,4")  
  else:
    response.view_event = ""
    response.event_disabled=True
    response.menu_event = ""
        
  return dict(form=form)

@ns_auth.requires_login()
def frm_project():
  audit_filter = ui.connect.get_audit_filter("project", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    project_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["project_page_"+str(project_id)] = "fieldvalue_page"
    redirect(URL('frm_project/view/project/'+str(project_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    project_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["project_page_"+str(project_id)] = "fieldvalue_page"
    if ns.connect.deleteData("fieldvalue", ref_id=fieldvalue_id):
      redirect(URL('frm_project/view/project/'+str(project_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    ui.connect.clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    row_id = ns.connect.updateData("fieldvalue", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["project_page_"+str(request.post_vars["ref_id"])] = "fieldvalue_page"
      redirect()
   
  if ruri.find("edit/address")>0 or ruri.find("view/address")>0:
    address_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    project_id = ns.db.address(id=address_id).ref_id
    session["project_page_"+str(project_id)] = "address_page"
    redirect(URL('frm_project/view/project/'+str(project_id)))
    
  if ruri.find("delete/address")>0:
    address_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    project_id = ns.db.address(id=address_id).ref_id
    session["project_page_"+str(project_id)] = "address_page"
    if ns.connect.deleteData("address", ref_id=address_id):
      redirect(URL('frm_project/view/project/'+str(project_id)))
        
  if request.post_vars["_formname"]=="address/create":
    ui.connect.clear_post_vars()
    row_id = ns.connect.updateData("address", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["project_page_"+str(request.post_vars["ref_id"])] = "address_page"
      redirect()
  
  if ruri.find("edit/contact")>0 or ruri.find("view/contact")>0:
    contact_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    project_id = ns.db.contact(id=contact_id).ref_id
    session["project_page_"+str(project_id)] = "contact_page"
    redirect(URL('frm_project/view/project/'+str(project_id)))
    
  if ruri.find("delete/contact")>0:
    contact_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    project_id = ns.db.contact(id=contact_id).ref_id
    session["project_page_"+str(project_id)] = "contact_page"
    if ns.connect.deleteData("contact", ref_id=contact_id):
      redirect(URL('frm_project/view/project/'+str(project_id)))
        
  if request.post_vars["_formname"]=="contact/create":
    ui.connect.clear_post_vars()
    row_id = ns.connect.updateData("contact", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["project_page_"+str(request.post_vars["ref_id"])] = "contact_page"
      redirect()
  
  if ruri.find("event")>0:
    ruri = "frm_event/view"+ruri[ruri.find("frm_project/edit")+16:]
    redirect(URL(ruri))
  
  if ruri.find("trans")>0:
    ruri = "frm_trans/view"+ruri[ruri.find("frm_project/edit")+16:]
    redirect(URL(ruri))
    
  if ruri.find("new/project")>0:
    project_id = -1
  else:
    project_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ns.db.project(id=project_id).deleted==1:
      return ui.connect.show_disabled(response.title)
      
  if ruri.find("delete/project")>0:
    if not ns.connect.deleteData("project", ref_id=project_id):
      session.flash = str(ns.error_message)
      redirect(URL('frm_project/view/project/'+str(project_id)))
    else:
      redirect(URL('find_project_project'))  
  
  response.view=ui.dir_view+'/project.html'
  response.pronumber = ""
  if not session.mobile:
    response.titleicon = URL(ui.dir_images,'icon16_date_edit.png')
    response.icon_deffield = IMG(_src=URL(ui.dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_address = IMG(_src=URL(ui.dir_images,'icon16_address.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_contact = IMG(_src=URL(ui.dir_images,'icon16_contact.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_calendar = IMG(_src=URL(ui.dir_images,'icon16_calendar.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_calculator = IMG(_src=URL(ui.dir_images,'icon16_calculator.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.lo_menu = []
  
  nervatype_project = ns.valid.get_groups_id("nervatype", "project")
  project_audit_filter = ui.connect.get_audit_filter("project", None)[0]
  ns.db.project.id.readable = ns.db.project.id.writable = False
  ns.db.project.deleted.readable = ns.db.project.deleted.writable = False
  if project_id>0:    
    response.subtitle=T('PROJECT')
    response.pronumber=ns.db.project(id=project_id).pronumber
    form = SQLFORM(ns.db.project, record = project_id, submit_button=T("Save"), _id="frm_project")
    if project_audit_filter!="disabled":
      response.cmd_report = ui.control.get_report_button(nervatype="project", title=T('Project Reports'), ref_id=project_id,
                                              label=response.pronumber)
    else:
      response.cmd_report = ""
    if project_audit_filter=="all":
      if session.mobile:
        response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
                                            onclick="if(confirm('"+T('Are you sure you want to delete this project?')+
                                            "')){window.location ='"+URL("frm_project/delete/project/"+str(project_id))+"';};return false;", theme="b")
      else:
        response.cmd_delete = ui.control.get_command_button(_id="cmd_delete", caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this project?')+
                              "')){window.location ='"+URL("frm_project/delete/project/"+str(project_id))+"';};return false;")
    else:
      response.cmd_delete = ""
  else:
    form = SQLFORM(ns.db.project, submit_button=T("Save"), _id="frm_project")
    form.vars.pronumber = ns.connect.nextNumber("pronumber",False)
    response.subtitle=T('New Project')
    response.pronumber = ""
    response.cmd_report = ""
    response.cmd_delete = ""
  
  if session.mobile:
    if project_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
                                             icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
    else:
      response.cmd_back = ui.control.get_mobil_button(label=T("SEARCH"), href=URL("frm_quick_project"), icon="search", cformat="ui-btn-left", ajax="false") 
  
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=project'),
                                           cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:
    if project_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_home_button()
    else:
      response.cmd_back = ui.control.get_back_button(URL("find_project_project"))
    response.cmd_help = ui.control.get_help_button("project")
  
  if project_audit_filter in ("readonly","disabled"):
    form.custom.submit = "" 
  elif session.mobile:
    form.custom.submit = ui.control.get_mobil_button(label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_project'].submit();")
            
  if form.validate(keepvalues=True):
    if request.post_vars.customer_id!="":
      form.vars.customer_id=request.post_vars.customer_id
    else:
      form.vars.customer_id=""      
    if project_id==-1:
      nextnumber = ns.connect.nextNumber("pronumber",False)
      if form.vars.pronumber == nextnumber:
        form.vars.pronumber = ns.connect.nextNumber("pronumber")
    else:
      form.vars.id = project_id      
    row_id = ns.connect.updateData("project", values=form.vars, validate=False, insert_row=True)  
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      redirect(URL('frm_project/view/project/'+str(row_id)))
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      if str(ns.db.project.fields).find(error)>0:
        flash+=ns.db.project[error].label+": "+form.errors[error]+", "
      else:
        flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  form.custom.widget.inactive = ui.control.get_bool_input(project_id,"project","inactive")
  
  customer_id=""
  customer_name=""
  if project_id>-1:  
    if ns.db.project(id=project_id).customer_id!=None:
      customer_id = ns.db.project(id=project_id).customer_id
      customer_name = ns.db.customer(id=ns.db.project(id=project_id).customer_id).custname
  response.customer_id = INPUT(_name="customer_id", _type="hidden", _value=customer_id, _id="customer_id")
  if response.customer_control==None:
    response.customer_control = ui.select.get_customer_selector(customer_name)
  
  if session.mobile:
    if session["project_page_"+str(project_id)]:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value=session["project_page_"+str(project_id)])
      session["project_page_"+str(project_id)]="project_page"
    else:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value="project_page")
    response.menu_project = ui.control.get_mobil_button(T("Project Data"), href="#", 
        cformat=None, icon="edit", style="text-align: left;",
        onclick= "show_page('project_page');", theme="a", rel="close")

  #additional fields data
  if project_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_project)&(ns.db.fieldvalue.ref_id==project_id))
    editable = not (project_audit_filter in ("readonly","disabled"))
    ui.select.set_view_fields("project", nervatype_project, 0, editable, fieldvalue, project_id, "/frm_project", "/frm_project/view/project/"+str(project_id))
  else:
    response.menu_fields = ""
     
  #address data
  if project_id>-1:
    address = ((ns.db.address.ref_id==project_id)&(ns.db.address.nervatype==nervatype_project)&(ns.db.address.deleted==0))
    address_count = ns.db(address).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if session.mobile:
      links = None
      response.menu_address = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Address Data"),address_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('address_page');",
        theme="a", rel="close")
      ns.db.address.id.label = T("*")
      ns.db.address.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, icon="edit", style="text-align: left;",
                            onclick="set_address("
                             +str(row["id"])+",'"
                             +json.dumps(str(row["country"]))[1:-1]+"','"
                             +json.dumps(str(row["state"]))[1:-1]+"','"
                             +json.dumps(str(row["zipcode"]))[1:-1]+"','"
                             +json.dumps(str(row["city"]))[1:-1]+"','"
                             +json.dumps(str(row["street"]))[1:-1]+"','"
                             +json.dumps(str(row["notes"]))[1:-1]+"')", theme="d")
    else:
      links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_address("
                           +str(row["id"])+",'"
                           +json.dumps(str(row["country"]))[1:-1]+"','"
                           +json.dumps(str(row["state"]))[1:-1]+"','"
                           +json.dumps(str(row["zipcode"]))[1:-1]+"','"
                           +json.dumps(str(row["city"]))[1:-1]+"','"
                           +json.dumps(str(row["street"]))[1:-1]+"','"
                           +json.dumps(str(row["notes"]))[1:-1]+"')",
                           _title=T("Edit Address"))]
      ns.db.address.id.label = T("No.")
      ns.db.address.id.represent = lambda value,row: ui.control.format_value("integer",row["id"])
    ns.db.address.nervatype.readable = ns.db.address.ref_id.readable = ns.db.address.deleted.readable = False
    ns.db.address.street.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
    
    if project_audit_filter in ("readonly","disabled"):
      if session.mobile:
        response.cmd_address_new = ""
      else:
        response.cmd_address_new = SPAN(" ",SPAN(str(address_count), _class="detail_count"))
      response.cmd_address_update = ""
      response.cmd_address_delete = ""
    else:
      if session.mobile:
        response.cmd_address_update = ui.control.get_mobil_button(label=T("Save Address"), href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
          onclick= "document.forms['frm_address'].submit();")
        response.cmd_address_delete = ui.control.get_mobil_button(label=T("Delete Address"), href="#", 
          cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to delete this data?')+
                              "')){if(document.getElementById('address_id').value>-1){window.location = '"
            +URL("frm_project")+"/delete/address/'+document.getElementById('address_id').value;} else {show_page('address_page');}}")
        response.cmd_address_new = ui.control.get_mobil_button(cmd_id="cmd_address_new",
          label=T("New Address"), href="#", 
          cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
          onclick= "set_address(-1,'','','','','','');", rel="close")
        response.cmd_address_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
          icon="back", ajax="true", theme="a",  
          onclick= "show_page('address_page');", rel="close")
      else:
        links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this address?')+
                                "')){window.location ='"+URL("frm_project/delete/address/"+str(row.id))+"';};return false;", 
                           _title=T("Delete Address")))
        response.cmd_address_update = ui.control.get_command_button(caption=T("Save"),title=T("Update address data"),color="008B00", _id="cmd_address_submit",
                                cmd="address_update();return true;")
        response.cmd_address_new = ui.control.get_tabnew_button(address_count,T('New Address'),cmd_id="cmd_address_new",
                                  cmd = "$('#tabs').tabs({ active: 1 });set_address(-1,'','','','','','')")
  
    response.view_address = ui.select.get_tab_grid(_query=address, _field_id=ns.db.address.id, _fields=None, _deletable=False, _editable=False, links=links, 
                               multi_page="address_page", rpl_1="/frm_project", rpl_2="/frm_project/view/project/"+str(project_id),_priority="0,4,5")
    
    response.address_form = SQLFORM(ns.db.address, submit_button=T("Save"),_id="frm_address")
    response.address_form.process()
    if not session.mobile:
      response.address_icon = URL(ui.dir_images,'icon16_address.png')
      response.cmd_address_cancel = A(SPAN(_class="icon cross"), _id="cmd_address_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_address').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.address_id = INPUT(_name="id", _type="hidden", _value="", _id="address_id")
    response.address_ref_id = INPUT(_name="ref_id", _type="hidden", _value=project_id, _id="address_ref_id")
    response.address_nervatype = INPUT(_name="nervatype", _type="hidden", _value=nervatype_project, _id="address_nervatype")
  else:
    response.menu_address = ""
    
  #contact data
  if project_id>-1:
    contact = ((ns.db.contact.ref_id==project_id)&(ns.db.contact.nervatype==nervatype_project)&(ns.db.contact.deleted==0))
    contact_count = ns.db(contact).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if session.mobile:
      links = None
      response.menu_contact = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Contact Info"),contact_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('contact_page');",
        theme="a", rel="close")
      ns.db.contact.id.label = T("*")
      ns.db.contact.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, icon="edit", style="text-align: left;",
                            onclick="set_contact("
                             +str(row["id"])+",'"
                             +json.dumps(str(row["firstname"]))[1:-1]+"','"
                             +json.dumps(str(row["surname"]))[1:-1]+"','"
                             +json.dumps(str(row["status"]))[1:-1]+"','"
                             +json.dumps(str(row["phone"]))[1:-1]+"','"
                             +json.dumps(str(row["fax"]))[1:-1]+"','"
                             +json.dumps(str(row["mobil"]))[1:-1]+"','"
                             +json.dumps(str(row["email"]))[1:-1]+"','"
                             +json.dumps(str(row["notes"]))[1:-1]+"')")
    else:
      ns.db.contact.id.label = T("No.")
      ns.db.contact.id.represent = lambda value,row: ui.control.format_value("integer",row["id"])
      links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                             _class="w2p_trap buttontext button", _href="#", _onclick="set_contact("
                             +str(row["id"])+",'"
                             +json.dumps(str(row["firstname"]))[1:-1]+"','"
                             +json.dumps(str(row["surname"]))[1:-1]+"','"
                             +json.dumps(str(row["status"]))[1:-1]+"','"
                             +json.dumps(str(row["phone"]))[1:-1]+"','"
                             +json.dumps(str(row["fax"]))[1:-1]+"','"
                             +json.dumps(str(row["mobil"]))[1:-1]+"','"
                             +json.dumps(str(row["email"]))[1:-1]+"','"
                             +json.dumps(str(row["notes"]))[1:-1]+"')",
                             _title=T("Edit Contact"))]
    ns.db.contact.nervatype.readable = ns.db.contact.ref_id.readable = ns.db.contact.deleted.readable = False
    
    if project_audit_filter in ("readonly","disabled"):
      if session.mobile:
        response.cmd_contact_new = ""
      else:
        response.cmd_contact_new = SPAN(" ",SPAN(str(contact_count), _class="detail_count"))
      response.cmd_contact_update = ""
      response.cmd_contact_delete = ""
    else:
      if session.mobile:
        response.cmd_contact_new = ui.control.get_mobil_button(cmd_id="cmd_contact_new",
          label=T("New Contact"), href="#", 
          cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
          onclick= "set_contact(-1,'','','','','','','','');", rel="close")
        response.cmd_contact_update = ui.control.get_mobil_button(label=T("Save Contact"), href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
          onclick= "document.forms['frm_contact'].submit();")
        response.cmd_contact_delete = ui.control.get_mobil_button(label=T("Delete Contact"), href="#", 
          cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to delete this data?')+
                              "')){if(document.getElementById('contact_id').value>-1){window.location = '"
            +URL("frm_project")+"/delete/contact/'+document.getElementById('contact_id').value;} else {show_page('contact_page');}}")
        response.cmd_contact_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
          icon="back", ajax="true", theme="a",  
          onclick= "show_page('contact_page');", rel="close")
      else:
        links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this contact?')+
                                "')){window.location ='"+URL("frm_project/delete/contact/"+str(row.id))+"';};return false;", 
                           _title=T("Delete Contact")))
        response.cmd_contact_update = ui.control.get_command_button(caption=T("Save"),title=T("Update contact data"),color="008B00", _id="cmd_contact_submit",
                                cmd="contact_update();return true;")
        response.cmd_contact_new = ui.control.get_tabnew_button(contact_count,T('New Contact'),cmd_id="cmd_contact_new",
                                  cmd = "$('#tabs').tabs({ active: 2 });set_contact(-1,'','','','','','','','')")
  
    response.view_contact = ui.select.get_tab_grid(_query=contact, _field_id=ns.db.contact.id, _fields=None, _deletable=False, _editable=False, links=links, 
                               multi_page="contact_page", rpl_1="/frm_project", rpl_2="/frm_project/view/project/"+str(project_id),_priority="0,1,2")
    
    response.contact_form = SQLFORM(ns.db.contact, submit_button=T("Save"),_id="frm_contact")
    response.contact_form.process()
    if not session.mobile:
      response.contact_icon = URL(ui.dir_images,'icon16_contact.png')
      response.cmd_contact_cancel = A(SPAN(_class="icon cross"), _id="cmd_contact_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_contact').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.contact_id = INPUT(_name="id", _type="hidden", _value="", _id="contact_id")
    response.contact_ref_id = INPUT(_name="ref_id", _type="hidden", _value=project_id, _id="contact_ref_id")
    response.contact_nervatype = INPUT(_name="nervatype", _type="hidden", _value=nervatype_project, _id="contact_nervatype")  
  else:
    response.menu_contact = ""
    
  #event data  
  event_audit_filter = ui.connect.get_audit_filter("event", None)[0]
  if event_audit_filter!="disabled" and project_id>-1:
    event = ((ns.db.event.ref_id==project_id)&(ns.db.event.nervatype==nervatype_project)&(ns.db.event.deleted==0))
    event_count = ns.db(event).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    ns.db.event.id.readable = ns.db.event.id.writable = False
    ns.db.event.nervatype.readable = ns.db.event.ref_id.readable = ns.db.event.uid.readable = False
    if session.mobile:
      links = None
      editable = False
      response.menu_event = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Project Events"),event_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('event_page');",
        theme="a", rel="close")
      ns.db.event.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL('frm_project/edit/event/')+str(row["id"]), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    else:
      editable = True
      links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("cmd_export_ical?id="+str(row.id)), _target="_blank", _title=T("Export Item"))]
  
    if (project_audit_filter in ("readonly","disabled")) or (event_audit_filter in ("readonly","disabled")):
      gdeleted = False
      if session.mobile:
        response.cmd_event_new = ""
      else:
        response.cmd_event_new = SPAN(" ",SPAN(str(event_count), _class="detail_count"))
    else:
      if session.mobile:
        gdeleted = False
        response.cmd_event_new = ui.control.get_mobil_button(cmd_id="cmd_event_new",
          label=T("New Event"), href=URL("frm_event/new/event")+"?refnumber="+form.formname, 
          cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
      else:
        gdeleted = True
        response.cmd_event_new = ui.control.get_tabnew_button(event_count,T('New Event'),cmd_id="tabs-events",url=URL("frm_event/new/event")+"?refnumber="+form.formname)
    
    response.view_event = ui.select.get_tab_grid(_query=event, _field_id=ns.db.event.id, _fields=None, _deletable=gdeleted, links=links, _editable=editable,
                             multi_page="event_page", rpl_1="/frm_project", rpl_2="/frm_project/view/project/"+str(project_id),_priority="0,4")  
  else:
    response.view_event = ""
    response.event_disabled=True
    response.menu_event = ""
  
  #trans data
  if project_id>-1:
    ns.db.trans.id.represent = lambda value,row: A(SPAN(ns.db.trans(id=int(value))["transnumber"]),
                       _href=URL(r=request, f="frm_trans/view/trans/"+str(value)), _target="_blank")
    ns.db.trans.id.label=T('Document No.')
    ns.db.trans.transtype.label=T('Type')
    ns.db.trans.transdate.label=T('Date')
    trans = ((ns.db.trans.project_id==project_id)&(ns.db.trans.deleted==0))
    fields = [ns.db.trans.id, ns.db.trans.transtype,ns.db.trans.direction,
              ns.db.trans.transdate,ns.db.trans.curr,ns.db.trans.customer_id]
    
    trans_count = ns.db(trans).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if session.mobile:
      editable = False
      response.menu_trans = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Documents"),trans_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('trans_page');", theme="a", rel="close")
    else:
      editable = True
      response.cmd_trans_new = SPAN(" ",SPAN(str(trans_count), _class="detail_count"))
    response.view_trans = ui.select.get_tab_grid(_query=trans, _field_id=ns.db.trans.id, _fields=fields, _deletable=False, links=None, _editable=editable,
                               multi_page="trans_page", rpl_1="/frm_project", rpl_2="/frm_project/view/project/"+str(project_id)) 
  else:
    response.view_trans = ""
    response.menu_trans = ""
        
  return dict(form=form)

@ns_auth.requires_login()
def frm_quick_customer():
  if session.mobile:
    fields = [ns.db.customer.id, ns.db.customer.custname, ns.db.customer.custtype, ns.db.customer.inactive]
    ns.db.customer.id.label = T('Customer No.')
    ns.db.customer.id.represent = lambda value,row: ui.control.get_mobil_button(SPAN(ns.db.customer(id=int(value))["custnumber"]), 
                                href=URL(r=request, f="frm_customer/view/customer/"+str(value)), 
                                cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
  else:
    ruri = request.wsgi.environ["REQUEST_URI"]
    if ruri.find("view")>0 or ruri.find("edit")>0:
      ruri = str(ruri).replace("frm_quick_customer", "frm_customer")
      redirect(ruri)
    response.margin_top = "20px"
    fields = [ns.db.customer.custnumber, ns.db.customer.custname, ns.db.customer.custtype, ns.db.customer.inactive]
    response.cmd_back = ui.control.get_home_button()
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
      
  response.view=ui.dir_view+'/quick.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select customer')
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.custtype!=ns.valid.get_groups_id("custtype", "own"))&(ns.db.customer.custtype==ns.db.groups.id))
  left = None
    
  ns.db.groups.groupvalue.label = T("Type")
  
  form = DIV(ui.select.create_search_form(URL("frm_quick_customer")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
  gform = ui.select.find_data(table="customer",query=query,fields=fields,orderby=ns.db.customer.custname,
                    paginate=20,maxtextlength=25,left=left,sortable=True,page_url=None,priority="0,1")
  
  return dict(form=form, gform=DIV(gform, _id="dlg_frm"))

@ns_auth.requires_login()
def frm_quick_employee():
  if session.mobile:
    fields = [ns.db.employee.id, ns.db.contact.firstname, ns.db.contact.surname, ns.db.employee.username, 
              ns.db.employee.usergroup, ns.db.employee.inactive]
    ns.db.employee.id.label = T('Employee No.')
    ns.db.employee.id.represent = lambda value,row: ui.control.get_mobil_button(SPAN(ns.db.employee(id=int(value))["empnumber"]), 
                                  href=URL(r=request, f="frm_employee/view/employee/"+str(value)), 
                                  cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
  else:
    ruri = request.wsgi.environ["REQUEST_URI"]
    if ruri.find("view")>0 or ruri.find("edit")>0:
      ruri = str(ruri).replace("frm_quick_employee", "frm_employee")
      redirect(ruri)
    response.margin_top = "20px"
    response.cmd_back = ui.control.get_home_button()
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
    fields = [ns.db.employee.empnumber, ns.db.contact.firstname, ns.db.contact.surname, ns.db.employee.username, 
            ns.db.employee.usergroup, ns.db.employee.inactive]
      
  response.view=ui.dir_view+'/quick.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select employee')
  
  nervatype_employee = ns.valid.get_groups_id("nervatype", "employee")
  query = ((ns.db.employee.deleted==0)&(ns.db.employee.usergroup==ns.db.groups.id)&
           (ns.db.employee.id==ns.db.contact.ref_id)&(ns.db.contact.nervatype==nervatype_employee)&(ns.db.contact.deleted==0))
  left = None
  
  form = DIV(ui.select.create_search_form(URL("frm_quick_employee")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
  gform = ui.select.find_data(table="employee",query=query,fields=fields,orderby=ns.db.employee.id,
                      paginate=20,maxtextlength=25,left=left,sortable=True,page_url=None,priority="0,2,3")
  
  return dict(form=form, gform=DIV(gform, _id="dlg_frm"))

@ns_auth.requires_login()
def frm_quick_menucmd():
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("new")>0:
    redirect(URL('frm_menucmd/new/ui_menu'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = str(ruri).replace("frm_quick_menucmd/edit", "frm_menucmd/view")
    redirect(ruri)
  if str(ruri).find("delete/ui_menu")>0:
    menu_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    menufields = ns.db(ns.db.ui_menufields.menu_id==menu_id).select(ns.db.ui_menufields.id)
    for menufields_id in menufields:
      ns.connect.deleteData("ui_menufields", ref_id=menufields_id)
    ns.connect.deleteData("ui_menu", ref_id=menu_id)
    redirect(URL('frm_quick_menucmd'))
  response.view=ui.dir_view+'/quick.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Menu Shortcuts')
  if session.mobile:
    ns.db.ui_menu.menukey.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_menucmd/view/ui_menu/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    deletable = False
  else:
    response.cmd_back = ui.control.get_home_button()
    response.titleicon = URL(ui.dir_images,'icon16_world_link.png')
    response.margin_top = "20px"
    deletable = (audit_filter=="all")
  if audit_filter=="all":
    if session.mobile:
      response.cmd_add_new = ui.control.get_mobil_button(
          label=T("New Shortcut"), href=URL('frm_quick_menucmd/new/ui_menu'), 
          cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
    else:
      response.cmd_add_new = ui.control.get_new_button(URL('frm_quick_menucmd/new/ui_menu'))
  else:
    response.cmd_add_new = ""    
  ns.db.ui_menu.id.readable = ns.db.ui_menu.id.writable = False
  
  fields = [ns.db.ui_menu.menukey, ns.db.ui_menu.description, ns.db.ui_menu.modul, ns.db.ui_menu.icon,
            ns.db.ui_menu.funcname, ns.db.ui_menu.url, ns.db.ui_menu.address]
  
  form = DIV(ui.select.create_search_form(URL("frm_quick_menucmd")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
  gform = ui.select.find_data(table="ui_menu",query=ns.db.ui_menu,fields=fields,orderby=ns.db.ui_menu.id,
                      paginate=10,maxtextlength=20,left=None,sortable=True,page_url=None,deletable=deletable,fullrow=True)
  
  return dict(form=form, gform=DIV(gform, _id="dlg_frm"))

@ns_auth.requires_login()
def frm_quick_movement():
  if session.mobile: 
    fields = [ns.db.trans.id, ns.db.trans.transtype, ns.db.trans.direction, ns.db.trans.transdate]
    ns.db.trans.id.label = T('Document No.')
    ns.db.trans.id.represent = lambda value,row: ui.control.get_mobil_button(SPAN(ns.db.trans(id=int(value))["transnumber"]), 
                                  href=URL(r=request, f="frm_trans/view/trans/"+str(value)), 
                                  cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
  else:
    ruri = request.wsgi.environ["REQUEST_URI"]
    if ruri.find("view")>0 or ruri.find("edit")>0:
      ruri = str(ruri).replace("frm_quick_movement", "frm_trans")
      redirect(ruri)
    response.margin_top = "20px"
    response.cmd_back = ui.control.get_home_button()
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
    fields = [ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, ns.db.trans.transdate]
    
  response.view=ui.dir_view+'/quick.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select document')
    
  query = ((ns.db.trans.deleted==0) & (ns.db.trans.transtype==ns.db.groups.id) & ns.db.groups.groupvalue.belongs("delivery","inventory","waybill","production","formula")) 
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = ui.select.set_transfilter(query)
  
  ns.db.groups.groupvalue.label = T("Doc.Type")
  ns.db.trans.transdate.label = T("Shipping Date")
  
  form = DIV(ui.select.create_search_form(URL("frm_quick_movement")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
  gform = ui.select.find_data(table="trans",query=query,fields=fields,orderby=ns.db.trans.id,
                      paginate=20,maxtextlength=25,left=None,sortable=True,page_url=None,priority="0,4,5")
    
  return dict(form=form, gform=DIV(gform, _id="dlg_frm"))

@ns_auth.requires_login()
def frm_quick_payment():
  if session.mobile:     
    fields = [ns.db.trans.id, ns.db.trans.transtype, ns.db.trans.place_id, ns.db.payment.paiddate, 
              ns.db.place.curr, ns.db.payment.amount] 
    ns.db.trans.id.label = T('Document No.')
    ns.db.trans.id.represent = lambda value,row: ui.control.get_mobil_button(SPAN(ns.db.trans(id=int(value))["transnumber"]), 
                                  href=URL(r=request, f="frm_trans/view/trans/"+str(value)), 
                                  cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
  else:
    ruri = request.wsgi.environ["REQUEST_URI"]
    if ruri.find("view")>0 or ruri.find("edit")>0:
      ruri = str(ruri).replace("frm_quick_payment", "frm_trans")
      redirect(ruri)
    response.margin_top = "20px"
    response.cmd_back = ui.control.get_home_button()
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
    fields = [ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.place_id, ns.db.payment.paiddate, 
            ns.db.place.curr, ns.db.payment.amount] 
    
  response.view=ui.dir_view+'/quick.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select document')
  
  transtype_cash_id = ns.valid.get_groups_id("transtype", "cash")
  query = (((ns.db.trans.deleted==0)|(ns.db.trans.transtype==transtype_cash_id))
           &(ns.db.trans.id==ns.db.payment.trans_id)&(ns.db.payment.deleted==0)
           &(ns.db.trans.place_id==ns.db.place.id)&(ns.db.trans.transtype==ns.db.groups.id))
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
    
  #set transfilter
  query = ui.select.set_transfilter(query)
  
  ns.db.groups.groupvalue.label = T("Doc.Type")
  ns.db.trans.place_id.label = T("Bank/Ch.")
  form = DIV(ui.select.create_search_form(URL("frm_quick_payment")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
  gform = ui.select.find_data(table="trans",query=query,fields=fields,orderby=ns.db.trans.id,
                    paginate=20,maxtextlength=25,left=None,sortable=True,page_url=None,priority="0,4,5")
  return dict(form=form, gform=DIV(gform, _id="dlg_frm"))

@ns_auth.requires_login()
def frm_quick_place():
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("new")>0:
    redirect(URL('frm_place/new/place'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = str(ruri).replace("frm_quick_place/edit", "frm_place/view")
    redirect(ruri)
  if str(ruri).find("delete/place")>0:
    redirect(URL('frm_quick_place'))
  response.view=ui.dir_view+'/quick.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Place')
  if session.mobile:
    ns.db.place.planumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_place/view/place/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
  else:
    response.margin_top = "20px"
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
      response.cmd_back = ui.control.get_back_button(session.back_url)
    else:
      response.cmd_back = ui.control.get_home_button()
    response.titleicon = URL(ui.dir_images,'icon16_book.png')
  
  if audit_filter=="all":
    if session.mobile:
      response.cmd_add_new = ui.control.get_mobil_button(
        label=T("New Place"), href=URL('frm_quick_place/new/place'), 
        cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
    else:
      response.cmd_add_new = ui.control.get_new_button(URL('frm_quick_place/new/place'))
  else:
    response.cmd_add_new = ""
    
  query=((ns.db.place.deleted==0)&(ns.db.place.placetype==ns.db.groups.id))
  fields = [ns.db.place.planumber, ns.db.place.placetype, ns.db.place.description, ns.db.place.inactive]
  ns.db.groups.groupvalue.label = T("Type")
  
  form = DIV(ui.select.create_search_form(URL("frm_quick_place")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
  gform = ui.select.find_data(table="place",query=query,fields=fields,orderby=ns.db.place.id,
                      paginate=20,maxtextlength=25,left=None,sortable=True,page_url=None,
                      priority="0,1",fullrow=True)
    
  return dict(form=form, gform=DIV(gform, _id="dlg_frm"))

@ns_auth.requires_login()
def frm_quick_product():
  if session.mobile:
    fields = [ns.db.product.id, ns.db.product.protype, ns.db.product.description, ns.db.product.unit, ns.db.product.inactive]
    ns.db.product.id.label = T('Product No.')
    ns.db.product.id.represent = lambda value,row: ui.control.get_mobil_button(SPAN(ns.db.product(id=int(value))["partnumber"]), 
                                  href=URL(r=request, f="frm_product/view/product/"+str(value)), 
                                  cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
  else:
    ruri = request.wsgi.environ["REQUEST_URI"]
    if ruri.find("view")>0 or ruri.find("edit")>0:
      ruri = str(ruri).replace("frm_quick_product", "frm_product")
      redirect(ruri)
    response.margin_top = "20px"
    response.cmd_back = ui.control.get_home_button()
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
    fields = [ns.db.product.partnumber, ns.db.product.protype, ns.db.product.description, ns.db.product.unit, ns.db.product.inactive]
      
  response.view=ui.dir_view+'/quick.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select product')
  
  query = ((ns.db.product.deleted==0)&(ns.db.product.protype==ns.db.groups.id))
  left = None
  ns.db.groups.groupvalue.label = T("Type")
  
  form = DIV(ui.select.create_search_form(URL("frm_quick_product")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
  gform = ui.select.find_data(table="product",query=query,fields=fields,orderby=ns.db.product.id,
                    paginate=20,maxtextlength=25,left=left,sortable=True,page_url=None,priority="0,1,2")

  return dict(form=form, gform=DIV(gform, _id="dlg_frm"))

@ns_auth.requires_login()
def frm_quick_project():
  if session.mobile:
    fields = [ns.db.project.id, ns.db.project.description, ns.db.project.startdate, ns.db.project.customer_id]
    ns.db.project.id.label = T('Project No.')
    ns.db.project.id.represent = lambda value,row: ui.control.get_mobil_button(SPAN(ns.db.project(id=int(value))["pronumber"]), 
                                  href=URL(r=request, f="frm_project/view/project/"+str(value)), 
                                  cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
  else:
    ruri = request.wsgi.environ["REQUEST_URI"]
    if ruri.find("view")>0 or ruri.find("edit")>0:
      ruri = str(ruri).replace("frm_quick_project", "frm_project")
      redirect(ruri)
    response.margin_top = "20px"
    response.cmd_back = ui.control.get_home_button()
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
    fields = [ns.db.project.pronumber, ns.db.project.description, ns.db.project.startdate, ns.db.project.enddate, ns.db.project.customer_id]
    
  response.view=ui.dir_view+'/quick.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select project')
  
  query = ((ns.db.project.deleted==0))
  left = (ns.db.customer.on(ns.db.project.customer_id==ns.db.customer.id))
  ns.db.project.startdate.represent = lambda value,row: ui.control.format_value("date",row["startdate"])
  ns.db.project.enddate.represent = lambda value,row: ui.control.format_value("date",row["enddate"])
  
  form = DIV(ui.select.create_search_form(URL("frm_quick_project")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
  gform = ui.select.find_data(table="project",query=query,fields=fields,orderby=ns.db.project.id,
                      paginate=20,maxtextlength=25,left=left,sortable=True,page_url=None,priority="0,1")
  return dict(form=form, gform=DIV(gform, _id="dlg_frm"))

@ns_auth.requires_login()
def frm_quick_tool():
  if session.mobile:
    fields = [ns.db.tool.id, ns.db.tool.description, ns.db.tool.product_id, ns.db.tool.inactive]
    ns.db.tool.id.label = T('Serial No.')
    ns.db.tool.id.represent = lambda value,row: ui.control.get_mobil_button(SPAN(ns.db.tool(id=int(value))["serial"]), 
                                  href=URL(r=request, f="frm_tool/view/tool/"+str(value)), 
                                  cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
  else:
    ruri = request.wsgi.environ["REQUEST_URI"]
    if ruri.find("view")>0 or ruri.find("edit")>0:
      ruri = str(ruri).replace("frm_quick_tool", "frm_tool")
      redirect(ruri)
    response.margin_top = "20px"
    response.cmd_back = ui.control.get_home_button()
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
    fields = [ns.db.tool.serial, ns.db.tool.description, ns.db.tool.product_id, ns.db.tool.inactive]
    
  response.view=ui.dir_view+'/quick.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select tool')
  
  if ns.connect.getSetting("printer_in_tool")!="true":
    printer_groups_id = ns.db((ns.db.groups.groupname=="toolgroup")&(ns.db.groups.groupvalue=='printer')).select(ns.db.groups.id)
    query = ((ns.db.tool.deleted==0)&(ns.db.product.id==ns.db.tool.product_id)&(ns.db.product.deleted==0)
             &(~ns.db.tool.toolgroup.belongs(printer_groups_id) | (ns.db.tool.toolgroup==None)))
  else:
    query = ((ns.db.tool.deleted==0)&(ns.db.product.id==ns.db.tool.product_id)&(ns.db.product.deleted==0))
  left = None
  
  form = DIV(ui.select.create_search_form(URL("")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
  gform = ui.select.find_data(table="tool",query=query,fields=fields,orderby=ns.db.tool.id,
                      paginate=20,maxtextlength=25,left=left,sortable=True,page_url=None,priority="0,1")
  return dict(form=form, gform=DIV(gform, _id="dlg_frm"))

@ns_auth.requires_login()
def frm_quick_tool_printer():
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  
  if session.mobile:
    fields = [ns.db.tool.id, ns.db.tool.description, ns.db.tool.product_id, ns.db.tool.inactive]
    ns.db.tool.id.label = T('Serial No.')
    ns.db.tool.id.represent = lambda value,row: ui.control.get_mobil_button(SPAN(ns.db.tool(id=int(value))["serial"]), 
                                  href=URL(r=request, f="frm_tool/view/tool/"+str(value)), 
                                  cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
  else:
    ruri = request.wsgi.environ["REQUEST_URI"]
    if ruri.find("view")>0 or ruri.find("edit")>0:
      ruri = str(ruri).replace("frm_quick_tool_printer", "frm_tool")
      redirect(ruri)
    response.margin_top = "20px"
    response.cmd_back = ui.control.get_home_button()
    response.titleicon = URL(ui.dir_images,'icon16_printer.png')
    fields = [ns.db.tool.serial, ns.db.tool.description, ns.db.tool.product_id, ns.db.tool.inactive]
    
  response.view=ui.dir_view+'/quick.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Server printers')
  
  query = ((ns.db.tool.deleted==0)&(ns.db.product.id==ns.db.tool.product_id)&(ns.db.product.deleted==0)
           &(ns.db.tool.toolgroup==ns.db.groups.id)
           &(ns.db.groups.groupvalue=='printer'))
  left = None
  
  if audit_filter=="all":
    if session.mobile:
      response.cmd_add_new = ui.control.get_mobil_button(
        label=T("New Printer"), href=URL('frm_tool/new/tool/printer'), 
        cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
    else:
      response.cmd_add_new = ui.control.get_new_button(URL('frm_tool/new/tool/printer'))
        
  form = DIV(ui.select.create_search_form(URL("frm_quick_tool_printer")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
  gform = ui.select.find_data(table="tool",query=query,fields=fields,orderby=ns.db.tool.id,
                      paginate=20,maxtextlength=25,left=left,sortable=True,page_url=None,priority="0,1")
  return dict(form=form, gform=DIV(gform, _id="dlg_frm"))

def frm_quick_transitem(form, transtype=None, frm_edit="frm_trans"):  
  response.view=ui.dir_view+'/quick.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select document')
  if session.mobile:
    fields = [ns.db.trans.id, ns.db.trans.transtype, ns.db.trans.direction, ns.db.trans.customer_id, ns.db.trans.transdate]    
    ns.db.trans.id.label = T('Document No.')
    ns.db.trans.id.represent = lambda value,row: ui.control.get_mobil_button(SPAN(ns.db.trans(id=int(value))["transnumber"]), 
                                  href=URL(r=request, f=frm_edit+"/view/trans/"+str(value)), 
                                  cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
  else:
    response.margin_top = "20px"
    response.cmd_back = ui.control.get_home_button()
    response.titleicon = URL(ui.dir_images,'icon16_find.png')
    fields = [ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, ns.db.trans.customer_id, ns.db.trans.transdate]
  
  transtype_invoice_id = ns.valid.get_groups_id("transtype", "invoice")
  transtype_receipt_id = ns.valid.get_groups_id("transtype", "receipt")
  direction_out_id = ns.valid.get_groups_id("direction", "out")    
  query = (((ns.db.trans.deleted==0)|((ns.db.trans.transtype==transtype_invoice_id)&(ns.db.trans.direction==direction_out_id))
           |((ns.db.trans.transtype==transtype_receipt_id)&(ns.db.trans.direction==direction_out_id)))
           &(ns.db.trans.transtype==ns.db.groups.id))
  left = [(ns.db.customer.on((ns.db.customer.id==ns.db.trans.customer_id)))]
  if request.vars.has_key("keywords"):
    if request.vars["keywords"].find("customer")>-1:
      query = query & (ns.db.customer.id==ns.db.trans.customer_id)
      left = None
  if transtype:
    query = query & (ns.db.groups.groupvalue.belongs(transtype))
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False:
    query = query & (ns.db.trans.id==-1)
  
  #disabled transtype list
  audit = ui.connect.get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = ui.select.set_transfilter(query)
    
  ns.db.trans.transdate.label = T("Date")
  ns.db.groups.groupvalue.label = T("Doc.type")
  
  gform = ui.select.find_data(table="trans",query=query,fields=fields,orderby=ns.db.trans.id,
                      paginate=20,maxtextlength=25,left=left,sortable=True,page_url=None,priority="0,1,2")
  return dict(form=form, gform=DIV(gform, _id="dlg_frm"))

@ns_auth.requires_login()
def frm_quick_transitem_all():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = str(ruri).replace("frm_quick_transitem_all", "frm_trans")
    redirect(ruri)
  form = DIV(ui.select.create_search_form(URL("frm_quick_transitem_all")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
  return frm_quick_transitem(form,("invoice","receipt","order","offer","worksheet","rent"))

@ns_auth.requires_login()
def frm_quick_transitem_delivery():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = str(ruri).replace("frm_quick_transitem_delivery", "frm_shipping")
    redirect(ruri)
  form = DIV(ui.select.create_search_form(URL("frm_quick_transitem_delivery")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
  return frm_quick_transitem(form,("order","worksheet","rent"),"frm_shipping")

@ns_auth.requires_login()
def frm_report_customer():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
    return ui.report.create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    return "Missing parameters: template or cmd!"

@ns_auth.requires_login()
def frm_report_employee():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
    return ui.report.create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    return "Missing parameters: template or cmd!"

@ns_auth.requires_login()
def frm_report_place():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
    return ui.report.create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    return "Missing parameters: template or cmd!"

@ns_auth.requires_login()
def frm_report_product():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
    return ui.report.create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    return "Missing parameters: template or cmd!"

@ns_auth.requires_login()
def frm_report_project():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
    return ui.report.create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    return "Missing parameters: template or cmd!"

@ns_auth.requires_login()
def frm_report_tool():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
    return ui.report.create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    return "Missing parameters: template or cmd!"

@ns_auth.requires_login()
def frm_report_trans():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
#   direction = ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-2]
#   transtype = ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-3]
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
#    if transtype=="invoice" and direction=="out" and request.vars["cmd"]=="pdf":
#      ns.connect.updateData("trans", values={"id":ref_id,"closed":1}, validate=False, insert_row=False)
    return ui.report.create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    return "Missing parameters: template or cmd!"

@ns_auth.requires_login()
def frm_reports():
  response.view=ui.dir_view+'/reports.html'
  sform = None
  if session.mobile:
    response.title="REPORTS"
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=report'),
                                           cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
    response.cmd_preview = ui.control.get_mobil_button(T("Show Report"), href="#", cformat=None, style="text-align: left",
                                              onclick="show_report('"+T("Missing required data")+"')", theme="b", rel="close")
  else:
    response.subtitle=""
    response.titleicon = URL(ui.dir_images,'icon16_report.png')
    response.cmd_help = ui.control.get_help_button("report")
    response.cmd_preview = ui.control.get_command_button(caption=T("Show Report"),title=T("Show Report"),color="008B00",
                              cmd="show_report('"+URL('frm_reports')+"','"+T("Missing required data")+"');")
  #request.post_vars
  if str(request.wsgi.environ["REQUEST_URI"]).find("view")>0 or str(request.wsgi.environ["REQUEST_URI"]).find("edit")>0:
    if session.mobile:
      response.cmd_back = ui.control.get_mobil_button(label=T("REPORTS"), href=URL('frm_reports'), icon="back", cformat="ui-btn-left", ajax="false")
    else:
      response.cmd_back = ui.control.get_back_button(URL('frm_reports'))
    path = str(request.wsgi.environ["REQUEST_URI"]).split("?")[0].split("/")
    report_id = int(path[len(path)-1])
    report = ns.db(ns.db.ui_report.id==report_id).select().as_list()[0]
    response.subtitle = report["repname"]
    response.description = report["description"]
    fieldtype = ns.db.groups.with_alias('fieldtype')
    wheretype = ns.db.groups.with_alias('wheretype')
    filetype = ns.db.groups(id=report["filetype"]).groupvalue
    reportfields = ns.db((ns.db.ui_reportfields.fieldtype==fieldtype.id)&(ns.db.ui_reportfields.wheretype==wheretype.id)&
                         (ns.db.ui_reportfields.report_id==report_id)).select(
                          ns.db.ui_reportfields.ALL, fieldtype.groupvalue, wheretype.groupvalue, orderby=ns.db.ui_reportfields.orderby).as_list()
    tfields=[]
    col3 = {}
    for field in reportfields:
      if field["fieldtype"]["groupvalue"]=="bool":
        tfield = Field(field["ui_reportfields"]["fieldname"], 'boolean', label=field["ui_reportfields"]["description"])
        if field["ui_reportfields"]["defvalue"]=="t" or field["ui_reportfields"]["defvalue"]=="true":
          tfield.default = True
        else:
          tfield.default = False
          
      elif field["fieldtype"]["groupvalue"]=="date":
        tfield = Field(field["ui_reportfields"]["fieldname"], 'date', label=field["ui_reportfields"]["description"])
        tfield.default = datetime.datetime.now().date()
        if field["ui_reportfields"]["defvalue"]!=None:
          try:
            tfield.default+=datetime.timedelta(days=int(field["ui_reportfields"]["defvalue"]))
          except Exception:
            pass
          
      elif field["fieldtype"]["groupvalue"]=="integer":
        tfield = Field(field["ui_reportfields"]["fieldname"], 'integer', label=field["ui_reportfields"]["description"])
        tfield.default = 0
        if field["ui_reportfields"]["defvalue"]!=None:
          try:
            tfield.default = int(field["ui_reportfields"]["defvalue"])
          except Exception:
            pass
          
      elif field["fieldtype"]["groupvalue"]=="float":
        tfield = Field(field["ui_reportfields"]["fieldname"], 'double', label=field["ui_reportfields"]["description"])
        tfield.default = 0
        if field["ui_reportfields"]["defvalue"]!=None:
          try:
            tfield.default = float(field["ui_reportfields"]["defvalue"])
          except Exception:
            pass
      
      elif field["fieldtype"]["groupvalue"]=="valuelist":
        valuelist = str(field["ui_reportfields"]["valuelist"]).split("|")
        tfield = Field(field["ui_reportfields"]["fieldname"], 'string', label=field["ui_reportfields"]["description"],
                       requires = IS_IN_SET(valuelist))
        if field["ui_reportfields"]["defvalue"]!=None:
          try:
            tfield.default = field["ui_reportfields"]["defvalue"]
          except Exception:
            pass
          
      else:
        tfield = Field(field["ui_reportfields"]["fieldname"], 'string', label=field["ui_reportfields"]["description"])
        if field["ui_reportfields"]["defvalue"]!=None:
          try:
            tfield.default = field["ui_reportfields"]["defvalue"]
          except Exception:
            pass
          
      if field["wheretype"]["groupvalue"]=="in":
        tfield.label +="*"
        if field["fieldtype"]["groupvalue"]!="bool":
          tfield.required = True
          tfield.requires = IS_NOT_EMPTY()
        col3[tfield.name]= INPUT(_type='checkbox', _name='rq_'+tfield.name, _value=tfield.name, _disabled='disabled', value=True)
      else:
        col3[tfield.name]= INPUT(_type='checkbox', _name='cb_'+tfield.name, _value=None, value=False)
      tfields.append(tfield)
    gform = SQLFORM.factory(*tfields, col3 = col3, submit_button=T("Show Report"),_id="frm_report", table_name="report", _target="_blank")
    gform[0].insert(-1, DIV(SPAN(T("* is a required field!"), _style="font-weight: bold;font-style: italic;")))
    submit_row = gform[0].element("#submit_record__row")
    for i in range(len(gform[0])):
      if gform[0][i]==submit_row:
        gform[0].__delitem__(i)
        break
    
    if filetype=="fpdf":
      response.rtable = TABLE(_style="width: 100%;")
      orientation = ns.db((ns.db.groups.groupname=="orientation")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.id)
      cmb_orientation = SELECT(*[OPTION(T(ori["description"]), _value=ori["groupvalue"]) for ori in orientation], 
                                 _id="cmb_orientation", _name="orientation",_style="width: 100%;")
      size = ns.db((ns.db.groups.groupname=="papersize")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.id)
      cmb_size = SELECT(*[OPTION(psize["description"], _value=psize["groupvalue"]) for psize in size], 
                                 _id="cmb_size", _name="size",_style="width: 100%;")
      cmb_size[1]["_selected"]=["selected"]
      cmb_output = SELECT([OPTION(T("HTML"), _value="html"),OPTION(T("PDF"), _value="pdf"),OPTION(T("XML"), _value="xml")], _id="cmb_output", _name="output",_style="width: 100%;")
      if session.mobile:
        response.rtable.append(TR(
                     TD(DIV(T("Orientation")+':',_class="label"),
                        _style="width: 100px;border-top: solid;"),
                     TD(cmb_orientation, _style="border-top: solid;")))
        response.rtable.append(TR(
                       TD(DIV(T("Size")+':',_class="label")),
                       TD(cmb_size, _style="")))
        response.rtable.append(TR(
                       TD(DIV(T("Output")+':',_class="label"),
                          _style="border-bottom: solid;"),
                       TD(cmb_output, _style="border-bottom: solid;")))

      else:
        response.rtable.append(TR(
                     TD(T("Orientation/Size/Output"),
                        _style="background-color: #F1F1F1;font-weight: bold;text-align: left;vertical-align: middle;padding: 5px;border-bottom: solid;border-top: solid;"),
                     TD(cmb_orientation, _style="width: 120px;padding: 5px;border-bottom: solid;border-top: solid;padding-right: 0px;"),
                     TD(cmb_size, _style="width: 80px;padding: 5px;border-bottom: solid;border-top: solid;padding-right: 0px;"),
                     TD(cmb_output, _style="width: 80px;padding: 5px;border-bottom: solid;border-top: solid;")))
    
    gform.process()
    if len(request.post_vars)>0 and request.post_vars._formkey:
      formkey = request.post_vars._formkey
      session[formkey]=Storage(params={},filters={})
      session[formkey].params["report_id"]=report_id
      for param in request.post_vars.keys():
        if not str(param).startswith("cb_") and col3.has_key(str(param)):
          if col3[str(param)]["_name"].startswith("rq_"):
            session[formkey].filters[str(param)]=request.post_vars[str(param)]
          else:
            if request.post_vars["cb_"+str(param)]:
              session[formkey].filters[str(param)]=request.post_vars[str(param)]
      if request.post_vars.output:
        session[formkey].params["output"] = request.post_vars.output
      else: 
        session[formkey].params["output"] = "html"
      session[formkey].params["orientation"] = request.post_vars.orientation if request.post_vars.orientation else "P"
      session[formkey].params["size"] = request.post_vars.size if request.post_vars.size else "A4"
      redirect(URL('cmd_get_report/'+str(request.post_vars._formkey)))
  else:  
    filetype_id = ns.db((ns.db.groups.groupname=="filetype")&(ns.db.groups.groupvalue.belongs(("html","fpdf","gshi","xls")))).select(ns.db.groups.id)
    nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="report")).select(ns.db.groups.id)
    reports = (ns.db.ui_report.filetype.belongs(filetype_id)&ns.db.ui_report.nervatype.belongs(nervatype_id))
    
    #disabled reports list
    audit = ui.connect.get_audit_subtype("report")
    if len(audit)>0:
      reports = reports & (~ns.db.ui_report.id.belongs(audit))
    
    if session.mobile:
      gform=None
      response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
                                               icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
      reports_lst = ns.db(reports).select(orderby=ns.db.ui_report.repname)
    
      reports = UL()
      reports["_data-role"] = "listview"
      reports["_data-filter"] = "true"
      reports["_data-filter-placeholder"] = T('Search reports...')
      reports["_data-split-icon"] = "info"
      reports["_data-split-theme"] = "d"
      for report in reports_lst:
        reports.append(LI(A(
                            H3(report.repname,_style="white-space: normal;"),
                      P(report.description,_style="white-space: normal;"),
                      P(STRONG(report.label),_class="ui-li-aside"),
                      _href=URL('frm_reports/view/'+str(report.id)))))
      response.reports = reports
    else:
      response.cmd_back = ui.control.get_home_button()

      fields = (ns.db.ui_report.id, ns.db.ui_report.repname, ns.db.ui_report.label,
                ns.db.ui_report.description)
      sform = DIV(ui.select.create_search_form(URL("frm_reports")),
               _style="background-color: #F2F2F2;padding:10px;padding-bottom:0px;")
      ns.db.ui_report.id.readable = ns.db.ui_report.id.writable = False
      gform = ui.select.find_data(table="ui_report",query=reports,fields=fields,orderby=ns.db.ui_report.repname,
                    paginate=20,maxtextlength=70,left=None,sortable=True,page_url=None,fullrow=True)
  return dict(form=gform, sform=sform)

def frm_setting():
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    redirect(URL('frm_setting'))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ns.connect.deleteData("fieldvalue", ref_id=fieldvalue_id):
      redirect(URL('frm_setting'))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    ui.connect.clear_post_vars()
    if request.post_vars.has_key("ref_id"):
      if request.post_vars["ref_id"]=="":
        del request.post_vars["ref_id"]
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    row_id = ns.connect.updateData("fieldvalue", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      redirect()
      
  response.view=ui.dir_view+'/setting.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Database Settings')
  nervatype_setting = ns.valid.get_groups_id("nervatype", "setting")
  setting_fields = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_setting))
  fields=[ns.db.deffield.description, ns.db.fieldvalue.value, ns.db.fieldvalue.notes]
  
  links = ui.select.set_view_fields("setting", nervatype_setting, 0, (audit_filter!="readonly"), setting_fields, None, "", "",False)
  if session.mobile:
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=setting'),
                                             cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
    links = None
  else:
    response.titleicon = URL(ui.dir_images,'icon16_numberdef.png')
    response.cmd_help = ui.control.get_help_button("setting")
    response.cmd_back = ui.control.get_home_button()
    response.margin_top = "20px"
    
  sform = ui.select.create_search_form(URL("frm_setting"))
  form = ui.select.find_data(table="fieldvalue",query=setting_fields,fields=fields,orderby=ns.db.deffield.description,
                      paginate=10,maxtextlength=30,links=links,left=None,sortable=True,page_url=None,deletable=False,fullrow=True)
  
  if DEMO_MODE:
    response.cmd_fieldvalue_update = DIV(SPAN(T('DEMO MODE')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
  return dict(form=form,sform=sform)

@ns_auth.requires_login()
def frm_shipping():
  delivery_audit_filter = ui.connect.get_audit_filter("trans", "delivery")[0]
  if delivery_audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("dlg_product_stock")>0 :
    return dlg_product_stock()
    
  trans_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if ns.db.trans(id=trans_id).deleted==1:
    return ui.connect.show_disabled(response.title)
  if not session.shiptemp:
    session.shiptemp = {}
  if session.shiptemp.has_key(trans_id)==False:
    session.shiptemp[trans_id]=[]
  
  def getOItem(oitems, item_id, product_id):
    retval = None
    index = next((i for i in xrange(len(oitems)) if oitems[i]["item_id"] == item_id and oitems[i]["product_id"] == product_id), None)
    if index is not None:
      retval = oitems[index]
    return retval
  
  def getItemsTable():
    if session.mobile:
      htmltable = TABLE(THEAD(TR(TH(T("Edit")),TH(T("Product No.")),TH(T("Qty")),TH(T("Batch No.")),TH(T("Product")))))
      tbody = TBODY()
      numrec=0
      for row in session.shiptemp[trans_id]:
        numrec+=1
        tbody.append(TR(
                        TD(ui.control.get_mobil_button(ui.control.format_value("integer",row["item_id"]), href="#", cformat=None, icon="edit", 
                            title=T("Edit item"), style="text-align: left;",
                            onclick="set_delivery("+str(row["item_id"])+","+str(row["product_id"])
                             +",'"+str(row["partnumber"])+"','"+str(row["batch"])+"',"+str(row["qty"])+")", theme="d")),
                        TD(row["partnumber"], 
                           ui.control.get_mobil_button(T("Delete item"), href="#", cformat=None, icon="trash", iconpos="notext",
                             title=T("Delete item"), style="text-align: left;",
                             onclick='del_delivery('+str(row["item_id"])+','+str(row["product_id"])+');', theme="d")),
                        TD(ui.control.format_value("number",row["qty"])),
                        TD(row["batch"]),
                        TD(A(row["description"], _href="#", 
                             _onclick="javascript:window.open('"+URL("frm_product/view/product/"+str(row["product_id"]))+"', '_blank');"))
                        ))
      htmltable.append(tbody)
      ui.control.set_htmltable_style(htmltable,"tbl_create_page","0,1,2")
      return htmltable
    else:
      htmltable = TABLE(THEAD(TR(TH(),TH(T("No.")),TH(T("Product No.")),TH(T("Product")),TH(T("Batch No.")),TH(T("Qty")))))
      tbody = TBODY()
      numrec=0
      for row in session.shiptemp[trans_id]:
        if numrec % 2 == 0:
          classtr = 'even'
        else:
          classtr = 'odd'
        numrec+=1
        tbody.append(TR(
                        TD(A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                             _class="w2p_trap buttontext button", _href="#", _onclick="set_delivery("+str(row["item_id"])+","+str(row["product_id"])
                             +",'"+str(row["partnumber"])+"','"+str(row["batch"])+"',"+str(row["qty"])+")",
                             _title=T("Edit item")),
                           A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                             _class="w2p_trap buttontext button", _href="#", _onclick="del_delivery("+str(row["item_id"])+","+str(row["product_id"])+")",
                             _title=T("Delete item")),
                             _class="row_buttons", _style="width:40px;"),
                        TD(ui.control.format_value("integer",row["item_id"])),
                        TD(row["partnumber"]),
                        TD(A(row["description"], _href="#", 
                             _onclick="javascript:window.open('"+URL("frm_product/view/product/"+str(row["product_id"]))+"', '_blank');")),
                        TD(row["batch"]),
                        TD(ui.control.format_value("number",row["qty"])),
                        _class=classtr))
      htmltable.append(tbody)
      return DIV(DIV(DIV(htmltable,_style='width:100%;overflow-x:auto;'),_class="web2py_table"),_class="web2py_grid")
  
  nervatype_movement_id = ns.valid.get_groups_id("nervatype", "movement")
  nervatype_item_id = ns.valid.get_groups_id("nervatype", "item")
  
  if request.vars.create_items and request.vars.create_place_id and request.vars.create_date:
    if len(session.shiptemp[trans_id])==0:
      return ""
    direction = ns.db.groups(id=ns.db.trans(id=trans_id).direction).groupvalue
    transnumber = ns.connect.nextNumber("delivery_"+direction)
    transtype_delivery = ns.valid.get_groups_id("transtype", "delivery")
    plst = ns.db((ns.db.pattern.deleted==0)&(ns.db.pattern.defpattern==1)&(ns.db.pattern.transtype==transtype_delivery)).select()
    if len(plst)>0:
      fnote = plst[0]["notes"]
    else:
      fnote=None
    values = {"transtype":transtype_delivery, "direction":ns.db.trans(id=trans_id).direction, "transnumber":transnumber, 
              "crdate":datetime.datetime.now().date(), "transdate":request.vars.create_date, "fnote":fnote,
              "transtate":ns.valid.get_groups_id("transtate", "ok"),
              "cruser_id":session.auth.user.id}
    del_trans_id = ns.connect.updateData("trans", values=values, validate=False, insert_row=True)
    movetype_inventory_id = ns.valid.get_groups_id("movetype", "inventory")
    for row in session.shiptemp[trans_id]:
      if direction=="out":
        qty=-row["qty"]
      else:
        qty=row["qty"]
      shippingdate = datetime.datetime.strptime(str(request.vars.create_date)+" 00:00:00", str('%Y-%m-%d %H:%M:%S'))
      values = {"trans_id":del_trans_id, "shippingdate":shippingdate, "movetype":movetype_inventory_id,
                "place_id":request.vars.create_place_id, "product_id":row["product_id"], "qty":qty, "notes":row["batch"]}
      movement_id = ns.connect.updateData("movement", values=values, validate=False, insert_row=True)
      values = {"nervatype_1":nervatype_movement_id, "ref_id_1":movement_id, "nervatype_2":nervatype_item_id, "ref_id_2":row["item_id"]}
      ns.connect.updateData("link", values=values, validate=False, insert_row=True)
    session.shiptemp[trans_id]=[]
    return "OK"
  
  if request.vars.add_item_id and request.vars.add_product_id and request.vars.add_qty:
    try:
      item_id = int(request.vars.add_item_id)
      product_id = int(request.vars.add_product_id)
      qty = float(request.vars.add_qty)
    except:
      return ""
    oitem = getOItem(session.shiptemp[trans_id],item_id,product_id)
    if not oitem:
      session.shiptemp[trans_id].append({"item_id":item_id, "product_id":product_id, 
                      "partnumber":ns.db.product(id=product_id).partnumber, "description":ns.db.product(id=product_id).description, 
                      "batch":"", "qty":qty})
      return "OK"
    return ""
  
  if request.vars.del_item_id and request.vars.del_product_id:
    try:
      item_id = int(request.vars.del_item_id)
      product_id = int(request.vars.del_product_id)
    except:
      return ""
    oitem = getOItem(session.shiptemp[trans_id],item_id,product_id)
    if oitem:
      session.shiptemp[trans_id].remove(oitem)
      return "OK"
    return ""  
  
  if request.vars.del_all:
    session.shiptemp[trans_id]=[]
    return "OK"
  
  if request.vars.edit_item_id and request.vars.edit_product_id:
    try:
      item_id = int(request.vars.edit_item_id)
      product_id = int(request.vars.edit_product_id)
      batch = str(request.vars.edit_batch)
      qty = float(request.vars.edit_qty)
    except:
      return ""
    oitem = getOItem(session.shiptemp[trans_id],item_id,product_id)
    if oitem:
      oitem["batch"] = batch
      oitem["qty"] = qty
      return getItemsTable()
    return ""
  
  response.view=ui.dir_view+'/shipping.html'
  response.subtitle=T('SHIPPING')
  if not session.mobile:
    response.titleicon = URL(ui.dir_images,'icon16_lorry.png')
    response.icon_order = IMG(_src=URL(ui.dir_images,'icon16_order.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_corrected = IMG(_src=URL(ui.dir_images,'icon16_corrected.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_lorry_go = IMG(_src=URL(ui.dir_images,'icon16_lorry_go.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.lo_menu = []
  
  
  response.transnumber = ns.db.trans(id=trans_id).transnumber
  response.direction = T(ns.db.groups(id=ns.db.trans(id=trans_id).direction).groupvalue)
  response.customer = DIV(A(ns.db.customer(id=ns.db.trans(id=trans_id).customer_id).custname, _href="#", _onclick="javascript:window.open('"
                           +URL("frm_customer/view/customer/"+str(ns.db.trans(id=trans_id).customer_id))+"', '_blank');")
                         ,_class="label_disabled", _style="display:block;")
  
  delivery_audit_filter = ui.connect.get_audit_filter("trans", "delivery")[0]
  
  if session.mobile:
    response.cmd_filter = ui.control.get_mobil_button(label=T("Filter data"), href="#", 
        cformat=None, style="text-align: left;", icon="search", ajax="false", theme="b",
        onclick= "document.forms['frm_filter'].submit();")
    if delivery_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
                                               icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
    else:
      response.cmd_back = ui.control.get_mobil_button(
          label=response.transnumber, href=URL("frm_trans/view/trans/")+str(trans_id), icon="back", cformat="ui-btn-left", ajax="false")   
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=shipping'),
                                               cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:
    if delivery_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_home_button()
    else:
      response.cmd_back = ui.control.get_back_button(URL("frm_trans/view/trans/")+str(trans_id))
    response.cmd_help = ui.control.get_help_button("shipping")
  
#product item list
  response.filter = SQLFORM.factory(
    Field('product', type='string', length=50, label=T('Description')),
    Field('nocomp', type='boolean', label=T('Not completed')),
    submit_button=T("Filter"), table_name="filter", _id="frm_filter"
  )
  response.filter.process(keepvalues=True,onfailure=None)
  response.filter.errors.clear()
  response.flash = None
  
  protype_item = ns.valid.get_groups_id("protype", "item")
  query = ((ns.db.item.deleted==0)&(ns.db.item.trans_id==trans_id))
  join = [(ns.db.product.on((ns.db.item.product_id==ns.db.product.id)&(ns.db.product.protype==protype_item)))]
  left = [(ns.db.fieldvalue.on((ns.db.item.product_id==ns.db.fieldvalue.ref_id)&(ns.db.fieldvalue.fieldname=="product_element")))]
  fields = [ns.db.item.id.with_alias('item_id'), ns.db.item.description, ns.db.item.product_id.with_alias('product_id'), 
            ns.db.item.qty, ns.db.product.partnumber, ns.db.fieldvalue.value, ns.db.fieldvalue.notes]
  if response.filter.vars.product:
    query= query & (ns.db.product.description.lower().like("%"+str(response.filter.vars.product).lower()+"%"))
  olist = ns.db(query).select(*fields,join=join,left=left,orderby=ns.db.item.id)
  
  oitems=[]
  plist=[]
  for item in olist:
    if item.fieldvalue.value:
      product_id = int(item.fieldvalue.value)
      if ns.db.product(id=product_id).protype != protype_item: continue
      partnumber = ns.db.product(id=product_id).partnumber
      qty = item.fieldvalue.notes.replace(item.fieldvalue.notes.rstrip('+-.0123456789'),'')
      if qty=="":
        qty = item.item.qty
      else:
        qty = item.item.qty*float(qty)
      pgroup = True
    else:
      product_id = item.product_id
      partnumber = item.product.partnumber
      qty = item.item.qty
      pgroup = False
    oitems.append({"item_id":item.item_id, "product_id":product_id, "description":item.item.description, 
           "partnumber":partnumber, "qty":qty, "tqty":0, "diff":qty, "pgroup":pgroup,"custpartnumber":None,"edit":""})
    plist.append(product_id)
    
  query = ((ns.db.item.trans_id==trans_id)&(ns.db.item.deleted==0))
  join = [(ns.db.product.on((ns.db.item.product_id==ns.db.product.id))),
          (ns.db.link.on((ns.db.link.nervatype_2==nervatype_item_id)&(ns.db.link.ref_id_2==ns.db.item.id)&
           (ns.db.link.nervatype_1==nervatype_movement_id)&(ns.db.link.deleted==0))),
          (ns.db.movement.on((ns.db.link.ref_id_1==ns.db.movement.id)&(ns.db.movement.deleted==0)))]
  groupfields=[ns.db.item.id.with_alias('item_id'),ns.db.movement.product_id.with_alias('product_id'),ns.db.movement.qty.sum().with_alias('qty')]
  groupby=[ns.db.item.id|ns.db.movement.product_id]
  olist = ns.db(query).select(*groupfields,join=join,groupby=groupby)
  
  for item in olist:
    oitem = getOItem(oitems,item.item_id,item.product_id)  
    if oitem:
      oitem["tqty"] = item.qty
      if ns.db.groups(id=ns.db.trans(id=trans_id).direction).groupvalue=="out":
        oitem["tqty"]=-oitem["tqty"]
      oitem["diff"]=oitem["qty"]-oitem["tqty"]
  
  query = ((ns.db.fieldvalue.ref_id.belongs(plist))&(ns.db.fieldvalue.fieldname=="product_custpartnumber")
           &(ns.db.fieldvalue.value==str(ns.db.trans(id=trans_id).customer_id)))
  fields=[ns.db.fieldvalue.ref_id.with_alias('product_id'),ns.db.fieldvalue.notes.with_alias('partnumber')]
  olist = ns.db(query).select(*fields)
  for item in olist:
    for oitem in oitems:
      if oitem["product_id"]==item.product_id:
        oitem["custpartnumber"]=item.partnumber
  
  for item in session.shiptemp[trans_id]:
    for oitem in oitems:
      if oitem["item_id"]==item["item_id"] and oitem["product_id"]==item["product_id"]:
        oitem["edit"]= "*"
  
  if session.mobile:
    htmltable = TABLE(THEAD(TR(TH(T("No.")),TH(T("Product No.")),TH(T("Difference"),_colspan="2"),
                             TH(T("Product")),TH(T("Description")),TH(T("Doc. qty")),TH(T("Turnover")))))
  else:
    htmltable = TABLE(THEAD(TR(TH(),TH(T("No.")),TH(T("Product No.")),TH(T("Product")),TH(T("Item description")),
                             TH(T("Doc. qty")),TH(T("Turnover")),TH(T("Difference"),_colspan="2"))))
  tbody = TBODY()
  numrec=0
  for row in oitems:
    if not session.mobile:
      if numrec % 2 == 0:
        classtr = 'even'
      else:
        classtr = 'odd'
    if row["diff"]!=0:
      dstyle="color: red;font-weight: bold;"
    else:
      if response.filter.vars.nocomp==True:
        continue
      dstyle="color: green;font-weight: bold;"
    numrec+=1
    if session.mobile:
      tbody.append(TR(
                    TD(ui.control.get_mobil_button(ui.control.format_value("integer",row["item_id"]), href="#", cformat=None, icon="plus", 
                          title=T("Add the difference"), style="text-align: left;",
                          onclick="add_delivery("+str(row["item_id"])+","+str(row["product_id"])+","+str(row["diff"])+",'"+str(row["edit"])+"')", theme="d")),
                    TD(row["partnumber"],
                       ui.control.get_mobil_button(T("Stock"), href="#", cformat=None, icon="info", iconpos="notext",
                           title=T("Show stock"), style="text-align: left;",
                           onclick='$("#stock_info").load("dlg_product_stock/'+str(row["product_id"])+'");$("#popup_stock_info").popup("open");return false;', theme="d")
                       ),
                    TD(ui.control.format_value("number",row["diff"]), _style=dstyle),
                    TD(row["edit"],_style="text-align: left;font-weight: bold;width:10px;"),
                    TD(A(ns.db.product(id=row["product_id"]).description, _href="#", 
                         _onclick="javascript:window.open('"+URL("frm_product/view/product/"+str(row["product_id"]))+"', '_blank');")),
                    TD(row["description"]),
                    TD(ui.control.format_value("number",row["qty"])),
                    TD(ui.control.format_value("number",row["tqty"])),
                    )
                 )
    else:
      tbody.append(TR(
                    TD(A(SPAN(_class="icon plus"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="add_delivery("+str(row["item_id"])+","+str(row["product_id"])+","+str(row["diff"])+",'"+str(row["edit"])+"')",
                         _title=T("Add the difference")),
                       A(SPAN(_class="icon book"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#null", _title=T("Show stock"), 
                         _onclick='$("#stock_info").load("dlg_product_stock/'+str(row["product_id"])
                           +'");$("#frm_stocks").dialog({dialogClass: "n2py-dialog", modal: true, minWidth: 600, resizable: false, position: {my:"center",at:"top"}, title: "STOCKS | '
                           +row["partnumber"]+' | '+ns.db.product(id=row["product_id"]).description[:20]+'"});'),
                         _class="row_buttons", _style="width:40px;"),
                    TD(ui.control.format_value("integer",row["item_id"])),
                    TD(row["partnumber"]),
                    TD(A(ns.db.product(id=row["product_id"]).description, _href="#", 
                         _onclick="javascript:window.open('"+URL("frm_product/view/product/"+str(row["product_id"]))+"', '_blank');")),
                    TD(row["description"]),
                    TD(ui.control.format_value("number",row["qty"])),
                    TD(ui.control.format_value("number",row["tqty"])),
                    TD(ui.control.format_value("number",row["diff"]),_style=dstyle),
                    TD(row["edit"],_style="vertical-align: middle;text-align: center;font-weight: bold;width:10px;"),
                    _class=classtr))
  htmltable.append(tbody)
  if session.mobile:
    ui.control.set_htmltable_style(htmltable,"tbl_item_page","0,1,2")
    response.view_oitems = htmltable
    response.cmd_oitems_add = ui.control.get_mobil_button(label=T("Add all of the difference"), href="#", 
            cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b",
            onclick= "add_all_delivery();", rel="close")
  else:
    response.view_oitems = DIV(DIV(DIV(htmltable,_style='width:100%;overflow-x:auto;'),_class="web2py_table"),_class="web2py_grid")
    response.cmd_oitems_add = ui.control.get_tabnew_button(T("ADD"),T('Add all of the difference'),"cmd_all_item", cmd="add_all_delivery()")
  
#create delivery
  if request.vars.add_all:
    for row in oitems:
      sitem = getOItem(session.shiptemp[trans_id],row["item_id"],row["product_id"])
      if not sitem and row["diff"]!=0:
        session.shiptemp[trans_id].append({"item_id":row["item_id"], "product_id":row["product_id"], 
                      "partnumber":row["partnumber"], "description":ns.db.product(id=row["product_id"]).description, 
                      "batch":"", "qty":row["diff"]})
    return "OK"
  
  if session.mobile:
    response.cmd_oitems_remove = ui.control.get_mobil_button(label=T("Remove all items"), href="#", 
          cformat=None, style="text-align: left;", icon="trash", ajax="false", theme="b",
          onclick= "remove_all_delivery();", rel="close")
    response.cmd_update = ui.control.get_mobil_button(label=T("Update changes"), href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
          onclick= "update_delivery();return true;", rel="back")
  else:
    response.cmd_oitems_remove = A(SPAN(_class="icon trash")," ",T("REMOVE"), _id="cmd_del_all", 
      _style="cursor: pointer; top:3px; text-align: center;padding: 2px;padding-left: 6px;padding-right: 3px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Remove all items'), _onclick= "remove_all_delivery()")
    response.cmd_update = ui.control.get_command_button(_id="cmd_update", caption=T("Save"),title=T("Update changes..."),color="008B00",
                                cmd="update_delivery();return true;", _height="30px")
    response.cmd_cancel = A(SPAN(_class="icon cross"), _id="cmd_cancel", 
      _style="cursor: pointer; top:2px; text-align: center;padding: 2px;padding-left: 6px;padding-right: 3px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "var tbl=document.getElementById('edit_item');tbl.style.display = 'none';return true;")
  response.shippingdate = INPUT(_class="date", _id="shippingdate", _name="shippingdate", _type="text", _value=datetime.datetime.now().date())
  response.place_control = ui.select.get_place_selector("", placetype="dlg_place_warehouse",title=T("Select warehouse"))
  response.place_id = INPUT(_name="place_id", _type="hidden", _value="", _id="place_id")
  if delivery_audit_filter in ("readonly","disabled"):
    response.cmd_create = ""
  else:
    if session.mobile:
      response.cmd_create = ui.control.get_mobil_button(label=T("Create delivery items"), href="#", 
          cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b",
          onclick= "create_delivery_items();return true;", rel="close")
    else:
      response.cmd_create = ui.control.get_command_button(_id="cmd_create", caption=T("Create"),title=T("Create delivery items"),color="008B00",
                              cmd="create_delivery_items();return true;", _height="30px")
  
  response.trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="trans_id")
  response.item_id = INPUT(_name="item_id", _type="hidden", _value="", _id="item_id")
  response.product_id = INPUT(_name="product_id", _type="hidden", _value="", _id="product_id")
  response.items_table=getItemsTable()
                  
#delivery data
  trans = ((ns.db.movement.deleted==0)&(ns.db.movement.product_id==ns.db.product.id)
           &(ns.db.movement.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_movement_id)&(ns.db.link.deleted==0)
           &(ns.db.link.nervatype_2==nervatype_item_id)&(ns.db.link.ref_id_2==ns.db.item.id)&(ns.db.item.trans_id==trans_id))
  trans_count = ns.db(trans).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
  if session.mobile:
    fields = [ns.db.movement.trans_id, ns.db.product.partnumber,  
            ns.db.movement.qty, ns.db.movement.shippingdate, ns.db.movement.notes, ns.db.movement.product_id]
    links = None
    if session["shipping_page_"+str(trans_id)]:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value=session["shipping_page_"+str(trans_id)])
      session["shipping_page_"+str(trans_id)]="item_page"
    else:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value="item_page")
    
    response.menu_item = ui.control.get_mobil_button(T("Document Items"), href="#", 
        cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('item_page');", theme="a", rel="close")
    response.menu_create = ui.control.get_mobil_button(T("Create Delivery"), href="#", 
        cformat=None, icon="edit", style="text-align: left;",
        onclick= "show_page('create_page');", theme="a", rel="close")
    response.menu_delivery = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Delivery Items"),trans_count), href="#", 
        cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('delivery_page');", theme="a", rel="close")
  else:
    fields = [ns.db.movement.trans_id, ns.db.movement.shippingdate, ns.db.movement.place_id, 
            ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, 
            ns.db.movement.notes, ns.db.movement.qty]
    response.cmd_trans_count= SPAN(" ",SPAN(str(trans_count), _class="detail_count"))
    links = [lambda row: A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("frm_trans/view/trans/")+str(row.movement.trans_id), 
                         _target="_blank", _title=T("Edit Delivery"))]
  ns.db.movement.shippingdate.represent = lambda value,row: ui.control.format_value("date",value)
  response.view_trans = ui.select.get_tab_grid(_query=trans, _field_id=ns.db.movement.id, _fields=fields, _deletable=False, links=links, 
                             multi_page="trans_page", rpl_1="/frm_shipping", rpl_2="/frm_shipping/view/trans/"+str(trans_id)
                             ,_paginate=100, _editable=False, _priority="0,1,2")
        
  return dict()

def frm_tax():
  audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return ui.connect.show_disabled(response.title)
  ruri = request.wsgi.environ["REQUEST_URI"]
  if str(ruri).find("delete/tax")>0:
    tax_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if not ns.connect.deleteData("tax", ref_id=tax_id):
      session.flash = str(ns.error_message)
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(URL('frm_tax'))
    redirect(URL('frm_tax'))
    
  response.view=ui.dir_view+'/tax.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Tax')
  if not session.mobile:
    if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
      session.back_url = request.wsgi.environ["HTTP_REFERER"]
    else:
      session.back_url = URL("index")
    response.titleicon = URL(ui.dir_images,'icon16_percent.png')
    response.cmd_back = ui.control.get_back_button(session.back_url)
  ns.db.tax.id.readable = ns.db.tax.id.writable = False
  ns.db.tax.taxcode.label = T('Code')
  if str(ruri).find("new/tax")>0 or str(ruri).find("edit/tax")>0:
    response.edit = True
    sform = None
    if str(ruri).find("edit/tax")>0:
      tax_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      response.subtitle=T('Edit tax')
      form = SQLFORM(ns.db.tax, record=tax_id, submit_button=T("Save"), comments = False, formstyle = 'divs', _id="frm_tax")
    else:
      tax_id = -1
      response.subtitle=T('New tax')
      form = SQLFORM(ns.db.tax, submit_button=T("Save"), comments = False, formstyle = 'divs', _id="frm_tax")
    
    if form.validate(keepvalues=True):      
      if tax_id>0: form.vars.id = tax_id
      row_id = ns.connect.updateData("tax", values=form.vars, validate=False, insert_row=True)  
      if not row_id:
        response.flash = str(ns.error_message)
      else:
        if tax_id==-1:
          redirect(URL('frm_tax'))
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    form.custom.widget.inactive = ui.control.get_bool_input(tax_id,"tax","inactive")
    if session.mobile:
      response.cmd_tax_close = ui.control.get_mobil_button(label=T("BACK"), href=URL('frm_tax'),
        icon="back", theme="a", ajax="false")
    else:
      response.cmd_back = ui.control.get_back_button(URL('frm_tax'))
    if audit_filter=="readonly":
      form.custom.submit = ""
      response.cmd_delete = ""
    elif session.mobile:
      form.custom.submit = ui.control.get_mobil_button(label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_tax'].submit();")
      if audit_filter=="all" and tax_id>-1:
        response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
                                            onclick="if(confirm('"+T('Are you sure you want to delete this tax?')+
                                            "')){window.location ='"+URL("frm_tax/delete/tax/"+str(tax_id))+"';};return false;", theme="b")
      else:
        response.cmd_delete = ""
  else:
    if session.mobile:
      ns.db.tax.taxcode.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL("frm_tax/edit/tax/"+str(row["id"])), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
      deletable = False
    else:
      response.margin_top = "20px"
      deletable = (audit_filter=="all")
    fields = [ns.db.tax.taxcode,ns.db.tax.description,ns.db.tax.rate,ns.db.tax.inactive]
    sform = ui.select.create_search_form(URL("frm_tax"))
    if audit_filter=="all":
      if session.mobile:
        response.cmd_add_new = ui.control.get_mobil_button(
          label=T("New Tax"), href=URL('frm_tax/new/tax'), 
          cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
      else:
        response.cmd_add_new = ui.control.get_new_button(URL('frm_tax/new/tax'))
    
    form = ui.select.find_data(table="tax",query=ns.db.tax,fields=fields,orderby=ns.db.tax.taxcode,
                       paginate=10,maxtextlength=25,links=None,left=None,page_url=None,
                       sortable=True,priority="0,1",deletable=deletable,fullrow=True)
      
  return dict(form=DIV(form, _id="dlg_frm"),sform=sform)

@ns_auth.requires_login()
def frm_tool():
  tool_audit_filter = ui.connect.get_audit_filter("tool", None)[0]
  setting_audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    tool_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["tool_page_"+str(tool_id)] = "fieldvalue_page"
    redirect(URL('frm_tool/view/tool/'+str(tool_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    tool_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["tool_page_"+str(tool_id)] = "fieldvalue_page"
    if ns.connect.deleteData("fieldvalue", ref_id=fieldvalue_id):
      redirect(URL('frm_tool/view/tool/'+str(tool_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    ui.connect.clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    row_id = ns.connect.updateData("fieldvalue", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["tool_page_"+str(request.post_vars["ref_id"])] = "fieldvalue_page"
      redirect()
  
  if ruri.find("event")>0:
    ruri = "frm_event/view"+ruri[ruri.find("frm_tool/edit")+13:]
    redirect(URL(ruri))
    
  if ruri.find("trans")>0:
    ruri = "frm_trans/view"+ruri[ruri.find("frm_tool/edit")+13:]
    redirect(URL(ruri))
  
  if ruri.find("new/tool")>0:
    tool_id = -1
  else:
    tool_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ns.db.tool(id=tool_id).deleted==1:
      return ui.connect.show_disabled(response.title)
      
  if ruri.find("delete/tool")>0:
    if not ns.connect.deleteData("tool", ref_id=tool_id):
      session.flash = str(ns.error_message)
      redirect(URL('frm_tool/view/tool/'+str(tool_id)))
    else:
      redirect(URL('find_tool_tool')) 
  
  response.view=ui.dir_view+'/tool.html'
  if not session.mobile:
    response.titleicon = URL(ui.dir_images,'icon16_wrench.png')
    response.icon_deffield = IMG(_src=URL(ui.dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_calendar = IMG(_src=URL(ui.dir_images,'icon16_calendar.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_wrench_page = IMG(_src=URL(ui.dir_images,'icon16_wrench_page.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.lo_menu = []
  nervatype_tool = ns.valid.get_groups_id("nervatype", "tool")
  
  #basic tool data
  printer_form = False
  ns.db.tool.id.readable = ns.db.tool.id.writable = False
  ns.db.tool.deleted.readable = ns.db.tool.deleted.writable = False
  ns.db.tool.description.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
  ns.db.tool.product_id.writable = False
  if tool_id>0:
    response.subtitle=T("TOOL")
    if ns.db.tool(id=tool_id).toolgroup:
      if ns.db.groups(id=ns.db.tool(id=tool_id).toolgroup).groupvalue=="printer":
        printer_form = True
        tool_audit_filter = setting_audit_filter
        response.subtitle=T("PRINTER")
        response.titleicon = URL(ui.dir_images,'icon16_printer.png')
    form = SQLFORM(ns.db.tool, record = tool_id, submit_button=T("Save"), _id="frm_tool")
    response.serial=ns.db.tool(id=tool_id).serial
    if tool_audit_filter!="disabled":
      response.cmd_report = ui.control.get_report_button(nervatype="tool", title=T('Tool Reports'), ref_id=tool_id,
                                              label=response.serial) 
    else:
      response.cmd_report = ""
    
    if tool_audit_filter=="all":
      if printer_form and DEMO_MODE:
        response.cmd_delete = ""
      elif session.mobile:
        response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
                              onclick="if(confirm('"+T('Are you sure you want to delete this tool?')+
                              "')){window.location ='"+URL("frm_tool/delete/tool/"+str(tool_id))+"';};return false;", theme="b")
      else:
        response.cmd_delete = ui.control.get_command_button(_id="cmd_delete", caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this tool?')+
                              "')){window.location ='"+URL("frm_tool/delete/tool/"+str(tool_id))+"';};return false;")
    else:
      response.cmd_delete = ""
  else:
    form = SQLFORM(ns.db.tool, submit_button=T("Save"), _id="frm_tool")
    form.vars.serial = ns.connect.nextNumber("serial",False)
    response.subtitle=T('NEW TOOL')
    response.serial=""
    response.cmd_report = ""
    response.cmd_delete = ""
    if ruri.find("new/tool/printer")>0:
      printer_form = True
      tool_audit_filter = setting_audit_filter
      response.subtitle=T('NEW PRINTER')
      response.titleicon = URL(ui.dir_images,'icon16_printer.png')
      if len(ns.db((ns.db.groups.groupname=="toolgroup")&(ns.db.groups.groupvalue=="printer")).select())>0:
        form.vars.toolgroup = ns.valid.get_groups_id("toolgroup", "printer")
  
  if printer_form:
    if setting_audit_filter=="disabled":
      return ui.connect.show_disabled(response.title)
  else:
    if tool_audit_filter=="disabled":
      return ui.connect.show_disabled(response.title)
  
  if session.mobile:
    if tool_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
                                             icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
    else:
      if printer_form:
        response.cmd_back = ui.control.get_mobil_button(label=T("SEARCH"), href=URL("frm_quick_tool_printer"), icon="search", cformat="ui-btn-left", ajax="false")
      else:
        response.cmd_back = ui.control.get_mobil_button(label=T("SEARCH"), href=URL("frm_quick_tool"), icon="search", cformat="ui-btn-left", ajax="false") 
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=tool'),
                                           cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:    
    if tool_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_home_button()
    else:
      if printer_form:
        response.cmd_back = ui.control.get_back_button(URL("frm_quick_tool_printer"))
      else:
        response.cmd_back = ui.control.get_back_button(URL("find_tool_tool")) 
    response.cmd_help = ui.control.get_help_button("tool")
  
  if tool_audit_filter in ("readonly","disabled"):
    form.custom.submit = ""
  if printer_form and DEMO_MODE:
    form.custom.submit = DIV(SPAN(T('DEMO MODE')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;") 
  elif session.mobile:
    form.custom.submit = ui.control.get_mobil_button(label=T("Save"), href="#", 
        cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
        onclick= "document.forms['frm_tool'].submit();") 
            
  if form.validate(keepvalues=True):
    if request.post_vars.product_id=="":
      response.product_control = ui.select.get_product_selector(T('Missing product name!'), error_label=True)
      response.flash = T('Missing product name!')
    else:
      form.vars.product_id = request.post_vars.product_id     
      if tool_id==-1:
        nextnumber = ns.connect.nextNumber("serial",False)
        if form.vars.serial == nextnumber:
          form.vars.serial = ns.connect.nextNumber("serial")
      else:
        form.vars.id = tool_id
      row_id = ns.connect.updateData("tool", values=form.vars, validate=False, insert_row=True)  
      if not row_id:
        response.flash = str(ns.error_message)
      else:
        redirect(URL('frm_tool/view/tool/'+str(row_id)))
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      if str(ns.db.tool.fields).find(error)>0:
        flash+=ns.db.tool[error].label+": "+form.errors[error]+", "
      else:
        flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  product_id=""
  product_description=""
  if tool_id>-1:  
    if ns.db.tool(id=tool_id).product_id!=None:
      product_id = ns.db.tool(id=tool_id).product_id
      product_description = ns.db.product(id=product_id).description
  elif ruri.find("new/tool/printer")>0:
    if ns.db.product(partnumber="printer"):
      product_id = ns.db.product(partnumber="printer").id
      product_description = ns.db.product(partnumber="printer").description
  response.product_id = INPUT(_name="product_id", _type="hidden", _value=product_id, _id="product_id")
  if response.product_control==None:
    response.product_control = ui.select.get_product_selector(product_description, protype="item")
    
  form.custom.widget.inactive = ui.control.get_bool_input(tool_id,"tool","inactive")
  
  if session.mobile:
    if session["tool_page_"+str(tool_id)]:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value=session["tool_page_"+str(tool_id)])
      session["tool_page_"+str(tool_id)]="tool_page"
    else:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value="tool_page") 
    response.menu_tool = ui.control.get_mobil_button(T("Tool Data"), href="#", 
        cformat=None, icon="edit", style="text-align: left;",
        onclick= "show_page('tool_page');", theme="a", rel="close")
  
  #show tool groups list
  if (tool_audit_filter not in ("readonly","disabled")) and (setting_audit_filter not in ("disabled")):
    if session.mobile:
      response.cmd_groups = ui.control.get_mobil_button(label=T("Edit Groups"), href="#", 
        icon="gear", cformat=None, ajax="true", theme="b", rel="close",
        onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
            +"')){window.location ='"+URL("frm_groups_toolgroup?back=1")+"';};return false;")  
    else:
      response.cmd_groups = ui.control.get_goprop_button(title=T("Edit Tool Groups"), url=URL("frm_groups_toolgroup?back=1"))  
  else:
    response.cmd_groups = ""
  
  #additional fields data
  if tool_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_tool)&(ns.db.fieldvalue.ref_id==tool_id))
    editable = not (tool_audit_filter in ("readonly","disabled"))
    ui.select.set_view_fields("tool", nervatype_tool, 0, editable, fieldvalue, tool_id, "/frm_tool", "/frm_tool/view/tool/"+str(tool_id))
  else:
    response.menu_fields = ""
      
  #event data
  event_audit_filter = ui.connect.get_audit_filter("event", None)[0]
  if event_audit_filter!="disabled" and tool_id>-1:
    event = ((ns.db.event.ref_id==tool_id)&(ns.db.event.nervatype==nervatype_tool)&(ns.db.event.deleted==0))
    event_count = ns.db(event).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    ns.db.event.id.readable = ns.db.event.id.writable = False
    ns.db.event.nervatype.readable = ns.db.event.ref_id.readable = ns.db.event.uid.readable = False
    if session.mobile:
      links = None
      editable = False
      response.menu_event = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Project Events"),event_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('event_page');",
        theme="a", rel="close")
      ns.db.event.calnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL('frm_tool/edit/event/')+str(row["id"]), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
    else:
      editable = True
      links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href=URL("cmd_export_ical?id="+str(row.id)), _target="_blank", _title=T("Export Item"))]
  
    if tool_audit_filter in ("readonly","disabled") or event_audit_filter in ("readonly","disabled"):
      gdeleted = False
      if session.mobile:
        response.cmd_event_new = ""
      else:
        response.cmd_event_new = SPAN(" ",SPAN(str(event_count), _class="detail_count"))
    else:
      if session.mobile:
        gdeleted = False
        response.cmd_event_new = ui.control.get_mobil_button(cmd_id="cmd_event_new",
          label=T("New Event"), href=URL("frm_event/new/event")+"?refnumber="+form.formname, 
          cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
      else:
        gdeleted = True
        response.cmd_event_new = ui.control.get_tabnew_button(event_count,T('New Event'),cmd_id="tabs-event",url=URL("frm_event/new/event")+"?refnumber="+form.formname)
    
    response.view_event = ui.select.get_tab_grid(_query=event, _field_id=ns.db.event.id, _fields=None, _deletable=gdeleted, links=links, _editable=editable,
                             multi_page="event_page", rpl_1="/frm_tool", rpl_2="/frm_tool/view/tool/"+str(tool_id),_priority="0,4")
  else:
    response.view_event = ""
    response.event_disabled=True
    response.menu_event = ""
  
  #trans data
  waybill_audit_filter = ui.connect.get_audit_filter("trans", "waybill")[0]
  if waybill_audit_filter!="disabled" and tool_id>-1:
    transtype_waybill = ns.valid.get_groups_id("transtype", "waybill")
    ns.db.movement.notes.label = T('Additional info')
    ns.db.movement.trans_id.label = T('Movement No.')
    query = ((ns.db.trans.deleted==0)&(ns.db.trans.id==ns.db.movement.trans_id)&(ns.db.movement.tool_id==tool_id)
             &(ns.db.trans.transtype==transtype_waybill))
    trans_count = ns.db(query).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if session.mobile:
      fields = [ns.db.trans.transnumber, ns.db.trans.direction,
                ns.db.movement.shippingdate,ns.db.tool.description,ns.db.trans.transtate]
      response.menu_trans = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Tool Movements"),trans_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('trans_page');",
        theme="a", rel="close")
      ns.db.trans.transnumber.represent = lambda value,row: ui.control.get_mobil_button(value, href=URL('frm_trans/edit/trans/')+str(row["id"]), 
                          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false", target="_blank")
    else:
      fields = [ns.db.movement.trans_id, ns.db.trans.crdate,ns.db.trans.direction,
                ns.db.movement.shippingdate,ns.db.tool.description,ns.db.movement.notes,
                ns.db.trans.transtate]
    if waybill_audit_filter!="all":
      gdeleted = False
      if session.mobile:
        response.cmd_waybill_new = ""
      else:
        response.cmd_waybill_new = SPAN(" ",SPAN(str(trans_count), _class="detail_count"))
    else:
      if session.mobile:
        gdeleted = False
        response.cmd_waybill_new = ui.control.get_mobil_button(label=T("New Movement"), 
          href=URL("frm_trans/new/trans/waybill/out"), target="_blank", 
          cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b")
      else:
        gdeleted = True
        response.cmd_waybill_new = ui.control.get_tabnew_button(trans_count,T('New Movement'),cmd_id="", 
                                      cmd="javascript:window.open('"+URL("frm_trans/new/trans/waybill/out")+"', '_blank');")
        
    response.view_trans = ui.select.get_tab_grid(query, ns.db.trans.id, _fields=fields, _deletable=False, _editable=False, links=None, 
                                          multi_page="trans_page", rpl_1="/frm_tool", rpl_2="/frm_tool/view/tool/"+str(tool_id),_priority="0,1")
  else:
    response.view_trans = ""
    response.waybill_disabled=True
        
  return dict(form=form)
  
@ns_auth.requires_login()
def frm_trans():
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/movement")>0 or ruri.find("view/movement")>0:
    movement_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.movement(id=movement_id).trans_id
    session["trans_page_"+str(trans_id)] = "movement_page"
    redirect(URL('frm_trans/view/trans/'+str(trans_id)))
    
  if ruri.find("delete/movement")>0:
    movement_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.movement(id=movement_id).trans_id
    session["trans_page_"+str(trans_id)] = "movement_page"
    if ns.connect.deleteData("movement", ref_id=movement_id):
      redirect(URL('frm_trans/view/trans/'+str(trans_id)))
  
  if request.post_vars["_formname"]=="movement/create":
    ui.connect.clear_post_vars()
    if not request.post_vars.has_key("shared"):
      request.post_vars["shared"]=0
    else:
      request.post_vars["shared"]=1
    if request.post_vars.has_key("target_place_id"):
      target_place_id = request.post_vars["target_place_id"]
      nervatype_movement_id = ns.valid.get_groups_id("nervatype", "movement")
      del request.post_vars["target_place_id"]
      place_id = request.post_vars["place_id"]
      del request.post_vars["place_id"]
    else:
      target_place_id=None
    if ns.db.groups(id=ns.db.trans(id=request.post_vars["trans_id"]).transtype).groupvalue == "production":
      request.post_vars["qty"] = -float(request.post_vars["qty"])
    
    row_id = ns.connect.updateData("movement", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      if target_place_id:
        links = ns.db((ns.db.link.ref_id_2==row_id)&(ns.db.link.nervatype_1==nervatype_movement_id)
                      &(ns.db.link.deleted==0)&(ns.db.link.nervatype_2==nervatype_movement_id)).select()
        if len(links)>0:
          values = {"id":links[0].ref_id_1, "product_id":request.post_vars.product_id,
                    "qty":-float(request.post_vars.qty),"notes":request.post_vars.notes}
          row_id = ns.connect.updateData("movement", values=values, validate=False, insert_row=True)
        else:
          values = {"trans_id":request.post_vars.trans_id,"shippingdate":request.post_vars.shippingdate,
                    "movetype":request.post_vars.movetype,"product_id":request.post_vars.product_id,
                    "qty":request.post_vars.qty,"notes":request.post_vars.notes}
          target_id = ns.connect.updateData("movement", values=values, validate=False, insert_row=True)
          values = {"id":row_id,"qty":-float(request.post_vars.qty)}
          row_id = ns.connect.updateData("movement", values=values, validate=False, insert_row=True)
          values = {"nervatype_1":nervatype_movement_id, "ref_id_1":row_id, 
                    "nervatype_2":nervatype_movement_id, "ref_id_2":target_id}
          ns.connect.updateData("link", values=values, validate=False, insert_row=True)
        
        if len(ns.db((ns.db.movement.trans_id==request.post_vars["trans_id"])&(ns.db.link.deleted==0)).select())>0:
          links = ns.db((ns.db.link.ref_id_1.belongs(ns.db(ns.db.movement.trans_id==request.post_vars["trans_id"]
                                                           ).select(ns.db.movement.id)))
                        &(ns.db.link.nervatype_1==nervatype_movement_id)&(ns.db.link.deleted==0)
                        &(ns.db.link.nervatype_2==nervatype_movement_id)).select()
          for link in links:
            ns.connect.updateData("movement", values={"id":link.ref_id_1,"place_id":place_id}, validate=False, insert_row=True)
            ns.connect.updateData("movement", values={"id":link.ref_id_2,"place_id":target_place_id}, validate=False, insert_row=True)
      session["trans_page_"+str(request.post_vars["trans_id"])] = "movement_page"
      redirect()
  
  if ruri.find("edit/item")>0 or ruri.find("view/item")>0:
    item_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.item(id=item_id).trans_id
    session["trans_page_"+str(trans_id)] = "item_page"
    redirect(URL('frm_trans/view/trans/'+str(trans_id)))
        
  if ruri.find("delete/item")>0:
    item_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.item(id=item_id).trans_id
    session["trans_page_"+str(trans_id)] = "item_page"
    if ns.connect.deleteData("item", ref_id=item_id):
      redirect(URL('frm_trans/view/trans/'+str(trans_id)))
  
  if request.post_vars["_formname"]=="item/create":
    ui.connect.clear_post_vars()
    if request.post_vars.has_key("digit"):
      del request.post_vars["digit"]
    if request.post_vars.has_key("rate"):
      del request.post_vars["rate"]
    if not request.post_vars.has_key("deposit"):
      request.post_vars["deposit"]=0
    else:
      request.post_vars["deposit"]=1
    row_id = ns.connect.updateData("item", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["trans_page_"+str(request.post_vars["trans_id"])] = "item_page"
      redirect()
  
  if ruri.find("edit/payment")>0 or ruri.find("view/payment")>0:
    payment_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.payment(id=payment_id).trans_id
    session["trans_page_"+str(trans_id)] = "payment_page"
    redirect(URL('frm_trans/view/trans/'+str(trans_id)))
    
  if ruri.find("delete/payment")>0:
    payment_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.payment(id=payment_id).trans_id
    session["trans_page_"+str(trans_id)] = "payment_page"
    if ns.connect.deleteData("payment", ref_id=trans_id):
      redirect(URL('frm_trans/view/trans/'+str(trans_id)))
        
  if request.post_vars["_formname"]=="payment/create":
    ui.connect.clear_post_vars()
    row_id = ns.connect.updateData("payment", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["trans_page_"+str(request.post_vars["trans_id"])] = "payment_page"
      redirect()    
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["trans_page_"+str(trans_id)] = "fieldvalue_page"
    redirect(URL('frm_trans/view/trans/'+str(trans_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    session["trans_page_"+str(trans_id)] = "fieldvalue_page"
    if ns.connect.deleteData("fieldvalue", ref_id=fieldvalue_id):
      redirect(URL('frm_trans/view/trans/'+str(trans_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    ui.connect.clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    row_id = ns.connect.updateData("fieldvalue", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["trans_page_"+str(request.post_vars["ref_id"])] = "fieldvalue_page"
      redirect()
  
  if ruri.find("delete/link")>0:
    link_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if ns.connect.deleteData("link", ref_id=link_id):
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(ruri[:ruri.find("delete/link")-1])
  
  if request.post_vars["_formname"]=="link/create":
    ui.connect.clear_post_vars()
    if request.post_vars.has_key("trans_id"):
      trans_id = request.post_vars["trans_id"]
      del request.post_vars["trans_id"]
    if request.post_vars.has_key("amount"):
      amount = request.post_vars["amount"]
      del request.post_vars["amount"]
    if request.post_vars.has_key("rate"):
      rate = request.post_vars["rate"]
      del request.post_vars["rate"]
    request.post_vars["link_qty"]=amount
    request.post_vars["link_rate"]=rate
    row_id = ns.connect.updateData("link", values=request.post_vars, validate=False, insert_row=True)
    if not row_id:
      response.flash = str(ns.error_message)
    else:
      session["trans_page_"+str(request.post_vars["trans_id"])] = "link_page"
      redirect()
          
  if ruri.find("new/link")>0:
    trans_id = int(request.vars.refnumber)
    trans_nervatype = ns.valid.get_groups_id("nervatype", "trans")
    groups_id = int(request.vars.groups_id)
    groups_nervatype = ns.valid.get_groups_id("nervatype", "groups")
    glink = ns.db((ns.db.link.ref_id_1==trans_id)&(ns.db.link.nervatype_1==trans_nervatype)&(ns.db.link.deleted==0)
              &(ns.db.link.nervatype_2==groups_nervatype)&(ns.db.link.ref_id_2==groups_id)).select().as_list()
    if len(glink)==0:
      values = {"nervatype_1":trans_nervatype, "ref_id_1":trans_id, "nervatype_2":groups_nervatype, "ref_id_2":groups_id}
      ns.connect.updateData("link", values=values, validate=False, insert_row=True)
    session["trans_page_"+str(trans_id)] = "groups_page"
    redirect(URL('frm_trans/view/trans/'+str(trans_id)))
  
  transtype=""
  direction="out"
  transcast="normal"
  if ruri.find("new/trans")>0:
    trans_id = -1
    sruri = ruri.split("/")
    for i in range(len(sruri)):
      if sruri[i]=="trans":
        transtype = sruri[i+1].split("?")[0]
        direction = sruri[i+2].split("?")[0]
        break
  else:
    trans_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    transtype = ns.db.groups(id=ns.db.trans(id=trans_id).transtype).groupvalue
    direction = ns.db.groups(id=ns.db.trans(id=trans_id).direction).groupvalue
    if ns.db.trans(id=trans_id).deleted==1 and transtype not in("invoice","receipt","cash"):
      return ui.connect.show_disabled(response.title)
  
  nervatype_trans = ns.valid.get_groups_id("nervatype", "trans")
  nervatype_groups = ns.valid.get_groups_id("nervatype", "groups")
  transtype_id = ns.valid.get_groups_id("transtype", transtype)
  direction_id = ns.valid.get_groups_id("direction", direction)
  transtype_audit_filter = ui.connect.get_audit_filter("trans", transtype)
  setting_audit_filter = ui.connect.get_audit_filter("setting", None)[0]
  
  if transtype_audit_filter[0]=="disabled":
    return ui.connect.show_disabled(response.title)
  
  if ruri.find("close/trans")>0:
    row_id = ns.connect.updateData("trans", values={"id":trans_id,"closed":1}, validate=False, insert_row=True)
    if row_id:
      redirect(URL('frm_trans/view/trans/'+str(trans_id)))
    else:
      response.flash = str(ns.error_message)
    
  if ruri.find("delete/trans")>0:
    if not ns.connect.deleteData("trans", ref_id=trans_id):
      session.flash = str(ns.error_message)
      redirect(URL('frm_trans/view/trans/'+str(trans_id)))
    else:
      if transtype in("invoice","receipt","cash"):
        redirect(URL('frm_trans/view/trans/'+str(trans_id)))
      else:
        redirect(URL('index'))
  
  #basic trans data
  ns.db.trans.id.readable = ns.db.trans.id.writable = False
  ns.db.trans.deleted.readable = ns.db.trans.deleted.writable = False
  ns.db.trans.customer_id.writable = False
  ns.db.trans.employee_id.writable = False
  ns.db.trans.project_id.writable = False

  response.subtitle=""
  response.transtype_name = transtype
  if not session.mobile:
    response.lo_menu = []
    response.icon_corrected = IMG(_src=URL(ui.dir_images,'icon16_corrected.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_deffield = IMG(_src=URL(ui.dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_money = IMG(_src=URL(ui.dir_images,'icon16_money.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_invoice = IMG(_src=URL(ui.dir_images,'icon16_invoice.png'),_style="vertical-align: top;",_height="16px",_width="16px")
    response.icon_lorry = IMG(_src=URL(ui.dir_images,'icon16_lorry.png'),_style="vertical-align: middle;",_height="16px",_width="16px")
    response.icon_wrench_page = IMG(_src=URL(ui.dir_images,'icon16_wrench_page.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  if transtype in("offer"):
    response.view=ui.dir_view+'/trans_item.html'
    response.tcolor='#B8860B'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_offer.png')
    if direction=="out":
      response.subtitle=response.subtitle+T('CUSTOMER OFFER')
    else:
      response.subtitle=response.subtitle+T('SUPPLIER OFFER')
    ns.db.trans.duedate.label = T('Valid Date')
    ns.db.trans.acrate.label = T('Paym.days')
    ns.db.trans.paid.label = T('Released')
    ns.db.item.deposit.label = T('Option')
    ns.db.trans.transnumber.label = T('Offer No.')
    ns.db.trans.transdate.label = T('Offer Date')
  
  if transtype in("order"):
    response.view=ui.dir_view+'/trans_item.html'
    response.tcolor='#228B22'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_order.png')
    if direction=="out":
      response.subtitle=response.subtitle+T('CUSTOMER ORDER')
    else:
      response.subtitle=response.subtitle+T('SUPPLIER ORDER')
    ns.db.trans.duedate.label = T('Delivery Date')
    ns.db.trans.acrate.label = T('Paym.days')
    ns.db.trans.paid.label = T('Released')
    ns.db.item.deposit.readable = ns.db.item.deposit.writable = False
    ns.db.trans.transnumber.label = T('Order No.')
    ns.db.trans.transdate.label = T('Order Date') 
  
  if transtype in("cash"):
    response.view=ui.dir_view+'/trans_payment.html'
    response.tcolor='#FF8C00'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_cashregister.png')
    response.subtitle=response.subtitle+T('CASH')
    ns.db.trans.place_id.label = T("Cash desk")
    ns.db.trans.transdate.label = T("Payment Date")
    ns.db.trans.direction.requires = IS_IN_DB(ns.db(((ns.db.groups.groupname.like('direction'))&(ns.db.groups.groupvalue=="in")) | 
                                     ((ns.db.groups.groupname.like('direction'))&(ns.db.groups.groupvalue=="out"))), ns.db.groups.id, '%(groupvalue)s')
      
  if transtype in("bank"):
    response.view=ui.dir_view+'/trans_payment.html'
    response.tcolor='#FF8C00'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_money.png')
    response.subtitle=response.subtitle+T('BANK STATEMENT')
    ns.db.trans.place_id.label = T("Account No.")
    ns.db.trans.transdate.label = T("Acc.Date")
  
  if transtype in("production"):
    response.view=ui.dir_view+'/trans_movement.html'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_production.png')
    response.subtitle=response.subtitle+T('PRODUCTION')
    ns.db.trans.place_id.label = T("Warehouse")
    ns.db.trans.transdate.label = T("Start Date")
    ns.db.trans.duedate.label = T('End Date')
    movetype_inventory = ns.valid.get_groups_id("movetype", "inventory")
    
  if transtype in("formula"):
    response.view=ui.dir_view+'/trans_movement.html'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_formula.png')
    response.subtitle=response.subtitle+T('FORMULA')
    if len(ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="head")).select())>0:
      movetype_head = ns.valid.get_groups_id("movetype", "head")
    else:
      movetype_head = ns.connect.updateData("groups", values={"groupname":"movetype","groupvalue":"head"}, validate=False, insert_row=True)
        
  if transtype in("inventory"):
    response.view=ui.dir_view+'/trans_movement.html'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_lorry_error.png')
    response.subtitle=response.subtitle+T('CORRECTION')
    ns.db.trans.place_id.label = T("Warehouse")
    ns.db.trans.transdate.label = T("Inv.Date")
  
  if transtype in("delivery") and direction=="transfer":
    response.view=ui.dir_view+'/trans_movement.html'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_lorry_go.png')
    response.subtitle=response.subtitle+T('TRANSFER')
    ns.db.trans.place_id.label = T("Warehouse")
    ns.db.trans.transdate.label = T("Trans.Date")
  
  if transtype in("delivery") and direction!="transfer":
    response.view=ui.dir_view+'/trans_movement.html'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_lorry_go.png')
    response.subtitle=response.subtitle+T('SHIPPING')+" "+T(direction.upper())
    ns.db.trans.place_id.label = T("Warehouse")
    ns.db.trans.transdate.label = T("Shipping")
    response.direction = direction
      
  if transtype in("worksheet"):
    response.view=ui.dir_view+'/trans_item.html'
    response.tcolor='#8470FF'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_worksheet.png')
    response.subtitle=response.subtitle+T('WORKSHEET')
    ns.db.trans.transdate.label = T('Start Date')
    ns.db.trans.duedate.label = T('End Date')
    ns.db.trans.acrate.label = T('Paym.days')
    ns.db.trans.paid.label = T('Released')
    ns.db.item.deposit.readable = ns.db.item.deposit.writable = False
    ns.db.trans.transnumber.label = T('Worksheet No.')
    
    trans_wsdistance = ui.connect.get_formvalue(fieldname="trans_wsdistance",table="fieldvalue",ref_id=trans_id,default="0",isempty=False)
    trans_wsrepair = ui.connect.get_formvalue(fieldname="trans_wsrepair",table="fieldvalue",ref_id=trans_id,default="0",isempty=False)
    trans_wstotal = ui.connect.get_formvalue(fieldname="trans_wstotal",table="fieldvalue",ref_id=trans_id,default="0",isempty=False)
    trans_wsnote = ui.connect.get_formvalue(fieldname="trans_wsnote",table="fieldvalue",ref_id=trans_id,default="",isempty=True)
    
  if transtype in("rent"):
    response.view=ui.dir_view+'/trans_item.html'
    response.tcolor='#A52A2A'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_rent.png')
    if direction=="out":
      response.subtitle=response.subtitle+T('CUSTOMER RENTAL')
    else:
      response.subtitle=response.subtitle+T('SUPPLIER RENTAL')
    ns.db.trans.transdate.label = T('Start Date')
    ns.db.trans.duedate.label = T('End Date')
    ns.db.trans.acrate.label = T('Paym.days')
    ns.db.trans.paid.label = T('Released')
    ns.db.item.deposit.readable = ns.db.item.deposit.writable = False
    ns.db.trans.transnumber.label = T('Contract No.')
    
    trans_reholiday = ui.connect.get_formvalue(fieldname="trans_reholiday",table="fieldvalue",ref_id=trans_id,default="0",isempty=False)
    trans_rebadtool = ui.connect.get_formvalue(fieldname="trans_rebadtool",table="fieldvalue",ref_id=trans_id,default="0",isempty=False)
    trans_reother = ui.connect.get_formvalue(fieldname="trans_reother",table="fieldvalue",ref_id=trans_id,default="0",isempty=False)
    trans_rentnote = ui.connect.get_formvalue(fieldname="trans_rentnote",table="fieldvalue",ref_id=trans_id,default="",isempty=True)
              
  if transtype in("invoice"):
    response.view=ui.dir_view+'/trans_item.html'
    response.tcolor='#2F4F4F'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_invoice.png')
    if direction=="out":
      response.subtitle=response.subtitle+T('CUSTOMER INVOICE')
    else:
      response.subtitle=response.subtitle+T('SUPPLIER INVOICE')
    ns.db.trans.transnumber.label = T('Invoice No.')
    ns.db.trans.transdate.label = T('Invoice Date')
  
  if transtype in("receipt"):
    response.view=ui.dir_view+'/trans_item.html'
    response.tcolor='#2F4F4F'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_invoice.png')
    if direction=="out":
      response.subtitle=response.subtitle+T('CUSTOMER RECEIPT')
    else:
      response.subtitle=response.subtitle+T('SUPPLIER RECEIPT')
    ns.db.trans.transnumber.label = T('Receipt No.')
    ns.db.trans.transdate.label = T('Receipt Date')
            
  if transtype in("offer", "order","worksheet","rent","invoice","receipt"):   
    if request.post_vars.has_key("duedate"):
      if request.post_vars["duedate"]!="":
        request.post_vars["duedate"] += " 00:00:00"
    request.post_vars["acrate"] = ui.connect.get_formvalue(fieldname="acrate",table="trans",ref_id=trans_id,default="0",isempty=False)
    ns.db.trans.curr.requires = IS_IN_DB(ns.db(ns.db.currency), ns.db.currency.curr, '%(curr)s')
    ns.db.trans.paidtype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('paidtype')), ns.db.groups.id, '%(groupvalue)s')
    
  if transtype in("waybill"):
    response.subtitle=response.subtitle+T('TOOL MOVEMENT')
    ns.db.trans.direction.requires = IS_IN_DB(ns.db(((ns.db.groups.groupname.like('direction'))&(ns.db.groups.groupvalue=="in")) | 
                                                    ((ns.db.groups.groupname.like('direction'))&(ns.db.groups.groupvalue=="out"))), ns.db.groups.id, '%(groupvalue)s')
  
  if transtype_audit_filter[1]==0:
    ns.db.trans.transtate.writable = False
  
  if trans_id>0:
    form = SQLFORM(ns.db.trans, record = trans_id, submit_button=T("Save"), _id="frm_trans")
    form.vars.transnumber=response.transnumber=ns.db.trans(id=trans_id).transnumber
    response.closed=ns.db.trans(id=trans_id).closed
    response.deleted=ns.db.trans(id=trans_id).deleted
    
    form.vars.transtype = ns.db.trans(id=trans_id).transtype
    form.vars.crdate = ns.db.trans(id=trans_id).crdate
    form.vars.duedate = ns.db.trans(id=trans_id).duedate
    form.vars.cruser_id = ns.db.trans(id=trans_id).cruser_id
    
    translink = ns.db((ns.db.link.ref_id_1==trans_id)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0)
              &(ns.db.link.nervatype_2==nervatype_trans)).select().as_list()
    if len(translink)>0:
      lnk_transnumber_id=str(translink[0]["ref_id_2"])
      lnk_transnumber = ns.db.trans(id=lnk_transnumber_id).transnumber
      ref_transnumber =""
    else:
      lnk_transnumber_id=""
      lnk_transnumber = ""
      ref_transnumber = ns.db.trans(id=trans_id).ref_transnumber
    
    response.cmd_report = ui.control.get_report_button(nervatype="trans", title=response.subtitle, ref_id=trans_id,
                                              label=form.vars.transnumber, 
                                              transtype=transtype, direction=direction)
    if session.mobile:
      response.cmd_fnote = ui.control.get_mobil_button(label=T("Document notes"), href="#", 
        icon="chat", cformat=None, ajax="false", theme="b", rel="close",
        onclick= "if(confirm('"+T('Any unsaved changes will be lost. Do you want to continue?')+
          "')){window.location ='"+URL("frm_trans_fnote/"+str(trans_id))+"';};return false;")
    else:
      response.cmd_fnote = ui.control.get_command_button(caption=T("Report notes"),title=T("Report notes"),color="483D8B",
                              cmd="if(confirm('"+T('Any unsaved changes will be lost. Do you want to continue?')+
                              "')){window.location ='"+URL("frm_trans_fnote/"+str(trans_id))+"';};return false;")
    if transtype_audit_filter[0]=="all":
      if session.mobile:
        response.cmd_delete = ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="trash", style="text-align: left;",
          onclick="if(confirm('"+T('Are you sure you want to delete this document?')+
            "')){window.location ='"+URL("frm_trans/delete/trans/"+str(trans_id))+"';};return false;", theme="b")
        response.cmd_trans_close = ui.control.get_mobil_button(label=T("Closing data"), href="#", 
          icon="lock", cformat=None, ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to close this document?')+
            "')){window.location ='"+URL("frm_trans/close/trans/"+str(trans_id))+"';};return false;")
        response.cmd_copy = ui.control.get_mobil_button(label=T("Copy from"), href="#", 
          icon="plus", cformat=None, ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to copy this document?')+
            "')){copy_trans('"+URL("cmd_trans_copy")+"?trans_id="+str(trans_id)
            +"','"+URL("frm_trans/view/trans")+"/')};return false;")
        
        if transtype in("offer","order","worksheet","rent","invoice","receipt"):
          response.cmd_create = ui.control.get_create_trans_button(trans_id=trans_id)
        else:
          response.cmd_create = ""
        
        response.cmd_cancellation = ui.control.get_mobil_button(label=T("Cancellation"), href="#", 
          icon="plus", cformat=None, ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to copy this document?')+
            "')){copy_trans('"+URL("cmd_trans_cancel")+"?trans_id="+str(trans_id)
            +"','"+URL("frm_trans/view/trans/")+"/')};return false;")
        response.cmd_corrective = ui.control.get_mobil_button(label=T("Corrective"), href="#", 
          icon="plus", cformat=None, ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to copy this document?')+
            "')){copy_trans('"+URL("cmd_trans_corr")+"?trans_id="+str(trans_id)
            +"','"+URL("frm_trans/view/trans")+"/')};return false;")
        response.cmd_more = ui.control.get_popup_cmd(pop_id="popup_more_cmd",
                              label=T("More commands"),theme="b",picon="forward") 
      else:
        response.cmd_delete = ui.control.get_command_button(caption=T("Delete"),title=T("Delete"),color="A52A2A",
                                cmd="if(confirm('"+T('Are you sure you want to delete this document?')+
                                "')){window.location ='"+URL("frm_trans/delete/trans/"+str(trans_id))+"';};return false;")
        response.cmd_close = ui.control.get_command_button(caption=T("Closing data"),title=T("Closing data"),color="8B4513",
                                cmd="if(confirm('"+T('Are you sure you want to close this document?')+
                                "')){window.location ='"+URL("frm_trans/close/trans/"+str(trans_id))+"';};return false;")
        response.cmd_copy = ui.control.get_command_button(caption=T("Copy from"),title=T("Copy a document from existing"),
                                cmd="if(confirm('"+T('Are you sure you want to copy this document?')+
                                "')){copy_trans('"+URL("cmd_trans_copy")+"?trans_id="+str(trans_id)
                                +"','"+URL("frm_trans/view/trans")+"/')};return false;")
        
        response.cmd_create = DIV(INPUT(_type="button", _value=T("Create from"), _title=T("Create a new document type"), 
                                        _style="height: 25px !important;padding-top: 2px !important;color: #B8860B;width: 100%;", 
                                        _onclick='$("#popup_create_trans").dialog({dialogClass: "n2py-dialog", modal: true, minWidth: 440, resizable: false});'),
                                  DIV(ui.select.dlg_create_trans(trans_id), _id="popup_create_trans", _title=T("Create a new document type"), 
                                      _style="display: none;"))
        
        response.cmd_cancellation = ui.control.get_command_button(caption=T("Cancellation"),title=T("Create a cancellation invoice"),color="F08080",
                                cmd="if(confirm('"+T('Are you sure you want to copy this document?')+
                                "')){copy_trans('"+URL("cmd_trans_cancel")+"?trans_id="+str(trans_id)
                                +"','"+URL("frm_trans/view/trans/")+"/')};return false;")
        response.cmd_corrective = ui.control.get_command_button(caption=T("Corrective"),title=T("Create a corrective invoice"),color="F08080",
                                cmd="if(confirm('"+T('Are you sure you want to copy this document?')+
                                "')){copy_trans('"+URL("cmd_trans_corr")+"?trans_id="+str(trans_id)
                                +"','"+URL("frm_trans/view/trans")+"/')};return false;")
        response.cmd_more = ui.control.get_more_button()             
    else:
      response.cmd_delete = ""
      response.cmd_close = ""
      response.cmd_copy = ""
      response.cmd_create = ""
      response.cmd_cancellation = ""
      response.cmd_corrective = ""
      response.cmd_more = ""
  else:
    form = SQLFORM(ns.db.trans, submit_button=T("Save"), _id="frm_trans")
    response.subtitle=T('NEW ')+response.subtitle
    response.transnumber = ""
    response.closed=0
    response.deleted=0
    if request.vars.init_refnumber_id!=None:
      lnk_transnumber_id = request.vars.init_refnumber_id
      lnk_transnumber = ns.db.trans(id=int(request.vars.init_refnumber_id)).transnumber
    else:
      lnk_transnumber_id = ""
      lnk_transnumber = ""
    ref_transnumber = ""
    
    response.cmd_report = ""
    response.cmd_delete = ""
    response.cmd_fnote = ""
    response.cmd_close = ""
    response.cmd_copy = ""
    response.cmd_create = ""
    response.cmd_cancellation = ""
    response.cmd_corrective = ""
    response.cmd_more = ""
    
    if transtype=="waybill" or transtype=="cash":
      form.vars.transnumber = ns.connect.nextNumber(transtype,False)
    else:
      form.vars.transnumber = ns.connect.nextNumber(transtype+"_"+direction,False)
    form.vars.transtype = transtype_id
    form.vars.direction = direction_id
    form.vars.crdate = datetime.datetime.now().date()
    form.vars.transdate = datetime.datetime.now().date()
    form.vars.duedate = datetime.datetime.strptime(str(datetime.date.today())+" 00:00:00", str('%Y-%m-%d %H:%M:%S'))
    form.vars.transtate = ns.valid.get_groups_id("transtate", "ok")
    form.vars.cruser_id = session.auth.user.id
    if transtype in("offer","order","worksheet","rent","invoice","receipt"):
      form.vars.curr = ns.connect.getSetting("default_currency")
      paidtype=ns.connect.getSetting("default_paidtype")
      if paidtype!="":
        form.vars.paidtype = ns.valid.get_groups_id("paidtype", paidtype)
    if transtype in("invoice"):
      if direction=="out":
        deadline=ns.connect.getSetting("default_deadline")
        if deadline!="":
          form.vars.duedate += datetime.timedelta(int(deadline))
  
  if session.mobile:
    if request.vars.has_key("back_url"):
      response.cmd_back = ui.control.get_mobil_button(
        label=T("BACK"), href=ruri[ruri.find("back_url=")+9:], icon="back", cformat="ui-btn-left", ajax="false")
    else:
      if transtype in("offer","order","worksheet","rent","invoice","receipt"):
        response.cmd_back = ui.control.get_mobil_button(
          label=T("SEARCH"), href=URL('find_transitem_trans'), icon="search", cformat="ui-btn-left", ajax="false")
      elif transtype=="waybill":
        response.cmd_back = ui.control.get_mobil_button(
          label=T("SEARCH"), href=URL('find_movement_tool'), icon="search", cformat="ui-btn-left", ajax="false")
      elif transtype in("cash", "bank"):
        response.cmd_back = ui.control.get_mobil_button(
          label=T("SEARCH"), href=URL('find_payment_payment'), icon="search", cformat="ui-btn-left", ajax="false")
      elif transtype in("inventory", "delivery","production"):
        response.cmd_back = ui.control.get_mobil_button(
          label=T("SEARCH"), href=URL('find_movement_product'), icon="search", cformat="ui-btn-left", ajax="false")
      elif transtype in("formula"):
        response.cmd_back = ui.control.get_mobil_button(
          label=T("SEARCH"), href=URL('find_movement_formula'), icon="search", cformat="ui-btn-left", ajax="false")
      else:
        response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
                                               icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
  
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page='+transtype),
                                               cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
    
    response.cmd_next = ui.control.get_mobil_button(label=T("NEXT"), 
      href=ui.connect.get_next_lnk(transtype,trans_id,direction), 
      ajax="false", cformat=None, icon="arrow-r", iconpos="right", theme="a", style="text-align: right;")
    response.cmd_prev = ui.control.get_mobil_button(label=T("PREVIOUS"), 
      href=ui.connect.get_prev_lnk(transtype,trans_id,direction), 
      ajax="false", cformat=None, icon="arrow-l", iconpos="left", theme="a")
  else:
    if request.vars.has_key("back_url"):
      response.cmd_back = ui.control.get_back_button(ruri[ruri.find("back_url=")+9:])
    else:
      if transtype in("offer","order","worksheet","rent","invoice","receipt"):
        response.cmd_back = ui.control.get_back_button(URL('find_transitem_trans'))
      elif transtype=="waybill":
        response.cmd_back = ui.control.get_back_button(URL('find_movement_tool'))
      elif transtype in("cash", "bank"):
        response.cmd_back = ui.control.get_back_button(URL('find_payment_payment'))
      elif transtype in("inventory", "delivery","production"):
        response.cmd_back = ui.control.get_back_button(URL('find_movement_product'))
      elif transtype in("formula"):
        response.cmd_back = ui.control.get_back_button(URL('find_movement_formula'))
      else:
        response.cmd_back = ui.control.get_home_button()
  
    response.cmd_help = ui.control.get_help_button(transtype)
    
    next_url = ui.connect.get_next_lnk(transtype,trans_id,direction)
    prev_url = ui.connect.get_prev_lnk(transtype,trans_id,direction)
    
    response.cmd_next = A(DIV(SPAN(_class="icon rightarrow"), _align="center", 
                              _style="height: 20px;width:24px;background-color:#A9A9A9;vertical-align: middle;border-radius: 4px;padding-left:2px;padding-top:1px;"), 
                          _style="height: 100%;width: 20px;padding-left: 8px;padding-top: 8px;", 
                          _class="w2p_trap buttontext button", _title=T('NEXT'), _href=next_url)
    response.cmd_prev = A(DIV(SPAN(_class="icon leftarrow"), _align="center", 
                              _style="height: 20px;width:24px;background-color:#A9A9A9;vertical-align: middle;border-radius: 4px;padding-left:2px;padding-top:1px;"), 
                          _style="height: 100%;width: 20px;padding-left: 8px;padding-top: 8px;", 
                          _class="w2p_trap buttontext button", _title=T('PREVIOUS'), _href=prev_url)
  
  customer_audit_filter = ui.connect.get_audit_filter("customer", None)[0]
  employee_audit_filter = ui.connect.get_audit_filter("employee", None)[0]
  product_audit_filter = ui.connect.get_audit_filter("product", None)[0]
    
  if form.validate(keepvalues=True):
    check_ok=True
    if transtype in("offer","order","worksheet","rent","invoice"):
      if request.post_vars.customer_id=="":
        response.customer_control = ui.select.get_customer_selector(T('Missing customer!'), error_label=True)
        response.flash = T('Missing customer!')
        check_ok=False
      else:
        form.vars.customer_id=request.post_vars.customer_id
    if transtype in("offer","order","worksheet","rent","invoice","receipt"):
      if request.post_vars.project_id!="":
        form.vars.project_id=request.post_vars.project_id
      else:
        form.vars.project_id=""
        
    if transtype in("offer","order","worksheet","rent","invoice","cash","receipt"):    
      if request.post_vars.employee_id!="":
        form.vars.employee_id=request.post_vars.employee_id
      else:
        form.vars.employee_id=""
        
    if transtype in("offer","order","worksheet","rent","invoice","cash","bank","inventory","production","formula","receipt") \
      or (transtype=="delivery" and direction=="transfer"):    
      if request.post_vars.trans_id!="":
        form.vars["ref_transnumber"]=ns.db.trans(id=int(request.post_vars.trans_id)).transnumber
        lnk_transnumber_id=request.post_vars.trans_id
        lnk_transnumber = form.vars["ref_transnumber"]
        ref_transnumber =""
      else:
        lnk_transnumber_id=""
        lnk_transnumber = ""
        ref_transnumber = request.post_vars.ref_transnumber
    
    if transtype in("inventory","cash","bank","production") or (transtype=="delivery" and direction=="transfer"):
      if request.post_vars.place_id=="":
        if transtype=="cash":
          response.place_control = ui.select.get_place_selector(T('Missing cash desk!'), error_label=True, placetype="dlg_place_cash",title=T("Select Cash desk"))
          response.flash = T('Missing cash desk!')
        elif transtype=="bank":
          response.place_control = ui.select.get_place_selector(T('Missing bank account!'), error_label=True, placetype="dlg_place_bank",title=T("Select account"))
          response.flash = T('Missing bank account!')
        elif transtype=="production":
          response.production_place_selector = ui.select.get_base_selector(fieldtype="place", search_url="dlg_place_warehouse",
                          label_id="production_place_label", 
                          label_url="'"+URL("frm_place/view/place")+"/'+document.getElementById('production_place_id').value",
                          label_txt=T('Missing warehouse!'),
                          value_id="production_place_id", error_label=True)
          response.flash = T('Missing warehouse!')
        else:
          response.place_control = ui.select.get_place_selector(T('Missing warehouse!'), error_label=True, placetype="dlg_place_warehouse",title=T("Select warehouse"))
          response.flash = T('Missing warehouse!')
        check_ok=False
      else:
        form.vars.place_id=request.post_vars.place_id
        
    if transtype=="waybill":
      if request.post_vars.refnumber_type=="trans":
        if request.post_vars.trans_id=="":
          response.trans_transnumber = ui.select.get_base_selector(fieldtype="transitem", search_url=URL("dlg_transitem_all"), 
            label_id="reftrans_transnumber", label_url="", label_txt=T('Missing reference number!'), 
            value_id="trans_id", error_label=True, div_id="fld_trans_transnumber")
          response.flash = T('Missing reference number!')
          check_ok=False
        else:
          form.vars["ref_transnumber"]=ns.db.trans(id=int(request.post_vars.trans_id)).transnumber
          form.vars["customer_id"]=None
          form.vars["employee_id"]=None
      elif request.post_vars.refnumber_type=="customer":
        if request.post_vars.customer_id=="":
          if customer_audit_filter!="disabled":
            response.customer_custname = ui.select.get_base_selector(fieldtype="customer", search_url=URL("dlg_customer"), 
              label_id="customer_custname", label_url="", label_txt=T('Missing customer!'), 
              value_id="customer_id", error_label=True, div_id="fld_customer_custname")
          else:
            response.customer_custname=DIV(
                                   SPAN(T('Missing customer!'), _id="customer_custname"), 
                                   _class="label_error", _id="fld_customer_custname", _style="display:block;")
          response.flash = T('Missing customer!')
          check_ok=False
        else:
          form.vars["customer_id"]=request.post_vars.customer_id
          form.vars["ref_transnumber"]=None
          form.vars["employee_id"]=None
      elif request.post_vars.refnumber_type=="employee":
        if request.post_vars.employee_id=="":
          if employee_audit_filter!="disabled":
            response.employee_empnumber = ui.select.get_base_selector(fieldtype="employee", search_url=URL("dlg_employee"), 
              label_id="employee_empnumber", label_url="", label_txt=T('Missing employee!'), 
              value_id="employee_id", error_label=True, div_id="fld_employee_empnumber")
          else:
            response.employee_empnumber=DIV(
                                   SPAN(T('Missing employee!'), _id="employee_empnumber"), 
                                   _class="label_error", _id="fld_employee_empnumber", _style="display:block;")
          response.flash = T('Missing employee!')
          check_ok=False
        else:
          form.vars["employee_id"]=request.post_vars.employee_id
          form.vars["ref_transnumber"]=None
          form.vars["customer_id"]=None
          
    if transtype in("production","formula"):
      production_qty = ui.connect.get_formvalue(fieldname="production_qty",default="0",isempty=False)
      if request.post_vars.product_id=="":
        if product_audit_filter!="disabled":
          response.production_product_selector = ui.select.get_base_selector(
            fieldtype="product", search_url=URL("dlg_product_item"),
            label_id="production_product_label",
            label_url="'"+URL("frm_product/view/product")+"/'+document.getElementById('production_product_id').value",
            label_txt=T('Missing product!'),value_id="production_product_id",width="100%",error_label=True)
        else:
          response.production_product_selector=DIV(
                                   SPAN(T('Missing product!'), _id="production_product_label"), 
                                   _class="label_error", _id="production_product_id", _style="display:block;")
        response.flash = T('Missing product!')
        check_ok=False
      else:
        product_id=request.post_vars.product_id
        
    if transtype=="production":
      if request.post_vars.duedate=="":
        form.errors["duedate"] = T("enter date as 1963-08-28")
        response.flash = T('Missing Start Date!')
        check_ok=False
        
    if check_ok==True:
      
      if trans_id==-1:
        if transtype=="waybill" or transtype=="cash":
          nextnumber_id = transtype
        else:
          nextnumber_id = transtype+"_"+direction
        nextnumber = ns.connect.nextNumber(nextnumber_id,False)
        if form.vars.transnumber == nextnumber:
          form.vars.transnumber = ns.connect.nextNumber(nextnumber_id)
        plst = ns.db((ns.db.pattern.deleted==0)&(ns.db.pattern.defpattern==1)
                     &(ns.db.pattern.transtype==form.vars.transtype)).select()
        if len(plst)>0:
          form.vars.fnote = plst[0]["notes"]
        form.vars.trans_transcast = transcast
      else:
        form.vars["id"]=trans_id
        if form.vars.has_key("fnote"):
          del form.vars["fnote"]
      
      #insert/update all additional data (from header)
      if transtype in("worksheet"):  
        form.vars.trans_wsdistance = trans_wsdistance
        form.vars.trans_wsrepair = trans_wsrepair
        form.vars.trans_wstotal = trans_wstotal
        form.vars.trans_wsnote = trans_wsnote
      if transtype in("rent"): 
        form.vars.trans_reholiday = trans_reholiday
        form.vars.trans_rebadtool = trans_rebadtool
        form.vars.trans_reother = trans_reother
        form.vars.trans_rentnote = trans_rentnote 
      if transtype in("invoice"):
        ns.valid.set_invoice_customer(form.vars,form.vars.customer_id)
                   
      row_id = ns.connect.updateData("trans", values=dict(form.vars), validate=False, insert_row=True)
      if not row_id:
        response.flash = str(ns.error_message)
      else:
                
        link = ns.db((ns.db.link.ref_id_1==row_id)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0)
            &(ns.db.link.nervatype_2==nervatype_trans)).select().as_list()
        if request.post_vars.trans_id=="" and len(link)>0:
          ns.connect.deleteData("link", ref_id=link[0]["id"])
        else:
          if (transtype=="waybill" and request.post_vars.refnumber_type!="trans"):
            if len(link)>0:
              ns.connect.deleteData("link", ref_id=link[0]["id"])
          else:
            if request.post_vars.trans_id and request.post_vars.trans_id!="":
              values = {"nervatype_1":nervatype_trans, "ref_id_1":row_id, "nervatype_2":nervatype_trans, 
                        "ref_id_2":request.post_vars.trans_id}
              if len(link)>0:
                values["id"]=link[0]["id"]
              ns.connect.updateData("link", values=values, validate=False, insert_row=True)
        
        if transtype in("production"):
          movements = ns.db((ns.db.movement.trans_id==row_id)&(ns.db.movement.deleted==0)
                            &(ns.db.movement.shared==1)).select()
          if len(movements)>1:
            for movement in movements:
              ns.connect.deleteData("movement", ref_id=movement.id)
          values = {"trans_id":row_id,"shippingdate":form.vars.duedate,
                    "movetype":movetype_inventory, "product_id":product_id, "qty":production_qty, 
                    "place_id":form.vars.place_id, "notes":request.post_vars.batch, "shared":1}
          if len(movements)==1:
            values["id"] = movements[0]["id"]
          ns.connect.updateData("movement", values=values, validate=False, insert_row=True)
        
        if transtype in("formula"):
          movements = ns.db((ns.db.movement.trans_id==row_id)&(ns.db.movement.deleted==0)
                            &(ns.db.movement.movetype==movetype_head)).select()
          if len(movements)>1:
            for movement in movements:
              ns.connect.deleteData("movement", ref_id=movement.id)
          values = {"trans_id":row_id,"shippingdate":str(form.vars.transdate)+" 00:00:00",
                    "movetype":movetype_head, "product_id":product_id, "qty":production_qty}
          if len(movements)==1:
            values["id"] = movements[0]["id"]
          ns.connect.updateData("movement", values=values, validate=False, insert_row=True)
        
        if transtype in("bank"):
          payments = ns.db((ns.db.payment.trans_id==row_id)&(ns.db.payment.deleted==0)).select()
          if len(payments)==0:
            values = {"trans_id":row_id,"paiddate":request.post_vars.transdate,"amount":0}
            ns.connect.updateData("payment", values=values, validate=False, insert_row=True)
          
        if transtype in("cash"):
          values = {"trans_id":row_id,"paiddate":request.post_vars.transdate}
          payments = ns.db((ns.db.payment.trans_id==row_id)&(ns.db.payment.deleted==0)).select()
          if len(payments)>1:
            for payment in payments:
              ns.connect.deleteData("payment", ref_id=payment.id)
            values["amount"]=0
          if request.post_vars.paidamount:
            if ns.valid.get_nervatype_name(ns.db.trans(id=row_id).direction)=="out":
              values["amount"]=-float(request.post_vars.paidamount)  
            else: 
              values["amount"]=request.post_vars.paidamount
          else:
            values["amount"]=0
          if len(payments)==1:
            values["id"] = payments[0]["id"]
          ns.connect.updateData("payment", values=values, validate=False, insert_row=True)
                        
        redirect(URL('frm_trans/view/trans/'+str(row_id)))
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      if str(ns.db.trans.fields).find(error)>0:
        flash+=ns.db.trans[error].label+": "+form.errors[error]+", "
      else:
        flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  item_fields=[]
  if response.transcast==None:
    transcast = ns.db((ns.db.fieldvalue.ref_id==trans_id)&(ns.db.fieldvalue.fieldname=="trans_transcast")).select().as_list()
    if len(transcast)>0:
      response.transcast = transcast[0]["value"]
    else:
      response.transcast = "normal"
  response.cruser_id = INPUT(_name="cruser_id", _type="hidden", _value=form.vars.cruser_id, _id="cruser_id")
  response.transtype = INPUT(_name="transtype", _type="hidden", _value=form.vars.transtype, _id="transtype")
  
  if transtype in("offer", "order","worksheet","rent","invoice","receipt"):
    if form.vars.duedate:
      form.custom.widget.duedate = INPUT(_class="date", _id="trans_duedate", _name="duedate", _type="text", _value=form.vars.duedate.date())
    else:
      form.custom.widget.duedate = INPUT(_class="date", _id="trans_duedate", _name="duedate", _type="text", _value="")
  
  if transtype in("offer","order","worksheet","rent","invoice","receipt"):  
    item_sum = ns.db((ns.db.item.trans_id==trans_id)&(ns.db.item.deleted==0)).select(ns.db.item.netamount.sum().with_alias('netamount'),
                                                                                     ns.db.item.vatamount.sum().with_alias('vatamount'),
                                                                                     ns.db.item.amount.sum().with_alias('amount')).as_list()
    if item_sum[0]["netamount"]==None:
      response.netamount = DIV("0", _class="label_disabled", 
                               _style="text-align: right;font-size: 12px;font-weight: bold;color: #551A8B;")
    else:
      response.netamount = DIV(ns.valid.split_thousands(float(item_sum[0]["netamount"])," ","."), _class="label_disabled",  
                               _style="text-align: right;font-size: 12px;font-weight: bold;color: #551A8B;")
    if item_sum[0]["vatamount"]==None:
      response.vatamount = DIV("0", _class="label_disabled", 
                               _style="text-align: right;font-size: 12px;font-weight: bold;color: #551A8B;")
    else:
      response.vatamount = DIV(ns.valid.split_thousands(float(item_sum[0]["vatamount"])," ","."), _class="label_disabled", 
                               _style="text-align: right;font-size: 12px;font-weight: bold;color: #551A8B;")
    if item_sum[0]["amount"]==None:
      response.amount = DIV("0", _class="label_disabled", 
                               _style="text-align: right;font-size: 12px;font-weight: bold;color: #551A8B;")
    else:
      response.amount = DIV(ns.valid.split_thousands(float(item_sum[0]["amount"])," ","."), _class="label_disabled", 
                               _style="text-align: right;font-size: 12px;font-weight: bold;color: #551A8B;")
    
    if session.mobile:
      response.cmd_item_total = ui.control.get_popup_cmd(
        pop_id="popup_total",label=T("Quick Total"),theme="e",inline=False,mini=False,picon="info")
      
    item_fields=[ns.db.item.id, ns.db.item.deposit, ns.db.item.product_id, ns.db.item.description, ns.db.item.qty, ns.db.item.unit, ns.db.item.fxprice,
                 ns.db.item.discount, ns.db.item.netamount, ns.db.item.vatamount, ns.db.item.tax_id]
    form.custom.widget.crdate["_disabled"]="disabled"
    response.crdate = INPUT(_name="crdate", _type="hidden", _value=form.vars.crdate, _id="crdate")
    if direction=="out":
      form.custom.widget.transnumber["_disabled"]="disabled"
      response.transnumber_post = INPUT(_name="transnumber", _type="hidden", _value=form.vars.transnumber, _id="transnumber")
    else:
      response.transnumber_post=""
      
    response.direction = direction
    response.direction_id = INPUT(_name="direction", _type="hidden", _value=direction_id, _id="direction")
    
    response.trans_id = INPUT(_name="trans_id", _type="hidden", _value=lnk_transnumber_id, _id="trans_id")
    response.trans_transnumber = ui.select.get_base_selector(fieldtype="transitem", search_url=URL("dlg_transitem_all"), 
            label_id="reftrans_transnumber",  
            label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('trans_id').value",
            label_txt=lnk_transnumber, 
            value_id="trans_id", error_label=False, div_id="fld_trans_transnumber")
    if session.mobile:
      response.transref_change = ui.control.get_mobil_button(label=T("Edit value or link Ref.No."), href="#",
                                          icon="edit", cformat="ui-btn-right", ajax="true", iconpos="notext", 
                                          onclick="javascript:document.getElementById('trans_id').value='';document.getElementById('reftrans_transnumber').innerHTML=''; \
                                     document.getElementById('trans_ref_transnumber').value='';var rt=document.getElementById('fld_trans_ref_transnumber'); \
                                     var rft=document.getElementById('fld_trans_transnumber'); \
                                     if(rft.style.display == 'none'){rft.style.display = 'block';rt.style.display = 'none';} else {rft.style.display = 'none';rt.style.display = 'block';};")
    else:
      response.transref_change = A(SPAN(_class="icon move"), _id="cmd_transref_change", 
                                     _style="padding: 0px;padding-left: 6px;padding-right: 3px;", 
                                     _class="w2p_trap buttontext button", _href="#null", _title=T("Edit value or link Ref.No."), 
                                     _onclick="javascript:document.getElementById('trans_id').value='';document.getElementById('reftrans_transnumber').innerHTML=''; \
                                     document.getElementById('trans_ref_transnumber').value='';var rt=document.getElementById('fld_trans_ref_transnumber'); \
                                     var rft=document.getElementById('fld_trans_transnumber'); \
                                     if(rft.style.display == 'none'){rft.style.display = 'block';rt.style.display = 'none';} else {rft.style.display = 'none';rt.style.display = 'block';};")
    response.ref_transnumber = DIV(INPUT(_name="ref_transnumber", _type="text", _value=ref_transnumber, _id="trans_ref_transnumber"), _id="fld_trans_ref_transnumber", _style="display:none;")
    if lnk_transnumber_id=="" and ref_transnumber!="":
      response.trans_transnumber["_style"] = str(response.trans_transnumber["_style"]).replace("display:block;", "display:none;")
      response.ref_transnumber["_style"] = str(response.ref_transnumber["_style"]).replace("display:none;", "display:block;")
    
    customer_id=""
    customer_name=""
    if trans_id>-1:  
      if ns.db.trans(id=trans_id).customer_id!=None:
        customer_id = ns.db.trans(id=trans_id).customer_id
        customer_name = ns.db.customer(id=ns.db.trans(id=trans_id).customer_id).custname
    response.customer_id = INPUT(_name="customer_id", _type="hidden", _value=customer_id, _id="customer_id")
    if response.customer_control==None:
      response.customer_control = ui.select.get_customer_selector(customer_name)
    
    employee_id=""
    employee_empnumber=""
    if trans_id>-1:  
      if ns.db.trans(id=trans_id).employee_id!=None:
        employee_id = ns.db.trans(id=trans_id).employee_id
        employee_empnumber = ns.db.employee(id=ns.db.trans(id=trans_id).employee_id).empnumber
    response.employee_id = INPUT(_name="employee_id", _type="hidden", _value=employee_id, _id="employee_id")
    response.employee_control = ui.select.get_employee_selector(employee_empnumber)
    
    project_id=""
    project_pronumber=""
    if trans_id>-1:  
      if ns.db.trans(id=trans_id).project_id!=None:
        project_id = ns.db.trans(id=trans_id).project_id
        project_pronumber = ns.db.project(id=ns.db.trans(id=trans_id).project_id).pronumber
    response.project_id = INPUT(_name="project_id", _type="hidden", _value=project_id, _id="project_id")
    response.project_control = ui.select.get_project_selector(project_pronumber)
    
    if setting_audit_filter in ("disabled"):
      response.cmd_curr = ""
      response.cmd_paidtype = ""
      response.cmd_department = ""
    else:
      if session.mobile:
        response.cmd_curr = ui.control.get_mobil_button(label=T("Edit currencies"), href="#", 
          icon="gear", cformat=None, ajax="true", theme="b", rel="close",
          onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
              +"')){window.location ='"+URL("frm_currency?back=1")+"';};return false;")
        response.cmd_paidtype = ui.control.get_mobil_button(label=T("Edit payments"), href="#", 
          icon="gear", cformat=None, ajax="true", theme="b", rel="close",
          onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
              +"')){window.location ='"+URL("frm_groups_paidtype?back=1")+"';};return false;")
        response.cmd_department = ui.control.get_mobil_button(label=T("Edit departments"), href="#", 
          icon="gear", cformat=None, ajax="true", theme="b", rel="close",
          onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
              +"')){window.location ='"+URL("frm_groups_department?back=1")+"';};return false;")
      else:
        response.cmd_curr = ui.control.get_goprop_button(title=T("Edit currencies"),url=URL("frm_currency?back=1"))
        response.cmd_paidtype = ui.control.get_goprop_button(title=T("Edit payment methods"),url=URL("frm_groups_paidtype?back=1"))
        response.cmd_department = ui.control.get_goprop_button(title=T("Edit departments"),url=URL("frm_groups_department?back=1"))
  
  if transtype in("cash", "bank", "inventory","production","formula") or (transtype=="delivery" and direction=="transfer"):
    place_id=""
    place_planumber=""
    place_curr=""
    if trans_id>-1:  
      if ns.db.trans(id=trans_id).place_id!=None:
        place_id = ns.db.trans(id=trans_id).place_id
        place_planumber = ns.db.place(id=ns.db.trans(id=trans_id).place_id).planumber
        place_curr = ns.db.place(id=ns.db.trans(id=trans_id).place_id).curr
    else:
      if transtype == "cash":
        defname="default_chest"
      elif transtype in("inventory","delivery","production"):
        defname="default_warehouse"
      else:
        defname="default_bank"
      if len(ns.db(ns.db.fieldvalue.fieldname==defname).select().as_list())>0:
        if len(ns.db(ns.db.place.planumber==ns.db.fieldvalue(fieldname=defname).value).select().as_list())>0:
          place_id = ns.db.place(planumber=ns.db.fieldvalue(fieldname=defname).value).id
          place_planumber = ns.db.fieldvalue(fieldname=defname).value
          place_curr = ns.db.place(id=place_id).curr
    response.place_id = INPUT(_name="place_id", _type="hidden", _value=place_id, _id="place_id")
    response.place_curr = DIV(place_curr, _id="place_curr", _class="label_disabled", _style="width: 35px;text-align: center;")
    
    response.trans_id = INPUT(_name="trans_id", _type="hidden", _value=lnk_transnumber_id, _id="trans_id")
    response.trans_transnumber = ui.select.get_base_selector(fieldtype="transitem", search_url=URL("dlg_transitem_all"), 
            label_id="reftrans_transnumber",  
            label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('trans_id').value",
            label_txt=lnk_transnumber, 
            value_id="trans_id", error_label=False, div_id="fld_trans_transnumber")
    if session.mobile:
      response.transref_change = ui.control.get_mobil_button(label=T("Edit value or link Ref.No."), href="#",
                                          icon="edit", cformat="ui-btn-right", ajax="true", iconpos="notext", 
                                          onclick="javascript:document.getElementById('trans_id').value='';document.getElementById('reftrans_transnumber').innerHTML=''; \
                                     document.getElementById('trans_ref_transnumber').value='';var rt=document.getElementById('fld_trans_ref_transnumber'); \
                                     var rft=document.getElementById('fld_trans_transnumber'); \
                                     if(rft.style.display == 'none'){rft.style.display = 'block';rt.style.display = 'none';} else {rft.style.display = 'none';rt.style.display = 'block';};")
    else:
      response.transref_change = A(SPAN(_class="icon move"), _id="cmd_transref_change", 
                                     _style="padding: 0px;padding-left: 6px;padding-right: 3px;", 
                                     _class="w2p_trap buttontext button", _href="#null", _title=T("Edit value or link Ref.No."), 
                                     _onclick="javascript:document.getElementById('trans_id').value='';document.getElementById('reftrans_transnumber').innerHTML=''; \
                                     document.getElementById('trans_ref_transnumber').value='';var rt=document.getElementById('fld_trans_ref_transnumber'); \
                                     var rft=document.getElementById('fld_trans_transnumber'); \
                                     if(rft.style.display == 'none'){rft.style.display = 'block';rt.style.display = 'none';} else {rft.style.display = 'none';rt.style.display = 'block';};")
    response.ref_transnumber = DIV(INPUT(_name="ref_transnumber", _type="text", _value=ref_transnumber, _id="trans_ref_transnumber"), _id="fld_trans_ref_transnumber", _style="display:none;")
    if lnk_transnumber_id=="" and ref_transnumber!="":
      response.trans_transnumber["_style"] = str(response.trans_transnumber["_style"]).replace("display:block;", "display:none;")
      response.ref_transnumber["_style"] = str(response.ref_transnumber["_style"]).replace("display:none;", "display:block;")
    
    if setting_audit_filter in ("disabled"):
      response.cmd_place = ""
    else:
      if session.mobile:
        response.cmd_place = ui.control.get_mobil_button(label=T("Edit places"), href="#", 
          icon="gear", cformat=None, ajax="true", theme="b", rel="close",
          onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
              +"')){window.location ='"+URL("frm_quick_place?back=1")+"';};return false;")
      else:
        response.cmd_place = ui.control.get_goprop_button(title=T("Edit places"),url=URL("frm_quick_place?back=1"))
  
  if transtype in("production","formula"):
    response.direction_id = INPUT(_name="direction", _type="hidden", _value=direction_id, _id="direction")
    form.custom.widget.crdate["_disabled"]="disabled"
    response.crdate = INPUT(_name="crdate", _type="hidden", _value=form.vars.crdate, _id="crdate")
    response.target_place_id = ""
    
    product_id=""
    product_description=""
    trans_probatch=""
    trans_proqty=0
    if trans_id>-1:
      if transtype=="formula":
        trans_product = ns.db((ns.db.movement.trans_id==trans_id)&(ns.db.movement.movetype==movetype_head)&(ns.db.movement.deleted==0)).select()
      else:
        trans_product = ns.db((ns.db.movement.trans_id==trans_id)&(ns.db.movement.shared==1)&(ns.db.movement.deleted==0)).select()
      if len(trans_product)>0:
        product_id = trans_product[0]["product_id"]
        product_description = ns.db.product(id=trans_product[0]["product_id"]).description
        trans_probatch = trans_product[0]["notes"]
        trans_proqty = trans_product[0]["qty"]
    response.trans_production_batch_label = T('Batch No.')
    response.trans_production_batch_data = INPUT(_name="batch", _type="text", _value=trans_probatch, _id="trans_production_batch", 
                                               _class="string", _style="width: 100%;")
    response.trans_production_qty_label = T('Qty')
    response.trans_production_qty_data = INPUT(_name="production_qty", _type="text", _value=trans_proqty, _id="trans_production_qty", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.production_product_id = INPUT(_name="product_id", _type="hidden", _value=product_id, _id="production_product_id")
    if response.production_product_selector==None:
      if product_audit_filter!="disabled":
        response.production_product_selector = ui.select.get_base_selector(
                        fieldtype="product", search_url=URL("dlg_product_item"),
                        label_id="production_product_label",
                        label_url="'"+URL("frm_product/view/product")+"/'+document.getElementById('production_product_id').value",
                        label_txt=product_description,value_id="production_product_id",error_label=False)
      else:
        response.production_product_selector = DIV(SPAN(product_description, _id="production_product_label"), _id="production_product_id", _class="label_disabled", 
              _style="display:block;")
      
  if transtype=="formula":
    response.transdate = INPUT(_name="transdate", _type="hidden", _value=form.vars.crdate, _id="transdate")
    
  if transtype=="production":
    response.production_id = INPUT(_name="production_id", _type="hidden", _value=trans_id, _id="production_production_id")
    response.production_place_id = INPUT(_name="place_id", _type="hidden", _value=place_id, _id="production_place_id")
    if response.production_place_selector==None:
      response.production_place_selector = ui.select.get_base_selector(
                          fieldtype="place", search_url=URL("dlg_place_warehouse"),
                          label_id="production_place_label",
                          label_url="'"+URL("frm_place/view/place")+"/'+document.getElementById('production_place_id').value",
                          label_txt=place_planumber,value_id="production_place_id",error_label=False)  
    
    transtype_id_formula = ns.valid.get_groups_id("transtype", "formula")
    movetype_head = ns.valid.get_groups_id("movetype", "head")
    pro_formula = ns.db((ns.db.trans.transtype==transtype_id_formula)&(ns.db.trans.deleted==0)
                        &(ns.db.trans.id==ns.db.movement.trans_id)&(ns.db.movement.deleted==0)
                        &(ns.db.movement.movetype==movetype_head)&(ns.db.movement.product_id==product_id)).select(ns.db.trans.id,ns.db.trans.transnumber)
    response.cmb_formula = SELECT(*[OPTION(field["transnumber"],_value=field["id"]) for field in pro_formula], 
                                  _id="cmb_formula", _title=T("Select product formula"), _style="height: 30px;width: 100%;")
    response.cmb_formula.insert(0, OPTION("", _value=""))
    if ui.connect.get_audit_filter("trans", "formula")[0]!="disabled":
      if session.mobile:
        response.cmd_load_formula = ui.control.get_mobil_button(T("Load formula"), href="#", cformat=None, icon="refresh", style="text-align: left;",
                                            onclick="load_formula();", theme="b")
      else:
        response.cmd_load_formula = A(SPAN(_class="icon loop"), _id="cmd_load_formula", 
                                     _style="padding: 0px;padding-left: 6px;padding-right: 3px;", 
                                     _class="w2p_trap buttontext button", _href="#null", _title=T("Load selected formula..."), 
                                     _onclick="load_formula();")
    else:
      response.cmd_load_formula =""  
    
  if transtype=="inventory":
    response.direction_id = INPUT(_name="direction", _type="hidden", _value=direction_id, _id="direction")
    response.crdate = ""
    response.transdate = ""
    response.target_place_id = ""
    if response.place_control==None:
      response.place_control = ui.select.get_place_selector(place_planumber, placetype="dlg_place_warehouse",title=T("Select warehouse"))
  
  if transtype=="delivery" and direction!="transfer":
    form.custom.widget.transnumber["_disabled"]="disabled"
    response.ref_transnumber = INPUT(_name="transnumber", _type="hidden", _value=ns.db.trans(id=trans_id).transnumber, _id="transnumber")
    response.trans_id =""
    form.custom.widget.crdate["_disabled"]="disabled"
    response.crdate = INPUT(_name="crdate", _type="hidden", _value=ns.db.trans(id=trans_id).crdate, _id="crdate")
    form.custom.widget.transdate["_disabled"]="disabled"
    response.transdate = INPUT(_name="transdate", _type="hidden", _value=ns.db.trans(id=trans_id).transdate, _id="transdate")
    
    response.direction_id = INPUT(_name="direction", _type="hidden", _value=direction_id, _id="direction")
    nervatype_item_id = ns.valid.get_groups_id("nervatype", "item")
    nervatype_movement_id = ns.valid.get_groups_id("nervatype", "movement")
    ref_trans = ((ns.db.movement.deleted==0)&(ns.db.movement.trans_id==trans_id)
                 &(ns.db.movement.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_movement_id)&(ns.db.link.deleted==0)
                 &(ns.db.link.nervatype_2==nervatype_item_id)&(ns.db.link.ref_id_2==ns.db.item.id))
    ref_trans = ns.db(ref_trans).select(ns.db.item.trans_id)
    if len(ref_trans)>0:
      response.trans_transnumber = DIV(A(ns.db.trans(id=ref_trans[0].trans_id).transnumber, _href="#", _onclick="javascript:window.open('"
                           +URL("frm_trans/view/trans/"+str(ref_trans[0].trans_id))+"', '_blank');")
                         ,_class="label_disabled", _style="display:block;")
    else:
      response.trans_transnumber = DIV(SPAN(""),_class="label_disabled", 
                                       _style="width: 100%;display:block;")
    
    response.place_id=""
    response.target_place_id=""
    ref_place = ns.db((ns.db.movement.deleted==0)&(ns.db.movement.trans_id==trans_id)).select(ns.db.movement.place_id)
    if len(ref_place)>0:
      response.place_control = DIV(A(ns.db.place(id=ref_place[0].place_id).planumber, _href="#", _onclick="javascript:window.open('"
                           +URL("frm_place/view/place/"+str(ref_place[0].place_id))+"', '_blank');")
                         ,_class="label_disabled", _style="width: 100%;display:block;;")
    else:
      response.place_control = DIV(SPAN(""),_class="label_disabled", 
                                   _style="width: 100%;display:block;")
    if setting_audit_filter in ("disabled"):
      response.cmd_place = ""
    else:
      if session.mobile:
        response.cmd_place = ui.control.get_mobil_button(label=T("Edit places"), href="#", 
          icon="gear", cformat=None, ajax="true", theme="b", rel="close",
          onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
              +"')){window.location ='"+URL("frm_quick_place?back=1")+"';};return false;")
      else:
        response.cmd_place = ui.control.get_goprop_button(title=T("Edit places"),url=URL("frm_quick_place?back=1"))
      
  if transtype=="delivery" and direction=="transfer":
    response.direction_id = INPUT(_name="direction", _type="hidden", _value=direction_id, _id="direction")
    response.crdate,response.transdate,target_place_id,target_place_planumber = "","","",""
    if trans_id>-1:
      movements = ns.db((ns.db.movement.deleted==0)&(ns.db.movement.trans_id==trans_id)&(ns.db.movement.place_id!=place_id)).select()  
      if len(movements)>0:
        target_place_id = movements[0].place_id
        target_place_planumber = ns.db.place(id=movements[0].place_id).planumber
        response.place_control = DIV(A(place_planumber, _id="place_planumber",  _href="#", _onclick="javascript:window.open('"
                           +URL("frm_place/view/place/"+str(ns.db.trans(id=trans_id).place_id)+"', '_blank');")
                         ,_class="label_disabled", _style="width: 100%;display:block;"))
      else:
        target_place_id = place_id
        target_place_planumber = place_planumber
    else:
      target_place_id = place_id
      target_place_planumber = place_planumber
    if response.place_control==None:
      response.place_control = ui.select.get_place_selector(place_planumber, placetype="dlg_place_warehouse",title=T("Select warehouse"))
    response.target_place_id = INPUT(_name="target_place_id", _type="hidden", _value=target_place_id, _id="target_place_id")
    if response.target_place_control==None:
      response.target_place_control = ui.select.get_place_selector(target_place_planumber, placetype="dlg_place_warehouse",
                                        title=T("Select warehouse"),value_id="target_place_id",label_id="target_place_planumber", fnum="2")
            
  if transtype=="bank":
    response.direction_id = INPUT(_name="direction", _type="hidden", _value=direction_id, _id="direction")
    response.crdate = ""
    response.transdate=""
    response.transnumber_post=""
    payment_sum = ns.db((ns.db.payment.trans_id==trans_id)&(ns.db.payment.deleted==0)&(ns.db.payment.amount<0)).select(ns.db.payment.amount.sum().with_alias('amount')).as_list()
    if payment_sum[0]["amount"]==None:
      response.expense = DIV("0", _class="label_disabled", 
                               _style="text-align: right;font-size: 12px;font-weight: bold;color: #551A8B;")
    else:
      response.expense = DIV(ns.valid.split_thousands(float(payment_sum[0]["amount"])," ","."), _class="label_disabled",  
                               _style="text-align: right;font-size: 12px;font-weight: bold;color: #551A8B;")
    
    payment_sum = ns.db((ns.db.payment.trans_id==trans_id)&(ns.db.payment.deleted==0)&(ns.db.payment.amount>0)).select(ns.db.payment.amount.sum().with_alias('amount')).as_list()
    if payment_sum[0]["amount"]==None:
      response.income = DIV("0", _class="label_disabled", 
                               _style="text-align: right;font-size: 12px;font-weight: bold;color: #551A8B;")
    else:
      response.income = DIV(ns.valid.split_thousands(float(payment_sum[0]["amount"])," ","."), _class="label_disabled",  
                               _style="text-align: right;font-size: 12px;font-weight: bold;color: #551A8B;")
    
    payment_sum = ns.db((ns.db.payment.trans_id==trans_id)&(ns.db.payment.deleted==0)).select(ns.db.payment.amount.sum().with_alias('amount')).as_list()
    if payment_sum[0]["amount"]==None:
      response.balance = DIV("0", _class="label_disabled", 
                               _style="text-align: right;font-size: 12px;font-weight: bold;color: #551A8B;")
    else:
      response.balance = DIV(ns.valid.split_thousands(float(payment_sum[0]["amount"])," ","."), _class="label_disabled",  
                               _style="text-align: right;font-size: 12px;font-weight: bold;color: #551A8B;")
    
    if session.mobile:  
      response.cmd_payment_total = ui.control.get_popup_cmd(
        pop_id="popup_total",label=T("Quick Total"),theme="e",inline=False,mini=False,picon="info")
    if response.place_control==None:
      response.place_control = ui.select.get_place_selector(place_planumber, placetype="dlg_place_bank",title=T("Select bank account"))
  
  if transtype=="cash":
    response.label_paidamount = T("Amount")
    paidamount = 0
    if trans_id>-1:
      form.custom.widget.direction["_disabled"]="disabled"
      response.direction_id = INPUT(_name="direction", _type="hidden", _value=direction_id, _id="direction")
      if len(ns.db(ns.db.payment.trans_id==trans_id).select().as_list())>0:
        paidamount = ns.db(ns.db.payment.trans_id==trans_id).select().as_list()[0]["amount"]
        if session.mobile:
          response.cmd_cash_link_new = ui.control.get_mobil_button(label=T("Link Invoice"), href="#", 
            cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
            onclick= "set_link_invoice(-1,"+str(ns.db(ns.db.payment.trans_id==trans_id).select().as_list()[0]["id"])
              +",'','','',"+str(paidamount)+",1);", rel="close")
      response.transdate = ""
    else:
      response.direction_id=""
      response.transdate = INPUT(_name="transdate", _type="hidden", _value=form.vars.crdate, _id="trans_transdate")
    if direction=="out":
      paidamount=-paidamount
    response.paidamount = INPUT(_name="paidamount", _type="text", _value=paidamount, _id="trans_paidamount", _class="double")
    
    if response.place_control==None:
      response.place_control = ui.select.get_place_selector(place_planumber, placetype="dlg_place_cash",title=T("Select Cash desk"))
          
    form.custom.widget.transnumber["_disabled"]="disabled"
    response.transnumber_post = INPUT(_name="transnumber", _type="hidden", _value=form.vars.transnumber, _id="transnumber")
    form.custom.widget.crdate["_disabled"]="disabled"
    response.crdate = INPUT(_name="crdate", _type="hidden", _value=form.vars.crdate, _id="crdate")
    
    employee_id=""
    employee_empnumber=""
    if trans_id>-1:  
      if ns.db.trans(id=trans_id).employee_id!=None:
        employee_id = ns.db.trans(id=trans_id).employee_id
        employee_empnumber = ns.db.employee(id=ns.db.trans(id=trans_id).employee_id).empnumber
    response.employee_id = INPUT(_name="employee_id", _type="hidden", _value=employee_id, _id="employee_id")
    response.employee_control = ui.select.get_employee_selector(employee_empnumber)
      
  if transtype=="waybill":
    response.view=ui.dir_view+'/trans_movement.html'
    if not session.mobile:
      response.titleicon = URL(ui.dir_images,'icon16_wrench_page.png')
    
    response.trans_id = INPUT(_name="trans_id", _type="hidden", _value="", _id="trans_id")
    response.target_place_id = ""
    if response.trans_transnumber==None:
      response.trans_transnumber = ui.select.get_base_selector(fieldtype="transitem", search_url=URL("dlg_transitem_all"), 
            label_id="reftrans_transnumber",  
            label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('trans_id').value",
            label_txt="", 
            value_id="trans_id", error_label=False, div_id="fld_trans_transnumber", display="none")
    
    response.customer_id = INPUT(_name="customer_id", _type="hidden", _value="", _id="customer_id")
    if response.customer_custname==None:
      if customer_audit_filter!="disabled":
        response.customer_custname = ui.select.get_base_selector(fieldtype="customer", search_url=URL("dlg_customer"), 
              label_id="customer_custname", label_url="", label_txt="", 
              value_id="customer_id", error_label=False, div_id="fld_customer_custname", display="none") 
      else:
        response.customer_custname = DIV(SPAN("", _id="customer_custname"), _id="fld_customer_custname", _class="label_disabled", 
              _style="display:none;")
    response.employee_id = INPUT(_name="employee_id", _type="hidden", _value="", _id="employee_id")  
    if response.employee_empnumber==None:
      if employee_audit_filter!="disabled":
        response.employee_empnumber = ui.select.get_base_selector(fieldtype="employee", search_url=URL("dlg_employee"), 
              label_id="employee_empnumber", label_url="", label_txt="", 
              value_id="employee_id", error_label=False, div_id="fld_employee_empnumber", display="none")
      else:
        response.employee_empnumber = DIV(SPAN("", _id="employee_empnumber"), _id="fld_employee_empnumber", _class="label_disabled", 
              _style="display:none;")
    response.employee_id = INPUT(_name="employee_id", _type="hidden", _value="", _id="employee_id")
    
    opt_trans = OPTION(T("Transaction"),_value="trans")
    opt_customer = OPTION(T("Customer"),_value="customer")
    opt_employee = OPTION(T("Employee"),_value="employee")
    
    form.custom.widget.crdate["_disabled"]="disabled"
    response.crdate = INPUT(_name="crdate", _type="hidden", _value=form.vars.crdate, _id="crdate")
    response.transdate = INPUT(_name="transdate", _type="hidden", _value=form.vars.crdate, _id="transdate")
    
    if trans_id==-1:
      form.vars.transnumber = ns.connect.nextNumber("waybill",False)
      form.vars.direction = ns.valid.get_groups_id("direction", direction)
      response.direction_id = ""
    else:
      form.custom.widget.direction["_disabled"]="disabled"
      response.direction_id = INPUT(_name="direction", _type="hidden", _value=direction_id, _id="direction")  
    if request.post_vars.has_key("refnumber_type"):
      refnumber_type = request.post_vars["refnumber_type"]
    elif request.vars.has_key("init_refnumber_type"):
      refnumber_type = request.vars["init_refnumber_type"]
    else:
      if trans_id==-1:
        refnumber_type = "trans"
      elif ns.db.trans(id=trans_id).customer_id!=None:
        refnumber_type = "customer"
      elif ns.db.trans(id=trans_id).employee_id!=None:
        refnumber_type = "employee"
      else:
        refnumber_type = "trans"
    
    if refnumber_type=="trans":
      response.trans_transnumber["_style"]=str(response.trans_transnumber["_style"]).replace("display:none;","display:block;")
      opt_trans["_selected"]="selected"
      response.refnumber_type = INPUT(_name="refnumber_type", _type="hidden", _value="trans", _id="refnumber_type")
      ref_id = -1
      if request.post_vars.has_key("trans_id"):
        if request.post_vars["trans_id"]!="":
          ref_id = request.post_vars["trans_id"]
      elif request.vars.has_key("init_trans_id"):
        if request.vars["init_trans_id"]!="":
          ref_id = request.vars["init_trans_id"]
      elif trans_id>-1:
        link = ns.db((ns.db.link.ref_id_1==trans_id)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0)
              &(ns.db.link.nervatype_2==nervatype_trans)).select().as_list()
        if len(link)>0:
          ref_id=link[0]["ref_id_2"]
      if ref_id>-1:
        response.trans_id = INPUT(_name="trans_id", _type="hidden", _value=ref_id, _id="trans_id")
        response.trans_transnumber = ui.select.get_base_selector(fieldtype="transitem", search_url=URL("dlg_transitem_all"), 
            label_id="reftrans_transnumber",  
            label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('trans_id').value",
            label_txt=ns.db.trans(id=ref_id).transnumber, 
            value_id="trans_id", error_label=False, div_id="fld_trans_transnumber")
    elif refnumber_type=="customer":
      response.customer_custname["_style"]=str(response.customer_custname["_style"]).replace("display:none;","display:block;")
      ref_id = -1
      if request.post_vars.has_key("customer_id"):
        if request.post_vars["customer_id"]!="":
          ref_id = request.post_vars["customer_id"]
      elif trans_id>-1:
        if ns.db.trans(id=trans_id).customer_id!=None:
          ref_id = ns.db.trans(id=trans_id).customer_id
      if ref_id>-1:
        response.customer_id = INPUT(_name="customer_id", _type="hidden", _value=ref_id, _id="customer_id")
        if customer_audit_filter!="disabled":
          response.customer_custname = ui.select.get_base_selector(fieldtype="customer", search_url=URL("dlg_customer"), 
              label_id="customer_custname", 
              label_url="'"+URL("frm_customer/view/customer")+"/'+document.getElementById('customer_id').value", 
              label_txt=ns.db.customer(id=ref_id).custname, 
              value_id="customer_id", error_label=False, div_id="fld_customer_custname")
        else:
          response.customer_custname = DIV(SPAN(ns.db.customer(id=ref_id).custname, _id="customer_custname"), _id="fld_customer_custname", _class="label_disabled", 
              _style="display:block;")
      opt_customer["_selected"]="selected"
      response.refnumber_type = INPUT(_name="refnumber_type", _type="hidden", _value="customer", _id="refnumber_type")
    elif refnumber_type=="employee":
      response.employee_empnumber["_style"]=str(response.employee_empnumber["_style"]).replace("display:none;","display:block;")
      ref_id = -1
      if request.post_vars.has_key("employee_id"):
        if request.post_vars["employee_id"]!="":
          ref_id = request.post_vars["employee_id"]
      elif trans_id>-1:
        if ns.db.trans(id=trans_id).employee_id!=None:
          ref_id = ns.db.trans(id=trans_id).employee_id
      if ref_id>-1:
        response.employee_id = INPUT(_name="employee_id", _type="hidden", _value=ref_id, _id="employee_id")
        if employee_audit_filter!="disabled":
          response.employee_empnumber = ui.select.get_base_selector(fieldtype="employee", search_url=URL("dlg_employee"), 
              label_id="employee_empnumber", 
              label_url="'"+URL("frm_employee/view/employee")+"/'+document.getElementById('employee_id').value", 
              label_txt=ns.db.employee(id=ref_id).empnumber, 
              value_id="employee_id", error_label=False, div_id="fld_employee_empnumber")
        else:
          response.employee_empnumber = DIV(SPAN(ns.db.employee(id=ref_id).empnumber, _id="employee_empnumber"), _id="fld_employee_empnumber", _class="label_disabled", 
              _style="display:block;")
      opt_employee["_selected"]="selected"
      response.refnumber_type = INPUT(_name="refnumber_type", _type="hidden", _value="employee", _id="refnumber_type")
    
    opt=[]
    opt.append(opt_trans)
    opt.append(opt_customer)
    opt.append(opt_employee)
    response.reftype = SELECT(*opt, _id="cmb_reftype", 
                              _onchange='javascript:\
                              document.getElementById("refnumber_type").value = this.value;\
                              document.getElementById("fld_trans_transnumber").style.display = "none";\
                              document.getElementById("fld_customer_custname").style.display = "none";\
                              document.getElementById("fld_employee_empnumber").style.display = "none";\
                              if (this.value=="trans"){document.getElementById("fld_trans_transnumber").style.display = "block";}\
                              else if (this.value=="customer"){document.getElementById("fld_customer_custname").style.display = "block";}\
                              else {document.getElementById("fld_employee_empnumber").style.display = "block";}')
    
  if transtype in("worksheet"):
    response.trans_wsdistance_label = T('Distance (km)')
    response.trans_wsdistance_data = INPUT(_name="trans_wsdistance", _type="text", _value=trans_wsdistance, _id="trans_wsdistance", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.trans_wsrepair_label = T('Repair time (h)')
    response.trans_wsrepair_data = INPUT(_name="trans_wsrepair", _type="text", _value=trans_wsrepair, _id="trans_wsrepair", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.trans_wstotal_label = T('Total time (h)')
    response.trans_wstotal_data = INPUT(_name="trans_wstotal", _type="text", _value=trans_wstotal, _id="trans_wstotal", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.trans_wsnote_label = T('Justification')
    response.trans_wsnote_data = INPUT(_name="trans_wsnote", _type="text", _value=trans_wsnote, _id="trans_wsnote", 
                                               _class="string", _style="width: 100%;")
  
  if transtype in("rent"):
    response.trans_reholiday_label = T('Holidays')
    response.trans_reholiday_data = INPUT(_name="trans_reholiday", _type="text", _value=trans_reholiday, _id="trans_reholiday", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.trans_rebadtool_label = T('Bad machine')
    response.trans_rebadtool_data = INPUT(_name="trans_rebadtool", _type="text", _value=trans_rebadtool, _id="trans_rebadtool", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.trans_reother_label = T('Other non-eligible')
    response.trans_reother_data = INPUT(_name="trans_reother", _type="text", _value=trans_reother, _id="trans_reother", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.trans_rentnote_label = T('Justification')
    response.trans_rentnote_data = INPUT(_name="trans_rentnote", _type="text", _value=trans_rentnote, _id="trans_rentnote", 
                                               _class="string", _style="width: 100%;")
    
  if response.deleted==1 or response.closed==1 or (transtype_audit_filter[0] in ("readonly","disabled")):
    editable = False
  else:
    editable = True
  
  if session.mobile:
    if session["trans_page_"+str(trans_id)]:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value=session["trans_page_"+str(trans_id)])
      session["trans_page_"+str(trans_id)]="trans_page"
    else:
      response.active_page = INPUT(_id="active_page", _type="hidden", _value="trans_page")
      
    response.menu_trans = ui.control.get_mobil_button(T("Document Data"), href="#", 
        cformat=None, icon="edit", style="text-align: left;",
        onclick= "show_page('trans_page');", theme="a", rel="close")
  
  response.menu_movement = ""
  if trans_id>-1 and transtype in("waybill","inventory","delivery","production","formula"):
    #movement data
    if transtype=="waybill":
      movement = ((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.tool_id==ns.db.tool.id))
      fields=[ns.db.movement.id, ns.db.movement.shippingdate, ns.db.movement.tool_id, ns.db.tool.description, ns.db.movement.notes]
      ns.db.movement.notes.label = T("Comments")
      response.movement_tool_id = INPUT(_name="tool_id", _type="hidden", _value="", _id="tool_id")
      response.movement_serial = ui.select.get_tool_selector("")
      priority="0,1,2"
    elif transtype=="production":
      movement = ((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)
                  &(ns.db.movement.shared==0)&(ns.db.movement.product_id==ns.db.product.id))
      fields=[ns.db.movement.id, ns.db.movement.shippingdate, ns.db.movement.place_id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, 
              ns.db.movement.notes, ns.db.movement.qty, ns.db.movement.shared]
      ns.db.movement.shared.readable = ns.db.movement.shared.writable = False
      ns.db.movement.qty.represent = lambda value,row: DIV(ns.valid.split_thousands(-float(value)," ","."), _align="right", _width="100%")
      priority="0,3,7"
    elif transtype=="formula":
      movement = ((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)
                  &(ns.db.movement.movetype==ns.valid.get_groups_id("movetype", "plan")) 
                  &(ns.db.movement.product_id==ns.db.product.id))
      fields=[ns.db.movement.id, ns.db.movement.shippingdate, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, 
              ns.db.movement.qty, ns.db.movement.shared, ns.db.movement.place_id, ns.db.movement.notes]
      ns.db.movement.notes.label = T("Comments")
      ns.db.movement.shippingdate.readable = ns.db.movement.shippingdate.writable = False
      priority="0,1,4"
    elif transtype=="inventory":
      movement = ((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.product_id==ns.db.product.id))
      fields=[ns.db.movement.id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes, ns.db.movement.qty]
      priority="0,1,5"
    elif transtype=="delivery" and direction!="transfer":
      movement = ((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.product_id==ns.db.product.id))
      fields=[ns.db.movement.id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes, ns.db.movement.qty]
      priority="0,1,5"
    elif transtype=="delivery" and direction=="transfer":
      nervatype_movement_id = ns.valid.get_groups_id("nervatype", "movement")
      if len(ns.db((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)).select(ns.db.movement.id))>0:
        movement = ((ns.db.movement.id.belongs(ns.db((ns.db.link.ref_id_1.belongs(ns.db(ns.db.movement.trans_id==trans_id).select(ns.db.movement.id)))
                       &(ns.db.link.nervatype_1==nervatype_movement_id)&(ns.db.link.deleted==0)
                       &(ns.db.link.nervatype_2==nervatype_movement_id)).select(ns.db.link.ref_id_2.with_alias('id'))))
                  &(ns.db.movement.deleted==0)&(ns.db.movement.product_id==ns.db.product.id))
      else:
        movement = ((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.product_id==ns.db.product.id))
      fields=[ns.db.movement.id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes, ns.db.movement.qty]
      priority="0,1,5"
      
    movement_count = ns.db(movement).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if transtype=="waybill":
      if session.mobile:
        ns.db.movement.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), 
                          href="#", cformat=None, icon="edit", style="text-align: left;",
                          onclick="set_movement("
                           +str(row["movement"]["id"])+",'"
                           +str(row["movement"]["shippingdate"])+"','','',"
                           +str(row["movement"]["tool_id"])
                           +",'"+ns.db.tool(id=row["movement"]["tool_id"]).serial+"',0,'"
                           +json.dumps(str(row["movement"]["notes"]))[1:-1]+"','','',0)", theme="d")
      else:
        links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_movement("
                           +str(row["movement"]["id"])+",'"
                           +str(row["movement"]["shippingdate"])+"','','',"
                           +str(row["movement"]["tool_id"])
                           +",'"+ns.db.tool(id=row["movement"]["tool_id"]).serial+"',0,'"
                           +json.dumps(str(row["movement"]["notes"]))[1:-1]+"','','',0)",
                           _title=T("Edit item"))]
      response.movement_qty = INPUT(_name="qty", _type="hidden", _value=0, _id="movement_qty")
      response.movement_movetype = INPUT(_name="movetype", _type="hidden",
        _value=ns.valid.get_groups_id("movetype", "tool"), 
         _id="movement_movetype")
    else:
      response.movement_product_id = INPUT(_name="product_id", _type="hidden", _value="", _id="product_id")
      response.movement_product_control=ui.select.get_product_selector("",protype="item")
      response.movement_shippingdate_disabled = INPUT(_name="shippingdate", _type="text", _value="", _id="movement_shippingdate", _disabled="disabled")
      response.movement_shippingdate_enabled = INPUT(_name="shippingdate", _type="text", _value="", _id="shippingdate", _class="datetime",_style="width: 100%;text-align: center;")
      response.movement_shippingdate = INPUT(_name="shippingdate", _type="hidden", _value="", _id="shippingdate")
      response.movement_place_id = INPUT(_name="place_id", _type="hidden", _value="", _id="movement_place_id")
      response.movement_place_control=ui.select.get_place_selector("",placetype="dlg_place_warehouse",title=T("Select warehouse"),
                       value_id="movement_place_id", label_id="movement_place_planumber")
      response.movement_place_planumber = DIV(A("", _id="movement_place_planumber", _href="#", _onclick="javascript:window.open("
                           +"'" + URL("frm_place/view/place") + "'+document.getElementById('movement_place_id').value, '_blank');")
                         ,_class="label_disabled", _style="width: 100%;display:block;")
      ns.db.movement.notes.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
      if transtype=="formula":
        response.movement_movetype = INPUT(_name="movetype", _type="hidden",
          _value=ns.valid.get_groups_id("movetype", "plan"),
          _id="movement_movetype")
      else:
        response.movement_movetype = INPUT(_name="movetype", _type="hidden",
          _value=ns.valid.get_groups_id("movetype", "inventory"),
          _id="movement_movetype")
      if transtype in("production","formula"):
        if session.mobile:
          ns.db.movement.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), 
                          href="#", cformat=None, icon="edit", style="text-align: left;",
                          onclick="set_movement("
                           +str(row["movement"]["id"])+",'"+str(row["movement"]["shippingdate"])+"',"
                           +str(row["movement"]["product_id"])
                           +",'"+ns.db.product(id=row["movement"]["product_id"]).description+"','','',"
                           +str(-row["movement"]["qty"] if transtype=="production" else row["movement"]["qty"])+",'"
                           +json.dumps(str(row["movement"]["notes"]))[1:-1]+"','"
                           +str(row["movement"]["place_id"])+"','"
                           +str(json.dumps(str(ns.db.place(id=row["movement"]["place_id"]).planumber))[1:-1] if row["movement"]["place_id"] else "")+"',"
                           +str(row["movement"]["shared"])+")", theme="d")
        else:
          links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_movement("
                           +str(row["movement"]["id"])+",'"+str(row["movement"]["shippingdate"])+"',"
                           +str(row["movement"]["product_id"])
                           +",'"+ns.db.product(id=row["movement"]["product_id"]).description+"','','',"
                           +str(-row["movement"]["qty"] if transtype=="production" else row["movement"]["qty"])+",'"
                           +json.dumps(str(row["movement"]["notes"]))[1:-1]+"','"
                           +str(row["movement"]["place_id"])+"','"
                           +str(json.dumps(str(ns.db.place(id=row["movement"]["place_id"]).planumber))[1:-1] if row["movement"]["place_id"] else "")+"',"
                           +str(row["movement"]["shared"])+")",
                           _title=T("Edit item"))]
      else:
        if session.mobile:
          ns.db.movement.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), 
                          href="#", cformat=None, icon="edit", style="text-align: left;",
                          onclick="set_movement("
                           +str(row["movement"]["id"])+",'',"
                           +str(row["movement"]["product_id"])
                           +",'"+ns.db.product(id=row["movement"]["product_id"]).description+"','','',"
                           +str(row["movement"]["qty"])+",'"
                           +json.dumps(str(row["movement"]["notes"]))[1:-1]+"','','',0)", theme="d")
        else:
          links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_movement("
                           +str(row["movement"]["id"])+",'',"
                           +str(row["movement"]["product_id"])
                           +",'"+ns.db.product(id=row["movement"]["product_id"]).description+"','','',"
                           +str(row["movement"]["qty"])+",'"
                           +json.dumps(str(row["movement"]["notes"]))[1:-1]+"','','',0)",
                           _title=T("Edit item"))]
    
    if session.mobile:
      links = None
      response.cmd_movement_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
        icon="back", ajax="true", theme="a",  
        onclick= "show_page('movement_page');", rel="close")
    else:
      response.movement_icon = URL(ui.dir_images,'icon16_corrected.png')
      response.cmd_movement_cancel = A(SPAN(_class="icon cross"), 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_movement').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    if editable:
      if transtype=="delivery" and direction!="transfer":
        if session.mobile:
          ns.db.movement.id.represent = lambda value,row: ui.control.format_value("integer",value)
          response.cmd_movement_new = ""
        else:
          response.cmd_movement_new = SPAN(" ",SPAN(str(movement_count), _class="detail_count"))
          links = []
      else:
        if session.mobile:
          response.cmd_movement_new = ui.control.get_mobil_button(
            label=T("New Item"), href="#", 
            cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
            onclick= "set_movement(-1, '"+str(datetime.date.today())+" 00:00:00"+"', '', '', '', '', 0, '','','',0);", 
            rel="close")
          response.cmd_movement_update = ui.control.get_mobil_button(label=T("Save item"), href="#", 
            cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
            onclick= "movement_update();return true;")
          
          response.cmd_movement_delete = ui.control.get_mobil_button(label=T("Delete Item"), href="#", 
            cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
            onclick= "if(confirm('"+T('Are you sure you want to delete this item?')+
                                "')){if(document.getElementById('movement_id').value>-1){window.location = '"
              +URL("frm_trans")+"/delete/movement/'+document.getElementById('movement_id').value;} else {show_page('movement_page');}}")
        else:
          response.cmd_movement_new = ui.control.get_tabnew_button(movement_count,T('New Item'), cmd_id="cmd_movement_new",
                                  cmd = "$('#tabs').tabs({ active: 0 });set_movement(-1, '"+str(datetime.date.today())+" 00:00:00"+"', '', '', '', '', 0, '','','',0)")
          response.cmd_movement_update = ui.control.get_command_button(caption=T("Save"),title=T("Update item data"),color="008B00", _id="cmd_movement_submit",
                                cmd="movement_update();return true;")
          links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this item?')+
                                "')){window.location ='"+URL("frm_trans/delete/movement/"+str(row["movement"]["id"]))+"';};return false;", 
                           _title=T("Delete Item")))
    else:
      if session.mobile:
        response.cmd_movement_new = ""
      else:
        response.cmd_movement_new = SPAN(" ",SPAN(str(movement_count), _class="detail_count"))
      response.cmd_movement_update = ""
      response.cmd_movement_delete = ""
    
    if session.mobile:
      response.menu_movement = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Items"),movement_count), 
        href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('movement_page');", theme="a", rel="close")
      ns.db.movement.id.label = T("*")
    else:
      ns.db.movement.id.label = T("No.")
      ns.db.movement.id.represent = lambda value,row: ui.control.format_value("integer",row["id"])
    response.view_movement = ui.select.get_tab_grid(movement, ns.db.movement.id, _fields=fields, _deletable=False, links=links, _editable=False,
                                          multi_page="movement_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id),_priority=priority)
            
    response.movement_form = SQLFORM(ns.db.movement, submit_button=T("Save"),_id="frm_movement")
    response.movement_form.process()
    response.movement_id = INPUT(_name="id", _type="hidden", _value="", _id="movement_id")
    response.movement_trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="movement_trans_id")
  
  response.item_rate_lst = []
  response.menu_item = ""
  if trans_id>-1 and transtype in("offer","order","worksheet","rent","invoice","receipt"):
    #item data
    item = ((ns.db.item.trans_id==trans_id)&(ns.db.item.deleted==0))
    item_count = ns.db(item).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']      
    if item_fields!=[]:
      fields = item_fields
    else:
      fields=[]
    
    if session.mobile:
      links = None
      response.menu_item = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Items"),item_count), 
        href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('item_page');", theme="a", rel="close")
      response.cmd_item_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
          icon="back", ajax="true", theme="a",  
          onclick= "show_page('item_page');", rel="close")
      ns.db.item.id.label = T("*")
      ns.db.item.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, icon="edit", style="text-align: left;",
                            onclick="set_item("
                             +str(row["id"])+","+str(row["product_id"])
                             +",'"+ns.db.product(id=row["product_id"]).description+"',"
                             +str(row["tax_id"])+","
                             +str(ns.db.tax(id=row["tax_id"]).rate)+","
                             +str(row["vatamount"])+","
                             +str(ns.db.currency(curr=ns.db.trans(id=trans_id).curr).digit)+",'"
                             +json.dumps(str(row["description"]))[1:-1]+"',"
                             +str(row["deposit"])+","
                             +str(row["qty"])+","
                             +str(row["discount"])+","
                             +str(row["fxprice"])+",'"
                             +str(row["unit"])+"',"
                             +str(row["netamount"])+","
                             +str(ns.db.item(id=row["id"]).amount)+","
                             +str(ns.db.item(id=row["id"]).ownstock)
                             +")", theme="d")
    else:
      ns.db.item.id.label = T("No.")
      ns.db.item.id.represent = lambda value,row: ui.control.format_value("integer",row["id"])
      response.item_icon = URL(ui.dir_images,'icon16_corrected.png')
      response.cmd_item_cancel = A(SPAN(_class="icon cross"), _id="cmd_item_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_item').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
      links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_item("
                           +str(row["id"])+","+str(row["product_id"])
                           +",'"+ns.db.product(id=row["product_id"]).description+"',"
                           +str(row["tax_id"])+","
                           +str(ns.db.tax(id=row["tax_id"]).rate)+","
                           +str(row["vatamount"])+","
                           +str(ns.db.currency(curr=ns.db.trans(id=trans_id).curr).digit)+",'"
                           +json.dumps(str(row["description"]))[1:-1]+"',"
                           +str(row["deposit"])+","
                           +str(row["qty"])+","
                           +str(row["discount"])+","
                           +str(row["fxprice"])+",'"
                           +str(row["unit"])+"',"
                           +str(row["netamount"])+","
                           +str(ns.db.item(id=row["id"]).amount)+","
                           +str(ns.db.item(id=row["id"]).ownstock)
                           +")",
                           _title=T("Edit item"))]
    if editable:
      if session.mobile:
        response.cmd_item_update = ui.control.get_mobil_button(label=T("Save Item"), href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
          onclick= "item_update();")
        response.cmd_item_delete = ui.control.get_mobil_button(label=T("Delete Item"), href="#", 
          cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to delete this data?')+
                              "')){if(document.getElementById('item_id').value>-1){window.location = '"
            +URL("frm_trans")+"/delete/item/'+document.getElementById('item_id').value;} else {show_page('item_page');}}")
        response.cmd_item_new = ui.control.get_mobil_button(label=T("New Item"), href="#", 
          cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
          onclick= "set_item(-1,'','','',0,0,0,'',0,0,0,0,'',0,0,0);", rel="close")
      else:
        links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this item?')+
                                "')){window.location ='"+URL("frm_trans/delete/item/"+str(row.id))+"';};return false;", 
                           _title=T("Delete Item")))
        response.cmd_item_update = ui.control.get_command_button(caption=T("Save"),title=T("Update item data"),color="008B00", _id="cmd_item_submit",
                                cmd="item_update();return true;")
        response.cmd_item_new = ui.control.get_tabnew_button(item_count,T('New Item'),cmd_id="cmd_item_new",
                                  cmd = "$('#tabs').tabs({ active: 0 });set_item(-1,'','','',0,0,0,'',0,0,0,0,'',0,0,0)")
    else:
      if session.mobile:
        response.cmd_item_new = ""
      else:
        response.cmd_item_new = SPAN(" ",SPAN(str(item_count), _class="detail_count"))
      response.cmd_item_update = ""
      response.cmd_item_delete = ""
      
    ns.db.item.deposit.label = T("Dep.")
    response.view_item = ui.select.get_tab_grid(item, ns.db.item.id, _fields=fields, _deletable=False, links=links, _editable=False,
                            multi_page="item_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id),_priority="0,3,4")
    
    response.item_form = SQLFORM(ns.db.item, submit_button=T("Save"),_id="frm_item")
    response.item_form.process()
    response.item_id = INPUT(_name="id", _type="hidden", _value="", _id="item_id")
    response.item_trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="item_trans_id")
    response.item_product_id = INPUT(_name="product_id", _type="hidden", _value="", _id="product_id")
    response.item_product_control=ui.select.get_product_selector("")
    response.item_rate = INPUT(_name="rate", _type="hidden", _value=0, _id="item_rate")
    response.item_vatamount = INPUT(_name="vatamount", _type="hidden", _value=0, _id="item_vatamount")
    if transtype=="offer":
      response.item_form.custom.label.deposit = T('Option')
      response.item_form.custom.label.ownstock = T('Group')
    else:
      response.item_form.custom.label.deposit = T('Deposit')
    if transtype in("order","worksheet","rent"):
      response.item_deposit = False
    response.item_digit = INPUT(_name="digit", _type="hidden", _value=ns.db.currency(curr=ns.db.trans(id=trans_id).curr).digit, _id="curr_digit")
    response.item_form.custom.widget.qty["_onblur"]= "load_price();calc_price('fxprice');"
    response.item_form.custom.widget.discount["_onblur"]="if(parseFloat(this.value)>100){this.value=100;};if(parseFloat(this.value)<0){this.value=0;};calc_price('fxprice');"
    response.item_form.custom.widget.fxprice["_onblur"]="calc_price('fxprice');"
    response.item_form.custom.widget.tax_id["_onblur"]="if(this.selectedIndex==0){this.selectedIndex=1};document.getElementById('item_rate').value=rate_lst[this.selectedIndex-1];calc_price('fxprice');"
    response.item_rate_lst = str([row.rate for row in ns.db().select(ns.db.tax.rate, orderby=ns.db.tax.taxcode)]).replace("[","").replace("]","")
    response.item_form.custom.widget.netamount["_onblur"]="calc_price('netamount');"
    response.item_form.custom.widget.amount["_onblur"]="calc_price('amount');"
  
  response.menu_payment = ""
  if trans_id>-1 and transtype in("bank"):
    #payment data
    payment = ((ns.db.payment.trans_id==trans_id)&(ns.db.payment.deleted==0))
    payment_count = ns.db(payment).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    ns.db.payment.id.label = T("Item No.")
    ns.db.payment.id.represent = lambda value,row: ui.control.format_value("integer",row["id"])
    ns.db.payment.paiddate.label = T("Payment Date")
    
    if session.mobile:
      links = None
      response.menu_payment = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Items"),payment_count), 
        href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('payment_page');", theme="a", rel="close")
      response.cmd_payment_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
          icon="back", ajax="true", theme="a",  
          onclick= "show_page('payment_page');", rel="close")
      fields=[ns.db.payment.trans_id, ns.db.payment.id, ns.db.payment.paiddate, ns.db.payment.amount, ns.db.payment.notes]
      ns.db.payment.trans_id.label = T("*")
      ns.db.payment.trans_id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, icon="edit", style="text-align: left;",
                            onclick="set_payment("
                             +str(row["id"])+",'"
                             +str(row["paiddate"])+"',"
                             +str(row["amount"])+",'"
                             +json.dumps(str(row["notes"]))[1:-1]+"')", theme="d")
    else:
      response.payment_icon = URL(ui.dir_images,'icon16_corrected.png')
      response.cmd_payment_cancel = A(SPAN(_class="icon cross"), _id="cmd_payment_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_payment').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
      fields=[ns.db.payment.id, ns.db.payment.paiddate, ns.db.payment.amount, ns.db.payment.notes]
      links = [lambda row: A(SPAN(_class="icon plus"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#",
                         _onclick = "$('#tabs').tabs({ active: 2 });set_link_invoice(-1,"+str(row.id)+",'','','',"+str(row["amount"])+",1);",
                         _title=T("Link Invoice")),
             lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_payment("
                           +str(row["id"])+",'"
                           +str(row["paiddate"])+"',"
                           +str(row["amount"])+",'"
                           +json.dumps(str(row["notes"]))[1:-1]+"')",
                           _title=T("Edit item"))]
    
    if editable:
      if session.mobile:
        response.cmd_payment_delete = ui.control.get_mobil_button(label=T("Delete Item"), href="#", 
          cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to delete this data?')+
                              "')){if(document.getElementById('payment_id').value>-1){window.location = '"
            +URL("frm_trans")+"/delete/payment/'+document.getElementById('payment_id').value;} else {show_page('payment_page');}}")
        response.cmd_link_new = ui.control.get_mobil_button(label=T("Link Invoice"), href="#", 
          cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
          onclick= "set_link_invoice(-1,document.getElementById('payment_id').value,'','','',document.getElementById('payment_amount').value,1);", rel="close")
        
        response.cmd_payment_update = ui.control.get_mobil_button(label=T("Save Item"), href="#", 
            cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
            onclick= "payment_update();")
        response.cmd_payment_new = ui.control.get_mobil_button(
            label=T("New Item"), href="#", 
            cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
            onclick= "set_payment(-1,'"+str(datetime.datetime.now().date())+"',0,'');", 
            rel="close")
      else:
        links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this item?')+
                              "')){window.location ='"+URL("frm_trans/delete/payment/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Item")))
        response.cmd_payment_update = ui.control.get_command_button(caption=T("Save"),title=T("Update item data"),color="008B00", _id="cmd_payment_submit",
                              cmd="payment_update();return true;")
        response.cmd_payment_new = ui.control.get_tabnew_button(payment_count,T('New Item'),cmd_id="cmd_item_new",
                                cmd = "$('#tabs').tabs({ active: 0 });set_payment(-1,'"+str(datetime.datetime.now().date())+"',0,'')")
    else:
      if session.mobile:
        response.cmd_payment_new = ""
      else:
        response.cmd_payment_new = SPAN(" ",SPAN(str(payment_count), _class="detail_count"))
      response.cmd_payment_update = ""
      response.cmd_payment_delete = ""
      response.cmd_payment_close = ""
      response.cmd_link_new = ""
      
    response.view_payment = ui.select.get_tab_grid(payment, ns.db.payment.id, _fields=fields, _deletable=False, _editable=False, links=links, 
                                          multi_page="payment_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id),_priority="0,1,2")
    
    response.payment_form = SQLFORM(ns.db.payment, submit_button=T("Save"),_id="frm_payment")
    response.payment_form.process()
    response.payment_id = INPUT(_name="id", _type="hidden", _value="", _id="payment_id")
    response.payment_trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="payment_trans_id")
    
  response.menu_link_invoice = ""
  if trans_id>-1 and transtype in("cash","bank"):
    #link invoice
    invoice_audit_filter = ui.connect.get_audit_filter("trans", "invoice")[0]
    if invoice_audit_filter!="disabled":
      nervatype_trans = ns.valid.get_groups_id("nervatype", "trans")
      nervatype_payment = ns.valid.get_groups_id("nervatype", "payment")
      
      link_qty = ns.db.fieldvalue.with_alias('link_qty')
      link_rate = ns.db.fieldvalue.with_alias('link_rate')
  
      join = [(ns.db.payment.on((ns.db.link.ref_id_1==ns.db.payment.id)&(ns.db.payment.deleted==0))),
              (ns.db.trans.on((ns.db.link.ref_id_2==ns.db.trans.id))),
              (link_qty.on((ns.db.link.id==link_qty.ref_id)&(link_qty.fieldname=="link_qty")&(link_qty.deleted==0))),
              (link_rate.on((ns.db.link.id==link_rate.ref_id)&(link_rate.fieldname=="link_rate")&(link_rate.deleted==0)))]
      query = ((ns.db.link.deleted==0)&(ns.db.link.nervatype_1==nervatype_payment)
               &(ns.db.link.nervatype_2==nervatype_trans)&(ns.db.payment.trans_id==trans_id))
      inv_count = ns.db(query).select('count(*)',join=join,left=None, cacheable=True).first()['count(*)']
      
      if session.mobile:
        links = None
        response.menu_link_invoice = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Invoices"),inv_count), 
          href="#", cformat=None, icon="grid", style="text-align: left;",
          onclick= "show_page('link_page');", theme="a", rel="close")
        response.cmd_link_invoice_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
            icon="back", ajax="true", theme="a",  
            onclick= "show_page('link_page');", rel="close")
        fields = [ns.db.link.id, ns.db.link.ref_id_2, link_qty.value, link_rate.value]
        ns.db.link.id.label = T("*")
        ns.db.link.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, icon="edit", style="text-align: left;",
                            onclick="set_link_invoice("
                             +str(row["link"]["id"])+","
                             +str(ns.db.link(id=row["link"]["id"]).ref_id_1)+","
                             +str(row["link"]["ref_id_2"])+",'"
                             +ns.db.trans(id=row["link"]["ref_id_2"]).transnumber+"','"
                             +ns.db.trans(id=row["link"]["ref_id_2"]).curr+"',"
                             +row["link_qty"]["value"]+","
                             +row["link_rate"]["value"]
                             +")", theme="d")
      else:
        response.link_invoice_icon = URL(ui.dir_images,'icon16_link_edit.png')
        response.cmd_link_invoice_cancel = A(SPAN(_class="icon cross"), _id="cmd_link_invoice_cancel", 
          _style="height: 15px;",
          _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
          _onclick= "document.getElementById('edit_link_invoice').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")      
        fields = [ns.db.link.ref_id_2, link_qty.value, link_rate.value]
        links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_link_invoice("
                           +str(row["link"]["id"])+","
                           +str(ns.db.link(id=row["link"]["id"]).ref_id_1)+","
                           +str(row["link"]["ref_id_2"])+",'"
                           +ns.db.trans(id=row["link"]["ref_id_2"]).transnumber+"','"
                           +ns.db.trans(id=row["link"]["ref_id_2"]).curr+"',"
                           +row["link_qty"]["value"]+","
                           +row["link_rate"]["value"]
                           +")",
                           _title=T("Edit link"))]
      
      ns.db.link.ref_id_2.label = T("Invoice No.")
      link_qty.value.label = T("Amount")
      link_rate.value.label = T("Rate")
      link_qty.value.represent = lambda value,row: ui.control.format_value("number",row["link_qty"]["value"])
      link_rate.value.represent = lambda value,row: ui.control.format_value("number",row["link_rate"]["value"])
      ns.db.link.ref_id_2.represent = lambda value,row: A(SPAN(ns.valid.show_refnumber("refnumber", "trans", value, "transnumber")),
                     _href=URL(r=request, f="frm_trans/view/trans/"+str(value)), _target="_blank")
      
      if editable:
        if session.mobile:
          response.cmd_link_invoice_update = ui.control.get_mobil_button(label=T("Save data"), href="#", 
            cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
            onclick= "link_invoice_update();")
          response.cmd_link_invoice_delete = ui.control.get_mobil_button(label=T("Delete Item"), href="#", 
            cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
            onclick= "if(confirm('"+T('Are you sure you want to delete this data?')+
                              "')){if(document.getElementById('link_invoice_id').value>-1){window.location = '"
            +URL("frm_trans")+"/delete/link/'+document.getElementById('link_invoice_id').value;} else {show_page('link_page');}}")
        else:
          response.cmd_link_invoice_update = ui.control.get_command_button(caption=T("Save"),title=T("Update data"),color="008B00", _id="cmd_link_invoice_submit",
                                cmd="link_invoice_update();return true;")
          links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this link?')+
                                "')){window.location ='"+URL("frm_trans/delete/link/"+str(row["link"]["id"]))+"';};return false;", 
                           _title=T("Delete link")))
        if transtype=="bank":
          ns.db.link.ref_id_1.label = T("Item No.")
          ns.db.link.ref_id_1.represent = lambda value,row: ui.control.format_value("integer",row["ref_id_1"])
          if session.mobile:
            fields.insert(1,ns.db.link.ref_id_1)
          else:
            fields.insert(0,ns.db.link.ref_id_1)
      else:
        response.cmd_link_invoice_update = ""
        response.cmd_link_invoice_close = ""
        response.cmd_link_invoice_delete = ""
    
      
      if inv_count>0:  
        response.view_link_invoice = ui.select.get_tab_grid(query, ns.db.link.id, _fields=fields, _deletable=False, _editable=False, links=links, 
                                          multi_page="link_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id),_join=join,_priority="0,1,2")
      else:
        response.view_link_invoice = ""
      
      if editable and transtype=="cash":
        if ns.db.payment(trans_id=trans_id):
          if session.mobile:
            response.cmd_link_invoice_new = ui.control.get_mobil_button(
              label=T("New link"), href="#", 
              cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
              onclick= "set_link_invoice(-1,"+str(ns.db.payment(trans_id=trans_id).id)+",'','','',"+str(ns.db.payment(trans_id=trans_id).amount)+",1);", 
              rel="close")
          else:
            response.cmd_link_invoice_new = ui.control.get_tabnew_button(inv_count,T('New link'),cmd_id="cmd_link_invoice_new",
                                  cmd = "$('#tabs').tabs({ active: 1 });set_link_invoice(-1,"+str(ns.db.payment(trans_id=trans_id).id)+",'','','',"+str(ns.db.payment(trans_id=trans_id).amount)+",1);")
        else:
          response.cmd_link_invoice_new = ""
      else:
        if session.mobile:
          response.cmd_link_invoice_new = ""
        else:
          response.cmd_link_invoice_new = SPAN(" ",SPAN(str(inv_count), _class="detail_count"))
      
      response.link_invoice_form = SQLFORM(ns.db.link, submit_button=T("Save"),_id="frm_link_invoice")
      response.link_invoice_form.process()
      response.link_invoice_id = INPUT(_name="id", _type="hidden", _value="", _id="link_invoice_id")
      response.link_invoice_trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="link_invoice_trans_id")
      response.link_invoice_nervatype_1 = INPUT(_name="nervatype_1", _type="hidden", _value=nervatype_payment, _id="nervatype_1")
      response.link_invoice_nervatype_2 = INPUT(_name="nervatype_2", _type="hidden", _value=nervatype_trans, _id="nervatype_2")
      response.link_invoice_linktype = INPUT(_name="linktype", _type="hidden", _value=0, _id="linktype")
      response.link_invoice_ref_id_1 = INPUT(_name="ref_id_1", _type="hidden", _value="", _id="ref_id_1")
      response.link_invoice_ref_id_2 = INPUT(_name="ref_id_2", _type="hidden", _value="", _id="ref_id_2")
      response.link_invoice_transitem_selector = ui.select.get_base_selector(
                            fieldtype="transitem", search_url=URL("dlg_transitem_invoice"),
                            label_id="link_transnumber",
                            label_url="'"+URL("frm_trans/view/trans/")+"'+document.getElementById('ref_id_2').value",
                            label_txt="")
      response.link_invoice_curr = DIV("", _id="link_curr", _class="label_disabled", _style="width: 35px;text-align: center;")
      response.link_invoice_amount = INPUT(_name="amount", _type="text", _value="", _id="link_amount", _class="double")
      response.link_invoice_rate = INPUT(_name="rate", _type="text", _value="", _id="link_rate", _class="double")
    else:
      response.view_link_invoice = ""
      response.invoice_disabled=True
  
  response.menu_link_payment = ""
  if trans_id>-1 and transtype in("invoice","receipt"):
    #payment data
    nervatype_payment = ns.valid.get_groups_id("nervatype", "payment")   
    link_qty = ns.db.fieldvalue.with_alias('link_qty')
    link_rate = ns.db.fieldvalue.with_alias('link_rate')
    
    join = [(ns.db.payment.on((ns.db.link.ref_id_1==ns.db.payment.id)&(ns.db.payment.deleted==0))),
            (ns.db.trans.on((ns.db.payment.trans_id==ns.db.trans.id))),
            (ns.db.place.on((ns.db.trans.place_id==ns.db.place.id))),
            (link_qty.on((ns.db.link.id==link_qty.ref_id)&(link_qty.fieldname=="link_qty")&(link_qty.deleted==0))),
            (link_rate.on((ns.db.link.id==link_rate.ref_id)&(link_rate.fieldname=="link_rate")&(link_rate.deleted==0)))]
    query = ((ns.db.link.deleted==0)&(ns.db.link.nervatype_1==nervatype_payment)
             &(ns.db.link.nervatype_2==nervatype_trans)&(ns.db.link.ref_id_2==trans_id))
    
    payment_count = ns.db(query).select('count(*)',join=join,left=None, cacheable=True).first()['count(*)']
    
    if session.mobile:
      links = None
      response.menu_link_payment = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Payments"),payment_count), 
        href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('link_page');", theme="a", rel="close")
      response.cmd_link_payment_close = ui.control.get_mobil_button(label=T("BACK"), href="#",
          icon="back", ajax="true", theme="a",  
          onclick= "show_page('link_page');", rel="close")
      fields=[ns.db.payment.id, ns.db.trans.id, ns.db.payment.paiddate, ns.db.trans.place_id, ns.db.payment.trans_id,
              ns.db.place.curr, link_qty.value, link_rate.value]
      ns.db.payment.id.label = T("*")
      ns.db.payment.id.represent = lambda value,row: ui.control.get_mobil_button(T("Edit"), href="#", cformat=None, icon="edit", style="text-align: left;",
                            onclick="set_link_invoice("
                           +str(row["link"]["id"])+","
                           +str(ns.db.link(id=row["link"]["id"]).ref_id_1)+","
                           +str(ns.db.link(id=row["link"]["id"]).ref_id_2)+",'"
                           +ns.db.trans(id=row["payment"]["trans_id"]).transnumber+"','"
                           +row["place"]["curr"]+"',"
                           +row["link_qty"]["value"]+","
                           +row["link_rate"]["value"]
                           +")", theme="d")
    else:
      response.link_invoice_icon = URL(ui.dir_images,'icon16_link_edit.png')
      response.cmd_link_invoice_cancel = A(SPAN(_class="icon cross"), _id="cmd_link_invoice_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_link_invoice').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
      fields=[ns.db.trans.id, ns.db.payment.paiddate, ns.db.trans.place_id, ns.db.payment.trans_id, ns.db.payment.id,
            ns.db.place.curr, link_qty.value, link_rate.value]
      ns.db.payment.id.label = T("Item No.")
      ns.db.payment.id.represent = lambda value,row: ui.control.format_value("integer",row["payment"]["id"])
      links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="set_link_invoice("
                         +str(row["link"]["id"])+","
                         +str(ns.db.link(id=row["link"]["id"]).ref_id_1)+","
                         +str(ns.db.link(id=row["link"]["id"]).ref_id_2)+",'"
                         +ns.db.trans(id=row["payment"]["trans_id"]).transnumber+"','"
                         +row["place"]["curr"]+"',"
                         +row["link_qty"]["value"]+","
                         +row["link_rate"]["value"]
                         +")",
                         _title=T("Edit link"))]
    
    ns.db.payment.paiddate.label = T("Payment Date")
    ns.db.trans.place_id.label = T("Bank/Checkout")
    link_qty.value.label = T("Amount")
    link_rate.value.label = T("Rate")
    link_qty.value.represent = lambda value,row: ui.control.format_value("number",row["link_qty"]["value"])
    link_rate.value.represent = lambda value,row: ui.control.format_value("number",row["link_rate"]["value"])
    
    if editable:
      if session.mobile:
        response.cmd_link_payment_update = ui.control.get_mobil_button(label=T("Save link"), href="#", 
            cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
            onclick= "link_invoice_update();return true;")
        response.cmd_link_payment_new = ui.control.get_mobil_button(
            label=T("New link"), href="#", 
            cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
            onclick= "set_link_invoice(-1,'',"+str(trans_id)+",'','',0,1);", 
            rel="close")
        response.cmd_link_payment_delete = ui.control.get_mobil_button(label=T("Delete link"), href="#", 
          cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
          onclick= "if(confirm('"+T('Are you sure you want to delete this data?')+
                              "')){if(document.getElementById('link_invoice_id').value>-1){window.location = '"
            +URL("frm_trans")+"/delete/link/'+document.getElementById('link_invoice_id').value;} else {show_page('link_page');}}")
      else:
        response.cmd_link_payment_update = ui.control.get_command_button(caption=T("Save"),title=T("Update data"),color="008B00", _id="cmd_link_invoice_submit",
                              cmd="link_invoice_update();return true;")
        response.cmd_link_payment_new = ui.control.get_tabnew_button(payment_count,T('New link'),cmd_id="cmd_payment_new",
                                cmd = "$('#tabs').tabs({ active: 2 });set_link_invoice(-1,'',"+str(trans_id)+",'','',0,1)")
        links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this link?')+
                              "')){window.location ='"+URL("frm_trans/delete/link/"+str(row["link"]["id"]))+"';};return false;", 
                         _title=T("Delete link")))
    else:
      if session.mobile:
        response.cmd_link_payment_new = ""
      else:
        response.cmd_link_payment_new = SPAN(" ",SPAN(str(payment_count), _class="detail_count"))
      response.cmd_link_payment_update = ""
      response.cmd_link_payment_close = ""
      response.cmd_link_payment_delete = ""
    
    response.view_payment = ui.select.get_tab_grid(query, ns.db.link.id, _fields=fields, _deletable=False, _editable=False, links=links, 
                                        multi_page="link_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id),_join=join,_priority="0,1,3")
    
    response.link_invoice_form = SQLFORM(ns.db.link, submit_button=T("Save"),_id="frm_link_invoice")
    response.link_invoice_form.process()
    response.link_invoice_id = INPUT(_name="id", _type="hidden", _value="", _id="link_invoice_id")
    response.link_invoice_trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="link_invoice_trans_id")
    response.link_invoice_nervatype_1 = INPUT(_name="nervatype_1", _type="hidden", _value=nervatype_payment, _id="nervatype_1")
    response.link_invoice_nervatype_2 = INPUT(_name="nervatype_2", _type="hidden", _value=nervatype_trans, _id="nervatype_2")
    response.link_invoice_linktype = INPUT(_name="linktype", _type="hidden", _value=0, _id="linktype")
    response.link_invoice_ref_id_1 = INPUT(_name="ref_id_1", _type="hidden", _value="", _id="ref_id_1")
    response.link_invoice_ref_id_2 = INPUT(_name="ref_id_2", _type="hidden", _value="", _id="ref_id_2")
    response.link_invoice_payment_selector = ui.select.get_base_selector(
                          fieldtype="payment", search_url=URL("dlg_payment_all"),
                          label_id="link_transnumber",
                          label_url="'"+URL("frm_trans/view/payment/")+"'+document.getElementById('ref_id_1').value", 
                          label_txt="")
    response.link_invoice_curr = DIV("", _id="link_curr", _class="label_disabled", _style="width: 35px;text-align: center;")
    response.link_invoice_amount = INPUT(_name="amount", _type="text", _value="", _id="link_amount", _class="double")
    response.link_invoice_rate = INPUT(_name="rate", _type="text", _value="", _id="link_rate", _class="double")
          
  response.menu_inventory = ""
  response.menu_invoice = ""
  if trans_id>-1 and transtype in("order","worksheet","rent"):
    #invoice
    invoice_audit_filter = ui.connect.get_audit_filter("trans", "invoice")[0]
    if invoice_audit_filter!="disabled":
      invoice_transtype_id = ns.valid.get_groups_id("transtype", "invoice")
      receipt_transtype_id = ns.valid.get_groups_id("transtype", "receipt")
      
      query = ((ns.db.link.ref_id_2==trans_id)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0)
                &(ns.db.link.nervatype_2==nervatype_trans)&(ns.db.link.ref_id_1==ns.db.trans.id)&(ns.db.trans.deleted==0)
                &((ns.db.trans.transtype==invoice_transtype_id)|(ns.db.trans.transtype==receipt_transtype_id))
                &(ns.db.trans.id==ns.db.item.trans_id)&(ns.db.item.deleted==0))
      inv_count = ns.db(query).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
      
      if session.mobile:
        response.menu_invoice = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Invoices"),inv_count), 
          href="#", cformat=None, icon="grid", style="text-align: left;",
          onclick= "show_page('invoice_page');", theme="a", rel="close")
        fields=[ns.db.item.trans_id, ns.db.item.description, ns.db.item.qty, ns.db.item.deposit, ns.db.trans.transdate, ns.db.trans.curr, ns.db.item.amount]
        ns.db.item.trans_id.represent = lambda value,row: ui.control.get_mobil_button(
          ns.db.trans(id=value).transnumber, href=URL('frm_trans/edit/trans/')+str(value), target="_blank",
          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
      else:
        fields=[ns.db.item.deposit, ns.db.item.trans_id, ns.db.trans.transdate, ns.db.item.description, ns.db.item.qty, ns.db.trans.curr, ns.db.item.amount]
      
      ns.db.item.trans_id.label = T("Invoice No.")
      ns.db.trans.transdate.label = T("Invoice Date")
      ns.db.item.deposit.readable = ns.db.item.deposit.writable = True
      ns.db.item.deposit.label = T("Deposit")
      
      if inv_count>0:  
        response.view_invoice = ui.select.get_tab_grid(query, ns.db.item.id, _fields=fields, _deletable=False, _editable=False, links=None, 
                                          multi_page="invoice_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id),_priority="0,1,2")
      else:
        response.view_invoice = ""
      
      if not session.mobile:
        if editable:
          response.cmd_invoice_new = DIV(DIV(ui.select.dlg_create_trans(trans_id), _id="popup_create_trans2", _title=T("Create a new document type"), 
                                      _style="display: none;"),
                                         ui.control.get_tabnew_button(inv_count,T('New Invoice'),cmd_id="cmd_invoice",
                                      cmd='$("#popup_create_trans2").dialog({dialogClass: "n2py-dialog", modal: true, minWidth: 440, resizable: false});'),
                                      _style="display: inline;") 
        else:
          response.cmd_invoice_new = SPAN(" ",SPAN(str(inv_count), _class="detail_count"))
    else:
      response.view_invoice = ""
      response.invoice_disabled=True
      
    #delivery
    delivery_audit_filter = ui.connect.get_audit_filter("trans", "delivery")[0]
    if delivery_audit_filter!="disabled":
      movement_nervatype_id = ns.valid.get_groups_id("nervatype", "movement")
      item_nervatype_id = ns.valid.get_groups_id("nervatype", "item")
      
      query = ((ns.db.item.trans_id==trans_id)&(ns.db.item.deleted==0)&
               (ns.db.link.nervatype_2==item_nervatype_id)&(ns.db.link.ref_id_2==ns.db.item.id)&
               (ns.db.item.product_id==ns.db.product.id)&
               (ns.db.link.nervatype_1==movement_nervatype_id)&(ns.db.link.ref_id_1==ns.db.movement.id)
               &(ns.db.link.deleted==0)&(ns.db.movement.deleted==0))
      
      if session.mobile:
        response.menu_inventory = ui.control.get_mobil_button(T("Shipping"), 
          href="#", cformat=None, icon="grid", style="text-align: left;",
          onclick= "show_page('inventory_page');", theme="a", rel="close")
      fields=[ns.db.item.product_id, ns.db.movement.product_id, ns.db.movement.qty]
      ns.db.item.product_id.label = T("Item Product")
      ns.db.movement.product_id.label = T("Shipping Product")
      ns.db.movement.qty.label = T("Shipping Qty")
      
      groupfields=[ns.db.item.product_id,ns.db.movement.product_id,ns.db.movement.qty.sum().with_alias('qty')]
      groupby=[ns.db.item.product_id|ns.db.product.description|ns.db.movement.product_id]
      
      request.vars.page = request.vars["inventory_page"]          
      response.view_inventory = SimpleGrid.grid(query=query, field_id=ns.db.movement.product_id, 
                 fields=fields, groupfields=groupfields, groupby=groupby, args=["view/trans/"+str(trans_id)],
                 orderby=ns.db.item.id, sortable=False, paginate=25, pagename="inventory_page", maxtextlength=25,
                 showbuttontext=False, editable=False, links=None)
      table = response.view_inventory.elements("div.web2py_table")
      if len(table)==0:
        response.view_inventory = ""
      elif type(table[0][0][0]).__name__!="TABLE":
        response.view_inventory = ""
      else:
        if session.mobile:
          ui.control.set_htmltable_style(table[0][0][0],"inventory_page","1,2")
        if response.view_inventory[len(response.view_inventory)-1]["_class"].startswith("web2py_paginator"):
          pages = response.view_inventory[len(response.view_inventory)-1].elements("a")
          for i in range(len(pages)):
            if pages[i]["_href"]:
              pages[i]["_href"] = pages[i]["_href"].replace("/frm_trans","/frm_trans/view/trans/"+str(trans_id)).replace("page=","inventory_page=")
              pages[i]["_data-ajax"] = "false"
        response.view_inventory.__delitem__(0)
      
      if editable and delivery_audit_filter=="all":
        if session.mobile:
          response.cmd_inventory_edit = ui.control.get_mobil_button(label=T("Edit Shipping"), href="#", 
            icon="edit", cformat=None, ajax="true", theme="b", rel="close",
            onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
              +"')){window.location ='"+URL("frm_shipping/view/trans/"+str(trans_id))+"';};return false;")
        else:
          response.cmd_inventory_edit = ui.control.get_tabedit_button(title=T('Edit Shipping'), cmd_id="cmd_inventory", 
                                      cmd="javascript:window.location='"+URL("frm_shipping/view/trans/"+str(trans_id))+"';")
      else:
        response.cmd_inventory_edit = ""
    else:
      response.view_inventory = ""
      response.inventory_disabled=True
  
  response.menu_tool = ""
  if trans_id>-1 and transtype in("order","worksheet","rent","invoice","receipt"):
    #tool movement
    movement_audit_filter = ui.connect.get_audit_filter("trans", "waybill")[0]
    if movement_audit_filter!="disabled":
      transtype_waybill = ns.valid.get_groups_id("transtype", "waybill")    
      ns.db.movement.notes.label = T('Additional info')
      ns.db.movement.trans_id.label = T('Movement No.')
      too = ((ns.db.trans.deleted==0)&(ns.db.trans.id==ns.db.movement.trans_id)
             &(ns.db.trans.transtype==transtype_waybill)
             &(ns.db.trans.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0)
             &(ns.db.link.nervatype_2==nervatype_trans)&(ns.db.link.ref_id_2==trans_id))
      too_count = ns.db(too).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
      fields = [ns.db.movement.trans_id, ns.db.trans.crdate,ns.db.trans.direction,
                ns.db.movement.shippingdate,ns.db.movement.tool_id,ns.db.tool.description,ns.db.movement.notes,
                ns.db.trans.transtate]
      
      if session.mobile:
        response.menu_tool= ui.control.get_mobil_button(ui.control.get_bubble_label(T("Tool Movements"),too_count), 
          href="#", cformat=None, icon="grid", style="text-align: left;",
          onclick= "show_page('tool_page');", theme="a", rel="close")
        ns.db.movement.trans_id.represent = lambda value,row: ui.control.get_mobil_button(
          ns.db.trans(id=value).transnumber, href=URL('frm_trans/edit/trans/')+str(value), target="_blank",
          cformat=None, icon=None, iconpos=None, style="text-align: left;", ajax="false")
      
      if editable and movement_audit_filter=="all":
        if session.mobile:
          response.cmd_movement_new = ui.control.get_mobil_button(
            label=T("New Movement"), href="#", 
            cformat=None, style="text-align: left;", icon="plus", ajax="false", theme="b",
            onclick= "window.open('"+URL("frm_trans/new/trans/waybill/out")+"?init_refnumber_type=trans&init_trans_id="+str(trans_id)+"', '_blank');", 
            rel="close")
        else:
          response.cmd_movement_new = ui.control.get_tabnew_button(too_count,T('New Movement'),cmd_id="", 
                                      cmd="javascript:window.open('"+URL("frm_trans/new/trans/waybill/out")+"?init_refnumber_type=trans&init_trans_id="+str(trans_id)+"', '_blank');")
      else:
        if session.mobile:
          response.cmd_movement_new = ""
        else:
          response.cmd_movement_new = SPAN(" ",SPAN(str(too_count), _class="detail_count"))
      
      response.view_too = ui.select.get_tab_grid(too, ns.db.movement.id, _fields=fields, _deletable=False, _editable=False, links=None, 
                                          multi_page="tool_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id),_priority="0,4")
    else:
      response.view_too = ""
      response.movement_disabled=True
    
  #show trans groups list
  response.menu_fields = ""
  response.menu_groups = ""
  if trans_id>-1:
    trans_groups = ((ns.db.link.ref_id_1==trans_id)&(ns.db.link.nervatype_1==nervatype_trans)&
            (ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.deleted==0))
    ns.db.link.ref_id_2.represent = lambda value,row: ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")
    ns.db.link.nervatype_1.readable = ns.db.link.ref_id_1.readable = ns.db.link.nervatype_2.readable = ns.db.link.linktype.readable = ns.db.link.deleted.readable = False
    ns.db.link.ref_id_2.label = T('Groups')
    groups_count = ns.db(trans_groups).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    
    if session.mobile:
      response.menu_groups = ui.control.get_mobil_button(ui.control.get_bubble_label(T("Document Groups"),groups_count), 
        href="#", cformat=None, icon="star", style="text-align: left;",
        onclick= "show_page('groups_page');", theme="a", rel="close")
      if transtype_audit_filter[0] not in ("readonly","disabled"):
        ns.db.link.id.label=T("Delete")
        ns.db.link.id.represent = lambda value,row: ui.control.get_mobil_button(T("Delete"), href="#", cformat=None, icon="delete", iconpos="notext",
          onclick="if(confirm(w2p_ajax_confirm_message||'"+T("Are you sure you want to delete this object?")
            +"')){ajax('"+URL('frm_trans/delete/link')+"/"+str(row["id"])
            +"',[],'');jQuery(this).closest('tr').remove();};var e = arguments[0] || window.event; e.cancelBubble=true; if (e.stopPropagation) {e.stopPropagation(); e.stopImmediatePropagation(); e.preventDefault();}", 
          theme="d")
      else:
        ns.db.link.id.readable = ns.db.link.id.writable = False
    else:
      ns.db.link.id.readable = ns.db.link.id.writable = False
    
    response.view_trans_groups = ui.select.get_tab_grid(trans_groups, ns.db.link.id, _fields=None, _editable=False,
                                     _deletable=(transtype_audit_filter[0] not in ("readonly","disabled")), links=None, 
                                    multi_page="groups_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id))
    
    #show add/remove trans groups combo and setting button
    response.cmb_groups = ui.control.get_cmb_groups("trans")
    if transtype_audit_filter[0] in ("readonly","disabled"):
      response.cmd_groups_add = ""
      response.cmb_groups = ""
    else:
      if session.mobile:
        response.cmd_groups_add = ui.control.get_mobil_button(label=T("Add to Group"), href="#", 
          icon="plus", cformat=None, ajax="true", theme="b",
          onclick= "var group_id = document.getElementById('cmb_groups').value;if(group_id!=''){window.location ='"+URL("frm_trans/new/link")
           +"?refnumber="+str(trans_id)+"&groups_id='+group_id;} else {alert('"+T('Missing Document Group!')+"');return false;}")
      else:                          
        response.cmd_groups_add = ui.control.get_icon_button(T('Add to Group'),"cmd_groups_add", 
          cmd="var group_id = document.getElementById('cmb_groups').value;if(group_id!=''){window.location ='"+URL("frm_trans/new/link")
          +"?refnumber="+str(trans_id)+"&groups_id='+group_id;} else {alert('"+T('Missing Transaction Group!')+"');return false;}")
    
    if setting_audit_filter in ("disabled"):
      response.cmd_groups = ""
    else:
      if session.mobile:
        response.cmd_groups = ui.control.get_mobil_button(label=T("Edit Groups"), href="#", 
          icon="gear", cformat=None, ajax="true", theme="b", rel="close",
          onclick= "javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
              +"')){window.location ='"+URL("frm_groups_trans?back=1")+"';};return false;")
      else:
        response.cmd_groups = ui.control.get_goprop_button(title=T("Edit Transaction Groups"), url=URL("frm_groups_trans?back=1"))
        
    #additional fields data
    query = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
             &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_trans)&(ns.db.fieldvalue.ref_id==trans_id))
    ui.select.set_view_fields("trans", nervatype_trans, 1, editable, query, trans_id, "/frm_trans", "/frm_trans/view/trans/"+str(trans_id))
  else:
    response.view_trans_groups=None
    response.view_fields=None
    
  if session.mobile:
    response.state_ico = DIV(SPAN(_class="ui-icon ui-icon-edit ui-icon-shadow"),
                               _align="center", _style="padding:9px;background-color: #008B00;")
    if response.deleted==1:
      if response.transcast=="cancellation":
        form.custom.submit = DIV(SPAN(T('CANCELLATION')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding: 9px;")
      else:
        form.custom.submit = DIV(SPAN(T('DELETED')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding: 9px;")
      response.state_ico = DIV(SPAN(_class="ui-icon ui-icon-lock ui-icon-shadow"),
                                 _align="center", _style="padding:9px;background-color: red;")
    elif response.closed==1:
      form.custom.submit = DIV(SPAN(T('CLOSED')),_style="background-color: #D9D9D9;color: #505050;text-align: center;font-weight: bold;padding: 9px;")
      response.state_ico = DIV(SPAN(_class="ui-icon ui-icon-lock ui-icon-shadow"),
                                 _align="center", _style="padding:9px;background-color: #393939;")
    elif transtype_audit_filter[0] in ("readonly","disabled"):
      form.custom.submit = ""
    else:
      form.custom.submit = ui.control.get_mobil_button(label=T("Save"), href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
          onclick= "document.forms['frm_trans'].submit();")
  else:
    response.state_ico = DIV(IMG(_style="vertical-align: top;padding-top:6px;", _height="16px", _width="16px", _src=URL(ui.dir_images,'icon16_lock_edit.png')),
                               _align="center", _style="width: 30px;height: 30px;background-color: #008B00;padding: 0px;padding-left: 2px;")
    if response.deleted==1:
      if response.transcast=="cancellation":
        form.custom.submit = DIV(SPAN(T('CANCELLATION')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
      else:
        form.custom.submit = DIV(SPAN(T('DELETED')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
      response.state_ico = DIV(IMG(_style="vertical-align: top;padding-top:6px;", _height="16px", _width="16px", _src=URL(ui.dir_images,'icon16_lock.png')),
                               _align="center", _style="width: 30px;height: 30px;background-color: red;padding: 0px;padding-left: 2px;")
    elif response.closed==1:
      form.custom.submit = DIV(SPAN(T('CLOSED')),_style="background-color: #D9D9D9;color: #505050;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
      response.state_ico = DIV(IMG(_style="vertical-align: top;padding-top:6px;", _height="16px", _width="16px", _src=URL(ui.dir_images,'icon16_lock.png')),
                               _align="center", _style="width: 30px;height: 30px;background-color: #393939;padding: 0px;padding-left: 2px;")
    elif transtype_audit_filter[0] in ("readonly","disabled"):
      form.custom.submit = "" 
  
  if transtype_audit_filter[1]==0:
    form.custom.widget.transtate = DIV(form.custom.widget.transtate, _class="label_disabled")
    
  return dict(form=form)

@ns_auth.requires_login()
def frm_trans_fnote():
  ruri = request.wsgi.environ["REQUEST_URI"]
  trans_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  
  if request.vars.has_key("new_tmp"):
    values = {"transtype":ns.db.trans(id=trans_id)["transtype"], "description":request.vars.new_tmp, "notes":""}
    ns.connect.updateData("pattern", values=values, validate=False, insert_row=True)
    return
  
  if request.vars.has_key("def_tmp_value"):
    if request.vars.def_tmp_value=="-1":
      plst = ns.db((ns.db.pattern.description==request.vars.def_tmp_name)&(ns.db.pattern.deleted==0)
                   &(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])).select().as_list()
      if len(plst)>0:
        pattern_id = plst[0]["id"]
      else:
        return
    else:
      pattern_id = int(request.vars.def_tmp_value)
    plst = ns.db((ns.db.pattern.deleted==0)&(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])).select().as_list()
    for pitem in plst:
      values= {"id":pitem["id"]}
      values["defpattern"]=1 if pitem["id"]==pattern_id else 0
      ns.connect.updateData("pattern", values=values, validate=False, insert_row=True)
  
  if request.vars.has_key("del_tmp_value"):
    if request.vars.del_tmp_value=="-1":
      plst = ns.db((ns.db.pattern.description==request.vars.del_tmp_name)&(ns.db.pattern.deleted==0)
                   &(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])).select().as_list()
      if len(plst)>0:
        pattern_id = plst[0]["id"]
      else:
        return
    else:
      pattern_id = int(request.vars.del_tmp_value)
    ns.connect.deleteData("pattern", ref_id=pattern_id)
  
  if request.vars.has_key("save_tmp_value"):
    if request.vars.del_tmp_value=="-1":
      plst = ns.db((ns.db.pattern.description==request.vars.save_tmp_name)&(ns.db.pattern.deleted==0)
                   &(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])).select().as_list()
      if len(plst)>0:
        pattern_id = plst[0]["id"]
      else:
        return
    else:
      pattern_id = int(request.vars.save_tmp_value)
    values = {"id":pattern_id, "notes":request.vars.fnote}
    ns.connect.updateData("pattern", values=values, validate=False, insert_row=True)
    
  if request.vars.has_key("load_tmp_value"):
    if request.vars.del_tmp_value=="-1":
      plst = ns.db((ns.db.pattern.description==request.vars.load_tmp_name)&(ns.db.pattern.deleted==0)
                   &(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])).select().as_list()
      if len(plst)>0:
        pattern_id = plst[0]["id"]
      else:
        return
    else:
      pattern_id = int(request.vars.load_tmp_value)
    if ns.db.pattern(id=pattern_id)["notes"]==None:
      return ""
    else:
      return ns.db.pattern(id=pattern_id)["notes"]
  
  ns.db.trans.fnote.widget = JqueryTeWidget()
    
  response.view=ui.dir_view+'/trans_fnote.html'
  response.transnumber = ns.db.trans(id=trans_id)["transnumber"]
  response.trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="trans_id")
  
  if request.post_vars.has_key("fnote"):
    values = {"id":trans_id, "fnote":request.vars.fnote}
    ns.connect.updateData("trans", values=values, validate=False, insert_row=False)
    response.flash = T('Success update!')
  
  note_temp = ns.db((ns.db.pattern.deleted==0)&(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])
                          ).select(orderby=ns.db.pattern.description).as_list()
  plst = ns.db((ns.db.pattern.deleted==0)&(ns.db.pattern.defpattern==1)
               &(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])).select()
  if len(plst)>0:
    deftemp = str(T("Default: "))+plst[0]["description"]
  else:
    deftemp = T("No default...")
  response.cmb_temp = SELECT(*[OPTION(field["description"],_value=field["id"]) for field in note_temp], _id="cmb_temp", _title=deftemp)
  response.cmb_temp.insert(0, OPTION("", _value=""))
  response.title=T('NOTES')
  response.subtitle=response.transnumber
  response.closed=ns.db.trans(id=trans_id).closed
  response.deleted=ns.db.trans(id=trans_id).deleted
  
  form = SQLFORM(ns.db.trans, record = trans_id, submit_button=T("Save"), _id="frm_note")
  
  transtype = ns.db.groups(id=ns.db.trans(id=trans_id).transtype).groupvalue
  nervatype_audit_filter = ui.connect.get_audit_filter("trans", transtype)[0]
  if session.mobile:
    response.cmd_note_update = ui.control.get_mobil_button(label=T("Save text"), href="#", 
            cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
            onclick= "document.forms['frm_note'].submit();") 
    
    response.cmd_template_update = ui.control.get_mobil_button(label=T("Create template"), href="#", 
            cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
            onclick= "new_template();", rel="back")
    response.cmd_default_template = ui.control.get_mobil_button(label=T("Set default"), href="#", 
            cformat=None, style="text-align: left;border-radius: 0px;", icon="home", ajax="true", theme="b",
            onclick= "set_default_template();")
    response.cmd_load_template = ui.control.get_mobil_button(label=T("Load"), href="#", 
            cformat=None, style="text-align: left;", icon="refresh", ajax="true", theme="b",
            onclick= "var ctmp=document.getElementById('cmb_temp');if(ctmp.value=='')"
            +"{alert('"+T('You have chosen a template!')+"')} else {if(confirm('"+T('Do you want to load the template text?')+"'))"
            +"{loadTemplate();}};return false;")
    response.cmd_save_template = ui.control.get_mobil_button(label=T("Save template"), href="#", 
            cformat=None, style="text-align: left;", icon="check", ajax="true", theme="b",
            onclick= "save_template();")
    response.cmd_new_template = ui.control.get_mobil_button(label=T("Add a new"), href="#", 
            cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
            onclick= '$("#popup_new_template").popup("open");')
    response.cmd_delete_template = ui.control.get_mobil_button(label=T("Delete"), href="#", 
            cformat=None, style="text-align: left;", icon="trash", ajax="true", theme="b",
            onclick= "delete_template();")
    
    if nervatype_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_mobil_button(label=T("HOME"), href=URL('index'),
                                               icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
    else:
      response.cmd_back = ui.control.get_mobil_button(
          label=T("Document"), href=URL("frm_trans/view/trans/"+str(trans_id)), icon="back", cformat="ui-btn-left", ajax="false")
    response.cmd_help = ui.control.get_mobil_button(label=T("HELP"), href=URL('cmd_go_help?page=fnote'),
                                               cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
  else:
    response.titleicon = URL(ui.dir_images,'icon16_edit.png')  
    rtable = TABLE(_style="width: 100%;height:100%;background-color: #F1F1F1;")
    rtable.append(TR(TD(form.custom.submit)))
    rtable.append(TR(TD(form.custom.widget.fnote)))
    if nervatype_audit_filter in ("disabled"):
      response.cmd_back = ui.control.get_home_button()
    else:
      response.cmd_back = ui.control.get_back_button(URL("frm_trans/view/trans/"+str(trans_id)))
    response.cmd_help = ui.control.get_help_button("fnote")
                
  if nervatype_audit_filter in ("readonly","disabled") or response.deleted==1 or response.closed==1:
    form.custom.submit = ""
    response.cmd_note_update = ""
    
  return dict(form=form)
