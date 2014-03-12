--Customer View;
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('CustomerView', '', 'and c.id = -1', 'customer', 'browser_customer_edit', 'CustomerView', 0);
UPDATE ui_applview SET sqlstr='select c.id,
  c.custnumber, c.custname, case when mst.msg is null then tg.groupvalue else mst.msg end as custtype,
  c.taxnumber, c.account, c.notax, c.terms, c.creditlimit,
  c.discount, c.notes, c.inactive, 
  case when addr.city is null then '''' else addr.city end || '' '' || case when addr.street is null then '''' else addr.street end as address
from customer c
inner join groups tg on c.custtype = tg.id
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''custtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
left join (select * from address
  where id in(select min(id) fid from address a
    where a.deleted=0 and a.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'')
    group by a.ref_id)) addr on c.id = addr.ref_id
where c.deleted=0 and c.id not in(select customer.id from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') @where_str '
WHERE viewname='CustomerView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerView', 'custnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'c.custnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerView', 'custname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'c.custname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerView', 'taxnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'c.taxnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerView', 'custtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));    
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerView', 'account', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'c.account ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));    
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerView', 'notax', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'c.notax ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerView', 'terms', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'c.terms ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerView', 'creditlimit', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'c.creditlimit ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerView', 'discount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'c.discount ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'c.notes', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));      
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerView', 'inactive', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'c.inactive', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerView', 'address', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 11, 'case when addr.city is null then '''' else addr.city end || '' '' || case when addr.street is null then '''' else addr.street end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('CustomerFieldsView', '', 'and c.id = -1', 'customer', 'browser_customer_edit', 'CustomerView', 1);
UPDATE ui_applview SET sqlstr='select c.id, c.custnumber, c.custname, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL) as number_value,
case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end as date_value,
case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end as bool_value,
case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end as refnumber,
fv.notes
from fieldvalue fv
inner join deffield df on fv.fieldname = df.fieldname and df.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') and df.visible = 1
inner join groups fg on df.fieldtype = fg.id
inner join customer c on fv.ref_id = c.id
left join customer rf_customer on fv.value = cast(rf_customer.id as text)
left join tool rf_tool on fv.value = cast(rf_tool.id as text)
left join trans rf_trans on fv.value = cast(rf_trans.id as text)
left join product rf_product on fv.value = cast(rf_product.id as text)
left join project rf_project on fv.value = cast(rf_project.id as text)
left join employee rf_employee on fv.value = cast(rf_employee.id as text)
left join place rf_place on fv.value = cast(rf_place.id as text)
where fv.deleted = 0 and c.deleted=0 and c.id not in(select customer.id from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') @where_str'
WHERE viewname='CustomerFieldsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerFieldsView', 'custnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'c.custnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerFieldsView', 'custname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'c.custname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerFieldsView', 'fielddef', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'df.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerFieldsView', 'text_value', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerFieldsView', 'number_value', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL)', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerFieldsView', 'date_value', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerFieldsView', 'bool_value', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerFieldsView', 'refnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerFieldsView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'fv.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('CustomerContactView', '', 'and c.id = -1', 'customer', 'browser_customer_edit', 'CustomerView', 2);
UPDATE ui_applview SET sqlstr='select c.id, c.custnumber, c.custname, co.firstname, co.surname, co.status, co.phone, co.fax, co.mobil, co.email, co.notes
from contact co
inner join customer c on co.ref_id = c.id
where co.deleted=0 and c.deleted=0 and co.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') 
  and c.id not in(select customer.id from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') @where_str'
WHERE viewname='CustomerContactView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerContactView', 'custnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'c.custnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerContactView', 'custname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'c.custname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerContactView', 'firstname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'co.firstname', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerContactView', 'surname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, ' co.surname', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerContactView', 'status', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, ' co.status', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerContactView', 'phone', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, ' co.phone', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerContactView', 'fax', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, ' co.fax', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerContactView', 'mobil', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, ' co.mobil', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerContactView', 'email', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, ' co.email', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerContactView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, ' co.notes', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('CustomerAddressView', '', 'and c.id = -1', 'customer', 'browser_customer_edit', 'CustomerView', 3);
UPDATE ui_applview SET sqlstr='select c.id, c.custnumber, c.custname, a.country, a.state, a.zipcode, a.city, a.street, a.notes 
from address a
inner join customer c on a.ref_id = c.id
where a.deleted=0 and c.deleted=0 and a.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') 
  and c.id not in(select customer.id from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') @where_str'
WHERE viewname='CustomerAddressView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerAddressView', 'custnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'c.custnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerAddressView', 'custname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'c.custname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerAddressView', 'country', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'a.country', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerAddressView', 'state', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'a.state', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerAddressView', 'zipcode', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'a.zipcode ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerAddressView', 'city', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'a.city', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerAddressView', 'street', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'a.street', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerAddressView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'a.notes', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('CustomerGroupsView', '', 'and c.id = -1', 'customer', 'browser_customer_edit', 'CustomerView', 4);
UPDATE ui_applview SET sqlstr='select c.id, c.custnumber, c.custname, g.groupvalue, g.description
from customer c
inner join link l on c.id = l.ref_id_1 and l.nervatype_1 = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'')
inner join groups g on l.ref_id_2 = g.id and l.nervatype_2 = (select id from groups where groupname=''nervatype'' and groupvalue=''groups'')
where c.deleted = 0 and g.deleted = 0 and l.deleted=0 and c.id not in(select customer.id from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') @where_str'
WHERE viewname='CustomerGroupsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerGroupsView', 'custnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'c.custnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerGroupsView', 'custname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'c.custname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerGroupsView', 'groupvalue', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'g.groupvalue', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerGroupsView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'g.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('CustomerEvents', '', 'and e.id = -1', 'event', 'browser_event_edit', 'CustomerView', 5);
UPDATE ui_applview SET sqlstr='select e.id, c.custnumber, c.custname, e.calnumber, eg.groupvalue as eventgroup, 
  cast(e.fromdate as date) as fromdate, substr(cast(cast(e.fromdate as time) as text), 0, 6) as fromtime, 
  cast(e.todate as date) as todate, substr(cast(cast(e.todate as time) as text), 0, 6) as totime,
  e.subject, e.place, e.description
from event e
inner join customer c on e.ref_id = c.id
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and c.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') 
  and c.id not in(select customer.id from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') @where_str'
WHERE viewname='CustomerEvents';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerEvents', 'custnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'c.custnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerEvents', 'custname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'c.custname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerEvents', 'calnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'e.calnumber', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerEvents', 'eventgroup', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'eg.groupvalue', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerEvents', 'fromdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'cast(e.fromdate as date)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerEvents', 'fromtime', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'substr(cast(cast(e.fromdate as time) as text), 0, 6)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerEvents', 'todate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'cast(e.todate as date)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerEvents', 'totime', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'substr(cast(cast(e.todate as time) as text), 0, 6)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerEvents', 'subject', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'e.subject', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerEvents', 'place', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'e.place', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('CustomerEvents', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'e.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

--Product View;
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProductView', '', 'and p.id = -1', 'product', 'browser_product_edit', 'ProductView', 0);
UPDATE ui_applview SET sqlstr='select p.id, p.partnumber, case when ms.msg is null then g.groupvalue else ms.msg end as protype, p.description, 
  t.taxcode as tax, p.notes, p.webitem, p.inactive
from product p
inner join groups g on p.protype = g.id
left join ui_message ms on ms.fieldname = g.groupvalue and  ms.secname = ''protype'' and ms.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join tax t on p.tax_id = t.id
where p.deleted = 0 @where_str'
WHERE viewname='ProductView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductView', 'partnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.partnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductView', 'protype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'case when ms.msg is null then g.groupvalue else ms.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductView', 'tax', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 't.taxcode ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductView', 'webitem', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'p.webitem  ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductView', 'inactive', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'p.inactive  ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'p.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProductFieldsView', '', 'and p.id = -1', 'product', 'browser_product_edit', 'ProductView', 1);
UPDATE ui_applview SET sqlstr='select p.id, p.partnumber, p.description, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL) as number_value,
case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end as date_value,
case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end as bool_value,
case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end as refnumber,
fv.notes
from fieldvalue fv
inner join deffield df on fv.fieldname = df.fieldname and df.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''product'') and df.visible = 1
inner join groups fg on df.fieldtype = fg.id
inner join product p on fv.ref_id = p.id
left join customer rf_customer on fv.value = cast(rf_customer.id as text)
left join tool rf_tool on fv.value = cast(rf_tool.id as text)
left join trans rf_trans on fv.value = cast(rf_trans.id as text)
left join product rf_product on fv.value = cast(rf_product.id as text)
left join project rf_project on fv.value = cast(rf_project.id as text)
left join employee rf_employee on fv.value = cast(rf_employee.id as text)
left join place rf_place on fv.value = cast(rf_place.id as text)
where fv.deleted = 0 and p.deleted=0  @where_str'
WHERE viewname='ProductFieldsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductFieldsView', 'partnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.partnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductFieldsView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductFieldsView', 'fielddef', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'df.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductFieldsView', 'text_value', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductFieldsView', 'number_value', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL)', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductFieldsView', 'date_value', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductFieldsView', 'bool_value', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductFieldsView', 'refnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductFieldsView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'fv.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
  
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProductGroupsView', '', 'and p.id = -1', 'product', 'browser_product_edit', 'ProductView', 2);
UPDATE ui_applview SET sqlstr='select p.id, p.partnumber, p.description as partname, g.groupvalue, g.description
from product p
inner join link l on p.id = l.ref_id_1 and l.nervatype_1 = (select id from groups where groupname=''nervatype'' and groupvalue=''product'')
inner join groups g on l.ref_id_2 = g.id and l.nervatype_2 = (select id from groups where groupname=''nervatype'' and groupvalue=''groups'')
where p.deleted = 0 and g.deleted = 0 and l.deleted=0 @where_str'
WHERE viewname='ProductGroupsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductGroupsView', 'partnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.partnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductGroupsView', 'partname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductGroupsView', 'groupvalue', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'g.groupvalue', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductGroupsView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'g.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProductBarcodeView', '', 'and p.id = -1', 'product', 'browser_product_edit', 'ProductView', 3);
UPDATE ui_applview SET sqlstr='select p.id, p.partnumber, p.description as partname, p.unit, b.code as barcode, b.description, g.description as barcodetype, 
  b.qty, b.defcode
from barcode b
inner join product p on b.product_id = p.id inner join groups g on b.barcodetype = g.id
where p.deleted = 0 @where_str'
WHERE viewname='ProductBarcodeView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductBarcodeView', 'partnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.partnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductBarcodeView', 'partname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductBarcodeView', 'unit', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'p.unit ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductBarcodeView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'b.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductBarcodeView', 'barcodetype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'g.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductBarcodeView', 'qty', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'b.qty ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductBarcodeView', 'defcode', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'b.defcode ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));  
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductBarcodeView', 'barcode', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'b.id ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
    
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProductPriceView', '', 'and p.id = -1', 'price', 'browser_product_edit', 'ProductView', 4);
UPDATE ui_applview SET sqlstr='select p.id, p.partnumber, p.description, p.unit, pr.vendorprice as vendor, c.custname, gc.groupvalue as custgroup, pr.validfrom, pr.validto, pr.curr, pr.qty, pr.pricevalue
from price pr
inner join product p on pr.product_id = p.id
left join link ln0 on ln0.nervatype_1 = (select id from groups where groupname=''nervatype'' and groupvalue=''price'') and ln0.ref_id_1 = pr.id 
  and ln0.deleted=0 and ln0.nervatype_2 = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'')
  left join customer c on ln0.ref_id_2 = c.id and c.deleted=0
