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
  global session; session = globals.Session()
  import gluon.languages.translator as T
  from gluon.sql import DAL
  global db; db = DAL()

from gluon.html import URL
from gluon.validators import IS_IN_DB, IS_IN_SET, IS_EMPTY_OR
from gluon.html import SELECT, OPTION, INPUT
from gluon.sqlhtml import SQLFORM, DIV
from gluon.html import TABLE, TR, TD, SPAN
from nerva2py.nervastore import NervaStore
from nerva2py.ndi import Ndi

ns = NervaStore(request, T, db)
ndi = Ndi(ns)
validator = ndi.getLogin({"database":"demo","username":"demo","password":""})
    
def index():
  response.title=T('NDI Demo')
  response.subtitle=T('Nervatura Data Interface Demo')
  lst_nom = ["address","barcode","contact","currency","customer","deffield","employee","event","fieldvalue","groups","item","link",
         "log","movement","numberdef","pattern","payment","place","price","product","project","rate","tax","tool","trans","setting","sql"]
  response.lst_nom = SELECT(*[OPTION(str(nom).upper(), _value=nom) for nom in lst_nom], _id="lst_nom", 
                            _size=len(lst_nom),_style="width: 100%;font-weight: bold;", 
                            _onchange="changeItem();setLabels(this.value.toUpperCase()+'"
                            +T(" fieldname and type values")+"','"+URL('ndr','getResource')+"?file_name=docs/ndi/ndi&content=view&lang=auto#'+this.value+'_fields');")
  return dict()
  
def get_nom_data():
  if validator["valid"]:
    if request.vars.nom:
      fields_lst = create_fieldlist(request.vars.nom)
      return get_view_lst(request.vars.nom)+"||"+get_update_lst(fields_lst)+"||"+get_delete_lst(fields_lst)
    else:
      return T("Missing parameter")
  else:
    return validator["message"]

checkbox_style="width: auto;border-bottom-style: double;border-width: 4px;border-color: #8B8B83;text-align: center;padding-top:8px;"
checkbox_style2="width: auto;text-align: left;vertical-align: bottom;border-bottom-style: double;border-width: 4px;border-color: #8B8B83;"
checklabel_style="width: auto;padding-top:0px;padding-bottom:0px;color: #FFD700;"

def get_view_lst(table):
  rtable = TABLE(_style="width: 100%;")
  if table in("address","contact"):
    nervatype_lst=['customer', 'employee', 'event', 'place', 'product', 'project', 'tool', 'trans']
    rtable.append(TR(TD(DIV("nervatype",_class="div_label"),_class="td_label",_style="width: 90px;"),
         TD(SELECT(*[OPTION(nervatype) for nervatype in nervatype_lst], _id="address_nervatype", _name="nervatype"),
            _class="td_input", _style="width: 175px;"),
         TD()
         ))
  elif table=="event":
    nervatype_lst=['customer', 'employee', 'place', 'product', 'project', 'tool', 'trans']
    rtable.append(TR(TD(DIV("nervatype",_class="div_label"),_class="td_label",_style="width: 90px;"),
         TD(SELECT(*[OPTION(nervatype) for nervatype in nervatype_lst], _id="event_nervatype", _name="nervatype"),
            _class="td_input", _style="width: 175px;"),
         TD()
         ))
  elif table=="fieldvalue":
    nervatype_lst=['customer', 'employee', 'event', 'groups', 'place', 'product', 'project', 'tool', 'trans']
    rtable.append(TR(TD(DIV("nervatype",_class="div_label"),_class="td_label",_style="width: 90px;"),
         TD(SELECT(*[OPTION(nervatype) for nervatype in nervatype_lst], _id="fieldvalue_nervatype", _name="nervatype"),
            _class="td_input", _style="width: 175px;"),
         TD()
         ))
  elif table=="link":
    nervatype_lst=['customer', 'employee', 'event', 'groups', 'place', 'product', 'project', 'tool', 'trans', 'item', 'movement', 'payment']
    rtable.append(TR(TD(DIV("nervatype1",_class="div_label"),_class="td_label",_style="width: 90px;"),
         TD(SELECT(*[OPTION(nervatype) for nervatype in nervatype_lst], _id="link_nervatype1", _name="nervatype1"),
            _class="td_input", _style="width: 175px;"),
         TD(DIV("nervatype2",_class="div_label"),_class="td_label",_style="width: 90px;"),
         TD(SELECT(*[OPTION(nervatype) for nervatype in nervatype_lst], _id="link_nervatype2", _name="nervatype2"),
            _class="td_input", _style="width: 175px;"),
         TD()
         ))
  elif table=="log":
    nervatype_lst=['notype','customer', 'employee', 'event', 'groups', 'place', 'product', 'project', 'tool', 'trans']
    rtable.append(TR(TD(DIV("nervatype",_class="div_label"),_class="td_label",_style="width: 90px;"),
         TD(SELECT(*[OPTION(nervatype) for nervatype in nervatype_lst], _id="log_nervatype", _name="nervatype"),
            _class="td_input", _style="width: 175px;"),
         TD()
         ))
  return rtable
  
