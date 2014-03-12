# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""
  
from gluon.sql import DAL, Field
from gluon import SQLFORM
from gluon.html import URL
from gluon.html import INPUT, DIV, A, SPAN
from gluon.validators import IS_IN_DB, IS_EMAIL, IS_EMPTY_OR, IS_NOT_IN_DB, IS_FLOAT_IN_RANGE #IS_STRONG, CRYPT
from gluon.storage import Storage
import datetime
import time
import os
from hashlib import md5
from base64 import encodestring, decodestring
from pyDes import des, PAD_PKCS5

from nerva2py.models import employee

class Validators(object):
  #general and validator functions
  def __init__(self, ns):
    self.ns = ns
  
  class check_boolean(object):
    def __init__(self, T):
      self.error_message = T("Invalid boolean type")
    def __call__(self, value):
      try:
        if value==1 or str(value).lower() in('true','t','y','yes','on','1'):
          value = 1
        else:
          value = 0
        return (value, None)
      except:
        return (value, self.error_message)
    def formatter(self, value):
      return INPUT(_type='checkbox', _value=value, value=bool(value), _disabled='disabled')
    
  class check_fieldvalue(object):
    def __init__(self, ns, row):
      self.ns = ns
      self.row = row
      self.error_message = self.ns.T("Invalid value type")
    def __call__(self, value):
      try:
        fld_type = self.ns.db(self.ns.db.groups.id==self.ns.db(self.ns.db.deffield.fieldname==self.row.fieldname).select()[0]["fieldtype"]).select()[0]["groupvalue"]
        ref_id=None
        if fld_type == 'bool':
          if value in('true','True','TRUE','t','T','y','YES','yes','1'):
            value = 'true'
          elif value in('false','False','FALSE','f','F','n','no','NO','0',None):
            value = 'false'
          else:
            return (value, value+str(self.ns.T(" not valid bool value (true or false)")))
          return (value, None)
        elif fld_type == 'integer':
          try:
            value = str(int(value))
            return (value, None)
          except:
            return (value, value+str(self.ns.T(" not valid integer")))
        elif fld_type == 'float':
          try:
            value = str(float(value))
            return (value, None)
          except:
            return (value, value+str(self.ns.T(" not valid float")))
        elif fld_type == 'date':
          try:
            y, m, d, hh, mm, ss, t0, t1, t2 = time.strptime(value, str('%Y-%m-%d')) #@UnusedVariable
            value = datetime.date(y, m, d)
            return (value, None)
          except:
            return (value, value+str(self.ns.T(' not valid date (YYYY-MM-DD)')))
        elif fld_type == 'password':
          try:
            if not (value.startswith("XXX") and value.endswith("XXX")):
              value = self.ns.valid.set_password_field(self.row.fieldname,value)
            return (value, None)
          except:
            return (value, value+str(self.ns.T(" can not be encrypted")))
        elif fld_type in ('string', 'valuelist', 'notes', 'urlink'):
          return (value, None)
        elif fld_type == 'customer':
          ref_id = self.ns.valid.get_id_from_refnumber("customer",value)
          if ref_id:
            return (ref_id, None)
          else:
            try:
              value = int(value)
            except:
              return (value, str(self.ns.T(' missing customer')))
            if self.ns.db.customer(id=value):
              return (value, None)
            else:
              return (value, value+str(self.ns.T(' not valid customer')))
        elif fld_type == 'tool':
          ref_id = self.ns.valid.get_id_from_refnumber("tool",value)
          if ref_id:
            return (ref_id, None)
          else:
            try:
              value = int(value)
            except:
              return (value, str(self.ns.T(' missing tool')))
            if self.ns.db.tool(id=int(value)):
              return (value, None)
            else:
              return (value, value+str(self.ns.T(' not valid tool')))
        elif fld_type == 'product':
          ref_id = self.ns.valid.get_id_from_refnumber("product",value)
          if ref_id:
            return (ref_id, None)
          else:
            try:
              value = int(value)
            except:
              return (value, str(self.ns.T(' missing product')))
            if len(self.ns.db.product(id=int(value)).items())>0:
              return (value, None)
            else:
              return (value, value+str(self.ns.T(' not valid product')))
        elif fld_type in ('transitem','transmovement','transpayment'):
          ref_id = self.ns.valid.get_id_from_refnumber("trans",value)
          if ref_id:
            return (ref_id, None)
          else:
            try:
              value = int(value)
            except:
              return (value, str(self.ns.T(' missing trans')))
            if len(self.ns.db.trans(id=int(value)).items())>0:
              return (value, None)
            else:
              return (value, value+str(self.ns.T(' not valid trans')))
        elif fld_type == 'project':
          ref_id = self.ns.valid.get_id_from_refnumber("project",value)
          if ref_id:
            return (ref_id, None)
          else:
            try:
              value = int(value)
            except:
              return (value, str(self.ns.T(' missing project')))
            if len(self.ns.db.project(id=int(value)).items())>0:
              return (value, None)
            else:
              return (value, value+str(self.ns.T(' not valid project')))
        elif fld_type == 'employee':
          ref_id = self.ns.valid.get_id_from_refnumber("employee",value)
          if ref_id:
            return (ref_id, None)
          else:
            try:
              value = int(value)
            except:
              return (value, str(self.ns.T(' missing employee')))  
            if len(self.ns.db.employee(id=int(value)).items())>0:
              return (value, None)
            else:
              return (value, value+str(self.ns.T(' not valid employee')))
        elif fld_type == 'place':
          ref_id = self.ns.valid.get_id_from_refnumber("place",value)
          if ref_id:
            return (ref_id, None)
          else:
            try:
              value = int(value)
            except:
              return (value, str(self.ns.T(' missing place')))
            if len(self.ns.db.place(id=int(value)).items())>0:
              return (value, None)
            else:
              return (value, value+str(self.ns.T(' not valid place')))
        else:
          return (value, self.error_message)    
      except:
        return (value, self.error_message)
    def formatter(self, value):
      return value
  
  def check_integrity(self, nervatype, ref_id):
    if not ref_id: return True
    if ref_id<0: return True
    retvalue = True
    nervatype_id = self.get_groups_id("nervatype",nervatype)
    
    #all nervatype: link
    if len(self.ns.db((self.ns.db.link.nervatype_1==nervatype_id)&(self.ns.db.link.ref_id_1==ref_id)
      &(self.ns.db.link.deleted==0)).select())>0: retvalue=False
    elif len(self.ns.db((self.ns.db.link.nervatype_2==nervatype_id)&(self.ns.db.link.ref_id_2==ref_id)
      &(self.ns.db.link.deleted==0)).select())>0: retvalue=False
    #no check: fieldvalue, log
#     if len(self.ns.db(self.ns.db.fieldvalue.fieldname.belongs(
#       self.ns.db((self.ns.db.deffield.nervatype==nervatype_id)&(self.ns.db.deffield.deleted==0)).select(self.ns.db.deffield.fieldname))
#       &(self.ns.db.fieldvalue.ref_id==ref_id)&(self.ns.db.fieldvalue.deleted==0)).select())>0: retvalue=False      
#     elif len(self.ns.db((self.ns.db.log.nervatype==nervatype_id)&(self.ns.db.log.ref_id==ref_id)).select())>0: retvalue=False
        
    if nervatype in("address","barcode","contact","fieldvalue","item","link","log","movement","pattern","payment",
                    "price","rate"):
      pass
    elif nervatype=="currency":
      #place,price,rate,trans
      curr = self.ns.db.currency(id=ref_id).curr
      if len(self.ns.db((self.ns.db.place.curr==curr)&(self.ns.db.place.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.price.curr==curr)&(self.ns.db.price.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.rate.curr==curr)&(self.ns.db.rate.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.trans.curr==curr)&(self.ns.db.trans.deleted==0)).select())>0: retvalue=False
    elif nervatype=="customer":
      #address,contact,event,project,trans
#       if len(self.ns.db((self.ns.db.address.nervatype==nervatype_id)&(self.ns.db.address.ref_id==ref_id)
#         &(self.ns.db.address.deleted==0)).select())>0: retvalue=False
#       elif len(self.ns.db((self.ns.db.contact.nervatype==nervatype_id)&(self.ns.db.contact.ref_id==ref_id)
#         &(self.ns.db.contact.deleted==0)).select())>0: retvalue=False
      if len(self.ns.db((self.ns.db.event.nervatype==nervatype_id)&(self.ns.db.event.ref_id==ref_id)
        &(self.ns.db.event.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.project.customer_id==ref_id)&(self.ns.db.project.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.trans.customer_id==ref_id)&(self.ns.db.trans.deleted==0)).select())>0: retvalue=False
    elif nervatype=="deffield":
      #fieldvalue
      fieldname = self.ns.db.deffield(id=ref_id).fieldname
      if len(self.ns.db((self.ns.db.fieldvalue.fieldname==fieldname)&(self.ns.db.fieldvalue.deleted==0)).select())>0: retvalue=False
    elif nervatype=="employee":
      #address,contact,event,trans,log
#       if len(self.ns.db((self.ns.db.address.nervatype==nervatype_id)&(self.ns.db.address.ref_id==ref_id)
#         &(self.ns.db.address.deleted==0)).select())>0: retvalue=False
#       elif len(self.ns.db((self.ns.db.contact.nervatype==nervatype_id)&(self.ns.db.contact.ref_id==ref_id)
#         &(self.ns.db.contact.deleted==0)).select())>0: retvalue=False
      if len(self.ns.db((self.ns.db.event.nervatype==nervatype_id)&(self.ns.db.event.ref_id==ref_id)
        &(self.ns.db.event.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.trans.employee_id==ref_id)&(self.ns.db.trans.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.trans.cruser_id==ref_id)&(self.ns.db.trans.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.log.employee_id==ref_id)).select())>0: retvalue=False
      #ui_filter,ui_printqueue,ui_userconfig
      if len(self.ns.db((self.ns.db.ui_filter.employee_id==ref_id)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.ui_printqueue.employee_id==ref_id)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.ui_userconfig.employee_id==ref_id)).select())>0: retvalue=False
    elif nervatype=="event":
      #address,contact
      if len(self.ns.db((self.ns.db.address.nervatype==nervatype_id)&(self.ns.db.address.ref_id==ref_id)
        &(self.ns.db.address.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.contact.nervatype==nervatype_id)&(self.ns.db.contact.ref_id==ref_id)
        &(self.ns.db.contact.deleted==0)).select())>0: retvalue=False
    elif nervatype=="groups":
      if self.ns.db.groups(id=ref_id).groupname in ("nervatype","custtype","fieldtype","logstate","movetype","transtype","placetype",
                                             "storetype","calcmode","protype","ratetype","direction","paidtype","transtate",
                                             "inputfilter","filetype","wheretype","aggretype"):
        #protected, always false
        retvalue=False
      elif len(self.ns.db((self.ns.db.barcode.barcodetype==ref_id)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.deffield.subtype==ref_id)&(self.ns.db.deffield.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.employee.usergroup==ref_id)&(self.ns.db.employee.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.employee.department==ref_id)&(self.ns.db.employee.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.event.eventgroup==ref_id)&(self.ns.db.event.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.rate.rategroup==ref_id)&(self.ns.db.rate.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.tool.toolgroup==ref_id)&(self.ns.db.tool.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.trans.department==ref_id)&(self.ns.db.trans.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.ui_groupinput. groups_id==ref_id)).select())>0: retvalue=False
    elif nervatype=="numberdef":
      #protected, always false
      retvalue=False
    elif nervatype=="place":
      #address,contact,event,movement,place,rate,trans
#       if len(self.ns.db((self.ns.db.address.nervatype==nervatype_id)&(self.ns.db.address.ref_id==ref_id)
#         &(self.ns.db.address.deleted==0)).select())>0: retvalue=False
#       elif len(self.ns.db((self.ns.db.contact.nervatype==nervatype_id)&(self.ns.db.contact.ref_id==ref_id)
#         &(self.ns.db.contact.deleted==0)).select())>0: retvalue=False
      if len(self.ns.db((self.ns.db.event.nervatype==nervatype_id)&(self.ns.db.event.ref_id==ref_id)
        &(self.ns.db.event.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.movement.place_id==ref_id)&(self.ns.db.movement.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.place.place_id==ref_id)&(self.ns.db.place.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.rate.place_id==ref_id)&(self.ns.db.rate.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.trans.place_id==ref_id)&(self.ns.db.trans.deleted==0)).select())>0: retvalue=False
    elif nervatype=="product":
      #address,barcode,contact,event,item,movement,price,tool
      if len(self.ns.db((self.ns.db.address.nervatype==nervatype_id)&(self.ns.db.address.ref_id==ref_id)
        &(self.ns.db.address.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.barcode.product_id==ref_id)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.contact.nervatype==nervatype_id)&(self.ns.db.contact.ref_id==ref_id)
        &(self.ns.db.contact.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.event.nervatype==nervatype_id)&(self.ns.db.event.ref_id==ref_id)
        &(self.ns.db.event.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.item.product_id==ref_id)&(self.ns.db.item.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.movement.product_id==ref_id)&(self.ns.db.movement.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.price.product_id==ref_id)&(self.ns.db.price.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.tool.product_id==ref_id)&(self.ns.db.tool.deleted==0)).select())>0: retvalue=False
    elif nervatype=="project":
      #address,contact,event,trans
#       if len(self.ns.db((self.ns.db.address.nervatype==nervatype_id)&(self.ns.db.address.ref_id==ref_id)
#         &(self.ns.db.address.deleted==0)).select())>0: retvalue=False
#       elif len(self.ns.db((self.ns.db.contact.nervatype==nervatype_id)&(self.ns.db.contact.ref_id==ref_id)
#         &(self.ns.db.contact.deleted==0)).select())>0: retvalue=False
      if len(self.ns.db((self.ns.db.event.nervatype==nervatype_id)&(self.ns.db.event.ref_id==ref_id)
        &(self.ns.db.event.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.trans.place_id==ref_id)&(self.ns.db.trans.deleted==0)).select())>0: retvalue=False  
    elif nervatype=="tax":
      #item,product
      if len(self.ns.db((self.ns.db.item.tax_id==ref_id)&(self.ns.db.item.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.product.tax_id==ref_id)&(self.ns.db.product.deleted==0)).select())>0: retvalue=False
    elif nervatype=="tool":
      #address,contact,event,movement
#       if len(self.ns.db((self.ns.db.address.nervatype==nervatype_id)&(self.ns.db.address.ref_id==ref_id)
#         &(self.ns.db.address.deleted==0)).select())>0: retvalue=False
#       elif len(self.ns.db((self.ns.db.contact.nervatype==nervatype_id)&(self.ns.db.contact.ref_id==ref_id)
#         &(self.ns.db.contact.deleted==0)).select())>0: retvalue=False
      if len(self.ns.db((self.ns.db.event.nervatype==nervatype_id)&(self.ns.db.event.ref_id==ref_id)
        &(self.ns.db.event.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.movement.tool_id==ref_id)&(self.ns.db.movement.deleted==0)).select())>0: retvalue=False
    elif nervatype=="trans":
      #address,contact,event,item,movement,payment
      if len(self.ns.db((self.ns.db.address.nervatype==nervatype_id)&(self.ns.db.address.ref_id==ref_id)
        &(self.ns.db.address.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.contact.nervatype==nervatype_id)&(self.ns.db.contact.ref_id==ref_id)
        &(self.ns.db.contact.deleted==0)).select())>0: retvalue=False
      elif len(self.ns.db((self.ns.db.event.nervatype==nervatype_id)&(self.ns.db.event.ref_id==ref_id)
        &(self.ns.db.event.deleted==0)).select())>0: retvalue=False