left join link ln1 on ln1.nervatype_1 = (select id from groups where groupname=''nervatype'' and groupvalue=''price'') and ln1.ref_id_1 = pr.id 
  and ln1.deleted=0 and ln1.nervatype_2 = (select id from groups where groupname=''nervatype'' and groupvalue=''groups'')
  left join groups gc on ln1.ref_id_2 = gc.id and gc.deleted=0
where p.deleted = 0 and pr.deleted = 0 and pr.discount is null @where_str'
WHERE viewname='ProductPriceView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductPriceView', 'partnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.partnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductPriceView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductPriceView', 'unit', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'p.unit ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductPriceView', 'vendor', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'pr.vendorprice ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductPriceView', 'custname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'c.custname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductPriceView', 'custgroup', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'gc.groupvalue ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductPriceView', 'validfrom', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'pr.validfrom ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductPriceView', 'validto', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'pr.validto ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductPriceView', 'curr', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'pr.curr ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductPriceView', 'qty', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'pr.qty ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductPriceView', 'pricevalue', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'pr.pricevalue ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));  
  
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProductDiscountView', '', 'and p.id = -1', 'price', 'browser_product_edit', 'ProductView', 5);
UPDATE ui_applview SET sqlstr='select p.id, p.partnumber, p.description, p.unit, pr.vendorprice as vendor, c.custname, gc.groupvalue as custgroup, pr.validfrom, pr.validto, pr.curr, 
  case when ms.msg is null then g.description else ms.msg end as calcmode,
  pr.qty, pr.pricevalue, pr.discount
from price pr
inner join product p on pr.product_id = p.id
left join groups g on pr.calcmode = g.id
  left join ui_message ms on ms.fieldname = g.groupvalue and  ms.secname = ''calcmode'' and ms.lang = (select value from fieldvalue where fieldname = ''default_lang'')
left join link ln0 on ln0.nervatype_1 = (select id from groups where groupname=''nervatype'' and groupvalue=''price'') and ln0.ref_id_1 = pr.id 
  and ln0.deleted=0 and ln0.nervatype_2 = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'')
  left join customer c on ln0.ref_id_2 = c.id and c.deleted=0
left join link ln1 on ln1.nervatype_1 = (select id from groups where groupname=''nervatype'' and groupvalue=''price'') and ln1.ref_id_1 = pr.id 
  and ln1.deleted=0 and ln1.nervatype_2 = (select id from groups where groupname=''nervatype'' and groupvalue=''groups'')
  left join groups gc on ln1.ref_id_2 = gc.id and gc.deleted=0
where p.deleted = 0 and pr.deleted = 0 and pr.discount is not null @where_str'
WHERE viewname='ProductDiscountView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'partnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.partnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'unit', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'p.unit ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
  INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'vendor', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'pr.vendorprice ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'custname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'c.custname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'custgroup', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'gc.groupvalue ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'validfrom', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'pr.validfrom ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'validto', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'pr.validto ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'curr', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'pr.curr ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'calcmode', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'case when ms.msg is null then g.description else ms.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'qty', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'pr.qty ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'pricevalue', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 11, 'pr.pricevalue ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductDiscountView', 'discount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 12, 'pr.discount ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
  
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProductEvents', '', 'and e.id = -1', 'event', 'browser_event_edit', 'ProductView', 6);
UPDATE ui_applview SET sqlstr='select e.id, p.partnumber, p.description as partname, e.calnumber, eg.groupvalue as eventgroup, 
  cast(e.fromdate as date) as fromdate, substr(cast(cast(e.fromdate as time) as text), 0, 6) as fromtime, 
  cast(e.todate as date) as todate, substr(cast(cast(e.todate as time) as text), 0, 6) as totime,
  e.subject, e.place, e.description
from event e
inner join product p on e.ref_id = p.id
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and p.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''product'') @where_str'
WHERE viewname='ProductEvents';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductEvents', 'partnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.partnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductEvents', 'partname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductEvents', 'calnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'e.calnumber', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductEvents', 'eventgroup', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'eg.groupvalue', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductEvents', 'fromdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'cast(e.fromdate as date)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductEvents', 'fromtime', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'substr(cast(cast(e.fromdate as time) as text), 0, 6)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductEvents', 'todate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'cast(e.todate as date)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductEvents', 'totime', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'substr(cast(cast(e.todate as time) as text), 0, 6)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductEvents', 'subject', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'e.subject', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductEvents', 'place', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'e.place', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProductEvents', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'e.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

