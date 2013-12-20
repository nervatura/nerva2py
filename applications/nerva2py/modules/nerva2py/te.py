from gluon import * #@UnusedWildImport
from gluon.storage import Storage

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


class JqueryTeWidget(object):
    
  def __init__(self):
    settings = self.settings = Storage()
    
    settings.title = 'true' #(optional) Setting to displaying titles
    settings.source = 'true' #(optional) The 'source field' button.
    #all possible settings, see: http://jqueryte.com/documentation

  def __call__(self, field, value, **attributes):
    if not self.settings.files:
      _files = [
          URL('static', 'css/jquery-te.css'),
          URL('static', 'js/jquery-te.min.js'),
      ]
    else:
      _files = self.settings.files
    _set_files(_files)
      
    from gluon.utils import web2py_uuid
    _id = '%s_%s_%s' % (field._tablename, field.name, web2py_uuid())
    attr = dict(_id=_id, _name=field.name,
                requires=field.requires, _class='text')
    
    script = SCRIPT("""
    $('#%(id)s').jqte({
      title: %(title)s,
      source: %(source)s
    });
    """% dict(id=_id, title=self.settings.title, source=self.settings.source)) 
    
    return SPAN(TEXTAREA((value != None and str(value)) or '', **attr),script, **attributes)