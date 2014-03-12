# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""
      
class ui_filter(object):
  __tablename__ = 'ui_filter'
  def __init__(self):
    self.id = None
    self.employee_id = None
    self.parentview = None
    self.viewname = None
    self.fieldname = None
    self.ftype = None
    self.fvalue = None
  def __repr__(self):
    return "<ui_filter('%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.employee_id, self.parentview, self.viewname, self.fieldname, self.ftype, self.fvalue) 

class ui_groupinput(object):
  __tablename__ = 'ui_groupinput'
  def __init__(self):
    self.id = None
    self.groups_id = None
    self.formname = None
    self.contname = None
    self.isenabled = 1
    self.isvisibled = 1
  def __repr__(self):
    return "<ui_groupinput('%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.groups_id, self.formname, self.contname, self.isenabled, self.isvisibled)

class ui_menu(object):
  __tablename__ = 'ui_menu'
  def __init__(self):
    self.id = None
    self.description = None
    self.modul = None
    self.icon = None
    self.funcname = None
    self.url = 0
    self.address = None
  def __repr__(self):
    return "<ui_menu('%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.description, self.modul, self.icon, self.funcname, self.url,self.address)

class ui_menufields(object):
  __tablename__ = 'ui_menufields'
  def __init__(self):
    self.id = None
    self.menu_id = None
    self.fieldname = None
    self.description = None
    self.fieldtype = None
    self.orderby = 0
  def __repr__(self):
    return "<ui_menufields('%s', '%s','%s','%s','%s','%s')>" % \
      (self.id, self.menu_id, self.fieldname, self.description, self.fieldtype, self.orderby)
                  
class ui_printqueue(object):
  __tablename__ = 'ui_printqueue'
  def __init__(self):
    self.id = None
    self.nervatype = None
    self.ref_id = None
    self.qty = 0
    self.employee_id = None
    self.report_id = None
  def __repr__(self):
    return "<ui_printqueue('%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.nervatype, self.ref_id, self.qty, self.employee_id, self.report_id)

class ui_report(object):
  __tablename__ = 'ui_report'
  def __init__(self):
    self.id = None
    self.reportkey = None
    self.nervatype = None
    self.transtype = None
    self.repname = None
    self.description = None
    self.filetype = None
    self.report = None
    self.label = None
  def __repr__(self):
    return "<ui_report('%s',%s','%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.reportkey, self.nervatype, self.transtype, self.repname, self.description, self.filetype, self.report, self.label)

class ui_reportfields(object):
  __tablename__ = 'ui_reportfields'
  def __init__(self):
    self.id = None
    self.report_id = None
    self.fieldname = None
    self.fieldtype = None
    self.wheretype = None
    self.description = None
    self.orderby = 0
    self.sqlstr = None
    self.parameter = 0
    self.dataset = None
    self.defvalue = None
    self.valuelist = None
  def __repr__(self):
    return "<ui_reportfields('%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % \
      (self.id, self.report_id, self.fieldname, self.fieldtype, self.wheretype, self.description, 
       self.orderby, self.sqlstr, self.parameter, self.dataset, self.defvalue, self.valuelist)

class ui_reportsources(object):
  __tablename__ = 'ui_reportsources'
  def __init__(self):
    self.id = None
    self.report_id = None
    self.dataset = None
    self.sqlstr = None
  def __repr__(self):
    return "<ui_reportsources('%s', '%s', '%s','%s')>" % \
      (self.id, self.report_id, self.dataset, self.sqlstr)
                                                                    
class ui_userconfig(object):
  __tablename__ = 'ui_userconfig'
  def __init__(self):
    self.id = None  
    self.employee_id = None
    self.section = None
    self.cfgroup = None
    self.cfname = None
    self.cfvalue = None
    self.orderby = None
  def __repr__(self):
    return "<ui_userconfig('%s', '%s','%s', '%s', '%s', '%s', '%s')>" % \
      (self.id, self.employee_id, self.section, self.cfgroup, self.cfname, self.cfvalue, self.orderby)
      
class address(object):
  __tablename__ = 'address'
  def __init__(self):
    self.id = None
    self.nervatype = None
    self.ref_id = None
    self.country = None
    self.state = None
    self.zipcode = None
    self.city = None
    self.street = None
    self.notes = None
    self.deleted = 0
  def __repr__(self):
    return "<address('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % \
      (self.id, self.nervatype, self.ref_id, self.country, self.state, self.zipcode, self.city, self.street, self.notes, self.deleted)

