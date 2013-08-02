# -*- coding: utf-8 -*-

from gluon.http import redirect

def index():
  redirect(URL(a='admin', c='default', f='index'))
