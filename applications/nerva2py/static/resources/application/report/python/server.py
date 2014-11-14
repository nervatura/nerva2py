#!/usr/bin/python
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingTCPServer
from os import curdir, sep
from nerva2py.report import Report

PORT_NUMBER = 8080

class report_demo(SimpleHTTPRequestHandler):
    
  def create_report(self, src, orient, output):
    rpt = Report(orientation=orient)
    if src=="xml":
      tfile = curdir+sep+"sample.xml"
      f = open(tfile)
      xdef = f.read()
      f.close()
      rpt.loadDefinition(xdef)
    else:
      from nerva2py.sample import sample_report
      rpt = sample_report(rpt)
    rpt.createReport()
    self.send_response(200)
    if output=="pdf":
      self.send_header("Content-type","application/pdf")
      self.send_header("Access-Control-Allow-Origin","*")
      self.send_header("Access-Control-Allow-Credentials","true")
      self.send_header("Access-Control-Allow-Methods","POST, GET, OPTIONS")
      self.send_header("Access-Control-Max-Age",86400)
      self.end_headers()
      self.wfile.write(rpt.save2Pdf())
    elif output=="html":
      self.send_header("Content-type","text/html")
      self.end_headers()
      self.wfile.write(rpt.save2Html())
    else:
      self.send_header("Content-type","text/xml")
      self.end_headers()
      self.wfile.write(rpt.save2Xml())
  
  def do_GET(self):
    cmd = str(self.path).split("?")[0]
    if cmd=="/document":
      orient = "p"; src = "xml"; output = "pdf"
      if len(str(self.path).split("?"))>1:
        params = str(self.path).split("?")[1]
        if params.find("landscape")>-1: 
          orient = "l"
        if params.find("data")>-1: 
          output = "xml"
        if params.find("html")>-1: 
          output = "html"
        if params.find("py")>-1: 
          src = "py"
      self.create_report(src, orient, output)
    elif cmd=="/template":
      ctype = "text/xml"; tfile = curdir+sep+"sample.xml"
      title = "XML Template"
      if len(str(self.path).split("?"))>1:
        params = str(self.path).split("?")[1]
        if str(params).find("py")>-1:
          title = "Python Template"
          ctype = "text/html"; tfile = curdir+sep+"ntura"+sep+"sample.py"
      f = open(tfile)
      tmp = f.read()
      f.close()
      self.send_response(200)
      self.send_header("Content-type",ctype)
      self.end_headers()
      if ctype == "text/xml":
        self.wfile.write(tmp)
      else:
        self.wfile.write('<!DOCTYPE html><html><head>')
        self.wfile.write('<title>Python Template</title>')
        self.wfile.write('<link rel="stylesheet" href="highlight/styles/default.css">')
        self.wfile.write('<script src="highlight/highlight.pack.js"></script>')
        self.wfile.write('<script>hljs.initHighlightingOnLoad();</script>')
        self.wfile.write('</head><body>')
        self.wfile.write('<pre><code class="python">')
        self.wfile.write(tmp)
        self.wfile.write('</code></pre>')
        self.wfile.write('</body></html>')
    else:
      return SimpleHTTPRequestHandler.do_GET(self)    
    return

try:
  server = ThreadingTCPServer(('localhost', PORT_NUMBER),report_demo)
  print "Started server on http://localhost:"+str(PORT_NUMBER)
  server.serve_forever()
        
except KeyboardInterrupt:
	print "^C received, shutting down the web server"
	server.socket.close()
