
from gluon import * #@UnusedWildImport
from gluon.storage import Storage
from gluon.contrib import simplejson as json

def _set_files(files):
  if current.request.ajax:
    current.response.js = (current.response.js or '') + """;(function ($) {
var srcs = $('script').map(function(){return $(this).attr('src');}),
  hrefs = $('link').map(function(){return $(this).attr('href');});
$.each(%s, function() {
  if ((this.slice(-3) == '.js') && ($.inArray(this.toString(), srcs) == -1)) {
      var el = document.createElement('script'); el.type = 'text/javascript'; el.src = this;
      document.body.appendChild(el);
  } else if ((this.slice(-4) == '.css') && ($.inArray(this.toString(), hrefs) == -1)) {
      $('<link rel="stylesheet" type="text/css" href="' + this + '" />').prependTo('head');
      if (/* for IE */ document.createStyleSheet){document.createStyleSheet(this);}
}});})(jQuery);""" % ('[%s]' % ','.join(["'%s'" % f.lower().split('?')[0] for f in files]))
  else:
    current.response.files[:0] = [f for f in files if f not in current.response.files]


class TinyEditorWidget(object):
    
  def __init__(self):
    settings = self.settings = Storage()
    
    #settings.id = 'input', #(required) ID of the textarea
    settings.width = '100%' #(optional) width of the editor
    settings.height = 'auto' #(optional) heightof the editor
    #settings.cssclass = 'tinyeditor', #(optional) CSS class of the editor
    #settings.controlclass = 'tinyeditor-control', #(optional) CSS class of the buttons
    #settings.rowclass = 'tinyeditor-header', #(optional) CSS class of the button rows
    #settings.dividerclass = 'tinyeditor-divider', #(optional) CSS class of the button diviers
    settings.controls = ['bold', 'italic', 'underline', 'strikethrough', '|', 'subscript', 'superscript', '|', 'orderedlist', 'unorderedlist', '|' ,'outdent' ,'indent', '|', 'leftalign', 'centeralign', 'rightalign', 'blockjustify', '|', 'unformat', '|', 'undo', 'redo', 'n', 'font', 'size', 'style', '|', 'image', 'hr', 'link', 'unlink', '|', 'print'] #(required) options you want available, a '|' represents a divider and an 'n' represents a new row
    settings.footer = 'true' #(optional) show the footer
    settings.fonts = ['Verdana','Arial','Georgia','Trebuchet MS']  #(optional) array of fonts to display
    settings.xhtml = 'true' #(optional) generate XHTML vs HTML
    #settings.cssfile = 'custom.css', #(optional) attach an external CSS file to the editor
    #settings.content = 'starting content', #(optional) set the starting content else it will default to the textarea content
    #settings.css = 'body{background-color = #ccc}', #(optional) attach CSS to the editor
    #settings.bodyid = 'editor', #(optional) attach an ID to the editor body
    #settings.footerclass = 'tinyeditor-footer', #(optional) CSS class of the footer
    #settings.toggle = {'text':'source','activetext':'wysiwyg','cssclass':'toggle'}, #(optional) toggle to markup view options
    #settings.resize = {'cssclass':'resize'} #(optional) display options for the editor resize

  def __call__(self, field, value, **attributes):
    if not self.settings.files:
      _files = [
          URL('static', 'tinyeditor/tinyeditor.css'),
          URL('static', 'tinyeditor/tiny.editor.js'),
      ]
      if self.settings.lang:
          _files.append(URL('static', 'tinyeditor/js/i18n/tinyeditor.%s.js' % self.settings.lang))
    else:
      _files = self.settings.files
    _set_files(_files)
      
    from gluon.utils import web2py_uuid
    _id = '%s_%s_%s' % (field._tablename, field.name, web2py_uuid())
    attr = dict(_id=_id, _name=field.name,
                requires=field.requires, _class='text')
    
    script = SCRIPT("""
    var editor = new TINY.editor.edit('editor', {
      id:'%(id)s',
      width: '%(width)s',
      height: '%(height)s',
      cssclass: 'tinyeditor',
      controlclass: 'tinyeditor-control',
      rowclass: 'tinyeditor-header',
      dividerclass: 'tinyeditor-divider',
      controls: %(controls)s,
      footer: %(footer)s,
      fonts: %(fonts)s,
      xhtml: %(xhtml)s,
      cssfile: 'custom.css',
      bodyid: 'editor',
      footerclass: 'tinyeditor-footer',
      toggle: {text: 'source', activetext: 'wysiwyg', cssclass: 'toggle'},
      resize: {cssclass: 'resize'}
    });
    """% dict(id=_id, width=self.settings.width, height=self.settings.height,
              controls=json.dumps(self.settings.controls), 
              footer=self.settings.footer,
              fonts=json.dumps(self.settings.fonts),
              xhtml=self.settings.xhtml)) 
    
    return SPAN(TEXTAREA((value != None and str(value)) or '', **attr),script, **attributes)