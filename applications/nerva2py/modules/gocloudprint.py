# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Project
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""

#see: https://developers.google.com/cloud-print/docs/pythonCode
#and https://github.com/armooo/cloudprint

import time, urllib, urllib2, mimetools, string

CRLF = '\r\n'
BOUNDARY = mimetools.choose_boundary()
 
LOGIN_URL = 'https://www.google.com/accounts/ClientLogin'
SERVICE = 'cloudprint'
 
CLOUDPRINT_URL = 'https://www.google.com/cloudprint'
CLIENT_NAME = 'Nervatura'
 
class goCloudPrint(object):
   
  auth = None
  error_message = ""
  printers = {}
   
  def __init__(self, email, password):
    self.getAuth(email, password)
     
  def getAuth(self, email, password):    
    params = {'accountType': 'GOOGLE',
              'Email': email,
              'Passwd': password,
              'service': SERVICE,
              'source': CLIENT_NAME}
    stream = urllib.urlopen(LOGIN_URL, urllib.urlencode(params))
 
    for line in stream:
      if line.strip().startswith('Auth='):
        self.auth = line.strip().replace('Auth=', '')
    return True
  
  def getUrl(self, url, data=None):
    request = urllib2.Request(url)
    request.add_header('Authorization', 'GoogleLogin auth=%s' % self.auth)
    request.add_header('X-CloudPrint-Proxy', 'api-prober')
    if data:
      request.add_data(data)
      request.add_header('Content-Length', str(len(data)))
      request.add_header('Content-Type', 'multipart/form-data;boundary=%s' % BOUNDARY)
    retry_count = 0
    while retry_count < 5:
      try:
        result = urllib2.urlopen(request).read()
        return result
      except urllib2.HTTPError, e:
        self.error_message = 'Error accessing %s\n%s' % (url, e)
        time.sleep(60)
        retry_count += 1
        if retry_count == 5:
          return False
          
  def getPrinters(self, proxy=None):
    
    def stripPunc(s):
      for c in string.punctuation:
        if c == '-':  # Could be negative number, so don't remove '-'.
          continue
        else:
          s = s.replace(c, '')
      return s.strip()
    def getKeyValue(line, sep=':'):
      s = line.split(sep)
      return stripPunc(s[1])
    
    printers = {}
    values = {}
    tokenss = ['"id"', '"name"', '"proxy"']
    for t in tokenss:
      values[t] = ''

    if proxy:
      response = self.getUrl('%s/list?proxy=%s' % (CLOUDPRINT_URL, proxy))
    else:
      response = self.getUrl('%s/search' % CLOUDPRINT_URL)
    sections = response.split('{')
    for printer in sections:
      lines = printer.split(',')
      for line in lines:
        for t in tokenss:
          if t in line:
            values[t] = getKeyValue(line)
          if values['"id"']:
            printers[values['"id"']] = {}
            printers[values['"id"']]['name'] = values['"name"']
            printers[values['"id"']]['proxy'] = values['"proxy"']
    self.printers = printers
    return True
  
  def encodeMultiPart(self, fields, files, file_type='application/pdf'):
    lines = []
    for (key, value) in fields:
      lines.append('--' + BOUNDARY)
      lines.append('Content-Disposition: form-data; name="%s"' % key)
      lines.append('')  # blank line
      lines.append(value)
    for (key, filename, value) in files:
      lines.append('--' + BOUNDARY)
      lines.append(
          'Content-Disposition: form-data; name="%s"; filename="%s"'
          % (key, filename))
      lines.append('Content-Type: %s' % file_type)
      lines.append('')  # blank line
      lines.append(value)
    lines.append('--' + BOUNDARY + '--')
    lines.append('')  # blank line
    return CRLF.join(lines)
  
  def getMessage(self, response):
    lines = response.split('\n')
    for line in lines:
      if '"message":' in line:
        msg = line.split(':')
        return msg[1]
    return None

  def submitJob(self, printerid, title, pdfdata):
    headers = [('printerid', printerid),
               ('title', title),
               ('contentType', 'application/pdf')]
    files = [('capabilities', 'capabilities', '{"capabilities":[]}')]
    files.append(('content', '', pdfdata))
    edata = self.encodeMultiPart(headers, files)
    response = self.getUrl('%s/submit' % CLOUDPRINT_URL, data=edata)
    if response.find('"success": true') == -1:
      self.error_message = self.getMessage(response)
      return False
    else:
      return True
