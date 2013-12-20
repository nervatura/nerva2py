# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

from gluon.html import XML, A, DIV, LI, SPAN, UL, INPUT
from gluon.html import TABLE, THEAD, TBODY, TR, TD, TH
from gluon.html import URL, CAT, FORM, truncate_string
from gluon import current, redirect, HTTP
from gluon.sqlhtml import ExporterTSV, ExporterCSV, ExporterXML, ExporterHTML, SQLFORM

def trap_class(_class=None,trap=True):
  return (trap and 'w2p_trap' or '')+(_class and ' '+_class or '')
  
class SimpleGrid():
  
  CLASS_VERSION='0.1'
  
  def __init__(self):
    pass
    
  @staticmethod
  def grid(query,
           fields=None,
           field_id=None,
           left=None,
           join=None, #!
           orderby=None,
           groupby=None,
           groupfields=None, #!
           having=None, #!
           headers={},
           searchable=False, #True,
           sortable=True,
           paginate=20,
           pagename="page", #!
           deletable=False, #! True,
           editable=True,
           details=False, #! True,
           selectable=None,
           create=False, #!True,
           csv=False, #!True,
           links=None,
           links_in_grid=True,
           upload = '<default>',
           args=[],
           user_signature = False, #!True,
           maxtextlengths={},
           maxtextlength=20,
           onvalidation=None,
           oncreate=None,
           onupdate=None,
           ondelete=None,
           sorter_icons=(XML('&#x2191;'),XML('&#x2193;')),
           ui = 'web2py',
           showbuttontext=True,
           _class="web2py_grid",
           formname='web2py_grid',
           search_widget='default',
           ignore_rw = False,
           formstyle = 'table3cols',
           exportclasses = None,
           formargs={},
           createargs={},
           editargs={},
           viewargs={},
          ):

      # jQuery UI ThemeRoller classes (empty if ui is disabled)
      if ui == 'jquery-ui':
          ui = dict(widget='ui-widget',
                    header='ui-widget-header',
                    content='ui-widget-content',
                    default='ui-state-default',
                    cornerall='ui-corner-all',
                    cornertop='ui-corner-top',
                    cornerbottom='ui-corner-bottom',
                    button='ui-button-text-icon-primary',
                    buttontext='ui-button-text',
                    buttonadd='ui-icon ui-icon-plusthick',
                    buttonback='ui-icon ui-icon-arrowreturnthick-1-w',
                    buttonexport='ui-icon ui-icon-transferthick-e-w',
                    buttondelete='ui-icon ui-icon-trash',
                    buttonedit='ui-icon ui-icon-pencil',
                    buttontable='ui-icon ui-icon-triangle-1-e',
                    buttonview='ui-icon ui-icon-zoomin',
                    )
      elif ui == 'web2py':
          ui = dict(widget='',
                    header='',
                    content='',
                    default='',
                    cornerall='',
                    cornertop='',
                    cornerbottom='',
                    button='button btn',
                    buttontext='buttontext button',
                    buttonadd='icon plus icon-plus',
                    buttonback='icon leftarrow icon-arrow-left',
                    buttonexport='icon downarrow icon-download',
                    buttondelete='icon trash icon-trash',
                    buttonedit='icon pen icon-pencil',
                    buttontable='icon rightarrow icon-arrow-right',
                    buttonview='icon magnifier icon-zoom-in',
                    )
      elif not isinstance(ui,dict):
          raise RuntimeError,'SQLFORM.grid ui argument must be a dictionary'
      
      db = query._db
      T = current.T
      request = current.request
      session = current.session
      response = current.response
      wenabled = (not user_signature or (session.auth and session.auth.user))
      create = wenabled and create
      editable = wenabled and editable
      deletable = wenabled and deletable

      def url(**b):
          b['args'] = args+b.get('args',[])
          b['hash_vars']=False
          b['user_signature'] = user_signature
          return URL(**b)

      def url2(**b):
          b['args'] = request.args+b.get('args',[])
          b['hash_vars']=False
          b['user_signature'] = user_signature
          return URL(**b)

      referrer = session.get('_web2py_grid_referrer_'+formname, url())
      # if not user_signature every action is accessible
      # else forbid access unless
      # - url is based url
      # - url has valid signature (vars are not signed, only path_info)
      # = url does not contain 'create','delete','edit' (readonly)
      if user_signature:
          if not(
              '/'.join(str(a) for a in args) == '/'.join(request.args) 
#              or
#              URL.verify(request,user_signature=user_signature,
#                         hash_vars=False) 
                  or not (
                  'create' in request.args or
                  'delete' in request.args or
                  'edit' in request.args)):
              session.flash = T('not authorized')                
              redirect(referrer)

      def gridbutton(buttonclass='buttonadd', buttontext='Add',
                     buttonurl=url(args=[]), callback=None,
                     delete=None, trap=True):
          if showbuttontext:
              if callback:
                  return A(SPAN(_class=ui.get(buttonclass)),
                           SPAN(T(buttontext),_title=buttontext,
                                _class=ui.get('buttontext')),
                           callback=callback,delete=delete,
                           _class=trap_class(ui.get('button'),trap))
              else:
                  return A(SPAN(_class=ui.get(buttonclass)),
                           SPAN(T(buttontext),_title=buttontext,
                                _class=ui.get('buttontext')),
                           _href=buttonurl,
                           _class=trap_class(ui.get('button'),trap))
          else:
              if callback:
                  return A(SPAN(_class=ui.get(buttonclass)),
                           callback=callback,delete=delete,
                           _title=buttontext,
                           _class=trap_class(ui.get('buttontext'),trap))
              else:
                  return A(SPAN(_class=ui.get(buttonclass)),
                           _href=buttonurl,_title=buttontext,
                           _class=trap_class(ui.get('buttontext'),trap))
      dbset = db(query)
      tablenames = db._adapter.tables(dbset.query)
      #if left!=None: tablenames+=db._adapter.tables(left)
      
      if left!=None:
        if isinstance(left,list):
          for _left in left:
            tablenames=tablenames+db._adapter.tables(_left)
        else:
          tablenames=tablenames+db._adapter.tables(left)
      if join!=None:
        if isinstance(join,list):
          for _join in join:
            tablenames=tablenames+db._adapter.tables(_join)
        else:
          tablenames=tablenames+db._adapter.tables(join)
      
      tables = [db[tablename] for tablename in tablenames]
      if not fields:
          fields = reduce(lambda a,b:a+b,
                          [[field for field in table] for table in tables])
      if not field_id:
          field_id = tables[0]._id
      columns = [str(field) for field in fields \
                     if field._tablename in tablenames]

      if not str(field_id) in [str(f) for f in fields]:
          fields.append(field_id)
      table = field_id.table
      tablename = table._tablename
      if upload=='<default>':
          upload = lambda filename: url(args=['download',filename])
          if len(request.args)>1 and request.args[-2]=='download':
              stream = response.download(request,db)
              raise HTTP(200,stream,**response.headers)

      def buttons(edit=False,view=False,record=None):
          buttons = DIV(gridbutton('buttonback', 'Back', referrer),
                        _class='form_header row_buttons %(header)s %(cornertop)s' % ui)
          if edit and (not callable(edit) or edit(record)):
              args = ['edit',table._tablename,request.args[-1]]
              buttons.append(gridbutton('buttonedit', 'Edit',
                                        url(args=args)))
          if view:
              args = ['view',table._tablename,request.args[-1]]
              buttons.append(gridbutton('buttonview', 'View',
                                        url(args=args)))
          if record and links:
              for link in links:
                  if isinstance(link,dict):
                      buttons.append(link['body'](record))
                  elif link(record):
                      buttons.append(link(record))
          return buttons

      formfooter = DIV(
          _class='form_footer row_buttons %(header)s %(cornerbottom)s' % ui)

      create_form = update_form = view_form = search_form = None
      sqlformargs = dict(formargs)

      if create and len(request.args)>1 and request.args[-2] == 'new':
          table = db[request.args[-1]]
          sqlformargs.update(createargs)
          create_form = SQLFORM(
              table, ignore_rw=ignore_rw, formstyle=formstyle,
              _class='web2py_form',
              **sqlformargs)
          create_form.process(formname=formname,
                  next=referrer,
                  onvalidation=onvalidation,
                  onsuccess=oncreate)
          res = DIV(buttons(), create_form, formfooter, _class=_class)
          res.create_form = create_form
          res.update_form = update_form
          res.view_form = view_form
          res.search_form = search_form
          return res

      elif details and len(request.args)>2 and request.args[-3]=='view':
          table = db[request.args[-2]]
          record = table(request.args[-1]) or redirect(URL('error'))
          sqlformargs.update(viewargs)
          view_form = SQLFORM(table, record, upload=upload, ignore_rw=ignore_rw,
                         formstyle=formstyle, readonly=True, _class='web2py_form',
                         **sqlformargs)
          res = DIV(buttons(edit=editable, record=record), view_form,
                    formfooter, _class=_class)
          res.create_form = create_form
          res.update_form = update_form
          res.view_form = view_form
          res.search_form = search_form
          return res
