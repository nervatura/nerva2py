function get_base_url(){return window.location.protocol+"//"+window.location.host+"/"+document.getElementById("appl_url").className}
function createDatabase(){var b=document.getElementById("cmb_alias").value;if(""==b)return alert("Missing database!"),!1;document.getElementById("msg_result").innerHTML="Process started. Waiting for the server to respond ...";confirm("Start the database creation. Do you want to continue?")?callFunction(get_base_url()+"/createDatabase?alias="+b,"msg_result"):document.getElementById("msg_result").innerHTML="Starting the process?";return!0}
function createDataBackup(){var b=document.getElementById("cmb_alias").value,c=document.getElementById("cmb_format").value,a=document.getElementById("cmb_filename").value,d="";null!=document.getElementById("cust_filename")&&(d=document.getElementById("cust_filename").value);if(""==b)return alert("Missing database!"),!1;if("custom"==a){if(""==d)return alert("Missing custom filename!"),!1;a=d}confirm("Start the customer backup creation. Do you want to continue?")?"download"==a?(document.getElementById("msg_result").innerHTML=
"Starting the process?",window.location.assign(get_base_url()+"/createDataBackup?alias="+b+"&bformat="+c+"&filename="+a)):(document.getElementById("msg_result").innerHTML="Process started. Waiting for the server to respond ...",callFunction(get_base_url()+"/createDataBackup?alias="+b+"&bformat="+c+"&filename="+a,"msg_result")):document.getElementById("msg_result").innerHTML="Starting the process?";return!0}
function callFunction(b,c){var a=new XMLHttpRequest;a.open("POST",b,!1);a.send();""!=c&&("alert"==c?alert(a.responseText):$("#"+c).html(a.responseText))};