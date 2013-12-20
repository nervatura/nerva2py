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
  
from nerva2py.localstore import getSql, setSqlParams, setEngine
from nerva2py.ordereddict import OrderedDict

from xlwt import easyxf
from xlwt import Workbook
from StringIO import StringIO
import os, subprocess
import datetime
from gluon.html import SPAN, DIV, P, BR, A, URL
from gluon.http import redirect

from xml.dom.minidom import Document, parseString
from zlib import compress, decompress

class dict2obj(dict):
  def __init__(self, dict_):
    super(dict2obj, self).__init__(dict_)
    for key in self:
      item = self[key]
      if isinstance(item, list):
        for idx, it in enumerate(item):
          if isinstance(it, dict):
            item[idx] = dict2obj(it)
      elif isinstance(item, dict):
        self[key] = dict2obj(item)

  def __getattr__(self, key):
    return self[key]

class auth_ini(object):
  def __init__(self,session,login_url):
    self.session = session
    self.login_url = login_url
  def requires_login(self):
    def decorator(action):
      def f(*a, **b):
        try:
          if self.session.alias==None or self.session.auth.user.alias != self.session.alias:
            redirect(self.login_url)
        except Exception:
          redirect(self.login_url)
        return action(*a, **b)
      f.__doc__ = action.__doc__
      f.__name__ = action.__name__
      f.__dict__.update(action.__dict__)
      return f
    return decorator
    