def get_delete_lst(fields_lst):
  rtable = TABLE(_style="width: 100%;")
  rtable.append(TR(TD(DIV(T("SELECT ROW"),_class="div_label",_style="color: #FFD700;"),_class="td_label",
                      _style="width: auto;border-bottom-style: double;border-width: 4px;border-color: #8B8B83;"),
         TD(SPAN("1",_class="div_label",_style=checklabel_style),
            INPUT(_type="checkbox",_value="on",_checked="checked",_disabled="disabled",_name="selrow",_id="row_1",_class="boolean", _style="vertical-align: middle;"),
            _class="td_input", _style=checkbox_style),
         TD(SPAN("2",_class="div_label",_style=checklabel_style),
            INPUT(_type="checkbox",_value="on",_name="selrow",_id="row_2",_class="boolean", _style="vertical-align: middle;"),
            _class="td_input", _style=checkbox_style),
         TD(SPAN("3",_class="div_label",_style=checklabel_style),
            INPUT(_type="checkbox",_value="on",_name="selrow",_id="row_3",_class="boolean", _style="vertical-align: middle;"),
            _class="td_input", _style=checkbox_style),
         TD(SPAN("4",_class="div_label",_style=checklabel_style),
            INPUT(_type="checkbox",_value="on",_name="selrow",_id="row_4",_class="boolean", _style="vertical-align: middle;"),
            _class="td_input", _style=checkbox_style),
         ))
  for field in fields_lst:
    if field["fieldcat"]==0:
      rtable.append(TR(TD(DIV(field["label"],_class="div_label"),_class="td_label",_style="width: auto;"),
         TD(field["widget"],_class="td_input", _style="width: auto;", _id="1"),
         TD(field["widget"],_class="td_input", _style="width: auto;", _id="2"),
         TD(field["widget"],_class="td_input", _style="width: auto;", _id="3"),
         TD(field["widget"],_class="td_input", _style="width: auto;", _id="4")
         ))
  return rtable

