var npiAdapter=function(l){var g=function(d,c){return{id:d,method:c,params:{},jsonrpc:"2.0"}},h=function(d,c){var b=new XMLHttpRequest;if("withCredentials"in b)b.open("post",l,!0);else if("undefined"!=typeof XDomainRequest)b=new XDomainRequest,b.open("post",l);else return c("error","CORS not supported.");b.onload=function(){var a=JSON.parse(b.responseText);return"error"in a?c("error",a.error.message+": "+a.error.data):"result"in a?c("ok",a.result):c("ok","OK")};b.onerror=function(){return c("error",
"POST ERROR")};b.setRequestHeader("Accept","application/json");b.send(JSON.stringify(d))};this.getLogin=function(d,c,b,a){var e=g(1,"getLogin_json");e.params.database=d;e.params.username=c;e.params.password=b;h(e,a)};this.loadView=function(d,c,b,a,e,f,l,m,n){var k=g(2,"loadView_json");k.params.login=d;k.params.sqlKey=c;k.params.sqlStr=b;k.params.whereStr=a;k.params.havingStr=e;k.params.paramList=f;k.params.simpleList=l;k.params.orderStr=m;h(k,n)};this.loadTable=function(d,c,b,a,e){var f=g(3,"loadTable_json");
f.params.login=d;f.params.classAlias=c;f.params.filterStr=b;f.params.orderStr=a;h(f,e)};this.loadDataSet=function(d,c,b){var a=g(4,"loadDataSet_json");a.params.login=d;a.params.dataSetInfo=c;h(a,b)};this.executeSql=function(d,c,b,a,e){var f=g(5,"executeSql_json");f.params.login=d;f.params.sqlKey=c;f.params.sqlStr=b;f.params.paramList=a;h(f,e)};this.saveRecord=function(d,c,b){var a=g(6,"saveRecord_json");a.params.login=d;a.params.record=c;h(a,b)};this.saveRecordSet=function(d,c,b){var a=g(7,"saveRecordSet_json");
a.params.login=d;a.params.recordSet=c;h(a,b)};this.saveDataSet=function(d,c,b){var a=g(8,"saveDataSet_json");a.params.login=d;a.params.dataSet=c;h(a,b)};this.deleteRecord=function(d,c,b){var a=g(9,"deleteRecord_json");a.params.login=d;a.params.record=c;h(a,b)};this.deleteRecordSet=function(d,c,b){var a=g(10,"deleteRecordSet_json");a.params.login=d;a.params.recordSet=c;h(a,b)};this.callFunction=function(d,c,b,a){var e=g(11,"callFunction_json");e.params.login=d;e.params.functionName=c;e.params.paramList=
b;h(e,a)}};