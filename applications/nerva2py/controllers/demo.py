# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Project
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

if 0:
  global request; request = globals.Request()
  global response; response = globals.Response()
  import gluon.languages.translator as T
  from gluon.sql import DAL
  global db; db = DAL()
  
from gluon.http import redirect 
from gluon.html import URL
from gluon.html import SPAN, DIV, P, BR
import datetime

from nerva2py.nervastore import NervaStore
from nerva2py.ndi import Ndi
from nerva2py.tools import NervaTools
from nerva2py.ordereddict import OrderedDict

#----------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------
#ndi server side sample
#call sample: .../nerva2py/demo/create_demo?database=demo&username=demo
#----------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------

ns = NervaStore(request, T, db)
ndi = Ndi(ns)
dbfu = NervaTools()

def create_demo():
#----------------------------------------------------------------------------------------------------
#insert/update a demo data and test ndi functions
#----------------------------------------------------------------------------------------------------
  param={}
  if request.vars.database:
    #set an existing database and insert data (or set to default value)
    param = {"database":request.vars.database}
    param["username"]=request.vars.username if request.vars.username else ""
    param["password"]=request.vars.password if request.vars.password else ""
    validator = ndi.getLogin(param)
    if validator["valid"]==False:
      return SPAN(validator["message"],_style="color:red;font-weight: bold;")
  else:
    return SPAN("Error|Missing database parameter",_style="color:red;font-weight: bold;")
  param["insert_row"] = True
  param["insert_field"] = True
  
  try:
    rs = DIV(P(SPAN("Database: ",_style="color:blue;font-weight: bold;"),
               SPAN(str(request.vars.database),_style="font-weight: bold;"), BR(),
               SPAN("Start process: ",_style="color:blue;font-weight: bold;"),
               SPAN(str(datetime.datetime.now()),_style="font-weight: bold;")))
  #----------------------------------------------------------------------------------------------------
    #groups: 
  #----------------------------------------------------------------------------------------------------
    #-> create 3 departments
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert group...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    groups=[{"groupname":"department","groupvalue":"sales","description":"Sample department"},
            {"groupname":"department","groupvalue":"logistics","description":"Sample department"},
            {"groupname":"department","groupvalue":"production","description":"Sample department"}]
    retvalue = ndi.update_groups(param,groups)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("groups"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("groups"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
      
  #----------------------------------------------------------------------------------------------------
    #customer: 
  #----------------------------------------------------------------------------------------------------
    #-> def. 4 customer additional data (float,date,valuelist,customer types), 
    #->create 3 customers, 
    #->and more create and link to contacts, addresses and events
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert customer data...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    deffield=[{"fieldname":"sample_customer_float","nervatype":"customer","fieldtype":"float","description":"Sample float","visible":1},
              {"fieldname":"sample_customer_date","nervatype":"customer","fieldtype":"date","description":"Sample date","visible":1},
              {"fieldname":"sample_customer_valuelist","nervatype":"customer","fieldtype":"valuelist","description":"Sample valuelist",
               "valuelist":"blue~yellow~white~brown~red","visible":1},
              {"fieldname":"sample_customer_reference","nervatype":"customer","fieldtype":"customer","description":"Sample customer","visible":1}]
    retvalue = ndi.update_deffield(param,deffield)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("deffield"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("deffield"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    customer=[{"custnumber":"DMCUST/00001","custtype":"company","custname":"First Customer Co.","taxnumber":"12345678-1-12","terms":8,
               "creditlimit":1000000,"discount":2,"sample_customer_float":123.4,"sample_customer_date":"2012-08-12"},
              {"custnumber":"DMCUST/00002","custtype":"private","custname":"Second Customer Name","taxnumber":"12121212-1-12","terms":1,
               "creditlimit":0,"discount":6,"sample_customer_float":56789.67,"sample_customer_date":"2012-09-01",
               "sample_customer_valuelist":"yellow","sample_customer_reference":"DMCUST/00001"},
              {"custnumber":"DMCUST/00003","custtype":"other","custname":"Third Customer Foundation","taxnumber":"10101010-1-01",
               "notax":1,"terms":4,"creditlimit":0,"sample_customer_valuelist":"brown"}]
    retvalue = ndi.update_customer(param,customer)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("customer"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("customer"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    address=[{"nervatype":"customer","refnumber":"DMCUST/00001","rownumber":1,"country":"Country1","state":"state01",
              "zipcode":"1234","city":"City1","street":"street 1.","notes":"address of registered office"},
             {"nervatype":"customer","refnumber":"DMCUST/00001","rownumber":2,"country":"Country1","state":"state02",
              "zipcode":"2345","city":"City2","street":"street 2.","notes":"postal address"},
             {"nervatype":"customer","refnumber":"DMCUST/00002","rownumber":1,"country":"Country1","state":"state03",
              "zipcode":"6789","city":"City3","street":"street 3."},
             {"nervatype":"customer","refnumber":"DMCUST/00003","rownumber":1,"country":"Country2","state":"state04",
              "zipcode":"6543","city":"City4","street":"street 4."}]
    retvalue = ndi.update_address(param,address)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("address"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("address"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    contact=[{"nervatype":"customer","refnumber":"DMCUST/00001","rownumber":1,"firstname":"Big","surname":"Man",
              "status":"manager","email":"man.big@company.co"},
             {"nervatype":"customer","refnumber":"DMCUST/00001","rownumber":2,"firstname":"Sales","surname":"Man",
              "status":"sales","email":"man.sales@company.co"},
             {"nervatype":"customer","refnumber":"DMCUST/00002","rownumber":1,"firstname":"Jack","surname":"Frost"},
             {"nervatype":"customer","refnumber":"DMCUST/00003","rownumber":1,"firstname":"Mother","surname":"Teresa"}]
    retvalue = ndi.update_contact(param,contact)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("contact"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("contact"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    deffield=[{"fieldname":"company_page","nervatype":"event","fieldtype":"flink","description":"Company page","visible":1}]
    retvalue = ndi.update_deffield(param,deffield)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("deffield"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("deffield"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
      
    event=[{"calnumber":"DMEVT/00001","nervatype":"customer","refnumber":"DMCUST/00001","eventgroup":"visit",
              "fromdate":"2012-04-05 08:00:00","todate":"2012-04-05 10:00:00","subject":"First visit",
              "place":"City1","description":"It was long ...  :-(","company_page":"http://nervatura.com/"},
             {"calnumber":"DMEVT/00002","nervatype":"customer","refnumber":"DMCUST/00001","eventgroup":"visit",
              "fromdate":"2012-04-06 08:00:00","todate":"2012-04-06 10:00:00","subject":"Second visit","place":"City1"},
             {"calnumber":"DMEVT/00003","nervatype":"customer","refnumber":"DMCUST/00002",
              "fromdate":"2012-04-07 08:00:00","todate":"2012-04-07 10:00:00","subject":"Training"},
             {"calnumber":"DMEVT/00004","nervatype":"customer","refnumber":"DMCUST/00003",
              "fromdate":"2012-04-08 08:00:00","subject":"Training"}]
    retvalue = ndi.update_event(param,event)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("event"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("event"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
  
  #----------------------------------------------------------------------------------------------------
    #employee: 
  #----------------------------------------------------------------------------------------------------
    #-> def. 1 employee additional data (integer type), 
    #->create 1 employee, 
    #->and more create and link to contact, address and event
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert employee data...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    deffield=[{"fieldname":"sample_employee_integer","nervatype":"employee","fieldtype":"integer","description":"Shoe size","visible":1}]
    retvalue = ndi.update_deffield(param,deffield)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("deffield"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("deffield"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    employee=[{"empnumber":"DMEMP/00001","usergroup":"guest","startdate":"2011-12-01","department":"production","sample_employee_integer":42}]
    retvalue = ndi.update_employee(param,employee)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("employee"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("employee"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    address=[{"nervatype":"employee","refnumber":"DMEMP/00001","rownumber":1,"country":"Country1",
              "zipcode":"1234","city":"City1","street":"Address 3. AB. 5.."}]
    retvalue = ndi.update_address(param,address)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("address"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("address"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR())) 
    
    contact=[{"nervatype":"employee","refnumber":"DMEMP/00001","rownumber":1,"firstname":"John","surname":"Strong",
              "status":"heaver","notes":"He's a good man ..."}]
    retvalue = ndi.update_contact(param,contact)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("contact"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("contact"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    event=[{"calnumber":"DMEVT/00005","nervatype":"employee","refnumber":"DMEMP/00001",
              "fromdate":"2012-12-15 00:00:00","todate":"2012-12-31 00:00:00","subject":"Holiday","place":"On the beach"}]
    retvalue = ndi.update_event(param,event)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("event"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("event"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
      
  #----------------------------------------------------------------------------------------------------
    #product:
  #----------------------------------------------------------------------------------------------------
    #-> def. 3 product additional data (product,integer and valulist types),
    #->create 13 products,
    #->and more create and link to barcodes, events, prices and discount, product groups, additional data
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert product data...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    deffield=[{"fieldname":"sample_product_reference","nervatype":"product","fieldtype":"product","description":"Sample product","visible":1},
              {"fieldname":"sample_product_integer","nervatype":"product","fieldtype":"integer","description":"Sample integer","visible":1},
              {"fieldname":"sample_product_valuelist","nervatype":"product","fieldtype":"valuelist","description":"Sample valuelist",
               "valuelist":"easy~heavy","visible":1}]
    retvalue = ndi.update_deffield(param,deffield)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("deffield"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("deffield"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    product=[{"partnumber":"DMPROD/00001","description":"Big product","protype":"item","unit":"piece","taxcode":"20%","webitem":1,
              "inactive":0,"sample_product_valuelist":"easy"},
             {"partnumber":"DMPROD/00002","description":"Good work","protype":"service","unit":"hour","taxcode":"20%","webitem":0,
              "inactive":0,"sample_product_reference":"DMPROD/00001","sample_product_integer":100000},
             {"partnumber":"DMPROD/00003","description":"Nice product","protype":"item","unit":"piece","taxcode":"20%","webitem":1,
              "inactive":0,"sample_product_valuelist":"heavy"},
             {"partnumber":"DMPROD/00004","description":"Car","protype":"item","unit":"piece","taxcode":"20%","webitem":1,
              "inactive":0,"notes":"Manufacturing products"},
             {"partnumber":"DMPROD/00005","description":"Wheel","protype":"item","unit":"piece","taxcode":"20%","webitem":1,
              "inactive":0,"notes":"Raw material, component"},
             {"partnumber":"DMPROD/00006","description":"Door","protype":"item","unit":"piece","taxcode":"20%","webitem":1,
              "inactive":0,"notes":"Raw material, component"},
             {"partnumber":"DMPROD/00007","description":"Paint","protype":"item","unit":"liter","taxcode":"20%","webitem":1,
              "inactive":0,"notes":"Raw material, component"},
             {"partnumber":"DMPROD/00008","description":"Pallet","protype":"item","unit":"piece","taxcode":"20%","webitem":1,
              "inactive":0,"notes":"Raw material, component (not share sample)"},
             {"partnumber":"DMPROD/00009","description":"Basket","protype":"item","unit":"piece","taxcode":"20%",
              "inactive":0,"notes":"Souvenir component"},
             {"partnumber":"DMPROD/00010","description":"Wine","protype":"item","unit":"piece","taxcode":"5%",
              "inactive":0,"notes":"Souvenir component"},
             {"partnumber":"DMPROD/00011","description":"Chocolate","protype":"item","unit":"piece","taxcode":"20%",
              "inactive":0,"notes":"Souvenir component"},
             OrderedDict([("partnumber", "DMPROD/00012"),("description", "Souvenir - virtual product"), 
                          ("protype", "item"),("unit", "piece"),("taxcode", "15%"),("inactive", 0),
                          ("notes", "A technical package, physically more real elements (or service)"),
                          ("product_element~1", "DMPROD/00009~1"),("product_element~2", "DMPROD/00010~1"),
                          ("product_element~3", "DMPROD/00011~2"),("product_element~4", "DMPROD/00002~1")]),
             {"partnumber":"DMPROD/00013","description":"Phone","protype":"item","unit":"piece","taxcode":"20%",
              "inactive":0,"notes":"for tool movement..."}]
    retvalue = ndi.update_product(param,product)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("product"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("product"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    barcode=[{"barcode":"BC0123456789","partnumber":"DMPROD/00001","barcodetype":"code128a","description":"Barcode1","defcode":1},
             {"barcode":"BC1212121212","partnumber":"DMPROD/00001","barcodetype":"code128b","description":"Barcode2","qty":5},
             {"barcode":"BC0101010101","partnumber":"DMPROD/00003","barcodetype":"code128c","description":"Barcode3","defcode":1}]
    retvalue = ndi.update_barcode(param,barcode)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("barcode"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("barcode"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    event=[{"calnumber":"DMEVT/00006","nervatype":"product","refnumber":"DMPROD/00001","eventgroup":"pricing",
            "fromdate":"2012-04-05 08:00:00","todate":"2012-04-05 15:00:00","subject":"New prices","place":"Office"},
           {"calnumber":"DMEVT/00007","nervatype":"product","refnumber":"DMPROD/00002","fromdate":"2012-04-08 08:00:00",
            "todate":"2012-04-12 18:00:00","subject":"business trip","place":"Hawaii"},
           {"calnumber":"DMEVT/00008","nervatype":"product","refnumber":"DMPROD/00002","fromdate":"2012-04-12 08:00:00",
            "subject":"Inventory","description":"Inventory in the warehouse"}]
    retvalue = ndi.update_event(param,event)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("event"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("event"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    price=[{"partnumber":"DMPROD/00001","pricetype":"price","validfrom":"2012-04-05","curr":"EUR","qty":0,"pricevalue":25},
           {"partnumber":"DMPROD/00001","pricetype":"price","validfrom":"2012-04-05","curr":"EUR","qty":10,"pricevalue":20},
           {"partnumber":"DMPROD/00001","pricetype":"discount","validfrom":"2012-04-12","validto":"2012-04-17","curr":"EUR",
            "discount":15,"calcmode":"ded"}]
    retvalue = ndi.update_price(param,price)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("price"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("price"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    groups=[{"groupname":"product","groupvalue":"big"},{"groupname":"product","groupvalue":"nice"},
            {"groupname":"product","groupvalue":"nice big"}]
    retvalue = ndi.update_groups(param,groups)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("groups"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("groups"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    link=[{"nervatype1":"product","refnumber1":"DMPROD/00001","nervatype2":"groups","refnumber2":"product~big"},
          {"nervatype1":"product","refnumber1":"DMPROD/00003","nervatype2":"groups","refnumber2":"product~nice"},
          {"nervatype1":"product","refnumber1":"DMPROD/00001","nervatype2":"groups","refnumber2":"product~nice big"},
          {"nervatype1":"product","refnumber1":"DMPROD/00003","nervatype2":"groups","refnumber2":"product~nice big"}]
    retvalue = ndi.update_link(param,link)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("link"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("link"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
  
  #----------------------------------------------------------------------------------------------------
    #project: 
  #----------------------------------------------------------------------------------------------------
    #-> def. 2 project additional data, 
    #->create 1 project, 
    #->and more create and link to contact, address and event
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert project data...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    deffield=[{"fieldname":"sample_project_state","nervatype":"project","fieldtype":"valuelist","description":"Status",
               "valuelist":"10%~20%~30%~40%~50%~60%~70%~80%~90%~100%","visible":1},
              {"fieldname":"sample_project_leader","nervatype":"project","fieldtype":"employee","description":"Coordinator","visible":1}]
    retvalue = ndi.update_deffield(param,deffield)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("deffield"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("deffield"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    project=[{"pronumber":"DMPRJ/00001","description":"Sample project","startdate":"2012-12-01","custnumber":"DMCUST/00001",
              "sample_project_state":"20%","sample_project_leader":"DMEMP/00001"}]
    retvalue = ndi.update_project(param,project)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("project"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("project"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    address=[{"nervatype":"project","refnumber":"DMPRJ/00001","rownumber":1,"country":"Country1",
              "zipcode":"1234","city":"City1","street":"Address 3. AB. 5.."}]
    retvalue = ndi.update_address(param,address)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("address"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("address"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR())) 
    
    contact=[{"nervatype":"project","refnumber":"DMPRJ/00001","rownumber":1,"firstname":"Big","surname":"Man"}]
    retvalue = ndi.update_contact(param,contact)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("contact"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("contact"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    event=[{"calnumber":"DMEVT/00009","nervatype":"project","refnumber":"DMPRJ/00001",
              "fromdate":"2012-12-10 09:00:00","todate":"2012-12-10 11:00:00","subject":"Project meeting","place":"Office"}]
    retvalue = ndi.update_event(param,event)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("event"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("event"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
  
  #----------------------------------------------------------------------------------------------------
    #tool:
  #----------------------------------------------------------------------------------------------------
    #-> def. 2 tool additional data,
    #->create 3 tools,
    #->and more create and link to event and additional data
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert tool data...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    deffield=[{"fieldname":"sample_tool_vin","nervatype":"tool","fieldtype":"string","description":"Vehicle id.No.","visible":1},
              {"fieldname":"sample_tool_color","nervatype":"tool","fieldtype":"valuelist","description":"Car colors",
               "valuelist":"blue~yellow~white~brown~red","visible":1}]
    retvalue = ndi.update_deffield(param,deffield)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("deffield"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("deffield"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    tool=[{"serial":"ABC-123","description":"Company car 1.", "partnumber":"DMPROD/00004","sample_tool_vin":"VIN12345678","sample_tool_color":"red"},
          {"serial":"DEF-456","description":"Company car 2.", "partnumber":"DMPROD/00004","sample_tool_vin":"VIN87654321","sample_tool_color":"blue"},
          {"serial":"IMEI-023456789","description":"NOKIA E5", "partnumber":"DMPROD/00013"}]
    retvalue = ndi.update_tool(param,tool)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("tool"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("tool"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    event=[{"calnumber":"DMEVT/00010","nervatype":"tool","refnumber":"ABC-123","eventgroup":"car",
            "fromdate":"2012-04-05 08:00:00","todate":"2012-04-05 15:00:00","subject":"Technical inspection","place":"Service"}]
    retvalue = ndi.update_event(param,event)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("event"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("event"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
        
  #----------------------------------------------------------------------------------------------------
    #place:
  #----------------------------------------------------------------------------------------------------
    #->create +1 warehouse
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert place...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    place=[{"planumber":"material","placetype":"warehouse","description":"Raw material"}]
    retvalue = ndi.update_place(param,place)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("place"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("place"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
    
  #----------------------------------------------------------------------------------------------------
    #documents:
  #----------------------------------------------------------------------------------------------------
    #->create 1 tool movement (for employee)
    #->and more create and link to movements
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert tool movement (employee)...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    trans=[{"transnumber":"DMMOVE/00001","transtype":"waybill","direction":"out","transdate":"2012-12-05",
            "empnumber":"DMEMP/00001","notes":"We will give you some of the work tool to the employee..."}]
    retvalue = ndi.update_trans(param,trans)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    movement=[{"transnumber":"DMMOVE/00001","rownumber":1,"movetype":"tool","shippingdate":"2012-12-05 00:00:00", "serial":"DEF-456"},
              {"transnumber":"DMMOVE/00001","rownumber":2,"movetype":"tool","shippingdate":"2012-12-05 00:00:00", "serial":"IMEI-023456789",
               "notes":"mobil phone"}]
    retvalue = ndi.update_movement(param,movement)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("movement"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("movement"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
    
    #----------------------------------------------------------------------------------------------------
    #->create 3 order (customer and vendor),
    #->and more create and link to items
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert order (vendor and customer)...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    trans=[{"transnumber":"DMORD/00001","transtype":"order","direction":"in","transdate":"2012-11-01",
            "duedate":"2012-11-10 00:00:00","custnumber":"DMCUST/00003","paidtype":"transfer","curr":"EUR",
            "department":"logistics",
            "notes":"We buy some of the basic material for the production and sale. Billed on the basis of delivery, but not all were shipped."},
           {"transnumber":"DMORD/00002","transtype":"order","direction":"out","transdate":"2012-12-04",
            "duedate":"2012-12-10 00:00:00","custnumber":"DMCUST/00002","paidtype":"transfer","curr":"EUR",
            "department":"sales","notes":"Virtual product sample."},
           {"transnumber":"DMORD/00003","transtype":"order","direction":"out","transdate":"2012-12-10",
            "duedate":"2012-12-20 00:00:00","custnumber":"DMCUST/00001","paidtype":"transfer","curr":"EUR",
            "department":"sales","notes":"DEMO invoice order."}]
    retvalue = ndi.update_trans(param,trans)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    item=[{"transnumber":"DMORD/00001","rownumber":1,"partnumber":"DMPROD/00005",
           "qty":40,"inputmode":"fxprice","inputvalue":10},
          {"transnumber":"DMORD/00001","rownumber":2,"partnumber":"DMPROD/00006",
           "qty":60,"inputmode":"fxprice","inputvalue":12},
          {"transnumber":"DMORD/00001","rownumber":3,"partnumber":"DMPROD/00007",
           "qty":50,"inputmode":"fxprice","inputvalue":16},
          {"transnumber":"DMORD/00001","rownumber":4,"partnumber":"DMPROD/00008",
           "qty":20,"inputmode":"fxprice","inputvalue":5},
          {"transnumber":"DMORD/00001","rownumber":5,"partnumber":"DMPROD/00001",
           "qty":10,"inputmode":"fxprice","inputvalue":120},
          {"transnumber":"DMORD/00001","rownumber":6,"partnumber":"DMPROD/00003",
           "qty":10,"inputmode":"fxprice","inputvalue":15},
          {"transnumber":"DMORD/00001","rownumber":7,"partnumber":"DMPROD/00009",
           "qty":20,"inputmode":"fxprice","inputvalue":8},
          {"transnumber":"DMORD/00001","rownumber":8,"partnumber":"DMPROD/00010",
           "qty":20,"inputmode":"fxprice","inputvalue":20},
          {"transnumber":"DMORD/00001","rownumber":9,"partnumber":"DMPROD/00011",
           "qty":20,"inputmode":"fxprice","inputvalue":16},
          {"transnumber":"DMORD/00002","rownumber":1,"partnumber":"DMPROD/00012",
           "qty":2,"inputmode":"fxprice","inputvalue":60},
          {"transnumber":"DMORD/00002","rownumber":2,"partnumber":"DMPROD/00001",
           "qty":3,"inputmode":"fxprice","inputvalue":25},
          {"transnumber":"DMORD/00003","rownumber":1,"partnumber":"DMPROD/00002","description":"Very good work!",
           "qty":1,"inputmode":"fxprice","inputvalue":120},
          {"transnumber":"DMORD/00003","rownumber":2,"partnumber":"DMPROD/00001",
           "qty":3,"inputmode":"amount","inputvalue":600},
          {"transnumber":"DMORD/00003","rownumber":3,"partnumber":"DMPROD/00003","taxcode":"5%",
           "qty":5,"inputmode":"netamount","inputvalue":100}]
    retvalue = ndi.update_item(param,item)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("item"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("item"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
    
    #----------------------------------------------------------------------------------------------------
    #->create delivery
    #->and more create and link to movements
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert delivery (in and out)...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    trans=[{"transnumber":"DMDEL/00001","transtype":"delivery","direction":"in","transdate":"2012-11-08"},
           {"transnumber":"DMDEL/00002","transtype":"delivery","direction":"out","transdate":"2012-12-10"},
           {"transnumber":"DMDEL/00003","transtype":"delivery","direction":"out","transdate":"2012-12-10"}]
    retvalue = ndi.update_trans(param,trans)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    movement=[{"transnumber":"DMDEL/00001","rownumber":1,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
               "planumber":"material","partnumber":"DMPROD/00005","qty":30,"notes":"demo"},
          {"transnumber":"DMDEL/00001","rownumber":2,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00006","qty":50,"notes":"demo"},
          {"transnumber":"DMDEL/00001","rownumber":3,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00007","qty":50,"notes":"demo"},
          {"transnumber":"DMDEL/00001","rownumber":4,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00008","qty":15,"notes":"demo"},
          {"transnumber":"DMDEL/00001","rownumber":5,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00001","qty":10,"notes":"demo"},
          {"transnumber":"DMDEL/00001","rownumber":6,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00003","qty":10,"notes":"demo"},
          {"transnumber":"DMDEL/00001","rownumber":7,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00009","qty":15,"notes":"demo"},
          {"transnumber":"DMDEL/00001","rownumber":8,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00010","qty":10,"notes":"demo"},
          {"transnumber":"DMDEL/00001","rownumber":9,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00011","qty":20,"notes":"demo"},
          {"transnumber":"DMDEL/00002","rownumber":1,"movetype":"inventory","shippingdate":"2012-12-10 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00009","qty":-2,"notes":"demo"},
          {"transnumber":"DMDEL/00002","rownumber":2,"movetype":"inventory","shippingdate":"2012-12-10 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00010","qty":-2,"notes":"demo"},
          {"transnumber":"DMDEL/00002","rownumber":3,"movetype":"inventory","shippingdate":"2012-12-10 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00011","qty":-4,"notes":"demo"},
          {"transnumber":"DMDEL/00002","rownumber":4,"movetype":"inventory","shippingdate":"2012-12-10 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00001","qty":-3,"notes":"demo"},
          {"transnumber":"DMDEL/00003","rownumber":1,"movetype":"inventory","shippingdate":"2012-12-10 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00001","qty":-3,"notes":"demo"},
          {"transnumber":"DMDEL/00003","rownumber":2,"movetype":"inventory","shippingdate":"2012-12-10 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00003","qty":-5,"notes":"demo"}]
    retvalue = ndi.update_movement(param,movement)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("movement"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("movement"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    link=[{"nervatype1":"movement","refnumber1":"DMDEL/00001~1","nervatype2":"item","refnumber2":"DMORD/00001~1"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00001~2","nervatype2":"item","refnumber2":"DMORD/00001~2"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00001~3","nervatype2":"item","refnumber2":"DMORD/00001~3"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00001~4","nervatype2":"item","refnumber2":"DMORD/00001~4"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00001~5","nervatype2":"item","refnumber2":"DMORD/00001~5"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00001~6","nervatype2":"item","refnumber2":"DMORD/00001~6"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00001~7","nervatype2":"item","refnumber2":"DMORD/00001~7"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00001~8","nervatype2":"item","refnumber2":"DMORD/00001~8"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00001~9","nervatype2":"item","refnumber2":"DMORD/00001~9"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00002~1","nervatype2":"item","refnumber2":"DMORD/00002~1"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00002~2","nervatype2":"item","refnumber2":"DMORD/00002~1"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00002~3","nervatype2":"item","refnumber2":"DMORD/00002~1"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00002~4","nervatype2":"item","refnumber2":"DMORD/00002~2"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00003~1","nervatype2":"item","refnumber2":"DMORD/00003~2"},
          {"nervatype1":"movement","refnumber1":"DMDEL/00003~2","nervatype2":"item","refnumber2":"DMORD/00003~3"}]
    retvalue = ndi.update_link(param,link)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("link"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("link"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
    
    #----------------------------------------------------------------------------------------------------
    #->create stock transfer
    #->and more create and link to movements
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert stock transfer...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    trans=[{"transnumber":"DMDTF/00001","transtype":"delivery","direction":"transfer","transdate":"2012-11-08","planumber":"material"}]
    retvalue = ndi.update_trans(param,trans)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    movement=[{"transnumber":"DMDTF/00001","rownumber":1,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00001","qty":-10,"notes":"demo"},
          {"transnumber":"DMDTF/00001","rownumber":2,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00001","qty":10,"notes":"demo"},
          {"transnumber":"DMDTF/00001","rownumber":3,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00003","qty":-10,"notes":"demo"},
          {"transnumber":"DMDTF/00001","rownumber":4,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00003","qty":10,"notes":"demo"},
          {"transnumber":"DMDTF/00001","rownumber":5,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00009","qty":-15,"notes":"demo"},
          {"transnumber":"DMDTF/00001","rownumber":6,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00009","qty":15,"notes":"demo"},
          {"transnumber":"DMDTF/00001","rownumber":7,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00010","qty":-10,"notes":"demo"},
          {"transnumber":"DMDTF/00001","rownumber":8,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00010","qty":10,"notes":"demo"},
          {"transnumber":"DMDTF/00001","rownumber":9,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"material","partnumber":"DMPROD/00011","qty":-20,"notes":"demo"},
          {"transnumber":"DMDTF/00001","rownumber":10,"movetype":"inventory","shippingdate":"2012-11-08 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00011","qty":20,"notes":"demo"}]
    retvalue = ndi.update_movement(param,movement)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("movement"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("movement"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    link=[{"nervatype1":"movement","refnumber1":"DMDTF/00001~1","nervatype2":"movement","refnumber2":"DMDTF/00001~2"},
          {"nervatype1":"movement","refnumber1":"DMDTF/00001~3","nervatype2":"movement","refnumber2":"DMDTF/00001~4"},
          {"nervatype1":"movement","refnumber1":"DMDTF/00001~5","nervatype2":"movement","refnumber2":"DMDTF/00001~6"},
          {"nervatype1":"movement","refnumber1":"DMDTF/00001~7","nervatype2":"movement","refnumber2":"DMDTF/00001~8"},
          {"nervatype1":"movement","refnumber1":"DMDTF/00001~9","nervatype2":"movement","refnumber2":"DMDTF/00001~10"}]
    retvalue = ndi.update_link(param,link)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("link"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("link"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
    
    #----------------------------------------------------------------------------------------------------
    #->create correction
    #->and more create and link to movements
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert stock correction...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    trans=[{"transnumber":"DMCORR/00001","transtype":"inventory","direction":"transfer","transdate":"2012-12-01",
            "planumber":"warehouse","notes":"Disposing of some bad product ..."}]
    retvalue = ndi.update_trans(param,trans)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    movement=[{"transnumber":"DMCORR/00001","rownumber":1,"movetype":"inventory","shippingdate":"2012-12-01 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00001","qty":-2,"notes":"demo"},
          {"transnumber":"DMCORR/00001","rownumber":2,"movetype":"inventory","shippingdate":"2012-12-01 00:00:00",
           "planumber":"warehouse","partnumber":"DMPROD/00010","qty":-3,"notes":"demo"}]
    retvalue = ndi.update_movement(param,movement)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("movement"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("movement"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
              
    #----------------------------------------------------------------------------------------------------
    #->create 1 offer,
    #->and more create and link to items
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert offer (customer)...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    trans=[{"transnumber":"DMOFF/00001","transtype":"offer","direction":"out","transdate":"2012-11-05",
            "duedate":"2012-11-30 00:00:00","custnumber":"DMCUST/00001","paidtype":"transfer","curr":"EUR","department":"sales",
            "ref_transnumber":"DMORD/00003","notes":"DEMO invoice offer"}]
    retvalue = ndi.update_trans(param,trans)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    item=[{"transnumber":"DMOFF/00001","rownumber":1,"partnumber":"DMPROD/00002","description":"Very good work!",
           "qty":1,"inputmode":"fxprice","inputvalue":120},
          {"transnumber":"DMOFF/00001","rownumber":2,"partnumber":"DMPROD/00001",
           "qty":3,"inputmode":"amount","inputvalue":600},
          {"transnumber":"DMOFF/00001","rownumber":3,"partnumber":"DMPROD/00003","taxcode":"5%",
           "qty":5,"inputmode":"netamount","inputvalue":100}]
    retvalue = ndi.update_item(param,item)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("item"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("item"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    link=[{"nervatype1":"trans","refnumber1":"DMOFF/00001","nervatype2":"trans","refnumber2":"DMORD/00003"}]
    retvalue = ndi.update_link(param,link)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("link"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("link"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
                
    #----------------------------------------------------------------------------------------------------
    #->create 3 invoice (vendor and customer),
    #->and more create and link to items
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert invoice (vendor and customer)...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    trans=[{"transnumber":"DMINV/00001","transtype":"invoice","direction":"out","transdate":"2012-12-10",
            "duedate":"2012-12-20 00:00:00","custnumber":"DMCUST/00001","paidtype":"transfer","curr":"EUR","department":"sales",
            "ref_transnumber":"DMORD/00003","fnote":"A long and <b><i>rich text</b></i> at the bottom of the invoice...<br><br>Can be multiple lines ..."},
           {"transnumber":"DMINV/00002","transtype":"invoice","direction":"out","transdate":"2012-12-10",
            "duedate":"2013-01-10 00:00:00","custnumber":"DMCUST/00002","paidtype":"transfer","curr":"EUR","department":"sales",
            "ref_transnumber":"DMORD/00002","notes":"Virtual product sample."},
           {"transnumber":"DMINV/00003","transtype":"invoice","direction":"in","transdate":"2012-11-10",
            "duedate":"2012-12-20 00:00:00","custnumber":"DMCUST/00003","paidtype":"transfer","curr":"EUR","department":"logistics",
            "ref_transnumber":"DMORD/00001","notes":"We buy some of the basic material for the production and sale. Billed on the basis of delivery, but not all were shipped."}]
    retvalue = ndi.update_trans(param,trans)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    item=[{"transnumber":"DMINV/00001","rownumber":1,"partnumber":"DMPROD/00002","description":"Very good work!",
           "qty":1,"inputmode":"fxprice","inputvalue":120},
          {"transnumber":"DMINV/00001","rownumber":2,"partnumber":"DMPROD/00001",
           "qty":3,"inputmode":"amount","inputvalue":600},
          {"transnumber":"DMINV/00001","rownumber":3,"partnumber":"DMPROD/00003","taxcode":"5%",
           "qty":5,"inputmode":"netamount","inputvalue":100},
          {"transnumber":"DMINV/00002","rownumber":1,"partnumber":"DMPROD/00012",
           "qty":2,"inputmode":"fxprice","inputvalue":60},
          {"transnumber":"DMINV/00002","rownumber":2,"partnumber":"DMPROD/00001",
           "qty":3,"inputmode":"fxprice","inputvalue":25},
          {"transnumber":"DMINV/00003","rownumber":1,"partnumber":"DMPROD/00005",
           "qty":30,"inputmode":"fxprice","inputvalue":10},
          {"transnumber":"DMINV/00003","rownumber":2,"partnumber":"DMPROD/00006",
           "qty":50,"inputmode":"fxprice","inputvalue":12},
          {"transnumber":"DMINV/00003","rownumber":3,"partnumber":"DMPROD/00007",
           "qty":50,"inputmode":"fxprice","inputvalue":16},
          {"transnumber":"DMINV/00003","rownumber":4,"partnumber":"DMPROD/00008",
           "qty":15,"inputmode":"fxprice","inputvalue":5},
          {"transnumber":"DMINV/00003","rownumber":5,"partnumber":"DMPROD/00001",
           "qty":10,"inputmode":"fxprice","inputvalue":120},
          {"transnumber":"DMINV/00003","rownumber":6,"partnumber":"DMPROD/00003",
           "qty":10,"inputmode":"fxprice","inputvalue":15},
          {"transnumber":"DMINV/00003","rownumber":7,"partnumber":"DMPROD/00009",
           "qty":15,"inputmode":"fxprice","inputvalue":8},
          {"transnumber":"DMINV/00003","rownumber":8,"partnumber":"DMPROD/00010",
           "qty":10,"inputmode":"fxprice","inputvalue":20},
          {"transnumber":"DMINV/00003","rownumber":9,"partnumber":"DMPROD/00011",
           "qty":20,"inputmode":"fxprice","inputvalue":16}]
    retvalue = ndi.update_item(param,item)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("item"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("item"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    link=[{"nervatype1":"trans","refnumber1":"DMINV/00001","nervatype2":"trans","refnumber2":"DMORD/00003"},
          {"nervatype1":"trans","refnumber1":"DMINV/00002","nervatype2":"trans","refnumber2":"DMORD/00002"},
          {"nervatype1":"trans","refnumber1":"DMINV/00003","nervatype2":"trans","refnumber2":"DMORD/00001"}]
    retvalue = ndi.update_link(param,link)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("link"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("link"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
    
    #----------------------------------------------------------------------------------------------------
    #->create 2 payments (bank and cash),
    #->and more create and link to payments
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert payment (bank and cash)...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    trans=[{"transnumber":"DMPMT/00001","transtype":"bank","direction":"transfer","transdate":"2013-01-15","planumber":"bank",
            "ref_transnumber":"BM0123456"},
           {"transnumber":"DMPMT/00002","transtype":"cash","direction":"out","transdate":"2012-12-18","planumber":"cash"}]
    retvalue = ndi.update_trans(param,trans)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    payment=[{"transnumber":"DMPMT/00001","rownumber":1,"paiddate":"2012-12-20","amount":-4000,"notes":"payment two divided..."},
             {"transnumber":"DMPMT/00001","rownumber":2,"paiddate":"2012-12-20","amount":849},
             {"transnumber":"DMPMT/00001","rownumber":3,"paiddate":"2013-01-10","amount":228},
             {"transnumber":"DMPMT/00002","rownumber":1,"paiddate":"2012-12-18","amount":-488}]
    retvalue = ndi.update_payment(param,payment)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("payment"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("payment"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    link=[{"nervatype1":"payment","refnumber1":"DMPMT/00001~1","nervatype2":"trans","refnumber2":"DMINV/00003",
           "link_qty":4000,"link_rate":1},
          {"nervatype1":"payment","refnumber1":"DMPMT/00001~2","nervatype2":"trans","refnumber2":"DMINV/00001",
           "link_qty":849,"link_rate":1},
          {"nervatype1":"payment","refnumber1":"DMPMT/00001~3","nervatype2":"trans","refnumber2":"DMINV/00002",
           "link_qty":228,"link_rate":1},
          {"nervatype1":"payment","refnumber1":"DMPMT/00002~1","nervatype2":"trans","refnumber2":"DMINV/00003",
           "link_qty":488,"link_rate":1}]
    retvalue = ndi.update_link(param,link)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("link"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("link"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
            
    #----------------------------------------------------------------------------------------------------
    #->create 2 formula and 1 production
    #->and more create and link to movements
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert formula and production",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    trans=[{"transnumber":"DMFRM/00001","transtype":"formula","direction":"transfer","notes":"Sample formula (4 door/car)"},
           {"transnumber":"DMFRM/00002","transtype":"formula","direction":"transfer","notes":"Sample formula (3 door/car)"},
           {"transnumber":"DMMAKE/00001","transtype":"production","direction":"transfer","transdate":"2012-12-01",
            "duedate":"2012-12-02 00:00:00","planumber":"warehouse","notes":"formula: 4 door/car"}]
    retvalue = ndi.update_trans(param,trans)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    movement=[{"transnumber":"DMFRM/00001","rownumber":1,"movetype":"head","partnumber":"DMPROD/00004","qty":5,"shared":0},
              {"transnumber":"DMFRM/00001","rownumber":2,"movetype":"plan","partnumber":"DMPROD/00005",
               "qty":20,"shared":0,"planumber":"material"},
              {"transnumber":"DMFRM/00001","rownumber":3,"movetype":"plan","partnumber":"DMPROD/00006",
               "qty":20,"shared":0,"planumber":"material"},
              {"transnumber":"DMFRM/00001","rownumber":4,"movetype":"plan","partnumber":"DMPROD/00007",
               "qty":30,"shared":0,"planumber":"material"},
              {"transnumber":"DMFRM/00001","rownumber":5,"movetype":"plan","partnumber":"DMPROD/00008",
               "qty":1,"shared":1,"planumber":"material"},
              {"transnumber":"DMFRM/00002","rownumber":1,"movetype":"head","partnumber":"DMPROD/00004","qty":5,"shared":0},
              {"transnumber":"DMFRM/00002","rownumber":2,"movetype":"plan","partnumber":"DMPROD/00005",
               "qty":20,"shared":0,"planumber":"material"},
              {"transnumber":"DMFRM/00002","rownumber":3,"movetype":"plan","partnumber":"DMPROD/00006",
               "qty":15,"shared":0},
              {"transnumber":"DMFRM/00002","rownumber":4,"movetype":"plan","partnumber":"DMPROD/00007",
               "qty":28,"shared":0,"planumber":"material"},
              {"transnumber":"DMFRM/00002","rownumber":5,"movetype":"plan","partnumber":"DMPROD/00008",
               "qty":1,"shared":1,"planumber":"material","notes":"demo"},
              {"transnumber":"DMMAKE/00001","rownumber":1,"movetype":"inventory","partnumber":"DMPROD/00004",
               "shippingdate":"2012-12-02 00:00:00","qty":2,"shared":1,"planumber":"warehouse","notes":"demo"},
              {"transnumber":"DMMAKE/00001","rownumber":2,"movetype":"inventory","partnumber":"DMPROD/00005",
               "shippingdate":"2012-12-01 00:00:00","qty":-8,"shared":0,"planumber":"material","notes":"demo"},
              {"transnumber":"DMMAKE/00001","rownumber":3,"movetype":"inventory","partnumber":"DMPROD/00006",
               "shippingdate":"2012-12-01 00:00:00","qty":-8,"shared":0,"planumber":"material","notes":"demo"},
              {"transnumber":"DMMAKE/00001","rownumber":4,"movetype":"inventory","partnumber":"DMPROD/00007",
               "shippingdate":"2012-12-01 00:00:00","qty":-12,"shared":0,"planumber":"material","notes":"demo"},
              {"transnumber":"DMMAKE/00001","rownumber":5,"movetype":"inventory","partnumber":"DMPROD/00008",
               "shippingdate":"2012-12-01 00:00:00","qty":-1,"shared":0,"planumber":"material","notes":"demo"}]
    retvalue = ndi.update_movement(param,movement)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("movement"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("movement"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
      
  #----------------------------------------------------------------------------------------------------
    #->create 1 worksheet,
    #->and more create and link to items
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert worksheet...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    trans=[{"transnumber":"DMWORK/00001","transtype":"worksheet","direction":"out","transdate":"2013-01-05",
            "duedate":"2013-01-05 00:00:00","custnumber":"DMCUST/00001","paidtype":"transfer","curr":"EUR","department":"sales",
            "empnumber":"DMEMP/00001","trans_wsdistance":200,"trans_wstotal":3}]
    retvalue = ndi.update_trans(param,trans)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    item=[{"transnumber":"DMWORK/00001","rownumber":1,"partnumber":"DMPROD/00002",
           "qty":2,"inputmode":"fxprice","inputvalue":130}]
    retvalue = ndi.update_item(param,item)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("item"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("item"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
  
  #----------------------------------------------------------------------------------------------------
    #->create 1 rent (customer),
    #->and more create and link to items
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert worksheet...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    trans=[{"transnumber":"DMRNT/00001","transtype":"rent","direction":"out","transdate":"2013-01-01",
            "duedate":"2013-01-11 00:00:00","custnumber":"DMCUST/00001","paidtype":"transfer","curr":"EUR","department":"logistics",
            "trans_reholiday":3}]
    retvalue = ndi.update_trans(param,trans)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("trans"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR()))
    
    item=[{"transnumber":"DMRNT/00001","rownumber":1,"partnumber":"DMPROD/00008",
           "qty":3,"fxprice":12,"netamount":396,"taxcode":"20%","vatamount":79.2,"amount":475.2}]
    retvalue = ndi.update_item(param,item)
    if retvalue.startswith("Error"):
      return rs.append(DIV(SPAN("item"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:red;font-weight: bold;"),BR()))
    else:
      rs.append(DIV(SPAN("item"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(str(retvalue),_style="color:green;font-weight: bold;"),BR(),BR()))
          
  #----------------------------------------------------------------------------------------------------
    #sample reports:
  #----------------------------------------------------------------------------------------------------
    #load 3 general reports and 4 other templates
    #----------------------------------------------------------------------------------------------------
    rs.append(DIV(SPAN("insert report...",_style="color:brown;font-weight: bold;font-style: italic;"),BR()))
    def set_def_report(key,value):
      if not ns.db.deffield(fieldname=key):
        fkey = key.split("_")
        nervatype_id = ns.db((ns.db.groups.groupname=="nervatype")&(ns.db.groups.groupvalue=="setting")).select().as_list()[0]["id"]
        if len(fkey)==4:
          description = "default "+fkey[1]+" "+fkey[2]+" report"
        else:
          description = "default "+fkey[1]+" report"
        fieldtype_id = ns.db((ns.db.groups.groupname=="fieldtype")&(ns.db.groups.groupvalue=="string")).select().as_list()[0]["id"]
        ns.db.deffield.insert(**{"fieldname":key,"nervatype":nervatype_id,"fieldtype":fieldtype_id,
                                 "description":description})
      if ns.db.fieldvalue(fieldname=key):
        ns.db(ns.db.fieldvalue.fieldname==key).update(**{"value":value})
      else:
        ns.db.fieldvalue.insert(**{"fieldname":key,"value":value})
    reports = {"fpdf_customer_sheet_en":"default_customer_report",
               "fpdf_employee_sheet_en":"default_employee_report",
               "fpdf_invoice_en":"default_trans_invoice_report",
               "fpdf_vat_en":None,
               "gshi_vat_en":None,
               "html_vat":None,
               "xls_vat_en":None}
    for report in reports.keys():
      load = dbfu.loadReport(ns=ns, fileName=report+".sql", fileStr=None, insert=(not ns.db.ui_report(reportkey=report)))
      if load != "OK":
        rs.append(DIV(SPAN("report"+": ",_style="color:blue;font-weight: bold;"),
                    SPAN(load,_style="color:red;font-weight: bold;"),BR()))
      else:
        if reports[report]:
          #set defaut report
          set_def_report(reports[report],report)
        rs.append(DIV(SPAN("report"+": ",_style="color:blue;font-weight: bold;"),
                      SPAN("OK|"+report,_style="color:green;font-weight: bold;"),BR()))
  
    rs.append(P(SPAN("End process: ",_style="color:blue;font-weight: bold;"),
                SPAN(str(datetime.datetime.now()),_style="font-weight: bold;")))
  except Exception, err:
    rs.append(P("Error: "+str(err),_style="color:red;font-weight: bold;"))
  finally:
    return rs

def get_demo_report():
  param={}
  if request.vars.database:
    param = {"database":request.vars.database}
    param["username"]=request.vars.username if request.vars.username else ""
    param["password"]=request.vars.password if request.vars.password else ""
    validator = ndi.getLogin(param)
    if validator["valid"]==False:
      return validator["message"]
    if param["password"]==None:
      param["password"]=""
  else:
    return "Error|Missing database parameter!"
  if request.vars.reportcode:
    param["reportcode"] = request.vars.reportcode
  else:
    return "Error|Missing reportcode!"
  if param["reportcode"]=="fpdf_customer_sheet_en":
    customer = ndi.ns.db.customer(custnumber="DMCUST/00001")
    if customer:
      param["filters"] = "@id="+str(customer.id)
    else:
      return "Error|Missing customer No.: DMCUST/00001"
  elif param["reportcode"]=="fpdf_invoice_en":
    trans = ndi.ns.db.trans(transnumber="DMINV/00001")
    if trans:
      param["filters"] = "@id="+str(trans.id)
    else:
      return "Error|Missing invoice No.: DMINV/00001"
  elif param["reportcode"]=="fpdf_employee_sheet_en":
    employee = ndi.ns.db.employee(empnumber="DMEMP/00001")
    if employee:
      param["filters"] = "@id="+str(employee.id)
    else:
      return "Error|Missing employee No.: DMEMP/00001"
  elif param["reportcode"] in("html_vat","gshi_vat_en","fpdf_vat_en","xls_vat_en"):
    param["filters"] = "date_from=2012-01-01|date_to=2012-12-31"
  else:
    return "Error|Unknown reportcode!"
  if request.vars.output:
    param["output"] = request.vars.output
  else:
    param["output"] = "html"
  redirect(URL( 'ndr', 'exportToReport', args=['database','username','password','reportcode','filters','output'], vars=param))