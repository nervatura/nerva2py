
function get_base_url() {
	return window.location.protocol+'//'+window.location.host+"/"+document.getElementById('appl_url').className;
}

//--------------------------------------------------
//index
//--------------------------------------------------
function call_menucmd(_menukey,new_window) {
	url_str = get_base_url()+'/frm_custom_menu/_menukey';
	url_str = url_str.replace("_menukey",_menukey);
	if (new_window==1) {
		window.open(url_str,'_blank');
	} else {
		window.location = url_str;
	}
}
//--------------------------------------------------
//general nervatype selectors
//--------------------------------------------------
function set_customer_value(_customer_id, _custnumber, _custname) {
	if (document.getElementById('edit_fieldvalue')!=null) {
		if (document.getElementById('edit_fieldvalue').style.display == 'block') {
			document.getElementById("fieldvalue_value").value = _customer_id;
			document.getElementById("fieldvalue_value_customer_label").innerHTML = _custname;
			return true;
		}
	}
	document.getElementById("customer_id").value = _customer_id;
	document.getElementById("customer_custname").innerHTML = _custname;
	return true;
}

function set_tool_value(_tool_id, _serial, _description) {
	if (document.getElementById('edit_fieldvalue')!=null) {
		if (document.getElementById('edit_fieldvalue').style.display == 'block') {
			document.getElementById("fieldvalue_value").value = _tool_id;
			document.getElementById("fieldvalue_value_tool_label").innerHTML = _serial;
			return true;
		}
	}
	document.getElementById("tool_id").value = _tool_id;
	document.getElementById("tool_serial").innerHTML = _serial;
	return true;
}

function set_product_value(_product_id, _partnumber, _description, _unit, _tax_id) {
	if (document.getElementById('cmb_formula')) {
		document.getElementById("cmb_formula").selectedIndex=0;
		document.getElementById("cmb_formula").disabled=true;
	}
	if (document.getElementById('edit_item')!=null) {
		if (document.getElementById('edit_item').style.display == 'block') {
			document.getElementById("product_id").value = _product_id;
			document.getElementById("product_description").innerHTML = _description;
			document.getElementById("item_description").value = _description;
			document.getElementById("item_unit").value = _unit;
			document.getElementById("item_tax_id").value = _tax_id;
			$('select#item_tax_id').selectmenu("refresh");
			document.getElementById("item_rate").value=rate_lst[document.getElementById("item_tax_id").selectedIndex-1];
			calc_price('fxprice');
			load_price(_product_id);
			return true;
		}
	}
	if (document.getElementById('edit_fieldvalue')!=null) {
		if (document.getElementById('edit_fieldvalue').style.display == 'block') {
			document.getElementById("fieldvalue_value").value = _product_id;
			document.getElementById("fieldvalue_value_product_label").innerHTML = _description;
			return true;
		}
	}
	if (document.getElementById('production_product_id')!=null) {
		if (document.getElementById('trans_page').style.display == 'block') {
			document.getElementById("production_product_id").value = _product_id;
			document.getElementById("production_product_label").innerHTML = _description;
			return true;
		}
	}
	document.getElementById("product_id").value = _product_id;
	document.getElementById("product_description").innerHTML = _description;
	return true;
}

function set_transitem_value(_trans_id, _transnumber, _transtype, _direction, _curr) {
	if (document.getElementById('link_edit')!=null) {
		if (document.getElementById('link_edit').style.display == 'block') {
			document.getElementById("ref_id_2").value = _trans_id;
			document.getElementById("link_transnumber").innerHTML = _transnumber;
			if (document.getElementById('trans_curr')!=null) {
				document.getElementById("trans_curr").innerHTML= _curr;	
			}
			return true;
		}
	}
	if (document.getElementById('edit_fieldvalue')!=null) {
		if (document.getElementById('edit_fieldvalue').style.display == 'block') {
			document.getElementById("fieldvalue_value").value = _trans_id;
			document.getElementById("fieldvalue_value_transitem_label").innerHTML = _transnumber;
			return true;
		}
	}
	document.getElementById("trans_id").value = _trans_id;
	document.getElementById("reftrans_transnumber").innerHTML = _transnumber;
	return true;
}

function set_transmovement_value(_trans_id, _transnumber, _transtype, _direction) {
	if (document.getElementById('edit_fieldvalue')!=null) {
		if (document.getElementById('edit_fieldvalue').style.display == 'block') {
			document.getElementById("fieldvalue_value").value = _trans_id;
			document.getElementById("fieldvalue_value_transmovement_label").innerHTML = _transnumber;
			return true;
		}
	}
	document.getElementById("trans_id").value = _trans_id;
	document.getElementById("reftrans_transnumber").innerHTML = _transnumber;
	return true;
}

function set_transpayment_value(_trans_id, _transnumber, _transtype, _curr) {
	if (document.getElementById('edit_fieldvalue')!=null) {
		if (document.getElementById('edit_fieldvalue').style.display == 'block') {
			document.getElementById("fieldvalue_value").value = _trans_id;
			document.getElementById("fieldvalue_value_transpayment_label").innerHTML = _transnumber;
			return true;
		}
	}
	document.getElementById("trans_id").value = _trans_id;
	document.getElementById("reftrans_transnumber").innerHTML = _transnumber;
	return true;
}

function set_project_value(_project_id, _pronumber, _description) {
	if (document.getElementById('edit_fieldvalue')!=null) {
		if (document.getElementById('edit_fieldvalue').style.display == 'block') {
			document.getElementById("fieldvalue_value").value = _project_id;
			document.getElementById("fieldvalue_value_project_label").innerHTML = _pronumber;
			return true;
		}
	}
    document.getElementById("project_id").value = _project_id;
    document.getElementById("project_pronumber").innerHTML = _pronumber;
    return true;
}

function set_employee_value(_employee_id, _empnumber, _username) {
	if (document.getElementById('edit_fieldvalue')!=null) {
		if (document.getElementById('edit_fieldvalue').style.display == 'block') {
			document.getElementById("fieldvalue_value").value = _employee_id;
			document.getElementById("fieldvalue_value_employee_label").innerHTML = _empnumber;
			return true;
		}
	}
    document.getElementById("employee_id").value = _employee_id;
    document.getElementById("employee_empnumber").innerHTML = _empnumber;
    return true;
}

function set_place_value(_place_id, _planumber, _description, _curr) {
	if (document.getElementById('edit_fieldvalue')!=null) {
		if (document.getElementById('edit_fieldvalue').style.display == 'block') {
			document.getElementById("fieldvalue_value").value = _place_id;
			document.getElementById("fieldvalue_value_place_label").innerHTML = _planumber;
			return true;
		}
	}
	if (document.getElementById('movement_edit')!=null) {
		if (document.getElementById('movement_edit').style.display == 'block') {
			document.getElementById("movement_place_id").value = _place_id;
			document.getElementById("movement_place_planumber").innerHTML = _planumber;
			return true;
		}
	}
	if (document.getElementById('production_place_id')!=null) {
		if (document.getElementById('trans_page').style.display == 'block') {
			document.getElementById("production_place_id").value = _place_id;
			document.getElementById("production_place_label").innerHTML = _planumber;
			return true;
		}
	}
	document.getElementById("place_id").value = _place_id;
	document.getElementById("place_planumber").innerHTML = _planumber;
	if (document.getElementById('place_curr')!=null) {
		document.getElementById("place_curr").innerHTML = _curr;}
	return true;
}
function set_place_value2(_place_id, _planumber, _description, _curr) {
    document.getElementById("target_place_id").value = _place_id;
    document.getElementById("target_place_planumber").innerHTML = _planumber;
    return true;
}

