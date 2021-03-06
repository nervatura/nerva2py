function sendToServer(){
  if (document.getElementById("rs_url").value!="") {
    window.open(document.getElementById("rs_url").value, '_blank');
  }
}

var jdata = null;
function sendToJsonServer(){
  if (jdata !== null) {
    jQuery.ajax({
      type: "post",
      url: window.location.protocol+'//'+window.location.host+"/nerva2py/ndi/call/jsonrpc2/",
      data: JSON.stringify(jdata),
      contentType: "application/json",
      success: function(response) {
        if (typeof response == "string") {
          alert(response);}
        else if (typeof response.error !== "undefined") {
          alert(response.error.message);}
        else {
          var result = response.result;
          if (typeof result === "object") {
            result = JSON.stringify(response.result);}
          var win = window.open("","_blank");
          win.document.write("<html><head><title>NDI RESULT</title></head><body>"+result+"</body></html>");
          win.document.close();}
      },
      error: function(jqXHR, textStatus, errorThrown ) {
       alert("POST ERROR");}
    });
  }
}

function setLabels(label,url){
  document.getElementById("help_label").innerHTML=label;
  document.getElementById("help_label").href=url;
}

function changeItem(){
  var nom = document.getElementById("lst_nom").value;
  document.getElementById("datatype").value = nom;
  document.getElementById("rs_url").value = "";
  document.getElementById("rs_server").value = "";
  document.getElementById("rs_json").value = "";
  document.getElementById("insert_field").checked = true;
  document.getElementById("insert_field").disabled = false;
  document.getElementById("no_deffield").checked = false;
  document.getElementById("no_deffield").disabled = false;
  
  url = window.location.protocol+'//'+window.location.host
  +'/nerva2py/wizard/get_nom_data?nom=@nom&database=@database&username=@username&password=@password';
  url = url.replace("@nom", nom);
  url = url.replace("@database", document.getElementById("database").value);
  url = url.replace("@username", document.getElementById("username").value);
  url = url.replace("@password", document.getElementById("password").value);
  
  switch (nom) {
    case "sql":
      document.getElementById("rs_sql").style.display="block";
      document.getElementById("rs_nosql").style.display="none";
      $("#tabs").tabs({active: 0});
      $("#tabs").tabs({disabled: [1,2]});
      break;
    default:
      document.getElementById("rs_sql").style.display="none";
      document.getElementById("rs_nosql").style.display="block";
      $("#tabs").tabs({disabled: false});
      switch (nom) {
        case "groups":
        case "fieldvalue":
        case "numberdef":
        case "deffield":
        case "pattern":
    	  document.getElementById("insert_field").checked = false;
    	  document.getElementById("insert_field").disabled = true;
    	  document.getElementById("no_deffield").checked = false;
    	  document.getElementById("no_deffield").disabled = true;
    	  break;
      }
      jQuery.ajax({type: "POST", 
    	  url: url, 
    	  success: function(data) {
    		document.getElementById("rs_view").innerHTML=data.split("||")[0];
    	    document.getElementById("rs_update").innerHTML=data.split("||")[1];
    	    document.getElementById("rs_delete").innerHTML=data.split("||")[2];
    	    } });
      }
}

function getUrl(urlfunc){
	var url = "@protocol//@server/@function?@code&@params&@data";
    url = url.replace("@protocol", window.location.protocol);
    url = url.replace("@server", window.location.host);
    url = url.replace("@function", "nerva2py/ndi/"+urlfunc);
    url = url.replace("@code", "code="+document.getElementById("code").value);
    return url;
}
function getParams(urlfunc){
	var params = "database=@database|username=@username|password=@password|datatype=@datatype";
  params = params.replace("@database", document.getElementById("database").value);
  params = params.replace("@username", document.getElementById("username").value);
  params = params.replace("@password", document.getElementById("password").value);
  params = params.replace("@datatype", document.getElementById("datatype").value);
  if (document.getElementById("use_deleted").checked) {
  	params = params+"|use_deleted";	
  }
  if (urlfunc=="updateData" && document.getElementById("insert_row").checked) {
  	params = params+"|insert_row";	
  }
  if (urlfunc=="updateData" && document.getElementById("insert_field").checked) {
  	params = params+"|insert_field";	
  }
  if (document.getElementById("code").value=="base64" || document.getElementById("code").value=="base64all") {
  	params = "params="+$.base64.encode(params);
  } else {
  	params = "params="+params;
  }
  return params;
}
function getParamsPy(urlfunc){
  var params = '"datatype":"'+document.getElementById("datatype").value+'"';
  if (document.getElementById("use_deleted").checked) {
    params = params+',"use_deleted":True'; 
  }
  if (urlfunc=="updateData" && document.getElementById("insert_row").checked) {
  	params = params+',"insert_row":True';	
  }
  if (urlfunc=="updateData" && document.getElementById("insert_field").checked) {
  	params = params+',"insert_field":True';	
  }
  return params;
}
function getParamsJson(urlfunc, jdata){
  jdata.params[0].database = document.getElementById("database").value;
  jdata.params[0].username = document.getElementById("username").value;
  jdata.params[0].password = document.getElementById("password").value;
  jdata.params[0].datatype = document.getElementById("datatype").value;
  if (document.getElementById("use_deleted").checked) {
    jdata.params[0].use_deleted = true;
  }
  if (urlfunc=="updateData" && document.getElementById("insert_row").checked) { 
    jdata.params[0].insert_row = true;
  }
  if (urlfunc=="updateData" && document.getElementById("insert_field").checked) { 
    jdata.params[0].insert_field = true;
  }
  return jdata;
}