--Trans Items;
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('TransItemHeadView', '', 'and t.id = -1', 'transitem', 'browser_transitem_edit', 'TransItemHeadView', 0);
UPDATE ui_applview SET sqlstr='select t.id||''_''||tg.groupvalue||''_''||dg.groupvalue as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when msd.msg is null then dg.groupvalue else msd.msg end as direction,
  case when msc.msg is null then fv.value else msc.msg end as transcast, 
  t.transnumber, t.ref_transnumber, t.crdate, t.transdate, t.duedate, c.custname, e.empnumber, deg.groupvalue as department, p.pronumber, 
  case when msp.msg is null then ptg.groupvalue else msp.msg end as paidtype,
  t.curr, irow.netamount, irow.vatamount, irow.amount,
  t.notax, t.paid,t.acrate, t.notes, t.intnotes, t.fnote,  
  case when mss.msg is null then sg.groupvalue else mss.msg end as transtate,
  t.closed, t.deleted,
  cast(reholiday.value as real) as reholiday, cast(rebadtool.value as real) as rebadtool, cast(reother.value as real) as reother, rentnote.value as rentnote,
  cast(wsdistance.value as real) as wsdistance, cast(wsrepair.value as real) as wsrepair, cast(wstotal.value as real) as wstotal, wsnote.value as wsnote
from trans t
inner join groups tg on t.transtype = tg.id and tg.groupvalue in(''invoice'',''receipt'',''order'',''offer'',''worksheet'',''rent'')
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''transtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join groups dg on t.direction = dg.id
  left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'')
left join customer c on t.customer_id = c.id
left join employee e on t.employee_id = e.id
left join groups deg on t.department = deg.id
left join project p on t.project_id = p.id
inner join groups ptg on t.paidtype = ptg.id
  left join ui_message msp on msp.fieldname = ptg.groupvalue and  msp.secname = ''paidtype'' and msp.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join groups sg on t.transtate = sg.id
  left join ui_message mss on mss.fieldname = sg.groupvalue and  mss.secname = ''transtate'' and mss.lang = (select value from fieldvalue where fieldname = ''default_lang'')
left join fieldvalue fv on t.id = fv.ref_id and fv.fieldname = ''trans_transcast''
  left join ui_message msc on msc.fieldname = fv.value and  msc.secname = ''trans_transcast'' and msc.lang = (select value from fieldvalue where fieldname = ''default_lang'')
left join fieldvalue reholiday on t.id = reholiday.ref_id and reholiday.fieldname = ''trans_reholiday''
left join fieldvalue rebadtool on t.id = rebadtool.ref_id and rebadtool.fieldname = ''trans_rebadtool''
left join fieldvalue reother on t.id = reother.ref_id and reother.fieldname = ''trans_reother''
left join fieldvalue rentnote on t.id = rentnote.ref_id and rentnote.fieldname = ''trans_rentnote''
left join fieldvalue wsdistance on t.id = wsdistance.ref_id and wsdistance.fieldname = ''trans_wsdistance''
left join fieldvalue wsrepair on t.id = wsrepair.ref_id and wsrepair.fieldname = ''trans_wsrepair''
left join fieldvalue wstotal on t.id = wstotal.ref_id and wstotal.fieldname = ''trans_wstotal''
left join fieldvalue wsnote on t.id = wsnote.ref_id and wsnote.fieldname = ''trans_wsnote''
left join (select trans_id, sum(netamount) as netamount, sum(vatamount) as vatamount, sum(amount) as amount
  from item where deleted=0 group by trans_id) irow on t.id = irow.trans_id
where (t.deleted=0 or (tg.groupvalue=''invoice'' and dg.groupvalue=''out'') or (tg.groupvalue=''receipt'' and dg.groupvalue=''out'')) @where_str'
WHERE viewname='TransItemHeadView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'transtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'case when msd.msg is null then dg.groupvalue else msd.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'transcast', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'case when msc.msg is null then fv.value else msc.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 't.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'ref_transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 't.ref_transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));  
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'crdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 't.crdate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'transdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 't.transdate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));   
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'duedate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 't.duedate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'custname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'c.custname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'empnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'e.empnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'department', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'deg.groupvalue ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'pronumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 11, 'p.pronumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'paidtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 12, 'case when msp.msg is null then ptg.groupvalue else msp.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'curr', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 13, 't.curr ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'netamount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 14, 'irow.netamount ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'vatamount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 15, 'irow.vatamount ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'amount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 16, 'irow.amount ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));    
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'notax', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 17, 't.notax ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'paid', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 18, 't.paid ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'acrate', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 19, 't.acrate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 20, 't.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'intnotes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 21, 't.intnotes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'fnote', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 22, 't.fnote ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'transtate', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 23, 'case when mss.msg is null then sg.groupvalue else mss.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'closed', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 24, 't.closed ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'deleted', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 25, 't.deleted ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'reholiday', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 26, 'cast(reholiday.value as real) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'rebadtool', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 27, 'cast(rebadtool.value as real) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));       
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'reother', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 28, 'cast(reother.value as real) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));  
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'rentnote', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 29, 'rentnote.value) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'wsdistance', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 30, 'cast(wsdistance.value as real) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'wsrepair', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 31, 'cast(wsrepair.value as real) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'wstotal', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 32, 'cast(wstotal.value as real) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'wsnote', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 33, 'cast(wsnote.value) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
    
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'cb_offer', (select id from groups where groupname='fieldtype' and groupvalue='checkbox'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'and (tg.groupvalue=''offer'') ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'cb_order', (select id from groups where groupname='fieldtype' and groupvalue='checkbox'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'and (tg.groupvalue=''order'') ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'cb_worksheet', (select id from groups where groupname='fieldtype' and groupvalue='checkbox'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'and (tg.groupvalue=''worksheet'') ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'cb_rent', (select id from groups where groupname='fieldtype' and groupvalue='checkbox'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'and (tg.groupvalue=''rent'') ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));  
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'cb_invoice', (select id from groups where groupname='fieldtype' and groupvalue='checkbox'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'and (tg.groupvalue=''invoice'') ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'fl_employee', (select id from groups where groupname='fieldtype' and groupvalue='filter'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 't.cruser_id=@employee_id ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemHeadView', 'fl_usergroup', (select id from groups where groupname='fieldtype' and groupvalue='filter'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 't.cruser_id in (select id from employee where usergroup = @usergroup_id) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
    
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('TransItemFieldsView', '', 'and t.id = -1', 'transitem', 'browser_transitem_edit', 'TransItemHeadView', 1);
UPDATE ui_applview SET sqlstr='select t.id||''_''||tg.groupvalue||''_''||dg.groupvalue as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when msd.msg is null then dg.groupvalue else msd.msg end as direction, t.transnumber, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL) as number_value,
case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end as date_value,
case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end as bool_value,
case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end as refnumber,
fv.notes
from fieldvalue fv
inner join deffield df on fv.fieldname = df.fieldname and df.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''trans'') and df.visible = 1
inner join groups fg on df.fieldtype = fg.id
inner join trans t on fv.ref_id = t.id
inner join groups tg on t.transtype = tg.id and tg.groupvalue in(''invoice'',''receipt'',''order'',''offer'',''worksheet'',''rent'')
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''transtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join groups dg on t.direction = dg.id
  left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'')
left join customer rf_customer on fv.value = cast(rf_customer.id as text)
left join tool rf_tool on fv.value = cast(rf_tool.id as text)
left join trans rf_trans on fv.value = cast(rf_trans.id as text)
left join product rf_product on fv.value = cast(rf_product.id as text)
left join project rf_project on fv.value = cast(rf_project.id as text)
left join employee rf_employee on fv.value = cast(rf_employee.id as text)
left join place rf_place on fv.value = cast(rf_place.id as text)
where fv.deleted = 0 and (t.deleted=0 or (tg.groupvalue=''invoice'' and dg.groupvalue=''out'') or (tg.groupvalue=''receipt'' and dg.groupvalue=''out''))  
 @where_str'
WHERE viewname='TransItemFieldsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemFieldsView', 'transtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemFieldsView', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'case when msd.msg is null then dg.groupvalue else msd.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemFieldsView', 'transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 't.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemFieldsView', 'fielddef', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'df.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemFieldsView', 'text_value', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemFieldsView', 'number_value', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL)', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemFieldsView', 'date_value', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemFieldsView', 'bool_value', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemFieldsView', 'refnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemFieldsView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'fv.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('TransItemRowView', '', 'and t.id = -1', 'transitem', 'browser_transitem_edit', 'TransItemHeadView', 2);
UPDATE ui_applview SET sqlstr='select t.id||''_''||tg.groupvalue||''_''||dg.groupvalue as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when msd.msg is null then dg.groupvalue else msd.msg end as direction, t.transnumber, t.transdate, t.curr,
  p.partnumber, i.description, i.unit, i.qty, i.fxprice, i.netamount, i.discount as discount, tax.taxcode, i.vatamount, i.amount,
  i.deposit, i.actionprice, i.ownstock 
