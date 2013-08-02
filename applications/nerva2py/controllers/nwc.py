# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Project
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
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
from gluon.html import INPUT, CAT, FORM, CENTER, HTML, TITLE, BODY, LINK, HEAD
from gluon.sqlhtml import SQLFORM, DIV, SPAN, IMG, A, HTTP
from gluon.html import HR, SELECT, OPTION, XML
from gluon.html import TABLE, TR, TD, LABEL, TBODY, THEAD, TH
from gluon import LOAD
from gluon.utils import web2py_uuid
import gluon.contrib.simplejson as json

from storage import Storage #@UnresolvedImport

from nerva2py.nervastore import NervaStore
from nerva2py.localstore import setEngine
from nerva2py.tools import NervaTools, dict2obj
from nerva2py.dialog import DIALOG
from nerva2py.elrte import ElrteWidget
from nerva2py.simplegrid import SimpleGrid

import os
import datetime
import math
import base64
from StringIO import StringIO
import re

DEMO_MODE = False
appl,contr = "nerva2py","nwc"
dir_view = "nwc"
dir_images = "static/resources/application/nwc/images"
dir_help = "static/resources/application/nwc/help"

class auth_ini(object):
  def __init__(self):
    pass
  def requires_login(self):
    def decorator(action):
      def f(*a, **b):
        try:
          if session.alias==None or session.auth.user.alias != session.alias:
            redirect(URL('alias_login'))
        except Exception:
          redirect(URL('alias_login'))
        return action(*a, **b)
      f.__doc__ = action.__doc__
      f.__name__ = action.__name__
      f.__dict__.update(action.__dict__)
      return f
    return decorator

def formatNumber(value):
  try:
    return DIV(ns.splitThousands(float(value)," ","."), _align="right", _width="100%")
  except Exception:
    pass
def formatInteger(value):
  try:
    return DIV(ns.splitThousands(int(value)," ","."), _align="right", _width="100%")
  except Exception:
    pass
def formatDate(value):
  try:
    if type(value) is datetime.datetime:
      return DIV(value.date(), _align="center", _width="100%")
    elif type(value).__name__=="unicode":
      return DIV(datetime.datetime.strptime(str(value).split(" ")[0], str('%Y-%m-%d')).date(), _align="center", _width="100%")
    else:
      return value
  except Exception:
    pass
        
def get_audit_filter(nervatype, transtype=None):
  if not session.auth:
    redirect(URL('index'))
  retvalue = ("all",1)
  nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue==nervatype)).select().as_list()[0]["id"]
  query = (ns.db.ui_audit.usergroup==ns.db.employee(id=session.auth.user.id).usergroup)&(ns.db.ui_audit.nervatype==nervatype_id)
  if nervatype=="trans" and transtype!=None:
    transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue==transtype)).select().as_list()[0]["id"]
    query = query &(ns.db.ui_audit.subtype==transtype_id)
  if nervatype=="menu" and transtype!=None:
    menu = ns.db((ns.db.ui_menu.menukey==transtype)).select()
    if len(menu)>0:
      query = query &(ns.db.ui_audit.subtype==menu[0]["id"])
  audit = ns.db(query).select().as_list()
  if len(audit)>0:
    inputfilter = ns.db.groups(id=audit[0]["inputfilter"]).groupvalue
    retvalue = (inputfilter,audit[0]["supervisor"])
  return retvalue

def get_audit_subtype(subtype):
  #return disabled report/transtype list
  nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue==subtype)).select().as_list()[0]["id"]
  disabled_inputfilter_id = ns.db((ns.db.groups.groupname=="inputfilter")&(ns.db.groups.groupvalue=="disabled")).select().as_list()[0]["id"]
  return ns.db((ns.db.ui_audit.usergroup==ns.db.employee(id=session.auth.user.id).usergroup)&(ns.db.ui_audit.nervatype==nervatype_id)
        &(ns.db.ui_audit.inputfilter==disabled_inputfilter_id)&(ns.db.ui_audit.subtype!=None)).select(ns.db.ui_audit.subtype.with_alias('id'))
        
def create_menu():
  ns_menu = []
  ns_menu.append((T('HOME'), False, URL('index'), []))
  ns_menu.append((T('TRANSACTIONS'), False, None, []))
  ns_menu.append((T('RESOURCES'), False, None, []))
  ns_menu.append((T('REPORTS'), False, URL('frm_reports'), []))
  ns_menu.append((T('ADMIN'), False, None, []))
  ns_menu.append((T('PROGRAM'), False, None, []))
  ns_menu.append((T('EXIT'), False, URL('alias_logout'), []))
  if session.auth!=None:
    
    #TRANSACTIONS
    mnu_operation = (T('DOCUMENTS'), False, None, [])
    audit_filter = get_audit_filter("trans", "offer")[0]
    if audit_filter=="all":
      mnu_offer = (T('OFFER'), False, None, [])
      mnu_offer[3].append((T('New Customer Offer'), False, URL('frm_trans/new/trans/offer/out'), []))
      mnu_offer[3].append((T('New Supplier Offer'), False, URL('frm_trans/new/trans/offer/in'), []))
      mnu_operation[3].append(mnu_offer)
    
    audit_filter = get_audit_filter("trans", "order")[0]
    if audit_filter=="all":
      mnu_order = (T('ORDER'), False, None, [])
      mnu_order[3].append((T('New Customer Order'), False, URL('frm_trans/new/trans/order/out'), []))
      mnu_order[3].append((T('New Supplier Order'), False, URL('frm_trans/new/trans/order/in'), []))
      mnu_operation[3].append(mnu_order)
    
    audit_filter = get_audit_filter("trans", "worksheet")[0]
    if audit_filter=="all":
      mnu_worksheet = (T('WORKSHEET'), False, None, [])
      mnu_worksheet[3].append((T('New Worksheet'), False, URL('frm_trans/new/trans/worksheet/out'), []))
      mnu_operation[3].append(mnu_worksheet)
    
    audit_filter = get_audit_filter("trans", "rent")[0]
    if audit_filter=="all":
      mnu_rent = (T('RENT'), False, None, [])
      mnu_rent[3].append((T('New Customer Rental'), False, URL('frm_trans/new/trans/rent/out'), []))
      mnu_rent[3].append((T('New Supplier Rental'), False, URL('frm_trans/new/trans/rent/in'), []))
      mnu_operation[3].append(mnu_rent)
    
    audit_filter = get_audit_filter("trans", "invoice")[0]
    audit_filter2 = get_audit_filter("trans", "receipt")[0]
    if audit_filter=="all" or audit_filter2=="all":
      mnu_invoice = (T('INVOICE'), False, None, [])
      if audit_filter=="all":
        mnu_invoice[3].append((T('New Customer Invoice'), False, URL('frm_trans/new/trans/invoice/out'), []))
        mnu_invoice[3].append((T('New Supplier Invoice'), False, URL('frm_trans/new/trans/invoice/in'), []))
      if audit_filter2=="all":
        mnu_invoice[3].append((T('New Receipt'), False, URL('frm_trans/new/trans/receipt/out'), []))
      mnu_operation[3].append(mnu_invoice)
    mnu_operation[3].append((HR(), False, None, []))
    mnu_operation[3].append((SPAN(T('Quick Search')), False, URL('find_transitem_quick_all'), []))
    mnu_operation[3].append((T('Documents Browser'), False, URL('find_transitem_trans'), []))
    ns_menu[1][3].append(mnu_operation)
    
    audit_filter = get_audit_filter("trans", "bank")[0]
    audit_filter2 = get_audit_filter("trans", "cash")[0]
    if audit_filter!="disabled" or audit_filter2!="disabled":
      mnu_payment = (T('PAYMENT'), False, None, [])
      if audit_filter=="all":
        mnu_payment[3].append((T('New Bank Statement'), False, URL('frm_trans/new/trans/bank/transfer'), []))
      if audit_filter2=="all":
        mnu_payment[3].append((T('New Cash'), False, URL('frm_trans/new/trans/cash/out'), []))
      if audit_filter=="all" or audit_filter2=="all":
        mnu_payment[3].append((HR(), False, None, []))
      mnu_payment[3].append((SPAN(T('Quick Search')), False, URL('find_payment_quick'), []))
      mnu_payment[3].append((T('Payment Browser'), False, URL('find_payment_payment'), []))
      ns_menu[1][3].append(mnu_payment)
    
    audit_filter_delivery = get_audit_filter("trans", "delivery")[0]
    audit_filter_inventory = get_audit_filter("trans", "inventory")[0]
    audit_filter_waybill = get_audit_filter("trans", "waybill")[0]
    audit_filter_production = get_audit_filter("trans", "production")[0]
    audit_filter_formula = get_audit_filter("trans", "formula")[0]
    if audit_filter_delivery!="disabled" or audit_filter_inventory!="disabled" or audit_filter_waybill!="disabled" or audit_filter_production!="disabled":
      mnu_stock = (T('STOCK CONTROL'), False, None, [])
      if audit_filter_delivery!="disabled" or audit_filter_inventory!="disabled":
        mnu_inventory = (T('INVENTORY'), False, None, [])
        if audit_filter_delivery=="all":
          mnu_inventory[3].append((T('New Delivery'), False, URL('find_transitem_quick_delivery'), []))
        if audit_filter_inventory=="all":
          mnu_inventory[3].append((T('New Stock Correction'), False, URL('frm_trans/new/trans/inventory/transfer'), []))
        if audit_filter_delivery=="all":
          mnu_inventory[3].append((T('New Stock Transfer'), False, URL('frm_trans/new/trans/delivery/transfer'), []))
        mnu_stock[3].append(mnu_inventory)
      if audit_filter_waybill=="all":
        mnu_waybill = (T('TOOL MOVEMENT'), False, None, [])
        mnu_waybill[3].append((T('New Tool Movement'), False, URL('frm_trans/new/trans/waybill/out'), []))
        mnu_stock[3].append(mnu_waybill)
      if audit_filter_production=="all" or audit_filter_formula=="all":
        mnu_production = (T('PRODUCTION'), False, None, [])
        if audit_filter_production=="all":
          mnu_production[3].append((T('New Production'), False, URL('frm_trans/new/trans/production/transfer'), []))
        if audit_filter_formula=="all":
          mnu_production[3].append((T('New Formula'), False, URL('frm_trans/new/trans/formula/transfer'), []))
        mnu_stock[3].append(mnu_production)
      mnu_stock[3].append((HR(), False, None, []))
      mnu_stock[3].append((SPAN(T('Quick Search')), False, URL('find_movement_quick'), []))
      mnu_stock[3].append((T('Stock Browser'), False, URL('find_movement_inventory'), []))
      ns_menu[1][3].append(mnu_stock)
    
    mnu_office = (T('BACK OFFICE'), False, None, [])
    mnu_office[3].append((T('Printer Queue'), False, URL('frm_printqueue'), []))
    menucmd = ns.db().select(ns.db.ui_menu.ALL)
    if len(menucmd)>0:
      mnu_office[3].append((HR(), False, None, []))
    for cmd in menucmd:
      audit_filter_menu = get_audit_filter("menu", cmd["menukey"])[0]
      if audit_filter_menu!="disabled":
        mnu_office[3].append((T(cmd["description"]), False, "javascript:call_menucmd('"+cmd["menukey"]+"',"+str(cmd["url"])+");", []))
    ns_menu[1][3].append(mnu_office)
    
    #RESOURCES
    audit_filter = get_audit_filter("customer", None)[0]
    if audit_filter!="disabled":
      mnu_customer = (T('CUSTOMER'), False, None, [])
      if audit_filter=="all":
        mnu_customer[3].append((T('New Customer'), False, URL('frm_customer/new/customer'), []))
        mnu_customer[3].append((HR(), False, None, []))
      mnu_customer[3].append((SPAN(T('Quick Search')), False, URL('find_customer_quick'), []))
      mnu_customer[3].append((T('Customer Browser'), False, URL('find_customer_customer'), []))
      ns_menu[2][3].append(mnu_customer)
    
    audit_filter = get_audit_filter("product", None)[0]
    if audit_filter!="disabled":
      mnu_product = (T('PRODUCT'), False, None, [])
      if audit_filter=="all":
        mnu_product[3].append((T('New Product'), False, URL('frm_product/new/product'), []))
        mnu_product[3].append((HR(), False, None, []))
      mnu_product[3].append((SPAN(T('Quick Search')), False, URL('find_product_quick'), []))
      mnu_product[3].append((T('Product Browser'), False, URL('find_product_product'), []))
      ns_menu[2][3].append(mnu_product)
    
    audit_filter = get_audit_filter("employee", None)[0]
    if audit_filter!="disabled":
      mnu_employee = (T('EMPLOYEE'), False, None, [])
      if audit_filter=="all":
        mnu_employee[3].append((T('New Employee'), False, URL('frm_employee/new/employee'), []))
        mnu_employee[3].append((HR(), False, None, []))
      mnu_employee[3].append((SPAN(T('Quick Search')), False, URL('find_employee_quick'), []))
      mnu_employee[3].append((T('Employee Browser'), False, URL('find_employee_employee'), []))
      ns_menu[2][3].append(mnu_employee)
    
    audit_filter = get_audit_filter("tool", None)[0]
    if audit_filter!="disabled":
      mnu_tool = (T('TOOL'), False, None, [])
      if audit_filter=="all":
        mnu_tool[3].append((T('New Tool'), False, URL('frm_tool/new/tool'), []))
        mnu_tool[3].append((HR(), False, None, []))
      mnu_tool[3].append((SPAN(T('Quick Search')), False, URL('find_tool_quick'), []))
      mnu_tool[3].append((T('Tool Browser'), False, URL('find_tool_tool'), []))
      ns_menu[2][3].append(mnu_tool)
    
    audit_filter = get_audit_filter("project", None)[0]
    if audit_filter!="disabled":
      mnu_project = (T('PROJECT'), False, None, [])
      if audit_filter=="all":
        mnu_project[3].append((T('New Project'), False, URL('frm_project/new/project'), []))
        mnu_project[3].append((HR(), False, None, []))
      mnu_project[3].append((SPAN(T('Quick Search')), False, URL('find_project_quick'), []))
      mnu_project[3].append((T('Project Browser'), False, URL('find_project_project'), []))
      ns_menu[2][3].append(mnu_project)
      
    #ADMIN
    audit_filter_setting = get_audit_filter("setting", None)[0]
    audit_filter_audit = get_audit_filter("audit", None)[0]
    if audit_filter_setting!="disabled":
      mnu_settings = (T('SETTINGS'), False, None, [])
      mnu_settings[3].append((T('Database Settings'), False, URL('frm_setting'), []))
      mnu_settings[3].append((T('Transaction Numbering'), False, URL('frm_numberdef'), []))
      if audit_filter_audit!="disabled":
        mnu_settings[3].append((T('Access Rights'), False, URL('frm_groups_usergroup'), []))
      mnu_settings[3].append((T('Server Printers'), False, URL('frm_groups_printer'), []))
      mnu_settings[3].append((T('Menu Shortcuts'), False, URL('find_menucmd'), []))
      mnu_settings[3].append((T('Database Logs'), False, URL('find_log'), []))
      ns_menu[4][3].append(mnu_settings)
      mnu_more = (T('MORE DATA'), False, None, [])
      mnu_more[3].append((T('Additional Data'), False, URL('frm_deffield_all?back=1'), []))
      mnu_more[3].append((T('Groups'), False, URL('frm_groups_all?back=1'), []))
      mnu_more[3].append((T('Place'), False, URL('find_place?back=1'), []))
      mnu_more[3].append((T('Currency'), False, URL('frm_currency?back=1'), []))
      mnu_more[3].append((T('Tax'), False, URL('frm_tax?back=1'), []))
      mnu_more[3].append((T('Interest and Exchange Rate'), False, URL('find_rate'), []))
      ns_menu[4][3].append(mnu_more)
      ns_menu[4][3].append((T('COMPANY'), False, URL('frm_customer/view/customer/1'), []))
    
    #PROGRAM
    ns_menu[5][3].append((T('Change Password'), False, URL('change_password/'+str(session.auth.user.id)), []))
  return ns_menu

def nwc_ini():
  #check and create some ui and version specifics settings
  
  #printertypes
  if len(ns.db((ns.db.groups.groupname=="printertype")&(ns.db.groups.groupvalue=="local")).select())==0:
    ns.db.groups.insert(**dict({'groupname':'printertype', 'groupvalue':'local', 'description':'Local port'}))
  if len(ns.db((ns.db.groups.groupname=="printertype")&(ns.db.groups.groupvalue=="network")).select())==0:
    ns.db.groups.insert(**dict({'groupname':'printertype', 'groupvalue':'network', 'description':'Local network'}))
  if len(ns.db((ns.db.groups.groupname=="printertype")&(ns.db.groups.groupvalue=="mail")).select())==0:
    ns.db.groups.insert(**dict({'groupname':'printertype', 'groupvalue':'mail', 'description':'HP ePrint via Email'}))
  if len(ns.db((ns.db.groups.groupname=="printertype")&(ns.db.groups.groupvalue=="google_cloud")).select())==0:
    ns.db.groups.insert(**dict({'groupname':'printertype', 'groupvalue':'google_cloud', 'description':'Google Cloud Print'}))
  
  if len(ns.db((ns.db.groups.groupname=="orientation")&(ns.db.groups.groupvalue=="P")).select())==0:
    ns.db.groups.insert(**dict({'groupname':'orientation', 'groupvalue':'P', 'description':'Portrait'}))
  if len(ns.db((ns.db.groups.groupname=="orientation")&(ns.db.groups.groupvalue=="L")).select())==0:
    ns.db.groups.insert(**dict({'groupname':'orientation', 'groupvalue':'L', 'description':'Landscape'}))
  
  if len(ns.db((ns.db.groups.groupname=="papersize")&(ns.db.groups.groupvalue=="a3")).select())==0:
    ns.db.groups.insert(**dict({'groupname':'papersize', 'groupvalue':'a3', 'description':'A3'}))
  if len(ns.db((ns.db.groups.groupname=="papersize")&(ns.db.groups.groupvalue=="a4")).select())==0:
    ns.db.groups.insert(**dict({'groupname':'papersize', 'groupvalue':'a4', 'description':'A4'}))
  if len(ns.db((ns.db.groups.groupname=="papersize")&(ns.db.groups.groupvalue=="a5")).select())==0:
    ns.db.groups.insert(**dict({'groupname':'papersize', 'groupvalue':'a5', 'description':'A5'}))
  if len(ns.db((ns.db.groups.groupname=="papersize")&(ns.db.groups.groupvalue=="letter")).select())==0:
    ns.db.groups.insert(**dict({'groupname':'papersize', 'groupvalue':'letter', 'description':'Letter'}))
  if len(ns.db((ns.db.groups.groupname=="papersize")&(ns.db.groups.groupvalue=="legal")).select())==0:
    ns.db.groups.insert(**dict({'groupname':'papersize', 'groupvalue':'legal', 'description':'Legal'}))
      
  nervatype_groups_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  if not ns.db.deffield(fieldname="printer_login"):
    string_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"printer_login","nervatype":nervatype_groups_id, 'subtype':None, "fieldtype":string_type,
                            "description":"Printer login", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0})
  if not ns.db.deffield(fieldname="printer_password"):
    password_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="password")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"printer_password","nervatype":nervatype_groups_id, 'subtype':None, "fieldtype":password_type,
                            "description":"Printer password", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0})
  if not ns.db.deffield(fieldname="printer_server"):
    string_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"printer_server","nervatype":nervatype_groups_id, 'subtype':None, "fieldtype":string_type,
                            "description":"Printer server", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0})
  if not ns.db.deffield(fieldname="printer_port"):
    integer_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="integer")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"printer_port","nervatype":nervatype_groups_id, 'subtype':None, "fieldtype":integer_type,
                            "description":"Printer port", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0})
  
  if not ns.db.deffield(fieldname="printer_mail_smtp"):
    string_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"printer_mail_smtp","nervatype":nervatype_groups_id, 'subtype':None, "fieldtype":string_type,
                            "description":"Printer mail smtp", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0})
  if not ns.db.deffield(fieldname="printer_mail_sender"):
    string_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"printer_mail_sender","nervatype":nervatype_groups_id, 'subtype':None, "fieldtype":string_type,
                            "description":"Printer mail sender", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0})
  if not ns.db.deffield(fieldname="printer_mail_login"):
    string_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"printer_mail_login","nervatype":nervatype_groups_id, 'subtype':None, "fieldtype":string_type,
                            "description":"Printer mail login (username:password)", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0})
  if not ns.db.deffield(fieldname="printer_mail_address"):
    string_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"printer_mail_address","nervatype":nervatype_groups_id, 'subtype':None, "fieldtype":string_type,
                            "description":"Printer mail address", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0})
  if not ns.db.deffield(fieldname="printer_mail_subject"):
    string_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"printer_mail_subject","nervatype":nervatype_groups_id, 'subtype':None, "fieldtype":string_type,
                            "description":"Printer mail subject", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0})
  if not ns.db.deffield(fieldname="printer_mail_message"):
    string_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"printer_mail_message","nervatype":nervatype_groups_id, 'subtype':None, "fieldtype":string_type,
                            "description":"Printer mail message", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0})
    
  if not ns.db.deffield(fieldname="printer_gsprint"):
    nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
    fieldtype_id = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**dict({'fieldname':'printer_gsprint', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                    'description':'gsprint path (windows pdf printing)', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
    ns.db.fieldvalue.insert(**dict({'fieldname':'printer_gsprint', 'ref_id':None, 'value':'C:\Progra~1\Ghostgum\gsview\gsprint', 'notes':None}))
    
  if not ns.db.deffield(fieldname="printer_clienthost"):
    nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
    fieldtype_id = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**dict({'fieldname':'printer_clienthost', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                    'description':'Client Additions host', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
    ns.db.fieldvalue.insert(**dict({'fieldname':'printer_clienthost', 'ref_id':None, 'value':'localhost:8080', 'notes':None}))
    
  #trans - worksheet
  nervatype_trans_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
  transtype_worksheet_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="worksheet")).select().as_list()[0]["id"]
  if not ns.db.deffield(fieldname="trans_wsdistance"):
    float_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"trans_wsdistance","nervatype":nervatype_trans_id, 'subtype':transtype_worksheet_id, "fieldtype":float_type,
                               "description":"worksheet distance", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1})
  if not ns.db.deffield(fieldname="trans_wsrepair"):
    float_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"trans_wsrepair","nervatype":nervatype_trans_id, 'subtype':transtype_worksheet_id, "fieldtype":float_type,
                               "description":"worksheet repair time (hour)", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1})
  if ns.db.deffield(fieldname="trans_wstotal")==None:
    float_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"trans_wstotal","nervatype":nervatype_trans_id, 'subtype':transtype_worksheet_id, "fieldtype":float_type,
                               "description":"worksheet total time (hour)", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1})
  if ns.db.deffield(fieldname="trans_wsnote")==None:
    string_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
    ns.db.deffield.insert(**{"fieldname":"trans_wsnote","nervatype":nervatype_trans_id, 'subtype':transtype_worksheet_id, "fieldtype":string_type,
                               "description":"worksheet justification", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1})
  
  #trans - rent    
  transtype_rent_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="rent")).select().as_list()[0]["id"]
  if ns.db.deffield(fieldname="trans_reholiday")==None:
      float_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
      ns.db.deffield.insert(**{"fieldname":"trans_reholiday","nervatype":nervatype_trans_id, 'subtype':transtype_rent_id, "fieldtype":float_type,
                               "description":"rent holidays", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1})
  if ns.db.deffield(fieldname="trans_rebadtool")==None:
      float_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
      ns.db.deffield.insert(**{"fieldname":"trans_rebadtool","nervatype":nervatype_trans_id, 'subtype':transtype_rent_id, "fieldtype":float_type,
                               "description":"rent bad machine", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1})
  if ns.db.deffield(fieldname="trans_reother")==None:
      float_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
      ns.db.deffield.insert(**{"fieldname":"trans_reother","nervatype":nervatype_trans_id, 'subtype':transtype_rent_id, "fieldtype":float_type,
                               "description":"rent other non-eligible", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1})
  if ns.db.deffield(fieldname="trans_rentnote")==None:
      string_type = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      ns.db.deffield.insert(**{"fieldname":"trans_rentnote","nervatype":nervatype_trans_id, 'subtype':transtype_rent_id, "fieldtype":string_type,
                               "description":"rent justification", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1})
            

def setLogtable(logstate, inikey=None, nervatype=None, log_id=None):  
  if inikey!=None:
    logini = ns.db((ns.db.fieldvalue.fieldname==inikey)).select().as_list()
    if len(logini)>0:
      if logini[0]["value"]!="true":
        return True
    else:
      return True
  if nervatype!=None:
    neraid = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue==nervatype)).select().as_list()[0]["id"]
  else:
    neraid = None
  logstate_id = ns.db((ns.db.groups.groupname=="logstate")&(ns.db.groups.groupvalue==logstate)).select().as_list()[0]["id"]
  values = {"nervatype":neraid, "ref_id":neraid, "ref_id":log_id, "logstate":logstate_id, "employee_id":session.auth.user.id, "crdate":datetime.datetime.now()}
  ret = ns.db.log.validate_and_insert(**values)
  if len(ret.errors.keys())>0:
    return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
  return True
  
if request.user_agent().is_mobile:
  redirect(URL(a='nerva2py', c='nmc', f='index'))
response.title=T('Nervatura Web Client')
ns = NervaStore(request, T, db)
dbfu = NervaTools()
ns_auth=auth_ini()
if session.alias!=None:
  if session.auth:
    if session.auth.user.alias != session.alias:
      session.alias=None
      redirect(URL('alias_login'))
  if setEngine(ns, session.alias):
    response.alias = session.alias
    ns_auth = Auth(ns.db, hmac_key=Auth.get_or_create_key(), controller=contr)
    ns_auth.define_tables(username=True, migrate=False, fake_migrate=False)
    if session.auth!=None:
      session.auth.user.alias = session.alias
      response.username = session.auth.user.username
      if session.auth.user.username=="demo" and session.alias=="demo":
        DEMO_MODE = True
  response.appl_url = appl+"/"+contr
  response.ns_menu = create_menu()
  response.icon_help = IMG(_src=URL(dir_images,'icon16_help.png'))
  response.icon_user = IMG(_src=URL(dir_images,'icon16_user.png'),_style="vertical-align: middle;",_height="16px",_width="16px")
  response.icon_address = IMG(_src=URL(dir_images,'icon16_address.png'),_style="vertical-align: middle;",_height="16px",_width="16px")

def login_methods(username, password):
  if session.nas_login: return False
  
def alias_login():
  if request.cookies.has_key('last_alias'):
    last_alias = request.cookies['last_alias'].value
  elif DEMO_MODE:
    last_alias = "demo"
  else:
    last_alias = ""
  if request.cookies.has_key('last_username'):
    last_username = request.cookies['last_username'].value
  elif DEMO_MODE:
    last_username = "demo"
  else:
    last_username = ""
  form = SQLFORM.factory(
    Field('alias', type='string', length=50, requires=IS_NOT_EMPTY(), label=T('Database'), default=last_alias),
    Field('username', type='string', length=50, requires=IS_NOT_EMPTY(), label=T('Username'), default=last_username),
    Field('password', type='password', length=50, label=T('Password')),
    submit_button=T("Login"), table_name="login"
  )
  response.cmd_help = get_help_button("login")
  #Opera and IE hack
  if request.vars.has_key("alias") and request.vars.has_key("username") and request.vars.has_key("password") and not request.vars.has_key("_formname"):
    request.vars["_formname"] = "login/create"
  if form.accepts(request.vars) and session.nas_login==None:
    if setEngine(ns, form.vars.alias):
      session.alias = form.vars.alias
      ns_auth = Auth(ns.db, hmac_key=Auth.get_or_create_key(), controller=contr)
      
      ns_auth.settings.table_user_name = 'employee'
      ns_auth.settings.login_next = URL('index')
      ns_auth.settings.logout_next = URL('alias_login')
      ns_auth.settings.login_methods = [login_methods]
      
      ns_auth.settings.expiration = 3600  # seconds
      ns_auth.settings.long_expiration = 3600*24*30 # one month
  
      ns_auth.define_tables(username=True, migrate=False, fake_migrate=False)
      
      if form.vars.password=="":
        form.vars.password=None
      if ns.setLogin(form.vars.username, form.vars.password):
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
        setLogtable("login", "log_userlogin")
        nwc_ini()
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

def alias_logout():
  session.alias=None
  try:
    ns_auth.logout(next=URL('alias_login'),log=None)
  except Exception:
    redirect(URL('alias_login'))

def user():
  if session.auth==None:
    redirect(URL('alias_login'))
  return dict(form=ns_auth())

def w2help():
  if request.vars.page:
    lang = session._language if session._language else "en"
    file_name = os.path.join(request.folder, dir_help, lang, str(request.vars.page)+'.html')
    if not os.path.isfile(file_name):
      file_name = os.path.join(request.folder, dir_help, lang, 'index.html')
      if not os.path.isfile(file_name):
        file_name = os.path.join(request.folder, dir_help, 'en', 'index.html')
        if not os.path.isfile(file_name):
          return "Missing index file!"
    response.view=file_name
    response.title = T("Nervatura Web Client")
    response.subtitle = "Ver.No: "+response.verNo
    return dict()
  else:
    return "Missing page parameter!"

def getItemFromKey(table, field, value):
  #from/return object
  retval = None
  index = next((i for i in xrange(len(table)) if table[i][field] == value), None)
  if index : retval = table[index]
  return retval

def get_formvalue(fieldname,table=None,ref_id=None,default="",isempty=True,key_field="id"):
  if request.post_vars.has_key(fieldname):
    return default if request.post_vars[fieldname]=="" and not isempty else request.post_vars[fieldname]
  else:
    if table and ref_id:
      if table == "fieldvalue":
        trow = ns.db((ns.db.fieldvalue.fieldname==fieldname) & (ns.db.fieldvalue.ref_id==ref_id)).select()
      else:
        trow = ns.db((ns.db[table][key_field]==ref_id)).select()
      if len(trow)>0:
        return trow[0]["value"] if table == "fieldvalue" else trow[0][fieldname]
      else:
        return default
    else:
      return default
        
def getSetting(fieldname):
  logini = ns.db((ns.db.fieldvalue.fieldname==fieldname)).select().as_list()
  if len(logini)>0:
    return logini[0]["value"]
  else:
    return ""

def updateFieldValue(refid, fieldname, value=None, notes=None):
  fieldvalue = ns.db((ns.db.fieldvalue.ref_id==refid)
                     &(ns.db.fieldvalue.fieldname==fieldname)&(ns.db.fieldvalue.deleted==0)).select().as_list()
  if len(fieldvalue)==0:
    ns.db.fieldvalue.validate_and_insert(**{"fieldname":fieldname,"ref_id":refid,"value":value,"notes":notes})
  else:
    ns.db(ns.db.fieldvalue.id==fieldvalue[0]["id"]).validate_and_update(**{"value":value,"notes":notes})
  
def deleteFieldValues(nervatype, refid, fieldname=None):
  delete_ini = getSetting("set_trans_deleted")
  neraid = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue==nervatype)).select().as_list()[0]["id"]
  deffields = ns.db((ns.db.deffield.nervatype==neraid)).select().as_list()
  if len(deffields)==0:
    return True
  if refid!=None:
    fieldvalues = ns.db(ns.db.fieldvalue.ref_id==refid).select().as_list()
    for field in fieldvalues:
      if getItemFromKey(deffields, "fieldname", field["fieldname"])!=None:
        if delete_ini != "true":
          values = {"deleted":1}
          ns.db(ns.db.fieldvalue.id==field["id"]).update(**values)
        else:
          try:
            ns.db(ns.db.fieldvalue.id == field["id"]).delete()
            ns.db.commit()
          except Exception, err:
            ns.db.rollback()
            return str(err)
  else:
    fieldvalues = ns.db(ns.db.fieldvalue.fieldname==fieldname).select().as_list()
    if len(fieldvalues)>0:
      if delete_ini != "true":
        values = {"deleted":1}
        ns.db(ns.db.fieldvalue.id==fieldvalues[0]["id"]).update(**values)
      else:
        try:
          ns.db(ns.db.fieldvalue.id == fieldvalues[0]["id"]).delete()
          ns.db.commit()
        except Exception, err:
          ns.db.rollback()
          return str(err)
  return True
    
@ns_auth.requires_login()
def index():
  if session.welcome==True:
    session.welcome=False
    response.flash = T('Welcome to Nervatura Web Client!')
  response.subtitle=T('START PAGE')
  response.titleicon = URL(dir_images,'icon16_home.png')
  return dict()

@ns_auth.requires_login()
def change_password():
  ruri = request.wsgi.environ["REQUEST_URI"]
  employee_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  employee = ns.db.employee(id=employee_id)
  if request.wsgi.environ.has_key("HTTP_REFERER"):
    if request.wsgi.environ["HTTP_REFERER"].find("change_password")>-1:
      response.back_url = URL('frm_employee/view/employee/'+str(employee_id))
    else:
      response.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    response.back_url = URL('index')
  response.title=T('SETTINGS')
  response.subtitle=T('Changing the password')
  response.titleicon = URL(dir_images,'icon16_key.png')
  if employee["username"]==None or employee["username"]=="":
    response.enabled = False
    response.username = "Missing username!"
  else:
    response.enabled = True
    response.username = employee["username"]
  form = SQLFORM.factory(
    Field('password_1', type='password', length=50, label=T('New password')),
    Field('password_2', type='password', length=50, label=T('Verify password')),
    submit_button=T("Save"), table_name="change"
  )
  if form.process().accepted:
    if form.vars.password_1!=form.vars.password_2:
      form.errors["password_2"]="Password fields don't match"
      response.flash = T("Form has errors: Password fields don't match")
    else:
      if form.vars.password_1=="":
        password=None
      else:
        password = ns.get_md5_value(form.vars.password_1)
      ns.db(ns.db.employee.id==employee_id).update(**{"password":password})
  if DEMO_MODE:
    form.custom.submit = DIV(SPAN(T('DEMO MODE')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
  return dict(form=form)

def get_nervatype_label(nervatype_name,ref_id):
  if nervatype_name=="customer":
    return ns.db.customer(id=ref_id).custname
  elif nervatype_name=="employee":
    return ns.db.employee(id=ref_id).empnumber
  elif nervatype_name=="product":
    return ns.db.product(id=ref_id).description
  elif nervatype_name=="tool":
    return ns.db.tool(id=ref_id).serial
  elif nervatype_name=="project":
    return ns.db.project(id=ref_id).pronumber
  elif nervatype_name=="trans":
    return ns.db.trans(id=ref_id).transnumber
  else:
    return ""

def get_home_button():
  return A(SPAN(_class="icon home"), _style="height: 15px;", _class="w2p_trap buttontext button", _title= T('Back'), _href=URL("index"))

def get_help_button(page):
  return A(IMG(_src=URL(dir_images,'icon16_help.png')), _style="height: 15px;", _target="_blank",
    _class="w2p_trap buttontext button", _href=URL('w2help?page='+page), _title= T('Help'))

def get_back_button(url):
  return A(SPAN(_class="icon leftarrow"), _style="height: 15px;", _class="w2p_trap buttontext button", _title= T('Back'), _href=url)

def get_new_button(url):
  return A(SPAN(_class="icon plus"), _style="height: 15px;", _class="w2p_trap buttontext button", _title= T('New'), _href=url)

def get_goprop_button(title,url):
  return A(SPAN(_class="icon cog"), _style="padding: 0px;padding-left: 6px;padding-right: 3px;", 
    _class="w2p_trap buttontext button", _href=url, _title=title, 
    _onclick="javascript:if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
            +"')){window.location ='"+url+"';};return false;")

def get_report_button(title,url):
  dlg_report = DIALOG(LOAD(f=url, ajax=True), title=title,
                        icon=URL(dir_images,'icon16_printer.png'), renderstyle=True, height=50, width=35)
  return INPUT(_type="button", _value=T("Reports"), _style="height: 25px !important;padding-top: 2px !important;color: #483D8B;width: 100%;", 
              _onclick='%s;return false' % dlg_report.show())

def get_command_button(caption,title,color="444444",cmd="",_id="",_height="25px", _top="2px"):
  return INPUT(_type="button", _value=caption, _title=title, _id=_id,
               _style="height: "+_height+" !important;padding-top: "+_top+" !important;color: #"+color+";", _onclick= cmd)

def get_more_button(dv_id='dv_more',sp_id='sp_more',img_id='img_more',title_1=T('More...'),title_2=T('Less...'),title_tool=T('More commands')):
  return A(IMG(_id=img_id,_style="vertical-align: top;padding-top: 2px;",_height="16px",_width="16px",
               _src=URL(dir_images,'control_down.png')), SPAN(title_1,_id=sp_id,_style="font-weight: bold;"),
               _style="text-align:center; height: 19px;padding-top: 2px; padding-bottom: 2px;width: 100%;",
               _class="w2p_trap buttontext button", _href="#", _title=title_tool,
               _onclick="javascript:var tbl=document.getElementById('"+dv_id+"');var sp=document.getElementById('"+sp_id+"');\
                         var ig=document.getElementById('"+img_id+"'); if(tbl.style.display == 'none'){tbl.style.display = 'block';\
                         sp.innerHTML='"+title_2+"';ig.src='"+URL(dir_images,'control_up.png')+"';} \
                         else {tbl.style.display = 'none';sp.innerHTML='"+title_1+"';ig.src='"+URL(dir_images,'control_down.png')+"';};")

def get_total_button():
  return A(IMG(_id="img_total",_style="vertical-align: top;padding-top: 2px;",_height="16px",_width="16px",
               _src=URL(dir_images,'control_down.png')),
           IMG(_style="vertical-align: top;padding-top: 2px;",_height="16px",_width="16px",
               _src=URL(dir_images,'icon16_sum.png')), 
               _style="text-align:center; height: 19px;padding-top: 2px; padding-bottom: 2px;width: 30px;",
               _class="w2p_trap buttontext button", _href="#", _title="Quick Total",
               _onclick="var tbl=document.getElementById('dv_total');\
                         var ig=document.getElementById('img_total'); if(tbl.style.display == 'none'){tbl.style.display = 'block';\
                         ig.src='"+URL(dir_images,'control_up.png')+"';} \
                         else {tbl.style.display = 'none';ig.src='"+URL(dir_images,'control_down.png')+"';};")
         
def get_tabnew_button(row_count,title,cmd_id,url="#",cmd=""):
  return A(SPAN(_class="icon plus")," ",str(row_count), _id=cmd_id, 
    _style="cursor: pointer; top:3px; text-align: center;padding: 2px;padding-left: 6px;padding-right: 3px;",
    _class="w2p_trap buttontext button", _href=url, _title=title, _onclick= cmd)

def get_tabedit_button(title,cmd_id,url="#",cmd=""):
  return A(SPAN(_class="icon pen"), _id=cmd_id, 
    _style="cursor: pointer; top:3px; text-align: center;padding: 2px;padding-left: 6px;padding-right: 3px;",
    _class="w2p_trap buttontext button", _href=url, _title=title, _onclick= cmd)
  
def get_icon_button(title,cmd_id,url="#",cmd="",icon="icon plus",label=""):
  return A(SPAN(_class=icon)+label, _id=cmd_id, _style="left: 3px; padding: 0px;padding-left: 6px;padding-right: 3px;", 
    _class="w2p_trap buttontext button", _href=url, _title=title, _onclick= cmd)

def get_cmb_fields(nervatype):
  nervatype_fields = ns.db((ns.db.deffield.nervatype==nervatype)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
                   &(ns.db.deffield.readonly==0)).select(orderby=ns.db.deffield.description).as_list()
  cmb_fields = SELECT(*[OPTION(field["description"], _value=field["fieldname"]+"~"+str(ns.db.groups(id=field["fieldtype"])["groupvalue"])+"~"+str(field["valuelist"])) for field in nervatype_fields], _id="cmb_fields")
  cmb_fields.insert(0, OPTION("", _value=""))
  return cmb_fields

def get_cmb_groups(groupname):
  groupname_groups = ns.db((ns.db.groups.groupname==groupname)&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)
                          ).select(orderby=ns.db.groups.groupvalue).as_list()
  cmb_groups = SELECT(*[OPTION(field["groupvalue"],_value=field["id"]) for field in groupname_groups], _id="cmb_groups")
  cmb_groups.insert(0, OPTION("", _value=""))
  return cmb_groups
    
def get_base_selector(dlg,label_id,label_url,label_txt="",value_id=None,width="98%",error_label=False, div_id=""):
  if error_label:
    cmd = DIV(dlg, _id=div_id, _class="label_error", _style="width: 98%;display:block;padding: 3px;height: 22px;".replace("98%", width))
    cmd.append(SPAN(label_txt, _id=label_id))
  elif label_url!="":  
    cmd = DIV(dlg, _id=div_id, _class="label_disabled", _style="width: 98%;display:block;padding: 3px;height: auto;padding-bottom: 0px;padding-top: 2px;".replace("98%", width))
    cmd.append(A(label_txt, _id=label_id, _href="#", _onclick="javascript:window.open("+label_url+", '_blank');"))
  else:
    cmd = DIV(dlg, _id=div_id, _class="label_disabled", _style="width: 98%;display:block;padding: 3px;height: auto;padding-bottom: 0px;padding-top: 2px;".replace("98%", width))
    cmd.append(SPAN(label_txt, _id=label_id))
  if value_id!=None:
    cmd.insert(1, A(SPAN(_class="icon trash"),_style="width: 16px;padding: 0px;padding-left: 6px;padding-right: 3px;", 
                                     _class="w2p_trap buttontext button", _href="#null", _title=T("Delete link"), 
                                     _onclick="document.getElementById('"+value_id+"').value='';document.getElementById('"+label_id+"').innerHTML='';"))
  return cmd                                 

def get_customer_selector(customer_custname,width="98%",error_label=False):
  audit_filter = get_audit_filter("customer", None)[0]
  if audit_filter!="disabled":
    return get_base_selector(dlg=get_find_customer_dlg(),label_id="customer_custname",
                          label_url="'"+URL("frm_customer/view/customer")+"/'+document.getElementById('customer_id').value",
                          label_txt=customer_custname,value_id="customer_id",width=width,error_label=error_label)
  else:
    return DIV(SPAN(customer_custname, _id="customer_custname"), _id="customer_id", _class="label_disabled", 
              _style="width: 98%;display:block;padding: 3px;height: 26px;padding-bottom: 0px;padding-top: 2px;".replace("98%", width))

def get_tool_selector(tool_serial,width="98%",error_label=False):
  audit_filter = get_audit_filter("tool", None)[0]
  if audit_filter!="disabled":
    return get_base_selector(dlg=get_find_tool_dlg(),label_id="tool_serial",
                          label_url="'"+URL("frm_tool/view/tool")+"/'+document.getElementById('tool_id').value",
                          label_txt=tool_serial,value_id="tool_id",width=width,error_label=error_label)
  else:
    return DIV(SPAN(tool_serial, _id="tool_serial"), _id="tool_id", _class="label_disabled", 
              _style="width: 98%;display:block;padding: 3px;height: 26px;padding-bottom: 0px;padding-top: 2px;".replace("98%", width))

def get_product_selector(product_description,width="98%",error_label=False,protype="all"):
  audit_filter = get_audit_filter("product", None)[0]
  if audit_filter!="disabled":
    return get_base_selector(dlg=get_find_product_dlg(protype),label_id="product_description",
                          label_url="'"+URL("frm_product/view/product")+"/'+document.getElementById('product_id').value",
                          label_txt=product_description,value_id="product_id",width=width,error_label=error_label)
  else:
    return DIV(SPAN(product_description, _id="product_description"), _id="product_id", _class="label_disabled", 
              _style="width: 98%;display:block;padding: 3px;height: 26px;padding-bottom: 0px;padding-top: 2px;".replace("98%", width))

def get_transitem_selector(reftrans_transnumber,width="98%",error_label=False):  
  return get_base_selector(dlg=get_find_transitem_dlg(),label_id="reftrans_transnumber",
                          label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('trans_id').value",
                          label_txt=reftrans_transnumber,value_id="trans_id",width=width,error_label=error_label)

def get_transpayment_selector(reftrans_transnumber,width="98%",error_label=False):  
  return get_base_selector(dlg=get_find_transpayment_dlg(),label_id="reftrans_transnumber",
                          label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('trans_id').value",
                          label_txt=reftrans_transnumber,value_id="trans_id",width=width,error_label=error_label)

def get_transmovement_selector(reftrans_transnumber,width="98%",error_label=False):  
  return get_base_selector(dlg=get_find_transmovement_dlg(),label_id="reftrans_transnumber",
                          label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('trans_id').value",
                          label_txt=reftrans_transnumber,value_id="trans_id",width=width,error_label=error_label)

def get_project_selector(project_pronumber,width="98%",error_label=False):  
  audit_filter = get_audit_filter("project", None)[0]
  if audit_filter!="disabled":
    return get_base_selector(dlg=get_find_project_dlg(),label_id="project_pronumber",
                          label_url="'"+URL("frm_project/view/project")+"/'+document.getElementById('project_id').value",
                          label_txt=project_pronumber,value_id="project_id",width=width,error_label=error_label)
  else:
    return DIV(SPAN(project_pronumber, _id="project_pronumber"), _id="project_id", _class="label_disabled", 
              _style="width: 98%;display:block;padding: 3px;height: 26px;padding-bottom: 0px;padding-top: 2px;".replace("98%", width))

def get_employee_selector(employee_empnumber,width="98%",error_label=False):
  audit_filter = get_audit_filter("employee", None)[0]
  if audit_filter!="disabled":  
    return get_base_selector(dlg=get_find_employee_dlg(),label_id="employee_empnumber",
                          label_url="'"+URL("frm_employee/view/employee")+"/'+document.getElementById('employee_id').value",
                          label_txt=employee_empnumber,value_id="employee_id",width=width,error_label=error_label)
  else:
    return DIV(SPAN(employee_empnumber, _id="employee_empnumber"), _id="employee_id", _class="label_disabled", 
              _style="width: 98%;display:block;padding: 3px;height: 26px;padding-bottom: 0px;padding-top: 2px;".replace("98%", width))

def get_place_selector(place_planumber,width="98%",error_label=False,placetype="find_place_dlg_all",title=T("Select Place"),
                       value_id="place_id", label_id="place_planumber", fnum=""):  
  return get_base_selector(dlg=get_find_place_dlg(placetype,title,fnum),label_id=label_id,
                          label_url="'"+URL("frm_place/view/place")+"/'+document.getElementById('"+value_id+"').value",
                          label_txt=place_planumber,value_id=value_id,width=width,error_label=error_label)

def get_tab_grid(_query, _field_id, _fields=None, _deletable=False, links=None, multi_page=None, rpl_1="", rpl_2="", 
                 _editable=True, _join=None,_paginate=25):
  try:
    if ns.db(_query).select('count(*)',join=_join,left=None, cacheable=True).first()['count(*)']==0:
      return ""
    if multi_page!=None:
      request.vars.page=request.vars[str(multi_page)]
    else:
      request.vars.page=None
    view_grid = SimpleGrid.grid(query=_query, field_id=_field_id, fields=_fields, 
             groupfields=None, groupby=None, left=None, having=None, join=_join,
             orderby=_field_id, sortable=False, paginate=_paginate, maxtextlength=20,
             showbuttontext=False, deletable=_deletable, editable=_editable, links=links)
    if type(view_grid[1][0][0]).__name__!="TABLE":
      return ""
    else:
      if multi_page!=None:
        if view_grid[len(view_grid)-1]["_class"].startswith("web2py_paginator"):
          pages = view_grid[len(view_grid)-1].elements("a")
          for i in range(len(pages)):
            if pages[i]["_href"]:
              pages[i]["_href"] = pages[i]["_href"].replace(rpl_1,rpl_2).replace("page=",str(multi_page)+"=")
      return view_grid
  except Exception:
    return ""

def get_bool_input(rid, table, fieldname):
  if rid==-1:
    value=ns.db[table][fieldname].default
  else:
    value=ns.db[table](id=rid)[fieldname]
  if value==1:
    return INPUT(_checked="checked",_class="boolean",_id=table+"_"+fieldname,_name=fieldname,_type="checkbox",_value="on")
  else:
    return INPUT(_class="boolean",_id=table+"_"+fieldname,_name=fieldname,_type="checkbox",_value="on")

def create_search_widget(search_menu):
  search_menu = SQLFORM.search_menu(search_menu)
  return lambda sfield, url: CAT(FORM(
      INPUT(_name='keywords', _value=request.vars.keywords,
            _id='web2py_keywords', _onfocus=""),
      INPUT(_type='submit', _value=T('Search'), _class="btn"),
      INPUT(_type='submit', _value=T('Clear'), _class="btn",
            _onclick="jQuery('#web2py_keywords').val('');"),
      INPUT(_type='button', _value=T('More'), _class="btn",
            _onclick="jQuery('#w2p_query_fields').change();jQuery('#w2p_query_panel').slideDown();"),
      _method="GET", _action=url), search_menu)

def show_disabled():
  return HTML(HEAD(TITLE(response.title),
                   LINK(_rel="shortcut icon", _href=URL('static','favicon.ico'), _type="image/x-icon")),
              BODY(DIV(CENTER(TABLE(TR(TD(IMG(_src=URL('static','images/dataprotection.jpg'),
                                      _style="border: solid;border-color: #FFFFFF;"),
                            _style="text-align: center;vertical-align: middle;font-weight: bold;font-family: Arial, Helvetica,  sans-serif;font-size: 20px;")),
                      _style="background-color:#FFFFFF;color:#444444;margin-top:200px;")),_style="width:100%;height:100%")),_style="background-color:#879FB7;")

def clear_post_vars():
  if request.post_vars["id"]=="-1":
    del request.post_vars["id"]
  if request.post_vars.has_key("_formname"):
    del request.post_vars["_formname"]
  if request.post_vars.has_key("_formkey"):
    del request.post_vars["_formkey"]

def set_view_fields(nervatype_name, nervatype_id, tab_index, editable, query, ref_id, rpl_1, rpl_2, add_view_fields=True): 
  def get_fieldlabel(value,row):
      try:
        return dbfu.represent(ns.db.fieldvalue.value,value,row,True)
      except Exception:
        return value
  if add_view_fields:
    fields=[ns.db.deffield.description, ns.db.fieldvalue.value, ns.db.fieldvalue.notes]  
  links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="set_fieldvalue("
                         +str(row["fieldvalue"]["id"])+",'"
                         +str(ns.db.fieldvalue(id=row["fieldvalue"]["id"]).fieldname)+"','"
                         +json.dumps(str(row["deffield"]["description"]))[1:-1]+"','"
                         +json.dumps(str(row["fieldvalue"]["value"]))[1:-1]+"','"
                         +json.dumps(str(get_fieldlabel(row["fieldvalue"]["value"],row)))[1:-1]+"','"
                         +json.dumps(str(row["fieldvalue"]["notes"]))[1:-1]+"','"
                         +ns.db.groups(id=ns.db.deffield(fieldname=ns.db.fieldvalue(id=row["fieldvalue"]["id"]).fieldname).fieldtype).groupvalue+"','"
                         +json.dumps(str(ns.db.deffield(fieldname=ns.db.fieldvalue(id=row["fieldvalue"]["id"]).fieldname).valuelist))[1:-1]+"',"
                         +str(ns.db.deffield(fieldname=ns.db.fieldvalue(id=row["fieldvalue"]["id"]).fieldname).readonly)
                         +")",
                         _title=T("Edit field"))]
  
  fieldvalue_count = ns.db(query).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
  if editable==False:
    response.cmd_fieldvalue_new = SPAN(" ",SPAN(str(fieldvalue_count), _class="detail_count"))
    response.cmd_fields = "" 
    response.cmb_fields = ""
    response.cmd_fieldvalue_submit = ""
  else:
    response.cmd_fieldvalue_new = get_tabnew_button(fieldvalue_count,T('New Additional Data'),cmd_id="cmd_fieldvalue_new",
                              cmd = "$('#tabs').tabs({ selected: "+str(tab_index)+" });set_fieldvalue(-1, '', '', '', '', '', '', '', 0)")
    response.cmd_fields = get_goprop_button(title=T("Edit Additional Data"), url=URL("frm_deffield_"+nervatype_name+"?back=1"))
    response.cmb_fields = get_cmb_fields(nervatype_id)
    response.cmd_fieldvalue_submit = get_command_button(caption=T("Save"),title=T("Update data"),color="008B00", _id="cmd_field_submit",
                            cmd="fieldvalue_update();return true;")
    if add_view_fields:
      links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                       _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this data?')+
                            "')){window.location ='"+URL("frm_"+nervatype_name+"/delete/fieldvalue/"+str(row["fieldvalue"]["id"]))+"';};return false;", 
                       _title=T("Delete Additional Data")))
  
  setting_audit_filter = get_audit_filter("setting", None)[0]
  if setting_audit_filter=="disabled":
    response.cmd_fields = ""
    
  if add_view_fields:
    response.view_fields = get_tab_grid(_query=query, _field_id=ns.db.fieldvalue.id, _fields=fields, _deletable=False, _editable=False, links=links, 
                             multi_page="fd_page", rpl_1=rpl_1, rpl_2=rpl_2)
  
  response.fieldvalue_form = SQLFORM(ns.db.fieldvalue, submit_button=T("Save"),_id="frm_fieldvalue")
  response.fieldvalue_form.process()  
  response.fieldvalue_icon = URL(dir_images,'icon16_deffield.png')
  response.cmd_fieldvalue_cancel = A(SPAN(_class="icon cross"), _id="cmd_fieldvalue_cancel", 
    _style="height: 15px;",
    _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
    _onclick= "document.getElementById('edit_fieldvalue').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
  response.fieldvalue_id = INPUT(_name="id", _type="hidden", _value="", _id="fieldvalue_id")
  response.fieldvalue_ref_id = INPUT(_name="ref_id", _type="hidden", _value=ref_id, _id="fieldvalue_ref_id")
  response.fieldvalue_fieldname = INPUT(_name="fieldname", _type="hidden", _value="", _id="fieldvalue_fieldname")
  response.fieldvalue_fieldtype = INPUT(_name="fieldtype", _type="hidden", _value="", _id="fieldvalue_fieldtype")
  response.fieldvalue_readonly = INPUT(_name="readonly", _type="hidden", _value="", _id="fieldvalue_readonly")
  
  audit_filter = get_audit_filter("customer", None)[0]
  if audit_filter!="disabled":
    response.fieldvalue_customer_selector = get_base_selector(dlg=get_find_customer_dlg(),label_id="fieldvalue_value_customer_label",
                        label_url="'"+URL("frm_customer/view/customer")+"/'+document.getElementById('fieldvalue_value').value",
                        label_txt="",value_id="fieldvalue_value",width="100%",error_label=False, div_id="fieldvalue_value_customer")
  else:
    response.fieldvalue_customer_selector = DIV(SPAN("", _id="fieldvalue_value_customer_label"), _id="fieldvalue_value_customer", _class="label_disabled", 
              _style="width: 100%;display:block;padding: 3px;height: 24px;padding-bottom: 0px;padding-top: 2px;")
  
  audit_filter = get_audit_filter("tool", None)[0]
  if audit_filter!="disabled":
    response.fieldvalue_tool_selector = get_base_selector(dlg=get_find_tool_dlg(),label_id="fieldvalue_value_tool_label",
                        label_url="'"+URL("frm_tool/view/tool")+"/'+document.getElementById('fieldvalue_value').value",
                        label_txt="",value_id="fieldvalue_value",width="100%",error_label=False, div_id="fieldvalue_value_tool")
  else:
    response.fieldvalue_tool_selector = DIV(SPAN("", _id="fieldvalue_value_tool_label"), _id="fieldvalue_value_tool", _class="label_disabled", 
              _style="width: 100%;display:block;padding: 3px;height: 24px;padding-bottom: 0px;padding-top: 2px;")
  
  audit_filter = get_audit_filter("product", None)[0]
  if audit_filter!="disabled":
    response.fieldvalue_product_selector = get_base_selector(dlg=get_find_product_dlg("all"),label_id="fieldvalue_value_product_label",
                        label_url="'"+URL("frm_product/view/product")+"/'+document.getElementById('fieldvalue_value').value",
                        label_txt="",value_id="fieldvalue_value",width="100%",error_label=False, div_id="fieldvalue_value_product")
  else:
    response.fieldvalue_product_selector = DIV(SPAN("", _id="fieldvalue_value_product_label"), _id="fieldvalue_value_product", _class="label_disabled", 
              _style="width: 100%;display:block;padding: 3px;height: 24px;padding-bottom: 0px;padding-top: 2px;")
    
  response.fieldvalue_transitem_selector = get_base_selector(dlg=get_find_transitem_dlg(),label_id="fieldvalue_value_transitem_label",
                        label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('fieldvalue_value').value",
                        label_txt="",value_id="fieldvalue_value",width="100%",error_label=False, div_id="fieldvalue_value_transitem")
  response.fieldvalue_transpayment_selector = get_base_selector(dlg=get_find_transpayment_dlg(),label_id="fieldvalue_value_transpayment_label",
                        label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('fieldvalue_value').value",
                        label_txt="",value_id="fieldvalue_value",width="100%",error_label=False, div_id="fieldvalue_value_transpayment")
  response.fieldvalue_transmovement_selector = get_base_selector(dlg=get_find_transmovement_dlg(),label_id="fieldvalue_value_transmovement_label",
                        label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('fieldvalue_value').value",
                        label_txt="",value_id="fieldvalue_value",width="100%",error_label=False, div_id="fieldvalue_value_transmovement")
  
  audit_filter = get_audit_filter("project", None)[0]
  if audit_filter!="disabled":
    response.fieldvalue_project_selector = get_base_selector(dlg=get_find_project_dlg(),label_id="fieldvalue_value_project_label",
                        label_url="'"+URL("frm_project/view/project")+"/'+document.getElementById('fieldvalue_value').value",
                        label_txt="",value_id="fieldvalue_value",width="100%",error_label=False, div_id="fieldvalue_value_project")
  else:
    response.fieldvalue_project_selector = DIV(SPAN("", _id="fieldvalue_value_project_label"), _id="fieldvalue_value_project", _class="label_disabled", 
              _style="width: 100%;display:block;padding: 3px;height: 24px;padding-bottom: 0px;padding-top: 2px;")
  
  audit_filter = get_audit_filter("employee", None)[0]
  if audit_filter!="disabled":
    response.fieldvalue_employee_selector = get_base_selector(dlg=get_find_employee_dlg(),label_id="fieldvalue_value_employee_label",
                        label_url="'"+URL("frm_employee/view/employee")+"/'+document.getElementById('fieldvalue_value').value",
                        label_txt="",value_id="fieldvalue_value",width="100%",error_label=False, div_id="fieldvalue_value_employee")
  else:
    response.fieldvalue_employee_selector = DIV(SPAN("", _id="fieldvalue_value_employee_label"), _id="fieldvalue_value_employee", _class="label_disabled", 
              _style="width: 100%;display:block;padding: 3px;height: 24px;padding-bottom: 0px;padding-top: 2px;")
  
  response.fieldvalue_place_selector = get_base_selector(dlg=get_find_place_dlg("find_place_dlg_all",T("Select Place"),""),label_id="fieldvalue_value_place_label",
                        label_url="'"+URL("frm_place/view/place")+"/'+document.getElementById('fieldvalue_value').value",
                        label_txt="",value_id="fieldvalue_value",width="100%",error_label=False, div_id="fieldvalue_value_place")
  return links 

@ns_auth.requires_login()
def frm_event():
  audit_filter = get_audit_filter("event", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    event_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    redirect(URL('frm_event/view/event/'+str(event_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    event_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    if delete_row("fieldvalue", fieldvalue_id, "event", event_id):
      redirect(URL('frm_event/view/event/'+str(event_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.fieldvalue.id==request.post_vars["id"]).validate_and_update(**request.post_vars)      
      else:
        ns.db.fieldvalue.validate_and_insert(**request.post_vars)
      setLogtable("update", "log_event_update", "event", request.post_vars["ref_id"])
      redirect(URL('frm_event/view/event/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
    
  if ruri.find("new")>0:
    event_id = -1
    nervatype_name = str(request.vars.refnumber).split("/")[0]
    ref_id = int(str(request.vars.refnumber).split("?")[0].split("/")[1])
  else:
    event_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    nervatype_name = ns.db.groups(id=ns.db.event(id=event_id).nervatype).groupvalue
    ref_id = ns.db.event(id=event_id).ref_id
  
  if ruri.find("delete/event")>0:
    setLogtable("deleted", "log_event_deleted", "event", event_id)
    delete_ini = getSetting("set_trans_deleted")
    if delete_ini != "true":
      values = {"deleted":1}
      ns.db(ns.db.event.id==event_id).update(**values)
    else:
      dfield = deleteFieldValues("event", event_id)
      if dfield!=True:
        session.flash = dfield
        redirect(URL("frm_"+nervatype_name+"/view/"+nervatype_name+"/"+str(ref_id)))
      ns.db(ns.db.event.id==event_id).delete()
      ns.db.commit()
    redirect(URL("frm_"+nervatype_name+"/view/"+nervatype_name+"/"+str(ref_id)))
  
  response.view=dir_view+'/event.html'
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  response.icon_deffield = IMG(_src=URL(dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_note = IMG(_src=URL(dir_images,'icon16_note.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.from_title = get_nervatype_label(nervatype_name,ref_id)
  ns.db.event.id.readable = ns.db.event.id.writable = False
  ns.db.event.nervatype.readable = ns.db.event.nervatype.writable = False
  ns.db.event.ref_id.readable = ns.db.event.ref_id.writable = False
  if event_id>0:
    form = SQLFORM(ns.db.event, record = event_id, submit_button=T("Save"),_id="frm_event")
    response.subtitle=T('EVENT')
    response.cmd_export = get_command_button(caption=T("Export"), title=T("Export to iCal"), 
                                             cmd = "window.open('"+URL("export2ical")+"?id="+str(event_id)+"', '_blank');")
  else:
    form = SQLFORM(ns.db.event, submit_button=T("Save"),_id="frm_event")
    form.vars.nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue==nervatype_name)).select().as_list()[0]["id"]
    form.vars.ref_id = ref_id
    form.vars.calnumber = dbfu.nextNumber(ns, {"id":"calnumber", "step":False})
    response.subtitle=T('NEW EVENT')
    response.cmd_export = ""
  
  response.cmd_update = get_command_button(caption=T("Save"), title=T("Save event data"), color="008B00",
                                             cmd = "event_update();")
  nervatype_audit_filter = get_audit_filter(nervatype_name, None)[0]
  event_audit_filter = get_audit_filter("event", None)[0]
  setting_audit_filter = get_audit_filter("setting", None)[0]
  if (nervatype_audit_filter in ("disabled")) or (event_audit_filter in ("disabled")):
    response.cmd_back = get_home_button()
  else:
    response.cmd_back = get_back_button(URL("frm_"+nervatype_name+"/view/"+nervatype_name+"/"+str(ref_id)))
  response.cmd_help = get_help_button("event") 
                
  if (nervatype_audit_filter in ("readonly","disabled")) or (event_audit_filter in ("readonly","disabled")):
    form.custom.submit = ""
    response.cmd_new = ""
  else:
    response.cmd_new = get_new_button(URL('frm_event/new/event?refnumber='+nervatype_name+"/"+str(ref_id)))  
  
  if form.validate(keepvalues=True):      
    if event_id==-1:
      nextnumber = dbfu.nextNumber(ns, {"id":"calnumber", "step":False})
      if form.vars.calnumber == nextnumber:
        form.vars.calnumber = dbfu.nextNumber(ns, {"id":"calnumber", "step":True})
      form.vars.id = ns.db.event.insert(**dict(form.vars))
      setLogtable("update", "log_event_update", "event", form.vars.id)
      redirect(URL('frm_event/view/event/'+str(form.vars.id)))      
    else:
      ns.db(ns.db.event.id==event_id).update(**form.vars)
      setLogtable("update", "log_event_update", "event", event_id)
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  else:
    pass
  
  #additional fields data
  nervatype_event = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="event")).select().as_list()[0]["id"]
  if event_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_event)&(ns.db.fieldvalue.ref_id==event_id))
    editable = not (nervatype_audit_filter in ("readonly","disabled")) or (event_audit_filter in ("readonly","disabled"))
    set_view_fields("event", nervatype_event, 1, editable, fieldvalue, event_id, "/frm_event", "/frm_event/view/event/"+str(event_id))
  
  if (nervatype_audit_filter in ("readonly","disabled")) or (event_audit_filter in ("readonly","disabled")) or (setting_audit_filter in ("disabled")):
    response.cmd_groups = ""
  else:
    response.cmd_groups = get_goprop_button(title=T("Edit Event Groups"), url=URL("frm_groups_eventgroup?back=1")) 
  
  return dict(form=form)

def get_default_value(fieldtype):
  fld_type = ns.db.groups(id=fieldtype)["groupvalue"]
  if fld_type == 'bool':
    return "false"
  elif fld_type == 'integer' or fld_type == 'float':
    return "0"
  else:
    return ""

def get_prev_lnk(transtype, cur_id, direction):
  transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue==transtype)).select().as_list()[0]["id"]
  direction_id = ns.db((ns.db.groups.groupname=="direction")&(ns.db.groups.groupvalue==direction)).select().as_list()[0]["id"]
  mid = ns.db.trans.id.max()
  query = (ns.db.trans.transtype==transtype_id)
  if transtype!="cash" and transtype!="waybill":
    query = query&(ns.db.trans.direction==direction_id)
  if cur_id>-1:
    query = query&(ns.db.trans.id<cur_id)
  if (transtype=="invoice" and direction=="out") or (transtype=="receipt" and direction=="out") or (transtype=="cash"):  
    pass
  else:
    query = query&(ns.db.trans.deleted==0)
  
  #set transfilter
  query = set_transfilter(query)
  
  mrow = ns.db(query).select(mid)
  if mrow.first()[mid]==None:
    prev_id = cur_id
  else:
    prev_id = mrow.first()[mid]
  if prev_id==-1:
    return URL('frm_trans/new/trans/'+transtype+'/'+direction)
  else:
    return URL('frm_trans/view/trans/'+str(prev_id))

def get_next_lnk(transtype, cur_id, direction):
  if cur_id==-1:
    return URL('frm_trans/new/trans/'+transtype+'/'+direction)
  
  transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue==transtype)).select().as_list()[0]["id"]
  direction_id = ns.db((ns.db.groups.groupname=="direction")&(ns.db.groups.groupvalue==direction)).select().as_list()[0]["id"]
  mid = ns.db.trans.id.min()
  query = (ns.db.trans.transtype==transtype_id)&(ns.db.trans.id>cur_id)
  if transtype!="cash" and transtype!="waybill":
    query = query&(ns.db.trans.direction==direction_id)
  if (transtype=="invoice" and direction=="out") or (transtype=="receipt" and direction=="out") or (transtype=="cash"):  
    pass
  else:
    query = query&(ns.db.trans.deleted==0)
  
  #set transfilter
  query = set_transfilter(query)
  
  mrow = ns.db(query).select(mid)
  if mrow.first()[mid]==None:
    return URL('frm_trans/new/trans/'+transtype+'/'+direction)
  else:
    next_id = mrow.first()[mid]
    return URL('frm_trans/view/trans/'+str(next_id))

@ns_auth.requires_login()
def get_product_price():
  #ruri = request.wsgi.environ["REQUEST_URI"]
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
      return dbfu.getPriceValueDal(ns, params)
    else:    
      return 0
  else:
    return 0

def update_custinvoice_prop(trans_id):
  updateFieldValue(trans_id, "trans_custinvoice_compname", value=ns.db.customer(id=1).custname)
  updateFieldValue(trans_id, "trans_custinvoice_comptax", value=ns.db.customer(id=1).taxnumber)
  customer_id = ns.db.trans(id=trans_id).customer_id
  updateFieldValue(trans_id, "trans_custinvoice_custname", value=ns.db.customer(id=customer_id).custname)
  updateFieldValue(trans_id, "trans_custinvoice_custtax", value=ns.db.customer(id=customer_id).taxnumber)
  
  customer_nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
  address = ns.db((ns.db.address.nervatype==customer_nervatype)&(ns.db.address.ref_id==1)&(ns.db.address.deleted==0)).select().as_list()
  if len(address)>0:
    address_str = str(address[0]["city"])+" "+str(address[0]["street"])
  else:
    address_str=""
  updateFieldValue(trans_id, "trans_custinvoice_compaddress", value=address_str)
  address = ns.db((ns.db.address.nervatype==customer_nervatype)&(ns.db.address.ref_id==customer_id)&(ns.db.address.deleted==0)).select().as_list()
  if len(address)>0:
    address_str = str(address[0]["city"])+" "+str(address[0]["street"])
  else:
    address_str=""
  updateFieldValue(trans_id, "trans_custinvoice_custaddress", value=address_str)

@ns_auth.requires_login()
def copy_trans():
  if request.vars.trans_id:
    try:
      return create_trans(request.vars.trans_id)
    except Exception, err:
      return "err|-1|"+str(err)
  else:
    return "err|-1|"+T("Missing trans id!")

@ns_auth.requires_login()
def cancel_trans():
  if request.vars.trans_id:
    try:
      return create_trans(request.vars.trans_id,"cancellation")
    except Exception, err:
      return "err|-1|"+str(err)
  else:
    return "err|-1|"+T("Missing trans id!")

@ns_auth.requires_login()
def corr_trans():
  if request.vars.trans_id:
    try:
      return create_trans(request.vars.trans_id,"amendment")
    except Exception, err:
      return "err|-1|"+str(err)
  else:
    return "err|-1|"+T("Missing trans id!")

@ns_auth.requires_login()
def create_from_trans():
  if request.vars.trans_id and request.vars.new_transtype and request.vars.new_direction and request.vars.from_inventory and request.vars.netto_qty:
    try:
      _from_inventory = (request.vars.from_inventory=='1')
      _netto_qty = (request.vars.netto_qty=='1')
      return create_trans(request.vars.trans_id,transcast="normal",new_transtype=request.vars.new_transtype,
                          new_direction=request.vars.new_direction,from_inventory=_from_inventory,netto_qty=_netto_qty)
    except Exception, err:
      return "err|-1|"+str(err)
  else:
    return "err|-1|"+T("Missing parameters!")
  
@ns_auth.requires_login()
def dlg_create_trans():
  ruri = request.wsgi.environ["REQUEST_URI"]
  trans_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  directions = ["in","out"]
  def_transtype = base_transtype = ns.db.groups(id=ns.db.trans(id=trans_id).transtype).groupvalue
  #disabled create fom delivery
  element_count = ns.db((ns.db.trans.id==trans_id)&(ns.db.item.trans_id==ns.db.trans.id)&(ns.db.item.deleted==0)
        &(ns.db.fieldvalue.ref_id==ns.db.item.product_id)
        &(ns.db.fieldvalue.fieldname=='product_element')).select('count(*)').first()['count(*)']
  if def_transtype=="offer":
    doctypes = ["offer","order","worksheet","rent"]
    def_transtype="order"
    netto_color = "#C5C5C5"
    from_color = "#C5C5C5"
  elif def_transtype=="order":
    doctypes = ["offer","order","worksheet","rent","invoice","receipt"]
    def_transtype="invoice"
    netto_color = "#444444"
    from_color = "#444444" if element_count==0 else "#C5C5C5"
  elif def_transtype=="worksheet":
    doctypes = ["offer","order","worksheet","rent","invoice","receipt"]
    def_transtype="invoice"
    netto_color = "#444444"
    from_color = "#444444" if element_count==0 else "#C5C5C5"
  elif def_transtype=="rent":
    doctypes = ["offer","order","worksheet","rent","invoice","receipt"]
    def_transtype="invoice"
    netto_color = "#444444"
    from_color = "#444444" if element_count==0 else "#C5C5C5"
  elif def_transtype=="invoice":
    doctypes = ["order","worksheet","rent","invoice","receipt"]
    def_transtype="order"
    netto_color = "#C5C5C5"
    from_color = "#C5C5C5"
  elif def_transtype=="receipt":
    doctypes = ["order","worksheet","rent","invoice","receipt"]
    def_transtype="order"
    netto_color = "#C5C5C5"
    from_color = "#C5C5C5"
  def_direction = ns.db.groups(id=ns.db.trans(id=trans_id).direction).groupvalue
                          
  rtable = TABLE(_style="width: 100%;")
  rtable.append(TR(TD(INPUT(_type="hidden", _value=base_transtype, _id="base_transtype"),
                      INPUT(_type="hidden", _value=element_count, _id="element_count"),
                      ns.db.trans(id=trans_id).transnumber,_colspan="3",
                      _style="background-color: #F1F1F1;font-weight: bold;text-align: center;border-bottom: solid;padding: 5px;")))
  cmb_doctypes = SELECT(*[OPTION(T(doctype), _value=doctype, _selected=(doctype==def_transtype)) for doctype in doctypes], 
                        _id="cmb_doctypes",_style="width: 100%;height: 25px;",
                        _onChange = "create_newtype_change();")
  cmb_directions = SELECT(*[OPTION(T(direc), _value=direc, _selected=(direc==def_direction)) for direc in directions], 
                          _id="cmb_directions",_style="width: 100%;height: 25px;")
  rtable.append(TR(
                   TD(T("New type"),_style="width: 100px;background-color: #F1F1F1;font-weight: bold;text-align: left;padding: 5px;border-bottom: solid;"),
                   TD(cmb_doctypes,_style="padding: 5px;padding-right: 0px;border-bottom: solid;"),
                   TD(cmb_directions,_style="width: 100px;padding: 5px;padding-right: 0px;border-bottom: solid;")))
  rtable_check = TABLE(_style="width: 100%;")
  rtable_check.append(TR(
                   TD(INPUT(_type='checkbox', _id='cb_netto', value='on', _disabled=(netto_color=="#C5C5C5")),_style="width: 10px;padding:0px;vertical-align: top;"),
                   TD(T("Invoiced amount deduction"), _id='cb_netto_label',_style="padding-top:3px;color:"+netto_color),
                   TD(INPUT(_type='checkbox', _id='cb_from', value='', _disabled=(from_color=="#C5C5C5"), _onChange = "from_delivery_change();"),
                      _style="width: 10px;padding:0px;vertical-align: top;"),
                   TD(T("Create by delivery"), _id='cb_from_label',_style="padding-top:3px;color:"+from_color)))
  rtable.append(TR(TD(rtable_check,_colspan="3", 
                      _style="background-color: #F1F1F1;font-weight: bold;text-align: left;padding: 5px;border-bottom: solid;")))
  cmd_ok = INPUT(_type="button", _value="Creating a document", _style="height: 40px !important;padding-top: 5px !important;",
                      _onclick="create_trans('"+URL("create_from_trans")+"?trans_id="+str(trans_id)
                              +"','"+URL("frm_trans/view/trans")+"/');return false;")
  rtable.append(TR(TD(cmd_ok,_colspan="3", 
                      _style="background-color: #F1F1F1;font-weight: bold;text-align: center;padding: 5px;padding-top: 8px;border-bottom: solid;")))  

  return DIV(rtable, _id="dlg_create_trans")
      
def create_trans(base_id,transcast="normal",new_transtype=None,new_direction=None,from_inventory=False,netto_qty=False):
  
  new_id = -1
  base_trans = ns.db.trans(id=base_id)
  base_transcast = ns.db((ns.db.fieldvalue.ref_id==base_id)&(ns.db.fieldvalue.fieldname=="trans_transcast")).select()
  base_transcast = base_transcast[0].value if len(base_transcast)>0 else "normal"
  
  #set base data
  if new_transtype and new_direction:
    transtype = new_transtype
    transtype_audit_filter = get_audit_filter("trans", transtype)
    if transtype_audit_filter[0]=="disabled":
      return "err|"+str(new_id)+"|"+T("Disabled type: "+transtype)
    transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue==new_transtype)).select()[0].id
    direction = new_direction
    direction_id = ns.db((ns.db.groups.groupname=="direction")&(ns.db.groups.groupvalue==new_direction)).select()[0].id
  else:
    transtype = ns.db.groups(id=base_trans.transtype).groupvalue
    transtype_id = base_trans.transtype
    direction = ns.db.groups(id=base_trans.direction).groupvalue
    direction_id = base_trans.direction
    
  #to check some things...
  if base_transcast=="cancellation":
    return "err|"+str(new_id)+"|"+T("Canceling document does not make a copy!")
  if transcast=="cancellation" and base_trans.deleted==0 and transtype not in("delivery","inventory"):
    return "err|"+str(new_id)+"|"+T("Create cancellation document, but may have been deleted document!")
  if transcast=="amendment" and base_trans.deleted==1:
    return "err|"+str(new_id)+"|"+T("Deleted document does not make a copy!")
  
  nervatype_trans_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
  nervatype_groups_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  nervatype_movement_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="movement")).select().as_list()[0]["id"]
  nervatype_item_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="item")).select().as_list()[0]["id"]
        
  nextnumber_id = transtype if transtype in("waybill","cash") else transtype+"_"+direction
  nextnumber = dbfu.nextNumber(ns, {"id":nextnumber_id, "step":True})
  
  duedate = datetime.datetime.strptime(str(datetime.date.today())+" 00:00:00", str('%Y-%m-%d %H:%M:%S'))
  if transtype=="invoice" and direction=="out":
    deadline=getSetting("default_deadline")
    if deadline!="": duedate += datetime.timedelta(int(deadline))
  
  #creat trand data from the original          
  values = {"transtype":transtype_id,"transnumber":nextnumber,"ref_transnumber":base_trans.transnumber,"crdate":datetime.datetime.now().date(),
            "transdate":datetime.datetime.now().date(),"duedate":duedate,"customer_id":base_trans.customer_id,
            "employee_id":base_trans.employee_id,"department":base_trans.department,"project_id":base_trans.project_id,
            "place_id":base_trans.place_id,"paidtype":base_trans.paidtype,"curr":base_trans.curr,"notax":base_trans.notax,
            "paid":0,"acrate":base_trans.acrate,"notes":base_trans.notes,"intnotes":base_trans.intnotes,"fnote":base_trans.fnote,
            "transtate":ns.db((ns.db.groups.groupname=="transtate")&(ns.db.groups.groupvalue=="ok")).select().as_list()[0]["id"],
            "closed":0,"deleted":0,"direction":direction_id,"cruser_id":session.auth.user.id}
  
  if transcast=="cancellation":
    values["transnumber"]+="/C"
    if transtype not in("delivery","inventory"): values["deleted"]=1
    values["transdate"]=base_trans.transdate
    values["duedate"]=base_trans.duedate
    linktype=1
  elif transcast=="amendment":
    values["transnumber"]+="/A"
    linktype=2
  else:
    linktype=0
  new_id = ns.db.trans.insert(**values)
  ns.db.fieldvalue.validate_and_insert(**{"fieldname":"trans_transcast","ref_id":new_id,"value":transcast})
  
  #set a link for the old trans
  if not (transtype=="delivery" and direction!="transfer"):
    values = {"nervatype_1":nervatype_trans_id,"ref_id_1":new_id,"nervatype_2":nervatype_trans_id,"ref_id_2":base_trans.id,"linktype":linktype}
    ns.db.link.insert(**values)
  
  #link to the all trans groups
  glinks = ns.db((ns.db.link.ref_id_1==base_trans.id)&(ns.db.link.nervatype_1==nervatype_trans_id)&(ns.db.link.deleted==0)
              &(ns.db.link.nervatype_2==nervatype_groups_id)).select(orderby=ns.db.link.id)
  for glink in glinks:       
    values = {"nervatype_1":nervatype_trans_id, "ref_id_1":new_id, "nervatype_2":nervatype_groups_id, "ref_id_2":glink.ref_id_2}
    ns.db.link.insert(**values)
  
  #link and set the additional fields
  fields = ns.db((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
             &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_trans_id)&(ns.db.fieldvalue.ref_id==base_trans.id)).select(ns.db.fieldvalue.ALL,orderby=ns.db.fieldvalue.id)
  for field in fields:
    ns.db.fieldvalue.validate_and_insert(**{"fieldname":field.fieldname,"ref_id":new_id,"value":field.value,"notes":field.notes})
  if transtype in("invoice"):
    update_custinvoice_prop(new_id)
  
  #item data
  if transtype in("invoice","receipt"):
    def get_product_qty(items,product_id,deposit):
      retvalue = 0
      for item in items:
        if item.product_id==product_id and item.deposit==deposit:
          retvalue+=item.qty
      return retvalue
    def recalc_item(item,digit):
      item.netamount = round(item.fxprice*(1-item.discount/100)*item.qty,digit);
      item.vatamount = round(item.netamount*ns.db.tax(id=item.tax_id).rate,digit);
      item.amount = item.netamount + item.vatamount;
      return item
    items=[]
    products={}
    transtype_invoice = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
    transtype_receipt = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="receipt")).select().as_list()[0]["id"]
    invoice_items = ns.db((ns.db.link.ref_id_2==base_trans.id)&(ns.db.link.nervatype_1==nervatype_trans_id)&(ns.db.link.deleted==0)
            &(ns.db.link.nervatype_2==nervatype_trans_id)&(ns.db.link.ref_id_1==ns.db.trans.id)&(ns.db.trans.deleted==0)
            &((ns.db.trans.transtype==transtype_invoice)|(ns.db.trans.transtype==transtype_receipt))
            &(ns.db.trans.id==ns.db.item.trans_id)&(ns.db.item.deleted==0)).select(ns.db.item.ALL,orderby=ns.db.item.id)
    base_digit = ns.db.currency(curr=base_trans.curr).digit
            
    if from_inventory:
      #create from order,worksheet and rent, on base the delivery rows
      query = ((ns.db.item.trans_id==base_trans.id)&(ns.db.item.deleted==0)&
               (ns.db.link.nervatype_2==nervatype_item_id)&(ns.db.link.ref_id_2==ns.db.item.id)&
               (ns.db.item.product_id==ns.db.product.id)&
               (ns.db.link.nervatype_1==nervatype_movement_id)&(ns.db.link.ref_id_1==ns.db.movement.id)
               &(ns.db.link.deleted==0)&(ns.db.movement.deleted==0))
      groupfields=[ns.db.item.id,ns.db.movement.product_id,ns.db.movement.qty.sum().with_alias('qty')]
      groupby=[ns.db.item.id|ns.db.movement.product_id]
      inventory_items = ns.db(query).select(*groupfields,groupby=groupby,cacheable=True,orderby=ns.db.item.id)
      base_direction = ns.db.groups(id=base_trans.direction).groupvalue
      
      for inv_item in inventory_items:
        item = ns.db.item(id=inv_item.item.id)
        if item:
          iqty = -inv_item.qty if base_direction=="out" else inv_item.qty
          if item.deleted==0 and iqty>0:
            if not products.has_key(item.product_id):
              iqty = iqty - get_product_qty(invoice_items,item.product_id,False)
              products[item.product_id]=True
            if iqty!=0:
              item.qty = iqty
              item = recalc_item(item,base_digit)
              items.append(item)
    else:
      if netto_qty:
        #create from order,worksheet and rent, on base the invoice rows
        base_items = ns.db((ns.db.item.trans_id==base_trans.id)&(ns.db.item.deleted==0)).select(orderby=ns.db.item.id)
        for item in base_items:
          iqty = item.qty
          if not products.has_key(item.product_id):
            iqty = iqty - get_product_qty(invoice_items,item.product_id,False)
            products[item.product_id]=True
          if iqty!=0:
            item.qty = iqty
            item = recalc_item(item,base_digit)
            items.append(item)
      else:
        items = ns.db((ns.db.item.trans_id==base_trans.id)&(ns.db.item.deleted==0)).select(orderby=ns.db.item.id).as_list(storage_to_dict=False)
    
    #put to deposit rows
    for item in invoice_items:
      if item.deposit==1:
        dqty = get_product_qty(invoice_items,item.product_id,True)
        if dqty!=0:
          item.qty = -dqty
          items.insert(0,item)
  else:
    items = ns.db((ns.db.item.trans_id==base_trans.id)&(ns.db.item.deleted==0)).select(orderby=ns.db.item.id)
    
  for item in items:
    del item.id
    del item.update_record
    del item.delete_record
    item.trans_id = new_id
    item.ownstock = 0
    if transtype not in("invoice","receipt"):
      item.deposit = 0
    if transcast=="cancellation":
      item.qty=-item.qty
      item.netamount=-item.netamount
      item.vatamount=-item.vatamount
      item.amount=-item.amount
    ns.db.item.insert(**dict(item))
    if transcast=="amendment":
      item.qty=-item.qty
      item.netamount=-item.netamount
      item.vatamount=-item.vatamount
      item.amount=-item.amount
      ns.db.item.insert(**dict(item))
      
  payments = ns.db((ns.db.payment.trans_id==base_trans.id)&(ns.db.payment.deleted==0)).select(orderby=ns.db.payment.id)
  for payment in payments:
    del payment.id
    del payment.update_record
    del payment.delete_record
    payment.trans_id = new_id
    if transcast=="cancellation": payment.amount = -payment.amount
    ns.db.payment.insert(**dict(payment))
  
  if transtype=="delivery" and direction=="transfer":
    movements = ns.db((ns.db.movement.id.belongs(ns.db((ns.db.link.ref_id_1.belongs(ns.db(ns.db.movement.trans_id==base_trans.id).select(ns.db.movement.id)))
                       &(ns.db.link.nervatype_1==nervatype_movement_id)&(ns.db.link.deleted==0)
                       &(ns.db.link.nervatype_2==nervatype_movement_id)).select(ns.db.link.ref_id_2.with_alias('id'))))
                  &(ns.db.movement.deleted==0)&(ns.db.movement.product_id==ns.db.product.id)).select(ns.db.movement.ALL,orderby=ns.db.movement.id)
  else:
    movements = ns.db((ns.db.movement.trans_id==base_trans.id)&(ns.db.movement.deleted==0)).select(orderby=ns.db.movement.id)
  for movement in movements:
    if transtype=="delivery" and direction=="transfer":
      ilinks = ns.db((ns.db.link.ref_id_2==movement.id)&(ns.db.link.nervatype_2==nervatype_movement_id)&(ns.db.link.deleted==0)
              &(ns.db.link.nervatype_1==nervatype_movement_id)).select()
      del movement.id
      del movement.update_record
      del movement.delete_record
      movement.trans_id = new_id
      if transcast=="cancellation": movement.qty = -movement.qty
      movement_id_1 = ns.db.movement.insert(**dict(movement))
      movement_2 = ns.db.movement(id=ilinks[0].ref_id_1)
      del movement_2.id
      del movement_2.update_record
      del movement_2.delete_record
      movement_2.trans_id = new_id
      if transcast=="cancellation": movement_2.qty = -movement_2.qty
      movement_id_2 = ns.db.movement.insert(**dict(movement_2))
      values = {"nervatype_2":nervatype_movement_id, "ref_id_2":movement_id_1, "nervatype_1":nervatype_movement_id, "ref_id_1":movement_id_2}
      ns.db.link.insert(**values)
    else:
      ilinks = ns.db((ns.db.link.ref_id_1==movement.id)&(ns.db.link.nervatype_1==nervatype_movement_id)&(ns.db.link.deleted==0)
              &(ns.db.link.nervatype_2==nervatype_item_id)).select()
      del movement.id
      del movement.update_record
      del movement.delete_record
      movement.trans_id = new_id
      if transcast=="cancellation": movement.qty = -movement.qty
      movement_id = ns.db.movement.insert(**dict(movement))
      for ilink in ilinks:       
        values = {"nervatype_1":nervatype_movement_id, "ref_id_1":movement_id, "nervatype_2":nervatype_item_id, "ref_id_2":ilink.ref_id_2}
        ns.db.link.insert(**values)
  
  return "ok|"+str(new_id)+"|"    

@ns_auth.requires_login()
def load_formula():
  if request.vars.production_id:
    production = ns.db.trans(id=request.vars.production_id)
    production_qty = ns.db((ns.db.movement.trans_id==production.id)&(ns.db.movement.shared==1)&(ns.db.movement.deleted==0)).select()[0].qty
  else:
    return T("Missing production!")
  if request.vars.formula_id:
    formula = ns.db.trans(id=request.vars.formula_id)
    movetype_head = ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="head")).select().as_list()[0]["id"]
    movetype_plan = ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="plan")).select().as_list()[0]["id"]
    formula_qty = ns.db((ns.db.movement.trans_id==formula.id)&(ns.db.movement.movetype==movetype_head)&(ns.db.movement.deleted==0)).select()[0].qty
    items = ns.db((ns.db.movement.trans_id==formula.id)&(ns.db.movement.deleted==0)&(ns.db.movement.movetype==movetype_plan)).select()
  else:
    return T("Missing formula!")
  movetype_inventory = ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="inventory")).select().as_list()[0]["id"]
  ns.db((ns.db.movement.trans_id==production.id)&(ns.db.movement.shared==0)).update(**{"deleted":1})
  for item in items:
    if item.shared==1:
      qty = -math.ceil(production_qty/formula_qty)
    else:
      qty = -(production_qty/formula_qty)*item.qty
    if item.place_id:
      place_id=item.place_id
    else:
      place_id=production.place_id
    ns.db.movement.insert(**{"trans_id":production.id,"shippingdate":production.transdate,"movetype":movetype_inventory, 
                             "product_id":item.product_id, "qty":qty,"place_id":place_id})
  return "OK"
  
@ns_auth.requires_login()
def frm_trans():
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/movement")>0 or ruri.find("view/movement")>0:
    movement_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.movement(id=movement_id).trans_id
    redirect(URL('frm_trans/view/trans/'+str(trans_id)))
    
  if ruri.find("delete/movement")>0:
    movement_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.movement(id=movement_id).trans_id
    if delete_row("movement", movement_id, "trans", trans_id):
      redirect(URL('frm_trans/view/trans/'+str(trans_id)))
  
  if request.post_vars["_formname"]=="movement/create":
    clear_post_vars()
    if not request.post_vars.has_key("shared"):
      request.post_vars["shared"]=0
    else:
      request.post_vars["shared"]=1
    if request.post_vars.has_key("target_place_id"):
      target_place_id = request.post_vars["target_place_id"]
      nervatype_movement_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="movement")).select().as_list()[0]["id"]
      del request.post_vars["target_place_id"]
      place_id = request.post_vars["place_id"]
      del request.post_vars["place_id"]
    else:
      target_place_id=None
    if ns.db.groups(id=ns.db.trans(id=request.post_vars["trans_id"]).transtype).groupvalue == "production":
      request.post_vars["qty"] = -float(request.post_vars["qty"])
    try:
      if request.post_vars.has_key("id"):
        if target_place_id:
          links = ns.db((ns.db.link.ref_id_2==request.post_vars["id"])&(ns.db.link.nervatype_1==nervatype_movement_id)
                        &(ns.db.link.deleted==0)&(ns.db.link.nervatype_2==nervatype_movement_id)).select()
          if len(links)>0:
            values = {"product_id":request.post_vars.product_id,"qty":-float(request.post_vars.qty),"notes":request.post_vars.notes}
            ns.db(ns.db.movement.id==links[0].ref_id_1).update(**values)
        ns.db(ns.db.movement.id==request.post_vars["id"]).update(**request.post_vars)      
      else:
        if target_place_id:
          request.post_vars.qty = -float(request.post_vars.qty)
          request.post_vars.id = ns.db.movement.insert(**dict(request.post_vars))
          values = {"trans_id":request.post_vars.trans_id,"shippingdate":request.post_vars.shippingdate,"movetype":request.post_vars.movetype,
                    "product_id":request.post_vars.product_id,
                    "qty":-float(request.post_vars.qty),"notes":request.post_vars.notes}
          target_id = ns.db.movement.insert(**values)
          values = {"nervatype_1":nervatype_movement_id, "ref_id_1":request.post_vars.id, "nervatype_2":nervatype_movement_id, "ref_id_2":target_id}
          ns.db.link.insert(**values)
        else:
          ns.db.movement.insert(**request.post_vars)
      setLogtable("update", "log_trans_update", "trans", request.post_vars["trans_id"])
      if target_place_id:
        if len(ns.db((ns.db.movement.trans_id==request.post_vars["trans_id"])&(ns.db.link.deleted==0)).select())>0:
          links = ns.db((ns.db.link.ref_id_1.belongs(ns.db(ns.db.movement.trans_id==request.post_vars["trans_id"]).select(ns.db.movement.id)))
                     &(ns.db.link.nervatype_1==nervatype_movement_id)&(ns.db.link.deleted==0)&(ns.db.link.nervatype_2==nervatype_movement_id)).select()
          for link in links:
            ns.db((ns.db.movement.id==link.ref_id_1)).update(**{"place_id":place_id})
            ns.db((ns.db.movement.id==link.ref_id_2)).update(**{"place_id":target_place_id})
      redirect(URL('frm_trans/view/trans/'+str(request.post_vars["trans_id"])))
    except Exception, err:
      response.flash = str(err)
  
  if ruri.find("edit/item")>0 or ruri.find("view/item")>0:
    item_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.item(id=item_id).trans_id
    redirect(URL('frm_trans/view/trans/'+str(trans_id)))
        
  if ruri.find("delete/item")>0:
    item_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.item(id=item_id).trans_id
    if delete_row("item", item_id, "trans", trans_id):
      redirect(URL('frm_trans/view/trans/'+str(trans_id)))
  
  if request.post_vars["_formname"]=="item/create":
    clear_post_vars()
    if request.post_vars.has_key("digit"):
      del request.post_vars["digit"]
    if request.post_vars.has_key("rate"):
      del request.post_vars["rate"]
    if not request.post_vars.has_key("deposit"):
      request.post_vars["deposit"]=0
    else:
      request.post_vars["deposit"]=1
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.item.id==request.post_vars["id"]).update(**request.post_vars)      
      else:
        ns.db.item.insert(**request.post_vars)
      setLogtable("update", "log_trans_update", "trans", request.post_vars["trans_id"])
      redirect(URL('frm_trans/view/trans/'+str(request.post_vars["trans_id"])))
    except Exception, err:
      response.flash = str(err)
  
  if ruri.find("edit/payment")>0 or ruri.find("view/payment")>0:
    payment_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.payment(id=payment_id).trans_id
    redirect(URL('frm_trans/view/trans/'+str(trans_id)))
    
  if ruri.find("delete/payment")>0:
    payment_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.payment(id=payment_id).trans_id
    if delete_row("payment", payment_id, "trans", trans_id):
      redirect(URL('frm_trans/view/trans/'+str(trans_id)))
        
  if request.post_vars["_formname"]=="payment/create":
    clear_post_vars()
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.payment.id==request.post_vars["id"]).update(**request.post_vars)      
      else:
        ns.db.payment.insert(**request.post_vars)
      setLogtable("update", "log_trans_update", "trans", request.post_vars["trans_id"])
      redirect(URL('frm_trans/view/trans/'+str(request.post_vars["trans_id"])))
    except Exception, err:
      response.flash = str(err)     
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    redirect(URL('frm_trans/view/trans/'+str(trans_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    trans_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    if delete_row("fieldvalue", fieldvalue_id, "trans", trans_id):
      redirect(URL('frm_trans/view/trans/'+str(trans_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.fieldvalue.id==request.post_vars["id"]).validate_and_update(**request.post_vars)      
      else:
        ns.db.fieldvalue.validate_and_insert(**request.post_vars)
      setLogtable("update", "log_trans_update", "trans", request.post_vars["ref_id"])
      redirect(URL('frm_trans/view/trans/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
  
  if ruri.find("delete/link")>0:
    link_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if delete_row("link",link_id):
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(ruri[:ruri.find("delete/link")-1])
  
  if request.post_vars["_formname"]=="link/create":
    clear_post_vars()
    if request.post_vars.has_key("trans_id"):
      trans_id = request.post_vars["trans_id"]
      del request.post_vars["trans_id"]
    if request.post_vars.has_key("amount"):
      amount = request.post_vars["amount"]
      del request.post_vars["amount"]
    if request.post_vars.has_key("rate"):
      rate = request.post_vars["rate"]
      del request.post_vars["rate"]
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.link.id==request.post_vars["id"]).update(**request.post_vars)
        link_qty = ns.db((ns.db.fieldvalue.ref_id==request.post_vars["id"])&(ns.db.fieldvalue.fieldname=="link_qty")&(ns.db.fieldvalue.deleted==0)).select().as_list()
        if len(link_qty)>0:
          ns.db((ns.db.fieldvalue.ref_id==request.post_vars["id"])&(ns.db.fieldvalue.fieldname=="link_qty")&(ns.db.fieldvalue.deleted==0)).validate_and_update(**{"value":amount})
        else:
          ns.db.fieldvalue.validate_and_insert(**{"fieldname":"link_qty","ref_id":request.post_vars["id"],"value":amount})
        link_rate = ns.db((ns.db.fieldvalue.ref_id==request.post_vars["id"])&(ns.db.fieldvalue.fieldname=="link_rate")&(ns.db.fieldvalue.deleted==0)).select().as_list()
        if len(link_rate)>0:
          ns.db((ns.db.fieldvalue.ref_id==request.post_vars["id"])&(ns.db.fieldvalue.fieldname=="link_rate")&(ns.db.fieldvalue.deleted==0)).validate_and_update(**{"value":rate})
        else:
          ns.db.fieldvalue.validate_and_insert(**{"fieldname":"link_rate","ref_id":request.post_vars["id"],"value":rate})      
      else:
        link_id = ns.db.link.insert(**request.post_vars)
        ns.db.fieldvalue.validate_and_insert(**{"fieldname":"link_qty","ref_id":link_id,"value":amount})
        ns.db.fieldvalue.validate_and_insert(**{"fieldname":"link_rate","ref_id":link_id,"value":rate})  
      setLogtable("update", "log_trans_update", "trans", trans_id)
      redirect(URL('frm_trans/view/trans/'+str(trans_id)))
    except Exception, err:
      response.flash = str(err)
          
  if ruri.find("new/link")>0:
    trans_id = int(request.vars.refnumber)
    trans_nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
    groups_id = int(request.vars.groups_id)
    groups_nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
    glink = ns.db((ns.db.link.ref_id_1==trans_id)&(ns.db.link.nervatype_1==trans_nervatype)&(ns.db.link.deleted==0)
              &(ns.db.link.nervatype_2==groups_nervatype)&(ns.db.link.ref_id_2==groups_id)).select().as_list()
    if len(glink)==0:
      values = {"nervatype_1":trans_nervatype, "ref_id_1":trans_id, "nervatype_2":groups_nervatype, "ref_id_2":groups_id}
      ns.db.link.insert(**values)
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
  
  response.lo_menu = []
  
  nervatype_trans = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
  nervatype_groups = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue==transtype)).select().as_list()[0]["id"]
  direction_id = ns.db((ns.db.groups.groupname=="direction")&(ns.db.groups.groupvalue==direction)).select().as_list()[0]["id"]
  transtype_audit_filter = get_audit_filter("trans", transtype)
  setting_audit_filter = get_audit_filter("setting", None)[0]
  
  if transtype_audit_filter[0]=="disabled":
    return show_disabled()
  
  if ruri.find("close/trans")>0:
    setLogtable("closed", "log_trans_closed", "trans", trans_id)
    ns.db(ns.db.trans.id==trans_id).update(**{"closed":1})
    redirect(URL('frm_trans/view/trans/'+str(trans_id)))
    
  if ruri.find("delete/trans")>0:
    setLogtable("deleted", "log_trans_deleted", "trans", trans_id)
    delete_ini = getSetting("set_trans_deleted")
    if delete_ini != "true":
      values = {"deleted":1}
      ns.db(ns.db.trans.id==trans_id).update(**values)
    else:
      dfield = deleteFieldValues("trans", trans_id)
      if dfield!=True:
        session.flash = dfield
        if request.wsgi.environ.has_key("HTTP_REFERER"):
          redirect(request.wsgi.environ["HTTP_REFERER"])
        else:
          redirect(URL('index'))
      ns.db(ns.db.trans.id==trans_id).delete()
      ns.db.commit()
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
  response.icon_corrected = IMG(_src=URL(dir_images,'icon16_corrected.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_deffield = IMG(_src=URL(dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_money = IMG(_src=URL(dir_images,'icon16_money.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_invoice = IMG(_src=URL(dir_images,'icon16_invoice.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_lorry = IMG(_src=URL(dir_images,'icon16_lorry.png'),_style="vertical-align: middle;",_height="16px",_width="16px")
  response.icon_wrench_page = IMG(_src=URL(dir_images,'icon16_wrench_page.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  if transtype in("offer"):
    response.view=dir_view+'/trans_item.html'
    response.tcolor='#B8860B'
    response.titleicon = URL(dir_images,'icon16_offer.png')
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
    response.view=dir_view+'/trans_item.html'
    response.tcolor='#228B22'
    response.titleicon = URL(dir_images,'icon16_order.png')
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
    response.view=dir_view+'/trans_payment.html'
    response.titleicon = URL(dir_images,'icon16_cashregister.png')
    response.subtitle=response.subtitle+T('CASH')
    ns.db.trans.place_id.label = T("Cash desk")
    ns.db.trans.transdate.label = T("Payment Date")
    ns.db.trans.direction.requires = IS_IN_DB(ns.db(((ns.db.groups.groupname.like('direction'))&(ns.db.groups.groupvalue=="in")) | 
                                     ((ns.db.groups.groupname.like('direction'))&(ns.db.groups.groupvalue=="out"))), ns.db.groups.id, '%(groupvalue)s')
      
  if transtype in("bank"):
    response.view=dir_view+'/trans_payment.html'
    response.titleicon = URL(dir_images,'icon16_money.png')
    response.subtitle=response.subtitle+T('BANK STATEMENT')
    ns.db.trans.place_id.label = T("Account No.")
    ns.db.trans.transdate.label = T("Acc.Date")
  
  if transtype in("production"):
    response.view=dir_view+'/trans_movement.html'
    response.titleicon = URL(dir_images,'icon16_production.png')
    response.subtitle=response.subtitle+T('PRODUCTION')
    ns.db.trans.place_id.label = T("Warehouse")
    ns.db.trans.transdate.label = T("Start Date")
    ns.db.trans.duedate.label = T('End Date')
    movetype_inventory = ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="inventory")).select().as_list()[0]["id"]
    
  if transtype in("formula"):
    response.view=dir_view+'/trans_movement.html'
    response.titleicon = URL(dir_images,'icon16_formula.png')
    response.subtitle=response.subtitle+T('FORMULA')
    if len(ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="head")).select())>0:
      movetype_head = ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="head")).select().as_list()[0]["id"]
    else:
      movetype_head = ns.db.groups.insert(**{"groupname":"movetype","groupvalue":"head"})
        
  if transtype in("inventory"):
    response.view=dir_view+'/trans_movement.html'
    response.titleicon = URL(dir_images,'icon16_lorry_error.png')
    response.subtitle=response.subtitle+T('CORRECTION')
    ns.db.trans.place_id.label = T("Warehouse")
    ns.db.trans.transdate.label = T("Inv.Date")
  
  if transtype in("delivery") and direction=="transfer":
    response.view=dir_view+'/trans_movement.html'
    response.titleicon = URL(dir_images,'icon16_lorry_go.png')
    response.subtitle=response.subtitle+T('TRANSFER')
    ns.db.trans.place_id.label = T("Warehouse")
    ns.db.trans.transdate.label = T("Trans.Date")
  
  if transtype in("delivery") and direction!="transfer":
    response.view=dir_view+'/trans_movement.html'
    response.titleicon = URL(dir_images,'icon16_lorry_go.png')
    response.subtitle=response.subtitle+T('SHIPPING')+" "+T(direction.upper())
    ns.db.trans.place_id.label = T("Warehouse")
    ns.db.trans.transdate.label = T("Shipping")
    response.direction = direction
      
  if transtype in("worksheet"):
    response.view=dir_view+'/trans_item.html'
    response.tcolor='#8470FF'
    response.titleicon = URL(dir_images,'icon16_worksheet.png')
    response.subtitle=response.subtitle+T('WORKSHEET')
    ns.db.trans.transdate.label = T('Start Date')
    ns.db.trans.duedate.label = T('End Date')
    ns.db.trans.acrate.label = T('Paym.days')
    ns.db.trans.paid.label = T('Released')
    ns.db.item.deposit.readable = ns.db.item.deposit.writable = False
    ns.db.trans.transnumber.label = T('Worksheet No.')
    
    trans_wsdistance = get_formvalue(fieldname="trans_wsdistance",table="fieldvalue",ref_id=trans_id,default="0",isempty=False)
    trans_wsrepair = get_formvalue(fieldname="trans_wsrepair",table="fieldvalue",ref_id=trans_id,default="0",isempty=False)
    trans_wstotal = get_formvalue(fieldname="trans_wstotal",table="fieldvalue",ref_id=trans_id,default="0",isempty=False)
    trans_wsnote = get_formvalue(fieldname="trans_wsnote",table="fieldvalue",ref_id=trans_id,default="",isempty=True)
    
  if transtype in("rent"):
    response.view=dir_view+'/trans_item.html'
    response.tcolor='#A52A2A'
    response.titleicon = URL(dir_images,'icon16_rent.png')
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
    
    trans_reholiday = get_formvalue(fieldname="trans_reholiday",table="fieldvalue",ref_id=trans_id,default="0",isempty=False)
    trans_rebadtool = get_formvalue(fieldname="trans_rebadtool",table="fieldvalue",ref_id=trans_id,default="0",isempty=False)
    trans_reother = get_formvalue(fieldname="trans_reother",table="fieldvalue",ref_id=trans_id,default="0",isempty=False)
    trans_rentnote = get_formvalue(fieldname="trans_rentnote",table="fieldvalue",ref_id=trans_id,default="",isempty=True)
              
  if transtype in("invoice"):
    response.view=dir_view+'/trans_item.html'
    response.tcolor='#2F4F4F'
    response.titleicon = URL(dir_images,'icon16_invoice.png')
    if direction=="out":
      response.subtitle=response.subtitle+T('CUSTOMER INVOICE')
    else:
      response.subtitle=response.subtitle+T('SUPPLIER INVOICE')
    ns.db.trans.transnumber.label = T('Invoice No.')
    ns.db.trans.transdate.label = T('Invoice Date')
  
  if transtype in("receipt"):
    response.view=dir_view+'/trans_item.html'
    response.tcolor='#2F4F4F'
    response.titleicon = URL(dir_images,'icon16_invoice.png')
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
    request.post_vars["acrate"] = get_formvalue(fieldname="acrate",table="trans",ref_id=trans_id,default="0",isempty=False)
    ns.db.trans.curr.requires = IS_IN_DB(ns.db(ns.db.currency), ns.db.currency.curr, '%(curr)s')
    ns.db.trans.paidtype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('paidtype')), ns.db.groups.id, '%(groupvalue)s')
    
  if transtype in("waybill"):
    response.subtitle=response.subtitle+T('TOOL MOVEMENT')
    ns.db.trans.direction.requires = IS_IN_DB(ns.db(((ns.db.groups.groupname.like('direction'))&(ns.db.groups.groupvalue=="in")) | 
                                                    ((ns.db.groups.groupname.like('direction'))&(ns.db.groups.groupvalue=="out"))), ns.db.groups.id, '%(groupvalue)s')
  
  if transtype_audit_filter[1]==0:
    ns.db.trans.transtate.writable = False
  
  if trans_id>0:
    form = SQLFORM(ns.db.trans, record = trans_id, submit_button=T("Save"))
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
    
    response.cmd_report = get_report_button(title=response.subtitle, url='frm_report_trans/'+transtype+'/'+direction+'/'+str(trans_id))
    response.cmd_fnote = get_command_button(caption=T("Report notes"),title=T("Report notes"),color="483D8B",
                              cmd="if(confirm('"+T('Any unsaved changes will be lost. Do you want to continue?')+
                              "')){window.location ='"+URL("frm_trans_fnote/"+str(trans_id))+"';};return false;")
    if transtype_audit_filter[0]=="all":
      response.cmd_delete = get_command_button(caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this document?')+
                              "')){window.location ='"+URL("frm_trans/delete/trans/"+str(trans_id))+"';};return false;")
      response.cmd_close = get_command_button(caption=T("Closing data"),title=T("Closing data"),color="8B4513",
                              cmd="if(confirm('"+T('Are you sure you want to close this document?')+
                              "')){window.location ='"+URL("frm_trans/close/trans/"+str(trans_id))+"';};return false;")
      response.cmd_copy = get_command_button(caption=T("Copy from"),title=T("Copy a document from existing"),
                              cmd="if(confirm('"+T('Are you sure you want to copy this document?')+
                              "')){copy_trans('"+URL("copy_trans")+"?trans_id="+str(trans_id)
                              +"','"+URL("frm_trans/view/trans")+"/')};return false;")
      
      dlg_create_trans = DIALOG(LOAD(f="dlg_create_trans/"+str(trans_id), ajax=True), title=T("Create a new document type"),
                        icon=URL(dir_images,'icon16_relation.png'), renderstyle=True, height=50, width=35)
      response.cmd_create = INPUT(_type="button", _value=T("Create from"), _title=T("Create a new document type from existing"), 
                            _style="height: 25px !important;padding-top: 2px !important;color: #B8860B;width: 100%;", 
                            _onclick='%s;return false' % dlg_create_trans.show())
      
      response.cmd_cancellation = get_command_button(caption=T("Cancellation"),title=T("Create a cancellation invoice"),color="F08080",
                              cmd="if(confirm('"+T('Are you sure you want to copy this document?')+
                              "')){copy_trans('"+URL("cancel_trans")+"?trans_id="+str(trans_id)
                              +"','"+URL("frm_trans/view/trans/")+"/')};return false;")
      response.cmd_corrective = get_command_button(caption=T("Corrective"),title=T("Create a corrective invoice"),color="F08080",
                              cmd="if(confirm('"+T('Are you sure you want to copy this document?')+
                              "')){copy_trans('"+URL("corr_trans")+"?trans_id="+str(trans_id)
                              +"','"+URL("frm_trans/view/trans")+"/')};return false;")
      response.cmd_more = get_more_button()             
    else:
      response.cmd_delete = ""
      response.cmd_close = ""
      response.cmd_copy = ""
      response.cmd_create = ""
      response.cmd_cancellation = ""
      response.cmd_corrective = ""
      response.cmd_more = ""
  else:
    form = SQLFORM(ns.db.trans, submit_button=T("Save"))
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
      form.vars.transnumber = dbfu.nextNumber(ns, {"id":transtype, "step":False})
    else:
      form.vars.transnumber = dbfu.nextNumber(ns, {"id":transtype+"_"+direction, "step":False})
    form.vars.transtype = transtype_id
    form.vars.direction = direction_id
    form.vars.crdate = datetime.datetime.now().date()
    form.vars.transdate = datetime.datetime.now().date()
    form.vars.duedate = datetime.datetime.strptime(str(datetime.date.today())+" 00:00:00", str('%Y-%m-%d %H:%M:%S'))
    form.vars.transtate = ns.db((ns.db.groups.groupname=="transtate")&(ns.db.groups.groupvalue=="ok")).select().as_list()[0]["id"]
    form.vars.cruser_id = session.auth.user.id
    if transtype in("offer","order","worksheet","rent","invoice","receipt"):
      form.vars.curr = getSetting("default_currency")
      paidtype=getSetting("default_paidtype")
      if paidtype!="":
        form.vars.paidtype = ns.db((ns.db.groups.groupname=="paidtype")&(ns.db.groups.groupvalue==paidtype)).select().as_list()[0]["id"]
    if transtype in("invoice"):
      if direction=="out":
        deadline=getSetting("default_deadline")
        if deadline!="":
          form.vars.duedate += datetime.timedelta(int(deadline))
  
  if request.vars.has_key("back_url"):
    response.cmd_back = get_back_button(ruri[ruri.find("back_url=")+9:])
  else:
    if transtype in("offer","order","worksheet","rent","invoice","receipt"):
      response.cmd_back = get_back_button(URL('find_transitem_trans'))
    elif transtype=="waybill":
      response.cmd_back = get_back_button(URL('find_movement_tool'))
    elif transtype in("cash", "bank"):
      response.cmd_back = get_back_button(URL('find_payment_payment'))
    elif transtype in("inventory", "delivery","production"):
      response.cmd_back = get_back_button(URL('find_movement_product'))
    elif transtype in("formula"):
      response.cmd_back = get_back_button(URL('find_movement_formula'))
    else:
      response.cmd_back = get_home_button()

  response.cmd_help = get_help_button(transtype)
  
  next_url = get_next_lnk(transtype,trans_id,direction)
  prev_url = get_prev_lnk(transtype,trans_id,direction)
  
  response.cmd_next = A(IMG(_style="vertical-align: top;", _height="24px", _width="24px", _src=URL(dir_images,'icon24_next.png')),
                        _style="height: 100%;width: 20px;padding-left: 8px;padding-top: 8px;", 
                        _class="w2p_trap buttontext button", _href=next_url, _title=T('NEXT'))
  response.cmd_prev = A(IMG(_style="vertical-align: top;", _height="24px", _width="24px", _src=URL(dir_images,'icon24_previous.png')),
                        _style="height: 100%;width: 20px;padding-left: 8px;padding-top: 8px;", 
                        _class="w2p_trap buttontext button", _href=prev_url, _title=T('PREVIOUS'))
  
  customer_audit_filter = get_audit_filter("customer", None)[0]
  employee_audit_filter = get_audit_filter("employee", None)[0]
  product_audit_filter = get_audit_filter("product", None)[0]
    
  if form.validate(keepvalues=True):
    check_ok=True
    if transtype in("offer","order","worksheet","rent","invoice"):
      if request.post_vars.customer_id=="":
        response.customer_control = get_customer_selector(T('Missing customer!'), error_label=True)
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
          response.place_control = get_place_selector(T('Missing cash desk!'), error_label=True,width="100%", placetype="find_place_dlg_cash",title=T("Select Cash desk"))
          response.flash = T('Missing cash desk!')
        elif transtype=="bank":
          response.place_control = get_place_selector(T('Missing bank account!'), error_label=True,width="100%", placetype="find_place_dlg_bank",title=T("Select account"))
          response.flash = T('Missing bank account!')
        elif transtype=="production":
          response.production_place_selector = get_base_selector(dlg=get_find_place_dlg("find_place_dlg_warehouse",T("Select warehouse"),""),label_id="production_place_label",
            label_url="'"+URL("frm_place/view/place")+"/'+document.getElementById('production_place_id').value",
            label_txt=T('Missing warehouse!'),value_id="production_place_id",width="100%",error_label=True)
          response.flash = T('Missing warehouse!')
        else:
          response.place_control = get_place_selector(T('Missing warehouse!'), error_label=True,width="100%", placetype="find_place_dlg_warehouse",title=T("Select warehouse"))
          response.flash = T('Missing warehouse!')
        check_ok=False
      else:
        form.vars.place_id=request.post_vars.place_id
        
    if transtype=="waybill":
      if request.post_vars.refnumber_type=="trans":
        if request.post_vars.trans_id=="":
          response.trans_transnumber=DIV(get_find_transitem_dlg(),
                                   SPAN(T('Missing reference number!'), _id="reftrans_transnumber"), 
                                   _class="label_error", _id="fld_trans_transnumber", _style="display:block;padding: 3px;height: 22px;")
          response.flash = T('Missing reference number!')
          check_ok=False
        else:
          form.vars["ref_transnumber"]=ns.db.trans(id=int(request.post_vars.trans_id)).transnumber
          form.vars["customer_id"]=None
          form.vars["employee_id"]=None
      elif request.post_vars.refnumber_type=="customer":
        if request.post_vars.customer_id=="":
          if customer_audit_filter!="disabled":
            response.customer_custname=DIV(get_find_customer_dlg(),
                                   SPAN(T('Missing customer!'), _id="customer_custname"), 
                                   _class="label_error", _id="fld_customer_custname", _style="display:block;padding: 3px;height: 22px;")
          else:
            response.customer_custname=DIV(
                                   SPAN(T('Missing customer!'), _id="customer_custname"), 
                                   _class="label_error", _id="fld_customer_custname", _style="display:block;padding: 3px;height: 22px;")
          response.flash = T('Missing customer!')
          check_ok=False
        else:
          form.vars["customer_id"]=request.post_vars.customer_id
          form.vars["ref_transnumber"]=None
          form.vars["employee_id"]=None
      elif request.post_vars.refnumber_type=="employee":
        if request.post_vars.employee_id=="":
          if employee_audit_filter!="disabled":
            response.employee_empnumber=DIV(get_find_employee_dlg(),
                                   SPAN(T('Missing employee!'), _id="employee_empnumber"), 
                                   _class="label_error", _id="fld_employee_empnumber", _style="display:block;padding: 3px;height: 22px;")
          else:
            response.employee_empnumber=DIV(
                                   SPAN(T('Missing employee!'), _id="employee_empnumber"), 
                                   _class="label_error", _id="fld_employee_empnumber", _style="display:block;padding: 3px;height: 22px;")
          response.flash = T('Missing employee!')
          check_ok=False
        else:
          form.vars["employee_id"]=request.post_vars.employee_id
          form.vars["ref_transnumber"]=None
          form.vars["customer_id"]=None
          
    if transtype in("production","formula"):
      production_qty = get_formvalue(fieldname="production_qty",default="0",isempty=False)
      if request.post_vars.product_id=="":
        if product_audit_filter!="disabled":
          response.production_product_selector = get_base_selector(dlg=get_find_product_dlg("item"),label_id="production_product_label",
                        label_url="'"+URL("frm_product/view/product")+"/'+document.getElementById('production_product_id').value",
                        label_txt=T('Missing product!'),value_id="production_product_id",width="100%",error_label=True)
        else:
          response.production_product_selector=DIV(
                                   SPAN(T('Missing product!'), _id="production_product_label"), 
                                   _class="label_error", _id="production_product_id", _style="display:block;padding: 3px;height: 22px;")
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
        nextnumber = dbfu.nextNumber(ns, {"id":nextnumber_id, "step":False})
        if form.vars.transnumber == nextnumber:
          form.vars.transnumber = dbfu.nextNumber(ns, {"id":nextnumber_id, "step":True})
        plst = ns.db((ns.db.pattern.deleted==0)&(ns.db.pattern.defpattern==1)&(ns.db.pattern.transtype==form.vars.transtype)).select().as_list()
        if len(plst)>0:
          form.vars.fnote = plst[0]["notes"]
        form.vars.id = ns.db.trans.insert(**dict(form.vars))
        direction = ns.db.groups(id=ns.db.trans(id=form.vars.id).direction).groupvalue
        
        ns.db.fieldvalue.validate_and_insert(**{"fieldname":"trans_transcast","ref_id":form.vars.id,"value":transcast})
        if transtype in("offer","order","worksheet","rent","invoice","cash","bank","inventory","delivery","receipt") or (transtype=="waybill" and request.post_vars.refnumber_type=="trans"):
          if request.post_vars.trans_id!="":
            values = {"nervatype_1":nervatype_trans, "ref_id_1":form.vars.id, "nervatype_2":nervatype_trans, "ref_id_2":request.post_vars.trans_id}
            ns.db.link.insert(**values)
        
        if transtype in("invoice"):
          update_custinvoice_prop(form.vars.id)
        
        if transtype in("worksheet"):  
          #insert all additional data (from header)
          ns.db.fieldvalue.validate_and_insert(**{"fieldname":"trans_wsdistance","ref_id":form.vars.id,"value":trans_wsdistance})
          ns.db.fieldvalue.validate_and_insert(**{"fieldname":"trans_wsrepair","ref_id":form.vars.id,"value":trans_wsrepair})
          ns.db.fieldvalue.validate_and_insert(**{"fieldname":"trans_wstotal","ref_id":form.vars.id,"value":trans_wstotal})
          ns.db.fieldvalue.validate_and_insert(**{"fieldname":"trans_wsnote","ref_id":form.vars.id,"value":trans_wsnote})
        
        if transtype in("rent"):  
          #insert all additional data (from header)
          ns.db.fieldvalue.validate_and_insert(**{"fieldname":"trans_reholiday","ref_id":form.vars.id,"value":trans_reholiday})
          ns.db.fieldvalue.validate_and_insert(**{"fieldname":"trans_rebadtool","ref_id":form.vars.id,"value":trans_rebadtool})
          ns.db.fieldvalue.validate_and_insert(**{"fieldname":"trans_reother","ref_id":form.vars.id,"value":trans_reother})
          ns.db.fieldvalue.validate_and_insert(**{"fieldname":"trans_rentnote","ref_id":form.vars.id,"value":trans_rentnote})
        
        if transtype in("production"):
          ns.db.movement.insert(**{"trans_id":form.vars.id,"shippingdate":form.vars.duedate,
            "movetype":movetype_inventory, "product_id":product_id, "qty":production_qty, 
            "place_id":form.vars.place_id, "notes":request.post_vars.batch, "shared":1})
        
        if transtype in("formula"):
          ns.db.movement.insert(**{"trans_id":form.vars.id,"shippingdate":str(form.vars.transdate)+" 00:00:00",
            "movetype":movetype_head, "product_id":product_id, "qty":production_qty})
          
        if transtype in("cash","bank"):
          ns.db.payment.insert(**{"trans_id":form.vars.id,"paiddate":form.vars.transdate,"amount":0})
            
        #add auto deffields
        addnew = ns.db((ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_trans)&
                       (ns.db.deffield.addnew==1)).select().as_list()
        for nfield in addnew:
          ns.db.fieldvalue.validate_and_insert(**{"fieldname":nfield["fieldname"],"ref_id":form.vars.id,"value":get_default_value(nfield["fieldtype"])})
        setLogtable("update", "log_trans_update", "trans", form.vars.id)
        redirect(URL('frm_trans/view/trans/'+str(form.vars.id)))      
      else:
        if form.vars.has_key("fnote"):
          del form.vars["fnote"]
        ns.db(ns.db.trans.id==trans_id).update(**form.vars)
        setLogtable("update", "log_trans_update", "trans", trans_id)
        direction = ns.db.groups(id=ns.db.trans(id=trans_id).direction).groupvalue
        
        link = ns.db((ns.db.link.ref_id_1==trans_id)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0)
            &(ns.db.link.nervatype_2==nervatype_trans)).select().as_list()
        if request.post_vars.trans_id=="" and len(link)>0:
          delete_row("link",link[0]["id"])
        else:
          if (transtype=="waybill" and request.post_vars.refnumber_type!="trans"):
            if len(link)>0:
              delete_row("link",link[0]["id"])
          else:
            if request.post_vars.trans_id and request.post_vars.trans_id!="":
              if len(link)>0:
                ns.db(ns.db.link.id==link[0]["id"]).update(**{"ref_id_2":request.post_vars.trans_id})
              else:
                values = {"nervatype_1":nervatype_trans, "ref_id_1":trans_id, "nervatype_2":nervatype_trans, "ref_id_2":request.post_vars.trans_id}
                ns.db.link.insert(**values)
        
        if transtype in("invoice"):
          update_custinvoice_prop(trans_id)
        
        if transtype in("worksheet"): 
          #update all additional data (from header)
          ns.db((ns.db.fieldvalue.fieldname=="trans_wsdistance")&(ns.db.fieldvalue.ref_id==trans_id)).validate_and_update(**{"value":trans_wsdistance})
          ns.db((ns.db.fieldvalue.fieldname=="trans_wsrepair")&(ns.db.fieldvalue.ref_id==trans_id)).validate_and_update(**{"value":trans_wsrepair})
          ns.db((ns.db.fieldvalue.fieldname=="trans_wstotal")&(ns.db.fieldvalue.ref_id==trans_id)).validate_and_update(**{"value":trans_wstotal})
          ns.db((ns.db.fieldvalue.fieldname=="trans_wsnote")&(ns.db.fieldvalue.ref_id==trans_id)).validate_and_update(**{"value":trans_wsnote})
          
        if transtype in("rent"): 
          #update all additional data (from header)
          ns.db((ns.db.fieldvalue.fieldname=="trans_reholiday")&(ns.db.fieldvalue.ref_id==trans_id)).validate_and_update(**{"value":trans_reholiday})
          ns.db((ns.db.fieldvalue.fieldname=="trans_rebadtool")&(ns.db.fieldvalue.ref_id==trans_id)).validate_and_update(**{"value":trans_rebadtool})
          ns.db((ns.db.fieldvalue.fieldname=="trans_reother")&(ns.db.fieldvalue.ref_id==trans_id)).validate_and_update(**{"value":trans_reother})
          ns.db((ns.db.fieldvalue.fieldname=="trans_rentnote")&(ns.db.fieldvalue.ref_id==trans_id)).validate_and_update(**{"value":trans_rentnote})
        
        if transtype in("production"):
          movement = ns.db((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.shared==1)).select()
          if len(movement)>1:
            ns.db((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.shared==1)).update(**{"deleted":1})
          if len(movement)==1:
            ns.db((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.shared==1)).update(**{
              "shippingdate":form.vars.duedate, "product_id":product_id, "qty":production_qty, 
              "place_id":form.vars.place_id, "notes":request.post_vars.batch})
          else:
            ns.db.movement.insert(**{"trans_id":trans_id,"shippingdate":form.vars.duedate,
              "movetype":movetype_inventory, "product_id":product_id, "qty":production_qty, 
              "place_id":form.vars.place_id, "notes":request.post_vars.batch, "shared":1})
        
        if transtype in("formula"):
          movement = ns.db((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.movetype==movetype_head)).select()
          if len(movement)>1:
            ns.db((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.movetype==movetype_head)).update(**{"deleted":1})
          if len(movement)==1:
            ns.db((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.movetype==movetype_head)).update(**{
              "shippingdate":str(form.vars.transdate)+" 00:00:00", "product_id":product_id, "qty":production_qty})
          else:
            ns.db.movement.insert(**{"trans_id":trans_id,"shippingdate":str(form.vars.transdate)+" 00:00:00",
            "movetype":movetype_head, "product_id":product_id, "qty":production_qty})
                  
        if transtype in("cash"):
          payment = ns.db((ns.db.payment.trans_id==trans_id)&(ns.db.payment.deleted==0)).select()
          if len(payment)>1:
            ns.db((ns.db.payment.trans_id==trans_id)&(ns.db.payment.deleted==0)).update(**{"deleted":1})
          if len(payment)==1:
            if direction=="out":
              ns.db((ns.db.payment.trans_id==trans_id)).update(**{"paiddate":request.post_vars.transdate,"amount":-float(request.post_vars.paidamount)})
            else:
              ns.db((ns.db.payment.trans_id==trans_id)).update(**{"paiddate":request.post_vars.transdate,"amount":request.post_vars.paidamount})
          else:
            ns.db.payment.insert(**{"trans_id":trans_id,"paiddate":form.vars.transdate,"amount":0})
                
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
                               _style="text-align: right;padding: 3px;height: 22px;font-size: 12px;font-weight: bold;color: #551A8B;")
    else:
      response.netamount = DIV(ns.splitThousands(float(item_sum[0]["netamount"])," ","."), _class="label_disabled",  
                               _style="text-align: right;padding: 3px;height: 22px;font-size: 12px;font-weight: bold;color: #551A8B;")
    if item_sum[0]["vatamount"]==None:
      response.vatamount = DIV("0", _class="label_disabled", 
                               _style="text-align: right;padding: 3px;height: 22px;font-size: 12px;font-weight: bold;color: #551A8B;")
    else:
      response.vatamount = DIV(ns.splitThousands(float(item_sum[0]["vatamount"])," ","."), _class="label_disabled", 
                               _style="text-align: right;padding: 3px;height: 22px;font-size: 12px;font-weight: bold;color: #551A8B;")
    if item_sum[0]["amount"]==None:
      response.amount = DIV("0", _class="label_disabled", 
                               _style="text-align: right;padding: 3px;height: 22px;font-size: 12px;font-weight: bold;color: #551A8B;")
    else:
      response.amount = DIV(ns.splitThousands(float(item_sum[0]["amount"])," ","."), _class="label_disabled", 
                               _style="text-align: right;padding: 3px;height: 22px;font-size: 12px;font-weight: bold;color: #551A8B;")
      
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
    response.trans_transnumber=DIV(get_find_transitem_dlg(),
                                   A(SPAN(_class="icon trash"), _id="cmd_remove_transitem_link", 
                                     _style="width: 16px;padding: 0px;padding-left: 6px;padding-right: 3px;", 
                                     _class="w2p_trap buttontext button", _href="#null", _title=T("Delete link"), 
                                     _onclick="document.getElementById('trans_id').value='';document.getElementById('reftrans_transnumber').innerHTML='';"),
                                   A(lnk_transnumber, _id="reftrans_transnumber", _href="#", 
                                     _onclick="javascript:window.open('"+URL("frm_trans/view/trans/")+"'+document.getElementById('trans_id').value, '_blank');"), 
                                   _class="label_disabled", _id="fld_trans_transnumber", _style="display:block;padding: 3px;height: 22px;")
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
      response.customer_control = get_customer_selector(customer_name)
    
    employee_id=""
    employee_empnumber=""
    if trans_id>-1:  
      if ns.db.trans(id=trans_id).employee_id!=None:
        employee_id = ns.db.trans(id=trans_id).employee_id
        employee_empnumber = ns.db.employee(id=ns.db.trans(id=trans_id).employee_id).empnumber
    response.employee_id = INPUT(_name="employee_id", _type="hidden", _value=employee_id, _id="employee_id")
    response.employee_control = get_employee_selector(employee_empnumber, width="96%")
    
    project_id=""
    project_pronumber=""
    if trans_id>-1:  
      if ns.db.trans(id=trans_id).project_id!=None:
        project_id = ns.db.trans(id=trans_id).project_id
        project_pronumber = ns.db.project(id=ns.db.trans(id=trans_id).project_id).pronumber
    response.project_id = INPUT(_name="project_id", _type="hidden", _value=project_id, _id="project_id")
    response.project_control = get_project_selector(project_pronumber, width="96%")
    
    if setting_audit_filter in ("disabled"):
      response.cmd_curr = ""
      response.cmd_paidtype = ""
      response.cmd_department = ""
    else:
      response.cmd_curr = get_goprop_button(title=T("Edit currencies"),url=URL("frm_currency?back=1"))
      response.cmd_paidtype = get_goprop_button(title=T("Edit payment methods"),url=URL("frm_groups_paidtype?back=1"))
      response.cmd_department = get_goprop_button(title=T("Edit departments"),url=URL("frm_groups_department?back=1"))
  
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
    response.place_curr = DIV(place_curr, _id="place_curr", _class="label_disabled", _style="width: 35px;padding: 3px;height: 22px;text-align: center;")
    
    response.trans_id = INPUT(_name="trans_id", _type="hidden", _value=lnk_transnumber_id, _id="trans_id")
    response.trans_transnumber=DIV(get_find_transitem_dlg(),
                                   A(SPAN(_class="icon trash"), _id="cmd_remove_transitem_link", 
                                     _style="width: 16px;padding: 0px;padding-left: 6px;padding-right: 3px;", 
                                     _class="w2p_trap buttontext button", _href="#null", _title=T("Delete link"), 
                                     _onclick="document.getElementById('trans_id').value='';document.getElementById('reftrans_transnumber').innerHTML='';"),
                                   A(lnk_transnumber, _id="reftrans_transnumber", _href="#", 
                                     _onclick="javascript:window.open('"+URL("frm_trans/view/trans/")+"'+document.getElementById('trans_id').value, '_blank');"), 
                                   _class="label_disabled", _id="fld_trans_transnumber", _style="display:block;padding: 3px;height: 22px;width: 100%;")
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
      response.cmd_place = get_goprop_button(title=T("Edit places"),url=URL("find_place?back=1"))
  
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
    response.trans_production_batch_label = LABEL(T('Batch No.'))
    response.trans_production_batch_data = INPUT(_name="batch", _type="text", _value=trans_probatch, _id="trans_production_batch", 
                                               _class="string", _style="width: 100%;")
    response.trans_production_qty_label = LABEL(T('Qty'))
    response.trans_production_qty_data = INPUT(_name="production_qty", _type="text", _value=trans_proqty, _id="trans_production_qty", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.production_product_id = INPUT(_name="product_id", _type="hidden", _value=product_id, _id="production_product_id")
    if response.production_product_selector==None:
      if product_audit_filter!="disabled":
        response.production_product_selector = get_base_selector(dlg=get_find_product_dlg("item"),label_id="production_product_label",
                        label_url="'"+URL("frm_product/view/product")+"/'+document.getElementById('production_product_id').value",
                        label_txt=product_description,value_id="production_product_id",width="100%",error_label=False)
      else:
        response.production_product_selector = DIV(SPAN(product_description, _id="production_product_label"), _id="production_product_id", _class="label_disabled", 
              _style="display:block;padding: 3px;height: 26px;padding-bottom: 0px;padding-top: 2px;")
      
  if transtype=="formula":
    response.transdate = INPUT(_name="transdate", _type="hidden", _value=form.vars.crdate, _id="transdate")
    
  if transtype=="production":
    response.production_id = INPUT(_name="production_id", _type="hidden", _value=trans_id, _id="production_production_id")
    response.production_place_id = INPUT(_name="place_id", _type="hidden", _value=place_id, _id="production_place_id")
    if response.production_place_selector==None:
      response.production_place_selector = get_base_selector(dlg=get_find_place_dlg("find_place_dlg_warehouse",T("Select warehouse"),""),label_id="production_place_label",
                          label_url="'"+URL("frm_place/view/place")+"/'+document.getElementById('production_place_id').value",
                          label_txt=place_planumber,value_id="production_place_id",width="100%",error_label=False)  
    
    transtype_id_formula = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="formula")).select().as_list()[0]["id"]
    movetype_head = ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="head")).select().as_list()[0]["id"]
    pro_formula = ns.db((ns.db.trans.transtype==transtype_id_formula)&(ns.db.trans.deleted==0)
                        &(ns.db.trans.id==ns.db.movement.trans_id)&(ns.db.movement.deleted==0)
                        &(ns.db.movement.movetype==movetype_head)&(ns.db.movement.product_id==product_id)).select(ns.db.trans.id,ns.db.trans.transnumber)
    response.cmb_formula = SELECT(*[OPTION(field["transnumber"],_value=field["id"]) for field in pro_formula], 
                                  _id="cmb_formula", _title=T("Select product formula"), _style="height: 30px;width: 100%;")
    response.cmb_formula.insert(0, OPTION("", _value=""))
    if get_audit_filter("trans", "formula")[0]!="disabled":
      response.load_formula = A(SPAN(_class="icon loop"), _id="cmd_load_formula", 
                                     _style="padding: 0px;padding-left: 6px;padding-right: 3px;", 
                                     _class="w2p_trap buttontext button", _href="#null", _title=T("Load selected formula..."), 
                                     _onclick="load_formula();")
    else:
      response.load_formula =""  
    
  if transtype=="inventory":
    response.direction_id = INPUT(_name="direction", _type="hidden", _value=direction_id, _id="direction")
    response.crdate = ""
    response.transdate = ""
    response.target_place_id = ""
    if response.place_control==None:
      response.place_control = get_place_selector(place_planumber, width="100%",placetype="find_place_dlg_warehouse",title=T("Select warehouse"))
  
  if transtype=="delivery" and direction!="transfer":
    form.custom.widget.transnumber["_disabled"]="disabled"
    response.ref_transnumber = INPUT(_name="transnumber", _type="hidden", _value=ns.db.trans(id=trans_id).transnumber, _id="transnumber")
    response.trans_id =""
    form.custom.widget.crdate["_disabled"]="disabled"
    response.crdate = INPUT(_name="crdate", _type="hidden", _value=ns.db.trans(id=trans_id).crdate, _id="crdate")
    form.custom.widget.transdate["_disabled"]="disabled"
    response.transdate = INPUT(_name="transdate", _type="hidden", _value=ns.db.trans(id=trans_id).transdate, _id="transdate")
    
    response.direction_id = INPUT(_name="direction", _type="hidden", _value=direction_id, _id="direction")
    nervatype_item_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="item")).select().as_list()[0]["id"]
    nervatype_movement_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="movement")).select().as_list()[0]["id"]
    ref_trans = ((ns.db.movement.deleted==0)&(ns.db.movement.trans_id==trans_id)
                 &(ns.db.movement.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_movement_id)&(ns.db.link.deleted==0)
                 &(ns.db.link.nervatype_2==nervatype_item_id)&(ns.db.link.ref_id_2==ns.db.item.id))
    ref_trans = ns.db(ref_trans).select(ns.db.item.trans_id)
    if len(ref_trans)>0:
      response.trans_transnumber = DIV(A(ns.db.trans(id=ref_trans[0].trans_id).transnumber, _href="#", _onclick="javascript:window.open('"
                           +URL("frm_trans/view/trans/"+str(ref_trans[0].trans_id))+"', '_blank');")
                         ,_class="label_disabled", _style="width: 100%;display:block;padding: 3px;height: 22px;padding-right: 0px;")
    else:
      response.trans_transnumber = DIV(SPAN(""),_class="label_disabled", 
                                       _style="width: 100%;display:block;padding: 3px;height: 22px;padding-right: 0px;")
    
    response.place_id=""
    response.target_place_id=""
    ref_place = ns.db((ns.db.movement.deleted==0)&(ns.db.movement.trans_id==trans_id)).select(ns.db.movement.place_id)
    if len(ref_place)>0:
      response.place_control = DIV(A(ns.db.place(id=ref_place[0].place_id).planumber, _href="#", _onclick="javascript:window.open('"
                           +URL("frm_place/view/place/"+str(ref_place[0].place_id))+"', '_blank');")
                         ,_class="label_disabled", _style="width: 100%;display:block;padding: 3px;height: 22px;padding-right: 0px;")
    else:
      response.place_control = DIV(SPAN(""),_class="label_disabled", 
                                   _style="width: 100%;display:block;padding: 3px;height: 22px;padding-right: 0px;")
    if setting_audit_filter in ("disabled"):
      response.cmd_place = ""
    else:
      response.cmd_place = get_goprop_button(title=T("Edit places"),url=URL("find_place?back=1"))
      
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
                         ,_class="label_disabled", _style="width: 100%;display:block;padding: 3px;height: 22px;padding-right: 0px;"))
      else:
        target_place_id = place_id
        target_place_planumber = place_planumber
    else:
      target_place_id = place_id
      target_place_planumber = place_planumber
    if response.place_control==None:
      response.place_control = get_place_selector(place_planumber, width="100%",placetype="find_place_dlg_warehouse",title=T("Select warehouse"))
    response.target_place_id = INPUT(_name="target_place_id", _type="hidden", _value=target_place_id, _id="target_place_id")
    if response.target_place_control==None:
      response.target_place_control = get_place_selector(target_place_planumber, width="300px",placetype="find_place_dlg_warehouse",
                                        title=T("Select warehouse"),value_id="target_place_id",label_id="target_place_planumber", fnum="2")
            
  if transtype=="bank":
    response.direction_id = INPUT(_name="direction", _type="hidden", _value=direction_id, _id="direction")
    response.crdate = ""
    response.transdate=""
    response.transnumber_post=""
    payment_sum = ns.db((ns.db.payment.trans_id==trans_id)&(ns.db.payment.deleted==0)&(ns.db.payment.amount<0)).select(ns.db.payment.amount.sum().with_alias('amount')).as_list()
    if payment_sum[0]["amount"]==None:
      response.expense = DIV("0", _class="label_disabled", 
                               _style="text-align: right;padding: 3px;height: 22px;font-size: 12px;font-weight: bold;color: #551A8B;")
    else:
      response.expense = DIV(ns.splitThousands(float(payment_sum[0]["amount"])," ","."), _class="label_disabled",  
                               _style="text-align: right;padding: 3px;height: 22px;font-size: 12px;font-weight: bold;color: #551A8B;")
    
    payment_sum = ns.db((ns.db.payment.trans_id==trans_id)&(ns.db.payment.deleted==0)&(ns.db.payment.amount>0)).select(ns.db.payment.amount.sum().with_alias('amount')).as_list()
    if payment_sum[0]["amount"]==None:
      response.income = DIV("0", _class="label_disabled", 
                               _style="text-align: right;padding: 3px;height: 22px;font-size: 12px;font-weight: bold;color: #551A8B;")
    else:
      response.income = DIV(ns.splitThousands(float(payment_sum[0]["amount"])," ","."), _class="label_disabled",  
                               _style="text-align: right;padding: 3px;height: 22px;font-size: 12px;font-weight: bold;color: #551A8B;")
    
    payment_sum = ns.db((ns.db.payment.trans_id==trans_id)&(ns.db.payment.deleted==0)).select(ns.db.payment.amount.sum().with_alias('amount')).as_list()
    if payment_sum[0]["amount"]==None:
      response.balance = DIV("0", _class="label_disabled", 
                               _style="text-align: right;padding: 3px;height: 22px;font-size: 12px;font-weight: bold;color: #551A8B;")
    else:
      response.balance = DIV(ns.splitThousands(float(payment_sum[0]["amount"])," ","."), _class="label_disabled",  
                               _style="text-align: right;padding: 3px;height: 22px;font-size: 12px;font-weight: bold;color: #551A8B;")
      
    if response.place_control==None:
      response.place_control = get_place_selector(place_planumber, width="100%",placetype="find_place_dlg_bank",title=T("Select bank account"))
  
  if transtype=="cash":
    response.label_paidamount = T("Amount")
    paidamount = 0
    if trans_id>-1:
      form.custom.widget.direction["_disabled"]="disabled"
      response.direction_id = INPUT(_name="direction", _type="hidden", _value=direction_id, _id="direction")
      if len(ns.db(ns.db.payment.trans_id==trans_id).select().as_list())>0:
        paidamount = ns.db(ns.db.payment.trans_id==trans_id).select().as_list()[0]["amount"]
      response.transdate = ""
    else:
      response.direction_id=""
      response.transdate = INPUT(_name="transdate", _type="hidden", _value=form.vars.crdate, _id="trans_transdate")
    if direction=="out":
      paidamount=-paidamount
    response.paidamount = INPUT(_name="paidamount", _type="text", _value=paidamount, _id="trans_paidamount", _class="double")
    
    if response.place_control==None:
      response.place_control = get_place_selector(place_planumber, width="100%",placetype="find_place_dlg_cash",title=T("Select Cash desk"))
          
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
    response.employee_control = get_employee_selector(employee_empnumber, width="93%")
      
  if transtype=="waybill":
    response.view=dir_view+'/trans_movement.html'
    response.titleicon = URL(dir_images,'icon16_wrench_page.png')
    
    response.trans_id = INPUT(_name="trans_id", _type="hidden", _value="", _id="trans_id")
    response.target_place_id = ""
    if response.trans_transnumber==None:
      response.trans_transnumber=DIV(get_find_transitem_dlg(),
                                   A("",_id="reftrans_transnumber", _href="#", 
                                     _onclick="javascript:window.open('"+URL("frm_trans/view/trans/")+"'+document.getElementById('trans_id').value, '_blank');"), 
                                   _class="label_disabled", _id="fld_trans_transnumber", _style="display:none;padding: 3px;height: 22px;")
    
    response.customer_id = INPUT(_name="customer_id", _type="hidden", _value="", _id="customer_id")
    if response.customer_custname==None:
      if customer_audit_filter!="disabled":
        response.customer_custname=DIV(get_find_customer_dlg(),
                               A("",_id="customer_custname", _href="#", 
                                 _onclick="javascript:window.open('"+URL("frm_customer/view/customer/")+"'+document.getElementById('customer_id').value, '_blank');"), 
                               _class="label_disabled", _id="fld_customer_custname", _style="display:none;padding: 3px;height: 22px;") 
      else:
        response.customer_custname = DIV(SPAN("", _id="customer_custname"), _id="fld_customer_custname", _class="label_disabled", 
              _style="display:block;padding: 3px;height: 22px;padding-bottom: 0px;padding-top: 2px;")
    response.employee_id = INPUT(_name="employee_id", _type="hidden", _value="", _id="employee_id")  
    if response.employee_empnumber==None:
      if employee_audit_filter!="disabled":
        response.employee_empnumber=DIV(get_find_employee_dlg(),
                                   A("",_id="employee_empnumber", _href="#", 
                                     _onclick="javascript:window.open('"+URL("frm_employee/view/employee/")+"'+document.getElementById('employee_id').value, '_blank');"), 
                                   _class="label_disabled", _id="fld_employee_empnumber", _style="display:none;padding: 3px;height: 22px;")
      else:
        response.employee_empnumber = DIV(SPAN("", _id="employee_empnumber"), _id="fld_employee_empnumber", _class="label_disabled", 
              _style="display:block;padding: 3px;height: 22px;padding-bottom: 0px;padding-top: 2px;")
    response.employee_id = INPUT(_name="employee_id", _type="hidden", _value="", _id="employee_id")
    
    opt_trans = OPTION(T("Transaction"),_value="trans")
    opt_customer = OPTION(T("Customer"),_value="customer")
    opt_employee = OPTION(T("Employee"),_value="employee")
    
    form.custom.widget.crdate["_disabled"]="disabled"
    response.crdate = INPUT(_name="crdate", _type="hidden", _value=form.vars.crdate, _id="crdate")
    response.transdate = INPUT(_name="transdate", _type="hidden", _value=form.vars.crdate, _id="transdate")
    
    if trans_id==-1:
      form.vars.transnumber = dbfu.nextNumber(ns, {"id":"waybill", "step":False})
      form.vars.direction = ns.db((ns.db.groups.groupname=="direction")&(ns.db.groups.groupvalue==direction)).select().as_list()[0]["id"]
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
        response.trans_transnumber=DIV(get_find_transitem_dlg(),
                                   A(ns.db.trans(id=ref_id).transnumber, _id="reftrans_transnumber", _href="#", 
                                     _onclick="javascript:window.open('"+URL("frm_trans/view/trans/")+"'+document.getElementById('trans_id').value, '_blank');"), 
                                   _class="label_disabled", _id="fld_trans_transnumber", _style="display:block;padding: 3px;height: 22px;")
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
          response.customer_custname=DIV(get_find_customer_dlg(),
                               A(ns.db.customer(id=ref_id).custname, _id="customer_custname", _href="#", 
                                 _onclick="javascript:window.open('"+URL("frm_customer/view/customer/")+"'+document.getElementById('customer_id').value, '_blank');"), 
                               _class="label_disabled", _id="fld_customer_custname", _style="display:block;padding: 3px;height: 22px;")
        else:
          response.customer_custname = DIV(SPAN(ns.db.customer(id=ref_id).custname, _id="customer_custname"), _id="fld_customer_custname", _class="label_disabled", 
              _style="display:block;padding: 3px;height: 22px;padding-bottom: 0px;padding-top: 2px;")
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
          response.employee_empnumber=DIV(get_find_employee_dlg(),
                                   A(ns.db.employee(id=ref_id).empnumber, _id="employee_empnumber", _href="#", 
                                     _onclick="javascript:window.open('"+URL("frm_employee/view/employee/")+"'+document.getElementById('employee_id').value, '_blank');"), 
                                   _class="label_disabled", _id="fld_employee_empnumber", _style="display:block;padding: 3px;height: 22px;")
        else:
          response.employee_empnumber = DIV(SPAN(ns.db.employee(id=ref_id).empnumber, _id="employee_empnumber"), _id="fld_employee_empnumber", _class="label_disabled", 
              _style="display:block;padding: 3px;height: 22px;padding-bottom: 0px;padding-top: 2px;")
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
    response.trans_wsdistance_label = LABEL(T('Distance (km)'))
    response.trans_wsdistance_data = INPUT(_name="trans_wsdistance", _type="text", _value=trans_wsdistance, _id="trans_wsdistance", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.trans_wsrepair_label = LABEL(T('Repair time (h)'))
    response.trans_wsrepair_data = INPUT(_name="trans_wsrepair", _type="text", _value=trans_wsrepair, _id="trans_wsrepair", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.trans_wstotal_label = LABEL(T('Total time (h)'))
    response.trans_wstotal_data = INPUT(_name="trans_wstotal", _type="text", _value=trans_wstotal, _id="trans_wstotal", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.trans_wsnote_label = LABEL(T('Justification'))
    response.trans_wsnote_data = INPUT(_name="trans_wsnote", _type="text", _value=trans_wsnote, _id="trans_wsnote", 
                                               _class="string", _style="width: 100%;")
  
  if transtype in("rent"):
    response.trans_reholiday_label = LABEL(T('Holidays'))
    response.trans_reholiday_data = INPUT(_name="trans_reholiday", _type="text", _value=trans_reholiday, _id="trans_reholiday", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.trans_rebadtool_label = LABEL(T('Bad machine'))
    response.trans_rebadtool_data = INPUT(_name="trans_rebadtool", _type="text", _value=trans_rebadtool, _id="trans_rebadtool", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.trans_reother_label = LABEL(T('Other non-eligible'))
    response.trans_reother_data = INPUT(_name="trans_reother", _type="text", _value=trans_reother, _id="trans_reother", 
                                               _class="double", _style="width: 100%;text-align: right;")
    response.trans_rentnote_label = LABEL(T('Justification'))
    response.trans_rentnote_data = INPUT(_name="trans_rentnote", _type="text", _value=trans_rentnote, _id="trans_rentnote", 
                                               _class="string", _style="width: 100%;")
    
  if response.deleted==1 or response.closed==1 or (transtype_audit_filter[0] in ("readonly","disabled")):
    editable = False
  else:
    editable = True
  
  if trans_id>-1 and transtype in("waybill","inventory","delivery","production","formula"):
    #movement data
    if transtype=="waybill":
      movement = ((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.tool_id==ns.db.tool.id))
      fields=[ns.db.movement.id, ns.db.movement.shippingdate, ns.db.movement.tool_id, ns.db.tool.description, ns.db.movement.notes]
      ns.db.movement.notes.label = T("Comments")
      response.movement_tool_id = INPUT(_name="tool_id", _type="hidden", _value="", _id="tool_id")
      response.movement_serial = get_tool_selector("", width="100%")
    elif transtype=="production":
      movement = ((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)
                  &(ns.db.movement.shared==0)&(ns.db.movement.product_id==ns.db.product.id))
      fields=[ns.db.movement.id, ns.db.movement.shippingdate, ns.db.movement.place_id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, 
              ns.db.movement.notes, ns.db.movement.qty, ns.db.movement.shared]
      ns.db.movement.shared.readable = ns.db.movement.shared.writable = False
      ns.db.movement.qty.represent = lambda value,row: DIV(ns.splitThousands(-float(value)," ","."), _align="right", _width="100%")
    elif transtype=="formula":
      movement = ((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)
                  &(ns.db.movement.movetype==ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="plan")).select().as_list()[0]["id"])
                  &(ns.db.movement.product_id==ns.db.product.id))
      fields=[ns.db.movement.id, ns.db.movement.shippingdate, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, 
              ns.db.movement.qty, ns.db.movement.shared, ns.db.movement.place_id, ns.db.movement.notes]
      ns.db.movement.notes.label = T("Comments")
      ns.db.movement.shippingdate.readable = ns.db.movement.shippingdate.writable = False
    elif transtype=="inventory":
      movement = ((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.product_id==ns.db.product.id))
      fields=[ns.db.movement.id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes, ns.db.movement.qty]
    elif transtype=="delivery" and direction!="transfer":
      movement = ((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.product_id==ns.db.product.id))
      fields=[ns.db.movement.id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes, ns.db.movement.qty]
    elif transtype=="delivery" and direction=="transfer":
      nervatype_movement_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="movement")).select().as_list()[0]["id"]
      if len(ns.db((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)).select(ns.db.movement.id))>0:
        movement = ((ns.db.movement.id.belongs(ns.db((ns.db.link.ref_id_1.belongs(ns.db(ns.db.movement.trans_id==trans_id).select(ns.db.movement.id)))
                       &(ns.db.link.nervatype_1==nervatype_movement_id)&(ns.db.link.deleted==0)
                       &(ns.db.link.nervatype_2==nervatype_movement_id)).select(ns.db.link.ref_id_2.with_alias('id'))))
                  &(ns.db.movement.deleted==0)&(ns.db.movement.product_id==ns.db.product.id))
      else:
        movement = ((ns.db.movement.trans_id==trans_id)&(ns.db.movement.deleted==0)&(ns.db.movement.product_id==ns.db.product.id))
      fields=[ns.db.movement.id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes, ns.db.movement.qty]
    
    movement_count = ns.db(movement).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if transtype=="waybill":
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
        _value=ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="tool")).select().as_list()[0]["id"], _id="movement_movetype")
    else:
      response.movement_product_id = INPUT(_name="product_id", _type="hidden", _value="", _id="product_id")
      response.movement_product_control=get_product_selector("",width="100%",protype="item")
      response.movement_shippingdate_disabled = INPUT(_name="shippingdate", _type="text", _value="", _id="movement_shippingdate", _disabled="disabled")
      response.movement_shippingdate_enabled = INPUT(_name="shippingdate", _type="text", _value="", _id="shippingdate", _class="datetime",_style="width: 100%;text-align: center;")
      response.movement_shippingdate = INPUT(_name="shippingdate", _type="hidden", _value="", _id="shippingdate")
      response.movement_place_id = INPUT(_name="place_id", _type="hidden", _value="", _id="movement_place_id")
      response.movement_place_control=get_place_selector("",width="100%",placetype="find_place_dlg_warehouse",title=T("Select warehouse"),
                       value_id="movement_place_id", label_id="movement_place_planumber")
      response.movement_place_planumber = DIV(A("", _id="movement_place_planumber", _href="#", _onclick="javascript:window.open("
                           +"'" + URL("frm_place/view/place") + "/'+document.getElementById('movement_place_id').value+', '_blank');")
                         ,_class="label_disabled", _style="width: 100%;display:block;padding: 3px;height: 22px;")
      ns.db.movement.notes.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
      if transtype=="formula":
        response.movement_movetype = INPUT(_name="movetype", _type="hidden",
          _value=ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="plan")).select().as_list()[0]["id"], _id="movement_movetype")
      else:
        response.movement_movetype = INPUT(_name="movetype", _type="hidden",
          _value=ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="inventory")).select().as_list()[0]["id"], _id="movement_movetype")
      if transtype in("production","formula"):
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
        links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_movement("
                           +str(row["movement"]["id"])+",'',"
                           +str(row["movement"]["product_id"])
                           +",'"+ns.db.product(id=row["movement"]["product_id"]).description+"','','',"
                           +str(row["movement"]["qty"])+",'"
                           +json.dumps(str(row["movement"]["notes"]))[1:-1]+"','','',0)",
                           _title=T("Edit item"))]
    if editable:
      if transtype=="delivery" and direction!="transfer":
        response.cmd_movement_new = SPAN(" ",SPAN(str(movement_count), _class="detail_count"))
        links = []
      else:
        response.cmd_movement_new = get_tabnew_button(movement_count,T('New Item'), cmd_id="cmd_movement_new",
                                cmd = "$('#tabs').tabs({ selected: 0 });set_movement(-1, '"+str(datetime.date.today())+" 00:00:00"+"', '', '', '', '', 0, '','','',0)")
        response.cmd_movement_submit = get_command_button(caption=T("Save"),title=T("Update item data"),color="008B00", _id="cmd_movement_submit",
                              cmd="movement_update();return true;")
        links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this item?')+
                              "')){window.location ='"+URL("frm_trans/delete/movement/"+str(row["movement"]["id"]))+"';};return false;", 
                         _title=T("Delete Item")))
    else:
      response.cmd_movement_new = SPAN(" ",SPAN(str(movement_count), _class="detail_count"))
      response.cmd_movement_submit = ""
    
    ns.db.movement.id.label = T("No.")
    ns.db.movement.id.represent = lambda value,row: formatInteger(row["id"])
    response.view_movement = get_tab_grid(movement, ns.db.movement.id, _fields=fields, _deletable=False, links=links, _editable=False,
                                          multi_page="mv_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id))
            
    response.movement_form = SQLFORM(ns.db.movement, submit_button=T("Save"),_id="frm_movement")
    response.movement_form.process()
    response.movement_icon = URL(dir_images,'icon16_corrected.png')
    response.cmd_movement_cancel = A(SPAN(_class="icon cross"), 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_movement').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.movement_id = INPUT(_name="id", _type="hidden", _value="", _id="movement_id")
    response.movement_trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="movement_trans_id")
  
  if trans_id>-1 and transtype in("offer","order","worksheet","rent","invoice","receipt"):
    #item data
    item = ((ns.db.item.trans_id==trans_id)&(ns.db.item.deleted==0))
    item_count = ns.db(item).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']      
    if item_fields!=[]:
      fields = item_fields
    else:
      fields=[]
    
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
      links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this item?')+
                              "')){window.location ='"+URL("frm_trans/delete/item/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Item")))
      response.cmd_item_submit = get_command_button(caption=T("Save"),title=T("Update item data"),color="008B00", _id="cmd_item_submit",
                              cmd="item_update();return true;")
      response.cmd_item_new = get_tabnew_button(item_count,T('New Item'),cmd_id="cmd_item_new",
                                cmd = "$('#tabs').tabs({ selected: 0 });set_item(-1,'','','',0,0,0,'',0,0,0,0,'',0,0,0)")
    else:
      response.cmd_item_submit = ""
      response.cmd_item_new = SPAN(" ",SPAN(str(item_count), _class="detail_count"))
    ns.db.item.id.label = T("No.")
    ns.db.item.id.represent = lambda value,row: formatInteger(row["id"])
    ns.db.item.deposit.label = T("Dep.")
    response.view_item = get_tab_grid(item, ns.db.item.id, _fields=fields, _deletable=False, links=links, _editable=False,
                                          multi_page="it_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id))
    
    response.item_form = SQLFORM(ns.db.item, submit_button=T("Save"),_id="frm_item")
    response.item_form.process()  
    response.item_icon = URL(dir_images,'icon16_corrected.png')
    response.cmd_item_cancel = A(SPAN(_class="icon cross"), _id="cmd_item_cancel", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_item').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.item_id = INPUT(_name="id", _type="hidden", _value="", _id="item_id")
    response.item_trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="item_trans_id")
    response.item_product_id = INPUT(_name="product_id", _type="hidden", _value="", _id="product_id")
    response.item_product_control=get_product_selector("",width="100%")
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
  
  if trans_id>-1 and transtype in("bank"):
    #payment data
    payment = ((ns.db.payment.trans_id==trans_id)&(ns.db.payment.deleted==0))
    payment_count = ns.db(payment).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    fields=[ns.db.payment.id, ns.db.payment.paiddate, ns.db.payment.amount, ns.db.payment.notes]
    ns.db.payment.id.label = T("Item No.")
    ns.db.payment.id.represent = lambda value,row: formatInteger(row["id"])
    ns.db.payment.paiddate.label = T("Payment Date")
    links = [lambda row: A(SPAN(_class="icon plus"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#",
                         _onclick = "$('#tabs').tabs({ selected: 2 });set_link_invoice(-1,"+str(row.id)+",'','','',"+str(row["amount"])+",1);",
                         _title=T("Link Invoice")),
             lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_payment("
                           +str(row["id"])+",'"
                           +str(row["paiddate"])+"',"
                           +str(row["amount"])+",'"
                           +json.dumps(str(row["notes"]))[1:-1]+"')",
                           _title=T("Edit item"))]
    if editable:
      links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this item?')+
                              "')){window.location ='"+URL("frm_trans/delete/payment/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Item")))
      response.cmd_payment_submit = get_command_button(caption=T("Save"),title=T("Update item data"),color="008B00", _id="cmd_payment_submit",
                              cmd="payment_update();return true;")
      response.cmd_payment_new = get_tabnew_button(payment_count,T('New Item'),cmd_id="cmd_item_new",
                                cmd = "$('#tabs').tabs({ selected: 0 });set_payment(-1,'"+str(datetime.datetime.now().date())+"',0,'')")
    else:
      response.cmd_payment_submit = ""
      response.cmd_payment_new = SPAN(" ",SPAN(str(payment_count), _class="detail_count"))
    response.view_payment = get_tab_grid(payment, ns.db.payment.id, _fields=fields, _deletable=False, _editable=False, links=links, 
                                          multi_page="it_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id))
    
    response.payment_form = SQLFORM(ns.db.payment, submit_button=T("Save"),_id="frm_payment")
    response.payment_form.process()
    response.payment_icon = URL(dir_images,'icon16_corrected.png')
    response.cmd_payment_cancel = A(SPAN(_class="icon cross"), _id="cmd_payment_cancel", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_payment').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.payment_id = INPUT(_name="id", _type="hidden", _value="", _id="payment_id")
    response.payment_trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="payment_trans_id")
    
  if trans_id>-1 and transtype in("cash","bank"):
    #link invoice
    invoice_audit_filter = get_audit_filter("trans", "invoice")[0]
    if invoice_audit_filter!="disabled":
      nervatype_trans = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]  
      nervatype_payment = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="payment")).select().as_list()[0]["id"]
      
      link_qty = ns.db.fieldvalue.with_alias('link_qty')
      link_rate = ns.db.fieldvalue.with_alias('link_rate')
  
      join = [(ns.db.payment.on((ns.db.link.ref_id_1==ns.db.payment.id)&(ns.db.payment.deleted==0))),
              (ns.db.trans.on((ns.db.link.ref_id_2==ns.db.trans.id))),
              (link_qty.on((ns.db.link.id==link_qty.ref_id)&(link_qty.fieldname=="link_qty")&(link_qty.deleted==0))),
              (link_rate.on((ns.db.link.id==link_rate.ref_id)&(link_rate.fieldname=="link_rate")&(link_rate.deleted==0)))]
      query = ((ns.db.link.deleted==0)&(ns.db.link.nervatype_1==nervatype_payment)
               &(ns.db.link.nervatype_2==nervatype_trans)&(ns.db.payment.trans_id==trans_id))
            
      fields = [ns.db.link.ref_id_2, link_qty.value, link_rate.value]
      
      ns.db.link.ref_id_2.label = T("Invoice No.")
      link_qty.value.label = T("Amount")
      link_rate.value.label = T("Rate")
      link_qty.value.represent = lambda value,row: formatNumber(row["link_qty"]["value"])
      link_rate.value.represent = lambda value,row: formatNumber(row["link_rate"]["value"])
      ns.db.link.ref_id_2.represent = lambda value,row: A(SPAN(ns._link_id_formatter(ns.db.trans, "transnumber", value)),
                     _href=URL(r=request, f="frm_trans/view/trans/"+str(value)), _target="_blank")
      
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
      
      if editable:
        response.cmd_link_invoice_submit = get_command_button(caption=T("Save"),title=T("Update data"),color="008B00", _id="cmd_link_invoice_submit",
                              cmd="link_invoice_update();return true;")
        links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this link?')+
                              "')){window.location ='"+URL("frm_trans/delete/link/"+str(row["link"]["id"]))+"';};return false;", 
                         _title=T("Delete link")))
        if transtype=="bank":
          ns.db.link.ref_id_1.label = T("Item No.")
          ns.db.link.ref_id_1.represent = lambda value,row: formatInteger(row["ref_id_1"])
          fields.insert(0,ns.db.link.ref_id_1)
      else:
        response.cmd_link_invoice_submit = ""
    
      inv_count = ns.db(query).select('count(*)',join=join,left=None, cacheable=True).first()['count(*)']
      if inv_count>0:  
        response.view_link_invoice = get_tab_grid(query, ns.db.link.id, _fields=fields, _deletable=False, _editable=False, links=links, 
                                          multi_page="inv_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id),_join=join)
      else:
        response.view_link_invoice = ""
      
      if editable and transtype=="cash":
        response.cmd_link_invoice_new = get_tabnew_button(inv_count,T('New link'),cmd_id="cmd_link_invoice_new",
                                cmd = "$('#tabs').tabs({ selected: 1 });set_link_invoice(-1,"+str(ns.db.payment(trans_id=trans_id).id)+",'','','',"+str(ns.db.payment(trans_id=trans_id).amount)+",1);")
      else:
        response.cmd_link_invoice_new = SPAN(" ",SPAN(str(inv_count), _class="detail_count"))
      
      response.link_invoice_form = SQLFORM(ns.db.link, submit_button=T("Save"),_id="frm_link_invoice")
      response.link_invoice_form.process()
      response.link_invoice_icon = URL(dir_images,'icon16_link_edit.png')
      response.cmd_link_invoice_cancel = A(SPAN(_class="icon cross"), _id="cmd_link_invoice_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
        _onclick= "document.getElementById('edit_link_invoice').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
      response.link_invoice_id = INPUT(_name="id", _type="hidden", _value="", _id="link_invoice_id")
      response.link_invoice_trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="link_invoice_trans_id")
      response.link_invoice_nervatype_1 = INPUT(_name="nervatype_1", _type="hidden", _value=nervatype_payment, _id="nervatype_1")
      response.link_invoice_nervatype_2 = INPUT(_name="nervatype_2", _type="hidden", _value=nervatype_trans, _id="nervatype_2")
      response.link_invoice_linktype = INPUT(_name="linktype", _type="hidden", _value=0, _id="linktype")
      response.link_invoice_ref_id_1 = INPUT(_name="ref_id_1", _type="hidden", _value="", _id="ref_id_1")
      response.link_invoice_ref_id_2 = INPUT(_name="ref_id_2", _type="hidden", _value="", _id="ref_id_2")
      response.link_invoice_transitem_selector = get_base_selector(dlg=get_find_transitem_dlg(transtype="invoice"),label_id="link_transnumber",
                            label_url="'"+URL("frm_trans/view/trans/")+"'+document.getElementById('ref_id_2').value",
                            label_txt="", width="100%")
      response.link_invoice_curr = DIV("", _id="link_curr", _class="label_disabled", _style="width: 35px;padding: 3px;height: 22px;text-align: center;")
      response.link_invoice_amount = INPUT(_name="amount", _type="text", _value="", _id="link_amount", _class="double")
      response.link_invoice_rate = INPUT(_name="rate", _type="text", _value="", _id="link_rate", _class="double")
    else:
      response.view_link_invoice = ""
      response.invoice_disabled=True
  
  if trans_id>-1 and transtype in("invoice","receipt"):
    #payment data      
    nervatype_payment = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="payment")).select().as_list()[0]["id"]
    link_qty = ns.db.fieldvalue.with_alias('link_qty')
    link_rate = ns.db.fieldvalue.with_alias('link_rate')
    
    join = [(ns.db.payment.on((ns.db.link.ref_id_1==ns.db.payment.id)&(ns.db.payment.deleted==0))),
            (ns.db.trans.on((ns.db.payment.trans_id==ns.db.trans.id))),
            (ns.db.place.on((ns.db.trans.place_id==ns.db.place.id))),
            (link_qty.on((ns.db.link.id==link_qty.ref_id)&(link_qty.fieldname=="link_qty")&(link_qty.deleted==0))),
            (link_rate.on((ns.db.link.id==link_rate.ref_id)&(link_rate.fieldname=="link_rate")&(link_rate.deleted==0)))]
    query = ((ns.db.link.deleted==0)&(ns.db.link.nervatype_1==nervatype_payment)
             &(ns.db.link.nervatype_2==nervatype_trans)&(ns.db.link.ref_id_2==trans_id))
    
    fields=[ns.db.trans.id, ns.db.payment.paiddate, ns.db.trans.place_id, ns.db.payment.trans_id, ns.db.payment.id,
            ns.db.place.curr, link_qty.value, link_rate.value]
    
    ns.db.payment.id.label = T("Item No.")
    ns.db.payment.paiddate.label = T("Payment Date")
    ns.db.trans.place_id.label = T("Bank/Checkout")
    link_qty.value.label = T("Amount")
    link_rate.value.label = T("Rate")
    link_qty.value.represent = lambda value,row: formatNumber(row["link_qty"]["value"])
    link_rate.value.represent = lambda value,row: formatNumber(row["link_rate"]["value"])
    ns.db.payment.id.represent = lambda value,row: formatInteger(row["payment"]["id"])
    
    payment_count = ns.db(query).select('count(*)',join=join,left=None, cacheable=True).first()['count(*)']
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
    if editable:
      response.cmd_link_invoice_submit = get_command_button(caption=T("Save"),title=T("Update data"),color="008B00", _id="cmd_link_invoice_submit",
                            cmd="link_invoice_update();return true;")
      response.cmd_link_invoice_new = get_tabnew_button(payment_count,T('New link'),cmd_id="cmd_payment_new",
                              cmd = "$('#tabs').tabs({ selected: 2 });set_link_invoice(-1,'','','',"+str(trans_id)+",0,1)")
      links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                       _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this link?')+
                            "')){window.location ='"+URL("frm_trans/delete/link/"+str(row["link"]["id"]))+"';};return false;", 
                       _title=T("Delete link")))
    else:
      response.cmd_link_invoice_submit = ""
      response.cmd_link_invoice_new = SPAN(" ",SPAN(str(payment_count), _class="detail_count"))
    
    response.view_payment = get_tab_grid(query, ns.db.link.id, _fields=fields, _deletable=False, _editable=False, links=links, 
                                        multi_page="pm_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id),_join=join)
    
    response.link_invoice_form = SQLFORM(ns.db.link, submit_button=T("Save"),_id="frm_link_invoice")
    response.link_invoice_form.process()
    response.link_invoice_icon = URL(dir_images,'icon16_link_edit.png')
    response.cmd_link_invoice_cancel = A(SPAN(_class="icon cross"), _id="cmd_link_invoice_cancel", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_link_invoice').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.link_invoice_id = INPUT(_name="id", _type="hidden", _value="", _id="link_invoice_id")
    response.link_invoice_trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="link_invoice_trans_id")
    response.link_invoice_nervatype_1 = INPUT(_name="nervatype_1", _type="hidden", _value=nervatype_payment, _id="nervatype_1")
    response.link_invoice_nervatype_2 = INPUT(_name="nervatype_2", _type="hidden", _value=nervatype_trans, _id="nervatype_2")
    response.link_invoice_linktype = INPUT(_name="linktype", _type="hidden", _value=0, _id="linktype")
    response.link_invoice_ref_id_1 = INPUT(_name="ref_id_1", _type="hidden", _value="", _id="ref_id_1")
    response.link_invoice_ref_id_2 = INPUT(_name="ref_id_2", _type="hidden", _value="", _id="ref_id_2")
    response.link_invoice_payment_selector = get_base_selector(dlg=get_find_payment_dlg(),label_id="link_transnumber",
                          label_url="'"+URL("frm_trans/view/payment/")+"'+document.getElementById('ref_id_1').value", 
                          label_txt="", width="100%")
    response.link_invoice_curr = DIV("", _id="link_curr", _class="label_disabled", _style="width: 35px;padding: 3px;height: 22px;text-align: center;")
    response.link_invoice_amount = INPUT(_name="amount", _type="text", _value="", _id="link_amount", _class="double")
    response.link_invoice_rate = INPUT(_name="rate", _type="text", _value="", _id="link_rate", _class="double")
          
  if trans_id>-1 and transtype in("order","worksheet","rent"):
    #invoice
    invoice_audit_filter = get_audit_filter("trans", "invoice")[0]
    if invoice_audit_filter!="disabled":
      invoice_transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
      receipt_transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="receipt")).select().as_list()[0]["id"]
      
      query = ((ns.db.link.ref_id_2==trans_id)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0)
                &(ns.db.link.nervatype_2==nervatype_trans)&(ns.db.link.ref_id_1==ns.db.trans.id)&(ns.db.trans.deleted==0)
                &((ns.db.trans.transtype==invoice_transtype_id)|(ns.db.trans.transtype==receipt_transtype_id))
                &(ns.db.trans.id==ns.db.item.trans_id)&(ns.db.item.deleted==0))
      
      fields=[ns.db.item.deposit, ns.db.item.trans_id, ns.db.trans.transdate, ns.db.item.description, ns.db.item.qty, ns.db.trans.curr, ns.db.item.amount]
      ns.db.item.trans_id.label = T("Invoice No.")
      ns.db.trans.transdate.label = T("Invoice Date")
      ns.db.item.deposit.readable = ns.db.item.deposit.writable = True
      ns.db.item.deposit.label = T("Deposit")
      
      inv_count = ns.db(query).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
      if inv_count>0:  
        response.view_invoice = get_tab_grid(query, ns.db.item.id, _fields=fields, _deletable=False, _editable=False, links=None, 
                                          multi_page="inv_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id))
      else:
        response.view_invoice = ""
      
      if editable:
        dlg_create_trans2 = DIALOG(LOAD(f="dlg_create_trans/"+str(trans_id), ajax=True), title=T("Create a new document type"),
                        icon=URL(dir_images,'icon16_relation.png'), renderstyle=True, height=50, width=35)
        response.cmd_invoice_new = get_tabnew_button(inv_count,T('New Invoice'),cmd_id="cmd_invoice",
                                                     cmd='%s;return false' % dlg_create_trans2.show()) 
      else:
        response.cmd_invoice_new = SPAN(" ",SPAN(str(inv_count), _class="detail_count"))
    else:
      response.view_invoice = ""
      response.invoice_disabled=True
      
    #delivery
    delivery_audit_filter = get_audit_filter("trans", "delivery")[0]
    if delivery_audit_filter!="disabled":
      movement_nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="movement")).select().as_list()[0]["id"]
      item_nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="item")).select().as_list()[0]["id"]
      
      query = ((ns.db.item.trans_id==trans_id)&(ns.db.item.deleted==0)&
               (ns.db.link.nervatype_2==item_nervatype_id)&(ns.db.link.ref_id_2==ns.db.item.id)&
               (ns.db.item.product_id==ns.db.product.id)&
               (ns.db.link.nervatype_1==movement_nervatype_id)&(ns.db.link.ref_id_1==ns.db.movement.id)
               &(ns.db.link.deleted==0)&(ns.db.movement.deleted==0))
      
      fields=[ns.db.item.product_id, ns.db.movement.product_id, ns.db.movement.qty]
      ns.db.item.product_id.label = T("Item Product")
      ns.db.movement.product_id.label = T("Shipping Product")
      ns.db.movement.qty.label = T("Shipping Qty")
      
      groupfields=[ns.db.item.product_id,ns.db.movement.product_id,ns.db.movement.qty.sum().with_alias('qty')]
      groupby=[ns.db.item.product_id|ns.db.product.description|ns.db.movement.product_id]
      
      request.vars.page = request.vars["shi_page"]          
      response.view_inventory = SimpleGrid.grid(query=query, field_id=ns.db.movement.product_id, 
                 fields=fields, groupfields=groupfields, groupby=groupby, args=["view/trans/"+str(trans_id)],
                 orderby=ns.db.item.id, sortable=False, paginate=25, pagename="del_page", maxtextlength=25,
                 showbuttontext=False, editable=False, links=None)
      if type(response.view_inventory[1][0][0]).__name__!="TABLE":
        response.view_inventory = ""
      else:
        if response.view_inventory[len(response.view_inventory)-1]["_class"].startswith("web2py_paginator"):
          pages = response.view_inventory[len(response.view_inventory)-1].elements("a")
          for i in range(len(pages)):
            if pages[i]["_href"]:
              pages[i]["_href"] = pages[i]["_href"].replace("/frm_trans","/frm_trans/view/trans/"+str(trans_id)).replace("page=","shi_page=")
      
      if editable and delivery_audit_filter=="all":
        response.cmd_inventory_edit = get_tabedit_button(title=T('Edit Shipping'), cmd_id="cmd_inventory", 
                                      cmd="javascript:window.location='"+URL("frm_shipping/view/trans/"+str(trans_id))+"';")
      else:
        response.cmd_inventory_edit = ""
    else:
      response.view_inventory = ""
      response.inventory_disabled=True
  
  if trans_id>-1 and transtype in("order","worksheet","rent","invoice","receipt"):
    #tool movement
    movement_audit_filter = get_audit_filter("trans", "waybill")[0]
    if movement_audit_filter!="disabled":    
      transtype_waybill = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="waybill")).select().as_list()[0]["id"]
      ns.db.movement.notes.label = T('Additional info')
      ns.db.movement.trans_id.label = T('Movement No.')
      too = ((ns.db.trans.deleted==0)&(ns.db.trans.id==ns.db.movement.trans_id)
             &(ns.db.trans.transtype==transtype_waybill)
             &(ns.db.trans.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0)
             &(ns.db.link.nervatype_2==nervatype_trans)&(ns.db.link.ref_id_2==trans_id))
      
      fields = [ns.db.movement.trans_id, ns.db.trans.crdate,ns.db.trans.direction,
                ns.db.movement.shippingdate,ns.db.movement.tool_id,ns.db.tool.description,ns.db.movement.notes,
                ns.db.trans.transtate]
      
      too_count = ns.db(too).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
      if editable and movement_audit_filter=="all":
        response.cmd_movement_new = get_tabnew_button(too_count,T('New Movement'),cmd_id="", 
                                      cmd="javascript:window.open('"+URL("frm_trans/new/trans/waybill/out")+"?init_refnumber_type=trans&init_trans_id="+str(trans_id)+"', '_blank');")
      else:
        response.cmd_movement_new = SPAN(" ",SPAN(str(too_count), _class="detail_count"))
      
      response.view_too = get_tab_grid(too, ns.db.movement.id, _fields=fields, _deletable=False, _editable=False, links=None, 
                                          multi_page="too_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id))
    else:
      response.view_too = ""
      response.movement_disabled=True
  
  #show add/remove trans groups combo and setting button
  response.cmb_groups = get_cmb_groups("trans")
  if transtype_audit_filter[0] in ("readonly","disabled"):
    response.cmd_groups_add = ""
  else:                          
    response.cmd_groups_add = get_icon_button(T('Add to Group'),"cmd_groups_add", 
      cmd="var group_id = document.getElementById('cmb_groups').value;if(group_id!=''){window.location ='"+URL("frm_trans/new/link")
      +"?refnumber="+str(trans_id)+"&groups_id='+group_id;} else {alert('"+T('Missing Transaction Group!')+"');return false;}")
  
  if setting_audit_filter in ("disabled"):
    response.cmd_groups = ""
  else:
    response.cmd_groups = get_goprop_button(title=T("Edit Transaction Groups"), url=URL("frm_groups_trans?back=1"))
    
  #show trans groups list
  if trans_id>-1:
    trans_groups = ((ns.db.link.ref_id_1==trans_id)&(ns.db.link.nervatype_1==nervatype_trans)&
            (ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.deleted==0))
    ns.db.link.ref_id_2.represent = lambda value,row: ns._link_id_formatter(ns.db.groups, "groupvalue", value)
    ns.db.link.id.readable = ns.db.link.id.writable = False
    ns.db.link.nervatype_1.readable = ns.db.link.ref_id_1.readable = ns.db.link.nervatype_2.readable = ns.db.link.linktype.readable = ns.db.link.deleted.readable = False
    ns.db.link.ref_id_2.label = T('Groups')
    
    response.view_trans_groups = get_tab_grid(trans_groups, ns.db.link.id, _fields=None, _editable=False,
                                     _deletable=(transtype_audit_filter[0] not in ("readonly","disabled")), links=None, 
                                    multi_page="gr_page", rpl_1="/frm_trans", rpl_2="/frm_trans/view/trans/"+str(trans_id))
      
    #additional fields data
    query = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
             &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_trans)&(ns.db.fieldvalue.ref_id==trans_id))
    set_view_fields("trans", nervatype_trans, 1, editable, query, trans_id, "/frm_trans", "/frm_trans/view/trans/"+str(trans_id))
  else:
    response.view_trans_groups=None
    response.view_fields=None
    
  response.state_ico = DIV(IMG(_style="vertical-align: top;padding-top:6px;", _height="16px", _width="16px", _src=URL(dir_images,'icon16_lock_edit.png')),
                               _align="center", _style="width: 30px;height: 30px;background-color: #008B00;padding: 0px;padding-left: 2px;")
  if response.deleted==1:
    if response.transcast=="cancellation":
      form.custom.submit = DIV(SPAN(T('CANCELLATION')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
    else:
      form.custom.submit = DIV(SPAN(T('DELETED')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
    response.state_ico = DIV(IMG(_style="vertical-align: top;padding-top:6px;", _height="16px", _width="16px", _src=URL(dir_images,'icon16_lock.png')),
                             _align="center", _style="width: 30px;height: 30px;background-color: red;padding: 0px;padding-left: 2px;")
  elif response.closed==1:
    form.custom.submit = DIV(SPAN(T('CLOSED')),_style="background-color: #D9D9D9;color: #505050;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
    response.state_ico = DIV(IMG(_style="vertical-align: top;padding-top:6px;", _height="16px", _width="16px", _src=URL(dir_images,'icon16_lock.png')),
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
    ns.db.pattern.insert(**values)
    return
  
  if request.vars.has_key("def_tmp_value"):
    if request.vars.def_tmp_value=="-1":
      plst = ns.db((ns.db.pattern.description==request.vars.def_tmp_name)&(ns.db.pattern.deleted==0)&(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])).select().as_list()
      if len(plst)>0:
        pattern_id = plst[0]["id"]
      else:
        return
    else:
      pattern_id = int(request.vars.def_tmp_value)
    plst = ns.db((ns.db.pattern.deleted==0)&(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])).select().as_list()
    for pitem in plst:
      if pitem["id"]==pattern_id:
        ns.db(ns.db.pattern.id==pitem["id"]).update(**{"defpattern":1})
      else:
        ns.db(ns.db.pattern.id==pitem["id"]).update(**{"defpattern":0})
  
  if request.vars.has_key("del_tmp_value"):
    if request.vars.del_tmp_value=="-1":
      plst = ns.db((ns.db.pattern.description==request.vars.del_tmp_name)&(ns.db.pattern.deleted==0)&(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])).select().as_list()
      if len(plst)>0:
        pattern_id = plst[0]["id"]
      else:
        return
    else:
      pattern_id = int(request.vars.del_tmp_value)
    ns.db(ns.db.pattern.id==pattern_id).update(**{"deleted":1})
  
  if request.vars.has_key("save_tmp_value"):
    if request.vars.del_tmp_value=="-1":
      plst = ns.db((ns.db.pattern.description==request.vars.save_tmp_name)&(ns.db.pattern.deleted==0)&(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])).select().as_list()
      if len(plst)>0:
        pattern_id = plst[0]["id"]
      else:
        return
    else:
      pattern_id = int(request.vars.save_tmp_value)
    ns.db(ns.db.pattern.id==pattern_id).update(**{"notes":request.vars.fnote})
    
  if request.vars.has_key("load_tmp_value"):
    if request.vars.del_tmp_value=="-1":
      plst = ns.db((ns.db.pattern.description==request.vars.load_tmp_name)&(ns.db.pattern.deleted==0)&(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])).select().as_list()
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
      
  ns.db.trans.fnote.widget = ElrteWidget()
  ns.db.trans.fnote.widget.settings.lang = session._language
  ns.db.trans.fnote.widget.settings.toolbar = 'min'
  ns.db.trans.fnote.widget.settings.cssfiles = [URL('static', 'css/base.css')]
  
  response.view=dir_view+'/trans_fnote.html'
  response.transnumber = ns.db.trans(id=trans_id)["transnumber"]
  response.titleicon = URL(dir_images,'icon16_edit.png')
  response.trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="trans_id")
  
  if request.post_vars.has_key("fnote"):
    setLogtable("update", "log_trans_update", "trans", trans_id)
    ns.db(ns.db.trans.id==trans_id).update(**{"fnote":request.post_vars.fnote})
    response.flash = T('Success update!')
  
  note_temp = ns.db((ns.db.pattern.deleted==0)&(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])
                          ).select(orderby=ns.db.pattern.description).as_list()
  plst = ns.db((ns.db.pattern.deleted==0)&(ns.db.pattern.defpattern==1)&(ns.db.pattern.transtype==ns.db.trans(id=trans_id)["transtype"])).select().as_list()
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
  
  form = SQLFORM(ns.db.trans, record = trans_id, submit_button=T("Save"))
    
  rtable = TABLE(_style="width: 100%;height:100%;background-color: #F1F1F1;")
  rtable.append(TR(TD(form.custom.submit)))
  rtable.append(TR(TD(form.custom.widget.fnote)))
  
  transtype = ns.db.groups(id=ns.db.trans(id=trans_id).transtype).groupvalue
  nervatype_audit_filter = get_audit_filter("trans", transtype)[0]
  if nervatype_audit_filter in ("disabled"):
    response.cmd_back = get_home_button()
  else:
    response.cmd_back = get_back_button(URL("frm_trans/view/trans/"+str(trans_id)))
  response.cmd_help = get_help_button("fnote")
                
  if nervatype_audit_filter in ("readonly","disabled") or response.deleted==1 or response.closed==1:
    form.custom.submit = ""
    
  return dict(form=form)

@ns_auth.requires_login()
def frm_shipping():
  delivery_audit_filter = get_audit_filter("trans", "delivery")[0]
  if delivery_audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
    
  trans_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
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
                      TD(formatInteger(row["item_id"])),
                      TD(row["partnumber"]),
                      TD(A(row["description"], _href="#", 
                           _onclick="javascript:window.open('"+URL("frm_product/view/product/"+str(row["product_id"]))+"', '_blank');")),
                      TD(row["batch"]),
                      TD(formatNumber(row["qty"])),
                      _class=classtr))
    htmltable.append(tbody)
    return DIV(DIV(DIV(htmltable,_style='width:100%;overflow-x:auto;'),_class="web2py_table"),_class="web2py_grid")
  
  nervatype_movement_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="movement")).select().as_list()[0]["id"]
  nervatype_item_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="item")).select().as_list()[0]["id"]
  
  if request.vars.create_items and request.vars.create_place_id and request.vars.create_date:
    if len(session.shiptemp[trans_id])==0:
      return ""
    direction = ns.db.groups(id=ns.db.trans(id=trans_id).direction).groupvalue
    transnumber = dbfu.nextNumber(ns, {"id":"delivery_"+direction, "step":True})
    transtype_delivery = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="delivery")).select().as_list()[0]["id"]
    plst = ns.db((ns.db.pattern.deleted==0)&(ns.db.pattern.defpattern==1)&(ns.db.pattern.transtype==transtype_delivery)).select().as_list()
    if len(plst)>0:
      fnote = plst[0]["notes"]
    else:
      fnote=None
    values = {"transtype":transtype_delivery, "direction":ns.db.trans(id=trans_id).direction, "transnumber":transnumber, 
              "crdate":datetime.datetime.now().date(), "transdate":request.vars.create_date, "fnote":fnote,
              "transtate":ns.db((ns.db.groups.groupname=="transtate")&(ns.db.groups.groupvalue=="ok")).select().as_list()[0]["id"],
              "cruser_id":session.auth.user.id}
    del_trans_id = ns.db.trans.insert(**values)
    movetype_inventory_id = ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="inventory")).select().as_list()[0]["id"]
    for row in session.shiptemp[trans_id]:
      if direction=="out":
        qty=-row["qty"]
      else:
        qty=row["qty"]
      shippingdate = datetime.datetime.strptime(str(request.vars.create_date)+" 00:00:00", str('%Y-%m-%d %H:%M:%S'))
      values = {"trans_id":del_trans_id, "shippingdate":shippingdate, "movetype":movetype_inventory_id,
                "place_id":request.vars.create_place_id, "product_id":row["product_id"], "qty":qty, "notes":row["batch"]}
      movement_id = ns.db.movement.insert(**values)
      values = {"nervatype_1":nervatype_movement_id, "ref_id_1":movement_id, "nervatype_2":nervatype_item_id, "ref_id_2":row["item_id"]}
      ns.db.link.insert(**values)
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
  
  response.view=dir_view+'/shipping.html'
  response.titleicon = URL(dir_images,'icon16_lorry.png')
  response.icon_order = IMG(_src=URL(dir_images,'icon16_order.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_corrected = IMG(_src=URL(dir_images,'icon16_corrected.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_lorry_go = IMG(_src=URL(dir_images,'icon16_lorry_go.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.lo_menu = []
  response.subtitle=T('SHIPPING')
  
  response.transnumber = ns.db.trans(id=trans_id).transnumber
  response.direction = T(ns.db.groups(id=ns.db.trans(id=trans_id).direction).groupvalue)
  response.customer = DIV(A(ns.db.customer(id=ns.db.trans(id=trans_id).customer_id).custname, _href="#", _onclick="javascript:window.open('"
                           +URL("frm_customer/view/customer/"+str(ns.db.trans(id=trans_id).customer_id))+"', '_blank');")
                         ,_class="label_disabled", _style="width: 100%;display:block;padding: 3px;height: 22px;")
  
  delivery_audit_filter = get_audit_filter("trans", "delivery")[0]
  
  if delivery_audit_filter in ("disabled"):
    response.cmd_back = get_home_button()
  else:
    response.cmd_back = get_back_button(URL("frm_trans/view/trans/")+str(trans_id))
  response.cmd_help = get_help_button("shipping")
  
#product item list
  response.filter = SQLFORM.factory(
    Field('product', type='string', length=50, label=T('Description')),
    Field('nocomp', type='boolean', label=T('Not completed')),
    submit_button=T("Filter"), table_name="filter"
  )
  response.filter.process(keepvalues=True,onfailure=None)
  response.filter.errors.clear()
  
  protype_item = ns.db((ns.db.groups.groupname=="protype")&(ns.db.groups.groupvalue=="item")).select()[0]["id"]
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
  
  htmltable = TABLE(THEAD(TR(TH(),TH(T("No.")),TH(T("Product No.")),TH(T("Product")),TH(T("Item description")),
                             TH(T("Doc. qty")),TH(T("Turnover")),TH(T("Difference"),_colspan="2"))))
  tbody = TBODY()
  numrec=0
  for row in oitems:
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
    tbody.append(TR(
                    TD(A(SPAN(_class="icon plus"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="add_delivery("+str(row["item_id"])+","+str(row["product_id"])+","+str(row["diff"])+",'"+str(row["edit"])+"')",
                         _title=T("Add the difference")),
                       A(SPAN(_class="icon book"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#null", _title=T("Show stock"), 
                         _onclick='%s;return false' % DIALOG(LOAD(f='find_product_stock_dlg/'+str(row["product_id"]), ajax=True), 
                         title= "STOCKS | "+row["partnumber"]+" | "+ns.db.product(id=row["product_id"]).description, 
                         icon=URL(dir_images,'icon16_parts.png'),
                         renderstyle=True, height=90).show()),
                         _class="row_buttons", _style="width:40px;"),
                    TD(formatInteger(row["item_id"])),
                    TD(row["partnumber"]),
                    TD(A(ns.db.product(id=row["product_id"]).description, _href="#", 
                         _onclick="javascript:window.open('"+URL("frm_product/view/product/"+str(row["product_id"]))+"', '_blank');")),
                    TD(row["description"]),
                    TD(formatNumber(row["qty"])),
                    TD(formatNumber(row["tqty"])),
                    TD(formatNumber(row["diff"]),_style=dstyle),
                    TD(row["edit"],_style="vertical-align: middle;text-align: center;font-weight: bold;width:10px;"),
                    _class=classtr))
  htmltable.append(tbody)
  response.view_oitems = DIV(DIV(DIV(htmltable,_style='width:100%;overflow-x:auto;'),_class="web2py_table"),_class="web2py_grid")
  response.cmd_oitems_add = get_tabnew_button(T("ADD"),T('Add all of the difference'),"cmd_all_item", cmd="add_all_delivery()")
  
#create delivery
  if request.vars.add_all:
    for row in oitems:
      sitem = getOItem(session.shiptemp[trans_id],row["item_id"],row["product_id"])
      if not sitem and row["diff"]!=0:
        session.shiptemp[trans_id].append({"item_id":row["item_id"], "product_id":row["product_id"], 
                      "partnumber":row["partnumber"], "description":ns.db.product(id=row["product_id"]).description, 
                      "batch":"", "qty":row["diff"]})
    return "OK"
  
  response.cmd_oitems_remove = A(SPAN(_class="icon trash")," ",T("REMOVE"), _id="cmd_del_all", 
    _style="cursor: pointer; top:3px; text-align: center;padding: 2px;padding-left: 6px;padding-right: 3px;",
    _class="w2p_trap buttontext button", _href="#", _title=T('Remove all items'), _onclick= "remove_all_delivery()")
  response.shippingdate = INPUT(_class="date", _id="shippingdate", _name="shippingdate", _type="text", _value=datetime.datetime.now().date())
  response.place_control = get_place_selector("", width="100%",placetype="find_place_dlg_warehouse",title=T("Select warehouse"))
  response.place_id = INPUT(_name="place_id", _type="hidden", _value="", _id="place_id")
  if delivery_audit_filter in ("readonly","disabled"):
    response.cmd_create = ""
  else:
    response.cmd_create = get_command_button(_id="cmd_create", caption=T("Create"),title=T("Create delivery items"),color="008B00",
                              cmd="create_delivery_items();return true;", _height="30px")
  
  response.trans_id = INPUT(_name="trans_id", _type="hidden", _value=trans_id, _id="trans_id")
  response.item_id = INPUT(_name="item_id", _type="hidden", _value="", _id="item_id")
  response.product_id = INPUT(_name="product_id", _type="hidden", _value="", _id="product_id")
  response.cmd_update = get_command_button(_id="cmd_update", caption=T("Save"),title=T("Update changes..."),color="008B00",
                              cmd="update_delivery();return true;", _height="30px")
  response.cmd_cancel = A(SPAN(_class="icon cross"), _id="cmd_cancel", 
    _style="cursor: pointer; top:2px; text-align: center;padding: 2px;padding-left: 6px;padding-right: 3px;",
    _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
    _onclick= "var tbl=document.getElementById('edit_item');tbl.style.display = 'none';return true;")
  response.items_table=getItemsTable()
                  
#delivery data
  fields = [ns.db.movement.trans_id, ns.db.movement.shippingdate, ns.db.movement.place_id, 
            ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, 
            ns.db.movement.notes, ns.db.movement.qty]
  trans = ((ns.db.movement.deleted==0)&(ns.db.movement.product_id==ns.db.product.id)
           &(ns.db.movement.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_movement_id)&(ns.db.link.deleted==0)
           &(ns.db.link.nervatype_2==nervatype_item_id)&(ns.db.link.ref_id_2==ns.db.item.id)&(ns.db.item.trans_id==trans_id))
  
  trans_count = ns.db(trans).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
  response.cmd_trans_count= SPAN(" ",SPAN(str(trans_count), _class="detail_count"))
  ns.db.movement.shippingdate.represent = lambda value,row: formatDate(value)
  links = [lambda row: A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("frm_trans/view/trans/")+str(row.movement.trans_id), 
                         _target="_blank", _title=T("Edit Delivery"))]
  response.view_trans = get_tab_grid(_query=trans, _field_id=ns.db.movement.id, _fields=fields, _deletable=False, links=links, 
                             multi_page="trans_page", rpl_1="/frm_shipping", rpl_2="/frm_shipping/view/trans/"+str(trans_id)
                             ,_paginate=100, _editable=False)
        
  return dict()

@ns_auth.requires_login()
def frm_project():
  audit_filter = get_audit_filter("project", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    project_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    redirect(URL('frm_project/view/project/'+str(project_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    project_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    if delete_row("fieldvalue", fieldvalue_id, "project", project_id):
      redirect(URL('frm_project/view/project/'+str(project_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.fieldvalue.id==request.post_vars["id"]).validate_and_update(**request.post_vars)      
      else:
        ns.db.fieldvalue.validate_and_insert(**request.post_vars)
      setLogtable("update", "log_project_update", "project", request.post_vars["ref_id"])
      redirect(URL('frm_project/view/project/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
   
  if ruri.find("edit/address")>0 or ruri.find("view/address")>0:
    address_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    project_id = ns.db.address(id=address_id).ref_id
    redirect(URL('frm_project/view/project/'+str(project_id)))
    
  if ruri.find("delete/address")>0:
    address_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    project_id = ns.db.address(id=address_id).ref_id
    if delete_row("address", address_id, "project", project_id):
      redirect(URL('frm_project/view/project/'+str(project_id)))
        
  if request.post_vars["_formname"]=="address/create":
    clear_post_vars()
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.address.id==request.post_vars["id"]).update(**request.post_vars)      
      else:
        ns.db.address.insert(**request.post_vars)
      setLogtable("update", "log_project_update", "project", request.post_vars["ref_id"])
      redirect(URL('frm_project/view/customer/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
  
  if ruri.find("edit/contact")>0 or ruri.find("view/contact")>0:
    contact_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    project_id = ns.db.contact(id=contact_id).ref_id
    redirect(URL('frm_project/view/project/'+str(project_id)))
    
  if ruri.find("delete/contact")>0:
    contact_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    project_id = ns.db.contact(id=contact_id).ref_id
    if delete_row("contact", contact_id, "project", project_id):
      redirect(URL('frm_project/view/project/'+str(project_id)))
        
  if request.post_vars["_formname"]=="contact/create":
    clear_post_vars()
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.contact.id==request.post_vars["id"]).update(**request.post_vars)      
      else:
        ns.db.contact.insert(**request.post_vars)
      setLogtable("update", "log_project_update", "project", request.post_vars["ref_id"])
      redirect(URL('frm_project/view/customer/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
  
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
      
  if ruri.find("delete/project")>0:
    setLogtable("deleted", "log_project_deleted", "project", project_id)
    delete_ini = getSetting("set_trans_deleted")
    if delete_ini != "true":
      values = {"deleted":1}
      ns.db(ns.db.project.id==project_id).update(**values)
    else:
      dfield = deleteFieldValues("project", project_id)
      if dfield!=True:
        session.flash = dfield
        if request.wsgi.environ.has_key("HTTP_REFERER"):
          redirect(request.wsgi.environ["HTTP_REFERER"])
        else:
          redirect(URL('find_project_project'))
      ns.db(ns.db.project.id==project_id).delete()
      ns.db.commit()
    redirect(URL('find_project_project'))  
  
  response.view=dir_view+'/project.html'
  response.titleicon = URL(dir_images,'icon16_date_edit.png')
  response.icon_deffield = IMG(_src=URL(dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_address = IMG(_src=URL(dir_images,'icon16_address.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_contact = IMG(_src=URL(dir_images,'icon16_contact.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_calendar = IMG(_src=URL(dir_images,'icon16_calendar.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_calculator = IMG(_src=URL(dir_images,'icon16_calculator.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.pronumber = ""
  response.lo_menu = []
  
  nervatype_project = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="project")).select().as_list()[0]["id"]
  project_audit_filter = get_audit_filter("project", None)[0]
  
  ns.db.project.id.readable = ns.db.project.id.writable = False
  ns.db.project.deleted.readable = ns.db.project.deleted.writable = False
  if project_id>0:    
    response.subtitle=T('PROJECT')
    response.pronumber=ns.db.project(id=project_id).pronumber
    form = SQLFORM(ns.db.project, record = project_id, submit_button=T("Save"))
    if project_audit_filter!="disabled":
      response.cmd_report = get_report_button(title=T('Project Reports'), url='frm_report_project/'+str(project_id))
    else:
      response.cmd_report = ""
    if project_audit_filter=="all":
      response.cmd_delete = get_command_button(_id="cmd_delete", caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this project?')+
                              "')){window.location ='"+URL("frm_project/delete/project/"+str(project_id))+"';};return false;")
    else:
      response.cmd_delete = ""
  else:
    form = SQLFORM(ns.db.project, submit_button=T("Save"))
    form.vars.pronumber = dbfu.nextNumber(ns, {"id":"pronumber", "step":False})
    response.subtitle=T('NEW Project')
    response.pronumber = ""
    response.cmd_report = ""
    response.cmd_delete = ""
  
  if project_audit_filter in ("disabled"):
    response.cmd_back = get_home_button()
  else:
    response.cmd_back = get_back_button(URL("find_project_project"))
  response.cmd_help = get_help_button("project")
  
  if project_audit_filter in ("readonly","disabled"):
    form.custom.submit = "" 
          
  if form.validate(keepvalues=True):
    if request.post_vars.customer_id!="":
      form.vars.customer_id=request.post_vars.customer_id
    else:
      form.vars.customer_id=""      
    if project_id==-1:
      nextnumber = dbfu.nextNumber(ns, {"id":"pronumber", "step":False})
      if form.vars.pronumber == nextnumber:
        form.vars.pronumber = dbfu.nextNumber(ns, {"id":"pronumber", "step":True})
      form.vars.id = ns.db.project.insert(**dict(form.vars))
      #add auto deffields
      addnew = ns.db((ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_project)&
                     (ns.db.deffield.addnew==1)).select().as_list()
      for nfield in addnew:
        ns.db.fieldvalue.validate_and_insert(**{"fieldname":nfield["fieldname"],"ref_id":form.vars.id,"value":get_default_value(nfield["fieldtype"])})
      setLogtable("update", "log_project_update", "project", form.vars.id)
      redirect(URL('frm_project/view/project/'+str(form.vars.id)))      
    else:
      setLogtable("update", "log_project_update", "project", project_id)
      ns.db(ns.db.project.id==project_id).update(**form.vars)
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      if str(ns.db.project.fields).find(error)>0:
        flash+=ns.db.project[error].label+": "+form.errors[error]+", "
      else:
        flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  form.custom.widget.inactive = get_bool_input(project_id,"project","inactive")
  
  customer_id=""
  customer_name=""
  if project_id>-1:  
    if ns.db.project(id=project_id).customer_id!=None:
      customer_id = ns.db.project(id=project_id).customer_id
      customer_name = ns.db.customer(id=ns.db.project(id=project_id).customer_id).custname
  response.customer_id = INPUT(_name="customer_id", _type="hidden", _value=customer_id, _id="customer_id")
  if response.customer_control==None:
    response.customer_control = get_customer_selector(customer_name)

  #additional fields data
  if project_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_project)&(ns.db.fieldvalue.ref_id==project_id))
    editable = not (project_audit_filter in ("readonly","disabled"))
    set_view_fields("project", nervatype_project, 0, editable, fieldvalue, project_id, "/frm_project", "/frm_project/view/project/"+str(project_id))
   
  #address data
  if project_id>-1:
    if request.vars.ad_page!=None:
      request.vars.page=request.vars.ad_page
    else:
      request.vars.page=None
    address = ((ns.db.address.ref_id==project_id)&(ns.db.address.nervatype==nervatype_project)&(ns.db.address.deleted==0))
    ns.db.address.id.label = T("No.")
    ns.db.address.id.represent = lambda value,row: formatInteger(row["id"])
    ns.db.address.nervatype.readable = ns.db.address.ref_id.readable = ns.db.address.deleted.readable = False
    ns.db.address.street.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
    
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
    
    address_count = ns.db(address).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if project_audit_filter in ("readonly","disabled"):
      response.cmd_address_new = SPAN(" ",SPAN(str(address_count), _class="detail_count"))
      response.cmd_address_submit = ""
    else:
      links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this address?')+
                              "')){window.location ='"+URL("frm_project/delete/address/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Address")))
      response.cmd_address_submit = get_command_button(caption=T("Save"),title=T("Update address data"),color="008B00", _id="cmd_address_submit",
                              cmd="address_update();return true;")
      response.cmd_address_new = get_tabnew_button(address_count,T('New Address'),cmd_id="cmd_address_new",
                                cmd = "$('#tabs').tabs({ selected: 1 });set_address(-1,'','','','','','')")
  
    response.view_address = get_tab_grid(_query=address, _field_id=ns.db.address.id, _fields=None, _deletable=False, _editable=False, links=links, 
                               multi_page="ad_page", rpl_1="/frm_project", rpl_2="/frm_project/view/project/"+str(project_id))
    
    response.address_form = SQLFORM(ns.db.address, submit_button=T("Save"),_id="frm_address")
    response.address_form.process()
    response.address_icon = URL(dir_images,'icon16_address.png')
    response.cmd_address_cancel = A(SPAN(_class="icon cross"), _id="cmd_address_cancel", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_address').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.address_id = INPUT(_name="id", _type="hidden", _value="", _id="address_id")
    response.address_ref_id = INPUT(_name="ref_id", _type="hidden", _value=project_id, _id="address_ref_id")
    response.address_nervatype = INPUT(_name="nervatype", _type="hidden", _value=nervatype_project, _id="address_nervatype")
  
  #contact data
  if project_id>-1:
    if request.vars.ct_page!=None:
      request.vars.page=request.vars.ct_page
    else:
      request.vars.page=None
    contact = ((ns.db.contact.ref_id==project_id)&(ns.db.contact.nervatype==nervatype_project)&(ns.db.contact.deleted==0))
    ns.db.contact.nervatype.readable = ns.db.contact.ref_id.readable = ns.db.contact.deleted.readable = False
    ns.db.contact.id.label = T("No.")
    ns.db.contact.id.represent = lambda value,row: formatInteger(row["id"])
    
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
    
    contact_count = ns.db(contact).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if project_audit_filter in ("readonly","disabled"):
      response.cmd_contact_submit = ""
      response.cmd_contact_new = SPAN(" ",SPAN(str(contact_count), _class="detail_count"))
    else:
      links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this contact?')+
                              "')){window.location ='"+URL("frm_project/delete/contact/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Contact")))
      response.cmd_contact_submit = get_command_button(caption=T("Save"),title=T("Update contact data"),color="008B00", _id="cmd_contact_submit",
                              cmd="contact_update();return true;")
      response.cmd_contact_new = get_tabnew_button(contact_count,T('New Contact'),cmd_id="cmd_contact_new",
                                cmd = "$('#tabs').tabs({ selected: 2 });set_contact(-1,'','','','','','','','')")
  
    response.view_contact = get_tab_grid(_query=contact, _field_id=ns.db.contact.id, _fields=None, _deletable=False, _editable=False, links=links, 
                               multi_page="ct_page", rpl_1="/frm_project", rpl_2="/frm_project/view/project/"+str(project_id))
    
    response.contact_form = SQLFORM(ns.db.contact, submit_button=T("Save"),_id="frm_contact")
    response.contact_form.process()
    response.contact_icon = URL(dir_images,'icon16_contact.png')
    response.cmd_contact_cancel = A(SPAN(_class="icon cross"), _id="cmd_contact_cancel", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_contact').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.contact_id = INPUT(_name="id", _type="hidden", _value="", _id="contact_id")
    response.contact_ref_id = INPUT(_name="ref_id", _type="hidden", _value=project_id, _id="contact_ref_id")
    response.contact_nervatype = INPUT(_name="nervatype", _type="hidden", _value=nervatype_project, _id="contact_nervatype")  
  
  #event data  
  event_audit_filter = get_audit_filter("event", None)[0]
  if event_audit_filter!="disabled" and project_id>-1:
    event = ((ns.db.event.ref_id==project_id)&(ns.db.event.nervatype==nervatype_project)&(ns.db.event.deleted==0))
    ns.db.event.id.readable = ns.db.event.id.writable = False
    ns.db.event.nervatype.readable = ns.db.event.ref_id.readable = ns.db.event.uid.readable = False
    links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("export2ical?id="+str(row.id)), _target="_blank", _title=T("Export Item"))]
  
    event_count = ns.db(event).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if (project_audit_filter in ("readonly","disabled")) or (event_audit_filter in ("readonly","disabled")):
      gdeleted = False
      response.cmd_event_new = SPAN(" ",SPAN(str(event_count), _class="detail_count"))
    else:
      gdeleted = True
      response.cmd_event_new = get_tabnew_button(event_count,T('New Event'),cmd_id="tabs-events",url=URL("frm_event/new/event")+"?refnumber="+form.formname)
    
    response.view_event = get_tab_grid(_query=event, _field_id=ns.db.event.id, _fields=None, _deletable=gdeleted, links=links, 
                             multi_page="ev_page", rpl_1="/frm_project", rpl_2="/frm_project/view/project/"+str(project_id))  
  else:
    response.view_event = ""
    response.event_disabled=True
  
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
    response.cmd_trans_new = SPAN(" ",SPAN(str(trans_count), _class="detail_count"))
    response.view_trans = get_tab_grid(_query=trans, _field_id=ns.db.trans.id, _fields=fields, _deletable=False, links=None, 
                               multi_page="trans_page", rpl_1="/frm_project", rpl_2="/frm_project/view/project/"+str(project_id)) 
      
  return dict(form=form)
                
@ns_auth.requires_login()
def frm_customer():
  customer_audit_filter = get_audit_filter("customer", None)[0]
  setting_audit_filter = get_audit_filter("setting", None)[0]
  
  if customer_audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    customer_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    redirect(URL('frm_customer/view/customer/'+str(customer_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    customer_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    if delete_row("fieldvalue", fieldvalue_id, "customer", customer_id):
      redirect(URL('frm_customer/view/customer/'+str(customer_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.fieldvalue.id==request.post_vars["id"]).validate_and_update(**request.post_vars)      
      else:
        ns.db.fieldvalue.validate_and_insert(**request.post_vars)
      setLogtable("update", "log_customer_update", "customer", request.post_vars["ref_id"])
      redirect(URL('frm_customer/view/customer/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
   
  if ruri.find("edit/address")>0 or ruri.find("view/address")>0:
    address_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    customer_id = ns.db.address(id=address_id).ref_id
    redirect(URL('frm_customer/view/customer/'+str(customer_id)))
    
  if ruri.find("delete/address")>0:
    address_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    customer_id = ns.db.address(id=address_id).ref_id
    if delete_row("address", address_id, "customer", customer_id):
      redirect(URL('frm_customer/view/customer/'+str(customer_id)))
        
  if request.post_vars["_formname"]=="address/create":
    clear_post_vars()
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.address.id==request.post_vars["id"]).update(**request.post_vars)      
      else:
        ns.db.address.insert(**request.post_vars)
      setLogtable("update", "log_customer_update", "customer", request.post_vars["ref_id"])
      redirect(URL('frm_customer/view/customer/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
  
  if ruri.find("edit/contact")>0 or ruri.find("view/contact")>0:
    contact_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    customer_id = ns.db.contact(id=contact_id).ref_id
    redirect(URL('frm_customer/view/customer/'+str(customer_id)))
    
  if ruri.find("delete/contact")>0:
    contact_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    customer_id = ns.db.contact(id=contact_id).ref_id
    if delete_row("contact", contact_id, "customer", customer_id):
      redirect(URL('frm_customer/view/customer/'+str(customer_id)))
        
  if request.post_vars["_formname"]=="contact/create":
    clear_post_vars()
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.contact.id==request.post_vars["id"]).update(**request.post_vars)      
      else:
        ns.db.contact.insert(**request.post_vars)
      setLogtable("update", "log_customer_update", "customer", request.post_vars["ref_id"])
      redirect(URL('frm_customer/view/customer/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
  
  if ruri.find("event")>0:
    ruri = "frm_event/view"+ruri[ruri.find("frm_customer/edit")+17:]
    redirect(URL(ruri))
  
  if ruri.find("new/link")>0:
    customer_id = int(request.vars.refnumber)
    cust_nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
    groups_id = int(request.vars.groups_id)
    groups_nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
    glink = ns.db((ns.db.link.ref_id_1==customer_id)&(ns.db.link.nervatype_1==cust_nervatype)&(ns.db.link.deleted==0)
              &(ns.db.link.nervatype_2==groups_nervatype)&(ns.db.link.ref_id_2==groups_id)).select().as_list()
    if len(glink)==0:
      values = {"nervatype_1":cust_nervatype, "ref_id_1":customer_id, "nervatype_2":groups_nervatype, "ref_id_2":groups_id}
      ns.db.link.insert(**values)
    redirect(URL('frm_customer/view/customer/'+str(customer_id)))
    
  if ruri.find("delete/link")>0:
    link_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if delete_row("link",link_id):
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(ruri[:ruri.find("delete/link")-1])
  
  if ruri.find("new/customer")>0:
    customer_id = -1
  else:
    customer_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      
  if ruri.find("delete/customer")>0:
    setLogtable("deleted", "log_customer_deleted", "customer", customer_id)
    delete_ini = getSetting("set_trans_deleted")
    if delete_ini != "true":
      values = {"deleted":1}
      ns.db(ns.db.customer.id==customer_id).update(**values)
    else:
      dfield = deleteFieldValues("customer", customer_id)
      if dfield!=True:
        session.flash = dfield
        if request.wsgi.environ.has_key("HTTP_REFERER"):
          redirect(request.wsgi.environ["HTTP_REFERER"])
        else:
          redirect(URL('find_customer_customer'))
      ns.db(ns.db.customer.id==customer_id).delete()
      ns.db.commit()
    redirect(URL('find_customer_customer'))  
  
  response.view=dir_view+'/customer.html'
  response.titleicon = URL(dir_images,'icon16_customer.png')
  response.icon_deffield = IMG(_src=URL(dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_address = IMG(_src=URL(dir_images,'icon16_address.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_contact = IMG(_src=URL(dir_images,'icon16_contact.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_calendar = IMG(_src=URL(dir_images,'icon16_calendar.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.custnumber = ""
  
  response.lo_menu = []
  
  nervatype_customer = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
  nervatype_groups = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  
  #basic customer data
  ns.db.customer.id.readable = ns.db.customer.id.writable = False
  ns.db.customer.deleted.readable = ns.db.customer.deleted.writable = False
  if customer_id>0:    
    if customer_id==1:
      response.home = True
      response.subtitle=T('COMPANY')
      response.custnumber=""
      ns.db.customer.custname.label = T('Company Name')
      response.titleicon = URL(dir_images,'icon16_home.png')
      customer_audit_filter = setting_audit_filter
      if len(request.post_vars)>0:
        request.post_vars.custtype = ns.db.customer(id=1).custtype
        request.post_vars.custnumber = ns.db.customer(id=1).custnumber
        request.post_vars.terms = ns.db.customer(id=1).terms
        request.post_vars.creditlimit = ns.db.customer(id=1).creditlimit
        request.post_vars.discount = ns.db.customer(id=1).discount
    else:
      response.subtitle=T('CUSTOMER')
      response.custnumber=ns.db.customer(id=customer_id).custnumber
      ns.db.customer.custtype.requires = IS_IN_DB(ns.db((ns.db.groups.groupname.like('custtype'))&(ns.db.groups.groupvalue!="own")), ns.db.groups.id, '%(groupvalue)s')
    form = SQLFORM(ns.db.customer, record = customer_id, submit_button=T("Save"))
    if customer_audit_filter!="disabled":
      response.cmd_report = get_report_button(title=T('Customer Reports'), url='frm_report_customer/'+str(customer_id))
    else:
      response.cmd_report = ""
    if customer_audit_filter=="all":
      response.cmd_delete = get_command_button(_id="cmd_delete", caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this customer?')+
                              "')){window.location ='"+URL("frm_customer/delete/customer/"+str(customer_id))+"';};return false;")
    else:
      response.cmd_delete = ""
  else:
    form = SQLFORM(ns.db.customer, submit_button=T("Save"))
    form.vars.custnumber = dbfu.nextNumber(ns, {"id":"custnumber", "step":False})
    form.vars.custtype = ns.db((ns.db.groups.groupname=="custtype")&(ns.db.groups.groupvalue=="company")).select().as_list()[0]["id"]
    response.subtitle=T('NEW CUSTOMER')
    response.custnumber = ""
    response.cmd_report = ""
    response.cmd_delete = ""
  
  if customer_id==1:
    response.cmd_back = get_home_button()
  else:
    if customer_audit_filter in ("disabled"):
      response.cmd_back = get_home_button()
    else:
      response.cmd_back = get_back_button(URL("find_customer_customer")) 

  response.cmd_help = get_help_button("customer")
  
  if (customer_id!=1 and (customer_audit_filter in ("readonly","disabled"))) or (customer_id==1 and (setting_audit_filter in ("readonly","disabled"))):
    form.custom.submit = ""      
  if form.validate(keepvalues=True):
    if customer_id==-1:
      nextnumber = dbfu.nextNumber(ns, {"id":"custnumber", "step":False})
      if form.vars.custnumber == nextnumber:
        form.vars.custnumber = dbfu.nextNumber(ns, {"id":"custnumber", "step":True})
      form.vars.id = ns.db.customer.insert(**dict(form.vars))
      #add auto deffields
      addnew = ns.db((ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_customer)&
                     (ns.db.deffield.addnew==1)).select().as_list()
      for nfield in addnew:
        ns.db.fieldvalue.validate_and_insert(**{"fieldname":nfield["fieldname"],"ref_id":form.vars.id,"value":get_default_value(nfield["fieldtype"])})
      setLogtable("update", "log_customer_update", "customer", form.vars.id)
      redirect(URL('frm_customer/view/customer/'+str(form.vars.id)))      
    else:
      ns.db(ns.db.customer.id==customer_id).update(**form.vars)
      setLogtable("update", "log_customer_update", "customer", customer_id)
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      if str(ns.db.customer.fields).find(error)>0:
        flash+=ns.db.customer[error].label+": "+form.errors[error]+", "
      else:
        flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  form.custom.widget.notax = get_bool_input(customer_id,"customer","notax")
  form.custom.widget.inactive = get_bool_input(customer_id,"customer","inactive")

  #show customer groups list
  if customer_id>-1:
    customer_groups = ((ns.db.link.ref_id_1==customer_id)&(ns.db.link.nervatype_1==nervatype_customer)&
            (ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.deleted==0))
    ns.db.link.ref_id_2.represent = lambda value,row: ns._link_id_formatter(ns.db.groups, "groupvalue", value)
    ns.db.link.id.readable = ns.db.link.id.writable = False
    ns.db.link.nervatype_1.readable = ns.db.link.ref_id_1.readable = ns.db.link.nervatype_2.readable = ns.db.link.linktype.readable = ns.db.link.deleted.readable = False
    ns.db.link.ref_id_2.label = T('Groups')
    response.view_customer_groups = get_tab_grid(customer_groups, ns.db.link.id, _fields=None, _editable=False,
                                     _deletable=(customer_audit_filter not in ("readonly","disabled")), links=None, 
                                    multi_page="gr_page", rpl_1="/frm_customer", rpl_2="/frm_customer/view/customer/"+str(customer_id))
    
    #show add/remove customer groups combo and setting button
    if customer_audit_filter not in ("readonly","disabled"):
      response.cmb_groups = get_cmb_groups("customer")
      response.cmd_groups_add = get_icon_button(T('Add to Group'),"cmd_groups_add", 
        cmd="var group_id = document.getElementById('cmb_groups').value;if(group_id!=''){window.location ='"+URL("frm_customer/new/link")
        +"?refnumber="+str(customer_id)+"&groups_id='+group_id;} else {alert('"+T('Missing Transaction Group!')+"');return false;}")                          
      response.cmd_groups = get_goprop_button(title=T("Edit Customer Groups"), url=URL("frm_groups_customer?back=1"))
    else:
      response.cmd_groups_add = ""
      response.cmb_groups = ""
      response.cmd_groups = ""
    
  setting_audit_filter = get_audit_filter("setting", None)[0]
  if setting_audit_filter=="disabled":
    response.cmd_groups = ""
                
  #additional fields data
  if customer_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_customer)&(ns.db.fieldvalue.ref_id==customer_id))
    editable = not customer_audit_filter in ("readonly","disabled")
    #editable = (not (customer_id!=1 and customer_audit_filter in ("readonly","disabled"))) or (not (customer_id==1 and setting_audit_filter in ("readonly","disabled")))
    set_view_fields("customer", nervatype_customer, 0, editable, fieldvalue, customer_id, "/frm_customer", "/frm_customer/view/customer/"+str(customer_id))   
  
  #address data
  if customer_id>-1:
    if request.vars.ad_page!=None:
      request.vars.page=request.vars.ad_page
    else:
      request.vars.page=None
    address = ((ns.db.address.ref_id==customer_id)&(ns.db.address.nervatype==nervatype_customer)&(ns.db.address.deleted==0))
    ns.db.address.id.label = T("No.")
    ns.db.address.id.represent = lambda value,row: formatInteger(row["id"])
    ns.db.address.nervatype.readable = ns.db.address.ref_id.readable = ns.db.address.deleted.readable = False
    ns.db.address.street.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
    
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
    
    address_count = ns.db(address).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if (customer_id!=1 and customer_audit_filter in ("readonly","disabled")) or (customer_id==1 and setting_audit_filter in ("readonly","disabled")):
      response.cmd_address_new = SPAN(" ",SPAN(str(address_count), _class="detail_count"))
      response.cmd_address_submit = ""
    else:
      links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this address?')+
                              "')){window.location ='"+URL("frm_customer/delete/address/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Address")))
      response.cmd_address_submit = get_command_button(caption=T("Save"),title=T("Update address data"),color="008B00", _id="cmd_address_submit",
                              cmd="address_update();return true;")
      response.cmd_address_new = get_tabnew_button(address_count,T('New Address'),cmd_id="cmd_address_new",
                                cmd = "$('#tabs').tabs({ selected: 1 });set_address(-1,'','','','','','')")
  
    response.view_address = get_tab_grid(_query=address, _field_id=ns.db.address.id, _fields=None, _deletable=False, _editable=False, links=links, 
                               multi_page="ad_page", rpl_1="/frm_customer", rpl_2="/frm_customer/view/customer/"+str(customer_id))
    
    response.address_form = SQLFORM(ns.db.address, submit_button=T("Save"),_id="frm_address")
    response.address_form.process()
    response.address_icon = URL(dir_images,'icon16_address.png')
    response.cmd_address_cancel = A(SPAN(_class="icon cross"), _id="cmd_address_cancel", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_address').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.address_id = INPUT(_name="id", _type="hidden", _value="", _id="address_id")
    response.address_ref_id = INPUT(_name="ref_id", _type="hidden", _value=customer_id, _id="address_ref_id")
    response.address_nervatype = INPUT(_name="nervatype", _type="hidden", _value=nervatype_customer, _id="address_nervatype")
    
  #contact data
  if customer_id>-1:
    if request.vars.ct_page!=None:
      request.vars.page=request.vars.ct_page
    else:
      request.vars.page=None
    contact = ((ns.db.contact.ref_id==customer_id)&(ns.db.contact.nervatype==nervatype_customer)&(ns.db.contact.deleted==0))
    ns.db.contact.nervatype.readable = ns.db.contact.ref_id.readable = ns.db.contact.deleted.readable = False
    ns.db.contact.id.label = T("No.")
    ns.db.contact.id.represent = lambda value,row: formatInteger(row["id"])
    
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
    
    contact_count = ns.db(contact).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if (customer_id!=1 and customer_audit_filter in ("readonly","disabled")) or (customer_id==1 and setting_audit_filter in ("readonly","disabled")):
      response.cmd_contact_submit = ""
      response.cmd_contact_new = SPAN(" ",SPAN(str(contact_count), _class="detail_count"))
    else:
      links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this contact?')+
                              "')){window.location ='"+URL("frm_customer/delete/contact/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Contact")))
      response.cmd_contact_submit = get_command_button(caption=T("Save"),title=T("Update contact data"),color="008B00", _id="cmd_contact_submit",
                              cmd="contact_update();return true;")
      response.cmd_contact_new = get_tabnew_button(contact_count,T('New Contact'),cmd_id="cmd_contact_new",
                                cmd = "$('#tabs').tabs({ selected: 2 });set_contact(-1,'','','','','','','','')")
  
    response.view_contact = get_tab_grid(_query=contact, _field_id=ns.db.contact.id, _fields=None, _deletable=False, _editable=False, links=links, 
                               multi_page="ct_page", rpl_1="/frm_customer", rpl_2="/frm_customer/view/customer/"+str(customer_id))
    
    response.contact_form = SQLFORM(ns.db.contact, submit_button=T("Save"),_id="frm_contact")
    response.contact_form.process()
    response.contact_icon = URL(dir_images,'icon16_contact.png')
    response.cmd_contact_cancel = A(SPAN(_class="icon cross"), _id="cmd_contact_cancel", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_contact').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.contact_id = INPUT(_name="id", _type="hidden", _value="", _id="contact_id")
    response.contact_ref_id = INPUT(_name="ref_id", _type="hidden", _value=customer_id, _id="contact_ref_id")
    response.contact_nervatype = INPUT(_name="nervatype", _type="hidden", _value=nervatype_customer, _id="contact_nervatype")
      
  #event data  
  event_audit_filter = get_audit_filter("event", None)[0]
  if event_audit_filter!="disabled" and customer_id>-1:
    event = ((ns.db.event.ref_id==customer_id)&(ns.db.event.nervatype==nervatype_customer)&(ns.db.event.deleted==0))
    ns.db.event.id.readable = ns.db.event.id.writable = False
    ns.db.event.nervatype.readable = ns.db.event.ref_id.readable = ns.db.event.uid.readable = False
    links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("export2ical?id="+str(row.id)), _target="_blank", _title=T("Export Item"))]
    event_count = ns.db(event).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if (customer_id!=1 and customer_audit_filter in ("readonly","disabled")) or (customer_id==1 and setting_audit_filter in ("readonly","disabled")) or (event_audit_filter in ("readonly","disabled")):
      gdeleted = False
      response.cmd_event_new = SPAN(" ",SPAN(str(event_count), _class="detail_count"))
    else:
      gdeleted = True
      response.cmd_event_new = get_tabnew_button(event_count,T('New Event'),cmd_id="tabs-events",url=URL("frm_event/new/event")+"?refnumber="+form.formname)

    response.view_event = get_tab_grid(_query=event, _field_id=ns.db.event.id, _fields=None, _deletable=gdeleted, links=links, 
                             multi_page="ev_page", rpl_1="/frm_customer", rpl_2="/frm_customer/view/customer/"+str(customer_id))
  else:
    response.view_event = ""
    response.event_disabled=True
      
  return dict(form=form)

@ns_auth.requires_login()
def frm_product():
  audit_filter = get_audit_filter("product", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
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
    redirect(URL('frm_product/view/product/'+str(product_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    product_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    if delete_row("fieldvalue", fieldvalue_id, "product", product_id):
      redirect(URL('frm_product/view/product/'+str(product_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.fieldvalue.id==request.post_vars["id"]).validate_and_update(**request.post_vars)      
      else:
        ns.db.fieldvalue.validate_and_insert(**request.post_vars)
      setLogtable("update", "log_product_update", "product", request.post_vars["ref_id"])
      redirect(URL('frm_product/view/product/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
    
  if ruri.find("edit/barcode")>0 or ruri.find("view/barcode")>0:
    barcode_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    product_id = ns.db.barcode(id=barcode_id).product_id
    redirect(URL('frm_product/view/product/'+str(product_id)))
    
  if ruri.find("delete/barcode")>0:
    barcode_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    product_id = ns.db.barcode(id=barcode_id).product_id 
    if delete_row("barcode", barcode_id, "product", product_id):
      redirect(URL('frm_product/view/product/'+str(product_id)))
        
  if request.post_vars["_formname"]=="barcode/create":
    clear_post_vars()
    if not request.post_vars.has_key("defcode"):
      request.post_vars["defcode"]=0
    else:
      request.post_vars["defcode"]=1
    if len(ns.db((ns.db.barcode.product_id==request.post_vars["product_id"])&(ns.db.barcode.defcode==1)).select())==0:
      request.post_vars["defcode"]=1
    else:
      if request.post_vars["defcode"]==1:
        ns.db((ns.db.barcode.product_id==request.post_vars["product_id"])&(ns.db.barcode.defcode==1)).update(**{"defcode":0})
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.barcode.id==request.post_vars["id"]).update(**request.post_vars)      
      else:
        ns.db.barcode.insert(**request.post_vars)
      setLogtable("update", "log_product_update", "product", request.post_vars["product_id"])
      redirect(URL('frm_product/view/product/'+str(request.post_vars["product_id"])))
    except Exception, err:
      response.flash = str(err)
  
  if ruri.find("event")>0:
    ruri = "frm_event/view"+ruri[ruri.find("frm_product/edit")+16:]
    redirect(URL(ruri))
  
  if ruri.find("new/link")>0:
    product_id = int(request.vars.refnumber)
    product_nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="product")).select().as_list()[0]["id"]
    groups_id = int(request.vars.groups_id)
    groups_nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
    glink = ns.db((ns.db.link.ref_id_1==product_id)&(ns.db.link.nervatype_1==product_nervatype)&(ns.db.link.deleted==0)
              &(ns.db.link.nervatype_2==groups_nervatype)&(ns.db.link.ref_id_2==groups_id)).select().as_list()
    if len(glink)==0:
      values = {"nervatype_1":product_nervatype, "ref_id_1":product_id, "nervatype_2":groups_nervatype, "ref_id_2":groups_id}
      ns.db.link.insert(**values)
    redirect(URL('frm_product/view/product/'+str(product_id)))
    
  if ruri.find("delete/link")>0:
    link_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if delete_row("link",link_id):
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(ruri[:ruri.find("delete/link")-1])
  
  if ruri.find("new/product")>0:
    product_id = -1
  else:
    product_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      
  if ruri.find("delete/product")>0:
    setLogtable("deleted", "log_product_deleted", "product", product_id)
    delete_ini = getSetting("set_trans_deleted")
    if delete_ini != "true":
      values = {"deleted":1}
      ns.db(ns.db.product.id==product_id).update(**values)
    else:
      dfield = deleteFieldValues("product", product_id)
      if dfield!=True:
        session.flash = dfield
        if request.wsgi.environ.has_key("HTTP_REFERER"):
          redirect(request.wsgi.environ["HTTP_REFERER"])
        else:
          redirect(URL('find_product_product'))
      ns.db(ns.db.product.id==product_id).delete()
      ns.db.commit()
    redirect(URL('find_product_product'))  
  
  response.view=dir_view+'/product.html'
  response.titleicon = URL(dir_images,'icon16_parts.png')
  response.icon_deffield = IMG(_src=URL(dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_barcode = IMG(_src=URL(dir_images,'icon16_barcode.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_calendar = IMG(_src=URL(dir_images,'icon16_calendar.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.lo_menu = []
  
  nervatype_product = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="product")).select().as_list()[0]["id"]
  nervatype_groups = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  
  product_audit_filter = get_audit_filter("product", None)[0]
  price_audit_filter = get_audit_filter("price", None)[0]
  
  #basic product data
  ns.db.product.id.readable = ns.db.product.id.writable = False
  ns.db.product.deleted.readable = ns.db.product.deleted.writable = False
  #ns.db.product.protype.requires = IS_IN_DB(ns.db((ns.db.groups.groupname.like('protype'))), ns.db.groups.id, '%(groupvalue)s')
  if product_id>0:
    ns.db.product.protype.writable = False
    form = SQLFORM(ns.db.product, record = product_id, submit_button=T("Save"))
    response.subtitle=T("PRODUCT")
    response.partnumber=ns.db.product(id=product_id).partnumber
    if product_audit_filter!="disabled":
      response.cmd_report = get_report_button(title=T('Product Reports'), url='frm_report_product/'+str(product_id))
    else:
      response.cmd_report = ""
    if product_audit_filter=="all":
      response.cmd_delete = get_command_button(_id="cmd_delete", caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this product?')+
                              "')){window.location ='"+URL("frm_product/delete/product/"+str(product_id))+"';};return false;")
    else:
      response.cmd_delete = ""
    if price_audit_filter!="disabled":
      response.cmd_price = get_command_button(_id="cmd_price", caption=T("Price"),title=T("Show Price"),color="483D8B",
                              _height="30px", _top="4px",
                              cmd="if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
                                  +"')){window.location ='"+URL('find_product_price/view/product/'+str(product_id))+"';};return false;")
      response.cmd_discount = get_command_button(_id="cmd_discount", caption=T("Discount"),title=T("Show Discount"),color="483D8B",
                              _height="30px", _top="4px",
                              cmd="if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
                                  +"')){window.location ='"+URL("find_product_discount/"+str(product_id))+"';};return false;")
    else:
      response.cmd_price = ""
      response.cmd_discount = ""
  else:
    form = SQLFORM(ns.db.product, submit_button=T("Save"))
    form.vars.partnumber = dbfu.nextNumber(ns, {"id":"partnumber", "step":False})
    form.vars.protype = ns.db((ns.db.groups.groupname=="protype")&(ns.db.groups.groupvalue=="item")).select().as_list()[0]["id"]
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
  
  if product_audit_filter in ("disabled"):
    response.cmd_back = get_home_button()
  else:
    response.cmd_back = get_back_button(URL("find_product_product")) 
  response.cmd_help = get_help_button("product")
  
  if product_audit_filter in ("readonly","disabled"):
    form.custom.submit = "" 
          
  if form.validate(keepvalues=True):      
    if product_id==-1:
      nextnumber = dbfu.nextNumber(ns, {"id":"partnumber", "step":False})
      if form.vars.partnumber == nextnumber:
        form.vars.partnumber = dbfu.nextNumber(ns, {"id":"partnumber", "step":True})
      form.vars.id = ns.db.product.insert(**dict(form.vars))
      #add auto deffields
      addnew = ns.db((ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_product)&
                     (ns.db.deffield.addnew==1)).select().as_list()
      for nfield in addnew:
        ns.db.fieldvalue.validate_and_insert(**{"fieldname":nfield["fieldname"],"ref_id":form.vars.id,"value":get_default_value(nfield["fieldtype"])})
      setLogtable("update", "log_product_update", "product", form.vars.id)
      redirect(URL('frm_product/view/product/'+str(form.vars.id)))      
    else:
      ns.db(ns.db.product.id==product_id).update(**form.vars)
      setLogtable("update", "log_product_update", "product", product_id)
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      if str(ns.db.product.fields).find(error)>0:
        flash+=ns.db.product[error].label+": "+form.errors[error]+", "
      else:
        flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  form.custom.widget.webitem = get_bool_input(product_id,"product","webitem")
  form.custom.widget.inactive = get_bool_input(product_id,"product","inactive")
  
  #show product groups list
  if product_id>-1:
    product_groups = ((ns.db.link.ref_id_1==product_id)&(ns.db.link.nervatype_1==nervatype_product)&
            (ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.deleted==0))
    ns.db.link.ref_id_2.represent = lambda value,row: ns._link_id_formatter(ns.db.groups, "groupvalue", value)
    ns.db.link.id.readable = ns.db.link.id.writable = False
    ns.db.link.nervatype_1.readable = ns.db.link.ref_id_1.readable = ns.db.link.nervatype_2.readable = ns.db.link.linktype.readable = ns.db.link.deleted.readable = False
    ns.db.link.ref_id_2.label = T('Groups')
    
    response.view_product_groups = get_tab_grid(product_groups, ns.db.link.id, _fields=None, _editable=False,
                                     _deletable=(product_audit_filter not in ("readonly","disabled")), links=None, 
                                    multi_page="gr_page", rpl_1="/frm_product", rpl_2="/frm_product/view/product/"+str(product_id))
    
    #show add/remove product groups combo and setting button
    if product_audit_filter not in ("readonly","disabled"):
      response.cmb_groups = get_cmb_groups("product")                          
      response.cmd_groups_add = get_icon_button(T('Add to Group'),"cmd_groups_add", 
        cmd="var group_id = document.getElementById('cmb_groups').value;if(group_id!=''){window.location ='"+URL("frm_product/new/link")
        +"?refnumber="+str(product_id)+"&groups_id='+group_id;} else {alert('"+T('Missing Transaction Group!')+"');return false;}")
      response.cmd_groups = get_goprop_button(title=T("Edit Product Groups"), url=URL("frm_groups_product?back=1"))
    else:
      response.cmb_groups = ""
      response.cmd_groups = ""
      response.cmd_groups_add = ""
  
  setting_audit_filter = get_audit_filter("setting", None)[0]
  if setting_audit_filter=="disabled":
    response.cmd_groups = ""
    
  #additional fields data
  if product_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_product)&(ns.db.fieldvalue.ref_id==product_id))
    editable = not product_audit_filter in ("readonly","disabled")
    set_view_fields("product", nervatype_product, 0, editable, fieldvalue, product_id, "/frm_product", "/frm_product/view/product/"+str(product_id))
    
  #barcode data
  if product_id>-1:
    if request.vars.bc_page!=None:
      request.vars.page=request.vars.bc_page
    else:
      request.vars.page=None
    barcode = ((ns.db.barcode.product_id==product_id))
    ns.db.barcode.id.readable = ns.db.barcode.id.writable = False
    ns.db.barcode.product_id.readable = ns.db.barcode.product_id.writable = False
    
    links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_barcode("
                           +str(row["id"])+",'"
                           +json.dumps(str(row["code"]))[1:-1]+"','"
                           +json.dumps(str(row["description"]))[1:-1]+"',"
                           +str(row["barcodetype"])+","
                           +str(row["qty"])+","
                           +str(row["defcode"])+")",
                           _title=T("Edit Barcode"))]
    
    barcode_count = ns.db(barcode).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if product_audit_filter not in ("readonly","disabled"):
      links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this barcode?')+
                              "')){window.location ='"+URL("frm_product/delete/barcode/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Barcode")))
      response.cmd_barcode_submit = get_command_button(caption=T("Save"),title=T("Update barcode data"),color="008B00", _id="cmd_barcode_submit",
                              cmd="barcode_update();return true;")
      response.cmd_barcode_new = get_tabnew_button(barcode_count,T('New Barcode'),cmd_id="cmd_barcode_new",
                                cmd = "$('#tabs').tabs({ selected: 1 });set_barcode(-1,'','','',0,'')") 
    else:
      response.cmd_barcode_submit = ""
      response.cmd_barcode_new = SPAN(" ",SPAN(str(barcode_count), _class="detail_count"))
    
    fields=[ns.db.barcode.id,ns.db.barcode.product_id,ns.db.barcode.defcode,ns.db.barcode.code,ns.db.barcode.barcodetype,
            ns.db.barcode.qty,ns.db.barcode.description]
    response.view_barcode = get_tab_grid(_query=barcode, _field_id=ns.db.barcode.id, _fields=fields, _deletable=False, 
                                         _editable=False ,links=links, multi_page="bc_page", 
                                         rpl_1="/frm_product", rpl_2="/frm_product/view/product/"+str(product_id))
    
    response.barcode_form = SQLFORM(ns.db.barcode, submit_button=T("Save"),_id="frm_barcode")
    response.barcode_form.process()
    response.barcode_icon = URL(dir_images,'icon16_barcode.png')
    response.cmd_barcode_cancel = A(SPAN(_class="icon cross"), _id="cmd_barcode_cancel", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_barcode').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.barcode_id = INPUT(_name="id", _type="hidden", _value="", _id="barcode_id")
    response.barcode_product_id = INPUT(_name="product_id", _type="hidden", _value=product_id, _id="barcode_ref_id")    
  
  #event data
  event_audit_filter = get_audit_filter("event", None)[0]
  if event_audit_filter!="disabled" and product_id>-1:
    event = ((ns.db.event.ref_id==product_id)&(ns.db.event.nervatype==nervatype_product)&(ns.db.event.deleted==0))
    ns.db.event.id.readable = ns.db.event.id.writable = False
    ns.db.event.nervatype.readable = ns.db.event.ref_id.readable = ns.db.event.uid.readable = False
    links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("export2ical?id="+str(row.id)), _target="_blank", _title=T("Export Item"))]
    event_count = ns.db(event).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if (product_audit_filter in ("readonly","disabled")) or (event_audit_filter in ("readonly","disabled")):
      gdeleted = False
      response.cmd_event_new = SPAN(" ",SPAN(str(event_count), _class="detail_count"))
    else:
      gdeleted = True
      response.cmd_event_new = get_tabnew_button(event_count,T('New Event'),cmd_id="tabs-event",url=URL("frm_event/new/event"+"?refnumber="+form.formname))

    response.view_event = get_tab_grid(_query=event, _field_id=ns.db.event.id, _fields=None, _deletable=gdeleted, links=links, 
                             multi_page="ev_page", rpl_1="/frm_product", rpl_2="/frm_product/view/product/"+str(product_id))  
  else:
    response.view_event = ""
    response.event_disabled=True
        
  return dict(form=form)

@ns_auth.requires_login()
def frm_place():
  place_audit_filter = get_audit_filter("setting", None)[0]
  if place_audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    place_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    redirect(URL('frm_place/view/place/'+str(place_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    place_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    if delete_row("fieldvalue", fieldvalue_id, "place", place_id):
      redirect(URL('frm_place/view/place/'+str(place_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.fieldvalue.id==request.post_vars["id"]).validate_and_update(**request.post_vars)      
      else:
        ns.db.fieldvalue.validate_and_insert(**request.post_vars)
      setLogtable("update", "log_place_update", "place", request.post_vars["ref_id"])
      redirect(URL('frm_place/view/place/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
  
  if ruri.find("edit/contact")>0 or ruri.find("view/contact")>0:
    contact_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    place_id = ns.db.contact(id=contact_id).ref_id
    redirect(URL('frm_place/view/place/'+str(place_id)))
    
  if ruri.find("delete/contact")>0:
    contact_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    place_id = ns.db.contact(id=contact_id).ref_id
    if delete_row("contact", contact_id, "place", place_id):
      redirect(URL('frm_place/view/place/'+str(place_id)))
        
  if request.post_vars["_formname"]=="contact/create":
    clear_post_vars()
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.contact.id==request.post_vars["id"]).update(**request.post_vars)      
      else:
        ns.db.contact.insert(**request.post_vars)
      setLogtable("update", "log_place_update", "place", request.post_vars["ref_id"])
      redirect(URL('frm_place/view/place/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
  
  if ruri.find("new/place")>0:
    place_id = -1
    placetype=""
  else:
    place_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    placetype= ns.db((ns.db.groups.id==ns.db.place(id=place_id).placetype)).select().as_list()[0]["groupvalue"]
      
  if ruri.find("delete/place")>0:
    setLogtable("deleted", "log_place_deleted", "place", place_id)
    delete_ini = getSetting("set_trans_deleted")
    if delete_ini != "true":
      values = {"deleted":1}
      ns.db(ns.db.place.id==place_id).update(**values)
    else:
      dfield = deleteFieldValues("place", place_id)
      if dfield!=True:
        session.flash = dfield
        if request.wsgi.environ.has_key("HTTP_REFERER"):
          redirect(request.wsgi.environ["HTTP_REFERER"])
        else:
          redirect(URL('find_place'))
      ns.db(ns.db.place.id==place_id).delete()
      ns.db.commit()
    redirect(URL('find_place'))  
  
  response.view=dir_view+'/place.html'
  response.titleicon = URL(dir_images,'icon16_book.png')
  response.icon_deffield = IMG(_src=URL(dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_contact = IMG(_src=URL(dir_images,'icon16_contact.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.title=T("PLACE")
  response.lo_menu = []
  
  nervatype_place = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="place")).select().as_list()[0]["id"]
  
  #basic place data
  if placetype not in ("bank", "cash"):
    ns.db.place.curr.readable = ns.db.place.curr.writable = False
  else:
    ns.db.place.curr.requires = IS_IN_DB(ns.db(ns.db.currency), ns.db.currency.curr, '%(curr)s')
  ns.db.place.deleted.readable = ns.db.place.deleted.writable = False
  ns.db.place.description.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
  if place_id>0:
    ns.db.place.placetype.writable = False
    form = SQLFORM(ns.db.place, record = place_id, submit_button=T("Save"))
    response.subtitle=ns.db.place(id=place_id).planumber
    if place_audit_filter!="disabled":
      response.cmd_report = get_report_button(title=T('Place Reports'), url='frm_report_place/'+str(place_id))
    else:
      response.cmd_report = ""
    if place_audit_filter=="all":
      response.cmd_delete = get_command_button(_id="cmd_delete", caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this place?')+
                              "')){window.location ='"+URL("frm_place/delete/place/"+str(place_id))+"';};return false;")
    else:
      response.cmd_delete = ""
    address = ns.db((ns.db.address.deleted==0)&(ns.db.address.nervatype==nervatype_place)&(ns.db.address.ref_id==place_id)).select()
    if len(address)>0:
      address_id = address[0].id
    else:
      address_id = ns.db.address.insert(**{"nervatype":nervatype_place,"ref_id":place_id})
  else:
    form = SQLFORM(ns.db.place, submit_button=T("Save"))
    form.vars.planumber = dbfu.nextNumber(ns, {"id":"planumber", "step":False})
    form.vars.placetype = ns.db((ns.db.groups.groupname=="placetype")&(ns.db.groups.groupvalue=="bank")).select().as_list()[0]["id"]
    response.subtitle=T('New place')
    response.serial=""
    response.cmd_report = ""
    response.cmd_delete = ""
    address_id=None
      
  if place_audit_filter in ("disabled"):
    response.cmd_back = get_home_button()
  else:
    response.cmd_back = get_back_button(URL("find_place")) 
  response.cmd_help = get_help_button("place")
  
  if place_audit_filter in ("readonly","disabled"):
    form.custom.submit = "" 
  
  if form.validate(keepvalues=True):   
    if place_id==-1:
      nextnumber = dbfu.nextNumber(ns, {"id":"planumber", "step":False})
      if form.vars.planumber == nextnumber:
        form.vars.planumber = dbfu.nextNumber(ns, {"id":"planumber", "step":True})
      form.vars.id = ns.db.place.insert(**dict(form.vars))
      
      ns.db.address.insert(**{"nervatype":nervatype_place,"ref_id":form.vars.id,"zipcode":request.post_vars.zipcode,
                            "city":request.post_vars.city,"street":request.post_vars.street})
      
      #add auto deffields
      addnew = ns.db((ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_place)&
                     (ns.db.deffield.addnew==1)).select().as_list()
      for nfield in addnew:
        ns.db.fieldvalue.validate_and_insert(**{"fieldname":nfield["fieldname"],"ref_id":form.vars.id,"value":get_default_value(nfield["fieldtype"])})
      setLogtable("update", "log_place_update", "place", form.vars.id)
      redirect(URL('frm_place/view/place/'+str(form.vars.id)))      
    else:
      ns.db(ns.db.place.id==place_id).update(**form.vars)
      ns.db((ns.db.address.ref_id==place_id)&(ns.db.address.nervatype==nervatype_place)).update(**{
                "zipcode":request.post_vars.zipcode,"city":request.post_vars.city,"street":request.post_vars.street})
      setLogtable("update", "log_place_update", "place", place_id)
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
    
  form.custom.widget.inactive = get_bool_input(place_id,"place","inactive")
  if address_id:
    response.zipcode = INPUT(_name="zipcode", _type="text", _value=str(ns.db.address(id=address_id).zipcode), _id="address_zipcode", _class="string")
    response.city = INPUT(_name="city", _type="text", _value=str(ns.db.address(id=address_id).city), _id="address_city", _class="string")
    response.street = INPUT(_name="street", _type="text", _value=str(ns.db.address(id=address_id).street), _id="address_street", _class="string")
  else:
    response.zipcode = INPUT(_name="zipcode", _type="text", _value="", _id="address_zipcode", _class="string")
    response.city = INPUT(_name="city", _type="text", _value="", _id="address_city", _class="string")
    response.street = INPUT(_name="street", _type="text", _value="", _id="address_street", _class="string")
  
  #additional fields data
  if place_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_place)&(ns.db.fieldvalue.ref_id==place_id))
    editable = not (place_audit_filter in ("readonly","disabled"))
    set_view_fields("place", nervatype_place, 0, editable, fieldvalue, place_id, "/frm_place", "/frm_place/view/place/"+str(place_id))
  
  #contact data
  if place_id>-1:
    if request.vars.ct_page!=None:
      request.vars.page=request.vars.ct_page
    else:
      request.vars.page=None
    contact = ((ns.db.contact.ref_id==place_id)&(ns.db.contact.nervatype==nervatype_place)&(ns.db.contact.deleted==0))
    ns.db.contact.nervatype.readable = ns.db.contact.ref_id.readable = ns.db.contact.deleted.readable = False
    ns.db.contact.id.label = T("No.")
    ns.db.contact.id.represent = lambda value,row: formatInteger(row["id"])
    
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
    
    contact_count = ns.db(contact).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if place_audit_filter in ("readonly","disabled"):
      response.cmd_contact_submit = ""
      response.cmd_contact_new = SPAN(" ",SPAN(str(contact_count), _class="detail_count"))
    else:
      links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this contact?')+
                              "')){window.location ='"+URL("frm_place/delete/contact/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Contact")))
      response.cmd_contact_submit = get_command_button(caption=T("Save"),title=T("Update contact data"),color="008B00", _id="cmd_contact_submit",
                              cmd="contact_update();return true;")
      response.cmd_contact_new = get_tabnew_button(contact_count,T('New Contact'),cmd_id="cmd_contact_new",
                                cmd = "$('#tabs').tabs({ selected: 1 });set_contact(-1,'','','','','','','','')")
  
    response.view_contact = get_tab_grid(_query=contact, _field_id=ns.db.contact.id, _fields=None, _deletable=False, _editable=False, links=links, 
                               multi_page="ct_page", rpl_1="/frm_place", rpl_2="/frm_place/view/place/"+str(place_id))
    
    response.contact_form = SQLFORM(ns.db.contact, submit_button=T("Save"),_id="frm_contact")
    response.contact_form.process()
    response.contact_icon = URL(dir_images,'icon16_contact.png')
    response.cmd_contact_cancel = A(SPAN(_class="icon cross"), _id="cmd_contact_cancel", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_contact').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
    response.contact_id = INPUT(_name="id", _type="hidden", _value="", _id="contact_id")
    response.contact_ref_id = INPUT(_name="ref_id", _type="hidden", _value=place_id, _id="contact_ref_id")
    response.contact_nervatype = INPUT(_name="nervatype", _type="hidden", _value=nervatype_place, _id="contact_nervatype")  
        
  return dict(form=form)
    
@ns_auth.requires_login()
def frm_employee():
  audit_filter = get_audit_filter("employee", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    employee_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    redirect(URL('frm_employee/view/employee/'+str(employee_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    employee_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    if delete_row("fieldvalue", fieldvalue_id, "employee", employee_id):
      redirect(URL('frm_employee/view/employee/'+str(employee_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.fieldvalue.id==request.post_vars["id"]).validate_and_update(**request.post_vars)      
      else:
        ns.db.fieldvalue.validate_and_insert(**request.post_vars)
      setLogtable("update", "log_employee_update", "employee", request.post_vars["ref_id"])
      redirect(URL('frm_employee/view/employee/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
  
  if ruri.find("event")>0:
    ruri = "frm_event/view"+ruri[ruri.find("frm_employee/edit")+17:]
    redirect(URL(ruri))
  
  if ruri.find("new/employee")>0:
    employee_id = -1
  else:
    employee_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      
  if ruri.find("delete/employee")>0:
    setLogtable("deleted", "log_employee_deleted", "employee", employee_id)
    delete_ini = getSetting("set_trans_deleted")
    if delete_ini != "true":
      values = {"deleted":1}
      ns.db(ns.db.employee.id==employee_id).update(**values)
    else:
      dfield = deleteFieldValues("employee", employee_id)
      if dfield!=True:
        session.flash = dfield
        if request.wsgi.environ.has_key("HTTP_REFERER"):
          redirect(request.wsgi.environ["HTTP_REFERER"])
        else:
          redirect(URL('find_employee_employee'))
      ns.db(ns.db.employee.id==employee_id).delete()
      ns.db.commit()
    redirect(URL('find_employee_employee'))  
  
  response.view=dir_view+'/employee.html'
  response.titleicon = URL(dir_images,'icon16_user.png')
  response.icon_deffield = IMG(_src=URL(dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_calendar = IMG(_src=URL(dir_images,'icon16_calendar.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.lo_menu = []
  
  nervatype_employee = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="employee")).select().as_list()[0]["id"]
  employee_audit_filter = get_audit_filter("employee", None)[0]
  setting_audit_filter = get_audit_filter("setting", None)[0]
  
  #basic employee data
  ns.db.employee.deleted.readable = ns.db.employee.deleted.writable = False
  ns.db.address.street.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
  if employee_id>0:
    employee = ns.db.employee(id=employee_id)
    contact = ns.db((ns.db.contact.ref_id==employee_id)&(ns.db.contact.nervatype==nervatype_employee)&(ns.db.contact.deleted==0)).select().as_list()
    if len(contact)>0:
      contact = contact[0]
    else:
      contact=None
    address = ns.db((ns.db.address.ref_id==employee_id)&(ns.db.address.nervatype==nervatype_employee)&(ns.db.address.deleted==0)).select().as_list()
    if len(address)>0:
      address = address[0]
    else:
      address=None
    response.subtitle=T('EMPLOYEE')
    response.empnumber = ns.db.employee(id=employee_id).empnumber
    if employee_audit_filter!="disabled":
      response.cmd_report = get_report_button(title=T('Employee Reports'), url='frm_report_employee/'+str(employee_id))
    else:
      response.cmd_report = ""
    if employee_audit_filter=="all":
      response.cmd_delete = get_command_button(_id="cmd_delete", caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this employee?')+
                              "')){window.location ='"+URL("frm_employee/delete/employee/"+str(employee_id))+"';};return false;")
    else:
      response.cmd_delete = ""
    if employee_audit_filter not in ("readonly","disabled"):
      response.cmd_password = get_command_button(_id="cmd_password", caption=T("Change password"),title=T("Change password"),color="483D8B",
                              _height="30px", _top= "4px",
                              cmd="if(confirm('"+T("Any unsaved changes will be lost. Do you want to continue?")
                                  +"')){window.location ='"+URL("change_password/"+str(employee_id))+"';};return false;")
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
  form = SQLFORM.factory(*fields,submit_button=T("Save"),table_name="employee")
  if employee==None:
    form.vars.empnumber = dbfu.nextNumber(ns, {"id":"empnumber", "step":False})
    form.vars.usergroup = ns.db((ns.db.groups.groupname=="usergroup")&(ns.db.groups.groupvalue=="admin")).select().as_list()[0]["id"]
  else:
    for fvalue in fvalues.items():
      if fvalue[1]!=None:
        form.vars[fvalue[0]]=fvalue[1]
  form.process(keepvalues=True,onfailure=None)
  form.errors.clear()
  
  if employee_audit_filter in ("disabled"):
    response.cmd_back = get_home_button()
  else:
    response.cmd_back = get_back_button(URL("find_employee_employee"))
  response.cmd_help = get_help_button("employee")
  
  if employee_audit_filter in ("readonly","disabled"):
    form.custom.submit = "" 
    
  if len(request.post_vars)>0:
    employee_values={}
    contact_values={}
    address_values={}
    for value_key in form.vars.keys():
      if value_key!="id":
        if str(ns.db.employee.fields).find(value_key)>0:
          employee_values[value_key]=form.vars[value_key]
        elif str(ns.db.contact.fields).find(value_key)>0:
          contact_values[value_key]=form.vars[value_key]
        elif str(ns.db.address.fields).find(value_key)>0:
          address_values[value_key]=form.vars[value_key]
    if employee_id==-1:
      empnumber = dbfu.nextNumber(ns, {"id":"empnumber", "step":False})
      if employee_values.has_key("empnumber"):
        if employee_values["empnumber"] == empnumber:
          employee_values["empnumber"] = dbfu.nextNumber(ns, {"id":"empnumber", "step":True})
      if employee_values.has_key("username"):
        if employee_values["username"]=="":
          del employee_values["username"]
      errnum=0
      if len(employee_values)>0:
        ret = ns.db.employee.validate_and_insert(**employee_values)
        if len(ret.errors.keys())>0:
          errnum=1
          flash=""
          for error in form.errors.keys():
            if str(ns.db.employee.fields).find(error)>0:
              flash+=ns.db.employee[error].label+": "+form.errors[error]+", "
            else:
              flash+=error+": "+form.errors[error]+", "
          response.flash = T('Form has errors: ')+flash
      if len(contact_values)>0 and errnum==0:
        employee_id = ret.id
        contact_values["nervatype"]=nervatype_employee
        contact_values["ref_id"]=employee_id
        ret = ns.db.contact.validate_and_insert(**contact_values)
        if len(ret.errors.keys())>0:
          errnum=1
          flash=""
          for error in form.errors.keys():
            if str(ns.db.contact.fields).find(error)>0:
              flash+=ns.db.contact[error].label+": "+form.errors[error]+", "
            else:
              flash+=error+": "+form.errors[error]+", "
          response.flash = T('Form has errors: ')+flash
      if len(address_values)>0 and errnum==0:
        address_values["nervatype"]=nervatype_employee
        address_values["ref_id"]=employee_id
        ret = ns.db.address.validate_and_insert(**address_values)
        if len(ret.errors.keys())>0:
          flash=""
          for error in form.errors.keys():
            if str(ns.db.address.fields).find(error)>0:
              flash+=ns.db.address[error].label+": "+form.errors[error]+", "
            else:
              flash+=error+": "+form.errors[error]+", "
          response.flash = T('Form has errors: ')+flash
        else:
          session.flash = 'Success!'
          setLogtable("update", "log_employee_update", "employee", form.vars.id)
          redirect(URL('frm_employee/view/employee/'+str(employee_id)))      
    else:
      if employee_values.has_key("username"):
        if (employee_values["username"]=="" and (ns.db.employee[employee_id]["username"]==None)) \
          or employee_values["username"]==ns.db.employee[employee_id]["username"]:
          del employee_values["username"]
      if employee_values.has_key("empnumber"):
        if employee_values["empnumber"]==ns.db.employee[employee_id]["empnumber"]:
          del employee_values["empnumber"]
      errnum=0
      if len(employee_values)>0:
        ret = ns.db(ns.db.employee.id==employee_id).validate_and_update(**employee_values)
        if len(ret.errors.keys())>0:
          errnum=1
          flash=""
          for error in form.errors.keys():
            if str(ns.db.employee.fields).find(error)>0:
              flash+=ns.db.employee[error].label+": "+form.errors[error]+", "
            else:
              flash+=error+": "+form.errors[error]+", "
          response.flash = T('Form has errors: ')+flash
      if len(contact_values)>0 and errnum==0:
        ret = ns.db((ns.db.contact.nervatype==nervatype_employee)&(ns.db.contact.ref_id==employee_id)).validate_and_update(**contact_values)
        if len(ret.errors.keys())>0:
          errnum=1
          flash=""
          for error in form.errors.keys():
            if str(ns.db.contact.fields).find(error)>0:
              flash+=ns.db.contact[error].label+": "+form.errors[error]+", "
            else:
              flash+=error+": "+form.errors[error]+", "
          response.flash = T('Form has errors: ')+flash
      if len(address_values)>0 and errnum==0:
        ret = ns.db((ns.db.address.nervatype==nervatype_employee)&(ns.db.address.ref_id==employee_id)).validate_and_update(**address_values)
        if len(ret.errors.keys())>0:
          flash=""
          for error in form.errors.keys():
            if str(ns.db.address.fields).find(error)>0:
              flash+=ns.db.address[error].label+": "+form.errors[error]+", "
            else:
              flash+=error+": "+form.errors[error]+", "
          response.flash = T('Form has errors: ')+flash
        setLogtable("update", "log_employee_update", "employee", employee_id)
        response.flash = T('Success!')
  
  form.custom.widget.inactive = get_bool_input(employee_id,"employee","inactive")                            
  
  if (employee_audit_filter in ("readonly","disabled")) or (setting_audit_filter in ("disabled")):
    response.cmd_department = ""
    response.cmd_usergroup = ""
  else:
    response.cmd_department = get_goprop_button(title=T("Edit Departments"), url=URL("frm_groups_department?back=1"))
    response.cmd_usergroup = get_goprop_button(title=T("Edit Usergroups"), url=URL("frm_groups_usergroup?back=1"))
    
  #additional fields data
  if employee_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_employee)&(ns.db.fieldvalue.ref_id==employee_id))
    editable = not employee_audit_filter in ("readonly","disabled")
    set_view_fields("employee", nervatype_employee, 0, editable, fieldvalue, employee_id, "/frm_employee", "/frm_employee/view/employee/"+str(employee_id))
  
  #event data
  event_audit_filter = get_audit_filter("event", None)[0]
  if event_audit_filter!="disabled" and employee_id>-1:
    event = ((ns.db.event.ref_id==employee_id)&(ns.db.event.nervatype==nervatype_employee)&(ns.db.event.deleted==0))
    ns.db.event.id.readable = ns.db.event.id.writable = False
    ns.db.event.nervatype.readable = ns.db.event.ref_id.readable = ns.db.event.uid.readable = False
    links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("export2ical?id="+str(row.id)), _target="_blank", _title=T("Export Item"))]
    event_count = ns.db(event).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if employee_audit_filter in ("readonly","disabled") or event_audit_filter in ("readonly","disabled"):
      gdeleted = False
      response.cmd_event_new = SPAN(" ",SPAN(str(event_count), _class="detail_count"))
    else:
      gdeleted = True
      response.cmd_event_new = get_tabnew_button(event_count,T('New Event'),cmd_id="tabs-event",url=URL("frm_event/new/event")+"?refnumber=employee/"+str(employee_id))
    
    response.view_event = get_tab_grid(_query=event, _field_id=ns.db.event.id, _fields=None, _deletable=gdeleted, links=links, 
                             multi_page="ev_page", rpl_1="/frm_employee", rpl_2="/frm_employee/view/employee/"+str(employee_id))
  else:
    response.view_event = ""
    response.event_disabled=True
      
  return dict(form=form)

@ns_auth.requires_login()
def frm_tool():
  audit_filter = get_audit_filter("tool", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    tool_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    redirect(URL('frm_tool/view/tool/'+str(tool_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    tool_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    if delete_row("fieldvalue", fieldvalue_id, "tool", tool_id):
      redirect(URL('frm_tool/view/tool/'+str(tool_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.fieldvalue.id==request.post_vars["id"]).validate_and_update(**request.post_vars)      
      else:
        ns.db.fieldvalue.validate_and_insert(**request.post_vars)
      setLogtable("update", "log_tool_update", "tool", request.post_vars["ref_id"])
      redirect(URL('frm_tool/view/tool/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
  
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
      
  if ruri.find("delete/tool")>0:
    setLogtable("deleted", "log_tool_deleted", "tool", tool_id)
    delete_ini = getSetting("set_trans_deleted")
    if delete_ini != "true":
      values = {"deleted":1}
      ns.db(ns.db.tool.id==tool_id).update(**values)
    else:
      dfield = deleteFieldValues("tool", tool_id)
      if dfield!=True:
        session.flash = dfield
        if request.wsgi.environ.has_key("HTTP_REFERER"):
          redirect(request.wsgi.environ["HTTP_REFERER"])
        else:
          redirect(URL('find_tool_tool'))
      ns.db(ns.db.tool.id==tool_id).delete()
      ns.db.commit()
    redirect(URL('find_tool_tool'))  
  
  response.view=dir_view+'/tool.html'
  response.titleicon = URL(dir_images,'icon16_wrench.png')
  response.icon_deffield = IMG(_src=URL(dir_images,'icon16_deffield.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_calendar = IMG(_src=URL(dir_images,'icon16_calendar.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.icon_wrench_page = IMG(_src=URL(dir_images,'icon16_wrench_page.png'),_style="vertical-align: top;",_height="16px",_width="16px")
  response.lo_menu = []
  
  nervatype_tool = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="tool")).select().as_list()[0]["id"]
  tool_audit_filter = get_audit_filter("tool", None)[0]
  setting_audit_filter = get_audit_filter("setting", None)[0]
  
  #basic tool data
  ns.db.tool.id.readable = ns.db.tool.id.writable = False
  ns.db.tool.deleted.readable = ns.db.tool.deleted.writable = False
  ns.db.tool.description.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
  ns.db.tool.product_id.writable = False
  if tool_id>0:
    form = SQLFORM(ns.db.tool, record = tool_id, submit_button=T("Save"))
    response.subtitle=T("TOOL")
    response.serial=ns.db.tool(id=tool_id).serial
    if tool_audit_filter!="disabled":
      response.cmd_report = get_report_button(title=T('Tool Reports'), url='frm_report_tool/'+str(tool_id))
    else:
      response.cmd_report = ""
    if tool_audit_filter=="all":
      response.cmd_delete = get_command_button(_id="cmd_delete", caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this tool?')+
                              "')){window.location ='"+URL("frm_tool/delete/tool/"+str(tool_id))+"';};return false;")
    else:
      response.cmd_delete = ""
  else:
    form = SQLFORM(ns.db.tool, submit_button=T("Save"))
    form.vars.serial = dbfu.nextNumber(ns, {"id":"serial", "step":False})
    response.subtitle=T('NEW TOOL')
    response.serial=""
    response.cmd_report = ""
    response.cmd_delete = ""
      
  if tool_audit_filter in ("disabled"):
    response.cmd_back = get_home_button()
  else:
    response.cmd_back = get_back_button(URL("find_tool_tool")) 
  response.cmd_help = get_help_button("tool")
  
  if tool_audit_filter in ("readonly","disabled"):
    form.custom.submit = "" 
          
  if form.validate(keepvalues=True):
    if request.post_vars.product_id=="":
      response.product_control = get_product_selector(T('Missing product name!'), width="97%", error_label=True)
      response.flash = T('Missing product name!')
    else:
      form.vars.product_id = request.post_vars.product_id     
      if tool_id==-1:
        nextnumber = dbfu.nextNumber(ns, {"id":"serial", "step":False})
        if form.vars.serial == nextnumber:
          form.vars.serial = dbfu.nextNumber(ns, {"id":"serial", "step":True})
        form.vars.id = ns.db.tool.insert(**dict(form.vars))
        #add auto deffields
        addnew = ns.db((ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_tool)&
                       (ns.db.deffield.addnew==1)).select().as_list()
        for nfield in addnew:
          ns.db.fieldvalue.validate_and_insert(**{"fieldname":nfield["fieldname"],"ref_id":form.vars.id,"value":get_default_value(nfield["fieldtype"])})
        setLogtable("update", "log_tool_update", "tool", form.vars.id)
        redirect(URL('frm_tool/view/tool/'+str(form.vars.id)))      
      else:
        ns.db(ns.db.tool.id==tool_id).update(**form.vars)
        setLogtable("update", "log_tool_update", "tool", tool_id)
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
  response.product_id = INPUT(_name="product_id", _type="hidden", _value=product_id, _id="product_id")
  if response.product_control==None:
    response.product_control = get_product_selector(product_description, width="97%",protype="item")
    
  form.custom.widget.inactive = get_bool_input(tool_id,"tool","inactive")
  
  #show tool groups list
  if (tool_audit_filter not in ("readonly","disabled")) and (setting_audit_filter not in ("disabled")):
    response.cmd_groups = get_goprop_button(title=T("Edit Tool Groups"), url=URL("frm_groups_toolgroup?back=1"))  
  else:
    response.cmd_groups = ""
  
  #additional fields data
  if tool_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_tool)&(ns.db.fieldvalue.ref_id==tool_id))
    editable = not (tool_audit_filter in ("readonly","disabled"))
    set_view_fields("tool", nervatype_tool, 0, editable, fieldvalue, tool_id, "/frm_tool", "/frm_tool/view/tool/"+str(tool_id))
    
  #event data
  event_audit_filter = get_audit_filter("event", None)[0]
  if event_audit_filter!="disabled" and tool_id>-1:
    if request.vars.ev_page!=None:
      request.vars.page=request.vars.ev_page
    else:
      request.vars.page=None
    event = ((ns.db.event.ref_id==tool_id)&(ns.db.event.nervatype==nervatype_tool)&(ns.db.event.deleted==0))
    ns.db.event.id.readable = ns.db.event.id.writable = False
    ns.db.event.nervatype.readable = ns.db.event.ref_id.readable = ns.db.event.uid.readable = False
    links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href=URL("export2ical?id="+str(row.id)), _target="_blank", _title=T("Export Item"))]
  
    event_count = ns.db(event).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if tool_audit_filter in ("readonly","disabled") or event_audit_filter in ("readonly","disabled"):
      gdeleted = False
      response.cmd_event_new = SPAN(" ",SPAN(str(event_count), _class="detail_count"))
    else:
      gdeleted = True
      response.cmd_event_new = get_tabnew_button(event_count,T('New Event'),cmd_id="tabs-event",url=URL("frm_event/new/event")+"?refnumber="+form.formname)
    
    response.view_event = get_tab_grid(_query=event, _field_id=ns.db.event.id, _fields=None, _deletable=gdeleted, links=links, 
                             multi_page="ev_page", rpl_1="/frm_tool", rpl_2="/frm_tool/view/tool/"+str(tool_id))
  else:
    response.view_event = ""
    response.event_disabled=True
  
  #trans data
  waybill_audit_filter = get_audit_filter("trans", "waybill")[0]
  if waybill_audit_filter!="disabled" and tool_id>-1:
    transtype_waybill = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="waybill")).select().as_list()[0]["id"]
    ns.db.movement.notes.label = T('Additional info')
    ns.db.movement.trans_id.label = T('Movement No.')
    query = ((ns.db.trans.deleted==0)&(ns.db.trans.id==ns.db.movement.trans_id)&(ns.db.movement.tool_id==tool_id)
             &(ns.db.trans.transtype==transtype_waybill))
    fields = [ns.db.movement.trans_id, ns.db.trans.crdate,ns.db.trans.direction,
                ns.db.movement.shippingdate,ns.db.tool.description,ns.db.movement.notes,
                ns.db.trans.transtate]
    
    trans_count = ns.db(query).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    if waybill_audit_filter!="all":
      gdeleted = False
      response.cmd_waybill_new = SPAN(" ",SPAN(str(trans_count), _class="detail_count"))
    else:
      gdeleted = True
      response.cmd_waybill_new = get_tabnew_button(trans_count,T('New Movement'),cmd_id="", 
                                      cmd="javascript:window.open('"+URL("frm_trans/new/trans/waybill/out")+"', '_blank');")
        
    response.view_trans = get_tab_grid(query, ns.db.trans.id, _fields=fields, _deletable=False, _editable=False, links=None, 
                                          multi_page="too_page", rpl_1="/frm_tool", rpl_2="/frm_tool/view/tool/"+str(tool_id))
  else:
    response.view_trans = ""
    response.waybill_disabled=True
        
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
    return base64.b64encode(dbfu.getReport(ns, params, filters)["template"])
  
  if request.vars.has_key("delete_rows"):
    if request.vars.has_key("rows"):
      rows = request.vars.rows.split("|")
      for row in rows:
        row = row.split(",")
        ns.db(ns.db.ui_printqueue.id==row[0]).delete()
      ns.db.commit()
    return "OK"
      
  if ruri.find("delete/ui_printqueue")>0:
    queue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    ns.db(ns.db.ui_printqueue.id==queue_id).delete()
    ns.db.commit()
  
  filter_form = SQLFORM.factory(
    Field('nervatype', "string", label=T('Type'), 
              requires = IS_EMPTY_OR(IS_IN_SET(["customer","product","employee","tool","project","order","offer","invoice",
                                                "receipt","rent","worksheet","delivery","inventory","waybill","production",
                                                "formula","bank","cash"]))),
    Field('transnumber', type='string', length=50, label=T('Doc.No.'), default=""),
    Field('fromdate', type='date', label=T('From Date')),
    Field('enddate', type='date', label=T('End Date')),
    Field('username', type='string', length=50, label=T('Username'), default=""),
    submit_button=T("Filter"), table_name="filter", _id="frm_print_filter"
  )
  
  errors={}
  query = (ns.db.ui_printqueue.id>0)
  if len(request.post_vars)>0:
    if request.post_vars.nervatype!="":
      if request.post_vars.nervatype in("order","offer","invoice","receipt","rent","worksheet","delivery","inventory","waybill","production","formula","bank","cash"):
        nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
        transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue==request.post_vars.nervatype)).select().as_list()[0]["id"]
        query= query&(ns.db.ui_printqueue.nervatype==nervatype_id)&(ns.db.ui_printqueue.ref_id==ns.db.trans.id)&(ns.db.trans.transtype==transtype_id)
      else:
        nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue==request.post_vars.nervatype)).select().as_list()[0]["id"]
        query= query&(ns.db.ui_printqueue.nervatype==nervatype_id)
      filter_form.vars.nervatype=request.post_vars.nervatype
    if request.post_vars.transnumber!="":
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
    if request.post_vars.fromdate!="":
      query= query&(ns.db.ui_printqueue.crdate>=datetime.datetime.strptime(request.post_vars.fromdate, str('%Y-%m-%d')))
      filter_form.vars.fromdate=request.post_vars.fromdate
    if request.post_vars.enddate!="":
      query= query&(ns.db.ui_printqueue.crdate<=datetime.datetime.strptime(request.post_vars.enddate, str('%Y-%m-%d')))
      filter_form.vars.enddate=request.post_vars.enddate
    if request.post_vars.username!="":
      query= query&(ns.db.ui_printqueue.employee_id==ns.db.employee.id)&(ns.db.employee.username==request.post_vars.username)
      filter_form.vars.username=request.post_vars.username
  
  #set transfilter
  query = set_transfilter(query,ns.db.ui_printqueue,"employee_id")
    
  if request.vars.has_key("print_selected"):
    if request.vars.selected_row!=None:
      if request.vars.printer_type in("local","export"):
        print_selected = []
        [print_selected.append(int(id_row)) for id_row in request.vars.selected_row]
        print_filter = ns.db(ns.db.ui_printqueue.id.belongs(print_selected)).select()
        print_selected = []
        [print_selected.append([int(id_row.id),int(id_row.report_id),int(id_row.ref_id),int(id_row.qty),
                                re.sub(r'[^0-9a-zA-Z]+','_',ns.show_refnumber("refnumber", ns.db.groups(id=id_row.nervatype).groupvalue, id_row.ref_id))]
                               ) for id_row in print_filter]
        return str(print_selected)[1:-1].replace("], [", "|").replace("[", "").replace("]", "").replace(" ", "")
      print_result = dbfu.printQueue(ns, request.vars.printer, request.vars.selected_row, request.vars.orientation, request.vars.size)
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
                              re.sub(r'[^0-9a-zA-Z]+','_',ns.show_refnumber("refnumber", ns.db.groups(id=id_row.nervatype).groupvalue, id_row.ref_id))]
                             ) for id_row in print_filter]
      return str(print_selected)[1:-1].replace("], [", "|").replace("[", "").replace("]", "").replace(" ", "")
    [print_selected.append(id_row.id) for id_row in print_filter]
    print_result = dbfu.printQueue(ns, request.vars.printer, print_selected, request.vars.orientation, request.vars.size)
    if not print_result["state"]:
      response.flash = print_result["error_message"]
  else:
    if filter_form.validate(keepvalues=True):
      pass
    for error in errors.keys():
      filter_form.errors[error] = errors[error]
  
  response.subtitle=T('PRINTER QUEUE')
  response.view=dir_view+'/printqueue.html'
  response.titleicon = URL(dir_images,'icon16_printer.png')
  response.cmd_back = get_home_button()
  response.cmd_help = get_help_button("printqueue")

  response.lo_menu = []
  printer_clienthost = getSetting("printer_clienthost")
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
  
  printers = ns.db((ns.db.groups.groupname=="printer")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.id).as_list()
  response.cmb_printers = SELECT(*[OPTION(field["groupvalue"], _value=field["groupvalue"], 
                                          _selected=(field["groupvalue"]==getSetting("default_printer"))) for field in printers], 
                                 _id="cmb_printers", _name="printer",_style="width: 100%;height: 28px;")
  
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
      
  ns.db.ui_printqueue.id.readable = ns.db.ui_printqueue.id.writable = False
  fields = [ns.db.ui_printqueue.id, ns.db.ui_printqueue.nervatype, ns.db.ui_printqueue.ref_id, ns.db.ui_printqueue.qty, 
            ns.db.ui_printqueue.crdate, ns.db.ui_printqueue.employee_id, ns.db.ui_printqueue.report_id]
  links = [lambda row: INPUT(_type='checkbox', _name='selected_row', _value=row.id)]
  view_printqueue = SQLFORM.grid(query=query, field_id=ns.db.ui_printqueue.id, fields=fields, #headers=headers,
                 orderby=ns.db.ui_printqueue.id, sortable=True, paginate=25, maxtextlength=25,
                 searchable=False, csv=False, details=False, showbuttontext=False,
                 create=False, deletable=True, editable=False, selectable=False, links=links, user_signature=False)
  if type(view_printqueue[1][0][0]).__name__!="TABLE":
    view_printqueue = ""
  else:
    view_printqueue=move_buttons(view_printqueue)
  
  return dict(form=filter_form, view_printqueue=view_printqueue)

def init_sfilter(sfilter_name):
  if not session[sfilter_name]:
    session[sfilter_name] = {}
  if len(request.post_vars)>0:
    if len(session[sfilter_name])==0:
      empty_post = True
    else:
      empty_post = False
    session[sfilter_name]["bool_filter_value"]=request.post_vars.bool_filter_value
    for filter_key in request.post_vars.keys():
      if request.post_vars[filter_key] and request.post_vars[filter_key]!="":
        empty_post = False
      if filter_key in("date_filter_value_1","date_filter_value_2","date_filter_value_3"):
        try:
          dt = str(request.post_vars[filter_key]).split("-")
          session[sfilter_name][filter_key] = datetime.date(int(dt[0]), int(dt[1]), int(dt[2]))
        except:
          session[sfilter_name][filter_key] = None
      else:
        session[sfilter_name][filter_key]=request.post_vars[filter_key]
    if empty_post:
      session[sfilter_name] = {}
      
def create_filter_form(sfilter_name,state_fields=None,bool_fields=None,date_fields=None,number_fields=None,data_fields=None,quick_total=None,more_data=None):
  
  if sfilter_name not in("transitem_trans_filter","payment_payment_filter","payment_invoice_filter","movement_inventory_filter","movement_product_filter","movement_formula_filter"):
    init_sfilter(sfilter_name)
      
  filter_fields=[]
  if state_fields:
    if str(state_fields).find("nervatype")>-1:
      filter_fields.append(Field('nervatype', "string", label=T('Ref.type'), default = session[sfilter_name].get("nervatype"),
           requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('nervatype')), ns.db.groups.id, '%(groupvalue)s')))
      
    if str(state_fields).find("transtype")>-1:
      filter_fields.append(Field('transtype', "string", label=T('Doc.Type'), default = session[sfilter_name].get("transtype"),
           requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('transtype')
           &ns.db.groups.groupvalue.belongs(("offer","order","worksheet","rent","invoice","receipt"))), 
           ns.db.groups.id, '%(groupvalue)s')))
    
    if str(state_fields).find("paymtype")>-1:
      filter_fields.append(Field('transtype', "string", label=T('Doc.Type'), default = session[sfilter_name].get("transtype"),
           requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('transtype')
           &ns.db.groups.groupvalue.belongs(("cash","bank"))), 
           ns.db.groups.id, '%(groupvalue)s')))
      
    if str(state_fields).find("direction")>-1:
      filter_fields.append(Field('direction', "string", label=T('Direction'), default = session[sfilter_name].get("direction"),
           requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('direction')), ns.db.groups.id, '%(groupvalue)s')))
    
    if str(state_fields).find("transtate")>-1:
      filter_fields.append(Field('transtate', "string", label=T('State'), default = session[sfilter_name].get("transtate"),
           requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('transtate')), ns.db.groups.id, '%(groupvalue)s')))
    
    if str(state_fields).find("transcast")>-1:
      transcast = str(ns.db.deffield(fieldname="trans_transcast").valuelist).split("|")
      transcast_label=[]
      for value in transcast:
        transcast_label.append(T(value))
      filter_fields.append(Field('transcast', "string", label=T('Doc.State'), default = session[sfilter_name].get("transcast"),
           requires = IS_IN_SET(transcast_label,transcast)))
      
    if str(state_fields).find("logstate")>-1:
      filter_fields.append(Field('logstate', "string", label=T('Log State'), default = session[sfilter_name].get("logstate"),
           requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('logstate')), ns.db.groups.id, '%(groupvalue)s')))
      
    if str(state_fields).find("ratetype")>-1:
      filter_fields.append(Field('ratetype', "string", label=T('Rate Type'), default = session[sfilter_name].get("ratetype"),
           requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('ratetype')), ns.db.groups.id, '%(groupvalue)s')))
    
    if str(state_fields).find("pricetype")>-1:
      filter_fields.append(Field('pricetype', "string", label=T('Price type'), default = session[sfilter_name].get("pricetype"),
           requires = IS_IN_SET(("list","customer","group"),(T("List"),T("Customer"),T("Group")))))
    
    if str(state_fields).find("headtype")>-1:
      filter_fields.append(Field('headtype', "string", label=T('Type'), default = session[sfilter_name].get("headtype"),
           requires = IS_IN_SET(("head","plan"),(T("in"),T("out")))))
      
    if str(state_fields).find("invtype")>-1:
      filter_fields.append(Field('invtype', "string", label=T('Doc.type'), default = session[sfilter_name].get("invtype"),
           requires = IS_IN_SET(("delivery","inventory","production"),(T("delivery"),T("inventory"),T("production")))))
      
  if bool_fields:
    filter_fields.append(Field('bool_filter_name', "string", default = session[sfilter_name].get("bool_filter_name"), 
              requires = IS_IN_SET(bool_fields["bool_fields_name"], bool_fields["bool_fields_label"])))
    filter_fields.append(Field('bool_filter_value', "boolean", default = session[sfilter_name].get("bool_filter_value")))
  
  if date_fields:
    for i in range(3):
      filter_fields.append(Field('date_filter_name_'+str(i+1), "string", default = session[sfilter_name].get("date_filter_name_"+str(i+1)), label=T("Date"),
            requires = IS_IN_SET(date_fields["date_fields_name"], date_fields["date_fields_label"])))
      filter_fields.append(Field('date_filter_rel_'+str(i+1), "string", default = session[sfilter_name].get("date_filter_rel_"+str(i+1)),
              requires = IS_IN_SET(["!=",">",">=","<","<="],zero="=")))
      filter_fields.append(Field('date_filter_value_'+str(i+1), "date", default = session[sfilter_name].get("date_filter_value_"+str(i+1))))
  
  if number_fields:
    for i in range(3):
      filter_fields.append(Field('number_filter_name_'+str(i+1), "string", default = session[sfilter_name].get("number_filter_name_"+str(i+1)), label=T("Amount"),
            requires = IS_IN_SET(number_fields["number_fields_name"], number_fields["number_fields_label"])))
      filter_fields.append(Field('number_filter_rel_'+str(i+1), "string", default = session[sfilter_name].get("number_filter_rel_"+str(i+1)),
              requires = IS_IN_SET(["!=",">",">=","<","<="],zero="=")))
      filter_fields.append(Field('number_filter_value_'+str(i+1), "double", default = session[sfilter_name].get("number_filter_value_"+str(i+1))))
  
  if data_fields:
    for i in range(3):
      filter_fields.append(Field('data_filter_name_'+str(i+1), "string", default = session[sfilter_name].get("data_filter_name_"+str(i+1)), label=T("Data"),
            requires = IS_IN_SET(data_fields["data_fields_name"], data_fields["data_fields_label"])))
      filter_fields.append(Field('data_filter_rel_'+str(i+1), "string", default = session[sfilter_name].get("data_filter_rel_"+str(i+1)),
              requires = IS_IN_SET(("~like","startswith","~startswith","contains","~contains"),
                                   ["not like",T("starts with"),T("not starts with"),T("contains"),T("not contains")],zero=T("like"))))
      filter_fields.append(Field('data_filter_value_'+str(i+1), "string", default = session[sfilter_name].get("data_filter_value_"+str(i+1))))
  
  filter_form = SQLFORM.factory(*filter_fields,submit_button=T("Filter"), table_name="filter")                        
  if len(session[sfilter_name])>0:
    sfilter_label = DIV(SPAN(T('FILTERED')),_style="background-color: #D9D9D9;color: #008B00;border-style: solid;border-width: 2px;text-align: center;font-weight: bold;padding-top: 0px;padding-bottom: 0px;")
  else:
    sfilter_label = ""
    
  filter_div = DIV(_id="filter_div", _style="display: block;")
  filter_div.append(filter_form.custom.begin)
  filter_table = TABLE(_style="width: 100%;border-style: solid;border-width: 1px;border-color: #CCCCCC;border-top: none;")
  head_row = TR()
  head_row.append(TD(filter_form.custom.submit, _style="width: 100px;padding-top: 10px;padding-bottom: 6px;padding-left: 10px;padding-right: 5px;"))
  ruri = str(request.wsgi.environ["REQUEST_URI"]).split("?")[0]+"?remove_filter"
  head_row.append(TD(get_command_button(caption=T("Clear Filter"),title=T("Remove all query filter"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to remove all filter?')+
                              "')){window.location ='"+ruri+"';};return false;"),
                            _style="width: 80px;padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 30px;"))
  if more_data:
    head_row.append(TD(get_command_button(caption=more_data["caption"],title=more_data["title"],color="483D8B",
                              cmd="window.location ='"+more_data["url"]+"';"),
                       _style="width: 100px;padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 30px;"))
    head_row.append(TD(sfilter_label,_style="width: 10px;padding-top: 10px;padding-bottom: 5px;padding-left: 5px;padding-right: 30px;"))
  else:
    head_row.append(TD(sfilter_label,_style="width: 100px;padding-top: 10px;padding-bottom: 5px;padding-left: 5px;padding-right: 30px;"))
  if state_fields or bool_fields:
    head_row.append(TD(get_more_button(dv_id='dv_type',sp_id='sp_type',img_id='img_type',title_1=T('Type and State'),title_2=T('Type and State'),title_tool=T('Type and State filters')),
                            _style="width: 80px;padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 30px;"))
  if date_fields:
    head_row.append(TD(get_more_button(dv_id='dv_date',sp_id='sp_date',img_id='img_date',title_1=T('Date'),title_2=T('Date'),title_tool=T('Date filters')),
                            _style="width: 80px;padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 30px;"))
  if number_fields:
    head_row.append(TD(get_more_button(dv_id='dv_number',sp_id='sp_number',img_id='img_number',title_1=T('Amount'),title_2=T('Amount'),title_tool=T('Amount filters')),
                            _style="width: 80px;padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 30px;"))
  if data_fields:
    head_row.append(TD(get_more_button(dv_id='dv_data',sp_id='sp_data',img_id='img_data',title_1=T('Data'),title_2=T('Data'),title_tool=T('Other data filters')),
                            _style="width: 80px;padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 30px;"))
  if quick_total:
    head_row.append(TD(get_total_button(), _style="padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 5px;"))
  head_row.append(TD())
  filter_table.append(head_row)
  filter_div.append(filter_table)
  
  if state_fields or bool_fields:
    filter_table = TABLE(_style="width: 100%;border-style: solid;border-width: 1px;border-color: #CCCCCC;border-top: none;")
    head_row = TR()
    
    if str(state_fields).find("nervatype")>-1:
      head_row.append(TD(DIV(filter_form.custom.label.nervatype, _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 5px;", _class="td_label"))
      head_row.append(TD(filter_form.custom.widget.nervatype, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 0px;padding-right: 0px;"))
      
    if str(state_fields).find("transtype")>-1 or str(state_fields).find("paymtype")>-1:
      head_row.append(TD(DIV(filter_form.custom.label.transtype, _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 5px;", _class="td_label"))
      head_row.append(TD(filter_form.custom.widget.transtype, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 0px;padding-right: 0px;"))
    
    if str(state_fields).find("direction")>-1:
      head_row.append(TD(DIV(filter_form.custom.label.direction, _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 5px;", _class="td_label"))
      head_row.append(TD(filter_form.custom.widget.direction, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 0px;padding-right: 0px;"))
    
    if str(state_fields).find("pricetype")>-1:
      head_row.append(TD(DIV(filter_form.custom.label.pricetype, _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 5px;", _class="td_label"))
      head_row.append(TD(filter_form.custom.widget.pricetype, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 0px;padding-right: 0px;"))
    
    if str(state_fields).find("headtype")>-1:
      head_row.append(TD(DIV(filter_form.custom.label.headtype, _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 5px;", _class="td_label"))
      head_row.append(TD(filter_form.custom.widget.headtype, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 0px;padding-right: 0px;"))
      
    if str(state_fields).find("invtype")>-1:
      head_row.append(TD(DIV(filter_form.custom.label.invtype, _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 5px;", _class="td_label"))
      head_row.append(TD(filter_form.custom.widget.invtype, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 0px;padding-right: 0px;"))
      
    if str(state_fields).find("logstate")>-1:
      head_row.append(TD(DIV(filter_form.custom.label.logstate, _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 5px;", _class="td_label"))
      head_row.append(TD(filter_form.custom.widget.logstate, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 0px;padding-right: 0px;"))
      
    if str(state_fields).find("ratetype")>-1:
      head_row.append(TD(DIV(filter_form.custom.label.ratetype, _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 5px;", _class="td_label"))
      head_row.append(TD(filter_form.custom.widget.ratetype, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 0px;padding-right: 0px;"))
      
    if str(state_fields).find("transtate")>-1 or str(state_fields).find("transcast")>-1 or bool_fields:
      head_row.append(TD(DIV(T('State'), _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 5px;", _class="td_label"))
    
    if str(state_fields).find("transtate")>-1:
      head_row.append(TD(filter_form.custom.widget.transtate, _style="width: 80px;padding-top: 10px;padding-bottom: 6px;padding-left: 0px;padding-right: 5px;"))
    
    if str(state_fields).find("transcast")>-1:
      head_row.append(TD(filter_form.custom.widget.transcast, _style="width: 120px;padding-top: 10px;padding-bottom: 6px;padding-left: 0px;padding-right: 5px;"))
      
    if bool_fields:
      head_row.append(TD(filter_form.custom.widget.bool_filter_name, _style="width: 100px;padding-top: 9px;padding-bottom: 8px;padding-left: 0px;padding-right: 0px;"))
      head_row.append(TD(filter_form.custom.widget.bool_filter_value, _style="width: 20px;padding-top: 8px;padding-bottom: 8px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD())
    filter_table.append(head_row)
    filter_div.append(DIV(filter_table,_id="dv_type",_style="display: none;"))
  
  if date_fields:
    filter_table = TABLE(_style="width: 100%;border-style: solid;border-width: 1px;border-color: #CCCCCC;border-top: none;")
    head_row = TR()
    head_row.append(TD(DIV(filter_form.custom.label.date_filter_name_1, _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;", _class="td_label"))
    head_row.append(TD(filter_form.custom.widget.date_filter_name_1, _style="width: 150px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.date_filter_rel_1, _style="width: 50px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.date_filter_value_1, _style="width: 80px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 5px;"))
    head_row.append(TD(DIV(" - ", _class="label"),_style="width: 10px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;", _class="td_label"))
    head_row.append(TD(filter_form.custom.widget.date_filter_name_2, _style="width: 150px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.date_filter_rel_2, _style="width: 50px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.date_filter_value_2, _style="width: 80px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 5px;"))
    head_row.append(TD(DIV(" - ", _class="label"),_style="width: 10px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;", _class="td_label"))
    head_row.append(TD(filter_form.custom.widget.date_filter_name_3, _style="width: 150px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.date_filter_rel_3, _style="width: 50px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.date_filter_value_3, _style="width: 80px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 10px;"))      
    head_row.append(TD())
    filter_table.append(head_row)
    filter_div.append(DIV(filter_table,_id="dv_date",_style="display: none;"))
  
  if number_fields:
    filter_table = TABLE(_style="width: 100%;border-style: solid;border-width: 1px;border-color: #CCCCCC;border-top: none;")
    head_row = TR()
    head_row.append(TD(DIV(filter_form.custom.label.number_filter_name_1, _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;", _class="td_label"))
    head_row.append(TD(filter_form.custom.widget.number_filter_name_1, _style="width: 150px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.number_filter_rel_1, _style="width: 50px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.number_filter_value_1, _style="width: 80px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 5px;"))
    head_row.append(TD(DIV(" - ", _class="label"),_style="width: 10px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;", _class="td_label"))
    head_row.append(TD(filter_form.custom.widget.number_filter_name_2, _style="width: 150px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.number_filter_rel_2, _style="width: 50px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.number_filter_value_2, _style="width: 80px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 5px;"))
    head_row.append(TD(DIV(" - ", _class="label"),_style="width: 10px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;", _class="td_label"))
    head_row.append(TD(filter_form.custom.widget.number_filter_name_3, _style="width: 150px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.number_filter_rel_3, _style="width: 50px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.number_filter_value_3, _style="width: 80px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 10px;"))                     
    head_row.append(TD())
    filter_table.append(head_row)
    filter_div.append(DIV(filter_table,_id="dv_number",_style="display: none;"))
    
  if data_fields:
    filter_table = TABLE(_style="width: 100%;border-style: solid;border-width: 1px;border-color: #CCCCCC;border-top: none;")
    head_row = TR()
    head_row.append(TD(DIV(filter_form.custom.label.data_filter_name_1, _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;", _class="td_label"))
    head_row.append(TD(filter_form.custom.widget.data_filter_name_1, _style="width: 110px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.data_filter_rel_1, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.data_filter_value_1, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 10px;"))
    head_row.append(TD(DIV(" - ", _class="label"),_style="width: 10px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;padding-left: 5px;", _class="td_label"))
    head_row.append(TD(filter_form.custom.widget.data_filter_name_2, _style="width: 110px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.data_filter_rel_2, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.data_filter_value_2, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 10px;"))
    head_row.append(TD(DIV(" - ", _class="label"),_style="width: 10px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;padding-left: 5px;", _class="td_label"))
    head_row.append(TD(filter_form.custom.widget.data_filter_name_3, _style="width: 110px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.data_filter_rel_3, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 0px;"))
    head_row.append(TD(filter_form.custom.widget.data_filter_value_3, _style="width: 100px;padding-top: 10px;padding-bottom: 10px;padding-left: 5px;padding-right: 10px;"))      
    head_row.append(TD())
    filter_table.append(head_row)
    filter_div.append(DIV(filter_table,_id="dv_data",_style="display: none;"))
  
  if quick_total:
    filter_table = TABLE(_style="width: 100%;border-style: solid;border-width: 1px;border-color: #CCCCCC;border-top: none;")
    head_row = TR()
    if quick_total.has_key("netamount"):
      head_row.append(TD(DIV(T("Netamount"), _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;", _class="td_label"))
      if quick_total["netamount"]:
        head_row.append(TD(DIV(SPAN(ns.splitThousands(float(quick_total["netamount"])," ",".")), _class="label_disabled", _style="text-align: right;"),_style="width: 150px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;"))
      else:
        head_row.append(TD(DIV(SPAN("0"), _class="label_disabled", _style="text-align: right;"),_style="width: 150px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;"))
    if quick_total.has_key("vatamount"):
      head_row.append(TD(DIV(T("VAT"), _class="label"),_style="width: 70px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;", _class="td_label"))
      if quick_total["vatamount"]:
        head_row.append(TD(DIV(SPAN(ns.splitThousands(float(quick_total["vatamount"])," ",".")), _class="label_disabled", _style="text-align: right;"),_style="width: 150px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;"))
      else:
        head_row.append(TD(DIV(SPAN("0"), _class="label_disabled", _style="text-align: right;"),_style="width: 140px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;"))
    if quick_total.has_key("amount"):
      head_row.append(TD(DIV(T("Amount"), _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;", _class="td_label"))
      if quick_total["amount"]:
        head_row.append(TD(DIV(SPAN(ns.splitThousands(float(quick_total["amount"])," ",".")), _class="label_disabled", _style="text-align: right;"),_style="width: 150px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;"))
      else:
        head_row.append(TD(DIV(SPAN("0"), _class="label_disabled", _style="text-align: right;"),_style="width: 150px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;"))
    if quick_total.has_key("qty"):
      head_row.append(TD(DIV(T("Qty"), _class="label"),_style="width: 100px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;", _class="td_label"))
      if quick_total["qty"]:
        head_row.append(TD(DIV(SPAN(ns.splitThousands(float(quick_total["qty"])," ",".")), _class="label_disabled", _style="text-align: right;"),_style="width: 150px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;"))
      else:
        head_row.append(TD(DIV(SPAN("0"), _class="label_disabled", _style="text-align: right;"),_style="width: 150px;padding-top: 6px;padding-bottom: 6px;padding-right: 0px;"))
    head_row.append(TD())
    filter_table.append(head_row)
    filter_div.append(DIV(filter_table,_id="dv_total",_style="display: none;"))
  
  filter_div.append(filter_form.custom.end) 
  return filter_div

def get_filter_query(sfilter,table,query):
  having = None
  if len(sfilter)>0:
    if sfilter.get("nervatype"):
      query = query & (ns.db[table].nervatype==int(sfilter.get("nervatype")))
    if sfilter.get("transtype"):
      if table=="fieldvalue":
        query = query & (ns.db.trans.with_alias('htab').transtype==int(sfilter.get("transtype")))
      elif table=="payment_invoice":
        query = query & (ns.db.trans.with_alias('ptrans').transtype==int(sfilter.get("transtype")))
      else:
        query = query & (ns.db.trans.transtype==int(sfilter.get("transtype")))
    if sfilter.get("direction"):
      if table=="fieldvalue":
        query = query & (ns.db.trans.with_alias('htab').direction==int(sfilter.get("direction")))
      elif table=="payment_invoice":
        query = query & (ns.db.trans.with_alias('ptrans').direction==int(sfilter.get("direction")))
      else:
        query = query & (ns.db.trans.direction==int(sfilter.get("direction")))
    if sfilter.get("transtate"):
      if table=="fieldvalue":
        query = query & (ns.db.trans.with_alias('htab').transtate==int(sfilter.get("transtate")))
      elif table=="payment_invoice":
        query = query & (ns.db.trans.with_alias('ptrans').transtate==int(sfilter.get("transtate")))
      else:
        query = query & (ns.db.trans.transtate==int(sfilter.get("transtate")))
    if sfilter.get("transcast"):
      if table=="fieldvalue":
        query = query & ((ns.db.trans.with_alias('htab').id == ns.db.fieldvalue.ref_id)&(ns.db.fieldvalue.fieldname=="trans_transcast")&(ns.db.fieldvalue.value==sfilter.get("transcast")))
      else:
        query = query & ((ns.db.trans.id == ns.db.fieldvalue.ref_id)&(ns.db.fieldvalue.fieldname=="trans_transcast")&(ns.db.fieldvalue.value==sfilter.get("transcast")))
    if sfilter.get("headtype"):
      query = query & (ns.db.movement.movetype==ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue==sfilter.get("headtype"))).select().as_list()[0]["id"])
    if sfilter.get("pricetype"):
      if sfilter.get("pricetype")=="list":
        query = query & ((ns.db.link.with_alias('custlink').ref_id_2==None)&(ns.db.link.with_alias('grouplink').ref_id_2==None))
      elif sfilter.get("pricetype")=="customer":
        query = query & (ns.db.link.with_alias('custlink').ref_id_2!=None)
      elif sfilter.get("pricetype")=="group":
        query = query & (ns.db.link.with_alias('grouplink').ref_id_2!=None)
    if sfilter.get("invtype"):
      if table=="fieldvalue":
        itrans = ns.db.trans.with_alias('htab')
      else:
        itrans = ns.db.trans
      if sfilter.get("invtype")=="delivery":
        transtype_delivery_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="delivery")).select().as_list()[0]["id"]
        query = query & ((itrans.transtype==transtype_delivery_id))
      if sfilter.get("invtype")=="inventory":
        transtype_inventory_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="inventory")).select().as_list()[0]["id"]
        query = query & ((itrans.transtype==transtype_inventory_id))
      if sfilter.get("invtype")=="production":
        transtype_production_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="production")).select().as_list()[0]["id"]
        query = query & ((itrans.transtype==transtype_production_id))
    if sfilter.get("logstate"):
      query = query & (ns.db[table].logstate==int(sfilter.get("logstate")))
    if sfilter.get("ratetype"):
      query = query & (ns.db[table].ratetype==int(sfilter.get("ratetype")))
    if sfilter.get("bool_filter_name"):
      if table=="fieldvalue":
        if sfilter.get("bool_filter_value"):
          query = query & ((ns.db.fieldvalue.fieldname==sfilter.get("bool_filter_name"))&(ns.db.fieldvalue.value=="true"))
        else:
          query = query & ((ns.db.fieldvalue.fieldname==sfilter.get("bool_filter_name"))&(ns.db.fieldvalue.value=="false"))
      else:
        if sfilter.get("bool_filter_value"):
          query = query & (ns.db[table][sfilter.get("bool_filter_name")]==1)
        else:
          query = query & (ns.db[table][sfilter.get("bool_filter_name")]==0)
    
    def get_date_query(table,fname,fvalue,frel):
      if not sfilter.get(frel):
        sfilter[frel] = "="
      if table=="fieldvalue":
        return (ns.db.fieldvalue.fieldname==sfilter.get(fname))& ("(cast(fieldvalue.value as date) %s '%s')" % (sfilter.get(frel),sfilter.get(fvalue)))
      elif table=="item" and sfilter.get(fname)=="transdate":
        return get_query_rel(ns.db.trans[sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue))
      elif table=="trans" and sfilter.get(fname)=="shippingdate":
        return get_query_rel(ns.db.movement[sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue))
      elif table in("trans","payment_invoice") and sfilter.get(fname)=="paiddate":
        return get_query_rel(ns.db.payment[sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue))
      else:
        return get_query_rel(ns.db[table][sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue))    
    if sfilter.get("date_filter_name_1") and sfilter.get("date_filter_value_1"):
      query = query & get_date_query(table,"date_filter_name_1","date_filter_value_1","date_filter_rel_1")
    if sfilter.get("date_filter_name_2") and sfilter.get("date_filter_value_2"):
      query = query & get_date_query(table,"date_filter_name_2","date_filter_value_2","date_filter_rel_2")
    if sfilter.get("date_filter_name_3") and sfilter.get("date_filter_value_3"):
      query = query & get_date_query(table,"date_filter_name_3","date_filter_value_3","date_filter_rel_3")
    
    def set_number_query(table,fname,fvalue,frel):
      if not sfilter.get(frel):
        sfilter[frel] = "="
      if table=="fieldvalue":
        return dict(query=(ns.db.fieldvalue.fieldname==sfilter.get(fname))& ("(cast(fieldvalue.value as real) %s %s)" % (sfilter.get(frel),sfilter.get(fvalue))),having=None)
      if table=="payment_invoice":
        ftable = ns.db.fieldvalue.with_alias(sfilter.get(fname))
        return dict(query=(ftable.fieldname==sfilter.get(fname))& ("(cast("+sfilter.get(fname)+".value as real) %s %s)" % (sfilter.get(frel),sfilter.get(fvalue))),having=None)
      elif table=="trans" and sfilter.get(fname) in("amount","netamount","vatamount"):
        return dict(query=None,having=get_query_rel(ns.db.item[sfilter.get(fname)].sum(),sfilter.get(frel),sfilter.get(fvalue)))
      elif table=="trans" and sfilter.get(fname) in("paidamount"):
        return dict(query=get_query_rel(ns.db.payment.amount,sfilter.get(frel),sfilter.get(fvalue)),having=None)
      elif table=="movement" and sfilter.get(fname) == "sqty":
        return dict(query=None,having=get_query_rel(ns.db.movement.qty.sum(),sfilter.get(frel),sfilter.get(fvalue)))
      elif table=="movement" and sfilter.get(fname) == "qty":
        return dict(query=get_query_rel(ns.db.movement.qty,sfilter.get(frel),sfilter.get(fvalue)),having=None)
      else:
        return dict(query=get_query_rel(ns.db[table][sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue)),having=None)      
    if sfilter.get("number_filter_name_1") and sfilter.get("number_filter_value_1"):
      nq=set_number_query(table,"number_filter_name_1","number_filter_value_1","number_filter_rel_1")
      if nq["query"]:
        query = query & nq["query"]
      else:
        if having:
          having &= nq["having"]
        else:
          having = nq["having"]
    if sfilter.get("number_filter_name_2") and sfilter.get("number_filter_value_2"):
      nq = set_number_query(table,"number_filter_name_2","number_filter_value_2","number_filter_rel_2")
      if nq["query"]:
        query = query & nq["query"]
      else:
        if having:
          having &= nq["having"]
        else:
          having = nq["having"]
    if sfilter.get("number_filter_name_3") and sfilter.get("number_filter_value_3"):
      nq = set_number_query(table,"number_filter_name_3","number_filter_value_3","number_filter_rel_3")
      if nq["query"]:
        query = query & nq["query"]
      else:
        if having:
          having &= nq["having"]
        else:
          having = nq["having"]
    
    def get_data_query(table,fname,fvalue,frel):
      if not sfilter.get(frel):
        sfilter[frel] = "like"
      def get_ref_value(table,fname,fvalue,frel,ftype=None):
        if fname=="customer_id" or ftype=="customer":
          if table in ("fieldvalue"):
            return ((ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=customer.id)") & get_query_rel(ns.db.customer.custname,frel,fvalue))
          else:
            return ((ns.db[table].customer_id == ns.db.customer.id)&get_query_rel(ns.db.customer.custname,frel,fvalue))
        elif fname=="tool_id" or ftype=="tool":
          if table in ("fieldvalue"):
            return ((ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=tool.id)") & get_query_rel(ns.db.tool.serial,frel,fvalue))
          else:
            return ((ns.db[table].tool_id == ns.db.tool.id)&get_query_rel(ns.db.tool.serial,frel,fvalue))
        elif fname=="employee_id" or ftype=="employee":
          if table in ("fieldvalue"):
            return ((ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=employee.id)") & get_query_rel(ns.db.employee.empnumber,frel,fvalue))
          else:
            return ((ns.db[table].employee_id == ns.db.employee.id)&get_query_rel(ns.db.employee.empnumber,frel,fvalue))
        elif fname=="place_id" or ftype=="place":
          if table in ("fieldvalue"):
            return ((ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=place.id)") & get_query_rel(ns.db.place.planumber,frel,fvalue))
          else:
            return ((ns.db[table].place_id == ns.db.place.id)&get_query_rel(ns.db.place.planumber,frel,fvalue))
        elif fname in("department","paidtype","eventgroup","custtype","usergroup","toolgroup","protype","rategroup"):
          return ((ns.db[table][fname]==ns.db.groups.id)&get_query_rel(ns.db.groups.groupvalue,frel,fvalue))
        elif fname=="project_id" or ftype=="project":
          if table in ("fieldvalue"):
            return ((ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=project.id)") & get_query_rel(ns.db.project.pronumber,frel,fvalue))  
          else:
            return ((ns.db[table].project_id == ns.db.project.id)&get_query_rel(ns.db.project.pronumber,frel,fvalue))
        elif fname=="trans_id" or ftype in("trans","transitem","transmovement","transpayment"):
          if table in ("fieldvalue"):
            return ((ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=trans.id)") & get_query_rel(ns.db.trans.transnumber,frel,fvalue))
          else:
            return ((ns.db[table].trans_id == ns.db.trans.id)&get_query_rel(ns.db.trans.transnumber,frel,fvalue))
        elif fname=="product_id" or ftype=="product":
          if table in ("fieldvalue"):
            return ((ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=product.id)") & get_query_rel(ns.db.product.description,frel,fvalue))
          else:
            return ((ns.db[table].product_id == ns.db.product.id)&get_query_rel(ns.db.product.description,frel,fvalue))
        elif fname=="tax_id":
          return ((ns.db[table].tax_id == ns.db.tax.id)&get_query_rel(ns.db.tax.taxcode,frel,fvalue))
        elif fname=="event_id":
          return ((ns.db[table].event_id == ns.db.event.id)&get_query_rel(ns.db.event.calnumber,frel,fvalue))
      
      if str(sfilter.get(fname)).startswith("htab_"):
        if table=="fieldvalue":
          return get_query_rel(ns.db[str(sfilter.get(fname)).split("_")[1]].with_alias('htab')[str(sfilter.get(fname)).split("_")[2]],sfilter.get(frel),sfilter.get(fvalue))
        else:
          return get_query_rel(ns.db[str(sfilter.get(fname)).split("_")[1]][str(sfilter.get(fname)).split("_")[2]],sfilter.get(frel),sfilter.get(fvalue))  
      elif table=="fieldvalue":
        if sfilter.get(fname)=="description":
          return get_query_rel(ns.db.deffield.description,sfilter.get(frel),sfilter.get(fvalue))
        elif sfilter.get(fname)=="notes":
          return get_query_rel(ns.db.fieldvalue.notes,sfilter.get(frel),sfilter.get(fvalue))
        else: 
          fieldtype = ns.db.groups(id=ns.db.deffield(fieldname=sfilter.get(fname)).fieldtype).groupvalue
          if fieldtype in("customer","tool","product","trans","transitem","transmovement","transpayment","project","employee","place"):
            return get_ref_value(table,sfilter.get(fname),sfilter.get(fvalue),sfilter.get(frel),fieldtype)
          else:
            return ((ns.db.fieldvalue.fieldname == sfilter.get(fname))&get_query_rel(ns.db.fieldvalue.value,sfilter.get(frel),sfilter.get(fvalue)))
      elif sfilter.get(fname) in("customer_id","employee_id","paidtype","project_id","trans_id","product_id","tax_id",
                                 "eventgroup","custtype","usergroup","toolgroup","protype","place_id","rategroup"):
        return get_ref_value(table,sfilter.get(fname),sfilter.get(fvalue),sfilter.get(frel))
      elif table=="employee" and sfilter.get(fname)=="department":
        department = ns.db.groups.with_alias('department')
        return get_query_rel(department.groupvalue,sfilter.get(frel),sfilter.get(fvalue))
      elif table=="trans" and sfilter.get(fname) in("place_curr"):
        return ((ns.db.trans.place_id == ns.db.place.id)&get_query_rel(ns.db.place.curr,sfilter.get(frel),sfilter.get(fvalue)))
      elif table=="trans" and sfilter.get(fname) in("payment_description"):
        return get_query_rel(ns.db.payment.notes,sfilter.get(frel),sfilter.get(fvalue))
      elif table=="movement" and sfilter.get(fname) in("partnumber","unit"):
        return get_query_rel(ns.db.product[sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue))
      elif table=="movement" and sfilter.get(fname) == "refcust":
        return ((ns.db.trans.with_alias('itrn').customer_id == ns.db.customer.id)&get_query_rel(ns.db.customer.custname,sfilter.get(frel),sfilter.get(fvalue)))
      elif table=="movement" and sfilter.get(fname) == "refnumber":
        return ((ns.db.item.trans_id == ns.db.trans.with_alias('rtrn').id)&get_query_rel(ns.db.trans.with_alias('rtrn').transnumber,sfilter.get(frel),sfilter.get(fvalue)))
      elif table=="payment_invoice":
        if sfilter.get(fname) in("place"):
          return ((ns.db.trans.with_alias('ptrans').place_id == ns.db.place.id)&get_query_rel(ns.db.place.planumber,sfilter.get(frel),sfilter.get(fvalue)))
        elif sfilter.get(fname) in("docnumber"):
          return get_query_rel(ns.db.trans.with_alias('ptrans').transnumber,sfilter.get(frel),sfilter.get(fvalue))
        elif sfilter.get(fname) in("doc_curr"):
          return get_query_rel(ns.db.trans.with_alias('ptrans').curr,sfilter.get(frel),sfilter.get(fvalue))
        elif sfilter.get(fname) in("invnumber"):
          return get_query_rel(ns.db.trans.with_alias('itrans').transnumber,sfilter.get(frel),sfilter.get(fvalue))
        elif sfilter.get(fname) in("inv_curr"):
          return get_query_rel(ns.db.trans.with_alias('itrans').curr,sfilter.get(frel),sfilter.get(fvalue))
      else:
        return get_query_rel(ns.db[table][sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue))
    if sfilter.get("data_filter_name_1") and sfilter.get("data_filter_value_1"):
      query = query & get_data_query(table,"data_filter_name_1","data_filter_value_1","data_filter_rel_1")
    if sfilter.get("data_filter_name_2") and sfilter.get("data_filter_value_2"):
      query = query & get_data_query(table,"data_filter_name_2","data_filter_value_2","data_filter_rel_2")
    if sfilter.get("data_filter_name_3") and sfilter.get("data_filter_value_3"):
      query = query & get_data_query(table,"data_filter_name_3","data_filter_value_3","data_filter_rel_3")
                              
  return dict(query=query,having=having)

def get_query_rel(field,rel,value):
  if rel=="=":
    return (field==value)
  if rel=="!=":
    return (field!=value)
  if rel==">":
    return (field>value)
  if rel==">=":
    return (field>=value)
  if rel=="<":
    return (field<value)
  if rel=="<=":
    return (field<=value)
  if rel=="like":
    return (field.like(value))
  if rel=="~like":
    return (~field.like(value))
  if rel=="startswith":
    return (field.startswith(value))
  if rel=="~startswith":
    return (~field.startswith(value))
  if rel=="contains":
    return (field.contains(value))
  if rel=="~contains":
    return (~field.contains(value))
  else:
    return None

def get_fields_filter(nervatype,sfilter_name,state_fields=None):
  nervatype_trans = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue==nervatype)).select().as_list()[0]["id"]
  rows = ns.db((ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_trans)).select().as_list()
  bool_fields_name=[]
  bool_fields_label=[]
  date_fields_name=[]
  date_fields_label=[]
  number_fields_name=[]
  number_fields_label=[]
  data_fields_name=[]
  data_fields_label=[]
  for field in rows:
    if ns.db.groups(id=field["fieldtype"]).groupvalue=="bool":
      bool_fields_name.append(field["fieldname"])
      bool_fields_label.append(field["description"])
    elif ns.db.groups(id=field["fieldtype"]).groupvalue=="date":
      date_fields_name.append(field["fieldname"])
      date_fields_label.append(field["description"])
    elif ns.db.groups(id=field["fieldtype"]).groupvalue in("float","integer"):
      number_fields_name.append(field["fieldname"])
      number_fields_label.append(field["description"])
    else:
      data_fields_name.append(field["fieldname"])
      data_fields_label.append(field["description"])
  if len(bool_fields_name)==0:
    bool_fields=None
  else:
    bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label}
  if len(date_fields_name)==0:
    date_fields=None
  else:
    date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label}
  if len(number_fields_name)==0:
    number_fields=None
  else:
    number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label}
  
  data_fields_name.insert(0, "notes")
  data_fields_label.insert(0, T("Other data"))
  data_fields_name.insert(0, "description")
  data_fields_label.insert(0, T("Description"))  
  if nervatype=="trans":
    data_fields_name.insert(0, "htab_trans_transnumber")
    data_fields_label.insert(0, T("Doc.No."))
  elif nervatype=="project":
    data_fields_name.insert(0, "htab_project_description")
    data_fields_label.insert(0, T("Project Name"))
    data_fields_name.insert(0, "htab_project_pronumber")
    data_fields_label.insert(0, T("Project No."))
  elif nervatype=="customer":
    data_fields_name.insert(0, "htab_customer_custname")
    data_fields_label.insert(0, T("Customer Name"))
    data_fields_name.insert(0, "htab_customer_custnumber")
    data_fields_label.insert(0, T("Customer No."))
  elif nervatype=="employee":
    data_fields_name.insert(0, "htab_employee_username")
    data_fields_label.insert(0, T("Username"))
    data_fields_name.insert(0, "htab_employee_empnumber")
    data_fields_label.insert(0, T("Employee No."))
  elif nervatype=="tool":
    data_fields_name.insert(0, "htab_tool_description")
    data_fields_label.insert(0, T("Tool description"))
    data_fields_name.insert(0, "htab_tool_serial")
    data_fields_label.insert(0, T("Serial No."))
  elif nervatype=="product":
    data_fields_name.insert(0, "htab_product_description")
    data_fields_label.insert(0, T("Product name"))
    data_fields_name.insert(0, "htab_product_partnumber")
    data_fields_label.insert(0, T("Product No."))
  elif nervatype=="event":
    data_fields_name.insert(0, "htab_event_subject")
    data_fields_label.insert(0, T("Subject"))
    data_fields_name.insert(0, "htab_event_calnumber")
    data_fields_label.insert(0, T("Event No."))
  return create_filter_form(sfilter_name=sfilter_name,state_fields=state_fields,
                                       bool_fields=bool_fields,date_fields=date_fields,number_fields=number_fields,
                                       data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})

def set_transfilter(query,alias=None,fieldname="cruser_id"):
  groups_nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  filterlink = ns.db((ns.db.link.ref_id_1==ns.db.employee(id=session.auth.user.id).usergroup)&(ns.db.link.nervatype_1==groups_nervatype_id)
                  &(ns.db.link.nervatype_2==groups_nervatype_id)&(ns.db.link.deleted==0)).select().as_list()
  if len(filterlink)>0:
    transfilter = ns.db.groups(id=filterlink[0]["ref_id_2"]).groupvalue
  else:
    transfilter = "all"
  if not alias: alias = ns.db.trans
  if transfilter=="usergroup":
    query = query & (alias[fieldname].belongs(ns.db((ns.db.employee.usergroup==ns.db.employee(id=session.auth.user.id).usergroup)&(ns.db.employee.deleted==0)).select(ns.db.employee.id)))
  elif transfilter=="own":
    query = query & (alias[fieldname]==session.auth.user.id)
  return query

@ns_auth.requires_login()
def find_movement_quick():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_movement_quick")+19:]
    redirect(URL(ruri))
      
  response.view=dir_view+'/gridform.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select document')
  response.margin_top = "20px"
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
    response.cmd_back = get_back_button(session.back_url)
  else:
    response.cmd_back = get_home_button()
  response.titleicon = URL(dir_images,'icon16_find.png')
  
  query = ((ns.db.trans.deleted==0) & (ns.db.trans.transtype==ns.db.groups.id) & ns.db.groups.groupvalue.belongs("delivery","inventory","waybill","production","formula")) 
  fields = [ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, ns.db.trans.transdate]
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = set_transfilter(query)
  
  ns.db.groups.groupvalue.label = T("Doc.Type")
  ns.db.trans.transdate.label = T("Shipping Date")
  smenu = [ns.db.trans.transnumber,ns.db.groups.groupvalue,ns.db.trans.transdate]
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False:
    query = query & (ns.db.movement.id==-1)
  search_widget = create_search_widget(smenu)

  form = SQLFORM.grid(query=query, field_id=ns.db.trans.id, fields=fields, left=None, #headers=headers,
               orderby=ns.db.trans.id, sortable=True, paginate=10, maxtextlength=25,
               searchable=True, csv=False, details=False, showbuttontext=False,
               create=False, deletable=False, editable=True, selectable=False, 
               user_signature=False, search_widget=search_widget)
  if type(form[1][0][0]).__name__=="TABLE":
    form=move_buttons(form)
  set_counter_bug(form)
  return dict(form=DIV(form, _id="dlg_frm"))

def set_find_movement_menu():
  response.lo_menu = []
  mnu_trans = (T('STOCK'), False, None, [])
  mnu_trans[3].append((T('Inventory'), False, URL('find_movement_inventory'), []))
  mnu_trans[3].append((T('Product Movement'), False, URL('find_movement_product'), []))
  audit_filter = get_audit_filter("trans", "waybill")[0]
  if audit_filter!="disabled":
    mnu_trans[3].append((T('Tool Movement'), False, URL('find_movement_tool'), []))
  audit_filter = get_audit_filter("trans", "formula")[0]
  if audit_filter!="disabled":
    mnu_trans[3].append((T('Formula'), False, URL('find_movement_formula'), []))
  mnu_trans[3].append((T('Additional Data'), False, URL('find_movement_fields'), []))
  mnu_trans[3].append((T('Groups'), False, URL('find_movement_groups'), []))
  response.lo_menu.append(mnu_trans)

@ns_auth.requires_login()
def find_movement_inventory():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.movement_inventory_filter=None
    redirect(URL("find_movement_inventory"))
          
  response.browsertype=T('Stock Browser')
  response.subtitle=T('Inventory')
  response.titleicon = URL(dir_images,'icon16_lorry.png')
  response.export_excel = ruri.replace("find_movement_inventory","find_movement_inventory/excel")
  response.export_csv = ruri.replace("find_movement_inventory","find_movement_inventory/csv")
  response.view=dir_view+'/browser.html'
  set_find_movement_menu()
  
  def get_find_movement_inventory_filter(quick_total):  
    
    date_fields_name = [ns.db.movement.shippingdate.name]
    date_fields_label = [ns.db.movement.shippingdate.label]
    
    number_fields_name = ["sqty"]
    number_fields_label = [ns.db.movement.qty.label]
    
    data_fields_name = [ns.db.movement.place_id.name, ns.db.product.partnumber.name, ns.db.movement.product_id.name, ns.db.product.unit.name, ns.db.movement.notes.name]
    data_fields_label = [ns.db.movement.place_id.label, ns.db.product.partnumber.label, ns.db.movement.product_id.label, ns.db.product.unit.label, ns.db.movement.notes.label]
    
    return create_filter_form(sfilter_name="movement_inventory_filter",state_fields=["invtype","transtate"],
                                         bool_fields=None,
                                         date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},
                                         number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label},
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label},
                                         quick_total=quick_total)
  
  movetype_inventory_id = ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="inventory")).select().as_list()[0]["id"]
  
  fields = [ns.db.movement.place_id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes,
            ns.db.movement.qty, ns.db.movement.shippingdate]
  join = [(ns.db.product.on((ns.db.movement.product_id==ns.db.product.id))),
          (ns.db.trans.on((ns.db.movement.trans_id==ns.db.trans.id)&(ns.db.trans.deleted==0)))]
  left = None
  
  query = ((ns.db.movement.deleted==0)&(ns.db.movement.movetype==movetype_inventory_id))
  
  init_sfilter("movement_inventory_filter")
  where = get_filter_query(sfilter=session.movement_inventory_filter,table="movement",query=query)
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
  ns.db.movement.shippingdate.represent = lambda value,row: formatDate(row["shippingdate"])  
  
  groupfields=[ns.db.movement.place_id, ns.db.product.partnumber, ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes,
               ns.db.movement.qty.sum().with_alias('qty'),ns.db.movement.shippingdate.max().with_alias('shippingdate')]
  groupby=[ns.db.movement.place_id|ns.db.product.partnumber|ns.db.movement.product_id|ns.db.product.unit|ns.db.movement.notes]  
  
  if ruri.find("find_movement_inventory/excel")>0:
    return export2excel("trans",query,left,fields,ns.db.product.partnumber,request.vars.keywords,
                        join=join,groupfields=groupfields,groupby=groupby,having=having)
  if ruri.find("find_movement_inventory/csv")>0:
    return export2csv("trans",query,left,fields,ns.db.product.partnumber,request.vars.keywords,
                        join=join,groupfields=groupfields,groupby=groupby,having=having)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.movement_inventory_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.movement.id==-1))
  
  quick_total={"qty":0}
  total_rows = ns.db(query).select(*[ns.db.movement.qty.sum().with_alias('qty')],
                      join=join,left=left,groupby=groupby,having=having).as_list()
  for row in total_rows:
    if row["qty"]:
      quick_total["qty"]+=row["qty"]
  response.filter_form = get_find_movement_inventory_filter(quick_total)
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.movement.place_id, 
             fields=fields, groupfields=groupfields, groupby=groupby, left=left, having=having, join=join,
             orderby=order, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=False, links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_lorry.png')
  response.export_excel = ruri.replace("find_movement_product","find_movement_product/excel")
  response.export_csv = ruri.replace("find_movement_product","find_movement_product/csv")
  response.view=dir_view+'/browser.html'
  set_find_movement_menu()
  
  def get_find_movement_product_filter(quick_total):  
    
    date_fields_name = [ns.db.movement.shippingdate.name]
    date_fields_label = [ns.db.movement.shippingdate.label]
    
    number_fields_name = [ns.db.movement.qty.name]
    number_fields_label = [ns.db.movement.qty.label]
    
    data_fields_name = [ns.db.movement.trans_id.name, ns.db.movement.place_id.name, ns.db.product.partnumber.name, 
                        ns.db.movement.product_id.name, ns.db.product.unit.name, ns.db.movement.notes.name,
                        "refnumber", "refcust"]
    data_fields_label = [ns.db.movement.trans_id.label, ns.db.movement.place_id.label, ns.db.product.partnumber.label, 
                         ns.db.movement.product_id.label, ns.db.product.unit.label, ns.db.movement.notes.label,
                         ns.db.item.trans_id.label, itrn.customer_id.label]
    
    return create_filter_form(sfilter_name="movement_product_filter",state_fields=["invtype","direction","transtate"],
                                         bool_fields=None,
                                         date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},
                                         number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label},
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label},
                                         quick_total=quick_total)
    
  iln = ns.db.link.with_alias('iln')
  itrn = ns.db.trans.with_alias('itrn')
  
  fields = [ns.db.trans.transtype, ns.db.trans.direction, ns.db.movement.trans_id, 
            ns.db.movement.shippingdate, ns.db.movement.place_id, ns.db.product.partnumber, 
            ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.notes, ns.db.movement.qty,
            ns.db.item.trans_id, itrn.customer_id]
  join = [(ns.db.product.on((ns.db.movement.product_id==ns.db.product.id))),
          (ns.db.trans.on((ns.db.movement.trans_id==ns.db.trans.id)&(ns.db.trans.deleted==0)))]
  
  nervatype_movement_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="movement")).select().as_list()[0]["id"]
  nervatype_item_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="item")).select().as_list()[0]["id"]
  left = [(iln.on((ns.db.movement.id==iln.ref_id_1)&(iln.nervatype_1==nervatype_movement_id)&(iln.deleted==0))),
          (ns.db.item.on((iln.nervatype_2==nervatype_item_id)&(iln.ref_id_2==ns.db.item.id))),
          (itrn.on((ns.db.item.trans_id==itrn.id)&(itrn.deleted==0)))]
  
  movetype_inventory_id = ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="inventory")).select().as_list()[0]["id"]
  query = ((ns.db.movement.deleted==0)&(ns.db.movement.movetype==movetype_inventory_id))
  
  init_sfilter("movement_product_filter")
  where = get_filter_query(sfilter=session.movement_product_filter,table="movement",query=query)
  query = where["query"]
  having = where["having"] 
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = set_transfilter(query)
  
  ns.db.movement.place_id.label = T("Warehouse No.")
  ns.db.movement.shippingdate.represent = lambda value,row: formatDate(row["shippingdate"])
  ns.db.item.trans_id.label = T("Ref.No.")    
  itrn.customer_id.label = T("Ref.Customer")
  
  if ruri.find("find_movement_product/excel")>0:
    return export2excel("trans",query,left,fields,ns.db.product.partnumber,request.vars.keywords,
                        join=join,groupfields=None,groupby=None,having=having)
  if ruri.find("find_movement_product/csv")>0:
    return export2csv("trans",query,left,fields,ns.db.product.partnumber,request.vars.keywords,
                        join=join,groupfields=None,groupby=None,having=having)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.movement_product_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.movement.id==-1))
  
  quick_total={"qty":0}
  total_rows = ns.db(query).select(*[ns.db.movement.qty.sum().with_alias('qty')],
                      join=join,left=left,groupby=None,having=having).as_list()
  for row in total_rows:
    if row["qty"]:
      quick_total["qty"]+=row["qty"]
  response.filter_form = get_find_movement_product_filter(quick_total)
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=having, join=join,
             orderby=ns.db.movement.id, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_wrench_page.png')
  response.export_excel = ruri.replace("find_movement_tool","find_movement_tool/excel")
  response.export_csv = ruri.replace("find_movement_tool","find_movement_tool/csv")
  response.view=dir_view+'/browser.html'
  set_find_movement_menu()
  
  ns.db.movement.notes.label = T('Additional info')
  ns.db.link.ref_id_2.label=T('Ref.No.')
  reftab = ns.db.trans.with_alias('reftab')
  
  def get_find_movement_tool_filter():  
    bool_fields_name = [ns.db.trans.closed.name]
    bool_fields_label = [ns.db.trans.closed.label]
    
    date_fields_name = [ns.db.trans.crdate.name,ns.db.movement.shippingdate.name]
    date_fields_label = [ns.db.trans.crdate.label,ns.db.movement.shippingdate.label]
    
    data_fields_name = [ns.db.trans.transnumber.name, "htab_reftab_transnumber", "htab_customer_custname", "htab_employee_empnumber",
                        "htab_tool_serial", "htab_tool_description", "htab_movement_notes", ns.db.trans.notes.name, ns.db.trans.intnotes.name]
    data_fields_label = [ns.db.trans.transnumber.label, ns.db.link.ref_id_2.label, ns.db.trans.customer_id.label, ns.db.trans.employee_id.label,
                        ns.db.movement.tool_id.label, ns.db.tool.description.label, ns.db.movement.notes.label, ns.db.trans.notes.label, ns.db.trans.intnotes.label]
    
    return create_filter_form(sfilter_name="movement_tool_filter",state_fields=["direction","transtate"],
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},
                                         number_fields=None,
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_movement_tool_filter()
  
  nervatype_trans = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
  transtype_waybill = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="waybill")).select().as_list()[0]["id"]
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
  
  where = get_filter_query(sfilter=session.movement_tool_filter,table="trans",query=query)
  query = where["query"]
  
  #set transfilter
  query = set_transfilter(query)
  
  fields = [ns.db.trans.transnumber, ns.db.trans.crdate,ns.db.trans.direction,ns.db.link.ref_id_2,ns.db.trans.customer_id,ns.db.trans.employee_id,
            ns.db.movement.shippingdate,ns.db.movement.tool_id,ns.db.tool.description,ns.db.movement.notes,
            ns.db.trans.transtate,ns.db.trans.closed,ns.db.trans.notes,ns.db.trans.intnotes]
  
  if ruri.find("find_movement_tool/excel")>0:
    return export2excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_movement_tool/csv")>0:
    return export2csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  
  audit_filter = get_audit_filter("trans", "waybill")[0]
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.movement_tool_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.trans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, create=(audit_filter=="all"), links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_formula.png')
  response.export_excel = ruri.replace("find_movement_formula","find_movement_formula/excel")
  response.export_csv = ruri.replace("find_movement_formula","find_movement_formula/csv")
  response.view=dir_view+'/browser.html'
  set_find_movement_menu()
  
  def get_find_movement_formula_filter(quick_total):  
    bool_fields_name = [ns.db.movement.shared.name]
    bool_fields_label = [ns.db.movement.shared.label]
    
    number_fields_name = [ns.db.movement.qty.name]
    number_fields_label = [ns.db.movement.qty.label]
    
    data_fields_name = [ns.db.movement.trans_id.name, ns.db.movement.place_id.name, ns.db.product.partnumber.name, 
                        ns.db.movement.product_id.name, ns.db.product.unit.name, ns.db.movement.notes.name]
    data_fields_label = [ns.db.movement.trans_id.label, ns.db.movement.place_id.label, ns.db.product.partnumber.label, 
                         ns.db.movement.product_id.label, ns.db.product.unit.label, ns.db.movement.notes.label]
    
    return create_filter_form(sfilter_name="movement_formula_filter",state_fields=["headtype","transtate"],
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         date_fields=None,
                                         number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label},
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label},
                                         quick_total=quick_total)
  
  fields = [ns.db.movement.trans_id, ns.db.movement.movetype, ns.db.product.partnumber, 
            ns.db.movement.product_id, ns.db.product.unit, ns.db.movement.qty, ns.db.movement.notes,
            ns.db.movement.place_id, ns.db.movement.shared]
  join = [(ns.db.product.on((ns.db.movement.product_id==ns.db.product.id))),
          (ns.db.trans.on((ns.db.movement.trans_id==ns.db.trans.id)&(ns.db.trans.deleted==0)))]
  left = None 
    
  transtype_formula = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="formula")).select().as_list()[0]["id"]
  query = ((ns.db.movement.deleted==0)&(ns.db.trans.transtype==transtype_formula))
  
  init_sfilter("movement_formula_filter")
  where = get_filter_query(sfilter=session.movement_formula_filter,table="movement",query=query)
  query = where["query"]
  having = where["having"] 
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = set_transfilter(query)
  
  ns.db.movement.place_id.label = T("Warehouse No.")
  ns.db.movement.movetype.label = T("Type")
  ns.db.movement.movetype.represent = lambda value,row: T("in") if ns.db.groups(id=value).groupvalue=="head" else T("out")
  
  if ruri.find("find_movement_formula/excel")>0:
    return export2excel("trans",query,left,fields,ns.db.product.partnumber,request.vars.keywords,
                        join=join,groupfields=None,groupby=None,having=having)
  if ruri.find("find_movement_formula/csv")>0:
    return export2csv("trans",query,left,fields,ns.db.product.partnumber,request.vars.keywords,
                        join=join,groupfields=None,groupby=None,having=having)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.movement_formula_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.movement.id==-1))
  
  quick_total={"qty":0}
  total_rows = ns.db(query).select(*[ns.db.movement.qty.sum().with_alias('qty')],
                      join=join,left=left,groupby=None,having=having).as_list()
  for row in total_rows:
    if row["qty"]:
      quick_total["qty"]+=row["qty"]
  response.filter_form = get_find_movement_formula_filter(quick_total)
  
  audit_filter = get_audit_filter("trans", "formula")[0]  
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=having, join=join,
             orderby=ns.db.movement.id, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, create=(audit_filter=="all"), links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_lorry.png')
  response.export_excel = ruri.replace("find_movement_fields","find_movement_fields/excel")
  response.export_csv = ruri.replace("find_movement_fields","find_movement_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_movement_menu()
  response.filter_form = get_fields_filter("trans","movement_fields_filter",["invtype","direction","transtate"])
  
  nervatype_trans = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
    
  htab = ns.db.trans.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(ns.db.fieldvalue.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_trans)))]
  query = (ns.db.fieldvalue.deleted==0)
  query = query & ((htab.deleted==0))
  
  where = get_filter_query(sfilter=session.movement_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  #set transtype
  query = query & (htab.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("delivery","inventory","waybill","production","formula"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~htab.transtype.belongs(audit))
  
  #set transfilter
  query = set_transfilter(query,htab)
        
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id, htab.transnumber, ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  if ruri.find("find_movement_fields/excel")>0:
    return export2excel("trans",query,left,fields,htab.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_movement_fields/csv")>0:
    return export2csv("trans",query,left,fields,htab.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.movement_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.fieldvalue.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_lorry.png')
  response.export_excel = ruri.replace("find_movement_groups","find_movement_groups/excel")
  response.export_csv = ruri.replace("find_movement_groups","find_movement_groups/csv")
  response.view=dir_view+'/browser.html'
  set_find_movement_menu()
  
  def get_find_movement_groups_filter():  
    data_fields_label = [ns.db.trans.transnumber.label,ns.db.groups.groupvalue.label,ns.db.groups.description.label]
    data_fields_name = ["htab_trans_transnumber",ns.db.groups.groupvalue.name,ns.db.groups.description.name]
    
    return create_filter_form(sfilter_name="movement_groups_filter",state_fields=["invtype","direction"],
                                         bool_fields=None, date_fields=None, number_fields=None,
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_movement_groups_filter()
  
  nervatype_trans = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
  nervatype_groups = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
    
  join = [(ns.db.link.on((ns.db.trans.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0))),
          (ns.db.groups.on((ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.ref_id_2==ns.db.groups.id)))]
  
  query = ((ns.db.trans.deleted==0)&(ns.db.groups.deleted==0))
  
  where = get_filter_query(sfilter=session.movement_groups_filter,table="groups",query=query)
  query = where["query"]
  
  #set transtype
  query = query & (ns.db.trans.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("delivery","inventory","waybill","production","formula"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = set_transfilter(query)
      
  fields = [ns.db.trans.transnumber,ns.db.groups.groupvalue,ns.db.groups.description]
  left = None
  if ruri.find("find_movement_groups/excel")>0:
    return export2excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_movement_groups/csv")>0:
    return export2csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.movement_groups_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.trans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
  return dict(form=form)

@ns_auth.requires_login()
def find_transitem_quick_all():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_transitem_quick_all")+24:]
    redirect(URL(ruri))
  return find_transitem_quick(("invoice","receipt","order","offer","worksheet","rent"))

@ns_auth.requires_login()
def find_transitem_quick_delivery():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_shipping"+ruri[ruri.find("find_transitem_quick_delivery")+29:]
    redirect(URL(ruri))
  return find_transitem_quick(("order","worksheet","rent"))

def find_transitem_quick(transtype=None):  
  response.view=dir_view+'/gridform.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select document')
  response.margin_top = "20px"
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
    response.cmd_back = get_back_button(session.back_url)
  else:
    response.cmd_back = get_home_button()
  response.titleicon = URL(dir_images,'icon16_find.png')
  
  transtype_invoice_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
  transtype_receipt_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="receipt")).select().as_list()[0]["id"]
  direction_out_id = ns.db((ns.db.groups.groupname=="direction")&(ns.db.groups.groupvalue=="out")).select().as_list()[0]["id"]
  
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
  fields = [ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, ns.db.trans.customer_id, ns.db.trans.transdate]
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = set_transfilter(query)
    
  ns.db.trans.transdate.label = T("Date")
  ns.db.groups.groupvalue.label = T("Doc.type")
  smenu = [ns.db.trans.transnumber,ns.db.trans.transdate,ns.db.customer.custname,ns.db.groups.groupvalue]
  search_widget = create_search_widget(smenu)

  form = SQLFORM.grid(query=query, field_id=ns.db.trans.id, fields=fields, left=left, #headers=headers,
               orderby=ns.db.trans.id, sortable=True, paginate=10, maxtextlength=25,
               searchable=True, csv=False, details=False, showbuttontext=False,
               create=False, deletable=False, editable=True, selectable=False, 
               user_signature=False, search_widget=search_widget)
  if type(form[1][0][0]).__name__=="TABLE":
    form=move_buttons(form)
  set_counter_bug(form)
  return dict(form=DIV(form, _id="dlg_frm"))
    
def set_find_transitem_menu():
  response.lo_menu = []
  mnu_trans = (T('TRANSACTIONS'), False, None, [])
  mnu_trans[3].append((T('Documents'), False, URL('find_transitem_trans'), []))
  mnu_trans[3].append((T('Additional Data'), False, URL('find_transitem_fields'), []))
  mnu_trans[3].append((T('Document rows'), False, URL('find_transitem_item'), []))
  mnu_trans[3].append((T('Groups'), False, URL('find_transitem_groups'), []))
  response.lo_menu.append(mnu_trans)
  
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
  response.titleicon = URL(dir_images,'icon16_find.png')
  response.export_excel = ruri.replace("find_transitem_trans","find_transitem_trans/excel")
  response.export_csv = ruri.replace("find_transitem_trans","find_transitem_trans/csv")
  response.view=dir_view+'/browser.html'
  set_find_transitem_menu()
  
  def get_find_transitem_trans_filter(quick_total):  
    bool_fields_name = [ns.db.trans.paid.name,ns.db.trans.closed.name]
    bool_fields_label = [ns.db.trans.paid.label,ns.db.trans.closed.label]
    
    date_fields_name = [ns.db.trans.crdate.name,ns.db.trans.transdate.name,ns.db.trans.duedate.name]
    date_fields_label = [ns.db.trans.crdate.label,ns.db.trans.transdate.label,ns.db.trans.duedate.label]
    
    number_fields_name = [ns.db.item.netamount.name,ns.db.item.vatamount.name,ns.db.item.amount.name,ns.db.trans.acrate.name]
    number_fields_label = [ns.db.item.netamount.label,ns.db.item.vatamount.label,ns.db.item.amount.label,ns.db.trans.acrate.label]
    
    data_fields_name = [ns.db.trans.transnumber.name, ns.db.trans.ref_transnumber.name, ns.db.trans.customer_id.name, 
                        ns.db.trans.employee_id.name, ns.db.trans.department.name, ns.db.trans.project_id.name, ns.db.trans.paidtype.name, 
                        ns.db.trans.curr.name, ns.db.trans.notes.name, ns.db.trans.intnotes.name]
    data_fields_label = [ns.db.trans.transnumber.label, ns.db.trans.ref_transnumber.label, ns.db.trans.customer_id.label, 
                        ns.db.trans.employee_id.label, ns.db.trans.department.label, ns.db.trans.project_id.label, ns.db.trans.paidtype.label, 
                        ns.db.trans.curr.label, ns.db.trans.notes.label, ns.db.trans.intnotes.label]
    
    return create_filter_form(sfilter_name="transitem_trans_filter",state_fields=["transtype","direction","transtate","transcast"],
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},
                                         number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label},
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label},
                                         quick_total=quick_total)
  
  transtype_invoice_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
  transtype_receipt_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="receipt")).select().as_list()[0]["id"]
  direction_out_id = ns.db((ns.db.groups.groupname=="direction")&(ns.db.groups.groupvalue=="out")).select().as_list()[0]["id"]
  
  fields = [ns.db.trans.transtype, ns.db.trans.direction, ns.db.fieldvalue.value, ns.db.trans.transnumber, ns.db.trans.ref_transnumber,
            ns.db.trans.crdate, ns.db.trans.transdate, ns.db.trans.duedate, ns.db.trans.customer_id, ns.db.trans.employee_id, ns.db.trans.department,
            ns.db.trans.project_id, ns.db.trans.paidtype, ns.db.trans.curr,
            ns.db.item.netamount, ns.db.item.vatamount, ns.db.item.amount,
            ns.db.trans.paid, ns.db.trans.acrate, ns.db.trans.notes, ns.db.trans.intnotes, ns.db.trans.transtate, ns.db.trans.closed, ns.db.trans.deleted]
  left = [(ns.db.item.on((ns.db.trans.id==ns.db.item.trans_id)&(ns.db.item.deleted==0))),
          (ns.db.fieldvalue.on((ns.db.trans.id==ns.db.fieldvalue.ref_id)&(ns.db.fieldvalue.fieldname=='trans_transcast')&(ns.db.fieldvalue.deleted==0)))]
  join = None
  
  query = ((ns.db.trans.deleted==0)|((ns.db.trans.transtype==transtype_invoice_id)&(ns.db.trans.direction==direction_out_id))
           |((ns.db.trans.transtype==transtype_receipt_id)&(ns.db.trans.direction==direction_out_id)))
  
  init_sfilter("transitem_trans_filter")
  where = get_filter_query(sfilter=session.transitem_trans_filter,table="trans",query=query)
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
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = set_transfilter(query)
    
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
  
  if ruri.find("find_transitem_trans/excel")>0:
    return export2excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,
                        join=join,groupfields=groupfields,groupby=groupby,having=having)
  if ruri.find("find_transitem_trans/csv")>0:
    return export2csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,
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
  
  response.filter_form = get_find_transitem_trans_filter(quick_total)
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=groupfields, groupby=groupby, left=left, having=having, join=join,
             orderby=order, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_find.png')
  response.export_excel = ruri.replace("find_transitem_fields","find_transitem_fields/excel")
  response.export_csv = ruri.replace("find_transitem_fields","find_transitem_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_transitem_menu()
  response.filter_form = get_fields_filter("trans","transitem_fields_filter",["transtype","direction","transtate","transcast"])
  
  nervatype_trans = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
  
  transtype_invoice_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
  transtype_receipt_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="receipt")).select().as_list()[0]["id"]
  direction_out_id = ns.db((ns.db.groups.groupname=="direction")&(ns.db.groups.groupvalue=="out")).select().as_list()[0]["id"]
  
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
  
  where = get_filter_query(sfilter=session.transitem_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  #set transtype
  query = query & (htab.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("offer","order","worksheet","rent","invoice","receipt"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~htab.transtype.belongs(audit))
  
  #set transfilter
  query = set_transfilter(query,htab)
        
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id, htab.transnumber, ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  if ruri.find("find_transitem_fields/excel")>0:
    return export2excel("trans",query,left,fields,htab.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_transitem_fields/csv")>0:
    return export2csv("trans",query,left,fields,htab.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.transitem_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_corrected.png')
  response.export_excel = ruri.replace("find_transitem_item","find_transitem_item/excel")
  response.export_csv = ruri.replace("find_transitem_item","find_transitem_item/csv")
  response.view=dir_view+'/browser.html'
  set_find_transitem_menu()
  
  def get_find_transitem_item_filter(quick_total):
    bool_fields_name = [ns.db.item.deposit.name, ns.db.item.actionprice.name, ns.db.item.ownstock.name]
    bool_fields_label = [ns.db.item.deposit.label, ns.db.item.actionprice.label, ns.db.item.ownstock.label]
    
    date_fields_name = [ns.db.trans.transdate.name]
    date_fields_label = [ns.db.trans.transdate.label]
    
    number_fields_name = [ns.db.item.qty.name, ns.db.item.fxprice.name,ns.db.item.netamount.name, ns.db.item.discount.name,ns.db.item.vatamount.name, ns.db.item.amount.name]
    number_fields_label = [ns.db.item.qty.label, ns.db.item.fxprice.label,ns.db.item.netamount.label, ns.db.item.discount.label,ns.db.item.vatamount.label, ns.db.item.amount.label]
    
    data_fields_name = [ns.db.item.trans_id.name, "htab_trans_curr", ns.db.item.product_id.name, ns.db.item.description.name, 
                        ns.db.item.unit.name, ns.db.item.tax_id.name]
    data_fields_label = [ns.db.item.trans_id.label, ns.db.trans.curr.label, ns.db.item.product_id.label, ns.db.item.description.label, 
                        ns.db.item.unit.label, ns.db.item.tax_id.label]
    
    return create_filter_form(sfilter_name="transitem_item_filter",state_fields=["transtype","direction","transtate","transcast"],
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},
                                         number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label},
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label},
                                         quick_total=quick_total)
  
  transtype_invoice_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
  transtype_receipt_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="receipt")).select().as_list()[0]["id"]
  direction_out_id = ns.db((ns.db.groups.groupname=="direction")&(ns.db.groups.groupvalue=="out")).select().as_list()[0]["id"]
  
  join = [(ns.db.item.on((ns.db.trans.id==ns.db.item.trans_id)&(ns.db.item.deleted==0)))]
  query = ((ns.db.trans.deleted==0)|((ns.db.trans.transtype==transtype_invoice_id)&(ns.db.trans.direction==direction_out_id))
           |((ns.db.trans.transtype==transtype_receipt_id)&(ns.db.trans.direction==direction_out_id)))
  
  init_sfilter("transitem_item_filter")
  where = get_filter_query(sfilter=session.transitem_item_filter,table="item",query=query)
  query = where["query"]
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = set_transfilter(query)
      
  fields = [ns.db.trans.transtype, ns.db.trans.direction, ns.db.item.trans_id, ns.db.trans.transdate, 
            ns.db.trans.curr, ns.db.item.product_id, ns.db.item.description, ns.db.item.unit, ns.db.item.qty, ns.db.item.fxprice,
            ns.db.item.netamount, ns.db.item.discount, ns.db.item.tax_id, ns.db.item.vatamount, ns.db.item.amount,
            ns.db.item.deposit, ns.db.item.actionprice, ns.db.item.ownstock]
  left = None
  
  ns.db.item.deposit.label = T('Deposit/Option')
  
  if ruri.find("find_transitem_item/excel")>0:
    return export2excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_transitem_item/csv")>0:
    return export2csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.transitem_item_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
  
  quick_total={"netamount":0,"vatamount":0,"amount":0}
  total_rows = ns.db(query).select(*[ns.db.item.netamount.sum().with_alias('netamount'),ns.db.item.vatamount.sum().with_alias('vatamount'),ns.db.item.amount.sum().with_alias('amount')],
                      join=join,left=left,groupby=None,having=None).as_list()
  if len(total_rows)>0:
    if total_rows[0]["netamount"]:
      quick_total={"netamount":total_rows[0]["netamount"],"vatamount":total_rows[0]["vatamount"],"amount":total_rows[0]["amount"]}
  response.filter_form = get_find_transitem_item_filter(quick_total)
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.trans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_find.png')
  response.export_excel = ruri.replace("find_transitem_groups","find_transitem_groups/excel")
  response.export_csv = ruri.replace("find_transitem_groups","find_transitem_groups/csv")
  response.view=dir_view+'/browser.html'
  set_find_transitem_menu()
  
  def get_find_transitem_groups_filter():  
    data_fields_label = [ns.db.trans.transnumber.label,ns.db.groups.groupvalue.label,ns.db.groups.description.label]
    data_fields_name = ["htab_trans_transnumber",ns.db.groups.groupvalue.name,ns.db.groups.description.name]
    
    return create_filter_form(sfilter_name="transitem_groups_filter",state_fields=["transtype","direction"],
                                         bool_fields=None, date_fields=None, number_fields=None,
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_transitem_groups_filter()
  
  nervatype_trans = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
  nervatype_groups = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  
  transtype_invoice_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
  transtype_receipt_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="receipt")).select().as_list()[0]["id"]
  transtype_cash_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="cash")).select().as_list()[0]["id"]
  direction_out_id = ns.db((ns.db.groups.groupname=="direction")&(ns.db.groups.groupvalue=="out")).select().as_list()[0]["id"]
  
  join = [(ns.db.link.on((ns.db.trans.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0))),
          (ns.db.groups.on((ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.ref_id_2==ns.db.groups.id)))]
  
  query = ((ns.db.trans.deleted==0)|((ns.db.trans.transtype==transtype_invoice_id)&(ns.db.trans.direction==direction_out_id))
           |((ns.db.trans.transtype==transtype_receipt_id)&(ns.db.trans.direction==direction_out_id)&(ns.db.groups.deleted==0))
           |((ns.db.trans.transtype==transtype_cash_id)))
  
  where = get_filter_query(sfilter=session.transitem_groups_filter,table="groups",query=query)
  query = where["query"]
  
  #set transtype
  query = query & (ns.db.trans.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("offer","order","worksheet","rent","invoice","receipt"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = set_transfilter(query)
      
  fields = [ns.db.trans.transnumber,ns.db.groups.groupvalue,ns.db.groups.description]
  left = None
  if ruri.find("find_transitem_groups/excel")>0:
    return export2excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_transitem_groups/csv")>0:
    return export2csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.transitem_groups_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.trans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
  return dict(form=form)

@ns_auth.requires_login()
def find_payment_quick():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_trans"+ruri[ruri.find("find_payment_quick")+18:]
    redirect(URL(ruri))
      
  response.view=dir_view+'/gridform.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select document')
  response.margin_top = "20px"
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
    response.cmd_back = get_back_button(session.back_url)
  else:
    response.cmd_back = get_home_button()
  response.titleicon = URL(dir_images,'icon16_find.png')
  
  transtype_cash_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="cash")).select().as_list()[0]["id"]
  query = (((ns.db.trans.deleted==0)|(ns.db.trans.transtype==transtype_cash_id))
           &(ns.db.trans.id==ns.db.payment.trans_id)&(ns.db.payment.deleted==0)
           &(ns.db.trans.place_id==ns.db.place.id)&(ns.db.trans.transtype==ns.db.groups.id))
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
    
  #set transfilter
  query = set_transfilter(query)
      
  fields = [ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.place_id, ns.db.payment.paiddate, 
            ns.db.place.curr, ns.db.payment.amount] 
  
  ns.db.groups.groupvalue.label = T("Doc.Type")
  ns.db.trans.place_id.label = T("Bank/Ch.")
  smenu = [ns.db.trans.transnumber,ns.db.payment.paiddate,ns.db.place.planumber,ns.db.groups.groupvalue,ns.db.place.curr, 
           ns.db.payment.amount]
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False:
    query = query & (ns.db.trans.id==-1)
  search_widget = create_search_widget(smenu)

  form = SQLFORM.grid(query=query, field_id=ns.db.trans.id, fields=fields, #headers=headers,
               orderby=ns.db.trans.id, sortable=True, paginate=10, maxtextlength=25,
               searchable=True, csv=False, details=False, showbuttontext=False,
               create=False, deletable=False, editable=True, selectable=False, 
               user_signature=False, search_widget=search_widget)
  if type(form[1][0][0]).__name__=="TABLE":
    form=move_buttons(form)
  set_counter_bug(form)
  return dict(form=DIV(form, _id="dlg_frm"))

def set_find_payment_menu():
  response.lo_menu = []
  mnu_payment = (T('PAYMENT VIEWS'), False, None, [])
  mnu_payment[3].append((T('Payments Data'), False, URL('find_payment_payment'), []))
  mnu_payment[3].append((T('Additional Data'), False, URL('find_payment_fields'), []))
  audit_filter = get_audit_filter("trans", "invoice")[0]
  if audit_filter!="disabled":
    mnu_payment[3].append((T('Invoice assignments'), False, URL('find_payment_invoice'), []))
  mnu_payment[3].append((T('Documents Groups'), False, URL('find_payment_groups'), []))
  response.lo_menu.append(mnu_payment)

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
  response.titleicon = URL(dir_images,'icon16_money.png')
  response.export_excel = ruri.replace("find_payment_payment","find_payment_payment/excel")
  response.export_csv = ruri.replace("find_payment_payment","find_payment_payment/csv")
  response.view=dir_view+'/browser.html'
  set_find_payment_menu()
  
  def get_find_payment_payment_filter(quick_total):
    bool_fields_name = [ns.db.trans.closed.name, ns.db.trans.deleted.name]
    bool_fields_label = [ns.db.trans.closed.label, ns.db.trans.deleted.label]
    
    date_fields_name = [ns.db.trans.crdate.name, ns.db.payment.paiddate.name]
    date_fields_label = [ns.db.trans.crdate.label, ns.db.payment.paiddate.label]
    
    number_fields_name = ["paidamount"]
    number_fields_label = [ns.db.payment.amount.label]
    
    data_fields_name = ["transnumber", ns.db.trans.ref_transnumber.name, ns.db.trans.place_id.name, "place_curr", 
                        "payment_description", ns.db.trans.employee_id.name, ns.db.trans.notes.name]
    data_fields_label = [ns.db.payment.trans_id.label, ns.db.trans.ref_transnumber.label, ns.db.trans.place_id.label, ns.db.place.curr.label, 
                        ns.db.payment.notes.label, ns.db.trans.employee_id.label, ns.db.trans.notes.label]
    
    return create_filter_form(sfilter_name="payment_payment_filter",state_fields=["paymtype","direction","transtate","transcast"],
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},
                                         number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label},
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label},
                                         quick_total=quick_total)
  
  transtype_cash_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="cash")).select().as_list()[0]["id"]
  
  join = [(ns.db.payment.on((ns.db.trans.id==ns.db.payment.trans_id)&(ns.db.payment.deleted==0))),
          (ns.db.place.on((ns.db.trans.place_id==ns.db.place.id)))]
  query = ((ns.db.trans.deleted==0)|(ns.db.trans.transtype==transtype_cash_id))
  
  init_sfilter("payment_payment_filter")
  where = get_filter_query(sfilter=session.payment_payment_filter,table="trans",query=query)
  query = where["query"]
  left = [(ns.db.fieldvalue.on((ns.db.trans.id==ns.db.fieldvalue.ref_id)&(ns.db.fieldvalue.fieldname=='trans_transcast')&(ns.db.fieldvalue.deleted==0)))]
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
    
  #set transfilter
  query = set_transfilter(query)
      
  fields = [ns.db.trans.transtype, ns.db.trans.direction, ns.db.fieldvalue.value, ns.db.payment.trans_id, ns.db.trans.ref_transnumber, 
            ns.db.trans.crdate, ns.db.payment.paiddate, ns.db.trans.place_id, ns.db.place.curr, ns.db.payment.amount,
            ns.db.payment.notes, ns.db.trans.employee_id, ns.db.trans.transtate, ns.db.trans.closed, ns.db.trans.deleted, ns.db.trans.notes]
  
  if ruri.find("find_payment_payment/excel")>0:
    return export2excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_payment_payment/csv")>0:
    return export2csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.payment_payment_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
  
  quick_total={"amount":0}
  total_rows = ns.db(query).select(*[ns.db.payment.amount.sum().with_alias('amount')],
                      join=join,left=left,groupby=None,having=None).as_list()
  if len(total_rows)>0:
    if total_rows[0]["amount"]:
      quick_total={"amount":total_rows[0]["amount"]}
  response.filter_form = get_find_payment_payment_filter(quick_total)
  
  ns.db.fieldvalue.value.label = T('Doc.State')
  ns.db.trans.crdate.label = T('Date')
  ns.db.trans.place_id.label = T('BankAcc/Checkout')
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.trans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_find.png')
  response.export_excel = ruri.replace("find_payment_fields","find_payment_fields/excel")
  response.export_csv = ruri.replace("find_payment_fields","find_payment_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_payment_menu()
  response.filter_form = get_fields_filter("trans","payment_fields_filter",["paymtype","direction","transtate","transcast"])
  
  nervatype_trans = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]  
  transtype_cash_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="cash")).select().as_list()[0]["id"]
  
  htab = ns.db.trans.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(ns.db.fieldvalue.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_trans)))]
  query = (ns.db.fieldvalue.deleted==0)
  query = query & ((htab.deleted==0)|(htab.transtype==transtype_cash_id))
  
  where = get_filter_query(sfilter=session.payment_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  #set transtype
  query = query & (htab.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("bank","cash"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~htab.transtype.belongs(audit))
    
  #set transfilter
  query = set_transfilter(query,htab)
        
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id, htab.transnumber, ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  if ruri.find("find_payment_fields/excel")>0:
    return export2excel("trans",query,left,fields,htab.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_payment_fields/csv")>0:
    return export2csv("trans",query,left,fields,htab.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.payment_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.fieldvalue.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_invoice.png')
  response.export_excel = ruri.replace("find_payment_invoice","find_payment_invoice/excel")
  response.export_csv = ruri.replace("find_payment_invoice","find_payment_invoice/csv")
  response.view=dir_view+'/browser.html'
  set_find_payment_menu()
  
  ptrans = ns.db.trans.with_alias('ptrans')
  itrans = ns.db.trans.with_alias('itrans')
  link_qty = ns.db.fieldvalue.with_alias('link_qty')
  link_rate = ns.db.fieldvalue.with_alias('link_rate')
  
  ptrans.place_id.label = T('BankAcc/Checkout')
  itrans.transnumber.label = T('Invoice No.')
  itrans.curr.label = T('Inv.Curr')
  link_qty.value.label = T('Amount')
  link_qty.value.represent = lambda value,row: formatNumber(row["link_qty"]["value"])
  link_rate.value.label = T('Rate')
  link_rate.value.represent = lambda value,row: formatNumber(row["link_rate"]["value"])
  
  def get_find_payment_invoice_filter(quick_total):
    
    date_fields_name = [ns.db.payment.paiddate.name]
    date_fields_label = [ns.db.payment.paiddate.label]
    
    number_fields_name = ["link_qty","link_rate"]
    number_fields_label = [link_qty.value.label, link_rate.value.label]
    
    data_fields_name = ["place", "docnumber", "doc_curr", "invnumber", "inv_curr"]
    data_fields_label = [ptrans.place_id.label, ptrans.transnumber.label, ns.db.place.curr.label, itrans.transnumber.label, 
                         itrans.curr.label]
    
    return create_filter_form(sfilter_name="payment_invoice_filter",state_fields=["paymtype","direction","transtate"],
                                         bool_fields=None,
                                         date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},
                                         number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label},
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label},
                                         quick_total=quick_total)
  
  nervatype_trans = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]  
  nervatype_payment = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="payment")).select().as_list()[0]["id"]
  transtype_cash_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="cash")).select().as_list()[0]["id"]
  
  join = [(ns.db.payment.on((ns.db.link.ref_id_1==ns.db.payment.id)&(ns.db.payment.deleted==0))),
          (ptrans.on((ns.db.payment.trans_id==ptrans.id)&((ptrans.deleted==0)|(ptrans.transtype==transtype_cash_id)))),
          (ns.db.place.on((ptrans.place_id==ns.db.place.id)&(ns.db.place.deleted==0))),
          (itrans.on((ns.db.link.ref_id_2==itrans.id)&(itrans.deleted==0))),
          (link_qty.on((ns.db.link.id==link_qty.ref_id)&(link_qty.fieldname=="link_qty")&(link_qty.deleted==0))),
          (link_rate.on((ns.db.link.id==link_rate.ref_id)&(link_rate.fieldname=="link_rate")&(link_rate.deleted==0)))]
  query = ((ns.db.link.deleted==0)&(ns.db.link.nervatype_1==nervatype_payment)&(ns.db.link.nervatype_2==nervatype_trans))
  
  init_sfilter("payment_invoice_filter")
  where = get_filter_query(sfilter=session.payment_invoice_filter,table="payment_invoice",query=query)
  query = where["query"]
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.ptrans.transtype.belongs(audit))
    
  #set transfilter
  query = set_transfilter(query,ptrans)
        
  fields = [ptrans.transtype, ptrans.direction, ns.db.payment.paiddate, ptrans.place_id, ptrans.transnumber,
            ns.db.place.curr, link_qty.value, link_rate.value, itrans.transnumber, itrans.curr]
  left = None
  if ruri.find("find_payment_invoice/excel")>0:
    return export2excel("trans",query,left,fields,ptrans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_payment_invoice/csv")>0:
    return export2csv("trans",query,left,fields,ptrans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.payment_invoice_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.payment.id==-1))
  
  quick_total={"amount":0}
  total_rows = ns.db(query).select(*[("sum(cast(link_qty.value as real))")],
                      join=join,left=left,groupby=None,having=None).as_list()
  if len(total_rows)>0:
    quick_total={"amount":total_rows[0].values()[0].values()[0]}
  response.filter_form = get_find_payment_invoice_filter(quick_total)
    
  form = SimpleGrid.grid(query=query, field_id=ptrans.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ptrans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_find.png')
  response.export_excel = ruri.replace("find_payment_groups","find_payment_groups/excel")
  response.export_csv = ruri.replace("find_payment_groups","find_payment_groups/csv")
  response.view=dir_view+'/browser.html'
  set_find_payment_menu()
  
  def get_find_payment_groups_filter():  
    data_fields_label = [ns.db.trans.transnumber.label,ns.db.groups.groupvalue.label,ns.db.groups.description.label]
    data_fields_name = ["htab_trans_transnumber",ns.db.groups.groupvalue.name,ns.db.groups.description.name]
    
    return create_filter_form(sfilter_name="payment_groups_filter",state_fields=["paymtype","direction"],
                                         bool_fields=None, date_fields=None, number_fields=None,
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_payment_groups_filter()
  
  nervatype_trans = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
  nervatype_groups = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  
  transtype_cash_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue=="cash")).select().as_list()[0]["id"]
  
  join = [(ns.db.link.on((ns.db.trans.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_trans)&(ns.db.link.deleted==0))),
          (ns.db.groups.on((ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.ref_id_2==ns.db.groups.id)))]
  
  query = ((ns.db.trans.deleted==0)|((ns.db.trans.transtype==transtype_cash_id)))
  
  where = get_filter_query(sfilter=session.payment_groups_filter,table="groups",query=query)
  query = where["query"]
  
  #set transtype
  query = query & (ns.db.trans.transtype.belongs(ns.db(ns.db.groups.groupname.like('transtype')
                  &ns.db.groups.groupvalue.belongs(("cash","bank"))).select(ns.db.groups.id)))
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
    
  #set transfilter
  query = set_transfilter(query)
      
  fields = [ns.db.trans.transnumber,ns.db.groups.groupvalue,ns.db.groups.description]
  left = None
  if ruri.find("find_payment_groups/excel")>0:
    return export2excel("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  if ruri.find("find_payment_groups/csv")>0:
    return export2csv("trans",query,left,fields,ns.db.trans.transnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.payment_groups_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.trans.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.trans.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.trans.transnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
  return dict(form=form)

@ns_auth.requires_login()
def find_project_quick():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_project"+ruri[ruri.find("find_project_quick")+18:]
    redirect(URL(ruri))
      
  response.view=dir_view+'/gridform.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select project')
  response.margin_top = "20px"
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
    response.cmd_back = get_back_button(session.back_url)
  else:
    response.cmd_back = get_home_button()
  response.titleicon = URL(dir_images,'icon16_find.png')
  
  query = ((ns.db.project.deleted==0))
  fields = [ns.db.project.pronumber, ns.db.project.description, ns.db.project.startdate, ns.db.project.enddate, ns.db.project.customer_id]
  left = (ns.db.customer.on(ns.db.project.customer_id==ns.db.customer.id))
  smenu = [ns.db.project.pronumber, ns.db.project.description, ns.db.project.startdate, ns.db.project.enddate, ns.db.customer.custname]
  ns.db.project.startdate.represent = lambda value,row: formatDate(row["startdate"])
  ns.db.project.enddate.represent = lambda value,row: formatDate(row["enddate"])
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False:
    query = query & (ns.db.project.id==-1)
  search_widget = create_search_widget(smenu)

  form = SQLFORM.grid(query=query, field_id=ns.db.project.id, fields=fields, left=left, #headers=headers,
               orderby=ns.db.project.id, sortable=True, paginate=10, maxtextlength=25,
               searchable=True, csv=False, details=False, showbuttontext=False,
               create=False, deletable=False, editable=True, selectable=False, 
               user_signature=False, search_widget=search_widget)
  if type(form[1][0][0]).__name__=="TABLE":
    form=move_buttons(form)
  set_counter_bug(form)
  return dict(form=DIV(form, _id="dlg_frm"))
  
def set_find_project_menu():
  response.lo_menu = []
  mnu_project = (T('PROJECT VIEWS'), False, None, [])
  mnu_project[3].append((T('Project Data'), False, URL('find_project_project'), []))
  mnu_project[3].append((T('Additional Data'), False, URL('find_project_fields'), []))
  mnu_project[3].append((T('Contact Persons'), False, URL('find_project_contact'), []))
  mnu_project[3].append((T('Addresses'), False, URL('find_project_address'), []))
  audit_filter = get_audit_filter("event", None)[0]
  if audit_filter!="disabled":
    mnu_project[3].append((T('Events'), False, URL('find_project_event'), []))
  response.lo_menu.append(mnu_project)
  
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
  response.titleicon = URL(dir_images,'icon16_date_edit.png')
  response.export_excel = ruri.replace("find_project_project","find_project_project/excel")
  response.export_csv = ruri.replace("find_project_project","find_project_project/csv")
  response.view=dir_view+'/browser.html'
  set_find_project_menu()
  
  def get_find_project_project_filter():  
    bool_fields_name = [ns.db.project.inactive.name]
    bool_fields_label = [ns.db.project.inactive.label]
    
    date_fields_name = [ns.db.project.startdate.name, ns.db.project.enddate.name]
    date_fields_label = [ns.db.project.startdate.label, ns.db.project.enddate.label]
    
    data_fields_name = [ns.db.project.pronumber.name, ns.db.project.description.name, ns.db.project.customer_id.name, ns.db.project.notes.name]
    data_fields_label = [ns.db.project.pronumber.label, ns.db.project.description.label, ns.db.project.customer_id.label, ns.db.project.notes.label]
    
    return create_filter_form(sfilter_name="project_project_filter",state_fields=None,
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},
                                         number_fields=None,
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_project_project_filter()
  
  query = ((ns.db.project.deleted==0))
  where = get_filter_query(sfilter=session.project_project_filter,table="project",query=query)
  query = where["query"]
  
  fields = [ns.db.project.pronumber, ns.db.project.description, ns.db.project.customer_id, ns.db.project.startdate, 
            ns.db.project.enddate, ns.db.project.inactive, ns.db.project.notes]
  left = None
  if ruri.find("find_project_project/excel")>0:
    return export2excel("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords)
  if ruri.find("find_project_project/csv")>0:
    return export2csv("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.project_project_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.project.id==-1))
  
  audit_filter = get_audit_filter("project", None)[0]  
  form = SimpleGrid.grid(query=query, field_id=ns.db.project.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=None,
             orderby=ns.db.project.pronumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, create=(audit_filter=="all"), links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_date_edit.png')
  response.export_excel = ruri.replace("find_project_fields","find_project_fields/excel")
  response.export_csv = ruri.replace("find_project_fields","find_project_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_project_menu()
  nervatype_project = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="project")).select().as_list()[0]["id"]
  response.filter_form = get_fields_filter("project","project_fields_filter")
  
  htab = ns.db.project.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_project)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = get_filter_query(sfilter=session.project_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.pronumber,htab.description,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_project_fields/excel")>0:
    return export2excel("project",query,left,fields,htab.pronumber,request.vars.keywords,join=join)
  if ruri.find("find_project_fields/csv")>0:
    return export2csv("project",query,left,fields,htab.pronumber,request.vars.keywords,join=join)
  
  audit_filter = get_audit_filter("project", None)[0]
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.project_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.pronumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, create=(audit_filter=="all"), links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_user.png')
  response.export_excel = ruri.replace("find_project_contact","find_project_contact/excel")
  response.export_csv = ruri.replace("find_project_contact","find_project_contact/csv")
  response.view=dir_view+'/browser.html'
  set_find_project_menu()
  
  def get_find_project_contact_filter():
    data_fields_name = ["htab_project_pronumber", "htab_project_description", ns.db.contact.firstname.name, ns.db.contact.surname.name,
                        ns.db.contact.status.name, ns.db.contact.phone.name, ns.db.contact.fax.name, ns.db.contact.mobil.name, ns.db.contact.email.name, ns.db.contact.notes.name]
    data_fields_label = [ns.db.project.pronumber.label, ns.db.project.description.label, ns.db.contact.firstname.label, ns.db.contact.surname.label,
                        ns.db.contact.status.label, ns.db.contact.phone.label, ns.db.contact.fax.label, ns.db.contact.mobil.label, ns.db.contact.email.label, ns.db.contact.notes.label]
    
    return create_filter_form(sfilter_name="project_contact_filter",state_fields=None,bool_fields=None,date_fields=None,number_fields=None,
                              data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_project_contact_filter()
  
  nervatype_project = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="project")).select().as_list()[0]["id"]
  
  join = [(ns.db.contact.on((ns.db.project.id==ns.db.contact.ref_id)&(ns.db.contact.nervatype==nervatype_project)&(ns.db.contact.deleted==0)))]
  query = (ns.db.project.deleted==0)
  
  where = get_filter_query(sfilter=session.project_contact_filter,table="contact",query=query)
  query = where["query"]
  
  fields = [ns.db.contact.id, ns.db.project.description, ns.db.contact.firstname,ns.db.contact.surname,
            ns.db.contact.status,ns.db.contact.phone,ns.db.contact.fax,ns.db.contact.mobil,ns.db.contact.email,ns.db.contact.notes]
  left = None
  
  if ruri.find("find_project_contact/excel")>0:
    return export2excel("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords,join=join)
  if ruri.find("find_project_contact/csv")>0:
    return export2csv("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.project_contact_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.project.id==-1))
  
  ns.db.contact.id.label = T("Contact No.")
  ns.db.contact.id.represent = lambda value,row: SPAN(ns.show_refnumber("refnumber","contact", value))  
  form = SimpleGrid.grid(query=query, field_id=ns.db.project.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.project.pronumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_address.png')
  response.export_excel = ruri.replace("find_project_address","find_project_address/excel")
  response.export_csv = ruri.replace("find_project_address","find_project_address/csv")
  response.view=dir_view+'/browser.html'
  set_find_project_menu()
  
  def get_find_project_address_filter():
    data_fields_name = ["htab_project_pronumber", "htab_project_description", ns.db.address.country.name, ns.db.address.state.name,
              ns.db.address.zipcode.name, ns.db.address.city.name, ns.db.address.street.name, ns.db.address.notes.name]
    data_fields_label = [ns.db.project.pronumber.label, ns.db.project.description.label, ns.db.address.country.label, ns.db.address.state.label,
              ns.db.address.zipcode.label, ns.db.address.city.label, ns.db.address.street.label, ns.db.address.notes.label]
    
    return create_filter_form(sfilter_name="project_address_filter",state_fields=None,bool_fields=None,date_fields=None,number_fields=None,
                              data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_project_address_filter()
  
  nervatype_project = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="project")).select().as_list()[0]["id"]
  join = [(ns.db.address.on((ns.db.project.id==ns.db.address.ref_id)&(ns.db.address.nervatype==nervatype_project)&(ns.db.address.deleted==0)))]
  query = (ns.db.project.deleted==0)
  
  where = get_filter_query(sfilter=session.project_address_filter,table="address",query=query)
  query = where["query"]
  
  fields = [ns.db.address.id, ns.db.project.description,ns.db.address.country,ns.db.address.state,
            ns.db.address.zipcode,ns.db.address.city,ns.db.address.street,ns.db.address.notes]
  left = None
  if ruri.find("find_project_address/excel")>0:
    return export2excel("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords,join=join)
  if ruri.find("find_project_address/csv")>0:
    return export2csv("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.project_address_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.project.id==-1))
  
  ns.db.address.id.label = T("Address No.")
  ns.db.address.id.represent = lambda value,row: SPAN(ns.show_refnumber("refnumber","address", value))  
  form = SimpleGrid.grid(query=query, field_id=ns.db.project.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.project.pronumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
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
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  response.export_excel = ruri.replace("find_project_event","find_project_event/excel")
  response.export_csv = ruri.replace("find_project_event","find_project_event/csv")
  response.view=dir_view+'/browser.html'
  set_find_project_menu()
  
  def get_find_project_event_filter():
    date_fields_name = [ns.db.event.fromdate.name,ns.db.event.todate.name]
    date_fields_label = [ns.db.event.fromdate.label,ns.db.event.todate.label]
    
    data_fields_name = [ns.db.event.calnumber.name, "htab_project_pronumber", "htab_project_description", 
                        ns.db.event.eventgroup.name, ns.db.event.subject.name, ns.db.event.place.name, ns.db.event.description.name]
    data_fields_label = [ns.db.event.calnumber.label, ns.db.project.pronumber.label, ns.db.project.description.label, 
                        ns.db.event.eventgroup.label, ns.db.event.subject.label, ns.db.event.place.label, ns.db.event.description.label]
    
    more_data = {"title":"Event Additional Data","caption":"Additional Data","url":URL('find_project_event_fields')}
    
    return create_filter_form(sfilter_name="project_event_filter",state_fields=None,bool_fields=None,
                              date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},number_fields=None,
                              data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label},more_data=more_data)
  response.filter_form = get_find_project_event_filter()
  
  ns.db.event.ref_id.represent = lambda value,row: A(SPAN(ns.db.project(id=int(value))["pronumber"]),
                     _href=URL(r=request, f="frm_project/view/project/"+str(value)), _target="_blank")
  ns.db.event.ref_id.label=T('Project No.')
  nervatype_project = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="project")).select().as_list()[0]["id"]
  
  join = [(ns.db.event.on((ns.db.project.id==ns.db.event.ref_id)&(ns.db.event.nervatype==nervatype_project)&(ns.db.event.deleted==0)))]
  left = [(ns.db.groups.on((ns.db.event.eventgroup==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  query = (ns.db.project.deleted==0)
  
  where = get_filter_query(sfilter=session.project_event_filter,table="event",query=query)
  query = where["query"]
  
  fields = [ns.db.event.calnumber,ns.db.event.ref_id, ns.db.project.description, ns.db.event.eventgroup,
            ns.db.event.fromdate,ns.db.event.todate,ns.db.event.subject,ns.db.event.place,ns.db.event.description]
  if ruri.find("find_project_event/excel")>0:
    return export2excel("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords,join=join)
  if ruri.find("find_project_event/csv")>0:
    return export2csv("project",query,left,fields,ns.db.project.pronumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.project_event_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.project.id==-1))
    
  links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("export2ical?id="+str(row.event.id)), _target="_blank", _title=T("Export Item"))]
  form = SimpleGrid.grid(query=query, field_id=ns.db.event.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.project.pronumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=links)
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
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  response.export_excel = ruri.replace("find_project_event_fields","find_project_event_fields/excel")
  response.export_csv = ruri.replace("find_project_event_fields","find_project_event_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_project_menu()
  nervatype_event = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="event")).select().as_list()[0]["id"]
  nervatype_project = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="project")).select().as_list()[0]["id"]
  response.filter_form = get_fields_filter("event","project_event_fields_filter")
  
  htab = ns.db.event.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(htab.nervatype==nervatype_project))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_event)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = get_filter_query(sfilter=session.project_event_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.calnumber,htab.subject,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_project_event_fields/excel")>0:
    return export2excel("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  if ruri.find("find_project_event_fields/csv")>0:
    return export2csv("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.project_event_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.calnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
  return dict(form=form)

def get_find_project_trans_filter():
  
  date_fields_name = [ns.db.trans.transdate.name]
  date_fields_label = [ns.db.trans.transdate.label]
  
  data_fields_name = [ns.db.trans.transnumber.name, "htab_project_pronumber", "htab_project_description", 
                      ns.db.trans.transtype.name, ns.db.trans.direction.name, ns.db.trans.curr.name, ns.db.trans.customer_id.name]
  data_fields_label = [ns.db.trans.transnumber.label, ns.db.project.pronumber.label, ns.db.project.description.label, 
                      ns.db.trans.transtype.label, ns.db.trans.direction.label, ns.db.trans.curr.label, ns.db.trans.customer_id.label]
  
  return create_filter_form(sfilter_name="project_trans_filter",state_fields=None,bool_fields=None,
                            date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},number_fields=None,
                            data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})

@ns_auth.requires_login()
def find_customer_quick():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_customer"+ruri[ruri.find("find_customer_quick")+19:]
    redirect(URL(ruri))
      
  response.view=dir_view+'/gridform.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select customer')
  response.margin_top = "20px"
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
    response.cmd_back = get_back_button(session.back_url)
  else:
    response.cmd_back = get_home_button()
  response.titleicon = URL(dir_images,'icon16_find.png')
  
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.id!=1)&(ns.db.customer.custtype==ns.db.groups.id))  
  fields = [ns.db.customer.custnumber, ns.db.customer.custname, ns.db.customer.custtype, ns.db.customer.inactive]
  
  left = None
  smenu = [ns.db.customer.custnumber, ns.db.customer.custname, ns.db.groups.groupvalue]
  ns.db.groups.groupvalue.label = T("Type")
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False:
    query = query & (ns.db.customer.id==-1)
  search_widget = create_search_widget(smenu)

  form = SQLFORM.grid(query=query, field_id=ns.db.customer.id, fields=fields, left=left, #headers=headers,
               orderby=ns.db.customer.id, sortable=True, paginate=10, maxtextlength=25,
               searchable=True, csv=False, details=False, showbuttontext=False,
               create=False, deletable=False, editable=True, selectable=False, 
               user_signature=False, search_widget=search_widget)
  if type(form[1][0][0]).__name__=="TABLE":
    form=move_buttons(form)
  set_counter_bug(form)
  return dict(form=DIV(form, _id="dlg_frm"))
  
def set_find_customer_menu():
  response.lo_menu = []
  mnu_customer = (T('CUSTOMER VIEWS'), False, None, [])
  mnu_customer[3].append((T('Customer Data'), False, URL('find_customer_customer'), []))
  mnu_customer[3].append((T('Additional Data'), False, URL('find_customer_fields'), []))
  mnu_customer[3].append((T('Contact Persons'), False, URL('find_customer_contact'), []))
  mnu_customer[3].append((T('Addresses'), False, URL('find_customer_address'), []))
  mnu_customer[3].append((T('Groups'), False, URL('find_customer_groups'), []))
  audit_filter = get_audit_filter("event", None)[0]
  if audit_filter!="disabled":
    mnu_customer[3].append((T('Events'), False, URL('find_customer_event'), []))
  response.lo_menu.append(mnu_customer)

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
  response.titleicon = URL(dir_images,'icon16_customer.png')
  response.export_excel = ruri.replace("find_customer_customer","find_customer_customer/excel")
  response.export_csv = ruri.replace("find_customer_customer","find_customer_customer/csv")
  response.view=dir_view+'/browser.html'
  set_find_customer_menu()
  
  def get_find_customer_customer_filter():  
    bool_fields_name = [ns.db.customer.notax.name, ns.db.customer.inactive.name]
    bool_fields_label = [ns.db.customer.notax.label, ns.db.customer.inactive.label]
    
    number_fields_name = [ns.db.customer.terms.name, ns.db.customer.creditlimit.name, ns.db.customer.discount.name]
    number_fields_label = [ns.db.customer.terms.label, ns.db.customer.creditlimit.label, ns.db.customer.discount.label]
    
    data_fields_name = [ns.db.customer.custnumber.name, ns.db.customer.custname.name, ns.db.customer.taxnumber.name, ns.db.customer.custtype.name, 
            ns.db.customer.account.name, ns.db.customer.notes.name, "htab_address_city", "htab_address_street"]
    data_fields_label = [ns.db.customer.custnumber.label, ns.db.customer.custname.label, ns.db.customer.taxnumber.label, ns.db.customer.custtype.label, 
            ns.db.customer.account.label, ns.db.customer.notes.label, ns.db.address.city.label, ns.db.address.street.label]
    
    return create_filter_form(sfilter_name="customer_customer_filter",state_fields=None,
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label},
                                         date_fields=None,
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_customer_customer_filter()
  
  nervatype_customer = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.id!=1))
  
  where = get_filter_query(sfilter=session.customer_customer_filter,table="customer",query=query)
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
    return export2excel("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords)
  if ruri.find("find_customer_customer/csv")>0:
    return export2csv("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_customer_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.customer.id==-1))
  
  audit_filter = get_audit_filter("customer", None)[0]  
  form = SimpleGrid.grid(query=query, field_id=ns.db.customer.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=None,
             orderby=ns.db.customer.custname, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, create=(audit_filter=="all"), links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_customer.png')
  response.export_excel = ruri.replace("find_customer_fields","find_customer_fields/excel")
  response.export_csv = ruri.replace("find_customer_fields","find_customer_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_customer_menu()
  nervatype_customer = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
  response.filter_form = get_fields_filter("customer","customer_fields_filter")
  
  htab = ns.db.customer.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(htab.id>1))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_customer)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = get_filter_query(sfilter=session.customer_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.custnumber,htab.custname,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None

  if ruri.find("find_customer_fields/excel")>0:
    return export2excel("customer",query,left,fields,htab.custname,request.vars.keywords,join=join)
  if ruri.find("find_customer_fields/csv")>0:
    return export2csv("customer",query,left,fields,htab.custname,request.vars.keywords,join=join)
  
  audit_filter = get_audit_filter("customer", None)[0]
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.custname, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, create=(audit_filter=="all"), links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_user.png')
  response.export_excel = ruri.replace("find_customer_contact","find_customer_contact/excel")
  response.export_csv = ruri.replace("find_customer_contact","find_customer_contact/csv")
  response.view=dir_view+'/browser.html'
  set_find_customer_menu()
  
  def get_find_customer_contact_filter():
    data_fields_name = ["htab_customer_custnumber", "htab_customer_custname", ns.db.contact.firstname.name, ns.db.contact.surname.name,
                        ns.db.contact.status.name, ns.db.contact.phone.name, ns.db.contact.fax.name, ns.db.contact.mobil.name, ns.db.contact.email.name, ns.db.contact.notes.name]
    data_fields_label = [ns.db.customer.custnumber.label, ns.db.customer.custname.label, ns.db.contact.firstname.label, ns.db.contact.surname.label,
                        ns.db.contact.status.label, ns.db.contact.phone.label, ns.db.contact.fax.label, ns.db.contact.mobil.label, ns.db.contact.email.label, ns.db.contact.notes.label]
    
    return create_filter_form(sfilter_name="customer_contact_filter",state_fields=None,bool_fields=None,date_fields=None,number_fields=None,
                              data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_customer_contact_filter()
  
  nervatype_customer = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
  
  join = [(ns.db.contact.on((ns.db.customer.id==ns.db.contact.ref_id)&(ns.db.contact.nervatype==nervatype_customer)&(ns.db.contact.deleted==0)))]
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.id>1))
  
  where = get_filter_query(sfilter=session.customer_contact_filter,table="contact",query=query)
  query = where["query"]
  
  fields = [ns.db.contact.id, ns.db.customer.custname, ns.db.contact.firstname,ns.db.contact.surname,
            ns.db.contact.status,ns.db.contact.phone,ns.db.contact.fax,ns.db.contact.mobil,ns.db.contact.email,ns.db.contact.notes]
  left = None
  
  if ruri.find("find_customer_contact/excel")>0:
    return export2excel("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  if ruri.find("find_customer_contact/csv")>0:
    return export2csv("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_contact_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.customer.id==-1))
  
  ns.db.contact.id.label = T("Contact No.")
  ns.db.contact.id.represent = lambda value,row: SPAN(ns.show_refnumber("refnumber","contact", value))  
  form = SimpleGrid.grid(query=query, field_id=ns.db.customer.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.customer.custname, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
  return dict(form=form)

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
  response.titleicon = URL(dir_images,'icon16_address.png')
  response.export_excel = ruri.replace("find_customer_address","find_customer_address/excel")
  response.export_csv = ruri.replace("find_customer_address","find_customer_address/csv")
  response.view=dir_view+'/browser.html'
  set_find_customer_menu()
  
  def get_find_customer_address_filter():
    data_fields_name = ["htab_customer_custnumber", "htab_customer_custname", ns.db.address.country.name, ns.db.address.state.name,
              ns.db.address.zipcode.name, ns.db.address.city.name, ns.db.address.street.name, ns.db.address.notes.name]
    data_fields_label = [ns.db.customer.custnumber.label, ns.db.customer.custname.label, ns.db.address.country.label, ns.db.address.state.label,
              ns.db.address.zipcode.label, ns.db.address.city.label, ns.db.address.street.label, ns.db.address.notes.label]
    
    return create_filter_form(sfilter_name="customer_address_filter",state_fields=None,bool_fields=None,date_fields=None,number_fields=None,
                              data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_customer_address_filter()
  
  nervatype_customer = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
  join = [(ns.db.address.on((ns.db.customer.id==ns.db.address.ref_id)&(ns.db.address.nervatype==nervatype_customer)&(ns.db.address.deleted==0)))]
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.id>1))
  
  where = get_filter_query(sfilter=session.customer_address_filter,table="customer",query=query)
  query = where["query"]
  
  fields = [ns.db.address.id,ns.db.customer.custname,ns.db.address.country,ns.db.address.state,
            ns.db.address.zipcode,ns.db.address.city,ns.db.address.street,ns.db.address.notes]
  left = None
  if ruri.find("find_customer_address/excel")>0:
    return export2excel("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  if ruri.find("find_customer_address/csv")>0:
    return export2csv("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_address_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.customer.id==-1))
  
  ns.db.address.id.label = T("Address No.")
  ns.db.address.id.represent = lambda value,row: SPAN(ns.show_refnumber("refnumber","address", value))  
  form = SimpleGrid.grid(query=query, field_id=ns.db.customer.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.customer.custname, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
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
  response.titleicon = URL(dir_images,'icon16_customer.png')
  response.export_excel = ruri.replace("find_customer_groups","find_customer_groups/excel")
  response.export_csv = ruri.replace("find_customer_groups","find_customer_groups/csv")
  response.view=dir_view+'/browser.html'
  set_find_customer_menu()
  
  def get_find_customer_groups_filter():  
    data_fields_label = [ns.db.customer.custnumber.label,ns.db.customer.custname.label,ns.db.groups.groupvalue.label,ns.db.groups.description.label]
    data_fields_name = ["htab_customer_custnumber","htab_customer_custname",ns.db.groups.groupvalue.name,ns.db.groups.description.name]
    
    return create_filter_form(sfilter_name="customer_groups_filter",state_fields=None,
                                         bool_fields=None, date_fields=None, number_fields=None,
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_customer_groups_filter()
  
  nervatype_customer = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
  nervatype_groups = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  
  join = [(ns.db.link.on((ns.db.customer.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_customer)&(ns.db.link.deleted==0))),
          (ns.db.groups.on((ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.ref_id_2==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.id!=1))
  
  where = get_filter_query(sfilter=session.customer_groups_filter,table="groups",query=query)
  query = where["query"]
  
  fields = [ns.db.customer.custnumber, ns.db.customer.custname,ns.db.groups.groupvalue,ns.db.groups.description]
  left = None
  
  if ruri.find("find_customer_groups/excel")>0:
    return export2excel("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  if ruri.find("find_customer_groups/csv")>0:
    return export2csv("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_groups_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.customer.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.customer.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.customer.custname, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  response.export_excel = ruri.replace("find_customer_event","find_customer_event/excel")
  response.export_csv = ruri.replace("find_customer_event","find_customer_event/csv")
  response.view=dir_view+'/browser.html'
  set_find_customer_menu()
  
  def get_find_customer_event_filter():
    date_fields_name = [ns.db.event.fromdate.name,ns.db.event.todate.name]
    date_fields_label = [ns.db.event.fromdate.label,ns.db.event.todate.label]
    
    data_fields_name = [ns.db.event.calnumber.name, "htab_customer_custnumber", "htab_customer_custname", 
                        ns.db.event.eventgroup.name, ns.db.event.subject.name, ns.db.event.place.name, ns.db.event.description.name]
    data_fields_label = [ns.db.event.calnumber.label, ns.db.customer.custnumber.label, ns.db.customer.custname.label, 
                        ns.db.event.eventgroup.label, ns.db.event.subject.label, ns.db.event.place.label, ns.db.event.description.label]
    
    more_data = {"title":"Event Additional Data","caption":"Additional Data","url":URL('find_customer_event_fields')}
    
    return create_filter_form(sfilter_name="customer_event_filter",state_fields=None,bool_fields=None,
                              date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},number_fields=None,
                              data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label},more_data=more_data)
  response.filter_form = get_find_customer_event_filter()
  
  ns.db.event.ref_id.represent = lambda value,row: A(SPAN(ns.db.customer(id=int(value))["custname"]),
                     _href=URL(r=request, f="frm_customer/view/customer/"+str(value)), _target="_blank")
  ns.db.event.ref_id.label=T('Customer')
  nervatype_customer = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
  
  join = [(ns.db.event.on((ns.db.customer.id==ns.db.event.ref_id)&(ns.db.event.nervatype==nervatype_customer)&(ns.db.event.deleted==0)))]
  left = [(ns.db.groups.on((ns.db.event.eventgroup==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.id!=1))
  
  where = get_filter_query(sfilter=session.customer_event_filter,table="event",query=query)
  query = where["query"]
  
  fields = [ns.db.event.calnumber,ns.db.customer.custnumber, ns.db.event.ref_id, ns.db.event.eventgroup,
            ns.db.event.fromdate,ns.db.event.todate,ns.db.event.subject,ns.db.event.place,ns.db.event.description]
  
  if ruri.find("find_customer_event/excel")>0:
    return export2excel("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  if ruri.find("find_customer_event/csv")>0:
    return export2csv("customer",query,left,fields,ns.db.customer.custname,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_event_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.customer.id==-1))
  
  links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("export2ical?id="+str(row.event.id)), _target="_blank", _title=T("Export Item"))]  
  form = SimpleGrid.grid(query=query, field_id=ns.db.event.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.customer.custname, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=links)
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
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  response.export_excel = ruri.replace("find_customer_event_fields","find_customer_event_fields/excel")
  response.export_csv = ruri.replace("find_customer_event_fields","find_customer_event_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_customer_menu()
  nervatype_event = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="event")).select().as_list()[0]["id"]
  nervatype_customer = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
  response.filter_form = get_fields_filter("event","customer_event_fields_filter")
  
  htab = ns.db.event.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(htab.nervatype==nervatype_customer))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_event)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = get_filter_query(sfilter=session.customer_event_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.calnumber,htab.subject,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_customer_event_fields/excel")>0:
    return export2excel("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  if ruri.find("find_customer_event_fields/csv")>0:
    return export2csv("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.customer_event_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.calnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
  return dict(form=form)

@ns_auth.requires_login()
def find_product_quick():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_product"+ruri[ruri.find("find_product_quick")+18:]
    redirect(URL(ruri))
      
  response.view=dir_view+'/gridform.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select product')
  response.margin_top = "20px"
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
    response.cmd_back = get_back_button(session.back_url)
  else:
    response.cmd_back = get_home_button()
  response.titleicon = URL(dir_images,'icon16_find.png')
  
  query = ((ns.db.product.deleted==0)&(ns.db.product.protype==ns.db.groups.id))
  fields = [ns.db.product.partnumber, ns.db.product.protype, ns.db.product.description, ns.db.product.unit, ns.db.product.inactive]
  left = None
  
  smenu = [ns.db.product.partnumber, ns.db.groups.groupvalue, ns.db.product.description, ns.db.product.unit]
  ns.db.groups.groupvalue.label = T("Type")
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False:
    query = query & (ns.db.product.id==-1)
  search_widget = create_search_widget(smenu)

  form = SQLFORM.grid(query=query, field_id=ns.db.product.id, fields=fields, left=left, #headers=headers,
               orderby=ns.db.product.id, sortable=True, paginate=10, maxtextlength=25,
               searchable=True, csv=False, details=False, showbuttontext=False,
               create=False, deletable=False, editable=True, selectable=False, 
               user_signature=False, search_widget=search_widget)
  if type(form[1][0][0]).__name__=="TABLE":
    form=move_buttons(form)
  set_counter_bug(form)
  return dict(form=DIV(form, _id="dlg_frm"))

def set_find_product_menu():
  response.lo_menu = []
  mnu_product = (T('PRODUCT VIEWS'), False, None, [])
  mnu_product[3].append((T('Product Data'), False, URL('find_product_product'), []))
  mnu_product[3].append((T('Additional Data'), False, URL('find_product_fields'), []))
  mnu_product[3].append((T('Groups'), False, URL('find_product_groups'), []))
  mnu_product[3].append((T('Barcode'), False, URL('find_product_barcode'), []))
  audit_filter = get_audit_filter("price", None)[0]
  if audit_filter!="disabled":
    mnu_product[3].append((T('Price'), False, URL('find_product_price'), []))
    mnu_product[3].append((T('Discount'), False, URL('find_product_discount'), []))
  audit_filter = get_audit_filter("event", None)[0]
  if audit_filter!="disabled":
    mnu_product[3].append((T('Events'), False, URL('find_product_event'), []))
  response.lo_menu.append(mnu_product)

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
  response.titleicon = URL(dir_images,'icon16_parts.png')
  response.export_excel = ruri.replace("find_product_product","find_product_product/excel")
  response.export_csv = ruri.replace("find_product_product","find_product_product/csv")
  response.view=dir_view+'/browser.html'
  set_find_product_menu()
  
  def get_find_product_product_filter():
    bool_fields_name = [ns.db.product.webitem.name, ns.db.product.inactive.name]
    bool_fields_label = [ns.db.product.webitem.label, ns.db.product.inactive.label]
    
    data_fields_name = [ns.db.product.partnumber.name, ns.db.product.protype.name, ns.db.product.description.name, ns.db.product.unit.name, 
            ns.db.product.tax_id.name, ns.db.product.notes.name]
    data_fields_label = [ns.db.product.partnumber.label, ns.db.product.protype.label, ns.db.product.description.label, ns.db.product.unit.label, 
            ns.db.product.tax_id.label, ns.db.product.notes.label]
    
    return create_filter_form(sfilter_name="product_product_filter",state_fields=None,
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         number_fields=None, date_fields=None,
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_product_product_filter()
  
  query = (ns.db.product.deleted==0)
  fields = [ns.db.product.partnumber, ns.db.product.protype, ns.db.product.description, ns.db.product.unit, 
            ns.db.product.tax_id, ns.db.product.notes, ns.db.product.webitem, ns.db.product.inactive]
  left = None
  
  where = get_filter_query(sfilter=session.product_product_filter,table="product",query=query)
  query = where["query"]
  
  if ruri.find("find_product_product/excel")>0:
    return export2excel("product",query,left,fields,ns.db.product.description,request.vars.keywords)
  if ruri.find("find_product_product/csv")>0:
    return export2csv("product",query,left,fields,ns.db.product.description,request.vars.keywords)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_product_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.product.id==-1))
  
  audit_filter = get_audit_filter("product", None)[0]  
  form = SimpleGrid.grid(query=query, field_id=ns.db.product.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=None,
             orderby=ns.db.product.description, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, create=(audit_filter=="all"), links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_parts.png')
  response.export_excel = ruri.replace("find_product_fields","find_product_fields/excel")
  response.export_csv = ruri.replace("find_product_fields","find_product_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_product_menu()
  nervatype_product = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="product")).select().as_list()[0]["id"]
  response.filter_form = get_fields_filter("product","product_fields_filter")
  
  htab = ns.db.product.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_product)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = get_filter_query(sfilter=session.product_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.partnumber,htab.description,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_product_fields/excel")>0:
    return export2excel("product",query,left,fields,htab.description,request.vars.keywords,join=join)
  if ruri.find("find_product_fields/csv")>0:
    return export2csv("product",query,left,fields,htab.description,request.vars.keywords,join=join)
  
  audit_filter = get_audit_filter("product", None)[0]
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.description, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, create=(audit_filter=="all"), links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_parts.png')
  response.export_excel = ruri.replace("find_product_groups","find_product_groups/excel")
  response.export_csv = ruri.replace("find_product_groups","find_product_groups/csv")
  response.view=dir_view+'/browser.html'
  set_find_product_menu()
  
  def get_find_product_groups_filter():  
    data_fields_label = [ns.db.product.partnumber.label,ns.db.product.description.label,ns.db.groups.groupvalue.label,ns.db.groups.description.label]
    data_fields_name = ["htab_product_partnumber","htab_product_description",ns.db.groups.groupvalue.name,ns.db.groups.description.name]
    
    return create_filter_form(sfilter_name="product_groups_filter",state_fields=None,
                                         bool_fields=None, date_fields=None, number_fields=None,
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_product_groups_filter()
  
  nervatype_product = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="product")).select().as_list()[0]["id"]
  nervatype_groups = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  
  join = [(ns.db.link.on((ns.db.product.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==nervatype_product)&(ns.db.link.deleted==0))),
          (ns.db.groups.on((ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.ref_id_2==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  
  query = (ns.db.product.deleted==0)
  
  where = get_filter_query(sfilter=session.product_groups_filter,table="groups",query=query)
  query = where["query"]
  
  fields = [ns.db.product.partnumber, ns.db.product.description,ns.db.groups.groupvalue,ns.db.groups.description]
  left = None
  
  if ruri.find("find_product_groups/excel")>0:
    return export2excel("product",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  if ruri.find("find_product_groups/csv")>0:
    return export2csv("product",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_groups_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.product.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.product.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.product.description, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_barcode.png')
  response.export_excel = ruri.replace("find_product_barcode","find_product_barcode/excel")
  response.export_csv = ruri.replace("find_product_barcode","find_product_barcode/csv")
  response.view=dir_view+'/browser.html'
  set_find_product_menu()
  
  def get_find_product_barcode_filter():    
    bool_fields_name = [ns.db.barcode.defcode.name]
    bool_fields_label = [ns.db.barcode.defcode.label]
    
    number_fields_name = [ns.db.barcode.qty.name]
    number_fields_label = [ns.db.barcode.qty.label]
    
    data_fields_name = ["htab_product_partnumber","htab_product_description", ns.db.barcode.code.name, 
                        ns.db.barcode.description.name, "htab_groups_groupvalue"]
    data_fields_label = [ns.db.product.partnumber.label, ns.db.product.description.label, ns.db.barcode.code.label, 
                        ns.db.barcode.description.label, ns.db.barcode.barcodetype.label]
    
    return create_filter_form(sfilter_name="product_barcode_filter",state_fields=None,
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label}, 
                                         date_fields=None,
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_product_barcode_filter()
  
  join = [ns.db.barcode.on((ns.db.barcode.product_id==ns.db.product.id)),
          ns.db.groups.on((ns.db.groups.id==ns.db.barcode.barcodetype))]
  left = None
  query = ((ns.db.product.deleted==0))
  
  where = get_filter_query(sfilter=session.product_barcode_filter,table="barcode",query=query)
  query = where["query"]
  
  fields = [ns.db.product.partnumber, ns.db.barcode.product_id, ns.db.barcode.code,ns.db.barcode.description,
            ns.db.barcode.barcodetype,ns.db.barcode.qty,ns.db.barcode.defcode]
  
  if ruri.find("find_product_barcode/excel")>0:
    return export2excel("product",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  if ruri.find("find_product_barcode/csv")>0:
    return export2csv("product",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_barcode_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.product.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.product.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=ns.db.product.description, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
  return dict(form=form)

@ns_auth.requires_login()
def find_product_price():
  audit_filter = get_audit_filter("price", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
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
    if delete_row("price", price_id, "product", product_id):
      redirect(URL('find_product_price/view/product/'+str(product_id)))
  
  nervatype_price = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="price")).select().as_list()[0]["id"]
  nervatype_customer = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
  nervatype_groups = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
        
  if request.post_vars["_formname"]=="price/create":
    clear_post_vars()
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
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.price.id==request.post_vars["id"]).update(**request.post_vars)
        if customer_id:
          linkrow = ns.db((ns.db.link.ref_id_1==request.post_vars["id"])&(ns.db.link.nervatype_1==nervatype_price)&(ns.db.link.nervatype_2==nervatype_customer)&(ns.db.link.deleted==0)).select()
          if len(linkrow)>0:
            ns.db(ns.db.link.id==linkrow[0]["id"]).update(**{"ref_id_2":customer_id})
          else:
            values = {"nervatype_1":nervatype_price, "ref_id_1":request.post_vars["id"], "nervatype_2":nervatype_customer, "ref_id_2":customer_id}
            ns.db.link.insert(**values)
        else:
          ns.db((ns.db.link.ref_id_1==request.post_vars["id"])&(ns.db.link.nervatype_1==nervatype_price)&(ns.db.link.nervatype_2==nervatype_customer)).delete()  
        if group_id:
          linkrow = ns.db((ns.db.link.ref_id_1==request.post_vars["id"])&(ns.db.link.nervatype_1==nervatype_price)&(ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.deleted==0)).select()
          if len(linkrow)>0:
            ns.db(ns.db.link.id==linkrow[0]["id"]).update(**{"ref_id_2":group_id})
          else:
            values = {"nervatype_1":nervatype_price, "ref_id_1":request.post_vars["id"], "nervatype_2":nervatype_groups, "ref_id_2":group_id}
            ns.db.link.insert(**values)
        else:
          ns.db((ns.db.link.ref_id_1==request.post_vars["id"])&(ns.db.link.nervatype_1==nervatype_price)&(ns.db.link.nervatype_2==nervatype_groups)).delete() 
      else:
        request.post_vars["id"] = ns.db.price.insert(**request.post_vars)
        if customer_id:
          values = {"nervatype_1":nervatype_price, "ref_id_1":request.post_vars["id"], "nervatype_2":nervatype_customer, "ref_id_2":customer_id}
          ns.db.link.insert(**values)
        if group_id:
          values = {"nervatype_1":nervatype_price, "ref_id_1":request.post_vars["id"], "nervatype_2":nervatype_groups, "ref_id_2":group_id}
          ns.db.link.insert(**values)
      setLogtable("update", "log_product_update", "product", request.post_vars["product_id"])
      redirect(URL('find_product_price/view/product/'+str(request.post_vars["product_id"])))
    except Exception, err:
      response.flash = str(err)
    
  response.titleicon = URL(dir_images,'icon16_money.png')
  response.export_excel = ruri.replace("find_product_price","find_product_price/excel")
  response.export_csv = ruri.replace("find_product_price","find_product_price/csv")
  response.view=dir_view+'/browser.html'
  
  custlink = ns.db.link.with_alias('custlink')
  ns.db.customer.id.represent = lambda value,row: A(SPAN(ns.db.customer(id=int(value))["custname"]),
                     _href=URL(r=request, f="frm_customer/view/customer/"+str(value)), _target="_blank")
  ns.db.customer.id.label=T('Customer')
  grouplink = ns.db.link.with_alias('grouplink')
  
  def get_find_product_price_filter():        
    bool_fields_name = [ns.db.price.vendorprice.name]
    bool_fields_label = [ns.db.price.vendorprice.label]
    
    number_fields_name = [ns.db.price.qty.name, ns.db.price.pricevalue.name]
    number_fields_label = [ns.db.price.qty.label, ns.db.price.pricevalue.label]
    
    date_fields_name = [ns.db.price.validfrom.name, ns.db.price.validto.name]
    date_fields_label = [ns.db.price.validfrom.label, ns.db.price.validto.label]
    
    data_fields_name = ["htab_product_partnumber", "htab_product_description", "htab_product_unit", "htab_customer_custname", 
                        "htab_groups_groupvalue", ns.db.price.curr.name]
    data_fields_label = [ns.db.product.partnumber.label, ns.db.product.description.label, ns.db.product.unit.label, 
                         ns.db.customer.id.label, ns.db.groups.groupvalue.label, ns.db.price.curr.label]
    
    return create_filter_form(sfilter_name="product_price_filter",state_fields=["pricetype"],
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label}, 
                                         date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  if product_id:
    response.browsertype=T('PRICE')
    response.subtitle= ns.db.product(id=product_id).partnumber +" - "+ ns.db.product(id=product_id).description
    response.cmd_back = get_back_button(URL("frm_product/view/product/"+str(product_id)))
    response.lo_menu = []
    query = (ns.db.product.id==product_id)
    _sortable = False
    _orderby=ns.db.price.validfrom
    ns.db.groups.id.readable = False
    ns.db.customer.custname.readable = False
    fields = [ns.db.customer.id, ns.db.customer.custname, ns.db.groups.id, ns.db.groups.groupvalue, ns.db.price.validfrom,ns.db.price.validto,ns.db.price.curr, 
              ns.db.price.qty, ns.db.price.pricevalue,ns.db.price.vendorprice]
    
    response.edit_form = SQLFORM(ns.db.price, submit_button=T("Save"),_id="frm_edit")
    response.edit_form.process()
    _field_id=ns.db.price.id
    def_calcmode = ns.db((ns.db.groups.groupname=="calcmode")&(ns.db.groups.groupvalue=="amo")).select().as_list()[0]["id"]
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
    if audit_filter!="readonly":
      response.cmd_edit_submit = get_command_button(caption=T("Save"),title=T("Update price data"),color="008B00", _id="cmd_edit_submit",
                              cmd="price_update();return true;")
    response.edit_title = T("PRICE")
    response.edit_icon = URL(dir_images,'icon16_money.png')
    response.cmd_edit_cancel = A(SPAN(_class="icon cross"), _id="cmd_edit_cancel", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_form').style.display = 'none';return true;")
    if audit_filter=="all":
      response.cmd_edit_new = A(SPAN(_class="icon plus"), _id="cmd_edit_new", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('New Price'), 
        _onclick= "set_price(-1,'"+str(datetime.datetime.now().date())+"','','"+getSetting("default_currency")+"',0,0,'',"+str(def_calcmode)+",0,'','','','"+json.dumps(str(T("New value")))[1:-1]+"');")
    response.edit_id = INPUT(_name="id", _type="hidden", _value="", _id="edit_id")
    cust_groups = ns.db((ns.db.groups.groupname=="customer")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.groupvalue)
    response.cmb_groups = SELECT(*[OPTION(group.groupvalue, _value=group.id) for group in cust_groups], _id="price_group_id", _name="group_id")
    response.cmb_groups.insert(0, OPTION("", _value=""))
    response.edit_items = DIV(
                            TABLE(TR(
                                 TD(DIV(response.edit_form.custom.label.validfrom,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.validfrom,
                                    _style="width: 70px;padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 5px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.validto,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.validto,
                                    _style="width: 70px;padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 5px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.curr,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.curr,
                                    _style="width: 60px;padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 0px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.qty,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 5px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.qty,
                                    _style="width: 60px;padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 10px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.pricevalue,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 5px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.pricevalue,
                                    _style="padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 20px;padding-left: 5px;")
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;"),
                            TABLE(TR(
                                 TD(DIV(T("Group"),_style="width: 80px;", _class="label"),
                                    _style="padding-top: 5px;padding-bottom: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.cmb_groups,
                                    INPUT(_name="product_id", _type="hidden", _value=product_id, _id="price_product_id"),
                                    INPUT(_name="calcmode", _type="hidden", _value=def_calcmode, _id="price_calcmode"),
                                    INPUT(_name="discount", _type="hidden", _value="", _id="price_discount"),
                                    _style="width: 175px;padding: 0px;padding-top: 0px;padding-bottom: 5px;vertical-align: middle;padding-right: 5px;padding-left: 5px;"),
                                 TD(DIV(T("Customer"),_style="width: 80px;", _class="label"),
                                    _style="padding-top: 5px;padding-bottom: 10px;width: 80px;padding-right: 0px;padding-left: 0px;", _class="td_label"),
                                 TD(INPUT(_name="customer_id", _type="hidden", _value="", _id="customer_id"),get_customer_selector("", width="100%"),
                                    _style="padding: 0px;padding-top: 0px;padding-bottom: 5px;vertical-align: middle;padding-right: 5px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.vendorprice,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 5px;padding-bottom: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.vendorprice,
                                    _style="width: 10px;padding: 0px;padding-top: 5px;padding-bottom: 5px;vertical-align: top;padding-right: 10px;padding-left: 5px;")
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;")
                            )
    
  else:
    response.browsertype=T('Product Browser')
    response.subtitle=T('Price')
    set_find_product_menu()
    response.filter_form = get_find_product_price_filter()
    query = (ns.db.product.deleted==0)
    where = get_filter_query(sfilter=session.product_price_filter,table="price",query=query)
    query = where["query"]
    _sortable = True
    _orderby=ns.db.product.description
    if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_price_filter)==0 and len(request.post_vars)==0:
      query = (query&(ns.db.product.id==-1))
    fields = [ns.db.product.partnumber, ns.db.price.product_id, ns.db.product.unit, ns.db.customer.id, ns.db.groups.groupvalue,
            ns.db.price.validfrom,ns.db.price.validto,ns.db.price.curr, ns.db.price.qty, ns.db.price.pricevalue,ns.db.price.vendorprice]
    _field_id=ns.db.product.id
    _links=None
  
  join = [ns.db.price.on((ns.db.price.product_id==ns.db.product.id)&(ns.db.price.deleted==0)&(ns.db.price.discount==None))]
  
  left = [custlink.on((ns.db.price.id==custlink.ref_id_1)&(custlink.nervatype_1==nervatype_price)
                            &(custlink.nervatype_2==nervatype_customer)&(custlink.deleted==0)),
          ns.db.customer.on((custlink.ref_id_2==ns.db.customer.id)&(ns.db.customer.deleted==0)),
          grouplink.on((ns.db.price.id==grouplink.ref_id_1)&(grouplink.nervatype_1==nervatype_price)
                            &(grouplink.nervatype_2==nervatype_groups)&(grouplink.deleted==0)),
          ns.db.groups.on((grouplink.ref_id_2==ns.db.groups.id)&(ns.db.groups.deleted==0))]
  
  if ruri.find("find_product_price/excel")>0:
    return export2excel("price",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  if ruri.find("find_product_price/csv")>0:
    return export2csv("price",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
    
  form = SimpleGrid.grid(query=query, field_id=_field_id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.product.description, sortable=_sortable, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=_sortable, links=_links)
  
  return dict(form=form)

@ns_auth.requires_login()
def find_product_discount():
  audit_filter = get_audit_filter("price", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
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
    if delete_row("price", price_id, "product", product_id):
      redirect(URL('find_product_discount/view/product/'+str(product_id)))
      
  nervatype_price = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="price")).select().as_list()[0]["id"]
  nervatype_customer = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
  nervatype_groups = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  
  if request.post_vars["_formname"]=="price/create":
    clear_post_vars()
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
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.price.id==request.post_vars["id"]).update(**request.post_vars)
        if customer_id:
          linkrow = ns.db((ns.db.link.ref_id_1==request.post_vars["id"])&(ns.db.link.nervatype_1==nervatype_price)&(ns.db.link.nervatype_2==nervatype_customer)&(ns.db.link.deleted==0)).select()
          if len(linkrow)>0:
            ns.db(ns.db.link.id==linkrow[0]["id"]).update(**{"ref_id_2":customer_id})
          else:
            values = {"nervatype_1":nervatype_price, "ref_id_1":request.post_vars["id"], "nervatype_2":nervatype_customer, "ref_id_2":customer_id}
            ns.db.link.insert(**values)
        else:
          ns.db((ns.db.link.ref_id_1==request.post_vars["id"])&(ns.db.link.nervatype_1==nervatype_price)&(ns.db.link.nervatype_2==nervatype_customer)).delete()  
        if group_id:
          linkrow = ns.db((ns.db.link.ref_id_1==request.post_vars["id"])&(ns.db.link.nervatype_1==nervatype_price)&(ns.db.link.nervatype_2==nervatype_groups)&(ns.db.link.deleted==0)).select()
          if len(linkrow)>0:
            ns.db(ns.db.link.id==linkrow[0]["id"]).update(**{"ref_id_2":group_id})
          else:
            values = {"nervatype_1":nervatype_price, "ref_id_1":request.post_vars["id"], "nervatype_2":nervatype_groups, "ref_id_2":group_id}
            ns.db.link.insert(**values)
        else:
          ns.db((ns.db.link.ref_id_1==request.post_vars["id"])&(ns.db.link.nervatype_1==nervatype_price)&(ns.db.link.nervatype_2==nervatype_groups)).delete() 
      else:
        request.post_vars["id"] = ns.db.price.insert(**request.post_vars)
        if customer_id:
          values = {"nervatype_1":nervatype_price, "ref_id_1":request.post_vars["id"], "nervatype_2":nervatype_customer, "ref_id_2":customer_id}
          ns.db.link.insert(**values)
        if group_id:
          values = {"nervatype_1":nervatype_price, "ref_id_1":request.post_vars["id"], "nervatype_2":nervatype_groups, "ref_id_2":group_id}
          ns.db.link.insert(**values)
      setLogtable("update", "log_product_update", "product", request.post_vars["product_id"])
      redirect(URL('find_product_discount/view/product/'+str(request.post_vars["product_id"])))
    except Exception, err:
      response.flash = str(err)
        
  response.titleicon = URL(dir_images,'icon16_money.png')
  response.export_excel = ruri.replace("find_product_discount","find_product_discount/excel")
  response.export_csv = ruri.replace("find_product_discount","find_product_discount/csv")
  response.view=dir_view+'/browser.html'
  
  custlink = ns.db.link.with_alias('custlink')
  ns.db.customer.id.represent = lambda value,row: A(SPAN(ns.db.customer(id=int(value))["custname"]),
                     _href=URL(r=request, f="frm_customer/view/customer/"+str(value)), _target="_blank")
  ns.db.customer.id.label=T('Customer')
  grouplink = ns.db.link.with_alias('grouplink')
  calcmode = ns.db.groups.with_alias('calcmode')
  ns.db.price.pricevalue.label = T("Limit")
  
  def get_find_product_discount_filter():        
    bool_fields_name = [ns.db.price.vendorprice.name]
    bool_fields_label = [ns.db.price.vendorprice.label]
    
    number_fields_name = [ns.db.price.qty.name, ns.db.price.pricevalue.name, ns.db.price.discount.name]
    number_fields_label = [ns.db.price.qty.label, ns.db.price.pricevalue.label, ns.db.price.discount.label]
    
    date_fields_name = [ns.db.price.validfrom.name, ns.db.price.validto.name]
    date_fields_label = [ns.db.price.validfrom.label, ns.db.price.validto.label]
    
    data_fields_name = ["htab_product_partnumber", "htab_product_description", "htab_product_unit", "htab_customer_custname", 
                        "htab_groups_groupvalue", "htab_calcmode_groupvalue", ns.db.price.curr.name]
    data_fields_label = [ns.db.product.partnumber.label, ns.db.product.description.label, ns.db.product.unit.label, 
                         ns.db.customer.id.label, ns.db.groups.groupvalue.label, ns.db.price.calcmode.label, ns.db.price.curr.label]
    
    return create_filter_form(sfilter_name="product_discount_filter",state_fields=["pricetype"],
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label}, 
                                         date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  
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
    response.subtitle= ns.db.product(id=product_id).partnumber +" - "+ ns.db.product(id=product_id).description
    response.cmd_back = get_back_button(URL("frm_product/view/product/"+str(product_id)))
    response.lo_menu = []
    query = (ns.db.product.id==product_id)
    _sortable = False
    _orderby=ns.db.price.validfrom
    ns.db.groups.id.readable = False
    ns.db.customer.custname.readable = False
    fields = [ns.db.customer.id, ns.db.customer.custname, ns.db.groups.id, ns.db.groups.groupvalue, ns.db.price.validfrom,
              ns.db.price.validto,ns.db.price.calcmode,ns.db.price.curr, ns.db.price.qty, ns.db.price.pricevalue,
              ns.db.price.discount,ns.db.price.vendorprice]
    
    response.edit_form = SQLFORM(ns.db.price, submit_button=T("Save"),_id="frm_edit")
    response.edit_form.process()
    _field_id=ns.db.price.id
    def_calcmode = ns.db((ns.db.groups.groupname=="calcmode")&(ns.db.groups.groupvalue=="amo")).select().as_list()[0]["id"]
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
                              "')){window.location ='"+URL("find_product_price/delete/price/"+str(row["price"]["id"]))+"';};return false;", 
                         _title=T("Delete Price"))]
    if audit_filter!="readonly":
      response.cmd_edit_submit = get_command_button(caption=T("Save"),title=T("Update price data"),color="008B00", _id="cmd_edit_submit",
                              cmd="price_update();return true;")
    response.edit_title = T("DISCOUNT")
    response.edit_icon = URL(dir_images,'icon16_money.png')
    response.cmd_edit_cancel = A(SPAN(_class="icon cross"), _id="cmd_edit_cancel", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
      _onclick= "document.getElementById('edit_form').style.display = 'none';return true;")
    if audit_filter=="all":
      response.cmd_edit_new = A(SPAN(_class="icon plus"), _id="cmd_edit_new", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=T('New Discount'), 
        _onclick= "set_price(-1,'"+str(datetime.datetime.now().date())+"','','"+getSetting("default_currency")+"',0,0,0,"+str(def_calcmode)+",0,'','','','"+json.dumps(str(T("New value")))[1:-1]+"');")
    response.edit_id = INPUT(_name="id", _type="hidden", _value="", _id="edit_id")
    cust_groups = ns.db((ns.db.groups.groupname=="customer")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.groupvalue)
    response.cmb_groups = SELECT(*[OPTION(group.groupvalue, _value=group.id) for group in cust_groups], _id="price_group_id", _name="group_id")
    response.cmb_groups.insert(0, OPTION("", _value=""))
    response.edit_items = DIV(
                            TABLE(TR(
                                 TD(DIV(response.edit_form.custom.label.validfrom,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.validfrom,
                                    _style="width: 70px;padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 5px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.validto,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.validto,
                                    _style="width: 70px;padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 5px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.curr,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.curr,
                                    _style="width: 60px;padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 0px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.qty,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 5px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.qty,
                                    _style="width: 60px;padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 10px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.pricevalue,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 5px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.pricevalue,
                                    _style="padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 20px;padding-left: 5px;")
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;"),
                            TABLE(TR(
                                 TD(DIV(T("Group"),_style="width: 80px;", _class="label"),
                                    _style="padding-top: 5px;padding-bottom: 5px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.cmb_groups,
                                    INPUT(_name="product_id", _type="hidden", _value=product_id, _id="price_product_id"),
                                    _style="width: 175px;padding: 0px;padding-top: 0px;padding-bottom: 0px;vertical-align: middle;padding-right: 5px;padding-left: 5px;"),
                                 TD(DIV(T("Customer"),_style="width: 80px;", _class="label"),
                                    _style="padding-top: 5px;padding-bottom: 5px;width: 80px;padding-right: 0px;padding-left: 0px;", _class="td_label"),
                                 TD(INPUT(_name="customer_id", _type="hidden", _value="", _id="customer_id"),get_customer_selector("", width="100%"),
                                    _style="padding: 0px;padding-top: 0px;padding-bottom: 0px;vertical-align: middle;padding-right: 5px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.vendorprice,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 5px;padding-bottom: 5px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.vendorprice,
                                    _style="width: 10px;padding: 0px;padding-top: 5px;padding-bottom: 0px;vertical-align: top;padding-right: 10px;padding-left: 5px;")
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;"),
                            TABLE(TR(
                                 TD(DIV(response.edit_form.custom.label.calcmode,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 5px;padding-bottom: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.calcmode,
                                    _style="width: 175px;padding: 0px;padding-top: 0px;padding-bottom: 5px;vertical-align: middle;padding-right: 5px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.discount,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 5px;padding-bottom: 10px;width: 80px;padding-right: 0px;padding-left: 0px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.discount,
                                    _style="width: 135px;padding: 0px;padding-top: 0px;padding-bottom: 5px;vertical-align: middle;padding-right: 5px;padding-left: 5px;"),
                                 TD()
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;")
                            )
    
  else:
    response.browsertype=T('Product Browser')
    response.subtitle=T('Discount')
    set_find_product_menu()
    response.filter_form = get_find_product_discount_filter()
    query = (ns.db.product.deleted==0)
    where = get_filter_query(sfilter=session.product_discount_filter,table="price",query=query)
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
    
  if ruri.find("find_product_discount/excel")>0:
    return export2excel("price",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  if ruri.find("find_product_discount/csv")>0:
    return export2csv("price",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  
  form = SimpleGrid.grid(query=query, field_id=_field_id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.product.description, sortable=_sortable, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=_sortable, links=_links)
  
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
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  response.export_excel = ruri.replace("find_product_event","find_product_event/excel")
  response.export_csv = ruri.replace("find_product_event","find_product_event/csv")
  response.view=dir_view+'/browser.html'
  set_find_product_menu()
  
  def get_find_product_event_filter():
    date_fields_name = [ns.db.event.fromdate.name,ns.db.event.todate.name]
    date_fields_label = [ns.db.event.fromdate.label,ns.db.event.todate.label]
    
    data_fields_name = [ns.db.event.calnumber.name, "htab_product_partnumber", "htab_product_description", 
                        ns.db.event.eventgroup.name, ns.db.event.subject.name, ns.db.event.place.name, ns.db.event.description.name]
    data_fields_label = [ns.db.event.calnumber.label, ns.db.product.partnumber.label, ns.db.product.description.label, 
                        ns.db.event.eventgroup.label, ns.db.event.subject.label, ns.db.event.place.label, ns.db.event.description.label]
    
    more_data = {"title":"Event Additional Data","caption":"Additional Data","url":URL('find_product_event_fields')}
    
    return create_filter_form(sfilter_name="product_event_filter",state_fields=None,bool_fields=None,
                              date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},number_fields=None,
                              data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label},more_data=more_data)
  response.filter_form = get_find_product_event_filter()
  
  ns.db.event.ref_id.represent = lambda value,row: A(SPAN(ns.db.product(id=int(value))["description"]),
                     _href=URL(r=request, f="frm_product/view/product/"+str(value)), _target="_blank")
  ns.db.event.ref_id.label=T('Product')
  nervatype_product = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="product")).select().as_list()[0]["id"]
  
  join = [(ns.db.event.on((ns.db.product.id==ns.db.event.ref_id)&(ns.db.event.nervatype==nervatype_product)&(ns.db.event.deleted==0)))]
  left = [(ns.db.groups.on((ns.db.event.eventgroup==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  query = ((ns.db.product.deleted==0))
  
  where = get_filter_query(sfilter=session.product_event_filter,table="event",query=query)
  query = where["query"]
  
  fields = [ns.db.event.calnumber,ns.db.product.partnumber, ns.db.event.ref_id, ns.db.event.eventgroup,
            ns.db.event.fromdate,ns.db.event.todate,ns.db.event.subject,ns.db.event.place,ns.db.event.description]
  
  if ruri.find("find_product_event/excel")>0:
    return export2excel("product",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  if ruri.find("find_product_event/csv")>0:
    return export2csv("product",query,left,fields,ns.db.product.description,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_event_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.product.id==-1))
    
  links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("export2ical?id="+str(row.event.id)), _target="_blank", _title=T("Export Item"))]
  form = SimpleGrid.grid(query=query, field_id=ns.db.event.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.product.description, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=links)
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
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  response.export_excel = ruri.replace("find_product_event_fields","find_product_event_fields/excel")
  response.export_csv = ruri.replace("find_product_event_fields","find_product_event_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_product_menu()
  nervatype_event = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="event")).select().as_list()[0]["id"]
  nervatype_product = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="product")).select().as_list()[0]["id"]
  response.filter_form = get_fields_filter("event","product_event_fields_filter")
  
  htab = ns.db.event.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(htab.nervatype==nervatype_product))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_event)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = get_filter_query(sfilter=session.product_event_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.calnumber,htab.subject,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_product_event_fields/excel")>0:
    return export2excel("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  if ruri.find("find_product_event_fields/csv")>0:
    return export2csv("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.product_event_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.calnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
  return dict(form=form)

@ns_auth.requires_login()
def find_employee_quick():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_employee"+ruri[ruri.find("find_employee_quick")+19:]
    redirect(URL(ruri))
      
  response.view=dir_view+'/gridform.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select employee')
  response.margin_top = "20px"
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
    response.cmd_back = get_back_button(session.back_url)
  else:
    response.cmd_back = get_home_button()
  response.titleicon = URL(dir_images,'icon16_find.png')
  
  nervatype_employee = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="employee")).select().as_list()[0]["id"]
  query = ((ns.db.employee.deleted==0)&(ns.db.employee.usergroup==ns.db.groups.id)&
           (ns.db.employee.id==ns.db.contact.ref_id)&(ns.db.contact.nervatype==nervatype_employee)&(ns.db.contact.deleted==0))
  left = None
  
  fields = [ns.db.employee.empnumber, ns.db.contact.firstname, ns.db.contact.surname, ns.db.employee.username, 
            ns.db.employee.usergroup, ns.db.employee.inactive]
  
  smenu = [ns.db.employee.empnumber, ns.db.contact.firstname, ns.db.contact.surname, ns.db.employee.username]
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False:
    query = query & (ns.db.employee.id==-1)
  search_widget = create_search_widget(smenu)

  form = SQLFORM.grid(query=query, field_id=ns.db.employee.id, fields=fields, left=left, #headers=headers,
               orderby=ns.db.employee.id, sortable=True, paginate=10, maxtextlength=25,
               searchable=True, csv=False, details=False, showbuttontext=False,
               create=False, deletable=False, editable=True, selectable=False, 
               user_signature=False, search_widget=search_widget)
  if type(form[1][0][0]).__name__=="TABLE":
    form=move_buttons(form)
  set_counter_bug(form)
  return dict(form=DIV(form, _id="dlg_frm"))

def set_find_employee_menu():
  response.lo_menu = []
  mnu_employee = (T('EMPLOYEE VIEWS'), False, None, [])
  mnu_employee[3].append((T('Employee Data'), False, URL('find_employee_employee'), []))
  mnu_employee[3].append((T('Additional Data'), False, URL('find_employee_fields'), []))
  audit_filter = get_audit_filter("event", None)[0]
  if audit_filter!="disabled":
    mnu_employee[3].append((T('Events'), False, URL('find_employee_event'), []))
  response.lo_menu.append(mnu_employee)

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
  response.titleicon = URL(dir_images,'icon16_user.png')
  response.export_excel = ruri.replace("find_employee_employee","find_employee_employee/excel")
  response.export_csv = ruri.replace("find_employee_employee","find_employee_employee/csv")
  response.view=dir_view+'/browser.html'
  set_find_employee_menu()
  
  def get_find_employee_employee_filter():
    bool_fields_name = [ns.db.employee.inactive.name]
    bool_fields_label = [ns.db.employee.inactive.label]
    
    date_fields_name = [ns.db.employee.startdate.name, ns.db.employee.enddate.name]
    date_fields_label = [ns.db.employee.startdate.label, ns.db.employee.enddate.label]
    
    data_fields_name = [ns.db.employee.empnumber.name, "htab_contact_firstname", "htab_contact_surname", ns.db.employee.username.name, ns.db.employee.usergroup.name,
            ns.db.employee.department.name, "htab_contact_status", "htab_contact_phone", "htab_contact_mobil", "htab_contact_email", "htab_contact_notes"]
    data_fields_label = [ns.db.employee.empnumber.label, ns.db.contact.firstname.label, ns.db.contact.surname.label, ns.db.employee.username.label, ns.db.employee.usergroup.label,
            ns.db.employee.department.label, ns.db.contact.status.label, ns.db.contact.phone.label, ns.db.contact.mobil.label,ns.db.contact.email.label, ns.db.contact.notes.label]
    
    return create_filter_form(sfilter_name="employee_employee_filter",state_fields=None,
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         number_fields=None,
                                         date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_employee_employee_filter()
  
  nervatype_employee = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="employee")).select().as_list()[0]["id"]
  query = ((ns.db.employee.deleted==0)&(ns.db.employee.usergroup==ns.db.groups.id))
  
  where = get_filter_query(sfilter=session.employee_employee_filter,table="employee",query=query)
  query = where["query"]
  
  department = ns.db.groups.with_alias('department')
  department.groupvalue.label=T("Department")
  fields = [ns.db.employee.empnumber, ns.db.contact.firstname, ns.db.contact.surname, ns.db.employee.username, ns.db.employee.usergroup,
            department.groupvalue, ns.db.employee.startdate, ns.db.employee.enddate, ns.db.contact.status, ns.db.contact.phone, ns.db.contact.mobil,
            ns.db.contact.email, ns.db.contact.notes, ns.db.employee.inactive]
  left = ([ns.db.contact.on((ns.db.employee.id==ns.db.contact.ref_id)&(ns.db.contact.nervatype==nervatype_employee)&(ns.db.contact.deleted==0)),
          department.on((ns.db.employee.department==department.id)&(department.deleted==0))])
  
  if ruri.find("find_employee_employee/excel")>0:
    return export2excel("employee",query,left,fields,ns.db.employee.empnumber,request.vars.keywords)
  if ruri.find("find_employee_employee/csv")>0:
    return export2csv("employee",query,left,fields,ns.db.employee.empnumber,request.vars.keywords)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.employee_employee_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.employee.id==-1))
  
  audit_filter = get_audit_filter("employee", None)[0]  
  form = SimpleGrid.grid(query=query, field_id=ns.db.employee.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=None,
             orderby=ns.db.employee.empnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, create=(audit_filter=="all"), links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_user.png')
  response.export_excel = ruri.replace("find_employee_fields","find_employee_fields/excel")
  response.export_csv = ruri.replace("find_employee_fields","find_employee_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_employee_menu()
  nervatype_employee = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="employee")).select().as_list()[0]["id"]
  response.filter_form = get_fields_filter("employee","employee_fields_filter")
  
  htab = ns.db.employee.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_employee)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = get_filter_query(sfilter=session.employee_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.empnumber,htab.username,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_employee_fields/excel")>0:
    return export2excel("employee",query,left,fields,htab.empnumber,request.vars.keywords,join=join)
  if ruri.find("find_employee_fields/csv")>0:
    return export2csv("employee",query,left,fields,htab.empnumber,request.vars.keywords,join=join)
    
  audit_filter = get_audit_filter("employee", None)[0]
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.employee_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.empnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, create=(audit_filter=="all"), links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  response.export_excel = ruri.replace("find_employee_event","find_employee_event/excel")
  response.export_csv = ruri.replace("find_employee_event","find_employee_event/csv")
  response.view=dir_view+'/browser.html'
  set_find_employee_menu()
  
  def get_find_employee_event_filter():
    date_fields_name = [ns.db.event.fromdate.name,ns.db.event.todate.name]
    date_fields_label = [ns.db.event.fromdate.label,ns.db.event.todate.label]
    
    data_fields_name = [ns.db.event.calnumber.name, "htab_employee_empnumber", "htab_employee_username", 
                        ns.db.event.eventgroup.name, ns.db.event.subject.name, ns.db.event.place.name, ns.db.event.description.name]
    data_fields_label = [ns.db.event.calnumber.label, ns.db.employee.empnumber.label, ns.db.employee.username.label, 
                        ns.db.event.eventgroup.label, ns.db.event.subject.label, ns.db.event.place.label, ns.db.event.description.label]
    
    more_data = {"title":"Event Additional Data","caption":"Additional Data","url":URL('find_employee_event_fields')}
    
    return create_filter_form(sfilter_name="employee_event_filter",state_fields=None,bool_fields=None,
                              date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},number_fields=None,
                              data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label},more_data=more_data)
  response.filter_form = get_find_employee_event_filter()
  
  ns.db.event.ref_id.represent = lambda value,row: A(SPAN(ns.db.employee(id=int(value))["empnumber"]),
                     _href=URL(r=request, f="frm_employee/view/employee/"+str(value)), _target="_blank")
  ns.db.event.ref_id.label=T('Employee No.')
  nervatype_employee = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="employee")).select().as_list()[0]["id"]
  
  join = [(ns.db.event.on((ns.db.employee.id==ns.db.event.ref_id)&(ns.db.event.nervatype==nervatype_employee)&(ns.db.event.deleted==0)))]
  left = [(ns.db.groups.on((ns.db.event.eventgroup==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  query = (ns.db.employee.deleted==0)
  
  where = get_filter_query(sfilter=session.employee_event_filter,table="event",query=query)
  query = where["query"]
  
  fields = [ns.db.event.calnumber,ns.db.event.ref_id, ns.db.employee.username, ns.db.event.eventgroup,
            ns.db.event.fromdate,ns.db.event.todate,ns.db.event.subject,ns.db.event.place,ns.db.event.description]
  if ruri.find("find_employee_event/excel")>0:
    return export2excel("employee",query,left,fields,ns.db.employee.empnumber,request.vars.keywords,join=join)
  if ruri.find("find_employee_event/csv")>0:
    return export2csv("employee",query,left,fields,ns.db.employee.empnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.employee_event_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.employee.id==-1))
    
  links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("export2ical?id="+str(row.event.id)), _target="_blank", _title=T("Export Item"))]
  form = SimpleGrid.grid(query=query, field_id=ns.db.event.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.employee.empnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=links)
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
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  response.export_excel = ruri.replace("find_employee_event_fields","find_employee_event_fields/excel")
  response.export_csv = ruri.replace("find_employee_event_fields","find_employee_event_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_employee_menu()
  nervatype_event = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="event")).select().as_list()[0]["id"]
  nervatype_employee = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="employee")).select().as_list()[0]["id"]
  response.filter_form = get_fields_filter("event","employee_event_fields_filter")
  
  htab = ns.db.event.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(htab.nervatype==nervatype_employee))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_event)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = get_filter_query(sfilter=session.employee_event_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.calnumber,htab.subject,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_employee_event_fields/excel")>0:
    return export2excel("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  if ruri.find("find_employee_event_fields/csv")>0:
    return export2csv("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.employee_event_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.calnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
  return dict(form=form)

@ns_auth.requires_login()
def find_tool_quick():
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_tool"+ruri[ruri.find("find_tool_quick")+15:]
    redirect(URL(ruri))
      
  response.view=dir_view+'/gridform.html'
  response.title=T('Quick Search')
  response.subtitle=T('Select tool')
  response.margin_top = "20px"
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
    response.cmd_back = get_back_button(session.back_url)
  else:
    response.cmd_back = get_home_button()
  response.titleicon = URL(dir_images,'icon16_find.png')
  
  query = ((ns.db.tool.deleted==0)&(ns.db.product.id==ns.db.tool.product_id)&(ns.db.product.deleted==0))
  left = None
  
  fields = [ns.db.tool.serial, ns.db.tool.description, ns.db.tool.product_id, ns.db.tool.inactive]
  smenu = [ns.db.tool.serial, ns.db.tool.description, ns.db.product.description]
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False:
    query = query & (ns.db.tool.id==-1)
  search_widget = create_search_widget(smenu)

  form = SQLFORM.grid(query=query, field_id=ns.db.tool.id, fields=fields, left=left, #headers=headers,
               orderby=ns.db.tool.id, sortable=True, paginate=10, maxtextlength=25,
               searchable=True, csv=False, details=False, showbuttontext=False,
               create=False, deletable=False, editable=True, selectable=False, 
               user_signature=False, search_widget=search_widget)
  if type(form[1][0][0]).__name__=="TABLE":
    form=move_buttons(form)
  set_counter_bug(form)
  return dict(form=DIV(form, _id="dlg_frm"))

def set_find_tool_menu():
  response.lo_menu = []
  mnu_tool = (T('TOOL VIEWS'), False, None, [])
  mnu_tool[3].append((T('Tool Data'), False, URL('find_tool_tool'), []))
  mnu_tool[3].append((T('Additional Data'), False, URL('find_tool_fields'), []))
  audit_filter = get_audit_filter("event", None)[0]
  if audit_filter!="disabled":
    mnu_tool[3].append((T('Events'), False, URL('find_tool_event'), []))
  response.lo_menu.append(mnu_tool)

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
  response.titleicon = URL(dir_images,'icon16_wrench.png')
  response.export_excel = ruri.replace("find_tool_tool","find_tool_tool/excel")
  response.export_csv = ruri.replace("find_tool_tool","find_tool_tool/csv")
  response.view=dir_view+'/browser.html'
  set_find_tool_menu()
  
  def get_find_tool_tool_filter():    
    bool_fields_name = [ns.db.tool.inactive.name]
    bool_fields_label = [ns.db.tool.inactive.label]
    
    data_fields_name = [ns.db.tool.serial.name, ns.db.tool.description.name, ns.db.tool.product_id.name, ns.db.tool.toolgroup.name, ns.db.tool.notes.name]
    data_fields_label = [ns.db.tool.serial.label, ns.db.tool.description.label, ns.db.tool.product_id.label, ns.db.tool.toolgroup.label, ns.db.tool.notes.label]
    
    return create_filter_form(sfilter_name="tool_tool_filter",state_fields=None,
                                         bool_fields={"bool_fields_name":bool_fields_name,"bool_fields_label":bool_fields_label},
                                         number_fields=None,
                                         date_fields=None,
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_tool_tool_filter()
  
  query = (ns.db.tool.deleted==0)
  where = get_filter_query(sfilter=session.tool_tool_filter,table="tool",query=query)
  query = where["query"]
  
  join = [(ns.db.product.on((ns.db.product.id==ns.db.tool.product_id)&(ns.db.product.deleted==0)))]
  left = (ns.db.groups.on((ns.db.tool.toolgroup==ns.db.groups.id)))
  
  fields = [ns.db.tool.serial, ns.db.tool.description, ns.db.tool.product_id, ns.db.groups.groupvalue, 
            ns.db.tool.notes, ns.db.tool.inactive]
  
  if ruri.find("find_tool_tool/excel")>0:
    return export2excel("tool",query,left,fields,ns.db.tool.serial,request.vars.keywords,join=join)
  if ruri.find("find_tool_tool/csv")>0:
    return export2csv("tool",query,left,fields,ns.db.tool.serial,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.tool_tool_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.tool.id==-1))
  
  audit_filter = get_audit_filter("tool", None)[0]  
  form = SimpleGrid.grid(query=query, field_id=ns.db.tool.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.tool.serial, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, create=(audit_filter=="all"), links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_wrench.png')
  response.export_excel = ruri.replace("find_tool_fields","find_tool_fields/excel")
  response.export_csv = ruri.replace("find_tool_fields","find_tool_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_tool_menu()
  nervatype_tool = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="tool")).select().as_list()[0]["id"]
  response.filter_form = get_fields_filter("tool","tool_fields_filter")
  
  htab = ns.db.tool.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_tool)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = get_filter_query(sfilter=session.tool_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  htab.description.label = T('Tool description')
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.serial,htab.description,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_tool_fields/excel")>0:
    return export2excel("tool",query,left,fields,htab.serial,request.vars.keywords,join=join)
  if ruri.find("find_tool_fields/csv")>0:
    return export2csv("tool",query,left,fields,htab.serial,request.vars.keywords,join=join)
  
  audit_filter = get_audit_filter("tool", None)[0]
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.tool_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.serial, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, create=(audit_filter=="all"), links=None)
  
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
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  response.export_excel = ruri.replace("find_tool_event","find_tool_event/excel")
  response.export_csv = ruri.replace("find_tool_event","find_tool_event/csv")
  response.view=dir_view+'/browser.html'
  set_find_tool_menu()
  
  def get_find_tool_event_filter():
    date_fields_name = [ns.db.event.fromdate.name,ns.db.event.todate.name]
    date_fields_label = [ns.db.event.fromdate.label,ns.db.event.todate.label]
    
    data_fields_name = [ns.db.event.calnumber.name, "htab_tool_serial", "htab_tool_description", 
                        ns.db.event.eventgroup.name, ns.db.event.subject.name, ns.db.event.place.name, ns.db.event.description.name]
    data_fields_label = [ns.db.event.calnumber.label, ns.db.tool.serial.label, ns.db.tool.description.label, 
                        ns.db.event.eventgroup.label, ns.db.event.subject.label, ns.db.event.place.label, ns.db.event.description.label]
    
    more_data = {"title":"Event Additional Data","caption":"Additional Data","url":URL('find_tool_event_fields')}
    
    return create_filter_form(sfilter_name="tool_event_filter",state_fields=None,bool_fields=None,
                              date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},number_fields=None,
                              data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label},more_data=more_data)
  response.filter_form = get_find_tool_event_filter()
  
  ns.db.event.ref_id.represent = lambda value,row: A(SPAN(ns.db.tool(id=int(value))["serial"]),
                     _href=URL(r=request, f="frm_tool/view/tool/"+str(value)), _target="_blank")
  ns.db.event.ref_id.label=T('Serial')
  nervatype_tool = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="tool")).select().as_list()[0]["id"]
  
  join = [(ns.db.event.on((ns.db.tool.id==ns.db.event.ref_id)&(ns.db.event.nervatype==nervatype_tool)&(ns.db.event.deleted==0)))]
  left = [(ns.db.groups.on((ns.db.event.eventgroup==ns.db.groups.id)&(ns.db.groups.deleted==0)))]
  query = (ns.db.tool.deleted==0)
  
  where = get_filter_query(sfilter=session.tool_event_filter,table="event",query=query)
  query = where["query"]
  
  fields = [ns.db.event.calnumber,ns.db.event.ref_id, ns.db.tool.description, ns.db.event.eventgroup,
            ns.db.event.fromdate,ns.db.event.todate,ns.db.event.subject,ns.db.event.place,ns.db.event.description]
  if ruri.find("find_tool_event/excel")>0:
    return export2excel("tool",query,left,fields,ns.db.tool.serial,request.vars.keywords,join=join)
  if ruri.find("find_tool_event/csv")>0:
    return export2csv("tool",query,left,fields,ns.db.tool.serial,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.tool_event_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.tool.id==-1))
    
  links = [lambda row: A(SPAN(_class="icon clock"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("export2ical?id="+str(row.event.id)), _target="_blank", _title=T("Export Item"))]
  form = SimpleGrid.grid(query=query, field_id=ns.db.event.id, 
             fields=fields, groupfields=None, groupby=None, left=left, having=None, join=join,
             orderby=ns.db.tool.serial, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=links)
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
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  response.export_excel = ruri.replace("find_tool_event_fields","find_tool_event_fields/excel")
  response.export_csv = ruri.replace("find_tool_event_fields","find_tool_event_fields/csv")
  response.view=dir_view+'/browser.html'
  set_find_tool_menu()
  nervatype_event = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="event")).select().as_list()[0]["id"]
  nervatype_tool = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="tool")).select().as_list()[0]["id"]
  response.filter_form = get_fields_filter("event","tool_event_fields_filter")
  
  htab = ns.db.event.with_alias('htab')
  join = [(htab.on((ns.db.fieldvalue.ref_id==htab.id)&(htab.deleted==0)&(htab.nervatype==nervatype_tool))),
          (ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
           &(ns.db.deffield.nervatype==nervatype_event)))]
  query = (ns.db.fieldvalue.deleted==0)
  
  where = get_filter_query(sfilter=session.tool_event_fields_filter,table="fieldvalue",query=query)
  query = where["query"]
  
  ns.db.fieldvalue.id.readable = False
  fields = [ns.db.fieldvalue.id,htab.calnumber,htab.subject,ns.db.deffield.description,ns.db.fieldvalue.value,ns.db.fieldvalue.notes]
  left = None
  
  if ruri.find("find_tool_event_fields/excel")>0:
    return export2excel("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  if ruri.find("find_tool_event_fields/csv")>0:
    return export2csv("event",query,left,fields,htab.calnumber,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.tool_event_fields_filter)==0 and len(request.post_vars)==0:
    query = (query&(htab.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=htab.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=join,
             orderby=htab.calnumber, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=True, links=None)
  
  return dict(form=form)

@ns_auth.requires_login()
def find_rate():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.rate_filter=None
    redirect(URL("find_rate"))
  
  if ruri.find("edit/rate")>0 or ruri.find("view/rate")>0:
    redirect(URL('find_rate'))
    
  if ruri.find("delete/rate")>0:
    rate_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if delete_row("rate", rate_id, "rate", rate_id):
      redirect(URL('find_rate'))
        
  if request.post_vars["_formname"]=="rate/create":
    clear_post_vars()
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.rate.id==request.post_vars["id"]).update(**request.post_vars)      
      else:
        request.post_vars["id"]= ns.db.rate.insert(**request.post_vars)
      setLogtable("update", "log_rate_update", "rate", request.post_vars["id"])
      redirect(URL('find_rate'))
    except Exception, err:
      response.flash = str(err) 
        
  response.browsertype=T('Rate Browser')
  response.subtitle=T('Interest and Exchange Rate')
  response.titleicon = URL(dir_images,'icon16_percent.png')
  response.export_excel = ruri.replace("find_rate","find_rate/excel")
  response.export_csv = ruri.replace("find_rate","find_rate/csv")
  response.view=dir_view+'/browser.html'
  response.lo_menu = []
  
  def get_find_rate_filter():
    date_fields_name = [ns.db.rate.ratedate.name]
    date_fields_label = [ns.db.rate.ratedate.label]
    
    number_fields_name = [ns.db.rate.ratevalue.name]
    number_fields_label = [ns.db.rate.ratevalue.label]
    
    data_fields_name = [ns.db.rate.curr.name,ns.db.rate.rategroup.name,ns.db.rate.place_id.name]
    data_fields_label = [ns.db.rate.curr.label,ns.db.rate.rategroup.label,ns.db.rate.place_id.label]
    
    return create_filter_form(sfilter_name="rate_filter",state_fields=["ratetype"],bool_fields=None,
                              date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},
                              number_fields={"number_fields_name":number_fields_name,"number_fields_label":number_fields_label},
                              data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_rate_filter()
  
  join = None
  left = None
  query = (ns.db.rate.deleted==0)
  
  where = get_filter_query(sfilter=session.rate_filter,table="rate",query=query)
  query = where["query"]
  
  fields = [ns.db.rate.ratetype,ns.db.rate.ratedate,ns.db.rate.curr,ns.db.rate.ratevalue,ns.db.rate.rategroup,ns.db.rate.place_id]
  if ruri.find("find_rate/excel")>0:
    return export2excel("rate",query,left,fields,ns.db.rate.ratedate,request.vars.keywords,join=join)
  if ruri.find("find_rate/csv")>0:
    return export2csv("rate",query,left,fields,ns.db.rate.ratedate,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.rate_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.rate.id==-1))
  
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
  if audit_filter!="readonly":
    response.cmd_edit_submit = get_command_button(caption=T("Save"),title=T("Update rate data"),color="008B00", _id="cmd_edit_submit",
                              cmd="rate_update();return true;")
  else:
    response.cmd_edit_submit = ""
  response.edit_form = SQLFORM(ns.db.rate, submit_button=T("Save"),_id="frm_edit")
  response.edit_form.process()
  response.edit_title = T("RATE")
  response.edit_icon = URL(dir_images,'icon16_percent.png')
  response.cmd_edit_cancel = A(SPAN(_class="icon cross"), _id="cmd_edit_cancel", 
    _style="height: 15px;",
    _class="w2p_trap buttontext button", _href="#", _title=T('Cancel update'), 
    _onclick= "document.getElementById('edit_form').style.display = 'none';document.getElementById('filter_div').style.display = 'block';return true;")
  if audit_filter=="all":
    links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+T('Are you sure you want to delete this rate?')+
                              "')){window.location ='"+URL("find_rate/delete/rate/"+str(row.id))+"';};return false;", 
                         _title=T("Delete Rate")))
    response.cmd_edit_new = A(SPAN(_class="icon plus"), _id="cmd_edit_new", 
      _style="height: 15px;",
      _class="w2p_trap buttontext button", _href="#", _title=T('New Rate'), 
      _onclick= "set_rate(-1,'','"+str(datetime.datetime.now().date())+"','"+getSetting("default_currency")+"','','',0,'"+json.dumps(str(T("New value")))[1:-1]+"');")
  else:
    response.cmd_edit_new = ""
  response.edit_id = INPUT(_name="id", _type="hidden", _value="", _id="edit_id")
  response.edit_items = DIV(
                            TABLE(TR(
                                 TD(DIV(response.edit_form.custom.label.ratetype,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.ratetype,
                                    _style="width: 100px;padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 0px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.ratedate,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.ratedate,
                                    _style="width: 90px;padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 10px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.curr,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.curr,
                                    _style="width: 80px;padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 5px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.ratevalue,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 10px;width: 80px;padding-right: 0px;padding-left: 5px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.ratevalue,
                                    _style="padding: 0px;padding-top: 5px;vertical-align: middle;padding-right: 20px;padding-left: 5px;")
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;"),
                            TABLE(TR(
                                 TD(DIV(response.edit_form.custom.label.rategroup,_style="width: 80px;", _class="label"),
                                    _style="padding-top: 5px;padding-bottom: 10px;width: 80px;padding-right: 0px;padding-left: 10px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.rategroup,
                                    _style="width: 275px;padding: 0px;padding-top: 0px;padding-bottom: 5px;vertical-align: middle;padding-right: 0px;padding-left: 5px;"),
                                 TD(get_goprop_button(title=T("Edit Groups"), url=URL("frm_groups_rategroup?back=1")),
                                    _style="width: 12px;padding: 0px;padding-top: 0px;padding-bottom: 5px;vertical-align: middle;padding-right: 0px;padding-left: 5px;"),
                                 TD(DIV(response.edit_form.custom.label.place_id,_style="width: 120px;", _class="label"),
                                    _style="padding-top: 5px;padding-bottom: 10px;width: 120px;padding-right: 0px;padding-left: 5px;", _class="td_label"),
                                 TD(response.edit_form.custom.widget.place_id,
                                    _style="padding: 0px;padding-top: 0px;padding-bottom: 5px;vertical-align: middle;padding-right: 10px;padding-left: 5px;")
                                 ),
                              _style="padding: 0px;margin: 0px;width: 100%;")
                            )
      
  form = SimpleGrid.grid(query=query, field_id=ns.db.rate.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=None,
             orderby=ns.db.rate.ratedate, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=False, deletable=False, links=links)
  return dict(form=form)

@ns_auth.requires_login()
def find_log():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  if request.vars.has_key("remove_filter"):
    session.log_filter=None
    redirect(URL("find_log"))
    
  response.browsertype=T('Log Browser')
  response.subtitle=T('Database Logs')
  response.titleicon = URL(dir_images,'icon16_book_edit.png')
  response.export_excel = ruri.replace("find_log","find_log/excel")
  response.export_csv = ruri.replace("find_log","find_log/csv")
  response.view=dir_view+'/browser.html'
  response.lo_menu = []
  
  def get_find_log_filter():
    date_fields_name = [ns.db.log.crdate.name,]
    date_fields_label = [ns.db.log.crdate.label]
    
    data_fields_name = [ns.db.log.employee_id.name]
    data_fields_label = [ns.db.log.employee_id.label]
    
    return create_filter_form(sfilter_name="log_filter",state_fields=["logstate","nervatype"],bool_fields=None,
                              date_fields={"date_fields_name":date_fields_name,"date_fields_label":date_fields_label},number_fields=None,
                              data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  response.filter_form = get_find_log_filter()
  
  join = None
  left = None
  query = (ns.db.log.id>0)
  
  where = get_filter_query(sfilter=session.log_filter,table="log",query=query)
  query = where["query"]
  
  fields = [ns.db.log.logstate,ns.db.log.employee_id,ns.db.log.crdate,ns.db.log.nervatype,ns.db.log.ref_id]
  if ruri.find("find_log/excel")>0:
    return export2excel("log",query,left,fields,ns.db.log.crdate,request.vars.keywords,join=join)
  if ruri.find("find_log/csv")>0:
    return export2csv("log",query,left,fields,ns.db.log.crdate,request.vars.keywords,join=join)
  
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False and len(session.log_filter)==0 and len(request.post_vars)==0:
    query = (query&(ns.db.log.id==-1))
    
  form = SimpleGrid.grid(query=query, field_id=ns.db.log.id, 
             fields=fields, groupfields=None, groupby=None, left=None, having=None, join=None,
             orderby=ns.db.log.crdate, sortable=True, paginate=25, maxtextlength=25,
             showbuttontext=False, editable=False, links=None)
  return dict(form=form)

def get_find_place_dlg(placetype,title,fnum=""):
  dlg = DIALOG(LOAD(f=placetype+fnum, ajax=True), title=title, icon=URL(dir_images,'icon16_book.png'),
                  renderstyle=True, height=75, add_lnk=URL('frm_place/new/place'))
  return A(SPAN(_class="icon magnifier"), _style="padding: 0px;padding-left: 6px;padding-right: 3px;", _class="w2p_trap buttontext button", 
           _href="#null", _title=T("Find Place"), _onclick='%s;return false' % dlg.show())

@ns_auth.requires_login()
def find_place_dlg_all():
  return find_place_dlg()

@ns_auth.requires_login()
def find_place_dlg_bank():
  return find_place_dlg("bank")

@ns_auth.requires_login()
def find_place_dlg_cash():
  return find_place_dlg("cash")

@ns_auth.requires_login()
def find_place_dlg_warehouse():
  return find_place_dlg("warehouse")

@ns_auth.requires_login()
def find_place_dlg_warehouse2():
  return find_place_dlg("warehouse","2")

@ns_auth.requires_login()
def find_place_dlg_store():
  return find_place_dlg("store")

def find_place_dlg(placetype=None,fnum=""):
  query = ((ns.db.place.deleted==0)&(ns.db.place.placetype==ns.db.groups.id))
  if placetype:
    placetype_id = ns.db((ns.db.groups.groupname=="placetype")&(ns.db.groups.groupvalue==placetype)).select().as_list()[0]["id"]
    query = query & ((ns.db.place.placetype==placetype_id))
    href=URL("find_place_dlg_"+placetype+fnum)
  else:
    href=URL("find_place_dlg_all")
  fields = [ns.db.place.id, ns.db.place.planumber, ns.db.groups.groupvalue, ns.db.place.description, ns.db.place.curr]
  left = None
  smenu = [ns.db.place.planumber, ns.db.groups.groupvalue, ns.db.place.description, ns.db.place.curr] 
  ns.db.groups.groupvalue.label=T("Type")
  links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href=href, _title=T("Select Item"), 
                         _onclick='set_place_value'+fnum+'("'+str(row.place.id)+'", "'+str(row.place.planumber)+'", "'+str(row.place.description)
                         +'", "'+str(row.place.curr)
                         +'");jQuery(this).parents(".dialog").hide();return true;')]
  return DIV(find_data("place",query,fields,ns.db.place.planumber,10,25,links,left,False,smenu=smenu), _id="dlg_filter")
  
def get_find_employee_dlg():
  dlg = DIALOG(LOAD(f='find_employee_dlg', ajax=True), title=T('Select Employee'), icon=URL(dir_images,'icon16_user.png'),
                  renderstyle=True, height=75, add_lnk=URL('frm_employee/new/employee'))
  return A(SPAN(_class="icon magnifier"), _style="padding: 0px;padding-left: 6px;padding-right: 3px;", _class="w2p_trap buttontext button", 
           _href="#null", _title=T("Find Employee"), _onclick='%s;return false' % dlg.show())

@ns_auth.requires_login()
def find_employee_dlg():
  query = ((ns.db.employee.deleted==0)&(ns.db.employee.usergroup==ns.db.groups.id))
  fields = [ns.db.employee.id, ns.db.employee.empnumber, ns.db.groups.groupvalue, ns.db.employee.username]
  left = None
  smenu = [ns.db.employee.empnumber, ns.db.groups.groupvalue, ns.db.employee.username] 
  links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href=URL("find_employee_dlg"), _title=T("Select Item"), 
                         _onclick='set_employee_value("'+str(row.employee.id)+'", "'+str(row.employee.empnumber)+'", "'+str(row.employee.username)+'");jQuery(this).parents(".dialog").hide();return true;')]
  return DIV(find_data("employee",query,fields,ns.db.employee.empnumber,10,25,links,left,False,smenu=smenu), _id="dlg_filter")
  
def get_find_project_dlg():
  dlg = DIALOG(LOAD(f='find_project_dlg', ajax=True), title=T('Select Project'), icon=URL(dir_images,'icon16_date_edit.png'),
                  renderstyle=True, height=75, add_lnk=URL('frm_project/new/project'))
  return A(SPAN(_class="icon magnifier"), _style="padding: 0px;padding-left: 6px;padding-right: 3px;", _class="w2p_trap buttontext button", 
           _href="#null", _title=T("Find Project"), _onclick='%s;return false' % dlg.show())

@ns_auth.requires_login()
def find_project_dlg():
  query = ((ns.db.project.deleted==0))
  fields = [ns.db.project.id, ns.db.project.pronumber, ns.db.project.description, ns.db.project.startdate, ns.db.project.enddate, ns.db.customer.custname]
  left = (ns.db.customer.on(ns.db.project.customer_id==ns.db.customer.id))
  smenu = [ns.db.project.pronumber, ns.db.project.description, ns.db.project.startdate, ns.db.project.enddate, ns.db.customer.custname]
  ns.db.project.startdate.represent = lambda value,row: formatDate(row.project["startdate"])
  ns.db.project.enddate.represent = lambda value,row: formatDate(row.project["enddate"])
  links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href=URL("find_project_dlg"), _title=T("Select Item"), 
                         _onclick='set_project_value("'+str(row.project.id)+'", "'+str(row.project.pronumber)+'", "'+str(row.project.description)+'");jQuery(this).parents(".dialog").hide();return true;')]
  return DIV(find_data("project",query,fields,ns.db.project.pronumber,10,25,links,left,False,smenu=smenu), _id="dlg_filter")
  
def get_find_product_dlg(protype):
  dlg = DIALOG(LOAD(f='find_product_dlg_'+protype, ajax=True), title=T('Select Product'), icon=URL(dir_images,'icon16_parts.png'),
                  renderstyle=True, height=75, add_lnk=URL('frm_product/new/product'))
  return A(SPAN(_class="icon magnifier"), _style="padding: 0px;padding-left: 6px;padding-right: 3px;", _class="w2p_trap buttontext button", 
           _id="cmd_product_find", _href="#null", _title=T("Find Product"), _onclick='%s;return false' % dlg.show())

@ns_auth.requires_login()
def find_product_dlg_all():
  return find_product_dlg("all")

@ns_auth.requires_login()
def find_product_dlg_item():
  return find_product_dlg("item")

@ns_auth.requires_login()
def find_product_dlg_service():
  return find_product_dlg("service")
      
def find_product_dlg(protype="all"):
  query = ((ns.db.product.deleted==0)&(ns.db.product.protype==ns.db.groups.id))
  if protype!="all":
    protype_id = ns.db((ns.db.groups.groupname=="protype")&(ns.db.groups.groupvalue==protype)).select().as_list()[0]["id"]
    query = query & ((ns.db.product.protype==protype_id))
    href=URL("find_product_dlg_"+protype)
  else:
    href=URL("find_product_dlg_all")
  fields = [ns.db.product.id, ns.db.product.partnumber, ns.db.product.description, ns.db.product.unit, ns.db.product.tax_id]
  left = None
  smenu = [ns.db.product.partnumber, ns.db.product.description, ns.db.product.unit]
  links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href=href, _title=T("Select Item"), 
                         _onclick='set_product_value("'+str(row.id)+'", "'+str(row.partnumber)+'", "'+str(row.description)+'", "'+str(row.unit)+'", "'+str(row.tax_id)+'");jQuery(this).parents(".dialog").hide();return true;')]
  return DIV(find_data("product",query,fields,ns.db.product.description,10,25,links,left,False,smenu=smenu), _id="dlg_filter")
  
def get_find_tool_dlg():
  dlg = DIALOG(LOAD(f='find_tool_dlg', ajax=True), title=T('Select Tool'), icon=URL(dir_images,'icon16_wrench.png'),
                  renderstyle=True, height=75, add_lnk=URL('frm_tool/new/tool'))
  return A(SPAN(_class="icon magnifier"), _style="padding: 0px;padding-left: 6px;padding-right: 3px;", _class="w2p_trap buttontext button", 
           _href="#null", _title=T("Find Tool"), _onclick='%s;return false' % dlg.show())

@ns_auth.requires_login()
def find_tool_dlg():
  query = ((ns.db.tool.deleted==0))
  fields = [ns.db.tool.id, ns.db.tool.serial, ns.db.tool.description, ns.db.groups.groupvalue]
  left = (ns.db.groups.on(ns.db.tool.toolgroup==ns.db.groups.id))
  smenu = [ns.db.tool.serial, ns.db.tool.description, ns.db.groups.groupvalue]
  links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href=URL("find_tool_dlg"), _title=T("Select Item"), 
                         _onclick='set_tool_value("'+str(row.tool.id)+'", "'+str(row.tool.serial)+'", "'+str(row.tool.description)+'");jQuery(this).parents(".dialog").hide();return true;')]
  return DIV(find_data("tool",query,fields,ns.db.tool.serial,10,25,links,left,False,smenu=smenu), _id="dlg_filter")

def get_find_customer_dlg():
  dlg = DIALOG(LOAD(f='find_customer_dlg', ajax=True), title=T('Select Customer'), icon=URL(dir_images,'icon16_customer.png'),
                  renderstyle=True, height=90, add_lnk=URL('frm_customer/new/customer'))
  return A(SPAN(_class="icon magnifier"), _style="padding: 0px;padding-left: 6px;padding-right: 3px;", _class="w2p_trap buttontext button", 
           _href="#null", _title=T("Find Customer"), _onclick='%s;return false' % dlg.show())

@ns_auth.requires_login()
def find_customer_dlg():
  nervatype_customer = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]  
  primary_address = ((ns.db.address.id.belongs(ns.db((ns.db.address.deleted==0)&(ns.db.address.nervatype==nervatype_customer)).select(ns.db.address.id.min().with_alias('id'), groupby=ns.db.address.ref_id))))
  query = ((ns.db.customer.deleted==0)&(ns.db.customer.id!=1))
  fields = [ns.db.customer.id, ns.db.customer.custnumber, ns.db.customer.custname, ns.db.address.city, ns.db.address.street]
  left = (ns.db.address.on((ns.db.customer.id==ns.db.address.ref_id) & primary_address))
  smenu = [ns.db.customer.custnumber, ns.db.customer.custname, ns.db.address.city, ns.db.address.street]
  links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href=URL("find_customer_dlg"), _title=T("Select Item"), 
                         _onclick='set_customer_value("'+str(row.customer.id)+'", "'+str(row.customer.custnumber)+'", "'+str(row.customer.custname)+'");jQuery(this).parents(".dialog").hide();return true;')]
  return DIV(find_data("customer",query,fields,ns.db.customer.custname,10,25,links,left,False,smenu=smenu), _id="dlg_filter")

def get_find_transitem_dlg(transtype="all"):
  dlg = DIALOG(LOAD(f='find_transitem_dlg_'+transtype, ajax=True), title=T('Select Document'), icon=URL(dir_images,'icon16_find.png'),
                  renderstyle=True, height=75)
  return A(SPAN(_class="icon magnifier"), _id="cmd_find_transitem", _style="padding: 0px;padding-left: 6px;padding-right: 3px;", _class="w2p_trap buttontext button", 
           _href="#null", _title=T("Find Document"), _onclick='%s;return false' % dlg.show())

@ns_auth.requires_login()
def find_transitem_dlg_all():
  return find_transitem_dlg()

@ns_auth.requires_login()
def find_transitem_dlg_invoice():
  return find_transitem_dlg("invoice,receipt")
  
def find_transitem_dlg(transtype=None):
  query = ((ns.db.trans.deleted==0)
           &(ns.db.trans.transtype==ns.db.groups.id))
  left = [(ns.db.customer.on((ns.db.customer.id==ns.db.trans.customer_id)))]
  if transtype:
    transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue.belongs(transtype.split(",")))).select(ns.db.groups.id)
    query = query & ((ns.db.trans.transtype.belongs(transtype_id)))
    href=URL("find_transitem_dlg_"+transtype.split(",")[0])
  else:
    query = query & (ns.db.groups.groupvalue.belongs(("invoice","receipt","order","offer","worksheet","rent")))
    href=URL("find_transitem_dlg_all")
  fields = [ns.db.trans.id, ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, ns.db.customer.custname, ns.db.trans.transdate, ns.db.trans.curr]
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = set_transfilter(query)
    
  ns.db.trans.transdate.label = T("Date")
  ns.db.groups.groupvalue.label = T("Doc.Type")
  smenu = [ns.db.trans.transnumber,ns.db.trans.transdate,ns.db.customer.custname,ns.db.groups.groupvalue,ns.db.trans.curr]
  links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href=href, _title=T("Select Item"), 
                         _onclick='set_transitem_value("'+str(row.id)+'", "'+str(row.transnumber)+'", "'
                         +str(row.transtype)+'", "'+str(row.direction)+'", "'+str(row.curr)
                         +'");jQuery(this).parents(".dialog").hide();return true;')]
  return DIV(find_data("trans",query,fields,ns.db.trans.transnumber,10,25,links,left,False,smenu=smenu), _id="dlg_filter")  

def get_find_transpayment_dlg(transtype="all"):
  dlg = DIALOG(LOAD(f='find_transpayment_dlg_'+transtype, ajax=True), title=T('Select Document'), icon=URL(dir_images,'icon16_find.png'),
                  renderstyle=True, height=75)
  return A(SPAN(_class="icon magnifier"), _id="cmd_find_transpayment", _style="padding: 0px;padding-left: 6px;padding-right: 3px;", _class="w2p_trap buttontext button", 
           _href="#null", _title=T("Find Document"), _onclick='%s;return false' % dlg.show())
  
@ns_auth.requires_login()
def find_transpayment_dlg_all():
  return find_transpayment_dlg()

@ns_auth.requires_login()
def find_transpayment_dlg_bank():
  return find_transpayment_dlg("bank")

@ns_auth.requires_login()
def find_transpayment_dlg_cash():
  return find_transpayment_dlg("cash")

def find_transpayment_dlg(transtype=None):
  query = ((ns.db.trans.deleted==0)
           &(ns.db.trans.transtype==ns.db.groups.id)
           &(ns.db.trans.place_id==ns.db.place.id))
  left = None
  if transtype:
    transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue==transtype)).select().as_list()[0]["id"]
    query = query & ((ns.db.trans.transtype==transtype_id))
    href=URL("find_transpayment_dlg_"+transtype)
  else:
    query = query & (ns.db.groups.groupvalue.belongs(("bank","cash")))
    href=URL("find_transpayment_dlg_all")
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
      
  #set transfilter
  query = set_transfilter(query)
  
  fields = [ns.db.trans.id, ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction, ns.db.place.planumber, ns.db.place.curr]
    
  ns.db.groups.groupvalue.label = T("Doc.Type")
  ns.db.place.planumber.label = T("Bank/Ch.")
  smenu = [ns.db.trans.transnumber,ns.db.place.planumber,ns.db.groups.groupvalue,ns.db.place.curr]
  links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href=href, _title=T("Select Item"), 
                         _onclick='set_transpayment_value("'+str(row.trans.id)+'", "'+str(row.trans.transnumber)+'", "'
                         +str(row.trans.transtype)+'", "'+str(row.place.curr)
                         +'");jQuery(this).parents(".dialog").hide();return true;')]
  return DIV(find_data("trans",query,fields,ns.db.trans.transnumber,10,25,links,left,False,smenu=smenu), _id="dlg_filter")

def get_find_transmovement_dlg(transtype="all"):
  dlg = DIALOG(LOAD(f='find_transmovement_dlg_'+transtype, ajax=True), title=T('Select Document'), icon=URL(dir_images,'icon16_find.png'),
                  renderstyle=True, height=75)
  return A(SPAN(_class="icon magnifier"), _id="cmd_find_transmovement", _style="padding: 0px;padding-left: 6px;padding-right: 3px;", _class="w2p_trap buttontext button", 
           _href="#null", _title=T("Find Document"), _onclick='%s;return false' % dlg.show())

@ns_auth.requires_login()
def find_transmovement_dlg_all():
  return find_transmovement_dlg()
  
def find_transmovement_dlg(transtype=None):
  query = ((ns.db.trans.deleted==0)
           &(ns.db.trans.transtype==ns.db.groups.id))
  left = None
  if transtype:
    transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue==transtype)).select().as_list()[0]["id"]
    query = query & ((ns.db.trans.transtype==transtype_id))
    href=URL("find_transmovement_dlg_"+transtype)
  else:
    query = query & (ns.db.groups.groupvalue.belongs(("inventory","delivery","production","waybill","formula")))
    href=URL("find_transmovement_dlg_all")
    
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
  
  #set transfilter
  query = set_transfilter(query)
  
  fields = [ns.db.trans.id, ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.trans.direction]
    
  ns.db.groups.groupvalue.label = T("Doc.Type")
  smenu = [ns.db.trans.transnumber,ns.db.groups.groupvalue]
  links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href=href, _title=T("Select Item"), 
                         _onclick='set_transmovement_value("'+str(row.id)+'", "'+str(row.transnumber)+'", "'
                         +str(row.transtype)+'", "'+str(row.direction)
                         +'");jQuery(this).parents(".dialog").hide();return true;')]
  return DIV(find_data("trans",query,fields,ns.db.trans.transnumber,10,25,links,left,False,smenu=smenu), _id="dlg_filter")  

def get_find_payment_dlg(transtype="all"):
  dlg = DIALOG(LOAD(f='find_payment_dlg_'+transtype, ajax=True), title=T('Select Transaction'), icon=URL(dir_images,'icon16_find.png'),
                  renderstyle=True, height=75)
  return A(SPAN(_class="icon magnifier"), _id="cmd_find_payment", _style="padding: 0px;padding-left: 6px;padding-right: 3px;", _class="w2p_trap buttontext button", 
           _href="#null", _title=T("Find Transaction"), _onclick='%s;return false' % dlg.show())
  
@ns_auth.requires_login()
def find_payment_dlg_all():
  return find_payment_dlg()

def find_payment_dlg(transtype=None):
  query = ((ns.db.trans.deleted==0)&(ns.db.trans.id==ns.db.payment.trans_id)&(ns.db.payment.deleted==0)&(ns.db.trans.place_id==ns.db.place.id))
  if transtype:
    transtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue==transtype)).select().as_list()[0]["id"]
    query = query & ((ns.db.trans.transtype==transtype_id))
    href=URL("find_payment_dlg_"+transtype)
  else:
    href=URL("find_payment_dlg_all")
  fields = [ns.db.payment.id, ns.db.trans.transnumber, ns.db.trans.transtype, ns.db.fieldvalue.value, 
            ns.db.payment.paiddate, ns.db.trans.place_id, ns.db.place.curr, ns.db.payment.amount]
  left = [(ns.db.fieldvalue.on((ns.db.trans.id==ns.db.fieldvalue.ref_id)&(ns.db.fieldvalue.fieldname=='trans_transcast')&(ns.db.fieldvalue.deleted==0)))]
  
  #disabled transtype list
  audit = get_audit_subtype("trans")
  if len(audit)>0:
    query = query & (~ns.db.trans.transtype.belongs(audit))
    
  #set transfilter
  query = set_transfilter(query)
  
  ns.db.groups.groupvalue.label = T("Doc.Type")
  smenu = [ns.db.trans.transnumber,ns.db.payment.paiddate,ns.db.place.planumber,ns.db.groups.groupvalue,ns.db.place.curr, ns.db.payment.amount]
  links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href=href, _title=T("Select Item"), 
                         _onclick='set_payment_value("'+str(row.payment.id)+'", "'+str(row.trans.transnumber)+'", "'
                         +str(row.trans.transtype)+'", "'+str(row.place.curr)+'", '+str(row.payment.amount)
                         +');jQuery(this).parents(".dialog").hide();return true;')]
  return DIV(find_data("payment",query,fields,ns.db.trans.transnumber,10,25,links,left,False,smenu=smenu), _id="dlg_filter")

@ns_auth.requires_login()
def find_product_stock_dlg():
  ruri = request.wsgi.environ["REQUEST_URI"]
  product_id = ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1]
  try:
    product_id = int(product_id)
  except Exception:
    product_id = None
  
  movetype_inventory_id = ns.db((ns.db.groups.groupname=="movetype")&(ns.db.groups.groupvalue=="inventory")).select().as_list()[0]["id"]
  
  join = [(ns.db.product.on((ns.db.movement.product_id==ns.db.product.id))),
          (ns.db.trans.on((ns.db.movement.trans_id==ns.db.trans.id)&(ns.db.trans.deleted==0))),
          (ns.db.place.on((ns.db.movement.place_id==ns.db.place.id)))]
  left = None
  
  query = ((ns.db.movement.deleted==0)&(ns.db.movement.movetype==movetype_inventory_id))
  if product_id:
    query = query &(ns.db.movement.product_id==product_id)
    fields = [ns.db.place.planumber, ns.db.place.description, ns.db.product.unit, ns.db.movement.notes,
            ns.db.movement.qty, ns.db.movement.shippingdate]
    groupfields=[ns.db.movement.place_id,ns.db.place.planumber, ns.db.place.description, ns.db.product.unit, ns.db.movement.notes,
               ns.db.movement.qty.sum().with_alias('qty'),ns.db.movement.shippingdate.max().with_alias('shippingdate')]
    groupby=[ns.db.movement.place_id|ns.db.place.planumber|ns.db.place.description|ns.db.product.unit|ns.db.movement.notes]
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
  ns.db.movement.shippingdate.represent = lambda value,row: formatDate(row["shippingdate"])  

  links = [lambda row: A(SPAN(_class="icon check"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", 
                         _class="w2p_trap buttontext button", _href=URL("find_customer_dlg"), _title=T("Select Warehouse"), 
                         _onclick='set_place_value("'+str(row.movement.place_id)+'", "'+str(row.place.planumber)+'");jQuery(this).parents(".dialog").hide();return true;')]
  
  form = SimpleGrid.grid(query=query, field_id=ns.db.movement.place_id, 
             fields=fields, groupfields=groupfields, groupby=groupby, left=left, having=None, join=join,
             orderby=ns.db.movement.place_id, sortable=True, paginate=10, maxtextlength=25,
             showbuttontext=False, editable=False, links=links)
  
  return DIV(form, _id="dlg_filter")

def find_data(table,query,fields,orderby,paginate,maxtextlength,links,left=None,create=True,searchable=True,smenu=None):
  if request.vars.has_key("keywords")==False and request.vars.has_key("page")==False:
    query = (query&(ns.db[table].id==-1))
  tablenames = db._adapter.tables(query)
  if left!=None:
    tablenames=tablenames+ns.db._adapter.tables(left)
  
  if smenu:
    search_widget = create_search_widget(smenu)
  else:
    search_widget="default"
    for qtable in tablenames:
      for field in ns.db[qtable].fields:
        ns.db[qtable][field].readable=False
    for field in fields:
      field.readable=True
  ns.db[table].id.readable = ns.db[table].id.writable = False
  gform = SQLFORM.grid(query=query, field_id=ns.db[table].id, fields=fields, left=left,
                     orderby=orderby, paginate=paginate, maxtextlength=maxtextlength, 
                     searchable=searchable, csv=False, details=(links==None), showbuttontext=False,
                     create=(((links==None) and (create==True)) or create), deletable=False, editable=False, selectable=False,
                     links=links, user_signature=False, search_widget=search_widget)
  if type(gform[1][0][0]).__name__!="TABLE":
    gform[1][0][0] = ""
  else:
    gform = move_buttons(gform)
  return gform

@ns_auth.requires_login()
def frm_deffield_all():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  response.title=T('SETTINGS')
  response.subtitle=T('Additional Data')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_deffield.png')
  return dict(form=frm_deffield("all"))

@ns_auth.requires_login()
def frm_deffield_employee():
  response.title=T('EMPLOYEE')
  response.subtitle=T('Additional Data')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_user.png')
  return dict(form=frm_deffield("employee"))

@ns_auth.requires_login()
def frm_deffield_place():
  response.title=T('PLACE')
  response.subtitle=T('Additional Data')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_book.png')
  return dict(form=frm_deffield("place"))

@ns_auth.requires_login()
def frm_deffield_groups():
  response.title=T('GROUPS')
  response.subtitle=T('Additional Data')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_edit.png')
  return dict(form=frm_deffield("groups"))

@ns_auth.requires_login()
def frm_deffield_setting():
  response.title=T('SETTINGS')
  response.subtitle=T('Database Settings')
  if request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_numberdef.png')
  return dict(form=frm_deffield("setting"))

@ns_auth.requires_login()
def frm_deffield_customer():
  response.title=T('CUSTOMER')
  response.subtitle=T('Additional Data')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_customer.png')
  return dict(form=frm_deffield("customer"))

@ns_auth.requires_login()
def frm_deffield_product():
  response.title=T('PRODUCT')
  response.subtitle=T('Additional Data')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_parts.png')
  return dict(form=frm_deffield("product"))

@ns_auth.requires_login()
def frm_deffield_event():
  response.title=T('EVENT')
  response.subtitle=T('Additional Data')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  return dict(form=frm_deffield("event"))

@ns_auth.requires_login()
def frm_deffield_tool():
  response.title=T('TOOL')
  response.subtitle=T('Additional Data')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_wrench.png')
  return dict(form=frm_deffield("tool"))

@ns_auth.requires_login()
def frm_deffield_project():
  response.title=T('PROJECT')
  response.subtitle=T('Additional Data')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_date_edit.png')
  return dict(form=frm_deffield("project"))

@ns_auth.requires_login()
def frm_deffield_trans():
  response.title=T('TRANSACTION')
  response.subtitle=T('Additional Data')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_deffield.png')
  return dict(form=frm_deffield("trans"))

def frm_deffield(nervatype,subtype=None):
  ruri = request.wsgi.environ["REQUEST_URI"]
  response.view=dir_view+'/deffield.html'
  response.cmd_help = get_help_button("deffield")
  if nervatype!="all":
    nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue==nervatype)).select().as_list()[0]["id"]
  else:
    ns.db.deffield.nervatype.label = T("N.Type")
    nervatype_id = None
  if subtype!=None:
    subtype_id = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue==subtype)).select().as_list()[0]["id"]
  else:
    subtype_id = None
  
  if str(ruri).find("delete/deffield")>0:
    deffield_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    delete_ini = getSetting("set_trans_deleted")
    if delete_ini != "true":
      values = {"deleted":1}
      ns.db(ns.db.deffield.id==deffield_id).update(**values)
    else:
      ns.db(ns.db.fieldvalue.fieldname == ns.db.deffield(id=deffield_id).fieldname).delete()
      ns.db(ns.db.deffield.id==deffield_id).delete()
      ns.db.commit()
    redirect(URL('frm_deffield_'+nervatype))
  
  ns.db.deffield.fieldtype.requires = IS_IN_DB(ns.db((ns.db.groups.groupname.like('fieldtype'))&(ns.db.groups.groupvalue!="filter")&(ns.db.groups.groupvalue!="checkbox")&(ns.db.groups.groupvalue!="trans")), ns.db.groups.id, '%(groupvalue)s')
  ns.db.deffield.id.readable = ns.db.deffield.id.writable = False
  ns.db.deffield.subtype.readable = ns.db.deffield.subtype.writable = False
  ns.db.deffield.deleted.readable = ns.db.deffield.deleted.writable = False
  audit_filter = get_audit_filter("setting", None)[0]
  
  if str(ruri).find("new/deffield")>0 or str(ruri).find("edit/deffield")>0 or str(ruri).find("view/groups")>0:
    response.prm_input = True
    response.cmd_back = get_back_button(URL('frm_deffield_'+nervatype))
    
    ns.db.deffield.fieldname.writable = False
    ns.db.deffield.description.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
    if str(ruri).find("edit/deffield")>0 or str(ruri).find("view/groups")>0:
      ns.db.deffield.nervatype.writable = False
      ns.db.deffield.fieldtype.writable = False
      deffield_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      valuelist_id = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="valuelist")).select().as_list()[0]["id"]
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
      form = SQLFORM(ns.db.deffield, record=deffield_id, submit_button=T("Save"), comments = False)
    else:
      deffield_id = -1
      form = SQLFORM(ns.db.deffield, submit_button=T("Save"), comments = False)
      form.vars.nervatype = nervatype_id
      
    if request.post_vars:
      form.vars.subtype = subtype
      if deffield_id == -1:
        form.vars.fieldname = web2py_uuid()
    if form.validate(keepvalues=True):
      if str(ruri).find("new/deffield")>0:
        form.vars.id = ns.db.deffield.insert(**dict(form.vars))
        redirect(URL('frm_deffield_'+nervatype+'/edit/deffield/'+str(form.vars.id)))
      else:
        ns.db(ns.db.deffield.id==deffield_id).update(**form.vars)
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        if str(ns.db.deffield.fields).find(error)>0:
          flash+=ns.db.deffield[error].label+": "+form.errors[error]+", "
        else:
          flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    form.custom.widget.addnew = get_bool_input(deffield_id,"deffield","addnew")
    form.custom.widget.visible = get_bool_input(deffield_id,"deffield","visible")
    form.custom.widget.readonly = get_bool_input(deffield_id,"deffield","readonly")
    if audit_filter=="readonly":
      form.custom.submit = ""
  else:
    response.cmd_back = get_back_button(session.back_url)
    response.margin_top = "20px"
    
    ns.db.deffield.fieldname.readable = ns.db.deffield.fieldname.writable = False
    ns.db.deffield.valuelist.readable = ns.db.deffield.valuelist.writable = False
    ns.db.deffield.addnew.readable = ns.db.deffield.addnew.writable = False
    ns.db.deffield.visible.readable = ns.db.deffield.visible.writable = False
    ns.db.deffield.readonly.readable = ns.db.deffield.readonly.writable = False
    ns.db.groups.groupvalue.label = T("N.Type")
    if nervatype!="all":
      fields=[ns.db.deffield.description,ns.db.deffield.fieldtype]
      deffield = ((ns.db.deffield.nervatype==nervatype_id)&(ns.db.deffield.subtype==subtype_id)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1))
      smenu = [ns.db.deffield.description]
    else:
      fields=[ns.db.groups.groupvalue,ns.db.deffield.description]
      deffield = ((ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==ns.db.groups.id))
      smenu = [ns.db.groups.groupvalue,ns.db.deffield.description]
    
    search_widget = create_search_widget(smenu)
    form = SQLFORM.grid(query=deffield, field_id=ns.db.deffield.id, fields=fields, #headers=headers,
                 orderby=ns.db.deffield.description, sortable=True, paginate=10, maxtextlength=25,
                 searchable=True, csv=False, details=False, showbuttontext=False,
                 create=(audit_filter=="all"), deletable=(audit_filter=="all"), editable=True, selectable=False, 
                 user_signature=False, search_widget=search_widget)
    if type(form[1][0][0]).__name__=="TABLE":
      form=move_buttons(form)
    set_counter_bug(form)
  return form

@ns_auth.requires_login()
def frm_groups_usergroup():
  audit_filter_setting = get_audit_filter("setting", None)[0]
  audit_filter_audit = get_audit_filter("audit", None)[0]
  if audit_filter_setting=="disabled" or audit_filter_audit=="disabled":
    audit_filter="disabled"
  elif audit_filter_setting=="readonly" or audit_filter_audit=="readonly":
    audit_filter="readonly"
  elif audit_filter_setting=="update" or audit_filter_audit=="update":
    audit_filter="update"
  else:
    audit_filter="all"
  if audit_filter=="disabled":
    return show_disabled()
  response.title=T('SETTINGS')
  response.subtitle=T('User groups and access rights')
  ruri = request.wsgi.environ["REQUEST_URI"]
  if str(ruri).find("new/groups")>0:
    redirect(URL('frm_audit/new/usergroup'))
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL('index')
  response.titleicon = URL(dir_images,'icon16_user.png')
  cmd_lnk = [lambda row: A(SPAN(_class="icon key"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("frm_audit/view/usergroup/"+str(row.id)), _title=T("Access rights"))]
  return dict(form=frm_groups("usergroup",cmd_lnk,audit_filter))

@ns_auth.requires_login()
def frm_groups_printer():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  response.title=T('SETTINGS')
  response.subtitle=T('Server printers')
  ruri = request.wsgi.environ["REQUEST_URI"]
  if str(ruri).find("new/groups")>0:
    redirect(URL('frm_printer/new/printer'))
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL('index')
  response.titleicon = URL(dir_images,'icon16_printer.png')
  cmd_lnk = [lambda row: A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href=URL("frm_printer/view/printer/"+str(row.id)), _title=T("Server printer"))]
  ns.db.groups.groupvalue.label = T('Name')
  return dict(form=frm_groups("printer",cmd_lnk,audit_filter))

@ns_auth.requires_login()
def frm_groups_all():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  response.title=T('SETTINGS')
  response.subtitle=T('Groups')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_edit.png')
  return dict(form=frm_groups("all"))

@ns_auth.requires_login()
def frm_groups_department():
  response.title=T('SETTINGS')
  response.subtitle=T('Departments')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_user.png')
  return dict(form=frm_groups("department"))

@ns_auth.requires_login()
def frm_groups_customer():
  response.title=T('CUSTOMER')
  response.subtitle=T('Groups')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_customer.png')
  return dict(form=frm_groups("customer"))

@ns_auth.requires_login()
def frm_groups_product():
  response.title=T('PRODUCT')
  response.subtitle=T('Groups')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_parts.png')
  return dict(form=frm_groups("product"))

@ns_auth.requires_login()
def frm_groups_eventgroup():
  response.title=T('EVENT')
  response.subtitle=T('Groups')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_calendar.png')
  return dict(form=frm_groups("eventgroup"))

@ns_auth.requires_login()
def frm_groups_toolgroup():
  response.title=T('TOOL')
  response.subtitle=T('Groups')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_wrench.png')
  return dict(form=frm_groups("toolgroup"))

@ns_auth.requires_login()
def frm_groups_rategroup():
  response.title=T('RATE')
  response.subtitle=T('Groups')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_percent.png')
  return dict(form=frm_groups("rategroup"))

@ns_auth.requires_login()
def frm_groups_trans():
  response.title=T('TRANSACTION')
  response.subtitle=T('Groups')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_edit.png')
  return dict(form=frm_groups("trans"))

@ns_auth.requires_login()
def frm_groups_paidtype():
  response.title=T('SETTINGS')
  response.subtitle=T('Payment types')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_money.png')
  return dict(form=frm_groups("paidtype"))

def frm_groups(groupname, cmd_lnk=None, audit_filter=None):
  ruri = request.wsgi.environ["REQUEST_URI"]
  response.view=dir_view+'/groups.html'
  response.cmd_help = get_help_button("groups")
  if not audit_filter:
    audit_filter = get_audit_filter("setting", None)[0]
  
  if str(ruri).find("delete/groups")>0:
    group_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    delete_ini = getSetting("set_trans_deleted")
    if delete_ini != "true":
      values = {"deleted":1}
      ns.db(ns.db.groups.id==group_id).update(**values)
    else:
      dfield = deleteFieldValues("groups", group_id)
      if dfield!=True:
        session.flash = dfield
        if request.wsgi.environ.has_key("HTTP_REFERER"):
          redirect(request.wsgi.environ["HTTP_REFERER"])
        else:
          redirect(URL('frm_groups_'+groupname))
      ns.db(ns.db.groups.id==group_id).delete()
      ns.db.commit()
    redirect(URL('frm_groups_'+groupname))
  
  ns.db.groups.groupname.label = T("G.Type")
  if str(ruri).find("new/groups")>0 or str(ruri).find("edit/groups")>0 or str(ruri).find("view/groups")>0:
    response.prm_input = True
    response.cmd_back = get_back_button(URL('frm_groups_'+groupname))
    
    if str(ruri).find("new/groups")>0:
      groups_id=-1
      ns.db.groups.groupname.requires = IS_IN_SET(("customer","department","eventgroup","paidtype","product","toolgroup","trans","rategroup"))
      form = SQLFORM(ns.db.groups, submit_button=T("Save"))
      if groupname!="all":
        form.vars.groupname=groupname
      response.subtitle=T('New value')
      response.cmd_delete = ""
    else: 
      groups_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      ns.db.groups.groupname.writable = False
      response.subtitle=T('Edit value')
      form = SQLFORM(ns.db.groups, record = groups_id, submit_button=T("Save"))
      if audit_filter=="all":
        response.cmd_delete = get_command_button(caption=T("Delete"),title=T("Delete"),color="A52A2A",
                              cmd="if(confirm('"+T('Are you sure you want to delete this group?')+
                              "')){window.location ='"+URL("frm_groups_"+groupname+"/delete/groups/"+str(groups_id))+"';};return false;")
      else:
        response.cmd_delete = ""
      
    if form.validate(keepvalues=True):
      group = ns.db((ns.db.groups.id!=groups_id)&(ns.db.groups.groupname==request.post_vars.groupname)&(ns.db.groups.groupvalue==form.vars.groupvalue)).select().as_list()
      if len(group)==0:
        if str(ruri).find("new/groups")>0:
          form.vars.id = ns.db.groups.insert(**dict(form.vars))
          redirect(URL('frm_groups_'+groupname+'/view/groups/'+str(form.vars.id)))
        else:
          ns.db(ns.db.groups.id==groups_id).update(**form.vars)
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
    
    form.custom.widget.inactive = get_bool_input(groups_id,"groups","inactive")
    if audit_filter=="readonly":
      form.custom.submit = ""
  else:
    response.cmd_back = get_back_button(session.back_url)
    response.margin_top = "20px"
    
    ns.db.groups.id.readable = ns.db.groups.id.writable = False
    ns.db.groups.deleted.readable = ns.db.groups.deleted.writable = False
    if groupname!="all":
      groups = ((ns.db.groups.groupname==groupname)&(ns.db.groups.deleted==0))
      ns.db.groups.groupname.readable = ns.db.groups.groupname.writable = False
    else:
      groups = ((ns.db.groups.groupname.belongs(("customer","department","eventgroup","paidtype","product","toolgroup","trans","rategroup")))&(ns.db.groups.deleted==0))
    
    if ns.db.groups.groupname.readable:
      fields = [ns.db.groups.groupname,ns.db.groups.groupvalue,ns.db.groups.description,ns.db.groups.inactive]
      smenu = [ns.db.groups.groupname,ns.db.groups.groupvalue,ns.db.groups.description]
    else:
      fields = [ns.db.groups.groupvalue,ns.db.groups.description,ns.db.groups.inactive]
      smenu = [ns.db.groups.groupvalue,ns.db.groups.description]
    search_widget = create_search_widget(smenu)
    form = SQLFORM.grid(query=groups, field_id=ns.db.groups.id, fields=fields, #headers=headers,
                 orderby=ns.db.groups.groupvalue, sortable=True, paginate=10, maxtextlength=25,
                 searchable=True, csv=False, details=False, showbuttontext=False,
                 create=(audit_filter=="all"), deletable=((cmd_lnk==None) and (audit_filter=="all")), 
                 editable=(cmd_lnk==None), selectable=False, 
                 links=cmd_lnk, user_signature=False, search_widget=search_widget)
    if type(form[1][0][0]).__name__=="TABLE":
      form=move_buttons(form)
    set_counter_bug(form)
  return form

def frm_setting():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    redirect(URL('frm_setting'))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    if delete_row("fieldvalue", fieldvalue_id, "setting", None):
      redirect(URL('frm_setting'))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    clear_post_vars()
    if request.post_vars.has_key("ref_id"):
      if request.post_vars["ref_id"]=="":
        del request.post_vars["ref_id"]
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.fieldvalue.id==request.post_vars["id"]).validate_and_update(**request.post_vars)      
      else:
        ns.db.fieldvalue.validate_and_insert(**request.post_vars)
      redirect(URL('frm_setting'))
    except Exception, err:
      response.flash = str(err)
      
  response.view=dir_view+'/setting.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Database Settings')
  response.titleicon = URL(dir_images,'icon16_numberdef.png')
  response.cmd_help = get_help_button("setting")
  response.cmd_back = get_home_button()
  response.margin_top = "20px"
  
  nervatype_setting = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
  setting_fields = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype_setting))
  fields=[ns.db.deffield.description, ns.db.fieldvalue.value, ns.db.fieldvalue.notes]
  smenu = [ns.db.deffield.description, ns.db.fieldvalue.value, ns.db.fieldvalue.notes]
  search_widget = create_search_widget(smenu)
  
  links = set_view_fields("setting", nervatype_setting, 0, (audit_filter!="readonly"), setting_fields, None, "", "",False)
      
  form = SQLFORM.grid(query=setting_fields, field_id=ns.db.fieldvalue.id, fields=fields, #headers=headers,
               orderby=ns.db.deffield.description, sortable=True, paginate=10, maxtextlength=25,
               searchable=True, csv=False, details=False, showbuttontext=False,
               create=False, deletable=False, editable=False, selectable=False, links=links, 
               user_signature=False, search_widget=search_widget)
  if type(form[1][0][0]).__name__=="TABLE":
    form=move_buttons(form)
  set_counter_bug(form)
  if DEMO_MODE:
    response.cmd_fieldvalue_submit = DIV(SPAN(T('DEMO MODE')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
  return dict(form=form)

def frm_numberdef():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  response.view=dir_view+'/numberdef.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Transaction Numbering')
  response.titleicon = URL(dir_images,'icon16_numberdef.png')
  response.cmd_help = get_help_button("numberdef")
  
  ns.db.numberdef.id.readable = ns.db.numberdef.id.writable = False
  ns.db.numberdef.visible.readable = ns.db.numberdef.visible.writable = False
  ns.db.numberdef.readonly.readable = ns.db.numberdef.readonly.writable = False
  ns.db.numberdef.orderby.readable = ns.db.numberdef.orderby.writable = False
  ns.db.numberdef.numberkey.writable = False
  ns.db.numberdef.description.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
  if str(ruri).find("edit/numberdef")>0:
    response.edit = True
    response.subtitle=T('Edit value')
    response.cmd_back = get_back_button(URL('frm_numberdef'))
    numberdef_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    form = SQLFORM(ns.db.numberdef, record=numberdef_id, submit_button=T("Save"), comments = False, formstyle = 'divs')
    if form.validate(keepvalues=True):
      ns.db(ns.db.numberdef.id==numberdef_id).update(**form.vars)
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    form.custom.widget.isyear = get_bool_input(numberdef_id,"numberdef","isyear")
    response.back_url = URL('frm_numberdef')
    response.readonly = ns.db.numberdef(id=numberdef_id)["readonly"]
    if audit_filter=="readonly":
      form.custom.submit=""
  else:
    response.margin_top = "20px"
    response.cmd_back = get_home_button()
    numberdef = ((ns.db.numberdef.visible==1))
    fields = [ns.db.numberdef.numberkey,ns.db.numberdef.prefix,ns.db.numberdef.curvalue,ns.db.numberdef.isyear,ns.db.numberdef.sep,
              ns.db.numberdef.len,ns.db.numberdef.description]
    smenu = [ns.db.numberdef.numberkey,ns.db.numberdef.prefix,ns.db.numberdef.description]
    search_widget = create_search_widget(smenu)
    form = SQLFORM.grid(query=numberdef, field_id=ns.db.numberdef.id, fields=fields, #headers=headers,
                 orderby=ns.db.numberdef.numberkey, sortable=True, paginate=10, maxtextlength=25,
                 searchable=True, csv=False, details=False, showbuttontext=False,
                 create=False, deletable=False, editable=True, selectable=False, 
                 user_signature=False, search_widget=search_widget)
    if type(form[1][0][0]).__name__=="TABLE":
      form=move_buttons(form)
    set_counter_bug(form)
  return dict(form=DIV(form, _id="dlg_frm"))

def frm_tax():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  if str(ruri).find("delete/tax")>0:
    tax_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
#    delete_ini = getSetting("set_trans_deleted")
#    if delete_ini != "true":
#      values = {"deleted":1}
#      ns.db(ns.db.tax.id==tax_id).update(**values)
#    else:
    dfield = deleteFieldValues("tax", tax_id)
    if dfield!=True:
      session.flash = dfield
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(URL('frm_tax'))
    ns.db(ns.db.tax.id==tax_id).delete()
    ns.db.commit()
    redirect(URL('frm_tax'))
    
  response.view=dir_view+'/tax.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Tax')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_percent.png')
  response.cmd_back = get_back_button(session.back_url)
  ns.db.tax.id.readable = ns.db.tax.id.writable = False
  ns.db.tax.taxcode.label = T('Code')
  if str(ruri).find("new/tax")>0 or str(ruri).find("edit/tax")>0:
    response.edit = True
    if str(ruri).find("edit/tax")>0:
      tax_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      response.subtitle=T('Edit tax')
      form = SQLFORM(ns.db.tax, record=tax_id, submit_button=T("Save"), comments = False, formstyle = 'divs')
    else:
      tax_id = -1
      response.subtitle=T('New tax')
      form = SQLFORM(ns.db.tax, submit_button=T("Save"), comments = False, formstyle = 'divs')
    
    if form.validate(keepvalues=True):
      if str(ruri).find("new/tax")>0:
        form.vars.id = ns.db.tax.insert(**dict(form.vars))
        redirect(URL('frm_tax'))
      else:
        ns.db(ns.db.tax.id==tax_id).update(**form.vars)
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    response.cmd_back = get_back_button(URL('frm_tax'))
    if audit_filter=="readonly":
      form.custom.submit = ""
  else:
    response.margin_top = "20px"
    fields = [ns.db.tax.taxcode,ns.db.tax.description,ns.db.tax.rate,ns.db.tax.inactive]
    smenu = [ns.db.tax.taxcode,ns.db.tax.description,ns.db.tax.rate,ns.db.tax.inactive]
    search_widget = create_search_widget(smenu)
    
    form = SQLFORM.grid(query=ns.db.tax, field_id=ns.db.tax.id, fields=fields, #headers=headers,
                 orderby=ns.db.tax.taxcode, sortable=True, paginate=10, maxtextlength=25,
                 searchable=False, csv=False, details=False, showbuttontext=False,
                 create=(audit_filter=="all"), deletable=(audit_filter=="all"), editable=True, selectable=False, 
                 user_signature=False, search_widget=search_widget)
    if type(form[1][0][0]).__name__!="TABLE":
      form = ""
    else:
      form=move_buttons(form)
  return dict(form=DIV(form, _id="dlg_frm"))

def frm_currency():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  if str(ruri).find("delete/currency")>0:
    currency_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
#    delete_ini = getSetting("set_trans_deleted")
#    if delete_ini != "true":
#      values = {"deleted":1}
#      ns.db(ns.db.currency.id==currency_id).update(**values)
#    else:
    dfield = deleteFieldValues("currency", currency_id)
    if dfield!=True:
      session.flash = dfield
      if request.wsgi.environ.has_key("HTTP_REFERER"):
        redirect(request.wsgi.environ["HTTP_REFERER"])
      else:
        redirect(URL('frm_currency'))
    ns.db(ns.db.currency.id==currency_id).delete()
    ns.db.commit()
    redirect(URL('frm_currency'))
  response.view=dir_view+'/currency.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Currency')
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
  else:
    session.back_url = URL("index")
  response.titleicon = URL(dir_images,'icon16_money.png')
  response.cmd_back = get_back_button(session.back_url)
  ns.db.currency.id.readable = ns.db.currency.id.writable = False
  ns.db.currency.curr.label = T('Currency')
  if str(ruri).find("new/currency")>0 or str(ruri).find("edit/currency")>0:
    response.edit = True
    if str(ruri).find("edit/currency")>0:
      currency_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      response.subtitle=T('Edit currency')
      form = SQLFORM(ns.db.currency, record=currency_id, submit_button=T("Save"), comments = False, formstyle = 'divs')
    else:
      currency_id = -1
      response.subtitle=T('New currency')
      form = SQLFORM(ns.db.currency, submit_button=T("Save"), comments = False, formstyle = 'divs')
    
    if form.validate(keepvalues=True):
      if str(ruri).find("new/currency")>0:
        form.vars.id = ns.db.currency.insert(**dict(form.vars))
        redirect(URL('frm_currency'))
      else:
        ns.db(ns.db.currency.id==currency_id).update(**form.vars)
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    response.cmd_back = get_back_button(URL('frm_currency'))
    if audit_filter=="readonly":
      form.custom.submit = ""
  else:
    response.margin_top = "20px"
    fields = [ns.db.currency.curr,ns.db.currency.description,ns.db.currency.digit,ns.db.currency.defrate, ns.db.currency.cround]
    smenu = [ns.db.currency.curr,ns.db.currency.description]
    search_widget = create_search_widget(smenu)
    
    form = SQLFORM.grid(query=ns.db.currency, field_id=ns.db.currency.id, fields=fields, #headers=headers,
                 orderby=ns.db.currency.curr, sortable=True, paginate=10, maxtextlength=25,
                 searchable=True, csv=False, details=False, showbuttontext=False,
                 create=(audit_filter=="all"), deletable=(audit_filter=="all"), editable=True, selectable=False, 
                 user_signature=False, search_widget=search_widget)
    if type(form[1][0][0]).__name__!="TABLE":
      form = ""
    else:
      form=move_buttons(form)
  return dict(form=DIV(form, _id="dlg_frm"))

def frm_printer():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  if ruri.find("edit/fieldvalue")>0 or ruri.find("view/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    group_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    redirect(URL('frm_printer/view/printer/'+str(group_id)))
  
  if ruri.find("delete/fieldvalue")>0:
    fieldvalue_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    group_id = ns.db.fieldvalue(id=fieldvalue_id).ref_id
    if delete_row("fieldvalue", fieldvalue_id, "groups", group_id):
      redirect(URL('frm_printer/view/printer/'+str(group_id)))
      
  if request.post_vars["_formname"]=="fieldvalue/create":
    clear_post_vars()
    for pkey in request.post_vars.keys():
      if (str(pkey).startswith("value") and pkey!="value") or pkey in("readonly","fieldtype") :
        del request.post_vars[pkey]
    try:
      if request.post_vars.has_key("id"):
        ns.db(ns.db.fieldvalue.id==request.post_vars["id"]).validate_and_update(**request.post_vars)      
      else:
        ns.db.fieldvalue.validate_and_insert(**request.post_vars)
      setLogtable("update", "log_groups_update", "groups", request.post_vars["ref_id"])
      redirect(URL('frm_printer/view/printer/'+str(request.post_vars["ref_id"])))
    except Exception, err:
      response.flash = str(err)
      
  response.title=T('SETTINGS')
  response.view=dir_view+'/printer.html'
  response.titleicon = URL(dir_images,'icon16_printer.png')
  response.cmd_help = get_help_button("printer")
  response.margin_top = "20px"
  
  if str(ruri).find("delete/printer")>0:
    group_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    delete_ini = getSetting("set_trans_deleted")
    if delete_ini != "true":
      values = {"deleted":1}
      ns.db(ns.db.groups.id==group_id).update(**values)
    else:
      dfield = deleteFieldValues("groups", group_id)
      if dfield!=True:
        session.flash = dfield
        if request.wsgi.environ.has_key("HTTP_REFERER"):
          redirect(request.wsgi.environ["HTTP_REFERER"])
        else:
          redirect(URL('frm_groups_printer'))
      ns.db(ns.db.ui_audit.usergroup==group_id).delete()
      ns.db(ns.db.groups.id==group_id).delete()
      ns.db.commit()
    redirect(URL('frm_groups_printer'))
  
  ns.db.groups.groupvalue.label = T('Name')
  if str(ruri).find("edit/printer")>0 or str(ruri).find("view/printer")>0: 
    group_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])   
    response.subtitle=T('Edit printer')
    form = SQLFORM(ns.db.groups, record = group_id, submit_button=T("Save"))
    if audit_filter=="all":
      response.cmd_delete = INPUT(_type="button", _value=T("Delete"),
                                _style="height: 28px !important;padding-top: 4px !important;color: #A52A2A;width: 100%;", 
                                _onclick="javascript:if(confirm(w2p_ajax_confirm_message||'"+T('Are you sure you want to delete this printer?')
                                  +"')){window.location ='"+URL("frm_printer/delete/printer/"+str(group_id))+"';};return false;")
    else:
      response.cmd_delete = ""
  else:
    group_id=-1
    form = SQLFORM(ns.db.groups, submit_button=T("Save"))
    response.subtitle=T('New printer')
    response.cmd_delete = ""
  
  if request.post_vars:
    request.post_vars.groupname = "printer"  
  groups_nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  if form.validate(keepvalues=True):
    group = ns.db((ns.db.groups.id!=group_id)&(ns.db.groups.groupname=="printer")&(ns.db.groups.groupvalue==form.vars.groupvalue)).select().as_list()
    if len(group)==0:
      if str(ruri).find("new/printer")>0:
        form.vars.id = ns.db.groups.insert(**dict(form.vars))
        values = {"nervatype_1":groups_nervatype_id, "ref_id_1":form.vars.id, "nervatype_2":groups_nervatype_id, "ref_id_2":int(request.post_vars.printertype_id)}
        ns.db.link.insert(**values)
        redirect(URL('frm_printer/view/printer/'+str(form.vars.id)))
      else:
        ns.db(ns.db.groups.id==group_id).update(**form.vars)
        typelink = ns.db((ns.db.link.ref_id_1==group_id)&(ns.db.link.nervatype_1==groups_nervatype_id)
                  &(ns.db.link.nervatype_2==groups_nervatype_id)&(ns.db.link.deleted==0)).select().as_list()
        if len(typelink)>0:
          ns.db(ns.db.link.id==typelink[0]["id"]).update(**{"ref_id_2":int(request.post_vars.printertype_id)})
        else:
          values = {"nervatype_1":groups_nervatype_id, "ref_id_1":group_id, "nervatype_2":groups_nervatype_id, "ref_id_2":int(request.post_vars.printertype_id)}
          ns.db.link.insert(**values)
    else:
      form.errors["groupvalue"] = T('The printer name already exists!')
      response.flash = T('Error: ')+str(T('The printer name already exists!'))
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  form.custom.widget.inactive = get_bool_input(group_id,"groups","inactive")
  typelink = ns.db((ns.db.link.ref_id_1==group_id)&(ns.db.link.nervatype_1==groups_nervatype_id)
                  &(ns.db.link.nervatype_2==groups_nervatype_id)&(ns.db.link.deleted==0)).select().as_list()
  if len(typelink)>0:
    typelink = typelink[0]["ref_id_2"]
  else:
    typelink = ns.db((ns.db.groups.groupname=="printertype")&(ns.db.groups.groupvalue=="local")).select().as_list()[0]["id"]
  printertype = ns.db((ns.db.groups.groupname=="printertype")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.id).as_list()
  response.cmb_printertype = SELECT(*[OPTION(field["groupvalue"], _value=field["id"], _selected=(field["id"]==typelink)) for field in printertype], _id="cmb_printertype",
                                    _onchange="document.getElementById('printertype_id').value=this.value")
  response.printertype_id = INPUT(_name="printertype_id", _type="hidden", _value=typelink, _id="printertype_id")
  
  response.cmd_back = get_back_button(URL('frm_groups_printer'))
  
  #additional fields data
  if group_id>-1:
    fieldvalue = ((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)
           &(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==groups_nervatype_id)&(ns.db.fieldvalue.ref_id==group_id))
    editable = not (audit_filter in ("readonly","disabled"))
    set_view_fields("printer", groups_nervatype_id, 0, editable, fieldvalue, group_id, "/frm_printer", "/frm_printer/view/printer/"+str(group_id))
    response.cmd_fields = get_goprop_button(title=T("Edit Additional Data"), url=URL("frm_deffield_groups?back=1"))
  
  if audit_filter=="readonly":
    form.custom.submit = ""
  
  return dict(form=form)

def frm_audit():
  audit_filter_setting = get_audit_filter("setting", None)[0]
  audit_filter_audit = get_audit_filter("audit", None)[0]
  if audit_filter_setting=="disabled" or audit_filter_audit=="disabled":
    audit_filter="disabled"
  elif audit_filter_setting=="readonly" or audit_filter_audit=="readonly":
    audit_filter="readonly"
  elif audit_filter_setting=="update" or audit_filter_audit=="update":
    audit_filter="update"
  else:
    audit_filter="all"
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  response.title=T('SETTINGS')
  response.view=dir_view+'/audit.html'
  response.titleicon = URL(dir_images,'icon16_key.png')
  response.cmd_help = get_help_button("audit")
  response.margin_top = "20px"
  
  if str(ruri).find("delete/usergroup")>0:
    usergroup_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    emplink = ns.db((ns.db.employee.usergroup==usergroup_id)&(ns.db.employee.deleted==0)).select().as_list()
    if len(emplink)>0:
      session.flash = T('Error: ')+str(T('The group can not be deleted, because users are assigned!'))
      redirect(URL('frm_audit/view/usergroup/'+str(usergroup_id)))
    else:
      delete_ini = getSetting("set_trans_deleted")
      if delete_ini != "true":
        values = {"deleted":1}
        ns.db(ns.db.groups.id==usergroup_id).update(**values)
      else:
        dfield = deleteFieldValues("groups", usergroup_id)
        if dfield!=True:
          session.flash = dfield
          if request.wsgi.environ.has_key("HTTP_REFERER"):
            redirect(request.wsgi.environ["HTTP_REFERER"])
          else:
            redirect(URL('frm_groups_usergroup'))
        ns.db(ns.db.ui_audit.usergroup==usergroup_id).delete()
        ns.db(ns.db.groups.id==usergroup_id).delete()
        ns.db.commit()
      redirect(URL('frm_groups_usergroup'))
  
  if str(ruri).find("delete/ui_audit")>0:
    audit_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    ns.db(ns.db.ui_audit.id==audit_id).delete()
    ns.db.commit()
  
  if str(ruri).find("edit/ui_audit")>0 or str(ruri).find("view/ui_audit")>0 or str(ruri).find("new/ui_audit")>0:
    response.prm_input = True
    ns.db.ui_audit.supervisor.readable = ns.db.ui_audit.supervisor.writable = False          
    if str(ruri).find("new/ui_audit")>0:
      audit_id=-1
      usergroup_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      ns.db.ui_audit.nervatype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('nervatype')
                                                      &ns.db.groups.groupvalue.belongs(("audit","customer","product","price","employee","tool","project","event","setting","trans","menu","report"))), 
                                                ns.db.groups.id, '%(groupvalue)s')
      ns.db.ui_audit.subtype.readable = ns.db.ui_audit.subtype.writable = False
      response.subtitle=T('New access right')
      form = SQLFORM(ns.db.ui_audit, submit_button=T("Save"))
      form.vars.inputfilter = ns.db((ns.db.groups.groupname=="inputfilter")&(ns.db.groups.groupvalue=="all")).select().as_list()[0]["id"]
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
      form = SQLFORM(ns.db.ui_audit, record = audit_id, submit_button=T("Save"))
    
    response.cmd_back = get_back_button(URL('frm_audit/view/usergroup/'+str(usergroup_id)))
    
    if request.post_vars:
      request.post_vars.usergroup = usergroup_id
    if form.validate(keepvalues=True):
      if str(ruri).find("new/ui_audit")>0:
        form.vars.id = ns.db.ui_audit.insert(**dict(form.vars))
        redirect(URL('frm_audit/view/ui_audit/'+str(form.vars.id)))
      else:
        ns.db(ns.db.ui_audit.id==audit_id).update(**form.vars)
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    form.custom.widget.supervisor = get_bool_input(audit_id,"ui_audit","supervisor")
    if audit_filter=="readonly":
      form.custom.submit = ""
    if DEMO_MODE:
      form.custom.submit = DIV(SPAN(T('DEMO MODE')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
    return dict(form=form,view_audit="")
  
  if str(ruri).find("edit/usergroup")>0 or str(ruri).find("view/usergroup")>0: 
    usergroup_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])   
    response.subtitle=T('Edit user group')
    form = SQLFORM(ns.db.groups, record = usergroup_id, submit_button=T("Save"))
    if audit_filter=="all" and not DEMO_MODE:
      response.cmd_delete = INPUT(_type="button", _value=T("Delete"),
                                _style="height: 28px !important;padding-top: 4px !important;color: #A52A2A;width: 100%;", 
                                _onclick="javascript:if(confirm(w2p_ajax_confirm_message||'"+T('Are you sure you want to delete this group?')
                                  +"')){window.location ='"+URL("frm_audit/delete/usergroup/"+str(usergroup_id))+"';};return false;")
    else:
      response.cmd_delete = ""
    audit = ((ns.db.ui_audit.usergroup==usergroup_id))
    ns.db.ui_audit.id.readable = ns.db.ui_audit.id.writable = False
    ns.db.ui_audit.usergroup.readable = ns.db.ui_audit.usergroup.writable = False
    view_audit = SQLFORM.grid(query=audit, field_id=ns.db.ui_audit.id, #fields=fields, #headers=headers,
                   orderby=ns.db.ui_audit.id, sortable=False, paginate=25, maxtextlength=25,
                   searchable=False, csv=False, details=False, showbuttontext=False,
                   create=False, deletable=(audit_filter=="all"), editable=True, selectable=False, user_signature=False)
    if type(view_audit[1][0][0]).__name__=="TABLE":
      view_audit=move_buttons(view_audit)
    else:
      view_audit[1][0][0]=""
    set_counter_bug(view_audit)
  else:
    usergroup_id=-1
    form = SQLFORM(ns.db.groups, submit_button=T("Save"))
    response.subtitle=T('New user group')
    response.cmd_delete = ""
    view_audit=""
  
  if DEMO_MODE:
    form.custom.submit = DIV(SPAN(T('DEMO MODE')),_style="background-color: red;color: #FFFFFF;text-align: center;font-weight: bold;padding-top: 3px;padding-bottom: 1px;margin-bottom: 4px;")
      
  if request.post_vars:
    request.post_vars.groupname = "usergroup"  
  groups_nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
  if form.validate(keepvalues=True):
    group = ns.db((ns.db.groups.id!=usergroup_id)&(ns.db.groups.groupname=="usergroup")&(ns.db.groups.groupvalue==form.vars.groupvalue)).select().as_list()
    if len(group)==0:
      if str(ruri).find("new/usergroup")>0:
        form.vars.id = ns.db.groups.insert(**dict(form.vars))
        values = {"nervatype_1":groups_nervatype_id, "ref_id_1":form.vars.id, "nervatype_2":groups_nervatype_id, "ref_id_2":int(request.post_vars.transfilter_id)}
        ns.db.link.insert(**values)
        redirect(URL('frm_audit/view/usergroup/'+str(form.vars.id)))
      else:
        ns.db(ns.db.groups.id==usergroup_id).update(**form.vars)
        filterlink = ns.db((ns.db.link.ref_id_1==usergroup_id)&(ns.db.link.nervatype_1==groups_nervatype_id)
                  &(ns.db.link.nervatype_2==groups_nervatype_id)&(ns.db.link.deleted==0)).select().as_list()
        if len(filterlink)>0:
          ns.db(ns.db.link.id==filterlink[0]["id"]).update(**{"ref_id_2":int(request.post_vars.transfilter_id)})
        else:
          values = {"nervatype_1":groups_nervatype_id, "ref_id_1":usergroup_id, "nervatype_2":groups_nervatype_id, "ref_id_2":int(request.post_vars.transfilter_id)}
          ns.db.link.insert(**values)
    else:
      form.errors["groupvalue"] = T('The group name already exists!')
      response.flash = T('Error: ')+str(T('The group name already exists!'))
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  form.custom.widget.inactive = get_bool_input(usergroup_id,"groups","inactive")
  filterlink = ns.db((ns.db.link.ref_id_1==usergroup_id)&(ns.db.link.nervatype_1==groups_nervatype_id)
                  &(ns.db.link.nervatype_2==groups_nervatype_id)&(ns.db.link.deleted==0)).select().as_list()
  if len(filterlink)>0:
    filterlink = filterlink[0]["ref_id_2"]
  else:
    filterlink = ns.db((ns.db.groups.groupname=="transfilter")&(ns.db.groups.groupvalue=="all")).select().as_list()[0]["id"]
  transfilter = ns.db((ns.db.groups.groupname=="transfilter")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.id).as_list()
  response.cmb_transfilter = SELECT(*[OPTION(field["groupvalue"], _value=field["id"], _selected=(field["id"]==filterlink)) for field in transfilter], _id="cmb_transfilter",
                                    _onchange="document.getElementById('transfilter_id').value=this.value")
  response.transfilter_id = INPUT(_name="transfilter_id", _type="hidden", _value=filterlink, _id="transfilter_id")
  
  response.cmd_back = get_back_button(URL('frm_groups_usergroup'))
  if usergroup_id>-1:
    response.cmd_add_audit = A(SPAN(_class="icon plus"), _style="height: 15px;vertical-align: middle;padding-top: 2px;padding-bottom: 4px;", 
               _class="w2p_trap buttontext button", 
             _href=URL('frm_audit/new/ui_audit/'+str(usergroup_id)), _title=T("Add access right"))
  else:
    response.cmd_add_audit = ""
  
  if audit_filter=="readonly":
    form.custom.submit = ""
  
  return dict(form=form,view_audit=view_audit)

def frm_menucmd():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  
  response.title=T('SETTINGS')
  response.view=dir_view+'/menucmd.html'
  response.titleicon = URL(dir_images,'icon16_world_link.png')
  response.cmd_help = get_help_button("menucmd")
  
  if str(ruri).find("delete/ui_menu")>0:
    menu_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    ns.db(ns.db.ui_menufields.menu_id==menu_id).delete()
    ns.db(ns.db.ui_menu.id==menu_id).delete()
    ns.db.commit()
    redirect(URL('find_menucmd'))
  
  if str(ruri).find("delete/ui_menufields")>0:
    menufields_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    ns.db(ns.db.ui_menufields.id==menufields_id).delete()
    ns.db.commit()
  
  if str(ruri).find("edit/ui_menufields")>0 or str(ruri).find("view/ui_menufields")>0 or str(ruri).find("new/ui_menufields")>0:
    response.prm_input = True
    if str(ruri).find("new/ui_menufields")>0:
      menufields_id=-1
      menu_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      response.subtitle=T('New parameter')
      form = SQLFORM(ns.db.ui_menufields, submit_button=T("Save"))
      form.vars.fieldtype = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
    else:
      menufields_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
      menu_id = ns.db.ui_menufields(id=menufields_id).menu_id
      response.subtitle=T('Edit parameter')
      form = SQLFORM(ns.db.ui_menufields, record = menufields_id, submit_button=T("Save"))
    
    response.cmd_back = get_back_button(URL('frm_menucmd/view/ui_menu/'+str(menu_id)))
    
    if request.post_vars:
      request.post_vars.menu_id = menu_id
    if form.validate(keepvalues=True):
      if str(ruri).find("new/ui_menufields")>0:
        form.vars.id = ns.db.ui_menufields.insert(**dict(form.vars))
        redirect(URL('frm_menucmd/view/ui_menufields/'+str(form.vars.id)))
      else:
        ns.db(ns.db.ui_menufields.id==menufields_id).update(**form.vars)
    elif form.errors:
      flash=""
      for error in form.errors.keys():
        flash+=error+": "+form.errors[error]+", "
      response.flash = T('Form has errors: ')+flash
    
    if audit_filter=="readonly":
      form.custom.submit=""
    return dict(form=form,view_menufields="")
  
  ns.db.ui_menu.address.widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
  if str(ruri).find("edit/ui_menu")>0 or str(ruri).find("view/ui_menu")>0: 
    menu_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])   
    response.subtitle=T('Edit shortcut')
    form = SQLFORM(ns.db.ui_menu, record = menu_id, submit_button=T("Save"))
    response.cmd_delete = INPUT(_type="button", _value=T("Delete"),
                                _style="height: 25px !important;padding-top: 2px !important;color: #A52A2A;width: 100%;", 
                                _onclick="javascript:if(confirm(w2p_ajax_confirm_message||'"+T('Are you sure you want to delete this shortcut?')
                                  +"')){window.location ='"+URL("frm_menucmd/delete/ui_menu/"+str(menu_id))+"';};return false;")
  
    menufields = ((ns.db.ui_menufields.menu_id==menu_id))
    ns.db.ui_menufields.id.readable = ns.db.ui_menufields.id.writable = False
    ns.db.ui_menufields.menu_id.readable = ns.db.ui_menufields.menu_id.writable = False
    view_menufields = SQLFORM.grid(query=menufields, field_id=ns.db.ui_menufields.id, #fields=fields, #headers=headers,
                   orderby=ns.db.ui_menufields.id, sortable=False, paginate=25, maxtextlength=25,
                   searchable=False, csv=False, details=False, showbuttontext=False,
                   create=False, deletable=(audit_filter=="all"), editable=True, selectable=False, user_signature=False)
    if type(view_menufields[1][0][0]).__name__=="TABLE":
      view_menufields=move_buttons(view_menufields)
    else:
      view_menufields[1][0][0]=""
    set_counter_bug(view_menufields)
  else:
    menu_id=-1
    form = SQLFORM(ns.db.ui_menu, submit_button=T("Save"))
    response.subtitle=T('New shortcut')
    response.cmd_add_field = ""
    response.cmd_delete = ""
    view_menufields=""
    
  if form.validate(keepvalues=True):
    if str(ruri).find("new/ui_menu")>0:
      form.vars.id = ns.db.ui_menu.insert(**dict(form.vars))
      redirect(URL('frm_menucmd/view/ui_menu/'+str(form.vars.id)))
    else:
      ns.db(ns.db.ui_menu.id==menu_id).update(**form.vars)
  elif form.errors:
    flash=""
    for error in form.errors.keys():
      flash+=error+": "+form.errors[error]+", "
    response.flash = T('Form has errors: ')+flash
  
  response.cmd_back = get_back_button(URL('find_menucmd'))
  if menu_id>-1:
    response.cmd_add_field = A(SPAN(_class="icon plus"), _style="height: 15px;vertical-align: middle;padding-top: 2px;padding-bottom: 4px;", 
               _class="w2p_trap buttontext button", 
             _href=URL('frm_menucmd/new/ui_menufields/'+str(menu_id)), _title=T("Add paramater"))
  else:
    response.cmd_add_field = ""
  form.custom.widget.url = get_bool_input(menu_id,"ui_menu","url")
  if audit_filter=="readonly":
    form.custom.submit=""
  return dict(form=form,view_menufields=view_menufields)


def find_menucmd():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("new")>0:
    redirect(URL('frm_menucmd/new/ui_menu'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_menucmd/view"+ruri[ruri.find("find_menucmd/edit")+17:]
    redirect(URL(ruri))
  if str(ruri).find("delete/ui_menu")>0:
    menu_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    ns.db(ns.db.ui_menufields.menu_id==menu_id).delete()
    ns.db(ns.db.ui_menu.id==menu_id).delete()
    ns.db.commit()
    redirect(URL('find_menucmd'))
  response.view=dir_view+'/gridform.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Menu Shortcuts')
  response.cmd_back = get_home_button()
  response.titleicon = URL(dir_images,'icon16_world_link.png')
  response.margin_top = "20px"
  ns.db.ui_menu.id.readable = ns.db.ui_menu.id.writable = False
  
  fields = [ns.db.ui_menu.menukey, ns.db.ui_menu.description, ns.db.ui_menu.modul, ns.db.ui_menu.icon,
            ns.db.ui_menu.funcname, ns.db.ui_menu.url, ns.db.ui_menu.address]
  smenu = [ns.db.ui_menu.menukey, ns.db.ui_menu.description, ns.db.ui_menu.modul]
  search_widget = create_search_widget(smenu)
  form = SQLFORM.grid(query=ns.db.ui_menu, field_id=ns.db.ui_menu.id, fields=fields, #headers=headers,
               orderby=ns.db.ui_menu.id, sortable=True, paginate=10, maxtextlength=25,
               searchable=True, csv=False, details=False, showbuttontext=False,
               create=(audit_filter=="all"), deletable=(audit_filter=="all"), editable=True, selectable=False, 
               user_signature=False, search_widget=search_widget)
  if type(form[1][0][0]).__name__=="TABLE":
    form=move_buttons(form)
  set_counter_bug(form)
  return dict(form=DIV(form, _id="dlg_frm"))

@ns_auth.requires_login()
def menufields():
  ruri = request.wsgi.environ["REQUEST_URI"]
  menukey = ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1]
  menucmd = ns.db.ui_menu(menukey=menukey)
  response.subtitle = menucmd.description
  response.cmd_help = get_help_button("menucmd")
  if menucmd.url==0 and session.back_url:
    response.cmd_back = get_back_button(session.back_url)
  else:
    response.cmd_back = get_home_button()
  if menucmd.icon==None:
    response.titleicon = URL(dir_images,'icon16_world_link.png')
  else:
    response.titleicon = URL(dir_images,'icon16_'+str(menucmd.icon)+'.png')
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
      func = getattr(dbfu, menucmd.funcname, None)
      if callable(func):
        response.return_value = func(ns, dict(request.post_vars))
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
    form = SQLFORM.factory(*tfields, submit_button=T("Call"), comments=False) 
    
  return dict(form=form)

def find_place():
  audit_filter = get_audit_filter("setting", None)[0]
  if audit_filter=="disabled":
    return show_disabled()
  ruri = request.wsgi.environ["REQUEST_URI"]
  if ruri.find("new")>0:
    redirect(URL('frm_place/new/place'))
  elif ruri.find("view")>0 or ruri.find("edit")>0:
    ruri = "frm_place/view"+ruri[ruri.find("find_place/edit")+15:]
    redirect(URL(ruri))
  if str(ruri).find("delete/place")>0:
    #place_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
    redirect(URL('find_place'))
  response.view=dir_view+'/gridform.html'
  response.title=T('SETTINGS')
  response.subtitle=T('Place')
  response.margin_top = "20px"
  if request.vars.has_key("back") and request.wsgi.environ.has_key("HTTP_REFERER"):
    session.back_url = request.wsgi.environ["HTTP_REFERER"]
    response.cmd_back = get_back_button(session.back_url)
  else:
    response.cmd_back = get_home_button()
  response.titleicon = URL(dir_images,'icon16_book.png')
  
  query=((ns.db.place.deleted==0)&(ns.db.place.placetype==ns.db.groups.id))
  fields = [ns.db.place.planumber, ns.db.place.placetype, ns.db.place.description, ns.db.place.inactive]
  smenu = [ns.db.place.planumber, ns.db.groups.groupvalue, ns.db.place.description]
  ns.db.groups.groupvalue.label = T("Type")
  search_widget = create_search_widget(smenu)
  form = SQLFORM.grid(query=query, field_id=ns.db.place.id, fields=fields, #headers=headers,
               orderby=ns.db.place.id, sortable=True, paginate=10, maxtextlength=25,
               searchable=True, csv=False, details=False, showbuttontext=False,
               create=(audit_filter=="all"), deletable=False, editable=True, selectable=False, 
               user_signature=False, search_widget=search_widget)
  if type(form[1][0][0]).__name__=="TABLE":
    form=move_buttons(form)
  set_counter_bug(form)
  return dict(form=DIV(form, _id="dlg_frm"))

def delete_row(rowtype, row_id, logtype=None, log_id=None):
  delete_ini = getSetting("set_trans_deleted")
  if delete_ini != "true" and rowtype!="barcode":
    values = {"deleted":1}
    ns.db(ns.db[rowtype].id==row_id).update(**values)
  else:
    dfield = deleteFieldValues(rowtype, row_id)
    if dfield!=True:
      session.flash = dfield
      return False
    ns.db(ns.db[rowtype].id==row_id).delete()
    ns.db.commit()
  if logtype:
    setLogtable("update", "log_"+logtype+"_update", logtype, log_id)
  return True

def move_buttons(form):
  #move buttons to 1. col
  if type(form[1][0][0]).__name__!="lazyT":
    thead_row = form[1][0][0][0][0]
    thead_row.insert(0,thead_row[len(thead_row)-1])
    thead_row.__delitem__(len(thead_row)-1)
    tbody = form[1][0][0][1]
    for trow in tbody:
      trow.insert(0,trow[len(trow)-1])
      trow.__delitem__(len(trow)-1)
  return form

def set_counter_bug(form):
  counter = form.elements("div.web2py_counter")
  if len(counter)>0:
    if counter[0][0]==None:
      counter[0][0] = ""

def export2excel(sheetname,query,left,fields,orderby,keywords,join=None,groupfields=None,groupby=None,having=None):
  from xlwt import Workbook
  
  output = StringIO()
  book = Workbook(encoding='utf-8')
  styles = dbfu.estyles
  
  sheet1 = book.add_sheet(sheetname)     
  colnum = 0
  for col in fields:
    if str(col.name)!="id":
      sheet1.write(0, colnum, str(col.label), styles["header"])
      colnum = colnum + 1
  dbset = ns.db(query)
  if keywords!=None and keywords!="":
    subquery = SQLFORM.build_query(fields, keywords)
    dbset = dbset(subquery)
  if groupby:
    rows = dbset.select(*groupfields,join=join,left=left,groupby=groupby,having=having,orderby=orderby,cacheable=True)
  else:
    rows = dbset.select(join=join,left=left,orderby=orderby,cacheable=True,*fields)
  rownum = 1  
  for row in rows:
    colnum = 0
    for col in fields:
      if row.has_key(col.name):
        value = str(row[col.name])
      elif row.has_key(col._tablename):
        value = str(row[col._tablename][col.name])
      else:
        value = "???"
      if col.type=="id":
        continue
      if ns.db[col._tablename][col.name].represent:
        try:
          rep_value=dbfu.represent(ns.db[col._tablename][col.name],value,dict2obj(row),True)
        except Exception:
          rep_value = value
      else:
        rep_value = value
      if col.type=="float" or col.type=="double":
        sheet1.write(rownum, colnum, value, styles["float"])
      elif rep_value!=value:
        sheet1.write(rownum, colnum, rep_value, styles["string"])
      elif col.type=="float" or col.type=="double":
        sheet1.write(rownum, colnum, value, styles["float"])
      elif col.type=="integer":
        sheet1.write(rownum, colnum, value, styles["integer"])
      elif col.type=="date":
        sheet1.write(rownum, colnum, value, styles["date"])
      elif col.type=="boolean":
        sheet1.write(rownum, colnum, value, styles["bool"])
      else:
        sheet1.write(rownum, colnum, value, styles["string"])
      colnum = colnum + 1
    rownum = rownum + 1
    
  book.save(output)
  contents = output.getvalue()
  output.close
  response.headers['Content-Type'] = "application/vnd.ms-excel"
  response.headers['Content-Disposition'] = 'attachment;filename="NervaturaExport.xls"'
  return contents

def export2csv(filename,query,left,fields,orderby,keywords,join=None,groupfields=None,groupby=None,having=None):
  dbset = ns.db(query)
  if keywords!=None and keywords!="":
    subquery = SQLFORM.build_query(fields, keywords)
    dbset = dbset(subquery)
  if groupby:
    rows = dbset.select(*groupfields,join=join,left=left,groupby=groupby,having=having,orderby=orderby,cacheable=True)
  else:
    rows = dbset.select(join=join,left=left,orderby=orderby,cacheable=True,*fields)
  import copy
  orows = copy.deepcopy(rows)
  for i in range(len(rows)):
    for col in fields:
      if rows[i].has_key(col.name):
        value = str(rows[i][col.name])
      elif rows[i].has_key(col._tablename):
        value = str(rows[i][col._tablename][col.name])
      else:
        value = "???"
      if col.type=="id":
        continue
      if ns.db[col._tablename][col.name].represent:
        try:
          rep_value=dbfu.represent(ns.db[col._tablename][col.name],value,dict2obj(orows[i]),True)
          if rows[i].has_key(col._tablename):
            rows[i][col._tablename][col.name] = rep_value
          else:
            rows[i][col.name] = rep_value
        except Exception:
          pass
  raise HTTP(200,str(rows),**{'Content-Type':'text/csv','Content-Disposition':'attachment;filename='+filename+'.csv;'})

def export2ical():
  response.headers['Content-Type'] = "text/ics"
  response.headers['Content-Disposition'] = 'attachment;filename="NervaturaEvents.ics"'
  return dbfu.exportToICalendar(ns, request.vars.id)

def show_report(output, report_tmp):
  if type(report_tmp).__name__=="str":
    if report_tmp=="NODATA":
      return HTML(HEAD(TITLE(response.title),
                   LINK(_rel="shortcut icon", _href=URL('static','favicon.ico'), _type="image/x-icon")),
              BODY(DIV(CENTER(TABLE(TR(TD(IMG(_src=URL('static','images/nodata.png'),
                                      _style="border: solid;border-color: #FFFFFF;"),
                            _style="text-align: center;vertical-align: middle;font-weight: bold;font-family: Arial, Helvetica,  sans-serif;font-size: 20px;")),
                      _style="background-color:#FFFFFF;color:#444444;margin-top:200px;")),_style="width:100%;height:100%")),_style="background-color:#000000;")
    else:
      return report_tmp
  
  if report_tmp["filetype"]=="html":
    response.view = "default/report.html"
    response.title = report_tmp["data"]["title"]
    response.subtitle = ""
    report_tmp["template"]=response.render(StringIO(report_tmp["template"]),report_tmp["data"])
    return dict(template=XML(report_tmp["template"]))
  elif report_tmp["filetype"]=="fpdf":
    if output=="xml":
      response.headers['Content-Type']='text/xml'
    elif output=="pdf":
      response.headers['Content-Type']='application/pdf'
    return report_tmp["template"]
  elif report_tmp["filetype"]=="xls":
      response.headers['Content-Type'] = "application/vnd.ms-excel"
      response.headers['Content-Disposition'] = 'attachment;filename="NervaturaReport.xls"'
      return report_tmp["template"]
  else:
    return report_tmp["template"]

@ns_auth.requires_login()
def get_report():
  ruri = request.wsgi.environ["REQUEST_URI"]
  formkey = ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1]
  if session[formkey]:
    return show_report(session[formkey].params["output"],dbfu.getReport(ns,session[formkey].params,session[formkey].filters))
  else:
    return HTML(HEAD(TITLE(response.title),
                   LINK(_rel="shortcut icon", _href=URL('static','favicon.ico'), _type="image/x-icon")),
              BODY(DIV(CENTER(TABLE(TR(TD(IMG(_src=URL('static','images/nodata.png'),
                                      _style="border: solid;border-color: #FFFFFF;"),
                            _style="text-align: center;vertical-align: middle;font-weight: bold;font-family: Arial, Helvetica,  sans-serif;font-size: 20px;")),
                      _style="background-color:#FFFFFF;color:#444444;margin-top:200px;")),_style="width:100%;height:100%")),_style="background-color:#000000;")
        
@ns_auth.requires_login()
def frm_reports():
  response.view=dir_view+'/reports.html'
  response.subtitle=""
  response.titleicon = URL(dir_images,'icon16_report.png')
  response.cmd_help = get_help_button("report")
  #request.post_vars
  if str(request.wsgi.environ["REQUEST_URI"]).find("view")>0:
    response.cmd_back = get_back_button(URL('frm_reports'))
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
    response.cmd_preview = get_command_button(caption=T("Show Report"),title=T("Show Report"),color="008B00",
                              cmd="show_report('"+URL('frm_reports')+"','"+T("Missing required data")+"');")
    
    if filetype=="fpdf":
      response.rtable = TABLE(_style="width: 100%;")
      orientation = ns.db((ns.db.groups.groupname=="orientation")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.id)
      cmb_orientation = SELECT(*[OPTION(T(ori["description"]), _value=ori["groupvalue"]) for ori in orientation], 
                                 _id="cmb_orientation", _name="orientation",_style="width: 100%;height: 25px;")
      size = ns.db((ns.db.groups.groupname=="papersize")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.id)
      cmb_size = SELECT(*[OPTION(psize["description"], _value=psize["groupvalue"]) for psize in size], 
                                 _id="cmb_size", _name="size",_style="width: 100%;height: 25px;")
      cmb_size[1]["_selected"]=["selected"]
      cmb_output = SELECT([OPTION(T("HTML"), _value="html"),OPTION(T("PDF"), _value="pdf"),OPTION(T("XML"), _value="xml")], _id="cmb_output", _name="output",_style="width: 100%;height: 25px;")
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
      redirect(URL('get_report/'+str(request.post_vars._formkey)))
  else:
    response.cmd_back = get_home_button()  
    filetype_id = ns.db((ns.db.groups.groupname=="filetype")&(ns.db.groups.groupvalue.belongs(("html","fpdf","gshi","xls")))).select(ns.db.groups.id)
    nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="report")).select(ns.db.groups.id)
    reports = (ns.db.ui_report.filetype.belongs(filetype_id)&ns.db.ui_report.nervatype.belongs(nervatype_id))
    
    #disabled reports list
    audit = get_audit_subtype("report")
    if len(audit)>0:
      reports = reports & (~ns.db.ui_report.id.belongs(audit))
    
    fields = (ns.db.ui_report.id, ns.db.ui_report.repname, ns.db.ui_report.label,
              ns.db.ui_report.description)
    smenu = [ns.db.ui_report.repname, ns.db.ui_report.label, ns.db.ui_report.description]
    search_widget = create_search_widget(smenu)
    
    ns.db.ui_report.id.readable = ns.db.ui_report.id.writable = False
    gform = SQLFORM.grid(query=reports, field_id=ns.db.ui_report.id, fields=fields,
                         orderby=ns.db.ui_report.repname, paginate=25, maxtextlength=70, 
                         searchable=True, csv=False, details=True, showbuttontext=False,
                         create=False, deletable=False, editable=False, selectable=False,
                         user_signature=False, search_widget=search_widget)
    if type(gform[1][0][0]).__name__=="TABLE":
      gform=move_buttons(gform)
    set_counter_bug(gform)
  return dict(form=gform)

@ns_auth.requires_login()
def frm_report_customer():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
    return create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    label = ns.db.customer(id=ref_id)["custname"]
    return dlg_report("customer",None,None,ref_id,label)

@ns_auth.requires_login()
def frm_report_product():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
    return create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    label = ns.db.product(id=ref_id)["description"]
    return dlg_report("product",None,None,ref_id,label)
    
@ns_auth.requires_login()
def frm_report_employee():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
    return create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    label = ns.db.employee(id=ref_id)["empnumber"]
    return dlg_report("employee",None,None,ref_id,label)

@ns_auth.requires_login()
def frm_report_tool():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
    return create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    label = ns.db.tool(id=ref_id)["serial"]
    return dlg_report("tool",None,None,ref_id,label)

@ns_auth.requires_login()
def frm_report_project():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
    return create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    label = ns.db.project(id=ref_id)["pronumber"]
    return dlg_report("project",None,None,ref_id,label)

@ns_auth.requires_login()
def frm_report_place():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
    return create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    label = ns.db.place(id=ref_id)["planumber"]
    return dlg_report("place",None,None,ref_id,label)
    
@ns_auth.requires_login()
def frm_report_trans():
  ruri = request.wsgi.environ["REQUEST_URI"]
  ref_id = int(ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-1])
  direction = ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-2]
  transtype = ruri.split("?")[0].split("/")[len(ruri.split("?")[0].split("/"))-3]
  if request.vars.has_key("cmd") and request.vars.has_key("template"):
#    if transtype=="invoice" and direction=="out" and request.vars["cmd"]=="pdf":
#      ns.db(ns.db.trans.id==ref_id).update(**{"closed":1})
    return create_report(request.vars["template"],ref_id,request.vars["cmd"],request.vars["orientation"],request.vars["size"])
  else:
    label = ns.db.trans(id=ref_id)["transnumber"]
    return dlg_report("trans",transtype,direction,ref_id,label)

def create_report(template,ref_id,output="html",orientation="P",size="a4"):
  params={}
  filters={}
  params["report_id"]=template
  params["output"]=output
  params["orientation"]=orientation
  params["size"]=size
  filters["@id"]=ref_id
  return show_report(output,dbfu.getReport(ns, params, filters))

def dlg_report(_nervatype,_transtype,_direction,ref_id,label,default=None):
  nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue==_nervatype)).select().as_list()[0]["id"]
  filetype = ns.db((ns.db.groups.groupname=="filetype")&(ns.db.groups.groupvalue=="fpdf")).select().as_list()[0]["id"]
  query = (ns.db.ui_report.nervatype==nervatype)&(ns.db.ui_report.filetype==filetype)&(ns.db.ui_report.repname!=None)
  if _transtype!=None:
    transtype = ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue==_transtype)).select().as_list()[0]["id"]
    query=query&(ns.db.ui_report.transtype==transtype)
  if _direction!=None:
    direction = ns.db((ns.db.groups.groupname=="direction")&(ns.db.groups.groupvalue==_direction)).select().as_list()[0]["id"]
    query=query&(ns.db.ui_report.direction==direction)
  
  #disabled reports list
  audit = get_audit_subtype("report")
  if len(audit)>0:
    query = query & (~ns.db.ui_report.id.belongs(audit))
  
  templates = ns.db(query).select(orderby=ns.db.ui_report.repname).as_list()
                          
  rtable = TABLE(_style="width: 100%;")
  rtable.append(TR(TD(label,_colspan="4",
                      _style="background-color: #F1F1F1;font-weight: bold;text-align: center;border-bottom: solid;padding: 5px;")))
  cmb_templates = SELECT(*[OPTION(field["repname"], _value=field["id"]) for field in templates], 
                         _id="cmb_templates", _name="template",_style="width: 100%;height: 25px;")
  if default!=None:
    for i in range(len(cmb_templates)):
      if cmb_templates[i]["id"]==default:
        cmb_templates[i]["_selected"]=["selected"]
  rtable.append(TR(
                   TD(T("Output Template"),_style="width: 170px;background-color: #F1F1F1;font-weight: bold;text-align: left;padding: 5px;border-bottom: solid;"),
                   TD(cmb_templates,_colspan="3", _style="padding: 5px;padding-right: 0px;border-bottom: solid;")))
  
  orientation = ns.db((ns.db.groups.groupname=="orientation")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.id)
  cmb_orientation = SELECT(*[OPTION(T(ori["description"]), _value=ori["groupvalue"]) for ori in orientation], 
                             _id="cmb_orientation", _name="orientation",_style="width: 100%;height: 25px;")
  size = ns.db((ns.db.groups.groupname=="papersize")&(ns.db.groups.deleted==0)&(ns.db.groups.inactive==0)).select(orderby=ns.db.groups.id)
  cmb_size = SELECT(*[OPTION(psize["description"], _value=psize["groupvalue"]) for psize in size], 
                             _id="cmb_size", _name="size",_style="width: 100%;height: 25px;")
  cmb_size[1]["_selected"]=["selected"]
  rtable.append(TR(
                   TD(T("Orientation/Size/Copy"),_style="width: 170px;background-color: #F1F1F1;font-weight: bold;text-align: left;padding: 5px;border-bottom: solid;"),
                   TD(cmb_orientation, _style="padding: 5px;border-bottom: solid;padding-right: 0px;"),
                   TD(cmb_size, _style="padding: 5px;border-bottom: solid;"),
                   TD(INPUT(_type="text",_value="1",_name="copy",_id="page_copy",_class="integer",_style="width: 20px;height: 10px;text-align: right;"), _style="width: 20px;padding-right: 0px;padding-left: 0px;border-bottom: solid;")))
  
  rtable_cmd = TABLE(_style="width: 100%;")
  
  cmd_preview = INPUT(_type="button", _value="HTML Preview", _style="width: 100%;height: 50px !important;padding-top: 5px !important;",
                      _onclick="create_report('html','"+T("Missing Output Template!")+"');")
  cmd_pdf = INPUT(_type="button", _value="Create PDF", _style="width: 100%;height: 50px !important;padding-top: 5px !important;",
                      _onclick="create_report('pdf','"+T("Missing Output Template!")+"');")
  rtable_cmd.append(TR(
                   TD(cmd_preview,_colspan="2", _style="padding:0px;padding-top:5px;padding-right:2px;"),
                   TD(cmd_pdf,_style="width: 50%;padding:0px;padding-top:5px;padding-left:2px;")))
  cmd_xml = INPUT(_type="button", _value="Create XML", _style="width: 100%;height: 50px !important;padding-top: 5px !important;",
                      _onclick="create_report('xml','"+T("Missing Output Template!")+"');")
  cmd_group = INPUT(_type="button", _value="Printer queue", _style="width: 100%;height: 50px !important;padding-top: 5px !important;",
                      _onclick="if(document.getElementById('cmb_templates').value==''){alert('"+T("Missing Output Template!")+"');} else {ajax('"+URL("add_print_queue")+"?nervatype="+str(nervatype)+"&ref_id="+str(ref_id)
                      +"&qty='+document.getElementById('page_copy').value+'&template='+document.getElementById('cmb_templates').value);alert('"+T("The document has been added to the Printing List")+"')}; return false;")
  rtable_cmd.append(TR(
                   TD(cmd_xml,_colspan="2", _style="padding:0px;padding-right:2px;border-bottom: solid;"),
                   TD(cmd_group,_style="width: 50%;padding:0px;padding-left:2px;border-bottom: solid;")))
  rtable.append(TR(
                   TD(rtable_cmd,_colspan="4", _style="padding:0px;")))
  rtable = FORM(rtable, _id="dlg_frm_report", _target="_blank", _action=URL("frm_report_"+_nervatype+"/"+str(ref_id)))
  return DIV(rtable, _id="dlg_report")

@ns_auth.requires_login()
def add_print_queue():
  if request.vars.qty=="":
    copy=1
  else:
    copy=request.vars.qty
  values = {"nervatype":request.vars.nervatype, "ref_id":request.vars.ref_id, "qty":copy, 
            "employee_id":session.auth.user.id, "report_id":request.vars.template, "crdate":datetime.datetime.now().date()}
  ns.db.ui_printqueue.insert(**values)
