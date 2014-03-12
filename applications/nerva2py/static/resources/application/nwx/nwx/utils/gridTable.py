# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import wx.grid
import datetime

class fieldTable(wx.grid.PyGridTableBase):
  def __init__(self, id=[], colLabels={}, data=[]):
    wx.grid.PyGridTableBase.__init__(self)
    self.identifiers = id
    rowLabels=[]
    for rowid in range(len(data)):
      rowLabels.append(str(rowid+1))
    self.rowLabels = rowLabels 
    self.colLabels = colLabels 
    self.data = data
  
  def GetNumberRows(self):
    return len(self.data)

  def GetNumberCols(self):
    return len(self.identifiers)

  def IsEmptyCell(self, row, col):
    id = self.identifiers[col]
    return not getattr(self.data[row], id) 
  
  def GetValue(self, row, col):
    id = self.identifiers[col]
    if getattr(self.data[row], id)==None:
      return ""
    if id=="value":
      ftype = getattr(self.data[row], "fieldtype")
      if ftype=="bool":
        if getattr(self.data[row], id)=="t" or getattr(self.data[row], id)=="true" or getattr(self.data[row], id)=="True":
          return 1
        else:
          return ""
      elif ftype=="integer" or ftype=="float":
        return getattr(self.data[row], id)
      elif ftype in("customer","tool","trans","transitem","transmovement","transpayment","product","project","employee","place"):
        return getattr(self.data[row], "valuelist")
      elif ftype=="notes":
        if len(getattr(self.data[row], id))>20:
          return getattr(self.data[row], id)[:20]+"..."
      else:
        return getattr(self.data[row], id)
    return getattr(self.data[row], id)

  def SetValue(self, row, col, value):
    id = self.identifiers[col]
    if id=="value":
      ftype = getattr(self.data[row], "fieldtype")
      if ftype=="bool":
        if value=="1":
          setattr(self.data[row], id, "t")
        else:
          setattr(self.data[row], id, "f")
        return
      if ftype=="date":
        try:
          if datetime.datetime.strptime(value,"%Y-%m-%d").__class__.__name__ == "datetime":
            pass
        except Exception:
          return
    setattr(self.data[row], id, value)
  
  def GetColId(self, col):
    return self.identifiers[col]
  
  def GetColIndex(self, key):
    return self.identifiers.index(key)
  
  def GetColLabelValue(self, col):
    id = self.identifiers[col]
    label = self.colLabels[id]
    return label

  def GetRowLabelValue(self,row):
    return self.rowLabels[row]
  
  def GetRowData(self, row):
    return self.data[row]
  
  def GetTypeName(self, row, col):
    id = self.identifiers[col]
    if id=="description":
      return wx.grid.GRID_VALUE_TEXT
    elif id=="value":
      ftype = getattr(self.data[row], "fieldtype")
      if ftype=="bool":
        return wx.grid.GRID_VALUE_BOOL
      elif ftype=="date":
        return wx.grid.GRID_VALUE_DATETIME
      elif ftype=="integer":
        return wx.grid.GRID_VALUE_LONG
      elif ftype=="float":
        return wx.grid.GRID_VALUE_NUMBER
      elif ftype=="valuelist":
        if getattr(self.data[row], "valuelist"):
          valuelist = ":"+getattr(self.data[row], "valuelist").replace("|", ",")
        else:
          valuelist = ""
        return wx.grid.GRID_VALUE_CHOICE+valuelist
      else:
        return wx.grid.GRID_VALUE_TEXT
      return wx.grid.GRID_VALUE_TEXT
    elif id=="notes":
      return wx.grid.GRID_VALUE_TEXT
      
  def GetAttr(self, row, col, kind):
    attr = wx.grid.GridCellAttr()
    id = self.identifiers[col]
    if id=="description":
      attr.SetReadOnly(True)
      attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
    elif id=="value":
      ftype = getattr(self.data[row], "fieldtype")
      if ftype=="bool" or ftype=="date":
        attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
      elif ftype=="integer" or ftype=="float":
        attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
      elif ftype=="urlink" or ftype=="customer":
        attr.SetReadOnly(True)
        attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
        attr.SetFont(wx.Font(9, wx.SWISS, wx.ITALIC, wx.BOLD, True))
        attr.SetTextColour("#0000FF")
      elif ftype in("notes","tool","trans","transitem","transmovement","transpayment","product","project","employee","place"):
        attr.SetReadOnly(True)
        attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
        attr.SetFont(wx.Font(9, wx.SWISS, wx.ITALIC, wx.BOLD, True))
        attr.SetTextColour("#44444444")
      else:
        attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
    elif id=="notes":
      attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
    return attr
  
