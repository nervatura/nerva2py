# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2015, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""
from datetime import date, datetime

from gluon.html import TABLE, TR, TH, TD
from nerva2py.ordereddict import OrderedDict

class Ndi(object):
  ns = None
  log_enabled = True
  validate = True
  
  def __init__(self, NervaStore, log_enabled=True, validate=True):
    self.ns = NervaStore
    self.log_enabled = log_enabled
    self.validate = validate
    
  def getLogin(self, params):
    validator = {}
    validator["valid"] = False   
    validator["message"] = "OK"
    if not params.has_key("database"):
      validator["message"] = str(self.ns.T("Error|Missing login parameter:"))+" database" 
      return validator
    if not params.has_key("username"):
      validator["message"] = str(self.ns.T("Error|Missing login parameter:"))+" username"
      return validator 
    if not params.has_key("password"):
      validator["message"] = str(self.ns.T("Error|Missing login parameter:"))+" password"
      return validator
    if params["password"]=="":
      params["password"] = None
    if self.ns.db==None:
      if self.ns.local.setEngine(params["database"],True)==False:
        validator["valid"] = False
        if self.ns.error_message!="":
          validator["message"] = str(self.ns.error_message)
        else: 
          validator["message"] = str(self.ns.T("Could not connect to the database: ")+params["database"])
        return validator
    if self.ns.connect.setLogin(params["username"], params["password"])==False:
      validator["valid"] = False
      if self.ns.error_message!="":
        validator["message"] = str(self.ns.error_message)
      else: 
        validator["message"] = str(self.ns.T("Invalid user: ")+params["username"])
      return validator
    validator["valid"] = True   
    validator["message"] = "OK"
    return validator
  
  def callNdiFunc(self,fname,param,items):
    if fname.startswith("get"):
      return self.getView(param, items)
    elif callable(self.__getattribute__(fname)):
      func = self.__getattribute__(fname)
      if callable(func):
        return func(param, items)
      else:
        return "Error|Unknown datatype!"
    else:
      return "Error|Unknown datatype!"
        
  #----------------------------------------------------------------------------------------------------
  #----------------------------------------------------------------------------------------------------
  
  def set_valid_value(self, table, row, key):
    if row[key]=="": 
      row[key]=None
    elif self.ns.db[table].has_key(key):
      if self.ns.db[table][key].type=="date" and str(row[key]).find(" 00:00:00")>-1: 
        row[key] = str(row[key]).strip(" 00:00:00")
      
  def delete_transitem(self, params, data, nervatype):
    retvalue = "OK"
    for row in data:
      if not row.has_key("transnumber"):
        return "Error|Missing required parameter: transnumber"
      if not row.has_key("rownumber"):
        return "Error|Missing required parameter: rownumber"
      if not self.ns.db.trans(transnumber=row["transnumber"]):
        return "Error|Unknown transnumber: " + str(row["transnumber"])
      else:
        transtype = self.ns.db.groups(id=self.ns.db.trans(transnumber=row["transnumber"]).transtype).groupvalue
        if self.validate:
          audit = self.ns.connect.getObjectAudit("trans", transtype)
          if audit == "error":
            return "Error|" + str(self.ns.error_message)
          if audit != "all":
            return "Error|Disabled or readonly transtype: " + transtype
      refnumber = str(row["transnumber"])+"~"+str(row["rownumber"])
      if self.ns.connect.deleteData(nervatype=nervatype, ref_id=None, refnumber=refnumber):
        retvalue = retvalue+"|"+refnumber
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
      
  def update_address(self, params, data):
    retvalue = "OK"
    for row in data:
      nervatype_id=None
      if not row.has_key("nervatype"):
        return "Error|Missing required parameter: nervatype"
      else:
        nervatype_id= self.ns.valid.get_groups_id("nervatype",row["nervatype"])
        if not nervatype_id:
          return "Error|Unknown nervatype: "+row["nervatype"]
      if not row.has_key("refnumber"):
        return "Error|Missing required parameter: refnumber"
      if not row.has_key("rownumber"):
        row["rownumber"]=-1
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit(row["nervatype"])
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled" or audit=="readonly":
          return "Error|Disabled or readonly type: "+row["nervatype"]
      else:
        audit = "all"
      
      ref_id, values = None, {"id":None}
      ref_id = self.ns.valid.get_id_from_refnumber(row["nervatype"],row["refnumber"],params.has_key("use_deleted"))
      if not ref_id:
        return "Error|Unknown refnumber No: "+row["refnumber"]
      values["id"] = self.ns.valid.get_id_from_refnumber("address",row["nervatype"]+"/"+row["refnumber"]+"~"+str(row["rownumber"]),params.has_key("use_deleted"))
        
      if not values["id"]:
        if not params.has_key("insert_row"):
          return "Error|Unknown address and missing insert_row parameter"
        if audit!="all":
          return "Error|Restricted type: "+row["nervatype"]
        values["nervatype"] = nervatype_id
        values["ref_id"] = ref_id    
      for key in row.keys():
        if key!="rownumber" and key!="refnumber" and key!="nervatype":
          self.set_valid_value("address", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("address", values, log_enabled=self.log_enabled, validate=self.validate, 
                         insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      #nervatype/refnumber~rownumber
      retvalue = retvalue+"|"+row["nervatype"]+"/"+str(row["refnumber"])+"~"+str(row["rownumber"])
    return retvalue
  
  def delete_address(self, params, data):
    retvalue = "OK"
    for row in data:
      if not row.has_key("nervatype"):
        return "Error|Missing required parameter: nervatype"
      if not row.has_key("refnumber"):
        return "Error|Missing required parameter: refnumber"
      if not row.has_key("rownumber"):
        return "Error|Missing required parameter: rownumber"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit(row["nervatype"])
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit!="all":
          return "Error|Restricted type: "+row["nervatype"]
      
      refnumber = row["nervatype"]+"/"+row["refnumber"]+"~"+str(row["rownumber"])
      if self.ns.connect.deleteData(nervatype="address", ref_id=None, refnumber=refnumber):
        retvalue = retvalue+"|"+refnumber
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
  
  def update_barcode(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("product")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: product"
    else:
      audit = "all"
    for row in data:
      if not row.has_key("code"):
        return "Error|Missing required parameter: code"
      values = {"id":None}
      values["id"] = self.ns.valid.get_id_from_refnumber("barcode",row["code"],params.has_key("use_deleted"))
      
      if row.has_key("partnumber"):
        ref_id = self.ns.valid.get_id_from_refnumber("product",row["partnumber"],params.has_key("use_deleted"))
        if not ref_id:
          return "Error|Unknown partnumber No: "+str(row["partnumber"])
        values["product_id"] = ref_id
      if row.has_key("barcodetype"):
        barcodetype_id= self.ns.valid.get_groups_id("barcodetype",row["barcodetype"],params.has_key("use_deleted"))
        if not barcodetype_id:
          return "Error|Unknown barcodetype: "+str(row["barcodetype"]) 
        values["barcodetype"] = barcodetype_id
        
      if not values["id"]:
        values["code"] = row["code"]
        if not params.has_key("insert_row"):
          return "Error|Unknown barcode and missing insert_row parameter"
        if not row.has_key("partnumber"):
          return "Error|Missing required parameter: partnumber"
        if not row.has_key("barcodetype"):
          return "Error|Missing required parameter: barcodetype"
        if audit!="all":
          return "Error|Restricted type: product"
          
      for key in row.keys():
        if key!="code" and key!="partnumber" and key!="barcodetype":
          self.set_valid_value("barcode", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("barcode", values, log_enabled=self.log_enabled, validate=self.validate, 
                         insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["code"])
    return retvalue 
  
  def delete_barcode(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("product")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: product"   
    retvalue = "OK"
    for row in data:
      if not row.has_key("code"):
        return "Error|Missing required parameter: code"
      if self.ns.connect.deleteData(nervatype="barcode", ref_id=None, refnumber=str(row["code"])):
        retvalue = retvalue+"|"+str(row["code"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue  
  
  def update_contact(self, params, data):  
    retvalue = "OK"
    for row in data:
      nervatype_id=None
      if not row.has_key("nervatype"):
        return "Error|Missing required parameter: nervatype"
      else:
        nervatype_id= self.ns.valid.get_groups_id("nervatype",row["nervatype"])
        if not nervatype_id:
          return "Error|Unknown nervatype: "+row["nervatype"]
      if not row.has_key("refnumber"):
        return "Error|Missing required parameter: refnumber"
      if not row.has_key("rownumber"):
        row["rownumber"]=-1
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit(row["nervatype"])
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled" or audit=="readonly":
          return "Error|Disabled or readonly type: "+row["nervatype"]
      else:
        audit = "all"

      ref_id, values = None, {"id":None}
      ref_id = self.ns.valid.get_id_from_refnumber(row["nervatype"],row["refnumber"],params.has_key("use_deleted"))
      if not ref_id:
        return "Error|Unknown refnumber No: "+row["refnumber"]
      values["id"] = self.ns.valid.get_id_from_refnumber("contact",row["nervatype"]+"/"+row["refnumber"]+"~"+str(row["rownumber"]),params.has_key("use_deleted"))
      
      if not values["id"]:
        if not params.has_key("insert_row"):
          return "Error|Unknown contact and missing insert_row parameter"
        if audit!="all":
          return "Error|Restricted type: "+row["nervatype"]
        values["nervatype"] = nervatype_id
        values["ref_id"] = ref_id
      for key in row.keys():
        if key!="rownumber" and key!="refnumber" and key!="nervatype":
          self.set_valid_value("contact", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("contact", values, log_enabled=self.log_enabled, validate=self.validate, 
                         insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      #ref_nervatype/refnumber~rownumber
      retvalue = retvalue+"|"+row["nervatype"]+"/"+row["refnumber"]+"~"+str(row["rownumber"])
    return retvalue
    
  def delete_contact(self, params, data):
    retvalue = "OK"
    for row in data:
      if not row.has_key("nervatype"):
        return "Error|Missing required parameter: nervatype"
      if not row.has_key("refnumber"):
        return "Error|Missing required parameter: refnumber"
      if not row.has_key("rownumber"):
        return "Error|Missing required parameter: rownumber"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit(row["nervatype"])
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit!="all":
          return "Error|Restricted type: "+row["nervatype"]
      
      refnumber = row["nervatype"]+"/"+row["refnumber"]+"~"+str(row["rownumber"])
      if self.ns.connect.deleteData(nervatype="contact", ref_id=None, refnumber=refnumber):
        retvalue = retvalue+"|"+refnumber
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
  
  def update_currency(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: setting"
    else:
      audit = "all"
    for row in data:
      values = {"id":None}
      if not row.has_key("curr"):
        return "Error|Missing required parameter: curr"
      values["id"] = self.ns.valid.get_id_from_refnumber("currency",row["curr"],params.has_key("use_deleted"))
      if not values["id"]:
        if not params.has_key("insert_row"):
          return "Error|Unknown currency and missing insert_row parameter"
        if audit!="all":
          return "Error|Restricted type: setting"
        values["curr"] = row["curr"]
        if not row.has_key("description"):
          return "Error|Missing required parameter: description"
        values["description"] = row["description"]
      for key in row.keys():
        if key!="curr":
          self.set_valid_value("currency", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("currency", values, log_enabled=self.log_enabled, validate=self.validate, 
                         insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["curr"])
    return retvalue
    
  def delete_currency(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: setting"
    retvalue = "OK"
    for row in data:
      if not row.has_key("curr"):
        return "Error|Missing required parameter: curr"
      if self.ns.connect.deleteData(nervatype="currency", ref_id=None, refnumber=str(row["curr"])):
        retvalue = retvalue+"|"+str(row["curr"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue 
  
  def update_customer(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("customer")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: customer"
    else:
      audit = "all"      
    for row in data:
      values = {"id":None}
      if row.has_key("custnumber"):
        values["id"] = self.ns.valid.get_id_from_refnumber("customer",row["custnumber"],params.has_key("use_deleted"))
      if row.has_key("custtype"):
        if row["custtype"]=="company":
          row["custtype"] = self.ns.valid.get_groups_id("custtype","company")
        elif row["custtype"]=="private":
          row["custtype"] = self.ns.valid.get_groups_id("custtype","private")
        elif row["custtype"]=="other" :
          row["custtype"] = self.ns.valid.get_groups_id("custtype","other")
        elif row["custtype"]=="own":
          company = self.ns.valid.get_own_customer()
          if values["id"]:
            if values["id"]==company.id:
              row["custtype"] = self.ns.valid.get_groups_id("custtype","own")
            else:
              return "Error|Valid customertype: company, private, other "
          else:
            values["id"] = company.id
            row["custtype"] = self.ns.valid.get_groups_id("custtype","own")
        else:
          return "Error|Valid customertype: company, private, other "
      if not values["id"]:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: customer"
          if not row.has_key("custname"):
            return "Error|Missing required parameter: custname"
          if not row.has_key("custnumber"):
            row["custnumber"] = self.ns.connect.nextNumber("custnumber")
          values["id"] = self.ns.valid.get_id_from_refnumber("customer",row["custnumber"],params.has_key("use_deleted"))
          if values["id"]:
            return "Error|New customer, but the retrieved customer No. is reserved: "+str(row["custnumber"])
          values["custnumber"] = row["custnumber"]
          values["custname"] = row["custname"]
          if row.has_key("custtype"):
            values["custtype"] = row["custtype"]
          else:
            values["custtype"] = self.ns.valid.get_groups_id("custtype","company")    
        else:
          return "Error|Missing custnumber and insert_row parameter"  
      
      for key in row.keys():
        if key!="custnumber":
          self.set_valid_value("customer", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("customer", values, log_enabled=self.log_enabled, validate=self.validate, 
                         insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+row["custnumber"]
    return retvalue
  
  def delete_customer(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("customer")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: customer"
    retvalue = "OK"
    for row in data:
      if not row.has_key("custnumber"):
        return "Error|Missing required parameter: custnumber"
      if self.ns.connect.deleteData(nervatype="customer", ref_id=None, refnumber=str(row["custnumber"])):
        retvalue = retvalue+"|"+str(row["custnumber"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue 
  
  def update_deffield(self, params, data):  
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: setting"
    else:
      audit = "all"
    for row in data:
      values = {"id":None}
      if not row.has_key("fieldname"):
        return "Error|Missing required parameter: fieldname"
      if row.has_key("valuelist"):
        row["valuelist"] = str(row["valuelist"]).replace("~", "|")
      
      values["id"] = self.ns.valid.get_id_from_refnumber("deffield",row["fieldname"],params.has_key("use_deleted"))
      if not values["id"]:
        if not params.has_key("insert_row"):
          return "Error|Unknown deffield and missing insert_row parameter"
        if audit!="all":
          return "Error|Restricted type: setting"
        if not row.has_key("nervatype"):
          return "Error|Missing required parameter: nervatype"
        else:
          nervatype = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==row["nervatype"])
                                 & self.ns.db.groups.groupvalue.belongs((
                                 'address', 'barcode', 'contact', 'currency', 'customer', 'employee', 'event', 'item', 'link', 
                                 'log', 'movement', 'payment', 'price', 'place', 'product', 'project', 'rate', 'tax',
                                 'tool', 'trans', 'setting'))).select().as_list()
          if len(nervatype)==0:
            return "Error|Unknown nervatype: "+str(row["nervatype"])
          values["nervatype"] = nervatype[0]["id"]
        if not row.has_key("fieldtype"):
          return "Error|Missing required parameter: fieldtype"
        else:
          values["fieldtype"] = self.ns.valid.get_groups_id("fieldtype",row["fieldtype"])
          if not values["fieldtype"]:
            return "Error|Unknown fieldtype: "+str(row["fieldtype"])
        values["fieldname"] = row["fieldname"]
        if row.has_key("description"):
          values["description"] = row["description"]
        else:
          values["description"] = row["fieldname"]
      if row.has_key("subtype"):
        if row["subtype"]!="":
          subtype = self.ns.db((self.ns.db.groups.groupname.belongs(("custtype","placetype","protype","toolgroup","transtype")))
                             &(self.ns.db.groups.groupvalue==row["subtype"])).select()
          if len(subtype)==0:
            return "Error|Unknown subtype: "+str(row["subtype"])
          else:
            row["subtype"] = subtype[0]["id"]
        else:
          row["subtype"] = None
      for key in row.keys():
        if key!="fieldname" and key!="nervatype" and key!="fieldtype":
          self.set_valid_value("deffield", row, key)
          values[key]= row[key]
          
      row_id = self.ns.connect.updateData("deffield", values, log_enabled=self.log_enabled, validate=self.validate, 
                         insert_row=params.has_key("insert_row"), insert_field=False)
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["fieldname"])
    return retvalue
  
  def delete_deffield(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: setting"
    retvalue = "OK"
    for row in data:
      if not row.has_key("fieldname"):
        return "Error|Missing required parameter: fieldname"
      if self.ns.connect.deleteData(nervatype="deffield", ref_id=None, refnumber=str(row["fieldname"])):
        retvalue = retvalue+"|"+str(row["fieldname"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue 
  
  def update_employee(self, params, data):  
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("employee")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: employee"
    else:
      audit = "all"
    for row in data:
      values = {"id":None}
      if row.has_key("empnumber"):
        values["id"] = self.ns.valid.get_id_from_refnumber("employee",row["empnumber"],params.has_key("use_deleted"))
      if row.has_key("usergroup"):
        row["usergroup"] = self.ns.valid.get_groups_id("usergroup",row["usergroup"],params.has_key("use_deleted"))
        if not row["usergroup"]:
          return "Error|Unknown usergroup: "+row["usergroup"]
      if row.has_key("department"):
        if row["department"]!="":
          row["department"] = self.ns.valid.get_groups_id("department",row["department"],params.has_key("use_deleted"))
          if not row["department"]:
            return "Error|Unknown department: "+row["department"]
      if row.has_key("username") and values["id"]:
        if self.ns.db.employee(id=values["id"])["username"]==row["username"]:
          del row["username"]
      if not values["id"]:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: employee"
          if not row.has_key("usergroup"):
            return "Error|Missing required parameter: usergroup"
          if not row.has_key("empnumber"):
            row["empnumber"] = self.ns.connect.nextNumber("empnumber")
          values["id"] = self.ns.valid.get_id_from_refnumber("employee",row["empnumber"],params.has_key("use_deleted"))
          if values["id"]:
            return "Error|New employee, but the retrieved employee No. is reserved: "+str(row["empnumber"])
          values["empnumber"] = row["empnumber"]
          values["usergroup"] = row["usergroup"]
        else:
          return "Error|Missing empnumber and insert_row parameter"          
        
      for key in row.keys():
        if key!="empnumber":
          self.set_valid_value("employee", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("employee", values, log_enabled=self.log_enabled, validate=self.validate, 
                         insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+row["empnumber"]
    return retvalue
  
  def delete_employee(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("employee")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: employee"
    retvalue = "OK"
    for row in data:
      if not row.has_key("empnumber"):
        return "Error|Missing required parameter: empnumber"
      if self.ns.connect.deleteData(nervatype="employee", ref_id=None, refnumber=str(row["empnumber"])):
        retvalue = retvalue+"|"+str(row["empnumber"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
  
  def update_event(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("event")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: event"
    else:
      audit = "all"
    for row in data:
      values = {"id":None}    
      if row.has_key("calnumber"):
        values["id"] = self.ns.valid.get_id_from_refnumber("event",row["calnumber"],params.has_key("use_deleted"))
      if not values["id"]:  
        if params.has_key("insert_row"):
          if not row.has_key("nervatype"):
            return "Error|Missing required parameter: nervatype"
          else:
            values["nervatype"]= self.ns.valid.get_groups_id("nervatype",row["nervatype"])
            if not values["nervatype"]:
              return "Error|Unknown nervatype: "+row["nervatype"]
          if not row.has_key("refnumber"):
            return "Error|Missing required parameter: refnumber"
          if audit!="all":
            return "Error|Restricted type: event"
          
          values["ref_id"] = self.ns.valid.get_id_from_refnumber(row["nervatype"],row["refnumber"],params.has_key("use_deleted"))
          if not values["ref_id"]:
            return "Error|Unknown refnumber No: "+row["refnumber"]
        
          if not row.has_key("calnumber"):
            row["calnumber"] = self.ns.connect.nextNumber("calnumber")
          values["id"] = self.ns.valid.get_id_from_refnumber("event",row["calnumber"],params.has_key("use_deleted"))
          if values["id"]:
            return "Error|New event, but the retrieved event No. is reserved: "+str(row["calnumber"])
          values["calnumber"]=row["calnumber"]  
        else:
          return "Error|Missing calnumber and insert_row parameter"  
      if row.has_key("eventgroup"):
        if row["eventgroup"]!="":
          eventgroup_id=None
          eventgroup_id = self.ns.valid.get_groups_id("eventgroup",row["eventgroup"],params.has_key("use_deleted"))
          if eventgroup_id:
            row["eventgroup"] = eventgroup_id
          else:
            row["eventgroup"] = self.ns.connect.updateData("groups", {"groupname":"eventgroup", "groupvalue":row["eventgroup"]}, 
                                        log_enabled=self.log_enabled, validate=self.validate, insert_row=True, insert_field=False)
            if not row["eventgroup"]:
              return "Error|"+str(self.ns.error_message)
      
      for key in row.keys():
        if key!="calnumber" and key!="nervatype" and key!="refnumber":
          self.set_valid_value("event", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("event", values, log_enabled=self.log_enabled, validate=self.validate, 
                         insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+row["calnumber"]
    return retvalue
    
  def delete_event(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("event")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: event"
    retvalue = "OK"
    for row in data:
      if not row.has_key("calnumber"):
        return "Error|Missing required parameter: calnumber"
      if self.ns.connect.deleteData(nervatype="event", ref_id=None, refnumber=str(row["calnumber"])):
        retvalue = retvalue+"|"+str(row["calnumber"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
  
  def update_fieldvalue(self, params, data):
    retvalue = "OK"
    for row in data:
      values,deffield_id = {},None
      if not row.has_key("fieldname"):
        return "Error|Missing required parameter: fieldname"
      values["fieldname"] = str(row["fieldname"]).split("~")[0]
      if not row.has_key("value"):
        return "Error|Missing required parameter: value"
      values["value"] = row["value"]
      if row.has_key("notes"):
        values["notes"] = str(row["notes"])
        
      deffield_id = self.ns.valid.get_id_from_refnumber("deffield",values["fieldname"],params.has_key("use_deleted"))
      if not deffield_id:
        return "Error|Unknown fieldname: "+str(row["fieldname"])
      nervatype = self.ns.db.groups(id=self.ns.db.deffield(id=deffield_id).nervatype).groupvalue
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit(nervatype)
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled" or audit=="readonly":
          return "Error|Disabled or readonly type: "+nervatype
      
      if len(str(row["fieldname"]).split("~"))>1:
        try:
          row["rownumber"] = int(str(row["fieldname"]).split("~")[1])
          if row["rownumber"]<1: row["rownumber"]=1
        except Exception:
          row["rownumber"] = 1
      elif row.has_key("rownumber"):
        try:
          row["rownumber"] = int(row["rownumber"])
          if row["rownumber"]<1: row["rownumber"]=1
        except Exception:
          row["rownumber"] = 1
        row["fieldname"] = str(row["fieldname"])+"~"+str(row["rownumber"])
        
      if nervatype=="setting":
        values["ref_id"] = None
      else:
        if not row.has_key("refnumber"):
          return "Error|Missing required parameter: refnumber"
        values["ref_id"] = self.ns.valid.get_id_from_refnumber(nervatype,row["refnumber"],params.has_key("use_deleted"))
        if not values["ref_id"]:
          return "Error|"+str(self.ns.error_message)
        row["fieldname"] = str(row["refnumber"])+"~~"+str(row["fieldname"])
      
      values["id"] = self.ns.valid.get_id_from_refnumber("fieldvalue",row["fieldname"],params.has_key("use_deleted"))  
      
      row_id = self.ns.connect.updateData("fieldvalue", values, log_enabled=self.log_enabled, validate=self.validate, 
                         insert_row=params.has_key("insert_row"), insert_field=False)
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["fieldname"])
    return retvalue
  
  def delete_fieldvalue(self, params, data):
    retvalue = "OK"
    for row in data:
      if not row.has_key("fieldname"):
        return "Error|Missing required parameter: fieldname"
      deffields = self.ns.db((self.ns.db.deffield.deleted==0)&(self.ns.db.deffield.fieldname==str(row["fieldname"]))).select()
      if len(deffields)==0:
        return "Error|Unknown fieldname: "+str(row["fieldname"])
      nervatype = self.ns.db.groups(id=deffields[0].nervatype).groupvalue
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit(nervatype)
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled" or audit=="readonly":
          return "Error|Disabled or readonly type: "+nervatype
      
      if row.has_key("refnumber"):
        row["fieldname"] = str(row["refnumber"])+"~~"+str(row["fieldname"])
      if row.has_key("rownumber"):
        try:
          row["rownumber"] = int(row["rownumber"])
        except Exception:
          row["rownumber"] = 1
        row["fieldname"] = str(row["fieldname"])+"~"+str(row["rownumber"])      
      if self.ns.connect.deleteData(nervatype="fieldvalue", ref_id=None, refnumber=str(row["fieldname"])):
        retvalue = retvalue+"|"+str(row["fieldname"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
  
  def update_groups(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: setting"
    else:
      audit = "all"
    for row in data:
      values = {"id":None}
      if not row.has_key("groupname"):
        return "Error|Missing required parameter: groupname"
      if not row.has_key("groupvalue"):
        return "Error|Missing required parameter: groupvalue"
      values["id"]= self.ns.valid.get_groups_id(row["groupname"],row["groupvalue"],params.has_key("use_deleted"))
      if not values["id"]:
        if audit!="all":
          return "Error|Restricted type: setting"
        values["groupname"]=row["groupname"]
        values["groupvalue"]=row["groupvalue"]
      for key in row.keys():
        if key!="groupname" and key!="groupvalue":
          self.set_valid_value("groups", row, key)
          values[key]= row[key]
      row_id = self.ns.connect.updateData("groups", values, log_enabled=self.log_enabled, validate=self.validate, 
                         insert_row=params.has_key("insert_row"), insert_field=False)
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      #groupname~groupvalue
      retvalue = retvalue+"|"+str(row["groupname"])+"~"+str(row["groupvalue"])
    return retvalue
    
  def delete_groups(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: setting"
    for row in data:
      if not row.has_key("groupname"):
        return "Error|Missing required parameter: groupname"
      if not row.has_key("groupvalue"):
        return "Error|Missing required parameter: groupvalue"
      if row["groupname"]=="usergroup":
        return "Error|Invalid groupname: usergroup"
      
      refnumber = str(row["groupname"])+"~"+str(row["groupvalue"])
      if self.ns.connect.deleteData(nervatype="groups", ref_id=None, refnumber=refnumber):
        retvalue = retvalue+"|"+refnumber
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
    
  def update_item(self, params, data):    
    retvalue = "OK"
    for row in data:
      values = {"id":None}
      item_,trans_id,curr,prod_,tax_id = None,None,None,None,None
      if not row.has_key("rownumber"):
        return "Error|Missing required parameter: rownumber"
      if row.has_key("transnumber"):     
        trans_id = self.ns.valid.get_id_from_refnumber("trans",row["transnumber"],params.has_key("use_deleted"))
        if not trans_id:
          return "Error|Unknown transnumber: "+str(row["transnumber"])
        curr = self.ns.db.trans(id=trans_id).curr
        values["id"] = self.ns.valid.get_id_from_refnumber("item",row["transnumber"]+"~"+str(row["rownumber"]),params.has_key("use_deleted"))
        if values["id"]: 
          item_=self.ns.db.item(id=values["id"])
          values["qty"] = item_["qty"]
          values["discount"] = item_["discount"]
          values["tax_id"] = item_["tax_id"]
      else:
        return "Error|Missing required parameter: transnumber"
      
      transtype= self.ns.db.groups(id=self.ns.db.trans(id=trans_id).transtype).groupvalue
      if self.validate:
        audit = self.ns.connect.getObjectAudit("trans",transtype)
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled" or audit=="readonly":
          return "Error|Disabled or readonly transtype: "+transtype
      else:
        audit = "all"
    
      if row.has_key("partnumber"):
        prod_ = self.ns.valid.get_id_from_refnumber("product",row["partnumber"],params.has_key("use_deleted"))
        if not prod_:
          return "Error|Unknown partnumber No: "+str(row["partnumber"])
        else:
          prod_=self.ns.db.product(id=prod_)
        values["product_id"] = prod_["id"]
        if not item_:
          values["unit"] = prod_["unit"]
          values["tax_id"] = prod_["tax_id"]
          values["description"] = prod_["description"]
        del row["partnumber"]
        
      if not item_:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: "+transtype
          if not values.has_key("product_id"):
            return "Error|Missing required parameter: partnumber"
          values["trans_id"] = trans_id
          values["qty"] = 1
          values["discount"] = 0
        else:
          return "Error|Missing item and no insert_row parameter"  
      
      if row.has_key("taxcode"):
        tax_id = self.ns.valid.get_id_from_refnumber("tax",row["taxcode"],params.has_key("use_deleted"))
        if tax_id:
          values["tax_id"] = tax_id
          del row["taxcode"] 
        else:
          return "Error|Unknown taxcode: "+row["taxcode"]
      if row.has_key("discount"):
        if str(row["discount"]).replace(".", "").isdigit()==False:
          return "Error|Invalid discount type!"
        if float(row["discount"])<0 or float(row["discount"])>100:
          return "Error|Valid discount value: 0-100"     
      if row.has_key("inputmode"):
        if not row.has_key("inputvalue"):
          return "Error|Set inputmode, but missing required parameter: inputvalue"
        if row.has_key("qty"):
          try:
            values["qty"] = float(row["qty"])
          except Exception:
            pass
        if row.has_key("discount"):
          try:
            values["discount"] = float(row["discount"])
          except Exception:
            pass
        
        tax_ = self.ns.db.tax(id=values["tax_id"])  
        currency_ = self.ns.db.currency(curr=curr)
        if row["inputmode"]=="fxprice":
          values["fxprice"] = float(row["inputvalue"])
          values["netamount"] = round(values["fxprice"]*(1-values["discount"]/100)*values["qty"],currency_["digit"])
          values["vatamount"] = round(values["netamount"]*tax_["rate"],currency_["digit"])
          values["amount"] = values["netamount"] + values["vatamount"]
        elif row["inputmode"]=="netamount":
          values["netamount"] = float(row["inputvalue"])
          if values["qty"]==0:
            values["fxprice"] = 0
            values["vatamount"] = 0
          else:
            values["fxprice"] = round(values["netamount"]/(1-values["discount"]/100)/values["qty"],currency_["digit"])
            values["vatamount"] = round(values["netamount"]*tax_["rate"],currency_["digit"])
          values["amount"] = values["netamount"] + values["vatamount"]
        elif row["inputmode"]=="amount":
          values["amount"] = float(row["inputvalue"])
          if values["qty"]==0:
            values["fxprice"] = 0
            values["netamount"] = 0
            values["vatamount"] = 0
          else:
            values["netamount"] = round(values["amount"]/(1+tax_["rate"]),currency_["digit"])
            values["vatamount"] = values["amount"] - values["netamount"]
            values["fxprice"] = round(values["netamount"]/(1-values["discount"]/100)/values["qty"],currency_["digit"])
        else:
          return "Error|Unknown inputmode: "+row["inputmode"]+" Valid values: fxprice, netamount, amount"
        del row["inputmode"]
        del row["inputvalue"]
        
      for key in row.keys():
        if key!="rownumber" and key!="transnumber":
          self.set_valid_value("item", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("item", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["transnumber"])+"~"+str(row["rownumber"])
    return retvalue
  
  def delete_item(self, params, data):
    return self.delete_transitem(params, data, "item")
  
  def check_link(self, params, row):
    retval={"id":None, "refnumber":None, "nervatype_1":None, "refnumber_1":None, "nervatype_2":None, "refnumber_2":None, "audit":None,"error":None}
    
    if not row.has_key("nervatype1"):
      retval["error"] = "Error|Missing required parameter: nervatype1"
      return retval
    if not row.has_key("refnumber1"):
      retval["error"] = "Error|Missing required parameter: refnumber1"
      return retval
    if not row.has_key("nervatype2"):
      retval["error"] = "Error|Missing required parameter: nervatype2"
      return retval
    if not row.has_key("refnumber2"):
      retval["error"] = "Error|Missing required parameter: refnumber2"
      return retval
    
    retval["nervatype_1"] = self.ns.valid.get_groups_id("nervatype",row["nervatype1"])
    if not retval["nervatype_1"]:
      retval["error"] = "Error|Unknown nervatype: "+row["nervatype1"]
      return retval
    
    retval["refnumber_1"] = self.ns.valid.get_id_from_refnumber(row["nervatype1"],row["refnumber1"],params.has_key("use_deleted"))
    if not retval["refnumber_1"]:
      retval["error"] = "Error|Unknown refnumber No: "+row["refnumber1"]
      return retval
    
    retval["nervatype_2"] = self.ns.valid.get_groups_id("nervatype",row["nervatype2"])
    if not retval["nervatype_2"]:
      retval["error"] = "Error|Unknown nervatype: "+row["nervatype2"]
      return retval
    
    retval["refnumber_2"] = self.ns.valid.get_id_from_refnumber(row["nervatype2"],row["refnumber2"],params.has_key("use_deleted"))
    if not retval["refnumber_2"]:
      retval["error"] = "Error|Unknown refnumber No: "+row["refnumber2"]
      return retval
    
    retval["audit"] = "all"
    if row["nervatype1"] in("trans","item","movement","payment"):
      if row["nervatype1"]=="trans":
        transtype = self.ns.db.groups(id=self.ns.db.trans(id=retval["refnumber_1"]).transtype).groupvalue
      else:
        transtype = self.ns.db.groups(id=self.ns.db.trans(id=self.ns.db[row["nervatype1"]](id=retval["refnumber_1"]).trans_id).transtype).groupvalue
      if self.validate:
        retval["audit"] = self.ns.connect.getObjectAudit("trans",transtype)
    else:
      if self.validate:
        retval["audit"] = self.ns.connect.getObjectAudit(row["nervatype1"])
    if retval["audit"]=="error":
      retval["error"] = "Error|"+str(self.ns.error_message)
      return retval
    if retval["audit"]=="disabled" or retval["audit"]=="readonly":
      retval["error"] = "Error|Disabled or readonly type"
      return retval
    
    audit_2 = "all"
    if row["nervatype2"] in("trans","item","movement","payment"):
      if row["nervatype2"]=="trans":
        transtype = self.ns.db.groups(id=self.ns.db.trans(id=retval["refnumber_2"]).transtype).groupvalue
      else:
        transtype = self.ns.db.groups(id=self.ns.db.trans(id=self.ns.db[row["nervatype2"]](id=retval["refnumber_2"]).trans_id).transtype).groupvalue
      if self.validate:
        audit_2 = self.ns.connect.getObjectAudit("trans",transtype)
    else:
      if self.validate:
        audit_2 = self.ns.connect.getObjectAudit(row["nervatype2"])
    if audit_2=="error":
      retval["error"] = "Error|"+str(self.ns.error_message)
      return retval
    if audit_2=="disabled" or audit_2=="readonly":
      retval["error"] = "Error|Disabled or readonly type"
      return retval
    if audit_2!="all":
      retval["audit"] = audit_2
    
    retval["refnumber"] = row["nervatype1"]+"~"+row["refnumber1"]+"~~"+row["nervatype2"]+"~"+row["refnumber2"]
    retval["id"] = self.ns.valid.get_id_from_refnumber("link",retval["refnumber"],params.has_key("use_deleted"))            
    return retval
    
  def update_link(self, params, data):
    retvalue = "OK"
    for row in data:
      values = {}
      check_row = self.check_link(params,row)
      if check_row["error"]:
        return check_row["error"]

      if not check_row["id"]:
        if check_row["audit"]!="all":
          return "Error|Restricted type "
        values["nervatype_1"] = check_row["nervatype_1"]
        values["ref_id_1"] = check_row["refnumber_1"]
        values["nervatype_2"] = check_row["nervatype_2"]
        values["ref_id_2"] = check_row["refnumber_2"]
      else:
        values["id"] = check_row["id"]
      for key in row.keys():
        if key!="nervatype1" and key!="refnumber1" and key!="nervatype2" and key!="refnumber2":
          self.set_valid_value("link", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("link", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      #nervatype_1~refnumber_1~~nervatype_2~refnumber_2
      retvalue = retvalue+"|"+str(check_row["refnumber"])
    return retvalue 
  
  def delete_link(self, params, data):
    retvalue = "OK"
    for row in data:
      check_row = self.check_link(params,row)
      if check_row["error"]:
        return check_row["error"]
      if check_row["id"]:
        if self.ns.connect.deleteData(nervatype="link", ref_id=check_row["id"], refnumber=None):
          retvalue = retvalue+"|"+check_row["refnumber"]
        else:
          return "Error|"+str(self.ns.error_message)
    return retvalue
  
  def update_log(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: setting"
    retvalue = "OK"
    for row in data:
      values = {"id":None}
      
      if not row.has_key("crdate"):
        values["crdate"] = datetime.now()
      else:
        values["crdate"] = row["crdate"]
          
      if not row.has_key("empnumber"):
        if not self.ns.employee:
          return "Error|Missing required parameter: empnumber"
        else:
          values["employee_id"] = self.ns.employee["id"]
          row["empnumber"] = self.ns.employee["empnumber"]
      else:
        if self.ns.db.employee(empnumber=row["empnumber"]):
          values["employee_id"] = self.ns.db.employee(empnumber=row["empnumber"]).id
        else:
          return "Error|Unknown empnumber: "+row["empnumber"]
      
      values["id"] = self.ns.valid.get_id_from_refnumber("log",row["empnumber"]+"~"+str(values["crdate"]),params.has_key("use_deleted"))
      del row["empnumber"]
        
      if row.has_key("logstate"):
        values["logstate"]= self.ns.valid.get_groups_id("logstate",row["logstate"],params.has_key("use_deleted"))
        if not values["logstate"]:
          return "Error|Unknown logstate: "+row["logstate"]
        if row["logstate"] not in("login","logout"):
          if not row.has_key("nervatype") and not values["id"]:
            return "Error|Missing required parameter: nervatype"
        else:
          if row.has_key("nervatype"): del row["nervatype"]
      elif not values["id"]:
        return "Error|Missing required parameter: logstate"
                         
      nervatype = None
      ref_id = None
      if row.has_key("nervatype"):
        nervatype= self.ns.valid.get_groups_id("nervatype",row["nervatype"])
        if not nervatype:
          return "Error|Unknown nervatype: "+row["nervatype"]
        else:
          values["nervatype"] = nervatype
        
        if not row.has_key("refnumber"):
          return "Error|Missing required parameter: refnumber"
        
        ref_id = self.ns.valid.get_id_from_refnumber(row["nervatype"],row["refnumber"],params.has_key("use_deleted"))
        if not ref_id:
          return "Error|"+str(self.ns.error_message)
        else:
          values["ref_id"] = ref_id
          del row["refnumber"]
      else:
        if row.has_key("refnumber"):
          if row["refnumber"]!="":
            return "Error|Missing required parameter: nervatype"
      
      for key in row.keys():
        if not self.ns.db.log.has_key(key) :
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("log", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(self.ns.db.employee(id=values["employee_id"]).empnumber)+"~"+str(values["crdate"])      
    return retvalue
  
  def delete_log(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: setting"
    for row in data:
      if not row.has_key("empnumber"):
        if not self.ns.employee:
          return "Error|Missing required parameter: empnumber"
        else:
          row["empnumber"] = self.ns.employee["empnumber"]
      else:
        if not self.ns.db.employee(empnumber=row["empnumber"]):
          return "Error|Unknown empnumber: "+row["empnumber"]
      if not row.has_key("crdate"):
        return "Error|Missing required parameter: crdate"
      
      refnumber = row["empnumber"]+"~"+row["crdate"]
      if self.ns.connect.deleteData(nervatype="log", ref_id=None, refnumber=refnumber):
        retvalue = retvalue+"|"+refnumber
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
      
  def update_movement(self, params, data):
    retvalue = "OK"
    for row in data:
      values = {"id":None,"trans_id":None}
      if not row.has_key("rownumber"):
        return "Error|Missing required parameter: rownumber"
      if row.has_key("transnumber"):
        values["trans_id"] = self.ns.valid.get_id_from_refnumber("trans",row["transnumber"],params.has_key("use_deleted"))
        if not values["trans_id"]:
          return "Error|Unknown transnumber: "+str(row["transnumber"])
        values["id"] = self.ns.valid.get_id_from_refnumber("movement",row["transnumber"]+"~"+str(row["rownumber"]),params.has_key("use_deleted"))
      else:
        return "Error|Missing required parameter: transnumber"
      
      transtype= self.ns.db.groups(id=self.ns.db.trans(id=values["trans_id"]).transtype).groupvalue
      if self.validate:
        audit = self.ns.connect.getObjectAudit("trans",transtype)
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled" or audit=="readonly":
          return "Error|Disabled or readonly transtype: "+transtype
      else:
        audit = "all"
      
      if not values["id"]:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: "+transtype
          if not row.has_key("movetype"):
            return "Error|Missing required parameter: movetype"
          else:
            values["movetype"] = self.ns.valid.get_groups_id("movetype",row["movetype"])
            if not values["movetype"]:
              return "Error|Unknown movetype: "+str(row["movetype"])+". Valid values: inventory, store, tool, head, plan."
            
            if (row["movetype"] in("store","inventory","formula","production")) and not row.has_key("partnumber"):
              return "Error|Missing required parameter: partnumber"
            if row["movetype"]=="tool" and not row.has_key("serial"):
              return "Error|Missing required parameter: serial"
            if (row["movetype"] in("store","inventory","production")) and not row.has_key("planumber"):
              return "Error|Missing required parameter: planumber"
            del row["movetype"]
          fmt = "%Y.%m.%d 00:00:00"
          values["shippingdate"] = datetime.strptime(date.strftime(datetime.now(),fmt),fmt)
        else:
          return "Error|Missing item and no insert_row parameter"
      if row.has_key("movetype") and values["id"]:
        if self.ns.valid.get_groups_id("movetype",row["movetype"])!=self.ns.db.movement(id=values["id"]).movetype:
          return "Error|Readonly parameter: movetype"
        del row["movetype"]
      if row.has_key("partnumber"):
        if row["partnumber"]!="":
          values["product_id"] = self.ns.valid.get_id_from_refnumber("product",row["partnumber"],params.has_key("use_deleted"))
          if not values["product_id"]:
            return "Error|Unknown partnumber No: "+str(row["partnumber"])
        else:
          values["product_id"] = None
        del row["partnumber"]
      if row.has_key("serial"):
        if row["serial"]!="":
          values["tool_id"] = self.ns.valid.get_id_from_refnumber("tool",row["serial"],params.has_key("use_deleted"))
          if not values["tool_id"]:
            return "Error|Unknown serial: "+str(row["serial"])
        else:
          values["tool_id"] = None
        del row["serial"]
      if row.has_key("planumber"):
        if row["planumber"]!="":
          values["place_id"] = self.ns.valid.get_id_from_refnumber("place",row["planumber"],params.has_key("use_deleted"))
          if not values["place_id"]:
            return "Error|Unknown planumber No: "+str(row["planumber"])
        else:
          values["place_id"] = None
        del row["planumber"]
        
      for key in row.keys():
        if key!="rownumber" and key!="transnumber":
          self.set_valid_value("movement", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("movement", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["transnumber"])+"["+str(row["rownumber"])+"]"
    return retvalue
    
  def delete_movement(self, params, data):
    return self.delete_transitem(params, data, "movement")
  
  def update_numberdef(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: setting"
    else:
      audit = "all"
    for row in data:
      values = {"id":None}
      if not row.has_key("numberkey"):
        return "Error|Missing required parameter: numberkey"
      else:
        values["id"] = self.ns.valid.get_id_from_refnumber("numberdef",row["numberkey"],params.has_key("use_deleted"))

      if not values["id"]:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: setting"
          values["numberkey"] = row["numberkey"]
        else:
          return "Error|Missing id and no insert_row parameter"
      
      for key in row.keys():
        if key!="numberkey":
          self.set_valid_value("numberdef", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("numberdef", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=False)
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["numberkey"])
    return retvalue
  
  def delete_numberdef(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: setting"
    retvalue = "OK"
    for row in data:
      if not row.has_key("numberkey"):
        return "Error|Missing required parameter: numberkey"
      if self.ns.connect.deleteData(nervatype="numberdef", ref_id=None, refnumber=str(row["numberkey"])):
        retvalue = retvalue+"|"+str(row["numberkey"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue 
  
  def update_pattern(self, params, data):
    retvalue = "OK"
    for row in data:
      values = {"id":None}
      if not row.has_key("description"):
        return "Error|Missing required parameter: description"
      else:
        values["id"] = self.ns.valid.get_id_from_refnumber("pattern",row["description"],params.has_key("use_deleted"))
      if row.has_key("transtype"):
        values["transtype"] = self.ns.valid.get_groups_id("transtype",row["transtype"])
        if not values["transtype"]:
          return "Error|Unknown transtype: "+str(row["transtype"])
      else:
        if values["id"]:
          row["transtype"] = self.ns.db.groups(id=self.ns.db.pattern(id=values["id"]).transtype).groupvalue
        else:
          return "Error|Missing required parameter: transtype"
        
      if self.validate:
        audit = self.ns.connect.getObjectAudit("trans",row["transtype"])
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled" or audit=="readonly":
          return "Error|Disabled or readonly transtype: "+row["transtype"]
      else:
        audit = "all"
          
      if not values["id"]:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: "+row["transtype"]
          values["description"] = row["description"]
        else:
          return "Error|Missing description and no insert_row parameter"
      
      for key in row.keys():
        if key!="description" and key!="transtype":
          self.set_valid_value("pattern", row, key)
          values[key]= row[key]
        
      row_id = self.ns.connect.updateData("pattern", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=False)
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["description"])
    return retvalue
  
  def delete_pattern(self, params, data):
    retvalue = "OK"
    for row in data:
      pattern_id = None
      if row.has_key("description"):
        pattern_id = self.ns.valid.get_id_from_refnumber("pattern",row["description"],params.has_key("use_deleted"))
        if pattern_id:
          transtype = self.ns.db.groups(id=self.ns.db.pattern(id=pattern_id).transtype).groupvalue
          if self.validate:
            audit = self.ns.connect.getObjectAudit("trans",transtype)
            if audit=="error":
              return "Error|"+str(self.ns.error_message)
            if audit!="all":
              return "Error|Restricted type: "+ transtype

      if self.ns.connect.deleteData(nervatype="pattern", ref_id=None, refnumber=str(row["description"])):
        retvalue = retvalue+"|"+str(row["description"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue   
  
  def update_payment(self, params, data):    
    retvalue = "OK"
    for row in data:
      values = {"id":None}
      if not row.has_key("rownumber"):
        return "Error|Missing required parameter: rownumber"
      if row.has_key("transnumber"):
        values["trans_id"] = self.ns.valid.get_id_from_refnumber("trans",row["transnumber"],params.has_key("use_deleted"))
        if not values["trans_id"]:
          return "Error|Unknown transnumber: "+str(row["transnumber"])
        values["id"] = self.ns.valid.get_id_from_refnumber("payment",row["transnumber"]+"~"+str(row["rownumber"]),params.has_key("use_deleted"))
      else:
        return "Error|Missing required parameter: transnumber"
      
      transtype= self.ns.db.groups(id=self.ns.db.trans(id=values["trans_id"]).transtype).groupvalue
      if self.validate:
        audit = self.ns.connect.getObjectAudit("trans",transtype)
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled" or audit=="readonly":
          return "Error|Disabled or readonly transtype: "+transtype
      else:
        audit = "all"
      
      if not values["id"]:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: "+transtype
          fmt = "%Y.%m.%d 00:00:00"
          values["paiddate"] = datetime.strptime(date.strftime(datetime.now(),fmt),fmt)
        else:
          return "Error|Missing item and no insert_row parameter"
      
      for key in row.keys():
        if key!="rownumber" and key!="transnumber":
          self.set_valid_value("payment", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("payment", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["transnumber"])+"~"+str(row["rownumber"])
    return retvalue
  
  def delete_payment(self, params, data):
    return self.delete_transitem(params, data, "payment")
  
  def update_place(self, params, data):  
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: setting"
    else:
      audit = "all"
    for row in data:
      values = {"id":None}
      if row.has_key("planumber"):
        values["id"] = self.ns.valid.get_id_from_refnumber("place",str(row["planumber"]),params.has_key("use_deleted"))
      
      if not values["id"]:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: setting"
          if not row.has_key("description"):
            return "Error|Missing required parameter: description"
          if not row.has_key("placetype"):
            return "Error|Missing required parameter: placetype. Valid values: bank, cash, warehouse, store"
          else:
            values["placetype"] = self.ns.valid.get_groups_id("placetype",row["placetype"])
            if not values["placetype"]:
              return "Error|Unknown placetype: "+str(row["placetype"])
            if (row["placetype"]=="bank" or row["placetype"]=="cash") and not row.has_key("curr"):
              return "Error|Missing required parameter: curr"
            del row["placetype"]
          if not row.has_key("planumber"):
            row["planumber"] = self.ns.connect.nextNumber("planumber")
          if self.ns.valid.get_id_from_refnumber("place",row["planumber"],params.has_key("use_deleted")):
            return "Error|New place, but the retrieved planumber is reserved: "+str(row["planumber"])
          values["planumber"] = row["planumber"]
          values["description"] = row["description"]
        else:
          return "Error|Missing planumber and insert_row parameter"
      if row.has_key("placetype") and values["id"]:
        if self.ns.valid.get_groups_id("placetype",row["placetype"])!=self.ns.db.place(id=values["id"]).placetype:
          return "Error|Readonly parameter: placetype"
        del row["placetype"]
      if row.has_key("curr"):
        if row["curr"]!="":
          if not self.ns.valid.get_id_from_refnumber("currency",str(row["curr"]),params.has_key("use_deleted")):
            return "Error|Unknown curr: "+row["curr"]
       
      for key in row.keys():
        if key!="planumber" and key!="placetype":
          self.set_valid_value("place", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("place", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["planumber"])
    return retvalue
  
  def delete_place(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: setting"
    retvalue = "OK"
    for row in data:
      if not row.has_key("planumber"):
        return "Error|Missing required parameter: planumber"
      if self.ns.connect.deleteData(nervatype="place", ref_id=None, refnumber=str(row["planumber"])):
        retvalue = retvalue+"|"+str(row["planumber"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
  
  def update_price(self, params, data):    
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("price")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: price"
    else:
      audit = "all"
    for row in data:
      values = {"id":None,"product_id":None}
      if not row.has_key("partnumber"):
        return "Error|Missing required parameter: partnumber"
      else:
        values["product_id"] = self.ns.valid.get_id_from_refnumber("product",row["partnumber"],params.has_key("use_deleted"))
        if not values["product_id"]:
          return "Error|Unknown partnumber No: "+str(row["partnumber"])
      if not row.has_key("pricetype"):
        return "Error|Missing required parameter: pricetype. Valid values: price or discount."
      elif row["pricetype"] not in("price","discount"):
        return "Error|Unknown pricetype: "+str(row["pricetype"])
      if not row.has_key("validfrom"):
        return "Error|Missing required parameter: validfrom"
      else:
        row["validfrom"] = str(row["validfrom"]).strip(" 00:00:00")
        try:
          if datetime.strptime(row["validfrom"],"%Y-%m-%d").__class__.__name__ == "datetime":
            pass
        except Exception:
          return "Error|Incorrect date value! Valid datetime format: YYYY-MM-DD. Fieldname: validfrom"
      if row.has_key("curr"):
        if not self.ns.valid.get_id_from_refnumber("currency",str(row["curr"]),params.has_key("use_deleted")):
          return "Error|Unknown curr: "+row["curr"]
      else:
        row["curr"] = self.ns.connect.getSetting("default_currency")
      if not row.has_key("qty"):
        row["qty"] = 0
      if row.has_key("calcmode"):
        if row["calcmode"]!="":
          row["calcmode"] = self.ns.valid.get_groups_id("calcmode",row["calcmode"],params.has_key("use_deleted"))
          if not row["calcmode"]:
            return "Error|Unknown calcmode: "+str(row["calcmode"])
            
      values["id"] = self.ns.valid.get_id_from_refnumber("price",row["partnumber"]+"~"+row["pricetype"]+"~"+row["validfrom"]+"~"+row["curr"]+"~"+str(row["qty"]),params.has_key("use_deleted"))
      if not values["id"]:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: price"
          values["validfrom"] = row["validfrom"]
          values["curr"] = row["curr"]
          if not row.has_key("calcmode"):
            values["calcmode"] = self.ns.valid.get_groups_id("calcmode","amo")
          if row["pricetype"]=="discount":
            values["discount"] = 0
        else:
          return "Error|Missing partnumber and insert_row parameter"
      
      for key in row.keys():
        if key!="partnumber" and key!="pricetype":
          self.set_valid_value("price", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("price", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      ##partnumber~pricetype~validfrom~curr~qty
      retvalue = retvalue+"|"+str(row["partnumber"])+"~"+row["pricetype"]+"~"+str(row["validfrom"])+"~"+str(row["curr"])+"~"+str(row["qty"])
    return retvalue
  
  def delete_price(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("price")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: price"
    else:
      audit = "all"
    for row in data:
      if not row.has_key("partnumber"):
        return "Error|Missing required parameter: partnumber"
      else:
        if not self.ns.valid.get_id_from_refnumber("product",row["partnumber"],params.has_key("use_deleted")):
          return "Error|Unknown partnumber No: "+str(row["partnumber"])
      if not row.has_key("pricetype"):
        return "Error|Missing required parameter: pricetype"
      elif row["pricetype"] not in("price","discount"):
        return "Error|Unknown pricetype: "+str(row["pricetype"])
      if not row.has_key("validfrom"):
        return "Error|Missing required parameter: validfrom"
      else:
        row["validfrom"] = str(row["validfrom"]).strip(" 00:00:00")
        try:
          if datetime.strptime(row["validfrom"],"%Y-%m-%d").__class__.__name__ == "datetime":
            pass
        except Exception:
          return "Error|Incorrect date value! Valid datetime format: YYYY-MM-DD. Fieldname: validfrom"
      if row.has_key("curr"):
        if not self.ns.valid.get_id_from_refnumber("currency",str(row["curr"]),params.has_key("use_deleted")):
          return "Error|Unknown curr: "+row["curr"]
      else:
        return "Error|Missing required parameter: curr"
      if not row.has_key("qty"):
        return "Error|Missing required parameter: qty"
          
      refnumber = row["partnumber"]+"~"+row["pricetype"]+"~"+row["validfrom"]+"~"+row["curr"]+"~"+str(row["qty"])
      if self.ns.connect.deleteData(nervatype="price", ref_id=None, refnumber=refnumber):
        retvalue = retvalue+"|"+refnumber
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
      
  def update_product(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("product")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: product"
    else:
      audit = "all"
    for row in data:
      values = {"id":None}
      if row.has_key("partnumber"):
        values["id"] = self.ns.valid.get_id_from_refnumber("product",row["partnumber"],params.has_key("use_deleted"))   
      if not values["id"]:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: product"
          if not row.has_key("description"):
            return "Error|Missing required parameter: description"
          if not row.has_key("partnumber"):
            row["partnumber"] = self.ns.connect.nextNumber("partnumber")
          values["id"] = self.ns.valid.get_id_from_refnumber("product",row["partnumber"],params.has_key("use_deleted"))
          if values["id"]:
            return "Error|New product, but the retrieved partnumber is reserved: "+str(row["partnumber"])
          values["partnumber"] = row["partnumber"]
          values["description"] = row["description"]
          values["protype"] = self.ns.valid.get_groups_id("protype","item")
          values["tax_id"] = self.ns.valid.get_id_from_refnumber("tax",self.ns.connect.getSetting("default_taxcode"),params.has_key("use_deleted"))
          if not values["tax_id"]:
            values["tax_id"] = self.ns.db(self.ns.db.tax).select()[0]["id"]
          values["unit"] = self.ns.connect.getSetting("default_unit")
        else:
          return "Error|Missing partnumber and insert_row parameter"
      if row.has_key("protype"):
        if row["protype"] in("item","service"):
          row["protype"] = self.ns.valid.get_groups_id("protype",row["protype"])
        else:
          return "Error|Valid transfilter: item, service "  
      if row.has_key("taxcode"):
        values["tax_id"] = self.ns.valid.get_id_from_refnumber("tax",row["taxcode"],params.has_key("use_deleted"))
        if values["tax_id"]:
          del row["taxcode"] 
        else:
          return "Error|Unknown taxcode: "+row["taxcode"]
      
      for key in row.keys():
        if key!="partnumber":
          self.set_valid_value("product", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("product", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["partnumber"])
    return retvalue
  
  def delete_product(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("product")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: product"
    retvalue = "OK"
    for row in data:
      if not row.has_key("partnumber"):
        return "Error|Missing required parameter: partnumber"
      if self.ns.connect.deleteData(nervatype="product", ref_id=None, refnumber=str(row["partnumber"])):
        retvalue = retvalue+"|"+str(row["partnumber"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
  
  def update_project(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("project")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: project"
    else:
      audit = "all"
    for row in data:
      values = {"id":None}
      if row.has_key("pronumber"):
        values["id"] = self.ns.valid.get_id_from_refnumber("project",row["pronumber"],params.has_key("use_deleted"))
      if not values["id"]:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: project"
          if not row.has_key("description"):
            return "Error|Missing required parameter: description"
          if not row.has_key("pronumber"):
            row["pronumber"] = self.ns.connect.nextNumber("pronumber")
          values["id"] = self.ns.valid.get_id_from_refnumber("project",row["pronumber"],params.has_key("use_deleted"))
          if values["id"]:
            return "Error|New project, but the retrieved pronumber is reserved: "+str(row["pronumber"])
          values["pronumber"] = row["pronumber"]
          values["description"] = row["description"]
        else:
          return "Error|Missing pronumber and insert_row parameter" 
      if row.has_key("custnumber"):
        if row["custnumber"]!="":
          values["customer_id"] = self.ns.valid.get_id_from_refnumber("customer",row["custnumber"],params.has_key("use_deleted"))
          if not values["customer_id"]:
            return "Error|Unknown custnumber: "+row["custnumber"]
        del row["custnumber"]
        
      for key in row.keys():
        if key!="pronumber":
          self.set_valid_value("project", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("project", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["pronumber"])
    return retvalue
  
  def delete_project(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("project")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: project"
    retvalue = "OK"
    for row in data:
      if not row.has_key("pronumber"):
        return "Error|Missing required parameter: pronumber"
      if self.ns.connect.deleteData(nervatype="project", ref_id=None, refnumber=str(row["pronumber"])):
        retvalue = retvalue+"|"+str(row["pronumber"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
  
  def update_rate(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: setting"
    else:
      audit = "all"
    for row in data:
      values = {"id":None}
      if not row.has_key("ratetype"):
        return "Error|Missing required parameter: ratetype. Valid values: rate,buy,sell,average."
      else:
        values["ratetype"] = self.ns.valid.get_groups_id("ratetype",row["ratetype"])
        if not values["ratetype"]:
          return "Error|Unknown ratetype: "+str(row["ratetype"])
      if not row.has_key("ratedate"):
        return "Error|Missing required parameter: ratedate"
      if not row.has_key("curr"):
        return "Error|Missing required parameter: curr"
      else:
        if not self.ns.valid.get_id_from_refnumber("currency",row["curr"],params.has_key("use_deleted")):
          return "Error|Unknown curr: "+str(row["curr"])
        else:
          values["curr"] = row["curr"]
      refnumber = row["ratetype"]+"~"+row["ratedate"]+"~"+row["curr"]
      if row.has_key("planumber"):
        if row["planumber"].lower() != "none" and row["planumber"].lower() != "null":
          values["place_id"] = self.ns.valid.get_id_from_refnumber("place",row["planumber"],params.has_key("use_deleted"))
          if not values["place_id"]:
            return "Error|Unknown planumber: "+str(row["planumber"])
          refnumber += "~"+row["planumber"]
        
      values["id"] = self.ns.valid.get_id_from_refnumber("rate",refnumber,params.has_key("use_deleted"))
      if not values["id"]:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: setting"
          values["ratedate"] = row["ratedate"]
        else:
          return "Error|Missing datarow and no insert_row parameter"
      if row.has_key("rategroup"):
        if row["rategroup"]!="":
          row["rategroup"] = self.ns.valid.get_groups_id("rategroup",row["rategroup"],params.has_key("use_deleted"))
          if not values["rategroup"]:
            return "Error|Unknown rategroup: "+str(row["rategroup"])
      
      for key in row.keys():
        if key!="ratetype" and key!="ratedate" and key!="curr" and key!="planumber":
          self.set_valid_value("rate", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("rate", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      #ratetype~ratedate~curr(~planumber)
      retvalue = retvalue+"|"+refnumber
    return retvalue
  
  def delete_rate(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: setting"
    for row in data:
      if not row.has_key("ratetype"):
        return "Error|Missing required parameter: ratetype"
      else:
        if not self.ns.valid.get_groups_id("ratetype",row["ratetype"]):
          return "Error|Unknown ratetype: "+str(row["ratetype"])
      if not row.has_key("ratedate"):
        return "Error|Missing required parameter: ratedate"
      if not row.has_key("curr"):
        return "Error|Missing required parameter: curr"
      else:
        if not self.ns.valid.get_id_from_refnumber("currency",row["curr"],params.has_key("use_deleted")):
          return "Error|Unknown curr: "+str(row["curr"])
      refnumber = row["ratetype"]+"~"+row["ratedate"]+"~"+row["curr"]
      if row.has_key("planumber"):
        if row["planumber"].lower() != "none" and row["planumber"].lower() != "null":
          if not self.ns.valid.get_id_from_refnumber("place",row["planumber"],params.has_key("use_deleted")):
            return "Error|Unknown planumber: "+str(row["planumber"])
          refnumber += "~"+row["planumber"]
        
      if self.ns.connect.deleteData(nervatype="rate", ref_id=None, refnumber=refnumber):
        retvalue = retvalue+"|"+refnumber
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
   
  def update_tax(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: setting"
    else:
      audit = "all"
    for row in data:
      values = {"id":None}
      if not row.has_key("taxcode"):
        return "Error|Missing required parameter: taxcode"
      else:
        values["id"] = self.ns.valid.get_id_from_refnumber("tax",row["taxcode"],params.has_key("use_deleted"))
      if not values["id"]:
        if not row.has_key("description"):
          return "Error|Missing required parameter: description"  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: setting"
          values["taxcode"] = row["taxcode"]
          values["description"] = row["description"]
        else:
          return "Error|Missing code and no insert_row parameter"
        
      for key in row.keys():
        if key!="taxcode":
          self.set_valid_value("tax", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("tax", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["taxcode"])
    return retvalue
  
  def delete_tax(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: setting"
    retvalue = "OK"
    for row in data:
      if not row.has_key("taxcode"):
        return "Error|Missing required parameter: taxcode"
      if self.ns.connect.deleteData(nervatype="tax", ref_id=None, refnumber=str(row["taxcode"])):
        retvalue = retvalue+"|"+str(row["taxcode"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
  
  def update_tool(self, params, data):
    retvalue = "OK"
    if self.validate:
      audit = self.ns.connect.getObjectAudit("tool")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: tool"
    else:
      audit = "all"
    for row in data:
      values = {"id":None}
      if row.has_key("serial"):
        values["id"] = self.ns.valid.get_id_from_refnumber("tool",row["serial"],params.has_key("use_deleted"))
      if row.has_key("partnumber"):
        values["product_id"] = self.ns.valid.get_id_from_refnumber("product",row["partnumber"],params.has_key("use_deleted"))
        if not values["product_id"]:
          return "Error|Unknown partnumber: "+row["partnumber"]
      if not values["id"]:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: tool"
          if not row.has_key("partnumber"):
            return "Error|Missing required parameter: partnumber"
          if not row.has_key("serial"):
            row["serial"] = self.ns.connect.nextNumber("serial")
          values["id"] = self.ns.valid.get_id_from_refnumber("tool",row["serial"],params.has_key("use_deleted"))
          if values["id"]:
            return "Error|New tool, but the retrieved serial is reserved: "+str(row["serial"])
          values["serial"] = row["serial"]
        else:
          return "Error|Missing serial and insert_row parameter"  
      if row.has_key("toolgroup"):
        if row["toolgroup"]!="":
          values["toolgroup"] = self.ns.valid.get_groups_id("toolgroup",row["toolgroup"],params.has_key("use_deleted"))
          if not values["toolgroup"]:
            return "Error|Unknown toolgroup: "+str(row["toolgroup"])
          else:
            del row["toolgroup"]
        
      for key in row.keys():
        if key!="serial" and key!="partnumber":
          self.set_valid_value("tool", row, key)
          values[key]= row[key]
      
      row_id = self.ns.connect.updateData("tool", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+str(row["serial"])
    return retvalue
  
  def delete_tool(self, params, data):
    if self.validate:
      audit = self.ns.connect.getObjectAudit("tool")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: tool"
    retvalue = "OK"
    for row in data:
      if not row.has_key("serial"):
        return "Error|Missing required parameter: serial"
      if self.ns.connect.deleteData(nervatype="tool", ref_id=None, refnumber=str(row["serial"])):
        retvalue = retvalue+"|"+str(row["serial"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
  
  def update_trans(self, params, data):    
    retvalue = "OK"      
    for row in data:
      values = {"id":None}
      if row.has_key("transnumber"):
        values["id"] = self.ns.valid.get_id_from_refnumber("trans",row["transnumber"],params.has_key("use_deleted"))
        if values["id"]:
          if row.has_key("transtype"):
            if self.ns.valid.get_groups_id("transtype",row["transtype"])!=self.ns.db.trans(id=values["id"]).transtype:
              return "Error|Readonly parameter: transtype"
          else:
            row["transtype"]=self.ns.db.groups(id=self.ns.db.trans(id=values["id"]).transtype).groupvalue
          if row.has_key("direction"):
            if self.ns.valid.get_groups_id("direction",row["direction"])!=self.ns.db.trans(id=values["id"]).direction:
              return "Error|Readonly parameter: direction"
          else:
            row["direction"]=self.ns.db.groups(id=self.ns.db.trans(id=values["id"]).direction).groupvalue
      
      if not row.has_key("transtype"):
        return "Error|Missing required parameter: transtype"
      else:
        if self.validate:
          audit = self.ns.connect.getObjectAudit("trans",row["transtype"])
          if audit=="error":
            return "Error|"+str(self.ns.error_message)
          if audit=="disabled" or audit=="readonly":
            return "Error|Disabled or readonly transtype: "+row["transtype"]
      
      if row.has_key("username") and self.validate:
        if self.ns.employee["id"]!=self.ns.db.employee(username=row["username"]).id:
          return "Error|Readonly field: username!"
        del row["username"]
      if row.has_key("empnumber"):
        if row["empnumber"]!="":
          row["employee_id"] = self.ns.valid.get_id_from_refnumber("employee",row["empnumber"],params.has_key("use_deleted"))
          if not row["employee_id"]:
            return "Error|Unknown empnumber No: "+str(row["empnumber"])
        else:
          row["employee_id"] = None
        del row["empnumber"]
      if row.has_key("department"):
        if row["department"]!="":
          row["department"] = self.ns.valid.get_groups_id("department",row["department"],params.has_key("use_deleted"))
          if not row["department"]:
            return "Error|Unknown department: "+str(row["department"])
      if row.has_key("pronumber"):
        if row["pronumber"]!="":
          row["project_id"] = self.ns.valid.get_id_from_refnumber("project",row["pronumber"],params.has_key("use_deleted"))
          if not row["project_id"]:
            return "Error|Unknown pronumber No: "+str(row["pronumber"])
        else:
          row["project_id"] = None
        del row["pronumber"]
      if row.has_key("planumber"):
        if row["planumber"]!="":
          row["place_id"] = self.ns.valid.get_id_from_refnumber("place",row["planumber"],params.has_key("use_deleted"))
          if not row["place_id"]:
            return "Error|Unknown pronumber No: "+str(row["planumber"]) 
        else:
          row["place_id"] = None
        del row["planumber"]
      if row.has_key("paidtype"):
        if row["paidtype"]!="":
          row["paidtype"] = self.ns.valid.get_groups_id("paidtype",row["paidtype"],params.has_key("use_deleted"))
          if not row["paidtype"]:
            return "Error|Unknown paidtype: "+str(row["paidtype"])      
      if row.has_key("curr"):
        if row["curr"]!="":
          if not self.ns.valid.get_id_from_refnumber("currency",row["curr"],params.has_key("use_deleted")):
            return "Error|Unknown curr: "+str(row["curr"])
      if row.has_key("transtate"):
        row["transtate"] = self.ns.valid.get_groups_id("transtate",row["transtate"],params.has_key("use_deleted"))
        if not row["transtate"]:
          return "Error|Unknown transtate: "+str(row["transtate"])
      if row.has_key("custnumber"):
        if row["custnumber"]!="":
          row["customer_id"] = self.ns.valid.get_id_from_refnumber("customer",row["custnumber"],params.has_key("use_deleted"))
          if not row["customer_id"]:
            return "Error|Unknown custnumber No: "+str(row["custnumber"])
        else:
          row["customer_id"] = None
        del row["custnumber"]
      
      if row.has_key("duedate"):
        if len(row["duedate"])>10: 
          row["duedate"]=row["duedate"][:10]
          row["duedate"] += " 00:00:00"
            
      if not values["id"]:  
        if params.has_key("insert_row"):
          if not row.has_key("transtype"):
            return "Error|Missing required parameter: transtype"
          else:
            if not self.ns.valid.get_groups_id("transtype",row["transtype"]):
              return "Error|Unknown transtype: "+str(row["transtype"])
            if self.validate:
              audit = self.ns.connect.getObjectAudit("trans",row["transtype"])
              if audit=="error":
                return "Error|"+str(self.ns.error_message)
              if audit!="all":
                return "Error|Restricted transtype: "+row["transtype"]
          if not row.has_key("direction"):
            return "Error|Missing required parameter: direction"
          else:
            if not self.ns.valid.get_groups_id("direction",row["direction"]):
              return "Error|Unknown direction: "+str(row["direction"])
          if not row.has_key("custnumber") and not row.has_key("customer_id") and (row["transtype"] in("offer","order","worksheet","rent","invoice")):
            return "Error|Missing required parameter: custnumber"
          if not row.has_key("planumber") and not row.has_key("place_id") and row["transtype"] in("bank","cash"):
            return "Error|Missing required parameter: planumber"
          
          if not row.has_key("transnumber"):
            tname = str(row["transtype"])+"_"+str(row["direction"])
            row["transnumber"] = self.ns.connect.nextNumber(tname)
          if self.ns.valid.get_id_from_refnumber("trans",row["transnumber"],params.has_key("use_deleted")):
            return "Error|New trans, but the retrieved trans No. is reserved: "+str(row["transnumber"])
          employee_id = None
          if not self.ns.employee:
            if self.validate: 
              return "Error|Invalid login!"
            else:
              if row.has_key("username"):
                emplist = self.ns.db((self.ns.db.employee.username==row["username"])).select()
                if len(emplist)>0: employee_id = emplist[0]["id"]
                del row["username"]
              if not employee_id:
                return "Error|Invalid username!"
          else:
            employee_id = self.ns.employee["id"]
          if row.has_key("crdate") and not self.validate:
            crdate = str(row["crdate"]).strip(" 00:00:00")
          else:
            crdate = date.today()
          values["transnumber"] = row["transnumber"]
          values["transtype"] = self.ns.valid.get_groups_id("transtype",row["transtype"])
          values["direction"] = self.ns.valid.get_groups_id("direction",row["direction"])
          values["crdate"] = crdate
          values["cruser_id"] = employee_id
          values["transdate"] = date.today()
          if row["transtype"] in("offer","order","worksheet","rent","invoice","receipt"):
            values["curr"] = self.ns.connect.getSetting("default_currency")
            values["paidtype"] = self.ns.valid.get_groups_id("paidtype",self.ns.connect.getSetting("default_paidtype"),params.has_key("use_deleted"))
          if self.ns.connect.getSetting("audit_control")=="true":
            values["transtate"] = self.ns.valid.get_groups_id("transtate","new")
          else:
            values["transtate"] = self.ns.valid.get_groups_id("transtate","ok")
          plst = self.ns.db((self.ns.db.pattern.deleted==0)&(self.ns.db.pattern.defpattern==1)&(self.ns.db.pattern.transtype==values["transtype"])).select()
          if len(plst)>0: values["fnote"] = plst[0]["notes"]
          
          values["trans_transcast"] = "normal"
        else:
          return "Error|Missing transnumber and insert_row parameter"
          
      if row["transtype"] =="invoice":
        if row.has_key("customer_id"):
          customer_id = row["customer_id"]
        elif values["id"]:
          customer_id = self.ns.db.trans(id=values["id"]).customer_id
        if not customer_id:
          return "Error|Missing required parameter: custnumber"
        self.ns.valid.set_invoice_customer(values,customer_id)
  
      for key in row.keys():
        if key not in("transnumber","transtype","direction"):
          self.set_valid_value("trans", row, key)
          values[key]= row[key] 
      
      row_id = self.ns.connect.updateData("trans", values, log_enabled=self.log_enabled, validate=self.validate, 
        insert_row=params.has_key("insert_row"), insert_field=params.has_key("insert_field"))
      if not row_id:
        return "Error|"+str(self.ns.error_message)
      retvalue = retvalue+"|"+row["transnumber"]
    return retvalue
  
  def delete_trans(self, params, data):
    retvalue = "OK"
    for row in data:
      trans_=None
      if row.has_key("transnumber"):
        trans_ = self.ns.valid.get_id_from_refnumber("trans",row["transnumber"],params.has_key("use_deleted"))
        if trans_: trans_ = self.ns.db.trans(id=trans_)
        if trans_:
          if self.validate:
            audit = self.ns.connect.getObjectAudit("trans",self.ns.db.groups(id=trans_["transtype"]).groupvalue)
            if audit=="error":
              return "Error|"+str(self.ns.error_message)
            if audit!="all":
              return "Error|Restricted type: "+ self.ns.db.groups(id=trans_["transtype"]).groupvalue
      else:
        return "Error|Missing required parameter: transnumber"
      if self.ns.connect.deleteData(nervatype="trans", ref_id=None, refnumber=str(row["transnumber"])):
        retvalue = retvalue+"|"+str(row["transnumber"])
      else:
        return "Error|"+str(self.ns.error_message)
    return retvalue
  
  def getView(self, params, filter):#@ReservedAssignment
      
    retvalue="OK"
    
    item_str = ""
    fld_value = ""
    fields = []
    items = []
    
    if not self.ns.employee:
      if self.validate: 
        return "Error|Invalid login!"
      
    if filter.has_key("output"):
      if filter["output"] not in("text","html","xml","excel","json"):
        return "Error|Valid output: text, html, xml, excel, json"
    else:
      filter["output"]="text"
    header=[]
    if filter.has_key("header"):
      header=filter["header"].split(",")
    
    if filter["output"].startswith("xml") and not filter.has_key("show_id"):
      filter["show_id"] = "xml"
    
    select_str=""
    from_str=""
    where_str=""
    orderby_str=""
    limit_str=""
    
    if filter.has_key("where"):
      if filter["where"]!="":
        where_str="and "+filter["where"]
    orderby=""
    if filter.has_key("orderby"):
      if filter["orderby"]!="":
        orderby=" order by "+filter["orderby"]
    if params["datatype"]!="sql" and filter.has_key("limit"):
      try:
        limit_str=" limit "+str(filter["limit"])
      except Exception, err:
        return "Error|"+str(err)
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    if params["datatype"]=="sql":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "item"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("setting")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: setting"
      
      filter["show_id"] = "sql"
      if not filter.has_key("sql"):
        return "Error|Sql datatype, but missing sql parameter!"
      if filter["sql"]=="":
        return "Error|Sql datatype, but missing sql parameter!"
      if not filter["sql"].lstrip().startswith("select") and not filter["sql"].lstrip().startswith("insert") and not filter["sql"].lstrip().startswith("update"):
        return "Error|Valid sql query: select, update or insert!"
      try:
        vrows = self.ns.db.executesql(filter["sql"], as_dict=True)
      except Exception, err:
        return "Error|"+str(err)
      if len(vrows)==0:
        return "OK|Could not find data!"
      fields = vrows[0].keys()
      for row in vrows:
        items.append(row.values())
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="address":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "address"
      fld_value = "address"
      nervatype_lst=['customer', 'employee', 'event', 'place', 'product', 'project', 'tool', 'trans']
      
      if filter.has_key("nervatype"):
        if str(filter["nervatype"]) not in nervatype_lst:
          return "Error|Invalid nervatype: "+str(filter["nervatype"])
        
        if self.validate:
          audit = self.ns.connect.getObjectAudit(str(filter["nervatype"]))
          if audit=="error":
            return "Error|"+str(self.ns.error_message)
          if audit=="disabled":
            return "Error|Disabled type: "+str(filter["nervatype"])

        nervanumber = self.ns.valid.get_table_key(filter["nervatype"])
      
        fields_ = [{"nervatype":"g.groupvalue"}, {"refnumber":"nerv."+str(nervanumber)}, 
                   {"represent_rownumber":"address.id"},
                   {"country":"address.country"}, {"state":"address.state"}, {"zipcode":"address.zipcode"}, {"city":"address.city"}, 
                   {"street":"address.street"}, {"notes":"address.notes"}]
        select_str ="select @id, g.groupvalue as nervatype, nerv."+str(nervanumber)+" as refnumber, address.id as represent_rownumber, \
          address.country, address.state, address.zipcode, address.city, address.street, address.notes "
        from_str = " from address \
          inner join groups g on address.nervatype=g.id and g.groupvalue = '"+str(filter["nervatype"])+"' \
          inner join "+str(filter["nervatype"])+" nerv on address.ref_id = nerv.id "
        if not params.has_key("use_deleted"):
          from_str+=" and nerv.deleted=0 "
      else:
        if self.validate:
          for ntype in nervatype_lst:
            audit = self.ns.connect.getObjectAudit(ntype)
            if audit=="error":
              return "Error|"+str(self.ns.error_message)
            if audit=="disabled":
              return "Error|Disabled type: "+ntype
          
        fields_ = [{"nervatype":"g.groupvalue"}, {"represent_refnumber_nervatype":"address.ref_id"}, {"represent_rownumber":"address.id"},
                   {"country":"address.country"}, {"state":"address.state"}, {"zipcode":"address.zipcode"}, {"city":"address.city"}, 
                   {"street":"address.street"}, {"notes":"address.notes"}]
        select_str ="select @id, g.groupvalue as nervatype, address.ref_id as represent_refnumber_nervatype, address.id as represent_rownumber, \
          address.country, address.state, address.zipcode, address.city, address.street, address.notes "
        from_str = " from address \
          inner join groups g on address.nervatype=g.id "
            
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "address.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"address.deleted"})
        select_str+=", address.deleted "
      else:
        where_str = " where address.deleted=0 "+where_str
      if orderby=="":
        orderby_str =  " order by nervatype, id "
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " address.id")
      orderby_str = orderby_str.replace(" id", " address.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])  
      
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="barcode":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "barcode"
      fld_value = "barcode"
      if self.validate:
        audit = self.ns.connect.getObjectAudit("product")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: product"
      
      fields_ = [{"code":"barcode.code"}, {"partnumber":"p.partnumber"}, {"barcodetype":"g.groupvalue"}, {"description":"barcode.description"}, 
                 {"qty":"barcode.qty"}, {"defcode":"barcode.defcode"}]
      select_str ="select @id, barcode.code as code, p.partnumber, g.groupvalue as barcodetype, barcode.description, barcode.qty, barcode.defcode "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "p.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = "  from barcode inner join groups g on barcode.barcodetype=g.id inner join product p on barcode.product_id = p.id "
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
      else:
        where_str = " where p.deleted=0 "+where_str
      if orderby=="":
        orderby_str = "order by id "
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " p.id")
      where_str = where_str.replace(" barcodetype", " g.groupvalue")
      orderby_str = orderby_str.replace(" id", " p.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="contact":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "contact"
      fld_value = "contact"
      nervatype_lst=['customer', 'employee', 'event', 'place', 'product', 'project', 'tool', 'trans']
      
      if filter.has_key("nervatype"):
        if str(filter["nervatype"]) not in nervatype_lst:
          return "Error|Invalid nervatype: "+str(filter["nervatype"])
        
        if self.validate:
          audit = self.ns.connect.getObjectAudit(str(filter["nervatype"]))
          if audit=="error":
            return "Error|"+str(self.ns.error_message)
          if audit=="disabled":
            return "Error|Disabled type: "+str(filter["nervatype"])
      
        nervanumber = self.ns.valid.get_table_key(filter["nervatype"])
        
        fields_ = [{"nervatype":"g.groupvalue"}, {"refnumber":"nerv."+str(nervanumber)},
                    {"represent_rownumber":"contact.id"}, 
                    {"firstname":"contact.firstname"}, {"surname":"contact.surname"}, {"status":"contact.status"}, 
                    {"phone":"contact.phone"}, {"fax":"contact.fax"}, {"mobil":"contact.mobil"}, {"email":"contact.email"}, 
                    {"notes":"contact.notes"}]
        select_str ="select @id, g.groupvalue as nervatype, nerv."+str(nervanumber)+" as refnumber,  contact.id as represent_rownumber, \
          contact.firstname, contact.surname, contact.status, contact.phone, contact.fax, contact.mobil, contact.email, contact.notes "
        from_str = "from contact inner join groups g on contact.nervatype=g.id and g.groupvalue = '"+str(filter["nervatype"])+"' \
          inner join "+str(filter["nervatype"])+" nerv on contact.ref_id = nerv.id "
        if not params.has_key("use_deleted"):
          from_str+=" and nerv.deleted=0 "
      else:
        if self.validate:
          for ntype in nervatype_lst:
            audit = self.ns.connect.getObjectAudit(ntype)
            if audit=="error":
              return "Error|"+str(self.ns.error_message)
            if audit=="disabled":
              return "Error|Disabled type: "+ntype
          
        fields_ = [{"nervatype":"g.groupvalue"}, {"represent_refnumber_nervatype":"contact.ref_id"}, 
                   {"represent_rownumber":"contact.id"},
                   {"firstname":"contact.firstname"}, {"surname":"contact.surname"}, {"status":"contact.status"}, 
                    {"phone":"contact.phone"}, {"fax":"contact.fax"}, {"mobil":"contact.mobil"}, {"email":"contact.email"}, 
                    {"notes":"contact.notes"}]
        select_str ="select @id, g.groupvalue as nervatype, contact.ref_id as represent_refnumber_nervatype, contact.id as represent_rownumber, \
          contact.firstname, contact.surname, contact.status, contact.phone, contact.fax, contact.mobil, contact.email, contact.notes "
        from_str = " from contact \
          inner join groups g on contact.nervatype=g.id "
      
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "contact.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"contact.deleted"})
        select_str+=", contact.deleted "
      else:
        where_str = " where contact.deleted=0 "+where_str
      if orderby=="":
        orderby_str = "order by nervatype, id "
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " contact.id")
      orderby_str = orderby_str.replace(" id", " contact.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="currency":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "currency"
      fld_value = "currency"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("setting")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: setting"
      
      fields = ["curr", "description", "digit", "defrate", "cround"]
      select_str ="select @id, curr, description, digit, defrate, cround "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from currency "
      where_str = " where 1=1 "+where_str
      if orderby=="":
        orderby_str = "order by curr "
      else:
        orderby_str = orderby
                      
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="customer":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "customer"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("customer")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: customer"
      
      fld_value = "customer"
      fields_ = [{"custnumber":"customer.custnumber"}, {"custtype":"g.groupvalue"}, {"custname":"customer.custname"}, {"taxnumber":"customer.taxnumber"}, 
                 {"account":"customer.account"}, {"notax":"customer.notax"}, {"terms":"customer.terms"}, {"creditlimit":"customer.creditlimit"},
                 {"discount":"customer.discount"}, {"notes":"customer.notes"}, {"inactive":"customer.inactive"}]
      select_str ="select @id, customer.custnumber, g.groupvalue as custtype, customer.custname, customer.taxnumber, customer.account, \
        customer.notax, customer.terms, customer.creditlimit, customer.discount, customer.notes, customer.inactive "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "customer.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from customer inner join groups g on customer.custtype=g.id "
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"customer.deleted"})
        select_str+=", customer.deleted "
      else:
        where_str = " where customer.deleted=0 "+where_str
      if orderby=="":
        orderby_str = "order by custnumber "
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " customer.id")
      orderby_str = orderby_str.replace(" id", " customer.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="deffield":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "deffield"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("setting")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: setting"
      
      fields_ = [{"fieldname":"df.fieldname"}, {"nervatype":"g.groupvalue"}, {"subtype":"sg.groupvalue"}, {"fieldtype":"fg.groupvalue"},
                 {"description":"df.description"}, {"valuelist":"df.valuelist"}, {"addnew":"df.addnew"}, {"visible":"df.visible"}, 
                 {"readonly":"df.readonly"}]
      select_str ="select @id, df.fieldname, g.groupvalue as nervatype, sg.groupvalue as subtype, fg.groupvalue as fieldtype, \
        df.description, df.valuelist, df.addnew, df.visible, df.readonly "
      
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        from_str = " from deffield df inner join groups g on df.nervatype=g.id \
          inner join groups fg on df.fieldtype=fg.id left join groups sg on (df.subtype=sg.id) "
        fields_.append({"deleted":"df.deleted"})
        select_str+=", df.deleted "
      else:
        where_str = " where df.deleted=0 "+where_str
        from_str = " from deffield df inner join groups g on df.nervatype=g.id \
          inner join groups fg on df.fieldtype=fg.id left join groups sg on (df.subtype=sg.id and sg.deleted=0) "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "df.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if orderby=="":
        orderby_str = "order by fieldname "
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " df.id")
      orderby_str = orderby_str.replace(" id", " df.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="employee":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "employee"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("employee")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: employee"
      
      fld_value = "employee"
      fields_ = [{"empnumber":"employee.empnumber"}, {"username":"employee.username"}, {"usergroup":"g.groupvalue"}, {"startdate":"employee.startdate"}, 
                 {"enddate":"employee.enddate"}, {"department":"dg.groupvalue"}, {"inactive":"employee.inactive"}]
      select_str ="select @id, employee.empnumber, employee.username, g.groupvalue as usergroup, employee.startdate, employee.enddate, \
        dg.groupvalue as department, employee.inactive "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "employee.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        from_str = " from employee inner join groups g on employee.usergroup=g.id \
          left join groups dg on (employee.department=dg.id) "
        fields_.append({"password":"employee.password"})
        fields_.append({"registration_key":"employee.registration_key"})
        fields_.append({"deleted":"employee.deleted"})
        select_str+=", employee.password, employee.registration_key, employee.deleted "
      else:
        where_str = " where employee.deleted=0 "+where_str
        from_str = " from employee inner join groups g on employee.usergroup=g.id \
          left join groups dg on (employee.department=dg.id and dg.deleted=0) "
      if orderby=="":
        orderby_str = " order by empnumber "
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " employee.id")
      orderby_str = orderby_str.replace(" id", " employee.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="event":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "event"
      fld_value = "event"
      nervatype_lst = ['customer', 'employee', 'place', 'product', 'project', 'tool', 'trans']
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("event")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: event"
      
      if filter.has_key("nervatype"):
        if str(filter["nervatype"]) not in nervatype_lst:
          return "Error|Invalid nervatype: "+str(filter["nervatype"])
        
        nervanumber = self.ns.valid.get_table_key(filter["nervatype"])
        fields_ = [{"calnumber":"event.calnumber"}, {"nervatype":"g.groupvalue"}, {"refnumber":"nerv."+str(nervanumber)}, {"uid":"event.uid"}, 
                   {"eventgroup":"eg.groupvalue"}, {"fromdate":"event.fromdate"}, {"todate":"event.todate"}, {"subject":"event.subject"}, 
                   {"place":"event.place"}, {"description":"event.description"}] 
        select_str ="select @id, event.calnumber, g.groupvalue as nervatype, nerv."+str(nervanumber)+" as refnumber, event.uid, \
          eg.groupvalue as eventgroup, event.fromdate, event.todate, event.subject, event.place, event.description "
        if params.has_key("use_deleted"):
          from_str = " from event inner join groups g on event.nervatype=g.id and g.groupvalue = '"+str(filter["nervatype"])+"'\
            inner join "+str(filter["nervatype"])+" nerv on event.ref_id = nerv.id \
            left join groups eg on event.eventgroup=eg.id " 
        else:
          from_str = " from event inner join groups g on event.nervatype=g.id and g.groupvalue = '"+str(filter["nervatype"])+"'\
            inner join "+str(filter["nervatype"])+" nerv on event.ref_id = nerv.id and nerv.deleted=0 \
            left join groups eg on event.eventgroup=eg.id "
      else:
        fields_ = [{"calnumber":"event.calnumber"}, {"nervatype":"g.groupvalue"}, {"represent_refnumber_nervatype":"event.ref_id"}, 
                   {"uid":"event.uid"}, 
                   {"eventgroup":"eg.groupvalue"}, {"fromdate":"event.fromdate"}, {"todate":"event.todate"}, {"subject":"event.subject"}, 
                   {"place":"event.place"}, {"description":"event.description"}]
        select_str ="select @id, event.calnumber, g.groupvalue as nervatype, event.ref_id as represent_refnumber_nervatype, event.uid, \
          eg.groupvalue as eventgroup, event.fromdate, event.todate, event.subject, event.place, event.description "
        if params.has_key("use_deleted"): 
          from_str = " from event \
            inner join groups g on event.nervatype=g.id left join groups eg on (event.eventgroup=eg.id) "
        else:
          from_str = " from event \
            inner join groups g on event.nervatype=g.id left join groups eg on (event.eventgroup=eg.id and eg.deleted=0) "
      
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "event.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"event.deleted"})
        select_str+=", event.deleted "
      else:
        where_str = " where event.deleted=0 "+where_str
      if orderby=="":
        orderby_str = " order by nervatype, calnumber "
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " event.id")
      orderby_str = orderby_str.replace(" id", " event.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="fieldvalue":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "fieldvalue"
      
      if self.validate:
        if filter.has_key("nervatype"):
          audit = self.ns.connect.getObjectAudit(str(filter["nervatype"]))
          if audit=="error":
            return "Error|"+str(self.ns.error_message)
          if audit=="disabled":
            return "Error|Disabled type: "+str(filter["nervatype"])
      
      if not filter.has_key("nervatype"):
        nervatype_lst=["address", "barcode", "contact", "currency", "customer", "employee", "event", "groups", "item", "link", "log", 
                       "movement", "price", "place", "product", "project", "rate", "tax", "tool", "trans", "setting"]
        if self.validate:
          for ntype in nervatype_lst:
            audit = self.ns.connect.getObjectAudit(ntype)
            if audit=="error":
              return "Error|"+str(self.ns.error_message)
            if audit=="disabled":
              return "Error|Disabled type: "+ntype
          
      fields_ = [{"nervatype":"g.groupvalue"}, 
                 {"represent_fieldname":"fv.id"}, {"represent_refnumber_nervatype":"fv.ref_id"}, 
                 {"description":"df.description"},
                 {"fieldtype":"fg.groupvalue"}, {"represent_fieldvalue":"fv.value"}, {"notes":"fv.notes"}]
      select_str ="select @id, g.groupvalue as nervatype, fv.id as represent_fieldname, fv.ref_id as represent_refnumber_nervatype, \
        df.description, fg.groupvalue as fieldtype, fv.value as represent_fieldvalue, fv.notes "
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        from_str = "from fieldvalue fv \
          inner join deffield df on (fv.fieldname=df.fieldname) inner join groups fg on df.fieldtype=fg.id \
          inner join groups g on df.nervatype=g.id "
        fields_.append({"deleted":"fv.deleted"})
        select_str+=", fv.deleted "
      else:
        where_str = " where fv.deleted=0 "+where_str
        from_str = "from fieldvalue fv \
          inner join deffield df on (fv.fieldname=df.fieldname and df.deleted=0) inner join groups fg on df.fieldtype=fg.id \
          inner join groups g on df.nervatype=g.id "
      if filter.has_key("nervatype"):
        where_str+=" and g.groupvalue='"+str(filter["nervatype"])+"' "
      if orderby=="":
        orderby_str = " order by g.groupvalue, fv.ref_id, fv.fieldname, fv.id "
      else:
        orderby_str = orderby
      
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "fv.id,")
      else:
        select_str = select_str.replace("@id,", "")
      where_str = where_str.replace(" id", " fv.id")
      orderby_str = orderby_str.replace(" id", " fv.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
        
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="groups":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "groups"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("setting")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: setting"
      
      fld_value = "groups"
      fields_ = [{"groupname":"groups.groupname"}, {"groupvalue":"groups.groupvalue"}, {"description":"groups.description"}, {"inactive":"groups.inactive"}]
      select_str ="select @id, groups.groupname, groups.groupvalue, groups.description, groups.inactive "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "groups.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from groups "
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"groups.deleted"})
        select_str+=", groups.deleted "
      else:
        where_str = " where groups.deleted=0 "+where_str
      if orderby=="":
        orderby_str = " order by groupname, groupvalue"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " groups.id")
      orderby_str = orderby_str.replace(" id", " groups.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="item":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "item"
      fld_value = "item"
      fields_ = [{"transnumber":"t.transnumber"}, {"represent_rownumber":"item.id"},
                 {"partnumber":"p.partnumber"}, {"unit":"item.unit"}, 
                 {"qty":"item.qty"}, {"fxprice":"item.fxprice"}, {"netamount":"item.netamount"}, {"discount":"item.discount"}, 
                 {"taxcode":"tx.taxcode"}, {"vatamount":"item.vatamount"}, {"amount":"item.amount"}, {"description":"item.description"}, 
                 {"deposit":"item.deposit"}, {"ownstock":"item.ownstock"}, {"actionprice":"item.actionprice"}]
      select_str ="select @id, t.transnumber, item.id as represent_rownumber, p.partnumber, item.unit, item.qty, item.fxprice, item.netamount, \
        item.discount, tx.taxcode as taxcode, item.vatamount, item.amount, item.description, item.deposit, item.ownstock, item.actionprice "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "item.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = "from item inner join trans t on item.trans_id=t.id inner join product p on item.product_id=p.id \
        inner join tax tx on item.tax_id=tx.id inner join groups g on t.transtype=g.id inner join groups gdir on t.direction=gdir.id "
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"item.deleted"})
        select_str+=", item.deleted "
      else:
        where_str = " where item.deleted=0 and (t.deleted=0 or (g.groupvalue='invoice' and gdir.groupvalue='out') or (g.groupvalue='receipt' and gdir.groupvalue='out')) "+where_str
      if self.ns.employee:
        where_str += " and t.transtype not in(select subtype from ui_audit \
          inner join groups nt on ui_audit.nervatype = nt.id and nt.groupvalue='trans' \
          inner join groups ifa on ui_audit.inputfilter = ifa.id and ifa.groupvalue='disabled' \
          where usergroup = "+str(self.ns.employee.usergroup)+") "
      if orderby=="":
        orderby_str = " order by transnumber, id"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " item.id")
      orderby_str = orderby_str.replace(" id", " item.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
      
      if self.validate:
        data_audit = self.ns.connect.getDataAudit()
        if data_audit=="usergroup":
          where_str += " and t.cruser_id in (select id from employee where usergroup = "+str(self.ns.employee.usergroup)+") "
        elif data_audit=="own":
          where_str += " and t.cruser_id = "+str(self.ns.employee.id)+" "
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="link":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "link"
      fld_value = "link"
      
      if self.validate:
        if filter.has_key("nervatype1"):
          audit = self.ns.connect.getObjectAudit(str(filter["nervatype1"]))
          if audit=="error":
            return "Error|"+str(self.ns.error_message)
          if audit=="disabled":
            return "Error|Disabled type: "+str(filter["nervatype1"])
        if filter.has_key("nervatype2"):
          audit = self.ns.connect.getObjectAudit(str(filter["nervatype2"]))
          if audit=="error":
            return "Error|"+str(self.ns.error_message)
          if audit=="disabled":
            return "Error|Disabled type: "+str(filter["nervatype2"])
      
      if not filter.has_key("nervatype1") or not filter.has_key("nervatype2"):
        nervatype_lst=['address', 'barcode', 'contact', 'currency', 'customer', 'employee', 'event', 'groups', 'item', 
                   'movement', 'payment', 'price', 'place', 'product', 'project', 'rate', 'tax',
                   'tool', 'trans', 'setting']
        if self.validate:
          for ntype in nervatype_lst:
            audit = self.ns.connect.getObjectAudit(ntype)
            if audit=="error":
              return "Error|"+str(self.ns.error_message)
            if audit=="disabled":
              return "Error|Disabled type: "+ntype
            
      fields_ = [{"nervatype1":"g1.groupvalue"}, {"represent_refnumber1":"link.ref_id_1"},
                 {"nervatype2":"g2.groupvalue"}, {"represent_refnumber2":"link.ref_id_2"}, 
                 {"linktype":"link.linktype"}]
      select_str ="select @id, g1.groupvalue as nervatype1, link.ref_id_1 as represent_refnumber1, \
      g2.groupvalue as nervatype2, link.ref_id_2 as represent_refnumber2, link.linktype "
      from_str = "from link inner join groups g1 on link.nervatype_1=g1.id inner join groups g2 on link.nervatype_2=g2.id "
            
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "link.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"link.deleted"})
        select_str+=", link.deleted "
      else:
        where_str = " where link.deleted=0 "+where_str
      if filter.has_key("nervatype1"):
        where_str+=" and g1.groupvalue='"+str(filter["nervatype1"])+"' "
      if filter.has_key("nervatype2"):
        where_str+=" and g2.groupvalue='"+str(filter["nervatype2"])+"' "
      if orderby=="":
        orderby_str = " order by nervatype1, nervatype1"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " link.id")
      orderby_str = orderby_str.replace(" id", " link.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="log":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "log"
      params["use_deleted"]=True
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("setting")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: setting"
      
      fld_value = "log"
      fields_ = [{"empnumber":"e.empnumber"}, {"crdate":"log.crdate"}, {"logstate":"lg.groupvalue"}, 
               {"nervatype":"g.groupvalue"}, {"represent_refnumber_nervatype":"log.ref_id"} 
                 ]
      select_str ="select @id, e.empnumber as empnumber, log.crdate, lg.groupvalue as logstate, case when g.groupvalue is null then '' else g.groupvalue end as nervatype, log.ref_id as represent_refnumber_nervatype "
      if params.has_key("use_deleted"):
        from_str = " from log left join groups g on (log.nervatype=g.id) \
          inner join groups lg on log.logstate=lg.id \
          inner join employee e on log.employee_id = e.id "
      else:
        from_str = " from log left join groups g on (log.nervatype=g.id and g.deleted=0) \
          inner join groups lg on log.logstate=lg.id \
          inner join employee e on log.employee_id = e.id "
      where_str = " where 1=1 "+where_str
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "log.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if orderby=="":
        orderby_str = " order by id"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " log.id")
      orderby_str = orderby_str.replace(" id", " log.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="movement":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "movement"
      fld_value = "movement"
      fields_ = [{"transnumber":"t.transnumber"}, {"represent_rownumber":"movement.id"},
                 {"movetype":"g.groupvalue"}, {"partnumber":"p.partnumber"}, 
                 {"serial":"tl.serial"}, {"planumber":"pl.planumber"}, {"shippingdate":"movement.shippingdate"}, 
                 {"qty":"movement.qty"}, {"notes":"movement.notes"}, {"shared":"movement.shared"}]
      select_str ="select @id, t.transnumber, movement.id as represent_rownumber, g.groupvalue as movetype, p.partnumber, \
      tl.serial, pl.planumber, movement.shippingdate, movement.qty, movement.notes, movement.shared "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "movement.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if params.has_key("use_deleted"):
        from_str = " from movement inner join trans t on (movement.trans_id=t.id) inner join groups g on movement.movetype=g.id \
          left join product p on (movement.product_id=p.id) left join tool tl on (movement.tool_id=tl.id) left join place pl on (movement.place_id = pl.id) "
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"movement.deleted"})
        select_str+=", movement.deleted "
      else:
        from_str = " from movement inner join trans t on (movement.trans_id=t.id and t.deleted=0) inner join groups g on movement.movetype=g.id \
          left join product p on (movement.product_id=p.id and p.deleted=0) left join tool tl on (movement.tool_id=tl.id and tl.deleted=0) left join place pl on (movement.place_id = pl.id and pl.deleted=0) "
        where_str = " where movement.deleted=0 "+where_str
      if self.ns.employee:
        where_str += " and t.transtype not in(select subtype from ui_audit \
          inner join groups nt on ui_audit.nervatype = nt.id and nt.groupvalue='trans' \
          inner join groups ifa on ui_audit.inputfilter = ifa.id and ifa.groupvalue='disabled' \
          where usergroup = "+str(self.ns.employee.usergroup)+") "
      if orderby=="":
        orderby_str = " order by transnumber, id"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " movement.id")
      orderby_str = orderby_str.replace(" id", " movement.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
      
      if self.validate:
        data_audit = self.ns.connect.getDataAudit()
        if data_audit=="usergroup":
          where_str += " and t.cruser_id in (select id from employee where usergroup = "+str(self.ns.employee.usergroup)+") "
        elif data_audit=="own":
          where_str += " and t.cruser_id = "+str(self.ns.employee.id)+" "
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="numberdef":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "numberdef"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("setting")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: setting"
      
      fields = ["numberkey", "prefix", "curvalue", "isyear", "sep", "len", "description", "visible", "readonly", "orderby"]
      select_str ="select @id, numberkey, prefix, curvalue, isyear, sep, len, description, visible, readonly, orderby "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from numberdef "
      where_str = " where 1=1 "+where_str
      if orderby=="":
        orderby_str = " order by id"
      else:
        orderby_str = orderby
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="pattern":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "pattern"
      fields_ = [{"description":"pattern.description"}, {"transtype":"g.groupvalue"}, {"notes":"pattern.notes"}, {"defpattern":"pattern.defpattern"}]
      select_str ="select @id, pattern.description, g.groupvalue as transtype, pattern.notes, pattern.defpattern "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "pattern.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from pattern inner join groups g on pattern.transtype=g.id "
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"pattern.deleted"})
        select_str+=", pattern.deleted "
      else:
        where_str = " where pattern.deleted=0 "+where_str
      if self.ns.employee:
        where_str += " and pattern.transtype not in(select subtype from ui_audit \
          inner join groups nt on ui_audit.nervatype = nt.id and nt.groupvalue='trans' \
          inner join groups ifa on ui_audit.inputfilter = ifa.id and ifa.groupvalue='disabled' \
          where usergroup = "+str(self.ns.employee.usergroup)+") "
      if orderby=="":
        orderby_str = " order by id"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " pattern.id")
      orderby_str = orderby_str.replace(" id", " pattern.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="payment":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "payment"
      fld_value = "payment"
      fields_ = [{"transnumber":"t.transnumber"}, 
                 {"represent_rownumber":"payment.id"}, {"paiddate":"payment.paiddate"}, 
                 {"amount":"payment.amount"}, {"notes":"payment.notes"}]
      select_str ="select @id, t.transnumber, payment.id as represent_rownumber, payment.paiddate, payment.amount, payment.notes "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "payment.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from payment inner join trans t on payment.trans_id=t.id inner join groups g on t.transtype=g.id "
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"payment.deleted"})
        select_str+=", payment.deleted "
      else:
        where_str = " where payment.deleted=0 and (t.deleted=0 or (g.groupvalue='cash'))"+where_str
      if orderby=="":
        orderby_str = " order by transnumber, id"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " payment.id")
      if self.ns.employee:
        where_str += " and t.transtype not in(select subtype from ui_audit \
          inner join groups nt on ui_audit.nervatype = nt.id and nt.groupvalue='trans' \
          inner join groups ifa on ui_audit.inputfilter = ifa.id and ifa.groupvalue='disabled' \
          where usergroup = "+str(self.ns.employee.usergroup)+") "
      orderby_str = orderby_str.replace(" id", " payment.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
      
      if self.validate:
        data_audit = self.ns.connect.getDataAudit()
        if data_audit=="usergroup":
          where_str += " and t.cruser_id in (select id from employee where usergroup = "+str(self.ns.employee.usergroup)+") "
        elif data_audit=="own":
          where_str += " and t.cruser_id = "+str(self.ns.employee.id)+" "
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="place":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "place"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("setting")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: setting"
      
      fld_value = "place"
      fields_ = [{"planumber":"place.planumber"}, {"placetype":"g.groupvalue"}, {"description":"place.description"}, 
                 {"curr":"place.curr"}, {"defplace":"place.defplace"}, {"notes":"place.notes"}, {"inactive":"place.inactive"}]
      select_str ="select @id, place.planumber, g.groupvalue as  placetype, place.description, place.curr, place.defplace, place.notes, place.inactive "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "place.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if params.has_key("use_deleted"):
        from_str = " from place inner join groups g on place.placetype=g.id "
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"place.deleted"})
        select_str+=", place.deleted "
      else:
        from_str = " from place inner join groups g on place.placetype=g.id "
        where_str = " where place.deleted=0 "+where_str
      if orderby=="":
        orderby_str = " order by planumber"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " place.id")
      orderby_str = orderby_str.replace(" id", " place.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="price":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "price"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("price")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: price"
      
      fld_value = "price"
      fields_ = [{"partnumber":"p.partnumber"}, {"pricetype":"case when discount is null then 'price' else 'discount' end"}, {"validfrom":"price.validfrom"}, 
                 {"validto":"price.validto"}, {"curr":"price.curr"}, {"qty":"price.qty"}, {"pricevalue":"price.pricevalue"}, 
                 {"discount":"price.discount"}, {"calcmode":"g.groupvalue"}, {"vendorprice":"price.vendorprice"}]
      select_str ="select @id, p.partnumber, case when discount is null then 'price' else 'discount' end as pricetype, price.validfrom, price.validto, price.curr, \
        price.qty, price.pricevalue, price.discount, case when discount is null then null else g.groupvalue end as calcmode, price.vendorprice "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "price.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if params.has_key("use_deleted"):
        from_str = " from price inner join product p on (price.product_id=p.id) left join groups g on price.calcmode=g.id "
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"price.deleted"})
        select_str+=", price.deleted "
      else:
        from_str = " from price inner join product p on (price.product_id=p.id and p.deleted=0) left join groups g on price.calcmode=g.id "
        where_str = " where price.deleted=0 "+where_str
      if orderby=="":
        orderby_str = " order by partnumber, validfrom"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " price.id")
      orderby_str = orderby_str.replace(" id", " price.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="product":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "product"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("product")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: product"
      
      fld_value = "product"
      fields_ = [{"partnumber":"product.partnumber"}, {"description":"product.description"}, {"protype":"g.groupvalue"}, {"unit":"product.unit"}, 
                 {"taxcode":"tax.taxcode"}, {"notes":"product.notes"}, {"webitem":"product.webitem"}, {"inactive":"product.inactive"}]
      select_str ="select @id, product.partnumber, product.description, g.groupvalue as protype, product.unit, tax.taxcode, product.notes, product.webitem, product.inactive "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "product.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from product inner join groups g on product.protype=g.id inner join tax on product.tax_id=tax.id "
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"product.deleted"})
        select_str+=", product.deleted "
      else:
        where_str = " where product.deleted=0 "+where_str
      if orderby=="":
        orderby_str = " order by partnumber"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " product.id")
      orderby_str = orderby_str.replace(" id", " product.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="project":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "project"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("project")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: project"
      
      fld_value = "project"
      fields_ = [{"pronumber":"project.pronumber"}, {"description":"project.description"}, {"custnumber":"c.custnumber"}, {"startdate":"project.startdate"}, 
                 {"enddate":"project.enddate"}, {"notes":"project.notes"}, {"inactive":"project.inactive"}]
      select_str ="select @id, project.pronumber, project.description, c.custnumber, project.startdate, project.enddate, project.notes, project.inactive "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "project.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if params.has_key("use_deleted"):
        from_str = " from project left join customer c on (project.customer_id=c.id) "
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"project.deleted"})
        select_str+=", project.deleted "
      else:
        from_str = " from project left join customer c on (project.customer_id=c.id and c.deleted=0) "
        where_str = " where project.deleted=0 "+where_str
      if orderby=="":
        orderby_str = " order by pronumber"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " project.id")
      orderby_str = orderby_str.replace(" id", " project.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="rate":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "rate"
      fld_value = "rate"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("setting")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: setting"
      
      fields_ = [{"ratetype":"g.groupvalue"}, {"ratedate":"rate.ratedate"}, {"curr":"rate.curr"}, {"planumber":"p.planumber"}, 
                 {"rategroup":"rg.groupvalue"}, {"ratevalue":"rate.ratevalue"}]
      select_str ="select @id, g.groupvalue as ratetype, ratedate, rate.curr, p.planumber, rg.groupvalue as rategroup, rate.ratevalue "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "rate.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if params.has_key("use_deleted"):
        from_str = " from rate inner join groups g on rate.ratetype=g.id left join place p on (rate.place_id=p.id) \
          left join groups rg on (rategroup=rg.id) "
        where_str = " where 1=1  "+where_str
        fields_.append({"deleted":"rate.deleted"})
        select_str+=", rate.deleted "
      else:
        from_str = " from rate inner join groups g on rate.ratetype=g.id left join place p on (rate.place_id=p.id and p.deleted=0) \
          left join groups rg on (rategroup=rg.id and rg.deleted=0) "
        where_str = " where rate.deleted=0  "+where_str
      if orderby=="":
        orderby_str = " order by rategroup, ratedate, curr"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " rate.id")
      orderby_str = orderby_str.replace(" id", " rate.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="tax":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "tax"
      fld_value = "tax"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("setting")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: setting"
      
      fields = ["taxcode", "description", "rate", "inactive"]
      select_str ="select @id, taxcode, description, rate, inactive "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "tax.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from tax "
      where_str = " where 1=1 "+where_str
      if orderby=="":
        orderby_str = " order by tax.id"
      else:
        orderby_str = orderby
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="tool":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "tool"
      
      if self.validate:
        audit = self.ns.connect.getObjectAudit("tool")
        if audit=="error":
          return "Error|"+str(self.ns.error_message)
        if audit=="disabled":
          return "Error|Disabled type: tool"
      
      fld_value = "tool"
      fields_ = [{"serial":"tool.serial"}, {"description":"tool.description"}, {"partnumber":"p.partnumber"}, {"toolgroup":"g.groupvalue"}, 
                 {"notes":"tool.notes"}, {"inactive":"tool.inactive"}]
      select_str ="select @id, tool.serial, tool.description, p.partnumber, g.groupvalue as toolgroup, tool.notes, tool.inactive "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "tool.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from tool inner join product p on tool.product_id=p.id left join groups g on tool.toolgroup=g.id "
      if params.has_key("use_deleted"):
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"tool.deleted"})
        select_str+=", tool.deleted "
      else:
        where_str = " where tool.deleted=0 "+where_str
      if orderby=="":
        orderby_str = " order by serial"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " tool.id")
      orderby_str = orderby_str.replace(" id", " tool.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="trans":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "trans"
      fld_value = "trans"
      fields_ = [{"transnumber":"trans.transnumber"}, {"transtype":"g.groupvalue"}, {"direction":"gdir.groupvalue"}, {"ref_transnumber":"trans.ref_transnumber"}, {"crdate":"trans.crdate"}, 
                 {"transdate":"trans.transdate"}, {"duedate":"trans.duedate"}, {"custnumber":"c.custnumber"}, {"empnumber":"e.empnumber"}, 
                 {"department":"dg.groupvalue"}, {"pronumber":"p.pronumber"}, {"planumber":"pl.planumber"}, {"paidtype":"pg.groupvalue"}, 
                 {"curr":"trans.curr"}, {"notax":"trans.notax"}, {"paid":"trans.paid"}, {"acrate":"trans.acrate"}, {"notes":"trans.notes"}, 
                 {"intnotes":"trans.intnotes"}, {"fnote":"trans.fnote"}, {"transtate":"sg.groupvalue"}, {"closed":"trans.closed"}, {"username":"cruser.username"}]
      select_str ="select @id, trans.transnumber, g.groupvalue as transtype, gdir.groupvalue as direction, trans.ref_transnumber, trans.crdate, trans.transdate, trans.duedate, c.custnumber, e.empnumber, \
        dg.groupvalue as department, p.pronumber, pl.planumber, pg.groupvalue as paidtype, trans.curr, trans.notax, trans.paid, trans.acrate, trans.notes, trans.intnotes, \
        trans.fnote, sg.groupvalue as transtate, trans.closed, cruser.username "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "trans.id,")
      else:
        select_str = select_str.replace("@id,", "")
      if params.has_key("use_deleted"):
        from_str = " from trans inner join groups g on trans.transtype=g.id inner join groups gdir on trans.direction=gdir.id left join customer c on (trans.customer_id=c.id) left join employee e on (trans.employee_id=e.id) \
          left join groups dg on (trans.department=dg.id) left join project p on (trans.project_id = p.id) left join place pl on (trans.place_id=pl.id) \
          left join groups pg on trans.paidtype=pg.id inner join groups sg on trans.transtate=sg.id inner join employee cruser on trans.cruser_id=cruser.id"
        where_str = " where 1=1 "+where_str
        fields_.append({"deleted":"trans.deleted"})
        select_str+=", trans.deleted "
      else:
        from_str = " from trans inner join groups g on trans.transtype=g.id inner join groups gdir on trans.direction=gdir.id left join customer c on (trans.customer_id=c.id and c.deleted=0) left join employee e on (trans.employee_id=e.id and e.deleted=0) \
          left join groups dg on (trans.department=dg.id and dg.deleted=0) left join project p on (trans.project_id = p.id and p.deleted=0) left join place pl on (trans.place_id=pl.id and pl.deleted=0) \
          left join groups pg on trans.paidtype=pg.id inner join groups sg on trans.transtate=sg.id inner join employee cruser on trans.cruser_id=cruser.id"
        where_str = " where (trans.deleted=0 or (g.groupvalue='invoice' and gdir.groupvalue='out') or (g.groupvalue='receipt' and gdir.groupvalue='out') or (g.groupvalue='cash')) "+where_str
      if self.ns.employee:
        where_str += " and trans.transtype not in(select subtype from ui_audit \
          inner join groups nt on ui_audit.nervatype = nt.id and nt.groupvalue='trans' \
          inner join groups ifa on ui_audit.inputfilter = ifa.id and ifa.groupvalue='disabled' \
          where usergroup = "+str(self.ns.employee.usergroup)+") "
      if orderby=="":
        orderby_str = " order by transnumber"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " trans.id")
      orderby_str = orderby_str.replace(" id", " trans.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
      
      if self.validate:
        data_audit = self.ns.connect.getDataAudit()
        if data_audit=="usergroup":
          where_str += " and trans.cruser_id in (select id from employee where usergroup = "+str(self.ns.employee.usergroup)+") "
        elif data_audit=="own":
          where_str += " and trans.cruser_id = "+str(self.ns.employee.id)+" "
                                                                                                                                          
  #--------------------------------------------------------------------------------------------------------------------------------------------        
    else:
      return "Error|Unknown datatype: "+params["datatype"]
  #--------------------------------------------------------------------------------------------------------------------------------------------        
    
    xml_query=""
    dfields={}
    if params["datatype"]!="sql":
      if fld_value!="" and not filter.has_key("no_deffield"):
        colname = "description"
        if self.ns.engine in("mysql","google_sql"):
          int_type = "signed"
        else:
          int_type = "integer"
        deffield_query = "select deffield.fieldname, deffield.description, groups.groupvalue as fieldtype from deffield inner join groups on deffield.fieldtype=groups.id \
          where deffield.deleted=0 and deffield.visible=1 and deffield.nervatype=(select id from groups where groupname='nervatype' and groupvalue='"+fld_value+"')"
        fv_query=""
        fieldnames = self.ns.db.executesql(deffield_query, as_dict=True)
        for idx in range(len(fieldnames)):
          dfields[fieldnames[idx]["fieldname"]]=fieldnames[idx]["description"]
          if filter["output"].startswith("xml"):
            if where_str.find(fieldnames[idx][colname])>-1:
              return "Error|Additional field xml output is not allowed in where string: "+fieldnames[idx][colname]+". Use the search fieldvalue object 'description' field!"
            if orderby_str.find(fieldnames[idx][colname])>-1:
              return "Error|Additional field xml output is not allowed in orderby string: "+fieldnames[idx][colname]
            xml_query += "union select fieldvalue.id as id, fieldvalue.fieldname as fieldname,'"+fieldnames[idx]["description"]+"' as description,'"+fieldnames[idx]["fieldtype"] \
              +"' as fieldtype, @value as value ,fieldvalue.notes as notes from fieldvalue @join_str where fieldvalue.deleted=0 and fieldname='"+fieldnames[idx]["fieldname"]+"' and ref_id = @id "
          else:
            fields.append(fieldnames[idx][colname])
            fv_query += " left join fieldvalue lj_"+str(idx)+" on "+fld_value+".id = lj_"+str(idx)+".ref_id and lj_"+str(idx)+".fieldname='"+fieldnames[idx]["fieldname"]+"' and lj_"+str(idx)+".deleted=0 \n"
          if fieldnames[idx]["fieldtype"]=="date":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "").replace("@value", "fieldvalue.value")
            else:
              select_str+=", lj_"+str(idx)+".value "
              where_str = where_str.replace(fieldnames[idx][colname], "cast(lj_"+str(idx)+".value as date)")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "cast(lj_"+str(idx)+".value as date)")
          elif fieldnames[idx]["fieldtype"]=="float":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "").replace("@value", "fieldvalue.value")
            else:
              select_str+=", lj_"+str(idx)+".value "
              where_str = where_str.replace(fieldnames[idx][colname], "cast(lj_"+str(idx)+".value as real)")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "cast(lj_"+str(idx)+".value as real)")
          elif fieldnames[idx]["fieldtype"]=="integer":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "").replace("@value", "fieldvalue.value")
            else:
              select_str+=", lj_"+str(idx)+".value "
              where_str = where_str.replace(fieldnames[idx][colname], "cast(lj_"+str(idx)+".value as "+int_type+")")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "cast(lj_"+str(idx)+".value as "+int_type+")")
          elif fieldnames[idx]["fieldtype"]=="customer":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join customer on cast(value as "+int_type+")=customer.id ").replace("@value", "customer.custnumber")
            else:
              fv_query += " left join customer rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as "+int_type+")=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".custname "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".custname")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".custname")
          elif fieldnames[idx]["fieldtype"]=="tool":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join tool on cast(value as "+int_type+")=tool.id ").replace("@value", "tool.serial")
            else:
              fv_query += " left join tool rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as "+int_type+")=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".serial "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".serial")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".serial")
          elif fieldnames[idx]["fieldtype"]in ('trans','transitem','transmovement','transpayment'):
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join trans on cast(value as "+int_type+")=trans.id ").replace("@value", "trans.transnumber")
            else:
              fv_query += " left join trans rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as "+int_type+")=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".transnumber "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".transnumber")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".transnumber")
          elif fieldnames[idx]["fieldtype"]=="product":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join product on cast(value as "+int_type+")=product.id ").replace("@value", "product.partnumber")
            else:
              fv_query += " left join product rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as "+int_type+")=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".partnumber "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".partnumber")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".partnumber")
          elif fieldnames[idx]["fieldtype"]=="project":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join project on cast(value as "+int_type+")=project.id ").replace("@value", "project.pronumber")
            else:
              fv_query += " left join project rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as "+int_type+")=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".pronumber "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".pronumber")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".pronumber")
          elif fieldnames[idx]["fieldtype"]=="employee":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join employee on cast(value as "+int_type+")=employee.id ").replace("@value", "employee.empnumber")
            else:
              fv_query += " left join employee rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as "+int_type+")=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".empnumber "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".empnumber")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".empnumber")
          elif fieldnames[idx]["fieldtype"]=="place":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join place on cast(value as "+int_type+")=place.id ").replace("@value", "place.planumber")
            else:
              fv_query += " left join place rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as "+int_type+")=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".planumber "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".planumber")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".planumber")
          else:
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "").replace("@value", "fieldvalue.value")
            else:
              select_str+=", lj_"+str(idx)+".value "
              where_str = where_str.replace(fieldnames[idx][colname], "lj_"+str(idx)+".value")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "lj_"+str(idx)+".value")
        if filter["output"].startswith("xml"):
          if xml_query!="":
            xml_query += " order by fieldname,id"
        else:
          from_str+=fv_query
      
      try:
        items = list(self.ns.db.executesql(select_str+" "+from_str+" "+where_str+" "+orderby_str+" "+limit_str, as_dict=False))
      except Exception, err:
        return "Error|"+str(err)
    
    def get_refnumber(row,repkey,use_deleted):
      try:
        ref_id = row[fields.index(represents[repkey]["ref_id_field"])]
        if represents[repkey]["nervatype_field"]==None:
          nervatype = params["datatype"]
        else:
          nervatype = row[fields.index(represents[repkey]["nervatype_field"])]
        if repkey=="represent_fieldvalue":
          if nervatype in("customer","employee","place","product","project","tool","trans","event"):
            return self.ns.valid.show_refnumber(represents[repkey]["rettype"],nervatype, int(ref_id), None, use_deleted)
          elif nervatype=="password":
            return ref_id
          else:
            return ref_id
        else:
          return self.ns.valid.show_refnumber(represents[repkey]["rettype"],nervatype, ref_id, None, use_deleted)
      except Exception:
        return "Missing refnumber value"
      
    represents = {
      "represent_rownumber":{
          "label":"rownumber*", "rettype":"index", "ref_id_field":"represent_rownumber", 
          "nervatype_field":None, "function":get_refnumber},
      "represent_refnumber":{
          "label":"refnumber*", "rettype":"refnumber", "ref_id_field":"represent_refnumber", 
          "nervatype_field":None, "function":get_refnumber},
      "represent_refnumber_nervatype":{
          "label":"refnumber*", "rettype":"refnumber", "ref_id_field":"represent_refnumber_nervatype", 
          "nervatype_field":"nervatype", "function":get_refnumber},
      "represent_refnumber1":{
          "label":"refnumber1*", "rettype":"refnumber", "ref_id_field":"represent_refnumber1", 
          "nervatype_field":"nervatype1", "function":get_refnumber},
      "represent_refnumber2":{
          "label":"refnumber2*", "rettype":"refnumber", "ref_id_field":"represent_refnumber2", 
          "nervatype_field":"nervatype2", "function":get_refnumber},
      "represent_fieldvalue":{
          "label":"value*", "rettype":"refnumber", "ref_id_field":"represent_fieldvalue", 
          "nervatype_field":"fieldtype", "function":get_refnumber},
      "represent_fieldname":{
          "label":"fieldname*", "rettype":"fieldname", "ref_id_field":"represent_fieldname", 
          "nervatype_field":None, "function":get_refnumber},
      }
    
    if len(items)>0:
      rep_cols,del_cols = {},[]
      for col in range(len(fields)):
        if fields[col].startswith("represent_"):
          if represents.has_key(fields[col]):
            rep_cols[str(fields[col])]=col
          if represents[fields[col]].has_key("replace_field"):
            del_cols.append(fields.index(represents[fields[col]]["replace_field"]))
      if len(rep_cols)>0:
        if len(del_cols)>0: del_cols.sort(reverse=True)
        for row in range(len(items)):
          items[row] = list(items[row])
          for del_col in del_cols:
            items[row].pop(del_col)
          for field in rep_cols.keys():
            items[row][rep_cols[field]] = represents[field]["function"](items[row],field,params.has_key("use_deleted"))
            if items[row][rep_cols[field]]==None: 
              items[row][0] = "__deleted__"  
        for field in rep_cols.keys():
          if represents[field].has_key("label"):
            fields[rep_cols[field]] = represents[field]["label"]
        items = [row for row in items if row[0]!="__deleted__"]
        for del_col in del_cols:
            fields.pop(del_col)
                  
      if filter.has_key("columns"):
        if filter["columns"]!="":
          items_=[]
          columns=filter["columns"].split(",")
          for item in items:
            item_ = []
            for col in range(len(columns)):
              ref_col = next((i for i in xrange(len(fields)) if fields[i] == columns[col]), None)
              if ref_col is not None:
                item_.append(item[ref_col])
              elif dfields.has_key(columns[col]):
                ref_col = next((i for i in xrange(len(fields)) if fields[i] == dfields[columns[col]]), None)
                if ref_col is not None:
                  item_.append(item[ref_col])
            items_.append(item_)          
          fields = columns
          items = items_         
      
      if filter["output"] in("html","excel"):
        if len(header)>0:
          for col in range(len(header)):
            if col <= len(fields)-1:
              fields[col] = header[col]
                    
      if filter["output"]=="json":
        retvalue = []
        for row in range(1,len(items)):
          jrow = OrderedDict()
          for col in range(len(fields)):
            jrow[fields[col]] = items[row][col]
          retvalue.append(jrow)  
      if filter["output"].startswith("xml"):
        retvalue = self.createXML(fields, items, item_str, xml_query, filter["show_id"])
      if filter["output"]=="text":
        retvalue = self.createText(fields, items)
      if filter["output"]=="html":
        for col in range(len(fields)):
          fields[col]=TH(*fields[col], _style="text-align:left;background-color: #8B8B83;color: #FFFFFF;padding:3px;")
        numrec=0
        for row in range(len(items)):
          if numrec % 2 == 0:
            style = ''
          else:
            style = 'background-color: #F9F9F9;'
          numrec+=1
          items[row]=TR(*[TD(field, _style="text-align:right;padding:3px;") if str(field).replace(".", "").replace(",", "").isdigit() else TD(field, _style="padding:3px;") for field in items[row]]
                        ,_style=style)
        retvalue = TABLE(TR(*fields), items, _style="border-style: solid;border-width: 1px;border-color: #8B8B83;font-size: small;", 
                         _cellspacing="3", _cellpadding="0")
      if filter["output"]=="excel":
        retvalue = self.createExcel(item_str, fields, items)
    else:
      retvalue = "OK|Filters that are not data..."     
    return retvalue
  
  def createText(self, fields, items):
    retstr = "|".join(str(v) for v in fields if v > 0)
    for row in items:
      retstr = retstr+"|\n"
      for cell in row:
        retstr = retstr+"|"+str(cell)
    return retstr
      
  def createXML(self, fields, items, datatype, fquery, show_id):
    from xml.dom.minidom import Document
    doc = Document()
    data = doc.createElement("data")
    doc.appendChild(data)
    for row in range(len(items)):
      xrow = doc.createElement(datatype)
      xvalue = None
      xname = None
      for col in range(len(fields)):
        if fields[col]=="id" and show_id!="sql":
          ref_id = items[row][col]
          if show_id!="xml":
            xrow.setAttribute("id",str(ref_id))
        else:
          xfield = doc.createElement("field")
          xname = doc.createElement("name")
          xname.appendChild(doc.createCDATASection(str(fields[col]).replace("*", "")))
          xfield.appendChild(xname)
          xvalue = doc.createElement("value")
          if str(items[row][col])!="None":
            xvalue.appendChild(doc.createCDATASection(str(items[row][col])))
          else:
            xvalue.appendChild(doc.createCDATASection(""))
          xfield.appendChild(xvalue)
          xrow.appendChild(xfield)
      if fquery!="":
        rquery = str(fquery)[6:].replace("@id",str(ref_id))
        findex = {}
        fvalues = self.ns.db.executesql(rquery, as_dict=True)
        for fvalue in fvalues:
          xfield = doc.createElement("field")
          xvalue = doc.createElement("name")
          xvalue.appendChild(doc.createCDATASection(str(fvalue["fieldname"])))
          xfield.appendChild(xvalue)
          xvalue = doc.createElement("index")
          if findex.has_key(fvalue["fieldname"]):
            findex[fvalue["fieldname"]]+=1
          else:
            findex[fvalue["fieldname"]]=1
          xvalue.appendChild(doc.createCDATASection(str(findex[fvalue["fieldname"]])))
          xfield.appendChild(xvalue)
          xvalue = doc.createElement("value")
          if str(fvalue["value"])!="None":
            xvalue.appendChild(doc.createCDATASection(str(fvalue["value"])))
          else:
            xvalue.appendChild(doc.createCDATASection(""))
          xfield.appendChild(xvalue)
          xvalue = doc.createElement("data")
          if str(fvalue["notes"])!="None":
            xvalue.appendChild(doc.createCDATASection(str(fvalue["notes"])))
          else:
            xvalue.appendChild(doc.createCDATASection(""))
          xfield.appendChild(xvalue)
          xrow.appendChild(xfield)
          xvalue = doc.createElement("type")
          xvalue.appendChild(doc.createCDATASection(str(fvalue["fieldtype"])))
          xfield.appendChild(xvalue)
          xvalue = doc.createElement("label")
          xvalue.appendChild(doc.createCDATASection(str(fvalue["description"])))
          xfield.appendChild(xvalue)
      data.appendChild(xrow)
    return doc.toxml(encoding='utf-8')
  
  def createExcel(self, sheetName, fields, items):
    import xlwt
    import StringIO
    
    output = StringIO.StringIO()
    book = xlwt.Workbook(encoding='utf-8')
    styles = {
    'header': xlwt.easyxf(
      'font: bold true, height 160;'
      'alignment: horizontal left, vertical center;'
      'pattern: back_colour gray25;'
      'borders: left thin, right thin, top thin, bottom thin;'),
    'float': xlwt.easyxf(
      'alignment: horizontal right, vertical center;'
      'borders: left thin, right thin, top thin, bottom thin;',
      num_format_str='# ### ##0.00'),
    'integer': xlwt.easyxf(
      'alignment: horizontal right, vertical center;'
      'borders: left thin, right thin, top thin, bottom thin;',
      num_format_str='# ### ##0'),
    'date': xlwt.easyxf(
      'alignment: horizontal center, vertical center;'
      'borders: left thin, right thin, top thin, bottom thin;',
      num_format_str='yyyy.mm.dd'),
    'datetime': xlwt.easyxf(
      'alignment: horizontal center, vertical center;'
      'borders: left thin, right thin, top thin, bottom thin;',
      num_format_str='yyyy.mm.dd HH:MM'),
    'bool': xlwt.easyxf(
      'alignment: horizontal center, vertical center;'
      'borders: left thin, right thin, top thin, bottom thin;'),
    'string': xlwt.easyxf(
      'alignment: horizontal left, vertical center;'
      'borders: left thin, right thin, top thin, bottom thin;')}
    sheet1 = book.add_sheet(sheetName)     
    colnum = 0;
    for col in fields:
      sheet1.write(0, colnum, col, styles["header"])
      colnum = colnum + 1
    rownum = 1  
    for row in items:
      colnum = 0;
      for cell in row:
        if type(cell).__name__=="datetime":
          sheet1.write(rownum, colnum, cell, styles["datetime"])
        elif type(cell).__name__=="date":
          sheet1.write(rownum, colnum, cell, styles["date"])
        elif type(cell).__name__=="float":
          sheet1.write(rownum, colnum, cell, styles["float"])
        elif type(cell).__name__=="int":
          sheet1.write(rownum, colnum, cell, styles["integer"])
        elif type(cell).__name__=="bool":
          sheet1.write(rownum, colnum, cell, styles["bool"])
        else:
          sheet1.write(rownum, colnum, cell, styles["string"])
        colnum = colnum + 1
      rownum = rownum + 1
    book.save(output)
    contents = output.getvalue()
    output.close
    
    return contents      