class ui_audit(object):
  __tablename__ = 'ui_audit'
  def __init__(self):
    self.id = None
    self.usergroup = None
    self.nervatype = None
    self.subtype = None
    self.inputfilter = None
    self.supervisor = 0
  def __repr__(self):
    return "<ui_audit('%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.usergroup, self.nervatype, self.subtype, self.inputfilter, self.supervisor)

class barcode(object):
  __tablename__ = 'barcode'
  def __init__(self):
    self.id = None
    self.code = None
    self.product_id = None
    self.description = None
    self.barcodetype = None
    self.qty = 0
    self.defcode = 0
  def __repr__(self):
    return "<barcode('%s','%s','%s', '%s', '%s', '%s', '%s')>" % \
      (self.id, self.code, self.product_id, self.description, self.barcodetype, self.qty, self.defcode)

class contact(object):
  __tablename__ = 'contact'
  def __init__(self):
    self.id = None
    self.nervatype = None
    self.ref_id = None
    self.firstname = None
    self.surname = None
    self.status = None
    self.phone = None
    self.fax = None
    self.mobil = None
    self.email = None
    self.notes = None
    self.deleted = 0
  def __repr__(self):
    return "<contact('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.nervatype, self.ref_id, self.firstname, self.surname, self.status, 
       self.phone, self.fax, self.mobil, self.email, self.notes, self.deleted)

class currency(object):
  __tablename__ = 'currency'
  def __init__(self):
    self.id = None
    self.curr = None
    self.description = None
    self.digit = 0
    self.defrate = 0
    self.cround = 0
  def __repr__(self):
    return "<currency('%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.curr, self.description, self.digit, self.defrate, self.cround)

class customer(object):
  __tablename__ = 'customer'
  def __init__(self):
    self.id = None
    self.custtype = None 
    self.custnumber = None 
    self.custname = None
    self.taxnumber = None
    self.account = None
    self.notax = 0
    self.terms = 0
    self.creditlimit = 0
    self.discount = 0
    self.notes = None
    self.inactive = 0
    self.deleted = 0
  def __repr__(self):
    return "<customer('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', \
      '%s', '%s', '%s', '%s')>" % \
      (self.id, self.custtype, self.custnumber, self.custname, self.taxnumber,
       self.account, self.notax, self.terms, self.creditlimit, self.discount,
       self.notes, self.inactive, self.deleted)

class deffield(object):
  __tablename__ = 'deffield'
  def __init__(self):
    self.id = None
    self.fieldname = None
    self.nervatype = None
    self.subtype = None
    self.fieldtype = None
    self.description = None
    self.valuelist = None
    self.addnew = 0
    self.visible = 1
    self.readonly = 0
    self.deleted = 0
  def __repr__(self):
    return "<deffield('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.fieldname, self.nervatype, self.subtype, self.fieldtype, self.description, 
       self.valuelist, self.addnew, self.visible, self.readonly, self.deleted)

class employee(object):
  __tablename__ = 'employee'
  def __init__(self):
    self.id = None
    self.empnumber = None
    self.username = None
    self.usergroup = None
    self.startdate = None
    self.enddate = None
    self.department = None
    self.inactive = None
    self.deleted = None
    self.password = None
    self.email = None
  def __repr__(self):
    return "<employee('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.empnumber, self.username, self.usergroup, self.startdate, self.enddate, self.department,
       self.inactive, self.deleted, self.password, self.email)

class event(object):
  __tablename__ = 'event'
  def __init__(self):
    self.id = None
    self.calnumber = None
    self.nervatype = None
    self.ref_id = None
    self.uid = None
    self.eventgroup = None
    self.fromdate = None
    self.todate = None
    self.subject = None
    self.place = None
    self.description = None
    self.deleted = 0
  def __repr__(self):
    return "<event('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',%s')>" % \
      (self.id, self.calnumber, self.nervatype, self.ref_id, self.uid, self.eventgroup, self.fromdate,
       self.todate, self.subject, self.place, self.description, self.deleted)
      
class fieldvalue(object):
  __tablename__ = 'fieldvalue'
  def __init__(self):
    self.id = None
    self.fieldname = None
    self.ref_id = None
    self.value = None
    self.notes = None
    self.deleted = None
  def __repr__(self):
    return "<fieldvalue('%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.fieldname, self.ref_id, self.value, self.notes, self.deleted)

