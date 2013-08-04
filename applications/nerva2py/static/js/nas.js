var appl_url = "nerva2py/nas";
var base_url = window.location.protocol+'//'+window.location.host+'/'+appl_url;

function createDatabase() {
	var cmb_alias=document.getElementById('cmb_alias').value;
	if (cmb_alias=="") {
		alert("Missing database!"); return false;}
    if(confirm('Start the database creation. Do you want to continue?')) {
    	msg_result.innerHTML='Process started. Waiting for the server to respond ...';
        callFunction(base_url+'/createDatabase?alias='+cmb_alias,'msg_result');
        }
    else {msg_result.innerHTML='Starting the process?'}
    return true;
}

function createDataBackup() {
	var cmb_alias=document.getElementById('cmb_alias').value;
	var cmb_format=document.getElementById('cmb_format').value;
	var cmb_btype=document.getElementById('cmb_btype').value;
	var cmb_filename=document.getElementById('cmb_filename').value;
	var cust_filename=document.getElementById('cust_filename').value;
	var cmb_nom=document.getElementById('cmb_nom').value;
	var cust_nom=document.getElementById('cust_nom').value;
	if (cmb_alias=="") {
		alert("Missing database!"); return false;}
	if (cmb_filename=="custom") {
		if (cust_filename=="") {
			alert("Missing custom filename!"); return false;			
		} else {
			cmb_filename = cust_filename;
		}
	}
	if (cmb_nom=="custom") {
		if (cmb_btype=="settings") {
			alert("The setting is selected, the backup only when all objects are allowed!"); return false;
		}
		if (cust_nom=="") {
			alert("Missing custom NOM list!"); return false;	
		} else {
			cmb_nom = cust_nom;
		}
	}
	if(confirm('Start the customer backup creation. Do you want to continue?')) {
    	if (cmb_filename=="download") {
    		msg_result.innerHTML='Starting the process?'
    		window.open(base_url+'/createDataBackup?alias='+cmb_alias+'&btype='+cmb_btype+'&bformat='+cmb_format
            		+'&lst_nom='+cmb_nom+'&filename='+cmb_filename, '_blank')
    	} else {
    		msg_result.innerHTML='Process started. Waiting for the server to respond ...';
    		callFunction(base_url+'/createDataBackup?alias='+cmb_alias+'&btype='+cmb_btype+'&bformat='+cmb_format
            		+'&lst_nom='+cmb_nom+'&filename='+cmb_filename,'msg_result');	
    	}
    } 
	else {msg_result.innerHTML='Starting the process?'}
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