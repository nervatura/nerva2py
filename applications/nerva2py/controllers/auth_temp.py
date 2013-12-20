# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
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
  from gluon.html import URL #@UnresolvedImport
  
from nerva2py.nervastore import NervaStore
from gluon.html import TABLE, TR, TD
from gluon.sqlhtml import SPAN, A

#postgres://username:password@localhost/database
#mysql://username:password@localhost/database
#sqlite://database.db

conStr="postgres://demo:@localhost/demo"
ns = NervaStore(request, T, None)
ns.setConnect(uri=conStr, pool_size=0)
if ns.db!=None:
  if ns.defineTable(create=False)==False:
    pass #"Error table define"
else:
  pass #ns.T("Could not connect to the database: ")+database

response.generic_patterns = ['*'] if request.is_local else []

def login_validation(form):
  if form.vars.password=="":
    form.vars.password=None
  else:
    form.vars.password = ns.get_md5_value(form.vars.password)

def change_pw_validation(form):
  if form.vars.old_password=="":
    form.vars.old_password=None
  else:
    form.vars.old_password = ns.get_md5_value(form.vars.old_password)
  if form.vars.new_password=="":
    form.vars.new_password=None
  else:
    form.vars.new_password = ns.get_md5_value(form.vars.new_password)

def log_event(description, vars=None, origin='auth'):
  pass

def update_groups():
  pass

from gluon.tools import Auth
auth = Auth(ns.db, hmac_key=Auth.get_or_create_key(), controller='auth_temp')

auth.settings.table_user_name = 'employee'
auth.settings.create_user_groups = False
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = False
auth.settings.login_onvalidation = login_validation
auth.settings.change_password_onvalidation = change_pw_validation
auth.log_event=log_event
auth.update_groups=update_groups

auth.define_tables(username=True, migrate=False, fake_migrate=False)


def index():
  
  company_name = ns.db.customer(id=1).custname
  customer_count_1 = len(ns.db((ns.db.customer.deleted==0)&(ns.db.customer.id!=1)).select().as_list())
  customer_count_2 = ns.db.executesql("select count(*) as rc from customer where deleted=0 and id<>1",as_dict = True)[0]["rc"]
  table = TABLE(TR(TD("Database company name: "+company_name)),
        TR(TD("Customer count: "+str(customer_count_1))),
        TR(TD("Secret page: ",A(SPAN("Login"), _href=URL("secret_page"), _title=T("Login...")))))
  return table

@auth.requires_login()
def secret_page():
  table = TABLE(TR(TD("Back to home: ",A(SPAN("HOME"), _href=URL("index"), _title=T("HOME")))),
                TR(TD("Change password: ",A(SPAN("Change password"), _href=URL("user/change_password"), _title=T("Change password...")))),
                TR(TD("Logout: ",A(SPAN("Exit"), _href=URL("user/logout"), _title=T("Logout...")))))
  return table

def user():
  table = TABLE(TR(TD("Back to home: ",A(SPAN("HOME"), _href=URL("index"), _title=T("HOME")))),
                TR(TD(auth())))
  return table