class formula(object):
  __tablename__ = 'formula'
  def __init__(self):
    self.id = None
    self.formnumber = None
    self.product_id = None
    self.formula_id = None
    self.qty = 0
    self.shared = 0
    self.place_id = None
    self.notes = None
    self.inactive = 0
    self.deleted = 0
  def __repr__(self):
    return "<formula('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.formnumber, self.product_id, self.formula_id, self.qty, 
       self.shared, self.place_id, self.notes, self.inactive, self.deleted)
  
class groups(object):
  __tablename__ = 'groups'
  def __init__(self):
    self.id = None
    self.groupname = None
    self.groupvalue = None
    self.description = None
    self.inactive = 0
    self.deleted = 0
  def __repr__(self):
    return "<groups('%s','%s', '%s', '%s', '%s', '%s')>" % \
      (self.id, self.groupname, self.groupvalue, self.description, self.inactive, self.deleted)

class item(object):
  __tablename__ = 'item'
  def __init__(self):
    self.id = None 
    self.trans_id = None 
    self.product_id = None 
    self.unit = None 
    self.qty = 0 
    self.fxprice = 0 
    self.netamount = 0 
    self.discount = 0 
    self.tax_id = None 
    self.vatamount = 0 
    self.amount = 0 
    self.description = None 
    self.deposit = 0 
    self.ownstock = 0 
    self.actionprice = 0
    self.deleted = 0
  def __repr__(self):
    return "<item('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.trans_id, self.product_id, self.unit, self.qty, self.fxprice, self.netamount, 
       self.discount, self.tax_id, self.vatamount, self.amount, self.description, self.deposit, 
       self.ownstock, self.actionprice, self.deleted)

class link(object):
  __tablename__ = 'link'
  def __init__(self):
    self.id = None
    self.nervatype_1 = None
    self.ref_id_1 = None
    self.nervatype_2 = None
    self.ref_id_2 = None
    self.linktype = 0
    self.deleted = 0
  def __repr__(self):
    return "<link('%s','%s', '%s', '%s', '%s', '%s', '%s')>" % \
      (self.id, self.nervatype_1, self.ref_id_1, self.nervatype_2, self.ref_id_2, self.linktype, self.deleted)

class log(object):
  __tablename__ = 'log'
  def __init__(self):
    self.id = None
    self.nervatype = None
    self.ref_id = None
    self.logstate = None
    self.employee_id = None
    self.crdate = None
  def __repr__(self):
    return "<log('%s','%s', '%s', '%s', '%s', '%s')>" % \
      (self.id, self.nervatype, self.ref_id, self.logstate, self.employee_id, self.crdate)

class movement(object):
  __tablename__ = 'movement'
  def __init__(self):
    self.id = None
    self.trans_id = None
    self.shippingdate = None
    self.movetype = None
    self.product_id = None
    self.tool_id = None
    self.qty = 0
    self.place_id = None
    self.shared = 0
    self.notes = None
    self.deleted = None
  def __repr__(self):
    return "<movement('%s','%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % \
      (self.id, self.trans_id, self.shippingdate, self.movetype, self.product_id, self.tool_id,
       self.qty, self.place_id, self.shared, self.notes, self.deleted)

class numberdef(object):
  __tablename__ = 'numberdef'
  def __init__(self):
    self.id = None
    self.numberkey = None
    self.prefix = None
    self.curvalue = 0
    self.isyear = 1
    self.separator = "/"
    self.len = 5
    self.description = None
    self.visible = 0
    self.readonly = 0
    self.orderby = 0
  def __repr__(self):
    return "<numberdef('%s','%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % \
      (self.id, self.numberkey, self.prefix, self.curvalue, self.isyear, self.separator, self.len, 
       self.description, self.visible, self.readonly, self.orderby)  
      
class pattern(object):
  __tablename__ = 'pattern'
  def __init__(self):
    self.id = None
    self.transtype = None
    self.description = None
    self.notes = None
    self.defpattern = 0
    self.deleted = 0
  def __repr__(self):
    return "<pattern('%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.transtype, self.description, self.notes, self.defpattern, self.deleted)

class payment(object):
  __tablename__ = 'payment'
  def __init__(self):
    self.id = None
    self.trans_id = None 
    self.paiddate = None 
    self.amount = None 
    self.notes = None
    self.deleted = None
  def __repr__(self):
    return "<payment('%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.trans_id, self.paiddate, self.amount, self.notes, self.deleted)

