# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Project
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

from gluon.contrib.fpdf.fpdf import FPDF #@UnresolvedImport
import xml.etree.ElementTree as et
from nerva2py.fpdf_html import HTMLMixin

class Report(FPDF, HTMLMixin):
  
  CLASS_VERSION='0.8'
  favicon = "/nerva2py/static/favicon.ico"
  report_style={}
  header_elements = None
  header_html = ""
  header_xml=""
  footer_elements = None
  footer_html = ""
  details_elements = None
  details_html = ""
  details_xml=""
  databind = {}
  images_folder=None
  footer_start = None
  def_row_height = 7
  
  def __init__(self,orientation='P',unit='mm',page='A4'):
    self.orientation=orientation
    self.unit=unit
    FPDF.__init__(self,orientation,unit,page)
    self.decode = "utf-8"
    self.encode = "latin_1"
    self.report_style["font-family"]="times"
    self.report_style["font-style"]=""
    self.report_style["font-size"]="12"
    self.report_style["color"]="0"
    self.report_style["border-color"]="0"
    self.report_style["background-color"]="0"
    self.set_style(self.report_style)
    self.alias_nb_pages('{{pages}}')
    
  def header(self):
    if self.header_elements!=None:
      ehtml=""
      for element in self.header_elements:
        ehtml+=self.show_element("header",element)
      if self.page_no()==1:
        self.header_html=ehtml.replace("{{pages}}", "1")
  
  def footer(self):
    if self.footer_elements!=None:
      ehtml=""
      if self.page_no()==1:
        if self.y < self.page_break_trigger-5:
          self.set_y(self.page_break_trigger-5)
        self.footer_start = self.get_y()
      elif self.footer_start!=self.get_y():
        self.set_y(self.footer_start)
      for element in self.footer_elements:
        ehtml+=self.show_element("footer",element)
      if self.page_no()==1:
        self.footer_html=ehtml.replace("{{pages}}", "1")
    
  def show_element(self, section, element):
    if element.tag =="row":
      return self.create_row(section,element)
    elif element.tag =="vgap":
      height = element.get("height","")
      if height!="":
        height=float(height)
      self.ln(h=height)
      return '<div style="height:'+str(height)+self.unit+';">&nbsp;</div>'
    elif element.tag =="hline":
      width = element.get("width",0)
      if width!="":
        width=float(width)
      if width==0:
        style="width:100%;"
      else:
        style='width:'+str(width)+self.unit+';'
      gap = element.get("gap",0)
      if gap!="":
        gap=float(gap)
      if element.get("border-color",None)!=None:
        style+="border-color:"+hex(int(element.get("border-color",0))).replace("0x","#").upper()+" !important;"
        self.set_draw_color(*self.rgb(int(element.get("border-color",0))))
      else:
        self.set_draw_color(*self.rgb(int(self.report_style["border-color"])))
      self.cell(w=width, h=gap, txt="", border="TB", ln=1)
      return '<hr style="'+style+'margin:3px;"/>'
    elif element.tag =="html":
      html = et.tostring(element, encoding="utf-8")
      html = html.replace("<html>","").replace("</html>","")
      fieldname=element.get("fieldname","head")
      html = self.setHtmlValue(html,fieldname)
      x = self.get_x()
      self.set_style(element.attrib)
      font = element.get("font-family",self.report_style["font-family"])
      fontsize=int(element.get("font-size",self.report_style["font-size"]))
      self.write_html(html.decode(self.decode).encode(self.encode,'replace'),font=font,fontsize=fontsize)
      self.set_x(x)
      self.ln()
      return html
    elif element.tag =="datagrid":
      datagrid = self.create_datagrid(element)
      x = self.get_x()
      self.ln(-self.lasth-3)
      font = element.get("font-family",self.report_style["font-family"])
      fontsize=int(element.get("font-size",self.report_style["font-size"]))
      self.write_html(datagrid.decode(self.decode).encode(self.encode,'replace'),font=font,fontsize=fontsize)
      self.ln(-self.lasth)
      self.set_x(x)
      return datagrid
    return ""
  
  def rgb(self,col):
    return (col // 65536), (col // 256 % 256), (col% 256)
  
  def set_style(self,attr):
    style=""
    if attr.has_key("font-style"):
      if str(attr["font-style"]).find("B")>-1:
        style+="font-weight:bold;"
      if str(attr["font-style"]).find("I")>-1:
        style+="font-style:italic;"
      if str(attr["font-style"]).find("U")>-1:
        style+="text-decoration:underline;"
    if attr.has_key("font-family"):
      family=attr["font-family"]
      style+="font-family:"+attr["font-family"]+";"
    else:
      style+="font-family:"+self.report_style["font-family"]+";"
      family=self.report_style["font-family"]
    if attr.has_key("font-style"):
      fstyle=attr["font-style"]
    else:
      fstyle=self.report_style["font-style"]
    self.set_font(family=family, style=fstyle)  
    if attr.has_key("font-size"):
      style+="font-size:"+str(attr["font-size"])+"px;"
      self.set_font_size(int(attr["font-size"]))
    else:
      style+="font-size:"+str(self.report_style["font-size"])+"px;"
      self.set_font_size(int(self.report_style["font-size"]))
    if attr.has_key("color"):
      style+="color:"+hex(int(attr["color"])).replace("0x","#").upper()+";"
      self.set_text_color(*self.rgb(int(attr["color"])))
    else:
      style+="color:"+hex(int(self.report_style["color"])).replace("0x","#").upper()+";"
      self.set_text_color(*self.rgb(int(self.report_style["color"])))
    if attr.has_key("border-color"):
      style+="border-color:"+hex(int(attr["border-color"])).replace("0x","#").upper()+" !important;"
      self.set_draw_color(*self.rgb(int(attr["border-color"])))
    else:
      style+="border-color:"+hex(int(self.report_style["border-color"])).replace("0x","#").upper()+" !important;"
      self.set_draw_color(*self.rgb(int(self.report_style["border-color"])))
    if attr.has_key("background-color"):
      style+="background-color:"+hex(int(attr["background-color"])).replace("0x","#").upper()+";"
      self.set_fill_color(*self.rgb(int(attr["background-color"])))
    else:
      style+="background-color:"+hex(int(self.report_style["background-color"])).replace("0x","#").upper()+";"
      self.set_fill_color(*self.rgb(int(self.report_style["background-color"])))
    return style
  
  def setValue(self,value):
    if str(value).find("{{page}}")>-1:
      value = str(value).replace("{{page}}", str(self.page_no()))
    if str(value).find("={{")>-1 and str(value).find("}}")>-1:
      _value = value[str(value).find("={{")+3:str(value).find("}}")]
      dbv = str(_value).split(".")
      if self.databind.has_key(dbv[0]):
        if type(self.databind[dbv[0]]).__name__=="list":
          try:
            return value.replace("={{"+_value+"}}", str(self.databind[dbv[0]][int(dbv[1])][dbv[2]]))
          except Exception:
            return value
        elif type(self.databind[dbv[0]]).__name__=="dict":
          try:
            return value.replace("={{"+_value+"}}", str(self.databind[dbv[0]][dbv[1]]))
          except Exception:
            return value
        elif self.databind[dbv[0]]!=None:
          return value.replace("={{"+_value+"}}", str(self.databind[dbv[0]]))
        else:
          return value
      else:
        return value
    else:
      return value
  
  def setHtmlValue(self,html,fieldname):
    start_index=str(html).find("={{")
    if start_index>-1:
      value_old = html[start_index:str(html).find("}}",start_index)+2]
      value_new = self.setValue(value_old)
      html = str(html).replace(value_old, value_new)
      self.details_xml += "\n      <"+str(fieldname)+"><![CDATA["+str(value_new)+"]]></"+str(fieldname)+">"
      if str(html).find("={{")>-1:
        return self.setHtmlValue(html,fieldname)
      else:
        return html
    else:
      return html
  
  def get_datagrid_col_align(self,col):
    align = col.get("align","L")
    if str(align).find("L")>-1:
      align="left"
    elif str(align).find("R")>-1:
      align="right"
    elif str(align).find("C")>-1:
      align="center"
    elif str(align).find("J")>-1:
      align="justify"
    return align
  
  def set_datagrid_col_number_format(self,col,value):
    digit = col.get("digit","")
    if digit!="":
      try:
        value = str("{0:."+digit+"f}").format(float(value))
      except Exception:
        pass
    thousands = col.get("thousands","")
    if thousands!="":
      value = self.splitThousands(value,thousands)
    return value
              
  def create_datagrid(self,grid_element):
    databind = grid_element.get("databind","")
    xname = grid_element.get("name","items")
    header=columns=None
    for element in grid_element:
      if element.tag =="header":
        header = element
      elif element.tag =="columns":
        columns = element
    border = grid_element.get("border","1")
    if border=="1":
      border_sty="border:2px solid;"
    else:
      border_sty="border:none;"
    dgwidth = grid_element.get("width","100%")
    fontsize = grid_element.get("font-size",self.report_style["font-size"])
    style = self.set_style(grid_element.attrib)
    style+=border_sty
    style='style="padding:1px;font-size:'+fontsize+';border-collapse: separate !important;'+style+'"'
    dgrid = '<table '+style+' border="'+border+'" width="'+dgwidth+'" cellpadding="0" cellspacing="0">'
    if header!=None:
      bgcolor = header.get("background-color","")
      if bgcolor!="":
        bgcolor=' bgcolor="'+hex(int(bgcolor)).replace("0x","#").upper()+'"'
    else:
      bgcolor=""
    dfoot='<tfoot><tr '+bgcolor+'>'
    dgrid+='<thead><tr '+bgcolor+'>'
    self.details_xml += "\n    <"+str(xname)+"_footer"+">"
    style = style.replace("border:2px", "border:1px").replace("padding:1px", "padding:4px")
    for col in columns:
      width = col.get("width","")
      label = self.setValue(col.get("label",""))
      if width=="":
        width=str(int(100/len(columns)))+"%"
      dgrid+='<th '+style+' width="'+width+'">'+label+'</th>'
      footer = self.setValue(col.get("footer",""))
      footer = self.set_datagrid_col_number_format(col,footer)
      dfoot+='<td '+style+' align="'+self.get_datagrid_col_align(col)+'">'+footer+'</td>'
      fieldname = col.get("fieldname","")
      self.details_xml += "\n      <"+str(fieldname)+"><![CDATA["+str(footer)+"]]></"+str(fieldname)+">"
    self.details_xml += "\n    </"+str(xname)+"_footer"+">"
    dfoot+="</tr></tfoot>"
    dgrid+="</tr></thead>"
    dgrid+="<tbody>"    
    if self.databind.has_key(databind) and columns!=None:
      rows = self.databind[databind]
      for rn in range(len(rows)):
        rheight = self.get_row_height(rows[rn], columns)
        row="<tr>"
        self.details_xml += "\n    <"+str(xname)+">"
        for col in columns:
          fieldname = col.get("fieldname","")
          if fieldname=="counter":
            value=str(rn+1)
          elif rows[rn].has_key(fieldname):
            if rows[rn][fieldname]!=None and rows[rn][fieldname]!="":
              value=str(rows[rn][fieldname])
            else:
              value="&nbsp; "
          else:
            value="&nbsp; "
          value = self.set_datagrid_col_number_format(col,value)
          row+='<td height="'+str(int(rheight["mrh"]))+'" multiline="'+rheight["rh"][fieldname]+'" '+style+' align="'+self.get_datagrid_col_align(col)+'">'+value+'</td>'
          self.details_xml += "\n      <"+str(fieldname)+"><![CDATA["+str(value)+"]]></"+str(fieldname)+">"
        dgrid+=row+"</tr>"
        self.details_xml += "\n    </"+str(xname)+">"
    dgrid+="</tbody>"+dfoot+'</table>'
    return dgrid
  
  def get_row_height(self, row,columns):
    retval = {"mrh":1, "rh":{}}
    for col in columns:
      fieldname = col.get("fieldname","")
      col_width = col.get("width","0")
      if col_width=="0":
        col_width=str(int(100/len(columns)))+"%"
      if col_width[-1]=='%':
        total = self.w - self.r_margin - self.l_margin
        col_width = float(col_width[:-1]) * total / 100
      else:
        col_width = col_width.replace(col_width.rstrip('0123456789'),"")
        col_width = float(col_width)
      if fieldname=="counter":
        rh=1
      else:
        rh = len(self.multi_cell(col_width,(self.font_size*1.50),str(row[fieldname]),0,'L',0,True))
      if rh>1:
        retval["rh"][fieldname]="multi"
        if retval["mrh"]<rh:
          retval["mrh"]=rh
      else:
        retval["rh"][fieldname]="single"
    return retval
  
  def handle_data(self, txt):
    pass
  
  def create_row(self,section,row_element):
    hrow = '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: separate !important;"><tr>'
    hgap = float(row_element.get("hgap",0))
    height = float(row_element.get("height",self.def_row_height))
    if height!=self.def_row_height:
      height=float(height)
    for ei in range(len(row_element)):
      style = self.set_style(row_element[ei].attrib)
      if height>0:
        style+="height:"+str(height)+self.unit+";"
      if row_element[ei].tag =="cell":
        value = self.setValue(row_element[ei].get("value",""))
        
        width = row_element[ei].get("width","0")
        if width[-1]=='%':
          style+="width:"+width+";"
          total = self.w - self.r_margin - self.l_margin
          width = float(width[:-1]) * total / 100
        else:
          width = float(width)
          if len(row_element)-1>ei and width==0:
            width = self.get_string_width(str(value))+4
          if width>0:
            style+="width:"+str(width)+self.unit+";"
        
        border = row_element[ei].get("border","0")
        if border=="0":
          border=0
          style+="border:none;"
        if border=="1":
          border=1
          style+="border:2px solid;"
        if str(border).find("L")>-1:
          style+="border-left:solid;"
        if str(border).find("R")>-1:
          style+="border-right:solid;"
        if str(border).find("B")>-1:
          style+="border-bottom:solid;"
        if str(border).find("T")>-1:
          style+="border-top:solid;"
        
        align = row_element[ei].get("align","L")
        if str(align).find("L")>-1:
          style+="text-align:left;"
        elif str(align).find("R")>-1:
          style+="text-align:right;"
        elif str(align).find("C")>-1:
          style+="text-align:center;"
        elif str(align).find("J")>-1:
          style+="text-align:justify;"
        
        if row_element[ei].get("background-color",None)!=None:
          fill=1
        else:
          fill=0 
        link = row_element[ei].get("link","")
        multiline = row_element[ei].get("multiline","false")
        if multiline=="true":
          self.multi_cell(w=width, h=height, txt=str(value).decode(self.decode).encode(self.encode,'replace'), border=border, align=align, fill=fill)
        else:
          if len(row_element)-1==ei:
            ln=1
          else:
            ln=0
          self.cell(w=width, h=height, txt=str(value).decode(self.decode).encode(self.encode,'replace'), border=border, ln=ln, align=align, fill=fill, link=link)
        style+="padding:2px;"
        if value=="":
          value="&nbsp;"
        if link!="":
          hrow+='<td style="'+style+'"><a href="'+link+'">'+str(value)+'</a></td>'
        else:
          hrow+='<td style="'+style+'">'+str(value)+'</td>'
        xname = row_element[ei].get("name","head")
        if section=="header" and xname!="label":
          self.header_xml += "\n    <"+str(xname)+"><![CDATA["+str(value)+"]]></"+str(xname)+">"
        if section=="details" and xname!="label":
          self.details_xml += "\n    <"+str(xname)+"><![CDATA["+str(value)+"]]></"+str(xname)+">"
      if row_element[ei].tag =="image":
        width = float(row_element[ei].get("width",0))
        if width>0:
          style+="width:"+str(width)+self.unit+";"
        name = self.setValue(row_element[ei].get("file",""))
        if name.find("/")==-1 and self.images_folder:
          name = self.images_folder+'/'+name
        link = row_element[ei].get("link","")
        if name!="":
          import os
          if os.path.isfile(name):
            self.image(name=name, x=self.get_x()+0.5, y=self.get_y()+0.5, w=width, link=link)
            self.set_x(self.get_x()+(self.images[name]['w']/self.k)+0.5)
          if link!="":
            hrow+='<td width="1'+self.unit+'"><a href="'+link+'"><img style="'+style+'" src="'+name+'"/></a></td>'
          else:
            hrow+='<td width="1 '+self.unit+'"><img style="'+style+'" src="'+name+'"/></td>'
      if row_element[ei].tag =="separator":
        gap = row_element[ei].get("gap",0)
        if gap!="":
          gap=float(gap)
        if len(row_element)-1==ei:
          ln=1
        else:
          ln=0
        if gap>0:
          width=gap
          border="LR"
        elif ei==0:
          width=1
          border="L"
        else:
          width=1
          border="R"
        self.cell(w=width, h=height, txt="", border=border, ln=ln)
      if row_element[ei].tag =="hgap":
        width = row_element[ei].get("width",0)
        if width!=0:
          width=float(width)
        if len(row_element)-1==ei:
          ln=1
        else:
          ln=0
        self.cell(w=width, txt="", border=0, ln=0)
        hrow+='<td style="width:'+str(width)+self.unit+';"> </td>'
      if len(row_element)-1>ei and hgap>0:
        self.cell(w=hgap, txt="", border=0, ln=0)
        hrow+='<td style="width:'+str(hgap)+self.unit+';"> </td>'
    hrow+='</tr></table>'
    return hrow
  
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
  
#public functions
  def loadDefinition(self,data):
    if data!="" or data!=None:
      repdef = et.XML(data)
      if len(repdef.getiterator("report"))>0:
        report_attr = repdef.getiterator("report")[0]
        self.set_author(report_attr.get("autor",""))
        self.set_creator(report_attr.get("creator",""))
        self.set_subject(report_attr.get("subject",""))
        self.set_title(report_attr.get("title",""))
        self.set_left_margin(int(report_attr.get("left-margin",12)))
        self.set_right_margin(int(report_attr.get("right-margin",12)))
        self.set_top_margin(int(report_attr.get("top-margin",6)))
        self.decode = report_attr.get("decode","utf-8")
        self.encode = report_attr.get("encode","latin_1")
        
        self.report_style["font-family"]=report_attr.get("font-family","times")
        self.report_style["font-style"]=report_attr.get("font-style","")
        self.report_style["font-size"]=report_attr.get("font-size","12")
        self.report_style["color"]=report_attr.get("color","0")
        self.report_style["border-color"]=report_attr.get("border-color","0")
        self.report_style["background-color"]=report_attr.get("background-color","0")
        self.set_style(self.report_style)
          
      if len(repdef.getiterator("header"))>0:
        self.header_elements = repdef.getiterator("header")[0]
        self.header_show = self.header_elements.get("show_in","all")
      if len(repdef.getiterator("footer"))>0:
        self.footer_elements = repdef.getiterator("footer")[0]
        self.footer_show = self.footer_elements.get("show_in","all")
      if len(repdef.getiterator("details"))>0:
        self.details_elements = repdef.getiterator("details")[0]
  
  def createReport(self):
    self.details_html=""
    self.add_page()
    if self.details_elements!=None:
      for element in self.details_elements:
        self.details_html+=self.show_element("details",element)
                    
  def save2PdfFile(self,path):
    return self.output(name=path,dest='F')
  
  def save2Pdf(self):
    return self.output(dest='S')
  
  def save2Html(self,details=False):
    style=""
    if self.orientation=="P":
      style+='width:'+str(self.fw)+self.unit+';'
    else:
      style+='width:'+str(self.fh)+self.unit+';'
    style+='word-wrap: break-word; overflow: auto;background-color:#FFFFFF;'
    style+='padding-left:'+str(self.l_margin)+self.unit+';padding-top:'+str(self.t_margin)+self.unit+';padding-right:'+str(self.r_margin)+self.unit+';'
    ohtml = '<html style="background-color:#CCCCCC;"><head><title>'+self.title+'</title><link rel="shortcut icon" href="'+self.favicon+'" type="image/x-icon"></head><body style="'+style+'">'
    if details==False:
      ohtml +=self.header_html
    ohtml +=self.details_html
    if details==False:
      ohtml +=self.footer_html
    ohtml +='<div style="height:'+str(self.t_margin)+self.unit+'"/></body></html>'
    return ohtml
  
  def save2Xml(self):
    return "<data>"+self.header_xml+self.details_xml+"\n</data>"