class inputTable(wx.grid.PyGridTableBase):
  def __init__(self, id=[], dataTypes={}, colLabels={}, data=[]):
    wx.grid.PyGridTableBase.__init__(self)
    self.identifiers = id
    self.dataTypes = dataTypes
    rowLabels=[]
    for rowid in range(len(data)):
      rowLabels.append(str(rowid+1))
    self.rowLabels = rowLabels 
    self.colLabels = colLabels 
    self.data = data
  
  def GetNumberRows(self):
    return len(self.data)

  def GetNumberCols(self):
    return len(self.identifiers)

  def IsEmptyCell(self, row, col):
    id = self.identifiers[col]
    return not getattr(self.data[row], id) 
  
  def GetValue(self, row, col):
    id = self.identifiers[col]
    if getattr(self.data[row], id)==None:
      return ""
    elif self.dataTypes==None:
      return getattr(self.data[row], id)
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_DATETIME:
      return datetime.date.strftime(getattr(self.data[row], id),"%Y.%m.%d")
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_LONG:
      return getattr(self.data[row], id)
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_FLOAT:
      return getattr(self.data[row], id)
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_NUMBER:
      return getattr(self.data[row], id)
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_BOOL:
      if getattr(self.data[row], id)==True or getattr(self.data[row], id)!="":
        return 1
      else:
        return ""
    else:
      return getattr(self.data[row], id)

  def SetValue(self, row, col, value):
    id = self.identifiers[col]
    setattr(self.data[row], id, value)
  
  def GetColId(self, col):
    return self.identifiers[col]
  
  def GetColIndex(self, key):
    return self.identifiers.index(key)
  
  def GetColLabelValue(self, col):
    id = self.identifiers[col]
    label = self.colLabels[id]
    return label

  def GetRowLabelValue(self,row):
    return self.rowLabels[row]
  
  def GetRowData(self, row):
    return self.data[row]
  
  def GetTypeName(self, row, col):
    if self.dataTypes==None:
      return wx.grid.GRID_VALUE_TEXT
    else:
      id = self.identifiers[col]
      return self.dataTypes[id]
  
  def GetAttr(self, row, col, kind):
    attr = wx.grid.GridCellAttr()
    if self.dataTypes==None:
      attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
      return attr
    id = self.identifiers[col]
    if self.dataTypes[id]==wx.grid.GRID_VALUE_BOOL or self.dataTypes[id]==wx.grid.GRID_VALUE_DATETIME:
      attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_LONG or self.dataTypes[id]==wx.grid.GRID_VALUE_FLOAT or self.dataTypes[id]==wx.grid.GRID_VALUE_NUMBER:
      attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_TEXT:
      attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
    else:
      attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
    return attr
    