//invoice-payment link: trans_invoice
function set_payment_value(_payment_id, _transnumber, _transtype, _curr, _amount) {
    document.getElementById("ref_id_1").value = _payment_id;
    document.getElementById("label_link_id").innerHTML = _payment_id;
    document.getElementById("link_transnumber").innerHTML = _transnumber;
    document.getElementById("link_curr").innerHTML = _curr;
    document.getElementById("link_amount").value= _amount;
    return true;
}

//--------------------------------------------------
//fieldvalue rows: trans_item, trans_payment, trans_movement
//--------------------------------------------------
function set_fieldvalue(_fieldvalue_id, _fieldname, _description, _value, _label, _notes, _fieldtype, _valuelist, _readonly) {

	if (_fieldvalue_id==-1) {
		if (document.getElementById("cmb_fields").value=="") {
			alert(ms_err_field_new);
			return true;
		}
		var fldpar = document.getElementById("cmb_fields").value.split("~")
		_fieldname = fldpar[0];
		_description = document.getElementById("cmb_fields").children[document.getElementById("cmb_fields").selectedIndex].text;
		_fieldtype = fldpar[1];
		switch(_fieldtype) {
		case "bool":
			_value = "false";
			break;
		case "integer":
		case "float":
			_value = 0;
			break;
		}
		if (fldpar[2]!="None") {
			_valuelist = fldpar[2];
		}
	}
	document.getElementById("fieldvalue_id").value= _fieldvalue_id;
	document.getElementById("fieldvalue_fieldname").value= _fieldname;
	document.getElementById("fieldvalue_fieldtype").value= _fieldtype;
	document.getElementById("fieldvalue_description").innerHTML = _description;
	document.getElementById("fieldvalue_notes").innerHTML = _notes;
	document.getElementById("fieldvalue_readonly").value = _readonly;
	document.getElementById("fieldvalue_value").value ="";

	var value_controls = document.getElementById("fieldvalue_value_controls").children;
	for (var i=0;i<value_controls.length;i++) {
		value_controls[i].style.display = 'none';
	}

	var control = null;
	var _focus = document.getElementById("fieldvalue_notes");
	if (document.getElementById("fieldvalue_value_"+_fieldtype)!=null) {
		control = document.getElementById("fieldvalue_value_"+_fieldtype);
	} else {
		control = document.getElementById("fieldvalue_value_text");}
	
	switch(control.nodeName) {
	case "DIV":
		document.getElementById("fieldvalue_value_"+_fieldtype+"_label").innerHTML = _label;
		document.getElementById("fieldvalue_value").value =_value;
		_focus = document.getElementById("fieldvalue_notes");
		break;
	case "INPUT":
	case "TEXTAREA":
		if (_fieldtype=="bool") {
			document.getElementById("fieldvalue_value_bool_label").style.display = 'block';
			$("input#fieldvalue_value_bool").prop("checked",(_value=="true")).checkboxradio("refresh");
			document.getElementById("fieldvalue_value_bool_text").innerHTML =_description;
			document.getElementById("fieldvalue_description").style.display = 'none';
		} else {
			control.value = _value;	
		}
		_focus = control;
		break;
	case "SELECT":
		while (control.options.length> 0) {
			control.options.remove(0);
		}
		options = _valuelist.split("|");
		for (var i=0;i<options.length;i++) {
			if (options[i]==_value) {
				control.options.add(new Option(options[i],options[i],true,true));
			} else {
				control.options.add(new Option(options[i]));}
		}
		$('select#fieldvalue_value_valuelist').selectmenu("refresh");
		break;
	default:
	}
	control.style.display = 'block';
	control.parentElement.style.display = 'block';
	control.parentElement.parentElement.style.display = 'block';
  
	document.getElementById('fieldvalue_page').style.display = 'none';
	document.getElementById('ctr_fieldvalue_page').style.display = 'none';
	if (document.getElementById('ctr_local_menu')!=null) {
		document.getElementById('ctr_local_menu').style.display = "none";}
	document.getElementById('edit_fieldvalue').style.display = 'block';
	document.getElementById('ctr_edit_fieldvalue').style.display = 'block';
	_focus.focus();
	return true;
}

function fieldvalue_update(){
	
	if (document.getElementById("fieldvalue_readonly").value=="1") {
		alert(ms_err_field_update);
		return false;
	}
	var _fieldtype = document.getElementById("fieldvalue_fieldtype").value;
	var control = null;
	if (document.getElementById("fieldvalue_value_"+_fieldtype)!=null) {
		control = document.getElementById("fieldvalue_value_"+_fieldtype);
	} else {
		control = document.getElementById("fieldvalue_value_text");}
	switch(control.nodeName) {
	case "INPUT":
		switch(_fieldtype) {
		case "bool":
			if (control.checked==true) {
				document.getElementById("fieldvalue_value").value ="true";
			} else {
				document.getElementById("fieldvalue_value").value ="false";
			}
			break;
		case "integer":
		case "float":
			if (control.value=="") {
				document.getElementById("fieldvalue_value").value =0;
			} else {
				document.getElementById("fieldvalue_value").value =control.value;
			}
			break;
		default:
			document.getElementById("fieldvalue_value").value =control.value;
		}
		break;
	case "TEXTAREA":
		document.getElementById("fieldvalue_value").value =control.value;
		break;
	case "SELECT":
		document.getElementById("fieldvalue_value").value =control.value;
		break;
	}
	
	document.forms["frm_fieldvalue"].submit();
}

//--------------------------------------------------
//item rows: trans_item
//--------------------------------------------------

function set_item(_item_id, _product_id, _product, _tax_id, _rate, _vatamount, _digit, _description, _deposit, _qty,
		_discount, _fxprice, _unit, _netamount, _amount, _ownstock){
	
	document.getElementById("item_id").value= _item_id;
	if (_item_id!=-1) {
		document.getElementById("label_item_id").innerHTML = _item_id;}
	else {
		document.getElementById("label_item_id").innerHTML = "000000";}
	document.getElementById("product_id").value = _product_id;
	document.getElementById("product_description").innerHTML = _product;
	document.getElementById("item_tax_id").value=_tax_id;
	$('select#item_tax_id').selectmenu("refresh");
	document.getElementById("item_rate").value=_rate;
	document.getElementById("item_vatamount").value=_vatamount;
	document.getElementById("curr_digit").value=_digit;
	document.getElementById("item_description").value=_description;
	if (document.getElementById("item_deposit")) {
		document.getElementById("item_deposit").value=_deposit;
		$("input#item_deposit").prop( "checked",(_deposit==1)).checkboxradio("refresh");}
	document.getElementById("item_qty").value=_qty;
	document.getElementById("item_discount").value=_discount;
	document.getElementById("item_fxprice").value=_fxprice;
	document.getElementById("item_unit").value=_unit;
	document.getElementById("item_netamount").value=_netamount;
	document.getElementById("item_amount").value=_amount;
	document.getElementById("item_ownstock").value=_ownstock;
  
	document.getElementById('item_page').style.display = 'none';
	document.getElementById('ctr_item_page').style.display = 'none';
	if (document.getElementById('ctr_local_menu')!=null) {
		document.getElementById('ctr_local_menu').style.display = "none";}
	document.getElementById('edit_item').style.display = 'block';
	document.getElementById('ctr_edit_item').style.display = 'block';
	document.getElementById("item_description").focus();
	return true;
}

