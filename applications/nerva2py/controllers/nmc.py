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
  import gluon.languages.translator as T

from gluon.html import HTML,TABLE, TR, TD, CENTER, SPAN, BR, DIV, BODY, HEAD, TITLE, LINK
from gluon.html import URL

def index():
  return HTML(HEAD(TITLE("Nervatura Mobil Client"),
                   LINK(_rel="shortcut icon", _href=URL('static','favicon.ico'), _type="image/x-icon")),
              BODY(DIV(CENTER(TABLE(TR(TD(SPAN(T("The Nervatura Web Client surfaces are primarily optimized for office and desktop like (PC, laptop) usage.")),BR(),
                            SPAN(T("The touch-optimized, HTML5-based user interface for smartphones and tablets is coming soon!")),
                            _style="text-align: center;vertical-align: middle;font-weight: bold;font-family: sans-serif;font-size: 20px;")),
                      _style="width:700px;background-color:#FFFFFF;color:#444444;margin-top:100px;")),_style="width:100%;height:100%")),_style="background-color:#879FB7;")