class browserTable(wx.grid.PyGridTableBase):
  
  def __init__(self, id=[], dataTypes={}, colLabels={}, data=[], sorting={}):
    wx.grid.PyGridTableBase.__init__(self)
    self.identifiers = id
    self.dataTypes = dataTypes
    rowLabels=[]
    for rowid in range(len(data)):
      rowLabels.append(str(rowid+1))
    self.rowLabels = rowLabels 
    self.colLabels = colLabels 
    self.data = data
    self.sorting = sorting 
  
  def GetNumberRows(self):
    return len(self.data)

  def GetNumberCols(self):
    return len(self.identifiers)

  def IsEmptyCell(self, row, col):
    id = self.identifiers[col]
    return not self.data[row][id]

  def GetValue(self, row, col):
    id = self.identifiers[col]
    if self.data[row][id]==None:
      return ""
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_DATETIME:
      if type(self.data[row][id]) is datetime.datetime:
        datetime.date.strftime(self.data[row][id],"%Y.%m.%d")
      elif type(self.data[row][id]).__name__=="unicode":
        return datetime.datetime.strptime(str(self.data[row][id]).split(" ")[0], str('%Y-%m-%d')).date()
      else:
        self.data[row][id]
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_LONG:
      return self.data[row][id]
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_FLOAT:
      return self.data[row][id]
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_NUMBER:
      return self.data[row][id]
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_BOOL:
      if self.data[row][id]==True:
        return 1
      else:
        return ""
    else:
      return self.data[row][id]

  def SetValue(self, row, col, value):
    id = self.identifiers[col]
    self.data[row][id] = value
  
  def GetColId(self, col):
    return self.identifiers[col]
  
  def GetColIndex(self, key):
    return self.identifiers.index(key)
    
  def GetColLabelValue(self, col):
    id = self.identifiers[col]
    label = self.colLabels[id]
    if len(self.sorting)>0:
      if self.sorting.has_key(id):
        if self.sorting[id]=="asc":
          label = "*" + label
        else:
          label = label + "*"
    return label

  def GetRowLabelValue(self,row):
    return self.rowLabels[row]
  
  def GetTypeName(self, row, col):
    id = self.identifiers[col]
    return self.dataTypes[id]
  
  def GetAttr(self, row, col, kind):
    attr = wx.grid.GridCellAttr()
    id = self.identifiers[col]
    if self.dataTypes[id]==wx.grid.GRID_VALUE_BOOL or self.dataTypes[id]==wx.grid.GRID_VALUE_DATETIME:
      attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_LONG or self.dataTypes[id]==wx.grid.GRID_VALUE_FLOAT or self.dataTypes[id]==wx.grid.GRID_VALUE_NUMBER:
      attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
    elif self.dataTypes[id]==wx.grid.GRID_VALUE_TEXT:
      attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
    else:
      attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
    return attr
      
  def MoveColumn(self,frm,to):
    grid = self.GetView()
    if grid:
      old = self.identifiers[frm]
      del self.identifiers[frm]
      if to > frm:
        self.identifiers.insert(to-1,old)
      else:
        self.identifiers.insert(to,old)
      grid.BeginBatch()
      msg = wx.grid.GridTableMessage(
              self, wx.grid.GRIDTABLE_NOTIFY_COLS_INSERTED, to, 1)
      grid.ProcessTableMessage(msg)
      msg = wx.grid.GridTableMessage(
              self, wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED, frm, 1)
      grid.ProcessTableMessage(msg)
      grid.EndBatch()

  def MoveRow(self,frm,to):
    grid = self.GetView()
    if grid:
      oldLabel = self.rowLabels[frm]
      oldData = self.data[frm]
      del self.rowLabels[frm]
      del self.data[frm]
      if to > frm:
        self.rowLabels.insert(to-1,oldLabel)
        self.data.insert(to-1,oldData)
      else:
        self.rowLabels.insert(to,oldLabel)
        self.data.insert(to,oldData)
      grid.BeginBatch()

      msg = wx.grid.GridTableMessage(
              self, wx.grid.GRIDTABLE_NOTIFY_ROWS_INSERTED, to, 1)
      grid.ProcessTableMessage(msg)
      msg = wx.grid.GridTableMessage(
              self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, frm, 1)
      grid.ProcessTableMessage(msg)
      grid.EndBatch()
      