#      elif editable and len(request.args)>2 and request.args[-3]=='edit':
#          table = db[request.args[-2]]
#          record = table(request.args[-1]) or redirect(URL('error'))
#          sqlformargs.update(editargs)
#          update_form = SQLFORM(table, record, upload=upload, ignore_rw=ignore_rw,
#                              formstyle=formstyle, deletable=deletable,
#                              _class='web2py_form',
#                              submit_button=T('Submit'),
#                              delete_label=T('Check to delete'),
#                              **sqlformargs)
#          update_form.process(formname=formname,
#                            onvalidation=onvalidation,
#                            onsuccess=onupdate,
#                            next=referrer)
#          res = DIV(buttons(view=details, record=record),
#                    update_form, formfooter, _class=_class)
#          res.create_form = create_form
#          res.update_form = update_form
#          res.view_form = view_form
#          res.search_form = search_form
#          return res
      elif deletable and len(request.args)>2 and request.args[-3]=='delete':
          table = db[request.args[-2]]
          if ondelete:
              ondelete(table,request.args[-1])
          ret = db(table[table._id.name]==request.args[-1]).delete()
          return ret

      exportManager = dict(
          csv_with_hidden_cols=(ExporterCSV,'CSV (hidden cols)'),
          csv=(ExporterCSV,'CSV'),
          xml=(ExporterXML, 'XML'),
          html=(ExporterHTML, 'HTML'),
          tsv_with_hidden_cols=\
              (ExporterTSV,'TSV (Excel compatible, hidden cols)'),
          tsv=(ExporterTSV, 'TSV (Excel compatible)'))
      if not exportclasses is None:
          exportManager.update(exportclasses)

      export_type = request.vars._export_type
      if export_type:
          order = request.vars.order or ''
          if sortable:
              if order and not order=='None':
                  if order[:1]=='~':
                      sign, rorder = '~', order[1:]
                  else:
                      sign, rorder = '', order
                  tablename,fieldname = rorder.split('.',1)
                  orderby=db[tablename][fieldname]
                  if sign=='~':
                      orderby=~orderby

          table_fields = [f for f in fields if f._tablename in tablenames]
          if export_type in ('csv_with_hidden_cols','tsv_with_hidden_cols'):
              if request.vars.keywords:
                  try:
                      dbset = dbset(SQLFORM.build_query(
                              fields,request.vars.get('keywords','')))
                      rows = dbset.select(cacheable=True)
                  except Exception:
                      response.flash = T('Internal Error')
                      rows = []
              else:
                  rows = dbset.select(cacheable=True)
          else:
              rows = dbset.select(left=left,orderby=orderby,
                                  cacheable=True*columns)

          if export_type in exportManager:
              value = exportManager[export_type]
              clazz = value[0] if hasattr(value, '__getitem__') else value
              oExp = clazz(rows)
              filename = '.'.join(('rows', oExp.file_ext))
              response.headers['Content-Type'] = oExp.content_type
              response.headers['Content-Disposition'] = \
                  'attachment;filename='+filename+';'
              raise HTTP(200, oExp.export(),**response.headers)

      elif request.vars.records and not isinstance(
          request.vars.records,list):
          request.vars.records=[request.vars.records]
      elif not request.vars.records:
          request.vars.records=[]

      session['_web2py_grid_referrer_'+formname] = url2(vars=request.vars)
      console = DIV(_class='web2py_console %(header)s %(cornertop)s' % ui)
      error = None
      
      search_actions = DIV(_class='web2py_search_actions')
      if create:
        search_actions.append(gridbutton(buttonclass='buttonadd',
                    buttontext=T('Add'), buttonurl=url(args=['new',tablename])))
        console.append(search_actions)

