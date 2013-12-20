# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
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

from gluon.html import FORM, SELECT, URL, OPTION
  
current_language = 'en'
languages=[('en','English'),
           ('hu','Magyar')]

session._language = request.vars._language or session._language or current_language
T.force(session._language)
if T.accepted_language != session._language:
    import re
    lang = re.compile('\w{2}').findall(session._language)[0]
    response.files.append(URL(r=request,c='static',f='js/jquery.translate.min.js'))
    response.files.append(URL(r=request,c='ndr',f='translate',args=lang+'.js'))

def translate():
    return FORM(SELECT(
            _id="translate",
            _onchange="document.location='%s?_language='+jQuery(this).val()" \
                % URL(r=request,args=request.args),
            value=session._language,
            *[OPTION(k,_value=v) for v,k in languages]))