#       elif len(self.ns.db((self.ns.db.item.trans_id==ref_id)&(self.ns.db.item.deleted==0)).select())>0: retvalue=False
#       elif len(self.ns.db((self.ns.db.movement.trans_id==ref_id)&(self.ns.db.movement.deleted==0)).select())>0: retvalue=False
#       elif len(self.ns.db((self.ns.db.payment.trans_id==ref_id)&(self.ns.db.payment.deleted==0)).select())>0: retvalue=False
    
    if not retvalue:
      self.ns.error_message = str(self.ns.T("Integrity error. The object can not be deleted!"))
    return retvalue
  
  class check_integrity_boolean(object):
    def __init__(self, ns, nervatype, row_id):
      self.ns = ns
      self.nervatype = nervatype
      self.id = row_id
      self.bool_error_message = ns.T("Invalid boolean type")
      self.integrity_error_message = ns.T("Integrity error. The object can not be deleted!")
    def __call__(self, value):
      try:
        if value==1 or str(value).lower() in('true','t','y','yes','on','1'):
          if self.ns.valid.check_integrity(self.nervatype,self.id): 
            value = 1
          else:
            return (value, self.integrity_error_message)
        else:
          value = 0
        return (value, None)
      except:
        return (value, self.error_message)
    def formatter(self, value):
      return INPUT(_type='checkbox', _value=value, value=bool(value), _disabled='disabled')
  
  def get_audit_subtype(self,row,value):
    retvalue=""
    nervatype = self.ns.db.groups(id=row.nervatype).groupvalue
    if nervatype=="trans" and value!=None:
      transtype = self.ns.db(self.ns.db.groups.id==value).select().as_list()
      if len(transtype)>0:
        return transtype[0]["groupvalue"]
    if nervatype=="report" and value!=None:
      report = self.ns.db(self.ns.db.ui_report.id==value).select().as_list()
      if len(report)>0:
        return report[0]["reportkey"]
    if nervatype=="menu" and value!=None:
      menu = self.ns.db(self.ns.db.ui_menu.id==value).select().as_list()
      if len(menu)>0:
        return menu[0]["menukey"]
    return retvalue
  
  def get_default_value(self, fieldtype):
    fld_type = self.get_nervatype_name(fieldtype)
    if fld_type == 'bool':
      return "false"
    elif fld_type == 'integer' or fld_type == 'float':
      return "0"
    else:
      return ""
    
  def get_groups_id(self,groupname,groupvalue,use_deleted=False):
    if use_deleted:
      groups = self.ns.db((self.ns.db.groups.groupname==groupname)&(self.ns.db.groups.groupvalue==groupvalue)).select()
    else:
      groups = self.ns.db((self.ns.db.groups.groupname==groupname)&(self.ns.db.groups.groupvalue==groupvalue)
                     &(self.ns.db.groups.deleted==0)).select()
    return groups[0]["id"] if len(groups)>0 else None
  
  def get_id_from_refnumber(self,nervatype,refnumber,use_deleted=False):
    try:
      if nervatype in("address","contact"):
        #ref_nervatype/refnumber~rownumber
        ref_nervatype = str(refnumber).split("/")[0]
        if len(str(str(refnumber)[len(ref_nervatype)+1:]).split("~"))>1:
          if int(str(str(refnumber)[len(ref_nervatype)+1:]).split("~")[1])<1:
            return None
          else:
            ref_index = int(str(str(refnumber)[len(ref_nervatype)+1:]).split("~")[1])-1
        else:
          ref_index = 0
        refnumber = str(str(refnumber)[len(ref_nervatype)+1:]).split("~")[0]
        if ref_nervatype in ('customer', 'employee', 'event', 'place', 'product', 'project', 'tool', 'trans'):
          ref_type_id = self.get_groups_id("nervatype", ref_nervatype, use_deleted)
          if use_deleted:
            head_row = self.ns.db((self.ns.db[ref_nervatype][self.ns.valid.get_table_key(ref_nervatype)]==refnumber)).select()
            return self.ns.db((self.ns.db[nervatype].ref_id==head_row[0]["id"])
                         &(self.ns.db[nervatype].nervatype==ref_type_id)).select()[ref_index]["id"]
          else:
            head_row = self.ns.db((self.ns.db[ref_nervatype][self.ns.valid.get_table_key(ref_nervatype)]==refnumber)
                             &(self.ns.db[ref_nervatype].deleted==0)).select()
            return self.ns.db((self.ns.db[nervatype].ref_id==head_row[0]["id"])
                         &(self.ns.db[nervatype].nervatype==ref_type_id)&(self.ns.db[nervatype].deleted==0)).select()[ref_index]["id"]
      elif nervatype=="barcode":
        #code
        if use_deleted:
          return self.ns.db.barcode(code=refnumber).id
        else:
          if self.ns.db((self.ns.db.product.id==self.ns.db.barcode(code=refnumber).id)
                   &(self.ns.db.product.deleted==0)).select()[0]["id"]:
            return self.ns.db.barcode(code=refnumber).id
      elif nervatype=="currency":
        #curr
        return self.ns.db.currency(curr=refnumber).id
      elif nervatype=="customer":
        #custnumber
        if use_deleted:
          return self.ns.db((self.ns.db.customer.custnumber==refnumber)).select()[0]["id"]
        else:
          return self.ns.db((self.ns.db.customer.custnumber==refnumber)&(self.ns.db.customer.deleted==0)).select()[0]["id"]
      elif nervatype=="deffield":
        #fieldname
        if use_deleted:
          return self.ns.db((self.ns.db.deffield.fieldname==str(refnumber).split("~")[0])).select()[0]["id"]
        else:
          return self.ns.db((self.ns.db.deffield.fieldname==str(refnumber).split("~")[0])&(self.ns.db.deffield.deleted==0)).select()[0]["id"]
      elif nervatype=="employee":
        #empnumber
        if use_deleted:
          return self.ns.db((self.ns.db.employee.empnumber==refnumber)).select()[0]["id"]
        else:
          return self.ns.db((self.ns.db.employee.empnumber==refnumber)&(self.ns.db.employee.deleted==0)).select()[0]["id"]
      elif nervatype=="event":
        #calnumber
        if use_deleted:
          return self.ns.db((self.ns.db.event.calnumber==refnumber)).select()[0]["id"]
        else:
          return self.ns.db((self.ns.db.event.calnumber==refnumber)&(self.ns.db.event.deleted==0)).select()[0]["id"]
      elif nervatype=="fieldvalue":
        #refnumber~~fieldname~rownumber
        if len(str(refnumber).split("~~"))>1:
          ref_value = str(refnumber).split("~~")[0]
          fieldname = str(str(refnumber).split("~~")[1]).split("~")[0]
          ref_type = self.ns.db.groups(id=self.ns.db.deffield(fieldname=fieldname).nervatype).groupvalue
          ref_id = self.get_id_from_refnumber(ref_type, ref_value, use_deleted=use_deleted)
          if len(str(str(refnumber).split("~~")[1]).split("~"))>1:
            if int(str(str(refnumber).split("~~")[1]).split("~")[1])<1:
              return None
            else:
              ref_index = int(str(str(refnumber).split("~~")[1]).split("~")[1])-1
          else:
            ref_index = 0
          if use_deleted:
            return self.ns.db((self.ns.db.fieldvalue.fieldname==fieldname)&(self.ns.db.fieldvalue.ref_id==ref_id)).select()[ref_index]["id"]
          else:
            return self.ns.db((self.ns.db.fieldvalue.fieldname==fieldname)&(self.ns.db.fieldvalue.ref_id==ref_id)
                         &(self.ns.db.fieldvalue.deleted==0)).select()[ref_index]["id"]
        else:
          #setting
          if use_deleted:
            return self.ns.db((self.ns.db.fieldvalue.fieldname==refnumber)&(self.ns.db.fieldvalue.ref_id==None)).select()[0].id
          else:
            return self.ns.db((self.ns.db.fieldvalue.fieldname==refnumber)&(self.ns.db.fieldvalue.ref_id==None)
                         &(self.ns.db.fieldvalue.deleted==0)).select()[0].id
      elif nervatype=="groups":
        #groupname~groupvalue
        ref_value = str(refnumber).split("~")
        if use_deleted:
          return self.ns.db((self.ns.db.groups.groupname==ref_value[0])&(self.ns.db.groups.groupvalue==ref_value[1])).select()[0].id
        else:
          return self.ns.db((self.ns.db.groups.groupname==ref_value[0])&(self.ns.db.groups.groupvalue==ref_value[1])
                       &(self.ns.db.groups.deleted==0)).select()[0].id
      elif nervatype in("item","payment","movement"):
        #refnumber~rownumber
        ref_value = str(refnumber).split("~")[0]
        if len(str(refnumber).split("~"))>1:
          if int(str(refnumber).split("~")[1])<1:
            return None
          else:
            ref_index = int(str(refnumber).split("~")[1])-1
        else:
          ref_index = 0
        if use_deleted:
          trans_id = self.ns.db((self.ns.db.trans.transnumber==ref_value)).select()[0]["id"]
          return self.ns.db((self.ns.db[nervatype].trans_id==trans_id)).select()[ref_index]["id"]
        else:
          trans_id = self.ns.db((self.ns.db.trans.transnumber==ref_value)&(self.ns.db.trans.deleted==0)).select()[0]["id"]
          return self.ns.db((self.ns.db[nervatype].trans_id==trans_id)&(self.ns.db[nervatype].deleted==0)).select()[ref_index]["id"]
      elif nervatype=="numberdef":
        #numberkey
        return self.ns.db.numberdef(numberkey=refnumber).id
      elif nervatype=="pattern":
        #description
        if use_deleted:
          return self.ns.db((self.ns.db.pattern.description==refnumber)).select()[0]["id"]
        else:
          return self.ns.db((self.ns.db.pattern.description==refnumber)&(self.ns.db.pattern.deleted==0)).select()[0]["id"]
      elif nervatype=="place":
        #planumber
        if use_deleted:
          return self.ns.db((self.ns.db.place.planumber==refnumber)).select()[0]["id"]
        else:
          return self.ns.db((self.ns.db.place.planumber==refnumber)&(self.ns.db.place.deleted==0)).select()[0]["id"]
      elif nervatype=="price":
        #partnumber~pricetype~validfrom~curr~qty
        ref_value = str(refnumber).split("~")
        if ref_value[1]=="price":
          pricetype = (self.ns.db.price.discount==None)
        elif ref_value[1]=="discount":
          pricetype = (self.ns.db.price.discount!=None)
        else:
          return None
        validfrom = datetime.datetime.strptime(ref_value[2],'%Y-%m-%d')
        curr = ref_value[3]
        qty = float(ref_value[4])
        if use_deleted:
          product_id = self.ns.db((self.ns.db.product.partnumber==ref_value[0])).select()[0]["id"]
          return self.ns.db((self.ns.db.price.product_id==product_id) & pricetype & (self.ns.db.price.curr==curr)
                       &(self.ns.db.price.validfrom==validfrom) & (self.ns.db.price.qty==qty)).select()[0].id
        else:
          product_id = self.ns.db((self.ns.db.product.partnumber==ref_value[0])&(self.ns.db.product.deleted==0)).select()[0]["id"]
          return self.ns.db((self.ns.db.price.product_id==product_id) & pricetype & (self.ns.db.price.curr==curr)
                       &(self.ns.db.price.validfrom==validfrom) & (self.ns.db.price.qty==qty)
                       &(self.ns.db.price.deleted==0)).select()[0].id
      elif nervatype=="product":
        #partnumber
        if use_deleted:
          return self.ns.db((self.ns.db.product.partnumber==refnumber)).select()[0]["id"]
        else:
          return self.ns.db((self.ns.db.product.partnumber==refnumber)&(self.ns.db.product.deleted==0)).select()[0]["id"]
      elif nervatype=="project":
        #pronumber
        if use_deleted:
          return self.ns.db((self.ns.db.project.pronumber==refnumber)).select()[0]["id"]
        else:
          return self.ns.db((self.ns.db.project.pronumber==refnumber)&(self.ns.db.project.deleted==0)).select()[0]["id"]
      elif nervatype=="tax":
        #taxcode
        return self.ns.db.tax(taxcode=refnumber).id
      elif nervatype=="tool":
        #serial
        if use_deleted:
          return self.ns.db((self.ns.db.tool.serial==refnumber)).select()[0]["id"]
        else:
          return self.ns.db((self.ns.db.tool.serial==refnumber)&(self.ns.db.tool.deleted==0)).select()[0]["id"]
      elif nervatype=="trans":
        #transnumber
        transtype_invoice_id = self.get_groups_id("transtype","invoice",use_deleted)
        transtype_receipt_id = self.get_groups_id("transtype","receipt",use_deleted)
        transtype_cash_id = self.get_groups_id("transtype","cash",use_deleted)
        direction_out_id = self.get_groups_id("direction","out",use_deleted)
        if use_deleted:
          return self.ns.db((self.ns.db.trans.transnumber==refnumber)).select()[0]["id"]
        else:
          return self.ns.db((self.ns.db.trans.transnumber==refnumber)
                       &((self.ns.db.trans.deleted==0)
                         |((self.ns.db.trans.transtype==transtype_invoice_id)&(self.ns.db.trans.direction==direction_out_id))
                         |((self.ns.db.trans.transtype==transtype_receipt_id)&(self.ns.db.trans.direction==direction_out_id))
                         |((self.ns.db.trans.transtype==transtype_cash_id)))
                       ).select()[0]["id"]
      elif nervatype=="setting":
        #fieldname
        if use_deleted:
          return self.ns.db((self.ns.db.fieldvalue.fieldname==refnumber)&(self.ns.db.fieldvalue.ref_id==None)).select()[0]["id"]
        else:
          return self.ns.db((self.ns.db.fieldvalue.fieldname==refnumber)&(self.ns.db.fieldvalue.ref_id==None)
                       &(self.ns.db.fieldvalue.deleted==0)).select()[0]["id"]
      elif nervatype=="link":
        #nervatype_1~refnumber_1~~nervatype_2~refnumber_2
        ref_type_1 = str(str(refnumber).split("~~")[0]).split("~")[0]
        ref_value_1 = str(str(refnumber).split("~~")[0])[len(ref_type_1)+1:]
        nervatype_1 = self.get_groups_id("nervatype", ref_type_1, use_deleted)
        ref_id_1 = self.get_id_from_refnumber(ref_type_1, ref_value_1, use_deleted=use_deleted)
        
        ref_type_2 = str(str(refnumber).split("~~")[1]).split("~")[0]
        ref_value_2 = str(str(refnumber).split("~~")[1])[len(ref_type_2)+1:]
        nervatype_2 = self.get_groups_id("nervatype", ref_type_2, use_deleted)
        ref_id_2 = self.get_id_from_refnumber(ref_type_2, ref_value_2, use_deleted=use_deleted)
        if use_deleted:
          return self.ns.db((self.ns.db.link.nervatype_1==nervatype_1)&(self.ns.db.link.ref_id_1==ref_id_1)
                       &(self.ns.db.link.nervatype_2==nervatype_2)&(self.ns.db.link.ref_id_2==ref_id_2)).select()[0]["id"]
        else:
          return self.ns.db((self.ns.db.link.nervatype_1==nervatype_1)&(self.ns.db.link.ref_id_1==ref_id_1)
                       &(self.ns.db.link.nervatype_2==nervatype_2)&(self.ns.db.link.ref_id_2==ref_id_2)
                       &(self.ns.db.link.deleted==0)).select()[0]["id"]
      elif nervatype=="rate":
        #ratetype~ratedate~curr~planumber
        ratetype = self.get_groups_id("ratetype", str(refnumber).split("~")[0], use_deleted)
        ratedate = datetime.datetime.strptime(str(refnumber).split("~")[1],'%Y-%m-%d')
        curr = str(refnumber).split("~")[2]
        if use_deleted:
          place_id = self.ns.db((self.ns.db.place.planumber==str(refnumber).split("~")[3])).select()[0]["id"]
          return self.ns.db((self.ns.db.rate.ratetype==ratetype)&(self.ns.db.rate.ratedate==ratedate)
                       &(self.ns.db.rate.curr==curr)&(self.ns.db.rate.place_id==place_id)).select()[0]["id"]
        else:
          place_id = self.ns.db((self.ns.db.place.planumber==str(refnumber).split("~")[3])&(self.ns.db.place.deleted==0)).select()[0]["id"]
          return self.ns.db((self.ns.db.rate.ratetype==ratetype)&(self.ns.db.rate.ratedate==ratedate)
                       &(self.ns.db.rate.curr==curr)&(self.ns.db.rate.place_id==place_id)
                       &(self.ns.db.rate.deleted==0)).select()[0]["id"]
      elif nervatype=="log":
        #empnumber~crdate
        if use_deleted:
          employee_id = self.ns.db((self.ns.db.employee.empnumber==str(refnumber).split("~")[0])).select()[0]["id"]
        else:
          employee_id = self.ns.db((self.ns.db.employee.empnumber==str(refnumber).split("~")[0])
                              &(self.ns.db.employee.deleted==0)).select()[0]["id"]
        crdate = datetime.datetime.strptime(str(refnumber).split("~")[1],'%Y-%m-%d %H:%M:%S')
        return self.ns.db((self.ns.db.log.employee_id==employee_id)&(self.ns.db.log.crdate==crdate)).select()[0]["id"]
      
      elif nervatype=="ui_applview":
        #viewname
        return self.ns.db.ui_applview(viewname=refnumber).id
      elif nervatype=="ui_viewfields":
        #viewname~fieldname
        viewname = str(refnumber).split("~")[0]
        fieldname = str(refnumber).split("~")[1]
        return self.ns.db((self.ns.db.ui_viewfields.viewname==viewname)
                          &(self.ns.db.ui_viewfields.fieldname==fieldname)).select()[0]["id"]
      
      elif nervatype=="ui_audit":
        #usergroup~nervatype~transtype
        usergroup = self.get_groups_id("usergroup", str(refnumber).split("~")[0])
        nervatype = self.get_groups_id("nervatype", str(refnumber).split("~")[1])
        if len(str(refnumber).split("~"))>2:
          subtype = self.get_groups_id("transtype", str(refnumber).split("~")[2])
        else:
          subtype = None
        return self.ns.db((self.ns.db.ui_audit.usergroup==usergroup)&(self.ns.db.ui_audit.nervatype==nervatype)
                          &(self.ns.db.ui_audit.subtype==subtype)).select()[0]["id"]
                          
      elif nervatype=="ui_language":
        #lang
        return self.ns.db.ui_language(lang=refnumber).id
      elif nervatype=="ui_locale":
        #country
        return self.ns.db.ui_locale(country=refnumber).id
      
      elif nervatype=="ui_menu":
        #menukey
        return self.ns.db.ui_menu(menukey=refnumber).id
      elif nervatype=="ui_menufields":
        #menukey~fieldname
        menu_id = self.get_id_from_refnumber("ui_menu", str(refnumber).split("~")[0])
        fieldname = str(refnumber).split("~")[1]
        return self.ns.db((self.ns.db.ui_menufields.menu_id==menu_id)
                          &(self.ns.db.ui_menufields.fieldname==fieldname)).select()[0]["id"]
      
      elif nervatype=="ui_report":
        #reportkey
        return self.ns.db.ui_report(reportkey=refnumber).id
      elif nervatype=="ui_reportfields":
        #reportkey~fieldname
        report_id = self.get_id_from_refnumber("ui_report", str(refnumber).split("~")[0])
        fieldname = str(refnumber).split("~")[1]
        return self.ns.db((self.ns.db.ui_reportfields.report_id==report_id)
                          &(self.ns.db.ui_reportfields.fieldname==fieldname)).select()[0]["id"]
      elif nervatype=="ui_reportsources":
        #reportkey~dataset
        report_id = self.get_id_from_refnumber("ui_report", str(refnumber).split("~")[0])
        dataset = str(refnumber).split("~")[1]
        return self.ns.db((self.ns.db.ui_reportsources.report_id==report_id)
                          &(self.ns.db.ui_reportsources.dataset==dataset)).select()[0]["id"]
                          
      self.ns.error_message = str(self.ns.T("Invalid refnumber:"))+str(refnumber)
      return None
    except Exception:
      self.ns.error_message = str(self.ns.T("Invalid refnumber:"))+str(refnumber)
      return None
            
  def get_md5_value(self, value):
    rv = md5()
    rv.update(value)
    return rv.hexdigest()
  
  def get_nervatype_name(self,group_id,ref_id=None):
    nervatype = self.ns.db.groups(id=group_id).groupvalue
    if nervatype=="trans" and ref_id!=None:
      nervatype = self.ns.db.groups(id=self.ns.db.trans(id=ref_id).transtype).groupvalue
    return nervatype
  
  def get_own_customer(self):
    company = self.ns.db(self.ns.db.customer.custtype==self.ns.valid.get_groups_id("custtype", "own")).select(orderby=self.ns.db.customer.id)
    if len(company)==0:
      self.ns.db.customer.insert(**dict({'custtype':self.ns.valid.get_groups_id("custtype", "own"), 
                                         'custnumber':'HOME', 'custname':'COMPANY NAME', 'taxnumber':'12345678-1-12'}))
      company = self.ns.db(self.ns.db.customer.custtype==self.ns.valid.get_groups_id("custtype", "own")).select(orderby=self.ns.db.customer.id)
    company = company[0]
    company.address = self.ns.db((self.ns.db.address.nervatype==self.ns.valid.get_groups_id("nervatype", "customer"))
                                 &(self.ns.db.address.ref_id==company.id)&(self.ns.db.address.deleted==0)).select()
    return company
  
  def get_password_field(self,fieldname,value):
    if value!=None and value!="" and value.startswith("XXX") and value.endswith("XXX"):
      try:
        key = fieldname[:8] if len(fieldname)>8 else fieldname.ljust(8,"*")
        return des(key, padmode=PAD_PKCS5).decrypt(decodestring(value[3:-3]))
      except:
        return value
    else:
      return value
  
  def get_represent(self,field,value,record,clear=False):
    f = field.represent
    if not callable(f):
      return value
    n = f.func_code.co_argcount-len(f.func_defaults or [])
    if n==1:
      rvalue = f(value)
    elif n==2:
      rvalue = f(value,record)
    else:
      rvalue = value
    if clear:
      if type(rvalue).__name__=="A":
        return rvalue[0][0]
      elif type(rvalue).__name__=="DIV":
        return rvalue[0]
    return rvalue
  
  def get_table_key(self, nervatype):
    if nervatype=="barcode":
      return "code"
    elif nervatype=="currency":
      return "curr"
    elif nervatype=="customer":
      return "custnumber"
    elif nervatype=="deffield":
      return "fieldname"
    elif nervatype=="employee":
      return "empnumber"
    elif nervatype=="event":
      return "calnumber"
    elif nervatype=="groups":
      return "groupvalue"
    elif nervatype=="place":
      return "planumber"
    elif nervatype=="product":
      return "partnumber"
    elif nervatype=="project":
      return "pronumber"
    elif nervatype=="tax":
      return "taxcode"
    elif nervatype=="tool":
      return "serial"
    elif nervatype=="trans":
      return "transnumber"
    else:
      return ""
  
  def set_invoice_customer(self,values,customer_id=None):
    if customer_id:
      customer = self.ns.db.customer(id=customer_id)
    elif values.has_key("id"):
      if self.ns.db.trans(id=values["id"]):
        customer = self.ns.db.customer(id=self.ns.db.trans(id=values["id"]).customer_id)
    if customer:
      values["trans_custinvoice_custname"] = str(customer["custname"])
      if customer["taxnumber"]:
        values["trans_custinvoice_custtax"] = str(customer["taxnumber"])
      address = self.ns.db((self.ns.db.address.deleted==0)
                           &(self.ns.db.address.nervatype==self.get_groups_id("nervatype","customer"))
                           &(self.ns.db.address.ref_id==customer["id"])).select()
      if len(address)>0:
        address_str=""
        if address[0]["zipcode"]: address_str = str(address[0]["zipcode"])
        if address[0]["city"]: address_str = address_str+" "+str(address[0]["city"])
        if address[0]["street"]: address_str = address_str+" "+str(address[0]["street"])
        values["trans_custinvoice_custaddress"] = address_str
      else:
        values["trans_custinvoice_custaddress"] = ""
    customer = self.ns.valid.get_own_customer()
    values["trans_custinvoice_compname"] = str(customer["custname"])
    if customer["taxnumber"]:
      values["trans_custinvoice_comptax"] = str(customer["taxnumber"])
    if len(customer.address)>0:
      address_str=""
      if customer.address[0]["zipcode"]: address_str = str(customer.address[0]["zipcode"])
      if customer.address[0]["city"]: address_str = address_str+" "+str(customer.address[0]["city"])
      if customer.address[0]["street"]: address_str = address_str+" "+str(customer.address[0]["street"])
      values["trans_custinvoice_compaddress"] = address_str
    else:
      values["trans_custinvoice_compaddress"] = ""
  
  def set_password_field(self,fieldname,value):
    if not value or value=="":
      return ""
    else:
      try:
        key = fieldname[:8] if len(fieldname)>8 else fieldname.ljust(8,"*")
        return "XXX"+encodestring(des(key, padmode=PAD_PKCS5).encrypt(value))+"XXX"
      except:
        return value
  
  def show_fieldvalue(self, row):
    retvalue = row.value
    fieldname = self.ns.db(self.ns.db.fieldvalue.id==row.id).select()[0]["fieldname"]
    fld_type = self.ns.db(self.ns.db.groups.id==self.ns.db(self.ns.db.deffield.fieldname==fieldname).select()[0]["fieldtype"]).select()[0]["groupvalue"]
    if fld_type == 'bool':
      retvalue = DIV(INPUT(_type="checkbox", value=(retvalue=="true"), _disabled="disabled"), _align="center", _width="100%")
    elif fld_type == 'integer':
      try:
        retvalue = DIV(self.ns.valid.split_thousands(float(retvalue)," ","."), _align="right", _width="100%")
      except Exception:
        pass
    elif fld_type == 'float':
      try:
        retvalue = DIV(self.ns.valid.split_thousands(float(retvalue)," ","."), _align="right", _width="100%")
      except Exception:
        pass
    elif fld_type == 'date':
      retvalue = DIV(retvalue, _align="center", _width="100%")
    elif fld_type in ('string', 'valuelist', 'notes'):
        pass
    elif fld_type == 'customer':
      if len(self.ns.db.customer(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.ns.db.customer(id=int(retvalue))["custname"]), 
                     _href=URL(r=self.ns.request, f="frm_customer/view/customer/"+retvalue), _target="_blank")
      else:
        retvalue = self.ns.T("Missing customer...")
    elif fld_type == 'tool':
      if len(self.ns.db.tool(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.ns.db.tool(id=int(retvalue))["serial"]),
                     _href=URL(r=self.ns.request, f="frm_tool/view/tool/"+retvalue), _target="_blank")
      else:
        retvalue = self.ns.T("Missing tool...")
    elif fld_type == 'product':
      if len(self.ns.db.product(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.ns.db.product(id=int(retvalue))["description"]),
                     _href=URL(r=self.ns.request, f="frm_product/view/product/"+retvalue), _target="_blank")
      else:
        retvalue = self.ns.T("Missing product...")
    elif fld_type in ('transitem','transmovement','transpayment'):
      if len(self.ns.db.trans(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.ns.db.trans(id=int(retvalue))["transnumber"]),
                     _href=URL(r=self.ns.request, f="frm_trans/view/trans/"+retvalue), _target="_blank")
      else:
        retvalue = self.ns.T("Missing transnumber...")
    elif fld_type == 'project':
      if len(self.ns.db.project(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.ns.db.project(id=int(retvalue))["pronumber"]),
                     _href=URL(r=self.ns.request, f="frm_project/view/project/"+retvalue), _target="_blank")
      else:
        retvalue = self.ns.T("Missing project...")
    elif fld_type == 'employee':
      if len(self.ns.db.employee(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.ns.db.employee(id=int(retvalue))["empnumber"]),
                     _href=URL(r=self.ns.request, f="frm_employee/view/employee/"+retvalue), _target="_blank")
      else:
        retvalue = self.ns.T("Missing employee...")
    elif fld_type == 'place':
      if len(self.ns.db.place(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.ns.db.place(id=int(retvalue))["planumber"]),
                     _href=URL(r=self.ns.request, f="frm_place/view/place/"+retvalue), _target="_blank")
      else:
        retvalue = self.ns.T("Missing place...")
    elif fld_type == 'urlink':
      retvalue = A(SPAN(retvalue), _href=retvalue, _target="_blank")
    elif fld_type == 'password':
      retvalue = "*****"
    else:
      pass
    return retvalue
  
  def show_refnumber(self, rettype, nervatype, ref_id, retfield=None, use_deleted=False):
    try:
      if ref_id==None:
        return ""
      if self.ns.db.has_key(nervatype):
        if self.ns.db[nervatype].has_key("deleted") and not use_deleted:
          self.ns.db((self.ns.db[nervatype].id==ref_id)&(self.ns.db[nervatype].deleted==0)).select()[0]
      if nervatype in("address","contact"):
        #ref_nervatype/refnumber~rownumber
        ref_nervatype_id = self.ns.db[nervatype](id=ref_id).nervatype
        ref_nervatype_name = self.ns.db.groups(id=ref_nervatype_id).groupvalue
        head_id = self.ns.db[nervatype](id=ref_id).ref_id
        refnumber = self.show_refnumber("refnumber",ref_nervatype_name,head_id,use_deleted=use_deleted)
        if not refnumber: return None
        if use_deleted:
          row_index = self.ns.db((self.ns.db[nervatype].nervatype==ref_nervatype_id)&(self.ns.db[nervatype].ref_id==head_id)
                   &(self.ns.db[nervatype].id<=ref_id)).select('count(*)').first()['count(*)']
        else:
          row_index = self.ns.db((self.ns.db[nervatype].nervatype==ref_nervatype_id)&(self.ns.db[nervatype].ref_id==head_id)
                   &(self.ns.db[nervatype].deleted==0)&(self.ns.db[nervatype].id<=ref_id)).select('count(*)').first()['count(*)']
        if rettype=="refnumber":
          if retfield:
            return self.ns.db[nervatype](id=ref_id)[retfield]
          else:
            return ref_nervatype_name+"/"+refnumber+"~"+str(row_index)
        elif rettype=="index":
          return row_index
        elif rettype=="href":
          return "frm_"+ref_nervatype_name+"/view/"+ref_nervatype_name+"/"+str(head_id)
      elif nervatype=="barcode":
        #code
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.barcode(id=ref_id)[retfield]
          else:
            return self.ns.db.barcode(id=ref_id).code
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_product/view/product/"+str(self.ns.db.barcode(id=ref_id).product_id)
      elif nervatype=="currency":
        #curr
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.currency(id=ref_id)[retfield]
          else:
            return self.ns.db.currency(id=ref_id).curr
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_currency/edit/currency/"+str(ref_id)
      elif nervatype=="customer":
        #custnumber
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.customer(id=ref_id)[retfield]
          else:
            return self.ns.db.customer(id=ref_id).custnumber
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_customer/view/customer/"+str(ref_id)
      elif nervatype=="deffield":
        #fieldname
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.deffield(id=ref_id)[retfield]
          else:
            return self.ns.db.deffield(id=ref_id).fieldname
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_deffield_all/edit/deffield/"+str(ref_id)
      elif nervatype=="employee":
        #empnumber
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.employee(id=ref_id)[retfield]
          else:
            return self.ns.db.employee(id=ref_id).empnumber
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_employee/view/employee/"+str(ref_id)
      elif nervatype=="event":
        #calnumber
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.event(id=ref_id)[retfield]
          else:
            return self.ns.db.event(id=ref_id).calnumber
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_event/view/event/"+str(ref_id)
      elif nervatype=="fieldvalue":
        #refnumber~~fieldname~rownumber
        fieldname = self.ns.db[nervatype](id=ref_id).fieldname
        ref_nervatype=self.ns.db.groups(id=self.ns.db.deffield(fieldname=fieldname).nervatype).groupvalue
        head_id = self.ns.db[nervatype](id=ref_id).ref_id
        if head_id:
          refnumber = self.show_refnumber("refnumber", ref_nervatype, head_id, retfield, use_deleted=use_deleted)
          if not refnumber: return None
          if use_deleted:
            row_index = self.ns.db((self.ns.db[nervatype].fieldname==fieldname)&(self.ns.db[nervatype].ref_id==head_id)
                            &(self.ns.db[nervatype].id<=ref_id)).select('count(*)').first()['count(*)']
          else:
            row_index = self.ns.db((self.ns.db[nervatype].fieldname==fieldname)&(self.ns.db[nervatype].deleted==0)
                            &(self.ns.db[nervatype].ref_id==head_id)
                            &(self.ns.db[nervatype].id<=ref_id)).select('count(*)').first()['count(*)']
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.fieldvalue(id=ref_id)[retfield]
          else:
            if head_id:
              return refnumber+"~~"+fieldname+"~"+str(row_index)
            else:
              return fieldname
        elif rettype=="fieldname":
          if head_id:
            return fieldname+"~"+str(row_index)
          else:
            return fieldname
        elif rettype=="index":
          return row_index
        elif rettype=="href":
          self.show_refnumber("href", ref_nervatype, head_id, retfield, use_deleted=use_deleted)
      elif nervatype=="groups":
        #groupname~groupvalue
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.groups(id=ref_id)[retfield]
          else:
            return self.ns.db.groups(id=ref_id).groupname+"~"+self.ns.db.groups(id=ref_id).groupvalue
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_groups_all/edit/groups/"+str(ref_id)
      elif nervatype in("item","payment","movement"):
        #refnumber~rownumber
        head_id = self.ns.db[nervatype](id=ref_id).trans_id
        head = self.ns.db.trans(id=head_id)
        transtype_invoice_id = self.get_groups_id("transtype","invoice",use_deleted)
        transtype_receipt_id = self.get_groups_id("transtype","receipt",use_deleted)
        transtype_cash_id = self.get_groups_id("transtype","cash",use_deleted)
        direction_out_id = self.get_groups_id("direction","out",use_deleted)
        if head.transtype==transtype_cash_id:
          pass
        elif ((head.transtype==transtype_invoice_id) or (head.transtype==transtype_receipt_id)) and head.direction==direction_out_id:
          pass
        elif head.deleted==1 and not use_deleted:
          return None
        if use_deleted:
          row_index = self.ns.db((self.ns.db[nervatype].trans_id==head_id)
                            &(self.ns.db[nervatype].id<=ref_id)).select('count(*)').first()['count(*)']
        else:
          row_index = self.ns.db((self.ns.db[nervatype].trans_id==head_id)&(self.ns.db[nervatype].deleted==0)
                            &(self.ns.db[nervatype].id<=ref_id)).select('count(*)').first()['count(*)']
        if rettype=="refnumber":
          if retfield:
            return self.ns.db[nervatype](id=ref_id)[retfield]
          else:
            return head.transnumber+"~"+str(row_index)
        elif rettype=="index":
          return row_index
        elif rettype=="href":
          return "frm_trans/view/trans/"+str(head_id)
      elif nervatype=="numberdef":
        #numberkey
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.numberdef(id=ref_id)[retfield]
          else:
            return self.ns.db.numberdef(id=ref_id).numberkey
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_numberdef/edit/numberdef/"+str(ref_id)
      elif nervatype=="pattern":
        #description
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.pattern(id=ref_id)[retfield]
          else:
            return self.ns.db.pattern(id=ref_id).description
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "index"
      elif nervatype=="place":
        #planumber
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.place(id=ref_id)[retfield]
          else:
            return self.ns.db.place(id=ref_id).planumber
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_place/view/place/"+str(ref_id)
      elif nervatype=="price":
        #partnumber~pricetype~validfrom~curr~qty
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.price(id=ref_id)[retfield]
          else:
            head_id = self.ns.db.price(id=ref_id).product_id
            if self.ns.db.product(id=head_id).deleted==1 and not use_deleted: return None
            partnumber = self.ns.db.product(id=head_id).partnumber
            validfrom = datetime.date.strftime(self.ns.db.price(id=ref_id).validfrom,'%Y-%m-%d')
            ptype="discount" if self.ns.db.price(id=ref_id).discount else "price"
            return partnumber+"~"+ptype+"~"+validfrom+"~"+self.ns.db.price(id=ref_id).curr+"~"+str(self.ns.db.price(id=ref_id).qty)
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "find_product_price/view/product/"+str(self.ns.db.price(id=ref_id).product_id)
      elif nervatype=="product":
        #partnumber
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.product(id=ref_id)[retfield]
          else:
            return self.ns.db.product(id=ref_id).partnumber
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_product/view/product/"+str(ref_id)
      elif nervatype=="project":
        #pronumber
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.project(id=ref_id)[retfield]
          else:
            return self.ns.db.project(id=ref_id).pronumber
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_project/view/project/"+str(ref_id)
      elif nervatype=="tax":
        #taxcode
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.tax(id=ref_id)[retfield]
          else:
            return self.ns.db.tax(id=ref_id).taxcode
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_tax/edit/tax/"+str(ref_id)
      elif nervatype=="tool":
        #serial
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.tool(id=ref_id)[retfield]
          else:
            return self.ns.db.tool(id=ref_id).serial
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_tool/view/tool/"+str(ref_id)
      elif nervatype=="trans":
        #transnumber
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.trans(id=ref_id)[retfield]
          else:
            return self.ns.db.trans(id=ref_id).transnumber
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_trans/view/trans/"+str(ref_id)
      elif nervatype=="setting":
        #fieldname
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.fieldvalue(id=ref_id)[retfield]
          else:
            return self.ns.db.fieldvalue(id=ref_id).fieldname
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "frm_setting"
      elif nervatype=="link":
        #nervatype_1~refnumber_1~~nervatype_2~refnumber_2
        head_id_1 = self.ns.db[nervatype](id=ref_id).ref_id_1
        ref_nervatype_1=self.ns.db.groups(id=self.ns.db[nervatype](id=ref_id).nervatype_1).groupvalue
        head_refnumber_1 = self.show_refnumber("refnumber", ref_nervatype_1, head_id_1, retfield, use_deleted=use_deleted)
        if not head_refnumber_1: return None
        head_id_2 = self.ns.db[nervatype](id=ref_id).ref_id_2
        ref_nervatype_2=self.ns.db.groups(id=self.ns.db[nervatype](id=ref_id).nervatype_2).groupvalue
        head_refnumber_2 = self.show_refnumber("refnumber", ref_nervatype_2, head_id_2, retfield, use_deleted=use_deleted)
        if not head_refnumber_2: return None
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.link(id=ref_id)[retfield]
          else:
            return ref_nervatype_1+"~"+head_refnumber_1+"~~"+ref_nervatype_2+"~"+head_refnumber_2
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "index"
      elif nervatype=="rate":
        #ratetype~ratedate~curr~planumber
        ratetype=self.ns.db.groups(id=self.ns.db[nervatype](id=ref_id).ratetype).groupvalue
        ratedate = datetime.date.strftime(self.ns.db[nervatype](id=ref_id).ratedate,'%Y-%m-%d')
        curr = self.ns.db[nervatype](id=ref_id).curr
        planumber = self.show_refnumber("refnumber", "place", self.ns.db[nervatype](id=ref_id).place_id, retfield, use_deleted=use_deleted)
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.rate(id=ref_id)[retfield]
          else:
            return ratetype+"~"+ratedate+"~"+curr+"~"+str(planumber)
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return ""
      elif nervatype=="log":
        #empnumber~crdate
        if self.ns.db.employee(id=self.ns.db[nervatype](id=ref_id).employee_id).deleted==1 and not use_deleted: return None
        empnumber=self.ns.db.employee(id=self.ns.db[nervatype](id=ref_id).employee_id).empnumber
        crdate = datetime.date.strftime(self.ns.db[nervatype](id=ref_id).crdate,'%Y-%m-%d %H:%M:%S')
        if rettype=="refnumber":
          if retfield:
            return self.ns.db.log(id=ref_id)[retfield]
          else:
            return empnumber+"~"+crdate
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "index"
      elif self.ns.db.has_key(nervatype):
        if rettype=="refnumber":
          if retfield:
            if self.ns.db[nervatype].has_key(retfield):
              return self.ns.db[nervatype](id=ref_id)[retfield]
            else:
              return self.ns.db[nervatype](id=ref_id).id
          else:
            return self.ns.db[nervatype](id=ref_id).id
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "index"
      else:
        if rettype=="refnumber":
          return ""
        elif rettype=="index":
          return 1
        elif rettype=="href":
          return "index"
      return ""
    except Exception:
      return None

  def split_thousands(self, s, tSep=',', dSep='.'):
    if s == None:
      return 0
    if not isinstance( s, str ):
      s = str( s )
    cnt=0
    numChars=dSep+'0123456789'
    ls=len(s)
    while cnt < ls and s[cnt] not in numChars: cnt += 1
    lhs = s[ 0:cnt ]
    s = s[ cnt: ]
    if dSep == '':
      cnt = -1
    else:
      cnt = s.rfind( dSep )
    if cnt > 0:
      rhs = dSep + s[ cnt+1: ]
      s = s[ :cnt ]
    else:
      rhs = ''
    splt=''
    while s != '':
      splt= s[ -3: ] + tSep + splt
      s = s[ :-3 ]
    return lhs + splt[ :-1 ] + rhs
            