from item i
inner join trans t on i.trans_id = t.id
inner join groups tg on t.transtype = tg.id
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''transtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join groups dg on t.direction = dg.id
  left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join product p on i.product_id = p.id
inner join tax on i.tax_id = tax.id
where i.deleted = 0 and (t.deleted=0 or (tg.groupvalue=''invoice'' and dg.groupvalue=''out'') or (tg.groupvalue=''receipt'' and dg.groupvalue=''out'')) @where_str'
WHERE viewname='TransItemRowView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'transtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'case when msd.msg is null then dg.groupvalue else msd.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 't.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'transdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 't.transdate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'curr', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 't.curr ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'partnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'p.partnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'i.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'unit', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'i.unit ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'qty', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'i.qty ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));        
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'fxprice', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'i.fxprice ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'netamount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'i.netamount ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'discount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 11, 'i.discount ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'taxcode', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 12, 'tax.taxcode ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'vatamount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 13, 'i.vatamount ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'amount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 14, 'i.amount ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));     
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'deposit', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 15, 'i.deposit ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'actionprice', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 16, 'i.actionprice ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemRowView', 'ownstock', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 17, 'i.ownstock ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
  
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('TransItemGroupsView', '', 'and t.id = -1', 'transitem', 'browser_transitem_edit', 'TransItemHeadView', 3);
UPDATE ui_applview SET sqlstr='select t.id||''_''||tg.groupvalue||''_''||dg.groupvalue as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when msd.msg is null then dg.groupvalue else msd.msg end as direction, t.transnumber, g.groupvalue, g.description
from trans t
inner join groups tg on t.transtype = tg.id and tg.groupvalue in(''invoice'',''receipt'',''order'',''offer'',''worksheet'',''rent'')
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''transtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join groups dg on t.direction = dg.id
  left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join link l on t.id = l.ref_id_1 and l.nervatype_1 = (select id from groups where groupname=''nervatype'' and groupvalue=''trans'')
inner join groups g on l.ref_id_2 = g.id and l.nervatype_2 = (select id from groups where groupname=''nervatype'' and groupvalue=''groups'')
where (t.deleted=0 or (tg.groupvalue=''invoice'' and dg.groupvalue=''out'') or (tg.groupvalue=''receipt'' and dg.groupvalue=''out''))and g.deleted = 0 and l.deleted=0
 @where_str'
WHERE viewname='TransItemGroupsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemGroupsView', 'transtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemGroupsView', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'case when msd.msg is null then dg.groupvalue else msd.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemGroupsView', 'transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 't.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemGroupsView', 'groupvalue', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'g.groupvalue', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('TransItemGroupsView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'g.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

--Payment;
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('PaymentView', '', 'and t.id = -1', 'payment', 'browser_payment_edit', 'PaymentView', 0);
UPDATE ui_applview SET sqlstr='select t.id||''_''||tg.groupvalue||''_''||dg.groupvalue as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when tg.groupvalue=''bank'' then '''' else case when msd.msg is null then dg.groupvalue else msd.msg end end as direction,
  case when msc.msg is null then fv.value else msc.msg end as transcast, 
  t.transnumber, t.ref_transnumber, t.crdate, pm.paiddate, pc.description as place, 
  pc.curr, case when dg.groupvalue=''out'' then -pm.amount else pm.amount end amount, pm.notes as description, e.empnumber,
  case when mss.msg is null then sg.groupvalue else mss.msg end as transtate,
  t.closed, t.deleted,
  t.notes, t.intnotes, t.fnote
from trans t
inner join groups tg on t.transtype = tg.id
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''transtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join groups dg on t.direction = dg.id
  left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join place pc on t.place_id = pc.id
left join employee e on t.employee_id = e.id
inner join groups sg on t.transtate = sg.id
  left join ui_message mss on mss.fieldname = sg.groupvalue and  mss.secname = ''transtate'' and mss.lang = (select value from fieldvalue where fieldname = ''default_lang'')
left join fieldvalue fv on t.id = fv.ref_id and fv.fieldname = ''trans_transcast''
  left join ui_message msc on msc.fieldname = fv.value and  msc.secname = ''trans_transcast'' and msc.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join payment pm on t.id = pm.trans_id and pm.deleted=0
where (t.deleted=0 or (tg.groupvalue=''cash'')) @where_str'
WHERE viewname='PaymentView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'transtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'case when tg.groupvalue=''bank'' then '''' else case when msd.msg is null then dg.groupvalue else msd.msg end end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'transcast', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'case when msc.msg is null then fv.value else msc.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 't.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'ref_transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 't.ref_transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));  
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'crdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 't.crdate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'paiddate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'pm.paiddate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));   
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'place', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'pc.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'curr', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'pc.curr ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'amount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'case when dg.groupvalue=''out'' then -pm.amount else pm.amount end ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));    
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'pm.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'empnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 11, 'e.empnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'transtate', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 12, 'case when mss.msg is null then sg.groupvalue else mss.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'closed', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 13, 't.closed ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'deleted', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 14, 't.deleted ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 15, 't.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'intnotes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 16, 't.intnotes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'fnote', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 17, 't.fnote ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
  
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'cb_bank', (select id from groups where groupname='fieldtype' and groupvalue='checkbox'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'and (tg.groupvalue=''bank'') ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'cb_cash', (select id from groups where groupname='fieldtype' and groupvalue='checkbox'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'and (tg.groupvalue=''cash'') ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'fl_employee', (select id from groups where groupname='fieldtype' and groupvalue='filter'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, ' t.cruser_id=@employee_id ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentView', 'fl_usergroup', (select id from groups where groupname='fieldtype' and groupvalue='filter'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 't.cruser_id in (select id from employee where usergroup = @usergroup_id) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
    
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('PaymentFieldsView', '', 'and t.id = -1', 'payment', 'browser_payment_edit', 'PaymentView', 1);
UPDATE ui_applview SET sqlstr='select t.id||''_''||tg.groupvalue||''_''||dg.groupvalue as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when tg.groupvalue=''bank'' then '''' else case when msd.msg is null then dg.groupvalue else msd.msg end end as direction, 
  t.transnumber, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL) as number_value,
case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end as date_value,
case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end as bool_value,
case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end as refnumber,
fv.notes
from fieldvalue fv
inner join deffield df on fv.fieldname = df.fieldname and df.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''trans'') and df.visible = 1
inner join groups fg on df.fieldtype = fg.id
inner join trans t on fv.ref_id = t.id
inner join groups tg on t.transtype = tg.id
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''transtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join groups dg on t.direction = dg.id
  left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'')
left join customer rf_customer on fv.value = cast(rf_customer.id as text)
left join tool rf_tool on fv.value = cast(rf_tool.id as text)
left join trans rf_trans on fv.value = cast(rf_trans.id as text)
left join product rf_product on fv.value = cast(rf_product.id as text)
left join project rf_project on fv.value = cast(rf_project.id as text)
left join employee rf_employee on fv.value = cast(rf_employee.id as text)
left join place rf_place on fv.value = cast(rf_place.id as text)
where fv.deleted = 0 and (t.deleted=0 or (tg.groupvalue=''cash''))  
  and fv.ref_id in (select trans_id from payment) @where_str'
WHERE viewname='PaymentFieldsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentFieldsView', 'transtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentFieldsView', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'case when tg.groupvalue=''bank'' then '''' else case when msd.msg is null then dg.groupvalue else msd.msg end end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentFieldsView', 'transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 't.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentFieldsView', 'fielddef', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'df.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentFieldsView', 'text_value', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentFieldsView', 'number_value', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL)', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentFieldsView', 'date_value', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentFieldsView', 'bool_value', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentFieldsView', 'refnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentFieldsView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'fv.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
  
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('PaymentInvoiceView', '', 'and t.id = -1', 'payment', 'browser_payment_edit', 'PaymentView', 2);
UPDATE ui_applview SET sqlstr='select t.id||''_''||tg.groupvalue||''_''||dg.groupvalue as id, 
  case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when tg.groupvalue=''bank'' then '''' else case when msd.msg is null then dg.groupvalue else msd.msg end end as direction, 
  p.paiddate, pa.description as place,
  t.transnumber as paidnumber, pa.curr as pcurr, cast(af.value as real) as paidamount, cast(rf.value as real) as prate,
  inv.transnumber as invnumber, inv.curr as icurr, irow.amount as invamount, p.notes as pnotes
from link ln 
inner join payment p on ln.ref_id_1 = p.id and p.deleted=0
inner join trans t on p.trans_id = t.id 
inner join groups tg on t.transtype = tg.id
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''transtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join groups dg on t.direction = dg.id
  left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join place pa on t.place_id = pa.id
inner join trans inv on ln.ref_id_2 = inv.id
inner join (select trans_id, sum(amount) as amount from item where deleted=0 group by trans_id) irow on inv.id = irow.trans_id
inner join fieldvalue af on ln.id = af.ref_id and af.fieldname=''link_qty''
inner join fieldvalue rf on ln.id = rf.ref_id and rf.fieldname=''link_rate''
where ln.deleted=0 and ln.nervatype_1 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''payment'') 
and ln.nervatype_2 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''trans'') @where_str '
WHERE viewname='PaymentInvoiceView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentInvoiceView', 'transtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentInvoiceView', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'case when tg.groupvalue=''bank'' then '''' else case when msd.msg is null then dg.groupvalue else msd.msg end end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentInvoiceView', 'paiddate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'p.paiddate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentInvoiceView', 'place', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'pa.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));  
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentInvoiceView', 'paidnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'tp.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentInvoiceView', 'pcurr', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'pa.curr ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentInvoiceView', 'paidamount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'cast(af.value as real) ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentInvoiceView', 'prate', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'cast(rf.value as real) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentInvoiceView', 'invnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'inv.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentInvoiceView', 'icurr', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'inv.curr ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentInvoiceView', 'invamount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'irow.amount ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentInvoiceView', 'pnotes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 11, 'p.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
  
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('PaymentGroupsView', '', 'and t.id = -1', 'payment', 'browser_payment_edit', 'PaymentView', 3);
UPDATE ui_applview SET sqlstr='select t.id||''_''||tg.groupvalue||''_''||dg.groupvalue as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when tg.groupvalue=''bank'' then '''' else case when msd.msg is null then dg.groupvalue else msd.msg end end as direction, 
  t.transnumber, g.groupvalue, g.description
from trans t
inner join groups tg on t.transtype = tg.id
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''transtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join groups dg on t.direction = dg.id
  left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join link l on t.id = l.ref_id_1 and l.nervatype_1 = (select id from groups where groupname=''nervatype'' and groupvalue=''trans'')
inner join groups g on l.ref_id_2 = g.id and l.nervatype_2 = (select id from groups where groupname=''nervatype'' and groupvalue=''groups'')
where (t.deleted=0 or (tg.groupvalue=''cash''))and g.deleted = 0 and l.deleted=0
  and t.id in (select trans_id from payment) @where_str'
WHERE viewname='PaymentGroupsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentGroupsView', 'transtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentGroupsView', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'case when tg.groupvalue=''bank'' then '''' else case when msd.msg is null then dg.groupvalue else msd.msg end end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentGroupsView', 'transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 't.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentGroupsView', 'groupvalue', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'g.groupvalue', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('PaymentGroupsView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'g.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

