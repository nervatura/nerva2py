# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

if 0:
  global response; response = globals.Response()
  global request; request = globals.Request()
  
from nerva2py.report import Report
from gluon.fileutils import read_file
import os
  
def index():
  response.view="report2py/index.html"
  response.title = "Nervatura Report Help & Demo"
  response.subtitle = "CLASS VERSION: "+Report().CLASS_VERSION
  return dict()
  
def report_test():
  
  filename = os.path.join(request.folder, 'static/resources/report', 'sample.xml')
  xdata = read_file(filename)
  
  customer=[{"custnumber":"CUST/12345678","custname":"Customer Name","custtype":"Company","taxnumber":"12345678-1-12",
             "account":"12345678-12345678-12345678","notax":"No","terms":0,"creditlimit":0,"discount":0,"inactive":"No",
             "notes":"This is a long text to test the multi-line writing ...This is a long text to test the multi-line writing ...\
             This is a long text to test the multi-line writing ...This is a long text to test the multi-line writing ..."}]
  address=[]
  for i in range(1, 40):
    address.append({"zipcode":"1234","city":"City"+str(i),"street":"Street"+str(i),"notes":"Comment..."})
  contact=[]
  for i in range(1, 10):
    contact.append({"firstname":"Firstname"+str(i), "surname":"Surname"+str(i), "status":" ", "phone":"1234567", "fax":"1234567", 
                    "mobil":"1234567", "email":"contact"+str(i)+"@mail.com", "notes":"Comment..."})
  labels={"title":"CUSTOMER DATASHEET","custnumber":"Customer No.","custname":"Name","custtype":"Customer type","taxnumber":"Taxnumber",
          "notax":"Tax free","terms":"Due Date (day)","creditlimit":"Credit limit","discount":"Discount(%)",
          "inactive":"Inactive","account":"Account","notes":"Notes","address":"Address details",
          "zipcode":"Zipcode","city":"City","street":"Street","notes":"Notes","counter":"No.","address_count":"Number of addresses",
          "contact":"Contact details", "firstname":"Firstname", "surname":"Surname", "status":"Status", "phone":"Phone",
          "fax":"Fax", "mobil":"Mobil", "email":"Email", "contact_count":"Number of contacts"}
  expr={"addr_count":len(address), "cont_count":len(contact)}
  
  if request.vars.orientation=="landscape":
    rpt = Report(orientation='L')
  else:
    rpt = Report(orientation='P')
  if request.vars.output in("html","xml"):
    rpt.images_folder = request.env.wsgi_url_scheme+"://"+request.env.http_host+"/"+request.application+"/static/images"
  else:
    rpt.images_folder = os.path.join(request.folder, 'static', 'images')
  rpt.databind["labels"]=labels
  rpt.databind["customer"]=customer
  rpt.databind["address"]=address
  rpt.databind["contact"]=contact
  rpt.databind["expr"]=expr
  #rpt.databind["images"]=images
  rpt.loadDefinition(xdata)
  rpt.createReport()
  
  if request.vars.output=="xml":
    response.headers['Content-Type']='text/xml'
    return rpt.save2Xml()
  elif request.vars.output=="html":
    return rpt.save2Html()
  else:
    response.headers['Content-Type']='application/pdf'  
    return rpt.save2Pdf()

