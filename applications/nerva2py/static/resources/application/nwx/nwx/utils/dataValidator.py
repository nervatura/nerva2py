# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2015, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

import wx
import string

class dataValidator(wx.PyValidator):
  
  def __init__(self, wtype="textBox", data=None, field=None, required=False, formatter=None, 
               validationCB=None, changeCB=None, maxLength=None):
    wx.PyValidator.__init__(self)
    self.wtype = wtype
    self.data = data
    self.field = field
    self.required = required
    self.formatter = formatter
    self.validationCB = validationCB
    self.changeCB = changeCB
    self.maxLength = maxLength
    if wtype=="radioBox" and self.changeCB!=None:
      self.Bind(wx.EVT_RADIOBOX, self._ctrlChange)
    elif wtype=="checkBox" and self.changeCB!=None:
      self.Bind(wx.EVT_CHECKBOX, self._ctrlChange)
    elif wtype=="spinBox" and self.changeCB!=None:
      self.Bind(wx.EVT_SPINCTRL, self._ctrlChange)
    elif wtype=="textBox" and self.changeCB!=None:  
      self.Bind(wx.EVT_TEXT, self._ctrlChange)
    elif wtype=="intBox" and self.changeCB!=None:  
      self.Bind(wx.EVT_CHAR, self._charChange)
      self.Bind(wx.wx.EVT_KILL_FOCUS, self._killFocus)
    else:
      pass

  def Clone(self):
    return self.__class__(self.wtype, self.data, self.field, self.required, self.formatter, 
                          self.validationCB, self.changeCB, self.maxLength)
  
  def Validate(self, win):
    flValid = True
    validateError=""
    wgt = self.GetWindow()
    if self.wtype=="textBox" or self.wtype=="checkBox" or self.wtype=="spinBox" or self.wtype=="intBox":
      value = wgt.GetValue()
    elif self.wtype=="radioBox":
      value = wgt.GetSelection()
    else:
      return False
    if self.required and value == "":
      validateError = "required|"+self.field
      flValid = False
    if flValid and self.formatter:
      flValid = self.formatter.validate(value)
    if self.validationCB:
      self.validationCB(self.data, self.field, value, self.required, flValid, validateError)
    return flValid
  
  def TransferToWindow(self):
    wgt = self.GetWindow()
    if self.data!=None:
      value = getattr(self.data, self.field)
      if value == None:
        value = ""
      if self.formatter:
        value = self.formatter.format(value)
      if self.wtype=="textBox":
        wgt.SetValue(value)
      elif self.wtype=="checkBox":
        if value==None:
          value=False
        wgt.SetValue(value)
      elif self.wtype=="spinBox":
        if value==None:
          value=0
        wgt.SetValue(value)
      elif self.wtype=="intBox":
        if value==None:
          value='0'
        wgt.SetValue(str(value))
      elif self.wtype=="radioBox":
        try:
          wgt.SetSelection(value)
        except:
          pass
      else:
        return False
    else:
      try:
        wgt.Clear()
      except:
        pass  
    return True
  
  def TransferFromWindow(self):
    wgt = self.GetWindow()
    if self.data!=None:
      if self.wtype=="textBox" or self.wtype=="spinBox" or self.wtype=="intBox":
        newValue = wgt.GetValue()
      elif self.wtype=="checkBox":
        newValue = int(wgt.GetValue())
      elif self.wtype=="radioBox":
        newValue = wgt.GetSelection()
      else:
        return False
      oldValue = getattr(self.data, self.field)
      if self.formatter:
        oldValue = self.formatter.format(oldValue)
      if oldValue==None:
        oldValue=""
      if newValue != oldValue:
        if self.formatter:
          newValue = self.formatter.coerce(newValue)
        setattr(self.data, self.field, newValue)
        if self.changeCB!=None:
          self.changeCB(wgt, oldValue, newValue, self.data, self.field)
    return True
    
  def _charChange(self, event):
    key = event.GetKeyCode()
    if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key == 45 or key > 255:
      event.Skip()
      return
    lvalue = self.GetWindow().GetValue()
    if len(lvalue)==self.maxLength:
      return
    if chr(key) in string.digits:
      event.Skip()
      return
    return
  
  def _killFocus(self, event):
    wgt = self.GetWindow()
    value = wgt.GetValue()
    if self.wtype=="intBox":
      try:
        value = int(value)
      except:
        value = 0
        wgt.SetValue(str(value))
      finally:
        self.TransferFromWindow()
        
  def _ctrlChange(self, event):
    self.TransferFromWindow()
    return
  