# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import datetime
from StringIO import StringIO

from gluon.html import URL, INPUT, CAT, FORM, CENTER, HTML, TITLE, BODY, LINK, HEAD, H1
from gluon.sqlhtml import SQLFORM, DIV, SPAN, IMG, A, HTTP
from gluon.html import HR, SELECT, OPTION, XML
from gluon.html import TABLE, TR, TD, LABEL
from gluon.utils import web2py_uuid
from gluon.sql import Field
from gluon.validators import IS_IN_DB, IS_IN_SET
from gluon.storage import Storage
import gluon.contrib.simplejson as json

from nerva2py.simplegrid import SimpleGrid
from nerva2py.tools import NervaTools, DataOutput

class WebUiConnect(object):
  
  def __init__(self, ui):
    self.ui = ui
  
  def clear_post_vars(self):
    if self.ui.ns.request.post_vars["id"]=="-1":
      del self.ui.ns.request.post_vars["id"]
    if self.ui.ns.request.post_vars.has_key("_formname"):
      del self.ui.ns.request.post_vars["_formname"]
    if self.ui.ns.request.post_vars.has_key("_formkey"):
      del self.ui.ns.request.post_vars["_formkey"]
    if self.ui.ns.request.post_vars.has_key("keywords"):
      del self.ui.ns.request.post_vars["keywords"]
  
  def create_trans(self, base_id,transcast="normal",new_transtype=None,new_direction=None,from_inventory=False,netto_qty=False):
    
    new_id = -1
    base_trans = self.ui.ns.db.trans(id=base_id)
    base_transcast = self.ui.ns.db((self.ui.ns.db.fieldvalue.ref_id==base_id)&(self.ui.ns.db.fieldvalue.fieldname=="trans_transcast")).select()
    base_transcast = base_transcast[0].value if len(base_transcast)>0 else "normal"
    
    #set base data
    if new_transtype and new_direction:
      transtype = new_transtype
      transtype_audit_filter = self.ui.connect.get_audit_filter("trans", transtype)
      if transtype_audit_filter[0]=="disabled":
        return "err|"+str(new_id)+"|"+self.ui.ns.T("Disabled type: "+transtype)
      transtype_id = self.ui.ns.valid.get_groups_id("transtype", new_transtype)
      direction = new_direction
      direction_id = self.ui.ns.valid.get_groups_id("direction", new_direction)
    else:
      transtype = self.ui.ns.db.groups(id=base_trans.transtype).groupvalue
      transtype_id = base_trans.transtype
      direction = self.ui.ns.db.groups(id=base_trans.direction).groupvalue
      direction_id = base_trans.direction
      
    #to check some things...
    if base_transcast=="cancellation":
      return "err|"+str(new_id)+"|"+self.ui.ns.T("Canceling document does not make a copy!")
    if transcast=="cancellation" and base_trans.deleted==0 and transtype not in("delivery","inventory"):
      return "err|"+str(new_id)+"|"+self.ui.ns.T("Create cancellation document, but may have been deleted document!")
    if transcast=="amendment" and base_trans.deleted==1:
      return "err|"+str(new_id)+"|"+self.ui.ns.T("Deleted document does not make a copy!")
    
    nervatype_trans_id = self.ui.ns.valid.get_groups_id("nervatype", "trans")
    nervatype_groups_id = self.ui.ns.valid.get_groups_id("nervatype", "groups")
    nervatype_movement_id = self.ui.ns.valid.get_groups_id("nervatype", "movement")
    nervatype_item_id = self.ui.ns.valid.get_groups_id("nervatype", "item")
          
    nextnumber_id = transtype if transtype in("waybill","cash") else transtype+"_"+direction
    nextnumber = self.ui.ns.connect.nextNumber(nextnumber_id)
    
    duedate = datetime.datetime.strptime(str(datetime.date.today())+" 00:00:00", str('%Y-%m-%d %H:%M:%S'))
    if transtype=="invoice" and direction=="out":
      deadline=self.ui.ns.connect.getSetting("default_deadline")
      if deadline!="": duedate += datetime.timedelta(int(deadline))
    
    #creat trans data from the original          
    values = {"transtype":transtype_id,"transnumber":nextnumber,"ref_transnumber":base_trans.transnumber,"crdate":datetime.datetime.now().date(),
              "transdate":datetime.datetime.now().date(),"duedate":duedate,"customer_id":base_trans.customer_id,
              "employee_id":base_trans.employee_id,"department":base_trans.department,"project_id":base_trans.project_id,
              "place_id":base_trans.place_id,"paidtype":base_trans.paidtype,"curr":base_trans.curr,"notax":base_trans.notax,
              "paid":0,"acrate":base_trans.acrate,"notes":base_trans.notes,"intnotes":base_trans.intnotes,"fnote":base_trans.fnote,
              "transtate":self.ui.ns.valid.get_groups_id("transtate", "ok"),
              "closed":0,"deleted":0,"direction":direction_id,"cruser_id":self.ui.ns.session.auth.user.id}
    
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
    values["trans_transcast"]=transcast
    if transtype in("invoice"):
      self.ui.ns.valid.set_invoice_customer(values,base_trans.customer_id)
    new_id = self.ui.ns.connect.updateData("trans", values=values, validate=False, insert_row=True)
    
    #set a link for the old trans
    if not (transtype=="delivery" and direction!="transfer"):
      values = {"nervatype_1":nervatype_trans_id,"ref_id_1":new_id,"nervatype_2":nervatype_trans_id,"ref_id_2":base_trans.id,"linktype":linktype}
      self.ui.ns.connect.updateData("link", values=values, validate=False, insert_row=True)
    
    #link to the all trans groups
    glinks = self.ui.ns.db((self.ui.ns.db.link.ref_id_1==base_trans.id)&(self.ui.ns.db.link.nervatype_1==nervatype_trans_id)&(self.ui.ns.db.link.deleted==0)
                &(self.ui.ns.db.link.nervatype_2==nervatype_groups_id)).select(orderby=self.ui.ns.db.link.id)
    for glink in glinks:       
      values = {"nervatype_1":nervatype_trans_id, "ref_id_1":new_id, "nervatype_2":nervatype_groups_id, "ref_id_2":glink.ref_id_2}
      self.ui.ns.connect.updateData("link", values=values, validate=False, insert_row=True)
    
    #link and set the additional fields
    fields = self.ui.ns.db((self.ui.ns.db.fieldvalue.deleted==0)&(self.ui.ns.db.fieldvalue.fieldname==self.ui.ns.db.deffield.fieldname)&(self.ui.ns.db.deffield.deleted==0)
               &(self.ui.ns.db.deffield.visible==1)&(self.ui.ns.db.deffield.nervatype==nervatype_trans_id)&(self.ui.ns.db.fieldvalue.ref_id==base_trans.id)).select(self.ui.ns.db.fieldvalue.ALL,orderby=self.ui.ns.db.fieldvalue.id)
    for field in fields:
      values = {"fieldname":field.fieldname,"ref_id":new_id,"value":field.value,"notes":field.notes}
      self.ui.ns.connect.updateData("fieldvalue", values=values, validate=False, insert_row=True)
    
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
        item.vatamount = round(item.netamount*self.ui.ns.db.tax(id=item.tax_id).rate,digit);
        item.amount = item.netamount + item.vatamount;
        return item
      items=[]
      products={}
      transtype_invoice = self.ui.ns.valid.get_groups_id("transtype", "invoice")
      transtype_receipt = self.ui.ns.valid.get_groups_id("transtype", "receipt")
      invoice_items = self.ui.ns.db((self.ui.ns.db.link.ref_id_2==base_trans.id)&(self.ui.ns.db.link.nervatype_1==nervatype_trans_id)&(self.ui.ns.db.link.deleted==0)
              &(self.ui.ns.db.link.nervatype_2==nervatype_trans_id)&(self.ui.ns.db.link.ref_id_1==self.ui.ns.db.trans.id)&(self.ui.ns.db.trans.deleted==0)
              &((self.ui.ns.db.trans.transtype==transtype_invoice)|(self.ui.ns.db.trans.transtype==transtype_receipt))
              &(self.ui.ns.db.trans.id==self.ui.ns.db.item.trans_id)&(self.ui.ns.db.item.deleted==0)).select(self.ui.ns.db.item.ALL,orderby=self.ui.ns.db.item.id)
      base_digit = self.ui.ns.db.currency(curr=base_trans.curr).digit
              
      if from_inventory:
        #create from order,worksheet and rent, on base the delivery rows
        query = ((self.ui.ns.db.item.trans_id==base_trans.id)&(self.ui.ns.db.item.deleted==0)&
                 (self.ui.ns.db.link.nervatype_2==nervatype_item_id)&(self.ui.ns.db.link.ref_id_2==self.ui.ns.db.item.id)&
                 (self.ui.ns.db.item.product_id==self.ui.ns.db.product.id)&
                 (self.ui.ns.db.link.nervatype_1==nervatype_movement_id)&(self.ui.ns.db.link.ref_id_1==self.ui.ns.db.movement.id)
                 &(self.ui.ns.db.link.deleted==0)&(self.ui.ns.db.movement.deleted==0))
        groupfields=[self.ui.ns.db.item.id,self.ui.ns.db.movement.product_id,self.ui.ns.db.movement.qty.sum().with_alias('qty')]
        groupby=[self.ui.ns.db.item.id|self.ui.ns.db.movement.product_id]
        inventory_items = self.ui.ns.db(query).select(*groupfields,groupby=groupby,cacheable=True,orderby=self.ui.ns.db.item.id)
        base_direction = self.ui.ns.db.groups(id=base_trans.direction).groupvalue
        
        for inv_item in inventory_items:
          item = self.ui.ns.db.item(id=inv_item.item.id)
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
          base_items = self.ui.ns.db((self.ui.ns.db.item.trans_id==base_trans.id)&(self.ui.ns.db.item.deleted==0)
                                  ).select(orderby=self.ui.ns.db.item.id)
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
          items = self.ui.ns.db((self.ui.ns.db.item.trans_id==base_trans.id)&(self.ui.ns.db.item.deleted==0)
                             ).select(orderby=self.ui.ns.db.item.id).as_list(storage_to_dict=False)
      
      #put to deposit rows
      for item in invoice_items:
        if item.deposit==1:
          dqty = get_product_qty(invoice_items,item.product_id,True)
          if dqty!=0:
            item.qty = -dqty
            items.insert(0,item)
    else:
      items = self.ui.ns.db((self.ui.ns.db.item.trans_id==base_trans.id)&(self.ui.ns.db.item.deleted==0)).select(orderby=self.ui.ns.db.item.id)
      
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
      self.ui.ns.connect.updateData("item", values=dict(item), validate=False, insert_row=True)
      if transcast=="amendment":
        item.qty=-item.qty
        item.netamount=-item.netamount
        item.vatamount=-item.vatamount
        item.amount=-item.amount
        self.ui.ns.connect.updateData("item", values=dict(item), validate=False, insert_row=True)
        
    payments = self.ui.ns.db((self.ui.ns.db.payment.trans_id==base_trans.id)&(self.ui.ns.db.payment.deleted==0)
                          ).select(orderby=self.ui.ns.db.payment.id)
    for payment in payments:
      del payment.id
      del payment.update_record
      del payment.delete_record
      payment.trans_id = new_id
      if transcast=="cancellation": payment.amount = -payment.amount
      self.ui.ns.connect.updateData("payment", values=dict(payment), validate=False, insert_row=True)
    
    if transtype=="delivery" and direction=="transfer":
      movements = self.ui.ns.db((self.ui.ns.db.movement.id.belongs(self.ui.ns.db((self.ui.ns.db.link.ref_id_1.belongs(
                          self.ui.ns.db(self.ui.ns.db.movement.trans_id==base_trans.id).select(self.ui.ns.db.movement.id)))
                         &(self.ui.ns.db.link.nervatype_1==nervatype_movement_id)&(self.ui.ns.db.link.deleted==0)
                         &(self.ui.ns.db.link.nervatype_2==nervatype_movement_id)).select(self.ui.ns.db.link.ref_id_2.with_alias('id'))))
                    &(self.ui.ns.db.movement.deleted==0)&(self.ui.ns.db.movement.product_id==self.ui.ns.db.product.id)).select(self.ui.ns.db.movement.ALL,orderby=self.ui.ns.db.movement.id)
    else:
      movements = self.ui.ns.db((self.ui.ns.db.movement.trans_id==base_trans.id)&(self.ui.ns.db.movement.deleted==0)
                             ).select(orderby=self.ui.ns.db.movement.id)
    for movement in movements:
      if transtype=="delivery" and direction=="transfer":
        ilinks = self.ui.ns.db((self.ui.ns.db.link.ref_id_2==movement.id)&(self.ui.ns.db.link.nervatype_2==nervatype_movement_id)
                            &(self.ui.ns.db.link.deleted==0)
                &(self.ui.ns.db.link.nervatype_1==nervatype_movement_id)).select()
        del movement.id
        del movement.update_record
        del movement.delete_record
        movement.trans_id = new_id
        if transcast=="cancellation": movement.qty = -movement.qty
        movement_id_1 = self.ui.ns.connect.updateData("movement", values=dict(movement), validate=False, insert_row=True)
        movement_2 = self.ui.ns.db.movement(id=ilinks[0].ref_id_1)
        del movement_2.id
        del movement_2.update_record
        del movement_2.delete_record
        movement_2.trans_id = new_id
        if transcast=="cancellation": movement_2.qty = -movement_2.qty
        movement_id_2 = self.ui.ns.connect.updateData("movement", values=dict(movement_2), validate=False, insert_row=True)
        values = {"nervatype_2":nervatype_movement_id, "ref_id_2":movement_id_1, "nervatype_1":nervatype_movement_id, "ref_id_1":movement_id_2}
        self.ui.ns.connect.updateData("link", values=values, validate=False, insert_row=True)
      else:
        ilinks = self.ui.ns.db((self.ui.ns.db.link.ref_id_1==movement.id)&(self.ui.ns.db.link.nervatype_1==nervatype_movement_id)&(self.ui.ns.db.link.deleted==0)
                &(self.ui.ns.db.link.nervatype_2==nervatype_item_id)).select()
        del movement.id
        del movement.update_record
        del movement.delete_record
        movement.trans_id = new_id
        if transcast=="cancellation": movement.qty = -movement.qty
        movement_id = self.ui.ns.connect.updateData("movement", values=dict(movement), validate=False, insert_row=True)
        for ilink in ilinks:       
          values = {"nervatype_1":nervatype_movement_id, "ref_id_1":movement_id, "nervatype_2":nervatype_item_id, 
                    "ref_id_2":ilink.ref_id_2}
          self.ui.ns.connect.updateData("link", values=values, validate=False, insert_row=True)
    
    return "ok|"+str(new_id)+"|"  
      
  def get_audit_filter(self, nervatype, transtype=None):
    if not self.ui.ns.session.auth:
      return ("disabled",0)
    retvalue = ("all",1)
    nervatype_id = self.ui.ns.valid.get_groups_id("nervatype", nervatype)
    query = (self.ui.ns.db.ui_audit.usergroup==self.ui.ns.db.employee(id=self.ui.ns.session.auth.user.id).usergroup)&(self.ui.ns.db.ui_audit.nervatype==nervatype_id)
    if nervatype=="trans" and transtype!=None:
      transtype_id = self.ui.ns.valid.get_groups_id("transtype", transtype)
      query = query &(self.ui.ns.db.ui_audit.subtype==transtype_id)
    if nervatype=="menu" and transtype!=None:
      menu = self.ui.ns.db((self.ui.ns.db.ui_menu.menukey==transtype)).select()
      if len(menu)>0:
        query = query &(self.ui.ns.db.ui_audit.subtype==menu[0]["id"])
    audit = self.ui.ns.db(query).select().as_list()
    if len(audit)>0:
      inputfilter = self.ui.ns.valid.get_nervatype_name(audit[0]["inputfilter"])
      retvalue = (inputfilter,audit[0]["supervisor"])
    return retvalue
  
  def get_audit_subtype(self, subtype):
    #return disabled report/transtype list
    nervatype_id = self.ui.ns.valid.get_groups_id("nervatype", subtype)
    disabled_inputfilter_id = self.ui.ns.valid.get_groups_id("inputfilter", "disabled")
    return self.ui.ns.db((self.ui.ns.db.ui_audit.usergroup==self.ui.ns.db.employee(id=self.ui.ns.session.auth.user.id).usergroup)&(self.ui.ns.db.ui_audit.nervatype==nervatype_id)
          &(self.ui.ns.db.ui_audit.inputfilter==disabled_inputfilter_id)&(self.ui.ns.db.ui_audit.subtype!=None)).select(self.ui.ns.db.ui_audit.subtype.with_alias('id'))
    
  def get_formvalue(self, fieldname,table=None,ref_id=None,default="",isempty=True,key_field="id"):
    if self.ui.ns.request.post_vars.has_key(fieldname):
      return default if self.ui.ns.request.post_vars[fieldname]=="" and not isempty else self.ui.ns.request.post_vars[fieldname]
    else:
      if table and ref_id:
        if table == "fieldvalue":
          trow = self.ui.ns.db((self.ui.ns.db.fieldvalue.fieldname==fieldname) & (self.ui.ns.db.fieldvalue.ref_id==ref_id)).select()
        else:
          trow = self.ui.ns.db((self.ui.ns.db[table][key_field]==ref_id)).select()
        if len(trow)>0:
          return trow[0]["value"] if table == "fieldvalue" else trow[0][fieldname]
        else:
          return default
      else:
        return default
  
  def get_next_lnk(self, transtype, cur_id, direction):
    if cur_id==-1:
      return URL('frm_trans/new/trans/'+transtype+'/'+direction)
    
    transtype_id = self.ui.ns.valid.get_groups_id("transtype", transtype)
    direction_id = self.ui.ns.valid.get_groups_id("direction", direction)
    mid = self.ui.ns.db.trans.id.min()
    query = (self.ui.ns.db.trans.transtype==transtype_id)&(self.ui.ns.db.trans.id>cur_id)
    if transtype!="cash" and transtype!="waybill":
      query = query&(self.ui.ns.db.trans.direction==direction_id)
    if (transtype=="invoice" and direction=="out") or (transtype=="receipt" and direction=="out") or (transtype=="cash"):  
      pass
    else:
      query = query&(self.ui.ns.db.trans.deleted==0)
    
    #set transfilter
    query = self.ui.select.set_transfilter(query)
    
    mrow = self.ui.ns.db(query).select(mid)
    if mrow.first()[mid]==None:
      return URL('frm_trans/new/trans/'+transtype+'/'+direction)
    else:
      next_id = mrow.first()[mid]
      return URL('frm_trans/view/trans/'+str(next_id))
  
  def get_prev_lnk(self, transtype, cur_id, direction):
    transtype_id = self.ui.ns.valid.get_groups_id("transtype", transtype)
    direction_id = self.ui.ns.valid.get_groups_id("direction", direction)
    mid = self.ui.ns.db.trans.id.max()
    query = (self.ui.ns.db.trans.transtype==transtype_id)
    if transtype!="cash" and transtype!="waybill":
      query = query&(self.ui.ns.db.trans.direction==direction_id)
    if cur_id>-1:
      query = query&(self.ui.ns.db.trans.id<cur_id)
    if (transtype=="invoice" and direction=="out") or (transtype=="receipt" and direction=="out") or (transtype=="cash"):  
      pass
    else:
      query = query&(self.ui.ns.db.trans.deleted==0)
    
    #set transfilter
    query = self.ui.select.set_transfilter(query)
    
    mrow = self.ui.ns.db(query).select(mid)
    if mrow.first()[mid]==None:
      prev_id = cur_id
    else:
      prev_id = mrow.first()[mid]
    if prev_id==-1:
      return URL('frm_trans/new/trans/'+transtype+'/'+direction)
    else:
      return URL('frm_trans/view/trans/'+str(prev_id))
      
  def show_disabled(self,title):
    if self.ui.ns.session.mobile:
      return HTML(HEAD(TITLE(title),
                     LINK(_rel="shortcut icon", _href=URL('static','favicon.ico'), _type="image/x-icon")),
                BODY(DIV(CENTER(TABLE(TR(TD(IMG(_src=URL('static','images/dataprotection_min.jpg'),
                                        _style="border: solid;border-color: #FFFFFF;"),
                              _style="text-align: center;vertical-align: middle;font-weight: bold;font-family: Arial, Helvetica,  sans-serif;font-size: 20px;")),
                        _style="background-color:#FFFFFF;color:#444444;margin-top:30px;")),_style="width:100%;height:100%;")),_style="background-color:#879FB7;")
    else:
      return HTML(HEAD(TITLE(title),
                     LINK(_rel="shortcut icon", _href=URL('static','favicon.ico'), _type="image/x-icon")),
                BODY(DIV(CENTER(TABLE(TR(TD(IMG(_src=URL('static','images/dataprotection.jpg'),
                                        _style="border: solid;border-color: #FFFFFF;"),
                              _style="text-align: center;vertical-align: middle;font-weight: bold;font-family: Arial, Helvetica,  sans-serif;font-size: 20px;")),
                        _style="background-color:#FFFFFF;color:#444444;margin-top:200px;")),_style="width:100%;height:100%")),_style="background-color:#879FB7;")

  def update_fieldvalue(self, refid, fieldname, value=None, notes=None):
    values={"id":None,"fieldname":fieldname,"ref_id":refid,"value":value,"notes":notes}
    fieldvalue = self.ui.ns.db((self.ui.ns.db.fieldvalue.ref_id==refid)
                       &(self.ui.ns.db.fieldvalue.fieldname==fieldname)&(self.ui.ns.db.fieldvalue.deleted==0)).select()
    if len(fieldvalue)>0:
      values["id"]=fieldvalue[0]["id"]
    self.ui.ns.connect.updateData(nervatype="fieldvalue", values=values, validate=False, insert_row=True)
                    
