# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import pyamf  # @UnresolvedImport

class RemoteClass(object):
  def __init__(self, alias):
    self.alias = alias
  def __call__(self, klass):
    pyamf.register_class(klass, self.alias)
    return klass

@RemoteClass(alias="models.customer")
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

@RemoteClass(alias="models.groups")
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

@RemoteClass(alias="models.deffield")
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

@RemoteClass(alias="models.link")
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

@RemoteClass(alias="models.fieldvalue")
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

@RemoteClass(alias="models.address")
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

@RemoteClass(alias="models.contact")
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
                        
@RemoteClass(alias="models.ui_filter")
class filter(object):  # @ReservedAssignment
  __tablename__ = 'ui_filter'
  def __init__(self):
    self.id = None
    self.employee_id = None
    self.parentview = None
    self.viewname = None
    self.fieldname = None
    self.ftype = None
    self.fvalue = None
    self.fieldlabel = None
    self.fieldtype = None
    self.wheretype = None
    self.sqlstr= None
  def __repr__(self):
    return "<ui_filter('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
      (self.id, self.employee_id, self.parentview, self.viewname, self.fieldname, self.ftype, self.fvalue,self.fieldlabel,
       self.fieldtype, self.wheretype, self.sqlstr) 
                                    
@RemoteClass(alias="models.ui_userconfig")
class userconfig():
  __tablename__ = 'ui_userconfig'  
  def __init__(self, *args, **kwargs):
    self.id = None  
    self.employee_id = None
    self.section = None
    self.cfgroup = None
    self.cfname = None
    self.cfvalue = None
    self.orderby = None
  def __repr__(self):
    return "<userconfig('%s', '%s','%s', '%s', '%s', '%s', '%s')>" % \
      (self.id, self.employee_id, self.section, self.cfgroup, self.cfname, self.cfvalue, self.orderby)
      
