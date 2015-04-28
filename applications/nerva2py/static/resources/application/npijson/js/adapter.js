/*
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2015, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
*/

var npiAdapter = function(host_address) {
//remote NPI adapter
  
  var initData = function(id, method) {
    return {"id":id, "method":method, "params":{}, "jsonrpc":"2.0"};};

  var postData = function(data, callback) {
    var xhr = new XMLHttpRequest();
    if ("withCredentials" in xhr) {
      xhr.open("post", host_address, true);
    } else if (typeof XDomainRequest != "undefined") {
      //for IE.
      xhr = new XDomainRequest();xhr.open("post", host_address);
    } else {
      return callback("error","CORS not supported.");}
  
    xhr.onload = function() {
      var response = JSON.parse(xhr.responseText);
      if ("error" in response) {
        return callback("error",response.error.message+": "+response.error.data);
      } else {
        if ("result" in response) {
          return callback("ok",response.result);
        } else {
          return callback("ok","OK");}
      }
    };

    xhr.onerror = function() {
      return callback("error","POST ERROR");};
  
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.send(JSON.stringify(data));
  };
  
  var postData_jquery = function(data, callback) {
    $.ajax({
      type: "post", contentType: "application/json",
      url: host_address, data: JSON.stringify(data),
      success: function(response){
        response = JSON.parse(response);
        if ("error" in response) {
          return callback("error",response.error.message+": "+response.error.data);
        } else {
          if ("result" in response) {
            return callback("ok",response.result);
          } else {
            return callback("ok","OK");}
        }},
      error: function(jqXHR, textStatus) {
        return callback("error","POST ERROR");}
    });
  };
  
  this.getLogin = function(database, username, password, callback) {
    var data = initData(1, "getLogin_json");
    data.params.database = database; data.params.username = username; data.params.password = password;
    postData(data, callback);
  };

  this.loadView = function(login, sqlKey, sqlStr, whereStr, havingStr, paramList, simpleList, 
                            orderStr, callback) {
    var data = initData(2, "loadView_json");
    data.params.login = login; data.params.sqlKey = sqlKey; data.params.sqlStr = sqlStr;
    data.params.whereStr = whereStr; data.params.havingStr = havingStr; data.params.paramList = paramList;
    data.params.simpleList = simpleList; data.params.orderStr = orderStr;
    postData(data, callback);
  };

  this.loadTable = function(login, classAlias, filterStr, orderStr, callback) {
    var data = initData(3, "loadTable_json");
    data.params.login = login; data.params.classAlias = classAlias; data.params.filterStr = filterStr;
    data.params.orderStr = orderStr;
    postData(data, callback);
  };

  this.loadDataSet = function(login, dataSetInfo, callback) {
    var data = initData(4, "loadDataSet_json");
    data.params.login = login; data.params.dataSetInfo = dataSetInfo;
    postData(data, callback);
  };

  this.executeSql = function(login, sqlKey, sqlStr, paramList, callback) {
    var data = initData(5, "executeSql_json");
    data.params.login = login; data.params.sqlKey = sqlKey; data.params.sqlStr = sqlStr;
    data.params.paramList = paramList;
    postData(data, callback);
  };

  this.saveRecord = function(login, record, callback) {
    var data = initData(6, "saveRecord_json");
    data.params.login = login; data.params.record = record;
    postData(data, callback);
  };

  this.saveRecordSet = function(login, recordSet, callback) {
    var data = initData(7, "saveRecordSet_json");
    data.params.login = login; data.params.recordSet = recordSet;
    postData(data, callback);
  };

  this.saveDataSet = function(login, dataSet, callback) {
    var data = initData(8, "saveDataSet_json");
    data.params.login = login; data.params.dataSet = dataSet;
    postData(data, callback);
  };

  this.deleteRecord = function(login, record, callback) {
    var data = initData(9, "deleteRecord_json");
    data.params.login = login; data.params.record = record;
    postData(data, callback);
  };

  this.deleteRecordSet = function(login, recordSet, callback) {
    var data = initData(10, "deleteRecordSet_json");
    data.params.login = login; data.params.recordSet = recordSet;
    postData(data, callback);
  };

  this.callFunction = function(login, functionName, paramList, callback) {
    var data = initData(11, "callFunction_json");
    data.params.login = login; data.params.functionName = functionName; data.params.paramList = paramList;
    postData(data, callback);
  };
};