def get_update_lst(fields_lst):
  rtable = TABLE(_style="width: 100%;")
  rtable.append(TR(
         TD(_style=checkbox_style2),
         TD(SPAN("1",_class="div_label",_style=checklabel_style),
            _class="td_input", _style=checkbox_style2+"padding-left:10px;padding-right:0px;"),
         TD(SPAN(T("ROW"),_class="div_label",_style=checklabel_style),
            _class="td_input", _style=checkbox_style2+"padding-left:0px;"),
         TD(SPAN("2",_class="div_label",_style=checklabel_style),
            _class="td_input", _style=checkbox_style2+"padding-right:0px;"),
         TD(SPAN(T("ROW"),_class="div_label",_style=checklabel_style),
            _class="td_input", _style=checkbox_style2+"padding-left:0px;"),
         TD(SPAN("3",_class="div_label",_style=checklabel_style),
            _class="td_input", _style=checkbox_style2+"padding-right:0px;"),
         TD(SPAN(T("ROW"),_class="div_label",_style=checklabel_style),
            _class="td_input", _style=checkbox_style2+"padding-left:0px;"),
         TD(SPAN("4",_class="div_label",_style=checklabel_style),
            _class="td_input", _style=checkbox_style2+"padding-right:0px;"),
         TD(SPAN(T("ROW"),_class="div_label",_style=checklabel_style),
            _class="td_input", _style=checkbox_style2+"padding-left:0px;")
         ))
  fieldcat=0
  for field in fields_lst:
    style="width: auto;vertical-align: middle;"
    if field["fieldcat"]==2:
      style += "font-style:italic;"
      if fieldcat<2:
        style+="border-top-style: double;border-width: 4px;border-color: #8B8B83;"
    fieldcat=field["fieldcat"]
    rtable.append(TR(
                     TD(DIV(field["label"],_class="div_label"),
                        _class="td_label",_style=style),
                     TD(INPUT(_type="checkbox",_value="on",_name="selfield",_id="select_"+field["fieldname"]+"_1",_class="boolean", 
                              _style="vertical-align: middle;"),_class="td_input", _style=style+"padding-right:0px;padding-left:10px;"),
                     TD(field["widget"],_class="td_input", _style=style+"padding-left:0px;", _id="1"),
                     TD(INPUT(_type="checkbox",_value="on",_name="selfield",_id="select_"+field["fieldname"]+"_2",_class="boolean", 
                              _style="vertical-align: middle;"),_class="td_input", _style=style+"padding-right:0px;padding-left:5px;"),
                     TD(field["widget"],_class="td_input", _style=style+"padding-left:0px;", _id="2"),
                     TD(INPUT(_type="checkbox",_value="on",_name="selfield",_id="select_"+field["fieldname"]+"_3",_class="boolean", 
                              _style="vertical-align: middle;"),_class="td_input", _style=style+"padding-right:0px;padding-left:5px;"),
                     TD(field["widget"],_class="td_input", _style=style+"padding-left:0px;", _id="3"),
                     TD(INPUT(_type="checkbox",_value="on",_name="selfield",_id="select_"+field["fieldname"]+"_4",_class="boolean", 
                              _style="vertical-align: middle;"),_class="td_input", _style=style+"padding-right:0px;padding-left:5px;"),
                     TD(field["widget"],_class="td_input", _style=style+"padding-left:0px;", _id="4")
       ))
  return rtable
  
