# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage

class DIALOG(DIV):
        
    def __init__(self, content, title=None, icon=None, close_button=None, 
                 width=70, height=70, onclose='', add_lnk=None, renderstyle=False, **attributes):
        DIV.__init__(self, **attributes)
        self.title, self.icon, self.content, self.close_button, self.width, self.height, self.onclose = (
            title, icon, content, close_button, width, height, onclose)
        if add_lnk:
          self.add_lnk = TD(DIV(A(SPAN(_class="icon plus"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;vertical-align: middle;", 
                              _class="w2p_trap buttontext button", _href=str(add_lnk), _title="New", _target="_blank"), _align="right", _style="padding: 0px; padding-top: 4px;text-align: right;"), _width="16px")
        else:
          self.add_lnk = ""
        self.attributes['_class'] = self.attributes.get('_class', 'dialog')
        
        import uuid
        self.attributes['_id'] = self.attributes.get('_id') or str(uuid.uuid4())
        self.attributes['_style'] = self.attributes.get('_style', 
            'display:none; z-index:1001; position:fixed; top:0%;left:0%;width:100%;height:100%;')
        
        if renderstyle:
            _url = URL('static','css/dialog.css')
            if _url not in current.response.files:
                current.response.files.append(_url)
                
    def show(self):
        import gluon.contrib.simplejson as json
        return """(function(){
var el = jQuery("#%(id)s");
if (el.length == 0) {el = jQuery(%(xml)s); jQuery(document.body).append(el);}
el.css('zIndex', (parseInt(el.css('zIndex')) || 1000) + 10);
el.show();})();"""  % dict(id=self.attributes['_id'], 
                       xml=json.dumps(self.xml().replace('<!--', '').replace('//-->', '')))
        
    def close(self):
        return '%s;jQuery("#%s").hide();' % (self.onclose, self.attributes['_id'])
        
    def xml(self): 
        self.components += [
            DIV(_style='width:100%;height:100%;',
                _class='dialog-back', 
                _onclick='%s;return false;' % self.close()),
            DIV(DIV(
                TABLE(TR(TD(IMG(_src=self.icon, _style='vertical-align: middle;'),
                            SPAN(self.title, _style='font-weight:bolder:font-size:20px;color: #FFFFFF;padding: 0px;padding-left: 10px;color: #FFD700;font-weight: bold;'),
                            _style='padding-left: 10px;vertical-align: middle;'),
                         self.add_lnk,
                         TD(DIV(A(SPAN(_class="icon cross"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;vertical-align: middle;", 
                              _class="w2p_trap buttontext button", _href="#null", _title="Cancel", 
                              _onclick='%s;return false' % self.close(),_id="dlg_close"), _align="right", _style="padding: 0px; padding-top: 4px;text-align: right;"), _width="16px")), 
                      _style="border-style: solid;border-width: 1px;border-color: #CCCCCC;background-color: #000000;padding: 0px;", 
                      _width="100%", _cellpadding="0", _cellspacing="0"),
#                SPAN(self.title, _style='font-weight:bold:font-size:18px;') if self.title else '',
#                SPAN(A(SPAN(_class="icon cross"), _style="padding-top: 1px;padding-left: 4px;padding-right: 2px;padding-bottom: 0px;", _class="w2p_trap buttontext button", _href="#null", _title="Cancel", _onclick='%s;return false' % self.close()),
#                #SPAN('[', A(self.close_button, _href='#', _onclick='%s;return false;' % self.close()), ']', 
#                     _style='float:right'
#                     ) if self.close_button else '',
#                HR(_style='margin-bottom: 0px;') if self.title else '',
                self.content, _id='c%s' % self.attributes['_id'],
                    _style=("""
position:absolute;top:%(top)s%%;left:%(left)s%%;
width:%(width)s%%;height:auto;
z-index:1100;overflow:auto;
""" % dict(left=(100-self.width)/2-2, top=(100-self.height)/2-2, width=self.width, height=self.height)),
                    _class='dialog-front', 
                    _onclick="""
var e = arguments[0] || window.event;
if (jQuery(e.target).parent().attr('id') == "c%s") {%s;};
""" % (self.attributes['_id'], self.close())
                ),
            )]
        return DIV.xml(self)