#      if create:
#          add = gridbutton(
#                  buttonclass='buttonadd',
#                  buttontext='Add',
#                  buttonurl=url(args=['new',tablename]))
#          if not searchable:
#              console.append(add)
      else:
          add = ''

      if searchable:
          sfields = reduce(lambda a,b:a+b,
                           [[f for f in t if f.readable] for t in tables])
          if isinstance(search_widget,dict):
              search_widget = search_widget[tablename]
          if search_widget=='default':
              search_menu = SQLFORM.search_menu(sfields)
              search_widget = lambda sfield, url: CAT(add,FORM(
                  INPUT(_name='keywords',_value=request.vars.keywords,
                        _id='web2py_keywords',_onfocus="jQuery('#w2p_query_fields').change();jQuery('#w2p_query_panel').slideDown();"),
                  INPUT(_type='submit',_value=T('Search'),_class="btn"),
                  INPUT(_type='submit',_value=T('Clear'),_class="btn",
                        _onclick="jQuery('#web2py_keywords').val('');"),
                  _method="GET",_action=url),search_menu)
          form = search_widget and search_widget(sfields,url()) or ''
          console.append(form)
          keywords = request.vars.get('keywords','')
          try:
              if callable(searchable):
                  subquery = searchable(sfields, keywords)
              else:
                  subquery = SQLFORM.build_query(sfields, keywords)
          except RuntimeError:
              subquery = None
              error = T('Invalid query')
      else:
          subquery = None

      if subquery:
          dbset = dbset(subquery)
      try:
          if groupby:
            nrows = len(dbset.select(*groupfields, join=join, left=left, groupby=groupby, having=having, cacheable=True))
          elif left or join:
            nrows = dbset.select('count(*)',join=join,left=left, cacheable=True).first()['count(*)']
          