function item_update(){
	if (document.getElementById("product_id").value=="") {
		alert(ms_err_item_update_product);
		return false;}
	if (document.getElementById("item_description").value=="") {
		alert(ms_err_item_update_description);
		return false;}
	if (document.getElementById("item_tax_id").value=="") {
		alert(ms_err_item_update_tax);
		return false;}
	document.forms["frm_item"].submit();
}

function load_price() {
	var product_id=document.getElementById("product_id");
	var qty=document.getElementById("item_qty");
	var fxprice=document.getElementById("item_fxprice");
	var trans_id=document.getElementById("item_trans_id").value;	
	var surl = get_base_url()+'/cmd_get_price?trans_id='+trans_id+'&product_id='+product_id.value+'&qty='+qty.value;
	jQuery.ajax({
		type: "POST",
		url: surl,
		success: function(data) {
			if (parseFloat(data)!=0) {
				fxprice.value = data;
				if (parseFloat(qty.value)==0) {
					qty.value = 1;
				}
				calc_price("fxprice");
			}
		}
	});
}
function _round(n,dec) {
	n = parseFloat(n);
	if(!isNaN(n)){
		if(!dec) var dec= 0;
		var factor= Math.pow(10,dec);
		return Math.floor(n*factor+((n*factor*10)%10>=5?1:0))/factor;
	}else{
		return n;}
}
function getNumObj(id) {
	if (document.getElementById(id).value=="") {
		document.getElementById(id).value=0;}
	return document.getElementById(id);
}
function calc_price(_calcmode) {
	var fxprice=getNumObj("item_fxprice");
	var qty=getNumObj("item_qty");
	var netamount=getNumObj("item_netamount");
	var amount=getNumObj("item_amount");
	var vatamount=getNumObj("item_vatamount");
	var rate=getNumObj("item_rate");
	var discount=getNumObj("item_discount");
	var digit=getNumObj("curr_digit");
	switch(_calcmode) {
	case "fxprice":
		netamount.value = _round(parseFloat(fxprice.value)*(1-parseFloat(discount.value)/100)*parseFloat(qty.value),parseInt(digit.value));
		vatamount.value = _round(parseFloat(netamount.value)*parseFloat(rate.value),parseInt(digit.value));
		amount.value = parseFloat(netamount.value) + parseFloat(vatamount.value);
		break;
	case "netamount":
		if (parseFloat(qty.value)==0) {
			fxprice.value = 0;
			vatamount.value = 0;
		} else {
			fxprice.value = _round(parseFloat(netamount.value)/(1-parseFloat(discount.value)/100)/parseFloat(qty.value),parseInt(digit.value));
			vatamount.value = _round(parseFloat(netamount.value)*parseFloat(rate.value),parseInt(digit.value));}
		amount.value = parseFloat(netamount.value) + parseFloat(vatamount.value);
		break;
	case "amount":
		if (parseFloat(qty.value)==0) {
			fxprice.value = 0;
			netamount.value = 0;
			vatamount.value = 0;
		} else {
			netamount.value = _round(parseFloat(amount.value)/(1+parseFloat(rate.value)),parseInt(digit.value));
			vatamount.value = parseFloat(amount.value) - parseFloat(netamount.value);
			fxprice.value = _round(parseFloat(netamount.value)/(1-parseFloat(discount.value)/100)/parseFloat(qty.value),parseInt(digit.value));}
		break;
	default:
	}
}

//--------------------------------------------------
//payment rows: trans_payment
//--------------------------------------------------
function set_payment(_payment_id, _paiddate, _amount, _notes){
	document.getElementById("payment_id").value= _payment_id;
	if (_payment_id!=-1) {
		document.getElementById("label_payment_id").innerHTML = _payment_id;
	}
	else {
		document.getElementById("label_payment_id").innerHTML = "000000";}
	
	document.getElementById("payment_paiddate").value = _paiddate;
	document.getElementById("payment_amount").value = _amount;
	document.getElementById("payment_notes").value = _notes;
  
	document.getElementById('payment_page').style.display = 'none';
  document.getElementById('ctr_payment_page').style.display = 'none';
  if (document.getElementById('ctr_local_menu')!=null) {
	  document.getElementById('ctr_local_menu').style.display = "none";}
  document.getElementById('payment_edit').style.display = 'block';
  document.getElementById('ctr_payment_edit').style.display = 'block';
	document.getElementById("payment_paiddate").focus();
	return true;
}

function payment_update(){
if (document.getElementById("payment_paiddate").value=="") {
  alert(ms_err_payment_paiddate);
  return false;}
if (document.getElementById("payment_amount").value=="") {
  document.getElementById("payment_amount").value=0;}
document.forms["frm_payment"].submit();
}

//--------------------------------------------------
//invoice-payment link rows: trans_item, trans_payment
//--------------------------------------------------
function set_link_invoice(_link_id,_ref_id_1,_ref_id_2,_transnumber,_curr,_amount,_rate){
	document.getElementById("link_invoice_id").value= _link_id;
	if (_link_id!=-1) {
	  document.getElementById("label_link_id").innerHTML = _ref_id_1;}
	else {
	  document.getElementById("label_link_id").innerHTML = "000000";}
	document.getElementById("ref_id_1").value= _ref_id_1;
	document.getElementById("ref_id_2").value= _ref_id_2;
	document.getElementById("link_transnumber").innerHTML= _transnumber;
	document.getElementById("link_curr").innerHTML= _curr;
	document.getElementById("link_amount").value= _amount;
	document.getElementById("link_rate").value= _rate;

	document.getElementById('link_page').style.display = 'none';
	document.getElementById('ctr_link_page').style.display = 'none';
	if (document.getElementById('payment_edit')!=null) {
		  document.getElementById('payment_edit').style.display = 'none';
		  document.getElementById('ctr_payment_edit').style.display = 'none';  
	}
	if (document.getElementById('ctr_local_menu')!=null) {
		document.getElementById('ctr_local_menu').style.display = "none";}
	document.getElementById('link_edit').style.display = 'block';
	document.getElementById('ctr_link_edit').style.display = 'block';
	document.getElementById("link_amount").focus();
	return true;
}
function link_invoice_update(){
	if (document.getElementById("ref_id_1").value=="") {
		alert(ms_err_link_invoice_rfid_1);
		return false;}
	if (document.getElementById("ref_id_2").value=="") {
		alert(ms_err_link_invoice_rfid_2);
		return false;}
	if (document.getElementById("link_amount").value=="") {
		document.getElementById("link_amount").value=0;}
	if (document.getElementById("link_rate").value=="") {
		document.getElementById("link_rate").value=1;}
		document.forms["frm_link_invoice"].submit();
}