class place(object):
  __tablename__ = 'place'
  def __init__(self):
    self.id = None
    self.planumber = None
    self.placetype = None
    self.description = None
    self.place_id = None
    self.curr = None
    self.storetype = None
    self.defplace = 0
    self.notes = None
    self.inactive = 0
    self.deleted = 0
  def __repr__(self):
    return "<place('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % \
      (self.id, self.planumber, self.placetype, self.description, self.place_id,
       self.curr, self.storetype, self.defplace, self.notes, self.inactive, self.deleted)

class price(object):
  __tablename__ = 'price'
  def __init__(self):
    self.id = None
    self.product_id = None
    self.validfrom = None
    self.validto = None
    self.curr = None
    self.qty = 0
    self.pricevalue = 0
    self.discount = None
    self.calcmode = None
    self.vendorprice = 0
    self.deleted = 0
  def __repr__(self):
    return "<price('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.product_id, self.validfrom, self.validto, 
       self.curr, self.qty, self.pricevalue, self.discount, self.calcmode, self.vendorprice, self.deleted)
                  
class product(object):
  __tablename__ = 'product'
  def __init__(self):
    self.id = None
    self.partnumber = None
    self.protype = None  
    self.description = None 
    self.unit = None 
    self.tax_id = None  
    self.notes = None
    self.webitem = 0
    self.inactive = 0
    self.deleted = 0
  def __repr__(self):
    return "<product('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s)>" % \
      (self.id, self.partnumber, self.protype,  self.description, self.unit, 
       self.tax_id, self.notes, self.webitem, self.inactive, self.deleted)

class project(object):
  __tablename__ = 'project'
  def __init__(self):
    self.id = None
    self.pronumber = None
    self.description = None
    self.customer_id = None
    self.startdate = None
    self.enddate = None
    self.notes = None
    self.inactive = 0
    self.deleted = 0
  def __repr__(self):
    return "<project('%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.pronumber, self.description, self.customer_id, self.startdate,
       self.enddate, self.notes, self.inactive, self.deleted)

class rate(object):
  __tablename__ = 'rate'
  def __init__(self):
    self.id = None
    self.ratetype = None
    self.ratedate = None
    self.curr = None
    self.place_id = None
    self.rategroup = None
    self.ratevalue = 0
    self.deleted = 0
  def __repr__(self):
    return "<rate('%s','%s','%s','%s','%s','%s','%s', '%s')>" % \
      (self.id, self.ratetype, self.ratedate, self.curr, self.place_id,
       self.rategroup, self.ratevalue, self.deleted)  
  
class tax(object):
  __tablename__ = 'tax'
  def __init__(self):
    self.id = None
    self.taxkey
    self.description = None
    self.rate = 0
    self.taxcode = None
    self.inactive = 0
  def __repr__(self):
    return "<tax('%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.taxkey, self.description, self.rate, self.taxcode, self.inactive)

class tool(object):
  __tablename__ = 'tool'
  def __init__(self):
    self.id = None
    self.serial = None
    self.description = None
    self.product_id = None
    self.toolgroup = None
    self.notes = None
    self.inactive = 0
    self.deleted = 0
  def __repr__(self):
    return "<tool('%s','%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.serial, self.description, self.product_id, self.toolgroup,
       self.notes, self.inactive, self.deleted)
    
class trans(object):
  __tablename__ = 'trans'
  def __init__(self):
    self.id = None
    self.transtype = None
    self.direction = None
    self.transnumber = None
    self.ref_transnumber = None
    self.crdate = None
    self.transdate = None
    self.duedate = None
    self.customer_id = None
    self.employee_id = None
    self.department = None
    self.project_id = None
    self.place_id = None
    self.paidtype = None
    self.curr = None
    self.notax = 0
    self.paid = 0
    self.acrate = 0
    self.notes = None
    self.intnotes = None
    self.fnote = None
    self.transtate = None
    self.cruser_id = None
    self.closed = 0
    self.deleted = 0
  def __repr__(self):
    return "<trans('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.transtype, self.direction, self.transnumber, self.ref_transnumber, self.crdate, self.transdate, self.duedate, 
       self.customer_id, self.employee_id, self.department, self.project_id, self.place_id, self.paidtype, 
       self.curr, self.notax, self.paid, self.acrate, self.notes, self.intnotes, self.fnote, self.transtate,
       self.cruser_id, self.closed, self.deleted)                                    
    