#          if left or groupby:
#              c = 'count(*)'
#              nrows = dbset.select(c,left=left,cacheable=True,
#                                   groupby=groupby).first()[c]
          else:
              nrows = dbset.count()
      except:
          nrows = 0
          error = T('Unsupported query')

      order = request.vars.order or ''
      if sortable:
        if order and not order=='None':
          if groupby:
            if str(groupby[0]).find(order)>-1:
              tablename,fieldname = order.split('~')[-1].split('.',1)
              sort_field = db[tablename][fieldname]
              exception = sort_field.type in ('date','datetime','time')
              if exception:
                  orderby = (order[:1]=='~' and sort_field) or ~sort_field
              else:
                  orderby = (order[:1]=='~' and ~sort_field) or sort_field
            else:
              tablename,fieldname = order.split('~')[-1].split('.',1)
              gfields = str(groupfields[0]).split(",")
              for gfield in gfields:
                if len(gfield.split(" AS "))>1:
                  if gfield.split(" AS ")[1]==fieldname:
                    if str(gfield.split(" AS ")[0]).find("SUM")>-1:
                      sort_field = db[tablename][fieldname].sum()
                    elif str(gfield.split(" AS ")[0]).find("COUNT")>-1:
                      sort_field = db[tablename][fieldname].count()
                    elif str(gfield.split(" AS ")[0]).find("MIN")>-1:
                      sort_field = db[tablename][fieldname].min()
                    elif str(gfield.split(" AS ")[0]).find("MAX")>-1:
                      sort_field = db[tablename][fieldname].max()
                    elif str(gfield.split(" AS ")[0]).find("LENGTH")>-1:
                      sort_field = db[tablename][fieldname].len()
                    else:
                      break
                    orderby = (order[:1]=='~' and ~sort_field) or sort_field
                    break
          else:
            tablename,fieldname = order.split('~')[-1].split('.',1)
            sort_field = db[tablename][fieldname]
            exception = sort_field.type in ('date','datetime','time')
            if exception:
              orderby = (order[:1]=='~' and sort_field) or ~sort_field
            else:
              orderby = (order[:1]=='~' and ~sort_field) or sort_field

      head = TR(_class=ui.get('header'))
      if selectable:
          head.append(TH(_class=ui.get('default')))
      for field in fields:
          if columns and not str(field) in columns: continue
          if not field.readable: continue
          key = str(field)
          header = headers.get(str(field),
                               hasattr(field,'label') and field.label or key)
          if sortable:
              if key == order:
                  key, marker = '~'+order, sorter_icons[0]
              elif key == order[1:]:
                  marker = sorter_icons[1]
              else:
                  marker = ''
              header = A(header,marker,_href=url(vars=dict(
                          keywords=request.vars.keywords or '',
                          order=key)),_class=trap_class())
          head.append(TH(header, _class=ui.get('default')))

      if links and links_in_grid:
          for link in links:
              if isinstance(link,dict):
                  head.append(TH(link['header'], _class=ui.get('default')))

      # Include extra column for buttons if needed.
      include_buttons_column = (details or editable or deletable or
          (links and links_in_grid and
           not all([isinstance(link, dict) for link in links])))
      if include_buttons_column:
        head.insert(0,TH(_class=ui.get('default','')))
        #  head.append(TH(_class=ui.get('default')))

      paginator = UL()
      if paginate and paginate<nrows:
          npages,reminder = divmod(nrows,paginate)
          if reminder: npages+=1
          try: page = int(request.vars.page or 1)-1
          except ValueError: page = 0
          limitby = (paginate*page,paginate*(page+1))
          def self_link(name,p):
              d = dict(page=p+1)
              if order: d['order']=order
              if request.vars.keywords: d['keywords']=request.vars.keywords
              return A(name,_href=url(vars=d),_class=trap_class())
          NPAGES = 5 # window is 2*NPAGES
          if page>NPAGES+1:
              paginator.append(LI(self_link('<<',0)))
          if page>NPAGES:
              paginator.append(LI(self_link('<',page-1)))
          pages = range(max(0,page-NPAGES),min(page+NPAGES,npages))
          for p in pages:
              if p == page:
                  paginator.append(LI(A(p+1,_onclick='return false'),
                                      _class=trap_class('current')))
              else:
                  paginator.append(LI(self_link(p+1,p)))
          if page<npages-NPAGES:
              paginator.append(LI(self_link('>',page+1)))
          if page<npages-NPAGES-1:
              paginator.append(LI(self_link('>>',npages-1)))
      else:
          limitby = None

      try:
          table_fields = [f for f in fields if f._tablename in tablenames]
          if groupby:
            rows = dbset.select(*groupfields,join=join,left=left,groupby=groupby,having=having,orderby=orderby,limitby=limitby,cacheable=True)
          else:
            rows = dbset.select(join=join,left=left,orderby=orderby,limitby=limitby,cacheable=True,*table_fields)
            