class WebUiControl(object):
  
  def __init__(self, ui):
    self.ui = ui
  
  def format_value(self,ftype,value):
    try:
      if ftype=="integer":
        return DIV(self.ui.ns.valid.split_thousands(int(value)," ","."), _align="right", _width="100%")
      elif ftype=="number":
        return DIV(self.ui.ns.valid.split_thousands(float(value)," ","."), _align="right", _width="100%")
      elif ftype=="date":
        if type(value) is datetime.datetime:
          return DIV(value.date(), _align="center", _width="100%")
        elif type(value).__name__=="unicode":
          return DIV(datetime.datetime.strptime(str(value).split(" ")[0], str('%Y-%m-%d')).date(), _align="center", _width="100%")
        else:
          return value
      else:
        return value
    except Exception:
      return value
  
  def get_back_button(self, url):
    return A(SPAN(_class="icon leftarrow"), _style="height: 15px;", _class="w2p_trap buttontext button", 
             _title= self.ui.ns.T('Back'), _href=url)
  
  def get_bool_input(self, rid, table, fieldname):
    if rid==-1:
      value=self.ui.ns.db[table][fieldname].default
    else:
      value=self.ui.ns.db[table](id=rid)[fieldname]
    if value==1:
      return INPUT(_checked="checked",_class="boolean",_id=table+"_"+fieldname,_name=fieldname,_type="checkbox",_value="on")
    else:
      return INPUT(_class="boolean",_id=table+"_"+fieldname,_name=fieldname,_type="checkbox",_value="on")
  
  def get_bubble_label(self,label, count):
    return DIV(SPAN(label), XML("&nbsp;&nbsp;&nbsp;"), SPAN(str(count),_class="ctr_bubble"))
  
  def get_cmb_fields(self, nervatype):
    nervatype_fields = self.ui.ns.db((self.ui.ns.db.deffield.nervatype==nervatype)&(self.ui.ns.db.deffield.deleted==0)
                    &(self.ui.ns.db.deffield.visible==1)&(self.ui.ns.db.deffield.readonly==0)
                    ).select(orderby=self.ui.ns.db.deffield.description).as_list()
    cmb_fields = SELECT(*[OPTION(field["description"], _value=field["fieldname"]+"~"+
                                 str(self.ui.ns.db.groups(id=field["fieldtype"])["groupvalue"])+"~"+str(field["valuelist"])
                                 ) for field in nervatype_fields], _id="cmb_fields")
    cmb_fields.insert(0, OPTION("", _value=""))
    return cmb_fields
  
  def get_cmb_groups(self, groupname):
    groupname_groups = self.ui.ns.db((self.ui.ns.db.groups.groupname==groupname)&(self.ui.ns.db.groups.deleted==0)
                                  &(self.ui.ns.db.groups.inactive==0)).select(orderby=self.ui.ns.db.groups.groupvalue).as_list()
    cmb_groups = SELECT(*[OPTION(field["groupvalue"],_value=field["id"]) for field in groupname_groups], _id="cmb_groups")
    cmb_groups.insert(0, OPTION("", _value=""))
    return cmb_groups 
  
  def get_command_button(self, caption,title,color="444444",cmd="",_id="",_height="25px", _top="2px"):
    return INPUT(_type="button", _value=caption, _title=title, _id=_id,
                 _style="height: "+_height+" !important;padding-top: "+_top+" !important;color: #"+color+";", _onclick= cmd)
  
  def get_create_trans_button(self, trans_id,label="Create a new type"):
    cmd = self.get_popup_cmd(pop_id="popup_create_trans",label=label,theme="b",inline=False,mini=False, picon="direction")
    frm = self.ui.select.get_popup_form("popup_create_trans",label,self.ui.select.dlg_create_trans(trans_id))
    return DIV(cmd,frm)
  
  def get_disabled_label(self,value,value_id,div_id):
    if self.ui.ns.session.mobile:
      return DIV(SPAN(value, _id=value_id), _id=div_id, _class="label_disabled", _style="display:block;")
    else:
      return DIV(SPAN(value, _id=value_id), _id=div_id, _class="label_disabled",
                 _style="width: 100%;display:block;padding: 3px;height: 24px;padding-bottom: 0px;padding-top: 2px;")
  
  def get_goprop_button(self, title,url):
    return A(SPAN(_class="icon cog"), _style="padding: 0px;padding-left: 6px;padding-right: 3px;", 
      _class="w2p_trap buttontext button", _href=url, _title=title, 
      _onclick="javascript:if(confirm('"+self.ui.ns.T("Any unsaved changes will be lost. Do you want to continue?")
              +"')){window.location ='"+url+"';};return false;")
            
  def get_help_button(self,page):
    return A(IMG(_src=URL(self.ui.dir_images,'icon16_help.png')), _style="height: 15px;", _target="_blank",
      _class="w2p_trap buttontext button", _href=URL('cmd_go_help?page='+page), _title= self.ui.ns.T('Help'))
    
  def get_home_button(self):
    return A(SPAN(_class="icon home"), _style="height: 15px;padding-top:0px;padding-bottom:6px;", 
             _class="w2p_trap buttontext button", _title= self.ui.ns.T('Back'), _href=URL("index"))
  
  def get_icon_button(self, title,cmd_id,url="#",cmd="",icon="icon plus",label=""):
    return A(SPAN(_class=icon)+label, _id=cmd_id, _style="left: 3px; padding: 0px;padding-left: 6px;padding-right: 3px;", 
      _class="w2p_trap buttontext button", _href=url, _title=title, _onclick= cmd)
      
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
  
  def get_more_button(self, dv_id='dv_more',sp_id='sp_more',img_id='img_more',title_1='More...',title_2='Less...'
                      ,title_tool='More commands'):
    return A(IMG(_id=img_id,_style="vertical-align: top;padding-top: 2px;",_height="16px",_width="16px",
                 _src=URL(self.ui.dir_images,'control_down.png')), SPAN(title_1,_id=sp_id,_style="font-weight: bold;"),
                 _style="text-align:center; height: 19px;padding-top: 2px; padding-bottom: 2px;width: 100%;",
                 _class="w2p_trap buttontext button", _href="#", _title=title_tool,
                 _onclick="javascript:var tbl=document.getElementById('"+dv_id+"');var sp=document.getElementById('"+sp_id+"');\
                           var ig=document.getElementById('"+img_id+"'); if(tbl.style.display == 'none'){tbl.style.display = 'block';\
                           sp.innerHTML='"+title_2+"';ig.src='"+URL(self.ui.dir_images,'control_up.png')+"';} \
                           else {tbl.style.display = 'none';sp.innerHTML='"+title_1+"';ig.src='"+
                           URL(self.ui.dir_images,'control_down.png')+"';};")
  
  def get_new_button(self, url):
    return A(SPAN(_class="icon plus"), _style="height: 15px;padding-top:4px;padding-bottom:6px;", 
             _class="w2p_trap buttontext button", _title= self.ui.ns.T('New'), _href=url)
      
  def get_popup_cmd(self, pop_id,label,theme="b",inline=False,mini=False,onclick=None, picon="search"):
    cmd = A(label, _href="#"+pop_id)
    cmd["_data-rel"] = "popup"
    cmd["_data-position-to"] = "#appl_url"
    cmd["_data-role"] = "button"
    if inline: cmd["_data-inline"] = "true"
    cmd["_data-icon"] = "search"
    cmd["_iconpos"] = "notext"
    cmd["_data-theme"] = theme
    if mini: cmd["_data-mini"] = "true"
    cmd["_data-transition"] = "pop"
    if onclick: cmd["_onclick"] = onclick
    if picon: cmd["_data-icon"]=picon
    return cmd
  
  def get_report_button(self, nervatype,title,ref_id,label,transtype=None, direction=None):
    if self.ui.ns.session.mobile:
      cmd = self.get_popup_cmd(pop_id="popup_reports",label=self.ui.ns.T("Reports"),theme="b",inline=False,mini=False, picon="page")
      frm = self.ui.select.get_popup_form("popup_reports",title,self.ui.report.dlg_report(nervatype,transtype,direction,ref_id,label))
    else:
      cmd = INPUT(_type="button", _value=self.ui.ns.T("Reports"), _style="height: 25px !important;padding-top: 2px !important;color: #483D8B;width: 100%;", 
                _onclick='$("#popup_reports").dialog({dialogClass: "n2py-dialog", modal: true, minWidth: 440, resizable: false});')
      frm = DIV(self.ui.report.dlg_report(nervatype,transtype,direction,ref_id,label),
              _id="popup_reports", _title=title, _style="display: none;padding:10px;padding-top:0px;")
    return DIV(cmd,frm)
  
  def get_select_button(self, onclick,label="OK",title="Select Item"):
    cmd = A(SPAN(_class="ui-icon ui-icon-check ui-icon-shadow",))
    cmd["_href"] = "#"
    cmd["_data-role"] = "button"
    cmd["_class"] = "ui-btn-right ui-btn ui-shadow  ui-mini ui-btn-icon-left ui-btn-up-b"
    cmd["_title"] = title
    cmd["_style"] = "font-weight: bold;padding: 10px;text-decoration:none"
    cmd["_onclick"] = onclick
    cmd["_data-rel"] = "back"
    return cmd
  
  def get_tabedit_button(self, title,cmd_id,url="#",cmd=""):
    return A(SPAN(_class="icon pen"), _id=cmd_id, 
      _style="cursor: pointer; top:3px; text-align: center;padding: 2px;padding-left: 6px;padding-right: 3px;",
      _class="w2p_trap buttontext button", _href=url, _title=title, _onclick= cmd) 
  
  def get_tabnew_button(self, row_count,title,cmd_id,url="#",cmd=""):
    return A(SPAN(_class="icon plus")," ",str(row_count), _id=cmd_id, 
      _style="cursor: pointer; top:3px; text-align: center;padding: 2px;padding-left: 6px;padding-right: 3px;",
      _class="w2p_trap buttontext button", _href=url, _title=title, _onclick= cmd) 
      
  def get_total_button(self):
    return A(IMG(_id="img_total",_style="vertical-align: top;padding-top: 2px;",_height="16px",_width="16px",
                 _src=URL(self.ui.dir_images,'control_down.png')),
             IMG(_style="vertical-align: top;padding-top: 2px;",_height="16px",_width="16px",
                 _src=URL(self.ui.dir_images,'icon16_sum.png')), 
                 _style="text-align:center; height: 19px;padding-top: 2px; padding-bottom: 2px;width: 30px;",
                 _class="w2p_trap buttontext button", _href="#", _title="Quick Total",
                 _onclick="var tbl=document.getElementById('dv_total');\
                           var ig=document.getElementById('img_total'); if(tbl.style.display == 'none'){tbl.style.display = 'block';\
                           ig.src='"+URL(self.ui.dir_images,'control_up.png')+"';} \
                           else {tbl.style.display = 'none';ig.src='"+URL(self.ui.dir_images,'control_down.png')+"';};")                             
            
  def set_htmltable_style(self, table, tbl_id=None, priority="0", columntoggle=True):
    table["_data-role"] = "table"
    if tbl_id:
      table["_id"] = tbl_id
    table["_class"] = "ui-body-d ui-shadow table-stripe ui-responsive"
    table["_data-column-btn-theme"] = "a"
    table["_width"] = "100%"
    if columntoggle:
      table["_data-mode"] = "columntoggle"
      table["_data-column-btn-text"] = self.ui.ns.T("Columns to display...")
      table["_data-column-popup-theme"] = "a"
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
    for i in range(len(head)):
      if len(head[i])>0:
        try:
          str(priority).split(",").index(str(i))
          head[i]["_data-priority"] = "critical"
        except Exception:
          head[i]["_data-priority"] = "6"
                
