# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Project
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

import sys,os
from gluon.sql import DAL, Field
from gluon.validators import IS_IN_DB

response.google_analytics_id = None
  
if not request.env.web2py_runtime_gae:
  ename="sqlite"
  db = DAL('sqlite://storage.sqlite', migrate=False, fake_migrate=False) 
  session_db = DAL('sqlite://session.sqlite')
  session.connect(request, response, db = session_db)
  reload(sys)
  sys.setdefaultencoding("utf-8")#@UndefinedVariable
else:
  ename="google_datastore"
  db = DAL('google:datastore://storage', migrate=False, fake_migrate=False)
  session.connect(request, response, db = db)
  #from gluon.contrib.memdb import MEMDB
  #from google.appengine.api.memcache import Client
  #session.connect(request, response, db = MEMDB(Client()))

response.generic_patterns = ['*'] if request.is_local else []
try:
  version_info = open(os.path.join(request.folder, 'VERSION'), 'r')
  response.verNo = version_info.read().split()[-1].strip()
  version_info.close()
except:
  raise RuntimeError("Cannot determine nerva2py version")
try:
  analytics_id = open(os.path.join(request.folder, 'GAID'), 'r')
  response.google_analytics_id = analytics_id.read().split()[-1].strip()
  analytics_id.close()
except:
  pass

def createTable(table):
    query = db._adapter.create_table(table,migrate=False,fake_migrate=False)
    db._adapter.create_sequence_and_triggers(query,table)
    db.commit()
    
table = db.define_table('settings',
    Field('id', readable=False, writable=False),
    Field('fieldname', type='string', label=T('FieldName'), length=150, notnull=True, required=True, unique=True),
    Field('value', type='string', label=T('Value'), length=255),
    Field('description', type='text', label=T('Description')))
try:
  create_tbl = not db().select(db.settings.ALL, limitby=(0))
except:
  create_tbl= True
if create_tbl: 
    createTable(table)
    db.settings.insert(fieldname="login_enabled_lst", description="Enabled admin login ip pattern. Comma-separated list (recommended to set the firewall)", value="")
    db.settings.insert(fieldname="request_enabled_lst", description="Enabled request ip pattern. Comma-separated list (recommended to set the firewall)", value="")

    from gluon.tools import Auth
    auth = Auth(db)
    auth.define_tables(username=True, migrate=False, fake_migrate=False)
    createTable(db[auth.settings.table_user_name])
    createTable(db[auth.settings.table_group_name])
    createTable(db[auth.settings.table_membership_name])
    createTable(db[auth.settings.table_event_name])
    #temp. test users!
    db.auth_user.insert(username="admin", #password: 12345
                       password="pbkdf2(1000,20,sha512)$8783641ae67d774b$cb9a2abc38f4297cd0c6fb050b2996759bd3e514")
    db.auth_user.insert(username="demo", #password: demo
                       password="pbkdf2(1000,20,sha512)$8eb3261f2d9578bd$b1f27ed01f7d75d9a09f5972b9ad8c1eb8c577f9")
        
table = db.define_table('engine',
    Field('id', readable=False, writable=False),
    Field('ename', type='string', length=150, label=T('Name'), notnull=True, required=True, unique=True),
    Field('description', type='string', length=150, label=T('Description'), notnull=True, required=True),
    Field('connection', type='string', length=255, label=T('Connection'), notnull=True, required=True),
    Field('inactive', type='boolean', label=T('Inactive'), default=False, notnull=True))
engine_id = {}
if create_tbl: 
  createTable(table)
  engine_id["sqlite"] = db.engine.insert(ename="sqlite", description="SQLite", connection="sqlite://database.db")
  engine_id["mysql"] = db.engine.insert(ename="mysql", description="MySQL", connection="mysql://username:password@localhost/database")
  engine_id["postgres"] = db.engine.insert(ename="postgres", description="PostgreSQL", connection="postgres://username:password@localhost/database")
  engine_id["mssql"] = db.engine.insert(ename="mssql", description="MSSQL", connection="mssql2://username:password@localhost/database")
  engine_id["google_sql"] = db.engine.insert(ename="google_sql", description="Google SQL", connection="google:sql://project:instance/database")
#  engine_id["mongodb"] = db.engine.insert(ename="mongodb", description="MongoDB", connection="mongodb://username:password@localhost/database")
#untested:    
#  engine_id["firebird"] = db.engine.insert(ename="firebird", description="FireBird", connection="firebird://username:password@localhost/database")
#  engine_id["oracle"] = db.engine.insert(ename="oracle", description="Oracle", connection="oracle://username/password@database")
#  engine_id["db2"] = db.engine.insert(ename="db2", description="DB2", connection="db2://username:password@database")
#  engine_id["ingres"] = db.engine.insert(ename="ingres", description="Ingres", connection="ingres://username:password@localhost/database")
#  engine_id["informix"] = db.engine.insert(ename="informix", description="Informix", connection="informix://username:password@database")
#  engine_id["cubrid"] = db.engine.insert(ename="cubrid", description="Cubrid", connection="cubrid://username:password@localhost/database")
#  engine_id["sapdb"] = db.engine.insert(ename="sapdb", description="SAPDB", connection="sapdb://username:password@localhost/database")
#  engine_id["sybase"] = db.engine.insert(ename="sybase", description="Sybase", connection="sybase://username:password@localhost/database")
  db.commit()
 
table = db.define_table('databases',
    Field('id', readable=False, writable=False),
    Field('alias', type='string', length=150, label=T('Alias'), notnull=True, required=True, unique=True),
    Field('engine_id', db.engine, label=T('Engine'), notnull=True, required=True, requires = IS_IN_DB(db, db.engine.id, '%(description)s')),
    Field('host', type='string', length=150, label=T('Host')),
    Field('port', type='string', length=150, label=T('Port')),
    Field('dbname', type='string', length=150, label=T('Database'), notnull=True, required=True),
    Field('username', type='string', length=150, label=T('UserName')),
    Field('password', type='password', length=150, label=T('Password')),
    Field('ndi_enabled', type='boolean', label=T('NDI Enabled'), default=True, notnull=True),
    Field('ndi_md5_password', type='boolean', label=T('NDI Md5 Password'), default=False, notnull=True),
    Field('ndi_encrypt_data', type='boolean', label=T('NDI Encrypt Data'), default=False, notnull=True),
    Field('ndi_encrypt_password', type='password', label=T('NDI Encrypt Password')),
    Field('request_enabled_lst', type='text', label=T('Request Enabled List'))
  )
if create_tbl: 
  createTable(table)
  if ename=="sqlite":
    db.databases.insert(alias="demo", engine_id=engine_id[ename], dbname="demo")
   
table = db.define_table('nflex',
    Field('id', readable=False, writable=False),
    Field('sqlkey', type='string', length=150, notnull=True, required=True),
    Field('engine', type='string', length=150, notnull=True, required=True),
    Field('section', type='string', length=150),
    Field('sqlstr', type='text', notnull=True, required=True)
  )
if create_tbl: 
  createTable(table)
  from nerva2py.nflex.insert_fbase_dal import insert_nflex_rows  # @UnresolvedImport
  insert_nflex_rows(db)
  