--Inventory;
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('InventoryView', '', 'and mv.id = -1', '', null, 'InventoryView', 0);
UPDATE ui_applview SET sqlstr='select pl.description as warehouse, p.partnumber, p.description, p.unit, mv.notes as pgroup, sum(mv.qty) as sqty, substr(max(mv.shippingdate),1,10) as posdate
from movement mv inner join groups g on mv.movetype = g.id and g.groupvalue = ''inventory''
inner join place pl on mv.place_id = pl.id inner join product p on mv.product_id = p.id
inner join trans t on mv.trans_id = t.id and t.deleted=0 inner join groups tg on t.transtype = tg.id inner join groups dg on t.direction = dg.id
where mv.deleted=0 and t.deleted=0 @where_str group by pl.description, p.partnumber, p.description, p.unit, mv.notes
having sum(mv.qty)<>0 @having_str '
WHERE viewname='InventoryView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('InventoryView', 'cb_delivery', (select id from groups where groupname='fieldtype' and groupvalue='checkbox'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'and (tg.groupvalue=''delivery'' and dg.groupvalue<>''transfer'') ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('InventoryView', 'cb_transfer', (select id from groups where groupname='fieldtype' and groupvalue='checkbox'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'and (tg.groupvalue=''delivery'' and dg.groupvalue=''transfer'') ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('InventoryView', 'cb_inventory', (select id from groups where groupname='fieldtype' and groupvalue='checkbox'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'and (tg.groupvalue=''inventory'') ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('InventoryView', 'fl_employee', (select id from groups where groupname='fieldtype' and groupvalue='filter'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, ' t.cruser_id=@employee_id ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('InventoryView', 'fl_usergroup', (select id from groups where groupname='fieldtype' and groupvalue='filter'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 't.cruser_id in (select id from employee where usergroup = @usergroup_id) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
    
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('InventoryView', 'warehouse', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'pl.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('InventoryView', 'partnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.partnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('InventoryView', 'unit', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'p.unit ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('InventoryView', 'sqty', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='having'), 3, 'sum(mv.qty) ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('InventoryView', 'posdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='having'), 4, 'max(mv.shippingdate) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('InventoryView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('MovementView', '', 'and mt.id = -1', 'movement', 'browser_movement_edit', 'InventoryView', 1);
UPDATE ui_applview SET sqlstr='select tg.groupvalue||''_''||dg.groupvalue||''_''||(case when it.id is null then cast(t.id as text) else cast(it.id as text) end) as id, 
  case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when msd.msg is null then dg.groupvalue else msd.msg end as direction,
  t.transnumber, substr(mt.shippingdate,1,10) as shippingdate, pt.description as warehouse, 
  p.partnumber, p.description, p.unit, mt.notes as pgroup, mt.qty, 
  case when it.transnumber is null then  case when vt1.transnumber is null then case when vt2.transnumber is null then tl.transnumber end
    else vt1.transnumber end else it.transnumber end as refnumber, 
    case when c1.custname is null then c2.custname else c1.custname end as refcustomer
  from movement mt
  inner join trans t on mt.trans_id = t.id
  inner join groups gm on mt.movetype = gm.id and gm.groupvalue=''inventory''
  inner join groups tg on t.transtype = tg.id
    left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''transtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
  inner join groups dg on t.direction = dg.id
    left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'')
  inner join product p on mt.product_id = p.id
  inner join place pt on mt.place_id = pt.id
  left join link iln on iln.nervatype_1 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''movement'')
    and iln.ref_id_1 = mt.id and iln.nervatype_2 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''item'')
    left join item i on iln.ref_id_2 = i.id left join trans it on i.trans_id = it.id left join customer c1 on it.customer_id = c1.id
  left join link tln on tln.nervatype_1 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''trans'')
    and tln.ref_id_1 = mt.trans_id and tln.nervatype_2 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''trans'') and tln.deleted=0
    left join trans tl on tln.ref_id_2 = tl.id left join customer c2 on tl.customer_id = c2.id
  left join link pln1 on pln1.nervatype_1 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''movement'')
    and pln1.ref_id_1 = mt.id and pln1.nervatype_2 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''movement'')
    left join movement mv1 on pln1.ref_id_2 = mv1.id left join trans vt1 on mv1.trans_id = vt1.id
  left join link pln2 on pln2.nervatype_1 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''movement'')
    and pln2.ref_id_2 = mt.id and pln2.nervatype_2 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''movement'')
    left join movement mv2 on pln2.ref_id_1 = mv2.id left join trans vt2 on mv2.trans_id = vt2.id
  where mt.deleted = 0 and t.deleted=0 @where_str '