def create_fieldlist(table):
  fields_lst = []
  if table=="setting":
    table="fieldvalue"
  fields = ns.db[table].fields
  for fname in fields:
    fieldcat=1
    if fname in("id","deleted"):
      continue
    
    if ns.db[table][fname].type=="text":
      ns.db[table][fname].widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
    if type(ns.db[table][fname].requires).__name__=="check_boolean":
      fields_lst.append({"fieldname":fname,"label":ns.db[table][fname].label,
                       "widget":SELECT([OPTION("", _value=""),OPTION(T("YES"), _value="1"),OPTION(T("NO"), _value="0",)], _id=table+"_"+fname, _name=fname),
                       "fieldcat":1})
      continue
    
    if table in("address","contact"):
      if fname=="nervatype":
        ns.db[table].nervatype.requires = IS_IN_SET(('customer', 'employee', 'event', 'place', 'product', 'project', 'tool', 'trans'))
        fieldcat=0
      elif fname=="ref_id":
        fields_lst.append({"fieldname":"refnumber","label":T('Ref.No.'),
                       "widget":INPUT(_type="text",_value="",_name="refnumber",_id=table+"_refnumber",_class="string"),
                       "fieldcat":0})
        fields_lst.append({"fieldname":"rownumber","label":T('Row No.'),
                       "widget":INPUT(_type="text",_value="0",_name="rownumber",_id=table+"_rownumber",_class="integer"),
                       "fieldcat":0})
        continue
    elif table=="barcode":
      if fname=="code":
        fields_lst.append({"fieldname":"barcode","label":T('Barcode'),
                       "widget":INPUT(_type="text",_value="",_name="barcode",_id=table+"_barcode",_class="string"),
                       "fieldcat":0})
        continue
      elif fname=="product_id":
        fields_lst.append({"fieldname":"partnumber","label":T('Product No.'),
                       "widget":INPUT(_type="text",_value="",_name="partnumber",_id=table+"_partnumber",_class="string"),
                       "fieldcat":1})
        continue
      elif fname=="barcodetype":
        ns.db.barcode.barcodetype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('barcodetype')), ns.db.groups.groupvalue, '%(groupvalue)s')
    elif table=="currency":
      if fname=="curr":
        fieldcat=0
    elif table=="customer":
      if fname=="custnumber":
        fieldcat=0
      elif fname=="custtype":
        ns.db.customer.custtype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('custtype')&(ns.db.groups.groupvalue!="own")), ns.db.groups.groupvalue, '%(groupvalue)s')
    elif table=="deffield":
      if fname=="fieldname":
        fieldcat=0
      elif fname=="nervatype":
        ns.db[table].nervatype.requires = IS_IN_SET(('address', 'contact', 'customer', 'employee', 'event', 'groups', 'item', 'link', 
                                                     'log', 'movement', 'price', 'place', 'product', 'project', 'tool', 'trans'))
      elif fname=="subtype":
        ns.db[table][fname].widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
      elif fname=="fieldtype":
        ns.db.deffield.fieldtype.requires = IS_IN_DB(ns.db((ns.db.groups.groupname.like('fieldtype'))
          &(ns.db.groups.groupvalue!="checkbox")&(ns.db.groups.groupvalue!="trans")), ns.db.groups.groupvalue, '%(groupvalue)s')
    elif table=="employee":
      if fname=="empnumber":
        fieldcat=0
      elif fname=="usergroup":
        ns.db.employee.usergroup.requires = IS_IN_DB(ns.db((ns.db.groups.groupname.like('usergroup'))&(ns.db.groups.deleted==0)), 
                                                     ns.db.groups.groupvalue, '%(groupvalue)s')
      elif fname=="department":
        ns.db.employee.department.requires = IS_EMPTY_OR(IS_IN_DB(ns.db((ns.db.groups.groupname.like('department'))
          &(ns.db.groups.deleted==0)), ns.db.groups.groupvalue, '%(groupvalue)s'))
      elif fname in("password","registration_key","reset_password_key","registration_id"):
        continue
    elif table=="event":
      if fname=="calnumber":
        fieldcat=0
      elif fname=="ref_id":
        fields_lst.append({"fieldname":"refnumber","label":T('Ref. No.'),
                       "widget":INPUT(_type="text",_value="",_name="refnumber",_id=table+"_refnumber",_class="string"),
                       "fieldcat":1})
        continue
      elif fname=="nervatype":
        ns.db[table].nervatype.requires = IS_IN_SET(('customer', 'employee', 'place', 'product', 'project', 'tool', 'trans'))
      elif fname=="eventgroup":
        ns.db[table][fname].widget=lambda field,value: SQLFORM.widgets.string.widget(field,value)
    elif table=="groups":
      if fname in("groupname","groupvalue"):
        fieldcat=0
    elif table=="item":
      if fname=="trans_id":
        fields_lst.append({"fieldname":"transnumber","label":T('Doc.No.'),
                       "widget":INPUT(_type="text",_value="",_name="transnumber",_id=table+"_transnumber",_class="string"),
                       "fieldcat":0})
        fields_lst.append({"fieldname":"rownumber","label":T('Row No.'),
                       "widget":INPUT(_type="text",_value="0",_name="rownumber",_id=table+"_rownumber",_class="integer"),
                       "fieldcat":0})
        fields_lst.append({"fieldname":"inputmode","label":T('Input mode'),
                       "widget":SELECT([OPTION("", _value=""),OPTION(T("fxprice"), _value="fxprice"),
                                        OPTION(T("netamount"), _value="netamount"),OPTION(T("amount"), _value="amount")
                                        ], _id="item_inputmode", _name="inputmode"),
                       "fieldcat":1})
        fields_lst.append({"fieldname":"inputvalue","label":T('Input value'),
                       "widget":INPUT(_type="text",_value="0",_name="inputvalue",_id=table+"_inputvalue",_class="double"),
                       "fieldcat":1})
        continue
      elif fname=="product_id":
        fields_lst.append({"fieldname":"partnumber","label":T('Product No.'),
                       "widget":INPUT(_type="text",_value="",_name="partnumber",_id=table+"_partnumber",_class="string"),
                       "fieldcat":1})
        continue
      elif fname=="tax_id":
        taxcode = ns.db(ns.db.tax.inactive==0).select(ns.db.tax.taxcode)
        widget=SELECT(*[OPTION(field.taxcode) for field in taxcode], _id="item_taxcode", _name="taxcode")
        widget.insert(0, OPTION(""))
        fields_lst.append({"fieldname":"taxcode","label":T('Tax'), "widget":widget, "fieldcat":0})
        continue
      elif fname in("fxprice","netamount","vatamount","amount"):
        continue
    elif table=="link":
      nervatype_lst=['customer', 'employee', 'event', 'groups', 'place', 'product', 'project', 'tool', 'trans', 'item', 'movement', 'payment']
      if fname == "nervatype_1":
        widget=SELECT(*[OPTION(nervatype) for nervatype in nervatype_lst], _id="link_nervatype1", _name="nervatype1")
        widget.insert(0, OPTION(""))
        fields_lst.append({"fieldname":"nervatype1","label":T('Nervatype 1'), "widget":widget, "fieldcat":0})
        continue
      elif fname == "nervatype_2":
        widget=SELECT(*[OPTION(nervatype) for nervatype in nervatype_lst], _id="link_nervatype2", _name="nervatype2")
        widget.insert(0, OPTION(""))
        fields_lst.append({"fieldname":"nervatype2","label":T('Nervatype 2'), "widget":widget, "fieldcat":0})
        continue
      elif fname=="ref_id_1":
        fields_lst.append({"fieldname":"refnumber1","label":T('Ref. No. 1'),
                       "widget":INPUT(_type="text",_value="",_name="refnumber1",_id=table+"_refnumber1",_class="string"),
                       "fieldcat":0})
        continue
      elif fname=="ref_id_2":
        fields_lst.append({"fieldname":"refnumber2","label":T('Ref. No. 2'),
                       "widget":INPUT(_type="text",_value="",_name="refnumber2",_id=table+"_refnumber2",_class="string"),
                       "fieldcat":0})
        continue
    elif table=="movement":
      if fname=="trans_id":
        fields_lst.append({"fieldname":"transnumber","label":T('Doc.No.'),
                       "widget":INPUT(_type="text",_value="",_name="transnumber",_id=table+"_transnumber",_class="string"),
                       "fieldcat":0})
        fields_lst.append({"fieldname":"rownumber","label":T('Row No.'),
                       "widget":INPUT(_type="text",_value="0",_name="rownumber",_id=table+"_rownumber",_class="integer"),
                       "fieldcat":0})
        continue
      elif fname=="movetype":
        ns.db.movement.movetype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('movetype')
                & ns.db.groups.groupvalue.belongs(('inventory', 'store', 'tool'))
                ), ns.db.groups.groupvalue, '%(groupvalue)s')
      elif fname=="product_id":
        fields_lst.append({"fieldname":"partnumber","label":T('Product No.'),
                       "widget":INPUT(_type="text",_value="",_name="partnumber",_id=table+"_partnumber",_class="string"),
                       "fieldcat":1})
        continue
      elif fname=="tool_id":
        fields_lst.append({"fieldname":"serial","label":T('Serial'),
                       "widget":INPUT(_type="text",_value="",_name="serial",_id=table+"_serial",_class="string"),
                       "fieldcat":1})
        continue
      elif fname=="place_id":
        fields_lst.append({"fieldname":"planumber","label":T('Place No.'),
                       "widget":INPUT(_type="text",_value="",_name="planumber",_id=table+"_planumber",_class="string"),
                       "fieldcat":1})
        continue
    elif table=="numberdef":
      if fname=="numberkey":
        fieldcat=0
    elif table=="pattern":
      if fname=="description":
        fieldcat=0
      elif fname=="transtype":  
        ns.db.pattern.transtype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('transtype')), 
                                                    ns.db.groups.groupvalue, '%(groupvalue)s')
    elif table=="payment":
      if fname=="trans_id":
        fields_lst.append({"fieldname":"transnumber","label":T('Doc.No.'),
                       "widget":INPUT(_type="text",_value="",_name="transnumber",_id=table+"_transnumber",_class="string"),
                       "fieldcat":0})
        fields_lst.append({"fieldname":"rownumber","label":T('Row No.'),
                       "widget":INPUT(_type="text",_value="0",_name="rownumber",_id=table+"_rownumber",_class="integer"),
                       "fieldcat":0})
        continue
    elif table=="place":
      if fname=="planumber":
        fieldcat=0
      elif fname=="place_id":
        fields_lst.append({"fieldname":"ref_planumber","label":T('Ref. No.'),
                       "widget":INPUT(_type="text",_value="",_name="ref_planumber",_id=table+"_ref_planumber",_class="string"),
                       "fieldcat":1})
        continue
      elif fname=="placetype":  
        ns.db.place.placetype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('placetype')), 
                                                    ns.db.groups.groupvalue, '%(groupvalue)s')
      elif fname=="storetype":
        continue
    elif table=="price":
      if fname=="product_id":
        fields_lst.append({"fieldname":"partnumber","label":T('Product No.'),
                       "widget":INPUT(_type="text",_value="",_name="partnumber",_id=table+"_partnumber",_class="string"),
                       "fieldcat":0})
        fields_lst.append({"fieldname":"pricetype","label":T('Type'),
                       "widget":SELECT([OPTION("", _value=""),OPTION(T("price"), _value="price"),
                                        OPTION(T("discount"), _value="discount")
                                        ], _id=table+"_pricetype", _name="pricetype"),
                       "fieldcat":0})
        continue
      elif fname=="validfrom":
        fieldcat=0
      elif fname=="pricevalue":
        ns.db.price.pricevalue.label = T("Value/limit")
      elif fname=="calcmode":  
        ns.db.price.calcmode.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('calcmode')), 
                                                    ns.db.groups.groupvalue, '%(description)s')
    elif table=="product":
      if fname=="partnumber":
        fieldcat=0
      elif fname=="protype":  
        ns.db.product.protype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('protype')), 
                                                    ns.db.groups.groupvalue, '%(groupvalue)s')
      elif fname=="tax_id":
        taxcode = ns.db(ns.db.tax.inactive==0).select(ns.db.tax.taxcode)
        widget=SELECT(*[OPTION(field.taxcode) for field in taxcode], _id="product_taxcode", _name="taxcode")
        widget.insert(0, OPTION(""))
        fields_lst.append({"fieldname":"taxcode","label":T('Tax'), "widget":widget, "fieldcat":0})
        continue
    elif table=="project":
      if fname=="pronumber":
        fieldcat=0
      elif fname=="customer_id":
        fields_lst.append({"fieldname":"custnumber","label":T('Customer No.'),
                       "widget":INPUT(_type="text",_value="",_name="custnumber",_id=table+"_custnumber",_class="string"),
                       "fieldcat":1})
        continue
    elif table=="rate":
      if fname == "ratetype":
        fieldcat=0
        ns.db.rate.ratetype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('ratetype')), 
                                                    ns.db.groups.groupvalue, '%(groupvalue)s')
      elif fname in("ratedate","curr"):
        fieldcat=0
      elif fname=="place_id":
        fields_lst.append({"fieldname":"planumber","label":T('Place No.'),
                       "widget":INPUT(_type="text",_value="",_name="planumber",_id=table+"_planumber",_class="string"),
                       "fieldcat":0})
        continue
      elif fname == "rategroup":
        ns.db.rate.rategroup.requires = IS_EMPTY_OR(IS_IN_DB(ns.db((ns.db.groups.deleted==0)
          &ns.db.groups.groupname.like('rategroup')), ns.db.groups.groupvalue, '%(groupvalue)s'))
    elif table=="tax":
      if fname=="taxcode":
        fieldcat=0
    elif table=="tool":
      if fname=="serial":
        fieldcat=0
      elif fname=="product_id":
        fields_lst.append({"fieldname":"partnumber","label":T('Product No.'),
                       "widget":INPUT(_type="text",_value="",_name="partnumber",_id=table+"_partnumber",_class="string"),
                       "fieldcat":1})
        continue
      elif fname == "toolgroup":
        ns.db.tool.toolgroup.requires = IS_EMPTY_OR(IS_IN_DB(ns.db((ns.db.groups.deleted==0)
          &ns.db.groups.groupname.like('toolgroup')), ns.db.groups.groupvalue, '%(groupvalue)s'))
    elif table=="trans":
      if fname=="transnumber":
        fieldcat=0
      elif fname == "transtype":
        ns.db.trans.transtype.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('transtype')), 
                                                    ns.db.groups.groupvalue, '%(groupvalue)s')
      elif fname == "direction":
        ns.db.trans.direction.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('direction')), 
                                                    ns.db.groups.groupvalue, '%(groupvalue)s')
      elif fname == "paidtype":
        ns.db.trans.paidtype.requires = IS_EMPTY_OR(IS_IN_DB(ns.db((ns.db.groups.deleted==0)
          &ns.db.groups.groupname.like('paidtype')), ns.db.groups.groupvalue, '%(groupvalue)s'))
      elif fname == "department":
        ns.db.trans.department.requires = IS_EMPTY_OR(IS_IN_DB(ns.db((ns.db.groups.deleted==0)
          &ns.db.groups.groupname.like('department')), ns.db.groups.groupvalue, '%(groupvalue)s'))
      elif fname == "transtate":
        ns.db.trans.transtate.requires = IS_IN_DB(ns.db(ns.db.groups.groupname.like('transtate')), 
                                                    ns.db.groups.groupvalue, '%(groupvalue)s')
      elif fname=="customer_id":
        fields_lst.append({"fieldname":"custnumber","label":T('Customer No.'),
                       "widget":INPUT(_type="text",_value="",_name="custnumber",_id=table+"_custnumber",_class="string"),
                       "fieldcat":1})
        continue
      elif fname=="employee_id":
        fields_lst.append({"fieldname":"empnumber","label":T('Employee No.'),
                       "widget":INPUT(_type="text",_value="",_name="empnumber",_id=table+"_empnumber",_class="string"),
                       "fieldcat":1})
        continue
      elif fname=="project_id":
        fields_lst.append({"fieldname":"pronumber","label":T('Project No.'),
                       "widget":INPUT(_type="text",_value="",_name="pronumber",_id=table+"_pronumber",_class="string"),
                       "fieldcat":1})
        continue
      elif fname=="place_id":
        fields_lst.append({"fieldname":"planumber","label":T('Place No.'),
                       "widget":INPUT(_type="text",_value="",_name="planumber",_id=table+"_planumber",_class="string"),
                       "fieldcat":1})
        continue
      elif fname=="cruser_id":
        continue
    elif table=="fieldvalue":
      if fname=="fieldname":
        fields_lst.append({"fieldname":"fieldname","label":T('Fieldname'),
                       "widget":INPUT(_type="text",_value="",_name="fieldname",_id=table+"_fieldname",_class="string"),
                       "fieldcat":0})
        continue
      elif fname=="ref_id":
        continue
      elif fname=="fieldtype":
        ns.db.fieldvalue.fieldtype.requires = IS_IN_DB(ns.db((ns.db.groups.groupname.like('fieldtype'))
          &(ns.db.groups.groupvalue!="checkbox")&(ns.db.groups.groupvalue!="trans")), ns.db.groups.id, '%(groupvalue)s')
                                                      
    form = SQLFORM(ns.db[table])
    fields_lst.append({"fieldname":fname,"label":form.custom.label[fname],
                       "widget":form.custom.widget[fname],"fieldcat":fieldcat})
  
  if table in("address", "contact", "customer", "employee", "event", "groups", "item", "link", "log", 
              "movement", "price", "place", "product", "project", "tool", "trans"):
    nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue==table)).select().as_list()[0]["id"]
    deffields = ns.db((ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)&(ns.db.deffield.nervatype==nervatype)
                      &(ns.db.deffield.readonly==0)&(ns.db.deffield.fieldtype==ns.db.groups.id)).select(
                        ns.db.deffield.fieldname,ns.db.groups.groupvalue,ns.db.deffield.description,ns.db.deffield.valuelist)
    for deffield in deffields:
      if deffield.groups.groupvalue=="bool":
        fields_lst.append({"fieldname":deffield.deffield.fieldname,"label":deffield.deffield.description,
                       "widget":INPUT(_type="checkbox",_value="on",_name=deffield.deffield.fieldname,_id=table+"_"+deffield.deffield.fieldname,_class="boolean"),
                       "fieldcat":2})
      elif deffield.groups.groupvalue=="integer":
        fields_lst.append({"fieldname":deffield.deffield.fieldname,"label":deffield.deffield.description,
                       "widget":INPUT(_type="text",_value="0",_name=deffield.deffield.fieldname,_id=table+"_"+deffield.deffield.fieldname,_class="integer"),
                       "fieldcat":2})
      elif deffield.groups.groupvalue=="float":
        fields_lst.append({"fieldname":deffield.deffield.fieldname,"label":deffield.deffield.description,
                       "widget":INPUT(_type="text",_value="0",_name=deffield.deffield.fieldname,_id=table+"_"+deffield.deffield.fieldname,_class="double"),
                       "fieldcat":2})
      elif deffield.groups.groupvalue=="date":
        fields_lst.append({"fieldname":deffield.deffield.fieldname,"label":deffield.deffield.description,
                       "widget":INPUT(_type="text",_value="",_name=deffield.deffield.fieldname,_id=table+"_"+deffield.deffield.fieldname,_class="date"),
                       "fieldcat":2})
      elif deffield.groups.groupvalue=="valuelist":
        widget = SELECT(*[OPTION(field) for field in deffield.deffield.valuelist.split("|")], _name=deffield.deffield.fieldname,_id=table+"_"+deffield.deffield.fieldname)
        widget.insert(0, OPTION("", _value=""))
        fields_lst.append({"fieldname":deffield.deffield.fieldname,"label":deffield.deffield.description,"widget":widget,"fieldcat":2})
      else:
        fields_lst.append({"fieldname":deffield.deffield.fieldname,"label":deffield.deffield.description,
                       "widget":INPUT(_type="text",_value="",_name=deffield.deffield.fieldname,_id=table+"_"+deffield.deffield.fieldname,_class="string"),
                       "fieldcat":2})
  return fields_lst
