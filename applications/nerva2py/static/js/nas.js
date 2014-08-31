function get_base_url() {
	return window.location.protocol+'//'+window.location.host+"/"+document.getElementById('appl_url').className;
}

function createDatabase() {
	var cmb_alias=document.getElementById('cmb_alias').value;
	if (cmb_alias=="") {
		alert("Missing database!"); return false;}
	document.getElementById('msg_result').innerHTML='Process started. Waiting for the server to respond ...';
    if(confirm('Start the database creation. Do you want to continue?')) {
        callFunction(get_base_url()+'/createDatabase?alias='+cmb_alias,'msg_result');
        }
    else {document.getElementById('msg_result').innerHTML='Starting the process?'}
    return true;
}

function createDataBackup() {
	var cmb_alias=document.getElementById('cmb_alias').value;
	var cmb_format=document.getElementById('cmb_format').value;;
	var cmb_filename=document.getElementById('cmb_filename').value;;
	var cust_filename="";
	if (document.getElementById('cust_filename')!=null) {
		cust_filename = document.getElementById('cust_filename').value;	
	}
	if (cmb_alias=="") {
		alert("Missing database!"); return false;}
	if (cmb_filename=="custom") {
		if (cust_filename=="") {
			alert("Missing custom filename!"); return false;			
		} else {
			cmb_filename = cust_filename;
		}
	}
	if(confirm('Start the customer backup creation. Do you want to continue?')) {
    	if (cmb_filename=="download") {
    		document.getElementById('msg_result').innerHTML='Starting the process?';
    		window.location.assign(get_base_url()+'/createDataBackup?alias='+cmb_alias+'&bformat='+cmb_format
    		  +'&filename='+cmb_filename)
    	} else {
    		document.getElementById('msg_result').innerHTML='Process started. Waiting for the server to respond ...';
    		callFunction(get_base_url()+'/createDataBackup?alias='+cmb_alias+'&bformat='+cmb_format
            		+'&filename='+cmb_filename,'msg_result');	
    	}
    } 
	else {document.getElementById('msg_result').innerHTML='Starting the process?'}
	return true;
}

function callFunction(url,retmsg) {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open("POST",url,false);
	xmlhttp.send();
	if (retmsg!="") {
		if (retmsg=="alert") {
			alert(xmlhttp.responseText);
		} else {
			$('#'+retmsg).html(xmlhttp.responseText);
		}}
	}