WHERE viewname='MovementView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementView', 'transtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementView', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'case when msd.msg is null then dg.groupvalue else msd.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementView', 'transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 't.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementView', 'shippingdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'mt.shippingdate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementView', 'warehouse', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'pt.description  ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementView', 'partnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'p.partnumber  ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));  
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'p.description  ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementView', 'unit', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'p.unit  ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementView', 'pgroup', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'mt.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementView', 'qty', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'mt.qty ', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementView', 'refnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'case when it.transnumber is null then  case when vt1.transnumber is null then case when vt2.transnumber is null then tl.transnumber end
    else vt1.transnumber end else it.transnumber end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementView', 'refcustomer', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 11, 'case when c1.custname is null then c2.custname else c1.custname end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ToolMovement', '', 'and t.id = -1', 'waybill', 'browser_waybill_edit', 'InventoryView', 2);
UPDATE ui_applview SET sqlstr='select t.id||''_''||tg.groupvalue||''_''||dg.groupvalue as id, t.transnumber, t.crdate, case when msd.msg is null then dg.groupvalue else msd.msg end as direction
  , lt.transnumber as refnumber, e.empnumber, c.custname
  , cast(mv.shippingdate as date) as shippingdate, tl.serial, tl.description, mv.notes as mvnotes
  , case when mss.msg is null then sg.groupvalue else mss.msg end as transtate
  , t.closed, t.notes, t.intnotes, t.fnote
from trans t
inner join movement mv on t.id = mv.trans_id
inner join tool tl on mv.tool_id = tl.id
inner join groups tg on t.transtype = tg.id and tg.groupvalue = ''waybill''
inner join groups dg on t.direction = dg.id
  left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' 
    and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join groups sg on t.transtate = sg.id
  left join ui_message mss on mss.fieldname = sg.groupvalue and  mss.secname = ''transtate'' and mss.lang = (select value from fieldvalue where fieldname = ''default_lang'')
left join link lnk on t.id = lnk.ref_id_1 and lnk.deleted=0 and lnk.nervatype_1 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''trans'') 
     and lnk.nervatype_2 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''trans'')
     left join trans lt on lnk.ref_id_2 = lt.id
left join employee e on t.employee_id = e.id
left join customer c on t.customer_id = c.id
where t.deleted = 0 and mv.deleted=0 @where_str'
WHERE viewname='ToolMovement';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 't.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'crdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 't.crdate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'case when msd.msg is null then dg.groupvalue else msd.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'refnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'lt.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'empnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'e.empnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'custname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'c.custname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'shippingdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'mv.shippingdate::date ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'serial', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'tl.serial ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'tl.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'mvnotes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'mv.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'closed', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 't.closed ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'transtate', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 11, 'case when mss.msg is null then sg.groupvalue else mss.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 12, 't.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'intnotes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 13, 't.intnotes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolMovement', 'fnote', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 14, 't.fnote ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
  
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('MovementFieldsView', '', 'and t.id = -1', 'movement', 'browser_movement_edit', 'InventoryView', 3);
UPDATE ui_applview SET sqlstr='select tg.groupvalue||''_''||dg.groupvalue||''_''||(case when delt.ref_id is null then cast(t.id as text) else cast(delt.ref_id as text) end) as id, 
  case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when msd.msg is null then dg.groupvalue else msd.msg end as direction, t.transnumber, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL) as number_value,
case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end as date_value,
case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end as bool_value,
case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end as refnumber,
fv.notes
from fieldvalue fv
inner join deffield df on fv.fieldname = df.fieldname and df.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''trans'') and df.visible = 1
inner join groups fg on df.fieldtype = fg.id
inner join trans t on fv.ref_id = t.id
inner join groups tg on t.transtype = tg.id
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''transtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join groups dg on t.direction = dg.id
  left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'')
left join customer rf_customer on fv.value = cast(rf_customer.id as text)
left join tool rf_tool on fv.value = cast(rf_tool.id as text)
left join trans rf_trans on fv.value = cast(rf_trans.id as text)
left join product rf_product on fv.value = cast(rf_product.id as text)
left join project rf_project on fv.value = cast(rf_project.id as text)
left join employee rf_employee on fv.value = cast(rf_employee.id as text)
left join place rf_place on fv.value = cast(rf_place.id as text)
left join (select mt.trans_id, min(it.id) as ref_id from movement mt
  inner join link iln on iln.nervatype_1 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''movement'')
    and iln.ref_id_1 = mt.id and iln.nervatype_2 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''item'')
    inner join item i on iln.ref_id_2 = i.id left join trans it on i.trans_id = it.id group by mt.trans_id) delt on fv.ref_id = delt.trans_id
where fv.deleted = 0 and t.deleted=0  
  and t.transtype in (select id from groups where groupname = ''transtype'' and groupvalue in(''delivery'',''inventory'',''waybill'',''production'')) @where_str'
WHERE viewname='MovementFieldsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementFieldsView', 'transtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementFieldsView', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'case when msd.msg is null then dg.groupvalue else msd.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementFieldsView', 'transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 't.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementFieldsView', 'fielddef', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'df.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementFieldsView', 'text_value', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementFieldsView', 'number_value', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL)', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementFieldsView', 'date_value', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementFieldsView', 'bool_value', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementFieldsView', 'refnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementFieldsView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'fv.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('MovementGroupsView', '', 'and t.id = -1', 'movement', 'browser_movement_edit', 'InventoryView', 4);
UPDATE ui_applview SET sqlstr='select tg.groupvalue||''_''||dg.groupvalue||''_''||(case when delt.ref_id is null then cast(t.id as text) else cast(delt.ref_id as text) end) as id, 
  case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when msd.msg is null then dg.groupvalue else msd.msg end as direction, t.transnumber, g.groupvalue, g.description
from trans t
inner join groups tg on t.transtype = tg.id
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''transtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join groups dg on t.direction = dg.id
  left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'')
inner join link l on t.id = l.ref_id_1 and l.nervatype_1 = (select id from groups where groupname=''nervatype'' and groupvalue=''trans'')
inner join groups g on l.ref_id_2 = g.id and l.nervatype_2 = (select id from groups where groupname=''nervatype'' and groupvalue=''groups'')
left join (select mt.trans_id, min(it.id) as ref_id from movement mt
  inner join link iln on iln.nervatype_1 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''movement'')
    and iln.ref_id_1 = mt.id and iln.nervatype_2 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''item'')
    inner join item i on iln.ref_id_2 = i.id left join trans it on i.trans_id = it.id group by mt.trans_id) delt on t.id = delt.trans_id
where t.deleted=0 and g.deleted = 0 and l.deleted=0
  and t.transtype in (select id from groups where groupname = ''transtype'' and groupvalue in(''delivery'',''inventory'',''waybill'',''production'')) @where_str'
WHERE viewname='MovementGroupsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementGroupsView', 'transtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementGroupsView', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'case when msd.msg is null then dg.groupvalue else msd.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementGroupsView', 'transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 't.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementGroupsView', 'groupvalue', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'g.groupvalue', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('MovementGroupsView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'g.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

--Employee;
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('EmployeeView', '', 'and e.id = -1', 'employee', 'browser_employee_edit', 'EmployeeView', 0);
UPDATE ui_applview SET sqlstr='select e.id, e.empnumber, c.firstname, c.surname, e.username, e.startdate, e.enddate,
  c.status, c.phone, c.mobil, c.email, a.zipcode, a.city, a.street,
  ug.groupvalue as usergroup, dg.groupvalue as department, c.notes, e.inactive
