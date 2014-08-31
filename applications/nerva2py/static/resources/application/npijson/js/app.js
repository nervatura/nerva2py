/*
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
*/

//default data
var def_login = {server:"http://127.0.0.1:8000/npi/call/jsonrpc2/", 
                 database:"demo", username:"demo", password:""};
  
var msg_required = "This field is required!";
var msg_saved_all = "All records saved.";
var msg_saved = "The record is saved.";
var msg_changed = "The data has changed!";

//top controller object
var cont = new function() {
  var self = this;
  self.error_msg = ko.observable("");
  self.info_msg = ko.observable("");
  self.dirty = ko.observable(false);
  self.get_msg = ko.computed(function() {
    if (self.error_msg()) {
      return self.error_msg();
    } else {
      if (self.dirty()) {
        return msg_changed} 
      else { return self.info_msg();}}});
  self.ds = null;
}

//validators
ko.extenders.changed = function(target, option) {
  target.subscribe(function(newValue) {cont.dirty(true);});
return target;};

ko.extenders.bool = function(target, options) {
  var bool = ko.pureComputed({
    read: function () {
      if (target() === true) return 1;
      else if (target() === false) return 0;},
    write: function(value) {
      if (!value || (value.match && value.match(/^(false)|(null)|0|(undefined)|(NaN)$/))) {
        target(false);} else {target(true);}}});
  bool(target());
  return bool;};

ko.extenders.string = function(target, options) {
  var string = ko.pureComputed({
    read: target,
    write: function(newValue) {
      var current = target();
      valueToWrite = newValue;
      if (options) {
        for (var prop in options) {
          switch(prop) {
            case "required":
              cont.error_msg(newValue ? "" : msg_required);
              break;
            case "lover":
              if (valueToWrite) {
                valueToWrite = valueToWrite.toLowerCase();}
              break;
            case "upper":
              if (valueToWrite) {
                valueToWrite = valueToWrite.toUpperCase();}
              break;
            case "length":
              if (valueToWrite) {
                valueToWrite = valueToWrite.substr(0,options.length);}
              break;
            default:
              break;}}}
      if (valueToWrite !== current) {target(valueToWrite);} 
      else {if (newValue !== current) {target.notifySubscribers(valueToWrite);}}}
  }).extend({notify:'always'});
      string(target());
      return string;};
  
    ko.extenders.numeric = function(target, precision) {
      var result = ko.pureComputed({
        read: target,
        write: function(newValue) {
          var current = target(),
          roundingMultiplier = Math.pow(10, precision),
          newValueAsNum = isNaN(newValue) ? 0 : parseFloat(+newValue),
          valueToWrite = Math.round(newValueAsNum * roundingMultiplier) / roundingMultiplier;
          if (valueToWrite !== current) {
            target(valueToWrite);
          } else {
            if (newValue !== current) {target.notifySubscribers(valueToWrite);}}}
      }).extend({notify:'always'});
  result(target());
  return result;};

ko.extenders.required = function(target, message) {
  function validate(newValue) {
    cont.error_msg(newValue ? "" : message || msg_required);}
  validate(target());
  target.subscribe(validate);
  return target;};

//data model sample: numberdef
var numberdef = function(object) {
  if (typeof object==="undefined"){object={}};
  this.__tablename__ = 'numberdef';
  
  this.id = ko.observable(object.hasOwnProperty("id") ? object.id : null);
  this.numberkey = 
    ko.observable(object.hasOwnProperty("numberkey") ? object.numberkey:"???").extend(
    {string:{required:null}, changed:null});
  this.prefix = ko.observable(object.hasOwnProperty("prefix") ? object.prefix:null).extend(
    {changed:null});
  this.curvalue = ko.observable(object.hasOwnProperty("curvalue") ? object.curvalue:0).extend(
    {numeric:0, changed:null});
  this.isyear = ko.observable(object.hasOwnProperty("isyear") ? object.isyear:1).extend(
    {bool:null, changed:null});
  this.sep = ko.observable(object.hasOwnProperty("sep") ? object.sep:"/").extend(
    {string:{length:1}, changed:null});
  this.len = ko.observable(object.hasOwnProperty("len") ? object.len:5).extend(
    {numeric:0, changed:null});
  this.description = 
    ko.observable(object.hasOwnProperty("description") ? object.description:null).extend(
    {changed:null});
  this.visible = ko.observable(object.hasOwnProperty("visible") ? object.visible:0).extend(
    {bool:null, changed:null});
  this.readonly = ko.observable(object.hasOwnProperty("readonly") ? object.readonly:0).extend(
    {bool:null, changed:null});
  this.orderby = ko.observable(object.hasOwnProperty("orderby") ? object.orderby:0).extend(
    {numeric:0, changed:null});
};

