# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import * #@UnusedWildImport
from gluon.storage import Storage
from gluon.contrib import simplejson as json

# For referencing static and views from other application
#import os
#APP = os.path.basename(os.path.dirname(os.path.dirname(__file__)))


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


class ElrteWidget(object):
    
    def __init__(self):

        settings = self.settings = Storage()
        self.settings.files = None
        settings.cssfiles = []
        settings.lang = None
        settings.toolbar = 'default'
        settings.fm_open = "''"

    def __call__(self, field, value, **attributes):
        if not self.settings.files:
            _files = [
                URL('static', 'plugin_elrte_widget/css/elrte.min.css'),
                URL('static', 'plugin_elrte_widget/css/elrte-inner.css'),
                URL('static', 'plugin_elrte_widget/css/smoothness/jquery-ui-1.8.13.custom.css'),
                URL('static', 'plugin_elrte_widget/js/jquery-ui-1.8.16.custom.min.js'),
                URL('static', 'plugin_elrte_widget/js/elrte.min.js'),
            ]
            if self.settings.lang:
                _files.append(URL('static', 'plugin_elrte_widget/js/i18n/elrte.%s.js' % self.settings.lang))
        else:
            _files = self.settings.files
        _set_files(_files)
          
        from gluon.utils import web2py_uuid
        _id = '%s_%s_%s' % (field._tablename, field.name, web2py_uuid())
        attr = dict(_id=_id, _name=field.name,
                    requires=field.requires, _class='text')
                
        script = SCRIPT("""
jQuery(function() { var t = 10; (function run() {if ((function() {
    if (typeof elRTE === 'undefined') { return true; }
    var opts = elRTE.prototype.options;
    opts.panels.default_1 = ['pastetext', 'pasteformattext', 'removeformat', 'undo', 'redo'];
    opts.panels.default_2 = ['formatblock', 'fontsize', 'fontname'];
    opts.panels.default_3 = ['bold', 'italic', 'underline', 'strikethrough', 'subscript', 'superscript'];
    opts.panels.default_4 = ['forecolor', 'hilitecolor', 'justifyleft', 'justifyright',
                      'justifycenter', 'justifyfull', 'outdent', 'indent'];
    opts.panels.default_5 = ['link', 'unlink', 'image', 'elfinder','insertorderedlist', 'insertunorderedlist',
                      'horizontalrule', 'blockquote', 'div', 'stopfloat', 'css', 'nbsp'];
    opts.toolbars = {'default': ['default_1', 'default_2', 'default_3', 'default_4', 'default_5', 'tables'],
                     'min': ['default_1', 'default_2', 'default_3', 'default_4']};

    if(typeof String.prototype.trim !== 'function') {
      String.prototype.trim = function() {return this.replace(/^\s+|\s+$/g, '');}
    }
    var el = $('#%(id)s');
    if(!$.support.opacity){if (el.text() == '') { el.text('<p>&nbsp;</p>')}}

    el.elrte({cssClass: 'el-rte', lang: '%(lang)s',
              allowSource: false,
              toolbar: '%(toolbar)s',
              fmOpen : %(fm_open)s,
              cssfiles: %(cssfiles)s});
})()) {setTimeout(run, t); t = 2*t;}})();});

""" % dict(id=_id, lang=self.settings.lang or '',
           toolbar=self.settings.toolbar,
           fm_open=self.settings.fm_open,
           cssfiles=json.dumps(self.settings.cssfiles),
           ))
        
        return SPAN(script, TEXTAREA((value != None and str(value)) or '', **attr), **attributes)