class filterTable(wx.grid.PyGridTableBase):
  def __init__(self, id=[], colLabels={}, labelChoice={}, data=[]):
    wx.grid.PyGridTableBase.__init__(self)
    self.identifiers = id
    rowLabels=[]
    for rowid in range(len(data)):
      rowLabels.append(str(rowid+1))
    self.rowLabels = rowLabels 
    self.colLabels = colLabels 
    self.data = data
    self.labelChoice = labelChoice
    self.ftypeset1 = ":==, =N, !="
    self.ftypeset2 = ":==, =N, !=, >=, <=" 
  
  def SetData(self, data=[]):
    self.data = data
  
  def GetNumberRows(self):
    return len(self.data)

  def GetNumberCols(self):
    return len(self.identifiers)

  def IsEmptyCell(self, row, col):
    id = self.identifiers[col]
    return not getattr(self.data[row], id)

  def GetValue(self, row, col):
    id = self.identifiers[col]
    rtype = getattr(self.data[row], "fieldtype")
    if id=="fvalue":
      if rtype=="bool":
        if getattr(self.data[row], id)=="t" or getattr(self.data[row], id)=="true" or getattr(self.data[row], id)=="True":
          return 1
        else:
          return ""
    return getattr(self.data[row], id)

  def SetValue(self, row, col, value):
    id = self.identifiers[col]
    rtype = getattr(self.data[row], "fieldtype")
    if id=="ftype" or id=="fieldlabel":
      setattr(self.data[row], id, value.strip())
      return
    if id=="fvalue":
      if rtype=="bool":
        if value=="1":
          setattr(self.data[row], id, "t")
        else:
          setattr(self.data[row], id, "f")
        return
      if rtype=="date":
        try:
          if datetime.datetime.strptime(value,"%Y-%m-%d").__class__.__name__ == "datetime":
            pass
        except Exception:
          return
    setattr(self.data[row], id, value)
  
  def GetColId(self, col):
    return self.identifiers[col]
  
  def GetRowData(self, row):
    return self.data[row]
  
  def GetColIndex(self, key):
    return self.identifiers.index(key)
    
  def GetColLabelValue(self, col):
    id = self.identifiers[col]
    return self.colLabels[id]

  def GetRowLabelValue(self,row):
    return self.rowLabels[row]
  
  def GetTypeName(self, row, col):
    id = self.identifiers[col]
    rtype = getattr(self.data[row], "fieldtype")
    if id=="fieldlabel":
      if rtype=="date":
        return wx.grid.GRID_VALUE_CHOICE + self.labelChoice["dateLabel"]
      elif rtype=="float" or rtype=="integer":
        return wx.grid.GRID_VALUE_CHOICE + self.labelChoice["numberLabel"]
      elif rtype=="bool":
        return wx.grid.GRID_VALUE_CHOICE + self.labelChoice["boolLabel"]
      else:
        return wx.grid.GRID_VALUE_CHOICE + self.labelChoice["stringLabel"]
    
    if id=="ftype":
      if rtype=="date" or rtype=="float" or rtype=="integer":
        return wx.grid.GRID_VALUE_CHOICE + self.ftypeset2
      else:
        return wx.grid.GRID_VALUE_CHOICE + self.ftypeset1
    if id=="fvalue":
      if rtype=="date":
        #return wx.grid.GRID_VALUE_DATETIME
        return wx.grid.GRID_VALUE_STRING
      elif rtype=="float" or rtype=="integer":
        return wx.grid.GRID_VALUE_NUMBER
      elif rtype=="bool":
        return wx.grid.GRID_VALUE_BOOL
      else:
        return wx.grid.GRID_VALUE_STRING
  
  def GetAttr(self, row, col, kind):
    attr = wx.grid.GridCellAttr()
    id = self.identifiers[col]
    if id=="fieldlabel":
      attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
      return attr
    if id=="ftype":
      attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
      return attr
    if id=="fvalue":
      rtype = getattr(self.data[row], "fieldtype")
      if rtype=="date":
        attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
      elif rtype=="float":
        attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
      elif rtype=="integer":
        attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
      elif rtype=="bool":
        attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
      else:
        attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
      return attr
  