class WebUiSelector(object):
  
  def __init__(self, ui):
    self.ui = ui
  
  def create_filter_form(self,sfilter_name,state_fields=None,bool_fields=None,date_fields=None,number_fields=None,
                         data_fields=None,quick_total=None,more_data=None):
    
    if self.ui.ns.session.mobile:
      self.ui.response.cmd_help = self.ui.control.get_mobil_button(label=self.ui.ns.T("HELP"), href=URL('cmd_go_help?page=browser'),
                                           cformat="ui-btn-left", icon="info", iconpos="left", target="blank")
    else:
      self.ui.response.cmd_help = self.ui.control.get_help_button("browser")
    if sfilter_name not in("transitem_trans_filter","payment_payment_filter","payment_invoice_filter",
                           "movement_inventory_filter","movement_product_filter","movement_formula_filter"):
      self.init_sfilter(sfilter_name)
        
    filter_fields=[]
    if state_fields:
      if str(state_fields).find("nervatype")>-1:
        filter_fields.append(Field('nervatype', "string", label=self.ui.ns.T('Ref.type'), default = self.ui.ns.session[sfilter_name].get("nervatype"),
             requires = IS_IN_DB(self.ui.ns.db(self.ui.ns.db.groups.groupname.like('nervatype')), self.ui.ns.db.groups.id, '%(groupvalue)s')))
        
      if str(state_fields).find("transtype")>-1:
        filter_fields.append(Field('transtype', "string", label=self.ui.ns.T('Doc.Type'), default = self.ui.ns.session[sfilter_name].get("transtype"),
             requires = IS_IN_DB(self.ui.ns.db(self.ui.ns.db.groups.groupname.like('transtype')
             &self.ui.ns.db.groups.groupvalue.belongs(("offer","order","worksheet","rent","invoice","receipt"))), 
             self.ui.ns.db.groups.id, '%(groupvalue)s')))
      
      if str(state_fields).find("paymtype")>-1:
        filter_fields.append(Field('transtype', "string", label=self.ui.ns.T('Doc.Type'), default = self.ui.ns.session[sfilter_name].get("transtype"),
             requires = IS_IN_DB(self.ui.ns.db(self.ui.ns.db.groups.groupname.like('transtype')
             &self.ui.ns.db.groups.groupvalue.belongs(("cash","bank"))), 
             self.ui.ns.db.groups.id, '%(groupvalue)s')))
        
      if str(state_fields).find("direction")>-1:
        filter_fields.append(Field('direction', "string", label=self.ui.ns.T('Direction'), default = self.ui.ns.session[sfilter_name].get("direction"),
             requires = IS_IN_DB(self.ui.ns.db(self.ui.ns.db.groups.groupname.like('direction')), self.ui.ns.db.groups.id, '%(groupvalue)s')))
      
      if str(state_fields).find("transtate")>-1:
        filter_fields.append(Field('transtate', "string", label=self.ui.ns.T('State'), default = self.ui.ns.session[sfilter_name].get("transtate"),
             requires = IS_IN_DB(self.ui.ns.db(self.ui.ns.db.groups.groupname.like('transtate')), self.ui.ns.db.groups.id, '%(groupvalue)s')))
      
      if str(state_fields).find("transcast")>-1:
        transcast = str(self.ui.ns.db.deffield(fieldname="trans_transcast").valuelist).split("|")
        transcast_label=[]
        for value in transcast:
          transcast_label.append(self.ui.ns.T(value))
        filter_fields.append(Field('transcast', "string", label=self.ui.ns.T('Doc.State'), default = self.ui.ns.session[sfilter_name].get("transcast"),
             requires = IS_IN_SET(transcast_label,transcast)))
        
      if str(state_fields).find("logstate")>-1:
        filter_fields.append(Field('logstate', "string", label=self.ui.ns.T('Log State'), default = self.ui.ns.session[sfilter_name].get("logstate"),
             requires = IS_IN_DB(self.ui.ns.db(self.ui.ns.db.groups.groupname.like('logstate')), self.ui.ns.db.groups.id, '%(groupvalue)s')))
        
      if str(state_fields).find("ratetype")>-1:
        filter_fields.append(Field('ratetype', "string", label=self.ui.ns.T('Rate Type'), default = self.ui.ns.session[sfilter_name].get("ratetype"),
             requires = IS_IN_DB(self.ui.ns.db(self.ui.ns.db.groups.groupname.like('ratetype')), self.ui.ns.db.groups.id, '%(groupvalue)s')))
      
      if str(state_fields).find("pricetype")>-1:
        filter_fields.append(Field('pricetype', "string", label=self.ui.ns.T('Price type'), default = self.ui.ns.session[sfilter_name].get("pricetype"),
             requires = IS_IN_SET(("list","customer","group"),(self.ui.ns.T("List"),self.ui.ns.T("Customer"),self.ui.ns.T("Group")))))
      
      if str(state_fields).find("headtype")>-1:
        filter_fields.append(Field('headtype', "string", label=self.ui.ns.T('Type'), default = self.ui.ns.session[sfilter_name].get("headtype"),
             requires = IS_IN_SET(("head","plan"),(self.ui.ns.T("in"),self.ui.ns.T("out")))))
        
      if str(state_fields).find("invtype")>-1:
        filter_fields.append(Field('invtype', "string", label=self.ui.ns.T('Doc.type'), default = self.ui.ns.session[sfilter_name].get("invtype"),
             requires = IS_IN_SET(("delivery","inventory","production"),(self.ui.ns.T("delivery"),self.ui.ns.T("inventory"),self.ui.ns.T("production")))))
        
    if bool_fields:
      filter_fields.append(Field('bool_filter_name', "string", default = self.ui.ns.session[sfilter_name].get("bool_filter_name"), 
                requires = IS_IN_SET(bool_fields["bool_fields_name"], bool_fields["bool_fields_label"])))
      filter_fields.append(Field('bool_filter_value', "boolean", default = self.ui.ns.session[sfilter_name].get("bool_filter_value")))
    
    if date_fields:
      for i in range(3):
        filter_fields.append(Field('date_filter_name_'+str(i+1), "string", default = self.ui.ns.session[sfilter_name].get("date_filter_name_"+str(i+1)), label=self.ui.ns.T("Date"),
              requires = IS_IN_SET(date_fields["date_fields_name"], date_fields["date_fields_label"])))
        filter_fields.append(Field('date_filter_rel_'+str(i+1), "string", default = self.ui.ns.session[sfilter_name].get("date_filter_rel_"+str(i+1)),
                requires = IS_IN_SET(["!=",">",">=","<","<="],zero="=")))
        if self.ui.ns.session[sfilter_name].has_key("date_filter_value_"+str(i+1)):
          filter_fields.append(Field('date_filter_value_'+str(i+1), "date", default = self.ui.ns.session[sfilter_name].get("date_filter_value_"+str(i+1))))
        else:
          filter_fields.append(Field('date_filter_value_'+str(i+1), "date", default = datetime.datetime.now().date()))
    
    if number_fields:
      for i in range(3):
        filter_fields.append(Field('number_filter_name_'+str(i+1), "string", default = self.ui.ns.session[sfilter_name].get("number_filter_name_"+str(i+1)), label=self.ui.ns.T("Amount"),
              requires = IS_IN_SET(number_fields["number_fields_name"], number_fields["number_fields_label"])))
        filter_fields.append(Field('number_filter_rel_'+str(i+1), "string", default = self.ui.ns.session[sfilter_name].get("number_filter_rel_"+str(i+1)),
                requires = IS_IN_SET(["!=",">",">=","<","<="],zero="=")))
        if str(self.ui.ns.session[sfilter_name].get("number_filter_value_"+str(i+1)))=="":
          self.ui.ns.session[sfilter_name]["number_filter_value_"+str(i+1)]="0"
        filter_fields.append(Field('number_filter_value_'+str(i+1), "double", default = self.ui.ns.session[sfilter_name].get("number_filter_value_"+str(i+1))))
    
    if data_fields:
      for i in range(3):
        filter_fields.append(Field('data_filter_name_'+str(i+1), "string", default = self.ui.ns.session[sfilter_name].get("data_filter_name_"+str(i+1)), label=self.ui.ns.T("Data"),
              requires = IS_IN_SET(data_fields["data_fields_name"], data_fields["data_fields_label"])))
        filter_fields.append(Field('data_filter_rel_'+str(i+1), "string", default = self.ui.ns.session[sfilter_name].get("data_filter_rel_"+str(i+1)),
                requires = IS_IN_SET(("~like","startswith","~startswith","contains","~contains"),
                                     ["not like",self.ui.ns.T("starts with"),self.ui.ns.T("not starts with"),self.ui.ns.T("contains"),self.ui.ns.T("not contains")],zero=self.ui.ns.T("like"))))
        filter_fields.append(Field('data_filter_value_'+str(i+1), "string", default = self.ui.ns.session[sfilter_name].get("data_filter_value_"+str(i+1))))
    
    filter_form = SQLFORM.factory(*filter_fields,submit_button=self.ui.ns.T("Filter"), table_name="filter", _id="frm_filter")
    filter_div = DIV(_id="filter_div", _style="display: block;")
    filter_div.append(filter_form.custom.begin)
    ruri = str(self.ui.ns.request.wsgi.environ["REQUEST_URI"]).split("?")[0]+"?remove_filter"
    if self.ui.ns.session.mobile:
      if len(self.ui.ns.session[sfilter_name])>0:
        self.ui.response.sfilter_label = DIV(SPAN(self.ui.ns.T('FILTERED')),
          _style="background-color: #FFFFFF;color: #008B00;border-style: solid;border-width: 2px;text-align: center;font-weight: bold;padding-top: 0px;padding-bottom: 0px;")
      else:
        self.ui.response.sfilter_label = ""
      self.ui.response.cmd_filter = self.ui.control.get_mobil_button(cmd_id="cmd_filter",
          label=self.ui.ns.T("Filter & Search"), href="#", 
          cformat=None, style="text-align: left;color:#00FF00;", icon="search", ajax="false", theme="b",
          onclick= "document.forms['frm_filter'].submit();")
      self.ui.response.cmd_clear_filter = self.ui.control.get_mobil_button(self.ui.ns.T("Clear Filter"),title=self.ui.ns.T("Remove all query filter"), href="#", 
          cformat=None, icon="delete", style="text-align: left;color: #FF6347;",
          onclick="if(confirm('"+self.ui.ns.T('Are you sure you want to remove all filter?')+
            "')){window.location ='"+ruri+"';};return false;", theme="b", ajax="false")
      
      if more_data:
        self.ui.response.cmd_more_data = self.ui.control.get_mobil_button(more_data["caption"],title=more_data["title"], href=more_data["url"], 
                              cformat=None, icon="info", style="text-align: left;", theme="b", ajax="false")
      
      if state_fields or bool_fields:
        filter_table = TABLE(_style="width: auto;min-width: 200px;background-color: #DBDBDB;padding:8px;",_cellpadding="5px;", _cellspacing="0px;")
        
        if str(state_fields).find("nervatype")>-1:
          filter_table.append(TR(
                         TD(filter_form.custom.label.nervatype),
                         TD(filter_form.custom.widget.nervatype)))
          
        if str(state_fields).find("transtype")>-1 or str(state_fields).find("paymtype")>-1:
          filter_table.append(TR(
                         TD(filter_form.custom.label.transtype),
                         TD(filter_form.custom.widget.transtype)))
          
        if str(state_fields).find("direction")>-1:
          filter_table.append(TR(
                         TD(filter_form.custom.label.direction),
                         TD(filter_form.custom.widget.direction)))
        
        if str(state_fields).find("pricetype")>-1:
          filter_table.append(TR(
                         TD(filter_form.custom.label.pricetype),
                         TD(filter_form.custom.widget.pricetype)))
        
        if str(state_fields).find("headtype")>-1:
          filter_table.append(TR(
                         TD(filter_form.custom.label.headtype),
                         TD(filter_form.custom.widget.headtype)))
          
        if str(state_fields).find("invtype")>-1:
          filter_table.append(TR(
                         TD(filter_form.custom.label.invtype),
                         TD(filter_form.custom.widget.invtype)))
          
        if str(state_fields).find("logstate")>-1:
          filter_table.append(TR(
                         TD(filter_form.custom.label.logstate),
                         TD(filter_form.custom.widget.logstate)))
          
        if str(state_fields).find("ratetype")>-1:
          filter_table.append(TR(
                         TD(filter_form.custom.label.ratetype),
                         TD(filter_form.custom.widget.ratetype)))
        
        if str(state_fields).find("transtate")>-1:
          filter_table.append(TR(TD(filter_form.custom.widget.transtate,_colspan="2")))
        
        if str(state_fields).find("transcast")>-1:
          filter_table.append(TR(TD(filter_form.custom.widget.transcast,_colspan="2")))
          
        if bool_fields:
          filter_table.append(TR(
                         TD(filter_form.custom.widget.bool_filter_name),
                         TD(filter_form.custom.widget.bool_filter_value)))
        filter_div.append(DIV(filter_table,_id="dv_type",_name="divs",_style="display: none;"))
        self.ui.response.cmd_filter_type = self.ui.control.get_popup_cmd(pop_id="pop_filter",label=self.ui.ns.T("Type & State"),theme="e",inline=False,mini=False,
                                                 onclick="show_div('dv_type','"+self.ui.ns.T("Type & State")+"');", picon="gear")
      
      if date_fields:    
        filter_table = TABLE(_style="width: 100%;background-color: #DBDBDB;padding:8px;",_cellpadding="5px;", _cellspacing="0px;")
        filter_table.append(TR(
                         TD(filter_form.custom.widget.date_filter_name_1,_colspan="2")))
        filter_table.append(TR(TD(filter_form.custom.widget.date_filter_rel_1,_style="width: 40px;"),
                         TD(filter_form.custom.widget.date_filter_value_1)))
        filter_table.append(TR(
                         TD(HR(_style="margin: 0px;"),_colspan="2")))
        filter_table.append(TR(
                         TD(filter_form.custom.widget.date_filter_name_2,_colspan="2")))
        filter_table.append(TR(TD(filter_form.custom.widget.date_filter_rel_2,_style="width: 40px;"),
                         TD(filter_form.custom.widget.date_filter_value_2)))
        filter_table.append(TR(
                         TD(HR(_style="margin: 0px;"),_colspan="2")))
        filter_table.append(TR(
                         TD(filter_form.custom.widget.date_filter_name_3,_colspan="2")))
        filter_table.append(TR(TD(filter_form.custom.widget.date_filter_rel_3,_style="width: 40px;"),
                         TD(filter_form.custom.widget.date_filter_value_3)))
        filter_div.append(DIV(filter_table,_id="dv_date",_name="divs",_style="display: none;"))
        self.ui.response.cmd_filter_date = self.ui.control.get_popup_cmd(pop_id="pop_filter",label=self.ui.ns.T("Date filters"),theme="e",inline=False,mini=False,
                                                 onclick="show_div('dv_date','"+self.ui.ns.T("Date filters")+"');", picon="gear")
      
      if number_fields:    
        filter_table = TABLE(_style="width: auto;background-color: #DBDBDB;padding:8px;",_cellpadding="5px;", _cellspacing="0px;")
        filter_table.append(TR(
                         TD(filter_form.custom.widget.number_filter_name_1,_colspan="2")))
        filter_table.append(TR(TD(filter_form.custom.widget.number_filter_rel_1,_style="width: 40px;"),
                         TD(filter_form.custom.widget.number_filter_value_1)))
        filter_table.append(TR(
                         TD(HR(_style="margin: 0px;"),_colspan="2")))
        filter_table.append(TR(
                         TD(filter_form.custom.widget.number_filter_name_2,_colspan="2")))
        filter_table.append(TR(TD(filter_form.custom.widget.number_filter_rel_2,_style="width: 40px;"),
                         TD(filter_form.custom.widget.number_filter_value_2)))
        filter_table.append(TR(
                         TD(HR(_style="margin: 0px;"),_colspan="2")))
        filter_table.append(TR(
                         TD(filter_form.custom.widget.number_filter_name_3,_colspan="2")))
        filter_table.append(TR(TD(filter_form.custom.widget.number_filter_rel_3,_style="width: 40px;"),
                         TD(filter_form.custom.widget.number_filter_value_3)))
        filter_div.append(DIV(filter_table,_id="dv_number",_name="divs",_style="display: none;"))
        self.ui.response.cmd_filter_number = self.ui.control.get_popup_cmd(pop_id="pop_filter",label=self.ui.ns.T("Amount filters"),theme="e",inline=False,mini=False,
                                                   onclick="show_div('dv_number','"+self.ui.ns.T("Amount filters")+"');", picon="gear")
        
      if data_fields:
        filter_table = TABLE(_style="width: auto;background-color: #DBDBDB;padding:8px;",_cellpadding="5px;", _cellspacing="0px;")
        filter_table.append(TR(TD(filter_form.custom.widget.data_filter_name_1)))
        filter_table.append(TR(TD(filter_form.custom.widget.data_filter_rel_1)))
        filter_table.append(TR(TD(filter_form.custom.widget.data_filter_value_1)))
        filter_table.append(TR(TD(HR(_style="margin: 0px;"))))
        filter_table.append(TR(TD(filter_form.custom.widget.data_filter_name_2)))
        filter_table.append(TR(TD(filter_form.custom.widget.data_filter_rel_2)))
        filter_table.append(TR(TD(filter_form.custom.widget.data_filter_value_2)))
        filter_table.append(TR(TD(HR(_style="margin: 0px;"))))
        filter_table.append(TR(TD(filter_form.custom.widget.data_filter_name_3)))
        filter_table.append(TR(TD(filter_form.custom.widget.data_filter_rel_3)))
        filter_table.append(TR(TD(filter_form.custom.widget.data_filter_value_3)))
        filter_div.append(DIV(filter_table,_id="dv_data",_name="divs",_style="display: none;"))
        self.ui.response.cmd_filter_data = self.ui.control.get_popup_cmd(pop_id="pop_filter",label=self.ui.ns.T("Other data filters"),theme="e",inline=False,mini=False,
                                                 onclick="show_div('dv_data','"+self.ui.ns.T("Other data")+"');", picon="gear")
      
      if quick_total:
        filter_table = TABLE(_style="width: 100%;background-color: #DBDBDB;padding:8px;",_cellpadding="5px;", _cellspacing="0px;")
        if quick_total.has_key("netamount"):
          label=TD(DIV(self.ui.ns.T("Netamount"), _class="label"))
          if quick_total["netamount"]:
            amount = TD(DIV(SPAN(self.ui.ns.valid.split_thousands(float(quick_total["netamount"])," ",".")), _class="label_disabled", _style="text-align: right;width: 150px;"))
          else:
            amount = TD(DIV(SPAN("0"), _class="label_disabled", _style="text-align: right;width: 150px;"))
          filter_table.append(TR(label,amount))
        if quick_total.has_key("vatamount"):
          label=TD(DIV(self.ui.ns.T("VAT"), _class="label"))
          if quick_total["vatamount"]:
            amount = TD(DIV(SPAN(self.ui.ns.valid.split_thousands(float(quick_total["vatamount"])," ",".")), _class="label_disabled", _style="text-align: right;width: 150px;"))
          else:
            amount = TD(DIV(SPAN("0"), _class="label_disabled", _style="text-align: right;width: 150px;"))
          filter_table.append(TR(label,amount))
        if quick_total.has_key("amount"):
          label=TD(DIV(self.ui.ns.T("Amount"), _class="label"))
          if quick_total["amount"]:
            amount = TD(DIV(SPAN(self.ui.ns.valid.split_thousands(float(quick_total["amount"])," ",".")), _class="label_disabled", _style="text-align: right;width: 150px;"))
          else:
            amount = TD(DIV(SPAN("0"), _class="label_disabled", _style="text-align: right;width: 150px;"))
          filter_table.append(TR(label,amount))
        if quick_total.has_key("qty"):
          label=TD(DIV(self.ui.ns.T("Qty"), _class="label"))
          if quick_total["qty"]:
            amount = TD(DIV(SPAN(self.ui.ns.valid.split_thousands(float(quick_total["qty"])," ",".")), _class="label_disabled", _style="text-align: right;width: 150px;"))
          else:
            amount = TD(DIV(SPAN("0"), _class="label_disabled", _style="text-align: right;width: 150px;"))
          filter_table.append(TR(label,amount))
        filter_div.append(DIV(filter_table,_id="dv_total",_name="divs",_style="display: none;"))
        self.ui.response.cmd_filter_total = self.ui.control.get_popup_cmd(pop_id="pop_filter",label=self.ui.ns.T("Quick Total"),theme="e",inline=False,mini=False,
                                                 onclick="show_div('dv_total','"+self.ui.ns.T("Quick Total")+"');", picon="info")
      
      filter_div.append(filter_form.custom.end)
      return self.get_popup_form("pop_filter",self.ui.ns.T("Set filters"),filter_div)
    else:                        
      if len(self.ui.ns.session[sfilter_name])>0:
        sfilter_label = DIV(SPAN(self.ui.ns.T('FILTERED')),_style="background-color: #D9D9D9;color: #008B00;border-style: solid;border-width: 2px;text-align: center;font-weight: bold;padding-top: 0px;padding-bottom: 0px;")
      else:
        sfilter_label = ""
      filter_table = TABLE(_style="width: 100%;border-style: solid;border-width: 1px;border-color: #CCCCCC;border-top: none;")
      head_row = TR()
      head_row.append(TD(filter_form.custom.submit, _style="width: 100px;padding-top: 10px;padding-bottom: 6px;padding-left: 10px;padding-right: 5px;"))
      head_row.append(TD(self.ui.control.get_command_button(caption=self.ui.ns.T("Clear Filter"),title=self.ui.ns.T("Remove all query filter"),color="A52A2A",
                                  cmd="if(confirm('"+self.ui.ns.T('Are you sure you want to remove all filter?')+
                                  "')){window.location ='"+ruri+"';};return false;"),
                                _style="width: 100px;padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 30px;"))
      if more_data:
        head_row.append(TD(self.ui.control.get_command_button(caption=more_data["caption"],title=more_data["title"],color="483D8B",
                                  cmd="window.location ='"+more_data["url"]+"';"),
                           _style="width: 130px;padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 30px;"))
        head_row.append(TD(sfilter_label,_style="width: 10px;padding-top: 10px;padding-bottom: 5px;padding-left: 5px;padding-right: 30px;"))
      else:
        head_row.append(TD(sfilter_label,_style="width: 100px;padding-top: 10px;padding-bottom: 5px;padding-left: 5px;padding-right: 30px;"))
      if state_fields or bool_fields:
        head_row.append(TD(self.ui.control.get_more_button(dv_id='dv_type',sp_id='sp_type',img_id='img_type',title_1=self.ui.ns.T('Type and State'),title_2=self.ui.ns.T('Type and State'),title_tool=self.ui.ns.T('Type and State filters')),
                                _style="width: 80px;padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 30px;"))
      if date_fields:
        head_row.append(TD(self.ui.control.get_more_button(dv_id='dv_date',sp_id='sp_date',img_id='img_date',title_1=self.ui.ns.T('Date'),title_2=self.ui.ns.T('Date'),title_tool=self.ui.ns.T('Date filters')),
                                _style="width: 80px;padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 30px;"))
      if number_fields:
        head_row.append(TD(self.ui.control.get_more_button(dv_id='dv_number',sp_id='sp_number',img_id='img_number',title_1=self.ui.ns.T('Amount'),title_2=self.ui.ns.T('Amount'),title_tool=self.ui.ns.T('Amount filters')),
                                _style="width: 80px;padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 30px;"))
      if data_fields:
        head_row.append(TD(self.ui.control.get_more_button(dv_id='dv_data',sp_id='sp_data',img_id='img_data',title_1=self.ui.ns.T('Data'),title_2=self.ui.ns.T('Data'),title_tool=self.ui.ns.T('Other data filters')),
                                _style="width: 80px;padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 30px;"))
      if quick_total:
        head_row.append(TD(self.ui.control.get_total_button(), _style="padding-top: 10px;padding-bottom: 6px;padding-left: 5px;padding-right: 5px;"))
      head_row.append(TD(DIV()))
      filter_table.append(head_row)
      filter_div.append(filter_table)
      
      if state_fields or bool_fields:
        filter_table = TABLE(_style="width: 100%;border-style: solid;border-width: 1px;border-color: #CCCCCC;border-top: none;")
        head_row = TR()
        
        if str(state_fields).find("nervatype")>-1:
          head_row.append(TD(DIV(filter_form.custom.label.nervatype, _class="label"),_style="width: 90px;padding: 6px 10px 6px 10px;"))
          head_row.append(TD(filter_form.custom.widget.nervatype, _style="width: 100px;padding: 10px 0px 10px 5px;"))
          
        if str(state_fields).find("transtype")>-1 or str(state_fields).find("paymtype")>-1:
          head_row.append(TD(DIV(filter_form.custom.label.transtype, _class="label"),_style="width: 90px;padding: 6px 10px 6px 10px;"))
          head_row.append(TD(filter_form.custom.widget.transtype, _style="width: 100px;padding: 10px 0px 10px 5px;"))
        
        if str(state_fields).find("direction")>-1:
          head_row.append(TD(DIV(filter_form.custom.label.direction, _class="label"),_style="width: 90px;padding: 6px 10px 6px 10px;"))
          head_row.append(TD(filter_form.custom.widget.direction, _style="width: 100px;padding: 10px 0px 10px 5px;"))
        
        if str(state_fields).find("pricetype")>-1:
          head_row.append(TD(DIV(filter_form.custom.label.pricetype, _class="label"),_style="width: 90px;padding: 6px 10px 6px 10px;"))
          head_row.append(TD(filter_form.custom.widget.pricetype, _style="width: 100px;padding: 10px 0px 10px 5px;"))
        
        if str(state_fields).find("headtype")>-1:
          head_row.append(TD(DIV(filter_form.custom.label.headtype, _class="label"),_style="width: 90px;padding: 6px 10px 6px 10px;"))
          head_row.append(TD(filter_form.custom.widget.headtype, _style="width: 100px;padding: 10px 0px 10px 5px;"))
          
        if str(state_fields).find("invtype")>-1:
          head_row.append(TD(DIV(filter_form.custom.label.invtype, _class="label"),_style="width: 90px;padding: 6px 10px 6px 10px;"))
          head_row.append(TD(filter_form.custom.widget.invtype, _style="width: 100px;padding: 10px 0px 10px 5px;"))
          
        if str(state_fields).find("logstate")>-1:
          head_row.append(TD(DIV(filter_form.custom.label.logstate, _class="label"),_style="width: 90px;padding: 6px 10px 6px 10px;"))
          head_row.append(TD(filter_form.custom.widget.logstate, _style="width: 100px;padding: 10px 0px 10px 5px;"))
          
        if str(state_fields).find("ratetype")>-1:
          head_row.append(TD(DIV(filter_form.custom.label.ratetype, _class="label"),_style="width: 90px;padding: 6px 10px 6px 10px;"))
          head_row.append(TD(filter_form.custom.widget.ratetype, _style="width: 100px;padding: 10px 0px 10px 5px;"))
          
        if str(state_fields).find("transtate")>-1 or str(state_fields).find("transcast")>-1 or bool_fields:
          head_row.append(TD(DIV(self.ui.ns.T('State'), _class="label"),_style="width: 90px;padding: 6px 10px 6px 10px;"))
        
        if str(state_fields).find("transtate")>-1:
          head_row.append(TD(filter_form.custom.widget.transtate, _style="width: 80px;padding: 10px 0px 10px 5px;"))
        
        if str(state_fields).find("transcast")>-1:
          head_row.append(TD(filter_form.custom.widget.transcast, _style="width: 120px;padding: 10px 0px 10px 10px;"))
          
        if bool_fields:
          head_row.append(TD(filter_form.custom.widget.bool_filter_name, _style="width: 100px;padding: 9px 0px 8px 10px;"))
          head_row.append(TD(filter_form.custom.widget.bool_filter_value, _style="width: 20px;padding: 4px 0px 8px 0px;"))
        head_row.append(TD(DIV()))
        filter_table.append(head_row)
        filter_div.append(DIV(filter_table,_id="dv_type",_style="display: none;"))
      
      if date_fields:
        filter_table = TABLE(_style="width: 100%;border-style: solid;border-width: 1px;border-color: #CCCCCC;border-top: none;")
        head_row = TR()
        head_row.append(TD(DIV(filter_form.custom.label.date_filter_name_1, _class="label"),_style="width: 90px;padding: 6px 10px 6px 10px;"))
        head_row.append(TD(filter_form.custom.widget.date_filter_name_1, _style="width: 150px;padding: 10px 0px 10px 5px;"))
        head_row.append(TD(filter_form.custom.widget.date_filter_rel_1, _style="width: 50px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.date_filter_value_1, _style="width: 80px;padding: 10px 10px 10px 0px;"))
        head_row.append(TD(SPAN("-",_class="label"),_style="width: 15px;"))
        head_row.append(TD(filter_form.custom.widget.date_filter_name_2, _style="width: 150px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.date_filter_rel_2, _style="width: 50px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.date_filter_value_2, _style="width: 80px;padding: 10px 10px 10px 0px;"))
        head_row.append(TD(SPAN("-",_class="label"),_style="width: 15px;"))
        head_row.append(TD(filter_form.custom.widget.date_filter_name_3, _style="width: 150px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.date_filter_rel_3, _style="width: 50px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.date_filter_value_3, _style="width: 80px;padding: 10px 20px 10px 0px;"))      
        head_row.append(TD(DIV()))
        filter_table.append(head_row)
        filter_div.append(DIV(filter_table,_id="dv_date",_style="display: none;"))
      
      if number_fields:
        filter_table = TABLE(_style="width: 100%;border-style: solid;border-width: 1px;border-color: #CCCCCC;border-top: none;")
        head_row = TR()
        head_row.append(TD(DIV(filter_form.custom.label.number_filter_name_1, _class="label"),_style="width: 90px;padding: 6px 10px 6px 10px;"))
        head_row.append(TD(filter_form.custom.widget.number_filter_name_1, _style="width: 150px;padding: 10px 0px 10px 5px;"))
        head_row.append(TD(filter_form.custom.widget.number_filter_rel_1, _style="width: 50px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.number_filter_value_1, _style="width: 80px;padding: 10px 10px 10px 0px;"))
        head_row.append(TD(SPAN("-",_class="label"),_style="width: 15px;"))
        head_row.append(TD(filter_form.custom.widget.number_filter_name_2, _style="width: 150px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.number_filter_rel_2, _style="width: 50px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.number_filter_value_2, _style="width: 80px;padding: 10px 10px 10px 0px;"))
        head_row.append(TD(SPAN("-",_class="label"),_style="width: 15px;"))
        head_row.append(TD(filter_form.custom.widget.number_filter_name_3, _style="width: 150px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.number_filter_rel_3, _style="width: 50px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.number_filter_value_3, _style="width: 80px;padding: 10px 20px 10px 0px;"))                     
        head_row.append(TD(DIV()))
        filter_table.append(head_row)
        filter_div.append(DIV(filter_table,_id="dv_number",_style="display: none;"))
        
      if data_fields:
        filter_table = TABLE(_style="width: 100%;border-style: solid;border-width: 1px;border-color: #CCCCCC;border-top: none;")
        head_row = TR()
        head_row.append(TD(DIV(filter_form.custom.label.data_filter_name_1, _class="label"),_style="width: 70px;padding: 6px 10px 6px 10px;"))
        head_row.append(TD(filter_form.custom.widget.data_filter_name_1, _style="width: 150px;padding: 10px 0px 10px 5px;"))
        head_row.append(TD(filter_form.custom.widget.data_filter_rel_1, _style="width: 70px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.data_filter_value_1, _style="width: 90px;padding: 10px 10px 10px 0px;"))
        head_row.append(TD(SPAN("-",_class="label"),_style="width: 15px;"))
        head_row.append(TD(filter_form.custom.widget.data_filter_name_2, _style="width: 150px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.data_filter_rel_2, _style="width: 70px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.data_filter_value_2, _style="width: 90px;padding: 10px 10px 10px 0px;"))
        head_row.append(TD(SPAN("-",_class="label"),_style="width: 15px;"))
        head_row.append(TD(filter_form.custom.widget.data_filter_name_3, _style="width: 150px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.data_filter_rel_3, _style="width: 70px;padding: 10px 0px 10px 0px;"))
        head_row.append(TD(filter_form.custom.widget.data_filter_value_3, _style="width: 90px;padding: 10px 20px 10px 0px;"))      
        head_row.append(TD(DIV()))
        filter_table.append(head_row)
        filter_div.append(DIV(filter_table,_id="dv_data",_style="display: none;"))
      
      if quick_total:
        filter_table = TABLE(_style="width: 100%;border-style: solid;border-width: 1px;border-color: #CCCCCC;border-top: none;")
        head_row = TR()
        if quick_total.has_key("netamount"):
          head_row.append(TD(DIV(self.ui.ns.T("Netamount"), _class="label"),_style="width:80px;padding: 6px 10px 6px 10px;"))
          if quick_total["netamount"]:
            head_row.append(TD(DIV(SPAN(self.ui.ns.valid.split_thousands(float(quick_total["netamount"])," ",".")), _class="label_disabled", _style="text-align: right;"),_style="width: 120px;padding: 10px 10px 10px 5px;"))
          else:
            head_row.append(TD(DIV(SPAN("0"), _class="label_disabled", _style="text-align: right;"),_style="width: 120px;padding: 10px 10px 10px 5px;"))
        if quick_total.has_key("vatamount"):
          head_row.append(TD(DIV(self.ui.ns.T("VAT"), _class="label"),_style="width: 60px;padding: 6px 10px 6px 10px;"))
          if quick_total["vatamount"]:
            head_row.append(TD(DIV(SPAN(self.ui.ns.valid.split_thousands(float(quick_total["vatamount"])," ",".")), _class="label_disabled", _style="text-align: right;"),_style="width: 100px;padding: 10px 10px 10px 5px;"))
          else:
            head_row.append(TD(DIV(SPAN("0"), _class="label_disabled", _style="text-align: right;"),_style="width: 100px;padding: 10px 10px 10px 5px;"))
        if quick_total.has_key("amount"):
          head_row.append(TD(DIV(self.ui.ns.T("Amount"), _class="label"),_style="width: 80px;padding: 6px 10px 6px 10px;"))
          if quick_total["amount"]:
            head_row.append(TD(DIV(SPAN(self.ui.ns.valid.split_thousands(float(quick_total["amount"])," ",".")), _class="label_disabled", _style="text-align: right;"),_style="width: 120px;padding: 10px 20px 10px 5px;"))
          else:
            head_row.append(TD(DIV(SPAN("0"), _class="label_disabled", _style="text-align: right;"),_style="width: 120px;padding: 10px 20px 10px 5px;"))
        if quick_total.has_key("qty"):
          head_row.append(TD(DIV(self.ui.ns.T("Qty"), _class="label"),_style="width: 80px;padding: 6px 10px 6px 10px;"))
          if quick_total["qty"]:
            head_row.append(TD(DIV(SPAN(self.ui.ns.valid.split_thousands(float(quick_total["qty"])," ",".")), _class="label_disabled", _style="text-align: right;"),_style="width: 120px;padding: 10px 20px 10px 5px;"))
          else:
            head_row.append(TD(DIV(SPAN("0"), _class="label_disabled", _style="text-align: right;"),_style="width: 120px;padding: 10px 20px 10px 5px;"))
        head_row.append(TD(DIV()))
        filter_table.append(head_row)
        filter_div.append(DIV(filter_table,_id="dv_total",_style="display: none;"))
      
      filter_div.append(filter_form.custom.end) 
      return filter_div
  
  def create_search_form(self, url,div=None):
    if self.ui.ns.session.mobile:
      if div:
        tb = INPUT(_type="search", _name='keywords', _value=self.ui.ns.request.vars.keywords,
                _id=div+'_keywords', _onfocus="", _placeholder="search data...",
                _onkeydown="if (event.keyCode == 13) document.getElementById('"+div+"_submit').click()")
        cmd = self.ui.control.get_mobil_button(self.ui.ns.T("Search"), "#", icon="search", mini="true", cmd_id=div+'_submit',
        ajax="true", onclick='$("#'+div+'").load("'+url+'",{keywords: $("#'+div+'_keywords").val()});return false;')
        cmd["_data-theme"] = "b"
        return TABLE(TR(TD(tb),TD(cmd,_style="width: 50px;")))
      else:
        tb = INPUT(_type="search", _name='keywords', _value=self.ui.ns.request.vars.keywords,
                _id='web2py_keywords', _onfocus="", _placeholder="search data...")
        cmd = INPUT(_type="submit",_value=self.ui.ns.T("Search"))
        cmd["_data-icon"] = "search"
        cmd["_data-mini"] = "true"
        cmd["_data-theme"] = "b"
        cmd["_data-ajax"] = "false"
    #   cmd["_data-iconpos"] = "notext"
        return FORM(TABLE(TR(TD(tb),TD(cmd,_style="width: 50px;"))),_action=url)
    else:
      if div:
        tb = INPUT(_type="text", _name='keywords', _value=self.ui.ns.request.vars.keywords,
                _id=div+'_keywords', _onfocus="", _placeholder="search data...",_style="width: 100%;",
                _onkeydown="if (event.keyCode == 13) document.getElementById('"+div+"_submit').click()")
        cmd_x = A(SPAN(_class="icon trash"), _style="padding: 4px;", _class="w2p_trap buttontext button", 
               _href="#", _title=self.ui.ns.T("Clear filter data"), 
               _onclick="document.getElementById('"+div+"_keywords').value='';")
        cmd = A(SPAN(_class="icon magnifier")+" "+SPAN(self.ui.ns.T("Search")), _style="padding: 4px;", 
                _class="w2p_trap buttontext button", 
               _href="#", _title=self.ui.ns.T("Search data"), _id=div+'_submit',
               _onclick='$("#'+div+'").load("'+url+'",{keywords: $("#'+div+'_keywords").val()});'+self.ui.jqload_hack)
        return TABLE(TR(TD(tb,_style="padding-right: 10px;"),TD(cmd_x,_style="width: 10px;padding-right: 0px;padding-top: 6px;"),
                               TD(cmd,_style="width: 50px;padding-top: 6px;padding-left: 0px;")),_style="width: 100%;")
      else:
        tb = INPUT(_type="text", _name='keywords', _value=self.ui.ns.request.vars.keywords,
                _id='web2py_keywords', _onfocus="", _placeholder="search data...",_style="width: 100%;")
        cmd_x = A(SPAN(_class="icon trash"), _style="padding: 4px;", _class="w2p_trap buttontext button", 
               _href="#", _title=self.ui.ns.T("Clear filter data"), 
               _onclick="document.getElementById('web2py_keywords').value='';")
        cmd = INPUT(_type="submit",_value=self.ui.ns.T("Search"),
                    _style="color: #483D8B;height: 28px !important;padding-top: 4px !important;")
        return FORM(TABLE(TR(TD(tb,_style="padding-right: 10px;vertical-align: middle;"),
                             TD(cmd_x,_style="width: 10px;padding-right: 0px;padding-top: 6px;"),
                             TD(cmd,_style="width: 50px;padding-top: 6px;padding-left: 0px;")),_style="width: 100%;")
                      ,_action=url)
  
  def create_search_widget(self,search_menu):
    search_menu = SQLFORM.search_menu(search_menu)
    return lambda sfield, url: CAT(FORM(
        INPUT(_name='keywords', _value=self.ui.ns.request.vars.keywords,
              _id='web2py_keywords', _onfocus=""),
        INPUT(_type='submit', _value=self.ui.ns.T('Search'), _class="btn"),
        INPUT(_type='submit', _value=self.ui.ns.T('Clear'), _class="btn",
              _onclick="jQuery('#web2py_keywords').val('');"),
        INPUT(_type='button', _value=self.ui.ns.T('More'), _class="btn",
              _onclick="jQuery('#w2p_query_fields').change();jQuery('#w2p_query_panel').slideDown();"),
        _method="GET", _action=url), search_menu)
  
  def dlg_create_trans(self, trans_id):
    directions = ["in","out"]
    def_transtype = base_transtype = self.ui.ns.valid.get_nervatype_name(self.ui.ns.db.trans(id=trans_id).transtype)
    #disabled create fom delivery
    element_count = self.ui.ns.db((self.ui.ns.db.trans.id==trans_id)&(self.ui.ns.db.item.trans_id==self.ui.ns.db.trans.id)&(self.ui.ns.db.item.deleted==0)
          &(self.ui.ns.db.fieldvalue.ref_id==self.ui.ns.db.item.product_id)
          &(self.ui.ns.db.fieldvalue.fieldname=='product_element')).select('count(*)').first()['count(*)']
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
    else:
      doctypes = ["order","worksheet","rent","invoice","receipt"]
      def_transtype="order"
      netto_color = "#C5C5C5"
      from_color = "#C5C5C5"
    
    def_direction = self.ui.ns.valid.get_nervatype_name(self.ui.ns.db.trans(id=trans_id).direction)
    cmb_doctypes = SELECT(*[OPTION(self.ui.ns.T(doctype), _value=doctype, _selected=(doctype==def_transtype)) for doctype in doctypes], 
                          _id="cmb_doctypes",_style="width: 100%;",
                          _onChange = "create_newtype_change();")
    cmb_directions = SELECT(*[OPTION(self.ui.ns.T(direc), _value=direc, _selected=(direc==def_direction)) for direc in directions], 
                            _id="cmb_directions",_style="width: 100%;")
    
    if self.ui.ns.session.mobile:
      rtable = TABLE(_style="width: 100%;",_cellpadding="0px;", _cellspacing="0px;")
      rtable.append(TR(TD(INPUT(_type="hidden", _value=base_transtype, _id="base_transtype"),
                          INPUT(_type="hidden", _value=element_count, _id="element_count"),
                          self.ui.ns.db.trans(id=trans_id).transnumber,
                          _style="background-color: #DBDBDB;font-weight: bold;text-align: center;padding: 8px;")))
      
      cmb_doctypes = SELECT(*[OPTION(self.ui.ns.T(doctype), _value=doctype, _selected=(doctype==def_transtype)) for doctype in doctypes], 
                            _id="cmb_doctypes",_style="width: 100%;height: 25px;",
                            _onChange = "create_newtype_change();")
      cmb_directions = SELECT(*[OPTION(self.ui.ns.T(direc), _value=direc, _selected=(direc==def_direction)) for direc in directions], 
                              _id="cmb_directions",_style="width: 100%;height: 25px;")
    
      rtable.append(TABLE(TR(TD(cmb_doctypes, _style="padding-right: 5px;"),
                       TD(cmb_directions)),
                       _style="width: 100%;",_cellpadding="0px;", _cellspacing="0px;"))
      rtable.append(TABLE(TR(TD(LABEL(INPUT(_type='checkbox', _id='cb_netto', value='on', _disabled=(netto_color=="#C5C5C5"),_class="boolean"),
                                self.ui.ns.T("Invoiced amount deduction"), _style="margin-bottom:0px;"))),
                    _style="width: 100%;",_cellpadding="0px;", _cellspacing="0px;"))
      rtable.append(TABLE(TR(TD(LABEL(INPUT(_type='checkbox', _id='cb_from', value='', _disabled=(from_color=="#C5C5C5"),_class="boolean", _onChange = "from_delivery_change();"),
                                self.ui.ns.T("Create by delivery"), _style=""))),
                    _style="width: 100%;",_cellpadding="0px;", _cellspacing="0px;"))
      rtable_cmd = DIV(_style="background-color: #393939;padding: 10px;") 
      rtable_cmd["_data-role"] = "controlgroup"
      rtable_cmd.append(self.ui.control.get_mobil_button(self.ui.ns.T("Creating a document"), href="#", cformat=None, icon="page", style="text-align: left;padding:0px;margin:0px;",
        onclick="create_trans('"+URL("dlg_create")+"?trans_id="+str(trans_id)
        +"','"+URL("frm_trans/view/trans")+"/');return false;", theme="b"))
      
      rtable.append(TR(TD(rtable_cmd)))
    else:                        
      rtable = TABLE(_style="width: 100%;")
      rtable.append(TR(TD(INPUT(_type="hidden", _value=base_transtype, _id="base_transtype"),
                          INPUT(_type="hidden", _value=element_count, _id="element_count"),
                          self.ui.ns.db.trans(id=trans_id).transnumber,_colspan="3",
                          _style="background-color: #F1F1F1;font-weight: bold;text-align: center;border-bottom: solid;padding: 5px;")))
      rtable.append(TR(
                       TD(self.ui.ns.T("New type"),_style="width: 100px;background-color: #F1F1F1;font-weight: bold;text-align: left;padding: 5px;border-bottom: solid;"),
                       TD(cmb_doctypes,_style="padding: 5px;padding-right: 0px;border-bottom: solid;"),
                       TD(cmb_directions,_style="width: 100px;padding: 5px;padding-right: 0px;border-bottom: solid;")))
      rtable_check = TABLE(_style="width: 100%;")
      rtable_check.append(TR(
                       TD(INPUT(_type='checkbox', _id='cb_netto', value='on', _disabled=(netto_color=="#C5C5C5")),_style="width: 10px;padding:0px;vertical-align: top;"),
                       TD(self.ui.ns.T("Invoiced amount deduction"), _id='cb_netto_label',_style="padding-top:3px;color:"+netto_color),
                       TD(INPUT(_type='checkbox', _id='cb_from', value='', _disabled=(from_color=="#C5C5C5"), _onChange = "from_delivery_change();"),
                          _style="width: 10px;padding:0px;vertical-align: top;"),
                       TD(self.ui.ns.T("Create by delivery"), _id='cb_from_label',_style="padding-top:3px;color:"+from_color)))
      rtable.append(TR(TD(rtable_check,_colspan="3", 
                          _style="background-color: #F1F1F1;font-weight: bold;text-align: left;padding: 5px;border-bottom: solid;")))
      cmd_ok = INPUT(_type="button", _value="Creating a document", _style="height: 40px !important;padding-top: 5px !important;",
                          _onclick="create_trans('"+URL("dlg_create")+"?trans_id="+str(trans_id)
                                  +"','"+URL("frm_trans/view/trans")+"/');return false;")
      rtable.append(TR(TD(cmd_ok,_colspan="3", 
                          _style="background-color: #F1F1F1;font-weight: bold;text-align: center;padding: 5px;padding-top: 8px;border-bottom: solid;")))  
  
    return DIV(rtable, _id="dlg_create_trans")
  
  def find_data(self,table,query,fields,orderby,paginate=10,maxtextlength=25,links=None,left=None,page_url=None,
                sortable=False,priority="0,1",deletable=False, fullrow=False):
    if self.ui.ns.request.vars.has_key("keywords")==False and self.ui.ns.request.vars.has_key("page")==False and not fullrow:
      query = (query&(self.ui.ns.db[table].id==-1))
    tablenames = self.ui.ns.db._adapter.tables(query)
    if left!=None:
      tablenames=tablenames+self.ui.ns.db._adapter.tables(left)
  
    if not links and not self.ui.ns.session.mobile:
      editable = True
    else:
      editable = False
    if not self.ui.ns.session.mobile:
      self.ui.ns.db[table].id.readable = self.ui.ns.db[table].id.writable = False
    gform = SQLFORM.grid(query=query, field_id=self.ui.ns.db[table].id, fields=fields, left=left,
                       orderby=orderby, sortable=sortable, paginate=paginate, maxtextlength=maxtextlength, 
                       searchable=True, csv=False, details=False, showbuttontext=False,
                       create=False, deletable=deletable, editable=editable, selectable=False,
                       links=links, user_signature=False, search_widget=None,
                       buttons_placement = 'left', links_placement = 'left')
    if type(gform[1][0][0]).__name__!="TABLE":
      gform[1][0][0] = ""
    else:
      if self.ui.ns.session.mobile:
        htable = gform.elements("div.web2py_htmltable")
        if len(htable)>0:
          self.ui.control.set_htmltable_style(htable[0][0],table+"_search",priority)
          htable[0][0]["_width"]="100%"
    counter = gform.elements("div.web2py_counter")
    if len(counter)>0:
      if counter[0][0]==None:
        counter[0][0] = ""
        
    if sortable==False:
      if gform[len(gform)-1]["_class"].startswith("web2py_paginator"):
        if not page_url:
          page_url = URL("find_"+table+"_dlg")
        pages = gform[len(gform)-1].elements("a")
        for i in range(len(pages)):
          if pages[i]["_href"]:
            pages[i]["_href"] = "#"
          if self.ui.ns.session.mobile:
            if i==0:
              pages[i]["_onclick"]="$('#popup_'+jQuery(this).parents('.ui-popup-container').attr('id').replace('-popup','')+'_result').load('"+page_url+"',{keywords: $('#popup_'+jQuery(this).parents('.ui-popup-container').attr('id').replace('-popup','')+'_result_keywords').val()});return false;"
            else:
              pages[i]["_onclick"]="$('#popup_'+jQuery(this).parents('.ui-popup-container').attr('id').replace('-popup','')+'_result').load('"+page_url+"',{keywords: $('#popup_'+jQuery(this).parents('.ui-popup-container').attr('id').replace('-popup','')+'_result_keywords').val(), page: "+str(i+1)+"});return false;"
          else:
            if i==0:
              pages[i]["_onclick"]="$('#popup_'+jQuery(this).parents('.ui-dialog-content').attr('id')+'_result').load('"+page_url+"',{keywords: $('#popup_'+jQuery(this).parents('.ui-dialog-content').attr('id')+'_result_keywords').val()});"+self.ui.jqload_hack
            else:
              pages[i]["_onclick"]="$('#popup_'+jQuery(this).parents('.ui-dialog-content').attr('id')+'_result').load('"+page_url+"',{keywords: $('#popup_'+jQuery(this).parents('.ui-dialog-content').attr('id')+'_result_keywords').val(), page: "+str(i+1)+"});"+self.ui.jqload_hack
    else:
      if self.ui.ns.session.mobile:
        if gform[len(gform)-1]["_class"].startswith("web2py_paginator"):
          pages = gform[len(gform)-1].elements("a")
          for i in range(len(pages)):
            pages[i]["_data-ajax"] = "false"
    return gform
  
  def get_base_selector(self, fieldtype,search_url,label_id,label_url,label_txt="",value_id=None,error_label=False, 
                        div_id="", display="block"):
    pop_key = web2py_uuid()
    if self.ui.ns.session.mobile:
      cmd = DIV(self.ui.control.get_popup_cmd(pop_id=pop_key,
                              label=self.ui.ns.T("Search"),theme="c",inline=True,mini=True),
              _id=div_id, _style="display:block;padding:4px;".replace("block", display))
    else:
      cmd = DIV(A(SPAN(_class="icon magnifier"), _style="padding: 0px;padding-left: 6px;padding-right: 3px;", 
                _class="w2p_trap buttontext button", _href="#", _title=self.ui.ns.T("Search data"), 
                _onclick="document.getElementById('popup_"+str(pop_key)+"_result_keywords').value='';$('#"+str(pop_key)
                +"').dialog({dialogClass: 'n2py-dialog', modal: true, minWidth: 600, resizable: false, position: {my:'center',at:'top'}});"),
              _id=div_id, _style="width: 100%;display:block;padding: 4px;height: auto;padding-bottom: 0px;".replace("block", display))
    if error_label:
      cmd["_class"]="label_error"
      cmd.append(SPAN(label_txt, _id=label_id, _style="font-weight: bold;"))
    elif label_url!="":
      cmd["_class"]="label_disabled"  
      cmd.append(A(label_txt, _id=label_id, _href="#", _onclick="javascript:window.open("+label_url+", '_blank');"))
    else:
      cmd["_class"]="label_disabled"
      cmd.append(SPAN(label_txt, _id=label_id))
    if self.ui.ns.session.mobile:
      if value_id!=None:
        cmd.insert(1, self.ui.control.get_mobil_button(label=self.ui.ns.T("Delete"), href="#", 
          icon="delete", ajax="true", iconpos="notext", title=self.ui.ns.T("Delete link"),
          onclick="document.getElementById('"+value_id+"').value='';document.getElementById('"+label_id+"').innerHTML='';"))
        cmd.insert(2, XML("&nbsp;"))
      def get_search_popup(pop_id, url):
        icon = A(self.ui.ns.T("Close"),_style="top:1px;", _href="#")
        icon["_data-icon"]="delete"
        icon["_data-iconpos"] = "notext"
        icon["_data-theme"] = "a"
        icon["_data-rel"] = "back"
        ftitle = DIV(_class="ui-corner-top")
        ftitle["_data-role"] = "header"
        ftitle["_data-theme"] = "a"
        ftitle.append(icon)
        ftitle.append(H1(self.ui.ns.T("Select data"), _style="color: #FFD700;font-size: small;"))
      
        sform = self.create_search_form(url,"popup_"+pop_id+"_result")
        frm = DIV(sform,DIV(_id="popup_"+pop_id+"_result"))
                                 
        pop = DIV(ftitle, frm, _id=pop_id)
        pop["_data-role"] = "popup"
      #   dlg["_data-dismissible"] = "false"
        pop["_data-theme"] = "c"
        pop["_data-overlay-theme"] = "a"
        pop["_data-corners"] = "false"
        pop["_data-tolerance"] = "15,15"
        pop["_style"] = "padding:10px;border-radius:10px;"
        return pop
      cmd.append(get_search_popup(pop_key,search_url))
    else:
      if value_id!=None:
        cmd.insert(1, A(SPAN(_class="icon trash"),_style="width: 16px;padding: 0px;padding-left: 6px;padding-right: 3px;", 
                      _class="w2p_trap buttontext button", _href="#null", _title=self.ui.ns.T("Delete link"), 
                      _onclick="document.getElementById('"+value_id+"').value='';document.getElementById('"+label_id+"').innerHTML='';"))  
      cmd.append(DIV(DIV(self.create_search_form(search_url,"popup_"+pop_key+"_result"),
                       DIV(_id="popup_"+pop_key+"_result")), 
                   _id=pop_key, _title=self.ui.ns.T("Select data"), _style="display: none;"))
    return cmd
  
  def get_customer_selector(self,customer_custname,error_label=False):
    audit_filter = self.ui.connect.get_audit_filter("customer", None)[0]
    if audit_filter!="disabled":
      return self.get_base_selector(fieldtype="customer", search_url=URL("dlg_customer"),
                            label_id="customer_custname", 
                            label_url="'"+URL("frm_customer/view/customer")+"/'+document.getElementById('customer_id').value",
                            label_txt=customer_custname,value_id="customer_id",error_label=error_label)
    else:
      return self.ui.control.get_disabled_label(customer_custname,"customer_custname","customer_id")
  
  def get_employee_selector(self,employee_empnumber,error_label=False):
    audit_filter = self.ui.connect.get_audit_filter("employee", None)[0]
    if audit_filter!="disabled":
      return self.get_base_selector(fieldtype="employee", search_url=URL("dlg_employee"),
                            label_id="employee_empnumber",
                            label_url="'"+URL("frm_employee/view/employee")+"/'+document.getElementById('employee_id').value",
                            label_txt=employee_empnumber,value_id="employee_id",error_label=error_label)  
    else:
      return self.ui.control.get_disabled_label(employee_empnumber,"employee_empnumber","employee_id")
  
  def get_fields_filter(self,nervatype,sfilter_name,state_fields=None):
    nervatype_trans = self.ui.ns.valid.get_groups_id("nervatype", nervatype)
    rows = self.ui.ns.db((self.ui.ns.db.deffield.deleted==0)&(self.ui.ns.db.deffield.visible==1)&(self.ui.ns.db.deffield.nervatype==nervatype_trans)).select().as_list()
    bool_fields_name=[]
    bool_fields_label=[]
    date_fields_name=[]
    date_fields_label=[]
    number_fields_name=[]
    number_fields_label=[]
    data_fields_name=[]
    data_fields_label=[]
    for field in rows:
      if self.ui.ns.db.groups(id=field["fieldtype"]).groupvalue=="bool":
        bool_fields_name.append(field["fieldname"])
        bool_fields_label.append(field["description"])
      elif self.ui.ns.db.groups(id=field["fieldtype"]).groupvalue=="date":
        date_fields_name.append(field["fieldname"])
        date_fields_label.append(field["description"])
      elif self.ui.ns.db.groups(id=field["fieldtype"]).groupvalue in("float","integer"):
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
    data_fields_label.insert(0, self.ui.ns.T("Other data"))
    data_fields_name.insert(0, "description")
    data_fields_label.insert(0, self.ui.ns.T("Description"))  
    if nervatype=="trans":
      data_fields_name.insert(0, "htab_trans_transnumber")
      data_fields_label.insert(0, self.ui.ns.T("Doc.No."))
    elif nervatype=="project":
      data_fields_name.insert(0, "htab_project_description")
      data_fields_label.insert(0, self.ui.ns.T("Project Name"))
      data_fields_name.insert(0, "htab_project_pronumber")
      data_fields_label.insert(0, self.ui.ns.T("Project No."))
    elif nervatype=="customer":
      data_fields_name.insert(0, "htab_customer_custname")
      data_fields_label.insert(0, self.ui.ns.T("Customer Name"))
      data_fields_name.insert(0, "htab_customer_custnumber")
      data_fields_label.insert(0, self.ui.ns.T("Customer No."))
    elif nervatype=="employee":
      data_fields_name.insert(0, "htab_employee_username")
      data_fields_label.insert(0, self.ui.ns.T("Username"))
      data_fields_name.insert(0, "htab_employee_empnumber")
      data_fields_label.insert(0, self.ui.ns.T("Employee No."))
    elif nervatype=="tool":
      data_fields_name.insert(0, "htab_tool_description")
      data_fields_label.insert(0, self.ui.ns.T("Tool description"))
      data_fields_name.insert(0, "htab_tool_serial")
      data_fields_label.insert(0, self.ui.ns.T("Serial No."))
    elif nervatype=="product":
      data_fields_name.insert(0, "htab_product_description")
      data_fields_label.insert(0, self.ui.ns.T("Product name"))
      data_fields_name.insert(0, "htab_product_partnumber")
      data_fields_label.insert(0, self.ui.ns.T("Product No."))
    elif nervatype=="event":
      data_fields_name.insert(0, "htab_event_subject")
      data_fields_label.insert(0, self.ui.ns.T("Subject"))
      data_fields_name.insert(0, "htab_event_calnumber")
      data_fields_label.insert(0, self.ui.ns.T("Event No."))
    return self.create_filter_form(sfilter_name=sfilter_name,state_fields=state_fields,
                                         bool_fields=bool_fields,date_fields=date_fields,number_fields=number_fields,
                                         data_fields={"data_fields_name":data_fields_name,"data_fields_label":data_fields_label})
  
  def get_filter_query(self,sfilter,table,query):
    having = None
    if len(sfilter)>0:
      if sfilter.get("nervatype"):
        query = query & (self.ui.ns.db[table].nervatype==int(sfilter.get("nervatype")))
      if sfilter.get("transtype"):
        if table=="fieldvalue":
          query = query & (self.ui.ns.db.trans.with_alias('htab').transtype==int(sfilter.get("transtype")))
        elif table=="payment_invoice":
          query = query & (self.ui.ns.db.trans.with_alias('ptrans').transtype==int(sfilter.get("transtype")))
        else:
          query = query & (self.ui.ns.db.trans.transtype==int(sfilter.get("transtype")))
      if sfilter.get("direction"):
        if table=="fieldvalue":
          query = query & (self.ui.ns.db.trans.with_alias('htab').direction==int(sfilter.get("direction")))
        elif table=="payment_invoice":
          query = query & (self.ui.ns.db.trans.with_alias('ptrans').direction==int(sfilter.get("direction")))
        else:
          query = query & (self.ui.ns.db.trans.direction==int(sfilter.get("direction")))
      if sfilter.get("transtate"):
        if table=="fieldvalue":
          query = query & (self.ui.ns.db.trans.with_alias('htab').transtate==int(sfilter.get("transtate")))
        elif table=="payment_invoice":
          query = query & (self.ui.ns.db.trans.with_alias('ptrans').transtate==int(sfilter.get("transtate")))
        else:
          query = query & (self.ui.ns.db.trans.transtate==int(sfilter.get("transtate")))
      if sfilter.get("transcast"):
        if table=="fieldvalue":
          query = query & ((self.ui.ns.db.trans.with_alias('htab').id == self.ui.ns.db.fieldvalue.ref_id)&(self.ui.ns.db.fieldvalue.fieldname=="trans_transcast")&(self.ui.ns.db.fieldvalue.value==sfilter.get("transcast")))
        else:
          query = query & ((self.ui.ns.db.trans.id == self.ui.ns.db.fieldvalue.ref_id)&(self.ui.ns.db.fieldvalue.fieldname=="trans_transcast")&(self.ui.ns.db.fieldvalue.value==sfilter.get("transcast")))
      if sfilter.get("headtype"):
        query = query & (self.ui.ns.db.movement.movetype==self.ui.ns.valid.get_groups_id("movetype", sfilter.get("headtype")))
      if sfilter.get("pricetype"):
        if sfilter.get("pricetype")=="list":
          query = query & ((self.ui.ns.db.link.with_alias('custlink').ref_id_2==None)&(self.ui.ns.db.link.with_alias('grouplink').ref_id_2==None))
        elif sfilter.get("pricetype")=="customer":
          query = query & (self.ui.ns.db.link.with_alias('custlink').ref_id_2!=None)
        elif sfilter.get("pricetype")=="group":
          query = query & (self.ui.ns.db.link.with_alias('grouplink').ref_id_2!=None)
      if sfilter.get("invtype"):
        if table=="fieldvalue":
          itrans = self.ui.ns.db.trans.with_alias('htab')
        else:
          itrans = self.ui.ns.db.trans
        if sfilter.get("invtype")=="delivery":
          query = query & ((itrans.transtype==self.ui.ns.valid.get_groups_id("transtype", "delivery")))
        if sfilter.get("invtype")=="inventory":
          query = query & ((itrans.transtype==self.ui.ns.valid.get_groups_id("transtype", "inventory")))
        if sfilter.get("invtype")=="production":
          query = query & ((itrans.transtype==self.ui.ns.valid.get_groups_id("transtype", "production")))
      if sfilter.get("logstate"):
        query = query & (self.ui.ns.db[table].logstate==int(sfilter.get("logstate")))
      if sfilter.get("ratetype"):
        query = query & (self.ui.ns.db[table].ratetype==int(sfilter.get("ratetype")))
      if sfilter.get("bool_filter_name"):
        if table=="fieldvalue":
          if sfilter.get("bool_filter_value"):
            query = query & ((self.ui.ns.db.fieldvalue.fieldname==sfilter.get("bool_filter_name"))&(self.ui.ns.db.fieldvalue.value=="true"))
          else:
            query = query & ((self.ui.ns.db.fieldvalue.fieldname==sfilter.get("bool_filter_name"))&(self.ui.ns.db.fieldvalue.value=="false"))
        else:
          if sfilter.get("bool_filter_value"):
            query = query & (self.ui.ns.db[table][sfilter.get("bool_filter_name")]==1)
          else:
            query = query & (self.ui.ns.db[table][sfilter.get("bool_filter_name")]==0)
      
      def get_date_query(table,fname,fvalue,frel):
        if not sfilter.get(frel):
          sfilter[frel] = "="
        if table=="fieldvalue":
          return (self.ui.ns.db.fieldvalue.fieldname==sfilter.get(fname))& ("(cast(fieldvalue.value as date) %s '%s')" % (sfilter.get(frel),sfilter.get(fvalue)))
        elif table=="item" and sfilter.get(fname)=="transdate":
          return self.get_query_rel(self.ui.ns.db.trans[sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue))
        elif table=="trans" and sfilter.get(fname)=="shippingdate":
          return self.get_query_rel(self.ui.ns.db.movement[sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue))
        elif table in("trans","payment_invoice") and sfilter.get(fname)=="paiddate":
          return self.get_query_rel(self.ui.ns.db.payment[sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue))
        else:
          return self.get_query_rel(self.ui.ns.db[table][sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue))    
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
          return dict(query=(self.ui.ns.db.fieldvalue.fieldname==sfilter.get(fname))& ("(cast(fieldvalue.value as real) %s %s)" % (sfilter.get(frel),sfilter.get(fvalue))),having=None)
        if table=="payment_invoice":
          ftable = self.ui.ns.db.fieldvalue.with_alias(sfilter.get(fname))
          return dict(query=(ftable.fieldname==sfilter.get(fname))& ("(cast("+sfilter.get(fname)+".value as real) %s %s)" % (sfilter.get(frel),sfilter.get(fvalue))),having=None)
        elif table=="trans" and sfilter.get(fname) in("amount","netamount","vatamount"):
          return dict(query=None,having=self.get_query_rel(self.ui.ns.db.item[sfilter.get(fname)].sum(),sfilter.get(frel),sfilter.get(fvalue)))
        elif table=="trans" and sfilter.get(fname) in("paidamount"):
          return dict(query=self.get_query_rel(self.ui.ns.db.payment.amount,sfilter.get(frel),sfilter.get(fvalue)),having=None)
        elif table=="movement" and sfilter.get(fname) == "sqty":
          return dict(query=None,having=self.get_query_rel(self.ui.ns.db.movement.qty.sum(),sfilter.get(frel),sfilter.get(fvalue)))
        elif table=="movement" and sfilter.get(fname) == "qty":
          return dict(query=self.get_query_rel(self.ui.ns.db.movement.qty,sfilter.get(frel),sfilter.get(fvalue)),having=None)
        else:
          return dict(query=self.get_query_rel(self.ui.ns.db[table][sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue)),having=None)      
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
              return ((self.ui.ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=customer.id)") & self.get_query_rel(self.ui.ns.db.customer.custname,frel,fvalue))
            else:
              return ((self.ui.ns.db[table].customer_id == self.ui.ns.db.customer.id)&self.get_query_rel(self.ui.ns.db.customer.custname,frel,fvalue))
          elif fname=="tool_id" or ftype=="tool":
            if table in ("fieldvalue"):
              return ((self.ui.ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=tool.id)") & self.get_query_rel(self.ui.ns.db.tool.serial,frel,fvalue))
            else:
              return ((self.ui.ns.db[table].tool_id == self.ui.ns.db.tool.id)&self.get_query_rel(self.ui.ns.db.tool.serial,frel,fvalue))
          elif fname=="employee_id" or ftype=="employee":
            if table in ("fieldvalue"):
              return ((self.ui.ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=employee.id)") & self.get_query_rel(self.ui.ns.db.employee.empnumber,frel,fvalue))
            else:
              return ((self.ui.ns.db[table].employee_id == self.ui.ns.db.employee.id)&self.get_query_rel(self.ui.ns.db.employee.empnumber,frel,fvalue))
          elif fname=="place_id" or ftype=="place":
            if table in ("fieldvalue"):
              return ((self.ui.ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=place.id)") & self.get_query_rel(self.ui.ns.db.place.planumber,frel,fvalue))
            else:
              return ((self.ui.ns.db[table].place_id == self.ui.ns.db.place.id)&self.get_query_rel(self.ui.ns.db.place.planumber,frel,fvalue))
          elif fname in("department","paidtype","eventgroup","custtype","usergroup","toolgroup","protype","rategroup"):
            return ((self.ui.ns.db[table][fname]==self.ui.ns.db.groups.id)&self.get_query_rel(self.ui.ns.db.groups.groupvalue,frel,fvalue))
          elif fname=="project_id" or ftype=="project":
            if table in ("fieldvalue"):
              return ((self.ui.ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=project.id)") & self.get_query_rel(self.ui.ns.db.project.pronumber,frel,fvalue))  
            else:
              return ((self.ui.ns.db[table].project_id == self.ui.ns.db.project.id)&self.get_query_rel(self.ui.ns.db.project.pronumber,frel,fvalue))
          elif fname=="trans_id" or ftype in("trans","transitem","transmovement","transpayment"):
            if table in ("fieldvalue"):
              return ((self.ui.ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=trans.id)") & self.get_query_rel(self.ui.ns.db.trans.transnumber,frel,fvalue))
            else:
              return ((self.ui.ns.db[table].trans_id == self.ui.ns.db.trans.id)&self.get_query_rel(self.ui.ns.db.trans.transnumber,frel,fvalue))
          elif fname=="product_id" or ftype=="product":
            if table in ("fieldvalue"):
              return ((self.ui.ns.db.fieldvalue.fieldname==fname) & ("(cast(fieldvalue.value as integer)=product.id)") & self.get_query_rel(self.ui.ns.db.product.description,frel,fvalue))
            else:
              return ((self.ui.ns.db[table].product_id == self.ui.ns.db.product.id)&self.get_query_rel(self.ui.ns.db.product.description,frel,fvalue))
          elif fname=="tax_id":
            return ((self.ui.ns.db[table].tax_id == self.ui.ns.db.tax.id)&self.get_query_rel(self.ui.ns.db.tax.taxcode,frel,fvalue))
          elif fname=="event_id":
            return ((self.ui.ns.db[table].event_id == self.ui.ns.db.event.id)&self.get_query_rel(self.ui.ns.db.event.calnumber,frel,fvalue))
        
        if str(sfilter.get(fname)).startswith("htab_"):
          if table=="fieldvalue":
            return self.get_query_rel(self.ui.ns.db[str(sfilter.get(fname)).split("_")[1]].with_alias('htab')[str(sfilter.get(fname)).split("_")[2]],sfilter.get(frel),sfilter.get(fvalue))
          else:
            return self.get_query_rel(self.ui.ns.db[str(sfilter.get(fname)).split("_")[1]][str(sfilter.get(fname)).split("_")[2]],sfilter.get(frel),sfilter.get(fvalue))  
        elif table=="fieldvalue":
          if sfilter.get(fname)=="description":
            return self.get_query_rel(self.ui.ns.db.deffield.description,sfilter.get(frel),sfilter.get(fvalue))
          elif sfilter.get(fname)=="notes":
            return self.get_query_rel(self.ui.ns.db.fieldvalue.notes,sfilter.get(frel),sfilter.get(fvalue))
          else: 
            fieldtype = self.ui.ns.db.groups(id=self.ui.ns.db.deffield(fieldname=sfilter.get(fname)).fieldtype).groupvalue
            if fieldtype in("customer","tool","product","trans","transitem","transmovement","transpayment","project","employee","place"):
              return get_ref_value(table,sfilter.get(fname),sfilter.get(fvalue),sfilter.get(frel),fieldtype)
            else:
              return ((self.ui.ns.db.fieldvalue.fieldname == sfilter.get(fname))&self.get_query_rel(self.ui.ns.db.fieldvalue.value,sfilter.get(frel),sfilter.get(fvalue)))
        elif sfilter.get(fname) in("customer_id","employee_id","paidtype","project_id","trans_id","product_id","tax_id",
                                   "eventgroup","custtype","usergroup","toolgroup","protype","place_id","rategroup"):
          return get_ref_value(table,sfilter.get(fname),sfilter.get(fvalue),sfilter.get(frel))
        elif table=="employee" and sfilter.get(fname)=="department":
          department = self.ui.ns.db.groups.with_alias('department')
          return self.get_query_rel(department.groupvalue,sfilter.get(frel),sfilter.get(fvalue))
        elif table=="trans" and sfilter.get(fname) == "place_curr":
          return ((self.ui.ns.db.trans.place_id == self.ui.ns.db.place.id)&self.get_query_rel(self.ui.ns.db.place.curr,sfilter.get(frel),sfilter.get(fvalue)))
        elif table=="trans" and sfilter.get(fname) == "payment_description":
          return self.get_query_rel(self.ui.ns.db.payment.notes,sfilter.get(frel),sfilter.get(fvalue))
        elif table=="movement" and sfilter.get(fname) in("partnumber","unit"):
          return self.get_query_rel(self.ui.ns.db.product[sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue))
        elif table=="movement" and sfilter.get(fname) == "refcust":
          return ((self.ui.ns.db.trans.with_alias('itrn').customer_id == self.ui.ns.db.customer.id)&self.get_query_rel(self.ui.ns.db.customer.custname,sfilter.get(frel),sfilter.get(fvalue)))
        elif table=="movement" and sfilter.get(fname) == "refnumber":
          return ((self.ui.ns.db.item.trans_id == self.ui.ns.db.trans.with_alias('rtrn').id)&self.get_query_rel(self.ui.ns.db.trans.with_alias('rtrn').transnumber,sfilter.get(frel),sfilter.get(fvalue)))
        elif table=="payment_invoice":
          if sfilter.get(fname) in("place"):
            return ((self.ui.ns.db.trans.with_alias('ptrans').place_id == self.ui.ns.db.place.id)&self.get_query_rel(self.ui.ns.db.place.planumber,sfilter.get(frel),sfilter.get(fvalue)))
          elif sfilter.get(fname) in("docnumber"):
            return self.get_query_rel(self.ui.ns.db.trans.with_alias('ptrans').transnumber,sfilter.get(frel),sfilter.get(fvalue))
          elif sfilter.get(fname) in("doc_curr"):
            return self.get_query_rel(self.ui.ns.db.trans.with_alias('ptrans').curr,sfilter.get(frel),sfilter.get(fvalue))
          elif sfilter.get(fname) in("invnumber"):
            return self.get_query_rel(self.ui.ns.db.trans.with_alias('itrans').transnumber,sfilter.get(frel),sfilter.get(fvalue))
          elif sfilter.get(fname) in("inv_curr"):
            return self.get_query_rel(self.ui.ns.db.trans.with_alias('itrans').curr,sfilter.get(frel),sfilter.get(fvalue))
        else:
          return self.get_query_rel(self.ui.ns.db[table][sfilter.get(fname)],sfilter.get(frel),sfilter.get(fvalue))
      if sfilter.get("data_filter_name_1") and sfilter.get("data_filter_value_1"):
        query = query & get_data_query(table,"data_filter_name_1","data_filter_value_1","data_filter_rel_1")
      if sfilter.get("data_filter_name_2") and sfilter.get("data_filter_value_2"):
        query = query & get_data_query(table,"data_filter_name_2","data_filter_value_2","data_filter_rel_2")
      if sfilter.get("data_filter_name_3") and sfilter.get("data_filter_value_3"):
        query = query & get_data_query(table,"data_filter_name_3","data_filter_value_3","data_filter_rel_3")
                                
    return dict(query=query,having=having)
  
  def get_place_selector(self,place_planumber,error_label=False,placetype="dlg_place_all",title="Select Place",
                         value_id="place_id", label_id="place_planumber", fnum=""):
    return self.get_base_selector(fieldtype="place", search_url=URL(placetype+fnum),
                            label_id=label_id, 
                            label_url="'"+URL("frm_place/view/place")+"/'+document.getElementById('"+value_id+"').value",
                            label_txt=place_planumber,value_id=value_id,error_label=error_label) 
                    
  def get_popup_form(self,pid, title, content):
    icon = A(self.ui.ns.T("Close"),_style="top:1px;", _href="#")
    icon["_data-icon"]="delete"
    icon["_data-iconpos"] = "notext"
    icon["_data-theme"] = "a"
    icon["_data-rel"] = "back"
    ftitle = DIV(_class="ui-corner-top")
    ftitle["_data-role"] = "header"
    ftitle["_data-theme"] = "a"
    ftitle.append(icon)
    ftitle.append(H1(title, _style="color: #FFD700;font-size: small;", _id="divs_title"))
                             
    pop = DIV(ftitle, content, _id=pid)
    pop["_data-role"] = "popup"
  #   dlg["_data-dismissible"] = "false"
    pop["_data-theme"] = "c"
    pop["_data-overlay-theme"] = "a"
    pop["_data-corners"] = "false"
    pop["_data-tolerance"] = "15,15"
    pop["_style"] = "padding:10px;border-radius:10px;"
    return pop
  
  def get_product_selector(self,product_description,error_label=False,protype="all"):
    audit_filter = self.ui.connect.get_audit_filter("product", None)[0]
    if audit_filter!="disabled":
      return self.get_base_selector(fieldtype="product", search_url=URL("dlg_product_"+protype),
                            label_id="product_description", 
                            label_url="'"+URL("frm_product/view/product")+"/'+document.getElementById('product_id').value",
                            label_txt=product_description,value_id="product_id",error_label=error_label)
    else:
      return self.ui.control.get_disabled_label(product_description,"product_description","product_id")
  
  def get_project_selector(self,project_pronumber,error_label=False):  
    audit_filter = self.ui.connect.get_audit_filter("project", None)[0]
    if audit_filter!="disabled":
      return self.get_base_selector(fieldtype="project", search_url=URL("dlg_project"),
                            label_id="project_pronumber",
                            label_url="'"+URL("frm_project/view/project")+"/'+document.getElementById('project_id').value",
                            label_txt=project_pronumber,value_id="project_id",error_label=error_label)
    else:
      return self.ui.control.get_disabled_label(project_pronumber,"project_pronumber","project_id")
  
  def get_query_rel(self,field,rel,value):
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
  
  def get_tab_grid(self, _query, _field_id, _fields=None, _deletable=False, links=None, multi_page=None, rpl_1="", rpl_2="", 
                   _editable=True, _join=None,_paginate=25,_priority="0",_show_count=False):
    try:
      if self.ui.ns.db(_query).select('count(*)',join=_join,left=None, cacheable=True).first()['count(*)']==0:
        return ""
      if multi_page!=None:
        self.ui.ns.request.vars.page=self.ui.ns.request.vars[str(multi_page)]
      else:
        self.ui.ns.request.vars.page=None
      view_grid = SimpleGrid.grid(query=_query, field_id=_field_id, fields=_fields, 
               groupfields=None, groupby=None, left=None, having=None, join=_join,
               orderby=_field_id, sortable=False, paginate=_paginate, maxtextlength=20,
               showbuttontext=False, deletable=_deletable, editable=_editable, links=links)
      table = view_grid.elements("div.web2py_table")
      if len(table)==0:
        return ""
      elif type(table[0][0][0]).__name__!="TABLE":
        return ""
      else:
        if self.ui.ns.session.mobile:
          self.ui.control.set_htmltable_style(table[0][0][0],multi_page,_priority)
        if multi_page!=None:
          if view_grid[len(view_grid)-1]["_class"].startswith("web2py_paginator"):
            pages = view_grid[len(view_grid)-1].elements("a")
            for i in range(len(pages)):
              if pages[i]["_href"]:
                pages[i]["_href"] = pages[i]["_href"].replace(rpl_1,rpl_2).replace("page=",str(multi_page)+"=")
                pages[i]["_data-ajax"] = "false"
        if not _show_count:
          view_grid.__delitem__(0)
        return view_grid
    except Exception:
      return ""
  
  def get_tool_selector(self,tool_serial,error_label=False):
    audit_filter = self.ui.connect.get_audit_filter("tool", None)[0]
    if audit_filter!="disabled":
      return self.get_base_selector(fieldtype="tool", search_url=URL("dlg_tool"),
                            label_id="tool_serial",
                            label_url="'"+URL("frm_tool/view/tool")+"/'+document.getElementById('tool_id').value",
                            label_txt=tool_serial,value_id="tool_id",error_label=error_label)
    else:
      return self.ui.control.get_disabled_label(tool_serial,"tool_serial","tool_id")
  
  def get_transitem_selector(self,reftrans_transnumber,error_label=False):
    return self.get_base_selector(fieldtype="transitem", search_url=URL("dlg_transitem_all"),
                            label_id="reftrans_transnumber",
                            label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('trans_id').value",
                            label_txt=reftrans_transnumber,value_id="trans_id",error_label=error_label)
  
  def get_transmovement_selector(self,reftrans_transnumber,error_label=False):
    return self.get_base_selector(fieldtype="transmovement", search_url=URL("dlg_transmovement_all"),
                            label_id="reftrans_transnumber",
                            label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('trans_id').value",
                            label_txt=reftrans_transnumber,value_id="trans_id",error_label=error_label) 
              
  def get_transpayment_selector(self,reftrans_transnumber,error_label=False):
    return self.get_base_selector(fieldtype="transpayment", search_url=URL("dlg_transpayment_all"),
                            label_id="reftrans_transnumber",
                            label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('trans_id').value",
                            label_txt=reftrans_transnumber,value_id="trans_id",error_label=error_label)
    
  def init_sfilter(self, sfilter_name):
    if not self.ui.ns.session[sfilter_name]:
      self.ui.ns.session[sfilter_name] = {}
    if len(self.ui.ns.request.post_vars)>0:
      if len(self.ui.ns.session[sfilter_name])==0:
        empty_post = True
      else:
        empty_post = False
      if self.ui.ns.request.post_vars["bool_filter_value"]:
        self.ui.ns.session[sfilter_name]["bool_filter_value"]=self.ui.ns.request.post_vars.bool_filter_value
      for filter_key in self.ui.ns.request.post_vars.keys():
        if self.ui.ns.request.post_vars[filter_key] and self.ui.ns.request.post_vars[filter_key]!="":
          empty_post = False
        if filter_key in("date_filter_value_1","date_filter_value_2","date_filter_value_3"):
          try:
            if self.ui.ns.request.post_vars[str(filter_key).replace("value", "name")]!="":
              dt = str(self.ui.ns.request.post_vars[filter_key]).split("-")
              self.ui.ns.session[sfilter_name][filter_key] = datetime.date(int(dt[0]), int(dt[1]), int(dt[2]))
          except:
            self.ui.ns.session[sfilter_name][filter_key] = None
        else:
          if self.ui.ns.request.post_vars[str(filter_key).replace("value", "name")]!="":
            self.ui.ns.session[sfilter_name][filter_key]=self.ui.ns.request.post_vars[filter_key]
      if empty_post:
        self.ui.ns.session[sfilter_name] = {}     
  
  def set_transfilter(self,query,alias=None,fieldname="cruser_id"):
    groups_nervatype_id = self.ui.ns.valid.get_groups_id("nervatype", "groups")
    filterlink = self.ui.ns.db((self.ui.ns.db.link.ref_id_1==self.ui.ns.db.employee(id=self.ui.ns.session.auth.user.id).usergroup)&(self.ui.ns.db.link.nervatype_1==groups_nervatype_id)
                    &(self.ui.ns.db.link.nervatype_2==groups_nervatype_id)&(self.ui.ns.db.link.deleted==0)).select().as_list()
    if len(filterlink)>0:
      transfilter = self.ui.ns.db.groups(id=filterlink[0]["ref_id_2"]).groupvalue
    else:
      transfilter = "all"
    if not alias: alias = self.ui.ns.db.trans
    if transfilter=="usergroup":
      query = query & (alias[fieldname].belongs(self.ui.ns.db((self.ui.ns.db.employee.usergroup==self.ui.ns.db.employee(id=self.ui.ns.session.auth.user.id).usergroup)&(self.ui.ns.db.employee.deleted==0)).select(self.ui.ns.db.employee.id)))
    elif transfilter=="own":
      query = query & (alias[fieldname]==self.ui.ns.session.auth.user.id)
    return query
  
  def set_view_fields(self, nervatype_name, nervatype_id, tab_index, editable, query, ref_id, rpl_1, rpl_2, add_view_fields=True): 
    def get_fieldlabel(value,row):
        try:
          return self.ui.ns.valid.get_represent(self.ui.ns.db.fieldvalue.value,value,row,True)
        except Exception:
          return value
    if add_view_fields:
      fields=[self.ui.ns.db.deffield.description, self.ui.ns.db.fieldvalue.value, self.ui.ns.db.fieldvalue.notes]  
    fieldvalue_count = self.ui.ns.db(query).select('count(*)',join=None,left=None, cacheable=True).first()['count(*)']
    
    if self.ui.ns.session.mobile:
      links = None
      self.ui.response.menu_fields = self.ui.control.get_mobil_button(self.ui.control.get_bubble_label(self.ui.ns.T("Additional Data"),fieldvalue_count), href="#", cformat=None, icon="grid", style="text-align: left;",
        onclick= "show_page('fieldvalue_page');",
        theme="a", rel="close")
      self.ui.response.cmd_fieldvalue_close = self.ui.control.get_mobil_button(label=self.ui.ns.T("BACK"), href="#",
          icon="back", ajax="true", theme="a",  
          onclick= "show_page('fieldvalue_page');", rel="close")
      self.ui.ns.db.deffield.description.represent = lambda value,row: self.ui.control.get_mobil_button(value, href="#", cformat=None, icon=None, iconpos=None, style="text-align: left;",
                            onclick="set_fieldvalue("
                           +str(row["fieldvalue"]["id"])+",'"
                           +str(self.ui.ns.db.fieldvalue(id=row["fieldvalue"]["id"]).fieldname)+"','"
                           +json.dumps(str(row["deffield"]["description"]))[1:-1]+"','"
                           +json.dumps(str(row["fieldvalue"]["value"]))[1:-1]+"','"
                           +json.dumps(str(get_fieldlabel(row["fieldvalue"]["value"],row)))[1:-1]+"','"
                           +json.dumps(str(row["fieldvalue"]["notes"]))[1:-1]+"','"
                           +self.ui.ns.db.groups(id=self.ui.ns.db.deffield(fieldname=self.ui.ns.db.fieldvalue(id=row["fieldvalue"]["id"]).fieldname).fieldtype).groupvalue+"','"
                           +json.dumps(str(self.ui.ns.db.deffield(fieldname=self.ui.ns.db.fieldvalue(id=row["fieldvalue"]["id"]).fieldname).valuelist))[1:-1]+"',"
                           +str(self.ui.ns.db.deffield(fieldname=self.ui.ns.db.fieldvalue(id=row["fieldvalue"]["id"]).fieldname).readonly)
                           +")", theme="d")
    else:
      self.ui.response.fieldvalue_icon = URL(self.ui.dir_images,'icon16_deffield.png')
      self.ui.response.cmd_fieldvalue_cancel = A(SPAN(_class="icon cross"), _id="cmd_fieldvalue_cancel", 
        _style="height: 15px;",
        _class="w2p_trap buttontext button", _href="#", _title=self.ui.ns.T('Cancel update'), 
        _onclick= "document.getElementById('edit_fieldvalue').style.display = 'none';document.getElementById('frm_head').style.display = 'block';return true;")
      links = [lambda row:A(SPAN(_class="icon pen"), _style="padding-top: 3px;padding-left: 5px;padding-right: 4px;padding-bottom: 3px;", 
                           _class="w2p_trap buttontext button", _href="#", _onclick="set_fieldvalue("
                           +str(row["fieldvalue"]["id"])+",'"
                           +str(self.ui.ns.db.fieldvalue(id=row["fieldvalue"]["id"]).fieldname)+"','"
                           +json.dumps(str(row["deffield"]["description"]))[1:-1]+"','"
                           +json.dumps(str(row["fieldvalue"]["value"]))[1:-1]+"','"
                           +json.dumps(str(get_fieldlabel(row["fieldvalue"]["value"],row)))[1:-1]+"','"
                           +json.dumps(str(row["fieldvalue"]["notes"]))[1:-1]+"','"
                           +self.ui.ns.db.groups(id=self.ui.ns.db.deffield(fieldname=self.ui.ns.db.fieldvalue(id=row["fieldvalue"]["id"]).fieldname).fieldtype).groupvalue+"','"
                           +json.dumps(str(self.ui.ns.db.deffield(fieldname=self.ui.ns.db.fieldvalue(id=row["fieldvalue"]["id"]).fieldname).valuelist))[1:-1]+"',"
                           +str(self.ui.ns.db.deffield(fieldname=self.ui.ns.db.fieldvalue(id=row["fieldvalue"]["id"]).fieldname).readonly)
                           +")",
                           _title=self.ui.ns.T("Edit field"))]
    
    if editable==False:
      if self.ui.ns.session.mobile:
        self.ui.response.cmd_fieldvalue_new = ""
      else:
        self.ui.response.cmd_fieldvalue_new = SPAN(" ",SPAN(str(fieldvalue_count), _class="detail_count"))
      self.ui.response.cmd_fields = "" 
      self.ui.response.cmb_fields = ""
      self.ui.response.cmd_fieldvalue_update = ""
      self.ui.response.cmd_fieldvalue_delete = ""
    else:
      if self.ui.ns.session.mobile:
        self.ui.response.cmd_fieldvalue_new = self.ui.control.get_mobil_button(cmd_id="cmd_fieldvalue_new",
          label=self.ui.ns.T("New Data"), href="#", 
          cformat=None, style="text-align: left;", icon="plus", ajax="true", theme="b",
          onclick= "set_fieldvalue(-1, '', '', '', '', '', '', '', 0);", rel="close")
        self.ui.response.cmd_fields = self.ui.control.get_mobil_button(label=self.ui.ns.T("Edit Additional Data"), href="#", 
          icon="gear", cformat=None, ajax="true", theme="b", rel="close",
          onclick= "javascript:if(confirm('"+self.ui.ns.T("Any unsaved changes will be lost. Do you want to continue?")
              +"')){window.location ='"+URL("frm_deffield_"+nervatype_name+"?back=1")+"';};return false;")
        self.ui.response.cmd_fieldvalue_update = self.ui.control.get_mobil_button(
          label=self.ui.ns.T("Save Data"), href="#", 
          cformat=None, style="text-align: left;", icon="check", ajax="false", theme="b",
          onclick= "fieldvalue_update();return true;")
      else:
        self.ui.response.cmd_fieldvalue_new = self.ui.control.get_tabnew_button(fieldvalue_count,self.ui.ns.T('New Additional Data'),cmd_id="cmd_fieldvalue_new",
                                cmd = "$('#tabs').tabs({ active: "+str(tab_index)+" });set_fieldvalue(-1, '', '', '', '', '', '', '', 0)")
        self.ui.response.cmd_fields = self.ui.control.get_goprop_button(title=self.ui.ns.T("Edit Additional Data"), url=URL("frm_deffield_"+nervatype_name+"?back=1"))
        self.ui.response.cmd_fieldvalue_update = self.ui.control.get_command_button(caption=self.ui.ns.T("Save"),title=self.ui.ns.T("Update data"),color="008B00", _id="cmd_field_submit",
                              cmd="fieldvalue_update();return true;")
      self.ui.response.cmb_fields = self.ui.control.get_cmb_fields(nervatype_id)
      if add_view_fields:
        if self.ui.ns.session.mobile:
          self.ui.response.cmd_fieldvalue_delete = self.ui.control.get_mobil_button(cmd_id="cmd_fieldvalue_delete",
            label=self.ui.ns.T("Delete Data"), href="#", 
            cformat=None, style="text-align: left;", icon="delete", ajax="false", theme="b", rel="close",
            onclick= "if(confirm('"+self.ui.ns.T('Are you sure you want to delete this data?')+
                              "')){if(document.getElementById('fieldvalue_id').value>-1){window.location = '"
              +URL("frm_"+nervatype_name)+"/delete/fieldvalue/'+document.getElementById('fieldvalue_id').value;} else {show_page('fieldvalue_page');}}")
        else:
          links.append(lambda row: A(SPAN(_class="icon trash"), _style="padding-top: 3px;padding-left: 4px;padding-right: 4px;padding-bottom: 3px;", 
                         _class="w2p_trap buttontext button", _href="#", _onclick="if(confirm('"+self.ui.ns.T('Are you sure you want to delete this data?')+
                              "')){window.location ='"+URL("frm_"+nervatype_name+"/delete/fieldvalue/"+str(row["fieldvalue"]["id"]))+"';};return false;", 
                         _title=self.ui.ns.T("Delete Additional Data")))
    
    setting_audit_filter = self.ui.connect.get_audit_filter("setting", None)[0]
    if setting_audit_filter=="disabled":
      self.ui.response.cmd_fields = ""
      
    if add_view_fields:
      self.ui.response.view_fields = self.get_tab_grid(_query=query, _field_id=self.ui.ns.db.fieldvalue.id, _fields=fields, _deletable=False, _editable=False, links=links, 
                               multi_page="fieldvalue_page", rpl_1=rpl_1, rpl_2=rpl_2,_priority="0,1")
    
    self.ui.response.fieldvalue_form = SQLFORM(self.ui.ns.db.fieldvalue, submit_button=self.ui.ns.T("Save"),_id="frm_fieldvalue")
    self.ui.response.fieldvalue_form.process()    
    self.ui.response.fieldvalue_id = INPUT(_name="id", _type="hidden", _value="", _id="fieldvalue_id")
    self.ui.response.fieldvalue_ref_id = INPUT(_name="ref_id", _type="hidden", _value=ref_id, _id="fieldvalue_ref_id")
    self.ui.response.fieldvalue_fieldname = INPUT(_name="fieldname", _type="hidden", _value="", _id="fieldvalue_fieldname")
    self.ui.response.fieldvalue_fieldtype = INPUT(_name="fieldtype", _type="hidden", _value="", _id="fieldvalue_fieldtype")
    self.ui.response.fieldvalue_readonly = INPUT(_name="readonly", _type="hidden", _value="", _id="fieldvalue_readonly")
    
    audit_filter = self.ui.connect.get_audit_filter("customer", None)[0]
    if audit_filter!="disabled":
      self.ui.response.fieldvalue_customer_selector = self.get_base_selector(fieldtype="customer", search_url=URL("dlg_customer"),
                            label_id="fieldvalue_value_customer_label", 
                            label_url="'"+URL("frm_customer/view/customer")+"/'+document.getElementById('fieldvalue_value').value",
                            label_txt="",value_id="fieldvalue_value",error_label=False, div_id="fieldvalue_value_customer")
    else:
      self.ui.response.fieldvalue_customer_selector = self.ui.control.get_disabled_label("","fieldvalue_value_customer_label","fieldvalue_value_customer")
    
    audit_filter = self.ui.connect.get_audit_filter("tool", None)[0]
    if audit_filter!="disabled":
      self.ui.response.fieldvalue_tool_selector = self.get_base_selector(fieldtype="tool",search_url=URL("dlg_tool"),
                          label_id="fieldvalue_value_tool_label",
                          label_url="'"+URL("frm_tool/view/tool")+"/'+document.getElementById('fieldvalue_value').value",
                          label_txt="",value_id="fieldvalue_value",error_label=False, div_id="fieldvalue_value_tool")
    else:
      self.ui.response.fieldvalue_tool_selector = self.ui.control.get_disabled_label("","fieldvalue_value_tool_label","fieldvalue_value_tool")
    
    audit_filter = self.ui.connect.get_audit_filter("product", None)[0]
    if audit_filter!="disabled":
      self.ui.response.fieldvalue_product_selector = self.get_base_selector(fieldtype="product",search_url=URL("dlg_product_all"),
                          label_id="fieldvalue_value_product_label",
                          label_url="'"+URL("frm_product/view/product")+"/'+document.getElementById('fieldvalue_value').value",
                          label_txt="",value_id="fieldvalue_value",error_label=False, div_id="fieldvalue_value_product")
    else:
      self.ui.response.fieldvalue_product_selector = self.ui.control.get_disabled_label("","fieldvalue_value_product_label","fieldvalue_value_product")
    
    self.ui.response.fieldvalue_transitem_selector = self.get_base_selector(fieldtype="transitem",search_url=URL("dlg_transitem_all"),
                          label_id="fieldvalue_value_transitem_label",
                          label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('fieldvalue_value').value",
                          label_txt="",value_id="fieldvalue_value",error_label=False, div_id="fieldvalue_value_transitem")  
    self.ui.response.fieldvalue_transpayment_selector = self.get_base_selector(fieldtype="transpayment",search_url=URL("dlg_transpayment_all"),
                          label_id="fieldvalue_value_transpayment_label",
                          label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('fieldvalue_value').value",
                          label_txt="",value_id="fieldvalue_value",error_label=False, div_id="fieldvalue_value_transpayment")
    self.ui.response.fieldvalue_transmovement_selector = self.get_base_selector(fieldtype="transmovement",search_url=URL("dlg_transmovement_all"),
                          label_id="fieldvalue_value_transmovement_label",
                          label_url="'"+URL("frm_trans/view/trans")+"/'+document.getElementById('fieldvalue_value').value",
                          label_txt="",value_id="fieldvalue_value",error_label=False, div_id="fieldvalue_value_transmovement")
    
    audit_filter = self.ui.connect.get_audit_filter("project", None)[0]
    if audit_filter!="disabled":
      self.ui.response.fieldvalue_project_selector = self.get_base_selector(fieldtype="project",search_url=URL("dlg_project"),
                          label_id="fieldvalue_value_project_label",
                          label_url="'"+URL("frm_project/view/project")+"/'+document.getElementById('fieldvalue_value').value",
                          label_txt="",value_id="fieldvalue_value",error_label=False, div_id="fieldvalue_value_project")
    else:
      self.ui.response.fieldvalue_project_selector = self.ui.control.get_disabled_label("","fieldvalue_value_project_label","fieldvalue_value_project")
    
    audit_filter = self.ui.connect.get_audit_filter("employee", None)[0]
    if audit_filter!="disabled":
      self.ui.response.fieldvalue_employee_selector = self.get_base_selector(fieldtype="employee",search_url=URL("dlg_employee"),
                          label_id="fieldvalue_value_employee_label",
                          label_url="'"+URL("frm_employee/view/employee")+"/'+document.getElementById('fieldvalue_value').value",
                          label_txt="",value_id="fieldvalue_value",error_label=False, div_id="fieldvalue_value_employee")
    else:
      self.ui.response.fieldvalue_employee_selector = self.ui.control.get_disabled_label("","fieldvalue_value_employee_label","fieldvalue_value_employee")
    
    self.ui.response.fieldvalue_place_selector = self.get_base_selector(fieldtype="place",search_url=URL("dlg_place_all"),
                          label_id="fieldvalue_value_place_label",
                          label_url="'"+URL("frm_place/view/place")+"/'+document.getElementById('fieldvalue_value').value",
                          label_txt="",value_id="fieldvalue_value",error_label=False, div_id="fieldvalue_value_place")
    return links
                            
class WebUiReport(object):
  
  def __init__(self, ui):
    self.ui = ui

  def create_report(self, template,ref_id,output="html",orientation="P",size="a4"):
    params={}
    filters={}
    params["report_id"]=template
    params["output"]=output
    params["orientation"]=orientation
    params["size"]=size
    filters["@id"]=ref_id
    return self.show_report(output,self.ui.dbout.getReport(params, filters))
  
  def dlg_report(self, _nervatype,_transtype,_direction,ref_id,label,default=None):
    nervatype = self.ui.ns.valid.get_groups_id("nervatype", _nervatype)
    filetype = self.ui.ns.valid.get_groups_id("filetype", "fpdf")
    query = (self.ui.ns.db.ui_report.nervatype==nervatype)&(self.ui.ns.db.ui_report.filetype==filetype)&(self.ui.ns.db.ui_report.repname!=None)
    if _transtype!=None:
      transtype = self.ui.ns.valid.get_groups_id("transtype", _transtype)
      query=query&(self.ui.ns.db.ui_report.transtype==transtype)
    if _direction!=None:
      direction = self.ui.ns.valid.get_groups_id("direction", _direction)
      query=query&(self.ui.ns.db.ui_report.direction==direction)
    
    #disabled reports list
    audit = self.ui.connect.get_audit_subtype("report")
    if len(audit)>0:
      query = query & (~self.ui.ns.db.ui_report.id.belongs(audit))
    
    templates = self.ui.ns.db(query).select(orderby=self.ui.ns.db.ui_report.repname).as_list()
    cmb_templates = SELECT(*[OPTION(field["repname"], _value=field["id"]) for field in templates], 
                           _id="cmb_templates", _name="template",_style="width: 100%;")
    if default!=None:
      for i in range(len(cmb_templates)):
        if cmb_templates[i]["id"]==default:
          cmb_templates[i]["_selected"]=["selected"]
    if len(cmb_templates)==0:
      cmb_templates.insert(0, OPTION("", _value=""))
    orientation = self.ui.ns.db((self.ui.ns.db.groups.groupname=="orientation")&(self.ui.ns.db.groups.deleted==0)&(self.ui.ns.db.groups.inactive==0)).select(orderby=self.ui.ns.db.groups.id)
    cmb_orientation = SELECT(*[OPTION(self.ui.ns.T(ori["description"]), _value=ori["groupvalue"]) for ori in orientation], 
                               _id="cmb_orientation", _name="orientation",_style="width: 100%;")
    size = self.ui.ns.db((self.ui.ns.db.groups.groupname=="papersize")&(self.ui.ns.db.groups.deleted==0)&(self.ui.ns.db.groups.inactive==0)).select(orderby=self.ui.ns.db.groups.id)
    cmb_size = SELECT(*[OPTION(psize["description"], _value=psize["groupvalue"]) for psize in size], 
                               _id="cmb_size", _name="size",_style="width: 100%;;")
    cmb_size[1]["_selected"]=["selected"]
            
    if self.ui.ns.session.mobile:
      rtable = TABLE(_style="width: 100%;",_cellpadding="0px;", _cellspacing="0px;")
      rtable.append(TR(TD(label,
                        _style="background-color: #DBDBDB;font-weight: bold;text-align: center;padding: 8px;")))
      rtable.append(TR(
                     TD(self.ui.ns.T("Output Template"),_style="background-color: #F1F1F1;font-weight: bold;text-align: left;padding: 5px;padding-top: 10px;")))
      rtable.append(TR(TD(cmb_templates, _style="margin: 0px;")))
      rtable.append(TR(
                     TD(self.ui.ns.T("Orientation/Size/Copy"),_style="background-color: #F1F1F1;font-weight: bold;text-align: left;padding: 5px;")))
      rtable.append(TABLE(TR(TD(cmb_orientation, _style="padding-right: 5px;"),
                       TD(cmb_size, _style="padding-right: 5px;"),
                       TD(INPUT(_type="text",_value="1",_name="copy",_id="page_copy",_class="integer",_style="width: 20px;text-align: right;"), _style="width: 20px;")),
                          _style="width: 100%;",_cellpadding="0px;", _cellspacing="0px;"))
      
      rtable_cmd = DIV(_style="background-color: #393939;padding: 10px;") 
      rtable_cmd["_data-role"] = "controlgroup"
      
      cmd_preview = self.ui.control.get_mobil_button(self.ui.ns.T("HTML Preview"), href="#", cformat=None, icon="page", style="text-align: left;padding:0px;margin:0px;border-radius: 0px;border-top-left-radius: 10px;border-top-right-radius:10px;",
                                                onclick="create_report('html','"+self.ui.ns.T("Missing Output Template!")+"');", theme="b")
      rtable_cmd.append(cmd_preview)
      cmd_pdf = self.ui.control.get_mobil_button(self.ui.ns.T("Create PDF"), href="#", cformat=None, icon="page", style="text-align: left;padding:0px;margin:0px;border-radius: 0px;",
                                                onclick="create_report('pdf','"+self.ui.ns.T("Missing Output Template!")+"');", theme="b")
      rtable_cmd.append(cmd_pdf)
      cmd_xml = self.ui.control.get_mobil_button(self.ui.ns.T("Create XML"), href="#", cformat=None, icon="page", style="text-align: left;padding:0px;margin:0px;border-radius: 0px;",
                                                onclick="create_report('xml','"+self.ui.ns.T("Missing Output Template!")+"');", theme="b")
      rtable_cmd.append(cmd_xml)
      cmd_group = self.ui.control.get_mobil_button(self.ui.ns.T("Printer Queue"), href="#", cformat=None, icon="plus", style="text-align: left;padding:0px;margin:0px;border-radius: 0px;border-bottom-left-radius: 10px;border-bottom-right-radius:10px;",
                                                onclick="if(document.getElementById('cmb_templates').value==''){alert('"+self.ui.ns.T("Missing Output Template!")+"');} else {ajax('"+URL("cmd_add_queue")+"?nervatype="+str(nervatype)+"&ref_id="+str(ref_id)
                          +"&qty='+document.getElementById('page_copy').value+'&template='+document.getElementById('cmb_templates').value);alert('"+self.ui.ns.T("The document has been added to the Printing List")+"')}; return false;", theme="b")
      rtable_cmd.append(cmd_group)
      rtable.append(TR(
                       TD(rtable_cmd, _style="padding:0px;")))
      rtable = FORM(rtable, _id="dlg_frm_report", _target="_blank", _action=URL("frm_report_"+_nervatype+"/"+str(ref_id)))
    else:                        
      rtable = TABLE(_style="width: 100%;")
      rtable.append(TR(TD(label,_colspan="2",
                        _style="background-color: #F1F1F1;font-weight: bold;text-align: center;border-bottom: solid;padding: 5px;")))
      rtable.append(TR(
                     TD(self.ui.ns.T("Output Template"),_style="width: 170px;background-color: #F1F1F1;font-weight: bold;text-align: left;padding: 5px;border-bottom: solid;"),
                     TD(cmb_templates, _style="padding: 5px;border-bottom: solid;")))
      rtable.append(TR(
                       TD(
                          TABLE(TR(
                                   TD(self.ui.ns.T("Orientation/Size/Copy"),_style="width: 170px;background-color: #F1F1F1;font-weight: bold;text-align: left;padding: 5px;border-bottom: solid;"),
                                   TD(cmb_orientation, _style="padding: 5px;border-bottom: solid;padding-right: 0px;"),
                                   TD(cmb_size, _style="width: 50px;padding: 5px;border-bottom: solid;"),
                                   TD(INPUT(_type="text",_value="1",_name="copy",_id="page_copy",_class="integer",_style="width: 20px;height: 10px;text-align: right;"), 
                                      _style="width: 20px;padding-right: 5px;padding-left: 0px;border-bottom: solid;")
                                   ),_style="width: 100%;",_cellpadding="0px", _cellspacing="0px"),
                          _colspan="2"
                          )))
      rtable_cmd = TABLE(_style="width: 100%;")
      cmd_preview = INPUT(_type="button", _value="HTML Preview", _style="width: 100%;height: 50px !important;padding-top: 5px !important;",
                        _onclick="create_report('html','"+self.ui.ns.T("Missing Output Template!")+"');")
      cmd_pdf = INPUT(_type="button", _value="Create PDF", _style="width: 100%;height: 50px !important;padding-top: 5px !important;",
                        _onclick="create_report('pdf','"+self.ui.ns.T("Missing Output Template!")+"');")
      rtable_cmd.append(TR(
                     TD(cmd_preview,_colspan="2", _style="padding:0px;padding-top:5px;padding-right:2px;"),
                     TD(cmd_pdf,_style="width: 50%;padding:0px;padding-top:5px;padding-left:2px;")))
      cmd_xml = INPUT(_type="button", _value="Create XML", _style="width: 100%;height: 50px !important;padding-top: 5px !important;",
                        _onclick="create_report('xml','"+self.ui.ns.T("Missing Output Template!")+"');")
      cmd_group = INPUT(_type="button", _value="Printer queue", _style="width: 100%;height: 50px !important;padding-top: 5px !important;",
                        _onclick="if(document.getElementById('cmb_templates').value==''){alert('"+self.ui.ns.T("Missing Output Template!")+"');} else {ajax('"+URL("cmd_add_queue")+"?nervatype="+str(nervatype)+"&ref_id="+str(ref_id)
                        +"&qty='+document.getElementById('page_copy').value+'&template='+document.getElementById('cmb_templates').value);alert('"+self.ui.ns.T("The document has been added to the Printing List")+"')}; return false;")
      rtable_cmd.append(TR(
                     TD(cmd_xml,_colspan="2", _style="padding:0px;padding-right:2px;border-bottom: solid;"),
                     TD(cmd_group,_style="width: 50%;padding:0px;padding-left:2px;border-bottom: solid;")))
      rtable.append(TR(
                     TD(rtable_cmd,
                        INPUT(_name="report_url", _type="hidden", _value=URL("frm_report_"+_nervatype+"/"+str(ref_id)), _id="report_url"),
                        _colspan="4", _style="padding:0px;")))
    return DIV(rtable, _id="dlg_report")
  
  def export_csv(self, filename,query,left,fields,orderby,keywords,join=None,groupfields=None,groupby=None,having=None):
    dbset = self.ui.ns.db(query)
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
        if self.ui.ns.db[col._tablename][col.name].represent:
          try:
            rep_value=self.ui.ns.valid.get_represent(self.ui.ns.db[col._tablename][col.name],value,Storage(orows[i]),True)
            if rows[i].has_key(col._tablename):
              rows[i][col._tablename][col.name] = rep_value
            else:
              rows[i][col.name] = rep_value
          except Exception:
            pass
    raise HTTP(200,str(rows),**{'Content-Type':'text/csv','Content-Disposition':'attachment;filename='+filename+'.csv;'})
  
  def export_excel(self, sheetname,query,left,fields,orderby,keywords,join=None,groupfields=None,groupby=None,having=None):
    from xlwt import Workbook
    
    output = StringIO()
    book = Workbook(encoding='utf-8')
    styles = self.ui.dbout.estyles
    
    sheet1 = book.add_sheet(sheetname)     
    colnum = 0
    for col in fields:
      if str(col.name)!="id":
        sheet1.write(0, colnum, str(col.label), styles["header"])
        colnum = colnum + 1
    dbset = self.ui.ns.db(query)
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
        if self.ui.ns.db[col._tablename][col.name].represent:
          try:
            rep_value=str(self.ui.ns.valid.get_represent(self.ui.ns.db[col._tablename][col.name],value,Storage(row),True))
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
    self.ui.response.headers['Content-Type'] = "application/vnd.ms-excel"
    self.ui.response.headers['Content-Disposition'] = 'attachment;filename="NervaturaExport.xls"'
    return contents  
  
  def show_report(self, output, report_tmp):
    if type(report_tmp).__name__=="str":
      if report_tmp=="NODATA":
        return HTML(HEAD(TITLE(self.ui.response.title),
                     LINK(_rel="shortcut icon", _href=URL('static','favicon.ico'), _type="image/x-icon")),
                BODY(DIV(CENTER(TABLE(TR(TD(IMG(_src=URL('static','images/nodata.png'),
                                        _style="border: solid;border-color: #FFFFFF;"),
                              _style="text-align: center;vertical-align: middle;font-weight: bold;font-family: Arial, Helvetica,  sans-serif;font-size: 20px;")),
                        _style="background-color:#FFFFFF;color:#444444;margin-top:200px;")),_style="width:100%;height:100%")),_style="background-color:#000000;")
      else:
        return report_tmp
    
    if report_tmp["filetype"]=="html":
      self.ui.response.view = "default/report.html"
      self.ui.response.title = report_tmp["data"]["title"]
      self.ui.response.subtitle = ""
      report_tmp["template"]=self.ui.response.render(StringIO(report_tmp["template"]),report_tmp["data"])
      return dict(template=XML(report_tmp["template"]))
    elif report_tmp["filetype"]=="fpdf":
      if output=="xml":
        self.ui.response.headers['Content-Type']='text/xml'
      elif output=="pdf":
        self.ui.response.headers['Content-Type']='application/pdf'
      return report_tmp["template"]
    elif report_tmp["filetype"]=="xls":
        self.ui.response.headers['Content-Type'] = "application/vnd.ms-excel"
        self.ui.response.headers['Content-Disposition'] = 'attachment;filename="NervaturaReport.xls"'
        return report_tmp["template"]
    else:
      return report_tmp["template"]

class WebUiMenu(object):
  
  def __init__(self, ui):
    self.ui = ui
  
  def create_menu(self):
    ns_menu = []
    if not self.ui.ns.session.mobile:
      ns_menu.append((self.ui.ns.T('HOME'), False, URL('index'), []))
    ns_menu_trans = (self.ui.ns.T('TRANSACTIONS'), False, None, [])
    ns_menu.append(ns_menu_trans)
    ns_menu_res = (self.ui.ns.T('RESOURCES'), False, None, [])
    ns_menu.append(ns_menu_res)
    ns_menu.append((self.ui.ns.T('REPORTS'), False, URL('frm_reports'), []))
    ns_menu_admin = (self.ui.ns.T('ADMIN'), False, None, [])
    ns_menu.append(ns_menu_admin)
    ns_menu_program = (self.ui.ns.T('PROGRAM'), False, None, [])
    ns_menu.append(ns_menu_program)
    if not self.ui.ns.session.mobile:
      ns_menu.append((self.ui.ns.T('EXIT'), False, URL('frm_logout'), []))
    if self.ui.ns.session.auth!=None:
       
      #TRANSACTIONS
      mnu_operation = (self.ui.ns.T('DOCUMENTS'), False, None, [])
      audit_filter = self.ui.connect.get_audit_filter("trans", "offer")[0]
      if audit_filter=="all":
        mnu_offer = (self.ui.ns.T('OFFER'), False, None, [])
        mnu_offer[3].append((self.ui.ns.T('New Customer Offer'), False, URL('frm_trans/new/trans/offer/out'), []))
        mnu_offer[3].append((self.ui.ns.T('New Supplier Offer'), False, URL('frm_trans/new/trans/offer/in'), []))
        mnu_operation[3].append(mnu_offer)
       
      audit_filter = self.ui.connect.get_audit_filter("trans", "order")[0]
      if audit_filter=="all":
        mnu_order = (self.ui.ns.T('ORDER'), False, None, [])
        mnu_order[3].append((self.ui.ns.T('New Customer Order'), False, URL('frm_trans/new/trans/order/out'), []))
        mnu_order[3].append((self.ui.ns.T('New Supplier Order'), False, URL('frm_trans/new/trans/order/in'), []))
        mnu_operation[3].append(mnu_order)
       
      audit_filter = self.ui.connect.get_audit_filter("trans", "worksheet")[0]
      if audit_filter=="all":
        mnu_worksheet = (self.ui.ns.T('WORKSHEET'), False, None, [])
        mnu_worksheet[3].append((self.ui.ns.T('New Worksheet'), False, URL('frm_trans/new/trans/worksheet/out'), []))
        mnu_operation[3].append(mnu_worksheet)
       
      audit_filter = self.ui.connect.get_audit_filter("trans", "rent")[0]
      if audit_filter=="all":
        mnu_rent = (self.ui.ns.T('RENTAL'), False, None, [])
        mnu_rent[3].append((self.ui.ns.T('New Customer Rental'), False, URL('frm_trans/new/trans/rent/out'), []))
        mnu_rent[3].append((self.ui.ns.T('New Supplier Rental'), False, URL('frm_trans/new/trans/rent/in'), []))
        mnu_operation[3].append(mnu_rent)
       
      audit_filter = self.ui.connect.get_audit_filter("trans", "invoice")[0]
      audit_filter2 = self.ui.connect.get_audit_filter("trans", "receipt")[0]
      if audit_filter=="all" or audit_filter2=="all":
        mnu_invoice = (self.ui.ns.T('INVOICE'), False, None, [])
        if audit_filter=="all":
          mnu_invoice[3].append((self.ui.ns.T('New Cust. Invoice'), False, URL('frm_trans/new/trans/invoice/out'), []))
          mnu_invoice[3].append((self.ui.ns.T('New Supplier Invoice'), False, URL('frm_trans/new/trans/invoice/in'), []))
        if audit_filter2=="all":
          mnu_invoice[3].append((self.ui.ns.T('New Receipt'), False, URL('frm_trans/new/trans/receipt/out'), []))
        mnu_operation[3].append(mnu_invoice)
      mnu_operation[3].append(("divider", False, "divider", []))
      mnu_operation[3].append((SPAN(self.ui.ns.T('Quick Search')), False, URL('frm_quick_transitem_all'), []))
      mnu_operation[3].append((self.ui.ns.T('Documents Browser'), False, URL('find_transitem_trans'), []))
      ns_menu_trans[3].append(mnu_operation)
       
      audit_filter = self.ui.connect.get_audit_filter("trans", "bank")[0]
      audit_filter2 = self.ui.connect.get_audit_filter("trans", "cash")[0]
      if audit_filter!="disabled" or audit_filter2!="disabled":
        mnu_payment = (self.ui.ns.T('PAYMENT'), False, None, [])
        if audit_filter=="all":
          mnu_payment[3].append((self.ui.ns.T('New Bank Statement'), False, URL('frm_trans/new/trans/bank/transfer'), []))
        if audit_filter2=="all":
          mnu_payment[3].append((self.ui.ns.T('New Cash'), False, URL('frm_trans/new/trans/cash/out'), []))
        if audit_filter=="all" or audit_filter2=="all":
          mnu_payment[3].append(("divider", False, "divider", []))
        mnu_payment[3].append((SPAN(self.ui.ns.T('Quick Search')), False, URL('frm_quick_payment'), []))
        mnu_payment[3].append((self.ui.ns.T('Payment Browser'), False, URL('find_payment_payment'), []))
        ns_menu_trans[3].append(mnu_payment)
       
      audit_filter_delivery = self.ui.connect.get_audit_filter("trans", "delivery")[0]
      audit_filter_inventory = self.ui.connect.get_audit_filter("trans", "inventory")[0]
      audit_filter_waybill = self.ui.connect.get_audit_filter("trans", "waybill")[0]
      audit_filter_production = self.ui.connect.get_audit_filter("trans", "production")[0]
      audit_filter_formula = self.ui.connect.get_audit_filter("trans", "formula")[0]
      if audit_filter_delivery!="disabled" or audit_filter_inventory!="disabled" or audit_filter_waybill!="disabled" or audit_filter_production!="disabled":
        mnu_stock = (self.ui.ns.T('STOCK CONTROL'), False, None, [])
        if audit_filter_delivery!="disabled" or audit_filter_inventory!="disabled":
          mnu_inventory = (self.ui.ns.T('INVENTORY'), False, None, [])
          if audit_filter_delivery=="all":
            mnu_inventory[3].append((self.ui.ns.T('New Delivery'), False, URL('frm_quick_transitem_delivery'), []))
          if audit_filter_inventory=="all":
            mnu_inventory[3].append((self.ui.ns.T('New Correction'), False, URL('frm_trans/new/trans/inventory/transfer'), []))
          if audit_filter_delivery=="all":
            mnu_inventory[3].append((self.ui.ns.T('New Stock Transfer'), False, URL('frm_trans/new/trans/delivery/transfer'), []))
          mnu_stock[3].append(mnu_inventory)
        if audit_filter_waybill=="all":
          mnu_waybill = (self.ui.ns.T('TOOL MOVEMENT'), False, None, [])
          mnu_waybill[3].append((self.ui.ns.T('New Tool Movement'), False, URL('frm_trans/new/trans/waybill/out'), []))
          mnu_stock[3].append(mnu_waybill)
        if audit_filter_production=="all" or audit_filter_formula=="all":
          mnu_production = (self.ui.ns.T('PRODUCTION'), False, None, [])
          if audit_filter_production=="all":
            mnu_production[3].append((self.ui.ns.T('New Production'), False, URL('frm_trans/new/trans/production/transfer'), []))
          if audit_filter_formula=="all":
            mnu_production[3].append((self.ui.ns.T('New Formula'), False, URL('frm_trans/new/trans/formula/transfer'), []))
          mnu_stock[3].append(mnu_production)
        mnu_stock[3].append(("divider", False, "divider", []))
        mnu_stock[3].append((SPAN(self.ui.ns.T('Quick Search')), False, URL('frm_quick_movement'), []))
        mnu_stock[3].append((self.ui.ns.T('Stock Browser'), False, URL('find_movement_inventory'), []))
        ns_menu_trans[3].append(mnu_stock)
       
      mnu_office = (self.ui.ns.T('BACK OFFICE'), False, None, [])
      mnu_office[3].append((self.ui.ns.T('Printer Queue'), False, URL('frm_printqueue'), []))
      menucmd = self.ui.ns.db().select(self.ui.ns.db.ui_menu.ALL)
      if len(menucmd)>0:
        mnu_office[3].append(("divider", False, "divider", []))
      for cmd in menucmd:
        audit_filter_menu = self.ui.connect.get_audit_filter("menu", cmd["menukey"])[0]
        if audit_filter_menu!="disabled":
          mnu_office[3].append((self.ui.ns.T(cmd["description"]), False, "javascript:call_menucmd('"+cmd["menukey"]+"',"+str(cmd["url"])+");", []))
      ns_menu_trans[3].append(mnu_office)
       
      #RESOURCES
      audit_filter = self.ui.connect.get_audit_filter("customer", None)[0]
      if audit_filter!="disabled":
        mnu_customer = (self.ui.ns.T('CUSTOMER'), False, None, [])
        if audit_filter=="all":
          mnu_customer[3].append((self.ui.ns.T('New Customer'), False, URL('frm_customer/new/customer'), []))
          mnu_customer[3].append(("divider", False, "divider", []))
        mnu_customer[3].append((SPAN(self.ui.ns.T('Quick Search')), False, URL('frm_quick_customer'), []))
        mnu_customer[3].append((self.ui.ns.T('Customer Browser'), False, URL('find_customer_customer'), []))
        ns_menu_res[3].append(mnu_customer)
       
      audit_filter = self.ui.connect.get_audit_filter("product", None)[0]
      if audit_filter!="disabled":
        mnu_product = (self.ui.ns.T('PRODUCT'), False, None, [])
        if audit_filter=="all":
          mnu_product[3].append((self.ui.ns.T('New Product'), False, URL('frm_product/new/product'), []))
          mnu_product[3].append(("divider", False, "divider", []))
        mnu_product[3].append((SPAN(self.ui.ns.T('Quick Search')), False, URL('frm_quick_product'), []))
        mnu_product[3].append((self.ui.ns.T('Product Browser'), False, URL('find_product_product'), []))
        ns_menu_res[3].append(mnu_product)
       
      audit_filter = self.ui.connect.get_audit_filter("employee", None)[0]
      if audit_filter!="disabled":
        mnu_employee = (self.ui.ns.T('EMPLOYEE'), False, None, [])
        if audit_filter=="all":
          mnu_employee[3].append((self.ui.ns.T('New Employee'), False, URL('frm_employee/new/employee'), []))
          mnu_employee[3].append(("divider", False, "divider", []))
        mnu_employee[3].append((SPAN(self.ui.ns.T('Quick Search')), False, URL('frm_quick_employee'), []))
        mnu_employee[3].append((self.ui.ns.T('Employee Browser'), False, URL('find_employee_employee'), []))
        ns_menu_res[3].append(mnu_employee)
       
      audit_filter = self.ui.connect.get_audit_filter("tool", None)[0]
      if audit_filter!="disabled":
        mnu_tool = (self.ui.ns.T('TOOL'), False, None, [])
        if audit_filter=="all":
          mnu_tool[3].append((self.ui.ns.T('New Tool'), False, URL('frm_tool/new/tool'), []))
          mnu_tool[3].append(("divider", False, "divider", []))
        mnu_tool[3].append((SPAN(self.ui.ns.T('Quick Search')), False, URL('frm_quick_tool'), []))
        mnu_tool[3].append((self.ui.ns.T('Tool Browser'), False, URL('find_tool_tool'), []))
        ns_menu_res[3].append(mnu_tool)
       
      audit_filter = self.ui.connect.get_audit_filter("project", None)[0]
      if audit_filter!="disabled":
        mnu_project = (self.ui.ns.T('PROJECT'), False, None, [])
        if audit_filter=="all":
          mnu_project[3].append((self.ui.ns.T('New Project'), False, URL('frm_project/new/project'), []))
          mnu_project[3].append(("divider", False, "divider", []))
        mnu_project[3].append((SPAN(self.ui.ns.T('Quick Search')), False, URL('frm_quick_project'), []))
        mnu_project[3].append((self.ui.ns.T('Project Browser'), False, URL('find_project_project'), []))
        ns_menu_res[3].append(mnu_project)
         
      #ADMIN
      audit_filter_setting = self.ui.connect.get_audit_filter("setting", None)[0]
      audit_filter_audit = self.ui.connect.get_audit_filter("audit", None)[0]
      if audit_filter_setting!="disabled":
        mnu_settings = (self.ui.ns.T('SETTINGS'), False, None, [])
        mnu_settings[3].append((self.ui.ns.T('Database Settings'), False, URL('frm_setting'), []))
        mnu_settings[3].append((self.ui.ns.T('Trans. Numbering'), False, URL('frm_numberdef'), []))
        if audit_filter_audit!="disabled":
          mnu_settings[3].append((self.ui.ns.T('Access Rights'), False, URL('frm_groups_usergroup'), []))
        mnu_settings[3].append((self.ui.ns.T('Server Printers'), False, URL('frm_quick_tool_printer'), []))
        mnu_settings[3].append((self.ui.ns.T('Menu Shortcuts'), False, URL('frm_quick_menucmd'), []))
        mnu_settings[3].append((self.ui.ns.T('Database Logs'), False, URL('find_log'), []))
        ns_menu_admin[3].append(mnu_settings)
        mnu_more = (self.ui.ns.T('MORE DATA'), False, None, [])
        mnu_more[3].append((self.ui.ns.T('Additional Data'), False, URL('frm_deffield_all?back=1'), []))
        mnu_more[3].append((self.ui.ns.T('Groups'), False, URL('frm_groups_all?back=1'), []))
        mnu_more[3].append((self.ui.ns.T('Place'), False, URL('frm_quick_place?back=1'), []))
        mnu_more[3].append((self.ui.ns.T('Currency'), False, URL('frm_currency?back=1'), []))
        mnu_more[3].append((self.ui.ns.T('Tax'), False, URL('frm_tax?back=1'), []))
        mnu_more[3].append((self.ui.ns.T('Interest and Rate'), False, URL('find_rate'), []))
        ns_menu_admin[3].append(mnu_more)
        ns_menu_admin[3].append((self.ui.ns.T('COMPANY'), False, URL('frm_customer/view/customer/'+str(self.ui.ns.valid.get_own_customer().id)), []))
       
      #PROGRAM
      ns_menu_program[3].append((self.ui.ns.T('Change Password'), False, URL('frm_password/'+str(self.ui.ns.session.auth.user.id)), []))
    self.ui.response.ns_menu = ns_menu
  
  def set_find_customer_menu(self):
    self.ui.response.lo_menu = []
    if self.ui.ns.session.mobile:
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Customer Data'), href=URL('find_customer_customer'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Additional Data'), href=URL('find_customer_fields'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Contact Persons'), href=URL('find_customer_contact'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Addresses'), href=URL('find_customer_address'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Groups'), href=URL('find_customer_groups'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      audit_filter = self.ui.connect.get_audit_filter("event", None)[0]
      if audit_filter!="disabled":
        self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Events'), href=URL('find_customer_event'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
    else:
      mnu_customer = (self.ui.ns.T('CUSTOMER VIEWS'), False, None, [])
      mnu_customer[3].append((self.ui.ns.T('Customer Data'), False, URL('find_customer_customer'), []))
      mnu_customer[3].append((self.ui.ns.T('Additional Data'), False, URL('find_customer_fields'), []))
      mnu_customer[3].append((self.ui.ns.T('Contact Persons'), False, URL('find_customer_contact'), []))
      mnu_customer[3].append((self.ui.ns.T('Addresses'), False, URL('find_customer_address'), []))
      mnu_customer[3].append((self.ui.ns.T('Groups'), False, URL('find_customer_groups'), []))
      audit_filter = self.ui.connect.get_audit_filter("event", None)[0]
      if audit_filter!="disabled":
        mnu_customer[3].append((self.ui.ns.T('Events'), False, URL('find_customer_event'), []))
      self.ui.response.lo_menu.append(mnu_customer)
  
  def set_find_employee_menu(self):
    self.ui.response.lo_menu = []
    if self.ui.ns.session.mobile:
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Employee Data'), href=URL('find_employee_employee'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Additional Data'), href=URL('find_employee_fields'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      audit_filter = self.ui.connect.get_audit_filter("event", None)[0]
      if audit_filter!="disabled":
        self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Events'), href=URL('find_employee_event'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
    else:
      mnu_employee = (self.ui.ns.T('EMPLOYEE VIEWS'), False, None, [])
      mnu_employee[3].append((self.ui.ns.T('Employee Data'), False, URL('find_employee_employee'), []))
      mnu_employee[3].append((self.ui.ns.T('Additional Data'), False, URL('find_employee_fields'), []))
      audit_filter = self.ui.connect.get_audit_filter("event", None)[0]
      if audit_filter!="disabled":
        mnu_employee[3].append((self.ui.ns.T('Events'), False, URL('find_employee_event'), []))
      self.ui.response.lo_menu.append(mnu_employee)
  
  def set_find_movement_menu(self):
    self.ui.response.lo_menu = []
    if self.ui.ns.session.mobile:
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Inventory'), href=URL('find_movement_inventory'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Product Movement'), href=URL('find_movement_product'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      audit_filter = self.ui.connect.get_audit_filter("trans", "waybill")[0]
      if audit_filter!="disabled":
        self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Tool Movement'), href=URL('find_movement_tool'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      audit_filter = self.ui.connect.get_audit_filter("trans", "formula")[0]
      if audit_filter!="disabled":
        self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Formula'), href=URL('find_movement_formula'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Additional Data'), href=URL('find_movement_fields'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Groups'), href=URL('find_movement_groups'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
    else:
      mnu_trans = (self.ui.ns.T('STOCK'), False, None, [])
      mnu_trans[3].append((self.ui.ns.T('Inventory'), False, URL('find_movement_inventory'), []))
      mnu_trans[3].append((self.ui.ns.T('Product Movement'), False, URL('find_movement_product'), []))
      audit_filter = self.ui.connect.get_audit_filter("trans", "waybill")[0]
      if audit_filter!="disabled":
        mnu_trans[3].append((self.ui.ns.T('Tool Movement'), False, URL('find_movement_tool'), []))
      audit_filter = self.ui.connect.get_audit_filter("trans", "formula")[0]
      if audit_filter!="disabled":
        mnu_trans[3].append((self.ui.ns.T('Formula'), False, URL('find_movement_formula'), []))
      mnu_trans[3].append((self.ui.ns.T('Additional Data'), False, URL('find_movement_fields'), []))
      mnu_trans[3].append((self.ui.ns.T('Groups'), False, URL('find_movement_groups'), []))
      self.ui.response.lo_menu.append(mnu_trans)
  
  def set_find_payment_menu(self):
    self.ui.response.lo_menu = []
    if self.ui.ns.session.mobile:
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Payments Data'), href=URL('find_payment_payment'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Additional Data'), href=URL('find_payment_fields'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      audit_filter = self.ui.connect.get_audit_filter("trans", "invoice")[0]
      if audit_filter!="disabled":
        self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Invoice assignments'), href=URL('find_payment_invoice'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Groups'), href=URL('find_payment_groups'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
  
    else:
      mnu_payment = (self.ui.ns.T('PAYMENT VIEWS'), False, None, [])
      mnu_payment[3].append((self.ui.ns.T('Payments Data'), False, URL('find_payment_payment'), []))
      mnu_payment[3].append((self.ui.ns.T('Additional Data'), False, URL('find_payment_fields'), []))
      audit_filter = self.ui.connect.get_audit_filter("trans", "invoice")[0]
      if audit_filter!="disabled":
        mnu_payment[3].append((self.ui.ns.T('Invoice assignments'), False, URL('find_payment_invoice'), []))
      mnu_payment[3].append((self.ui.ns.T('Documents Groups'), False, URL('find_payment_groups'), []))
      self.ui.response.lo_menu.append(mnu_payment)
  
  def set_find_product_menu(self):
    self.ui.response.lo_menu = []
    if self.ui.ns.session.mobile:
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Product Data'), href=URL('find_product_product'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Additional Data'), href=URL('find_product_fields'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Groups'), href=URL('find_product_groups'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Barcode'), href=URL('find_product_barcode'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      audit_filter = self.ui.connect.get_audit_filter("price", None)[0]
      if audit_filter!="disabled":
        self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Price'), href=URL('find_product_price'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
        self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Discount'), href=URL('find_product_discount'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      audit_filter = self.ui.connect.get_audit_filter("event", None)[0]
      if audit_filter!="disabled":
        self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Events'), href=URL('find_product_event'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
  
    else:
      mnu_product = (self.ui.ns.T('PRODUCT VIEWS'), False, None, [])
      mnu_product[3].append((self.ui.ns.T('Product Data'), False, URL('find_product_product'), []))
      mnu_product[3].append((self.ui.ns.T('Additional Data'), False, URL('find_product_fields'), []))
      mnu_product[3].append((self.ui.ns.T('Groups'), False, URL('find_product_groups'), []))
      mnu_product[3].append((self.ui.ns.T('Barcode'), False, URL('find_product_barcode'), []))
      audit_filter = self.ui.connect.get_audit_filter("price", None)[0]
      if audit_filter!="disabled":
        mnu_product[3].append((self.ui.ns.T('Price'), False, URL('find_product_price'), []))
        mnu_product[3].append((self.ui.ns.T('Discount'), False, URL('find_product_discount'), []))
      audit_filter = self.ui.connect.get_audit_filter("event", None)[0]
      if audit_filter!="disabled":
        mnu_product[3].append((self.ui.ns.T('Events'), False, URL('find_product_event'), []))
      self.ui.response.lo_menu.append(mnu_product)
          
  def set_find_project_menu(self):
    self.ui.response.lo_menu = []
    if self.ui.ns.session.mobile:
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Project Data'), href=URL('find_project_project'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Additional Data'), href=URL('find_project_fields'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Contact Persons'), href=URL('find_project_contact'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Addresses'), href=URL('find_project_address'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      audit_filter = self.ui.connect.get_audit_filter("event", None)[0]
      if audit_filter!="disabled":
        self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Events'), href=URL('find_project_event'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
    else:
      mnu_project = (self.ui.ns.T('PROJECT VIEWS'), False, None, [])
      mnu_project[3].append((self.ui.ns.T('Project Data'), False, URL('find_project_project'), []))
      mnu_project[3].append((self.ui.ns.T('Additional Data'), False, URL('find_project_fields'), []))
      mnu_project[3].append((self.ui.ns.T('Contact Persons'), False, URL('find_project_contact'), []))
      mnu_project[3].append((self.ui.ns.T('Addresses'), False, URL('find_project_address'), []))
      audit_filter = self.ui.connect.get_audit_filter("event", None)[0]
      if audit_filter!="disabled":
        mnu_project[3].append((self.ui.ns.T('Events'), False, URL('find_project_event'), []))
      self.ui.response.lo_menu.append(mnu_project)

  def set_find_tool_menu(self):
    self.ui.response.lo_menu = []
    if self.ui.ns.session.mobile:
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Tool Data'), href=URL('find_tool_tool'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Additional Data'), href=URL('find_tool_fields'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      audit_filter = self.ui.connect.get_audit_filter("event", None)[0]
      if audit_filter!="disabled":
        self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Events'), href=URL('find_tool_event'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
    else:
      mnu_tool = (self.ui.ns.T('TOOL VIEWS'), False, None, [])
      mnu_tool[3].append((self.ui.ns.T('Tool Data'), False, URL('find_tool_tool'), []))
      mnu_tool[3].append((self.ui.ns.T('Additional Data'), False, URL('find_tool_fields'), []))
      audit_filter = self.ui.connect.get_audit_filter("event", None)[0]
      if audit_filter!="disabled":
        mnu_tool[3].append((self.ui.ns.T('Events'), False, URL('find_tool_event'), []))
      self.ui.response.lo_menu.append(mnu_tool)
  
  def set_find_transitem_menu(self):
    self.ui.response.lo_menu = []
    if self.ui.ns.session.mobile:
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Documents'), href=URL('find_transitem_trans'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Additional Data'), href=URL('find_transitem_fields'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Document rows'), href=URL('find_transitem_item'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
      self.ui.response.lo_menu.append(self.ui.control.get_mobil_button(self.ui.ns.T('Groups'), href=URL('find_transitem_groups'), 
                              cformat=None, icon="grid", style="text-align: left;", theme="a", ajax="false"))
    else:
      mnu_trans = (self.ui.ns.T('TRANSACTIONS'), False, None, [])
      mnu_trans[3].append((self.ui.ns.T('Documents'), False, URL('find_transitem_trans'), []))
      mnu_trans[3].append((self.ui.ns.T('Additional Data'), False, URL('find_transitem_fields'), []))
      mnu_trans[3].append((self.ui.ns.T('Document rows'), False, URL('find_transitem_item'), []))
      mnu_trans[3].append((self.ui.ns.T('Groups'), False, URL('find_transitem_groups'), []))
      self.ui.response.lo_menu.append(mnu_trans)
                            
class WebUi(object):
  
  application = "nerva2py"
  controller = "nwc"
  dir_view = ""
  dir_images = ""
  dir_help = ""
  response = None
  jqload_hack = ""
  tool = NervaTools(None)
  dbout = DataOutput(None)
  menu = WebUiMenu(None)
  report = WebUiReport(None)
  select = WebUiSelector(None)
  control = WebUiControl(None)
  connect = WebUiConnect(None)
  
  def __init__(self, ns, response):
    self.ns = ns
    self.response = response
    self.tool = NervaTools(ns)
    self.dbout = DataOutput(ns)
    self.menu = WebUiMenu(self)
    self.report = WebUiReport(self)
    self.select = WebUiSelector(self)
    self.control = WebUiControl(self)
    self.connect = WebUiConnect(self)
    self.set_mobile()
    self.set_ini_values()

  def set_mobile(self):
    if self.ns.request.user_agent().has_key("browser"):
      if self.ns.request.user_agent()["browser"].has_key("name"):
        if self.ns.request.user_agent()["browser"]["name"]=="Microsoft Internet Explorer":
          if int(str(self.ns.request.user_agent()["browser"]["version"]).split(".")[0])<9:
            self.jqload_hack = 'alert("'+self.ns.T('Please wait!')+'");'
    if not self.ns.session.mobile:
      if self.ns.request.user_agent()["is_mobile"] or self.ns.request.user_agent()["is_tablet"]:
        self.ns.session.mobile = True
      else:
        self.ns.session.mobile = False
    if self.ns.request.vars.has_key("desktop"):
      self.ns.session.mobile = False
    elif self.ns.request.vars.has_key("mobile"):
      self.ns.session.mobile = True
  
  def set_ini_values(self):
    if self.ns.session.mobile:
      self.dir_view = "nmc"
      self.dir_images = "static/resources/application/nmc/images"
      self.dir_help = "static/resources/application/nmc/help"
      self.response.title=self.ns.T('Nervatura Mobile Client')
      self.response.cmd_menu = self.control.get_mobil_button(label=self.ns.T("MENU"), href="#main-menu",
                                                 icon="bars", cformat="ui-btn-left", ajax="true", iconpos="left")
      self.response.cmd_commands = self.control.get_mobil_button(label=self.ns.T("MORE..."), href="#local-menu",
                                                 icon="forward", cformat="ui-btn-right", ajax="true", iconpos="left")
      self.response.cmd_exit = self.control.get_mobil_button(label=self.ns.T("EXIT"), href=URL('frm_logout'),
                                                 icon="power", cformat="ui-btn-right", ajax="false", iconpos="left",
                                                 style="color: red;margin:2px;")
      self.response.cmd_help = self.control.get_mobil_button(label=self.ns.T("HELP"), href=URL('cmd_go_help?page=index'),
                                                 cformat=None, icon="info", iconpos="left", target="blank",
                                                 style="margin:5px;")
      self.response.cmd_home = self.control.get_mobil_button(label=self.ns.T("HOME"), href=URL('index'),
                                                 icon="home", cformat="ui-btn-left", ajax="false", iconpos="left")
      self.response.cmd_close = self.control.get_mobil_button(label=self.ns.T("Close"), href="#",
                                              icon="delete", cformat="ui-btn-right", ajax="true", iconpos="notext", 
                                              rel="close")
    else:
      self.dir_view = "nwc"
      self.dir_images = "static/resources/application/nwc/images"
      self.dir_help = "static/resources/application/nwc/help"
      self.response.title=self.ns.T('Nervatura Web Client')
      self.response.icon_help = IMG(_src=URL(self.dir_images,'icon16_help.png'))
      self.response.icon_user = IMG(_src=URL(self.dir_images,'icon16_user.png'),
                                    _style="vertical-align: middle;",_height="16px",_width="16px")
      self.response.icon_address = IMG(_src=URL(self.dir_images,'icon16_address.png'),
                                    _style="vertical-align: middle;",_height="16px",_width="16px")
  
  def nwc_ini(self):
    #check and create some ui and version specifics settings
    #compatibility bugfixes
    update_ini = False
    deffield = [{'nervatype':'deffield','id':self.ns.valid.get_id_from_refnumber('deffield','printer_login')},
                  {'nervatype':'deffield','id':self.ns.valid.get_id_from_refnumber('deffield','printer_password')},
                  {'nervatype':'deffield','id':self.ns.valid.get_id_from_refnumber('deffield','printer_server')},
                  {'nervatype':'deffield','id':self.ns.valid.get_id_from_refnumber('deffield','printer_port')},
                  {'nervatype':'deffield','id':self.ns.valid.get_id_from_refnumber('deffield','printer_mail_smtp')},
                  {'nervatype':'deffield','id':self.ns.valid.get_id_from_refnumber('deffield','printer_mail_sender')},
                  {'nervatype':'deffield','id':self.ns.valid.get_id_from_refnumber('deffield','printer_mail_login')},
                  {'nervatype':'deffield','id':self.ns.valid.get_id_from_refnumber('deffield','printer_mail_address')},
                  {'nervatype':'deffield','id':self.ns.valid.get_id_from_refnumber('deffield','printer_mail_subject')},
                  {'nervatype':'deffield','id':self.ns.valid.get_id_from_refnumber('deffield','printer_mail_message')}]
    for values in deffield:
      if not values["id"]: update_ini=True
      self.ns.connect.deleteData(values["nervatype"], ref_id=values["id"])
    if update_ini:  
      self.ns.store.setIniData()
    
