# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Project
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

from gluon.html import TABLE, TR, TH, TD
from nerva2py.localstore import setEngine
from nerva2py.tools import NervaTools

class Ndi(object):
  ns = None
  dbfu = NervaTools()
  logState = True
  
  def __init__(self, NervaStore):
    self.ns = NervaStore
    
  def getLogin(self, params):
    validator = {}
    validator["valid"] = False   
    validator["message"] = "OK"
    if params.has_key("database")!=True:
      validator["message"] = str(self.ns.T("Error|Missing login parameter:"))+" database" 
      return validator
    if params.has_key("username")!=True:
      validator["message"] = str(self.ns.T("Error|Missing login parameter:"))+" username"
      return validator 
    if  params.has_key("password")!=True:
      validator["message"] = str(self.ns.T("Error|Missing login parameter:"))+" password"
      return validator
    if params["password"]=="":
      params["password"] = None
    if self.ns.db==None:
      if setEngine(self.ns, params["database"],True)==False:
        validator["valid"] = False
        if self.ns.error_message!="":
          validator["message"] = str(self.ns.error_message)
        else: 
          validator["message"] = str(self.ns.T("Could not connect to the database: ")+params["database"])
        return validator
    if self.ns.setLogin(params["username"], params["password"])==False:
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
    
  def getNumberName(self, nervatype):
    if nervatype=="customer":
      return "custnumber"
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
    elif nervatype=="tool":
      return "serial"
    elif nervatype=="trans":
      return "transnumber"
    else:
      return "Error|Unknown nervatype. Valid values: customer, employee, event, groups, place, product, project, tool, trans."
  
  def getItemFromKey(self, table, field, value):
    #from/return object
    retval = None
    index = next((i for i in xrange(len(table)) if table[i][field] == value), None)
    if index is not None:
      retval = table[index]
    return retval
        
  #----------------------------------------------------------------------------------------------------
  #----------------------------------------------------------------------------------------------------
  
  def getSetting(self, fieldname):
    logini = self.ns.db((self.ns.db.fieldvalue.fieldname==fieldname)).select().as_list()
    return logini[0]["value"] if len(logini)>0 else ""
  
  def get_default_value(self, fieldtype):
    fld_type = self.ns.db.groups(id=fieldtype)["groupvalue"]
    if fld_type == 'bool':
      return "false"
    elif fld_type == 'integer' or fld_type == 'float':
      return "0"
    else:
      return ""
      
  def setLogtable(self, params, logstate, inikey=None, nervatype=None, log_id=None):
    from datetime import datetime
    
    if not self.logState: return True
    if inikey:
      update_log = self.getSetting(inikey)
      if update_log!="true": return True
    if nervatype:
      neraid = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==nervatype)).select().as_list()[0]["id"]
    else:
      neraid = None
    logstate_id = self.ns.db((self.ns.db.groups.groupname=="logstate")&(self.ns.db.groups.groupvalue==logstate)).select().as_list()[0]["id"]
    values = {"nervatype":neraid, "ref_id":neraid, "ref_id":log_id, "logstate":logstate_id, "employee_id":self.ns.employee["id"], "crdate":datetime.now()}
    ret = self.ns.db.log.validate_and_insert(**values)
    if ret.errors:
      return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
    return True
  
  def deleteNervaObj1(self, params, data, nervatype, refnumber, refid=None):
    retvalue = "OK"
    if not refid: refid = refnumber
    for row in data:
      if row.has_key(refnumber)!=True:
        return "Error|Missing required parameter: "+str(refnumber)
      objlist = self.ns.db(self.ns.db[nervatype][refid]==row[refnumber]).select().as_list()
      if len(objlist)>0:    
        try:
          self.ns.db(self.ns.db[nervatype]["id"] == objlist[0]["id"]).delete()
        except Exception, err:
          self.ns.db.rollback()
          return str(err)
        retvalue = retvalue+"|"+str(row[refnumber])
    return retvalue
  
  def deleteNervaObj2(self, params, data, nervatype, refnumber, refid=None, refnumber2=None, refid2=None):
    retvalue = "OK"
    if nervatype not in("deffield","groups","pattern","place"):
      audit = self.ns.getObjectAudit(nervatype)
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: "+ nervatype
    delete_ini = self.getSetting("set_trans_deleted")
    if not refid: refid = refnumber
    for row in data:
      if row.has_key(refnumber)!=True:
        return "Error|Missing required parameter: "+str(refnumber)   
      delobj_ = None
      if not refnumber2:
        objlist = self.ns.db(self.ns.db[nervatype][refid]==row[refnumber]).select().as_list()
      else:
        if row.has_key(refnumber2)!=True:
          return "Error|Missing required parameter: "+str(refnumber2)
        if not refid2: refid2 = refnumber2
        objlist = self.ns.db((self.ns.db[nervatype][refid]==row[refnumber])&(self.ns.db[nervatype][refid2]==row[refnumber2])).select().as_list()
      if len(objlist)>0:
        delobj_ = objlist[0]
      if delobj_ and delobj_.has_key("id"):
        if delobj_.has_key("deleted") and delete_ini != "true":
          values = {"deleted":1}
          ret = self.ns.db(self.ns.db[nervatype]["id"]==delobj_["id"]).validate_and_update(**values)
          if ret.errors:
            self.ns.db.rollback()
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          dfield = self.deleteFieldValues(params, nervatype, delobj_["id"])
          if dfield!=True: return dfield
          try:
            self.ns.db(self.ns.db[nervatype]["id"] == delobj_["id"]).delete()
          except Exception, err:
            self.ns.db.rollback()
            return str(err)
        logst = self.setLogtable(params, "update", "log_"+nervatype+"_delete", nervatype, delobj_["id"])
        if logst!=True: return logst 
        retvalue = retvalue+"|"+str(row[refnumber])
    return retvalue
  
  def deleteTransItem(self, params, data, nervatype):
    #refnumber&rownumber
    retvalue = "OK"
    delete_ini = self.getSetting("set_trans_deleted")
    for row in data:
      if row.has_key("rownumber")!=True:
        return "Error|Missing required parameter: rownumber"
      delobj_ = None
      if row.has_key("transnumber")==True:
        translist = self.ns.db((self.ns.db.trans.deleted==0)&(self.ns.db.trans.transnumber==row["transnumber"])).select().as_list()
        if len(translist)>0:
          itemlist = self.ns.db((self.ns.db[nervatype]["deleted"]==0)&(self.ns.db[nervatype]["trans_id"]==translist[0]["id"])).select().as_list()
          if len(itemlist)>0 and int(row["rownumber"])>0:
            if int(row["rownumber"])<=len(itemlist):
              delobj_ = itemlist[int(row["rownumber"])-1]
        else:
          return "Error|Unknown transnumber: "+str(row["transnumber"])
      else:
        return "Error|Missing required parameter: transnumber"
      
      transtype = self.ns.db((self.ns.db.groups.id==translist[0]["transtype"])).select().as_list()[0]["groupvalue"]
      audit = self.ns.getObjectAudit("trans",transtype)
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Disabled or readonly transtype: "+transtype
      
      if delobj_!=None and delobj_.has_key("id"):
        if delobj_.has_key("deleted") and delete_ini != "true":
          values = {"deleted":1}
          ret = self.ns.db(self.ns.db[nervatype]["id"]==delobj_["id"]).validate_and_update(**values)
          if ret.errors:
            self.ns.db.rollback()
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          dfield = self.deleteFieldValues(params, nervatype, delobj_["id"])
          if dfield!=True:
            return dfield
          try:
            self.ns.db(self.ns.db[nervatype]["id"] == delobj_["id"]).delete()
          except Exception, err:
            self.ns.db.rollback()
            return str(err)
        logst = self.setLogtable(params, "update", "log_trans_delete", "trans", translist[0]["id"])
        if logst!=True:
          return logst 
        retvalue = retvalue+"|"+str(row["transnumber"])+"["+str(row["rownumber"])+"]"
    return retvalue
        
  def setFieldValue(self, fieldname, value, nervatype, refid, insert_field=True):
    from datetime import datetime
    
    if fieldname=="":
      return "Error|Missing required parameter: fieldname"
    else:
      if len(str(fieldname).split("~"))>1:
        try:
          field_index = int(str(fieldname).split("~")[1])
        except Exception:
          field_index = 1
        fieldname = str(fieldname).split("~")[0]
      else:
        field_index = 1
      self.ns.request.vars["fieldname"]=fieldname
    neraid = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==nervatype)).select().as_list()[0]["id"]
    fieldtypes = self.ns.db((self.ns.db.groups.groupname=="fieldtype")).select().as_list()
    deffield = None
    deffields = self.ns.db((self.ns.db.deffield.fieldname==fieldname)).select().as_list()
    if len(deffields)>0:
      if deffields[0]["nervatype"]!=neraid:
        return "Error|Contained new fieldname: "+str(fieldname)
      deffield = deffields[0]
    else:
      if insert_field==True:     
        values = {"fieldname":fieldname, "nervatype":neraid, "fieldtype":self.getItemFromKey(fieldtypes, "groupvalue", "string")["id"],
                  "description":fieldname}
        ret = self.ns.db.deffield.validate_and_insert(**values)
        if ret.errors:
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          deffield = self.ns.db((self.ns.db.deffield.id==ret.id)).select().as_list()[0]     
      else:
        return "Error|Unknown fieldname and missing insert_field parameter"
    
    fieldvalue_id = -1
    if refid!=None:
      fieldvalues = self.ns.db((self.ns.db.fieldvalue.fieldname==fieldname)&(self.ns.db.fieldvalue.ref_id==refid)).select(orderby=self.ns.db.fieldvalue.id).as_list()
    else:
      fieldvalues = self.ns.db(self.ns.db.fieldvalue.fieldname==fieldname).select(orderby=self.ns.db.fieldvalue.id).as_list()
    
    if field_index<=len(fieldvalues):
        fieldvalue_id = fieldvalues[field_index-1]["id"]
            
    if fieldvalue_id == -1:
      if insert_field==True:
        values = {"fieldname":fieldname, "ref_id":refid}
        ret = self.ns.db.fieldvalue.validate_and_insert(**values)
        if ret.errors:
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          fieldvalue_id = self.ns.db((self.ns.db.fieldvalue.id==ret.id)).select().as_list()[0]["id"]
      else:
        return "Error|Unknown fieldname and missing insert_field parameter"
    fieldtype = self.getItemFromKey(fieldtypes, "id", deffield["fieldtype"])["groupvalue"]
    fieldvalue={}
    fieldvalue["deleted"]=0
    if len(str(value).split("~"))>1:
      if str(value).split("~")[1]=="":
        fieldvalue["notes"] = None
      else:
        fieldvalue["notes"] = str(value).split("~")[1]
      value = str(value).split("~")[0]
    if fieldtype=="string" or fieldtype=="notes" or fieldtype=="password":
      fieldvalue["value"] = str(value)
    elif fieldtype=="bool":
      if value=="true" or value=="True" or value=="1":
        fieldvalue["value"] = "true"
      elif value=="false" or value=="False" or value=="0":
        fieldvalue["value"] = "false"
      else:
        return "Error|Incorrect boolen value! Valid values: true, True, 1 or false, False, 0. Fieldname: "+str(fieldname)
    elif fieldtype=="date":
      try:
        if datetime.strptime(value,"%Y-%m-%d").__class__.__name__ == "datetime":
          fieldvalue["value"] = str(value)
      except Exception:
        return "Error|Incorrect date value! Valid datetime format: YYYY-MM-DD. Fieldname: "+str(fieldname)
    elif fieldtype=="float":
      try:
        fieldvalue["value"] = str(float(value))
      except Exception:
        return "Error|Incorrect float value! Fieldname: "+str(fieldname)
    elif fieldtype=="integer":
      try:
        fieldvalue["value"] = str(int(value))
      except Exception:
        return "Error|Incorrect integer value! Fieldname: "+str(fieldname)
    elif fieldtype=="valuelist":
      if deffield["valuelist"]!=None:
        valuelist = deffield["valuelist"].split("|")
        fvalue = next((i for i in xrange(len(valuelist)) if valuelist[i] == value), None)
        if fvalue!=None:
          fieldvalue["value"] = str(value)
        else:
          return "Error|Incorrect valuelist value! Fieldname: "+str(fieldname)
      else:
        return "Error|Incorrect valuelist value! Fieldname: "+str(fieldname)
    elif value=="":
      fieldvalue["value"] = None
    elif fieldtype=="flink":
      fieldvalue["value"] = str(value)
    elif fieldtype=="customer":
      custlist = self.ns.db((self.ns.db.customer.custnumber==value)).select().as_list()
      if len(custlist)>0:
        fieldvalue["value"] = str(custlist[0]["id"])
      else:
        return "Error|Unknown custnumber value! Fieldname: "+str(fieldname)
    elif fieldtype=="tool":
      toolist = self.ns.db((self.ns.db.tool.serial==value)).select().as_list()
      if len(toolist)>0:
        fieldvalue["value"] = str(toolist[0]["id"])
      else:
        return "Error|Unknown serial value! Fieldname: "+str(fieldname)
    elif fieldtype in ('trans','transitem','transmovement','transpayment'):
      translist = self.ns.db((self.ns.db.trans.transnumber==value)).select().as_list()
      if len(translist)>0:
        fieldvalue["value"] = str(translist[0]["id"])
      else:
        return "Error|Unknown transnumber value! Fieldname: "+str(fieldname)
    elif fieldtype=="product":
      prolist = self.ns.db((self.ns.db.product.partnumber==value)).select().as_list()
      if len(prolist)>0:
        fieldvalue["value"] = str(prolist[0]["id"])
      else:
        return "Error|Unknown partnumber value! Fieldname: "+str(fieldname)
    elif fieldtype=="project":
      prolist = self.ns.db((self.ns.db.project.pronumber==value)).select().as_list()
      if len(prolist)>0:
        fieldvalue["value"] = str(prolist[0]["id"])
      else:
        return "Error|Unknown pronumber value! Fieldname: "+str(fieldname)
    elif fieldtype=="employee":
      emplist = self.ns.db((self.ns.db.employee.empnumber==value)).select().as_list()
      if len(emplist)>0:
        fieldvalue["value"] = str(emplist[0]["id"])
      else:
        return "Error|Unknown empnumber value! Fieldname: "+str(fieldname)
    elif fieldtype=="place":
      plalist = self.ns.db((self.ns.db.place.planumber==value)).select().as_list()
      if len(plalist)>0:
        fieldvalue["value"] = str(plalist[0]["id"])
      else:
        return "Error|Unknown planumber value! Fieldname: "+str(fieldname)
    else:
      return "Error|Unknown or can not use a fieldtype: "+str(fieldtype)+" ("+str(fieldname)+")"
    if len(fieldvalue)>0:
      ret = self.ns.db(self.ns.db.fieldvalue.id==fieldvalue_id).validate_and_update(**fieldvalue)
      if ret.errors:
        self.ns.db.rollback()
        return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
    return True
  
  def deleteFieldValues(self, params, nervatype, refid, fieldname=None):
    delete_ini = self.getSetting("set_trans_deleted")
    neraid = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==nervatype)).select().as_list()[0]["id"]
    deffields = self.ns.db((self.ns.db.deffield.nervatype==neraid)).select().as_list()
    if len(deffields)==0:
      return True
    if refid!=None:
      fieldvalues = self.ns.db(self.ns.db.fieldvalue.ref_id==refid).select().as_list()
      for field in fieldvalues:
        if self.getItemFromKey(deffields, "fieldname", field["fieldname"])!=None:
          if delete_ini != "true":
            values = {"deleted":1}
            ret = self.ns.db(self.ns.db.fieldvalue.id==field["id"]).validate_and_update(**values)
            if ret.errors:
              self.ns.db.rollback()
              return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            try:
              self.ns.db(self.ns.db.fieldvalue.id == field["id"]).delete()
            except Exception, err:
              self.ns.db.rollback()
              return str(err)
    else:
      fieldvalues = self.ns.db(self.ns.db.fieldvalue.fieldname==fieldname).select().as_list()
      if len(fieldvalues)>0:
        if delete_ini != "true":
          values = {"deleted":1}
          ret = self.ns.db(self.ns.db.fieldvalue.id==fieldvalues[0]["id"]).validate_and_update(**values)
          if ret.errors:
            self.ns.db.rollback()
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          try:
            self.ns.db(self.ns.db.fieldvalue.id == fieldvalues[0]["id"]).delete()
          except Exception, err:
            self.ns.db.rollback()
            return str(err)
    return True
      
  def update_address(self, params, data):
    retvalue = "OK"
    for row in data:
      if row.has_key("nervatype")!=True:
        return "Error|Missing required parameter: nervatype"
      if row.has_key("refnumber")!=True:
        return "Error|Missing required parameter: refnumber"
      if row.has_key("rownumber")!=True:
        row["rownumber"]=-1
      
      audit = self.ns.getObjectAudit(row["nervatype"])
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: "+row["nervatype"]
      
      nervanumber = self.getNumberName(row["nervatype"])
      if nervanumber.startswith("Error"):
        return nervanumber
      neraid = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==row["nervatype"])).select().as_list()[0]["id"]
      lnkobj=None
      lnkobj = self.ns.db((self.ns.db[row["nervatype"]][nervanumber]==row["refnumber"])).select().as_list()
      if len(lnkobj)==0:
        return "Error|Unknown refnumber No: "+row["refnumber"]
      else:
        lnkobj = lnkobj[0]
        
      address = None
      addlist = self.ns.db((self.ns.db.address.deleted==0)&(self.ns.db.address.nervatype==neraid)&(self.ns.db.address.ref_id==lnkobj["id"])).select(orderby=self.ns.db.address.id).as_list()
      if len(addlist)>0:
        if int(row["rownumber"])>0:
          if int(row["rownumber"])<=len(addlist):
            address = addlist[int(row["rownumber"])-1]
          else:
            row["rownumber"]=len(addlist)+1
        else:
          row["rownumber"]=len(addlist)+1
      else:
          row["rownumber"]=len(addlist)+1
      if address==None:
        if params.has_key("insert_row")!=True:
          return "Error|Unknown address and missing insert_row parameter"
        if audit!="all":
          return "Error|Restricted type: "+row["nervatype"]
        values = {"nervatype":neraid, "ref_id":lnkobj["id"]}
        ret = self.ns.db.address.validate_and_insert(**values)
        if ret.errors:
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          address = self.ns.db(self.ns.db.address.id==ret.id).select().as_list()[0]
      values={}    
      for key in row.keys():
        if key!="rownumber" and key!="refnumber" and key!="nervatype":
          if row[key]=="": row[key]=None
          if self.ns.db.address.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "address", address["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.address.id==address["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["refnumber"])+"["+str(row["rownumber"])+"]"
      logst = self.setLogtable(params, "update", "log_address_update", "address", lnkobj["id"])
      if logst!=True:
        return logst
    return retvalue
  
  def delete_address(self, params, data):
    retvalue = "OK"
    delete_ini = self.getSetting("set_trans_deleted")
    for row in data:
      if row.has_key("nervatype")!=True:
        return "Error|Missing required parameter: nervatype"
      if row.has_key("refnumber")!=True:
        return "Error|Missing required parameter: refnumber"
      if row.has_key("rownumber")!=True:
        return "Error|Missing required parameter: rownumber"
      
      audit = self.ns.getObjectAudit(row["nervatype"])
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: "+row["nervatype"]
      
      nervanumber = self.getNumberName(row["nervatype"])
      if nervanumber.startswith("Error"):
        return nervanumber
      neraid = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==row["nervatype"])).select().as_list()[0]["id"]
      lnkobj=None
      lnkobj = self.ns.db(self.ns.db[row["nervatype"]][nervanumber]==row["refnumber"]).select().as_list()
      if len(lnkobj)==0:
        return "Error|Unknown refnumber No: "+row["refnumber"]
      else:
        lnkobj = lnkobj[0]
        
      addr = None
      addr_ = self.ns.db((self.ns.db.address.deleted==0)&(self.ns.db.address.nervatype==neraid)&(self.ns.db.address.ref_id==lnkobj["id"])).select().as_list()
      if len(addr_)>0:
        if int(row["rownumber"])<0:
          addr = addr_[0]
        if int(row["rownumber"])<=len(addr_):
          addr = addr_[int(row["rownumber"])-1]
      if addr!=None:
        if delete_ini != "true":
          values = {"deleted":1}
          ret = self.ns.db(self.ns.db.address.id==addr["id"]).validate_and_update(**values)
          if ret.errors:
            self.ns.db.rollback()
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          dfield = self.deleteFieldValues(params, "address", addr["id"])
          if dfield!=True:
            return dfield
          try:
            self.ns.db(self.ns.db.address.id == addr["id"]).delete()
          except Exception, err:
            self.ns.db.rollback()
            return str(err)
        retvalue = retvalue+"|"+str(row["refnumber"])+"-"+str(row["rownumber"])
        logst = self.setLogtable(params, "update", "log_address_delete", "address", lnkobj["id"])
        if logst!=True:
          return logst
    return retvalue
  
  def update_barcode(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("product")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: product"
    for row in data:
      if row.has_key("barcode")!=True:
        return "Error|Missing required parameter: barcode"
      brc = None
      brc_ = self.ns.db(self.ns.db.barcode.code==row["barcode"]).select().as_list()
      values = {}
      if len(brc_)>0:    
        brc = brc_[0]
      
      if row.has_key("partnumber")==True:
        prod_ = self.ns.db((self.ns.db.product.deleted==0)&(self.ns.db.product.partnumber==row["partnumber"])).select().as_list()
        if len(prod_)==0:
          return "Error|Unknown partnumber No: "+str(row["partnumber"])
        values["product_id"] = prod_[0]["id"]
      if row.has_key("barcodetype")==True:
        bctype_ = self.ns.db((self.ns.db.groups.groupname=="barcodetype")&(self.ns.db.groups.groupvalue==row["barcodetype"])).select().as_list()
        if len(bctype_)==0:
          return "Error|Unknown barcodetype: "+str(row["barcodetype"])  
        values["barcodetype"] = bctype_[0]["id"]
        
      if brc==None:
        values["code"] = row["barcode"]
        if params.has_key("insert_row")!=True:
          return "Error|Unknown barcode and missing insert_row parameter"
        if row.has_key("partnumber")!=True:
          return "Error|Missing required parameter: partnumber"
        if row.has_key("barcodetype")!=True:
          return "Error|Missing required parameter: barcodetype"
        if audit!="all":
          return "Error|Restricted type: product"
        ret = self.ns.db.barcode.validate_and_insert(**values)
        if ret.errors:
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          brc = self.ns.db(self.ns.db.barcode.id==ret.id).select().as_list()[0]
          values = {}
          
      for key in row.keys():
        if key!="barcode" and key!="partnumber" and key!="barcodetype":
          if row[key]=="": row[key]=None
          if self.ns.db.barcode.has_key(key):
            values[key]= row[key]
          else:
            return "Error|Unknown fieldname: "+key
      if len(values)>0:    
        ret = self.ns.db(self.ns.db.barcode.id==brc["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["barcode"])
    return retvalue 
  
  def delete_barcode(self, params, data):
    audit = self.ns.getObjectAudit("product")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit!="all":
      return "Error|Restricted type: product"
    return self.deleteNervaObj1(params, data, "barcode", "barcode", "code")
  
  def update_contact(self, params, data):  
    retvalue = "OK"
    for row in data:
      if row.has_key("nervatype")!=True:
        return "Error|Missing required parameter: nervatype"
      if row.has_key("refnumber")!=True:
        return "Error|Missing required parameter: refnumber"
      if row.has_key("rownumber")!=True:
        row["rownumber"]=-1
      
      audit = self.ns.getObjectAudit(row["nervatype"])
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type: "+row["nervatype"]
      
      nervanumber = self.getNumberName(row["nervatype"])
      if nervanumber.startswith("Error"):
        return nervanumber
      neraid = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==row["nervatype"])).select().as_list()[0]["id"]
      lnkobj=None
      lnkobj = self.ns.db(self.ns.db[row["nervatype"]][nervanumber]==row["refnumber"]).select().as_list()
      if len(lnkobj)==0:
        return "Error|Unknown refnumber No: "+row["refnumber"]
      else:
        lnkobj = lnkobj[0]
        
      contact_ = None
      contlist = self.ns.db((self.ns.db.contact.deleted==0)&(self.ns.db.contact.nervatype==neraid)&(self.ns.db.contact.ref_id==lnkobj["id"])).select(orderby=self.ns.db.contact.id).as_list()
      if len(contlist)>0:
        if int(row["rownumber"])>0:
          if int(row["rownumber"])<=len(contlist):
            contact_ = contlist[int(row["rownumber"])-1]
          else:
            row["rownumber"]=len(contlist)+1
        else:
          row["rownumber"]=len(contlist)+1
      else:
          row["rownumber"]=len(contlist)+1
      if contact_==None:
        if params.has_key("insert_row")!=True:
          return "Error|Unknown contact and missing insert_row parameter"
        if audit!="all":
          return "Error|Restricted type: "+row["nervatype"]
        values = {"nervatype":neraid, "ref_id":lnkobj["id"]}
        ret = self.ns.db.contact.validate_and_insert(**values)
        if ret.errors:
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          contact_ = self.ns.db(self.ns.db.contact.id==ret.id).select().as_list()[0]
      values={} 
      for key in row.keys():
        if key!="rownumber" and key!="refnumber" and key!="nervatype":
          if row[key]=="": row[key]=None
          if self.ns.db.contact.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "contact", contact_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.contact.id==contact_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["refnumber"])+"["+str(row["rownumber"])+"]"
      logst = self.setLogtable(params, "update", "log_contact_update", "contact", lnkobj["id"])
      if logst!=True:
          return logst
    return retvalue
    
  def delete_contact(self, params, data):
    retvalue = "OK"
    delete_ini = self.getSetting("set_trans_deleted")
    for row in data:
      if row.has_key("nervatype")!=True:
        return "Error|Missing required parameter: nervatype"
      if row.has_key("refnumber")!=True:
        return "Error|Missing required parameter: refnumber"
      if row.has_key("rownumber")!=True:
        return "Error|Missing required parameter: rownumber"
      
      audit = self.ns.getObjectAudit(row["nervatype"])
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type: "+row["nervatype"]
      
      nervanumber = self.getNumberName(row["nervatype"])
      if nervanumber.startswith("Error"):
        return nervanumber
      neraid = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==row["nervatype"])).select().as_list()[0]["id"]
      lnkobj=None
      lnkobj = self.ns.db(self.ns.db[row["nervatype"]][nervanumber]==row["refnumber"]).select().as_list()
      if len(lnkobj)==0:
        return "Error|Unknown refnumber No: "+row["refnumber"]
      else:
        lnkobj = lnkobj[0]
        
      cont = None
      cont_ = self.ns.db((self.ns.db.contact.deleted==0)&(self.ns.db.contact.nervatype==neraid)&(self.ns.db.contact.ref_id==lnkobj["id"])).select().as_list()
      if len(cont_)>0:
        if int(row["rownumber"])<0:
          cont = cont_[0]
        if int(row["rownumber"])<=len(cont_):
          cont = cont_[int(row["rownumber"])-1]
      if cont!=None:
        if delete_ini != "true":
          values = {"deleted":1}
          ret = self.ns.db(self.ns.db.contact.id==cont["id"]).validate_and_update(**values)
          if ret.errors:
            self.ns.db.rollback()
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          dfield = self.deleteFieldValues(params, "contact", cont["id"])
          if dfield!=True:
            return dfield
          try:
            self.ns.db(self.ns.db.contact.id == cont["id"]).delete()
          except Exception, err:
            self.ns.db.rollback()
            return str(err)
        retvalue = retvalue+"|"+str(row["refnumber"])+"-"+str(row["rownumber"])
        logst = self.setLogtable(params, "update", "log_contact_delete", "contact", lnkobj["id"])
        if logst!=True:
          return logst
    return retvalue
  
  def update_currency(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: setting"
    for row in data:
      values = {}
      if row.has_key("curr")!=True:
        return "Error|Missing required parameter: curr"
      curr = None
      curr_ = self.ns.db(self.ns.db.currency.curr==row["curr"]).select().as_list()
      if len(curr_)>0:    
        curr = curr_[0]
      if curr==None:
        if params.has_key("insert_row")!=True:
          return "Error|Unknown currency and missing insert_row parameter"
        if audit!="all":
          return "Error|Restricted type: setting"
        values["curr"] = row["curr"]
        if row.has_key("description")!=True:
          return "Error|Missing required parameter: description"
        values["description"] = row["description"]
        ret = self.ns.db.currency.validate_and_insert(**values)
        if ret.errors:
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          curr = self.ns.db(self.ns.db.currency.id==ret.id).select().as_list()[0]
          values = {}
      for key in row.keys():
        if key!="curr":
          if row[key]=="": row[key]=None
          if self.ns.db.currency.has_key(key):
            values[key]= row[key]
          else:
            return "Error|Unknown fieldname: "+key
      if len(values)>0:    
        ret = self.ns.db(self.ns.db.currency.id==curr["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["curr"])
    return retvalue
    
  def delete_currency(self, params, data):
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit!="all":
      return "Error|Restricted type: setting"
    return self.deleteNervaObj1(params, data, "currency", "curr")
  
  def update_customer(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("customer")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: customer"      
    for row in data:
      values = {}
      customer_ = None
      if row.has_key("custnumber")==True:
        custlist = self.ns.db((self.ns.db.customer.deleted==0)&(self.ns.db.customer.custnumber==row["custnumber"])).select().as_list()
        if len(custlist)>0:
          customer_ = custlist[0]
      if row.has_key("custtype"):
        if row["custtype"]=="company":
          row["custtype"] = self.ns.db((self.ns.db.groups.groupname=="custtype")&(self.ns.db.groups.groupvalue=="company")).select().as_list()[0]["id"]
        elif row["custtype"]=="private":
          row["custtype"] = self.ns.db((self.ns.db.groups.groupname=="custtype")&(self.ns.db.groups.groupvalue=="private")).select().as_list()[0]["id"]
        elif row["custtype"]=="other" :
          row["custtype"] = self.ns.db((self.ns.db.groups.groupname=="custtype")&(self.ns.db.groups.groupvalue=="other")).select().as_list()[0]["id"]
        elif row["custtype"]=="own" :
          if customer_:
            if customer_["id"]==1:
              del row["custtype"]
            else:
              return "Error|Valid customertype: company, private, other "
          else:
            return "Error|Valid customertype: company, private, other "
        else:
          return "Error|Valid customertype: company, private, other "
      if customer_==None:  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: customer"
          if row.has_key("custname")!=True:
            return "Error|Missing required parameter: custname"
          if row.has_key("custnumber")!=True:
            custnumber = self.dbfu.nextNumber(self.ns, {"id":"custnumber", "step":True})
          else:
            custnumber = row["custnumber"]
          custlist = self.ns.db(self.ns.db.customer.custnumber==custnumber).select().as_list()
          if len(custlist)>0:
            return "Error|New customer, but the retrieved customer No. is reserved: "+str(custnumber)
          values["custnumber"] = custnumber
          values["custname"] = row["custname"]
          if row.has_key("custtype"):
            values["custtype"] = row["custtype"]
          else:
            values["custtype"] = self.ns.db((self.ns.db.groups.groupname=="custtype")&(self.ns.db.groups.groupvalue=="company")).select().as_list()[0]["id"]
          ret = self.ns.db.customer.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            customer_ = self.ns.db(self.ns.db.customer.id==ret.id).select().as_list()[0]
            values = {}     
        else:
          return "Error|Missing custnumber and insert_row parameter"  
      
      for key in row.keys():
        if key!="custnumber":
          if row[key]=="": row[key]=None
          if self.ns.db.customer.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "customer", customer_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.customer.id==customer_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+customer_["custnumber"]
      logst = self.setLogtable(params, "update", "log_customer_update", "customer", customer_["id"])
      if logst!=True:
          return logst
    return retvalue
  
  def delete_customer(self, params, data):
    return self.deleteNervaObj2(params, data, "customer", "custnumber")
  
  def update_deffield(self, params, data):  
    retvalue = "OK"
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: setting"
    for row in data:
      values = {}
      if row.has_key("fieldname")!=True:
        return "Error|Missing required parameter: fieldname"
      if row.has_key("valuelist"):
        row["valuelist"] = str(row["valuelist"]).replace("~", "|")
      deffld = None
      deffld_ = self.ns.db(self.ns.db.deffield.fieldname==row["fieldname"]).select().as_list()
      if len(deffld_)>0:    
        deffld = deffld_[0]
      if deffld==None:
        if params.has_key("insert_row")!=True:
          return "Error|Unknown deffield and missing insert_row parameter"
        if audit!="all":
          return "Error|Restricted type: setting"
        if row.has_key("nervatype")!=True:
          return "Error|Missing required parameter: nervatype"
        else:
          nervatype = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==row["nervatype"])).select().as_list()
          if len(nervatype)==0:
            return "Error|Unknown nervatype: "+str(row["nervatype"])
          values["nervatype"] = nervatype[0]["id"]
        if row.has_key("fieldtype")!=True:
          return "Error|Missing required parameter: fieldtype"
        else:
          fieldtype = self.ns.db((self.ns.db.groups.groupname=="fieldtype")&(self.ns.db.groups.groupvalue==row["fieldtype"])).select().as_list()
          if len(fieldtype)==0:
            return "Error|Unknown fieldtype: "+str(row["fieldtype"])
          values["fieldtype"] = fieldtype[0]["id"]
        values["fieldname"] = row["fieldname"]
        if row.has_key("description"):
          values["description"] = row["description"]
        else:
          values["description"] = row["fieldname"]
        ret = self.ns.db.deffield.validate_and_insert(**values)
        if ret.errors:
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          deffld = self.ns.db(self.ns.db.deffield.id==ret.id).select().as_list()[0]
          values = {}
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
          if row[key]=="": row[key]=None
          if self.ns.db.deffield.has_key(key):
            values[key]= row[key]
          else:
            return "Error|Unknown fieldname: "+key
      if len(values)>0:    
        ret = self.ns.db(self.ns.db.deffield.id==deffld["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["fieldname"])
    return retvalue
  
  def delete_deffield(self, params, data):
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit!="all":
      return "Error|Restricted type: setting"
    return self.deleteNervaObj2(params, data, "deffield", "fieldname")
  
  def update_employee(self, params, data):  
    retvalue = "OK"
    audit = self.ns.getObjectAudit("employee")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: employee"
    for row in data:
      values = {}
      employee_ = None
      if row.has_key("empnumber"):
        emplist = self.ns.db((self.ns.db.employee.deleted==0)&(self.ns.db.employee.empnumber==row["empnumber"])).select().as_list()
        if len(emplist)>0:
          employee_ = emplist[0]
      if row.has_key("usergroup"):
        usergroup = self.ns.db((self.ns.db.groups.groupname=="usergroup")&(self.ns.db.groups.groupvalue==row["usergroup"])).select().as_list()
        if len(usergroup)>0:
          row["usergroup"] = usergroup[0]["id"]
        else:
          return "Error|Unknown usergroup: "+row["usergroup"]
      if row.has_key("department"):
        if row["department"]!="":
          department = self.ns.db((self.ns.db.groups.groupname=="department")&(self.ns.db.groups.groupvalue==row["department"])).select().as_list()
          if len(department)>0:
            row["department"] = department[0]["id"]
          else:
            return "Error|Unknown department: "+row["department"]
      if row.has_key("username") and employee_:
        if employee_["username"]==row["username"]:
          del row["username"]
      if employee_==None:  
        if params.has_key("insert_row"):
          if audit!="all":
            return "Error|Restricted type: employee"
          if row.has_key("usergroup")!=True:
            return "Error|Missing required parameter: usergroup"
          if row.has_key("empnumber")!=True:
            empnumber = self.dbfu.nextNumber(self.ns, {"id":"empnumber", "step":True})
          else:
            empnumber = row["empnumber"]
          emplist = self.ns.db(self.ns.db.employee.empnumber==empnumber).select().as_list()
          if len(emplist)>0:
            return "Error|New employee, but the retrieved employee No. is reserved: "+str(empnumber)
          values["empnumber"] = empnumber
          values["usergroup"] = row["usergroup"]
          ret = self.ns.db.employee.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            employee_ = self.ns.db(self.ns.db.employee.id==ret.id).select().as_list()[0]
            values = {}
        else:
          return "Error|Missing empnumber and insert_row parameter"          
        
      for key in row.keys():
        if key!="empnumber":
          if row[key]=="": row[key]=None
          if self.ns.db.employee.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "employee", employee_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.employee.id==employee_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+employee_["empnumber"]
      logst = self.setLogtable(params, "update", "log_employee_update", "employee", employee_["id"])
      if logst!=True:
          return logst
    return retvalue
  
  def delete_employee(self, params, data):
    return self.deleteNervaObj2(params, data, "employee", "empnumber")
  
  def update_event(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("event")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: event"
    for row in data:
      values = {}
      event_ = None       
      if row.has_key("calnumber")==True:
        emplist = self.ns.db((self.ns.db.event.deleted==0)&(self.ns.db.event.calnumber==row["calnumber"])).select().as_list()
        if len(emplist)>0:
          event_ = emplist[0]
      if event_==None:  
        if params.has_key("insert_row")==True:
          if row.has_key("nervatype")!=True:
            return "Error|Missing required parameter: nervatype"
          if row.has_key("refnumber")!=True:
            return "Error|Missing required parameter: refnumber"
          if audit!="all":
            return "Error|Restricted type: event"
          
          nervanumber = self.getNumberName(row["nervatype"])
          if nervanumber.startswith("Error"):
            return nervanumber
          neraid = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==row["nervatype"])).select().as_list()[0]["id"]
          lnkobj=None
          lnkobj = self.ns.db(self.ns.db[row["nervatype"]][nervanumber]==row["refnumber"]).select().as_list()
          if len(lnkobj)==0:
            return "Error|Unknown refnumber No: "+row["refnumber"]
          else:
            lnkobj = lnkobj[0]
        
          if row.has_key("calnumber")!=True:
            calnumber = self.dbfu.nextNumber(self.ns, {"id":"calnumber", "step":True})
          else:
            calnumber = row["calnumber"]
          emplist = self.ns.db(self.ns.db.event.calnumber==calnumber).select().as_list()
          if len(emplist)>0:
            return "Error|New event, but the retrieved event No. is reserved: "+str(calnumber)
              
          values = {"calnumber":calnumber, "nervatype":neraid, "ref_id":lnkobj["id"]}
          ret = self.ns.db.event.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            event_ = self.ns.db(self.ns.db.event.id==ret.id).select().as_list()[0]
            values={} 
        else:
          return "Error|Missing calnumber and insert_row parameter"  
      if row.has_key("eventgroup"):
        if row["eventgroup"]!="":
          eventgroup = self.ns.db((self.ns.db.groups.groupname=="eventgroup")&(self.ns.db.groups.groupvalue==row["eventgroup"])).select().as_list()
          if len(eventgroup)>0:
            row["eventgroup"] = eventgroup[0]["id"]
          else:
            ret = self.ns.db.groups.validate_and_insert(**{"groupname":"eventgroup", "groupvalue":row["eventgroup"]})
            if ret.errors:
              return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
            else:
              row["eventgroup"] = ret.id
      for key in row.keys():
        if key!="calnumber" and key!="nervatype" and key!="refnumber":
          if row[key]=="": row[key]=None
          if self.ns.db.event.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "event", event_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.event.id==event_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+event_["calnumber"]
      logst = self.setLogtable(params, "update", "log_event_update", "event", event_["id"])
      if logst!=True:
          return logst
    return retvalue
    
  def delete_event(self, params, data):
    return self.deleteNervaObj2(params, data, "event", "calnumber")
  
  def update_groups(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: setting"
    for row in data:
      values = {}
      if row.has_key("groupname")!=True:
        return "Error|Missing required parameter: groupname"
      if row.has_key("groupvalue")!=True:
        return "Error|Missing required parameter: groupvalue"
      group = None
      grouplist = self.ns.db((self.ns.db.groups.groupname==row["groupname"])&(self.ns.db.groups.groupvalue==row["groupvalue"])).select().as_list()
      if len(grouplist)>0:    
        group = grouplist[0]
      if group==None:
        if audit!="all":
          return "Error|Restricted type: setting"
        values = {"groupname":row["groupname"], "groupvalue":row["groupvalue"]}
        ret = self.ns.db.groups.validate_and_insert(**values)
        if ret.errors:
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          group = self.ns.db(self.ns.db.groups.id==ret.id).select().as_list()[0]
          values={} 
      for key in row.keys():
        if key!="groupname" and key!="groupvalue":
          if row[key]=="": row[key]=None
          if self.ns.db.groups.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "groups", group["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.groups.id==group["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["groupname"])+"["+str(row["groupvalue"])+"]"
      logst = self.setLogtable(params, "update", "log_groups_update", "groups", group["id"])
      if logst!=True:
          return logst
    return retvalue
    
  def delete_groups(self, params, data):
    for row in data:
      if row.has_key("groupname")!=True:
        return "Error|Missing required parameter: groupname"
      if row.has_key("groupvalue")!=True:
        return "Error|Missing required parameter: groupvalue"
      if row["groupname"]=="usergroup":
        return "Error|Invalid groupname: usergroup"
      nervatype = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue=="groups")).select().as_list()
      ref_id = self.ns.db((self.ns.db.groups.groupname==row["groupname"])&(self.ns.db.groups.groupvalue==row["groupvalue"])).select().as_list()
      if len(nervatype)>0 and len(ref_id)>0:
        linklist = self.ns.db((self.ns.db.link.deleted==0)&(self.ns.db.link.nervatype_1==nervatype[0]["id"])&(self.ns.db.link.ref_id_1==ref_id[0]["id"])).select().as_list()
        if len(linklist)>0:
          return "Error|The group can not be deleted because it is in use: "+str(row["groupname"])+"-"+str(row["groupvalue"])
        linklist = self.ns.db((self.ns.db.link.deleted==0)&(self.ns.db.link.nervatype_2==nervatype[0]["id"])&(self.ns.db.link.ref_id_2==ref_id[0]["id"])).select().as_list()
        if len(linklist)>0:
          return "Error|The group can not be deleted because it is in use: "+str(row["groupname"])+"-"+str(row["groupvalue"])      
    return self.deleteNervaObj2(params, data, "groups", "groupname", "groupname", "groupvalue", "groupvalue")
    
  def update_item(self, params, data):    
    retvalue = "OK"
    for row in data:
      values = {}
      item_ = None
      trans_id = None
      curr = None
      if row.has_key("rownumber")!=True:
        return "Error|Missing required parameter: rownumber"
      if row.has_key("transnumber")==True:
        translist = self.ns.db((self.ns.db.trans.deleted==0)&(self.ns.db.trans.transnumber==row["transnumber"])).select().as_list()
        if len(translist)>0:
          trans_id = translist[0]["id"]
          curr = translist[0]["curr"]
          itemlist = self.ns.db((self.ns.db.item.deleted==0)&(self.ns.db.item.trans_id==trans_id)).select(orderby=self.ns.db.item.id).as_list()
          if len(itemlist)>0 and int(row["rownumber"])>0:
            if int(row["rownumber"])<=len(itemlist):
              item_ = itemlist[int(row["rownumber"])-1]
            else:
              row["rownumber"]=len(itemlist)+1
          else:
            row["rownumber"]=len(itemlist)+1
        else:
          return "Error|Unknown transnumber: "+str(row["transnumber"])
      else:
        return "Error|Missing required parameter: transnumber"
      
      transtype = self.ns.db((self.ns.db.groups.id==translist[0]["transtype"])).select().as_list()[0]["groupvalue"]
      audit = self.ns.getObjectAudit("trans",transtype)
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly transtype: "+transtype
    
      if row.has_key("partnumber")==True:
        prod_ = self.ns.db((self.ns.db.product.deleted==0)&(self.ns.db.product.partnumber==row["partnumber"])).select().as_list()
        if len(prod_)==0:
          return "Error|Unknown partnumber No: "+str(row["partnumber"])
        values["product_id"] = prod_[0]["id"]
        if item_==None:
          values["unit"] = prod_[0]["unit"]
          values["tax_id"] = prod_[0]["tax_id"]
          values["description"] = prod_[0]["description"]
        del row["partnumber"]
        
      if item_==None:  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: "+transtype
          if values.has_key("product_id")!=True:
            return "Error|Missing required parameter: partnumber"
          values["trans_id"] = trans_id
          ret = self.ns.db.item.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            item_ = self.ns.db(self.ns.db.item.id==ret.id).select().as_list()[0]
            values={}
        else:
          return "Error|Missing item and no insert_row parameter"  
      
      if row.has_key("taxcode"):
        tax = self.ns.db((self.ns.db.tax.taxcode==row["taxcode"])).select().as_list()
        if len(tax)>0:
          values["tax_id"] = tax[0]["id"]
          del row["taxcode"] 
        else:
          return "Error|Unknown taxcode: "+row["taxcode"]
      if row.has_key("discount")==True:
        if str(row["discount"]).replace(".", "").isdigit()==False:
          return "Error|Invalid discount type!"
        if float(row["discount"])<0 or float(row["discount"])>100:
          return "Error|Valid discount value: 0-100"     
      if row.has_key("inputmode")==True:
        if row.has_key("inputvalue")!=True:
          return "Error|Set inputmode, but missing required parameter: inputvalue"
        if row.has_key("qty")!=True:
          values["qty"] = item_["qty"]
        else:
          values["qty"] = float(row["qty"])
        if row.has_key("discount")!=True:
          values["discount"] = item_["discount"]
        else:
          values["discount"] = float(row["discount"])
        
        tax_ = self.ns.db((self.ns.db.tax.id==item_["tax_id"])).select().as_list()[0]  
        currency_ = self.ns.db((self.ns.db.currency.curr==curr)).select().as_list()[0]
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
          if row[key]=="": row[key]=None
          if self.ns.db.item.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "item", item_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.item.id==item_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["transnumber"])+"["+str(row["rownumber"])+"]"
      logst = self.setLogtable(params, "update", "log_trans_update", "trans", trans_id)
      if logst!=True:
          return logst
    return retvalue
    
  def delete_item(self, params, data):
    return self.deleteTransItem(params, data, "item")
    
  def update_link(self, params, data):
    retvalue = "OK"
    for row in data:
      values = {}
      if row.has_key("nervatype1")!=True:
        return "Error|Missing required parameter: nervatype1"
      if row.has_key("refnumber1")!=True:
        return "Error|Missing required parameter: refnumber1"
      if row.has_key("nervatype2")!=True:
        return "Error|Missing required parameter: nervatype2"
      if row.has_key("refnumber2")!=True:
        return "Error|Missing required parameter: refnumber2"
    
      if row["nervatype1"] in("groups","item","movement","payment"):
        if len(str(row["refnumber1"]).split("~"))<2:
          if row["nervatype1"]=="groups":
            return "Error|valid groups refnumber format: groupname~groupvalue"
          else:
            return "Error|valid refnumber format: transnumber~rownumber"
      if row["nervatype2"] in("groups","item","movement","payment"):
        if len(str(row["refnumber2"]).split("~"))<2:
          if row["nervatype1"]=="groups":
            return "Error|valid groups refnumber format: groupname~groupvalue"
          else:
            return "Error|valid refnumber format: transnumber~rownumber"
        
      nervaid1 = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==row["nervatype1"])).select().as_list()
      if len(nervaid1)==0:
        return "Error|Unknown nervatype: "+row["nervatype1"]
      else:
        nervaid1 = nervaid1[0]["id"]
      lnkobj1=None
      if row["nervatype1"] in("groups","item","movement","payment"):
        ref = str(row["refnumber1"]).split("~")
        if row["nervatype1"]=="groups":
          lnkobj1 = self.ns.db((self.ns.db.groups.groupname==ref[0])&(self.ns.db.groups.groupvalue==ref[1])).select().as_list()
        else:
          if len(self.ns.db((self.ns.db.trans.transnumber==ref[0])&(self.ns.db.trans.deleted==0)).select())==0:
            return "Error|Unknown refnumber No: "+row["refnumber1"]
          else:
            ref[0] = self.ns.db((self.ns.db.trans.transnumber==ref[0])&(self.ns.db.trans.deleted==0)).select()[0]["id"]
          if ref[1]=="" or not str(ref[1]).isdigit():
            return "Error|Unknown refnumber No: "+row["refnumber1"]
          else:
            ref[1]=int(ref[1])
          rowlist = self.ns.db((self.ns.db[row["nervatype1"]].deleted==0)&(self.ns.db[row["nervatype1"]].trans_id==ref[0])).select(orderby=self.ns.db[row["nervatype1"]].id).as_list()
          if len(rowlist)>0 and ref[1]>0 and ref[1]<=len(rowlist):
            lnkobj1 = [rowlist[ref[1]-1]]
          else:
            return "Error|Unknown refnumber No: "+row["refnumber1"]
      else:
        nervanumber = self.getNumberName(row["nervatype1"])
        if nervanumber.startswith("Error"):
          return nervanumber
        lnkobj1 = self.ns.db(self.ns.db[row["nervatype1"]][nervanumber]==row["refnumber1"]).select().as_list()
      if len(lnkobj1)==0:
        return "Error|Unknown refnumber No: "+row["refnumber1"]
      else:
        lnkobj1 = lnkobj1[0]
      
      if row["nervatype1"] in("trans","item","movement","payment"):
        if row["nervatype1"]=="trans":
          transtype = self.ns.db.groups(id=lnkobj1["transtype"]).groupvalue
        else:
          transtype = self.ns.db.groups(id=self.ns.db.trans(id=ref[0]).transtype).groupvalue
        audit = self.ns.getObjectAudit("trans",transtype)
      else:
        audit = self.ns.getObjectAudit(row["nervatype1"])
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly type"
      
      nervaid2 = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==row["nervatype2"])).select().as_list()
      if len(nervaid2)==0:
        return "Error|Unknown nervatype: "+row["nervatype2"]
      else:
        nervaid2 = nervaid2[0]["id"]
      lnkobj2=None
      if row["nervatype2"] in("groups","item","movement","payment"):
        ref = str(row["refnumber2"]).split("~")
        if row["nervatype2"]=="groups":
          lnkobj2 = self.ns.db((self.ns.db.groups.groupname==ref[0])&(self.ns.db.groups.groupvalue==ref[1])).select().as_list()
        else:
          if len(self.ns.db((self.ns.db.trans.transnumber==ref[0])&(self.ns.db.trans.deleted==0)).select())==0:
            return "Error|Unknown refnumber No: "+row["refnumber2"]
          else:
            ref[0] = self.ns.db((self.ns.db.trans.transnumber==ref[0])&(self.ns.db.trans.deleted==0)).select()[0]["id"]
          if ref[1]=="" or not str(ref[1]).isdigit():
            return "Error|Unknown refnumber No: "+row["refnumber2"]
          else:
            ref[1]=int(ref[1])
          rowlist = self.ns.db((self.ns.db[row["nervatype2"]].deleted==0)&(self.ns.db[row["nervatype2"]].trans_id==ref[0])).select(orderby=self.ns.db[row["nervatype2"]].id).as_list()
          if len(rowlist)>0 and ref[1]>0 and ref[1]<=len(rowlist):
            lnkobj2 = [rowlist[ref[1]-1]]
          else:
            return "Error|Unknown refnumber No: "+row["refnumber2"]
      else:
        nervanumber = self.getNumberName(row["nervatype2"])
        if nervanumber.startswith("Error"):
          return nervanumber
        lnkobj2 = self.ns.db(self.ns.db[row["nervatype2"]][nervanumber]==row["refnumber2"]).select().as_list()
      if len(lnkobj2)==0:
        return "Error|Unknown refnumber No: "+row["refnumber2"]
      else:
        lnkobj2 = lnkobj2[0]
        
      link_ = None
      linklist = self.ns.db((self.ns.db.link.deleted==0)&(self.ns.db.link.nervatype_1==nervaid1)&(self.ns.db.link.ref_id_1==lnkobj1["id"])
                       &(self.ns.db.link.nervatype_2==nervaid2)&(self.ns.db.link.ref_id_2==lnkobj2["id"])).select().as_list()
      if len(linklist)>0:    
        link_ = linklist[0]
      if link_==None:
        if audit!="all":
          return "Error|Restricted type "
        values["nervatype_1"] = nervaid1
        values["ref_id_1"] = lnkobj1["id"]
        values["nervatype_2"] = nervaid2
        values["ref_id_2"] = lnkobj2["id"]
        ret = self.ns.db.link.validate_and_insert(**values)
        if ret.errors:
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          link_ = self.ns.db(self.ns.db.link.id==ret.id).select().as_list()[0]
          values={}
      for key in row.keys():
        if key!="nervatype1" and key!="refnumber1" and key!="nervatype2" and key!="refnumber2":
          if row[key]=="": row[key]=None
          if self.ns.db.link.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "link", link_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.link.id==link_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["nervatype1"])+"["+str(row["refnumber1"])+"]+"+str(row["nervatype2"])+"["+str(row["refnumber2"])+"]"
    return retvalue 
    
  def delete_link(self, params, data):
    retvalue = "OK"
    delete_ini = self.getSetting("set_trans_deleted")
    for row in data:
      values = {}
      if row.has_key("nervatype1")!=True:
        return "Error|Missing required parameter: nervatype1"
      if row.has_key("refnumber1")!=True:
        return "Error|Missing required parameter: refnumber1"
      if row.has_key("nervatype2")!=True:
        return "Error|Missing required parameter: nervatype2"
      if row.has_key("refnumber2")!=True:
        return "Error|Missing required parameter: refnumber2"
      
      if row["nervatype1"]=="groups":
        if len(str(row["refnumber1"]).split("~"))<2:
          return "Error|valid groups refnumber format: groupname~groupvalue"
      if row["nervatype2"]=="groups":
        if len(str(row["refnumber2"]).split("~"))<2:
          return "Error|valid groups refnumber format: groupname~groupvalue"
        
      nervaid1 = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==row["nervatype1"])).select().as_list()
      if len(nervaid1)==0:
        return "Error|Unknown nervatype: "+row["nervatype1"]
      else:
        nervaid1 = nervaid1[0]["id"]
      lnkobj1=None
      if row["nervatype1"] in("groups","item","movement","payment"):
        ref = str(row["refnumber1"]).split("~")
        if row["nervatype1"]=="groups":
          lnkobj1 = self.ns.db((self.ns.db.groups.groupname==ref[0])&(self.ns.db.groups.groupvalue==ref[1])).select().as_list()
        else:
          if len(self.ns.db((self.ns.db.trans.transnumber==ref[0])&(self.ns.db.trans.deleted==0)).select())==0:
            return "Error|Unknown refnumber No: "+row["refnumber1"]
          else:
            ref[0] = self.ns.db((self.ns.db.trans.transnumber==ref[0])&(self.ns.db.trans.deleted==0)).select()[0]["id"]
          if ref[1]=="" or not str(ref[1]).isdigit():
            return "Error|Unknown refnumber No: "+row["refnumber1"]
          else:
            ref[1]=int(ref[1])
          rowlist = self.ns.db((self.ns.db[row["nervatype1"]].deleted==0)&(self.ns.db[row["nervatype1"]].trans_id==ref[0])).select(orderby=self.ns.db[row["nervatype1"]].id).as_list()
          if len(rowlist)>0 and ref[1]>0 and ref[1]<=len(rowlist):
            lnkobj1 = [rowlist[ref[1]-1]]
          else:
            return "Error|Unknown refnumber No: "+row["refnumber1"]
      else:
        nervanumber = self.getNumberName(row["nervatype1"])
        if nervanumber.startswith("Error"):
          return nervanumber
        lnkobj1 = self.ns.db(self.ns.db[row["nervatype1"]][nervanumber]==row["refnumber1"]).select().as_list()
        
      if len(lnkobj1)==0:
        return "Error|Unknown refnumber No: "+row["refnumber1"]
      else:
        lnkobj1 = lnkobj1[0]
      
      if row["nervatype1"] in("trans","item","movement","payment"):
        if row["nervatype1"]=="trans":
          transtype = self.ns.db.groups(id=lnkobj1["transtype"]).groupvalue
        else:
          transtype = self.ns.db.groups(id=self.ns.db.trans(id=ref[0]).transtype).groupvalue
        audit = self.ns.getObjectAudit("trans",transtype)
      else:
        audit = self.ns.getObjectAudit(row["nervatype1"])
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit!="all":
        return "Error|Restricted type!"
      
      nervaid2 = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue==row["nervatype2"])).select().as_list()
      if len(nervaid2)==0:
        return "Error|Unknown nervatype: "+row["nervatype2"]
      else:
        nervaid2 = nervaid2[0]["id"]
      lnkobj2=None
      if row["nervatype2"] in("groups","item","movement","payment"):
        ref = str(row["refnumber2"]).split("~")
        if row["nervatype2"]=="groups":
          lnkobj2 = self.ns.db((self.ns.db.groups.groupname==ref[0])&(self.ns.db.groups.groupvalue==ref[1])).select().as_list()
        else:
          if len(self.ns.db((self.ns.db.trans.transnumber==ref[0])&(self.ns.db.trans.deleted==0)).select())==0:
            return "Error|Unknown refnumber No: "+row["refnumber2"]
          else:
            ref[0] = self.ns.db((self.ns.db.trans.transnumber==ref[0])&(self.ns.db.trans.deleted==0)).select()[0]["id"]
          if ref[1]=="" or not str(ref[1]).isdigit():
            return "Error|Unknown refnumber No: "+row["refnumber2"]
          else:
            ref[1]=int(ref[1])
          rowlist = self.ns.db((self.ns.db[row["nervatype2"]].deleted==0)&(self.ns.db[row["nervatype2"]].trans_id==ref[0])).select(orderby=self.ns.db[row["nervatype2"]].id).as_list()
          if len(rowlist)>0 and ref[1]>0 and ref[1]<=len(rowlist):
            lnkobj2 = [rowlist[ref[1]-1]]
          else:
            return "Error|Unknown refnumber No: "+row["refnumber2"]
      else:
        nervanumber = self.getNumberName(row["nervatype2"])
        if nervanumber.startswith("Error"):
          return nervanumber
        lnkobj2 = self.ns.db(self.ns.db[row["nervatype2"]][nervanumber]==row["refnumber2"]).select().as_list()
      if len(lnkobj2)==0:
        return "Error|Unknown refnumber No: "+row["refnumber2"]
      else:
        lnkobj2 = lnkobj2[0]
        
      linklist = self.ns.db((self.ns.db.link.deleted==0)&(self.ns.db.link.nervatype_1==nervaid1)&(self.ns.db.link.ref_id_1==lnkobj1["id"])
                       &(self.ns.db.link.nervatype_2==nervaid2)&(self.ns.db.link.ref_id_2==lnkobj2["id"])).select().as_list()
      if len(linklist)>0:
        if delete_ini != "true":
          values = {"deleted":1}
          ret = self.ns.db(self.ns.db.link.id==linklist[0]["id"]).validate_and_update(**values)
          if ret.errors:
            self.ns.db.rollback()
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          dfield = self.deleteFieldValues(params, "link", linklist[0]["id"])
          if dfield!=True:
            return dfield
          try:
            self.ns.db(self.ns.db.link.id == linklist[0]["id"]).delete()
          except Exception, err:
            self.ns.db.rollback()
            return str(err)
        retvalue = retvalue+"|"+str(row["nervatype1"])+"["+str(row["refnumber1"])+"]+"+str(row["nervatype2"])+"["+str(row["refnumber2"])+"]"
    return retvalue
  
  def update_movement(self, params, data):
    from datetime import date, datetime
    
    retvalue = "OK"
    for row in data:
      values = {}
      movement_ = None
      trans_id = None
      if row.has_key("rownumber")!=True:
        return "Error|Missing required parameter: rownumber"
      if row.has_key("transnumber")==True:
        translist = self.ns.db((self.ns.db.trans.deleted==0)&(self.ns.db.trans.transnumber==row["transnumber"])).select().as_list()
        if len(translist)>0:
          trans_id = translist[0]["id"]
          itemlist = self.ns.db((self.ns.db.movement.deleted==0)&(self.ns.db.movement.trans_id==trans_id)).select(orderby=self.ns.db.movement.id).as_list()
          if len(itemlist)>0 and int(row["rownumber"])>0:
            if int(row["rownumber"])<=len(itemlist):
              movement_ = itemlist[int(row["rownumber"])-1]
            else:
              row["rownumber"]=len(itemlist)+1
          else:
            row["rownumber"]=len(itemlist)+1
        else:
          return "Error|Unknown transnumber: "+str(row["transnumber"])
      else:
        return "Error|Missing required parameter: transnumber"
      
      transtype = self.ns.db((self.ns.db.groups.id==translist[0]["transtype"])).select().as_list()[0]["groupvalue"]
      audit = self.ns.getObjectAudit("trans",transtype)
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly transtype: "+transtype
      
      if movement_==None:  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: "+transtype
          if row.has_key("movetype")!=True:
            return "Error|Missing required parameter: movetype"
          else:
            movetype = self.ns.db((self.ns.db.groups.groupname=="movetype")&(self.ns.db.groups.groupvalue==row["movetype"])).select().as_list()
            if len(movetype)==0:
              return "Error|Unknown movetype: "+str(row["movetype"])+". Valid values: inventory, store, tool, head, plan."
            else:
              movetype = movetype[0]
            del row["movetype"]
          if (movetype["groupvalue"] in("store","inventory","formula","production")) and row.has_key("partnumber")!=True:
            return "Error|Missing required parameter: partnumber"
          if movetype["groupvalue"]=="tool" and row.has_key("serial")!=True:
            return "Error|Missing required parameter: serial"
          if (movetype["groupvalue"] in("store","inventory","production")) and row.has_key("planumber")!=True:
            return "Error|Missing required parameter: planumber"
          
          values["trans_id"] = trans_id
          values["movetype"] = movetype["id"]
          fmt = "%Y.%m.%d 00:00:00"
          values["shippingdate"] = datetime.strptime(date.strftime(datetime.now(),fmt),fmt)
          ret = self.ns.db.movement.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            movement_ = self.ns.db(self.ns.db.movement.id==ret.id).select().as_list()[0]
            values={}
        else:
          return "Error|Missing item and no insert_row parameter"
      if row.has_key("movetype"):
        movetype = self.ns.db((self.ns.db.groups.groupname=="movetype")&(self.ns.db.groups.groupvalue==row["movetype"])).select()
        if len(movetype)>0:
          movetype = movetype[0]["id"]
          if movement_["movetype"]!=movetype:
            return "Error|Readonly parameter: movetype"
          else:
            del row["movetype"]
        else:
          return "Error|Unknown movetype: "+str(row["movetype"])  
      if row.has_key("partnumber"):
        if row["partnumber"]!="":
          prod_ = self.ns.db((self.ns.db.product.deleted==0)&(self.ns.db.product.partnumber==row["partnumber"])).select().as_list()
          if len(prod_)==0:
            return "Error|Unknown partnumber No: "+str(row["partnumber"])
          values["product_id"] = prod_[0]["id"]
        else:
          values["product_id"] = None
        del row["partnumber"]
      if row.has_key("serial"):
        if row["serial"]!="":
          prod_ = self.ns.db((self.ns.db.tool.deleted==0)&(self.ns.db.tool.serial==row["serial"])).select().as_list()
          if len(prod_)==0:
            return "Error|Unknown serial: "+str(row["serial"])
          values["tool_id"] = prod_[0]["id"]
        else:
          values["tool_id"] = None
        del row["serial"]
      if row.has_key("planumber"):
        if row["planumber"]!="":
          prod_ = self.ns.db((self.ns.db.place.deleted==0)&(self.ns.db.place.planumber==row["planumber"])).select().as_list()
          if len(prod_)==0:
            return "Error|Unknown planumber No: "+str(row["planumber"])
          values["place_id"] = prod_[0]["id"]
        else:
          values["place_id"] = None
        del row["planumber"]
        
      for key in row.keys():
        if key!="rownumber" and key!="transnumber":
          if row[key]=="": row[key]=None
          if self.ns.db.movement.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "movement", movement_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.movement.id==movement_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["transnumber"])+"["+str(row["rownumber"])+"]"
      logst = self.setLogtable(params, "update", "log_trans_update", "trans", trans_id)
      if logst!=True:
          return logst
    return retvalue
    
  def delete_movement(self, params, data):
    return self.deleteTransItem(params, data, "movement")
  
  def update_numberdef(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: setting"
    for row in data:
      values = {}
      numberdef_ = None
      if row.has_key("numberkey")!=True:
        return "Error|Missing required parameter: numberkey"
      if row.has_key("numberkey")==True:
        deflist = self.ns.db((self.ns.db.numberdef.numberkey==row["numberkey"])).select().as_list()
        if len(deflist)>0:
          numberdef_ = deflist[0]
      if numberdef_==None:  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: setting"
          values["numberkey"] = row["numberkey"]
          ret = self.ns.db.numberdef.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            numberdef_ = self.ns.db(self.ns.db.numberdef.id==ret.id).select().as_list()[0]
            values={}
        else:
          return "Error|Missing id and no insert_row parameter"
      
      for key in row.keys():
        if key!="numberkey":
          if row[key]=="": row[key]=None
          if self.ns.db.numberdef.has_key(key):
            values[key]= row[key]
          else:
            return "Error|Unknown fieldname: "+key
      if len(values)>0:    
        ret = self.ns.db(self.ns.db.numberdef.id==numberdef_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["numberkey"])
    return retvalue
  
  def delete_numberdef(self, params, data):
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit!="all":
      return "Error|Restricted type: setting"
    return self.deleteNervaObj1(params, data, "numberdef", "numberkey")
  
  def update_pattern(self, params, data):
    retvalue = "OK"
    for row in data:
      values = {}
      pattern_ = None
      if row.has_key("description")!=True:
        return "Error|Missing required parameter: description"
      if row.has_key("id")==True:
        deflist = self.ns.db((self.ns.db.pattern.description==row["description"])).select().as_list()
        if len(deflist)>0:
          pattern_ = deflist[0]
      if row.has_key("transtype")==True:
        transtype = self.ns.db((self.ns.db.groups.groupname=="transtype")&(self.ns.db.groups.groupvalue==row["transtype"])).select().as_list()
        if len(transtype)>0:
          values["transtype"] = transtype[0]["id"]
        else:
          return "Error|Unknown transtype: "+str(row["transtype"])
      
      audit = self.ns.getObjectAudit("trans",transtype)
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly transtype: "+transtype
          
      if pattern_==None:
        if row.has_key("transtype")!=True:
          return "Error|Missing required parameter: transtype"  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: "+transtype
          values["description"] = row["description"]
          ret = self.ns.db.pattern.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            pattern_ = self.ns.db(self.ns.db.pattern.id==ret.id).select().as_list()[0]
            values={}
        else:
          return "Error|Missing description and no insert_row parameter"
      
      for key in row.keys():
        if key!="description" and key!="transtype":
          if row[key]=="": row[key]=None
          if self.ns.db.pattern.has_key(key):
            values[key]= row[key]
          else:
            return "Error|Unknown fieldname: "+key
      if len(values)>0:    
        ret = self.ns.db(self.ns.db.pattern.id==pattern_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["description"])
    return retvalue
  
  def delete_pattern(self, params, data):
    for row in data:
      if row.has_key("description"):
        pattern = self.ns.db(self.ns.db.pattern.description==row["description"]).select().as_list()
        if len(pattern)>0:
          transtype = self.ns.db.groups(id=pattern[0]["transtype"]).groupvalue
          audit = self.ns.getObjectAudit("trans",transtype)
          if audit=="error":
            return "Error|"+str(self.ns.error_message)
          if audit!="all":
            return "Error|Restricted type: "+ transtype
    return self.deleteNervaObj2(params, data, "pattern", "description")    
  
  def update_payment(self, params, data):
    from datetime import date, datetime
    
    retvalue = "OK"
    for row in data:
      values = {}
      payment_ = None
      trans_id = None
      if row.has_key("rownumber")!=True:
        return "Error|Missing required parameter: rownumber"
      if row.has_key("transnumber")==True:
        translist = self.ns.db((self.ns.db.trans.deleted==0)&(self.ns.db.trans.transnumber==row["transnumber"])).select().as_list()
        if len(translist)>0:
          trans_id = translist[0]["id"]
          itemlist = self.ns.db((self.ns.db.payment.deleted==0)&(self.ns.db.payment.trans_id==trans_id)).select(orderby=self.ns.db.payment.id).as_list()
          if len(itemlist)>0 and int(row["rownumber"])>0:
            if int(row["rownumber"])<=len(itemlist):
              payment_ = itemlist[int(row["rownumber"])-1]
            else:
              row["rownumber"]=len(itemlist)+1
          else:
            row["rownumber"]=len(itemlist)+1
        else:
          return "Error|Unknown transnumber: "+str(row["transnumber"])
      else:
        return "Error|Missing required parameter: transnumber"
      
      transtype = self.ns.db((self.ns.db.groups.id==translist[0]["transtype"])).select().as_list()[0]["groupvalue"]
      audit = self.ns.getObjectAudit("trans",transtype)
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled" or audit=="readonly":
        return "Error|Disabled or readonly transtype: "+transtype
      
      if payment_==None:  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: "+transtype
          values["trans_id"] = trans_id
          fmt = "%Y.%m.%d 00:00:00"
          values["paiddate"] = datetime.strptime(date.strftime(datetime.now(),fmt),fmt)
          ret = self.ns.db.payment.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            payment_ = self.ns.db(self.ns.db.payment.id==ret.id).select().as_list()[0]
            values={}
        else:
          return "Error|Missing item and no insert_row parameter"
      
      for key in row.keys():
        if key!="rownumber" and key!="transnumber":
          if row[key]=="": row[key]=None
          if self.ns.db.payment.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "payment", payment_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.payment.id==payment_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["transnumber"])+"["+str(row["rownumber"])+"]"
      logst = self.setLogtable(params, "update", "log_trans_update", "trans", trans_id)
      if logst!=True:
          return logst
    return retvalue
  
  def delete_payment(self, params, data):
    return self.deleteTransItem(params, data, "payment")
  
  def update_place(self, params, data):  
    retvalue = "OK"
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: setting"
    for row in data:
      values = {}
      place_ = None
      if row.has_key("planumber")==True:
        plalist = self.ns.db((self.ns.db.place.deleted==0)&(self.ns.db.place.planumber==row["planumber"])).select().as_list()
        if len(plalist)>0:
          place_ = plalist[0]
      
      if place_==None:  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: setting"
          if row.has_key("description")!=True:
            return "Error|Missing required parameter: description"
          if row.has_key("placetype")!=True:
            return "Error|Missing required parameter: placetype. Valid values: bank, cash, warehouse, store"
          else:
            placetype = self.ns.db((self.ns.db.groups.groupname=="placetype")&(self.ns.db.groups.groupvalue==row["placetype"])).select().as_list()
            if len(placetype)>0:
              placetype = placetype[0]
            else:
              return "Error|Unknown placetype: "+str(row["placetype"])
            del row["placetype"]
          if (placetype["groupvalue"]=="bank" or placetype["groupvalue"]=="cash") and row.has_key("curr")!=True:
            return "Error|Missing required parameter: curr"
          if (placetype["groupvalue"]=="store") and row.has_key("ref_planumber")!=True:
            return "Error|Missing required parameter: ref_planumber"
          if (placetype["groupvalue"]=="store") and row.has_key("storetype")!=True:
            return "Error|Missing required parameter: storetype"
          
          if row.has_key("planumber")!=True:
            planumber = self.dbfu.nextNumber(self.ns, {"id":"planumber", "step":True})
          else:
            planumber = row["planumber"]
          plalist = self.ns.db((self.ns.db.place.planumber==planumber)).select().as_list()
          if len(plalist)>0:
            return "Error|New place, but the retrieved planumber is reserved: "+str(planumber)
          
          values["planumber"] = planumber
          values["placetype"] = placetype["id"]
          values["description"] = row["description"]
          ret = self.ns.db.place.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            place_ = self.ns.db(self.ns.db.place.id==ret.id).select().as_list()[0]
            values={}
        else:
          return "Error|Missing planumber and insert_row parameter"
      if row.has_key("placetype"):
        placetype = self.ns.db((self.ns.db.groups.groupname=="placetype")&(self.ns.db.groups.groupvalue==row["placetype"])).select()
        if len(placetype)>0:
          placetype = placetype[0]["id"]
          if place_["placetype"]!=placetype:
            return "Error|Readonly parameter: placetype"
          else:
            del row["placetype"]
        else:
          return "Error|Unknown placetype: "+str(row["placetype"])  
      if row.has_key("curr"):
        if row["curr"]!="":
          curr = self.ns.db((self.ns.db.currency.curr==row["curr"])).select().as_list()
          if len(curr)>0:
            row["curr"] = curr[0]["curr"] 
          else:
            return "Error|Unknown curr: "+row["curr"]
      if row.has_key("ref_planumber")==True:
        if row["ref_planumber"]!="":
          plalist = self.ns.db((self.ns.db.place.deleted==0)&(self.ns.db.place.planumber==row["ref_planumber"])).select().as_list()
          if len(plalist)>0:
            values["place_id"] = plalist[0]["id"] 
          else:
            return "Error|Unknown ref_planumber: "+row["ref_planumber"]
        else:
          values["place_id"] = None
        del row["ref_planumber"]
      if row.has_key("storetype"):
        if row["storetype"]!="":
          storetype = self.ns.db((self.ns.db.groups.groupname=="storetype")&(self.ns.db.groups.groupvalue==row["storetype"])).select().as_list()
          if len(storetype)>0:
            values["storetype"] = storetype[0]["id"]
          else:
            return "Error|Unknown storetype: "+str(row["storetype"])
       
      for key in row.keys():
        if key!="planumber" and key!="placetype":
          if row[key]=="": row[key]=None
          if self.ns.db.place.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "place", place_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.place.id==place_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(place_["planumber"])
      logst = self.setLogtable(params, "update", "log_place_update", "place", place_["id"])
      if logst!=True:
          return logst
    return retvalue
  
  def delete_place(self, params, data):
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit!="all":
      return "Error|Restricted type: setting"
    return self.deleteNervaObj2(params, data, "place", "planumber")
  
  def update_price(self, params, data):
    from datetime import datetime
    
    retvalue = "OK"
    audit = self.ns.getObjectAudit("price")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: price"
    for row in data:
      values = {}
      if row.has_key("partnumber")!=True:
        return "Error|Missing required parameter: partnumber"
      else:
        prod_ = self.ns.db((self.ns.db.product.deleted==0)&(self.ns.db.product.partnumber==row["partnumber"])).select().as_list()
        if len(prod_)==0:
          return "Error|Unknown partnumber No: "+str(row["partnumber"])
        product_id = prod_[0]["id"]
      if row.has_key("pricetype")!=True:
        return "Error|Missing required parameter: pricetype. Valid values: price or discount."
      elif row["pricetype"]=="price":
        pricetype = (self.ns.db.price.discount==None)
      elif row["pricetype"]=="discount":
        pricetype = (self.ns.db.price.discount!=None)
      else:
        return "Error|Unknown pricetype: "+str(row["pricetype"])
      if row.has_key("validfrom")!=True:
        return "Error|Missing required parameter: validfrom"
      else:
        try:
          if datetime.strptime(row["validfrom"],"%Y-%m-%d").__class__.__name__ == "datetime":
            pass
        except Exception:
          return "Error|Incorrect date value! Valid datetime format: YYYY-MM-DD. Fieldname: validfrom"
      if row.has_key("curr"):
        curr = self.ns.db((self.ns.db.currency.curr==row["curr"])).select().as_list()
        if len(curr)>0:
          row["curr"] = curr[0]["curr"] 
        else:
          return "Error|Unknown curr: "+row["curr"]
      else:
        row["curr"] = self.getSetting("default_currency")
      if not row.has_key("qty"):
        row["qty"] = 0
        
      price_ = None
      pricelist = self.ns.db((self.ns.db.price.deleted==0)&(self.ns.db.price.product_id==product_id)
                        &(self.ns.db.price.validfrom==row["validfrom"])&(pricetype)
                        &(self.ns.db.price.curr==row["curr"])&(self.ns.db.price.qty==row["qty"])).select().as_list()
      if len(pricelist)>0:
        price_ = pricelist[0]
      if price_==None:  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: price"
          
          values["product_id"] = product_id
          values["validfrom"] = row["validfrom"]
          values["curr"] = row["curr"]
          if row.has_key("calcmode")!=True:
            calcmode = self.ns.db((self.ns.db.groups.groupname=="calcmode")&(self.ns.db.groups.groupvalue=="ded")).select().as_list()
            if len(calcmode)>0:
              values["calcmode"] = calcmode[0]["id"]
          else:
            values["calcmode"] = self.ns.db((self.ns.db.groups.groupname=="calcmode")&(self.ns.db.groups.groupvalue=="amo")).select().as_list()[0]["id"]
          if row["pricetype"]=="discount":
            values["discount"] = 0
            
          ret = self.ns.db.price.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            price_ = self.ns.db(self.ns.db.price.id==ret.id).select().as_list()[0]
            values={}
        else:
          return "Error|Missing partnumber and insert_row parameter"
      if row.has_key("calcmode"):
        if row["calcmode"]!="":
          calcmode = self.ns.db((self.ns.db.groups.groupname=="calcmode")&(self.ns.db.groups.groupvalue==row["calcmode"])).select().as_list()
          if len(calcmode)>0:
            row["calcmode"] = calcmode[0]["id"]
          else:
            return "Error|Unknown calcmode: "+row["calcmode"]
      
      for key in row.keys():
        if key!="partnumber" and key!="pricetype":
          if row[key]=="": row[key]=None
          if self.ns.db.price.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "price", price_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.price.id==price_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["partnumber"])+"["+str(price_["validfrom"])+"-"+price_["curr"]+"]"
      logst = self.setLogtable(params, "update", "log_product_update", "product", product_id)
      if logst!=True:
          return logst
    return retvalue
  
  def delete_price(self, params, data):
    from datetime import datetime
    
    retvalue = "OK"
    audit = self.ns.getObjectAudit("price")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit!="all":
      return "Error|Restricted type: price"
    delete_ini = self.getSetting("set_trans_deleted")
    for row in data:
      if row.has_key("partnumber")!=True:
        return "Error|Missing required parameter: partnumber"
      else:
        prod_ = self.ns.db((self.ns.db.product.deleted==0)&(self.ns.db.product.partnumber==row["partnumber"])).select().as_list()
        if len(prod_)==0:
          return "Error|Unknown partnumber No: "+str(row["partnumber"])
        product_id = prod_[0]["id"]
      if row.has_key("pricetype")!=True:
        return "Error|Missing required parameter: pricetype"
      elif row["pricetype"]=="price":
        pricetype = (self.ns.db.price.discount==None)
      elif row["pricetype"]=="discount":
        pricetype = (self.ns.db.price.discount!=None)
      else:
        return "Error|Unknown pricetype: "+str(row["pricetype"])
      if row.has_key("validfrom")!=True:
        return "Error|Missing required parameter: validfrom"
      else:
        try:
          if datetime.strptime(row["validfrom"],"%Y-%m-%d").__class__.__name__ == "datetime":
            pass
        except Exception:
          return "Error|Incorrect date value! Valid datetime format: YYYY-MM-DD. Fieldname: validfrom"
  
      pricelist = self.ns.db((self.ns.db.price.deleted==0)&(self.ns.db.price.product_id==product_id)&(self.ns.db.price.validfrom==row["validfrom"])&(pricetype)).select().as_list()
      
      if len(pricelist)>0:
        if delete_ini != "true":
          values = {"deleted":1}
          ret = self.ns.db(self.ns.db.price.id==pricelist[0]["id"]).validate_and_update(**values)
          if ret.errors:
            self.ns.db.rollback()
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          dfield = self.deleteFieldValues(params, "price", pricelist[0]["id"])
          if dfield!=True:
            return dfield
          try:
            self.ns.db(self.ns.db.price.id==pricelist[0]["id"]).delete()
          except Exception, err:
            self.ns.db.rollback()
            return str(err)
        logst = self.setLogtable(params, "update", "log_product_delete", "product", product_id)
        if logst!=True:
          return logst 
        retvalue = retvalue+"|"+str(row["partnumber"])+"["+str(pricelist[0]["validfrom"])+"-"+pricelist[0]["curr"]+"]"
    return retvalue
      
  def update_product(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("product")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: product"
    for row in data:
      values = {}
      product_ = None
      if row.has_key("partnumber")==True:
        partlist = self.ns.db((self.ns.db.product.deleted==0)&(self.ns.db.product.partnumber==row["partnumber"])).select().as_list()
        if len(partlist)>0:
          product_ = partlist[0]
      if product_==None:  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: product"
          if row.has_key("description")!=True:
            return "Error|Missing required parameter: description"
          if row.has_key("partnumber")!=True:
            partnumber = self.dbfu.nextNumber(self.ns, {"id":"partnumber", "step":True})
          else:
            partnumber = row["partnumber"]
          partlist = self.ns.db((self.ns.db.product.partnumber==partnumber)).select().as_list()
          if len(partlist)>0:
            return "Error|New product, but the retrieved partnumber is reserved: "+str(partnumber)
          
          values["partnumber"] = partnumber
          values["description"] = row["description"]
          values["protype"] = self.ns.db((self.ns.db.groups.groupname=="protype")&(self.ns.db.groups.groupvalue=="item")).select().as_list()[0]["id"]
          tax = self.ns.db(self.ns.db.tax.taxcode==self.getSetting("default_taxcode")).select().as_list()
          if len(tax)>0:
            tax = tax[0]
          else:
            tax = self.ns.db(self.ns.db.tax).select().as_list()[0]
          values["tax_id"] = tax["id"]
          values["unit"] = self.getSetting("default_unit")
          ret = self.ns.db.product.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            product_ = self.ns.db(self.ns.db.product.id==ret.id).select().as_list()[0]
            values={}
        else:
          return "Error|Missing partnumber and insert_row parameter"
      if row.has_key("protype")==True:
        if row["protype"]=="item":
          row["protype"] = self.ns.db((self.ns.db.groups.groupname=="protype")&(self.ns.db.groups.groupvalue=="item")).select().as_list()[0]["id"]
        elif row["protype"]=="service":
          row["protype"] = self.ns.db((self.ns.db.groups.groupname=="protype")&(self.ns.db.groups.groupvalue=="service")).select().as_list()[0]["id"]
        else:
          return "Error|Valid transfilter: item, service "  
      if row.has_key("taxcode")==True:
        tax = self.ns.db(self.ns.db.tax.taxcode==row["taxcode"]).select().as_list()
        if len(tax)>0:
          values["tax_id"] = tax[0]["id"]
          del row["taxcode"] 
        else:
          return "Error|Unknown taxcode: "+row["taxcode"]
      
      for key in row.keys():
        if key!="partnumber":
          if row[key]=="": row[key]=None
          if self.ns.db.product.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "product", product_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.product.id==product_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(product_["partnumber"])
      logst = self.setLogtable(params, "update", "log_product_update", "product", product_["id"])
      if logst!=True:
          return logst
    return retvalue
  
  def delete_product(self, params, data):
    return self.deleteNervaObj2(params, data, "product", "partnumber")
  
  def update_project(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("project")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: project"
    for row in data:
      values = {}
      project_ = None
      if row.has_key("pronumber")==True:
        prolist = self.ns.db((self.ns.db.project.deleted==0)&(self.ns.db.project.pronumber==row["pronumber"])).select().as_list()
        if len(prolist)>0:
          project_ = prolist[0]
      if project_==None:  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: project"
          if row.has_key("description")!=True:
            return "Error|Missing required parameter: description"
          if row.has_key("pronumber")!=True:
            pronumber = self.dbfu.nextNumber(self.ns, {"id":"pronumber", "step":True})
          else:
            pronumber = row["pronumber"]
          prolist = self.ns.db((self.ns.db.project.pronumber==pronumber)).select().as_list()
          if len(prolist)>0:
            return "Error|New project, but the retrieved pronumber is reserved: "+str(pronumber)
            
          values["pronumber"] = pronumber
          values["description"] = row["description"]
          ret = self.ns.db.project.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            project_ = self.ns.db(self.ns.db.project.id==ret.id).select().as_list()[0]
            values={}
        else:
          return "Error|Missing pronumber and insert_row parameter" 
      if row.has_key("custnumber"):
        if row["custnumber"]!="":
          customer = self.ns.db((self.ns.db.customer.deleted==0)&(self.ns.db.customer.custnumber==row["custnumber"])).select().as_list()
          if len(customer)>0:
            values["customer_id"] = customer[0]["id"] 
          else:
            return "Error|Unknown custnumber: "+row["custnumber"]
        else:
          values["customer_id"] = None
        del row["custnumber"]
        
      for key in row.keys():
        if key!="pronumber":
          if row[key]=="": row[key]=None
          if self.ns.db.project.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "project", project_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.project.id==project_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(project_["pronumber"])
      logst = self.setLogtable(params, "update", "log_project_update", "project", project_["id"])
      if logst!=True:
          return logst
    return retvalue
  
  def delete_project(self, params, data):
    return self.deleteNervaObj2(params, data, "project", "pronumber")
  
  def update_rate(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: setting"
    for row in data:
      values = {}
      rate_ = None
      if row.has_key("ratetype")!=True:
        return "Error|Missing required parameter: ratetype. Valid values: rate,buy,sell,average."
      else:
        ratetype = self.ns.db((self.ns.db.groups.groupname=="ratetype")&(self.ns.db.groups.groupvalue==row["ratetype"])).select().as_list()
        if len(ratetype)>0:
          values["ratetype"] = ratetype[0]["id"]
        else:
          return "Error|Unknown ratetype: "+str(row["ratetype"])
      if row.has_key("ratedate")!=True:
        return "Error|Missing required parameter: ratedate"
      if row.has_key("curr")!=True:
        return "Error|Missing required parameter: curr"
      else:
        currlist = self.ns.db((self.ns.db.currency.curr==row["curr"])).select().as_list()
        if len(currlist)>0:
          values["curr"] = currlist[0]["curr"]
        else:
          return "Error|Unknown curr: "+str(row["curr"])
      if row.has_key("planumber")!=True:
        return "Error|Missing required parameter: planumber"
      else:
        plalist = self.ns.db((self.ns.db.place.deleted==0)&(self.ns.db.place.planumber==row["planumber"])).select().as_list()
        if len(plalist)>0:
          values["place_id"] = plalist[0]["id"]
        else:
          return "Error|Unknown planumber: "+str(row["planumber"])
        del row["planumber"]
      
      ratelist = self.ns.db((self.ns.db.rate.deleted==0)&(self.ns.db.rate.ratetype==values["ratetype"])&(self.ns.db.rate.ratedate==row["ratedate"])
                       &(self.ns.db.rate.curr==values["curr"])&(self.ns.db.rate.place_id==values["place_id"])).select().as_list()
      if len(ratelist)>0:
        rate_ = ratelist[0]
      if rate_==None:  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: setting"
          values["ratedate"] = row["ratedate"]
          ret = self.ns.db.rate.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            rate_ = self.ns.db(self.ns.db.rate.id==ret.id).select().as_list()[0]
            values={}
        else:
          return "Error|Missing datarow and no insert_row parameter"
      if row.has_key("rategroup")==True:
        if row["rategroup"]!="":
          rategroup = self.ns.db((self.ns.db.groups.groupname=="rategroup")&(self.ns.db.groups.groupvalue==row["rategroup"])).select().as_list()
          if len(rategroup)>0:
            row["rategroup"] = rategroup[0].id
          else:
            return "Error|Unknown rategroup: "+str(row["rategroup"])
      
      for key in row.keys():
        if key!="ratetype" and key!="ratedate" and key!="curr" and key!="planumber":
          if row[key]=="": row[key]=None
          if self.ns.db.rate.has_key(key):
            values[key]= row[key]
          else:
            return "Error|Unknown fieldname: "+key
      if len(values)>0:
        ret = self.ns.db(self.ns.db.rate.id==rate_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["ratedate"])+"-"+str(row["curr"])
      logst = self.setLogtable(params, "update", "log_rate_update", "rate", rate_["id"])
      if logst!=True:
          return logst
    return retvalue
  
  def delete_rate(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit!="all":
      return "Error|Restricted type: setting"
    delete_ini = self.getSetting("set_trans_deleted")
    for row in data:
      if row.has_key("ratetype")!=True:
        return "Error|Missing required parameter: ratetype"
      else:
        ratetype = self.ns.db((self.ns.db.groups.groupname=="ratetype")&(self.ns.db.groups.groupvalue==row["ratetype"])).select().as_list()
        if len(ratetype)>0:
          row["ratetype"] = ratetype[0]["id"]
        else:
          return "Error|Unknown ratetype: "+str(row["ratetype"])
      if row.has_key("ratedate")!=True:
        return "Error|Missing required parameter: ratedate"
      if row.has_key("curr")!=True:
        return "Error|Missing required parameter: curr"
      else:
        currlist = self.ns.db((self.ns.db.currency.curr==row["curr"])).select().as_list()
        if len(currlist)>0:
          row["curr"] = currlist[0]["curr"]
        else:
          return "Error|Unknown curr: "+str(row["curr"])
      if row.has_key("planumber")!=True:
        return "Error|Missing required parameter: planumber"
      else:
        plalist = self.ns.db((self.ns.db.place.deleted==0)&(self.ns.db.place.planumber==row["planumber"])).select().as_list()
        if len(plalist)>0:
          row["place_id"] = plalist[0]["id"]
        else:
          return "Error|Unknown planumber: "+str(row["planumber"])
        del row["planumber"]
      
      ratelist = self.ns.db((self.ns.db.rate.deleted==0)&(self.ns.db.rate.ratetype==row["ratetype"])&(self.ns.db.rate.ratedate==row["ratedate"])
                       &(self.ns.db.rate.curr==row["curr"])&(self.ns.db.rate.place_id==row["place_id"])).select().as_list()
      if len(ratelist)>0:
        if delete_ini != "true":
          values = {"deleted":1}
          ret = self.ns.db(self.ns.db.rate.id==ratelist[0]["id"]).validate_and_update(**values)
          if ret.errors:
            self.ns.db.rollback()
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
        else:
          try:
            self.ns.db(self.ns.db.rate.id==ratelist[0]["id"]).delete()
          except Exception, err:
            self.ns.db.rollback()
            return str(err)
        logst = self.setLogtable(params, "update", "log_rate_delete", "rate", ratelist[0]["id"])
        if logst!=True:
          return logst 
        retvalue = retvalue+"|"+str(row["ratedate"])+"-"+str(row["curr"])
    return retvalue
   
  def update_tax(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: setting"
    for row in data:
      values = {}
      tax_ = None
      if row.has_key("taxcode")!=True:
        return "Error|Missing required parameter: taxcode"
      else:
        taxlist = self.ns.db((self.ns.db.tax.taxcode==row["taxcode"])).select().as_list()
        if len(taxlist)>0:
          tax_ = taxlist[0]
      if tax_==None:
        if row.has_key("description")!=True:
          return "Error|Missing required parameter: description"  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: setting"
          values["taxcode"] = row["taxcode"]
          values["description"] = row["description"]
          ret = self.ns.db.tax.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            tax_ = self.ns.db(self.ns.db.tax.id==ret.id).select().as_list()[0]
            values={}
  
        else:
          return "Error|Missing code and no insert_row parameter"
        
      for key in row.keys():
        if key!="taxcode":
          if row[key]=="": row[key]=None
          if self.ns.db.tax.has_key(key):
            values[key]= row[key]
          else:
            return "Error|Unknown fieldname: "+key
      if len(values)>0:
        ret = self.ns.db(self.ns.db.tax.id==tax_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(row["taxcode"])
      logst = self.setLogtable(params, "update", "log_tax_update", "tax", tax_["id"])
      if logst!=True:
          return logst
    return retvalue
  
  def delete_tax(self, params, data):
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit!="all":
      return "Error|Restricted type: setting"
    return self.deleteNervaObj1(params, data, "tax", "taxcode", "taxcode")
  
  def update_tool(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("tool")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: tool"
    for row in data:
      values = {}
      tool_ = None
      if row.has_key("serial")==True:
        toollist = self.ns.db((self.ns.db.tool.deleted==0)&(self.ns.db.tool.serial==row["serial"])).select().as_list()
        if len(toollist)>0:
          tool_ = toollist[0]
      if row.has_key("partnumber")==True:
        product = self.ns.db((self.ns.db.product.deleted==0)&(self.ns.db.product.partnumber==row["partnumber"])).select().as_list()
        if len(product)>0:
          values["product_id"] = product[0]["id"]
        else:
          return "Error|Unknown partnumber: "+row["partnumber"]
      if tool_==None:  
        if params.has_key("insert_row")==True:
          if audit!="all":
            return "Error|Restricted type: tool"
          if row.has_key("partnumber")!=True:
            return "Error|Missing required parameter: partnumber"
          if row.has_key("serial")!=True:
            serial = self.dbfu.nextNumber(self.ns, {"id":"serial", "step":True})
          else:
            serial = row["serial"]
          toollist = self.ns.db((self.ns.db.tool.serial==serial)).select().as_list()
          if len(toollist)>0:
            return "Error|New tool, but the retrieved serial is reserved: "+str(serial)
            
          values["serial"] = serial
          ret = self.ns.db.tool.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            tool_ = self.ns.db(self.ns.db.tool.id==ret.id).select().as_list()[0]
            values={}
        else:
          return "Error|Missing serial and insert_row parameter"  
      if row.has_key("toolgroup")==True:
        if row["toolgroup"]!="":
          toolgroup = self.ns.db((self.ns.db.groups.groupname=="toolgroup")&(self.ns.db.groups.groupvalue==row["toolgroup"])).select().as_list()
          if len(toolgroup)>0:
            values["toolgroup"] = toolgroup[0]["id"]
          else:
            return "Error|Unknown toolgroup: "+str(row["toolgroup"])
        
      for key in row.keys():
        if key!="serial" and key!="partnumber":
          if row[key]=="": row[key]=None
          if self.ns.db.tool.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "tool", tool_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.tool.id==tool_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
      retvalue = retvalue+"|"+str(tool_["serial"])
      logst = self.setLogtable(params, "update", "log_tool_update", "tool", tool_["id"])
      if logst!=True:
          return logst
    return retvalue
  
  def delete_tool(self, params, data):
    return self.deleteNervaObj2(params, data, "tool", "serial")
  
  def update_trans(self, params, data):
    from datetime import date
    
    retvalue = "OK"      
    for row in data:
      values = {}
      trans_ = None
      if row.has_key("transnumber"):
        translist = self.ns.db((self.ns.db.trans.deleted==0)&(self.ns.db.trans.transnumber==row["transnumber"])).select().as_list()
        if len(translist)>0:
          trans_ = translist[0]
          transtype = self.ns.db.groups(id=translist[0]["transtype"]).groupvalue
          audit = self.ns.getObjectAudit("trans",transtype)
          if audit=="error":
            return "Error|"+str(self.ns.error_message)
          if audit=="disabled" or audit=="readonly":
            return "Error|Disabled or readonly transtype: "+transtype
      
      if row.has_key("empnumber"):
        if row["empnumber"]!="":
          employee_ = self.ns.db((self.ns.db.employee.deleted==0)&(self.ns.db.employee.empnumber==row["empnumber"])).select().as_list()
          if len(employee_)==0:
            return "Error|Unknown empnumber No: "+str(row["empnumber"])
          row["employee_id"] = employee_[0]["id"]
        else:
          row["employee_id"] = None
        del row["empnumber"]
      if row.has_key("department"):
        if row["department"]!="":
          department = self.ns.db((self.ns.db.groups.groupname=="department")&(self.ns.db.groups.groupvalue==row["department"])).select().as_list()
          if len(department)>0:
            row["department"] = department[0]["id"]
          else:
            return "Error|Unknown department: "+str(row["department"])
      if row.has_key("pronumber"):
        if row["pronumber"]!="":
          project_ = self.ns.db((self.ns.db.project.deleted==0)&(self.ns.db.project.pronumber==row["pronumber"])).select().as_list()
          if len(project_)==0:
            return "Error|Unknown pronumber No: "+str(row["pronumber"])
          row["project_id"] = project_[0]["id"]
        else:
          row["project_id"] = None
        del row["pronumber"]
      if row.has_key("planumber"):
        if row["planumber"]!="":
          place_ = self.ns.db((self.ns.db.place.deleted==0)&(self.ns.db.place.planumber==row["planumber"])).select().as_list()
          if len(place_)==0:
            return "Error|Unknown pronumber No: "+str(row["planumber"]) 
          row["place_id"] = place_[0]["id"]
        else:
          row["place_id"] = None
        del row["planumber"]
      if row.has_key("paidtype"):
        if row["paidtype"]!="":
          paidtype = self.ns.db((self.ns.db.groups.groupname=="paidtype")&(self.ns.db.groups.groupvalue==row["paidtype"])).select().as_list()
          if len(paidtype)>0:
            row["paidtype"] = paidtype[0]["id"]
          else:
            return "Error|Unknown paidtype: "+str(row["paidtype"])      
      if row.has_key("curr"):
        if row["curr"]!="":
          curr_ = self.ns.db(self.ns.db.currency.curr==row["curr"]).select().as_list()
          if len(curr_)==0:
            return "Error|Unknown curr: "+str(row["curr"])
          row["curr"] = curr_[0]["curr"]
      if row.has_key("transtate"):
        transtate = self.ns.db((self.ns.db.groups.groupname=="transtate")&(self.ns.db.groups.groupvalue==row["transtate"])).select().as_list()
        if len(transtate)>0:
          row["transtate"] = transtate[0]["id"]
        else:
          return "Error|Unknown transtate: "+str(row["transtate"])
      if row.has_key("custnumber"):
        if row["custnumber"]!="":
          customer_ = self.ns.db((self.ns.db.customer.deleted==0)&(self.ns.db.customer.custnumber==row["custnumber"])).select().as_list()
          if len(customer_)==0:
            return "Error|Unknown custnumber No: "+str(row["custnumber"])
          row["customer_id"] = customer_[0]["id"]
        else:
          row["customer_id"] = None
        del row["custnumber"]
          
      if trans_==None:  
        if params.has_key("insert_row")==True:
          if row.has_key("transtype")!=True:
            return "Error|Missing required parameter: transtype"
          else:
            transtype = self.ns.db((self.ns.db.groups.groupname=="transtype")&(self.ns.db.groups.groupvalue==row["transtype"])).select().as_list()
            if len(transtype)>0:
              transtype = transtype[0]
            else:
              return "Error|Unknown transtype: "+str(row["transtype"])
            audit = self.ns.getObjectAudit("trans",row["transtype"])
            if audit=="error":
              return "Error|"+str(self.ns.error_message)
            if audit!="all":
              return "Error|Restricted transtype: "+row["transtype"]
            del row["transtype"]
          if row.has_key("direction")!=True:
            return "Error|Missing required parameter: direction"
          else:
            direction = self.ns.db((self.ns.db.groups.groupname=="direction")&(self.ns.db.groups.groupvalue==row["direction"])).select().as_list()
            if len(direction)>0:
              direction = direction[0]
            else:
              return "Error|Unknown direction: "+str(row["direction"])
            del row["direction"]
          if row.has_key("custnumber")!=True and row.has_key("customer_id")!=True and (transtype["groupvalue"] in("offer","order","worksheet","rent","invoice")):
            return "Error|Missing required parameter: custnumber"
          if row.has_key("planumber")!=True and row.has_key("place_id")!=True and transtype["groupvalue"]in("bank","cash"):
            return "Error|Missing required parameter: planumber"
          transcast="normal"
          if row.has_key("transcast"):
            transcast = self.ns.db((self.ns.db.fieldvalue.ref_id==trans_["id"])&(self.ns.db.fieldvalue.fieldname=="trans_transcast")).select()
            if len(transcast)>0:
              transcast = transcast[0]["value"]
          
          if row.has_key("transnumber")!=True:
            tname = str(transtype["groupvalue"])+"_"+str(direction["groupvalue"])
            transnumber = self.dbfu.nextNumber(self.ns, {"id":tname, "step":True})
          else:
            transnumber = row["transnumber"]
          checklist = self.ns.db((self.ns.db.trans.transnumber==transnumber)).select().as_list()
          if len(checklist)>0:
            return "Error|New trans, but the retrieved trans No. is reserved: "+str(transnumber)
          values["transnumber"] = transnumber
          values["transtype"] = transtype["id"]
          values["direction"] = direction["id"]
          values["crdate"] = date.today()
          values["cruser_id"] = self.ns.employee["id"]
          values["transdate"] = date.today()
          if transtype["groupvalue"] in("offer","order","worksheet","rent","invoice","receipt"):
            values["curr"] = self.getSetting("default_currency")
            values["paidtype"] = self.ns.db((self.ns.db.groups.groupname=="paidtype")&(self.ns.db.groups.groupvalue==self.getSetting("default_paidtype"))).select().as_list()[0]["id"]
          if self.getSetting("audit_control")=="true":
            values["transtate"] = self.ns.db((self.ns.db.groups.groupname=="transtate")&(self.ns.db.groups.groupvalue=="new")).select().as_list()[0]["id"]
          else:
            values["transtate"] = self.ns.db((self.ns.db.groups.groupname=="transtate")&(self.ns.db.groups.groupvalue=="ok")).select().as_list()[0]["id"]
          plst = self.ns.db((self.ns.db.pattern.deleted==0)&(self.ns.db.pattern.defpattern==1)&(self.ns.db.pattern.transtype==values["transtype"])).select().as_list()
          if len(plst)>0:
            values["fnote"] = plst[0]["notes"]
          ret = self.ns.db.trans.validate_and_insert(**values)
          if ret.errors:
            return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0]
          else:
            trans_ = self.ns.db(self.ns.db.trans.id==ret.id).select().as_list()[0]
            values={}
            #set transcast
            self.ns.db.fieldvalue.insert(**{"fieldname":"trans_transcast","ref_id":trans_["id"],"value":transcast})
            #add auto deffields
            nervatype_trans = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
            addnew = self.ns.db((self.ns.db.deffield.deleted==0)&(self.ns.db.deffield.visible==1)&(self.ns.db.deffield.nervatype==nervatype_trans)&
                       (self.ns.db.deffield.addnew==1)).select()
            for nfield in addnew:
              self.ns.db.fieldvalue.insert(**{"fieldname":nfield["fieldname"],"ref_id":trans_["id"],"value":self.get_default_value(nfield["fieldtype"])})
            
        else:
          return "Error|Missing transnumber and insert_row parameter"
        
      if row.has_key("transtype"):
        transtype = self.ns.db((self.ns.db.groups.groupname=="transtype")&(self.ns.db.groups.groupvalue==row["transtype"])).select()
        if len(transtype)>0:
          transtype = transtype[0]["id"]
          if trans_["transtype"]!=transtype:
            return "Error|Readonly parameter: transtype "
        else:
          return "Error|Unknown transtype: "+str(row["transtype"])
        del row["transtype"]
      if row.has_key("direction"):
        direction = self.ns.db((self.ns.db.groups.groupname=="direction")&(self.ns.db.groups.groupvalue==row["direction"])).select().as_list()
        if len(direction)>0:
          direction = direction[0]["id"]
          if trans_["direction"]!=direction:
            return "Error|Readonly parameter: direction "
        else:
          return "Error|Unknown direction: "+str(row["direction"])
        del row["direction"]
      
      transtype = self.ns.db((self.ns.db.groups.id==trans_["transtype"])).select().as_list()[0]["groupvalue"]    
      if transtype=="invoice":
        if row["customer_id"]!=None:
          customer_id = row["customer_id"]
        elif trans_["customer_id"]!=None:
          customer_id = trans_["customer_id"]
        else:
          return "Error|Missing required parameter: custnumber"
        customer_ = self.ns.db((self.ns.db.customer.id==customer_id)).select().as_list()
        neraid = self.ns.db((self.ns.db.groups.groupname=="nervatype")&(self.ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
        self.setFieldValue("trans_custinvoice_custname", str(customer_[0]["custname"]), "trans", trans_["id"], True)
        if customer_[0]["taxnumber"]!=None:
          self.setFieldValue("trans_custinvoice_custtax", str(customer_[0]["taxnumber"]), "trans", trans_["id"], True)
        addr_ = self.ns.db((self.ns.db.address.deleted==0)&(self.ns.db.address.nervatype==neraid)&(self.ns.db.address.ref_id==customer_[0]["id"])).select().as_list()
        if len(addr_)>0:
          address=""
          if addr_[0]["zipcode"]!=None:
            address = str(addr_[0]["zipcode"])
          if addr_[0]["city"]!=None:
            address = address+" "+str(addr_[0]["city"])
          if addr_[0]["street"]!=None:
            address = address+" "+str(addr_[0]["street"])
          self.setFieldValue("trans_custinvoice_custaddress", address, "trans", trans_["id"], True)        
        customer_ = self.ns.db((self.ns.db.customer.id==1)).select().as_list()
        self.setFieldValue("trans_custinvoice_compname", str(customer_[0]["custname"]), "trans", trans_["id"], True)
        if customer_[0]["taxnumber"]!=None:
          self.setFieldValue("trans_custinvoice_comptax", str(customer_[0]["taxnumber"]), "trans", trans_["id"], True)
        addr_ = self.ns.db((self.ns.db.address.deleted==0)&(self.ns.db.address.nervatype==neraid)&(self.ns.db.address.ref_id==customer_[0]["id"])).select().as_list()
        if len(addr_)>0:
          address=""
          if addr_[0]["zipcode"]!=None:
            address = str(addr_[0]["zipcode"])
          if addr_[0]["city"]!=None:
            address = address+" "+str(addr_[0]["city"])
          if addr_[0]["street"]!=None:
            address = address+" "+str(addr_[0]["street"])
          self.setFieldValue("trans_custinvoice_compaddress", address, "trans", trans_["id"], True)
  
      for key in row.keys():
        if key!="transnumber":
          if row[key]=="": row[key]=None
          if self.ns.db.trans.has_key(key):
            values[key]= row[key]
          else:
            retval = self.setFieldValue(key, row[key], "trans", trans_["id"], params.has_key("insert_field"))
            if retval!=True:
              return retval
      if len(values)>0:
        ret = self.ns.db(self.ns.db.trans.id==trans_["id"]).validate_and_update(**values)
        if ret.errors:
          self.ns.db.rollback()
          return "Error|"+ret.errors.keys()[0]+": "+ret.errors.values()[0] 
      retvalue = retvalue+"|"+trans_["transnumber"]
      logst = self.setLogtable(params, "update", "log_trans_update", "trans", trans_["id"])
      if logst!=True:
        return logst
    return retvalue
  
  def delete_trans(self, params, data):
    for row in data:
      if row.has_key("transnumber"):
        trans = self.ns.db(self.ns.db.trans.transnumber==row["transnumber"]).select().as_list()
        if len(trans)>0:
          transtype = self.ns.db.groups(id=trans[0]["transtype"]).groupvalue
          audit = self.ns.getObjectAudit("trans",transtype)
          if audit=="error":
            return "Error|"+str(self.ns.error_message)
          if audit!="all":
            return "Error|Restricted type: "+ transtype
    return self.deleteNervaObj2(params, data, "trans", "transnumber")
  
  def update_setting(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit=="disabled" or audit=="readonly":
      return "Error|Disabled or readonly type: setting"
    for row in data:
      if row.has_key("fieldname")!=True:
        return "Error|Missing required parameter: fieldname"
      if row.has_key("value")!=True:
        return "Error|Missing required parameter: value"
      deffields = self.ns.db((self.ns.db.deffield.deleted==0)&(self.ns.db.deffield.fieldname==row["fieldname"])).select().as_list()
      if len(deffields)==0:
        return "Error|Unknown fieldname: "+str(row["fieldname"])
      else:
        retval = self.setFieldValue(row["fieldname"], row["value"], "setting", None, True)
        if retval!=True:
          return retval
      retvalue = retvalue+"|"+row["fieldname"]
    return retvalue
  
  def delete_setting(self, params, data):
    retvalue = "OK"
    audit = self.ns.getObjectAudit("setting")
    if audit=="error":
      return "Error|"+str(self.ns.error_message)
    if audit!="all":
      return "Error|Restricted type: setting"
    for row in data:
      if row.has_key("fieldname")!=True:
        return "Error|Missing required parameter: fieldname"
      deffields = self.ns.db((self.ns.db.deffield.deleted==0)&(self.ns.db.deffield.fieldname==row["fieldname"])).select().as_list()
      if len(deffields)==0:
        return "Error|Unknown fieldname: "+str(row["fieldname"])
      else:
        retval = self.deleteFieldValues(params, "setting", None, row["fieldname"])
        if retval!=True:
          return retval
      retvalue = retvalue+"|"+row["fieldname"]
    return retvalue
  
  def getView(self, params, filter):#@ReservedAssignment
      
    retvalue="OK"
    
    item_str = ""
    fld_value = ""
    fields = []
    items = []
    
    if filter.has_key("output")==True:
      if filter["output"] not in("text","html","xml","excel"):
        return "Error|Valid output: text, html, xml, excel"
    else:
      filter["output"]="text"
    header=[]
    if filter.has_key("header")==True:
      header=filter["header"].split(",")
    
    if filter["output"].startswith("xml") and not filter.has_key("show_id"):
      filter["show_id"] = "xml"
    
    select_str=""
    from_str=""
    where_str=""
    orderby_str=""
    limit_str=""
    
    if filter.has_key("where")==True:
      if filter["where"]!="":
        where_str="and "+filter["where"]
    orderby=""
    if filter.has_key("orderby")==True:
      if filter["orderby"]!="":
        orderby=" order by "+filter["orderby"]
    if params["datatype"]!="sql" and filter.has_key("limit")==True:
      try:
        limit_str=" limit "+str(filter["limit"])
      except Exception, err:
        return "Error|"+str(err)
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    if params["datatype"]=="sql":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "item"
      
      audit = self.ns.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: setting"
      
      filter["show_id"] = "sql"
      if filter.has_key("sql")!=True:
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
      if filter.has_key("nervatype")!=True:
        return "Error|Missing required parameter: nervatype"
      nervanumber = self.getNumberName(filter["nervatype"])
      if nervanumber.startswith("Error"):
        return nervanumber
      
      audit = self.ns.getObjectAudit(filter["nervatype"])
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: "+filter["nervatype"]
      
      fields_ = [{"nervatype":"g.groupvalue"}, {"refnumber":"nerv."+str(nervanumber)}, {"rownumber":"rownumber"}, 
                 {"represent_rownumber":"rownumber"},
                 {"country":"address.country"}, {"state":"address.state"}, {"zipcode":"address.zipcode"}, {"city":"address.city"}, 
                 {"street":"address.street"}, {"notes":"address.notes"}]
      select_str ="select @id, g.groupvalue as nervatype, nerv."+str(nervanumber)+" as refnumber,  1 as rownumber, address.id as represent_rownumber, \
        address.country, address.state, address.zipcode, address.city, address.street, address.notes "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "address.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from address \
        inner join groups g on address.nervatype=g.id and g.groupvalue = '"+str(filter["nervatype"])+"' \
        inner join "+str(filter["nervatype"])+" nerv on address.ref_id = nerv.id and nerv.deleted=0 "
      where_str = " where address.deleted=0 "+where_str
      if orderby=="":
        orderby_str =  " order by refnumber, id "
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
      audit = self.ns.getObjectAudit("product")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: product"
      
      fields_ = [{"barcode":"b.code"}, {"partnumber":"p.partnumber"}, {"barcodetype":"g.groupvalue"}, {"description":"b.description"}, 
                 {"qty":"b.qty"}, {"defcode":"b.defcode"}]
      select_str ="select @id, b.code as barcode, p.partnumber, g.groupvalue as barcodetype, b.description, b.qty, b.defcode "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "p.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = "  from barcode b inner join groups g on b.barcodetype=g.id inner join product p on b.product_id = p.id "
      where_str = " where p.deleted=0 "+where_str
      if orderby=="":
        orderby_str = "order by id "
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " p.id")
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
      if filter.has_key("nervatype")!=True:
        return "Error|Missing required parameter: nervatype"
      nervanumber = self.getNumberName(filter["nervatype"])
      if nervanumber.startswith("Error"):
        return nervanumber
      
      audit = self.ns.getObjectAudit(filter["nervatype"])
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: "+filter["nervatype"]
      
      fields_ = [{"nervatype":"g.groupvalue"}, {"refnumber":"nerv."+str(nervanumber)}, {"rownumber":"rownumber"},
                  {"represent_rownumber":"rownumber"}, 
                  {"firstname":"contact.firstname"}, {"surname":"contact.surname"}, {"status":"contact.status"}, 
                  {"phone":"contact.phone"}, {"fax":"contact.fax"}, {"mobil":"contact.mobil"}, {"email":"contact.email"}, 
                  {"notes":"contact.notes"}]
      select_str ="select @id, g.groupvalue as nervatype, nerv."+str(nervanumber)+" as refnumber,  1 as rownumber, contact.id as represent_rownumber, \
        contact.firstname, contact.surname, contact.status, contact.phone, contact.fax, contact.mobil, contact.email, contact.notes "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "contact.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = "from contact inner join groups g on contact.nervatype=g.id and g.groupvalue = '"+str(filter["nervatype"])+"' \
        inner join "+str(filter["nervatype"])+" nerv on contact.ref_id = nerv.id and nerv.deleted=0 "
      where_str = "where contact.deleted=0 "+where_str
      if orderby=="":
        orderby_str = "order by refnumber, id "
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
      
      audit = self.ns.getObjectAudit("setting")
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
      
      audit = self.ns.getObjectAudit("customer")
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
      
      audit = self.ns.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: setting"
      
      fields_ = [{"fieldname":"df.fieldname"}, {"nervatype":"g.groupvalue"}, {"subtype":"sg.groupvalue"}, {"fieldtype":"fg.groupvalue"},
                 {"description":"df.description"}, {"valuelist":"df.valuelist"}, {"addnew":"df.addnew"}, {"visible":"df.visible"}, 
                 {"readonly":"df.readonly"}]
      select_str ="select @id, df.fieldname, g.groupvalue as nervatype, sg.groupvalue as subtype, fg.groupvalue as fieldtype, \
        df.description, df.valuelist, df.addnew, df.visible, df.readonly "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "df.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from deffield df inner join groups g on df.nervatype=g.id \
        left join groups sg on df.subtype=sg.id inner join groups fg on df.fieldtype=fg.id "
      where_str = " where df.deleted=0 "+where_str
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
      
      audit = self.ns.getObjectAudit("employee")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: employee"
      
      fld_value = "employee"
      fields_ = [{"empnumber":"employee.empnumber"}, {"username":"employee.username"}, {"usergroup":"g.groupvalue"}, {"startdate":"employee.startdate"}, 
                 {"enddate":"employee.enddate"}, {"department":"dg.groupvalue"}, {"email":"employee.email"}, {"inactive":"employee.inactive"}]
      select_str ="select @id, employee.empnumber, employee.username, g.groupvalue as usergroup, employee.startdate, employee.enddate, \
        dg.groupvalue as department, employee.email, employee.inactive "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "employee.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from employee inner join groups g on employee.usergroup=g.id \
        left join groups dg on employee.department=dg.id "
      where_str = " where employee.deleted=0 "+where_str
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
      
      audit = self.ns.getObjectAudit("event")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: event"
      
      fld_value = "event"
      if filter.has_key("nervatype")!=True:
        return "Error|Missing required parameter: nervatype"
      nervanumber = self.getNumberName(filter["nervatype"])
      if nervanumber.startswith("Error"):
        return nervanumber
      fields_ = [{"calnumber":"event.calnumber"}, {"nervatype":"g.groupvalue"}, {"refnumber":"nerv."+str(nervanumber)}, {"uid":"event.uid"}, 
                 {"eventgroup":"eg.groupvalue"}, {"fromdate":"event.fromdate"}, {"todate":"event.todate"}, {"subject":"event.subject"}, 
                 {"place":"event.place"}, {"description":"event.description"}] 
      select_str ="select @id, event.calnumber, g.groupvalue as nervatype, nerv."+str(nervanumber)+" as refnumber, event.uid, \
        eg.groupvalue as eventgroup, event.fromdate, event.todate, event.subject, event.place, event.description "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "event.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from event inner join groups g on event.nervatype=g.id and g.groupvalue = '"+str(filter["nervatype"])+"'\
        inner join "+str(filter["nervatype"])+" nerv on event.ref_id = nerv.id and nerv.deleted=0 \
        left join groups eg on event.eventgroup=eg.id "
      where_str = " where event.deleted=0 "+where_str
      if orderby=="":
        orderby_str = " order by calnumber "
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
      if filter.has_key("nervatype")!=True:
        return "Error|Missing required parameter: nervatype"
      
      audit = self.ns.getObjectAudit(filter["nervatype"])
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: "+filter["nervatype"]
      
      nervanumber = self.getNumberName(filter["nervatype"])
      if nervanumber.startswith("Error")==False:
        fields_ = [{"nervatype":"g.groupvalue"}, {"refnumber":"nerv."+str(nervanumber)}, {"fieldname":"fv.fieldname"}, {"description":"df.description"},
                   {"fieldtype":"fg.groupvalue"}, {"value":"fv.value"}, {"notes":"fv.notes"}]
        select_str ="select @id, g.groupvalue as nervatype, nerv."+str(nervanumber)+" as refnumber, \
          fv.fieldname, df.description, fg.groupvalue as fieldtype, fv.value, fv.notes "
        from_str = "from fieldvalue fv \
          inner join deffield df on fv.fieldname=df.fieldname inner join groups fg on df.fieldtype=fg.id \
          inner join groups g on df.nervatype=g.id and g.groupvalue = '"+str(filter["nervatype"])+"' \
          inner join "+str(filter["nervatype"])+" nerv on fv.ref_id = nerv.id and nerv.deleted=0 "
        where_str = "where fv.deleted=0 "+where_str
        if orderby=="":
          orderby_str = " order by refnumber, fieldname "
        else:
          orderby_str = orderby
      elif filter["nervatype"]=="address" or filter["nervatype"]=="contact" or filter["nervatype"]=="link" or filter["nervatype"]=="log":
        fields_ = [{"nervatype":"g.groupvalue"}, {"refnumber":"fv.ref_id"}, {"fieldname":"fv.fieldname"}, {"description":"df.description"}, 
                   {"fieldtype":"fg.groupvalue"}, {"value":"fv.value"}, {"notes":"fv.notes"}]
        select_str ="select @id, g.groupvalue as nervatype, fv.ref_id as refnumber, fv.fieldname, df.description, fg.groupvalue as fieldtype, fv.value, fv.notes "
        from_str = "from fieldvalue fv inner join deffield df on fv.fieldname=df.fieldname inner join groups fg on df.fieldtype=fg.id \
          inner join groups g on df.nervatype=g.id and g.groupvalue = '"+str(filter["nervatype"])+"' "
        where_str = "where fv.deleted=0 "+where_str
        if orderby=="":
          orderby_str = " order by refnumber, fieldname "
        else:
          orderby_str = orderby
      elif filter["nervatype"]=="item" or filter["nervatype"]=="movement" or filter["nervatype"]=="payment":
        fields_ = [{"nervatype":"g.groupvalue"}, {"refnumber":"t.transnumber"}, {"fieldname":"fv.fieldname"}, {"description":"df.description"},
                   {"fieldtype":"fg.groupvalue"}, {"value":"fv.value"}, {"notes":"fv.notes"}]
        select_str ="select @id, g.groupvalue as nervatype, t.transnumber as refnumber, fv.fieldname, df.description, fg.groupvalue as fieldtype, fv.value, fv.notes "
        from_str = " from fieldvalue fv inner join deffield df on fv.fieldname=df.fieldname inner join groups fg on df.fieldtype=fg.id \
          inner join groups g on df.nervatype=g.id and g.groupvalue = '"+str(filter["nervatype"])+"' \
          inner join "+str(filter["nervatype"])+" i on fv.ref_id = i.id and i.deleted=0 \
          inner join trans t on i.trans_id=t.id and t.deleted=0 "
        where_str = " where fv.deleted=0 "+where_str
        if orderby=="":
          orderby_str = " order by refnumber, fieldname "
        else:
          orderby_str = orderby
      elif filter["nervatype"]=="price":
        fields_ = [{"nervatype":"g.groupvalue"}, {"refnumber":"p.partnumber"}, {"fieldname":"fv.fieldname"}, {"description":"df.description"},
                   {"fieldtype":"fg.groupvalue"}, {"value":"fv.value"}, {"notes":"fv.notes"}]
        select_str ="select @id, g.groupvalue as nervatype, p.partnumber as refnumber, fv.fieldname, df.description, fg.groupvalue as fieldtype, fv.value, fv.notes "
        from_str = " from fieldvalue fv inner join deffield df on fv.fieldname=df.fieldname inner join groups fg on df.fieldtype=fg.id \
          inner join groups g on df.nervatype=g.id and g.groupvalue = 'price' \
          inner join price pr on fv.ref_id = pr.id and pr.deleted=0 \
          inner join product p on pr.product_id=p.id and p.deleted=0 "
        where_str = " where fv.deleted=0 "+where_str
        if orderby=="":
          orderby_str = " order by refnumber, fieldname "
        else:
          orderby_str = orderby
      elif filter["nervatype"]=="setting":
        fields_ = [{"fieldname":"fv.fieldname"}, {"description":"df.description"}, {"fieldtype":"fg.groupvalue"}, {"value":"fv.value"}, {"notes":"fv.notes"}, 
                   {"visible":"df.visible"}, {"readonly":"df.readonly"}]
        select_str ="select @id, fv.fieldname, df.description, fg.groupvalue as fieldtype, fv.value, fv.notes, df.visible, df.readonly "
        from_str = " from fieldvalue fv inner join deffield df on fv.fieldname=df.fieldname inner join groups fg on df.fieldtype=fg.id \
          inner join groups g on df.nervatype=g.id and g.groupvalue = 'setting' "
        where_str = "where fv.deleted=0 "+where_str
        if orderby=="":
          orderby_str = " order by fieldname"
        else:
          orderby_str = orderby
      else:
        return "Error|Unknown nervatype. Valid values: customer, employee, event, formula, groups, place, product, project, tool, trans."
      
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
      
      audit = self.ns.getObjectAudit("setting")
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
      fields_ = [{"transnumber":"t.transnumber"}, {"rownumber":"rownumber"}, {"represent_rownumber":"rownumber"},
                 {"partnumber":"p.partnumber"}, {"unit":"item.unit"}, 
                 {"qty":"item.qty"}, {"fxprice":"item.fxprice"}, {"netamount":"item.netamount"}, {"discount":"item.discount"}, 
                 {"taxcode":"tx.taxcode"}, {"vatamount":"item.vatamount"}, {"amount":"item.amount"}, {"description":"item.description"}, 
                 {"deposit":"item.deposit"}, {"ownstock":"item.ownstock"}, {"actionprice":"item.actionprice"}]
      select_str ="select @id, t.transnumber, 1 as rownumber, item.id as represent_rownumber, p.partnumber, item.unit, item.qty, item.fxprice, item.netamount, \
        item.discount, tx.taxcode as taxcode, item.vatamount, item.amount, item.description, item.deposit, item.ownstock, item.actionprice "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "item.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = "from item inner join trans t on item.trans_id=t.id and t.deleted=0 inner join product p on item.product_id=p.id \
        inner join tax tx on item.tax_id=tx.id "
      where_str = " where item.deleted=0 "+where_str
      if self.ns.employee:
        where_str += " and t.transtype not in(select subtype from ui_audit \
          inner join groups nt on ui_audit.nervatype = nt.id and nt.groupvalue='trans' \
          inner join groups if on ui_audit.inputfilter = if.id and if.groupvalue='disabled' \
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
      
      data_audit = self.ns.getDataAudit()
      if data_audit=="usergroup":
        where_str += " and t.cruser_id in (select id from employee where usergroup = "+str(self.ns.employee.usergroup)+") "
      elif data_audit=="own":
        where_str += " and t.cruser_id = "+str(self.ns.employee.id)+" "
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="link":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "link"
      fld_value = "link"
      select_str ="select @id,"
      fields_ = []
      
      if filter.has_key("nervatype1")!=True:
        return "Error|Missing required parameter: nervatype1"
      if filter["nervatype1"] in("item","payment","movement"):
        nervanumber1 = "transnumber"
        inner_str1 = "inner join "+str(filter["nervatype1"])+" r1 on link.ref_id_1=r1.id and r1.deleted=0 \
          inner join trans nerv1 on r1.trans_id = nerv1.id and nerv1.deleted=0 "
        select_str +="g1.groupvalue as nervatype1, nerv1."+str(nervanumber1)+" as refnumber1, r1.id as represent_refnumber1, "
        fields_.extend([{"nervatype1":"g1.groupvalue"}, {"refnumber1":"nerv1."+str(nervanumber1)}, {"represent_refnumber1":"r1."+str(nervanumber1)}])
      elif filter["nervatype1"]=="groups":
        inner_str1 = "inner join groups nerv1 on link.ref_id_1=nerv1.id and nerv1.deleted=0"
        select_str +="g1.groupvalue as nervatype1, nerv1.groupvalue as refnumber1, nerv1.id as represent_refnumber1, "
        fields_.extend([{"nervatype1":"g1.groupvalue"}, {"refnumber1":"nerv1.groupvalue"}, {"represent_refnumber1":"nerv1.groupvalue"}])
      else:
        nervanumber1 = self.getNumberName(filter["nervatype1"])
        if nervanumber1.startswith("Error"):
          return nervanumber1
        inner_str1 = "inner join "+str(filter["nervatype1"])+" nerv1 on link.ref_id_1=nerv1.id and nerv1.deleted=0"
        select_str +="g1.groupvalue as nervatype1, nerv1."+str(nervanumber1)+" as refnumber1, nerv1.id as represent_refnumber1, "
        fields_.extend([{"nervatype1":"g1.groupvalue"}, {"refnumber1":"nerv1."+str(nervanumber1)}, {"represent_refnumber1":"nerv1."+str(nervanumber1)}])
      
      if filter.has_key("nervatype2")!=True:
        return "Error|Missing required parameter: nervatype2"
      if filter["nervatype2"] in("item","payment","movement"):
        nervanumber2 = "transnumber"
        inner_str2 = "inner join "+str(filter["nervatype2"])+" r2 on link.ref_id_2=r2.id and r2.deleted=0 \
          inner join trans nerv2 on r2.trans_id = nerv2.id and nerv2.deleted=0 "
        select_str +="g2.groupvalue as nervatype2, nerv2."+str(nervanumber2)+" as refnumber2, r2.id as represent_refnumber2, "
        fields_.extend([{"nervatype2":"g2.groupvalue"}, {"refnumber2":"nerv2."+str(nervanumber2)}, {"represent_refnumber2":"r2."+str(nervanumber2)}])
      elif filter["nervatype2"]=="groups":
        inner_str2 = "inner join groups nerv2 on link.ref_id_2=nerv2.id and nerv2.deleted=0"
        select_str +="g2.groupvalue as nervatype2, nerv2.groupvalue as refnumber2, nerv2.id as represent_refnumber2, "
        fields_.extend([{"nervatype2":"g2.groupvalue"}, {"refnumber2":"nerv2.groupvalue"}, {"represent_refnumber2":"nerv2.groupvalue"}])
      else:
        nervanumber2 = self.getNumberName(filter["nervatype2"])
        if nervanumber2.startswith("Error"):
          return nervanumber2
        inner_str2 = "inner join "+str(filter["nervatype2"])+" nerv2 on link.ref_id_2=nerv2.id and nerv2.deleted=0"
        select_str +="g2.groupvalue as nervatype2, nerv2."+str(nervanumber2)+" as refnumber2, nerv2.id as represent_refnumber2, "
        fields_.extend([{"nervatype2":"g2.groupvalue"}, {"refnumber2":"nerv2."+str(nervanumber2)}, {"represent_refnumber2":"nerv2."+str(nervanumber2)}])
      
      select_str +=" linktype "
      fields_.append({"linktype":"linktype"})
            
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "link.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from link inner join groups g1 on link.nervatype_1=g1.id "+inner_str1 \
          +" inner join groups g2 on link.nervatype_2=g2.id "+inner_str2+" "
      where_str = " where link.deleted=0 and nervatype1='"+str(filter["nervatype1"])+"' and nervatype2='"+str(filter["nervatype2"])+"' "+where_str
      if orderby=="":
        orderby_str = " order by refnumber1"
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
      
      audit = self.ns.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: setting"
      
      fld_value = "log"
      if filter.has_key("nervatype")!=True and filter.has_key("notype")!=True:
        return "Error|Missing required parameter: nervatype or notype"
      nervanumber=None
      if filter.has_key("nervatype"):
        nervanumber = self.getNumberName(filter["nervatype"])
        if nervanumber.startswith("Error"):
          return nervanumber
        fields_ = [{"nervatype":"g.groupvalue"}, {"refnumber":"nerv."+str(nervanumber)}, {"logstate":"lg.groupvalue"}, 
                 {"empnumber":"e.empnumber"}, {"crdate":"log.crdate"}]
        select_str ="select @id, g.groupvalue as nervatype, nerv."+str(nervanumber)+" as refnumber, lg.groupvalue as logstate, e.empnumber as empnumber, log.crdate "
        from_str = " from log inner join groups g on log.nervatype=g.id and g.groupvalue = '"+str(filter["nervatype"])+"' \
          inner join "+str(filter["nervatype"])+" nerv on log.ref_id=nerv.id inner join groups lg on log.logstate=lg.id \
          inner join employee e on log.employee_id = e.id "
        where_str = " where 1=1 "+where_str
        
      else:
        fields_ = [{"logstate":"lg.groupvalue"}, {"empnumber":"e.empnumber"}, {"crdate":"log.crdate"}]
        select_str ="select @id, lg.groupvalue as logstate, e.empnumber as empnumber, log.crdate "
        from_str = " from log inner join groups lg on log.logstate=lg.id \
          inner join employee e on log.employee_id = e.id "
        where_str = " where nervatype is null "+where_str
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
      fields_ = [{"transnumber":"t.transnumber"}, {"rownumber":"rownumber"}, {"represent_rownumber":"rownumber"},
                 {"movetype":"g.groupvalue"}, {"partnumber":"p.partnumber"}, 
                 {"serial":"tl.serial"}, {"planumber":"pl.planumber"}, {"shippingdate":"movement.shippingdate"}, {"qty":"movement.qty"}, {"notes":"movement.notes"}]
      select_str ="select @id, t.transnumber, 1 as rownumber, movement.id as represent_rownumber, g.groupvalue as movetype, p.partnumber, tl.serial, pl.planumber, movement.shippingdate, movement.qty, movement.notes "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "movement.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from movement inner join trans t on movement.trans_id=t.id inner join groups g on movement.movetype=g.id \
        left join product p on movement.product_id=p.id left join tool tl on movement.tool_id=tl.id left join place pl on movement.place_id = pl.id "
      where_str = " where movement.deleted=0 "+where_str
      if self.ns.employee:
        where_str += " and t.transtype not in(select subtype from ui_audit \
          inner join groups nt on ui_audit.nervatype = nt.id and nt.groupvalue='trans' \
          inner join groups if on ui_audit.inputfilter = if.id and if.groupvalue='disabled' \
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
      
      data_audit = self.ns.getDataAudit()
      if data_audit=="usergroup":
        where_str += " and t.cruser_id in (select id from employee where usergroup = "+str(self.ns.employee.usergroup)+") "
      elif data_audit=="own":
        where_str += " and t.cruser_id = "+str(self.ns.employee.id)+" "
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="numberdef":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "numberdef"
      
      audit = self.ns.getObjectAudit("setting")
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
      where_str = " where pattern.deleted=0 "+where_str
      if self.ns.employee:
        where_str += " and pattern.transtype not in(select subtype from ui_audit \
          inner join groups nt on ui_audit.nervatype = nt.id and nt.groupvalue='trans' \
          inner join groups if on ui_audit.inputfilter = if.id and if.groupvalue='disabled' \
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
      fields_ = [{"transnumber":"t.transnumber"}, {"rownumber":"rownumber"}, 
                 {"represent_rownumber":"rownumber"}, {"paiddate":"payment.paiddate"}, 
                 {"amount":"payment.amount"}, {"notes":"payment.notes"}]
      select_str ="select @id, t.transnumber, 1 as rownumber, payment.id as represent_rownumber, payment.paiddate, payment.amount, payment.notes "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "payment.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from payment inner join trans t on payment.trans_id=t.id "
      where_str = " where payment.deleted=0 "+where_str
      if orderby=="":
        orderby_str = " order by transnumber, id"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " payment.id")
      if self.ns.employee:
        where_str += " and t.transtype not in(select subtype from ui_audit \
          inner join groups nt on ui_audit.nervatype = nt.id and nt.groupvalue='trans' \
          inner join groups if on ui_audit.inputfilter = if.id and if.groupvalue='disabled' \
          where usergroup = "+str(self.ns.employee.usergroup)+") "
      orderby_str = orderby_str.replace(" id", " payment.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
      
      data_audit = self.ns.getDataAudit()
      if data_audit=="usergroup":
        where_str += " and t.cruser_id in (select id from employee where usergroup = "+str(self.ns.employee.usergroup)+") "
      elif data_audit=="own":
        where_str += " and t.cruser_id = "+str(self.ns.employee.id)+" "
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="place":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "place"
      
      audit = self.ns.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: setting"
      
      fld_value = "place"
      fields_ = [{"planumber":"place.planumber"}, {"placetype":"g.groupvalue"}, {"description":"place.description"}, {"ref_planumber":"pm.planumber"}, 
                 {"curr":"place.curr"}, {"storetype":"sg.groupvalue"}, {"defplace":"place.defplace"}, {"notes":"place.notes"}, {"inactive":"place.inactive"}]
      select_str ="select @id, place.planumber, g.groupvalue as  placetype, place.description, pm.planumber as ref_planumber, place.curr, sg.groupvalue as storetype, place.defplace, place.notes, place.inactive "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "place.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from place inner join groups g on place.placetype=g.id left join place pm on place.place_id=pm.id \
        left join groups sg on place.storetype=sg.id "
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
      
      audit = self.ns.getObjectAudit("price")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: price"
      
      fld_value = "price"
      fields_ = [{"partnumber":"p.partnumber"}, {"pricetype":"case when discount is null then 'price' else 'discount' end"}, {"validfrom":"price.validfrom"}, 
                 {"validto":"price.validto"}, {"curr":"price.curr"}, {"qty":"price.qty"}, {"pricevalue":"price.pricevalue"}, 
                 {"discount":"price.discount"}, {"calcmode":"g.groupvalue"}, {"vendorprice":"price.vendorprice"}]
      select_str ="select @id, p.partnumber, case when discount is null then 'price' else 'discount' end as pricetype, price.validfrom, price.validto, price.curr, \
        price.qty, price.pricevalue, price.discount, g.groupvalue as calcmode, price.vendorprice "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "price.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from price inner join product p on price.product_id=p.id inner join groups g on price.calcmode=g.id "
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
      
      audit = self.ns.getObjectAudit("product")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: product"
      
      fld_value = "product"
      fields_ = [{"partnumber":"product.partnumber"}, {"description":"product.description"}, {"protype":"g.groupvalue"}, {"unit":"product.unit"}, 
                 {"tax":"tax.taxcode"}, {"notes":"product.notes"}, {"webitem":"product.webitem"}, {"inactive":"product.inactive"}]
      select_str ="select @id, product.partnumber, product.description, g.groupvalue as protype, product.unit, tax.taxcode as tax, product.notes, product.webitem, product.inactive "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "product.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from product inner join groups g on product.protype=g.id inner join tax on product.tax_id=tax.id "
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
      
      audit = self.ns.getObjectAudit("project")
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
      from_str = " from project left join customer c on project.customer_id=c.id "
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
      
      audit = self.ns.getObjectAudit("setting")
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
      from_str = " from rate inner join groups g on rate.ratetype=g.id inner join place p on rate.place_id=p.id \
        left join groups rg on rategroup=rg.id "
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
      
      audit = self.ns.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: setting"
      
      fields = ["taxcode", "description", "rate", "inactive"]
      select_str ="select @id, taxcode, description, rate, inactive "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from tax "
      where_str = " where 1=1 "+where_str
      if orderby=="":
        orderby_str = " order by id"
      else:
        orderby_str = orderby
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="tool":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "tool"
      
      audit = self.ns.getObjectAudit("tool")
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
      fields_ = [{"transnumber":"trans.transnumber"}, {"transtype":"g.groupvalue"}, {"ref_transnumber":"trans.ref_transnumber"}, {"crdate":"trans.crdate"}, 
                 {"transdate":"trans.transdate"}, {"duedate":"trans.duedate"}, {"custnumber":"c.custnumber"}, {"empnumber":"e.empnumber"}, 
                 {"department":"dg.groupvalue"}, {"pronumber":"p.pronumber"}, {"planumber":"pl.planumber"}, {"paidtype":"pg.groupvalue"}, 
                 {"curr":"trans.curr"}, {"notax":"trans.notax"}, {"paid":"trans.paid"}, {"acrate":"trans.acrate"}, {"notes":"trans.notes"}, 
                 {"intnotes":"trans.intnotes"}, {"fnote":"trans.fnote"}, {"transtate":"sg.groupvalue"}, {"closed":"trans.closed"}]
      select_str ="select @id, trans.transnumber, g.groupvalue as transtype, trans.ref_transnumber, trans.crdate, trans.transdate, trans.duedate, c.custnumber, e.empnumber, \
        dg.groupvalue as department, p.pronumber, pl.planumber, pg.groupvalue as paidtype, trans.curr, trans.notax, trans.paid, trans.acrate, trans.notes, trans.intnotes, \
        trans.fnote, sg.groupvalue as transtate, trans.closed "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "trans.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from trans inner join groups g on trans.transtype=g.id left join customer c on trans.customer_id=c.id left join employee e on trans.employee_id=e.id \
        left join groups dg on trans.department=dg.id left join project p on trans.project_id = p.id left join place pl on trans.place_id=pl.id \
        left join groups pg on trans.paidtype=pg.id inner join groups sg on trans.transtate=sg.id "
      where_str = " where trans.deleted=0 "+where_str
      if self.ns.employee:
        where_str += " and trans.transtype not in(select subtype from ui_audit \
          inner join groups nt on ui_audit.nervatype = nt.id and nt.groupvalue='trans' \
          inner join groups if on ui_audit.inputfilter = if.id and if.groupvalue='disabled' \
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
      
      data_audit = self.ns.getDataAudit()
      if data_audit=="usergroup":
        where_str += " and trans.cruser_id in (select id from employee where usergroup = "+str(self.ns.employee.usergroup)+") "
      elif data_audit=="own":
        where_str += " and trans.cruser_id = "+str(self.ns.employee.id)+" "
  
  #--------------------------------------------------------------------------------------------------------------------------------------------    
    elif params["datatype"]=="setting":
  #--------------------------------------------------------------------------------------------------------------------------------------------
      item_str = "setting"
      
      audit = self.ns.getObjectAudit("setting")
      if audit=="error":
        return "Error|"+str(self.ns.error_message)
      if audit=="disabled":
        return "Error|Disabled type: setting"
      
      fields_ = [{"fieldname":"fieldvalue.fieldname"}, {"fieldtype":"fg.groupvalue"}, {"value":"fieldvalue.value"}, 
                 {"notes":"fieldvalue.notes"}, {"visible":"df.visible"}, {"readonly":"df.readonly"}]
      select_str ="select @id, fieldvalue.fieldname, fg.groupvalue as fieldtype, fieldvalue.value, fieldvalue.notes, df.visible, df.readonly "
      if filter.has_key("show_id"):
        fields.insert(0, "id")
        select_str = select_str.replace("@id,", "fieldvalue.id,")
      else:
        select_str = select_str.replace("@id,", "")
      from_str = " from fieldvalue inner join deffield df on fieldvalue.fieldname=df.fieldname inner join groups fg on df.fieldtype=fg.id \
        inner join groups g on df.nervatype=g.id and g.groupvalue = 'setting' "
      where_str = " where fieldvalue.deleted=0 "+where_str
      if orderby=="":
        orderby_str = " order by fieldname"
      else:
        orderby_str = orderby
      where_str = where_str.replace(" id", " fieldvalue.id")
      orderby_str = orderby_str.replace(" id", " fieldvalue.id")
      for field in fields_:
        where_str = where_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        orderby_str = orderby_str.replace(" "+field.keys()[0], " "+field.values()[0]).replace(","+field.keys()[0], ","+field.values()[0])
        fields.append(field.keys()[0])
                                                                                                                                          
  #--------------------------------------------------------------------------------------------------------------------------------------------        
    else:
      return "Error|Unknown datatype: "+params["datatype"]
  #--------------------------------------------------------------------------------------------------------------------------------------------        
    
    xml_query=""
    dfields={}
    if params["datatype"]!="sql":
      if fld_value!="":
        colname = "description"
        deffield_query = "select deffield.fieldname, deffield.description, groups.groupvalue as fieldtype from deffield inner join groups on deffield.fieldtype=groups.id \
          where deffield.deleted=0 and deffield.nervatype=(select id from groups where groupname='nervatype' and groupvalue='"+fld_value+"')"
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
              where_str = where_str.replace(fieldnames[idx][colname], "cast(lj_"+str(idx)+".value as integer)")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "cast(lj_"+str(idx)+".value as integer)")
          elif fieldnames[idx]["fieldtype"]=="customer":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join customer on cast(value as integer)=customer.id ").replace("@value", "customer.custnumber")
            else:
              fv_query += " left join customer rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as integer)=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".custname "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".custname")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".custname")
          elif fieldnames[idx]["fieldtype"]=="tool":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join tool on cast(value as integer)=tool.id ").replace("@value", "tool.serial")
            else:
              fv_query += " left join tool rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as integer)=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".serial "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".serial")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".serial")
          elif fieldnames[idx]["fieldtype"]in ('trans','transitem','transmovement','transpayment'):
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join trans on cast(value as integer)=trans.id ").replace("@value", "trans.transnumber")
            else:
              fv_query += " left join trans rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as integer)=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".transnumber "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".transnumber")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".transnumber")
          elif fieldnames[idx]["fieldtype"]=="product":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join product on cast(value as integer)=product.id ").replace("@value", "product.partnumber")
            else:
              fv_query += " left join product rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as integer)=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".partnumber "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".partnumber")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".partnumber")
          elif fieldnames[idx]["fieldtype"]=="project":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join project on cast(value as integer)=project.id ").replace("@value", "project.pronumber")
            else:
              fv_query += " left join project rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as integer)=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".pronumber "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".pronumber")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".pronumber")
          elif fieldnames[idx]["fieldtype"]=="employee":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join employee on cast(value as integer)=employee.id ").replace("@value", "employee.empnumber")
            else:
              fv_query += " left join employee rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as integer)=rlj_"+str(idx)+".id \n"
              select_str+=", rlj_"+str(idx)+".empnumber "
              where_str = where_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".empnumber")
              orderby_str = orderby_str.replace(fieldnames[idx][colname], "rlj_"+str(idx)+".empnumber")
          elif fieldnames[idx]["fieldtype"]=="place":
            if filter["output"].startswith("xml"):
              xml_query = xml_query.replace("@join_str", "inner join place on cast(value as integer)=place.id ").replace("@value", "place.planumber")
            else:
              fv_query += " left join place rlj_"+str(idx)+" on cast(lj_"+str(idx)+".value as integer)=rlj_"+str(idx)+".id \n"
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
    
    def get_refnumber(row, repkey):
      try:
        ref_id = row[fields.index(represents[repkey]["ref_id_field"])]
        if represents[repkey]["nervatype_field"]==None:
          nervatype = params["datatype"]
        else:
          nervatype = row[fields.index(represents[repkey]["nervatype_field"])]
        return self.ns.show_refnumber(represents[repkey]["rettype"],nervatype, ref_id)
      except Exception:
        return "Missing refnumber value"
    
    represents = {
      "represent_rownumber":{
          "label":"rownumber*", "rettype":"index", "ref_id_field":"represent_rownumber", 
          "nervatype_field":None, "function":get_refnumber, "replace_field":"rownumber"},
      "represent_refnumber1":{
          "label":"refnumber1", "rettype":"refnumber", "ref_id_field":"represent_refnumber1", 
          "nervatype_field":"nervatype1", "function":get_refnumber, "replace_field":"refnumber1"},
      "represent_refnumber2":{
          "label":"refnumber2", "rettype":"refnumber", "ref_id_field":"represent_refnumber2", 
          "nervatype_field":"nervatype2", "function":get_refnumber, "replace_field":"refnumber2"}
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
          for field in rep_cols.keys():
            items[row][rep_cols[field]] = represents[field]["function"](items[row],field)
          for del_col in del_cols:
            items[row].pop(del_col)
        for field in rep_cols.keys():
          if represents[field].has_key("label"):
            fields[rep_cols[field]] = represents[field]["label"]
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