//--------------------------------------------------
//barcode rows: product
//--------------------------------------------------
function set_barcode(_barcode_id,_code,_description,_barcodetype,_qty,_defcode) {
	document.getElementById("barcode_id").value= _barcode_id;
	document.getElementById("barcode_code").value = _code;
	document.getElementById("barcode_description").value = _description;
	document.getElementById("barcode_barcodetype").value = _barcodetype;
	$('select#barcode_barcodetype').selectmenu("refresh");
	document.getElementById("barcode_qty").value = _qty;
	document.getElementById("barcode_defcode").value = _defcode;
	$("input#barcode_defcode").prop( "checked",(_defcode==1)).checkboxradio( "refresh" );
	
	document.getElementById('barcode_page').style.display = 'none';
	document.getElementById('ctr_barcode_page').style.display = 'none';
	if (document.getElementById('ctr_local_menu')!=null) {
		document.getElementById('ctr_local_menu').style.display = "none";}
	document.getElementById('barcode_edit').style.display = 'block';
	document.getElementById('ctr_barcode_edit').style.display = 'block';
	document.getElementById("barcode_code").focus();
	return true;
}

function barcode_update(){
	if (document.getElementById("barcode_code").value=="") {
	      alert(ms_err_barcode_missing_code);
	      return false;}
	if (document.getElementById("barcode_barcodetype").value=="") {
	      alert(ms_err_barcode_missing_barcodetype);
	      return false;}
	if (document.getElementById("barcode_qty").value=="") {
		document.getElementById("barcode_qty").value=0;}
	
	var foget_url = document.forms["frm_barcode"].baseURI.split("?")[0].replace("#","");
	foget_url += "?check_barcode=true";
	foget_url += "&barcode_id="+document.getElementById("barcode_id").value;
	foget_url += "&code="+document.getElementById("barcode_code").value;
	
	jQuery.ajax({
		type : "POST",
		url : foget_url,
		success : function(data) {
			if (data == "OK") {
				document.forms["frm_barcode"].submit();
			} else {
				alert(data);
			}
		}
	});
	return true;
}

//--------------------------------------------------
//address rows: customer, project
//--------------------------------------------------
function set_address(_address_id,_country,_state,_zipcode,_city,_street,_notes) {
	document.getElementById("address_id").value= _address_id;
	if (_address_id!=-1) {
		document.getElementById("label_address_id").innerHTML = _address_id;
	}
	else {
		document.getElementById("label_address_id").innerHTML = "000000";
	}
	document.getElementById("address_country").value = _country;
	document.getElementById("address_state").value = _state;
	document.getElementById("address_zipcode").value = _zipcode;
	document.getElementById("address_city").value = _city;
	document.getElementById("address_street").value = _street;
	document.getElementById("address_notes").value = _notes;
	
	document.getElementById('address_page').style.display = 'none';
	document.getElementById('ctr_address_page').style.display = 'none';
	if (document.getElementById('ctr_local_menu')!=null) {
		document.getElementById('ctr_local_menu').style.display = "none";}
	document.getElementById('address_edit').style.display = 'block';
	document.getElementById('ctr_address_edit').style.display = 'block';
	document.getElementById("address_country").focus();
	return true;
}

//--------------------------------------------------
//contact rows: customer, project, place
//--------------------------------------------------
function set_contact(_contact_id,_firstname,_surname,_status,_phone,_fax,_mobil,_email,_notes) {
	document.getElementById("contact_id").value= _contact_id;
	if (_contact_id!=-1) {
		document.getElementById("label_contact_id").innerHTML = _contact_id;
	}
	else {
		document.getElementById("label_contact_id").innerHTML = "000000";
	}
	document.getElementById("contact_firstname").value = _firstname;
	document.getElementById("contact_surname").value = _surname;
	document.getElementById("contact_status").value = _status;
	document.getElementById("contact_phone").value = _phone;
	document.getElementById("contact_fax").value = _fax;
	document.getElementById("contact_mobil").value = _mobil;
	document.getElementById("contact_email").value = _email;
	document.getElementById("contact_notes").value = _notes;
	
	document.getElementById('contact_page').style.display = 'none';
	document.getElementById('ctr_contact_page').style.display = 'none';
	if (document.getElementById('ctr_local_menu')!=null) {
		document.getElementById('ctr_local_menu').style.display = "none";}
	document.getElementById('contact_edit').style.display = 'block';
	document.getElementById('ctr_contact_edit').style.display = 'block';
	document.getElementById("contact_firstname").focus();
	return true;
}