#          rows = dbset.select(left=left,orderby=orderby,
#                              groupby=groupby,limitby=limitby,
#                              cacheable=True,*table_fields)

      except SyntaxError:
          rows = None
          error = T("Query Not Supported")
      if nrows:
          message = error or T('%(nrows)s records found') % dict(nrows=nrows)
          console.append(DIV(message,_class='web2py_counter'))

      if rows:
          htmltable = TABLE(THEAD(head))
          tbody = TBODY()
          numrec=0
          for row in rows:
              if numrec % 2 == 0:
                  classtr = 'even'
              else:
                  classtr = 'odd'
              numrec+=1
              id = row[field_id] #@ReservedAssignment
              if id:
                  rid = id
                  if callable(rid): ### can this ever be callable?
                      rid = rid(row)
                  tr = TR(_id=rid, _class='%s %s' % (classtr, 'with_id'))
              else:
                  tr = TR(_class=classtr)
              if selectable:
                  tr.append(INPUT(_type="checkbox",_name="records",_value=id,
                                  value=request.vars.records))
              for field in fields:
                  if not str(field) in columns: continue
                  if not field.readable: continue
                  if field.type=='blob': continue
                  value = row[field]
                  maxlength = maxtextlengths.get(str(field),maxtextlength)
                  if field.represent:
                      try:
                          value=field.represent(value,row)
                      except Exception:
                          try:
                              value=field.represent(value,row[field._tablename])
                          except Exception:
                              pass
                  elif field.type=='boolean':
                      value = INPUT(_type="checkbox",_checked = value,
                                    _disabled=True)
                  elif field.type=='upload':
                      if value:
                          if callable(upload):
                              value = A(current.T('file'), _href=upload(value))
                          elif upload:
                              value = A(current.T('file'),
                                        _href='%s/%s' % (upload, value))
                      else:
                          value = ''
                  if isinstance(value,str):
                      value = truncate_string(value,maxlength)
                  elif not isinstance(value,DIV):
                      value = field.formatter(value)
                  tr.append(TD(value))
              row_buttons = TD(_class='row_buttons')
              if links and links_in_grid:
                  for link in links:
                      if isinstance(link, dict):
                          tr.append(TD(link['body'](row)))
                      else:
                          if link(row):
                              row_buttons.append(link(row))
              if include_buttons_column:
                  if details and (not callable(details) or details(row)):
                      row_buttons.append(gridbutton(
                              'buttonview', 'View',
                              url(args=['view',tablename,id])))
                  if editable and (not callable(editable) or editable(row)):
                      row_buttons.append(gridbutton(
                              'buttonedit', 'Edit',
                              url(args=['edit',tablename,id])))
                  if deletable and (not callable(deletable) or deletable(row)):
                      row_buttons.append(gridbutton(
                              'buttondelete', 'Delete',
                              callback=url(args=['delete',tablename,id]),
                              delete='tr'))
                  #tr.append(row_buttons)
                  tr.insert(0,row_buttons)
              tbody.append(tr)
          htmltable.append(tbody)
          htmltable = DIV(htmltable,_style='width:100%;overflow-x:auto')
          if selectable:
              htmltable = FORM(htmltable,INPUT(_type="submit"))
              if htmltable.process(formname=formname).accepted:#
                  htmltable.vars.records = htmltable.vars.records or []
                  htmltable.vars.records = htmltable.vars.records if type(htmltable.vars.records) == list else [htmltable.vars.records]
                  records = [int(r) for r in htmltable.vars.records]
                  selectable(records)
                  redirect(referrer)
      else:
          htmltable = DIV(current.T('No records found'))

      if csv and nrows:
          export_links =[]
          for k,v in sorted(exportManager.items()):
              label = v[1] if hasattr(v, "__getitem__") else k
              link = url2(vars=dict(
                      order=request.vars.order or '',
                      _export_type=k,
                      keywords=request.vars.keywords or ''))
              export_links.append(A(T(label),_href=link))
          export_menu = \
              DIV(T('Export:'),_class="w2p_export_menu",*export_links)
      else:
          export_menu = None

      res = DIV(console,DIV(htmltable,_class="web2py_table"),
                _class='%s %s' % (_class, ui.get('widget')))
      if paginator.components:
          res.append(
              DIV(paginator,
                  _class="web2py_paginator %(header)s %(cornerbottom)s"%ui))
      if export_menu: res.append(export_menu)
      res.create_form = create_form
      res.update_form = update_form
      res.view_form = view_form
      res.search_form = search_form
      return res
    