class NervaTools(object):

  def checkValues(self, ns, params):
    #return {"returnType":"warning", "returnValue":"Warning message. Continue?"}
    #return {"returnType":"error", "returnValue":"Error message. The operation can not continue!"}
    return {"returnType":"ok", "returnValue":""}
  
  def callMenuCmd(self, ns, params):
    fnum1 = 0
    try:
      if type(params).__name__=="dict":
        fnum1 = params["number_1"]
      else:
        fnum1 = params[0].value
      fnum1 = float(fnum1.replace(",","."))
    except Exception:
      return "Invalid number: "+str(fnum1)
    fnum2 = 0
    try:
      if type(params).__name__=="dict":
        fnum2 = params["number_2"]
      else:
        fnum2 = params[1].value
      fnum2 = float(fnum2.replace(",","."))
    except Exception:
      return "Invalid number: "+str(fnum2)
    return "Successfully processed: "+str(fnum1+fnum2)
  
  def convert_numtotext_hu(self, ns, params):
    if params["numvalue"]==None:
      return ""
    if len(str(int(abs(params["numvalue"]))))>12:
      return ""
    
    in_number_str = str(int(abs(params["numvalue"])));
    if len(in_number_str) > 9:
      tmp_str4 = in_number_str[0:len(in_number_str)-9]
      tmp_str4 = self.convert_numtotext_gen(ns, params["lang"], tmp_str4)
    else:
      tmp_str4=""
    if tmp_str4 != "":
      tmp_str4 = tmp_str4 + 'milliárd'
      in_number_str = in_number_str[len(in_number_str)-9:]
    else:
      tmp_str4 = ""
    
    if len(in_number_str) > 6:
      tmp_str3 = in_number_str[0:len(in_number_str)-6]
      tmp_str3 = self.convert_numtotext_gen(ns, params["lang"], tmp_str3)
    else:
      tmp_str3=""
    if tmp_str3 != "":
      tmp_str3 = tmp_str3 + 'millió'
      in_number_str = in_number_str[len(in_number_str)-6:]
    else:
      tmp_str3 = ""
    
    if len(in_number_str) > 3:
      tmp_str2 = in_number_str[0:len(in_number_str)-3]
      tmp_str2 = self.convert_numtotext_gen(ns, params["lang"], tmp_str2)
    else:
      tmp_str2=""
    if tmp_str2 != "":
      tmp_str2 = tmp_str2 + 'ezer'
      in_number_str = in_number_str[len(in_number_str)-3:]
    else:
      tmp_str2 = ""
        
    if len(in_number_str) > 0:
      tmp_str = in_number_str
      tmp_str = self.convert_numtotext_gen(ns, params["lang"], tmp_str)
    else:
      tmp_str=""
  
    out_string = ""
    if tmp_str4 != "":
      out_string = tmp_str4
    if tmp_str3 != "":
      if out_string !="":
        out_string = out_string + '-' + tmp_str3
      else:
        out_string = tmp_str3
    if tmp_str2 !="":
      if out_string !="":
        out_string = out_string + '-' + tmp_str2
      else:
        out_string = tmp_str2
    if tmp_str != "":
      if out_string != "":
        out_string = out_string + '-' + tmp_str
      else:
        out_string = tmp_str
    if params["numvalue"]<0:
      out_string = "mínusz " + out_string
    return out_string
  
  def convert_numtotext_gen(self, ns, lang, inumvalue):
    
    in_number_str = inumvalue;
    tmp_str3 = ""
    if len(str(in_number_str)) == 3:
      nstr = ns.db((ns.db.ui_numtotext.lang==lang.upper())
                   &(ns.db.ui_numtotext.digi==len(in_number_str))
                   &(ns.db.ui_numtotext.deci==int(in_number_str[0:1]))).select()
      if len(nstr)>0:
        nstr = nstr[0]
        if nstr.number_str != None:
          tmp_str3 = nstr.number_str
      in_number_str = in_number_str[1:]
        
    tmp_str2 = ""
    if len(str(in_number_str)) == 2:
      nstr = ns.db((ns.db.ui_numtotext.lang==lang.upper())
                   &(ns.db.ui_numtotext.digi==len(in_number_str))
                   &(ns.db.ui_numtotext.deci==int(in_number_str[0:1]))).select()
      if len(nstr)>0:
        nstr = nstr[0]
        if in_number_str[1:2]=="0":
          number_str = nstr.number_str
        else:
          number_str = nstr.number_str2
        if number_str != None:
          tmp_str2 = nstr.number_str
      in_number_str = in_number_str[1:]

    tmp_str = ""
    if len(str(in_number_str)) == 1:
      nstr = ns.db((ns.db.ui_numtotext.lang==lang.upper())
                   &(ns.db.ui_numtotext.digi==len(in_number_str))
                   &(ns.db.ui_numtotext.deci==int(in_number_str[0:1]))).select()
      if len(nstr)>0:
        nstr = nstr[0]
        if nstr.number_str != None:
          tmp_str = nstr.number_str
    
    out_string = tmp_str3 + tmp_str2 + tmp_str
    return out_string;
  
  def getPriceValueDal(self, ns, params):
    price = 0
    #best listprice
    price_nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="price")).select().as_list()[0]["id"]
    left = (ns.db.link.on((ns.db.price.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==price_nervatype)&(ns.db.link.deleted==0)))
    prow = ns.db((ns.db.price.deleted==0)&(ns.db.price.discount==None)&(ns.db.price.vendorprice==params["vendorprice"])
          &(ns.db.price.pricevalue!=0)&(ns.db.price.product_id==params["product_id"])&(ns.db.price.validfrom<=params["posdate"])
          &((ns.db.price.validto>=params["posdate"])|(ns.db.price.validto==None))
          &(ns.db.price.curr==params["curr"])&(ns.db.price.qty<=params["qty"])&(ns.db.link.ref_id_2==None)
          ).select(ns.db.price.pricevalue.min().with_alias('mp'), left=left).as_list()
    if len(prow)>0:
      if prow[0]["mp"]!=None:
        price = prow[0]["mp"]
    
    #best customer price
    customer_nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="customer")).select().as_list()[0]["id"]
    prow = ns.db((ns.db.price.deleted==0)&(ns.db.link.deleted==0)
          &(ns.db.price.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==price_nervatype)
          &(params["customer_id"]==ns.db.link.ref_id_2)&(ns.db.link.nervatype_2==customer_nervatype)
          &(ns.db.price.discount==None)&(ns.db.price.vendorprice==params["vendorprice"])
          &(ns.db.price.pricevalue!=0)&(ns.db.price.product_id==params["product_id"])&(ns.db.price.validfrom<=params["posdate"])
          &((ns.db.price.validto>=params["posdate"])|(ns.db.price.validto==None))
          &(ns.db.price.curr==params["curr"])&(ns.db.price.qty<=params["qty"])).select(ns.db.price.pricevalue.min().with_alias('mp')).as_list()
    if len(prow)>0:
      if prow[0]["mp"]!=None:
        if prow[0]["mp"]!=0 and prow[0]["mp"]<price:
          price = prow[0]["mp"]
          
    #best customer groups price    
    groups_nervatype = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
    cgroup_count = ns.db((ns.db.link.deleted==0)&(ns.db.link.nervatype_1==customer_nervatype)
                      &(ns.db.link.nervatype_2==groups_nervatype)&(ns.db.link.ref_id_1==params["customer_id"])).select().as_list()
    if len(cgroup_count)>0:
      customer_group = (ns.db.groups.id.belongs(ns.db((ns.db.link.deleted==0)&(ns.db.link.nervatype_1==customer_nervatype)
                        &(ns.db.link.nervatype_2==groups_nervatype)&(ns.db.link.ref_id_1==params["customer_id"])).select(ns.db.link.ref_id_2.with_alias('id'))))
      prow = ns.db((ns.db.price.deleted==0)&(ns.db.link.deleted==0)
            &(ns.db.price.id==ns.db.link.ref_id_1)&(ns.db.link.nervatype_1==price_nervatype)
            &(ns.db.groups.id==ns.db.link.ref_id_2)&(ns.db.link.nervatype_2==groups_nervatype)&customer_group
            &(ns.db.price.discount==None)&(ns.db.price.vendorprice==params["vendorprice"])
            &(ns.db.price.pricevalue!=0)&(ns.db.price.product_id==params["product_id"])&(ns.db.price.validfrom<=params["posdate"])
            &((ns.db.price.validto>=params["posdate"])|(ns.db.price.validto==None))
            &(ns.db.price.curr==params["curr"])&(ns.db.price.qty<=params["qty"])).select(ns.db.price.pricevalue.min().with_alias('mp')).as_list()
      if len(prow)>0:
        if prow[0]["mp"]!=None:
          if prow[0]["mp"]!=0 and prow[0]["mp"]<price:
            price = prow[0]["mp"]
    return price
  
  def getPriceValue(self, ns, params):
    if params.has_key("appl"):
      appl = params["appl"]
    else:
      appl = "nflex"
    sql_str = getSql(ns.lstore, ns.engine, "dbsFunctions_getPriceValue_1",appl)
    sql_str = sql_str.replace("@product_id", str(params["product_id"]))
    sql_str = sql_str.replace(":row_id", str(params["row_id"]))
    sql_str = sql_str.replace(":qty", str(params["qty"]))
    sql_str = sql_str.replace(":customer_id", str(params["customer_id"]))
    rowList = ns.db.executesql(sql_str, as_dict=True)
    
    for product in rowList:
      #set best price
      sql_str = getSql(ns.lstore, ns.engine, "dbsFunctions_getPriceValue_2",appl)
      sql_str = sql_str.replace(":posdate", "'"+str(params["posdate"])+"'")
      sql_str = sql_str.replace(":qty", str(params["qty"]))
      sql_str = sql_str.replace(":curr", "'"+str(params["curr"])+"'")
      sql_str = sql_str.replace(":vendorprice", str(params["vendorprice"]))
      sql_str = sql_str.replace(":product_id", str(product["id"]))
      sql_str = sql_str.replace(":customer_id", str(params["customer_id"]))
      prow = ns.db.executesql(sql_str, as_dict=True)
      if len(prow)>0:
        row = prow[0]
        if row["pricevalue"]!=None:
          product["fxprice"] = row["pricevalue"]
      
      #available discounts
      if product["fxprice"]<>0:
        sql_str = getSql(ns.lstore, ns.engine, "dbsFunctions_getPriceValue_3",appl)
        sql_str = sql_str.replace(":posdate", "'"+str(params["posdate"])+"'")
        sql_str = sql_str.replace(":qty", str(params["qty"]))
        sql_str = sql_str.replace(":curr", "'"+str(params["curr"])+"'")
        sql_str = sql_str.replace(":vendorprice", str(params["vendorprice"]))
        sql_str = sql_str.replace(":product_id", str(product["id"]))
        sql_str = sql_str.replace(":customer_id", str(params["customer_id"]))
        prow = ns.db.executesql(sql_str, as_dict=True)
        discount = 0
        disprice = product["fxprice"]
        for disrow in prow:
          if disrow["lmt"]<>0 and product["fxprice"]*params["qty"]<disrow["lmt"]:
            continue
          if disrow["calcmode"]=="ded":
            #deduction(%)
            if disrow["discount"]>0 and disrow["discount"]<100:
              if disprice>product["fxprice"]*(1-disrow["discount"]/100):
                disprice=product["fxprice"]*(1-disrow["discount"]/100)
                discount=disrow["discount"]
          elif disrow["calcmode"]=="add":
            #adding(%)
            if disrow["discount"]>0 and disrow["discount"]<100:
              if disprice>product["fxprice"]*(1+disrow["discount"]/100) and disprice != product["fxprice"]:
                disprice=product["fxprice"]*(1+disrow["discount"]/100)
                discount=0
          elif disrow["calcmode"]=="amo":
            #amount(+/-)
            if disprice>product["fxprice"]+disrow["discount"]:
              disprice=product["fxprice"]+disrow["discount"]
              discount=0
        if disprice<>0:
          if discount>0:
            product["discount"] = discount
          else:
            product["fxprice"] = disprice
          product["actionprice"] = 1
    return rowList
  
  def nextNumber(self, ns, params):
    #Get current value from numberdef table (transnumber, custnumber, partnumber etc.)
    #Params:
    #0: number id (current custnumber = customer_number etc.)
    #1: if True, increases by 1
    retnumber = ""
    try:
      defrow = ns.db(ns.db.numberdef.numberkey==params["id"]).select()
      if len(defrow)==0:
        ns.db.numberdef.insert(numberkey=params["id"])
        defrow = ns.db(ns.db.numberdef.numberkey==params["id"]).select()
      defrow = defrow[0]
      if defrow.prefix != None:
        retnumber = defrow.prefix+defrow.sep
      if defrow.isyear == 1:
        transyear = ns.db(ns.db.fieldvalue.fieldname=="transyear").select()
        if len(transyear)>0:
          transyear = transyear[0]
          retnumber = retnumber+transyear.value+defrow.sep
      retnumber = retnumber+str(defrow.curvalue+1).zfill(defrow.len)
      if params["step"]== True:
        defrow.curvalue +=1
        defrow.update_record()
    except Exception, err:
      raise RuntimeError(err)
    return retnumber
  
  def exportToICalendar(self, ns, event_id, export_fields=False):
    from icalendar import Calendar, Event, vDatetime
    import uuid
    
    cal = Calendar()
    cal.add('prodid', '-//nervatura.com/NONSGML Nervatura Calendar//EN')
    cal.add('version', '2.0')
    clevent = Event()
    events = ns.db(ns.db.event.id==event_id).select()
    if len(events)>0:
      event = events[0]
      if event.uid!=None:
        clevent['uid'] = event.uid
      else:
        clevent['uid'] = uuid.uuid4()
      if event.fromdate!=None:
        clevent['dtstart'] = vDatetime(event.fromdate).ical()
      if event.todate!=None:
        clevent['dtend'] = vDatetime(event.todate).ical()  
      if event.subject!=None:
        clevent['summary'] = event.subject
      if event.place!=None:
        clevent['location'] = event.place
      if event.eventgroup!=None:
        eventgroup = ns.db(ns.db.groups.id==event.eventgroup).select()
        if len(eventgroup)>0:
          clevent['category'] = eventgroup[0].groupvalue
      if event.description!=None:
        clevent['description'] = event.description
      if export_fields:
        nervatype_event = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="event")).select().as_list()[0]["id"]
        join = [(ns.db.deffield.on((ns.db.fieldvalue.fieldname==ns.db.deffield.fieldname)&(ns.db.deffield.deleted==0)&(ns.db.deffield.visible==1)
             &(ns.db.deffield.nervatype==nervatype_event)))]
        fields = ns.db((ns.db.fieldvalue.deleted==0)&(ns.db.fieldvalue.ref_id==event_id)).select(ns.db.fieldvalue.fieldname, ns.db.deffield.description, ns.db.fieldvalue.value, ns.db.fieldvalue.notes, join=join)
        for field in fields:
          if field.fieldvalue.value:
            clevent[field.fieldvalue.fieldname+'_value'] = str(field.fieldvalue.value)
          if field.fieldvalue.notes:
            clevent[field.fieldvalue.notes+'_data'] = str(field.fieldvalue.notes)
    cal.add_component(clevent)
    return cal.as_string()
  
  estyles = {
      'header': easyxf(
        'font: bold true, height 160;'
        'alignment: horizontal left, vertical center;'
        'pattern: back_colour gray25;'
        'borders: left thin, right thin, top thin, bottom thin;'),
      'float': easyxf(
        'alignment: horizontal right, vertical center;'
        'borders: left thin, right thin, top thin, bottom thin;',
        num_format_str='# ### ##0.00'),
      'integer': easyxf(
        'alignment: horizontal right, vertical center;'
        'borders: left thin, right thin, top thin, bottom thin;',
        num_format_str='# ### ##0'),
      'date': easyxf(
        'alignment: horizontal center, vertical center;'
        'borders: left thin, right thin, top thin, bottom thin;',
        num_format_str='yyyy.mm.dd'),
      'bool': easyxf(
        'alignment: horizontal center, vertical center;'
        'borders: left thin, right thin, top thin, bottom thin;'),
      'string': easyxf(
        'alignment: horizontal left, vertical center;'
        'borders: left thin, right thin, top thin, bottom thin;')}
  
  def exportToExcel(self, ns, sheet, view, ibook=None):
    if ibook:
      book = ibook
    else:
      book = Workbook(encoding='utf-8')
    
    styles = self.estyles
    sheet1 = book.add_sheet(sheet["sheetName"])     
    colnum = 0;
    for col in sheet["columns"]:
      sheet1.write(0, colnum, col["label"], styles["header"])
      colnum = colnum + 1
    
    if type(view).__name__!="list":
      sqlStr = setSqlParams(ns.lstore, ns.engine, None, view["sqlStr"], view["whereStr"], 
                          view["havingStr"], view["paramList"], False, "")
      view = ns.db.executesql(sqlStr, as_dict=True)    
    rownum = 1  
    for row in view:
      colnum = 0
      for col in sheet["columns"]:
        if col["type"]=="float":
          sheet1.write(rownum, colnum, row[col["name"]], styles["float"])
        if col["type"]=="integer":
          sheet1.write(rownum, colnum, row[col["name"]], styles["integer"])
        if col["type"]=="date":
          sheet1.write(rownum, colnum, row[col["name"]], styles["date"])
        if col["type"]=="bool":
          sheet1.write(rownum, colnum, row[col["name"]], styles["bool"])
        if col["type"]=="string":
          sheet1.write(rownum, colnum, row[col["name"]], styles["string"])
        colnum = colnum + 1
      rownum = rownum + 1
    
    if ibook:
      return book
    else:
      output = StringIO()
      book.save(output)
      contents = output.getvalue()
      output.close
      return contents
  
  def getItemFromKey(self, table, field, value):
    #from/return object
    retval = None
    index = next((i for i in xrange(len(table)) if table[i][field] == value), None)
    if index is not None:
      retval = table[index]
    return retval

  def getReport(self, ns, params, filters):
    if params.has_key("reportcode"):
      report_ = ns.db(ns.db.ui_report.reportkey==params["reportcode"]).select().as_list()
    elif params.has_key("report_id"):
      report_ = ns.db(ns.db.ui_report.id==params["report_id"]).select().as_list()
    else:
      return "Error|Missing reportcode or report_id"
    if len(report_)>0:
      report = report_[0]
    else:
      return str(ns.T("Error|Unknown reportcode: "))+str(params["reportcode"])
    fieldtypes = ns.db(ns.db.groups.groupname=="fieldtype").select().as_list()
    wheretypes = ns.db(ns.db.groups.groupname=="wheretype").select().as_list()
    reportfields = ns.db(ns.db.ui_reportfields.report_id==report["id"]).select().as_list()
    reportsources = ns.db(ns.db.ui_reportsources.report_id==report["id"]).select().as_list()
    where_str = {}
    for fieldname in filters.keys():
      reportfield = self.getItemFromKey(reportfields, "fieldname", fieldname)
      if reportfield==None:
        if fieldname=="@id":
          for rs in reportsources:
            rs["sqlstr"] = rs["sqlstr"].replace(str(fieldname), str(filters[fieldname]))
          continue
        else:
          return str(ns.T("Error|Unknown reportfield: "))+str(fieldname)
      fieldtype = self.getItemFromKey(fieldtypes, "id", reportfield["fieldtype"])["groupvalue"]
      wheretype = self.getItemFromKey(wheretypes, "id", reportfield["wheretype"])["groupvalue"]
      rel=" = "
      if fieldtype=="date":
        if not str(filters[fieldname]).startswith("'"): filters[fieldname]="'"+filters[fieldname]+"'"
      if fieldtype=="string":
        if not str(filters[fieldname]).startswith("'"): filters[fieldname]="'"+filters[fieldname]+"%'"
        rel = " like "
      for rs in reportsources:
        if reportfield["dataset"]==rs["dataset"] or reportfield["dataset"]==None:
          if wheretype=="where":
            if reportfield["dataset"]==None:
              wkey = "nods"
            else:
              wkey = str(reportfield["dataset"])
            if reportfield["sqlstr"]==None or reportfield["sqlstr"]=="":
              fstr = str(fieldname)+rel+str(filters[fieldname])
            else:
              fstr = reportfield["sqlstr"].replace("@"+str(fieldname), str(filters[fieldname]))
            if where_str.has_key(wkey)==False:
              where_str[wkey]=" and "+fstr
            else:
              where_str[wkey]=where_str[wkey]+" and "+fstr
          else:
            if reportfield["sqlstr"]==None or reportfield["sqlstr"]=="":
              rs["sqlstr"] = rs["sqlstr"].replace("@"+str(fieldname), str(filters[fieldname]))
            else:
              fstr = reportfield["sqlstr"].replace("@"+str(fieldname), str(filters[fieldname]))
              rs["sqlstr"] = rs["sqlstr"].replace("@"+str(fieldname), fstr)
    datarows = {}
    trows = 0
    for rs in reportsources:
      if str(rs["sqlstr"]).startswith("function"):
        fu_str = str(rs["sqlstr"]).split("|")
        func = fu_str[1]
        if callable(self.__getattribute__(func)):
          func = self.__getattribute__(func)
          fparams={}
          for prm in fu_str:
            if len(str(prm).split("=>"))>1:
              pname = str(prm).split("=>")[0]
              pvalue = str(prm).split("=>")[1]
              if str(pvalue).startswith("select"):
                pvalue = ns.db.executesql(str(pvalue))[0][0]
              fparams[pname] = pvalue
          datarows[str(rs["dataset"])] = func(ns, fparams)
          trows = trows+len(datarows[str(rs["dataset"])])
      else:
        if where_str.has_key(str(rs["dataset"]))==True:
          rs["sqlstr"] = rs["sqlstr"].replace("@where_str", str(where_str[rs["dataset"]]))
        if where_str.has_key("nods")==True:
          rs["sqlstr"] = rs["sqlstr"].replace("@where_str", str(where_str["nods"]))
        rs["sqlstr"] = rs["sqlstr"].replace("@where_str", "")
        datarows[str(rs["dataset"])] = ns.db.executesql(rs["sqlstr"], as_dict=True)
        trows = trows+len(datarows[str(rs["dataset"])])
    datarows["title"]=report["repname"]
    datarows["crtime"]=datetime.date.strftime(datetime.datetime.now(),"%Y.%m.%d %H:%M")
    if trows==0:
      return str(ns.T("NODATA"))
    elif datarows.has_key("ds"):
      if len(datarows["ds"])==0:
        return str(ns.T("NODATA"))
    filetype = ns.db.groups(id=report["filetype"])["groupvalue"]
    if filetype=="fpdf":
      from nerva2py.report import Report
      try:
        rpt = Report(orientation=params["orientation"],page=params["size"])
        rpt.databind = datarows
        if params["output"] in("html","xml"):
          rpt.images_folder = ns.request.env.wsgi_url_scheme+"://"+ns.request.env.http_host+"/"+ns.request.application+"/static/images"
        else:
          rpt.images_folder = os.path.join(ns.request.folder, 'static', 'images')
        rpt.loadDefinition(report["report"])
        rpt.createReport()
        if params["output"]=="html":
          return {"filetype":filetype, "template":rpt.save2Html(),"data":None}
        elif params["output"]=="xml":
          return {"filetype":filetype, "template":rpt.save2Xml(),"data":None}
        else: 
          return {"filetype":filetype, "template":rpt.save2Pdf(),"data":None}
      except Exception, err:
        return "Error|"+str(err)
    elif filetype=="xls":
      book = Workbook(encoding='utf-8')
      import ast
      report_tmp = ast.literal_eval(report["report"])
      for skey in datarows.keys():
        if type(datarows[skey]).__name__=="list":
          if len(datarows[skey])>0:
            sheetName = skey
            columns = []
            if report_tmp.has_key(skey):
              if report_tmp[skey].has_key("sheetName"):
                sheetName = report_tmp[skey]["sheetName"]
              if report_tmp[skey].has_key("columns"):
                columns = report_tmp[skey]["columns"]
            else:
              for colname in datarows[skey][0].keys():
                columns.append({"name":colname,"label":colname,"type":"string"})
            sheet = {"sheetName":sheetName,"columns":columns}
            book = self.exportToExcel(ns, sheet, datarows[skey], book)
      output = StringIO()
      book.save(output)
      contents = output.getvalue()
      output.close
      return {"filetype":filetype, "template":contents,"data":None}
    elif filetype=="html":
      return {"filetype":filetype, "template":report["report"],"data":datarows}
    elif filetype=="gshi":
      from genshi.template import MarkupTemplate  #@UnresolvedImport
      try:
        tmpl = MarkupTemplate(report["report"])
        html_tmpl = tmpl.generate(**datarows).render('html', doctype='html')
        return {"filetype":filetype, "template":html_tmpl,"data":None}
      except Exception, err:
        return "Error|"+str(err)
    else:
      return str(ns.T("Error|Unknown filetype: "))+str(filetype)
    
  def loadReport(self, ns, fileName=None, fileStr=None, insert=True):
    try:
      if fileName:
        if not os.path.isfile(os.path.join(ns.request.folder,'static/resources/report/'+fileName)):
          return "Error|Missing application!"
        rp_sql = str(open(os.path.join(ns.request.folder,'static/resources/report/'+fileName), 'r').read()).split(";--")
      elif fileStr:
        rp_sql = str(fileStr).split(";--")
      else:
        return "Error|Missing parameter filename or file..."
      for sql in rp_sql:
        if (str(sql).lower().find("insert")>-1 and insert) or str(sql).lower().find("update")>-1:
          if str(sql).lower().find("set report")>-1:
            report = str(sql)[str(sql).lower().find("'")+1:str(sql).lower().rfind("'",0,str(sql).lower().rfind("where"))]
            reportkey = str(sql)[str(sql).lower().rfind("'",0,str(sql).lower().rfind("'")-1)+1:str(sql).lower().rfind("'")]
            ns.db(ns.db.ui_report.reportkey==reportkey).update(**{"report":report})
          else:
            if str(sql).lower().find("engine")>-1:
              if str(sql).lower().find(ns.engine)>-1:
                sql = str(sql).replace("[engine "+ns.engine+"]", "")
                ns.db._adapter.execute(sql)
            else:
              ns.db._adapter.execute(sql)
      return "OK"
    except Exception, err:
      return "Error|"+str(err)
    
  def createDatabase(self, ns, alias):
    rs = DIV()
    err_no = 0
    try:
      dbref = ns.lstore(ns.lstore.databases.alias == alias).select()
      if len(dbref) == 0:
        rs.append(DIV(SPAN(str("Error: "+str(ns.T("Unknown database alias!"))),_style="color:red;font-weight: bold;"),BR()))
      else:
        rs.append(DIV(SPAN("Database alias: ",_style="color:blue;font-weight: bold;"),
             SPAN(str(alias),_style="font-weight: bold;"),BR()))
        rs.append(DIV(SPAN("Start process: ",_style="color:blue;font-weight: bold;"),
             SPAN(str(datetime.datetime.now()),_style="font-weight: bold;"),BR()))    
        if setEngine(ns, alias,True, True)==False:
          rs.append(DIV(SPAN("Error: "+str(ns.error_message),_style="color:red;font-weight: bold;"),BR()))
          err_no+=1
        else:
          rs.append(DIV(SPAN("OK ",_style="color:green;font-weight: bold;"),
                        SPAN("Creating database tables ...",_style="font-weight: bold;"),BR()))
        
        if ns.createIndex()==False:
          rs.append(DIV(SPAN("Error: "+str(ns.error_message),_style="color:red;font-weight: bold;"),BR()))
          err_no+=1
        else:
          rs.append(DIV(SPAN("OK ",_style="color:green;font-weight: bold;"),
                        SPAN("Creating indexes ...",_style="font-weight: bold;"),BR()))
          
        if ns.insertIniData()==False:
          rs.append(DIV(SPAN("Error: "+str(ns.error_message),_style="color:red;font-weight: bold;"),BR()))
          err_no+=1
        else:
          rs.append(DIV(SPAN("OK ",_style="color:green;font-weight: bold;"),
                        SPAN("Data initialization ...",_style="font-weight: bold;"),BR()))
           
        if ns.insertDfReports()==False:
          rs.append(DIV(SPAN("Error: "+str(ns.error_message),_style="color:red;font-weight: bold;"),BR()))
          err_no+=1
        else:
          rs.append(DIV(SPAN("OK ",_style="color:green;font-weight: bold;"),
                        SPAN("Loading report templates and data ...",_style="font-weight: bold;"),BR()))

        #only nervaflex ini
        if ns.insertNfbase()==False:
          rs.append(DIV(SPAN("Error: "+str(ns.error_message),_style="color:red;font-weight: bold;"),BR()))
          err_no+=1
        else:
          rs.append(DIV(SPAN("OK ",_style="color:green;font-weight: bold;"),
                        SPAN("NervaFlex data initialization ...",_style="font-weight: bold;"),BR()))
        if err_no==0:
          rs.append(DIV(SPAN("Result: ",_style="color:blue;font-weight: bold;"),
                  SPAN("The process has run without error!",_style="font-weight: bold;"),BR(),
                  SPAN("The database created successfully!",_style="font-weight: bold;"),BR()))  
        else:
          rs.append(DIV(SPAN("Result: ",_style="color:blue;font-weight: bold;"),
                  SPAN("Error messages: "+str(err_no),_style="font-weight: bold;"),BR()))
        rs.append(DIV(SPAN("End process: ",_style="color:blue;font-weight: bold;"),
                SPAN(str(datetime.datetime.now()),_style="font-weight: bold;"),BR()))
    except Exception, err:
      rs.append(P("Error: "+str(err),_style="color:red;font-weight: bold;"))
    finally:
      return rs
  
  def represent(self,field,value,record,clear=False):
    f = field.represent
    if not callable(f):
      return value
    n = f.func_code.co_argcount-len(f.func_defaults or [])
    if n==1:
      rvalue = f(value)
    elif n==2:
      rvalue = f(value,record)
    else:
      rvalue = value
    if clear:
      if type(rvalue).__name__=="A":
        return rvalue[0][0]
      elif type(rvalue).__name__=="DIV":
        return rvalue[0]
    return rvalue
  
  lst_nom = ["address","barcode","contact","currency","customer","deffield","employee","event","groups","item","link",
             "movement","numberdef","pattern","payment","place","price","product","project","rate","tax","tool",
             "trans","setting"]
  
  lst_senom = ["ui_menu","ui_menufields","ui_report", "ui_reportfields","ui_reportsources",
               "ui_applview","ui_viewfields","ui_filter","ui_groupinput", "ui_language","ui_locale","ui_message",
               "ui_zipcatalog","ui_numtotext","ui_userconfig","ui_audit"]
    
  def createDataBackup(self, ns, ndi, alias, btype, lst_nom=[], bformat="backup", filename="",verNo="?"):
    rs = DIV()
    try:
      dbref = ns.lstore(ns.lstore.databases.alias == alias).select()
      if len(dbref) == 0:
        rs = DIV(SPAN(str("Error: "+str(ns.T("Unknown database alias!"))),_style="color:red;font-weight: bold;"),BR())
        return
      else:
        if btype not in("customer","settings"):
          rs = SPAN("Error: Valid backuptype parameter: customer, settings",_style="color:red;font-weight: bold;")
          return
        if bformat not in("backup","xml"):
          rs = SPAN("Error: Valid format parameter: backup, xml",_style="color:red;font-weight: bold;")
          return
        if len(lst_nom)>0:
          for nom in lst_nom:
            try:
              if btype=="customer":
                self.lst_nom.index(str(nom).strip())
              else:
                self.lst_senom.index(str(nom).strip())
            except Exception:
              rs = SPAN("Error: Invalid Nervatura object: "+str(nom),_style="color:red;font-weight: bold;")
              return
        else:
          lst_nom = self.lst_nom if btype=="customer" else self.lst_senom
        if filename == None:
          filename = "download"
        elif filename == "":
          filename = alias+"_"+btype
      
      err_no=0
      rs.append(DIV(SPAN("Database alias: ",_style="color:blue;font-weight: bold;"),
             SPAN(str(alias),_style="font-weight: bold;"),
             BR(),
             SPAN("Format: ",_style="color:blue;font-weight: bold;"),
             SPAN(str(bformat),_style="font-weight: bold;"),BR()))
      rs.append(DIV(SPAN("Start process: ",_style="color:blue;font-weight: bold;"),
                 SPAN(str(datetime.datetime.now()),_style="font-weight: bold;")))
        
      doc = Document()
      data = doc.createElement("data")
      data.setAttribute("timestamp",str(datetime.datetime.now()))
      data.setAttribute("verno",verNo)
      data.setAttribute("type",btype)
      doc.appendChild(data)
      
      def insertDoc(btype,err_no):
        if str(nom_xml).startswith("OK"):
          rs.append(DIV(SPAN(btype+": ",_style="color:blue;font-weight: bold;"),SPAN(str(nom_xml),_style="color:brown;font-weight: bold;"),BR()))
        elif str(nom_xml).startswith("<?xml"):
          ndoc = parseString(nom_xml)
          rs.append(DIV(SPAN(btype+": ",_style="color:blue;font-weight: bold;"),
                        SPAN("OK|Backup "+str(len(ndoc.childNodes[0].childNodes))+" rows",_style="color:green;font-weight: bold;"),BR()))
          for row in ndoc.childNodes[0].childNodes:
            data.appendChild(row.cloneNode(True))
        else:
          rs.append(DIV(SPAN(btype+": ",_style="color:blue;font-weight: bold;"),SPAN(str(nom_xml),_style="color:red;font-weight: bold;"),BR()))
          err_no+=1
        return err_no
      
      def insertRow():
        xrow = doc.createElement(nom)
        for nom_field in nom_row.keys():
          if nom_field not in("delete_record","update_record","id") and type(nom_row[nom_field]).__name__!="LazySet":
            xfield = doc.createElement("field")
            xname = doc.createElement("name")
            if str(nom_field)=="employee_id":
              xname.appendChild(doc.createCDATASection("empnumber"))
            elif str(nom_field)=="ref_id":
              xname.appendChild(doc.createCDATASection("refnumber"))
            elif str(nom_field)=="groups_id" and nom=="ui_groupinput":
              xname.appendChild(doc.createCDATASection("usergroup"))
            elif str(nom_field)=="menu_id":
              xname.appendChild(doc.createCDATASection("menukey"))
            elif str(nom_field)=="report_id":
              xname.appendChild(doc.createCDATASection("reportkey"))
            else:
              xname.appendChild(doc.createCDATASection(str(nom_field)))
            xfield.appendChild(xname)
            xvalue = doc.createElement("value")
            if nom_row[nom_field]!=None:
              if ns.db[nom][str(nom_field)].represent:
                value = self.represent(ns.db[nom][str(nom_field)], nom_row[nom_field], nom_row,True)
                xvalue.appendChild(doc.createCDATASection(str(value)))
              else:
                xvalue.appendChild(doc.createCDATASection(str(nom_row[nom_field])))
            else:
              xvalue.appendChild(doc.createCDATASection(""))
            xfield.appendChild(xvalue)
            xrow.appendChild(xfield)
        data.appendChild(xrow)
      
      if btype=="customer":
        for nom in lst_nom:
          nom = str(nom).strip()
          nom_xml=""
          if nom=="address":
            join = [(ns.db.groups.on((ns.db.address.nervatype==ns.db.groups.id)))]
            ntypes = ns.db((ns.db.address.deleted==0)).select(*[ns.db.groups.groupvalue.with_alias('nervatype')],join=join,distinct=True)
            for ntype in ntypes:
              nom_xml = ndi.getView({"datatype":nom},{"output":"xml","nervatype":ntype.nervatype})
              err_no = insertDoc(nom+"-"+ntype.nervatype,err_no)
          elif nom=="contact":
            join = [(ns.db.groups.on((ns.db.contact.nervatype==ns.db.groups.id)))]
            ntypes = ns.db((ns.db.contact.deleted==0)).select(*[ns.db.groups.groupvalue.with_alias('nervatype')],join=join,distinct=True)
            for ntype in ntypes:
              nom_xml = ndi.getView({"datatype":nom},{"output":"xml","nervatype":ntype.nervatype})
              err_no = insertDoc(nom+"-"+ntype.nervatype,err_no)
          elif nom=="event":
            join = [(ns.db.groups.on((ns.db.event.nervatype==ns.db.groups.id)))]
            ntypes = ns.db((ns.db.event.deleted==0)).select(*[ns.db.groups.groupvalue.with_alias('nervatype')],join=join,distinct=True)
            for ntype in ntypes:
              nom_xml = ndi.getView({"datatype":nom},{"output":"xml","nervatype":ntype.nervatype})
              err_no = insertDoc(nom+"-"+ntype.nervatype,err_no)
          elif nom=="link":
            ngroups1 = ns.db.groups.with_alias('ngroups1')
            ngroups2 = ns.db.groups.with_alias('ngroups2')
            join = [(ngroups1.on((ns.db.link.nervatype_1==ngroups1.id))),
              (ngroups2.on((ns.db.link.nervatype_2==ngroups2.id)))]
            ntypes = ns.db((ns.db.link.deleted==0)).select(*[ngroups1.groupvalue.with_alias('nervatype1'),ngroups2.groupvalue.with_alias('nervatype2')],join=join,distinct=True)
            for ntype in ntypes:
              nom_xml = ndi.getView({"datatype":nom},{"output":"xml","nervatype1":ntype.nervatype1,"nervatype2":ntype.nervatype2})
              err_no = insertDoc(nom+"-"+ntype.nervatype1+":"+ntype.nervatype2,err_no)
          else:
            nom_xml = ndi.getView({"datatype":nom},{"output":"xml"})
            err_no = insertDoc(nom,err_no)
      else:
        for nom in lst_nom:
          nom = str(nom).strip()
          nom_rows = []
          _query,_join,_left = None,None,None
          fields = ns.db[nom].ALL
          nom_rows = ns.db(_query).select(fields,join=_join,left=_left, orderby=ns.db[nom].id, cacheable=True)
          for nom_row in nom_rows:
            insertRow()
          color="green" if len(nom_rows)>0 else "brown"
          rs.append(DIV(SPAN(nom+": ",_style="color:blue;font-weight: bold;"),
                          SPAN("OK|Backup "+str(len(nom_rows))+" rows",_style="color:"+color+";font-weight: bold;"),BR()))  
          
      if err_no>0:
        rs.append(DIV(SPAN("Result: ",_style="color:blue;font-weight: bold;"),
                    SPAN("Processing errors: "+str(err_no),_style="color:red;font-weight: bold;"),BR()))
      else:
        rs.append(DIV(SPAN("Result: ",_style="color:blue;font-weight: bold;"),
                    SPAN("The process has run without error!",_style="font-weight: bold;"),BR()))
      rs.append(DIV(SPAN("End process: ",_style="color:blue;font-weight: bold;"),
                  SPAN(str(datetime.datetime.now()),_style="font-weight: bold;"),BR()))
      
      doc_xml = doc.toxml(encoding='utf-8')
      if bformat=="backup":
        doc_xml = compress(doc_xml,9)
        
      if filename!="download":
        file_name = os.path.join(ns.request.folder, 'static/backup', filename+'.'+bformat)
        f = open(file_name, 'w')
        f.write(doc_xml)
        f.close()
        rs.insert(1,DIV(SPAN("Download file: ",_style="color:blue;font-weight: bold;"),
                  A(SPAN(_class="icon downarrow")," ",SPAN(filename+'.'+bformat, _style="font-weight: bold;"), 
                    _style="height: 20px;vertical-align: middle;", _class="w2p_trap buttontext button", 
                    _title= ns.T('Download file'), 
                    _href=URL( 'ndr', 'getResource', args=['file_name','file_type','content'], 
                               vars=dict(file_name='backup/'+filename,file_type=bformat,content="application/octet-stream")), 
                    _target="_blank"),BR(),BR()))
      else:
        rs = doc_xml
    
    except Exception, err:
      rs.append(P("Error: "+str(err),_style="color:red;font-weight: bold;"))
    finally:
      return rs
    
  def loadBackupData(self, ns, ndi, filename=None, bfile=None):
    rs = DIV()
    if filename==None and bfile==None:
      rs = DIV(SPAN(str("Error: "+str(ns.T("Missing parameters!"))),_style="color:red;font-weight: bold;"),BR())
      err_no=1
      return
    try:
      err_no=0
      rs.append(DIV(SPAN("Start process: ",_style="color:blue;font-weight: bold;"),
                 SPAN(str(datetime.datetime.now()),_style="font-weight: bold;")))
      if bfile==None:
        file_name = os.path.join(ns.request.folder, 'static/backup', filename)
        if not os.path.isfile(file_name):
          rs = DIV(SPAN(str("Error: "+str(ns.T("Missing file:"))+str(filename)),_style="color:red;font-weight: bold;"),BR())
          err_no=1
          return
        f = open(file_name, 'rb')
        doc_xml = f.read()
        f.close()
        if str(file_name).endswith(".backup"):
          doc_xml = decompress(doc_xml)
      else:
        if str(bfile.filename).endswith(".backup") or str(bfile.filename).endswith(".xml"):
          doc_xml = bfile.file.read()
          if str(bfile.filename).endswith("backup"):
            doc_xml = decompress(doc_xml)
        else:
          rs = DIV(SPAN("Error: "+str(ns.T("Valid filetype: backup or XML")),_style="color:red;font-weight: bold;"),BR())
          err_no=1
          return
      
      param={}
      param["insert_row"], param["insert_field"] = True, True  
      doc = parseString(doc_xml)
      btype = str(doc.childNodes[0].getAttribute("type"))
      if btype not in("customer","settings"):
        rs = DIV(SPAN("Error: "+str(ns.T("Invalid backup type!")),_style="color:red;font-weight: bold;"),BR())
        err_no=1
        return
      rs.append(DIV(SPAN("Backup type: ",_style="color:blue;font-weight: bold;"),SPAN(btype,_style="font-weight: bold;"),BR()))
      rs.append(DIV(SPAN("Backup time: ",_style="color:blue;font-weight: bold;"),SPAN(str(doc.childNodes[0].getAttribute("timestamp")),_style="font-weight: bold;"),BR()))
      rs.append(DIV(SPAN("Backup ver.No: ",_style="color:blue;font-weight: bold;"),SPAN(str(doc.childNodes[0].getAttribute("verno")),_style="font-weight: bold;"),BR(),BR()))
      
      def getRefId(table,refkey1,refnumber1,refkey2=None,refnumber2=None):
        if refnumber1=="": return None
        retval = -1
        if refkey2:
          refrows = ns.db((ns.db[table][refkey1]==refnumber1)&(ns.db[table][refkey2]==refnumber2)).select(ns.db[table].id)
        else:
          refrows = ns.db(ns.db[table][refkey1]==refnumber1).select(ns.db[table].id)
        if len(refrows)>0:
          retval = refrows[0].id
        return retval
        
      def loadNomItems():
        items=[]
        rows = doc.childNodes[0].getElementsByTagName(nom)
        for row in rows:
          item = OrderedDict()
          fields = row.getElementsByTagName("field")
          for field in fields:
            name = field.getElementsByTagName("name")[0].childNodes[0].data
            if len(field.getElementsByTagName("index"))>0:
              name += "~"+field.getElementsByTagName("index")[0].childNodes[0].data
            value =""
            if len(field.getElementsByTagName("value")[0].childNodes)>0:
              if field.getElementsByTagName("value")[0].childNodes[0].data != "None":
                value = field.getElementsByTagName("value")[0].childNodes[0].data
            if len(field.getElementsByTagName("data"))>0:
              if len(field.getElementsByTagName("data")[0].childNodes)>0:
                if field.getElementsByTagName("data")[0].childNodes[0].data != "None":
                  value += "~"+field.getElementsByTagName("data")[0].childNodes[0].data
            item[name] = value
            
          if btype=="settings":
            if item.has_key("subtype") and nom=="ui_audit":
              if item["nervatype"]=="trans" and item["subtype"]!="":
                if len(ns.db((ns.db.groups.groupname=="transtype")&(ns.db.groups.groupvalue==item["subtype"])).select())>0:
                  item["subtype"] = ns.db((ns.db.groups.groupname=="transtype")
                                          &(ns.db.groups.groupvalue==item["subtype"])).select()[0].id
              if item["nervatype"]=="report" and item["subtype"]!="":
                if ns.db.ui_report(reportkey=item["subtype"]):
                  item["subtype"] = ns.db.ui_report(reportkey=item["subtype"]).id
            
            for fname in item.keys():
              if item[fname]=="" and fname!="number_str":
                del item[fname]
              else:
                if fname=="usergroup" and nom=="ui_groupinput":
                  item["groups_id"] = value = getRefId("groups","groupname",fname,"groupvalue",item[fname])
                  del item["usergroup"]
                if fname=="empnumber":
                  item["employee_id"] = getRefId("employee",fname,item[fname])
                  del item["empnumber"]
                if fname=="menukey" and nom=="ui_menufields":
                  item["menu_id"] = getRefId("ui_menu",fname,item[fname])
                  del item["menukey"]
                if fname=="reportkey" and nom in("ui_printqueue","ui_reportfields","ui_reportsources"):
                  item["report_id"] = getRefId("ui_report",fname,item[fname])
                  del item["reportkey"]
                if fname in("usergroup","nervatype","inputfilter","nervatype","logstate","transtype","direction","filetype",
                           "fieldtype","wheretype","aggretype"):
                  item[fname] = getRefId("groups","groupname",fname,"groupvalue",item[fname])
          items.append(item)
        return items
      
      if btype=="customer":
        ndi.logState = False
        for nom in self.lst_nom:
          items = loadNomItems()
          nrs = ndi.callNdiFunc("update_"+nom, param, items)
          if str(nrs).startswith("OK"):
            rs.append(DIV(SPAN(nom+": ",_style="color:blue;font-weight: bold;"),SPAN(str(nrs),_style="color:green;font-weight: bold;"),BR()))
          else:
            rs.append(DIV(SPAN(nom+": ",_style="color:blue;font-weight: bold;"),SPAN(str(nrs),_style="color:red;font-weight: bold;"),BR()))
            err_no+=1
      else:
        for nom in reversed(self.lst_senom):
          ns.db[nom].truncate()
          rs.append(DIV(SPAN(nom+": ",_style="color:blue;font-weight: bold;"),SPAN("All previous data is deleted.",_style="color:brown;font-weight: bold;"),BR()))
        for nom in self.lst_senom:
          items = loadNomItems()
          if len(items)>0:
            ins_no=0
            for item in items:
              ret = ns.db[nom].validate_and_insert(**item)
              if ret.errors:
                rs.append(DIV(SPAN(nom+": ",_style="color:blue;font-weight: bold;"),SPAN(str(ret.errors.keys()[0]+"-> "+ret.errors.values()[0]),_style="color:red;font-weight: bold;"),BR()))
                err_no+=1
              else:
                ins_no+=1
            if ins_no>0:
              rs.append(DIV(SPAN(nom+": ",_style="color:blue;font-weight: bold;"),SPAN("All previous data is deleted. "+str(ins_no)+" rows restored",_style="color:green;font-weight: bold;"),BR()))
    except Exception, err:
      rs.append(P("Error: "+str(err),_style="color:red;font-weight: bold;"))
      err_no=1
    finally:
      if err_no>0:
        rs.append(P(SPAN("Result: ",_style="color:blue;font-weight: bold;"),
                    SPAN("Processing errors: "+str(err_no),_style="color:red;font-weight: bold;")))
      else:
        rs.append(P(SPAN("Result: ",_style="color:blue;font-weight: bold;"),
                    SPAN("The process has run without error!",_style="font-weight: bold;")))
      rs.append(P(SPAN("End process: ",_style="color:blue;font-weight: bold;"),
                  SPAN(str(datetime.datetime.now()),_style="font-weight: bold;")))
      return rs
  
  def createTempFile(self,output,suffix=".pdf",delete=False):
    import tempfile
    tfile = tempfile.NamedTemporaryFile(suffix=suffix, delete=delete)
    tfile.file.write(output)
    tfile.close()
    return tfile.name
  
  def printReport(self, printer_prop, report, title="Nervatura Report", copies=1, orientation="P", size="a4"):
    if printer_prop["method"]=="gcloud":
      for i in range(int(copies)):  # @UnusedVariable
        if not printer_prop["conn"].submitJob(printer_prop["printer_id"], title, report):
          return {"state":False, "error_message":printer_prop["conn"].error_message}
    
    elif printer_prop["method"]=="mail":
      try:
        tfilename = self.createTempFile(report)
        printer_prop["conn"].send(printer_prop["printer_mail_address"],
                                printer_prop["printer_mail_subject"],
                                printer_prop["printer_mail_message"],
                                attachments = printer_prop["conn"].Attachment(tfilename, content_type='application/pdf', 
                                                                              filename=title.replace(" ","_")))
      except Exception, err:
        return {"state":False, "error_message":str(err)}
    
    elif printer_prop["method"]=="cups":
      try:
        tfilename = self.createTempFile(report)
        landscape = "True" if orientation=="L" else "False"
        media = str(size).upper()
        for i in range(int(copies)):  # @UnusedVariable
          printer_prop["conn"].printFile(printer_prop["name"], filename=tfilename, title=title, options={"landscape":landscape,"media":media})
        os.remove(tfilename)
      except Exception, err:
        return {"state":False, "error_message":str(err)}
    
    elif printer_prop["method"]=="gsprint":  
      tfilename = self.createTempFile(report)
      arg = [printer_prop["gsprint"], tfilename]
      arg.insert(len(arg), '-printer')
      arg.insert(len(arg), printer_prop["name"])
      if orientation=="P":
        arg.insert(len(arg), '-portrait')
      else:
        arg.insert(len(arg), '-landscape')
      arg.insert(len(arg), '-option')
      arg.insert(len(arg), '-sPAPERSIZE='+str(size))
      for i in range(int(copies)):  # @UnusedVariable
        p = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()  # @UnusedVariable
        if stderr!="":
          return {"state":False, "error_message":stderr}
      os.remove(tfilename)
    return {"state":True, "error_message":None}
  
  def callPrintQueue(self, ns, params):
    retval = self.printQueue(ns, params["printer"], params["items"], params["orientation"], params["size"])
    retval["error_message"] = str(retval["error_message"])
    return retval
  
  def printQueue(self, ns, printer, items, orientation="P", size="a4"):
    retval = {"state":True, "error_message":None}
    printer_prop = self.check_printer(ns, printer)
    if printer_prop["state"]==False:
      return printer_prop
    for item_id in items:
      item = ns.db(ns.db.ui_printqueue.id==item_id).select()
      if len(item)>0:
        item = item[0]
        filters={"@id":item.ref_id}
        params={"report_id":item.report_id, "output":"pdf", "orientation":orientation, "size":size}
        report_tmp = self.getReport(ns, params, filters)
        if type(report_tmp).__name__=="str":
          return {"state":False, "error_message":report_tmp}
        else:
          title=ns.db.ui_report(id=item.report_id).repname
          print_item = self.printReport(printer_prop, report_tmp["template"], title, item.qty, orientation, size)
          if print_item["state"]==False:
            return print_item
        ns.db(ns.db.ui_printqueue.id==item_id).delete()
        ns.db.commit()
    return retval
  
  def check_printer(self, ns, printer):
    printer_prop = {"state":True, "error_message":None, "name":printer}
    printers = ns.db((ns.db.groups.groupname=="printer")&(ns.db.groups.groupvalue==printer)&(ns.db.groups.deleted==0)).select()
    if len(printers)==0:
      return {"state":False, "error_message":ns.T("Missing or unknown printer!")}
    else:
      printer_prop["group_id"] = printers[0]["id"]
      
    groups_nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="groups")).select().as_list()[0]["id"]
    printertype = ns.db((ns.db.link.ref_id_1==printers[0]["id"])&(ns.db.link.nervatype_1==groups_nervatype_id)
                  &(ns.db.link.nervatype_2==groups_nervatype_id)&(ns.db.link.deleted==0)).select().as_list()
    if len(printertype)>0:
      printer_prop["printertype"] = ns.db.groups(id=printertype[0]["ref_id_2"]).groupvalue
    else:
      printer_prop["printertype"] = "local"
    printer_prop["name"] = printer
    
    if printer_prop["printertype"]=="google_cloud":
      printer_login = ns.db((ns.db.fieldvalue.fieldname=="printer_login")&(ns.db.fieldvalue.ref_id==printer_prop["group_id"])
                            &(ns.db.fieldvalue.deleted==0)).select()
      if len(printer_login)==0:
        return {"state":False, "error_message":ns.T("Missing cloud login name!")}
      elif printer_login[0]["value"]=="" or printer_login[0]["value"]==None:
        return {"state":False, "error_message":ns.T("Missing cloud login name!")}
      else:
        printer_prop["printer_login"] = printer_login[0]["value"]
      
      printer_password = ns.db((ns.db.fieldvalue.fieldname=="printer_password")&(ns.db.fieldvalue.ref_id==printer_prop["group_id"])
                            &(ns.db.fieldvalue.deleted==0)).select()
      if len(printer_password)==0:
        return {"state":False, "error_message":ns.T("Missing cloud login password!")}
      elif printer_password[0]["value"]=="" or printer_password[0]["value"]==None:
        return {"state":False, "error_message":ns.T("Missing cloud login password!")}
      else:
        printer_prop["printer_password"] = ns.get_password_field("printer_password", printer_password[0]["value"])
      
      from gocloudprint import goCloudPrint
      
      gcloud = goCloudPrint(printer_prop["printer_login"], printer_prop["printer_password"])
      if not gcloud.auth:
        return {"state":False, "error_message":gcloud.error_message}
      if not gcloud.getPrinters():
        return {"state":False, "error_message":gcloud.error_message}
      for pid in gcloud.printers.keys():
        if pid==printer or gcloud.printers[pid]["name"]==printer:
          printer_prop["printer_id"] = pid
          printer_prop["method"] = "gcloud"
          printer_prop["conn"] = gcloud
          return printer_prop
      return {"state":False, "error_message":ns.T("Missing or unknown printer!")}
    
    elif printer_prop["printertype"]=="mail":
      printer_mail_smtp = ns.db((ns.db.fieldvalue.fieldname=="printer_mail_smtp")&(ns.db.fieldvalue.ref_id==printer_prop["group_id"])
                            &(ns.db.fieldvalue.deleted==0)).select()
      if len(printer_mail_smtp)==0:
        return {"state":False, "error_message":ns.T("Missing mail smtp server!")}
      elif printer_mail_smtp[0]["value"]=="" or printer_mail_smtp[0]["value"]==None:
        return {"state":False, "error_message":ns.T("Missing mail smtp server!")}
      else:
        printer_prop["printer_mail_smtp"] = printer_mail_smtp[0]["value"]
      
      printer_mail_sender = ns.db((ns.db.fieldvalue.fieldname=="printer_mail_sender")&(ns.db.fieldvalue.ref_id==printer_prop["group_id"])
                            &(ns.db.fieldvalue.deleted==0)).select()
      if len(printer_mail_sender)==0:
        return {"state":False, "error_message":ns.T("Missing mail sender address!")}
      elif printer_mail_sender[0]["value"]=="" or printer_mail_sender[0]["value"]==None:
        return {"state":False, "error_message":ns.T("Missing mail sender address!")}
      else:
        printer_prop["printer_mail_sender"] = printer_mail_sender[0]["value"]
        
      printer_mail_login = ns.db((ns.db.fieldvalue.fieldname=="printer_mail_login")&(ns.db.fieldvalue.ref_id==printer_prop["group_id"])
                            &(ns.db.fieldvalue.deleted==0)).select()
      if len(printer_mail_login)==0:
        return {"state":False, "error_message":ns.T("Missing mail login!")}
      elif printer_mail_login[0]["value"]=="" or printer_mail_login[0]["value"]==None:
        return {"state":False, "error_message":ns.T("Missing mail login!")}
      else:
        printer_prop["printer_mail_login"] = printer_mail_login[0]["value"]
        
      printer_mail_address = ns.db((ns.db.fieldvalue.fieldname=="printer_mail_address")&(ns.db.fieldvalue.ref_id==printer_prop["group_id"])
                            &(ns.db.fieldvalue.deleted==0)).select()
      if len(printer_mail_address)==0:
        return {"state":False, "error_message":ns.T("Missing printer mail address!")}
      elif printer_mail_address[0]["value"]=="" or printer_mail_address[0]["value"]==None:
        return {"state":False, "error_message":ns.T("Missing printer mail address!")}
      else:
        printer_prop["printer_mail_address"] = printer_mail_address[0]["value"]
        
      printer_prop["printer_mail_subject"] = ""
      printer_mail_subject = ns.db((ns.db.fieldvalue.fieldname=="printer_mail_subject")&(ns.db.fieldvalue.ref_id==printer_prop["group_id"])
                            &(ns.db.fieldvalue.deleted==0)).select()
      if len(printer_mail_subject)!=0:
        if printer_mail_subject[0]["value"]!="" or printer_mail_subject[0]["value"]!=None:
          printer_prop["printer_mail_subject"] = printer_mail_subject[0]["value"]
      
      printer_prop["printer_mail_message"] = ""
      printer_mail_message = ns.db((ns.db.fieldvalue.fieldname=="printer_mail_message")&(ns.db.fieldvalue.ref_id==printer_prop["group_id"])
                            &(ns.db.fieldvalue.deleted==0)).select()
      if len(printer_mail_message)!=0:
        if printer_mail_message[0]["value"]!="" or printer_mail_message[0]["value"]!=None:
          printer_prop["printer_mail_message"] = printer_mail_message[0]["value"]
          
      from gluon.tools import Mail
      mail = Mail()
      mail.settings.server = printer_prop["printer_mail_smtp"]
      mail.settings.sender = printer_prop["printer_mail_sender"]
      mail.settings.login = printer_prop["printer_mail_login"]
      
      printer_prop["method"] = "mail"
      printer_prop["conn"] = mail
      return printer_prop

    else:
      import platform
      system = platform.system()
      if system=="Linux":
        try:
          import cups #pycups support
          
          printer_server = ns.db((ns.db.fieldvalue.fieldname=="printer_server")&(ns.db.fieldvalue.ref_id==printer_prop["group_id"])
                            &(ns.db.fieldvalue.deleted==0)).select()
          if len(printer_server)!=0:
            if printer_server[0]["value"]!="" and printer_server[0]["value"]!=None:
              printer_prop["printer_server"] = printer_server[0]["value"]
              cups.setServer(printer_prop["printer_server"])
          
          printer_port = ns.db((ns.db.fieldvalue.fieldname=="printer_port")&(ns.db.fieldvalue.ref_id==printer_prop["group_id"])
                            &(ns.db.fieldvalue.deleted==0)).select()
          if len(printer_port)!=0:
            if printer_port[0]["value"]!="" and printer_port[0]["value"]!=None:
              printer_prop["printer_port"] = printer_port[0]["value"]
              cups.setPort(int(printer_prop["printer_port"]))
          
          printer_login = ns.db((ns.db.fieldvalue.fieldname=="printer_login")&(ns.db.fieldvalue.ref_id==printer_prop["group_id"])
                            &(ns.db.fieldvalue.deleted==0)).select()
          if len(printer_login)!=0:
            if printer_login[0]["value"]!="" or printer_login[0]["value"]!=None:
              printer_prop["printer_login"] = printer_login[0]["value"]
              cups.setUser(printer_prop["printer_login"])
                  
          conn = cups.Connection ()
          printers = conn.getPrinters ()
          if not dict(printers).has_key(printer):
            return {"state":False, "error_message":ns.T("Missing or unknown printer!")}
          printer_prop["method"] = "cups"
          printer_prop["conn"] = conn
        except:
          return {"state":False, "error_message":ns.T("Missing cups support")}
      
      elif system=="Windows":
        
        printer_gsprint = ns.db((ns.db.fieldvalue.fieldname=="printer_gsprint")&(ns.db.fieldvalue.ref_id==None)
                            &(ns.db.fieldvalue.deleted==0)).select()
        if len(printer_gsprint)!=0:
          if printer_gsprint[0]["value"]!="" and printer_gsprint[0]["value"]!=None:
            printer_prop["gsprint"] = printer_gsprint[0]["value"]
        if not printer_prop.has_key("gsprint"):
          return {"state":False, "error_message":ns.T("Missing gsprint path")}
              
        try:
          p = subprocess.Popen([printer_prop["gsprint"], '-printer', '?'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          stdout, stderr = p.communicate()  # @UnusedVariable
        except Exception, err:
          return {"state":False, "error_message":str(err)}
        if str(stderr).find("Available printers")>-1:
          if str(stderr).find(printer)==-1:
            return {"state":False, "error_message":ns.T("Missing or unknown printer!")}
        else:
          return {"state":False, "error_message":stderr}
        printer_prop["method"] = "gsprint"
        
      else:
        return {"state":False, "error_message":ns.T("Unsupported platform: "+system)}
    
    return printer_prop
  
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
  
  def formatNumber(self, value):
    try:
      return DIV(self.splitThousands(float(value)," ","."), _align="right", _width="100%")
    except Exception:
      pass
  def formatInteger(self, value):
    try:
      return DIV(self.splitThousands(int(value)," ","."), _align="right", _width="100%")
    except Exception:
      pass
  def formatDate(self, value):
    try:
      if type(value) is datetime.datetime:
        return DIV(value.date(), _align="center", _width="100%")
      elif type(value).__name__=="unicode":
        return DIV(datetime.datetime.strptime(str(value).split(" ")[0], str('%Y-%m-%d')).date(), _align="center", _width="100%")
      else:
        return value
    except Exception:
      pass
    