from employee e
left join contact c on e.id = c.ref_id and c.nervatype = (select id from groups where groupname = ''nervatype'' and groupvalue = ''employee'')
left join address a on e.id = a.ref_id and a.nervatype = (select id from groups where groupname = ''nervatype'' and groupvalue = ''employee'')
inner join groups ug on e.usergroup = ug.id
left join groups dg on e.department = dg.id
where e.deleted=0 @where_str '
WHERE viewname='EmployeeView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'empnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'e.empnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'firstname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'c.firstname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'surname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'c.surname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'username', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'e.username ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'startdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'e.startdate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'enddate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'e.enddate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'status', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'c.status ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'phone', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'c.phone ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'mobil', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'c.mobil ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'email', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'c.email ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'zipcode', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'a.zipcode ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'city', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 11, 'a.city ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));  
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'street', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 12, 'a.street ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));        
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'usergroup', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 13, 'ug.groupvalue ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'department', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 14, 'dg.groupvalue ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));  
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'inactive', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 15, 'e.inactive ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 16, 'c.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>')); 

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('EmployeeFieldsView', '', 'and e.id = -1', 'employee', 'browser_employee_edit', 'EmployeeView', 1);
UPDATE ui_applview SET sqlstr='select e.id, e.empnumber, c.firstname, c.surname, e.username, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL) as number_value,
case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end as date_value,
case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end as bool_value,
case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end as refnumber,
fv.notes
from fieldvalue fv
inner join deffield df on fv.fieldname = df.fieldname and df.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''employee'') and df.visible = 1
inner join groups fg on df.fieldtype = fg.id
inner join employee e on fv.ref_id = e.id
left join contact c on e.id = c.ref_id and c.nervatype = (select id from groups where groupname = ''nervatype'' and groupvalue = ''employee'')
left join customer rf_customer on fv.value = cast(rf_customer.id as text)
left join tool rf_tool on fv.value = cast(rf_tool.id as text)
left join trans rf_trans on fv.value = cast(rf_trans.id as text)
left join product rf_product on fv.value = cast(rf_product.id as text)
left join project rf_project on fv.value = cast(rf_project.id as text)
left join employee rf_employee on fv.value = cast(rf_employee.id as text)
left join place rf_place on fv.value = cast(rf_place.id as text)
where fv.deleted = 0 and e.deleted=0 @where_str'
WHERE viewname='EmployeeFieldsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeFieldsView', 'empnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'e.empnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeFieldsView', 'firstname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'c.firstname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeFieldsView', 'surname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'c.surname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeFieldsView', 'username', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'e.username ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeFieldsView', 'fielddef', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'df.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeFieldsView', 'text_value', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeFieldsView', 'number_value', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL)', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeFieldsView', 'date_value', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeFieldsView', 'bool_value', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeFieldsView', 'refnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeFieldsView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'fv.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
  
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('EmployeeEvents', '', 'and e.id = -1', 'event', 'browser_event_edit', 'EmployeeView', 2);
UPDATE ui_applview SET sqlstr='select e.id, em.empnumber, c.firstname, c.surname, em.username, e.calnumber, eg.groupvalue as eventgroup, 
  cast(e.fromdate as date) as fromdate, substr(cast(cast(e.fromdate as time) as text), 0, 6) as fromtime, 
  cast(e.todate as date) as todate, substr(cast(cast(e.todate as time) as text), 0, 6) as totime,
  e.subject, e.place, e.description
from event e
inner join employee em on e.ref_id = em.id
left join contact c on em.id = c.ref_id and c.nervatype = (select id from groups where groupname = ''nervatype'' and groupvalue = ''employee'')
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and em.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''employee'') @where_str'
WHERE viewname='EmployeeEvents';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'empnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'e.empnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'firstname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'c.firstname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'surname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'c.surname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'username', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'e.username ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'calnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'e.calnumber', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'eventgroup', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'eg.groupvalue', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'fromdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'cast(e.fromdate as date)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'fromtime', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'substr(cast(cast(e.fromdate as time) as text), 0, 6)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'todate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'cast(e.todate as date)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'totime', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'substr(cast(cast(e.todate as time) as text), 0, 6)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'subject', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'e.subject', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'place', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 11, 'e.place', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('EmployeeEvents', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 12, 'e.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

--Project;
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProjectView', '', 'and p.id = -1', 'project', 'browser_project_edit', 'ProjectView', 0);
UPDATE ui_applview SET sqlstr='select p.id, p.pronumber, p.description, c.custname as customer, cast(p.startdate as date) as startdate, 
  cast(p.enddate as date) as enddate, p.inactive, p.notes
from project p
left join customer c on p.customer_id = c.id
where p.deleted=0 @where_str '
WHERE viewname='ProjectView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectView', 'pronumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.pronumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectView', 'customer', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'c.custname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectView', 'startdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'cast(p.startdate as date) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectView', 'enddate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'cast(p.enddate as date) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectView', 'inactive', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'p.inactive', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'p.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProjectFieldsView', '', 'and p.id = -1', 'project', 'browser_project_edit', 'ProjectView', 1);
UPDATE ui_applview SET sqlstr='select p.id, p.pronumber, p.description, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL) as number_value,
case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end as date_value,
case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end as bool_value,
case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end as refnumber,
fv.notes
from fieldvalue fv
inner join deffield df on fv.fieldname = df.fieldname and df.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''project'') and df.visible = 1
inner join groups fg on df.fieldtype = fg.id
inner join project p on fv.ref_id = p.id
left join customer rf_customer on fv.value = cast(rf_customer.id as text)
left join tool rf_tool on fv.value = cast(rf_tool.id as text)
left join trans rf_trans on fv.value = cast(rf_trans.id as text)
left join product rf_product on fv.value = cast(rf_product.id as text)
left join project rf_project on fv.value = cast(rf_project.id as text)
left join employee rf_employee on fv.value = cast(rf_employee.id as text)
left join place rf_place on fv.value = cast(rf_place.id as text)
where fv.deleted = 0 and p.deleted=0 @where_str'
WHERE viewname='ProjectFieldsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectFieldsView', 'pronumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.pronumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectFieldsView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectFieldsView', 'fielddef', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'df.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectFieldsView', 'text_value', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectFieldsView', 'number_value', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL)', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectFieldsView', 'date_value', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectFieldsView', 'bool_value', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectFieldsView', 'refnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectFieldsView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'fv.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProjectContactView', '', 'and p.id = -1', 'project', 'browser_project_edit', 'ProjectView', 2);
UPDATE ui_applview SET sqlstr='select p.id, p.pronumber, p.description, co.firstname, co.surname, co.status, co.phone, co.fax, co.mobil, co.email, co.notes
from contact co
inner join project p on co.ref_id = p.id
where co.deleted=0 and p.deleted=0 and co.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''project'') @where_str'
WHERE viewname='ProjectContactView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectContactView', 'pronumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.pronumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectContactView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectContactView', 'firstname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'co.firstname', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectContactView', 'surname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, ' co.surname', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectContactView', 'status', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, ' co.status', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectContactView', 'phone', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, ' co.phone', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectContactView', 'fax', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, ' co.fax', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectContactView', 'mobil', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, ' co.mobil', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectContactView', 'email', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, ' co.email', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectContactView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, ' co.notes', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProjectAddressView', '', 'and p.id = -1', 'project', 'browser_project_edit', 'ProjectView', 3);
UPDATE ui_applview SET sqlstr='select p.id, p.pronumber, p.description, a.country, a.state, a.zipcode, a.city, a.street, a.notes 
from address a
inner join project p on a.ref_id = p.id
where a.deleted=0 and p.deleted=0 and a.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''project'') @where_str'
WHERE viewname='ProjectAddressView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectAddressView', 'pronumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.pronumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectAddressView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectAddressView', 'country', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'a.country', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectAddressView', 'state', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'a.state', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectAddressView', 'zipcode', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'a.zipcode ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectAddressView', 'city', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'a.city', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectAddressView', 'street', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'a.street', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectAddressView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'a.notes', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProjectEvents', '', 'and e.id = -1', 'event', 'browser_event_edit', 'ProjectView', 4);
UPDATE ui_applview SET sqlstr='select e.id, p.pronumber, p.description as pdescription, e.calnumber, eg.groupvalue as eventgroup, 
  cast(e.fromdate as date) as fromdate, substr(cast(cast(e.fromdate as time) as text), 0, 6) as fromtime, 
  cast(e.todate as date) as todate, substr(cast(cast(e.todate as time) as text), 0, 6) as totime,
  e.subject, e.place, e.description
from event e
inner join project p on e.ref_id = p.id
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and p.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''project'') @where_str'
WHERE viewname='ProjectEvents';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectEvents', 'pronumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.pronumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectEvents', 'pdescription', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectEvents', 'calnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'e.calnumber', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectEvents', 'eventgroup', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'eg.groupvalue', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectEvents', 'fromdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'cast(e.fromdate as date)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectEvents', 'fromtime', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'substr(cast(cast(e.fromdate as time) as text), 0, 6)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectEvents', 'todate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'cast(e.todate as date)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectEvents', 'totime', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'substr(cast(cast(e.todate as time) as text), 0, 6)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectEvents', 'subject', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'e.subject', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectEvents', 'place', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'e.place', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectEvents', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'e.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ProjectTrans', '', 'and p.id = -1', 'project', 'browser_project_edit', 'ProjectView', 5);
UPDATE ui_applview SET sqlstr='select p.id, p.pronumber, p.description, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype,
  case when msd.msg is null then dg.groupvalue else msd.msg end as direction, 
  t.transnumber, t.transdate,  t.curr, sum(i.amount) as amount, c.custname
