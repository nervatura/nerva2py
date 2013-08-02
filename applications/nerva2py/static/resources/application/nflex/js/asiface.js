
function getVernum(taskId, localHost) {	
	jQuery.ajax({
    	type: "POST", url: "http://"+localHost,
    	data: {"cmd":"vernum"},
    	contentType: "application/x-www-form-urlencoded; charset=UTF-8",
    	success: function(data) {
    		document.getElementById(attributes.id).setJSRequest(taskId, "vernum", data);
    		},
	    error: function(jqXHR, textStatus, errorThrown ) {
	    	document.getElementById(attributes.id).setJSRequest(taskId, "vernum", textStatus, "error");
	    	}
    });
}

function getPrinterSettings(taskId, localHost, orientation, size) {
	jQuery.ajax({
    	type: "POST", url: "http://"+localHost,
    	data: {"cmd":"printers","orientation":orientation,"size":size},
    	success: function(data) {
    		document.getElementById(attributes.id).setJSRequest(taskId, "printset", data);
    		},
	    error: function(jqXHR, textStatus, errorThrown ) {
	    	document.getElementById(attributes.id).setJSRequest(taskId, "printset", textStatus, "error");
	    	}
    });
}

function exportPdf(taskId, localHost, refnumber, pdf) {
	jQuery.ajax({
    	type: "POST", url: "http://"+localHost,
    	data: {"cmd":"export","file":pdf,"filename":refnumber+".pdf","dir":"export","encode":"base64"},
    	success: function(data) {
    		document.getElementById(attributes.id).setJSRequest(taskId, "export", data);
    		},
	    error: function(jqXHR, textStatus, errorThrown ) {
	    	document.getElementById(attributes.id).setJSRequest(taskId, "export", textStatus, "error");
	    	}
    });
}

function printPdf(taskId, localHost, refnumber, pdf, printer, copies, size, orientation) {
	jQuery.ajax({
    	type: "POST", url: "http://"+localHost,
    	data: {"cmd":"print","file":pdf,"filename":refnumber+".pdf",
    		"printer":printer,"copies":copies,"size":size,"orientation":orientation,"encode":"base64"},
    	success: function(data) {
    		document.getElementById(attributes.id).setJSRequest(taskId, "export", data);
    		},
	    error: function(jqXHR, textStatus, errorThrown ) {
	    	document.getElementById(attributes.id).setJSRequest(taskId, "export", textStatus, "error");
	    	}
    });
}