class DataConnect(object):
  #dbs connect, user login, authentication, data access
  def __init__(self, ns):
    self.ns = ns
  
  def deleteData(self, nervatype, ref_id=None, refnumber=None, log_enabled=True):
    try:
      if not self.ns.db.has_key(nervatype):
        self.ns.error_message = str(self.ns.T("Unknown nervatype value: "))+str(nervatype) 
        return False
      if not ref_id:
        ref_id = self.ns.valid.get_id_from_refnumber(nervatype, refnumber)
      if not self.ns.db[nervatype](id=ref_id):
        if refnumber:
          self.ns.error_message = str(self.ns.T("Unknown refnumber value: "))+str(refnumber)
        else:
          self.ns.error_message = str(self.ns.T("Unknown id value: "))+str(ref_id) 
        return False
      if not self.ns.valid.check_integrity(nervatype, ref_id): return False
      nervatype_id = self.ns.valid.get_groups_id("nervatype", nervatype)
      logical_delete=True
      if self.ns.db.fieldvalue(fieldname="not_logical_delete"):
        if self.ns.db.fieldvalue(fieldname="not_logical_delete")["value"]=="true": logical_delete=False
      if self.ns.db[nervatype].has_key("deleted") and logical_delete:
        self.ns.db(self.ns.db[nervatype]["id"]==ref_id).update(**{"deleted":1})
      else:
        try:
          self.ns.db(self.ns.db.fieldvalue.id.belongs(self.ns.db(self.ns.db.fieldvalue.fieldname.belongs(
            self.ns.db((self.ns.db.deffield.nervatype==nervatype_id)&(self.ns.db.deffield.deleted==0)).select(self.ns.db.deffield.fieldname))
            &(self.ns.db.fieldvalue.ref_id==ref_id)).select(self.ns.db.fieldvalue.id))).delete()
          self.ns.db(self.ns.db[nervatype].id==ref_id).delete()
          self.ns.db.commit()
          ref_id=None
        except Exception, err:
          self.ns.db.rollback()
          self.ns.error_message = str(err)
          return False
      if log_enabled:
        self.insertLog(logstate="deleted", nervatype=nervatype, ref_id=ref_id, refnumber=refnumber)
      return True
    except Exception, err:
      self.ns.error_message = str(err)
      self.ns.db.rollback()
      return None
  
  def getDataAudit(self):
    #Nervatura data access rights: own,usergroup,all
    #see: employee.usergroup+link+transfilter
    try:
      if self.ns.employee==None:
        self.ns.error_message = str(self.ns.T("Login required!"))
        return "error"
      if self.ns.employee.usergroup==None:
        self.ns.error_message = str(self.ns.T("Missing usergroup!"))
        return "error"
      nervatype_id = self.ns.valid.get_groups_id("nervatype", "groups")
      transfilter_id = self.ns.db((self.ns.db.link.deleted==0)&(self.ns.db.link.nervatype_1==nervatype_id)
                            &(self.ns.db.link.nervatype_2==nervatype_id)&(self.ns.db.link.ref_id_1==self.ns.employee.usergroup)).select()
      if len(transfilter_id)>0:   
        transfilter = self.ns.db(self.ns.db.groups.id==transfilter_id[0]["ref_id_2"]).select().as_list()
        if len(transfilter)>0:
          return transfilter[0]["groupvalue"]
        else:
          return "all"
      else:
        return "all"
    except Exception, err:
      self.ns.error_message = err
      return "error" 
  
  def getObjectAudit(self, nervatype, transtype=None):
    #Nervatura objects access rights: disabled,readonly,update,all
    #see: audit
    try:
      if self.ns.employee==None:
        self.ns.error_message = str(self.ns.T("Login required!"))
        return "error"
      if self.ns.employee.usergroup==None:
        self.ns.error_message = str(self.ns.T("Missing usergroup!"))
        return "error"
      if nervatype=="sql" or nervatype=="fieldvalue":
        return "all"
      if nervatype==None:
        self.ns.error_message = str(self.ns.T("Missing nervatype!"))
        return "error"
      else:
        nervatype_id = self.ns.valid.get_groups_id("nervatype", nervatype)
        if not nervatype_id:   
          self.ns.error_message = str(self.ns.T("Unknown nervatype!"))
          return "error"
      if transtype!=None:
        transtype_id = self.ns.valid.get_groups_id("transtype", transtype)
        if not transtype_id:   
          self.ns.error_message = str(self.ns.T("Unknown transtype!"))
          return "error"
        audit = self.ns.db((self.ns.db.ui_audit.usergroup==self.ns.employee.usergroup)
                        &(self.ns.db.ui_audit.nervatype==nervatype_id)
                        &(self.ns.db.ui_audit.subtype==transtype_id)).select().as_list()
      else:
        audit = self.ns.db((self.ns.db.ui_audit.usergroup==self.ns.employee.usergroup)&(self.ns.db.ui_audit.nervatype==nervatype_id)).select().as_list()
      if len(audit)==0:
        return "all"
      else:
        inputfilter = self.ns.db(self.ns.db.groups.id==audit[0]["inputfilter"]).select().as_list()
        if len(inputfilter)>0:   
          return inputfilter[0]["groupvalue"]
        else:
          return "all"
    except Exception, err:
      self.ns.error_message = err
      return "error"  
  
  def getSetting(self,fieldname):
    setting = self.ns.db((self.ns.db.fieldvalue.fieldname==fieldname)&(self.ns.db.fieldvalue.ref_id==None)).select()
    return setting[0]["value"] if len(setting)>0 else ""
  
  def insertLog(self, logstate, nervatype=None, ref_id=None, refnumber=None):
    if self.ns.employee and nervatype!="log":
      log_enabled=False
      if self.ns.db.fieldvalue(fieldname="log_"+str(logstate)):
        log_enabled=True if self.ns.db.fieldvalue(fieldname="log_"+str(logstate))["value"]=="true" else False
      if self.ns.db.fieldvalue(fieldname="log_"+str(nervatype)+"_"+str(logstate)):
        log_enabled=True if self.ns.db.fieldvalue(fieldname="log_"+str(nervatype)+"_"+str(logstate))["value"]=="true" else False
      if log_enabled:
        logstate_id = self.ns.valid.get_groups_id("logstate", logstate)
        values = {"logstate":logstate_id, 
                  "employee_id":self.ns.employee["id"], "crdate":datetime.datetime.now()}
        if nervatype:
          values["nervatype"] = self.ns.valid.get_groups_id("nervatype", nervatype)
          if ref_id:
            values["ref_id"] = ref_id
          elif refnumber:
            values["ref_id"] = self.ns.valid.get_id_from_refnumber(nervatype, refnumber)
        self.ns.db.log.insert(**values)  
    return True
  
  def nextNumber(self, numberkey, step=True):
    #Get current value from numberdef table (transnumber, custnumber, partnumber etc.)
    retnumber = ""
    if not self.ns.db.numberdef(numberkey=numberkey):
      self.ns.db.numberdef.insert(numberkey=numberkey)
    defrow = self.ns.db.numberdef(numberkey=numberkey)
    if defrow.prefix:
      retnumber = defrow.prefix+defrow.sep
    if defrow.isyear == 1:
      transyear = self.getSetting("transyear")
      if transyear=="": transyear = str(datetime.date.today().year)
      retnumber = retnumber+transyear+defrow.sep
    retnumber = retnumber+str(defrow.curvalue+1).zfill(defrow.len)
    if step:
      defrow.curvalue +=1
      defrow.update_record()
    return retnumber
        
  def setConnect(self, uri, pool_size=0, createdb=True):
    try:
      self.ns.db = DAL(uri=uri, pool_size=pool_size, folder=self.ns.request.data_folder, adapter_args={'createdb':createdb})
    except Exception, err:
      self.ns.error_message = err
      self.ns.db = None
  
  def setLogin(self, username, password):
    try:
      if username==None:
        self.ns.error_message = str(self.ns.T("Missing user!"))
        return False
      employee = self.ns.db((self.ns.db.employee.inactive==0)&(self.ns.db.employee.deleted==0)&(self.ns.db.employee.username==username)).select()
      if len(employee)==0:   
        self.ns.error_message = str(self.ns.T("Unknown user!"))
        return False
      if password=="":
        password = None
      if password!=None and (hasattr(self, 'encrypt_data')==False or self.ns.md5_password==False):
        psw = self.ns.valid.get_md5_value(password)
      else:
        psw = password
      if psw!=employee[0].password:   
        self.ns.error_message = str(self.ns.T("Wrong password!"))
        return False
      self.ns.employee = employee[0]
      return True
    except Exception, err:
      self.ns.error_message = err
      return False
  
  def updateData(self, nervatype, values, log_enabled=True, validate=True, insert_row=False, insert_field=False, update_row=True):
    try:
      ref_id,nt_values,fv_values=None,{},{}
      if not self.ns.db.has_key(nervatype):
        self.ns.error_message = str(self.ns.T("Unknown nervatype value: "))+str(nervatype) 
        return None
      if values.has_key("id"):
        if self.ns.db[nervatype](id=values["id"]):
          ref_id = values["id"]
          if not update_row: return ref_id
        del values["id"]
      if not ref_id and not insert_row:
        self.ns.error_message = str(self.ns.T("New record and missing insert_row parameter!")) 
        return None
      for key in values.keys():
        if self.ns.db[nervatype].has_key(key):
          nt_values[key]= values[key]
        elif nervatype not in("groups","numberdef","deffield","pattern","fieldvalue"):
          fv_values[key]= values[key]
        else:
          self.ns.error_message = str(self.ns.T("Unknown fieldname: "))+key
          return None
        #add auto deffields
        if not ref_id:
          addnew = self.ns.db((self.ns.db.deffield.deleted==0)&(self.ns.db.deffield.visible==1)
                              &(self.ns.db.deffield.nervatype==self.ns.valid.get_groups_id("nervatype", nervatype))
                              &(self.ns.db.deffield.addnew==1)).select()
          for nfield in addnew:
            fv_values[nfield["fieldname"]]= self.ns.valid.get_default_value(nfield["fieldtype"])
          
      if len(nt_values)>0:
        if nervatype=="fieldvalue":
          self.ns.db.fieldvalue.value.requires = self.ns.valid.check_fieldvalue(self.ns, Storage(nt_values))
        if not ref_id:
          if validate:
            ret = self.ns.db[nervatype].validate_and_insert(**nt_values)
            if ret.errors:
              self.ns.error_message = str(ret.errors.keys()[0])+": "+str(ret.errors.values()[0])
              return ref_id
            else:
              ref_id = ret.id
          else:
            try:
              ref_id = self.ns.db[nervatype].insert(**nt_values)
            except Exception, err:
              self.ns.error_message = str(err)
              self.ns.db.rollback()
              return ref_id
        else:
          if validate:
            ret = self.ns.db(self.ns.db[nervatype].id==ref_id).validate_and_update(**nt_values)
            if ret.errors:
              self.ns.error_message = str(ret.errors.keys()[0])+": "+str(ret.errors.values()[0])
              self.ns.db.rollback()
              return None
          else:
            try:
              self.ns.db(self.ns.db[nervatype].id==ref_id).update(**nt_values)
            except Exception, err:
              self.ns.error_message = str(err)
              self.ns.db.rollback()
              return None
            
      if len(fv_values)>0:
        if not ref_id:
          self.ns.error_message = str(self.ns.T("Missing record id!"))
          self.ns.db.rollback()
          return None
        for key in fv_values.keys():
          fv_id=None
          if len(str(key).split("~"))>1:
            try:
              field_index = int(str(key).split("~")[1])-1
            except Exception:
              field_index = 0
            fieldname = str(key).split("~")[0]
          else:
            fieldname = key
            field_index = 0
          try:
            fv_id = self.ns.db((self.ns.db.fieldvalue.fieldname==fieldname)&(self.ns.db.fieldvalue.ref_id==ref_id)
                           &(self.ns.db.fieldvalue.deleted==0)).select()[field_index]["id"]
          except Exception:
            pass
          values={"fieldname":fieldname,"ref_id":ref_id}
          if len(str(fv_values[key]).split("~"))>1:
            values["value"] = str(fv_values[key]).split("~")[0]
            values["notes"] = str(fv_values[key]).split("~")[1]
          else:
            values["value"] = fv_values[key]
          self.ns.db.fieldvalue.value.requires = self.ns.valid.check_fieldvalue(self.ns, Storage(values))
          if not fv_id:
            nervatype_id = self.ns.valid.get_groups_id("nervatype", nervatype)
            deffield = self.ns.db((self.ns.db.deffield.fieldname==values["fieldname"])&(self.ns.db.deffield.nervatype==nervatype_id)
                           &(self.ns.db.deffield.deleted==0)).select()
            if len(deffield)==0:
              if not insert_field:
                self.ns.error_message = str(self.ns.T("Unknown fieldname and missing insert_field parameter: "))+str(values["fieldname"])
                self.ns.db.rollback()
                return None
              if self.ns.db.deffield(fieldname=values["fieldname"]):
                self.ns.error_message = str(self.ns.T("Invalid (contained) new fieldname: "))+str(values["fieldname"])
                self.ns.db.rollback()
                return None
              self.ns.db.deffield.insert(**dict({'fieldname':values["fieldname"], 'nervatype':nervatype_id, 
                                        'subtype':None, 'fieldtype':self.ns.valid.get_groups_id("fieldtype", "string"), 
                                        'description':values["fieldname"], 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
            if validate:
              ret = self.ns.db.fieldvalue.validate_and_insert(**values)
              if ret.errors:
                self.ns.error_message = str(ret.errors.keys()[0])+": "+str(ret.errors.values()[0])
                return None
            else:
              try:
                self.ns.db.fieldvalue.insert(**values)
              except Exception, err:
                self.ns.error_message = str(err)
                self.ns.db.rollback()
                return None
          else:
            if validate:
              ret = self.ns.db(self.ns.db.fieldvalue.id==fv_id).validate_and_update(**values)
              if ret.errors:
                self.ns.db.rollback()
                self.ns.error_message = str(ret.errors.keys()[0])+": "+str(ret.errors.values()[0])
                return None
            else:
              try:
                self.ns.db(self.ns.db.fieldvalue.id==fv_id).update(**values)
              except Exception, err:
                self.ns.db.rollback()
                self.ns.error_message = str(err)
                return None
        
      if log_enabled and ref_id>0:
        self.insertLog(logstate="update", nervatype=nervatype, ref_id=ref_id)
      return ref_id
    except Exception, err:
      self.ns.error_message = str(err)
      self.ns.db.rollback()
      return None

class DataStore(object):
  #database structure and initial values
  
  #specified in the order (Refuse to drop the table if any objects depend on it.)
  drop_all_table_lst = ["ui_zipcatalog","pattern","movement","payment","item","trans","barcode","price","tool",
                        "product","tax","rate","place","currency","project","customer","event","contact","address","numberdef",
                        "log","fieldvalue","deffield","ui_audit","link","ui_userconfig","ui_filter","ui_printqueue","employee",
                        "ui_viewfields","ui_groupinput","ui_reportsources","ui_reportfields","ui_report","ui_numtotext",
                        "ui_message","ui_menufields","ui_menu","ui_locale","ui_language","ui_applview","groups"]
  
  backup_nom_table_lst = ["groups","numberdef", #level 1a
                          "currency","tax", #level 1b
                          "deffield","pattern", #level 2a
                          "customer","employee","place","product", #level 2b
                          "barcode","price","project","rate","tool", #level 3
                          "trans", #level 4
                          "event","item","movement","payment", #level 5
                          "address","contact", #level 6
                          "link","log", #level 7
                          "fieldvalue"] #level 8
  
  backup_ui_table_lst = ["ui_applview","ui_menu","ui_language", #level 1
                          "ui_locale","ui_message","ui_numtotext", #level 2a
                          "ui_report","ui_audit","ui_groupinput","ui_viewfields", #level 2b
                          "ui_zipcatalog", #level 3a
                          "ui_menufields","ui_reportfields","ui_reportsources", #level 3b
                          "ui_filter","ui_userconfig" #level 4
                          #ui_printqueue no backup
                          ] 
  
  def __init__(self, ns):
    self.ns = ns
  
  def createIndex(self):
    try:
      self.ns.db.executesql("CREATE UNIQUE INDEX groups_namevalue_idx ON groups (groupname, groupvalue)")
      self.ns.db.executesql("CREATE INDEX groups_groupname_idx ON groups (groupname)")
      self.ns.db.executesql("CREATE INDEX groups_groupvalue_id_idx ON groups (groupvalue)")
      self.ns.db.executesql("CREATE INDEX groups_deleted_idx ON groups (deleted)")
      self.ns.db.executesql("CREATE INDEX groups_inactive_idx ON groups (inactive)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX applview_viewname_idx ON ui_applview (viewname)")
      self.ns.db.executesql("CREATE INDEX applview_parent_idx ON ui_applview (parentview)")
          
      self.ns.db.executesql("CREATE INDEX menucmd_modul_idx ON ui_menu (modul)")
      
      self.ns.db.executesql("CREATE INDEX menufields_menu_idx ON ui_menufields (menu_id)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX message_pk_idx ON ui_message (secname, fieldname, lang)")
      self.ns.db.executesql("CREATE INDEX message_fieldname_idx ON ui_message (fieldname)")
      self.ns.db.executesql("CREATE INDEX message_lang_idx ON ui_message (lang)")
      self.ns.db.executesql("CREATE INDEX message_secname_idx ON ui_message (secname)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX numtotext_pk_idx ON ui_numtotext (lang, digi, deci)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX report_reportkey_idx ON ui_report (reportkey)")
      self.ns.db.executesql("CREATE INDEX report_filetype_idx ON ui_report (filetype)")
      self.ns.db.executesql("CREATE INDEX report_reporttype_idx ON ui_report (nervatype)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX reportfields_pk_idx ON ui_reportfields (report_id, fieldname)")
      self.ns.db.executesql("CREATE INDEX reportfields_report_id_idx ON ui_reportfields (report_id)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX reportsources_pk_idx ON ui_reportsources (report_id, dataset)")
      self.ns.db.executesql("CREATE INDEX reportsources_reports_idx ON ui_reportsources (report_id)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX groupinput_pk_idx ON ui_groupinput (groups_id, formname, contname)")
      self.ns.db.executesql("CREATE INDEX groupinput_contname_idx ON ui_groupinput (contname)")
      self.ns.db.executesql("CREATE INDEX groupinput_formname_idx ON ui_groupinput (formname)")
      self.ns.db.executesql("CREATE INDEX groupinput_groups_id_idx ON ui_groupinput (groups_id)")

      self.ns.db.executesql("CREATE UNIQUE INDEX viewfields_pk_idx ON ui_viewfields (viewname, fieldname)")
      self.ns.db.executesql("CREATE INDEX viewfields_viewname_idx ON ui_viewfields (viewname)")
      self.ns.db.executesql("CREATE INDEX viewfields_fieldname_idx ON ui_viewfields (fieldname)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX employee_empnumber_idx ON employee (empnumber)")
      self.ns.db.executesql("CREATE UNIQUE INDEX employee_username_idx ON employee (username)")
      self.ns.db.executesql("CREATE INDEX employee_inactiv_idx ON employee (inactive)")
      self.ns.db.executesql("CREATE INDEX employee_deleted_idx ON employee (deleted)")
      
      self.ns.db.executesql("CREATE INDEX printqueue_nervatype_idx ON ui_printqueue (nervatype)")
      self.ns.db.executesql("CREATE INDEX printqueue_usename_idx ON ui_printqueue (employee_id)")
      
      self.ns.db.executesql("CREATE INDEX filter_parent_idx ON ui_filter (parentview)")

      self.ns.db.executesql("CREATE INDEX idx_userconfig_pk ON ui_userconfig (employee_id, cfgroup, cfname)")
      self.ns.db.executesql("CREATE INDEX idx_userconfig_ec ON ui_userconfig (employee_id, cfgroup)")
      self.ns.db.executesql("CREATE INDEX idx_userconfig_employee_ide ON ui_userconfig (employee_id)")

      self.ns.db.executesql("CREATE INDEX idx_link_nervatype_1 ON link (nervatype_1)")
      self.ns.db.executesql("CREATE INDEX idx_link_ref_id_1 ON link (ref_id_1)")
      self.ns.db.executesql("CREATE INDEX idx_link_nervatype_2 ON link (nervatype_2)")
      self.ns.db.executesql("CREATE INDEX idx_link_ref_id_2 ON link (ref_id_2)")
      self.ns.db.executesql("CREATE INDEX idx_link_deleted ON link (deleted)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX idx_audit_pk ON ui_audit (usergroup, nervatype, subtype)")
      self.ns.db.executesql("CREATE INDEX idx_audit_usergroup ON ui_audit (usergroup)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX deffield_fieldname_idx ON deffield (fieldname)")
      self.ns.db.executesql("CREATE INDEX deffield_nervatype_id_idx ON deffield (nervatype, subtype)")
      self.ns.db.executesql("CREATE INDEX deffield_deleted_idx ON deffield (deleted)")

      self.ns.db.executesql("CREATE INDEX fieldvalue_fieldname_idx ON fieldvalue (fieldname)")
      self.ns.db.executesql("CREATE INDEX fieldvalue_ref_id_idx ON fieldvalue (ref_id)")

      self.ns.db.executesql("CREATE INDEX log_logstate_idx ON log (logstate)")
      self.ns.db.executesql("CREATE INDEX log_nervatype_idx ON log (nervatype, ref_id)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX numberdef_numberkey_idx ON numberdef (numberkey)")
      
      self.ns.db.executesql("CREATE INDEX address_nervatype_idx ON address (nervatype, ref_id)")
      self.ns.db.executesql("CREATE INDEX address_deleted_idx ON address (deleted)")
      
      self.ns.db.executesql("CREATE INDEX contact_nervatype_idx ON contact (nervatype, ref_id)")
      self.ns.db.executesql("CREATE INDEX contact_deleted_idx ON contact (deleted)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX event_calnumber_idx ON event (calnumber)")
      self.ns.db.executesql("CREATE INDEX event_fromdate_idx ON event (fromdate)")
      self.ns.db.executesql("CREATE INDEX event_eventgroup_idx ON event (eventgroup)")
      self.ns.db.executesql("CREATE INDEX event_nervatype_idx ON event (nervatype)")
      self.ns.db.executesql("CREATE INDEX event_ref_idx ON event (ref_id)")
      self.ns.db.executesql("CREATE INDEX event_deleted_idx ON event (deleted)")
      self.ns.db.executesql("CREATE INDEX event_uid_idx ON event (uid)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX customer_custnumber_idx ON customer (custnumber)")
      self.ns.db.executesql("CREATE INDEX customer_custtype_idx ON customer (custtype)")
      self.ns.db.executesql("CREATE INDEX customer_inactive_idx ON customer (inactive)")
      self.ns.db.executesql("CREATE INDEX customer_deleted_idx ON customer (deleted)")
      self.ns.db.executesql("CREATE INDEX customer_custname_idx ON customer (custname)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX project_pronumber_idx ON project (pronumber)")
      self.ns.db.executesql("CREATE INDEX project_customer_id_idx ON project (customer_id)")
      self.ns.db.executesql("CREATE INDEX project_inactive_idx ON project (inactive)")
      self.ns.db.executesql("CREATE INDEX project_deleted_idx ON project (deleted)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX currency_curr_idx ON currency (curr)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX place_planumber_idx ON place (planumber)")
      self.ns.db.executesql("CREATE INDEX place_placetype_idx ON place (placetype)")
      self.ns.db.executesql("CREATE INDEX place_deleted_idx ON place (deleted)")
      
      self.ns.db.executesql("CREATE INDEX rate_curr_idx ON rate (curr)")
      self.ns.db.executesql("CREATE INDEX rate_ref_idx ON rate (ratedate, curr, place_id, ratetype)")
      self.ns.db.executesql("CREATE INDEX rate_ratedate_idx ON rate (ratedate)")
      self.ns.db.executesql("CREATE INDEX rate_deleted_idx ON rate (deleted)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX tax_taxcode_idx ON tax (taxcode)")
      self.ns.db.executesql("CREATE INDEX tax_inactive_idx ON tax (inactive)")

      self.ns.db.executesql("CREATE UNIQUE INDEX product_partnumber_idx ON product (partnumber)")
      self.ns.db.executesql("CREATE INDEX product_tax_id_idx ON product (tax_id)")
      self.ns.db.executesql("CREATE INDEX product_inactive_idx ON product (inactive)")
      self.ns.db.executesql("CREATE INDEX product_deleted_idx ON product (deleted)")
      self.ns.db.executesql("CREATE INDEX product_protype_idx ON product (protype)")
      self.ns.db.executesql("CREATE INDEX product_webitem_idx ON product (webitem)")
      
      self.ns.db.executesql("CREATE UNIQUE INDEX tool_serial_idx ON tool (serial)")
      self.ns.db.executesql("CREATE INDEX tool_groups_id_idx ON tool (toolgroup)")
      self.ns.db.executesql("CREATE INDEX tool_inactive_idx ON tool (inactive)")
      self.ns.db.executesql("CREATE INDEX tool_deleted_idx ON tool (deleted)")
      self.ns.db.executesql("CREATE INDEX tool_product_id_idx ON tool (product_id)")
      
      self.ns.db.executesql("CREATE INDEX price_curr_idx ON price (curr)")
      self.ns.db.executesql("CREATE INDEX price_product_id_idx ON price (product_id)")
      self.ns.db.executesql("CREATE INDEX price_validfrom_idx ON price (validfrom)")
      self.ns.db.executesql("CREATE INDEX price_validto_idx ON price (validto)")
      self.ns.db.executesql("CREATE INDEX price_vendor_idx ON price (vendorprice)")
      self.ns.db.executesql("CREATE INDEX price_deleted_idx ON price (deleted)")

      self.ns.db.executesql("CREATE UNIQUE INDEX barcode_code_idx ON barcode (code)")
      self.ns.db.executesql("CREATE INDEX barcode_defcode_idx ON barcode (defcode)")
      self.ns.db.executesql("CREATE INDEX barcode_parts_id_idx ON barcode (product_id)")

      self.ns.db.executesql("CREATE UNIQUE INDEX trans_transnumber_idx ON trans (transnumber)")
      self.ns.db.executesql("CREATE INDEX trans_curr_idx ON trans (curr)")
      self.ns.db.executesql("CREATE INDEX trans_duedate_idx ON trans (duedate)")
      self.ns.db.executesql("CREATE INDEX trans_paidtype_idx ON trans (paidtype)")
      self.ns.db.executesql("CREATE INDEX trans_project_id_idx ON trans (project_id)")
      self.ns.db.executesql("CREATE INDEX trans_employee_id_idx ON trans (employee_id)")
      self.ns.db.executesql("CREATE INDEX trans_cruser_idx ON trans (cruser_id)")
      self.ns.db.executesql("CREATE INDEX trans_customer_idx ON trans (customer_id)")
      self.ns.db.executesql("CREATE INDEX trans_department_idx ON trans (department)")
      self.ns.db.executesql("CREATE INDEX trans_transtate_idx ON trans (transtate)")
      self.ns.db.executesql("CREATE INDEX trans_transdate_idx ON trans (transdate)")
      self.ns.db.executesql("CREATE INDEX trans_crdate_idx ON trans (crdate)")
      self.ns.db.executesql("CREATE INDEX trans_ref_transnumber_idx ON trans (ref_transnumber)")
      self.ns.db.executesql("CREATE INDEX trans_transtype_idx ON trans (transtype)")
      self.ns.db.executesql("CREATE INDEX trans_direction_idx ON trans (direction)")

      self.ns.db.executesql("CREATE INDEX item_product_id_idx ON item (product_id)")
      self.ns.db.executesql("CREATE INDEX item_tax_id_idx ON item (tax_id)")
      self.ns.db.executesql("CREATE INDEX item_trans_id_idx ON item (trans_id)")
      self.ns.db.executesql("CREATE INDEX item_deleted_idx ON item (deleted)")

      self.ns.db.executesql("CREATE INDEX payment_paiddate_idx ON payment (paiddate)")
      self.ns.db.executesql("CREATE INDEX payment_trans_id_idx ON payment (trans_id)")
      self.ns.db.executesql("CREATE INDEX payment_deleted_idx ON payment (deleted)")

      self.ns.db.executesql("CREATE INDEX movement_product_id_idx ON movement (product_id)")
      self.ns.db.executesql("CREATE INDEX movement_tool_id_idx ON movement (tool_id)")
      self.ns.db.executesql("CREATE INDEX movement_shipdate_idx ON movement (shippingdate)")
      self.ns.db.executesql("CREATE INDEX movement_trans_id_idx ON movement (trans_id)")
      self.ns.db.executesql("CREATE INDEX movement_place_id_idx ON movement (place_id)")
      self.ns.db.executesql("CREATE INDEX movement_movetype_idx ON movement (movetype)")
      self.ns.db.executesql("CREATE INDEX movement_deleted_idx ON movement (deleted)")

      self.ns.db.executesql("CREATE INDEX patterns_transtype_idx ON pattern (transtype)")
      self.ns.db.executesql("CREATE INDEX pattern_deleted_idx ON rate (deleted)")

      self.ns.db.executesql("CREATE UNIQUE INDEX zipcatalog_pk_idx ON ui_zipcatalog (country, city, zipcode)")
      self.ns.db.executesql("CREATE INDEX zipcatalog_country_city_idx ON ui_zipcatalog (country, city)")
      self.ns.db.executesql("CREATE INDEX zipcatalog_country_zipcode_idx ON ui_zipcatalog (country, zipcode)")

      self.ns.db.commit()  
      return True
    except Exception, err:
      self.ns.db.rollback()
      self.ns.error_message = err
      return False
  
  def createTable(self, table):
    query = self.ns.db._adapter.create_table(table,migrate=False,fake_migrate=False)
    self.ns.db._adapter.create_sequence_and_triggers(query,table)
    self.ns.db.commit()
                   
  def defineTable(self, create=False):
    try:
      self.ns.db._migrate_enabled = False
      if create:
        self.dropTables()
        
      table = self.ns.db.define_table('groups',
        Field('id', readable=False, writable=False),
        Field('groupname', type='string', length=150, required=True, notnull=True),
        Field('groupvalue', type='string', length=150, required=True, notnull=True, label=self.ns.T('Group')),
        Field('description', type='text', label=self.ns.T('Description')),
        Field('inactive', type='integer', default=0, notnull=True, label=self.ns.T('Inactive'), 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull = True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))  
      if self.ns.engine in("mssql"):
        table.description.type = 'string'
        table.description.length = 'max'
      if create:
        self.createTable(table)
      
      table = self.ns.db.define_table('ui_applview',
        Field('id', readable=False, writable=False),
        Field('viewname', type='string', length=150, required=True, notnull=True, unique=True),
        Field('sqlstr', type='text', required=True, notnull=True),
        Field('inistr', type='text'),
        Field('menu', type='string', length=150),
        Field('menuitem', type='string', length=150),
        Field('parentview', type='string', length=150, required=True, notnull=True),
        Field('orderby', type='integer', default=0, required=True, notnull=True))
      if self.ns.engine in("mssql"):
        table.sqlstr.type = 'string'
        table.sqlstr.length = 'max'
        table.inistr.type = 'string'
        table.inistr.length = 'max'
      if create:
        self.createTable(table)
      
      table = self.ns.db.define_table('ui_language',
        Field('id', readable=False, writable=False),
        Field('lang', type='string', length=2, required=True, notnull=True, unique=True),
        Field('description', type='string', length=150))
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('ui_locale',
        Field('id', readable=False, writable=False),
        Field('country', type='string', length=150, required=True, notnull=True, unique=True),
        Field('lang', type='string', length=2, required=True, notnull=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.ui_language), self.ns.db.ui_language.lang, '%(lang)s')),
        Field('description', type='text'))
      if self.ns.engine in("mssql"):
        table.description.type = 'string'
        table.description.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('ui_menu',
        Field('id', readable=False, writable=False),
        Field('menukey', type='string', length=255, required=True, notnull=True, unique=True),
        Field('description', type='string', length=255, required=True, notnull=True),
        Field('modul', type='string', length=255),
        Field('icon', type='string', length=255),
        Field('funcname', type='string', length=255, required=True, notnull=True),
        Field('url', type='integer', default=0, required=True, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('address', type='text'))
      if self.ns.engine in("mssql"):
        table.address.type = 'string'
        table.address.length = 'max'
      if create:
        self.createTable(table)
     
      table = self.ns.db.define_table('ui_menufields',
        Field('id', readable=False, writable=False),
        Field('menu_id', self.ns.db.ui_menu, ondelete='CASCADE', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db, self.ns.db.ui_menu.id, '%(menukey)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "ui_menu", value, "menukey")),
        Field('fieldname', type='string', length=150, required=True, notnull=True, label=self.ns.T('Name')),
        Field('description', type='string', length=255, required=True, notnull=True),
        Field('fieldtype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, label=self.ns.T('Type'), 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('fieldtype')&self.ns.db.groups.groupvalue.belongs(('bool','date','integer','float','string'))), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('orderby', type='integer', default=0, required=True, notnull=True, label=self.ns.T('Order'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(int(value)," ","."), _align="right", _width="100%")))
      if self.ns.engine in("mssql"):
        table.fieldtype.ondelete = "NO ACTION"
      if create:
        self.createTable(table)
      
      table = self.ns.db.define_table('ui_message',
        Field('id', readable=False, writable=False),
        Field('secname', type='string', length=150, required=True, notnull=True),
        Field('fieldname', type='string', length=150, required=True, notnull=True),
        Field('lang', type='string', length=2, required=True, notnull=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.ui_language), self.ns.db.ui_language.lang, '%(lang)s')),
        Field('msg', type='text', required=True, notnull=True))
      if self.ns.engine in("mssql"):
        table.msg.type = 'string'
        table.msg.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('ui_numtotext',
        Field('id', readable=False, writable=False),
        Field('lang', type='string', length=2, required=True, notnull=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.ui_language), self.ns.db.ui_language.lang, '%(lang)s')),
        Field('digi', type='integer', default=0, required=True, notnull=True),
        Field('deci', type='integer', default=0, required=True, notnull=True),
        Field('number_str', type='string', length=150),
        Field('number_str2', type='string', length=150))
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('ui_report',
        Field('id', readable=False, writable=False),                   
        Field('reportkey', type='string', length=255, required=True, notnull=True, unique=True),
        Field('nervatype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('nervatype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('transtype', self.ns.db.groups, ondelete='RESTRICT', 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('transtype')), self.ns.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('direction', self.ns.db.groups, ondelete='RESTRICT', 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('direction')), self.ns.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('repname', type='string', length=255, required=True, notnull=True, label=self.ns.T('Report')),
        Field('description', type='string', length=255, label=self.ns.T('Description')),
        Field('label', type='string', length=255, label=self.ns.T('Group')),
        Field('filetype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('filetype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('report', type='text'))
      if self.ns.engine in("mssql"):
        table.nervatype.ondelete = "NO ACTION"
        table.transtype.ondelete = "NO ACTION"
        table.direction.ondelete = "NO ACTION"
        table.filetype.ondelete = "NO ACTION"
        table.report.type = 'string'
        table.report.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('ui_reportfields',
        Field('id', readable=False, writable=False),
        Field('report_id', self.ns.db.ui_report, ondelete='CASCADE', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db, self.ns.db.ui_report.id, '%(reportkey)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "ui_report", value, "reportkey")),
        Field('fieldname', type='string', length=150, required=True, notnull=True),
        Field('fieldtype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('fieldtype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('wheretype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('wheretype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('description', type='string', length=255),
        Field('orderby', type='integer', default=0, notnull=True, required=True),
        Field('sqlstr', type='text'),
        Field('parameter', type='integer', default=0, notnull=True, required=True,
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('dataset', type='string', length=150),
        Field('defvalue', type='string', length=255),
        Field('valuelist', type='text'))
      if self.ns.engine in("mssql"):
        table.fieldtype.ondelete = "NO ACTION"
        table.wheretype.ondelete = "NO ACTION"
        table.sqlstr.type = 'string'
        table.sqlstr.length = 'max'
        table.valuelist.type = 'string'
        table.valuelist.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('ui_reportsources',
        Field('id', readable=False, writable=False),
        Field('report_id', self.ns.db.ui_report, ondelete='CASCADE', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db, self.ns.db.ui_report.id, '%(reportkey)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "ui_report", value, "reportkey")),
        Field('dataset', type='string', length=150, notnull=True, required=True),
        Field('sqlstr', type='text'))
      if self.ns.engine in("mssql"):
        table.sqlstr.type = 'string'
        table.sqlstr.length = 'max'
      if create:
        self.createTable(table)
      
      table = self.ns.db.define_table('ui_groupinput',
        Field('id', readable=False, writable=False),
        Field('groups_id', self.ns.db.groups, ondelete='CASCADE', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('usergroup') & (self.ns.db.groups.deleted==0)), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('formname', type='string', length=150, required=True, notnull=True),
        Field('contname', type='string', length=150, required=True, notnull=True),
        Field('isenabled', type='integer', default=0, required=True, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('isvisibled', type='integer', default=0, required=True, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        self.createTable(table)
      
      table = self.ns.db.define_table('ui_viewfields',
        Field('id', readable=False, writable=False),
        Field('viewname', type='string', length=150, notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.ui_applview), self.ns.db.ui_applview.viewname, '%(viewname)s')),
        Field('fieldname', type='string', length=150, required=True, notnull=True),
        Field('fieldtype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('fieldtype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('wheretype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('wheretype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('orderby', type='integer', default=0, notnull=True, required=True),
        Field('sqlstr', type='text'),
        Field('aggretype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('aggretype')), self.ns.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")))
      if self.ns.engine in("mssql"):
        table.fieldtype.ondelete = "NO ACTION"
        table.wheretype.ondelete = "NO ACTION"
        table.aggretype.ondelete = "NO ACTION"
        table.sqlstr.type = 'string'
        table.sqlstr.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('employee',
        Field('id', readable=False, writable=False),
        Field('empnumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.ns.T('Employee No.')),
        Field('username', type='string', length=150, unique=True,
              requires=IS_EMPTY_OR(IS_NOT_IN_DB(self.ns.db, "employee.username"))),
        Field('usergroup', self.ns.db.groups, ondelete='RESTRICT', notnull=True, label=self.ns.T('Usergroup'), 
              requires = IS_IN_DB(self.ns.db((self.ns.db.groups.groupname.like('usergroup'))&(self.ns.db.groups.deleted==0)), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('startdate', type='date', label=self.ns.T('Start Date')),
        Field('enddate', type='date', label=self.ns.T('End Date')),
        Field('department', self.ns.db.groups, ondelete='RESTRICT', required=False, 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db((self.ns.db.groups.groupname.like('department'))&(self.ns.db.groups.deleted==0)), self.ns.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        #Field('password', type='password', length=512, readable=False, writable=False, 
        #      requires = [IS_EMPTY_OR(IS_STRONG(), CRYPT())]),
        Field('password', type='password', length=512, readable=False, writable=False),
        Field('registration_key', length=512, writable=False, readable=False, default=''),
        Field('inactive', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.usergroup.ondelete = "NO ACTION"
        table.department.ondelete = "NO ACTION"
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('ui_printqueue',
        Field('id', readable=False, writable=False),
        Field('nervatype', self.ns.db.groups, ondelete='CASCADE', notnull=True, required=True, label=self.ns.T('Doc.type'), 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('nervatype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.get_nervatype_name(value,row.ref_id)),
        Field('ref_id', type='integer', notnull=True, required=True, label=self.ns.T('Doc.No./Description'),
              represent = lambda value,row: A(SPAN(str(self.ns.valid.show_refnumber("refnumber", self.ns.db.groups(id=row.nervatype).groupvalue, row.ref_id))),
                     _href=URL(r=self.ns.request, f=str(self.ns.valid.show_refnumber("href", self.ns.db.groups(id=row.nervatype).groupvalue, row.ref_id))), 
                     _target="_blank")),
        Field('qty', type='double', default=0, notnull=True, required=True, label=self.ns.T('Copies'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('employee_id', self.ns.db.employee, ondelete='CASCADE', notnull=True, required=True, label=self.ns.T('Employee'), 
              requires = IS_IN_DB(self.ns.db, self.ns.db.employee.id, '%(username)s'),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "employee", value, "empnumber")),
                     _href=URL(r=self.ns.request, f="frm_employee/view/employee/"+str(value)), _target="_blank")),
        Field('report_id', self.ns.db.ui_report, ondelete='CASCADE', notnull=True, required=True, label=self.ns.T('Template'), 
              requires = IS_IN_DB(self.ns.db, self.ns.db.ui_report.id, '%(reportkey)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "ui_report", value, "repname")),
        Field('crdate', type='date', notnull=True, required=True, label=self.ns.T('Date'), default=datetime.datetime.now().date()))
      if self.ns.engine in("mssql"):
        table.employee_id.ondelete = "NO ACTION"
        table.report_id.ondelete = "NO ACTION"
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('ui_filter',
        Field('id', readable=False, writable=False),
        Field('employee_id', self.ns.db.employee, ondelete='CASCADE', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db, self.ns.db.employee.id, '%(username)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "employee", value, "username")),
        Field('parentview', type='string', length=150, notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.ui_applview), self.ns.db.ui_applview.viewname, '%(viewname)s')),
        Field('viewname', type='string', length=150, notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.ui_applview), self.ns.db.ui_applview.viewname, '%(viewname)s')),
        Field('fieldname', type='string', length=150, required=True, notnull=True),
        Field('ftype', type='string', length=150, required=True, notnull=True),
        Field('fvalue', type='text'))
      if self.ns.engine in("mssql"):
        table.fvalue.type = 'string'
        table.fvalue.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('ui_userconfig',
        Field('id', readable=False, writable=False),
        Field('employee_id', self.ns.db.employee, ondelete='CASCADE', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db, self.ns.db.employee.id, '%(username)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "employee", value, "username")),
        Field('section', type='string', length=150),
        Field('cfgroup', type='string', length=150, notnull=True, required=True),
        Field('cfname', type='string', length=150, notnull=True, required=True),
        Field('cfvalue', type='text'),
        Field('orderby', type='integer', default=0, notnull=True, required=True))
      if self.ns.engine in("mssql"):
        table.cfvalue.type = 'string'
        table.cfvalue.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('link',
        Field('id', readable=False, writable=False),
        Field('nervatype_1', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('nervatype')), self.ns.db.groups.id, '%(groupvalue)s')),
        Field('ref_id_1', type='integer', notnull=True, required=True),
        Field('nervatype_2', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('nervatype')), self.ns.db.groups.id, '%(groupvalue)s')),
        Field('ref_id_2', type='integer', notnull=True, required=True),
        Field('linktype', type='integer', default=0, notnull=True),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.nervatype_1.ondelete = "NO ACTION"
        table.nervatype_2.ondelete = "NO ACTION"
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('ui_audit',
        Field('id', readable=False, writable=False),
        Field('usergroup', self.ns.db.groups, ondelete='CASCADE', notnull=True, 
              required=True, requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('usergroup') & (self.ns.db.groups.deleted==0)), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('nervatype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, label=self.ns.T('Type'), 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('nervatype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('subtype', type='integer', 
              represent = lambda value,row: self.ns.valid.get_audit_subtype(row, value)),
        Field('inputfilter', self.ns.db.groups, ondelete='RESTRICT', notnull=True, label=self.ns.T('Filter'), 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('inputfilter')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('supervisor', type='integer', default=1, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.nervatype.ondelete = "NO ACTION"
        table.inputfilter.ondelete = "NO ACTION"
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('deffield',
        Field('id', readable=False, writable=False),
        Field('fieldname', type='string', length=150, required=True, notnull=True, unique=True),
        Field('nervatype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('nervatype')
                & self.ns.db.groups.groupvalue.belongs(('address', 'barcode', 'contact', 'currency', 'customer', 'employee', 'event', 'item', 'link', 
                                                     'log', 'movement', 'payment', 'price', 'place', 'product', 'project', 'rate', 'tax',
                                                     'tool', 'trans', 'setting'))), 
                self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('subtype', self.ns.db.groups, ondelete='RESTRICT', 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db, self.ns.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('fieldtype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('fieldtype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('description', type='text', notnull=True),
        Field('valuelist', type='text'),
        Field('addnew', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('visible', type='integer', default=1, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('readonly', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.nervatype.ondelete = "NO ACTION"
        table.subtype.ondelete = "NO ACTION"
        table.fieldtype.ondelete = "NO ACTION"
        table.description.type = 'string'
        table.description.length = 'max'
        table.valuelist.type = 'string'
        table.valuelist.length = 'max'
      if create:
        self.createTable(table) 

      table = self.ns.db.define_table('fieldvalue',
        Field('id', readable=False, writable=False),
        Field('fieldname', type='string', length=150, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.deffield), self.ns.db.deffield.fieldname, '%(description)s (%(fieldname)s)')),
        Field('ref_id', type='integer'),
        Field('value', type='text', 
              requires = self.ns.valid.check_fieldvalue(self.ns, self.ns.request.vars),
              represent = lambda value,row: self.ns.valid.show_fieldvalue(row["fieldvalue"])),
        Field('notes', type='text', label=self.ns.T('Other data')),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.value.type = 'string'
        table.value.length = 'max'
        table.notes.type = 'string'
        table.notes.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('log',
        Field('id', readable=False, writable=False),
        Field('employee_id', self.ns.db.employee, ondelete='RESTRICT', notnull=True, required=True, label=self.ns.T('Employee'),
              requires = IS_IN_DB(self.ns.db, self.ns.db.employee.id, '%(username)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "employee", value, "username")),
        Field('crdate', type='datetime', notnull=True, required=True, default=datetime.datetime.now(), label=self.ns.T('Date')),
        Field('nervatype', self.ns.db.groups, ondelete='RESTRICT', label=self.ns.T('Ref.type'),
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('nervatype')
                & self.ns.db.groups.groupvalue.belongs(('address', 'barcode', 'contact', 'currency', 'customer', 'employee', 'deffield',
                                                     'event', 'groups', 'item', 'link', 
                                                     'movement', 'payment', 'price', 'place', 'product', 'project', 'rate', 'tax',
                                                     'tool', 'trans', 'setting'))), 
                self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('ref_id', type='integer', label=self.ns.T('Doc.No./Description'),
              represent = lambda value,row: A(SPAN(str(self.ns.valid.show_refnumber("refnumber", self.ns.db.groups(id=row.nervatype).groupvalue, row.ref_id, use_deleted=True))),
                     _href=URL(r=self.ns.request, f=str(self.ns.valid.show_refnumber("href", self.ns.db.groups(id=row.nervatype).groupvalue, row.ref_id, use_deleted=True))), _target="_blank")),
        Field('logstate', self.ns.db.groups, ondelete='CASCADE', notnull=True, required=True, label=self.ns.T('State'),
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('logstate')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")))
      if self.ns.engine in("mssql"):
        table.nervatype.ondelete = "NO ACTION"
        table.employee_id.ondelete = "NO ACTION"
      if create:
        self.createTable(table)
     
      table = self.ns.db.define_table('numberdef',
        Field('id', readable=False, writable=False),
        Field('numberkey', type='string', length=150, required=True, notnull=True, unique=True, label=self.ns.T('Code')),
        Field('prefix', type='string', length=150, label=self.ns.T('Prefix')),
        Field('curvalue', type='integer', default=0, notnull=True, label=self.ns.T('Value'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(int(value)," ","."), _align="right", _width="100%")),
        Field('isyear', type='integer', default=1, notnull=True, label=self.ns.T('Year'), 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('sep', type='string', length=1, default="/",
              represent = lambda value,row: DIV(value, _align="center", _width="100%")),
        Field('len', type='integer', default=5, notnull=True,
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(int(value)," ","."), _align="right", _width="100%")),
        Field('description', type='text'),
        Field('visible', type='integer', default=1, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('readonly', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('orderby', type='integer', default=0, notnull=True))
      if self.ns.engine in("mssql"):
        table.description.type = 'string'
        table.description.length = 'max'
      if create:
        self.createTable(table)
      
      table = self.ns.db.define_table('address',
        Field('id', readable=False, writable=False),
        Field('nervatype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('nervatype')
                                          & self.ns.db.groups.groupvalue.belongs(('customer', 'employee', 'event', 'place', 'product', 'project', 'tool', 'trans'))
                                  ), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('ref_id', type='integer', notnull=True),
        Field('country', type='string', length=255, label=self.ns.T('Country')),
        Field('state', type='string', length=255, label=self.ns.T('State')),
        Field('zipcode', type='string', length=150, label=self.ns.T('Zipcode')),
        Field('city', type='string', length=255, label=self.ns.T('City')),
        Field('street', type='text', label=self.ns.T('Street')),
        Field('notes', type='text', label=self.ns.T('Comment')),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.nervatype.ondelete = "NO ACTION"
        table.street.type = 'string'
        table.street.length = 'max'
        table.notes.type = 'string'
        table.notes.length = 'max'
      if create:
        self.createTable(table)
      
      table = self.ns.db.define_table('contact',
        Field('id', readable=False, writable=False),
        Field('nervatype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('nervatype')
                                          & self.ns.db.groups.groupvalue.belongs(('customer', 'employee', 'event', 'place', 'product', 'project', 'tool', 'trans'))
                                 ), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('ref_id', type='integer', notnull=True, required=True),
        Field('firstname', type='string', length=255, label=self.ns.T('Firstname')),
        Field('surname', type='string', length=255, label=self.ns.T('Surname')),
        Field('status', type='string', length=255, label=self.ns.T('Status')),
        Field('phone', type='string', length=255, label=self.ns.T('Phone')),
        Field('fax', type='string', length=255, label=self.ns.T('Fax')),
        Field('mobil', type='string', length=255, label=self.ns.T('Mobil')),
        Field('email', type='string', length=255, label=self.ns.T('Email'), 
              requires = IS_EMPTY_OR(IS_EMAIL(error_message=self.ns.T('invalid email!')))),
        Field('notes', type='text', label=self.ns.T('Comment')),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.nervatype.ondelete = "NO ACTION"
        table.notes.type = 'string'
        table.notes.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('event',
        Field('id', readable=False, writable=False),
        Field('calnumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.ns.T('Event No.')),
        Field('nervatype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('nervatype')
                & self.ns.db.groups.groupvalue.belongs(('customer', 'employee', 'place', 'product', 'project', 'tool', 'trans'))
                ), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('ref_id', type='integer', notnull=True),
        Field('uid', type='string', length=255, label=self.ns.T('UID')),
        Field('eventgroup', self.ns.db.groups, ondelete='CASCADE', label=self.ns.T('Group'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('eventgroup') & (self.ns.db.groups.deleted==0)), self.ns.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('fromdate', type='datetime', label=self.ns.T('Start Date')),
        Field('todate', type='datetime', label=self.ns.T('End Date')),
        Field('subject', type='string', length=255, label=self.ns.T('Subject')),
        Field('place', type='string', length=255, label=self.ns.T('Place')),
        Field('description', type='text', label=self.ns.T('Description')),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.nervatype.ondelete = "NO ACTION"
        table.description.type = 'string'
        table.description.length = 'max'
      if create:
        self.createTable(table)
         
      table = self.ns.db.define_table('customer',
        Field('id', readable=False, writable=False),
        Field('custtype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, label=self.ns.T('Customer Type'), 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('custtype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('custnumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.ns.T('Customer No.')),
        Field('custname', type='string', length=255, notnull=True, label=self.ns.T('Customer Name')),
        Field('taxnumber', type='string', length=255, label=self.ns.T('Taxnumber')),
        Field('account', type='string', length=255, label=self.ns.T('Account')),
        Field('notax', type='integer', default=0, notnull=True, label=self.ns.T('Tax-free'), 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('terms', type='integer', default=0, notnull=True, label=self.ns.T('Payment per.'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(int(value)," ","."), _align="right", _width="100%")),
        Field('creditlimit', type='double', default=0, notnull=True, label=self.ns.T('Credit line'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('discount', type='double', default=0, notnull=True, label=self.ns.T('Discount%'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('notes', type='text', label=self.ns.T('Comment')),
        Field('inactive', type='integer', default=0, notnull=True, label=self.ns.T('Inactive'),
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_integrity_boolean(self.ns,'customer',self.ns.request.vars.id), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.custtype.ondelete = "NO ACTION"
        table.notes.type = 'string'
        table.notes.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('project',
        Field('id', readable=False, writable=False),
        Field('pronumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.ns.T('Project No.')),
        Field('description', type='string', length=255, label=self.ns.T('Project')),
        Field('customer_id', self.ns.db.customer, ondelete='RESTRICT', label=self.ns.T('Customer'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db, self.ns.db.customer.id, '%(custname)s (%(custnumber)s)')),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "customer", value, "custname")),
                     _href=URL(r=self.ns.request, f="frm_customer/view/customer/"+str(value)), _target="_blank")),
        Field('startdate', type='date', label=self.ns.T('Start Date')),
        Field('enddate', type='date', label=self.ns.T('End Date')),
        Field('notes', type='text'),
        Field('inactive', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.customer_id.ondelete = "CASCADE"
        table.notes.type = 'string'
        table.notes.length = 'max'
      if create:
        self.createTable(table)
      
      table = self.ns.db.define_table('currency',
        Field('id', readable=False, writable=False),
        Field('curr', type='string', length=3, required=True, notnull=True, unique=True),
        Field('description', type='string', length=255),
        Field('digit', type='integer', default=0, notnull=True,
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(int(value)," ","."), _align="right", _width="100%")),
        Field('defrate', type='double', default=0, notnull=True, label=self.ns.T('Def.Rate'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('cround', type='integer', default=0, notnull=True, label=self.ns.T('Round'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(int(value)," ","."), _align="right", _width="100%")))
      if create:
        self.createTable(table)
      
      table = self.ns.db.define_table('place',
        Field('id', readable=False, writable=False),
        Field('planumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.ns.T('Place No.')),
        Field('placetype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, label=self.ns.T('Type'), 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('placetype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('description', type='string', length=255, notnull=True),
        Field('place_id', 'reference place', ondelete='RESTRICT', label=self.ns.T('Ref.No.')),
        Field('curr', type='string', length=3, 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db(self.ns.db.currency), self.ns.db.currency.curr, '%(curr)s'))),
        Field('storetype', self.ns.db.groups, ondelete='RESTRICT', label=self.ns.T('StoreType'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('storetype')), self.ns.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('defplace', type='integer', default=0, notnull=True, label=self.ns.T('Default'), 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('notes', type='text', label=self.ns.T('Comment')),
        Field('inactive', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      self.ns.db.place.place_id.requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db, self.ns.db.place.id, '%(description)s (%(planumber)s)'))
      self.ns.db.place.place_id.represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "place", value, "planumber")
      if self.ns.engine in("mssql"):
        table.placetype.ondelete = "NO ACTION"
        table.place_id.ondelete = "NO ACTION"
        table.storetype.ondelete = "NO ACTION"
        table.notes.type = 'string'
        table.notes.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('rate',
        Field('id', readable=False, writable=False),
        Field('ratetype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, required=True, label=self.ns.T('Type'), 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('ratetype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('ratedate', type='date', notnull=True, required=True, label=self.ns.T('Date')),
        Field('curr', type='string', length=3, required=True, notnull=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.currency), self.ns.db.currency.curr, '%(curr)s')),
        Field('place_id', self.ns.db.place, ondelete='RESTRICT', label=self.ns.T('Account No.'),
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db((self.ns.db.place.deleted==0)&self.ns.db.place.placetype.belongs(
                           self.ns.db((self.ns.db.groups.groupname=='placetype')&(self.ns.db.groups.groupvalue=='bank')
                                      ).select(self.ns.db.groups.id))), self.ns.db.place.id, '%(planumber)s (%(description)s)')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "place", value, "planumber")),
        Field('rategroup', self.ns.db.groups, ondelete='RESTRICT', label=self.ns.T('Group'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db((self.ns.db.groups.deleted==0)&self.ns.db.groups.groupname.like('rategroup')), self.ns.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('ratevalue', type='double', default=0, notnull=True, label=self.ns.T('Value'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.ratetype.ondelete = "NO ACTION"
        table.place_id.ondelete = "CASCADE"
        table.rategroup.ondelete = "NO ACTION"
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('tax',
        Field('id', readable=False, writable=False),
        Field('taxcode', type='string', length=150, required=True, notnull=True, unique=True),                
        Field('description', type='string', length=255, notnull=True),
        Field('rate', type='double', default=0, notnull=True,
              requires = IS_FLOAT_IN_RANGE(0, 1, dot=".", error_message=self.ns.T('Valid range: 0-1')),
              represent = lambda value,row: DIV(str(float(value)*100)+"%", _align="right", _width="100%")),
        Field('inactive', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('product',
        Field('id', readable=False, writable=False),
        Field('partnumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.ns.T('Product No.')),
        Field('protype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, label=self.ns.T('Product type'), 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('protype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('description', type='string', length=255, notnull=True, label=self.ns.T('Product name')),
        Field('unit', type='string', length=150, notnull=True),
        Field('tax_id', self.ns.db.tax, ondelete='RESTRICT', label=self.ns.T('Tax'), 
              requires = IS_IN_DB(self.ns.db, self.ns.db.tax.id, '%(taxcode)s'),
              represent = lambda value,row: DIV(self.ns.valid.show_refnumber("refnumber", "tax", value, "taxcode"), _align="right", _width="100%")),
        Field('notes', type='text'),
        Field('webitem', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('inactive', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.protype.ondelete = "NO ACTION"
        table.tax_id.ondelete = "CASCADE"
        table.notes.type = 'string'
        table.notes.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('tool',
        Field('id', readable=False, writable=False),
        Field('serial', type='string', length=150, required=True, notnull=True, unique=True),
        Field('description', type='text'),
        Field('product_id', self.ns.db.product, ondelete='RESTRICT', label=self.ns.T('Product'),
              requires = IS_IN_DB(self.ns.db, self.ns.db.product.id, '%(description)s (%(partnumber)s)'),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "product", value, "description")),
                     _href=URL(r=self.ns.request, f="frm_product/view/product/"+str(value)), _target="_blank")),
        Field('toolgroup', self.ns.db.groups, ondelete='RESTRICT', label=self.ns.T('Group'),
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('toolgroup') & (self.ns.db.groups.deleted==0)), self.ns.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('notes', type='text'),
        Field('inactive', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.product_id.ondelete = "CASCADE"
        table.toolgroup.ondelete = "NO ACTION"
        table.description.type = 'string'
        table.description.length = 'max'
        table.notes.type = 'string'
        table.notes.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('price',
        Field('id', readable=False, writable=False),
        Field('product_id', self.ns.db.product, ondelete='CASCADE', label=self.ns.T('Product'), 
              requires = IS_IN_DB(self.ns.db, self.ns.db.product.id, '%(description)s (%(partnumber)s)'),
              represent = lambda value,row: A(SPAN(self.ns.db.product(id=int(value))["description"]),
                     _href=URL(r=self.ns.request, f="frm_product/view/product/"+str(value)), _target="_blank")),
        Field('validfrom', type='date', notnull=True, label=self.ns.T('Start Date')),
        Field('validto', type='date', label=self.ns.T('End Date')),
        Field('curr', type='string', length=3, notnull=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.currency), self.ns.db.currency.curr, '%(curr)s')),
        Field('qty', type='double', default=0,
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('pricevalue', type='double', default=0, notnull=True, label=self.ns.T('Price'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('discount', type='double',
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('calcmode', self.ns.db.groups, ondelete='RESTRICT', notnull=True, label=self.ns.T('Mode'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('calcmode')), self.ns.db.groups.id, '%(description)s')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "description")),
        Field('vendorprice', type='integer', default=0, notnull=True, label=self.ns.T('Vendor'), 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.calcmode.ondelete = "NO ACTION"
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('barcode',
        Field('id', readable=False, writable=False),
        Field('code', type='string', length=255, required=True, notnull=True, unique=True),
        Field('product_id', self.ns.db.product, ondelete='CASCADE', label=self.ns.T('Product'),
              requires = IS_IN_DB(self.ns.db, self.ns.db.product.id, '%(description)s (%(partnumber)s)'),
              represent = lambda value,row: A(SPAN(self.ns.db.product(id=int(value))["description"]),
                     _href=URL(r=self.ns.request, f="frm_product/view/product/"+str(value)), _target="_blank")),
        Field('description', type='text'),
        Field('barcodetype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, label=self.ns.T('Type'), 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('barcodetype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('qty', type='double', default=0, notnull=True,
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('defcode', type='integer', default=0, notnull=True, label=self.ns.T('Default'), 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.barcodetype.ondelete = "NO ACTION"
        table.description.type = 'string'
        table.description.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('trans',
        Field('id', readable=False, writable=False),
        Field('transnumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.ns.T('Doc.No.')),
        Field('transtype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, label=self.ns.T('Doc.Type'), 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('transtype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('direction', self.ns.db.groups, ondelete='RESTRICT', notnull=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('direction')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('ref_transnumber', type='string', length=150, label=self.ns.T('Ref.No.')),
        Field('crdate', type='date', notnull=True, label=self.ns.T('Creation')),
        Field('transdate', type='date', notnull=True),
        Field('duedate', type='datetime'),
        Field('customer_id', self.ns.db.customer, ondelete='RESTRICT', label=self.ns.T('Customer'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db, self.ns.db.customer.id, '%(custname)s (%(custnumber)s)')),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "customer", value, "custname")),
                     _href=URL(r=self.ns.request, f="frm_customer/view/customer/"+str(value)), _target="_blank")),
        Field('employee_id', self.ns.db.employee, ondelete='RESTRICT', label=self.ns.T('Employee'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db, self.ns.db.employee.id, '%(empnumber)s')),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "employee", value, "empnumber")),
                     _href=URL(r=self.ns.request, f="frm_employee/view/employee/"+str(value)), _target="_blank")),
        Field('department', self.ns.db.groups, ondelete='RESTRICT', 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('department') & (self.ns.db.groups.deleted==0)), self.ns.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('project_id', self.ns.db.project, ondelete='RESTRICT', label=self.ns.T('Project'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db, self.ns.db.project.id, '%(pronumber)s')),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "project", value, "pronumber")),
                     _href=URL(r=self.ns.request, f="frm_project/view/project/"+str(value)), _target="_blank")),
        Field('place_id', self.ns.db.place, ondelete='RESTRICT', label=self.ns.T('Place'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db, self.ns.db.place.id, '%(description)s (%(planumber)s)')),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "place", value, "planumber")),
                     _href=URL(r=self.ns.request, f="frm_place/view/place/"+str(value)), _target="_blank")),
        Field('paidtype', self.ns.db.groups, ondelete='RESTRICT', label=self.ns.T('Payment'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('paidtype') & (self.ns.db.groups.deleted==0)), self.ns.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('curr', type='string', length=3, 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db(self.ns.db.currency), self.ns.db.currency.curr, '%(curr)s'))),
        Field('notax', type='integer', default=0, notnull=True, requires=self.ns.valid.check_boolean(self.ns.T), widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('paid', type='integer', default=0, notnull=True, requires=self.ns.valid.check_boolean(self.ns.T), widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('acrate', type='double', default=0, label=self.ns.T('Acc.Rate'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('notes', type='text', label=self.ns.T('Comment')),
        Field('intnotes', type='text', label=self.ns.T('Internal notes')),
        Field('fnote', type='text'),
        Field('transtate', self.ns.db.groups, ondelete='RESTRICT', notnull=True, label=self.ns.T('State'),
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('transtate')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('closed', type='integer', default=0, notnull=True, requires=self.ns.valid.check_boolean(self.ns.T), widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, requires=self.ns.valid.check_boolean(self.ns.T), widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('cruser_id', self.ns.db.employee, ondelete='RESTRICT', 
              requires = IS_IN_DB(self.ns.db, self.ns.db.employee.id, '%(username)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "employee", value, "username")))
      if self.ns.engine in("mssql"):
        table.transtype.ondelete = "NO ACTION"
        table.direction.ondelete = "NO ACTION"
        table.customer_id.ondelete = "NO ACTION"
        table.employee_id.ondelete = "NO ACTION"
        table.department.ondelete = "NO ACTION"
        table.project_id.ondelete = "NO ACTION"
        table.place_id.ondelete = "NO ACTION"
        table.paidtype.ondelete = "NO ACTION"
        table.transtate.ondelete = "NO ACTION"
        table.cruser_id.ondelete = "NO ACTION"
        table.notes.type = 'string'
        table.notes.length = 'max'
        table.intnotes.type = 'string'
        table.intnotes.length = 'max'
        table.fnote.type = 'string'
        table.fnote.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('item',
        Field('id', readable=False, writable=False),
        Field('trans_id', self.ns.db.trans, ondelete='CASCADE', label=self.ns.T('Doc.No.'),
              requires = IS_IN_DB(self.ns.db, self.ns.db.trans.id, '%(transnumber)s'),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "trans", value, "transnumber")),
                     _href=URL(r=self.ns.request, f="frm_trans/view/trans/"+str(value)), _target="_blank")),
        Field('product_id', self.ns.db.product, ondelete='CASCADE', label=self.ns.T('Product'), 
              requires = IS_IN_DB(self.ns.db, self.ns.db.product.id, '%(description)s (%(partnumber)s)'),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "product", value, "description")),
                     _href=URL(r=self.ns.request, f="frm_product/view/product/"+str(value)), _target="_blank")),
        Field('unit', type='string', length=150, notnull=True),
        Field('qty', type='double', default=0, notnull=True,
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('fxprice', type='double', default=0, notnull=True, label=self.ns.T('UnitPrice'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('netamount', type='double', default=0, notnull=True, label=self.ns.T('NetAmount'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('discount', type='double', default=0, notnull=True,
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('tax_id', self.ns.db.tax, ondelete='CASCADE', label=self.ns.T('TaxRate'), 
              requires = IS_IN_DB(self.ns.db, self.ns.db.tax.id, '%(taxcode)s'),
              represent = lambda value,row: DIV(self.ns.valid.show_refnumber("refnumber", "tax", value, "taxcode"), _align="right", _width="100%")),
        Field('vatamount', type='double', default=0, notnull=True, label=self.ns.T('VAT'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('amount', type='double', default=0, notnull=True,
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('description', type='text', notnull=True),
        Field('deposit', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('ownstock', type='double', default=0, notnull=True, label=self.ns.T('OwnStock'),
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('actionprice', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.description.type = 'string'
        table.description.length = 'max'
        table.tax_id.ondelete = "NO ACTION"
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('payment',
        Field('id', readable=False, writable=False),
        Field('trans_id', self.ns.db.trans, ondelete='CASCADE', label=self.ns.T('Doc No.'), 
              requires = IS_IN_DB(self.ns.db, self.ns.db.trans.id, '%(transnumber)s'),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "trans", value, "transnumber")),
                     _href=URL(r=self.ns.request, f="frm_trans/view/trans/"+str(value)), _target="_blank")),
        Field('paiddate', type='date', notnull=True, label=self.ns.T('PaymentDate')),
        Field('amount', type='double', default=0, notnull=True,
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('notes', type='text', label=self.ns.T('Description')),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.notes.type = 'string'
        table.notes.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('movement',
        Field('id', readable=False, writable=False),
        Field('trans_id', self.ns.db.trans, ondelete='CASCADE', label=self.ns.T('Document No.'), 
              requires = IS_IN_DB(self.ns.db, self.ns.db.trans.id, '%(transnumber)s'),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "trans", value, "transnumber")),
                     _href=URL(r=self.ns.request, f="frm_trans/view/trans/"+str(value)), _target="_blank")),
        Field('shippingdate', type='datetime', notnull=True, label=self.ns.T('Shipping Date')),
        Field('movetype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('movetype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('product_id', self.ns.db.product, ondelete='RESTRICT', label=self.ns.T('Product'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db, self.ns.db.product.id, '%(description)s (%(partnumber)s)')),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "product", value, "description")),
                     _href=URL(r=self.ns.request, f="frm_product/view/product/"+str(value)), _target="_blank")),
        Field('tool_id', self.ns.db.tool, ondelete='RESTRICT', label=self.ns.T('Serial'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db, self.ns.db.tool.id, '%(serial)s')),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "tool", value, "serial")),
                     _href=URL(r=self.ns.request, f="frm_tool/view/tool/"+str(value)), _target="_blank")),
        Field('place_id', self.ns.db.place, ondelete='RESTRICT', label=self.ns.T('Place No.'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.ns.db, self.ns.db.place.id, '%(description)s (%(planumber)s)')),
              represent = lambda value,row: A(SPAN(self.ns.valid.show_refnumber("refnumber", "place", value, "planumber")),
                     _href=URL(r=self.ns.request, f="frm_place/view/place/"+str(value)), _target="_blank")),
        Field('qty', type='double', default=0, notnull=True,
              represent = lambda value,row: DIV(self.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")),
        Field('notes', type='text', label=self.ns.T('Batch No.')),
        Field('shared', type='integer', default=0, notnull=True, label=self.ns.T('Not shared'), 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.movetype.ondelete = "NO ACTION"
        table.product_id.ondelete = "NO ACTION"
        table.tool_id.ondelete = "NO ACTION"
        table.place_id.ondelete = "NO ACTION"
        table.notes.type = 'string'
        table.notes.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('pattern',
        Field('id', readable=False, writable=False),
        Field('description', type='string', length=150, required=True, notnull=True, unique=True),
        Field('transtype', self.ns.db.groups, ondelete='RESTRICT', notnull=True, label=self.ns.T('Doc.type'),
              requires = IS_IN_DB(self.ns.db(self.ns.db.groups.groupname.like('transtype')), self.ns.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.ns.valid.show_refnumber("refnumber", "groups", value, "groupvalue")),
        Field('notes', type='text'),
        Field('defpattern', type='integer', label=self.ns.T('Default'), default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=self.ns.valid.check_boolean(self.ns.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if self.ns.engine in("mssql"):
        table.transtype.ondelete = "NO ACTION"
        table.notes.type = 'string'
        table.notes.length = 'max'
      if create:
        self.createTable(table)

      table = self.ns.db.define_table('ui_zipcatalog',
        Field('id', readable=False, writable=False),
        Field('country', type='string', length=150, required=True, notnull=True, 
              requires = IS_IN_DB(self.ns.db(self.ns.db.ui_locale), self.ns.db.ui_locale.country, '%(country)s')),
        Field('zipcode', type='string', length=150, notnull=True, required=True),
        Field('city', type='string', length=150, notnull=True, required=True))
      if create:
        self.createTable(table)
  
      return True
    except Exception, err:
      self.ns.error_message = err
      return False
      
  def dropTables(self):
    for table in self.drop_all_table_lst:
      try:
        queries = self.ns.db._adapter._drop(Storage({"sqlsafe":table}), "")
        for query in queries:
          self.ns.db.executesql(query)
      except:
        continue
    self.ns.db.commit()
  
  def insertDefaultReports(self):
    #default reports init
    try:
      rfiles = os.listdir(os.path.join(self.ns.request.folder,'static/resources/report/dbs_ini/'))
      for rfile in rfiles:
        rp_sql = str(open(os.path.join(self.ns.request.folder,'static/resources/report/dbs_ini/'+rfile), 'r').read()).split(";")
        for sql in rp_sql:
          if str(sql).lower().find("insert")>-1 or str(sql).lower().find("update")>-1:
            self.ns.db.executesql(sql)
  
      self.ns.db.commit()  
      return True
    except Exception, err:
      self.ns.db.rollback()
      self.ns.error_message = err
      return False
  
  def insertFlashClientData(self):
    #Flash Client db init
    try:      
      pg_sql = str(open(os.path.join(self.ns.request.folder,'modules/nerva2py/nflex/insert_fbase_pg.sql'), 'r').read()).split(";")
      for sql in pg_sql:
        if str(sql).find("INSERT")>-1 or str(sql).find("UPDATE")>-1:
          self.ns.db.executesql(sql)
      
      upd_sql=[]
      if self.ns.engine=="postgres":
        pass
      elif self.ns.engine=="sqlite":
        upd_sql = str(open(os.path.join(self.ns.request.folder,'modules/nerva2py/nflex/insert_fbase_lite.sql'), 'r').read()).split(";")
      elif self.ns.engine in("mysql","google_sql"):
        upd_sql = str(open(os.path.join(self.ns.request.folder,'modules/nerva2py/nflex/insert_fbase_mysql.sql'), 'r').read()).split(";")
      elif self.ns.engine=="mssql":
        upd_sql = str(open(os.path.join(self.ns.request.folder,'modules/nerva2py/nflex/insert_fbase_mssql.sql'), 'r').read()).split(";")
      else:
        self.ns.error_message = str(self.ns.T('Unsupported Nervatura Flash Client database engine: ')) +self.ns.engine
        return False
      for sql in upd_sql:
        if str(sql).find("INSERT")>-1 or str(sql).find("UPDATE")>-1:
          self.ns.db.executesql(sql)
      
      lfiles = os.listdir(os.path.join(self.ns.request.folder,'modules/nerva2py/nflex/'))
      for lfile in lfiles:
        if lfile.startswith("locale_"):
          lc_sql = str(open(os.path.join(self.ns.request.folder,'modules/nerva2py/nflex/'+lfile), 'r').read()).split(";")
          for sql in lc_sql:
            if str(sql).find("INSERT")>-1 or str(sql).find("UPDATE")>-1:
              self.ns.db.executesql(sql)
  
      self.ns.db.commit()  
      return True
    except Exception, err:
      self.ns.db.rollback()
      self.ns.error_message = err
      return False
  
  def setIniData(self):
    #create if does not exist (update_row=False)
    try:
      
      aggretype = [{'id':self.ns.valid.get_groups_id('aggretype', '<>'), 
                    'groupname':'aggretype', 'groupvalue':'<>', 'description':None},
                   {'id':self.ns.valid.get_groups_id('aggretype', 'avg'), 
                    'groupname':'aggretype', 'groupvalue':'avg', 'description':None},
                   {'id':self.ns.valid.get_groups_id('aggretype', 'count'), 
                    'groupname':'aggretype', 'groupvalue':'count', 'description':None},
                   {'id':self.ns.valid.get_groups_id('aggretype', 'sum'), 
                    'groupname':'aggretype', 'groupvalue':'sum', 'description':None}]
      for values in aggretype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      nervatype = [{'id':self.ns.valid.get_groups_id('nervatype', 'address'),
                    'groupname':'nervatype', 'groupvalue':'address', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'audit'),
                    'groupname':'nervatype', 'groupvalue':'audit', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'barcode'),
                    'groupname':'nervatype', 'groupvalue':'barcode', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'contact'),
                    'groupname':'nervatype', 'groupvalue':'contact', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'currency'),
                    'groupname':'nervatype', 'groupvalue':'currency', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'customer'),
                    'groupname':'nervatype', 'groupvalue':'customer', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'deffield'),
                    'groupname':'nervatype', 'groupvalue':'deffield', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'employee'),
                    'groupname':'nervatype', 'groupvalue':'employee', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'event'),
                    'groupname':'nervatype', 'groupvalue':'event', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'groups'),
                    'groupname':'nervatype', 'groupvalue':'groups', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'item'),
                    'groupname':'nervatype', 'groupvalue':'item', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'link'),
                    'groupname':'nervatype', 'groupvalue':'link', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'log'),
                    'groupname':'nervatype', 'groupvalue':'log', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'menu'),
                    'groupname':'nervatype', 'groupvalue':'menu', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'movement'),
                    'groupname':'nervatype', 'groupvalue':'movement', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'numberdef'),
                    'groupname':'nervatype', 'groupvalue':'numberdef', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'pattern'),
                    'groupname':'nervatype', 'groupvalue':'pattern', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'payment'),
                    'groupname':'nervatype', 'groupvalue':'payment', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'place'),
                    'groupname':'nervatype', 'groupvalue':'place', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'price'),
                    'groupname':'nervatype', 'groupvalue':'price', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'product'),
                    'groupname':'nervatype', 'groupvalue':'product', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'project'),
                    'groupname':'nervatype', 'groupvalue':'project', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'rate'),
                    'groupname':'nervatype', 'groupvalue':'rate', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'report'),
                    'groupname':'nervatype', 'groupvalue':'report', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'tax'),
                    'groupname':'nervatype', 'groupvalue':'tax', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'tool'),
                    'groupname':'nervatype', 'groupvalue':'tool', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'trans'),
                    'groupname':'nervatype', 'groupvalue':'trans', 'description':None},
                   {'id':self.ns.valid.get_groups_id('nervatype', 'setting'),
                    'groupname':'nervatype', 'groupvalue':'setting', 'description':None}]
      for values in nervatype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
        
      fieldtype = [{'id':self.ns.valid.get_groups_id('fieldtype', 'bool'),
                    'groupname':'fieldtype', 'groupvalue':'bool', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'checkbox'),
                    'groupname':'fieldtype', 'groupvalue':'checkbox', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'date'),
                    'groupname':'fieldtype', 'groupvalue':'date', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'float'),
                    'groupname':'fieldtype', 'groupvalue':'float', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'integer'),
                    'groupname':'fieldtype', 'groupvalue':'integer', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'string'),
                    'groupname':'fieldtype', 'groupvalue':'string', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'valuelist'),
                    'groupname':'fieldtype', 'groupvalue':'valuelist', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'notes'),
                    'groupname':'fieldtype', 'groupvalue':'notes', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'filter'),
                    'groupname':'fieldtype', 'groupvalue':'filter', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'urlink'),
                    'groupname':'fieldtype', 'groupvalue':'urlink', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'password'),
                    'groupname':'fieldtype', 'groupvalue':'password', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'customer'),
                    'groupname':'fieldtype', 'groupvalue':'customer', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'tool'),
                    'groupname':'fieldtype', 'groupvalue':'tool', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'transitem'),
                    'groupname':'fieldtype', 'groupvalue':'transitem', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'transmovement'),
                    'groupname':'fieldtype', 'groupvalue':'transmovement', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'transpayment'),
                    'groupname':'fieldtype', 'groupvalue':'transpayment', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'product'),
                    'groupname':'fieldtype', 'groupvalue':'product', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'project'),
                    'groupname':'fieldtype', 'groupvalue':'project', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'employee'),
                    'groupname':'fieldtype', 'groupvalue':'employee', 'description':None},
                   {'id':self.ns.valid.get_groups_id('fieldtype', 'place'),
                    'groupname':'fieldtype', 'groupvalue':'place', 'description':None}]
      for values in fieldtype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      filetype = [{'id':self.ns.valid.get_groups_id('filetype', 'doc'),
                   'groupname':'filetype', 'groupvalue':'doc', 'description':'MsWord document'},
                  {'id':self.ns.valid.get_groups_id('filetype', 'xls'),
                   'groupname':'filetype', 'groupvalue':'xls', 'description':'MsExcel workbook'},
                  {'id':self.ns.valid.get_groups_id('filetype', 'odt'),
                   'groupname':'filetype', 'groupvalue':'odt', 'description':'OpenOffice document'},
                  {'id':self.ns.valid.get_groups_id('filetype', 'mxml'),
                   'groupname':'filetype', 'groupvalue':'mxml', 'description':'Flash report'},
                  {'id':self.ns.valid.get_groups_id('filetype', 'html'),
                   'groupname':'filetype', 'groupvalue':'html', 'description':'HTML document'},
                  {'id':self.ns.valid.get_groups_id('filetype', 'gshi'),
                   'groupname':'filetype', 'groupvalue':'gshi', 'description':'Genshi template'},
                  {'id':self.ns.valid.get_groups_id('filetype', 'fpdf'),
                   'groupname':'filetype', 'groupvalue':'fpdf', 'description':'FPDF template'}]
      for values in filetype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
        
      transtype = [{'id':self.ns.valid.get_groups_id('transtype', 'invoice'),
                    'groupname':'transtype', 'groupvalue':'invoice', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'receipt'),
                    'groupname':'transtype', 'groupvalue':'receipt', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'order'),
                    'groupname':'transtype', 'groupvalue':'order', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'offer'),
                    'groupname':'transtype', 'groupvalue':'offer', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'worksheet'),
                    'groupname':'transtype', 'groupvalue':'worksheet', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'rent'),
                    'groupname':'transtype', 'groupvalue':'rent', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'delivery'),
                    'groupname':'transtype', 'groupvalue':'delivery', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'store'),
                    'groupname':'transtype', 'groupvalue':'store', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'inventory'),
                    'groupname':'transtype', 'groupvalue':'inventory', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'waybill'),
                    'groupname':'transtype', 'groupvalue':'waybill', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'production'),
                    'groupname':'transtype', 'groupvalue':'production', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'formula'),
                    'groupname':'transtype', 'groupvalue':'formula', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'bank'),
                    'groupname':'transtype', 'groupvalue':'bank', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'cash'),
                    'groupname':'transtype', 'groupvalue':'cash', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtype', 'filing'),
                    'groupname':'transtype', 'groupvalue':'filing', 'description':None}]
      for values in transtype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      direction = [{'id':self.ns.valid.get_groups_id('direction', 'out'),
                    'groupname':'direction', 'groupvalue':'out', 'description':None},
                   {'id':self.ns.valid.get_groups_id('direction', 'in'),
                    'groupname':'direction', 'groupvalue':'in', 'description':None},
                   {'id':self.ns.valid.get_groups_id('direction', 'transfer'),
                    'groupname':'direction', 'groupvalue':'transfer', 'description':None},
                   {'id':self.ns.valid.get_groups_id('direction', 'return'),
                    'groupname':'direction', 'groupvalue':'return', 'description':None}]
      for values in direction:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      wheretype = [{'id':self.ns.valid.get_groups_id('wheretype', 'where'),
                    'groupname':'wheretype', 'groupvalue':'where', 'description':None},
                   {'id':self.ns.valid.get_groups_id('wheretype', 'having'),
                    'groupname':'wheretype', 'groupvalue':'having', 'description':None},
                   {'id':self.ns.valid.get_groups_id('wheretype', 'in'),
                    'groupname':'wheretype', 'groupvalue':'in', 'description':None}]
      for values in wheretype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      barcodetype = [{'id':self.ns.valid.get_groups_id('barcodetype', 'code128a'),
                      'groupname':'barcodetype', 'groupvalue':'code128a', 'description':'Code128A'},
                     {'id':self.ns.valid.get_groups_id('barcodetype', 'code128b'),
                      'groupname':'barcodetype', 'groupvalue':'code128b', 'description':'Code128B'},
                     {'id':self.ns.valid.get_groups_id('barcodetype', 'code128c'),
                      'groupname':'barcodetype', 'groupvalue':'code128c', 'description':'Code128C'},
                     {'id':self.ns.valid.get_groups_id('barcodetype', 'code39'),
                      'groupname':'barcodetype', 'groupvalue':'code39', 'description':'USD-3 (Code39)'},
                     {'id':self.ns.valid.get_groups_id('barcodetype', 'code93'),
                      'groupname':'barcodetype', 'groupvalue':'code93', 'description':'USS-93 (Code93)'},
                     {'id':self.ns.valid.get_groups_id('barcodetype', 'code25'),
                      'groupname':'barcodetype', 'groupvalue':'code25', 'description':'2of5 (Industrial)'},
                     {'id':self.ns.valid.get_groups_id('barcodetype', 'code25i'),
                      'groupname':'barcodetype', 'groupvalue':'code25i', 'description':'Interleaved 2of5'},
                     {'id':self.ns.valid.get_groups_id('barcodetype', 'postnet'),
                      'groupname':'barcodetype', 'groupvalue':'postnet', 'description':'Postnet'},
                     {'id':self.ns.valid.get_groups_id('barcodetype', 'upca'),
                      'groupname':'barcodetype', 'groupvalue':'upca', 'description':'UPC-A'},
                     {'id':self.ns.valid.get_groups_id('barcodetype', 'upce'),
                      'groupname':'barcodetype', 'groupvalue':'upce', 'description':'UPC-E'},
                     {'id':self.ns.valid.get_groups_id('barcodetype', 'ean13'),
                      'groupname':'barcodetype', 'groupvalue':'ean13', 'description':'EAN-13'},
                     {'id':self.ns.valid.get_groups_id('barcodetype', 'ean8'),
                      'groupname':'barcodetype', 'groupvalue':'ean8', 'description':'EAN-8'}]
      for values in barcodetype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
        
      ratetype = [{'id':self.ns.valid.get_groups_id('ratetype', 'rate'),
                   'groupname':'ratetype', 'groupvalue':'rate', 'description':None},
                  {'id':self.ns.valid.get_groups_id('ratetype', 'buy'),
                   'groupname':'ratetype', 'groupvalue':'buy', 'description':None},
                  {'id':self.ns.valid.get_groups_id('ratetype', 'sell'),
                   'groupname':'ratetype', 'groupvalue':'sell', 'description':None},
                  {'id':self.ns.valid.get_groups_id('ratetype', 'average'),
                   'groupname':'ratetype', 'groupvalue':'average', 'description':None}]
      for values in ratetype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      filtertype = [{'id':self.ns.valid.get_groups_id('filtertype', '=='),
                     'groupname':'filtertype', 'groupvalue':'==', 'description':None},
                    {'id':self.ns.valid.get_groups_id('filtertype', '=N'),
                     'groupname':'filtertype', 'groupvalue':'=N', 'description':None},
                    {'id':self.ns.valid.get_groups_id('filtertype', '!='),
                     'groupname':'filtertype', 'groupvalue':'!=', 'description':None},
                    {'id':self.ns.valid.get_groups_id('filtertype', '>='),
                     'groupname':'filtertype', 'groupvalue':'>=', 'description':None},
                    {'id':self.ns.valid.get_groups_id('filtertype', '<='),
                     'groupname':'filtertype', 'groupvalue':'<=', 'description':None}]
      for values in filtertype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      movetype = [{'id':self.ns.valid.get_groups_id('movetype', 'inventory'),
                   'groupname':'movetype', 'groupvalue':'inventory', 'description':None},
                  {'id':self.ns.valid.get_groups_id('movetype', 'store'),
                   'groupname':'movetype', 'groupvalue':'store', 'description':None},
                  {'id':self.ns.valid.get_groups_id('movetype', 'tool'),
                   'groupname':'movetype', 'groupvalue':'tool', 'description':None},
                  {'id':self.ns.valid.get_groups_id('movetype', 'plan'),
                   'groupname':'movetype', 'groupvalue':'plan', 'description':None},
                  {'id':self.ns.valid.get_groups_id('movetype', 'head'),
                   'groupname':'movetype', 'groupvalue':'head', 'description':None}]
      for values in movetype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      transtate = [{'id':self.ns.valid.get_groups_id('transtate', 'ok'),
                    'groupname':'transtate', 'groupvalue':'ok', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtate', 'new'),
                    'groupname':'transtate', 'groupvalue':'new', 'description':None},
                   {'id':self.ns.valid.get_groups_id('transtate', 'back'),
                    'groupname':'transtate', 'groupvalue':'back', 'description':None}]
      for values in transtate:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      logstate = [{'id':self.ns.valid.get_groups_id('logstate', 'update'),
                   'groupname':'logstate', 'groupvalue':'update', 'description':None},
                  {'id':self.ns.valid.get_groups_id('logstate', 'closed'),
                   'groupname':'logstate', 'groupvalue':'closed', 'description':None},
                  {'id':self.ns.valid.get_groups_id('logstate', 'deleted'),
                   'groupname':'logstate', 'groupvalue':'deleted', 'description':None},
                  {'id':self.ns.valid.get_groups_id('logstate', 'print'),
                   'groupname':'logstate', 'groupvalue':'print', 'description':None},
                  {'id':self.ns.valid.get_groups_id('logstate', 'login'),
                   'groupname':'logstate', 'groupvalue':'login', 'description':None},
                  {'id':self.ns.valid.get_groups_id('logstate', 'logout'),
                   'groupname':'logstate', 'groupvalue':'logout', 'description':None}]
      for values in logstate:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      usergroup = [{'id':self.ns.valid.get_groups_id('usergroup', 'admin'),
                    'groupname':'usergroup', 'groupvalue':'admin', 'description':'Admin'},
                   {'id':self.ns.valid.get_groups_id('usergroup', 'user'),
                    'groupname':'usergroup', 'groupvalue':'user', 'description':'Employee'},
                   {'id':self.ns.valid.get_groups_id('usergroup', 'guest'),
                    'groupname':'usergroup', 'groupvalue':'guest', 'description':'Guest'},
                   {'id':self.ns.valid.get_groups_id('usergroup', 'demo'),
                    'groupname':'usergroup', 'groupvalue':'demo', 'description':'Demo'}]
      for values in usergroup:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      inputfilter = [{'id':self.ns.valid.get_groups_id('inputfilter', 'disabled'),
                      'groupname':'inputfilter', 'groupvalue':'disabled', 'description':None},
                     {'id':self.ns.valid.get_groups_id('inputfilter', 'readonly'),
                      'groupname':'inputfilter', 'groupvalue':'readonly', 'description':None},
                     {'id':self.ns.valid.get_groups_id('inputfilter', 'update'),
                      'groupname':'inputfilter', 'groupvalue':'update', 'description':None},
                     {'id':self.ns.valid.get_groups_id('inputfilter', 'all'),
                      'groupname':'inputfilter', 'groupvalue':'all', 'description':None}]
      for values in inputfilter:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      transfilter = [{'id':self.ns.valid.get_groups_id('transfilter', 'own'),
                      'groupname':'transfilter', 'groupvalue':'own', 'description':None},
                     {'id':self.ns.valid.get_groups_id('transfilter', 'usergroup'),
                      'groupname':'transfilter', 'groupvalue':'usergroup', 'description':None},
                     {'id':self.ns.valid.get_groups_id('transfilter', 'all'),
                      'groupname':'transfilter', 'groupvalue':'all', 'description':None}]
      for values in transfilter:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      protype = [{'id':self.ns.valid.get_groups_id('protype', 'item'),
                  'groupname':'protype', 'groupvalue':'item', 'description':None},
                 {'id':self.ns.valid.get_groups_id('protype', 'service'),
                  'groupname':'protype', 'groupvalue':'service', 'description':None}]
      for values in protype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      custtype = [{'id':self.ns.valid.get_groups_id('custtype', 'own'),
                  'groupname':'custtype', 'groupvalue':'own', 'description':None},
                  {'id':self.ns.valid.get_groups_id('custtype', 'company'),
                   'groupname':'custtype', 'groupvalue':'company', 'description':None},
                  {'id':self.ns.valid.get_groups_id('custtype', 'private'),
                   'groupname':'custtype', 'groupvalue':'private', 'description':None},
                  {'id':self.ns.valid.get_groups_id('custtype', 'other'),
                   'groupname':'custtype', 'groupvalue':'other', 'description':None}]
      for values in custtype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      calcmode = [{'id':self.ns.valid.get_groups_id('calcmode', 'ded'),
                   'groupname':'calcmode', 'groupvalue':'ded', 'description':'deduction (%)'},
                  {'id':self.ns.valid.get_groups_id('calcmode', 'add'),
                   'groupname':'calcmode', 'groupvalue':'add', 'description':'adding (%)'},
                  {'id':self.ns.valid.get_groups_id('calcmode', 'amo'),
                   'groupname':'calcmode', 'groupvalue':'amo', 'description':'amount (+/-)'}]
      for values in calcmode:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      paidtype = [{'id':self.ns.valid.get_groups_id('paidtype', 'cash'),
                   'groupname':'paidtype', 'groupvalue':'cash', 'description':None},
                  {'id':self.ns.valid.get_groups_id('paidtype', 'transfer'),
                   'groupname':'paidtype', 'groupvalue':'transfer', 'description':None},
                  {'id':self.ns.valid.get_groups_id('paidtype', 'credit_card'),
                   'groupname':'paidtype', 'groupvalue':'credit_card', 'description':None}]
      for values in paidtype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      storetype = [{'id':self.ns.valid.get_groups_id('storetype', 'sps'),
                    'groupname':'storetype', 'groupvalue':'sps', 'description':'Singlepart - Single FIFO'},
                   {'id':self.ns.valid.get_groups_id('storetype', 'spm'),
                    'groupname':'storetype', 'groupvalue':'spm', 'description':'Singlepart - Multi FIFO'},
                   {'id':self.ns.valid.get_groups_id('storetype', 'mps'),
                    'groupname':'storetype', 'groupvalue':'mps', 'description':'Multipart - Single FIFO'},
                   {'id':self.ns.valid.get_groups_id('storetype', 'mpm'),
                    'groupname':'storetype', 'groupvalue':'mpm', 'description':'Multipart - Multi FIFO'}]
      for values in storetype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      placetype = [{'id':self.ns.valid.get_groups_id('placetype', 'bank'),
                    'groupname':'placetype', 'groupvalue':'bank', 'description':None},
                   {'id':self.ns.valid.get_groups_id('placetype', 'cash'),
                    'groupname':'placetype', 'groupvalue':'cash', 'description':None},
                   {'id':self.ns.valid.get_groups_id('placetype', 'warehouse'),
                    'groupname':'placetype', 'groupvalue':'warehouse', 'description':None},
                   {'id':self.ns.valid.get_groups_id('placetype', 'store'),
                    'groupname':'placetype', 'groupvalue':'store', 'description':None}]
      for values in placetype:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      toolgroup = [{'id':self.ns.valid.get_groups_id('toolgroup', 'printer'),
                    'groupname':'toolgroup', 'groupvalue':'printer', 'description':'Printer'}]
      for values in toolgroup:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      orientation = [{'id':self.ns.valid.get_groups_id('orientation', 'P'),
                      'groupname':'orientation', 'groupvalue':'P', 'description':'Portrait'},
                     {'id':self.ns.valid.get_groups_id('orientation', 'L'),
                      'groupname':'orientation', 'groupvalue':'L', 'description':'Landscape'}]
      for values in orientation:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
        
      papersize = [{'id':self.ns.valid.get_groups_id('papersize', 'a3'),
                    'groupname':'papersize', 'groupvalue':'a3', 'description':'A3'},
                   {'id':self.ns.valid.get_groups_id('papersize', 'a4'),
                    'groupname':'papersize', 'groupvalue':'a4', 'description':'A4'},
                   {'id':self.ns.valid.get_groups_id('papersize', 'a5'),
                    'groupname':'papersize', 'groupvalue':'a5', 'description':'A5'},
                   {'id':self.ns.valid.get_groups_id('papersize', 'letter'),
                    'groupname':'papersize', 'groupvalue':'letter', 'description':'Letter'},
                   {'id':self.ns.valid.get_groups_id('papersize', 'legal'),
                    'groupname':'papersize', 'groupvalue':'legal', 'description':'Legal'}]
      for values in papersize:
        self.ns.connect.updateData("groups", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)

      
      currency = [{'id':self.ns.valid.get_id_from_refnumber('currency','EUR'),
                   'curr':'EUR', 'description':'euro', 'digit':2, 'defrate':0, 'cround':0}]
      for values in currency:
        self.ns.connect.updateData("currency", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      employee = [{'id':self.ns.valid.get_id_from_refnumber('employee','admin'),
                   'empnumber':'admin', 'username':'admin', 'usergroup':self.ns.valid.get_groups_id("usergroup", "admin")},
                  {'id':self.ns.valid.get_id_from_refnumber('employee','user'),
                   'empnumber':'user', 'username':'user', 'usergroup':self.ns.valid.get_groups_id("usergroup", "user")},
                  {'id':self.ns.valid.get_id_from_refnumber('employee','guest'),
                   'empnumber':'guest', 'username':'guest', 'usergroup':self.ns.valid.get_groups_id("usergroup", "guest")},
                  {'id':self.ns.valid.get_id_from_refnumber('employee','demo'),
                   'empnumber':'demo', 'username':'demo', 'usergroup':self.ns.valid.get_groups_id("usergroup", "demo")}]
      for values in employee:
        self.ns.connect.updateData("employee", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      nervatype_employee_id = self.ns.valid.get_groups_id("nervatype", "employee")
      employee_address = [{'id':self.ns.valid.get_id_from_refnumber('address','employee/admin'),
                           'nervatype':nervatype_employee_id, 'ref_id':self.ns.valid.get_id_from_refnumber('employee','admin')},
                          {'id':self.ns.valid.get_id_from_refnumber('address','employee/user'),
                           'nervatype':nervatype_employee_id, 'ref_id':self.ns.valid.get_id_from_refnumber('employee','user')},
                          {'id':self.ns.valid.get_id_from_refnumber('address','employee/guest'),
                           'nervatype':nervatype_employee_id, 'ref_id':self.ns.valid.get_id_from_refnumber('employee','guest')},
                          {'id':self.ns.valid.get_id_from_refnumber('address','employee/demo'),
                           'nervatype':nervatype_employee_id, 'ref_id':self.ns.valid.get_id_from_refnumber('employee','demo')}]
      for values in employee_address:
        self.ns.connect.updateData("address", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      employee_contact = [{'id':self.ns.valid.get_id_from_refnumber('contact','employee/admin'),
                           'nervatype':nervatype_employee_id, 'ref_id':self.ns.valid.get_id_from_refnumber('employee','admin')},
                          {'id':self.ns.valid.get_id_from_refnumber('contact','employee/user'),
                           'nervatype':nervatype_employee_id, 'ref_id':self.ns.valid.get_id_from_refnumber('employee','user')},
                          {'id':self.ns.valid.get_id_from_refnumber('contact','employee/guest'),
                           'nervatype':nervatype_employee_id, 'ref_id':self.ns.valid.get_id_from_refnumber('employee','guest')},
                          {'id':self.ns.valid.get_id_from_refnumber('contact','employee/demo'),
                           'nervatype':nervatype_employee_id, 'ref_id':self.ns.valid.get_id_from_refnumber('employee','demo')}]
      for values in employee_contact:
        self.ns.connect.updateData("contact", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      self.ns.valid.get_own_customer()
      
      place = [{'id':self.ns.valid.get_id_from_refnumber('place','bank'),
                'planumber':'bank', 'placetype':self.ns.valid.get_groups_id("placetype", "bank"), 
                'description':'Bank', 'curr':'EUR'},
               {'id':self.ns.valid.get_id_from_refnumber('place','cash'),
                'planumber':'cash', 'placetype':self.ns.valid.get_groups_id("placetype", "cash"), 
                'description':'Cash', 'curr':'EUR'},
               {'id':self.ns.valid.get_id_from_refnumber('place','warehouse'),
                'planumber':'warehouse', 'placetype':self.ns.valid.get_groups_id("placetype", "warehouse"), 
                'description':'Warehouse'}]
      for values in place:
        self.ns.connect.updateData("place", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      product = [{"id":self.ns.valid.get_id_from_refnumber("product","printer"),
                  "protype":self.ns.valid.get_groups_id("protype", "item"),
                  "partnumber":"printer", "description":"Generic printer", "unit":"piece",
                  "tax_id":self.ns.valid.get_id_from_refnumber("tax","0%")}]
      for values in product:
        self.ns.connect.updateData("product", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
        
      numberdef = [{'id':self.ns.valid.get_id_from_refnumber('numberdef','bank_transfer'),
                    'numberkey': 'bank_transfer', 'prefix':  'BANK', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'statement', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','calnumber'),
                    'numberkey': 'calnumber', 'prefix':  'EVT', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'event', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','cash'),
                    'numberkey': 'cash', 'prefix':  'CASH', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'cash payment', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','custnumber'),
                    'numberkey': 'custnumber', 'prefix':  'CUS', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'customer', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','delivery_in'),
                    'numberkey': 'delivery_in', 'prefix':  'DELIN', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'delivery in', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','delivery_out'),
                    'numberkey': 'delivery_out', 'prefix':  'DELOU', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'delivery out', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','delivery_transfer'),
                    'numberkey': 'delivery_transfer', 'prefix':  'DELTF', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'delivery transfer', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','empnumber'),
                    'numberkey': 'empnumber', 'prefix':  'EMP', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'employee', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','filing_in'),
                    'numberkey': 'filing_in', 'prefix':  'FILIN', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'filing in', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','filing_out'),
                    'numberkey': 'filing_out', 'prefix':  'FILOU', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'filing out', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','formula_transfer'),
                    'numberkey': 'formula_transfer', 'prefix':  'FRM', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'formula', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','inventory_transfer'),
                    'numberkey': 'inventory_transfer', 'prefix':  'VENDL', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'inventory delivery', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','invoice_in'),
                    'numberkey': 'invoice_in', 'prefix':  'INVVD', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'vendor invoice', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','invoice_out'),
                    'numberkey': 'invoice_out', 'prefix':  'INVCT', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'customer invoice', 'visible': 1, 'readonly': 1, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','offer_in'),
                    'numberkey': 'offer_in', 'prefix':  'OFFVD', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'vendor offer', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','offer_out'),
                    'numberkey': 'offer_out', 'prefix':  'OFFCT', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'customer offer', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','order_in'),
                    'numberkey': 'order_in', 'prefix':  'ORDVD', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'vendor order', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','order_out'),
                    'numberkey': 'order_out', 'prefix':  'ORDCT', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'customer order', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','order_return'),
                    'numberkey': 'order_return', 'prefix':  'ORDRE', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'goods return', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','partnumber'),
                    'numberkey': 'partnumber', 'prefix':  'PRO', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'poduct', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','production_transfer'),
                    'numberkey': 'production_transfer', 'prefix':  'MAKE', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'production', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','pronumber'),
                    'numberkey': 'pronumber', 'prefix':  'PRJ', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'project', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','receipt_in'),
                    'numberkey': 'receipt_in', 'prefix':  'RECVD', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'vendor receipt', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','receipt_out'),
                    'numberkey': 'receipt_out', 'prefix':  'RECCT', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'customer receipt', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','rent_in'),
                    'numberkey': 'rent_in', 'prefix':  'RENVD', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'vendor rent', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','rent_out'),
                    'numberkey': 'rent_out', 'prefix':  'RENCT', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'customer rent', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','serial'),
                    'numberkey': 'serial', 'prefix':  'SER', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'tool', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','store_in'),
                    'numberkey': 'store_in', 'prefix':  'STOIN', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'store in', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','store_out'),
                    'numberkey': 'store_out', 'prefix':  'STOOU', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'store out', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','store_transfer'),
                    'numberkey': 'store_transfer', 'prefix':  'STOTF', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'store transfer', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','waybill'),
                    'numberkey': 'waybill', 'prefix':  'MOVE', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'tool movement', 'visible': 1, 'readonly': 0, 'orderby': 0},
                   {'id':self.ns.valid.get_id_from_refnumber('numberdef','worksheet_out'),
                    'numberkey': 'worksheet_out', 'prefix':  'WORK', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 
                    'description':  'worksheet', 'visible': 1, 'readonly': 0, 'orderby': 0}]
      for values in numberdef:
        self.ns.connect.updateData("numberdef", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
        
      tax = [{'id':self.ns.valid.get_id_from_refnumber('tax','TAM'), 'description':'tax-free (by product)', 'rate':0, 'taxcode':'TAM'},
             {'id':self.ns.valid.get_id_from_refnumber('tax','AAM'), 'description':'tax-free (by customer)', 'rate':0, 'taxcode':'AAM'},
             {'id':self.ns.valid.get_id_from_refnumber('tax','0%'), 'description':'VAT 0%', 'rate':0, 'taxcode':'0%'},
             {'id':self.ns.valid.get_id_from_refnumber('tax','5%'), 'description':'VAT 5%', 'rate':0.05, 'taxcode':'5%'},
             {'id':self.ns.valid.get_id_from_refnumber('tax','10%'), 'description':'VAT 10%', 'rate':0.1, 'taxcode':'10%'},
             {'id':self.ns.valid.get_id_from_refnumber('tax','15%'), 'description':'VAT 15%', 'rate':0.15, 'taxcode':'15%'},
             {'id':self.ns.valid.get_id_from_refnumber('tax','20%'), 'description':'VAT 20%', 'rate':0.2, 'taxcode':'20%'},
             {'id':self.ns.valid.get_id_from_refnumber('tax','25%'), 'description':'VAT 25%', 'rate':0.25, 'taxcode':'25%'}]
      for values in tax:
        self.ns.connect.updateData("tax", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      nervatype_trans_id = self.ns.valid.get_groups_id("nervatype", "trans")
      nervatype_tool_id = self.ns.valid.get_groups_id("nervatype", "tool")
      nervatype_setting_id = self.ns.valid.get_groups_id("nervatype", "setting")
      nervatype_link_id = self.ns.valid.get_groups_id("nervatype", "link")
      nervatype_product_id = self.ns.valid.get_groups_id("nervatype", "product")
      transtype_invoice_id = self.ns.valid.get_groups_id("transtype", "invoice")
      transtype_worksheet_id = self.ns.valid.get_groups_id("transtype", "worksheet")
      transtype_rent_id = self.ns.valid.get_groups_id("transtype", "rent")
      fieldtype_string = self.ns.valid.get_groups_id("fieldtype", "string")
      fieldtype_float = self.ns.valid.get_groups_id("fieldtype", "float")
      fieldtype_bool = self.ns.valid.get_groups_id("fieldtype", "bool")
      
      deffield_trans = [{'id':self.ns.valid.get_id_from_refnumber('deffield','trans_transitem_link'),
                         'fieldname':'trans_transitem_link', 'nervatype':nervatype_trans_id, 
                         'subtype':None, 'fieldtype':self.ns.valid.get_groups_id("fieldtype", "transitem"), 
                         'description':'Ref.No.', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                        {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_transcast'),
                         'fieldname':'trans_transcast', 'nervatype':nervatype_trans_id,
                         'subtype':None, 'fieldtype':self.ns.valid.get_groups_id("fieldtype", "valuelist"), 
                         'description':'transaction special state', 'valuelist':'normal|cancellation|amendment', 
                         'addnew':1, 'visible':0, 'readonly':1}]
      for values in deffield_trans:
        self.ns.connect.updateData("deffield", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
                                  
      deffield_trans_invoice = [
                        {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_custinvoice_compname'),
                         'fieldname':'trans_custinvoice_compname', 'nervatype':nervatype_trans_id,
                         'subtype':transtype_invoice_id, 'fieldtype':fieldtype_string, 
                         'description':'customer invoice company name', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1},
                        {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_custinvoice_compaddress'),
                         'fieldname':'trans_custinvoice_compaddress', 'nervatype':nervatype_trans_id,
                         'subtype':transtype_invoice_id, 'fieldtype':fieldtype_string, 
                         'description':'customer invoice company address', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1},
                        {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_custinvoice_comptax'),
                         'fieldname':'trans_custinvoice_comptax', 'nervatype':nervatype_trans_id,
                         'subtype':transtype_invoice_id, 'fieldtype':fieldtype_string, 
                         'description':'customer invoice company taxnumber', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1},
                        {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_custinvoice_custname'),
                         'fieldname':'trans_custinvoice_custname', 'nervatype':nervatype_trans_id,
                         'subtype':transtype_invoice_id, 'fieldtype':fieldtype_string, 
                         'description':'customer invoice customer name', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1},
                        {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_custinvoice_custaddress'),
                         'fieldname':'trans_custinvoice_custaddress', 'nervatype':nervatype_trans_id, 
                         'subtype':transtype_invoice_id, 'fieldtype':fieldtype_string, 
                         'description':'customer invoice customer address', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1},
                        {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_custinvoice_custtax'),
                         'fieldname':'trans_custinvoice_custtax', 'nervatype':nervatype_trans_id, 
                         'subtype':transtype_invoice_id, 'fieldtype':fieldtype_string, 
                         'description':'customer invoice customer taxnumber', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}]
      for values in deffield_trans_invoice:
        self.ns.connect.updateData("deffield", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)

      deffield_trans_closed = [
                         {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_closed_policy_invoice_out'),
                          'fieldname':'trans_closed_policy_invoice_out', 'nervatype':nervatype_trans_id,
                          'subtype':None, 'fieldtype':fieldtype_string,
                          'description':'transaction closed policy', 'valuelist':'print', 'addnew':0, 'visible':0, 'readonly':1},
                         {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_closed_policy_receipt_out'),
                          'fieldname':'trans_closed_policy_receipt_out', 'nervatype':nervatype_trans_id,
                          'subtype':None, 'fieldtype':fieldtype_string,
                          'description':'transaction closed policy', 'valuelist':'print', 'addnew':0, 'visible':0, 'readonly':1}]
      for values in deffield_trans_closed:
        self.ns.connect.updateData("deffield", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      deffield_trans_worksheet = [
                         {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_wsdistance'),
                          "fieldname":"trans_wsdistance","nervatype":nervatype_trans_id,
                          'subtype':transtype_worksheet_id, "fieldtype":fieldtype_float,
                          "description":"worksheet distance", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1},
                         {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_wsrepair'),
                          "fieldname":"trans_wsrepair","nervatype":nervatype_trans_id, 
                          'subtype':transtype_worksheet_id, "fieldtype":fieldtype_float,
                          "description":"worksheet repair time (hour)", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1},
                         {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_wstotal'),
                          "fieldname":"trans_wstotal","nervatype":nervatype_trans_id, 
                          'subtype':transtype_worksheet_id, "fieldtype":fieldtype_float,
                          "description":"worksheet total time (hour)", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1},
                         {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_wsnote'),
                          "fieldname":"trans_wsnote","nervatype":nervatype_trans_id, 
                          'subtype':transtype_worksheet_id, "fieldtype":fieldtype_string,
                          "description":"worksheet justification", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}]
      for values in deffield_trans_worksheet:
        self.ns.connect.updateData("deffield", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      deffield_trans_rent = [{'id':self.ns.valid.get_id_from_refnumber('deffield','trans_reholiday'),
                               "fieldname":"trans_reholiday","nervatype":nervatype_trans_id,
                               'subtype':transtype_rent_id, "fieldtype":fieldtype_float,
                               "description":"rent holidays", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1},
                              {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_rebadtool'),
                               "fieldname":"trans_rebadtool","nervatype":nervatype_trans_id,
                               'subtype':transtype_rent_id, "fieldtype":fieldtype_float,
                               "description":"rent bad machine", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1},
                              {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_reother'),
                               "fieldname":"trans_reother","nervatype":nervatype_trans_id,
                               'subtype':transtype_rent_id, "fieldtype":fieldtype_float,
                               "description":"rent other non-eligible", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1},
                              {'id':self.ns.valid.get_id_from_refnumber('deffield','trans_rentnote'),
                               "fieldname":"trans_rentnote","nervatype":nervatype_trans_id,
                               'subtype':transtype_rent_id, "fieldtype":fieldtype_string,
                               "description":"rent justification", 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}]
      for values in deffield_trans_rent:
        self.ns.connect.updateData("deffield", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
                               
      deffield_tool =[{'id':self.ns.valid.get_id_from_refnumber('deffield','tool_printertype'),
                       'fieldname':'tool_printertype', 'nervatype':nervatype_tool_id, 
                       'subtype':None, 'fieldtype':self.ns.valid.get_groups_id("fieldtype", "valuelist"), 
                       'description':'Printer type', 'valuelist':'local|network|mail|gcloud', 'addnew':0, 'visible':1, 'readonly':0},
                      {'id':self.ns.valid.get_id_from_refnumber('deffield','tool_printer_login'),
                       "fieldname":"tool_printer_login","nervatype":nervatype_tool_id, 
                       'subtype':None, "fieldtype":fieldtype_string,
                       "description":"Printer login", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                      {'id':self.ns.valid.get_id_from_refnumber('deffield','tool_printer_password'),
                       "fieldname":"tool_printer_password","nervatype":nervatype_tool_id, 
                       'subtype':None, "fieldtype":self.ns.valid.get_groups_id("fieldtype", "password"),
                       "description":"Printer password", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                      {'id':self.ns.valid.get_id_from_refnumber('deffield','tool_printer_server'),
                       "fieldname":"tool_printer_server","nervatype":nervatype_tool_id, 
                       'subtype':None, "fieldtype":fieldtype_string,
                       "description":"Printer server", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                      {'id':self.ns.valid.get_id_from_refnumber('deffield','tool_printer_port'),
                       "fieldname":"tool_printer_port","nervatype":nervatype_tool_id, 
                       'subtype':None, "fieldtype":self.ns.valid.get_groups_id("fieldtype", "integer"),
                       "description":"Printer port", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                      {'id':self.ns.valid.get_id_from_refnumber('deffield','tool_printer_mail_smtp'),
                       "fieldname":"tool_printer_mail_smtp","nervatype":nervatype_tool_id, 
                       'subtype':None, "fieldtype":fieldtype_string,
                       "description":"Printer mail smtp", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                      {'id':self.ns.valid.get_id_from_refnumber('deffield','tool_printer_mail_sender'),
                       "fieldname":"tool_printer_mail_sender","nervatype":nervatype_tool_id, 
                       'subtype':None, "fieldtype":fieldtype_string,
                       "description":"Printer mail sender", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                      {'id':self.ns.valid.get_id_from_refnumber('deffield','tool_printer_mail_login'),
                       "fieldname":"tool_printer_mail_login","nervatype":nervatype_tool_id, 
                       'subtype':None, "fieldtype":fieldtype_string,
                       "description":"Printer mail login (username:password)", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                      {'id':self.ns.valid.get_id_from_refnumber('deffield','tool_printer_mail_address'),
                       "fieldname":"tool_printer_mail_address","nervatype":nervatype_tool_id, 
                       'subtype':None, "fieldtype":fieldtype_string,
                       "description":"Printer mail address", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                      {'id':self.ns.valid.get_id_from_refnumber('deffield','tool_printer_mail_subject'),
                       "fieldname":"tool_printer_mail_subject","nervatype":nervatype_tool_id, 
                       'subtype':None, "fieldtype":fieldtype_string,
                       "description":"Printer mail subject", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                      {'id':self.ns.valid.get_id_from_refnumber('deffield','tool_printer_mail_message'),
                       "fieldname":"tool_printer_mail_message","nervatype":nervatype_tool_id, 
                       'subtype':None, "fieldtype":fieldtype_string,
                       "description":"Printer mail message", 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}]
      for values in deffield_tool:
        self.ns.connect.updateData("deffield", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      deffield_link = [{'id':self.ns.valid.get_id_from_refnumber('deffield','link_qty'),
                        'fieldname':'link_qty', 'nervatype':nervatype_link_id,
                        'subtype':None, 'fieldtype':self.ns.valid.get_groups_id("fieldtype", "float"),
                        'description':'link qty value', 'valuelist':None, 'addnew':0, 'visible':0, 'readonly':0},
                       {'id':self.ns.valid.get_id_from_refnumber('deffield','link_rate'),
                        'fieldname':'link_rate', 'nervatype':nervatype_link_id,
                        'subtype':None, 'fieldtype':self.ns.valid.get_groups_id("fieldtype", "float"),
                        'description':'link rate value', 'valuelist':None, 'addnew':0, 'visible':0, 'readonly':0}]
      for values in deffield_link:
        self.ns.connect.updateData("deffield", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)

      deffield_product = [{'id':self.ns.valid.get_id_from_refnumber('deffield','product_custpartnumber'),
                           'fieldname':'product_custpartnumber', 'nervatype':nervatype_product_id,
                           'subtype':None, 'fieldtype':self.ns.valid.get_groups_id("fieldtype", "customer"),
                           'description':'Customer Product No. (pricing)', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','product_alternative'),
                           'fieldname':'product_alternative', 'nervatype':nervatype_product_id,
                           'subtype':None, 'fieldtype':self.ns.valid.get_groups_id("fieldtype", "product"),
                           'description':'Alternative Product', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','product_element'),
                           'fieldname':'product_element', 'nervatype':nervatype_product_id,
                           'subtype':None, 'fieldtype':self.ns.valid.get_groups_id("fieldtype", "product"),
                           'description':'Element Product', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}]
      for values in deffield_product:
        self.ns.connect.updateData("deffield", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
        
      deffield_setting = [{'id':self.ns.valid.get_id_from_refnumber('deffield','printer_gsprint'),
                           'fieldname':'printer_gsprint', 'nervatype':nervatype_setting_id, 
                           'subtype':None, 'fieldtype':fieldtype_string, 
                           'description':'gsprint path (windows pdf printing)', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','printer_clienthost'),
                           'fieldname':'printer_clienthost', 'nervatype':nervatype_setting_id, 
                           'subtype':None, 'fieldtype':fieldtype_string, 
                           'description':'Client Additions host', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','printer_in_tool'),
                           'fieldname':'printer_in_tool', 'nervatype':nervatype_setting_id, 
                           'subtype':None, 'fieldtype':fieldtype_bool, 
                           'description':'show printers in tools', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','default_bank'),
                           'fieldname':'default_bank', 'nervatype':nervatype_setting_id, 
                           'subtype':None, 'fieldtype':fieldtype_string,
                           'description':'default bank place no.', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','default_chest'),
                           'fieldname':'default_chest', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_string,
                           'description':'default checkout place no.', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','default_warehouse'),
                           'fieldname':'default_warehouse', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_string,
                           'description':'default warehouse place no.', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','default_country'),
                           'fieldname':'default_country', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_string,
                           'description':'default country', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','default_lang'),
                           'fieldname':'default_lang', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_string,
                           'description':'default language', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','default_currency'),
                           'fieldname':'default_currency', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_string,
                           'description':'default currency', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','default_deadline'),
                           'fieldname':'default_deadline', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':self.ns.valid.get_groups_id("fieldtype", "integer"),
                           'description':'default deadline (payment)', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','default_paidtype'),
                           'fieldname':'default_paidtype', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_string,
                           'description':'default paidtype', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','default_unit'),
                           'fieldname':'default_unit', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_string,
                           'description':'default unit', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','default_taxcode'),
                           'fieldname':'default_taxcode', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_string,
                           'description':'default taxcode', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','false_bool'),
                           'fieldname':'false_bool', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_string,
                           'description':'false string', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','invoice_copy'),
                           'fieldname':'invoice_copy', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':self.ns.valid.get_groups_id("fieldtype", "integer"),
                           'description':'invoice copy', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','transyear'),
                           'fieldname':'transyear', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':self.ns.valid.get_groups_id("fieldtype", "integer"),
                           'description':'business year', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','true_bool'),
                           'fieldname':'true_bool', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_string,
                           'description':'true string', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','audit_control'),
                           'fieldname':'audit_control', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'set audit control', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','invoice_from_inventory'),
                           'fieldname':'invoice_from_inventory', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'invoice from inventory(yes) or order items(no)', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','set_outstock_enabled'),
                           'fieldname':'set_outstock_enabled', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'enabled inventory deficit', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','set_stocklimit_warning'),
                           'fieldname':'set_stocklimit_warning', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'inventory stock limit warning', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','not_logical_delete'),
                           'fieldname':'not_logical_delete', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'enabled trans deletion', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','show_partcustomer'),
                           'fieldname':'show_partcustomer', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'show customer number column', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','show_partnumber'),
                           'fieldname':'show_partnumber', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'show product number column', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','log_deleted'),
                           'fieldname':'log_deleted', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'enabled deleted log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','log_update'),
                           'fieldname':'log_update', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'enabled update log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','log_trans_closed'),
                           'fieldname':'log_trans_closed', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'enabled trans closed log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','log_login'),
                           'fieldname':'log_login', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'enabled userlogin', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','prenew_all'),
                           'fieldname':'prenew_all', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'set new row control', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0},
                          {'id':self.ns.valid.get_id_from_refnumber('deffield','presave_all'),
                           'fieldname':'presave_all', 'nervatype':nervatype_setting_id,
                           'subtype':None, 'fieldtype':fieldtype_bool,
                           'description':'set update row control', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}]
      for values in deffield_setting:
        self.ns.connect.updateData("deffield", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      fieldvalue_setting = [{'id':self.ns.valid.get_id_from_refnumber('fieldvalue','printer_gsprint'),
                             'fieldname':'printer_gsprint', 'ref_id':None, 'value':'C:\Progra~1\Ghostgum\gsview\gsprint', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','printer_clienthost'),
                             'fieldname':'printer_clienthost', 'ref_id':None, 'value':'localhost:8080', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','printer_in_tool'),
                             'fieldname':'printer_in_tool', 'ref_id':None, 'value':'false', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','default_bank'),
                             'fieldname':'default_bank', 'ref_id':None, 'value':'bank', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','default_chest'),
                             'fieldname':'default_chest', 'ref_id':None, 'value':'cash', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','default_warehouse'),
                             'fieldname':'default_warehouse', 'ref_id':None, 'value':'warehouse', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','default_country'),
                             'fieldname':'default_country', 'ref_id':None, 'value':'EU', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','default_lang'),
                             'fieldname':'default_lang', 'ref_id':None, 'value':'en', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','default_currency'),
                             'fieldname':'default_currency', 'ref_id':None, 'value':'EUR', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','default_deadline'),
                             'fieldname':'default_deadline', 'ref_id':None, 'value':'8', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','default_paidtype'),
                             'fieldname':'default_paidtype', 'ref_id':None, 'value':'transfer', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','default_unit'),
                             'fieldname':'default_unit', 'ref_id':None, 'value':'piece', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','default_taxcode'),
                             'fieldname':'default_taxcode', 'ref_id':None, 'value':'20%', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','false_bool'),
                             'fieldname':'false_bool', 'ref_id':None, 'value':'FALSE', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','invoice_copy'),
                             'fieldname':'invoice_copy', 'ref_id':None, 'value':'2', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','transyear'),
                             'fieldname':'transyear', 'ref_id':None, 'value':str(datetime.date.today().year), 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','true_bool'),
                             'fieldname':'true_bool', 'ref_id':None, 'value':'TRUE', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','audit_control'),
                             'fieldname':'audit_control', 'ref_id':None, 'value':'false', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','invoice_from_inventory'),
                             'fieldname':'invoice_from_inventory', 'ref_id':None, 'value':'false', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','set_outstock_enabled'),
                             'fieldname':'set_outstock_enabled', 'ref_id':None, 'value':'true', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','set_stocklimit_warning'),
                             'fieldname':'set_stocklimit_warning', 'ref_id':None, 'value':'false', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','not_logical_delete'),
                             'fieldname':'not_logical_delete', 'ref_id':None, 'value':'false', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','show_partcustomer'),
                             'fieldname':'show_partcustomer', 'ref_id':None, 'value':'false', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','show_partnumber'),
                             'fieldname':'show_partnumber', 'ref_id':None, 'value':'false', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','log_deleted'),
                             'fieldname':'log_deleted', 'ref_id':None, 'value':'true', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','log_update'),
                             'fieldname':'log_update', 'ref_id':None, 'value':'false', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','log_trans_closed'),
                             'fieldname':'log_trans_closed', 'ref_id':None, 'value':'false', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','log_login'),
                             'fieldname':'log_login', 'ref_id':None, 'value':'false', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','prenew_all'),
                             'fieldname':'prenew_all', 'ref_id':None, 'value':'false', 'notes':None},
                            {'id':self.ns.valid.get_id_from_refnumber('fieldvalue','presave_all'),
                             'fieldname':'presave_all', 'ref_id':None, 'value':'false', 'notes':None}]
      for values in fieldvalue_setting:
        self.ns.connect.updateData("fieldvalue", values=values, log_enabled=False, validate=False, insert_row=True, update_row=False)
      
      self.ns.db.commit()  
      return True
    except Exception, err:
      self.ns.db.rollback()
      self.ns.error_message = err
      return False
  
  def upgradeData(self):
    
    if not self.setIniData():
      return False
    
    return True
    
class LocalStore(object):
  #server side data
  def __init__(self, ns):
    self.ns = ns
  
  def formatParamType(self, ptype, value):
    if ((ptype =="string") or (ptype =="date")):
      return "'"+value+"'"
    if ((ptype=="integer") or (ptype=="number") or (ptype=="boolean")):
      return value
  
  def getAppEngine(self, app_engine):
    if app_engine=="google_sql":
      return "mysql"  
    else: 
      return app_engine
  
  def getSql(self, engine, sqlid, appl):
    sql = self.ns.lstore((self.ns.lstore[appl].sqlkey == sqlid)&(self.ns.lstore[appl].engine == self.getAppEngine(engine))).select()
    if len(sql)==0:
      sql = self.ns.lstore((self.ns.lstore[appl].sqlkey == sqlid)&(self.ns.lstore[appl].engine == "all")).select()
    return sql[0].sqlstr
    
  def setEngine(self, database, check_ndi=False, created=False, createdb=True):
    arows = self.ns.lstore(self.ns.lstore.databases.alias == database).select()
    if len(arows)==0:
      self.ns.error_message = self.ns.T("Missing database: ") + database
      return False
    if arows[0].request_enabled_lst==None or arows[0].request_enabled_lst=="":
      pass
    else:
      if str(arows[0].request_enabled_lst).find(self.ns.request.client)==-1:
        self.ns.error_message = self.ns.T("Invalid client IP address!")
        return False
    if check_ndi==True:
      if arows[0].ndi_enabled==False:
        self.ns.error_message = self.ns.T("Disabled interface connection!")
        return False
      else:
        self.ns.md5_password = arows[0].ndi_md5_password
        self.ns.encrypt_data = arows[0].ndi_encrypt_data
        self.ns.encrypt_password = arows[0].ndi_encrypt_password
    erow = self.ns.lstore(self.ns.lstore.engine.id == arows[0].engine_id).select()[0]
    conStr = erow.connection
    self.ns.engine = erow.ename
    
    for pardata in arows[0]:
      if str(arows[0][pardata]).startswith("$"):
        if os.environ.has_key(str(arows[0][pardata])[1:]):
          arows[0][pardata] = os.environ[str(arows[0][pardata])[1:]]
    
    if erow.ename in("sqlite"):
      conStr = conStr.replace("database", arows[0].dbname)
    elif erow.ename=="google_sql":
      conStr = conStr.replace("project:instance", arows[0].host)
      conStr = conStr.replace("database", arows[0].dbname)
    else:
      conStr = conStr.replace("database", arows[0].dbname)
      if arows[0].username==None or arows[0].username=="":
        conStr = conStr.replace("username:password@", "")
      else:
        conStr = conStr.replace("username", arows[0].username)
        conStr = conStr.replace("password", arows[0].password)
      if arows[0].port==0 or arows[0].port==None or arows[0].port=="":
        conStr = conStr.replace("localhost", arows[0].host)
      else:
        conStr = conStr.replace("localhost", arows[0].host+":"+str(arows[0].port))
    self.ns.connect.setConnect(uri=conStr, pool_size=0, createdb=createdb)
    if self.ns.db!=None:
      if self.ns.store.defineTable(create=created)==False:
        return False
      if self.ns.session.auth:
        if self.ns.session.auth.user:
          self.ns.employee = self.ns.db.employee(id=self.ns.session.auth.user.id)
    else:
      self.ns.error_message = self.ns.T("Could not connect to the database: ")+database
      return False
    return True
  
  def setSqlParams(self, sqlKey, sqlStr, whereStr, havingStr, paramList, rlimit=False, orderbyStr="", rowlimit=500, appl="nflex"):
    if (sqlStr == None): 
      sqlStr = self.getSql(self.getAppEngine(self.ns.engine), sqlKey, appl)
    else:
      sqlStr = str(sqlStr)
    if (paramList != None):
      for param in paramList:
        param["value"] = self.formatParamType(param["type"], param["value"])
        
        if (param["wheretype"]=="where"):
          whereStr = whereStr.replace(param["name"], str(param["value"]))
        if (param["wheretype"]=="having"):
          havingStr = havingStr.replace(param["name"], str(param["value"]))
        if (param["wheretype"]=="in"):
          sqlStr = sqlStr.replace(param["name"], str(param["value"]))
    sqlStr = sqlStr.replace("@where_str", str(whereStr))
    sqlStr = sqlStr.replace("@having_str", str(havingStr))
    sqlStr = sqlStr.replace("@orderby_str", str(orderbyStr))
    if (rlimit == True):
      sqlStr = sqlStr.replace(";", "")
      sqlStr = sqlStr + " limit " + str(rowlimit)
    return str(sqlStr)
                                
class NervaStore(object):
  error_message = ""
  md5_password = False
  valid = Validators(None)
  connect = DataConnect(None)
  store = DataStore(None)
  local = LocalStore(None)
  db = DAL(None)
  employee = employee()
      
  def __init__(self, request, session, T, lstore=None):
    self.request = request
    self.session = session
    self.T = T
    self.lstore = lstore
    self.valid = Validators(self)
    self.connect = DataConnect(self)
    self.store = DataStore(self)
    self.local = LocalStore(self)
    self.db = None
    self.employee = None
   

  

  
  
