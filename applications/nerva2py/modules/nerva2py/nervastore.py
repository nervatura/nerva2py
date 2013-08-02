# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Project
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""
  
from gluon.sql import DAL, Field
from gluon import SQLFORM
from gluon.html import URL
from gluon.html import INPUT, DIV, A, SPAN
from gluon.validators import IS_IN_DB, IS_EMAIL, IS_EMPTY_OR, IS_NOT_IN_DB, IS_FLOAT_IN_RANGE #IS_STRONG, CRYPT
import datetime
import time
from hashlib import md5
from base64 import encodestring, decodestring
from pyDes import des, PAD_PKCS5  # @UnresolvedImport

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
    self.db = ns.db
    self.T = ns.T
    self.row = row
    self.error_message = self.T("Invalid value type")
  def __call__(self, value):
    try:
      fld_type = self.db(self.db.groups.id==self.db(self.db.deffield.fieldname==self.row.fieldname).select()[0]["fieldtype"]).select()[0]["groupvalue"]
      if fld_type == 'bool':
        if value in('true','True','TRUE','t','T','y','YES','yes','1'):
          value = 'true'
        elif value in('false','False','FALSE','f','F','n','no','NO','0',None):
          value = 'false'
        else:
          return (value, value+self.T(" not valid bool value (true or false)"))
        return (value, None)
      elif fld_type == 'integer':
        try:
          value = str(int(value))
          return (value, None)
        except:
          return (value, value+self.T(" not valid integer"))
      elif fld_type == 'float':
        try:
          value = str(float(value))
          return (value, None)
        except:
          return (value, value+self.T(" not valid float"))
      elif fld_type == 'date':
        try:
          y, m, d, hh, mm, ss, t0, t1, t2 = time.strptime(value, str('%Y-%m-%d')) #@UnusedVariable
          value = datetime.date(y, m, d)
          return (value, None)
        except:
          return (value, value+self.T(' not valid date (YYYY-MM-DD)'))
      elif fld_type == 'password':
        try:
          if not (value.startswith("XXX") and value.endswith("XXX")):
            value = self.ns.set_password_field(self.row.fieldname,value)
          return (value, None)
        except:
          return (value, value+self.T(" can not be encrypted"))
      elif fld_type in ('string', 'valuelist', 'notes', 'flink'):
        return (value, None)
      elif fld_type == 'customer':
        try:
          value = int(value)
        except:
          return (value, self.T(' missing customer'))
        if len(self.db.customer(id=int(value)).items())>0:
          return (value, None)
        else:
          return (value, value+self.T(' not valid customer'))
      elif fld_type == 'tool':
        try:
          value = int(value)
        except:
          return (value, self.T(' missing tool'))
        if len(self.db.tool(id=int(value)).items())>0:
          return (value, None)
        else:
          return (value, value+self.T(' not valid tool'))
      elif fld_type == 'product':
        try:
          value = int(value)
        except:
          return (value, self.T(' missing product'))
        if len(self.db.product(id=int(value)).items())>0:
          return (value, None)
        else:
          return (value, value+self.T(' not valid product'))
      elif fld_type in ('trans','transitem','transmovement','transpayment'):
        try:
          value = int(value)
        except:
          return (value, self.T(' missing trans'))
        if len(self.db.trans(id=int(value)).items())>0:
          return (value, None)
        else:
          return (value, value+self.T(' not valid trans'))
      elif fld_type == 'project':
        try:
          value = int(value)
        except:
          return (value, self.T(' missing project'))
        if len(self.db.project(id=int(value)).items())>0:
          return (value, None)
        else:
          return (value, value+self.T(' not valid project'))
      elif fld_type == 'employee':
        try:
          value = int(value)
        except:
          return (value, self.T(' missing employee'))  
        if len(self.db.employee(id=int(value)).items())>0:
          return (value, None)
        else:
          return (value, value+self.T(' not valid employee'))
      elif fld_type == 'place':
        try:
          value = int(value)
        except:
          return (value, self.T(' missing place'))
        if len(self.db.place(id=int(value)).items())>0:
          return (value, None)
        else:
          return (value, value+self.T(' not valid place'))
      else:
        return (value, self.error_message)    
    except:
      return (value, self.error_message)
  def formatter(self, value):
    return value
  