//--------------------------------------------------
//price rows: product
//--------------------------------------------------
function set_price(_price_id,_validfrom,_validto,_curr,_qty,_pricevalue,_discount,_calcmode,_vendorprice,
		_groups_id,_customer_id,_custname,_title) {
	document.getElementById("edit_id").value= _price_id;
	if (_price_id!=-1) {
		document.getElementById("label_edit_id").innerHTML = _price_id;
	}
	else {
		document.getElementById("label_edit_id").innerHTML = "000000";
	}
	document.getElementById("title_item").innerHTML = _title;
	document.getElementById("price_validfrom").value = _validfrom;
	if (_validto!="None") {
		document.getElementById("price_validto").value = _validto;	
	} else {
		document.getElementById("price_validto").value = "";
	}
	document.getElementById("price_curr").value = _curr;
	$('select#price_curr').selectmenu("refresh");
	document.getElementById("price_qty").value = _qty;
	document.getElementById("price_pricevalue").value = _pricevalue;
	document.getElementById("price_vendorprice").value = _vendorprice;
	$("input#price_vendorprice").prop("checked",(_vendorprice==1)).checkboxradio("refresh");
	if (_discount!="None") {
		document.getElementById("price_discount").value = _discount;
	} else {
		document.getElementById("price_discount").value ="";
	}
	document.getElementById("price_calcmode").value = _calcmode;
	$('select#price_calcmode').selectmenu("refresh");
	if (_groups_id!="None") {
		document.getElementById("price_group_id").value = _groups_id;
	} else {
		document.getElementById("price_group_id").value = "";
	}
	$('select#price_group_id').selectmenu("refresh");
	if (_customer_id!="None") {
		document.getElementById("customer_id").value = _customer_id;
		document.getElementById("customer_custname").innerHTML = _custname;
	} else {
		document.getElementById("customer_id").value = "";
		document.getElementById("customer_custname").innerHTML = "";
	}
	
	document.getElementById('view_page').style.display = 'none';
	document.getElementById('ctr_view_page').style.display = 'none';
	document.getElementById('edit_page').style.display = 'block';
	document.getElementById('ctr_edit_page').style.display = 'block';
	document.getElementById("price_validfrom").focus();
	return true;
}
function price_update(){
	if (document.getElementById("price_validfrom").value=="") {
	      alert(ms_err_price_missing_validfrom);
	      return false;}
	if (document.getElementById("price_calcmode").value=="") {
	      alert(ms_err_price_missing_calcmode);
	      return false;}
	if (document.getElementById("price_curr").value=="") {
	      alert(ms_err_missing_curr);
	      return false;}
	if (document.getElementById("customer_id").value!="" & document.getElementById("price_group_id").value!="") {
		alert(ms_err_price_no_list);
	    return false;
	}
	if (document.getElementById("price_qty").value=="") {
		document.getElementById("price_qty").value=0;}
	if (document.getElementById("price_pricevalue").value=="") {
		document.getElementById("price_pricevalue").value=0;}
	if (document.getElementById("price_discount").value=="" & document.getElementById("price_discount").type!="hidden") {
		document.getElementById("price_discount").value=0;}
	
	document.forms["frm_edit"].submit();
}
//--------------------------------------------------
//rate rows: setting
//--------------------------------------------------
function set_rate(_rate_id,_ratetype,_ratedate,_curr,_place_id,_rategroup,_ratevalue,_title) {
	document.getElementById("edit_id").value= _rate_id;
	if (_rate_id!=-1) {
		document.getElementById("label_edit_id").innerHTML = _rate_id;
	}
	else {
		document.getElementById("label_edit_id").innerHTML = "000000";
	}
	document.getElementById("title_item").innerHTML = _title;
	document.getElementById("rate_ratetype").value= _ratetype;
	$('select#rate_ratetype').selectmenu("refresh");
	document.getElementById("rate_ratedate").value= _ratedate;
	document.getElementById("rate_curr").value= _curr;
	$('select#rate_curr').selectmenu("refresh");
	document.getElementById("rate_ratevalue").value= _ratevalue;
	if (_rategroup!="None") {
		document.getElementById("rate_rategroup").value= _rategroup;
		$('select#rate_rategroup').selectmenu("refresh");
	} else {
		document.getElementById("rate_rategroup").value= "";}
	if (_place_id!="None") {
		document.getElementById("rate_place_id").value= _place_id;
		$('select#rate_place_id').selectmenu("refresh");
	} else {
		document.getElementById("rate_place_id").value= "";}
	
	document.getElementById('view_page').style.display = 'none';
	document.getElementById('ctr_view_page').style.display = 'none';
	document.getElementById('edit_page').style.display = 'block';
	document.getElementById('ctr_edit_page').style.display = 'block';
	document.getElementById("rate_ratevalue").focus();
	return true;
}
function rate_update(){
	if (document.getElementById("rate_ratetype").value=="") {
	      alert(ms_err_rate_missing_ratetype);
	      return false;}
	if (document.getElementById("rate_ratedate").value=="") {
	      alert(ms_err_rate_missing_ratedate);
	      return false;}
	if (document.getElementById("rate_curr").value=="") {
	      alert(ms_err_missing_curr);
	      return false;}
	if (document.getElementById("rate_ratevalue").value=="") {
		document.getElementById("rate_ratevalue").value=0;}
	document.forms["frm_edit"].submit();
}

//--------------------------------------------------
//movement rows: trans_movement
//--------------------------------------------------
function set_movement(_movement_id, _shippingdate, _product_id, _product, _tool_id, _serial, _qty, _notes, _place_id, _planumber, _shared){
	document.getElementById("movement_id").value= _movement_id;
	if (_movement_id!=-1) {
		document.getElementById("label_movement_id").innerHTML = _movement_id;
	}
	else {
		document.getElementById("label_movement_id").innerHTML = "000000";
	}
	if (document.getElementById("tool_id")) {
		document.getElementById("tool_id").value= _tool_id;
		document.getElementById("tool_serial").innerHTML= _serial;
		document.getElementById("movement_shippingdate").value = _shippingdate;
	} else {
		document.getElementById("movement_qty").value = _qty;
		document.getElementById("product_id").value = _product_id;
		document.getElementById("product_description").innerHTML = _product;
		if (document.getElementById("place_id")) {
			document.getElementById("movement_shippingdate").value = document.getElementById("trans_transdate").value;
			document.getElementById("shippingdate").value = document.getElementById("trans_transdate").value+" 00:00:00";
			document.getElementById("movement_place_id").value = document.getElementById("place_id").value;
			document.getElementById("movement_place_planumber").innerHTML = document.getElementById("place_planumber").innerHTML;	
		} else {
			document.getElementById("shippingdate").value = _shippingdate;
			document.getElementById("movement_place_id").value = _place_id;
			document.getElementById("movement_place_planumber").innerHTML = _planumber;
			if (document.getElementById("movement_shared")) {
				if (document.getElementById("movement_shared")) {
					document.getElementById("movement_shared").value=_shared;
					$("input#movement_shared").prop("checked",(_shared==1)).checkboxradio("refresh");}
			}
		}
	}
	document.getElementById("movement_notes").value = _notes;
  
	document.getElementById('movement_page').style.display = 'none';
	document.getElementById('ctr_movement_page').style.display = 'none';
	if (document.getElementById('ctr_local_menu')!=null) {
	  document.getElementById('ctr_local_menu').style.display = "none";}
	document.getElementById('movement_edit').style.display = 'block';
	document.getElementById('ctr_movement_edit').style.display = 'block';
	  
	if (document.getElementById("tool_id")) {
		document.getElementById("movement_shippingdate").focus();
	} else {
		document.getElementById("movement_qty").focus();
	}
	return true;
}

function movement_update(){
	if (document.getElementById("tool_id")) {
		if (document.getElementById("tool_id").value=="") {
			alert(ms_err_movement_tool);
			return false;}
	} else {
		if (document.getElementById("product_id").value=="") {
			alert(ms_err_movement_product);
			return false;}
		if (document.getElementById("movement_place_id").value=="None") {
			document.getElementById("movement_place_id").value="";}
		if (document.getElementById("movement_shared")==null) {
			if (document.getElementById("movement_place_id").value=="") {
				alert(ms_err_movement_warehouse);
				return false;}}	
		}
	if (document.getElementById("target_place_id")) {
		if (document.getElementById("target_place_id").value=="") {
			alert(ms_err_movement_target_warehouse);
			return false;}
		if (document.getElementById("target_place_id").value==document.getElementById("movement_place_id").value) {
			alert(ms_err_movement_diff_warehouse);
			return false;}}
	if (document.getElementById("shippingdate")) {
		if (document.getElementById("shippingdate").value=="") {
			alert(ms_err_movement_shipping);
			return false;}	
	}
	if (document.getElementById("movement_qty").value=="") {
		document.getElementById("movement_qty").value=0;}
	document.forms["frm_movement"].submit();
}