//general data source
var dataSource = function(data_model) {
  var self = this;
  var table = data_model;
  var loadKoData = function(object, data) {
    for (var prop in data) {
      if(object.hasOwnProperty(prop)) {
        if(typeof object[prop] === "function") {
          object[prop](data[prop]);
        } else {
          object[prop] = data[prop];}}}}
  
  var loadTable = function(id) {
    var whereStr="";
    if (id!==null) {whereStr = "id="+id.toString();}
    var da = new ndiAdapter(self.database.server());
    da.loadTable(self.database.login(), self.current.__tablename__, whereStr, "", function(state,data){
      if (state==="ok") {
        self.items.removeAll();
        if (data.length===0) {
          self.newRecord();
        } else {
          for(var i=0; i<data.length; i++) {
            data[i].__tablename__ = self.current.__tablename__
            self.items.push(data[i]);
          }
          if (self.index()>=data.length) {self.index(0);}
          loadKoData(self.current,self.items()[self.index()]);
          cont.dirty(false);cont.error_msg("");cont.info_msg("");}
       } 
       else {cont.error_msg(data);}
     });
  };
  self.loadRecord = function() {
    loadTable(self.current.id());
  }
  self.loadRecordSet = function() {
    loadTable(null);
  }
  self.saveRecord = function() {
    if (!cont.error_msg() && cont.dirty()) {
      var da = new ndiAdapter(self.database.server());
      da.saveRecord(self.database.login(), ko.toJS(self.current), function(state,data){
        if (state==="ok") {
          loadKoData(self.current,data);
          cont.dirty(false);cont.info_msg(msg_saved);
        }
        else {cont.error_msg(data);}
      })
    }};
  self.saveRecordSet = function() {
    if (!cont.error_msg() && cont.dirty()) {
      self.items()[self.index()] = ko.toJS(self.current);
      var da = new ndiAdapter(self.database.server());
      da.saveRecordSet(self.database.login(), self.items(), function(state,data){
        if (state==="ok") {
          loadKoData(self.current,data);
          cont.dirty(false);cont.info_msg(msg_saved_all);
        }
        else {cont.error_msg(data);}
      })
    }};
  self.newRecord = function() {
    if (!cont.error_msg()) {
      var record = new table();
      self.items.push(ko.toJS(record));
      if (self.current) {
        goRecord(self.items().length-1);
      } else {
        return record;
      }
    }};
  self.deleteRecord = function() {
    if (!cont.error_msg() && self.current.id()) {
      var da = new ndiAdapter(self.database.server());
      da.deleteRecord(self.database.login(), ko.toJS(self.current), function(state,data){
        if (state==="ok") {
              self.loadRecordSet(null);
            }
            else {cont.error_msg(data);}
          })
        }
      }
      var goRecord = function(index) {
        var state = cont.dirty();
        self.items()[self.index()] = ko.toJS(self.current);
        self.index(index); loadKoData(self.current,self.items()[self.index()]);
        cont.dirty(state);
        return self.items()[self.index()]};
      self.firstRecord = function() {
        if (!cont.error_msg() && self.index()>0) {
          goRecord(0);}};
      self.prevRecord = function() {
        if (!cont.error_msg() && self.index()>0) {
          goRecord(self.index()-1);}};
      self.nextRecord = function() {
        if (!cont.error_msg() && self.index()<self.items().length-1) {
          goRecord(self.index()+1);}};
      self.lastRecord = function() {
        if (!cont.error_msg() && self.index()<self.items().length-1) {
          goRecord(self.items().length-1);}};
      
      self.items = ko.observableArray();
      self.index = ko.observable(0);
      self.current =self.newRecord();
      self.database = {
        server : ko.observable(def_login.server),
        database : ko.observable(def_login.database),
        username : ko.observable(def_login.username),
        password : ko.observable(def_login.password),
        login : function() {
          return {database:self.database.database(), 
            username:self.database.username(), password:self.database.password()};}}
    }
    cont.ds = new dataSource(numberdef);
 