class NervaStore(object):
  
  db = None
  error_message = ""
  employee = None
  md5_password = False
  admin_user = False
  
  def __init__(self, request, T, lstore=None):
    self.request = request
    self.T = T
    self.lstore = lstore
  
  def setConnect(self, uri, pool_size=0):
    try:
      self.db = DAL(uri=uri, pool_size=pool_size)
    except Exception, err:
      self.error_message = err
      self.db = None
  
  def _link_id_formatter(self, table, field, value):
    if value==None:
      return ""
    ltable = self.db(table.id==value).select()
    if len(ltable.as_list())>0:
      return ltable[0][field]
    else:
      return ""
  
  def get_md5_value(self, value):
    rv = md5()
    rv.update(value)
    return rv.hexdigest()
  
  def get_audit_subtype(self,row,value):
    retvalue=""
    nervatype = self.db.groups(id=row.nervatype).groupvalue
    if nervatype=="trans" and value!=None:
      transtype = self.db(self.db.groups.id==value).select().as_list()
      if len(transtype)>0:
        return transtype[0]["groupvalue"]
    if nervatype=="report" and value!=None:
      report = self.db(self.db.ui_report.id==value).select().as_list()
      if len(report)>0:
        return report[0]["reportkey"]
    if nervatype=="menu" and value!=None:
      menu = self.db(self.db.ui_menu.id==value).select().as_list()
      if len(menu)>0:
        return menu[0]["menukey"]
    return retvalue
  
  def get_nervatype_name(self,group_id,ref_id=None):
    nervatype = self.db.groups(id=group_id).groupvalue
    if nervatype=="trans" and ref_id!=None:
      nervatype = self.db.groups(id=self.db.trans(id=ref_id).transtype).groupvalue
    return nervatype
  
  def show_refnumber(self, rettype, nervatype, ref_id, retfield=None):
    if ref_id==None:
      return ""
    if nervatype in("address","contact"):
      head_nervatype_id = self.db[nervatype](id=ref_id).nervatype
      head_nervatype_name = self.db.groups(id=head_nervatype_id).groupvalue
      head_id = self.db[nervatype](id=ref_id).ref_id
      head_refnumber = self.show_refnumber("refnumber",head_nervatype_name,head_id)
      row_index = self.db((self.db[nervatype].nervatype==head_nervatype_id)&(self.db[nervatype].ref_id==head_id)
                 &(self.db[nervatype].deleted==0)&(self.db[nervatype].id<=ref_id)).select('count(*)').first()['count(*)']
      if rettype=="refnumber":
        return head_refnumber+"~"+str(row_index)
      elif rettype=="index":
        return row_index
      elif rettype=="href":
        return "frm_"+head_nervatype_name+"/view/"+head_nervatype_name+"/"+str(head_id)
    elif nervatype=="barcode":
      if rettype=="refnumber":
        if retfield:
          self.db.barcode(id=ref_id)[retfield]
        else:
          return self.db.barcode(id=ref_id).code
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_product/view/product/"+str(self.db.barcode(id=ref_id).product_id)
    elif nervatype=="currency":
      if rettype=="refnumber":
        if retfield:
          self.db.currency(id=ref_id)[retfield]
        else:
          return self.db.currency(id=ref_id).curr
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_currency/edit/currency/"+str(ref_id)
    elif nervatype=="customer":
      if rettype=="refnumber":
        if retfield:
          self.db.customer(id=ref_id)[retfield]
        else:
          return self.db.customer(id=ref_id).custnumber
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_customer/view/customer/"+str(ref_id)
    elif nervatype=="deffield":
      if rettype=="refnumber":
        if retfield:
          self.db.deffield(id=ref_id)[retfield]
        else:
          return self.db.deffield(id=ref_id).fieldname
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_deffield_all/edit/deffield/"+str(ref_id)
    elif nervatype=="employee":
      if rettype=="refnumber":
        if retfield:
          self.db.employee(id=ref_id)[retfield]
        else:
          return self.db.employee(id=ref_id).empnumber
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_employee/view/employee/"+str(ref_id)
    elif nervatype=="event":
      if rettype=="refnumber":
        if retfield:
          self.db.event(id=ref_id)[retfield]
        else:
          return self.db.event(id=ref_id).calnumber
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_event/view/event/"+str(ref_id)
    elif nervatype=="groups":
      if rettype=="refnumber":
        if retfield:
          self.db.groups(id=ref_id)[retfield]
        else:
          return self.db.groups(id=ref_id).groupname+"~"+self.db.groups(id=ref_id).groupvalue
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_groups_all/edit/groups/"+str(ref_id)
    elif nervatype in("item","payment","movement"):
      head_id = self.db[nervatype](id=ref_id).trans_id
      head_refnumber = self.db.trans(id=head_id).transnumber
      row_index = self.db((self.db[nervatype].trans_id==head_id)&(self.db[nervatype].deleted==0)
                          &(self.db[nervatype].id<=ref_id)).select('count(*)').first()['count(*)']
      if rettype=="refnumber":
        return head_refnumber+"~"+str(row_index)
      elif rettype=="index":
        return row_index
      elif rettype=="href":
        return "frm_trans/view/trans/"+str(head_id)
    elif nervatype=="numberdef":
      if rettype=="refnumber":
        if retfield:
          self.db.numberdef(id=ref_id)[retfield]
        else:
          return self.db.numberdef(id=ref_id).numberkey
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_numberdef/edit/numberdef/"+str(ref_id)
    elif nervatype=="pattern":
      if rettype=="refnumber":
        if retfield:
          self.db.pattern(id=ref_id)[retfield]
        else:
          return self.db.pattern(id=ref_id).description
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "index"
    elif nervatype=="place":
      if rettype=="refnumber":
        if retfield:
          self.db.place(id=ref_id)[retfield]
        else:
          return self.db.place(id=ref_id).planumber
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_place/view/place/"+str(ref_id)
    elif nervatype=="price":
      if rettype=="refnumber":
        head_id = self.db.price(id=ref_id).product_id
        head_refnumber = self.db.product(id=head_id).partnumber
        if retfield:
          self.db.price(id=ref_id)[retfield]
        else:
          return head_refnumber+"~"+self.db.price(id=ref_id).curr+"~"+str(self.db.price(id=ref_id).validfrom)
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "find_product_price/view/product/"+str(self.db.price(id=ref_id).product_id)
    elif nervatype=="product":
      if rettype=="refnumber":
        if retfield:
          self.db.product(id=ref_id)[retfield]
        else:
          return self.db.product(id=ref_id).partnumber
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_product/view/product/"+str(ref_id)
    elif nervatype=="project":
      if rettype=="refnumber":
        if retfield:
          self.db.project(id=ref_id)[retfield]
        else:
          return self.db.project(id=ref_id).pronumber
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_project/view/project/"+str(ref_id)
    elif nervatype=="tax":
      if rettype=="refnumber":
        if retfield:
          self.db.tax(id=ref_id)[retfield]
        else:
          return self.db.tax(id=ref_id).taxcode
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_tax/edit/tax/"+str(ref_id)
    elif nervatype=="tool":
      if rettype=="refnumber":
        if retfield:
          self.db.tool(id=ref_id)[retfield]
        else:
          return self.db.tool(id=ref_id).serial
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_tool/view/tool/"+str(ref_id)
    elif nervatype=="trans":
      if rettype=="refnumber":
        if retfield:
          self.db.trans(id=ref_id)[retfield]
        else:
          return self.db.trans(id=ref_id).transnumber
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_trans/view/trans/"+str(ref_id)
    elif nervatype=="setting":
      if rettype=="refnumber":
        if retfield:
          self.db.fieldvalue(id=ref_id)[retfield]
        else:
          return self.db.fieldvalue(id=ref_id).fieldname
      elif rettype=="index":
        return 1
      elif rettype=="href":
        return "frm_setting"
    elif nervatype in("audit","link","log","rate"):
      if rettype=="refnumber":
        return ""
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
  
  def splitThousands(self, s, tSep=',', dSep='.'):
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

  def show_fieldvalue(self, row):
    retvalue = row.value
    fieldname = self.db(self.db.fieldvalue.id==row.id).select()[0]["fieldname"]
    fld_type = self.db(self.db.groups.id==self.db(self.db.deffield.fieldname==fieldname).select()[0]["fieldtype"]).select()[0]["groupvalue"]
    if fld_type == 'bool':
      retvalue = DIV(INPUT(_type="checkbox", value=(retvalue=="true"), _disabled="disabled"), _align="center", _width="100%")
    elif fld_type == 'integer':
      try:
        retvalue = DIV(self.splitThousands(float(retvalue)," ","."), _align="right", _width="100%")
      except Exception:
        pass
    elif fld_type == 'float':
      try:
        retvalue = DIV(self.splitThousands(float(retvalue)," ","."), _align="right", _width="100%")
      except Exception:
        pass
    elif fld_type == 'date':
      retvalue = DIV(retvalue, _align="center", _width="100%")
    elif fld_type in ('string', 'valuelist', 'notes'):
        pass
    elif fld_type == 'customer':
      if len(self.db.customer(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.db.customer(id=int(retvalue))["custname"]), 
                     _href=URL(r=self.request, f="frm_customer/view/customer/"+retvalue), _target="_blank")
      else:
        retvalue = self.T("Missing customer...")
    elif fld_type == 'tool':
      if len(self.db.tool(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.db.tool(id=int(retvalue))["serial"]),
                     _href=URL(r=self.request, f="frm_tool/view/tool/"+retvalue), _target="_blank")
      else:
        retvalue = self.T("Missing tool...")
    elif fld_type == 'product':
      if len(self.db.product(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.db.product(id=int(retvalue))["description"]),
                     _href=URL(r=self.request, f="frm_product/view/product/"+retvalue), _target="_blank")
      else:
        retvalue = self.T("Missing product...")
    elif fld_type in ('trans','transitem','transmovement','transpayment'):
      if len(self.db.trans(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.db.trans(id=int(retvalue))["transnumber"]),
                     _href=URL(r=self.request, f="frm_trans/view/trans/"+retvalue), _target="_blank")
      else:
        retvalue = self.T("Missing transnumber...")
    elif fld_type == 'project':
      if len(self.db.project(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.db.project(id=int(retvalue))["pronumber"]),
                     _href=URL(r=self.request, f="frm_project/view/project/"+retvalue), _target="_blank")
      else:
        retvalue = self.T("Missing project...")
    elif fld_type == 'employee':
      if len(self.db.employee(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.db.employee(id=int(retvalue))["empnumber"]),
                     _href=URL(r=self.request, f="frm_employee/view/employee/"+retvalue), _target="_blank")
      else:
        retvalue = self.T("Missing employee...")
    elif fld_type == 'place':
      if len(self.db.place(id=int(retvalue)).items())>0:
        retvalue = A(SPAN(self.db.place(id=int(retvalue))["planumber"]),
                     _href=URL(r=self.request, f="frm_place/view/place/"+retvalue), _target="_blank")
      else:
        retvalue = self.T("Missing place...")
    elif fld_type == 'flink':
      retvalue = A(SPAN(retvalue), _href=retvalue, _target="_blank")
    elif fld_type == 'password':
      retvalue = "*****"
    else:
      pass
    return retvalue
  
  def set_password_field(self,fieldname,value):
    if not value or value=="":
      return ""
    else:
      try:
        key = fieldname[:8] if len(fieldname)>8 else fieldname.ljust(8,"*")
        return "XXX"+encodestring(des(key, padmode=PAD_PKCS5).encrypt(value))+"XXX"
      except:
        return value
    
  def get_password_field(self,fieldname,value):
    if value!=None and value!="" and value.startswith("XXX") and value.endswith("XXX"):
      try:
        key = fieldname[:8] if len(fieldname)>8 else fieldname.ljust(8,"*")
        return des(key, padmode=PAD_PKCS5).decrypt(decodestring(value[3:-3]))
      except:
        return value
    else:
      return value
  
  def dropTables(self):
    #specified in the order (Refuse to drop the table if any objects depend on it.)
    tables = ["ui_zipcatalog","pattern","movement","payment","item","trans","barcode","price","tool",
              "product","tax","rate","place","currency","project","customer","event","contact","address","numberdef",
              "log","fieldvalue","deffield","ui_audit","link","ui_userconfig","ui_filter","ui_printqueue","employee",
              "ui_viewfields","ui_groupinput","ui_reportsources","ui_reportfields","ui_report","ui_numtotext",
              "ui_message","ui_menufields","ui_menu","ui_locale","ui_language","ui_applview","groups"]
    for table in tables:
      try:
        queries = self.db._adapter._drop(table, "")
        for query in queries:
          self.db.executesql(query)
      except:
        continue
    self.db.commit()
    
  def createTable(self, table):
    query = self.db._adapter.create_table(table,migrate=False,fake_migrate=False)
    self.db._adapter.create_sequence_and_triggers(query,table)
    self.db.commit()
                   
  def defineTable(self, create=False):
    try:
      self.db._migrate_enabled = False
      if create:
        self.dropTables()
        
      table = self.db.define_table('groups',
        Field('id', readable=False, writable=False),
        Field('groupname', type='string', length=150, required=True, notnull=True),
        Field('groupvalue', type='string', length=150, required=True, notnull=True, label=self.T('Group')),
        Field('description', type='text', label=self.T('Description')),
        Field('inactive', type='integer', default=0, notnull=True, label=self.T('Inactive'), 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull = True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))  
      if create:
        if self.engine in("mssql"):
          table.description.type = 'string'
          table.description.length = 'max'
        self.createTable(table)
      
      table = self.db.define_table('ui_applview',
        Field('id', readable=False, writable=False),
        Field('viewname', type='string', length=150, required=True, notnull=True, unique=True),
        Field('sqlstr', type='text', required=True, notnull=True),
        Field('inistr', type='text'),
        Field('menu', type='string', length=150),
        Field('menuitem', type='string', length=150),
        Field('parentview', type='string', length=150, required=True, notnull=True),
        Field('orderby', type='integer', default=0, required=True, notnull=True))
      if create:
        if self.engine in("mssql"):
          table.sqlstr.type = 'string'
          table.sqlstr.length = 'max'
          table.inistr.type = 'string'
          table.inistr.length = 'max'
        self.createTable(table)
      
      table = self.db.define_table('ui_language',
        Field('id', readable=False, writable=False),
        Field('lang', type='string', length=2, required=True, notnull=True, unique=True),
        Field('description', type='string', length=150))
      if create:
        self.createTable(table)

      table = self.db.define_table('ui_locale',
        Field('id', readable=False, writable=False),
        Field('country', type='string', length=150, required=True, notnull=True, unique=True),
        Field('lang', type='string', length=2, required=True, notnull=True, 
              requires = IS_IN_DB(self.db(self.db.ui_language), self.db.ui_language.lang, '%(lang)s')),
        Field('description', type='text'))
      if create:
        if self.engine in("mssql"):
          table.description.type = 'string'
          table.description.length = 'max'
        self.createTable(table)

      table = self.db.define_table('ui_menu',
        Field('id', readable=False, writable=False),
        Field('menukey', type='string', length=255, required=True, notnull=True, unique=True),
        Field('description', type='string', length=255, required=True, notnull=True),
        Field('modul', type='string', length=255),
        Field('icon', type='string', length=255),
        Field('funcname', type='string', length=255, required=True, notnull=True),
        Field('url', type='integer', default=0, required=True, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('address', type='text'))
      if create:
        if self.engine in("mssql"):
          table.address.type = 'string'
          table.address.length = 'max'
        self.createTable(table)
     
      table = self.db.define_table('ui_menufields',
        Field('id', readable=False, writable=False),
        Field('menu_id', self.db.ui_menu, ondelete='CASCADE', notnull=True, required=True, 
              requires = IS_IN_DB(self.db, self.db.ui_menu.id, '%(menukey)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.ui_menu, "menukey", value)),
        Field('fieldname', type='string', length=150, required=True, notnull=True, label=self.T('Name')),
        Field('description', type='string', length=255, required=True, notnull=True),
        Field('fieldtype', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, label=self.T('Type'), 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('fieldtype')&self.db.groups.groupvalue.belongs(('bool','date','integer','float','string'))), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('orderby', type='integer', default=0, required=True, notnull=True, label=self.T('Order'),
              represent = lambda value,row: DIV(self.splitThousands(int(value)," ","."), _align="right", _width="100%")))
      if create:
        if self.engine in("mssql"):
          table.fieldtype.ondelete = "NO ACTION"
        self.createTable(table)
      
      table = self.db.define_table('ui_message',
        Field('id', readable=False, writable=False),
        Field('secname', type='string', length=150, required=True, notnull=True),
        Field('fieldname', type='string', length=150, required=True, notnull=True),
        Field('lang', type='string', length=2, required=True, notnull=True, 
              requires = IS_IN_DB(self.db(self.db.ui_language), self.db.ui_language.lang, '%(lang)s')),
        Field('msg', type='text', required=True, notnull=True))
      if create:
        if self.engine in("mssql"):
          table.msg.type = 'string'
          table.msg.length = 'max'
        self.createTable(table)

      table = self.db.define_table('ui_numtotext',
        Field('id', readable=False, writable=False),
        Field('lang', type='string', length=2, required=True, notnull=True, 
              requires = IS_IN_DB(self.db(self.db.ui_language), self.db.ui_language.lang, '%(lang)s')),
        Field('digi', type='integer', default=0, required=True, notnull=True),
        Field('deci', type='integer', default=0, required=True, notnull=True),
        Field('number_str', type='string', length=150),
        Field('number_str2', type='string', length=150))
      if create:
        self.createTable(table)

      table = self.db.define_table('ui_report',
        Field('id', readable=False, writable=False),                   
        Field('reportkey', type='string', length=255, required=True, notnull=True, unique=True),
        Field('nervatype', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('nervatype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('transtype', self.db.groups, ondelete='RESTRICT', 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db(self.db.groups.groupname.like('transtype')), self.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('direction', self.db.groups, ondelete='RESTRICT', 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db(self.db.groups.groupname.like('direction')), self.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('repname', type='string', length=255, required=True, notnull=True, label=self.T('Report')),
        Field('description', type='string', length=255, label=self.T('Description')),
        Field('label', type='string', length=255, label=self.T('Group')),
        Field('filetype', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('filetype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('report', type='text'))
      if create:
        if self.engine in("mssql"):
          table.nervatype.ondelete = "NO ACTION"
          table.transtype.ondelete = "NO ACTION"
          table.direction.ondelete = "NO ACTION"
          table.filetype.ondelete = "NO ACTION"
          table.report.type = 'string'
          table.report.length = 'max'
        self.createTable(table)

      table = self.db.define_table('ui_reportfields',
        Field('id', readable=False, writable=False),
        Field('report_id', self.db.ui_report, ondelete='CASCADE', notnull=True, required=True, 
              requires = IS_IN_DB(self.db, self.db.ui_report.id, '%(reportkey)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.ui_report, "reportkey", value)),
        Field('fieldname', type='string', length=150, required=True, notnull=True),
        Field('fieldtype', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('fieldtype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('wheretype', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('wheretype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('description', type='string', length=255),
        Field('orderby', type='integer', default=0, notnull=True, required=True),
        Field('sqlstr', type='text'),
        Field('parameter', type='integer', default=0, notnull=True, required=True,
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('dataset', type='string', length=150),
        Field('defvalue', type='string', length=255),
        Field('valuelist', type='text'))
      if create:
        if self.engine in("mssql"):
          table.fieldtype.ondelete = "NO ACTION"
          table.wheretype.ondelete = "NO ACTION"
          table.sqlstr.type = 'string'
          table.sqlstr.length = 'max'
          table.valuelist.type = 'string'
          table.valuelist.length = 'max'
        self.createTable(table)

      table = self.db.define_table('ui_reportsources',
        Field('id', readable=False, writable=False),
        Field('report_id', self.db.ui_report, ondelete='CASCADE', notnull=True, required=True, 
              requires = IS_IN_DB(self.db, self.db.ui_report.id, '%(reportkey)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.ui_report, "reportkey", value)),
        Field('dataset', type='string', length=150, notnull=True, required=True),
        Field('sqlstr', type='text'))
      if create:
        if self.engine in("mssql"):
          table.sqlstr.type = 'string'
          table.sqlstr.length = 'max'
        self.createTable(table)
      
      table = self.db.define_table('ui_groupinput',
        Field('id', readable=False, writable=False),
        Field('groups_id', self.db.groups, ondelete='CASCADE', notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('usergroup') & (self.db.groups.deleted==0)), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('formname', type='string', length=150, required=True, notnull=True),
        Field('contname', type='string', length=150, required=True, notnull=True),
        Field('isenabled', type='integer', default=0, required=True, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('isvisibled', type='integer', default=0, required=True, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        self.createTable(table)
      
      table = self.db.define_table('ui_viewfields',
        Field('id', readable=False, writable=False),
        Field('viewname', type='string', length=150, notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.ui_applview), self.db.ui_applview.viewname, '%(viewname)s')),
        Field('fieldname', type='string', length=150, required=True, notnull=True),
        Field('fieldtype', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('fieldtype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('wheretype', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('wheretype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('orderby', type='integer', default=0, notnull=True, required=True),
        Field('sqlstr', type='text'),
        Field('aggretype', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db(self.db.groups.groupname.like('aggretype')), self.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)))
      if create:
        if self.engine in("mssql"):
          table.fieldtype.ondelete = "NO ACTION"
          table.wheretype.ondelete = "NO ACTION"
          table.aggretype.ondelete = "NO ACTION"
          table.sqlstr.type = 'string'
          table.sqlstr.length = 'max'
        self.createTable(table)

      table = self.db.define_table('employee',
        Field('id', readable=False, writable=False),
        Field('empnumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.T('Employee No.')),
        Field('username', type='string', length=150, unique=True,
              requires=IS_EMPTY_OR(IS_NOT_IN_DB(self.db, "employee.username"))),
        Field('usergroup', self.db.groups, ondelete='RESTRICT', notnull=True, label=self.T('Usergroup'), 
              requires = IS_IN_DB(self.db((self.db.groups.groupname.like('usergroup'))&(self.db.groups.deleted==0)), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('startdate', type='date', label=self.T('Start Date')),
        Field('enddate', type='date', label=self.T('End Date')),
        Field('department', self.db.groups, ondelete='RESTRICT', required=False, 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db((self.db.groups.groupname.like('department'))&(self.db.groups.deleted==0)), self.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('inactive', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        #Field('password', type='password', length=512, readable=False, writable=False, 
        #      requires = [IS_EMPTY_OR(IS_STRONG(), CRYPT())]),
        Field('password', type='password', length=512, readable=False, writable=False),
        Field('email', length=128, #unique=True, 
              requires = [IS_EMPTY_OR(IS_EMAIL(error_message=self.T("Invalid email!")))]),
        Field('registration_key', length=512, writable=False, readable=False, default=''),
        Field('reset_password_key', length=512, writable=False, readable=False, default=''),
        Field('registration_id', length=512, writable=False, readable=False, default=''))
      if create:
        if self.engine in("mssql"):
          table.usergroup.ondelete = "NO ACTION"
          table.department.ondelete = "NO ACTION"
        self.createTable(table)

      table = self.db.define_table('ui_printqueue',
        Field('id', readable=False, writable=False),
        Field('nervatype', self.db.groups, ondelete='CASCADE', notnull=True, required=True, label=self.T('Doc.type'), 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('nervatype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self.get_nervatype_name(value,row.ref_id)),
        Field('ref_id', type='integer', notnull=True, required=True, label=self.T('Doc.No./Description'),
              represent = lambda value,row: A(SPAN(self.show_refnumber("refnumber", self.db.groups(id=row.nervatype).groupvalue, row.ref_id)),
                     _href=URL(r=self.request, f=self.show_refnumber("href", self.db.groups(id=row.nervatype).groupvalue, row.ref_id)), 
                     _target="_blank")),
        Field('qty', type='double', default=0, notnull=True, required=True, label=self.T('Copies'),
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('employee_id', self.db.employee, ondelete='CASCADE', notnull=True, required=True, label=self.T('Employee'), 
              requires = IS_IN_DB(self.db, self.db.employee.id, '%(username)s'),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.employee, "empnumber", value)),
                     _href=URL(r=self.request, f="frm_employee/view/employee/"+str(value)), _target="_blank")),
        Field('report_id', self.db.ui_report, ondelete='CASCADE', notnull=True, required=True, label=self.T('Template'), 
              requires = IS_IN_DB(self.db, self.db.ui_report.id, '%(reportkey)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.ui_report, "repname", value)),
        Field('crdate', type='date', notnull=True, required=True, label=self.T('Date'), default=datetime.datetime.now().date()))
      if create:
        if self.engine in("mssql"):
          table.employee_id.ondelete = "NO ACTION"
          table.report_id.ondelete = "NO ACTION"
        self.createTable(table)

      table = self.db.define_table('ui_filter',
        Field('id', readable=False, writable=False),
        Field('employee_id', self.db.employee, ondelete='CASCADE', notnull=True, required=True, 
              requires = IS_IN_DB(self.db, self.db.employee.id, '%(username)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.employee, "username", value)),
        Field('parentview', type='string', length=150, notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.ui_applview), self.db.ui_applview.viewname, '%(viewname)s')),
        Field('viewname', type='string', length=150, notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.ui_applview), self.db.ui_applview.viewname, '%(viewname)s')),
        Field('fieldname', type='string', length=150, required=True, notnull=True),
        Field('ftype', type='string', length=150, required=True, notnull=True),
        Field('fvalue', type='text'))
      if create:
        if self.engine in("mssql"):
          table.fvalue.type = 'string'
          table.fvalue.length = 'max'
        self.createTable(table)

      table = self.db.define_table('ui_userconfig',
        Field('id', readable=False, writable=False),
        Field('employee_id', self.db.employee, ondelete='CASCADE', notnull=True, required=True, 
              requires = IS_IN_DB(self.db, self.db.employee.id, '%(username)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.employee, "username", value)),
        Field('section', type='string', length=150),
        Field('cfgroup', type='string', length=150, notnull=True, required=True),
        Field('cfname', type='string', length=150, notnull=True, required=True),
        Field('cfvalue', type='text'),
        Field('orderby', type='integer', default=0, notnull=True, required=True))
      if create:
        if self.engine in("mssql"):
          table.cfvalue.type = 'string'
          table.cfvalue.length = 'max'
        self.createTable(table)

      table = self.db.define_table('link',
        Field('id', readable=False, writable=False),
        Field('nervatype_1', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('nervatype')), self.db.groups.id, '%(groupvalue)s')),
        Field('ref_id_1', type='integer', notnull=True, required=True),
        Field('nervatype_2', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('nervatype')), self.db.groups.id, '%(groupvalue)s')),
        Field('ref_id_2', type='integer', notnull=True, required=True),
        Field('linktype', type='integer', default=0, notnull=True),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.nervatype_1.ondelete = "NO ACTION"
          table.nervatype_2.ondelete = "NO ACTION"
        self.createTable(table)

      table = self.db.define_table('ui_audit',
        Field('id', readable=False, writable=False),
        Field('usergroup', self.db.groups, ondelete='CASCADE', notnull=True, 
              required=True, requires = IS_IN_DB(self.db(self.db.groups.groupname.like('usergroup') & (self.db.groups.deleted==0)), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('nervatype', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, label=self.T('Type'), 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('nervatype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('subtype', type='integer', 
              represent = lambda value,row: self.get_audit_subtype(row, value)),
        Field('inputfilter', self.db.groups, ondelete='RESTRICT', notnull=True, label=self.T('Filter'), 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('inputfilter')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('supervisor', type='integer', default=1, notnull=True, 
              requires=check_boolean(self.T), widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.nervatype.ondelete = "NO ACTION"
          table.inputfilter.ondelete = "NO ACTION"
        self.createTable(table)

      table = self.db.define_table('deffield',
        Field('id', readable=False, writable=False),
        Field('fieldname', type='string', length=150, required=True, notnull=True, unique=True),
        Field('nervatype', self.db.groups, ondelete='RESTRICT', notnull=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('nervatype')
                & self.db.groups.groupvalue.belongs(('address', 'contact', 'customer', 'employee', 'event', 'groups', 'item', 'link', 
                                                     'log', 'movement', 'price', 'place', 'product', 'project', 'tool', 'trans'))), 
                self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('subtype', self.db.groups, ondelete='RESTRICT', 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db, self.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('fieldtype', self.db.groups, ondelete='RESTRICT', notnull=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('fieldtype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('description', type='text', notnull=True),
        Field('valuelist', type='text'),
        Field('addnew', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('visible', type='integer', default=1, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('readonly', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.nervatype.ondelete = "NO ACTION"
          table.subtype.ondelete = "NO ACTION"
          table.fieldtype.ondelete = "NO ACTION"
          table.description.type = 'string'
          table.description.length = 'max'
          table.valuelist.type = 'string'
          table.valuelist.length = 'max'
        self.createTable(table) 

      table = self.db.define_table('fieldvalue',
        Field('id', readable=False, writable=False),
        Field('fieldname', type='string', length=150, 
              requires = IS_IN_DB(self.db(self.db.deffield), self.db.deffield.fieldname, '%(description)s (%(fieldname)s)')),
        Field('ref_id', type='integer'),
        Field('value', type='text', 
              requires = check_fieldvalue(self, self.request.vars),
              represent = lambda value,row: self.show_fieldvalue(row["fieldvalue"])),
        Field('notes', type='text', label=self.T('Other data')),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.value.type = 'string'
          table.value.length = 'max'
          table.notes.type = 'string'
          table.notes.length = 'max'
        self.createTable(table)

      table = self.db.define_table('log',
        Field('id', readable=False, writable=False),
        Field('nervatype', self.db.groups, ondelete='RESTRICT', label=self.T('Ref.type'),
              requires = IS_EMPTY_OR(IS_IN_DB(self.db(self.db.groups.groupname.like('nervatype')), self.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('ref_id', type='integer', label=self.T('Doc.No./Description'),
              represent = lambda value,row: A(SPAN(self.show_refnumber("refnumber", self.db.groups(id=row.nervatype).groupvalue, row.ref_id)),
                     _href=URL(r=self.request, f=self.show_refnumber("href", self.db.groups(id=row.nervatype).groupvalue, row.ref_id)), _target="_blank")),
        Field('logstate', self.db.groups, ondelete='CASCADE', notnull=True, required=True, label=self.T('State'),
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('logstate')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('employee_id', self.db.employee, ondelete='RESTRICT', notnull=True, required=True, label=self.T('Username'),
              requires = IS_IN_DB(self.db, self.db.employee.id, '%(username)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.employee, "username", value)),
        Field('crdate', type='datetime', notnull=True, required=True, default=datetime.datetime.now(), label=self.T('Date')))
      if create:
        if self.engine in("mssql"):
          table.nervatype.ondelete = "NO ACTION"
          table.employee_id.ondelete = "NO ACTION"
        self.createTable(table)
     
      table = self.db.define_table('numberdef',
        Field('id', readable=False, writable=False),
        Field('numberkey', type='string', length=150, required=True, notnull=True, unique=True, label=self.T('Code')),
        Field('prefix', type='string', length=150, label=self.T('Prefix')),
        Field('curvalue', type='integer', default=0, notnull=True, label=self.T('Value'),
              represent = lambda value,row: DIV(self.splitThousands(int(value)," ","."), _align="right", _width="100%")),
        Field('isyear', type='integer', default=1, notnull=True, label=self.T('Year'), 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('sep', type='string', length=1, default="/",
              represent = lambda value,row: DIV(value, _align="center", _width="100%")),
        Field('len', type='integer', default=5, notnull=True,
              represent = lambda value,row: DIV(self.splitThousands(int(value)," ","."), _align="right", _width="100%")),
        Field('description', type='text'),
        Field('visible', type='integer', default=1, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('readonly', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('orderby', type='integer', default=0, notnull=True))
      if create:
        if self.engine in("mssql"):
          table.description.type = 'string'
          table.description.length = 'max'
        self.createTable(table)
      
      table = self.db.define_table('address',
        Field('id', readable=False, writable=False),
        Field('nervatype', self.db.groups, ondelete='RESTRICT', notnull=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('nervatype')
                                          & self.db.groups.groupvalue.belongs(('customer', 'employee', 'event', 'place', 'product', 'project', 'tool', 'trans'))
                                  ), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('ref_id', type='integer', notnull=True),
        Field('country', type='string', length=255, label=self.T('Country')),
        Field('state', type='string', length=255, label=self.T('State')),
        Field('zipcode', type='string', length=150, label=self.T('Zipcode')),
        Field('city', type='string', length=255, label=self.T('City')),
        Field('street', type='text', label=self.T('Street')),
        Field('notes', type='text', label=self.T('Comment')),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.nervatype.ondelete = "NO ACTION"
          table.street.type = 'string'
          table.street.length = 'max'
          table.notes.type = 'string'
          table.notes.length = 'max'
        self.createTable(table)
      
      table = self.db.define_table('contact',
        Field('id', readable=False, writable=False),
        Field('nervatype', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('nervatype')
                                          & self.db.groups.groupvalue.belongs(('customer', 'employee', 'event', 'place', 'product', 'project', 'tool', 'trans'))
                                 ), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('ref_id', type='integer', notnull=True, required=True),
        Field('firstname', type='string', length=255, label=self.T('Firstname')),
        Field('surname', type='string', length=255, label=self.T('Surname')),
        Field('status', type='string', length=255, label=self.T('Status')),
        Field('phone', type='string', length=255, label=self.T('Phone')),
        Field('fax', type='string', length=255, label=self.T('Fax')),
        Field('mobil', type='string', length=255, label=self.T('Mobil')),
        Field('email', type='string', length=255, label=self.T('Email'), 
              requires = IS_EMPTY_OR(IS_EMAIL(error_message=self.T('invalid email!')))),
        Field('notes', type='text', label=self.T('Comment')),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.nervatype.ondelete = "NO ACTION"
          table.notes.type = 'string'
          table.notes.length = 'max'
        self.createTable(table)

      table = self.db.define_table('event',
        Field('id', readable=False, writable=False),
        Field('calnumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.T('Event No.')),
        Field('nervatype', self.db.groups, ondelete='RESTRICT', notnull=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('nervatype')
                & self.db.groups.groupvalue.belongs(('customer', 'employee', 'place', 'product', 'project', 'tool', 'trans'))
                ), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('ref_id', type='integer', notnull=True),
        Field('uid', type='string', length=255, label=self.T('UID')),
        Field('eventgroup', self.db.groups, ondelete='CASCADE', label=self.T('Group'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db(self.db.groups.groupname.like('eventgroup') & (self.db.groups.deleted==0)), self.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('fromdate', type='datetime', label=self.T('Start Date')),
        Field('todate', type='datetime', label=self.T('End Date')),
        Field('subject', type='string', length=255, label=self.T('Subject')),
        Field('place', type='string', length=255, label=self.T('Place')),
        Field('description', type='text', label=self.T('Description')),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.nervatype.ondelete = "NO ACTION"
          table.description.type = 'string'
          table.description.length = 'max'
        self.createTable(table)
         
      table = self.db.define_table('customer',
        Field('id', readable=False, writable=False),
        Field('custtype', self.db.groups, ondelete='RESTRICT', notnull=True, label=self.T('Customer Type'), 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('custtype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('custnumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.T('Customer No.')),
        Field('custname', type='string', length=255, notnull=True, label=self.T('Customer Name')),
        Field('taxnumber', type='string', length=255, label=self.T('Taxnumber')),
        Field('account', type='string', length=255, label=self.T('Account')),
        Field('notax', type='integer', default=0, notnull=True, label=self.T('Tax-free'), 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('terms', type='integer', default=0, notnull=True, label=self.T('Payment per.'),
              represent = lambda value,row: DIV(self.splitThousands(int(value)," ","."), _align="right", _width="100%")),
        Field('creditlimit', type='double', default=0, notnull=True, label=self.T('Credit line'),
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('discount', type='double', default=0, notnull=True, label=self.T('Discount%'),
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('notes', type='text', label=self.T('Comment')),
        Field('inactive', type='integer', default=0, notnull=True, label=self.T('Inactive'),
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.custtype.ondelete = "NO ACTION"
          table.notes.type = 'string'
          table.notes.length = 'max'
        self.createTable(table)

      table = self.db.define_table('project',
        Field('id', readable=False, writable=False),
        Field('pronumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.T('Project No.')),
        Field('description', type='string', length=255, label=self.T('Project')),
        Field('customer_id', self.db.customer, ondelete='RESTRICT', label=self.T('Customer'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db, self.db.customer.id, '%(custname)s (%(custnumber)s)')),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.customer, "custname", value)),
                     _href=URL(r=self.request, f="frm_customer/view/customer/"+str(value)), _target="_blank")),
        Field('startdate', type='date', label=self.T('Start Date')),
        Field('enddate', type='date', label=self.T('End Date')),
        Field('notes', type='text'),
        Field('inactive', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.customer_id.ondelete = "CASCADE"
          table.notes.type = 'string'
          table.notes.length = 'max'
        self.createTable(table)
      
      table = self.db.define_table('currency',
        Field('id', readable=False, writable=False),
        Field('curr', type='string', length=3, required=True, notnull=True, unique=True),
        Field('description', type='string', length=255),
        Field('digit', type='integer', default=0, notnull=True,
              represent = lambda value,row: DIV(self.splitThousands(int(value)," ","."), _align="right", _width="100%")),
        Field('defrate', type='double', default=0, notnull=True, label=self.T('Def.Rate'),
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('cround', type='integer', default=0, notnull=True, label=self.T('Round'),
              represent = lambda value,row: DIV(self.splitThousands(int(value)," ","."), _align="right", _width="100%")))
      if create:
        self.createTable(table)
      
      table = self.db.define_table('place',
        Field('id', readable=False, writable=False),
        Field('planumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.T('Place No.')),
        Field('placetype', self.db.groups, ondelete='RESTRICT', notnull=True, label=self.T('Type'), 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('placetype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('description', type='string', length=255, notnull=True),
        Field('place_id', 'reference place', ondelete='RESTRICT', label=self.T('Ref.No.')),
        Field('curr', type='string', length=3, 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db(self.db.currency), self.db.currency.curr, '%(curr)s'))),
        Field('storetype', self.db.groups, ondelete='RESTRICT', label=self.T('StoreType'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db(self.db.groups.groupname.like('storetype')), self.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('defplace', type='integer', default=0, notnull=True, label=self.T('Default'), 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('notes', type='text', label=self.T('Comment')),
        Field('inactive', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      self.db.place.place_id.requires = IS_EMPTY_OR(IS_IN_DB(self.db, self.db.place.id, '%(description)s (%(planumber)s)'))
      self.db.place.place_id.represent = lambda value,row: self._link_id_formatter(self.db.place, "planumber", value)
      if create:
        if self.engine in("mssql"):
          table.placetype.ondelete = "NO ACTION"
          table.place_id.ondelete = "NO ACTION"
          table.storetype.ondelete = "NO ACTION"
          table.notes.type = 'string'
          table.notes.length = 'max'
        self.createTable(table)

      table = self.db.define_table('rate',
        Field('id', readable=False, writable=False),
        Field('ratetype', self.db.groups, ondelete='RESTRICT', notnull=True, required=True, label=self.T('Type'), 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('ratetype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('ratedate', type='date', notnull=True, required=True, label=self.T('Date')),
        Field('curr', type='string', length=3, required=True, notnull=True, 
              requires = IS_IN_DB(self.db(self.db.currency), self.db.currency.curr, '%(curr)s')),
        Field('place_id', self.db.place, ondelete='RESTRICT', label=self.T('Account No.'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db((self.db.place.deleted==0)&self.db.place.placetype.belongs(
                           self.db((self.db.groups.groupname=='placetype')&(self.db.groups.groupvalue=='bank')
                                      ).select(self.db.groups.id))), self.db.place.id, '%(planumber)s (%(description)s)')),
              represent = lambda value,row: self._link_id_formatter(self.db.place, "planumber", value)),
        Field('rategroup', self.db.groups, ondelete='RESTRICT', label=self.T('Group'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db((self.db.groups.deleted==0)&self.db.groups.groupname.like('rategroup')), self.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('ratevalue', type='double', default=0, notnull=True, label=self.T('Value'),
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.ratetype.ondelete = "NO ACTION"
          table.place_id.ondelete = "CASCADE"
          table.rategroup.ondelete = "NO ACTION"
        self.createTable(table)

      table = self.db.define_table('tax',
        Field('id', readable=False, writable=False),
        Field('taxcode', type='string', length=150, required=True, notnull=True, unique=True),                
        Field('description', type='string', length=255, notnull=True),
        Field('rate', type='double', default=0, notnull=True,
              requires = IS_FLOAT_IN_RANGE(0, 1, dot=".", error_message=self.T('Valid range: 0-1')),
              represent = lambda value,row: DIV(str(float(value)*100)+"%", _align="right", _width="100%")),
        Field('inactive', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        self.createTable(table)

      table = self.db.define_table('product',
        Field('id', readable=False, writable=False),
        Field('partnumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.T('Product No.')),
        Field('protype', self.db.groups, ondelete='RESTRICT', notnull=True, label=self.T('Product type'), 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('protype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('description', type='string', length=255, notnull=True, label=self.T('Product name')),
        Field('unit', type='string', length=150, notnull=True),
        Field('tax_id', self.db.tax, ondelete='RESTRICT', label=self.T('Tax'), 
              requires = IS_IN_DB(self.db, self.db.tax.id, '%(taxcode)s'),
              represent = lambda value,row: DIV(self._link_id_formatter(self.db.tax, "taxcode", value), _align="right", _width="100%")),
        Field('notes', type='text'),
        Field('webitem', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('inactive', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.protype.ondelete = "NO ACTION"
          table.tax_id.ondelete = "CASCADE"
          table.notes.type = 'string'
          table.notes.length = 'max'
        self.createTable(table)

      table = self.db.define_table('tool',
        Field('id', readable=False, writable=False),
        Field('serial', type='string', length=150, required=True, notnull=True, unique=True),
        Field('description', type='text'),
        Field('product_id', self.db.product, ondelete='RESTRICT', label=self.T('Product'),
              requires = IS_IN_DB(self.db, self.db.product.id, '%(description)s (%(partnumber)s)'),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.product, "description", value)),
                     _href=URL(r=self.request, f="frm_product/view/product/"+str(value)), _target="_blank")),
        Field('toolgroup', self.db.groups, ondelete='RESTRICT', label=self.T('Group'),
              requires = IS_EMPTY_OR(IS_IN_DB(self.db(self.db.groups.groupname.like('toolgroup') & (self.db.groups.deleted==0)), self.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('notes', type='text'),
        Field('inactive', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.product_id.ondelete = "CASCADE"
          table.toolgroup.ondelete = "NO ACTION"
          table.description.type = 'string'
          table.description.length = 'max'
          table.notes.type = 'string'
          table.notes.length = 'max'
        self.createTable(table)

      table = self.db.define_table('price',
        Field('id', readable=False, writable=False),
        Field('product_id', self.db.product, ondelete='CASCADE', label=self.T('Product'), 
              requires = IS_IN_DB(self.db, self.db.product.id, '%(description)s (%(partnumber)s)'),
              represent = lambda value,row: A(SPAN(self.db.product(id=int(value))["description"]),
                     _href=URL(r=self.request, f="frm_product/view/product/"+str(value)), _target="_blank")),
        Field('validfrom', type='date', notnull=True, label=self.T('Start Date')),
        Field('validto', type='date', label=self.T('End Date')),
        Field('curr', type='string', length=3, notnull=True, 
              requires = IS_IN_DB(self.db(self.db.currency), self.db.currency.curr, '%(curr)s')),
        Field('qty', type='double', default=0,
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('pricevalue', type='double', default=0, notnull=True, label=self.T('Price'),
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('discount', type='double',
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('calcmode', self.db.groups, ondelete='RESTRICT', notnull=True, label=self.T('Mode'), 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('calcmode')), self.db.groups.id, '%(description)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "description", value)),
        Field('vendorprice', type='integer', default=0, notnull=True, label=self.T('Vendor'), 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.calcmode.ondelete = "NO ACTION"
        self.createTable(table)

      table = self.db.define_table('barcode',
        Field('id', readable=False, writable=False),
        Field('code', type='string', length=255, required=True, notnull=True, unique=True),
        Field('product_id', self.db.product, ondelete='CASCADE', label=self.T('Product'),
              requires = IS_IN_DB(self.db, self.db.product.id, '%(description)s (%(partnumber)s)'),
              represent = lambda value,row: A(SPAN(self.db.product(id=int(value))["description"]),
                     _href=URL(r=self.request, f="frm_product/view/product/"+str(value)), _target="_blank")),
        Field('description', type='text'),
        Field('barcodetype', self.db.groups, ondelete='RESTRICT', notnull=True, label=self.T('Type'), 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('barcodetype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('qty', type='double', default=0, notnull=True,
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('defcode', type='integer', default=0, notnull=True, label=self.T('Default'), 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.barcodetype.ondelete = "NO ACTION"
          table.description.type = 'string'
          table.description.length = 'max'
        self.createTable(table)

      table = self.db.define_table('trans',
        Field('id', readable=False, writable=False),
        Field('transnumber', type='string', length=150, required=True, notnull=True, unique=True, label=self.T('Doc.No.')),
        Field('transtype', self.db.groups, ondelete='RESTRICT', notnull=True, label=self.T('Doc.Type'), 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('transtype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('direction', self.db.groups, ondelete='RESTRICT', notnull=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('direction')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('ref_transnumber', type='string', length=150, label=self.T('Ref.No.')),
        Field('crdate', type='date', notnull=True, label=self.T('Creation')),
        Field('transdate', type='date', notnull=True),
        Field('duedate', type='datetime'),
        Field('customer_id', self.db.customer, ondelete='RESTRICT', label=self.T('Customer'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db, self.db.customer.id, '%(custname)s (%(custnumber)s)')),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.customer, "custname", value)),
                     _href=URL(r=self.request, f="frm_customer/view/customer/"+str(value)), _target="_blank")),
        Field('employee_id', self.db.employee, ondelete='RESTRICT', label=self.T('Employee'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db, self.db.employee.id, '%(empnumber)s')),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.employee, "empnumber", value)),
                     _href=URL(r=self.request, f="frm_employee/view/employee/"+str(value)), _target="_blank")),
        Field('department', self.db.groups, ondelete='RESTRICT', 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db(self.db.groups.groupname.like('department') & (self.db.groups.deleted==0)), self.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('project_id', self.db.project, ondelete='RESTRICT', label=self.T('Project'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db, self.db.project.id, '%(pronumber)s')),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.project, "pronumber", value)),
                     _href=URL(r=self.request, f="frm_project/view/project/"+str(value)), _target="_blank")),
        Field('place_id', self.db.place, ondelete='RESTRICT', label=self.T('Place'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db, self.db.place.id, '%(description)s (%(planumber)s)')),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.place, "planumber", value)),
                     _href=URL(r=self.request, f="frm_place/view/place/"+str(value)), _target="_blank")),
        Field('paidtype', self.db.groups, ondelete='RESTRICT', label=self.T('Payment'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db(self.db.groups.groupname.like('paidtype') & (self.db.groups.deleted==0)), self.db.groups.id, '%(groupvalue)s')),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('curr', type='string', length=3, 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db(self.db.currency), self.db.currency.curr, '%(curr)s'))),
        Field('notax', type='integer', default=0, notnull=True, requires=check_boolean(self.T), widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('paid', type='integer', default=0, notnull=True, requires=check_boolean(self.T), widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('acrate', type='double', default=0, label=self.T('Acc.Rate'),
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('notes', type='text', label=self.T('Comment')),
        Field('intnotes', type='text', label=self.T('Internal notes')),
        Field('fnote', type='text'),
        Field('transtate', self.db.groups, ondelete='RESTRICT', notnull=True, label=self.T('State'),
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('transtate')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('closed', type='integer', default=0, notnull=True, requires=check_boolean(self.T), widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, requires=check_boolean(self.T), widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('cruser_id', self.db.employee, ondelete='RESTRICT', 
              requires = IS_IN_DB(self.db, self.db.employee.id, '%(username)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.employee, "username", value)))
      if create:
        if self.engine in("mssql"):
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
        self.createTable(table)

      table = self.db.define_table('item',
        Field('id', readable=False, writable=False),
        Field('trans_id', self.db.trans, ondelete='CASCADE', label=self.T('Doc.No.'),
              requires = IS_IN_DB(self.db, self.db.trans.id, '%(transnumber)s'),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.trans, "transnumber", value)),
                     _href=URL(r=self.request, f="frm_trans/view/trans/"+str(value)), _target="_blank")),
        Field('product_id', self.db.product, ondelete='CASCADE', label=self.T('Product'), 
              requires = IS_IN_DB(self.db, self.db.product.id, '%(description)s (%(partnumber)s)'),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.product, "description", value)),
                     _href=URL(r=self.request, f="frm_product/view/product/"+str(value)), _target="_blank")),
        Field('unit', type='string', length=150, notnull=True),
        Field('qty', type='double', default=0, notnull=True,
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('fxprice', type='double', default=0, notnull=True, label=self.T('UnitPrice'),
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('netamount', type='double', default=0, notnull=True, label=self.T('NetAmount'),
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('discount', type='double', default=0, notnull=True,
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('tax_id', self.db.tax, ondelete='CASCADE', label=self.T('TaxRate'), 
              requires = IS_IN_DB(self.db, self.db.tax.id, '%(taxcode)s'),
              represent = lambda value,row: DIV(self._link_id_formatter(self.db.tax, "taxcode", value), _align="right", _width="100%")),
        Field('vatamount', type='double', default=0, notnull=True, label=self.T('VAT'),
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('amount', type='double', default=0, notnull=True,
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('description', type='text', notnull=True),
        Field('deposit', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('ownstock', type='double', default=0, notnull=True, label=self.T('OwnStock'),
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('actionprice', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.description.type = 'string'
          table.description.length = 'max'
          table.tax_id.ondelete = "NO ACTION"
        self.createTable(table)

      table = self.db.define_table('payment',
        Field('id', readable=False, writable=False),
        Field('trans_id', self.db.trans, ondelete='CASCADE', label=self.T('Doc No.'), 
              requires = IS_IN_DB(self.db, self.db.trans.id, '%(transnumber)s'),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.trans, "transnumber", value)),
                     _href=URL(r=self.request, f="frm_trans/view/trans/"+str(value)), _target="_blank")),
        Field('paiddate', type='date', notnull=True, label=self.T('PaymentDate')),
        Field('amount', type='double', default=0, notnull=True,
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('notes', type='text', label=self.T('Description')),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.notes.type = 'string'
          table.notes.length = 'max'
        self.createTable(table)

      table = self.db.define_table('movement',
        Field('id', readable=False, writable=False),
        Field('trans_id', self.db.trans, ondelete='CASCADE', label=self.T('Document No.'), 
              requires = IS_IN_DB(self.db, self.db.trans.id, '%(transnumber)s'),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.trans, "transnumber", value)),
                     _href=URL(r=self.request, f="frm_trans/view/trans/"+str(value)), _target="_blank")),
        Field('shippingdate', type='datetime', notnull=True, label=self.T('Shipping Date')),
        Field('movetype', self.db.groups, ondelete='RESTRICT', notnull=True, 
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('movetype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('product_id', self.db.product, ondelete='RESTRICT', label=self.T('Product'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db, self.db.product.id, '%(description)s (%(partnumber)s)')),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.product, "description", value)),
                     _href=URL(r=self.request, f="frm_product/view/product/"+str(value)), _target="_blank")),
        Field('tool_id', self.db.tool, ondelete='RESTRICT', label=self.T('Serial'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db, self.db.tool.id, '%(serial)s')),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.tool, "serial", value)),
                     _href=URL(r=self.request, f="frm_tool/view/tool/"+str(value)), _target="_blank")),
        Field('place_id', self.db.place, ondelete='RESTRICT', label=self.T('Place No.'), 
              requires = IS_EMPTY_OR(IS_IN_DB(self.db, self.db.place.id, '%(description)s (%(planumber)s)')),
              represent = lambda value,row: A(SPAN(self._link_id_formatter(self.db.place, "planumber", value)),
                     _href=URL(r=self.request, f="frm_place/view/place/"+str(value)), _target="_blank")),
        Field('qty', type='double', default=0, notnull=True,
              represent = lambda value,row: DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")),
        Field('notes', type='text', label=self.T('Batch No.')),
        Field('shared', type='integer', default=0, notnull=True, label=self.T('Not shared'), 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.movetype.ondelete = "NO ACTION"
          table.product_id.ondelete = "NO ACTION"
          table.tool_id.ondelete = "NO ACTION"
          table.place_id.ondelete = "NO ACTION"
          table.notes.type = 'string'
          table.notes.length = 'max'
        self.createTable(table)

      table = self.db.define_table('pattern',
        Field('id', readable=False, writable=False),
        Field('description', type='string', length=150, required=True, notnull=True, unique=True),
        Field('transtype', self.db.groups, ondelete='RESTRICT', notnull=True, label=self.T('Doc.type'),
              requires = IS_IN_DB(self.db(self.db.groups.groupname.like('transtype')), self.db.groups.id, '%(groupvalue)s'),
              represent = lambda value,row: self._link_id_formatter(self.db.groups, "groupvalue", value)),
        Field('notes', type='text'),
        Field('defpattern', type='integer', label=self.T('Default'), default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))),
        Field('deleted', type='integer', default=0, notnull=True, 
              requires=check_boolean(self.T), 
              widget=lambda field,value: SQLFORM.widgets.boolean.widget(field,bool(value))))
      if create:
        if self.engine in("mssql"):
          table.transtype.ondelete = "NO ACTION"
          table.notes.type = 'string'
          table.notes.length = 'max'
        self.createTable(table)

      table = self.db.define_table('ui_zipcatalog',
        Field('id', readable=False, writable=False),
        Field('country', type='string', length=150, required=True, notnull=True, 
              requires = IS_IN_DB(self.db(self.db.ui_locale), self.db.ui_locale.country, '%(country)s')),
        Field('zipcode', type='string', length=150, notnull=True, required=True),
        Field('city', type='string', length=150, notnull=True, required=True))
      if create:
        self.createTable(table)
  
      return True
    except Exception, err:
      self.error_message = err
      return False
    
  def createIndex(self):
    try:
      self.db.executesql("CREATE UNIQUE INDEX groups_namevalue_idx ON groups (groupname, groupvalue)")
      self.db.executesql("CREATE INDEX groups_groupname_idx ON groups (groupname)")
      self.db.executesql("CREATE INDEX groups_groupvalue_id_idx ON groups (groupvalue)")
      self.db.executesql("CREATE INDEX groups_deleted_idx ON groups (deleted)")
      self.db.executesql("CREATE INDEX groups_inactive_idx ON groups (inactive)")
      
      self.db.executesql("CREATE UNIQUE INDEX applview_viewname_idx ON ui_applview (viewname)")
      self.db.executesql("CREATE INDEX applview_parent_idx ON ui_applview (parentview)")
          
      self.db.executesql("CREATE INDEX menucmd_modul_idx ON ui_menu (modul)")
      
      self.db.executesql("CREATE INDEX menufields_menu_idx ON ui_menufields (menu_id)")
      
      self.db.executesql("CREATE UNIQUE INDEX message_pk_idx ON ui_message (secname, fieldname, lang)")
      self.db.executesql("CREATE INDEX message_fieldname_idx ON ui_message (fieldname)")
      self.db.executesql("CREATE INDEX message_lang_idx ON ui_message (lang)")
      self.db.executesql("CREATE INDEX message_secname_idx ON ui_message (secname)")
      
      self.db.executesql("CREATE UNIQUE INDEX numtotext_pk_idx ON ui_numtotext (lang, digi, deci)")
      
      self.db.executesql("CREATE UNIQUE INDEX report_reportkey_idx ON ui_report (reportkey)")
      self.db.executesql("CREATE INDEX report_filetype_idx ON ui_report (filetype)")
      self.db.executesql("CREATE INDEX report_reporttype_idx ON ui_report (nervatype)")
      
      self.db.executesql("CREATE UNIQUE INDEX reportfields_pk_idx ON ui_reportfields (report_id, fieldname)")
      self.db.executesql("CREATE INDEX reportfields_report_id_idx ON ui_reportfields (report_id)")
      
      self.db.executesql("CREATE UNIQUE INDEX reportsources_pk_idx ON ui_reportsources (report_id, dataset)")
      self.db.executesql("CREATE INDEX reportsources_reports_idx ON ui_reportsources (report_id)")
      
      self.db.executesql("CREATE UNIQUE INDEX groupinput_pk_idx ON ui_groupinput (groups_id, formname, contname)")
      self.db.executesql("CREATE INDEX groupinput_contname_idx ON ui_groupinput (contname)")
      self.db.executesql("CREATE INDEX groupinput_formname_idx ON ui_groupinput (formname)")
      self.db.executesql("CREATE INDEX groupinput_groups_id_idx ON ui_groupinput (groups_id)")

      self.db.executesql("CREATE UNIQUE INDEX viewfields_pk_idx ON ui_viewfields (viewname, fieldname)")
      self.db.executesql("CREATE INDEX viewfields_viewname_idx ON ui_viewfields (viewname)")
      self.db.executesql("CREATE INDEX viewfields_fieldname_idx ON ui_viewfields (fieldname)")
      
      self.db.executesql("CREATE UNIQUE INDEX employee_empnumber_idx ON employee (empnumber)")
      self.db.executesql("CREATE UNIQUE INDEX employee_username_idx ON employee (username)")
      self.db.executesql("CREATE INDEX employee_inactiv_idx ON employee (inactive)")
      self.db.executesql("CREATE INDEX employee_deleted_idx ON employee (deleted)")
      
      self.db.executesql("CREATE INDEX printqueue_nervatype_idx ON ui_printqueue (nervatype)")
      self.db.executesql("CREATE INDEX printqueue_usename_idx ON ui_printqueue (employee_id)")
      
      self.db.executesql("CREATE INDEX filter_parent_idx ON ui_filter (parentview)")

      self.db.executesql("CREATE INDEX idx_userconfig_pk ON ui_userconfig (employee_id, cfgroup, cfname)")
      self.db.executesql("CREATE INDEX idx_userconfig_ec ON ui_userconfig (employee_id, cfgroup)")
      self.db.executesql("CREATE INDEX idx_userconfig_employee_ide ON ui_userconfig (employee_id)")

      self.db.executesql("CREATE INDEX idx_link_nervatype_1 ON link (nervatype_1)")
      self.db.executesql("CREATE INDEX idx_link_ref_id_1 ON link (ref_id_1)")
      self.db.executesql("CREATE INDEX idx_link_nervatype_2 ON link (nervatype_2)")
      self.db.executesql("CREATE INDEX idx_link_ref_id_2 ON link (ref_id_2)")
      self.db.executesql("CREATE INDEX idx_link_deleted ON link (deleted)")
      
      self.db.executesql("CREATE UNIQUE INDEX idx_audit_pk ON ui_audit (usergroup, nervatype, subtype)")
      self.db.executesql("CREATE INDEX idx_audit_usergroup ON ui_audit (usergroup)")
      
      self.db.executesql("CREATE UNIQUE INDEX deffield_fieldname_idx ON deffield (fieldname)")
      self.db.executesql("CREATE INDEX deffield_nervatype_id_idx ON deffield (nervatype, subtype)")
      self.db.executesql("CREATE INDEX deffield_deleted_idx ON deffield (deleted)")

      self.db.executesql("CREATE INDEX fieldvalue_fieldname_idx ON fieldvalue (fieldname)")
      self.db.executesql("CREATE INDEX fieldvalue_ref_id_idx ON fieldvalue (ref_id)")

      self.db.executesql("CREATE INDEX log_logstate_idx ON log (logstate)")
      self.db.executesql("CREATE INDEX log_nervatype_idx ON log (nervatype, ref_id)")
      
      self.db.executesql("CREATE UNIQUE INDEX numberdef_numberkey_idx ON numberdef (numberkey)")
      
      self.db.executesql("CREATE INDEX address_nervatype_idx ON address (nervatype, ref_id)")
      self.db.executesql("CREATE INDEX address_deleted_idx ON address (deleted)")
      
      self.db.executesql("CREATE INDEX contact_nervatype_idx ON contact (nervatype, ref_id)")
      self.db.executesql("CREATE INDEX contact_deleted_idx ON contact (deleted)")
      
      self.db.executesql("CREATE UNIQUE INDEX event_calnumber_idx ON event (calnumber)")
      self.db.executesql("CREATE INDEX event_fromdate_idx ON event (fromdate)")
      self.db.executesql("CREATE INDEX event_eventgroup_idx ON event (eventgroup)")
      self.db.executesql("CREATE INDEX event_nervatype_idx ON event (nervatype)")
      self.db.executesql("CREATE INDEX event_ref_idx ON event (ref_id)")
      self.db.executesql("CREATE INDEX event_deleted_idx ON event (deleted)")
      self.db.executesql("CREATE INDEX event_uid_idx ON event (uid)")
      
      self.db.executesql("CREATE UNIQUE INDEX customer_custnumber_idx ON customer (custnumber)")
      self.db.executesql("CREATE INDEX customer_custtype_idx ON customer (custtype)")
      self.db.executesql("CREATE INDEX customer_inactive_idx ON customer (inactive)")
      self.db.executesql("CREATE INDEX customer_deleted_idx ON customer (deleted)")
      self.db.executesql("CREATE INDEX customer_custname_idx ON customer (custname)")
      
      self.db.executesql("CREATE UNIQUE INDEX project_pronumber_idx ON project (pronumber)")
      self.db.executesql("CREATE INDEX project_customer_id_idx ON project (customer_id)")
      self.db.executesql("CREATE INDEX project_inactive_idx ON project (inactive)")
      self.db.executesql("CREATE INDEX project_deleted_idx ON project (deleted)")
      
      self.db.executesql("CREATE UNIQUE INDEX currency_curr_idx ON currency (curr)")
      
      self.db.executesql("CREATE UNIQUE INDEX place_planumber_idx ON place (planumber)")
      self.db.executesql("CREATE INDEX place_placetype_idx ON place (placetype)")
      self.db.executesql("CREATE INDEX place_deleted_idx ON place (deleted)")
      
      self.db.executesql("CREATE INDEX rate_curr_idx ON rate (curr)")
      self.db.executesql("CREATE INDEX rate_ref_idx ON rate (ratedate, curr, place_id, ratetype)")
      self.db.executesql("CREATE INDEX rate_ratedate_idx ON rate (ratedate)")
      self.db.executesql("CREATE INDEX rate_deleted_idx ON rate (deleted)")
      
      self.db.executesql("CREATE UNIQUE INDEX tax_taxcode_idx ON tax (taxcode)")
      self.db.executesql("CREATE INDEX tax_inactive_idx ON tax (inactive)")

      self.db.executesql("CREATE UNIQUE INDEX product_partnumber_idx ON product (partnumber)")
      self.db.executesql("CREATE INDEX product_tax_id_idx ON product (tax_id)")
      self.db.executesql("CREATE INDEX product_inactive_idx ON product (inactive)")
      self.db.executesql("CREATE INDEX product_deleted_idx ON product (deleted)")
      self.db.executesql("CREATE INDEX product_protype_idx ON product (protype)")
      self.db.executesql("CREATE INDEX product_webitem_idx ON product (webitem)")
      
      self.db.executesql("CREATE UNIQUE INDEX tool_serial_idx ON tool (serial)")
      self.db.executesql("CREATE INDEX tool_groups_id_idx ON tool (toolgroup)")
      self.db.executesql("CREATE INDEX tool_inactive_idx ON tool (inactive)")
      self.db.executesql("CREATE INDEX tool_deleted_idx ON tool (deleted)")
      self.db.executesql("CREATE INDEX tool_product_id_idx ON tool (product_id)")
      
      self.db.executesql("CREATE INDEX price_curr_idx ON price (curr)")
      self.db.executesql("CREATE INDEX price_product_id_idx ON price (product_id)")
      self.db.executesql("CREATE INDEX price_validfrom_idx ON price (validfrom)")
      self.db.executesql("CREATE INDEX price_validto_idx ON price (validto)")
      self.db.executesql("CREATE INDEX price_vendor_idx ON price (vendorprice)")
      self.db.executesql("CREATE INDEX price_deleted_idx ON price (deleted)")

      self.db.executesql("CREATE UNIQUE INDEX barcode_code_idx ON barcode (code)")
      self.db.executesql("CREATE INDEX barcode_defcode_idx ON barcode (defcode)")
      self.db.executesql("CREATE INDEX barcode_parts_id_idx ON barcode (product_id)")

      self.db.executesql("CREATE UNIQUE INDEX trans_transnumber_idx ON trans (transnumber)")
      self.db.executesql("CREATE INDEX trans_curr_idx ON trans (curr)")
      self.db.executesql("CREATE INDEX trans_duedate_idx ON trans (duedate)")
      self.db.executesql("CREATE INDEX trans_paidtype_idx ON trans (paidtype)")
      self.db.executesql("CREATE INDEX trans_project_id_idx ON trans (project_id)")
      self.db.executesql("CREATE INDEX trans_employee_id_idx ON trans (employee_id)")
      self.db.executesql("CREATE INDEX trans_cruser_idx ON trans (cruser_id)")
      self.db.executesql("CREATE INDEX trans_customer_idx ON trans (customer_id)")
      self.db.executesql("CREATE INDEX trans_department_idx ON trans (department)")
      self.db.executesql("CREATE INDEX trans_transtate_idx ON trans (transtate)")
      self.db.executesql("CREATE INDEX trans_transdate_idx ON trans (transdate)")
      self.db.executesql("CREATE INDEX trans_crdate_idx ON trans (crdate)")
      self.db.executesql("CREATE INDEX trans_ref_transnumber_idx ON trans (ref_transnumber)")
      self.db.executesql("CREATE INDEX trans_transtype_idx ON trans (transtype)")
      self.db.executesql("CREATE INDEX trans_direction_idx ON trans (direction)")

      self.db.executesql("CREATE INDEX item_product_id_idx ON item (product_id)")
      self.db.executesql("CREATE INDEX item_tax_id_idx ON item (tax_id)")
      self.db.executesql("CREATE INDEX item_trans_id_idx ON item (trans_id)")
      self.db.executesql("CREATE INDEX item_deleted_idx ON item (deleted)")

      self.db.executesql("CREATE INDEX payment_paiddate_idx ON payment (paiddate)")
      self.db.executesql("CREATE INDEX payment_trans_id_idx ON payment (trans_id)")
      self.db.executesql("CREATE INDEX payment_deleted_idx ON payment (deleted)")

      self.db.executesql("CREATE INDEX movement_product_id_idx ON movement (product_id)")
      self.db.executesql("CREATE INDEX movement_tool_id_idx ON movement (tool_id)")
      self.db.executesql("CREATE INDEX movement_shipdate_idx ON movement (shippingdate)")
      self.db.executesql("CREATE INDEX movement_trans_id_idx ON movement (trans_id)")
      self.db.executesql("CREATE INDEX movement_place_id_idx ON movement (place_id)")
      self.db.executesql("CREATE INDEX movement_movetype_idx ON movement (movetype)")
      self.db.executesql("CREATE INDEX movement_deleted_idx ON movement (deleted)")

      self.db.executesql("CREATE INDEX patterns_transtype_idx ON pattern (transtype)")
      self.db.executesql("CREATE INDEX pattern_deleted_idx ON rate (deleted)")

      self.db.executesql("CREATE UNIQUE INDEX zipcatalog_pk_idx ON ui_zipcatalog (country, city, zipcode)")
      self.db.executesql("CREATE INDEX zipcatalog_country_city_idx ON ui_zipcatalog (country, city)")
      self.db.executesql("CREATE INDEX zipcatalog_country_zipcode_idx ON ui_zipcatalog (country, zipcode)")

      self.db.commit()  
      return True
    except Exception, err:
      self.db.rollback()
      self.error_message = err
      return False
  
  def insertNfbase(self):
    #nervaflex nervatura db init
    try:
      import os
      
      pg_sql = str(open(os.path.join(self.request.folder,'modules/nerva2py/nflex/insert_fbase_pg.sql'), 'r').read()).split(";")
      for sql in pg_sql:
        if str(sql).find("INSERT")>-1 or str(sql).find("UPDATE")>-1:
          self.db.executesql(sql)
      
      upd_sql=[]
      if self.engine=="postgres":
        pass
      elif self.engine=="sqlite":
        upd_sql = str(open(os.path.join(self.request.folder,'modules/nerva2py/nflex/insert_fbase_lite.sql'), 'r').read()).split(";")
      elif self.engine=="mysql":
        upd_sql = str(open(os.path.join(self.request.folder,'modules/nerva2py/nflex/insert_fbase_mssql.sql'), 'r').read()).split(";")
      elif self.engine=="mssql":
        upd_sql = str(open(os.path.join(self.request.folder,'modules/nerva2py/nflex/insert_fbase_mysql.sql'), 'r').read()).split(";")
      else:
        self.error_message = str(self.T('Unsupported nervaflex database engine: ')) +self.ename
        return False
      for sql in upd_sql:
        if str(sql).find("INSERT")>-1 or str(sql).find("UPDATE")>-1:
          self.db.executesql(sql)
      
      lfiles = os.listdir(os.path.join(self.request.folder,'modules/nerva2py/nflex/'))
      for lfile in lfiles:
        if lfile.startswith("locale_"):
          lc_sql = str(open(os.path.join(self.request.folder,'modules/nerva2py/nflex/'+lfile), 'r').read()).split(";")
          for sql in lc_sql:
            if str(sql).find("INSERT")>-1 or str(sql).find("UPDATE")>-1:
              self.db.executesql(sql)
  
      self.db.commit()  
      return True
    except Exception, err:
      self.db.rollback()
      self.error_message = err
      return False

  def insertDfReports(self):
    #default reports init
    try:
      import os
      rfiles = os.listdir(os.path.join(self.request.folder,'static/resources/report/dbs_ini/'))
      for rfile in rfiles:
        rp_sql = str(open(os.path.join(self.request.folder,'static/resources/report/dbs_ini/'+rfile), 'r').read()).split(";")
        for sql in rp_sql:
          if str(sql).lower().find("insert")>-1 or str(sql).lower().find("update")>-1:
            self.db.executesql(sql)
  
      self.db.commit()  
      return True
    except Exception, err:
      self.db.rollback()
      self.error_message = err
      return False
  
  def insertIniData(self):
    try:
      
      self.db.groups.insert(**dict({'groupname':'aggretype', 'groupvalue':'<>', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'aggretype', 'groupvalue':'avg', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'aggretype', 'groupvalue':'count', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'aggretype', 'groupvalue':'sum', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'address', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'audit', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'barcode', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'contact', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'currency', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'customer', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'deffield', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'employee', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'event', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'groups', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'item', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'link', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'log', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'menu', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'movement', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'numberdef', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'pattern', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'payment', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'place', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'price', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'product', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'project', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'rate', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'report', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'tax', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'tool', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'trans', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'nervatype', 'groupvalue':'setting', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'bool', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'checkbox', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'date', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'float', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'integer', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'string', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'valuelist', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'notes', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'filter', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'flink', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'password', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'customer', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'tool', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'trans', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'transitem', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'transmovement', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'transpayment', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'product', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'project', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'employee', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'fieldtype', 'groupvalue':'place', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'filetype', 'groupvalue':'doc', 'description':'MsWord document'}))
      self.db.groups.insert(**dict({'groupname':'filetype', 'groupvalue':'xls', 'description':'MsExcel workbook'}))
      self.db.groups.insert(**dict({'groupname':'filetype', 'groupvalue':'odt', 'description':'OpenOffice document'}))
      self.db.groups.insert(**dict({'groupname':'filetype', 'groupvalue':'mxml', 'description':'Flash report'}))
      self.db.groups.insert(**dict({'groupname':'filetype', 'groupvalue':'html', 'description':'HTML document'}))
      self.db.groups.insert(**dict({'groupname':'filetype', 'groupvalue':'gshi', 'description':'Genshi template'}))
      self.db.groups.insert(**dict({'groupname':'filetype', 'groupvalue':'fpdf', 'description':'FPDF template'}))
      
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'invoice', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'receipt', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'order', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'offer', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'worksheet', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'rent', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'delivery', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'store', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'inventory', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'waybill', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'production', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'formula', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'bank', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'cash', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtype', 'groupvalue':'filing', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'direction', 'groupvalue':'out', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'direction', 'groupvalue':'in', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'direction', 'groupvalue':'transfer', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'direction', 'groupvalue':'return', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'wheretype', 'groupvalue':'where', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'wheretype', 'groupvalue':'having', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'wheretype', 'groupvalue':'in', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'barcodetype', 'groupvalue':'code128a', 'description':'Code128A'}))
      self.db.groups.insert(**dict({'groupname':'barcodetype', 'groupvalue':'code128b', 'description':'Code128B'}))
      self.db.groups.insert(**dict({'groupname':'barcodetype', 'groupvalue':'code128c', 'description':'Code128C'}))
      self.db.groups.insert(**dict({'groupname':'barcodetype', 'groupvalue':'code39', 'description':'USD-3 (Code39)'}))
      self.db.groups.insert(**dict({'groupname':'barcodetype', 'groupvalue':'code93', 'description':'USS-93 (Code93)'}))
      self.db.groups.insert(**dict({'groupname':'barcodetype', 'groupvalue':'code25', 'description':'2of5 (Industrial)'}))
      self.db.groups.insert(**dict({'groupname':'barcodetype', 'groupvalue':'code25i', 'description':'Interleaved 2of5'}))
      self.db.groups.insert(**dict({'groupname':'barcodetype', 'groupvalue':'postnet', 'description':'Postnet'}))
      self.db.groups.insert(**dict({'groupname':'barcodetype', 'groupvalue':'upca', 'description':'UPC-A'}))
      self.db.groups.insert(**dict({'groupname':'barcodetype', 'groupvalue':'upce', 'description':'UPC-E'}))
      self.db.groups.insert(**dict({'groupname':'barcodetype', 'groupvalue':'ean13', 'description':'EAN-13'}))
      self.db.groups.insert(**dict({'groupname':'barcodetype', 'groupvalue':'ean8', 'description':'EAN-8'}))
      
      self.db.groups.insert(**dict({'groupname':'ratetype', 'groupvalue':'rate', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'ratetype', 'groupvalue':'buy', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'ratetype', 'groupvalue':'sell', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'ratetype', 'groupvalue':'average', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'filtertype', 'groupvalue':'==', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'filtertype', 'groupvalue':'=N', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'filtertype', 'groupvalue':'!=', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'filtertype', 'groupvalue':'>=', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'filtertype', 'groupvalue':'<=', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'movetype', 'groupvalue':'inventory', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'movetype', 'groupvalue':'store', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'movetype', 'groupvalue':'tool', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'movetype', 'groupvalue':'plan', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'movetype', 'groupvalue':'head', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'transtate', 'groupvalue':'ok', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtate', 'groupvalue':'new', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transtate', 'groupvalue':'back', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'logstate', 'groupvalue':'update', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'logstate', 'groupvalue':'closed', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'logstate', 'groupvalue':'deleted', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'logstate', 'groupvalue':'print', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'logstate', 'groupvalue':'login', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'logstate', 'groupvalue':'logout', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'usergroup', 'groupvalue':'admin', 'description':'Admin'}))
      self.db.groups.insert(**dict({'groupname':'usergroup', 'groupvalue':'user', 'description':'Employee'}))
      self.db.groups.insert(**dict({'groupname':'usergroup', 'groupvalue':'guest', 'description':'Guest'}))
      self.db.groups.insert(**dict({'groupname':'usergroup', 'groupvalue':'demo', 'description':'Demo'}))
      
      self.db.groups.insert(**dict({'groupname':'inputfilter', 'groupvalue':'disabled', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'inputfilter', 'groupvalue':'readonly', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'inputfilter', 'groupvalue':'update', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'inputfilter', 'groupvalue':'all', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'transfilter', 'groupvalue':'own', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transfilter', 'groupvalue':'usergroup', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'transfilter', 'groupvalue':'all', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'protype', 'groupvalue':'item', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'protype', 'groupvalue':'service', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'custtype', 'groupvalue':'own', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'custtype', 'groupvalue':'company', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'custtype', 'groupvalue':'private', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'custtype', 'groupvalue':'other', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'calcmode', 'groupvalue':'ded', 'description':'deduction (%)'}))
      self.db.groups.insert(**dict({'groupname':'calcmode', 'groupvalue':'add', 'description':'adding (%)'}))
      self.db.groups.insert(**dict({'groupname':'calcmode', 'groupvalue':'amo', 'description':'amount (+/-)'}))
      
      self.db.groups.insert(**dict({'groupname':'paidtype', 'groupvalue':'cash', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'paidtype', 'groupvalue':'transfer', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'paidtype', 'groupvalue':'credit_card', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'storetype', 'groupvalue':'sps', 'description':'Singlepart - Single FIFO'}))
      self.db.groups.insert(**dict({'groupname':'storetype', 'groupvalue':'spm', 'description':'Singlepart - Multi FIFO'}))
      self.db.groups.insert(**dict({'groupname':'storetype', 'groupvalue':'mps', 'description':'Multipart - Single FIFO'}))
      self.db.groups.insert(**dict({'groupname':'storetype', 'groupvalue':'mpm', 'description':'Multipart - Multi FIFO'}))
      
      self.db.groups.insert(**dict({'groupname':'placetype', 'groupvalue':'bank', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'placetype', 'groupvalue':'cash', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'placetype', 'groupvalue':'warehouse', 'description':None}))
      self.db.groups.insert(**dict({'groupname':'placetype', 'groupvalue':'store', 'description':None}))
      
      self.db.groups.insert(**dict({'groupname':'printertype', 'groupvalue':'local', 'description':'Local port'}))
      self.db.groups.insert(**dict({'groupname':'printertype', 'groupvalue':'network', 'description':'Local network'}))
      self.db.groups.insert(**dict({'groupname':'printertype', 'groupvalue':'mail', 'description':'HP ePrint via Email'}))
      self.db.groups.insert(**dict({'groupname':'printertype', 'groupvalue':'google_cloud', 'description':'Google Cloud Print'}))
      
      self.db.groups.insert(**dict({'groupname':'orientation', 'groupvalue':'P', 'description':'Portrait'}))
      self.db.groups.insert(**dict({'groupname':'orientation', 'groupvalue':'L', 'description':'Landscape'}))
      
      self.db.groups.insert(**dict({'groupname':'papersize', 'groupvalue':'a3', 'description':'A3'}))
      self.db.groups.insert(**dict({'groupname':'papersize', 'groupvalue':'a4', 'description':'A4'}))
      self.db.groups.insert(**dict({'groupname':'papersize', 'groupvalue':'a5', 'description':'A5'}))
      self.db.groups.insert(**dict({'groupname':'papersize', 'groupvalue':'letter', 'description':'Letter'}))
      self.db.groups.insert(**dict({'groupname':'papersize', 'groupvalue':'legal', 'description':'Legal'}))
      
      self.db.currency.insert(**dict({'curr':'EUR', 'description':'euro', 'digit':2, 'defrate':0, 'cround':0}))
      
      usergroup_id = self.db((self.db.groups.groupname=="usergroup")&(self.db.groups.groupvalue=="admin")).select().as_list()[0]["id"]
      employee_id = self.db.employee.insert(**dict({'empnumber':'admin', 'username':'admin', 'usergroup':usergroup_id}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="employee")).select().as_list()[0]["id"]
      self.db.address.insert(**dict({'nervatype':nervatype_id, 'ref_id':employee_id}))
      self.db.contact.insert(**dict({'nervatype':nervatype_id, 'ref_id':employee_id, "surname":"admin"}))
      usergroup_id = self.db((self.db.groups.groupname=="usergroup")&(self.db.groups.groupvalue=="user")).select().as_list()[0]["id"]
      employee_id = self.db.employee.insert(**dict({'empnumber':'user', 'username':'user', 'usergroup':usergroup_id}))
      self.db.address.insert(**dict({'nervatype':nervatype_id, 'ref_id':employee_id}))
      self.db.contact.insert(**dict({'nervatype':nervatype_id, 'ref_id':employee_id, "surname":"user"}))
      usergroup_id = self.db((self.db.groups.groupname=="usergroup")&(self.db.groups.groupvalue=="guest")).select().as_list()[0]["id"]
      employee_id = self.db.employee.insert(**dict({'empnumber':'guest', 'username':'guest', 'usergroup':usergroup_id}))
      self.db.address.insert(**dict({'nervatype':nervatype_id, 'ref_id':employee_id}))
      self.db.contact.insert(**dict({'nervatype':nervatype_id, 'ref_id':employee_id, "surname":"guest"}))
      usergroup_id = self.db((self.db.groups.groupname=="usergroup")&(self.db.groups.groupvalue=="demo")).select().as_list()[0]["id"]
      employee_id = self.db.employee.insert(**dict({'empnumber':'demo', 'username':'demo', 'usergroup':usergroup_id}))
      self.db.address.insert(**dict({'nervatype':nervatype_id, 'ref_id':employee_id}))
      self.db.contact.insert(**dict({'nervatype':nervatype_id, 'ref_id':employee_id, "surname":"demo"}))
      
      custtype_id = self.db((self.db.groups.groupname=="custtype")&(self.db.groups.groupvalue=="own")).select().as_list()[0]["id"]
      self.db.customer.insert(**dict({'custtype':custtype_id, 'custnumber':'HOME', 'custname':'COMPANY NAME', 'taxnumber':'12345678-1-12'}))
      
      placetype_id = self.db((self.db.groups.groupname=="placetype")&(self.db.groups.groupvalue=="bank")).select().as_list()[0]["id"]
      self.db.place.insert(**dict({'planumber':'bank', 'placetype':placetype_id, 'description':'Bank', 'curr':'EUR'}))
      placetype_id = self.db((self.db.groups.groupname=="placetype")&(self.db.groups.groupvalue=="cash")).select().as_list()[0]["id"]
      self.db.place.insert(**dict({'planumber':'cash', 'placetype':placetype_id, 'description':'Cash', 'curr':'EUR'}))
      placetype_id = self.db((self.db.groups.groupname=="placetype")&(self.db.groups.groupvalue=="warehouse")).select().as_list()[0]["id"]
      self.db.place.insert(**dict({'planumber':'warehouse', 'placetype':placetype_id, 'description':'Warehouse'}))
      
      self.db.numberdef.insert(**dict({'numberkey': 'bank_transfer', 'prefix':  'BANK', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'statement', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'calnumber', 'prefix':  'EVT', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'event', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'cash', 'prefix':  'CASH', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'cash payment', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'custnumber', 'prefix':  'CUS', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'customer', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'delivery_in', 'prefix':  'DELIN', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'delivery in', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'delivery_out', 'prefix':  'DELOU', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'delivery out', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'delivery_transfer', 'prefix':  'DELTF', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'delivery transfer', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'empnumber', 'prefix':  'EMP', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'employee', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'filing_in', 'prefix':  'FILIN', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'filing in', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'filing_out', 'prefix':  'FILOU', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'filing out', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'formula_transfer', 'prefix':  'FRM', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'formula', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'inventory_transfer', 'prefix':  'VENDL', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'inventory delivery', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'invoice_in', 'prefix':  'INVVD', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'vendor invoice', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'invoice_out', 'prefix':  'INVCT', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'customer invoice', 'visible': 1, 'readonly': 1, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'offer_in', 'prefix':  'OFFVD', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'vendor offer', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'offer_out', 'prefix':  'OFFCT', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'customer offer', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'order_in', 'prefix':  'ORDVD', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'vendor order', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'order_out', 'prefix':  'ORDCT', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'customer order', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'order_return', 'prefix':  'ORDRE', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'goods return', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'partnumber', 'prefix':  'PRO', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'poduct', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'production_transfer', 'prefix':  'MAKE', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'production', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'pronumber', 'prefix':  'PRJ', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'project', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'receipt_in', 'prefix':  'RECVD', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'vendor receipt', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'receipt_out', 'prefix':  'RECCT', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'customer receipt', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'rent_in', 'prefix':  'RENVD', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'vendor rent', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'rent_out', 'prefix':  'RENCT', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'customer rent', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'serial', 'prefix':  'SER', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'tool', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'store_in', 'prefix':  'STOIN', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'store in', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'store_out', 'prefix':  'STOOU', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'store out', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'store_transfer', 'prefix':  'STOTF', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'store transfer', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'waybill', 'prefix':  'MOVE', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'tool movement', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      self.db.numberdef.insert(**dict({'numberkey': 'worksheet_out', 'prefix':  'WORK', 'curvalue': 0, 'isyear': 1, 'sep':  '/', 'len': 5, 'description':  'worksheet', 'visible': 1, 'readonly': 0, 'orderby': 0}))
      
      self.db.tax.insert(**dict({'description':'tax-free (by product)', 'rate':0, 'taxcode':'TAM'}))
      self.db.tax.insert(**dict({'description':'tax-free (by customer)', 'rate':0, 'taxcode':'AAM'}))
      self.db.tax.insert(**dict({'description':'VAT 0%', 'rate':0, 'taxcode':'0%'}))
      self.db.tax.insert(**dict({'description':'VAT 5%', 'rate':0.05, 'taxcode':'5%'}))
      self.db.tax.insert(**dict({'description':'VAT 10%', 'rate':0.1, 'taxcode':'10%'}))
      self.db.tax.insert(**dict({'description':'VAT 15%', 'rate':0.15, 'taxcode':'15%'}))
      self.db.tax.insert(**dict({'description':'VAT 20%', 'rate':0.2, 'taxcode':'20%'}))
      self.db.tax.insert(**dict({'description':'VAT 25%', 'rate':0.25, 'taxcode':'25%'}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="valuelist")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_transcast', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'transaction special state', 'valuelist':'normal|cancellation|amendment', 
                                      'addnew':1, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_custinvoice_compname', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'customer invoice company name', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_custinvoice_compaddress', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'customer invoice company address', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_custinvoice_comptax', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'customer invoice company taxnumber', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_custinvoice_custname', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'customer invoice customer name', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_custinvoice_custaddress', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'customer invoice customer address', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="invoice")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_custinvoice_custtax', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'customer invoice customer taxnumber', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))

      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_closed_policy_invoice_out', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'transaction closed policy', 'valuelist':'print', 'addnew':0, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_closed_policy_receipt_out', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'transaction closed policy', 'valuelist':'print', 'addnew':0, 'visible':0, 'readonly':1}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="rent")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_reholiday', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'rent holidays', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="rent")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_rebadtool', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'rent bad machine', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="rent")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_reother', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'rent other non-eligible', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="rent")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_rentnote', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'rent justification', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="worksheet")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_wsdistance', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'worksheet distance', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="worksheet")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_wsrepair', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'worksheet repair time (hour)', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="worksheet")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_wstotal', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'worksheet total time (hour)', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue=="worksheet")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_wsnote', 'nervatype':nervatype_id, 'subtype':transtype_id, 'fieldtype':fieldtype_id, 
                                      'description':'worksheet justification', 'valuelist':None, 'addnew':1, 'visible':0, 'readonly':1}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="trans")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="transitem")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'trans_transitem_link', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Ref.No.', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'printer_login', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Printer login', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="password")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'printer_password', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Printer password', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'printer_server', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Printer server', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="integer")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'printer_port', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Printer port', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'printer_gsprint', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'gsprint path (windows pdf printing)', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'printer_gsprint', 'ref_id':None, 'value':'C:\Progra~1\Ghostgum\gsview\gsprint', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'printer_clienthost', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Client Additions host', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'printer_clienthost', 'ref_id':None, 'value':'localhost:8080', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'printer_mail_smtp', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Printer mail smtp', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'printer_mail_sender', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Printer mail sender', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'printer_mail_login', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Printer mail login (username:password)', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'printer_mail_address', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Printer mail address', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'printer_mail_subject', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Printer mail subject', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'printer_mail_message', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Printer mail message', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'default_bank', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'default bank place no.', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'default_bank', 'ref_id':None, 'value':'bank', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'default_chest', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'default checkout place no.', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'default_chest', 'ref_id':None, 'value':'cash', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'default_warehouse', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'default warehouse place no.', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'default_warehouse', 'ref_id':None, 'value':'warehouse', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'default_country', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'default country', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'default_country', 'ref_id':None, 'value':'EU', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'default_lang', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'default language', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'default_lang', 'ref_id':None, 'value':'en', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'default_currency', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'default currency', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'default_currency', 'ref_id':None, 'value':'EUR', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="integer")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'default_deadline', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'default deadline (payment)', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'default_deadline', 'ref_id':None, 'value':'8', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'default_paidtype', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'default paidtype', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'default_paidtype', 'ref_id':None, 'value':'transfer', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'default_unit', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'default unit', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'default_unit', 'ref_id':None, 'value':'piece', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'default_taxcode', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'default taxcode', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'default_taxcode', 'ref_id':None, 'value':'20%', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'false_bool', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'false string', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'false_bool', 'ref_id':None, 'value':'FALSE', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="integer")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'invoice_copy', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'invoice copy', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'invoice_copy', 'ref_id':None, 'value':'2', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="integer")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'transyear', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'business year', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'transyear', 'ref_id':None, 'value':'2012', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'true_bool', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'true string', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'true_bool', 'ref_id':None, 'value':'TRUE', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'audit_control', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'set audit control', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'audit_control', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'invoice_from_inventory', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'invoice from inventory(yes) or order items(no)', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'invoice_from_inventory', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'set_outstock_enabled', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled inventory deficit', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'set_outstock_enabled', 'ref_id':None, 'value':'true', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'set_stocklimit_warning', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'inventory stock limit warning', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'set_stocklimit_warning', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'set_trans_deleted', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled trans deletion', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'set_trans_deleted', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'show_partcustomer', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'show customer number column', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'show_partcustomer', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'show_partnumber', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'show product number column', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'show_partnumber', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_address_update', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled address update log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_address_update', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_address_deleted', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled address deleted log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_address_deleted', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_contact_update', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled contact  update log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_contact_update', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_contact_deleted', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled contact deleted log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_contact_deleted', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_customer_update', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled customer  update log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_customer_update', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_customer_deleted', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled customer deleted log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_customer_deleted', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_product_update', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled product  update log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_product_update', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_product_deleted', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled product deleted log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_product_deleted', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_price_update', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled price  update log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_price_update', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_price_deleted', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled price deleted log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_price_deleted', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_event_update', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled event  update log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_event_update', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_event_deleted', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled event deleted log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_event_deleted', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_trans_update', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled trans  update log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_trans_update', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_trans_deleted', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled trans deleted log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_trans_deleted', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_project_update', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled project  update log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_project_update', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_project_deleted', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled project deleted log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_project_deleted', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_employee_update', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled employee  update log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_employee_update', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_employee_deleted', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled employee deleted log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_employee_deleted', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_tool_update', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled tool  update log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_tool_update', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_tool_deleted', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled tool deleted log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_tool_deleted', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_formula_update', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled formula  update log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_formula_update', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_formula_deleted', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled formula deleted log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_formula_deleted', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_trans_closed', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled trans closed log', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_trans_closed', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'log_userlogin', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'enabled userlogin', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'log_userlogin', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="link")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'link_qty', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'link qty value', 'valuelist':None, 'addnew':0, 'visible':0, 'readonly':0}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="link")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'link_rate', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'link rate value', 'valuelist':None, 'addnew':0, 'visible':0, 'readonly':0}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'prenew_all', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'set new row control', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'prenew_all', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="bool")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'presave_all', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'set update row control', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      self.db.fieldvalue.insert(**dict({'fieldname':'presave_all', 'ref_id':None, 'value':'false', 'notes':None}))
      
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="product")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'product_custpartnumber', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Customer Product No. (pricing)', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="product")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="product")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'product_alternative', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Alternative Product', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="product")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="product")).select().as_list()[0]["id"]
      self.db.deffield.insert(**dict({'fieldname':'product_element', 'nervatype':nervatype_id, 'subtype':None, 'fieldtype':fieldtype_id, 
                                      'description':'Element Product', 'valuelist':None, 'addnew':0, 'visible':1, 'readonly':0}))
      
      menu_id = self.db.ui_menu.insert(**dict({'menukey':'mnu_exp_1', 'description':'Server function example', 'funcname':'callMenuCmd', 'url':0}))
      #menu_id = self.db((self.db.ui_menu.menukey=="mnu_exp_1")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="float")).select().as_list()[0]["id"]
      self.db.ui_menufields.insert(**dict({'menu_id':menu_id, 'fieldname':'number_1', 'description':'first number', 'fieldtype':fieldtype_id, 'orderby':0}))
      self.db.ui_menufields.insert(**dict({'menu_id':menu_id, 'fieldname':'number_2', 'description':'second number', 'fieldtype':fieldtype_id, 'orderby':1}))
      self.db.ui_menu.insert(**dict({'menukey':'mnu_exp_2', 'description':'Server URL example', 'funcname':'nerva2py/ndi/getVernum', 'url':1}))
      menu_id = self.db.ui_menu.insert(**dict({'menukey':'mnu_exp_3', 'description':'Internet URL example', 'funcname':'search', 'url':1, 'address':'https://www.google.com'}))
      #menu_id = self.db((self.db.ui_menu.menukey=="mnu_exp_3")).select().as_list()[0]["id"]
      fieldtype_id = self.db((self.db.groups.groupname=="fieldtype")&(self.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
      self.db.ui_menufields.insert(**dict({'menu_id':menu_id, 'fieldname':'q', 'description':'google search', 'fieldtype':fieldtype_id, 'orderby':0}))
      
      self.db.commit()  
      return True
    except Exception, err:
      self.db.rollback()
      self.error_message = err
      return False
    
  def setLogin(self, username, password):
    try:
      if username==None:
        self.error_message = str(self.T("Missing user!"))
        return False
      employee = self.db((self.db.employee.inactive==0)&(self.db.employee.deleted==0)&(self.db.employee.username==username)).select()
      if len(employee.as_list())==0:   
        self.error_message = str(self.T("Unknown user!"))
        return False
      if password=="":
        password = None
      if password!=None and (hasattr(self, 'encrypt_data')==False or self.md5_password==False):
        psw = self.get_md5_value(password)
      else:
        psw = password
      if psw!=employee[0].password:   
        self.error_message = str(self.T("Wrong password!"))
        return False
      self.employee = employee[0]
      return True
    except Exception, err:
      self.error_message = err
      return False
  
  def getObjectAudit(self, nervatype, transtype=None):
    #Nervatura objects access rights: disabled,readonly,update,all
    #see: audit
    try:
      if self.admin_user:
        return "all"
      if self.employee==None:
        self.error_message = str(self.T("Login required!"))
        return "error"
      if self.employee.usergroup==None:
        self.error_message = str(self.T("Missing usergroup!"))
        return "error"
      if nervatype=="sql" or nervatype=="fieldvalue":
        return "all"
      if nervatype==None:
        self.error_message = str(self.T("Missing nervatype!"))
        return "error"
      else:
        nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue==nervatype)).select().as_list()
        if len(nervatype_id)==0:   
          self.error_message = str(self.T("Unknown nervatype!"))
          return "error"
        else:
          nervatype_id = nervatype_id[0]["id"]
      if transtype!=None:
        transtype_id = self.db((self.db.groups.groupname=="transtype")&(self.db.groups.groupvalue==transtype)).select().as_list()
        if len(transtype_id)==0:   
          self.error_message = str(self.T("Unknown transtype!"))
          return "error"
        else:
          transtype_id = transtype_id[0]["id"]
        audit = self.db((self.db.ui_audit.usergroup==self.employee.usergroup)
                        &(self.db.ui_audit.nervatype==nervatype_id)
                        &(self.db.ui_audit.subtype==transtype_id)).select().as_list()
      else:
        audit = self.db((self.db.ui_audit.usergroup==self.employee.usergroup)&(self.db.ui_audit.nervatype==nervatype_id)).select().as_list()
      if len(audit)==0:
        return "all"
      else:
        inputfilter = self.db(self.db.groups.id==audit[0]["inputfilter"]).select().as_list()
        if len(inputfilter)>0:   
          return inputfilter[0]["groupvalue"]
        else:
          return "all"
    except Exception, err:
      self.error_message = err
      return "error"
    
  def getDataAudit(self):
    #Nervatura data access rights: own,usergroup,all
    #see: employee.usergroup+link+transfilter
    try:
      if self.admin_user:
        return "all"
      if self.employee==None:
        self.error_message = str(self.T("Login required!"))
        return "error"
      if self.employee.usergroup==None:
        self.error_message = str(self.T("Missing usergroup!"))
        return "error"
      nervatype_id = self.db((self.db.groups.groupname=="nervatype")&(self.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
      transfilter_id = self.db((self.db.link.deleted==0)&(self.db.link.nervatype_1==nervatype_id)
                            &(self.db.link.nervatype_2==nervatype_id)&(self.db.link.ref_id_1==self.employee.usergroup)).select().as_list()
      if len(transfilter_id)>0:   
        transfilter = self.db(self.db.groups.id==transfilter_id[0]["ref_id_2"]).select().as_list()
        if len(transfilter)>0:
          return transfilter[0]["groupvalue"]
        else:
          return "all"
      else:
        return "all"
    except Exception, err:
      self.error_message = err
      return "error"