//--------------------------------------------------
//load selected formula: trans_movement
//--------------------------------------------------
function load_formula(){
	if (document.getElementById("production_product_id").value=="") {
		alert(ms_err_movement_product);
		return false;}	
	if (document.getElementById("cmb_formula").disabled==true) {
		alert(ms_err_movement_save);
		return false;}
	if (document.getElementById("cmb_formula").selectedIndex<=0) {
		alert(ms_err_movement_formula);
		return false;}
	else {
		var formula_id = document.getElementById("cmb_formula").value}
	var res = confirm(ms_err_movement_load_formula);
	if (res==false) {
		return false;}
	
	var foget_url = get_base_url()+'/cmd_get_formula?production_id='+document.getElementById("production_production_id").value+"&formula_id="+formula_id;
	jQuery.ajax({
  	type: "POST", 
  	url: foget_url,
  	success: function(data) {
  		if (data=="OK") {
  			location.reload(true);
  		} else {
  			alert(ms_err_movement_load_formula_err);	
  		}
  	}
	});
}
//--------------------------------------------------
//create from base trans: trans_item, trans_payment, trans_movement
//--------------------------------------------------
function copy_trans(copy_url,redir_url){
	jQuery.ajax({
  	type: "POST", 
  	url: copy_url,
  	success: function(data) {
  		if (data.split('|')[0]=="ok") {
  			window.location = redir_url+data.split('|')[1];
  		} else {
  			alert(data.split('|')[2]);	
  		}
  	}
	});
}

//--------------------------------------------------
//create new document type from base trans: trans_item
//--------------------------------------------------
function create_newtype_change(){
	var seltype = document.getElementById('cmb_doctypes').value;
	var base_transtype = document.getElementById('base_transtype').value;
	var element_count = document.getElementById('element_count').value;
	if(seltype=='invoice' || seltype=='receipt'){
		$("input#cb_netto").checkboxradio("enable");
	} else {
		$("input#cb_netto").checkboxradio("disable");}
	if((seltype=='invoice'||seltype=='receipt') 
			&& (base_transtype=='order' || base_transtype=='rent' || base_transtype=='worksheet') 
	    	&& (element_count=='0')) {
		$("input#cb_from").checkboxradio("enable");
	} else {
		$("input#cb_from").checkboxradio("disable");}
}
function from_delivery_change(){
	if (document.getElementById('cb_from').checked) {
		$("input#cb_netto").checkboxradio("disable");
	} else {
		$("input#cb_netto").checkboxradio("enable");}
}
function create_trans(create_url,redir_url){
	create_url+="&new_transtype="+document.getElementById('cmb_doctypes').value;
	create_url+="&new_direction="+document.getElementById('cmb_directions').value;
	if (document.getElementById('cb_netto').checked && (document.getElementById('cb_netto').disabled==false)) {
		create_url+="&netto_qty=1";
	} else {
		create_url+="&netto_qty=0";}
	if (document.getElementById('cb_from').checked && (document.getElementById('cb_from').disabled==false)) {
		create_url+="&from_inventory=1";
	} else {
		create_url+="&from_inventory=0";}
	
	jQuery.ajax({
  	type: "POST", 
  	url: create_url,
  	success: function(data) {
  		if (data.split('|')[0]=="ok") {
  			window.location = redir_url+data.split('|')[1];
  		} else {
  			alert(data.split('|')[2]);	
  		}
  	}
	});
	return true;
}

//--------------------------------------------------
//create general reports: reports
//--------------------------------------------------
function show_report(ms_missing){
	var frm = document.forms["frm_report"];
	for (var i=0;i<frm.elements.length;i++) {
		if (frm.elements[i].name.substr(0,3)=="rq_" && frm.elements[i].checked){
			var pid = "report_"+frm.elements[i].name.substring(3);
			var pval = document.getElementById(pid);
			if (pval.value=="") {
				alert(ms_missing+": "+document.getElementById(pid+"__label").innerHTML.replace("*","").replace(":",""));
				return false;
			}
		}
	}
	document.forms["frm_report"].submit();
}

//--------------------------------------------------
//shipping
//--------------------------------------------------
function create_delivery_items(){
  var place_id=document.getElementById("place_id");
  if (place_id.value=="") {
    alert(ms_err_missing_wh);
    return true;
  }
  var shippingdate=document.getElementById("shippingdate");
  if (shippingdate.value=="") {
    alert(ms_err_missing_date);
    return true;
  }
  var trans_id=document.getElementById("trans_id").value;
  var url = get_base_url()+'/frm_shipping/edit/trans/'+trans_id+'?create_items=true&create_place_id='+place_id.value+'&create_date='+shippingdate.value;
  jQuery.ajax({
    	type: "POST", url: url, 
    	success: function(data) {
    		if (data=="OK") {
    			window.location.reload();
    			}
    		}
    });
  return true;
}
function set_delivery(_item_id, _product_id, _partnumber, _batch, _qty){
  var item_id=document.getElementById("item_id");
  item_id.value = _item_id;
  var product_id=document.getElementById("product_id");
  product_id.value = _product_id;
  var partnumber=document.getElementById("partnumber");
  partnumber.innerHTML = _item_id+' | '+_partnumber;
  var batch=document.getElementById("batch");
  batch.value = _batch;
  var qty=document.getElementById("qty");
  qty.value = _qty;
  var tbl=document.getElementById('edit_item');
  $("#popup_edit_item").popup("open");
  batch.focus();
  return true;
}
function update_delivery(){
  var trans_id=document.getElementById("trans_id").value;
  var item_id=document.getElementById("item_id").value;
  var product_id=document.getElementById("product_id").value;
  var batch=document.getElementById("batch").value;
  var qty=document.getElementById("qty").value;
  
  var url = get_base_url()+'/frm_shipping/edit/trans/'+trans_id+'?edit_item_id='+item_id+'&edit_product_id='+product_id+'&edit_batch='+batch+'&edit_qty='+qty;
  jQuery.ajax({
  	type: "POST", url: url, 
  	success: function(data) {
  		if (data!="") {
  			$("#items_table").html(data).trigger("create");
  		    return true;
  		    }
  		}
  });
}
function add_delivery(item_id,product_id,qty,edit){
  if (edit!="*") {
    var trans_id=document.getElementById("trans_id").value;
    var url = get_base_url()+'/frm_shipping/edit/trans/'+trans_id+'?add_item_id='+item_id+'&add_product_id='+product_id+'&add_qty='+qty;
    jQuery.ajax({
    	type: "POST", url: url, 
    	success: function(data) {
    		if (data=="OK") {
    			window.location.reload();
    			}
    		}
    });
  }
}
function del_delivery(item_id,product_id){
  var trans_id=document.getElementById("trans_id").value;
  var url = get_base_url()+'/frm_shipping/edit/trans/'+trans_id+'?del_item_id='+item_id+'&del_product_id='+product_id;
  jQuery.ajax({
  	type: "POST", url: url, 
  	success: function(data) {
  		if (data=="OK") {
  			window.location.reload();
  			}
  		}
  });
}
function add_all_delivery(){
  var trans_id=document.getElementById("trans_id").value;
  var url = get_base_url()+'/frm_shipping/edit/trans/'+trans_id+'?add_all=true';
  jQuery.ajax({
  	type: "POST", url: url, 
  	success: function(data) {
  		if (data=="OK") {
  			window.location.reload();
  			}
  		}
  });
}
function remove_all_delivery(){
  var trans_id=document.getElementById("trans_id").value;
  var url = get_base_url()+'/frm_shipping/edit/trans/'+trans_id+'?del_all=true';
  jQuery.ajax({
  	type: "POST", url: url, 
  	success: function(data) {
  		if (data=="OK") {
  			window.location.reload();
  			}
  		}
  });
}