function createView(){
	if (document.getElementById("datatype").value=="") return;
	var url = getUrl("getData");
	var params = getParams("getData");
	var params_py = getParamsPy("getData");
	jdata = {"id":1, "method":"getData_json", "jsonrpc":"2.0", params:[{},{}]};
	jdata = getParamsJson("getData", jdata);
	
	var filters = ""; var filters_py = "";
	if (document.getElementById("datatype").value!="sql") {
		filters += "output="+document.getElementById("output").value;
		filters_py += '"output":"'+document.getElementById("output").value+'"';
		jdata.params[1].output = document.getElementById("output").value;
		var inputs = $("#rs_view :input");
		for (var i=0;i<inputs.length;i++) {
			if (inputs[i].value!='') {
				if (document.getElementById("datatype").value=="log" && inputs[i].value=="notype") {
					filters += "|"+inputs[i].value;
					filters_py += ',"notype":True';
					jdata.params[1].notype = true;
				} else {
					filters += "|"+inputs[i].name+"="+inputs[i].value;
					filters_py += ',"'+inputs[i].name+'":"'+inputs[i].value+'"';
					jdata.params[1][inputs[i].name] = inputs[i].value;
				}	
			}
		}
		var inputs = ["where","orderby","header","columns"];
		for (var i=0;i<inputs.length;i++) {
			if (document.getElementById(inputs[i]).value!="") {
				filters += "|"+inputs[i]+"="+document.getElementById(inputs[i]).value;
				filters_py += ',"'+inputs[i]+'":"'+document.getElementById(inputs[i]).value+'"';
				jdata.params[1][inputs[i]] = document.getElementById(inputs[i]).value;
			}	
		}
		if (document.getElementById("show_id").checked) {
			filters += "|show_id";
			filters_py += ',"show_id":True';
			jdata.params[1].show_id = true;
		}
		if (document.getElementById("no_deffield").checked) {
			filters += "|no_deffield";
			filters_py += ',"no_deffield":True';
			jdata.params[1].no_deffield = true;
		}
	} else {
		filters += "output="+document.getElementById("output_sql").value;
		filters_py += '"output":"'+document.getElementById("output_sql").value+'"';
		jdata.params[1].output = document.getElementById("output_sql").value;
		filters += "|sql="+document.getElementById("sql").value;
		filters_py += ',"sql":"'+document.getElementById("sql").value+'"';
		jdata.params[1].sql = document.getElementById("sql").value;
	}
	if (jdata.params[1].output === "xml" || jdata.params[1].output === "excel") {
    jdata.params[1].output = "json";}
      
	if (document.getElementById("code").value=="base64" || document.getElementById("code").value=="base64all") {
		filters = "filters="+$.base64.encode(filters);
    } else {
    	filters = "filters="+filters;
    }
	url = url.replace("@params", params);
	url = url.replace("@data", filters);
	document.getElementById("rs_url").value = url;
	filters_py = 'getView({'+params_py+'},{'+filters_py+'})';
	document.getElementById("rs_server").value = filters_py;
	document.getElementById("rs_json").value = "url: "+window.location.protocol+'//'+
	  window.location.host+"/nerva2py/ndi/call/jsonrpc2/\ndata: "+JSON.stringify(jdata);
}