from project p inner join trans t on p.id = t.project_id
inner join groups tg on t.transtype = tg.id 
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''transtype'' 
    and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'') 
inner join groups dg on t.direction = dg.id
  left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = ''direction'' 
    and msd.lang = (select value from fieldvalue where fieldname = ''default_lang'') 
left join customer c on t.customer_id = c.id 
inner join item i on t.id = i.trans_id and i.deleted=0
where p.deleted=0 and (t.deleted=0 or (tg.groupvalue=''invoice'' and dg.groupvalue=''out'') or (tg.groupvalue=''receipt'' and dg.groupvalue=''out''))
group by p.id, p.pronumber, p.description, tg.groupvalue, dg.groupvalue, mst.msg, msd.msg, t.transnumber, t.transdate, c.custname, t.curr @where_str '
WHERE viewname='ProjectTrans';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectTrans', 'pronumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 'p.pronumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectTrans', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectTrans', 'transtype', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'case when mst.msg is null then tg.groupvalue else mst.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));  
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectTrans', 'direction', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'case when msd.msg is null then dg.groupvalue else msd.msg end ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectTrans', 'transnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 't.transnumber ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectTrans', 'transdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 't.transdate ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectTrans', 'curr', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 't.curr ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectTrans', 'amount', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'sum(i.amount) ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ProjectTrans', 'custname', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'c.custname ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

--Tools;
INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ToolView', '', 'and t.id = -1', 'tool', 'browser_tool_edit', 'ToolView', 0);
UPDATE ui_applview SET sqlstr='select t.id, t.serial, t.description, p.description as product, case when ssel.state is null then ''***************'' else ssel.state end  as state
, tg.groupvalue as toolgroup, p.inactive, t.notes
from tool t
inner join product p on t.product_id = p.id
left join groups tg on t.toolgroup = tg.id
left join (select mv.tool_id,  case when t.direction = (select id from groups where groupname = ''direction'' and groupvalue = ''in'') then 
  (select custname from customer where id in(select min(customer.id) from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own''))
  when c.custname is not null then c.custname 
  when e.empnumber is not null then e.empnumber 
  else ltc.custname end as state
from movement mv
inner join trans t on mv.trans_id=t.id
left join customer c on t.customer_id=c.id
left join employee e on t.employee_id=e.id
left join link lnk on t.id = lnk.ref_id_1 and lnk.deleted=0 and lnk.nervatype_1 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''trans'') 
     and lnk.nervatype_2 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''trans'')
     left join trans lt on lnk.ref_id_2 = lt.id left join customer ltc on lt.customer_id=ltc.id
where mv.id in(select max(id) from movement mv
  inner join (select tool_id, max(shippingdate) as ldate from movement mv
    inner join trans t on mv.trans_id=t.id
    where mv.deleted=0 and tool_id is not null and t.deleted=0 and cast(shippingdate as date) <= current_date 
    group by tool_id) lst_date on mv.tool_id=lst_date.tool_id and mv.shippingdate=lst_date.ldate group by mv.tool_id)) ssel on t.id = ssel.tool_id
where t.deleted = 0 and (t.toolgroup not in(select id from groups where groupname=''toolgroup'' and groupvalue=''printer'') or t.toolgroup is null) @where_str '
WHERE viewname='ToolView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolView', 'serial', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 't.serial ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 't.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolView', 'product', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'p.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolView', 'toolgroup', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'tg.groupvalue ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolView', 'state', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'ssel.state ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolView', 'inactive', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 't.inactive', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 't.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ToolFieldsView', '', 'and p.id = -1', 'tool', 'browser_tool_edit', 'ToolView', 1);
UPDATE ui_applview SET sqlstr='select t.id, t.serial, t.description, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL) as number_value,
case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end as date_value,
case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end as bool_value,
case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end as refnumber,
fv.notes
from fieldvalue fv
inner join deffield df on fv.fieldname = df.fieldname and df.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''tool'') and df.visible = 1
inner join groups fg on df.fieldtype = fg.id
inner join tool t on fv.ref_id = t.id
left join customer rf_customer on fv.value = cast(rf_customer.id as text)
left join tool rf_tool on fv.value = cast(rf_tool.id as text)
left join trans rf_trans on fv.value = cast(rf_trans.id as text)
left join product rf_product on fv.value = cast(rf_product.id as text)
left join project rf_project on fv.value = cast(rf_project.id as text)
left join employee rf_employee on fv.value = cast(rf_employee.id as text)
left join place rf_place on fv.value = cast(rf_place.id as text)
where fv.deleted = 0 and t.deleted=0 and (t.toolgroup not in(select id from groups where groupname=''toolgroup'' and groupvalue=''printer'') or t.toolgroup is null) @where_str'
WHERE viewname='ToolFieldsView';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolFieldsView', 'serial', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 't.serial ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolFieldsView', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 't.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolFieldsView', 'fielddef', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'df.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolFieldsView', 'text_value', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolFieldsView', 'number_value', (select id from groups where groupname='fieldtype' and groupvalue='float'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS REAL)', 
  (select id from groups where groupname='aggretype' and groupvalue='sum'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolFieldsView', 'date_value', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'case when fg.groupvalue in (''date'') and fv.value not in('''') then cast(fv.value as date) else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolFieldsView', 'bool_value', (select id from groups where groupname='fieldtype' and groupvalue='bool'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'case when fg.groupvalue in (''bool'') then case when fv.value = ''true'' then 1 else 0 end else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolFieldsView', 'refnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'case when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'', ''transitem'', ''transmovement'', ''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else null end', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolFieldsView', 'notes', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'fv.notes ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));

INSERT INTO ui_applview (viewname, sqlstr, inistr, menu, menuitem, parentview, orderby) 
  VALUES ('ToolEvents', '', 'and e.id = -1', 'event', 'browser_event_edit', 'ToolView', 2);
UPDATE ui_applview SET sqlstr='select e.id, t.serial, t.description as pdescription, e.calnumber, eg.groupvalue as eventgroup, 
  cast(e.fromdate as date) as fromdate, substr(cast(cast(e.fromdate as time) as text), 0, 6) as fromtime, 
  cast(e.todate as date) as todate, substr(cast(cast(e.todate as time) as text), 0, 6) as totime,
  e.subject, e.place, e.description
from event e
inner join tool t on e.ref_id = t.id
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and t.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''tool'') 
  and (t.toolgroup not in(select id from groups where groupname=''toolgroup'' and groupvalue=''printer'') or t.toolgroup is null) @where_str'
WHERE viewname='ToolEvents';
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolEvents', 'serial', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 0, 't.serial ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolEvents', 'pdescription', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 1, 't.description ', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolEvents', 'calnumber', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 2, 'e.calnumber', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolEvents', 'eventgroup', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 3, 'eg.groupvalue', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolEvents', 'fromdate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 4, 'cast(e.fromdate as date)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolEvents', 'fromtime', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 5, 'substr(cast(cast(e.fromdate as time) as text), 0, 6)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolEvents', 'todate', (select id from groups where groupname='fieldtype' and groupvalue='date'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 6, 'cast(e.todate as date)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolEvents', 'totime', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 7, 'substr(cast(cast(e.todate as time) as text), 0, 6)', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolEvents', 'subject', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 8, 'e.subject', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolEvents', 'place', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 9, 'e.place', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));
INSERT INTO ui_viewfields (viewname, fieldname, fieldtype, wheretype, orderby, sqlstr, aggretype) 
  VALUES ('ToolEvents', 'description', (select id from groups where groupname='fieldtype' and groupvalue='string'), 
  (select id from groups where groupname='wheretype' and groupvalue='where'), 10, 'e.description', 
  (select id from groups where groupname='aggretype' and groupvalue='<>'));


