function get_base_url(){return window.location.protocol+"//"+window.location.host+"/"+document.getElementById("appl_url").className}function call_menucmd(a,b){url_str=get_base_url()+"/frm_custom_menu/_menukey";url_str=url_str.replace("_menukey",a);1==b?window.open(url_str,"_blank"):window.location=url_str}
function set_customer_value(a,b,c){if(null!=document.getElementById("edit_fieldvalue")&&"block"==document.getElementById("edit_fieldvalue").style.display)return document.getElementById("fieldvalue_value").value=a,document.getElementById("fieldvalue_value_customer_label").innerHTML=c,!0;document.getElementById("customer_id").value=a;document.getElementById("customer_custname").innerHTML=c;return!0}
function set_tool_value(a,b,c){if(null!=document.getElementById("edit_fieldvalue")&&"block"==document.getElementById("edit_fieldvalue").style.display)return document.getElementById("fieldvalue_value").value=a,document.getElementById("fieldvalue_value_tool_label").innerHTML=b,!0;document.getElementById("tool_id").value=a;document.getElementById("tool_serial").innerHTML=b;return!0}
function set_product_value(a,b,c,d,e){document.getElementById("cmb_formula")&&(document.getElementById("cmb_formula").selectedIndex=0,document.getElementById("cmb_formula").disabled=!0);if(null!=document.getElementById("edit_item")&&"block"==document.getElementById("edit_item").style.display)return document.getElementById("product_id").value=a,document.getElementById("product_description").innerHTML=c,document.getElementById("item_description").value=c,document.getElementById("item_unit").value=d,
document.getElementById("item_tax_id").value=e,$("select#item_tax_id").selectmenu("refresh"),document.getElementById("item_rate").value=rate_lst[document.getElementById("item_tax_id").selectedIndex-1],calc_price("fxprice"),load_price(a),!0;if(null!=document.getElementById("edit_fieldvalue")&&"block"==document.getElementById("edit_fieldvalue").style.display)return document.getElementById("fieldvalue_value").value=a,document.getElementById("fieldvalue_value_product_label").innerHTML=c,!0;if(null!=document.getElementById("production_product_id")&&
"block"==document.getElementById("trans_page").style.display)return document.getElementById("production_product_id").value=a,document.getElementById("production_product_label").innerHTML=c,!0;document.getElementById("product_id").value=a;document.getElementById("product_description").innerHTML=c;return!0}
function set_transitem_value(a,b,c,d,e){if(null!=document.getElementById("link_edit")&&"block"==document.getElementById("link_edit").style.display)return document.getElementById("ref_id_2").value=a,document.getElementById("link_transnumber").innerHTML=b,null!=document.getElementById("trans_curr")&&(document.getElementById("trans_curr").innerHTML=e),!0;if(null!=document.getElementById("edit_fieldvalue")&&"block"==document.getElementById("edit_fieldvalue").style.display)return document.getElementById("fieldvalue_value").value=
a,document.getElementById("fieldvalue_value_transitem_label").innerHTML=b,!0;document.getElementById("trans_id").value=a;document.getElementById("reftrans_transnumber").innerHTML=b;return!0}
function set_transmovement_value(a,b,c,d){if(null!=document.getElementById("edit_fieldvalue")&&"block"==document.getElementById("edit_fieldvalue").style.display)return document.getElementById("fieldvalue_value").value=a,document.getElementById("fieldvalue_value_transmovement_label").innerHTML=b,!0;document.getElementById("trans_id").value=a;document.getElementById("reftrans_transnumber").innerHTML=b;return!0}
function set_transpayment_value(a,b,c,d){if(null!=document.getElementById("edit_fieldvalue")&&"block"==document.getElementById("edit_fieldvalue").style.display)return document.getElementById("fieldvalue_value").value=a,document.getElementById("fieldvalue_value_transpayment_label").innerHTML=b,!0;document.getElementById("trans_id").value=a;document.getElementById("reftrans_transnumber").innerHTML=b;return!0}
function set_project_value(a,b,c){if(null!=document.getElementById("edit_fieldvalue")&&"block"==document.getElementById("edit_fieldvalue").style.display)return document.getElementById("fieldvalue_value").value=a,document.getElementById("fieldvalue_value_project_label").innerHTML=b,!0;document.getElementById("project_id").value=a;document.getElementById("project_pronumber").innerHTML=b;return!0}
function set_employee_value(a,b,c){if(null!=document.getElementById("edit_fieldvalue")&&"block"==document.getElementById("edit_fieldvalue").style.display)return document.getElementById("fieldvalue_value").value=a,document.getElementById("fieldvalue_value_employee_label").innerHTML=b,!0;document.getElementById("employee_id").value=a;document.getElementById("employee_empnumber").innerHTML=b;return!0}
function set_place_value(a,b,c,d){if(null!=document.getElementById("edit_fieldvalue")&&"block"==document.getElementById("edit_fieldvalue").style.display)return document.getElementById("fieldvalue_value").value=a,document.getElementById("fieldvalue_value_place_label").innerHTML=b,!0;if(null!=document.getElementById("movement_edit")&&"block"==document.getElementById("movement_edit").style.display)return document.getElementById("movement_place_id").value=a,document.getElementById("movement_place_planumber").innerHTML=
b,!0;if(null!=document.getElementById("production_place_id")&&"block"==document.getElementById("trans_page").style.display)return document.getElementById("production_place_id").value=a,document.getElementById("production_place_label").innerHTML=b,!0;document.getElementById("place_id").value=a;document.getElementById("place_planumber").innerHTML=b;null!=document.getElementById("place_curr")&&(document.getElementById("place_curr").innerHTML=d);return!0}
function set_place_value2(a,b,c,d){document.getElementById("target_place_id").value=a;document.getElementById("target_place_planumber").innerHTML=b;return!0}function set_payment_value(a,b,c,d,e){document.getElementById("ref_id_1").value=a;document.getElementById("label_link_id").innerHTML=a;document.getElementById("link_transnumber").innerHTML=b;document.getElementById("link_curr").innerHTML=d;document.getElementById("link_amount").value=e;return!0}
function set_fieldvalue(a,b,c,d,e,f,g,k,h){if(-1==a){if(""==document.getElementById("cmb_fields").value)return alert(ms_err_field_new),!0;var l=document.getElementById("cmb_fields").value.split("~");b=l[0];c=document.getElementById("cmb_fields").children[document.getElementById("cmb_fields").selectedIndex].text;g=l[1];switch(g){case "bool":d="false";break;case "integer":case "float":d=0}"None"!=l[2]&&(k=l[2])}document.getElementById("fieldvalue_id").value=a;document.getElementById("fieldvalue_fieldname").value=
b;document.getElementById("fieldvalue_fieldtype").value=g;document.getElementById("fieldvalue_description").innerHTML=c;document.getElementById("fieldvalue_notes").innerHTML=f;document.getElementById("fieldvalue_readonly").value=h;document.getElementById("fieldvalue_value").value="";b=document.getElementById("fieldvalue_value_controls").children;for(a=0;a<b.length;a++)b[a].style.display="none";b=null;f=document.getElementById("fieldvalue_notes");b=null!=document.getElementById("fieldvalue_value_"+
g)?document.getElementById("fieldvalue_value_"+g):document.getElementById("fieldvalue_value_text");switch(b.nodeName){case "DIV":document.getElementById("fieldvalue_value_"+g+"_label").innerHTML=e;document.getElementById("fieldvalue_value").value=d;f=document.getElementById("fieldvalue_notes");break;case "INPUT":case "TEXTAREA":"bool"==g?(document.getElementById("fieldvalue_value_bool_label").style.display="block",$("input#fieldvalue_value_bool").prop("checked","true"==d).checkboxradio("refresh"),
document.getElementById("fieldvalue_value_bool_text").innerHTML=c,document.getElementById("fieldvalue_description").style.display="none"):b.value=d;f=b;break;case "SELECT":for(;0<b.options.length;)b.options.remove(0);options=k.split("|");for(a=0;a<options.length;a++)options[a]==d?b.options.add(new Option(options[a],options[a],!0,!0)):b.options.add(new Option(options[a]));$("select#fieldvalue_value_valuelist").selectmenu("refresh")}b.style.display="block";b.parentElement.style.display="block";b.parentElement.parentElement.style.display=
"block";document.getElementById("fieldvalue_page").style.display="none";document.getElementById("ctr_fieldvalue_page").style.display="none";null!=document.getElementById("ctr_local_menu")&&(document.getElementById("ctr_local_menu").style.display="none");document.getElementById("edit_fieldvalue").style.display="block";document.getElementById("ctr_edit_fieldvalue").style.display="block";f.focus();return!0}
function fieldvalue_update(){if("1"==document.getElementById("fieldvalue_readonly").value)return alert(ms_err_field_update),!1;var a=document.getElementById("fieldvalue_fieldtype").value,b=null,b=null!=document.getElementById("fieldvalue_value_"+a)?document.getElementById("fieldvalue_value_"+a):document.getElementById("fieldvalue_value_text");switch(b.nodeName){case "INPUT":switch(a){case "bool":1==b.checked?document.getElementById("fieldvalue_value").value="true":document.getElementById("fieldvalue_value").value=
"false";break;case "integer":case "float":""==b.value?document.getElementById("fieldvalue_value").value=0:document.getElementById("fieldvalue_value").value=b.value;break;default:document.getElementById("fieldvalue_value").value=b.value}break;case "TEXTAREA":document.getElementById("fieldvalue_value").value=b.value;break;case "SELECT":document.getElementById("fieldvalue_value").value=b.value}document.forms.frm_fieldvalue.submit()}
function set_item(a,b,c,d,e,f,g,k,h,l,m,n,p,q,r,s){document.getElementById("item_id").value=a;-1!=a?document.getElementById("label_item_id").innerHTML=a:document.getElementById("label_item_id").innerHTML="000000";document.getElementById("product_id").value=b;document.getElementById("product_description").innerHTML=c;document.getElementById("item_tax_id").value=d;$("select#item_tax_id").selectmenu("refresh");document.getElementById("item_rate").value=e;document.getElementById("item_vatamount").value=
f;document.getElementById("curr_digit").value=g;document.getElementById("item_description").value=k;document.getElementById("item_deposit")&&(document.getElementById("item_deposit").value=h,$("input#item_deposit").prop("checked",1==h).checkboxradio("refresh"));document.getElementById("item_qty").value=l;document.getElementById("item_discount").value=m;document.getElementById("item_fxprice").value=n;document.getElementById("item_unit").value=p;document.getElementById("item_netamount").value=q;document.getElementById("item_amount").value=
r;document.getElementById("item_ownstock").value=s;document.getElementById("item_page").style.display="none";document.getElementById("ctr_item_page").style.display="none";null!=document.getElementById("ctr_local_menu")&&(document.getElementById("ctr_local_menu").style.display="none");document.getElementById("edit_item").style.display="block";document.getElementById("ctr_edit_item").style.display="block";document.getElementById("item_description").focus();return!0}
function item_update(){if(""==document.getElementById("product_id").value)return alert(ms_err_item_update_product),!1;if(""==document.getElementById("item_description").value)return alert(ms_err_item_update_description),!1;if(""==document.getElementById("item_tax_id").value)return alert(ms_err_item_update_tax),!1;document.forms.frm_item.submit()}
function load_price(){var a=document.getElementById("product_id"),b=document.getElementById("item_qty"),c=document.getElementById("item_fxprice"),d=document.getElementById("item_trans_id").value,a=get_base_url()+"/cmd_get_price?trans_id="+d+"&product_id="+a.value+"&qty="+b.value;jQuery.ajax({type:"POST",url:a,success:function(a){0!=parseFloat(a)&&(c.value=a,0==parseFloat(b.value)&&(b.value=1),calc_price("fxprice"))}})}
function _round(a,b){a=parseFloat(a);if(isNaN(a))return a;b||(b=0);var c=Math.pow(10,b);return Math.floor(a*c+(5<=a*c*10%10?1:0))/c}function getNumObj(a){""==document.getElementById(a).value&&(document.getElementById(a).value=0);return document.getElementById(a)}
function calc_price(a){var b=getNumObj("item_fxprice"),c=getNumObj("item_qty"),d=getNumObj("item_netamount"),e=getNumObj("item_amount"),f=getNumObj("item_vatamount"),g=getNumObj("item_rate"),k=getNumObj("item_discount"),h=getNumObj("curr_digit");switch(a){case "fxprice":d.value=_round(parseFloat(b.value)*(1-parseFloat(k.value)/100)*parseFloat(c.value),parseInt(h.value));f.value=_round(parseFloat(d.value)*parseFloat(g.value),parseInt(h.value));e.value=parseFloat(d.value)+parseFloat(f.value);break;
case "netamount":0==parseFloat(c.value)?(b.value=0,f.value=0):(b.value=_round(parseFloat(d.value)/(1-parseFloat(k.value)/100)/parseFloat(c.value),parseInt(h.value)),f.value=_round(parseFloat(d.value)*parseFloat(g.value),parseInt(h.value)));e.value=parseFloat(d.value)+parseFloat(f.value);break;case "amount":0==parseFloat(c.value)?(b.value=0,d.value=0,f.value=0):(d.value=_round(parseFloat(e.value)/(1+parseFloat(g.value)),parseInt(h.value)),f.value=parseFloat(e.value)-parseFloat(d.value),b.value=_round(parseFloat(d.value)/
(1-parseFloat(k.value)/100)/parseFloat(c.value),parseInt(h.value)))}}
function set_payment(a,b,c,d){document.getElementById("payment_id").value=a;-1!=a?document.getElementById("label_payment_id").innerHTML=a:document.getElementById("label_payment_id").innerHTML="000000";document.getElementById("payment_paiddate").value=b;document.getElementById("payment_amount").value=c;document.getElementById("payment_notes").value=d;document.getElementById("payment_page").style.display="none";document.getElementById("ctr_payment_page").style.display="none";null!=document.getElementById("ctr_local_menu")&&
(document.getElementById("ctr_local_menu").style.display="none");document.getElementById("payment_edit").style.display="block";document.getElementById("ctr_payment_edit").style.display="block";document.getElementById("payment_paiddate").focus();return!0}
function payment_update(){if(""==document.getElementById("payment_paiddate").value)return alert(ms_err_payment_paiddate),!1;""==document.getElementById("payment_amount").value&&(document.getElementById("payment_amount").value=0);document.forms.frm_payment.submit()}
function set_link_invoice(a,b,c,d,e,f,g){document.getElementById("link_invoice_id").value=a;-1!=a?document.getElementById("label_link_id").innerHTML=b:document.getElementById("label_link_id").innerHTML="000000";document.getElementById("ref_id_1").value=b;document.getElementById("ref_id_2").value=c;document.getElementById("link_transnumber").innerHTML=d;document.getElementById("link_curr").innerHTML=e;document.getElementById("link_amount").value=f;document.getElementById("link_rate").value=g;document.getElementById("link_page").style.display=
"none";document.getElementById("ctr_link_page").style.display="none";null!=document.getElementById("payment_edit")&&(document.getElementById("payment_edit").style.display="none",document.getElementById("ctr_payment_edit").style.display="none");null!=document.getElementById("ctr_local_menu")&&(document.getElementById("ctr_local_menu").style.display="none");document.getElementById("link_edit").style.display="block";document.getElementById("ctr_link_edit").style.display="block";document.getElementById("link_amount").focus();
return!0}function link_invoice_update(){if(""==document.getElementById("ref_id_1").value)return alert(ms_err_link_invoice_rfid_1),!1;if(""==document.getElementById("ref_id_2").value)return alert(ms_err_link_invoice_rfid_2),!1;""==document.getElementById("link_amount").value&&(document.getElementById("link_amount").value=0);""==document.getElementById("link_rate").value&&(document.getElementById("link_rate").value=1);document.forms.frm_link_invoice.submit()}
function set_barcode(a,b,c,d,e,f){document.getElementById("barcode_id").value=a;document.getElementById("barcode_code").value=b;document.getElementById("barcode_description").value=c;document.getElementById("barcode_barcodetype").value=d;$("select#barcode_barcodetype").selectmenu("refresh");document.getElementById("barcode_qty").value=e;document.getElementById("barcode_defcode").value=f;$("input#barcode_defcode").prop("checked",1==f).checkboxradio("refresh");document.getElementById("barcode_page").style.display=
"none";document.getElementById("ctr_barcode_page").style.display="none";null!=document.getElementById("ctr_local_menu")&&(document.getElementById("ctr_local_menu").style.display="none");document.getElementById("barcode_edit").style.display="block";document.getElementById("ctr_barcode_edit").style.display="block";document.getElementById("barcode_code").focus();return!0}
function barcode_update(){if(""==document.getElementById("barcode_code").value)return alert(ms_err_barcode_missing_code),!1;if(""==document.getElementById("barcode_barcodetype").value)return alert(ms_err_barcode_missing_barcodetype),!1;""==document.getElementById("barcode_qty").value&&(document.getElementById("barcode_qty").value=0);var a=document.forms.frm_barcode.baseURI.split("?")[0].replace("#",""),a=a+"?check_barcode=true"+("&barcode_id="+document.getElementById("barcode_id").value),a=a+("&code="+
document.getElementById("barcode_code").value);jQuery.ajax({type:"POST",url:a,success:function(a){"OK"==a?document.forms.frm_barcode.submit():alert(a)}});return!0}
function set_address(a,b,c,d,e,f,g){document.getElementById("address_id").value=a;-1!=a?document.getElementById("label_address_id").innerHTML=a:document.getElementById("label_address_id").innerHTML="000000";document.getElementById("address_country").value=b;document.getElementById("address_state").value=c;document.getElementById("address_zipcode").value=d;document.getElementById("address_city").value=e;document.getElementById("address_street").value=f;document.getElementById("address_notes").value=
g;document.getElementById("address_page").style.display="none";document.getElementById("ctr_address_page").style.display="none";null!=document.getElementById("ctr_local_menu")&&(document.getElementById("ctr_local_menu").style.display="none");document.getElementById("address_edit").style.display="block";document.getElementById("ctr_address_edit").style.display="block";document.getElementById("address_country").focus();return!0}
function set_contact(a,b,c,d,e,f,g,k,h){document.getElementById("contact_id").value=a;-1!=a?document.getElementById("label_contact_id").innerHTML=a:document.getElementById("label_contact_id").innerHTML="000000";document.getElementById("contact_firstname").value=b;document.getElementById("contact_surname").value=c;document.getElementById("contact_status").value=d;document.getElementById("contact_phone").value=e;document.getElementById("contact_fax").value=f;document.getElementById("contact_mobil").value=
g;document.getElementById("contact_email").value=k;document.getElementById("contact_notes").value=h;document.getElementById("contact_page").style.display="none";document.getElementById("ctr_contact_page").style.display="none";null!=document.getElementById("ctr_local_menu")&&(document.getElementById("ctr_local_menu").style.display="none");document.getElementById("contact_edit").style.display="block";document.getElementById("ctr_contact_edit").style.display="block";document.getElementById("contact_firstname").focus();
return!0}
function set_price(a,b,c,d,e,f,g,k,h,l,m,n,p){document.getElementById("edit_id").value=a;-1!=a?document.getElementById("label_edit_id").innerHTML=a:document.getElementById("label_edit_id").innerHTML="000000";document.getElementById("title_item").innerHTML=p;document.getElementById("price_validfrom").value=b;"None"!=c?document.getElementById("price_validto").value=c:document.getElementById("price_validto").value="";document.getElementById("price_curr").value=d;$("select#price_curr").selectmenu("refresh");document.getElementById("price_qty").value=
e;document.getElementById("price_pricevalue").value=f;document.getElementById("price_vendorprice").value=h;$("input#price_vendorprice").prop("checked",1==h).checkboxradio("refresh");"None"!=g?document.getElementById("price_discount").value=g:document.getElementById("price_discount").value="";document.getElementById("price_calcmode").value=k;$("select#price_calcmode").selectmenu("refresh");"None"!=l?document.getElementById("price_group_id").value=l:document.getElementById("price_group_id").value="";
$("select#price_group_id").selectmenu("refresh");"None"!=m?(document.getElementById("customer_id").value=m,document.getElementById("customer_custname").innerHTML=n):(document.getElementById("customer_id").value="",document.getElementById("customer_custname").innerHTML="");document.getElementById("view_page").style.display="none";document.getElementById("ctr_view_page").style.display="none";document.getElementById("edit_page").style.display="block";document.getElementById("ctr_edit_page").style.display=
"block";document.getElementById("price_validfrom").focus();return!0}
function price_update(){if(""==document.getElementById("price_validfrom").value)return alert(ms_err_price_missing_validfrom),!1;if(""==document.getElementById("price_calcmode").value)return alert(ms_err_price_missing_calcmode),!1;if(""==document.getElementById("price_curr").value)return alert(ms_err_missing_curr),!1;if(""!=document.getElementById("customer_id").value&""!=document.getElementById("price_group_id").value)return alert(ms_err_price_no_list),!1;""==document.getElementById("price_qty").value&&
(document.getElementById("price_qty").value=0);""==document.getElementById("price_pricevalue").value&&(document.getElementById("price_pricevalue").value=0);""==document.getElementById("price_discount").value&"hidden"!=document.getElementById("price_discount").type&&(document.getElementById("price_discount").value=0);document.forms.frm_edit.submit()}
function set_rate(a,b,c,d,e,f,g,k){document.getElementById("edit_id").value=a;-1!=a?document.getElementById("label_edit_id").innerHTML=a:document.getElementById("label_edit_id").innerHTML="000000";document.getElementById("title_item").innerHTML=k;document.getElementById("rate_ratetype").value=b;$("select#rate_ratetype").selectmenu("refresh");document.getElementById("rate_ratedate").value=c;document.getElementById("rate_curr").value=d;$("select#rate_curr").selectmenu("refresh");document.getElementById("rate_ratevalue").value=
g;"None"!=f?(document.getElementById("rate_rategroup").value=f,$("select#rate_rategroup").selectmenu("refresh")):document.getElementById("rate_rategroup").value="";"None"!=e?(document.getElementById("rate_place_id").value=e,$("select#rate_place_id").selectmenu("refresh")):document.getElementById("rate_place_id").value="";document.getElementById("view_page").style.display="none";document.getElementById("ctr_view_page").style.display="none";document.getElementById("edit_page").style.display="block";
document.getElementById("ctr_edit_page").style.display="block";document.getElementById("rate_ratevalue").focus();return!0}
function rate_update(){if(""==document.getElementById("rate_ratetype").value)return alert(ms_err_rate_missing_ratetype),!1;if(""==document.getElementById("rate_ratedate").value)return alert(ms_err_rate_missing_ratedate),!1;if(""==document.getElementById("rate_curr").value)return alert(ms_err_missing_curr),!1;""==document.getElementById("rate_ratevalue").value&&(document.getElementById("rate_ratevalue").value=0);document.forms.frm_edit.submit()}
function set_movement(a,b,c,d,e,f,g,k,h,l,m){document.getElementById("movement_id").value=a;-1!=a?document.getElementById("label_movement_id").innerHTML=a:document.getElementById("label_movement_id").innerHTML="000000";document.getElementById("tool_id")?(document.getElementById("tool_id").value=e,document.getElementById("tool_serial").innerHTML=f,document.getElementById("movement_shippingdate").value=b):(document.getElementById("movement_qty").value=g,document.getElementById("product_id").value=c,
document.getElementById("product_description").innerHTML=d,document.getElementById("place_id")?(document.getElementById("movement_shippingdate").value=document.getElementById("trans_transdate").value,document.getElementById("shippingdate").value=document.getElementById("trans_transdate").value+" 00:00:00",document.getElementById("movement_place_id").value=document.getElementById("place_id").value,document.getElementById("movement_place_planumber").innerHTML=document.getElementById("place_planumber").innerHTML):
(document.getElementById("shippingdate").value=b,document.getElementById("movement_place_id").value=h,document.getElementById("movement_place_planumber").innerHTML=l,document.getElementById("movement_shared")&&document.getElementById("movement_shared")&&(document.getElementById("movement_shared").value=m,$("input#movement_shared").prop("checked",1==m).checkboxradio("refresh"))));document.getElementById("movement_notes").value=k;document.getElementById("movement_page").style.display="none";document.getElementById("ctr_movement_page").style.display=
"none";null!=document.getElementById("ctr_local_menu")&&(document.getElementById("ctr_local_menu").style.display="none");document.getElementById("movement_edit").style.display="block";document.getElementById("ctr_movement_edit").style.display="block";document.getElementById("tool_id")?document.getElementById("movement_shippingdate").focus():document.getElementById("movement_qty").focus();return!0}
function movement_update(){if(document.getElementById("tool_id")){if(""==document.getElementById("tool_id").value)return alert(ms_err_movement_tool),!1}else{if(""==document.getElementById("product_id").value)return alert(ms_err_movement_product),!1;"None"==document.getElementById("movement_place_id").value&&(document.getElementById("movement_place_id").value="");if(null==document.getElementById("movement_shared")&&""==document.getElementById("movement_place_id").value)return alert(ms_err_movement_warehouse),
!1}if(document.getElementById("target_place_id")){if(""==document.getElementById("target_place_id").value)return alert(ms_err_movement_target_warehouse),!1;if(document.getElementById("target_place_id").value==document.getElementById("movement_place_id").value)return alert(ms_err_movement_diff_warehouse),!1}if(document.getElementById("shippingdate")&&""==document.getElementById("shippingdate").value)return alert(ms_err_movement_shipping),!1;""==document.getElementById("movement_qty").value&&(document.getElementById("movement_qty").value=
0);document.forms.frm_movement.submit()}
function load_formula(){if(""==document.getElementById("production_product_id").value)return alert(ms_err_movement_product),!1;if(1==document.getElementById("cmb_formula").disabled)return alert(ms_err_movement_save),!1;if(0>=document.getElementById("cmb_formula").selectedIndex)return alert(ms_err_movement_formula),!1;var a=document.getElementById("cmb_formula").value;if(0==confirm(ms_err_movement_load_formula))return!1;a=get_base_url()+"/cmd_get_formula?production_id="+document.getElementById("production_production_id").value+
"&formula_id="+a;jQuery.ajax({type:"POST",url:a,success:function(a){"OK"==a?location.reload(!0):alert(ms_err_movement_load_formula_err)}})}function copy_trans(a,b){jQuery.ajax({type:"POST",url:a,success:function(a){"ok"==a.split("|")[0]?window.location=b+a.split("|")[1]:alert(a.split("|")[2])}})}
function create_newtype_change(){var a=document.getElementById("cmb_doctypes").value,b=document.getElementById("base_transtype").value,c=document.getElementById("element_count").value;"invoice"==a||"receipt"==a?$("input#cb_netto").checkboxradio("enable"):$("input#cb_netto").checkboxradio("disable");"invoice"!=a&&"receipt"!=a||"order"!=b&&"rent"!=b&&"worksheet"!=b||"0"!=c?$("input#cb_from").checkboxradio("disable"):$("input#cb_from").checkboxradio("enable")}
function from_delivery_change(){document.getElementById("cb_from").checked?$("input#cb_netto").checkboxradio("disable"):$("input#cb_netto").checkboxradio("enable")}
function create_trans(a,b){a+="&new_transtype="+document.getElementById("cmb_doctypes").value;a+="&new_direction="+document.getElementById("cmb_directions").value;a=document.getElementById("cb_netto").checked&&0==document.getElementById("cb_netto").disabled?a+"&netto_qty=1":a+"&netto_qty=0";a=document.getElementById("cb_from").checked&&0==document.getElementById("cb_from").disabled?a+"&from_inventory=1":a+"&from_inventory=0";jQuery.ajax({type:"POST",url:a,success:function(a){"ok"==a.split("|")[0]?
window.location=b+a.split("|")[1]:alert(a.split("|")[2])}});return!0}function show_report(a){for(var b=document.forms.frm_report,c=0;c<b.elements.length;c++)if("rq_"==b.elements[c].name.substr(0,3)&&b.elements[c].checked){var d="report_"+b.elements[c].name.substring(3);if(""==document.getElementById(d).value)return alert(a+": "+document.getElementById(d+"__label").innerHTML.replace("*","").replace(":","")),!1}document.forms.frm_report.submit()}
function create_delivery_items(){var a=document.getElementById("place_id");if(""==a.value)return alert(ms_err_missing_wh),!0;var b=document.getElementById("shippingdate");if(""==b.value)return alert(ms_err_missing_date),!0;var c=document.getElementById("trans_id").value,a=get_base_url()+"/frm_shipping/edit/trans/"+c+"?create_items=true&create_place_id="+a.value+"&create_date="+b.value;jQuery.ajax({type:"POST",url:a,success:function(a){"OK"==a&&window.location.reload()}});return!0}
function set_delivery(a,b,c,d,e){document.getElementById("item_id").value=a;document.getElementById("product_id").value=b;document.getElementById("partnumber").innerHTML=a+" | "+c;a=document.getElementById("batch");a.value=d;document.getElementById("qty").value=e;document.getElementById("edit_item");$("#popup_edit_item").popup("open");a.focus();return!0}
function update_delivery(){var a=document.getElementById("trans_id").value,b=document.getElementById("item_id").value,c=document.getElementById("product_id").value,d=document.getElementById("batch").value,e=document.getElementById("qty").value,a=get_base_url()+"/frm_shipping/edit/trans/"+a+"?edit_item_id="+b+"&edit_product_id="+c+"&edit_batch="+d+"&edit_qty="+e;jQuery.ajax({type:"POST",url:a,success:function(a){if(""!=a)return $("#items_table").html(a).trigger("create"),!0}})}
function add_delivery(a,b,c,d){"*"!=d&&(d=document.getElementById("trans_id").value,a=get_base_url()+"/frm_shipping/edit/trans/"+d+"?add_item_id="+a+"&add_product_id="+b+"&add_qty="+c,jQuery.ajax({type:"POST",url:a,success:function(a){"OK"==a&&window.location.reload()}}))}
function del_delivery(a,b){var c=document.getElementById("trans_id").value,c=get_base_url()+"/frm_shipping/edit/trans/"+c+"?del_item_id="+a+"&del_product_id="+b;jQuery.ajax({type:"POST",url:c,success:function(a){"OK"==a&&window.location.reload()}})}function add_all_delivery(){var a=document.getElementById("trans_id").value,a=get_base_url()+"/frm_shipping/edit/trans/"+a+"?add_all=true";jQuery.ajax({type:"POST",url:a,success:function(a){"OK"==a&&window.location.reload()}})}
function remove_all_delivery(){var a=document.getElementById("trans_id").value,a=get_base_url()+"/frm_shipping/edit/trans/"+a+"?del_all=true";jQuery.ajax({type:"POST",url:a,success:function(a){"OK"==a&&window.location.reload()}})}
function set_default_template(){var a=document.getElementById("cmb_temp");if(""==a.value)alert(ms_wn_chosen);else if(confirm(ms_wn_conf)){var b=document.getElementById("trans_id").value;jQuery.ajax({type:"POST",url:get_base_url()+"/frm_trans_fnote/"+b+"?def_tmp_value="+a.value+"&def_tmp_name="+a.options[a.selectedIndex].text,success:function(b){a.title=title_def+a.options[a.selectedIndex].text}})}return!0}
function save_template(){var a=document.getElementsByName("fnote")[0],b=document.getElementById("cmb_temp");if(""==b.value)alert(ms_wn_chosen);else if(confirm(ms_wn_save)){var c=document.getElementById("trans_id").value,a=get_base_url()+"/frm_trans_fnote/"+c+"?save_tmp_value="+b.value+"&save_tmp_name="+b.options[b.selectedIndex].text+"&fnote="+encodeURIComponent($("#"+a.id).val());jQuery.ajax({type:"POST",url:a,success:function(a){}})}return!0}
function delete_template(){var a=document.getElementById("cmb_temp");if(""==a.value)alert(ms_wn_chosen);else if(confirm(ms_wn_delete)){var b=document.getElementById("trans_id").value,a=get_base_url()+"/frm_trans_fnote/"+b+"?del_tmp_value="+a.value+"&del_tmp_name="+a.options[a.selectedIndex].text;jQuery.ajax({type:"POST",url:a,success:function(a){window.location.reload()}})}return!0}
function new_template(){var a=document.getElementById("new_tempdesc");document.getElementById("cmb_temp");document.getElementById("irow");if(""==a.value)alert(ms_err_new);else if(get_tmp_opt(a.value)){var b=document.getElementById("trans_id").value,a=get_base_url()+"/frm_trans_fnote/"+b+"?new_tmp="+a.value;jQuery.ajax({type:"POST",url:a,success:function(a){window.location.reload()}})}return!0}
function get_tmp_opt(a){for(var b=document.getElementById("cmb_temp"),c=0;c<b.options.length;c++)if(b.options[c].innerText==a)return alert(ms_er_exists),!1;return!0}
function loadTemplate(){var a=document.getElementById("cmb_temp"),b=document.getElementById("trans_id").value,a=get_base_url()+"/frm_trans_fnote/"+b+"?load_tmp_value="+a.value+"&load_tmp_name="+a.options[a.selectedIndex].text;jQuery.ajax({type:"POST",url:a,success:function(a){""==a&&(a=" ");var b=document.getElementsByName("fnote")[0];$("#"+b.id).jqteVal(a)}})}
function create_report(a,b){if(""==document.getElementById("cmb_templates").value)return alert(b),!0;if(null==document.getElementById("dlg_report_cmd")){var c=document.createElement("input");c.setAttribute("id","dlg_report_cmd");c.setAttribute("type","hidden");c.setAttribute("name","cmd");document.forms.dlg_frm_report.appendChild(c)}document.getElementById("dlg_report_cmd").value=a;document.forms.dlg_frm_report.submit()}
function pdf_export(a,b,c,d,e,f,g){jQuery.ajax({type:"POST",data:{get_report:!0,report_id:c,ref_id:d,orientation:e,size:f},success:function(c){jQuery.ajax({type:"POST",url:"http://"+b,data:{cmd:"export",file:c,filename:g.replace(/\'/g,"")+".pdf",dir:"export",encode:"base64"},success:function(b){"OK"==b?set_task(a):set_task(a,b)},error:function(b,c,d){set_task(a,ms_err_local_printer)}})},error:function(b,c,d){set_task(a,ms_err_local_printer)}})}
function pdf_printing(a,b,c,d,e,f,g,k,h){jQuery.ajax({type:"POST",data:{get_report:!0,report_id:c,ref_id:d,orientation:e,size:f},success:function(c){jQuery.ajax({type:"POST",url:"http://"+b,data:{cmd:"print",file:c,filename:h.replace(/\'/g,"")+".pdf",printer:k,copies:g,size:f,orientation:e,encode:"base64"},success:function(b){"OK"==b?set_task(a):set_task(a,b)},error:function(b,c,d){set_task(a,ms_err_local_printer)}})},error:function(b,c,d){set_task(a,ms_err_local_printer)}})}
function printer_settings(a,b,c){var d=null;jQuery.ajax({type:"POST",url:"http://"+a,async:!1,data:{cmd:"printers",orientation:b,size:c},success:function(a){""!=a&&(d=a.split("|"))},error:function(a,b,c){alert(ms_err_local_printer)}});return d}var local_tasks={};
function set_task(a,b){local_tasks.hasOwnProperty(a)&&!local_tasks[a].cancel&&(null!=b?(local_tasks[a].cancel=!0,alert(b)):(local_tasks[a].current+=1,local_tasks[a].total==local_tasks[a].current&&(local_tasks[a].cancel=!0,jQuery.ajax({type:"POST",data:{delete_rows:!0,rows:local_tasks[a].rows},success:function(a){"OK"==a&&location.reload()},error:function(a,b,e){}}),-1<a.indexOf("local")?alert(ms_ok_print.replace("%",local_tasks[a].total)):alert(ms_ok_export.replace("%",local_tasks[a].total)))))}
function local_printing(a){jQuery.ajax({type:"POST",data:$("#frm_print_filter").serialize(),success:function(b){printer_type=document.getElementById("cmb_printer_type").value;if(""!=b){rows=b.split("|");if(0==rows.length)return!1;var c=printer_type+(new Date).getTime().toString();local_tasks[c]={};local_tasks[c].rows=b;local_tasks[c].cancel=!1;local_tasks[c].total=rows.length;local_tasks[c].current=0;b="";var d=1,e=document.getElementById("cmb_orientation").value,f=document.getElementById("cmb_size").value;
if("local"==printer_type){if(e=printer_settings(a,e,f)){b=e[0];for(var d=e[1],f=e[2],e=e[3],g=0;g<rows.length;g++)item=rows[g].split(","),pdf_printing(c,a,item[1],item[2],e,f,d,b,item[4]+"_"+item[0])}}else for(g=0;g<rows.length;g++)item=rows[g].split(","),pdf_export(c,a,item[1],item[2],e,f,item[4]+"_"+item[0])}},error:function(a,c,d){alert(ms_err_local_printer);return!0}})}
function print_items(a,b){if(null==document.getElementById("selmode")){var c=document.createElement("input");c.setAttribute("id","selmode");c.setAttribute("type","hidden");c.setAttribute("name",a);c.setAttribute("value","true");document.forms.frm_print_filter.appendChild(c)}else document.getElementById("selmode").setAttribute("name",a);if("server"!=document.getElementById("cmb_printer_type").value)jQuery.ajax({type:"POST",url:"http://"+b,data:{cmd:"vernum"},contentType:"application/x-www-form-urlencoded; charset=UTF-8",
success:function(a){local_printing(b)},error:function(a,b,c){alert(ms_err_missing_local_printer_support);window.location.reload()}});else{if(""==document.getElementById("cmb_printers").value)return alert(ms_err_missing_printer),!0;document.forms.frm_print_filter.submit()}}
function set_filter_values(){null!=document.getElementById("selmode")&&document.getElementById("selmode").setAttribute("name","filter");document.getElementById("nervatype").value=document.getElementById("filter_nervatype").value;document.getElementById("transnumber").value=document.getElementById("filter_transnumber").value;document.getElementById("fromdate").value=document.getElementById("filter_fromdate").value;document.getElementById("enddate").value=document.getElementById("filter_enddate").value;
document.getElementById("username").value=document.getElementById("filter_username").value;document.getElementById("printer_type").value=document.getElementById("cmb_printer_type").value;document.getElementById("printer").value=document.getElementById("cmb_printers").value;document.getElementById("size").value=document.getElementById("cmb_size").value;document.getElementById("orientation").value=document.getElementById("cmb_orientation").value}
function getParameterByName(a){var b=document.URL;a=b.indexOf(a);sub=b.substring(a);amper=sub.indexOf("&");eq=sub.indexOf("=");return-1<a&&-1<eq?("-1"==amper?sub.split("="):sub.substr(0,amper).split("="))[1]:""}
function page_ini(){for(var a="",b=document.getElementsByName("pages"),c=0;c<b.length;c++)""!=getParameterByName(b[c].id)&&(a=b[c].id);""==a&&null!=document.getElementById("active_page")&&null!=document.getElementById(document.getElementById("active_page").value)&&(a=document.getElementById("active_page").value);""!=a&&show_page(a)}
function show_page(a){for(var b=document.getElementsByName("pages"),c=0;c<b.length;c++)b[c].style.display=b[c].id==a?"block":"none",null!=document.getElementById("ctr_"+b[c].id)&&(document.getElementById("ctr_"+b[c].id).style.display=b[c].style.display);null!=document.getElementById("ctr_local_menu")&&(document.getElementById("ctr_local_menu").style.display="block");return!0}
function show_div(a,b){for(var c=document.getElementsByName("divs"),d=0;d<c.length;d++)c[d].style.display=c[d].id==a?"block":"none";null!=b&&null!=document.getElementById("divs_title")&&(document.getElementById("divs_title").innerHTML=b);return!0};