function getUpdateInputs(){
	var ilist=[];ilist[1]=[];ilist[2]=[];ilist[3]=[];ilist[4]=[];
	var inputs = $("#rs_update :input");
	for (var i=0;i<inputs.length;i++) {
		if (inputs[i].id.indexOf("select_")==-1) {
			if (document.getElementById("select_"+inputs[i].name+"_"+inputs[i].parentElement.id).checked) {
				ilist[inputs[i].parentElement.id].push(inputs[i]);
			}
		}
	}
	return ilist;
}

function createUpdate(){
	if (document.getElementById("datatype").value=="") return;
	
	var url = getUrl("updateData");
	var params = getParams("updateData");
	var params_py = getParamsPy("updateData");
	jdata = {"id":2, "method":"updateData_json", "jsonrpc":"2.0", params:[{},[]]};
  jdata = getParamsJson("updateData", jdata);
  
	var data = ""; var data_py = "";
	var inputs = getUpdateInputs();
	for (var fn=1;fn<5;fn++) {
		var data_row=""; var data_py_row=""; var data_json_row = {};
		for (var i=0;i<inputs[fn].length;i++) {
			data_row += "|"+inputs[fn][i].name+"="+inputs[fn][i].value;
			data_py_row += ',"'+inputs[fn][i].name+'":"'+inputs[fn][i].value+'"';
			data_json_row[inputs[fn][i].name] = inputs[fn][i].value;
		}
		if (data_row!="") {
			data += '|'+data_row;
			data_py += ',{'+data_py_row.substring(1)+'}';
			jdata.params[1].push(data_json_row);
		}
	}
	
	if (document.getElementById("code").value=="base64" || document.getElementById("code").value=="base64all") {
		data = "data="+$.base64.encode(data.substring(2));
    } else {
    	data = "data="+data.substring(2);
    }
	
	url = url.replace("@params", params);
	url = url.replace("@data", data);
	document.getElementById("rs_url").value = url;
	data_py = 'update_'+document.getElementById("datatype").value+'({'+params_py+'},['+data_py.substring(1)+'])';
	document.getElementById("rs_server").value = data_py;
	document.getElementById("rs_json").value = "url: "+window.location.protocol+'//'+
	  window.location.host+"/nerva2py/ndi/call/jsonrpc2/\ndata: "+JSON.stringify(jdata);
}

function getDeleteInputs(index){
	var ilist = [];
	var inputs = $("#rs_delete :input");
	for (var i=0;i<inputs.length;i++) {
		if (inputs[i].parentElement.id==index) {
			ilist.push(inputs[i]);
		}
	}
	return ilist;
}

function createDelete(){
if (document.getElementById("datatype").value=="") return;
	
	var url = getUrl("deleteData");
	var params = getParams("deleteData");
	var params_py = getParamsPy("deleteData");
	jdata = {"id":3, "method":"deleteData_json", "jsonrpc":"2.0", params:[{},[]]};
  jdata = getParamsJson("deleteData", jdata);
  
	var data = "";
	var data_py = "";
	
	for (var fn=1;fn<5;fn++) {
		if (document.getElementById("row_"+fn).checked || fn==1) {
			var inputs = getDeleteInputs(fn);
			var data_row=""; var data_py_row=""; var data_json_row = {};
			for (var i=0;i<inputs.length;i++) {
				if (inputs[i].value=="") {
					alert(ms_missing);
					return;
				}
				data_row += "|"+inputs[i].name+"="+inputs[i].value;
				data_py_row += ',"'+inputs[i].name+'":"'+inputs[i].value+'"';
				data_json_row[inputs[i].name] = inputs[i].value;
			}
			data += '|'+data_row;
			data_py += ',{'+data_py_row.substring(1)+'}';
			jdata.params[1].push(data_json_row);
		}
	}
	
	if (document.getElementById("code").value=="base64" || document.getElementById("code").value=="base64all") {
		data = "data="+$.base64.encode(data.substring(2));
    } else {
    	data = "data="+data.substring(2);
    }
	
	url = url.replace("@params", params);
	url = url.replace("@data", data);
	document.getElementById("rs_url").value = url;
	data_py = 'delete_'+document.getElementById("datatype").value+'({'+params_py+'},['+data_py.substring(1)+'])';
	document.getElementById("rs_server").value = data_py;
	document.getElementById("rs_json").value = "url: "+window.location.protocol+'//'+
	  window.location.host+"/nerva2py/ndi/call/jsonrpc2/\ndata: "+JSON.stringify(jdata);
}