//--------------------------------------------------
//fnote : trans_fnote
//--------------------------------------------------
function set_default_template() {
	var ctmp=document.getElementById('cmb_temp');
	if(ctmp.value==''){
		alert(ms_wn_chosen)
		} 
	else {
		if(confirm(ms_wn_conf)){
			var trans_id=document.getElementById("trans_id").value;
			jQuery.ajax({
		    	type: "POST", 
		    	url: get_base_url()+'/frm_trans_fnote/'+trans_id+
		    	  '?def_tmp_value='+ctmp.value+'&def_tmp_name='+ctmp.options[ctmp.selectedIndex].text, 
		    	success: function(data) {
		    		ctmp.title=title_def+ctmp.options[ctmp.selectedIndex].text;
		    		}
			});}
		};
	return true;
}
function save_template() {
	var fnote=document.getElementsByName('fnote')[0];
	var ctmp=document.getElementById('cmb_temp');
	if(ctmp.value==''){
		alert(ms_wn_chosen);} 
	else {
		if(confirm(ms_wn_save)){
			var trans_id=document.getElementById("trans_id").value;
			var surl = get_base_url()+'/frm_trans_fnote/'+trans_id+
	    	  '?save_tmp_value='+ctmp.value+'&save_tmp_name='+ctmp.options[ctmp.selectedIndex].text+'&fnote='+encodeURIComponent($('#'+fnote.id).val())
			jQuery.ajax({
		    	type: "POST", 
		    	url: surl,
		    	success: function(data) {}
			});
			}
	};
	return true;
}
function delete_template() {
	var ctmp=document.getElementById('cmb_temp');
	if(ctmp.value==''){
		alert(ms_wn_chosen)
		} 
	else {
		if(confirm(ms_wn_delete)){
			var trans_id=document.getElementById("trans_id").value;
			var surl = get_base_url()+'/frm_trans_fnote/'+trans_id
			  +'?del_tmp_value='+ctmp.value+'&del_tmp_name='+ctmp.options[ctmp.selectedIndex].text;
			jQuery.ajax({
		    	type: "POST", 
		    	url: surl,
		    	success: function(data) {
		    		window.location.reload();
		    	}
			});
			}
		};
	return true;
}
function new_template() {
	var itmp=document.getElementById('new_tempdesc');
	var isel=document.getElementById('cmb_temp');
	var irow=document.getElementById('irow');
	if(itmp.value==''){
		alert(ms_err_new);
		} 
	else {
		if(get_tmp_opt(itmp.value)){
			var trans_id=document.getElementById("trans_id").value;
			var surl = get_base_url()+'/frm_trans_fnote/'+trans_id+'?new_tmp='+itmp.value
			jQuery.ajax({
		    	type: "POST", 
		    	url: surl,
		    	success: function(data) {
		    		window.location.reload();
		    	}
			});
			}
		};
  return true;
}
function get_tmp_opt( new_opt) {
  var isel=document.getElementById('cmb_temp');
  for (var i=0; i<isel.options.length; i++){
    if (isel.options[i].innerText==new_opt) {
  	  alert(ms_er_exists);
  	  return false;
    }
  }
  return true;
}

function loadTemplate() {
	var ctmp=document.getElementById('cmb_temp');
	var trans_id=document.getElementById("trans_id").value;
	var pget_url = get_base_url()+'/frm_trans_fnote/'+trans_id
	  +'?load_tmp_value='+ctmp.value+'&load_tmp_name='+ctmp.options[ctmp.selectedIndex].text;
	jQuery.ajax({
  	type: "POST", url: pget_url, 
  	success: function(data) {
  		if (data=="") {data=" "};
  		var fnote=document.getElementsByName('fnote')[0];
  		$('#'+fnote.id).jqteVal(data);
  		}
  });
}

//--------------------------------------------------
//dlg_report
//--------------------------------------------------
function create_report(cmd,ms_missing) {
	if(document.getElementById('cmb_templates').value==''){
		alert(ms_missing);
		return true;
	}
	if (document.getElementById('dlg_report_cmd')==null) {
		var report_cmd = document.createElement("input");
		report_cmd.setAttribute("id", "dlg_report_cmd");
		report_cmd.setAttribute("type", "hidden");
		report_cmd.setAttribute("name", "cmd");
		document.forms["dlg_frm_report"].appendChild(report_cmd);	
	}
	document.getElementById('dlg_report_cmd').value = cmd;
	document.forms["dlg_frm_report"].submit();
}

