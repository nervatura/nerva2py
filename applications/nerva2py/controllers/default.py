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

from gluon.html import URL
import os

response.title='Nervatura Framework'
response.menu = [
    (T('HOME'), False, URL('default','index'), []),
    (T('DOCUMENTATION & RESOURCES'), False, URL('default','ndoc'), []),
    (T('ABOUT'), False, URL('default','about'), []),
    (T('NAS ADMIN'), False, URL('nas','index'), [])
    ]

def index():
  response.subtitle=T('Welcome')
  if session._language:
    view='default/index_'+str(session._language)+'.html'
    folder = request.folder
    filename = os.path.join(folder, 'views', view)
    if os.path.exists(filename):
      response.view=view
  return dict()

def ndoc():
  response.subtitle=T('Docs & Resources')
  return dict()

def about():
  response.subtitle=T('About')
  return dict()

def licenses():
  response.subtitle=T('License Agreement')
  return dict()