//--------------------------------------------------
//frm_printqueue
//--------------------------------------------------
function pdf_export(task_id, printer_clienthost, report_id, ref_id, orientation, size, refnumber) {
	jQuery.ajax({
  	type: "POST",
  	data: {"get_report":true,"report_id":report_id, "ref_id":ref_id, "orientation":orientation, "size":size},
  	success: function(data) {
  		jQuery.ajax({
  	    	type: "POST", url: "http://"+printer_clienthost,
  	    	data: {"cmd":"export","file":data,"filename":refnumber.replace(/\'/g,"")+".pdf","dir":"export","encode":"base64"},
  	    	success: function(data) {
  	    		if (data=="OK") {
  	    			set_task(task_id);}
  	    		else {
  	    			set_task(task_id, data);
  	    		}
  	    		},
  		    error: function(jqXHR, textStatus, errorThrown ) {
  		    	set_task(task_id, ms_err_local_printer);
  		    	}
  	    });
  		},
	    error: function(jqXHR, textStatus, errorThrown ) {
	    	set_task(task_id, ms_err_local_printer);
	    	}
  });
}
function pdf_printing(task_id, printer_clienthost, report_id, ref_id, orientation, size, copies, printer, refnumber) {
	jQuery.ajax({
  	type: "POST",
  	data: {"get_report":true,"report_id":report_id, "ref_id":ref_id, "orientation":orientation, "size":size},
  	success: function(data) {
  		jQuery.ajax({
  	    	type: "POST", url: "http://"+printer_clienthost,
  	    	data: {"cmd":"print","file":data,"filename":refnumber.replace(/\'/g,"")+".pdf",
  	    		"printer":printer,"copies":copies,"size":size,"orientation":orientation,"encode":"base64"},
  	    	success: function(data) {
  	    		if (data=="OK") {
  	    			set_task(task_id);}
  	    		else {
  	    			set_task(task_id, data);
  	    		}
  	    		},
  		    error: function(jqXHR, textStatus, errorThrown ) {
  		    	set_task(task_id, ms_err_local_printer);
  		    	}
  	    });
  		},
	    error: function(jqXHR, textStatus, errorThrown ) {
	    	set_task(task_id, ms_err_local_printer);
	    	}
  });
}
function printer_settings(printer_clienthost, orientation, size) {
	var psettings = null;
	jQuery.ajax({
  	type: "POST", url: "http://"+printer_clienthost, async: false,
  	data: {"cmd":"printers","orientation":orientation,"size":size},
  	success: function(data) {
  		if (data!="") {
  			psettings = data.split("|");	
  		}
  		},
	    error: function(jqXHR, textStatus, errorThrown ) {
	    	alert(ms_err_local_printer);
	    	}
  });
	return psettings;
}
var local_tasks = new Object();
function set_task(task_id, error_msg) {
	if (local_tasks.hasOwnProperty(task_id)) {
		if (!local_tasks[task_id].cancel) {
			if (error_msg!=null) {
				local_tasks[task_id].cancel = true;
				alert(error_msg);
			} else {
				local_tasks[task_id].current += 1;
				if (local_tasks[task_id].total==local_tasks[task_id].current) {
					local_tasks[task_id].cancel = true;
					jQuery.ajax({
				    	type: "POST",
				    	data: {"delete_rows":true,"rows":local_tasks[task_id].rows},
				    	success: function(data) {
				    		if (data=="OK")
				    			location.reload(); 
				    		},
					    error: function(jqXHR, textStatus, errorThrown ) {
					    	}
				    });
					if (task_id.indexOf("local")>-1) {
						alert(ms_ok_print.replace("%",local_tasks[task_id].total));
					} else {
						alert(ms_ok_export.replace("%",local_tasks[task_id].total));
					}
				}
			}
		}
	}
}
function local_printing(printer_clienthost) {
	var frm = document.forms["frm_print_filter"];
	jQuery.ajax({
	    	type: "POST",
	    	data: $("#frm_print_filter").serialize(),
	    	success: function(data) {	
	    		printer_type = document.getElementById('cmb_printer_type').value;
	    		var irow = 0;
	    		if (data!="") {
	    			rows = data.split("|");
	    			if (rows.length==0)
	    				return false;
	    			
	    			var task_id = printer_type+(new Date()).getTime().toString();
	    			local_tasks[task_id] = new Object();
	    			local_tasks[task_id].rows = data;
		    		local_tasks[task_id].cancel = false;
		    		local_tasks[task_id].total = rows.length;
		    		local_tasks[task_id].current = 0;
		    		
	    			var printer = ""; var copies = 1;
	    			var orientation = document.getElementById('cmb_orientation').value;
	    			var size = document.getElementById('cmb_size').value;
	    			
	    			if (printer_type=="local") {
	    				var psettings = printer_settings(printer_clienthost, orientation, size);
	    				if (psettings) {
	    					printer = psettings[0];copies = psettings[1];
	    					size = psettings[2];orientation = psettings[3];
	    					for (var i=0;i<rows.length;i++) {
			    				item = rows[i].split(",");
			    				//0:printqueue_id, 1:report_id, 2:ref_id, 3:copies, 4:refnumber
			    				pdf_printing(task_id, printer_clienthost, item[1], item[2], orientation, size, copies, printer, item[4]+"_"+item[0]);
			    			}
	    				}
	    			} else {
	    				for (var i=0;i<rows.length;i++) {
		    				item = rows[i].split(",");
		    				//0:printqueue_id, 1:report_id, 2:ref_id, 3:copies, 4:refnumber
		    				pdf_export(task_id, printer_clienthost, item[1], item[2], orientation, size, item[4]+"_"+item[0]);
		    			}
	    			}
	    		}
	    		},
		    error: function(jqXHR, textStatus, errorThrown ) {
		    	alert(ms_err_local_printer);
		    	return true;
		    	}
	    });
}
function print_items(selmode,printer_clienthost) {
	if (document.getElementById('selmode')==null) {
		var sign = document.createElement("input");
		sign.setAttribute("id", "selmode");
		sign.setAttribute("type", "hidden");
		sign.setAttribute("name", selmode);
		sign.setAttribute("value", "true");
		document.forms["frm_print_filter"].appendChild(sign);	
	} else {
		document.getElementById('selmode').setAttribute("name", selmode);
	}
	if (document.getElementById('cmb_printer_type').value!="server") {
		jQuery.ajax({
	    	type: "POST", url: "http://"+printer_clienthost,
	    	data: {"cmd":"vernum"},
	    	contentType: "application/x-www-form-urlencoded; charset=UTF-8",
	    	success: function(data) {
	    		local_printing(printer_clienthost);
	    		},
		    error: function(jqXHR, textStatus, errorThrown ) {
		    	alert(ms_err_missing_local_printer_support);
		    	window.location.reload();
		    	}
	    });
	} else {
		if (document.getElementById('cmb_printers').value=="") {
			alert(ms_err_missing_printer);
		    return true;
		}
		document.forms["frm_print_filter"].submit();	
	}
}

function set_filter_values() {
	if (document.getElementById('selmode')!=null) {
		document.getElementById('selmode').setAttribute("name", "filter");
	}
	document.getElementById('nervatype').value = document.getElementById('filter_nervatype').value;
	document.getElementById('transnumber').value = document.getElementById('filter_transnumber').value;
	document.getElementById('fromdate').value = document.getElementById('filter_fromdate').value;
	document.getElementById('enddate').value = document.getElementById('filter_enddate').value;
	document.getElementById('username').value = document.getElementById('filter_username').value;
	
	document.getElementById('printer_type').value = document.getElementById('cmb_printer_type').value;
	document.getElementById('printer').value = document.getElementById('cmb_printers').value;
	document.getElementById('size').value = document.getElementById('cmb_size').value;
	document.getElementById('orientation').value = document.getElementById('cmb_orientation').value;
}

//--------------------------------------------------
//general page commands
//--------------------------------------------------
function getParameterByName(name){
  var url     = document.URL,
      count   = url.indexOf(name);
      sub     = url.substring(count);
      amper   = sub.indexOf("&");
      eq   = sub.indexOf("=");

  if (count>-1 && eq>-1) {
  	if(amper == "-1"){
          var param = sub.split("=");
          return param[1];
      }else{
          var param = sub.substr(0,amper).split("=");
          return param[1];
      }	
  } else {
  	return "";
  }

}
function page_ini(){
	var page = "";
	var pages = document.getElementsByName("pages");
	for (var i=0;i<pages.length;i++) {
		if (getParameterByName(pages[i].id)!="") {
			page = pages[i].id;
		}
	}
	if (page==""){
		if (document.getElementById('active_page')!=null) {
			if (document.getElementById(document.getElementById('active_page').value)!=null) {
				page = document.getElementById('active_page').value;
			}
		}	
	}
	if (page!=""){
		show_page(page);	
	}
}
function show_page(page){
	var pages = document.getElementsByName("pages");
	for (var i=0;i<pages.length;i++) {
		if (pages[i].id==page) {
			pages[i].style.display = "block";
		} else {
			pages[i].style.display = "none";
		}
		if (document.getElementById('ctr_'+pages[i].id)!=null) {
			document.getElementById('ctr_'+pages[i].id).style.display = pages[i].style.display;
		}
	}
	if (document.getElementById('ctr_local_menu')!=null) {
		document.getElementById('ctr_local_menu').style.display = "block";
	}
	return true;
}
function show_div(div, title){
	var divs = document.getElementsByName("divs");
	for (var i=0;i<divs.length;i++) {
		if (divs[i].id==div) {
			divs[i].style.display = "block";
		} else {
			divs[i].style.display = "none";
		}
	}
	if (title!=null){
		if (document.getElementById('divs_title')!=null) {
			document.getElementById('divs_title').innerHTML = title;
		}
	}
	return true;
}