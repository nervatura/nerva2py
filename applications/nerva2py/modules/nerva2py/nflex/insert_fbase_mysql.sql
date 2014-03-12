UPDATE ui_applview SET sqlstr='select c.id,
  c.custnumber, c.custname, case when mst.msg is null then tg.groupvalue else mst.msg end as custtype,
  c.taxnumber, c.account, c.notax, c.terms, c.creditlimit,
  c.discount, c.notes, c.inactive, 
  CONCAT(case when addr.city is null then '''' else addr.city end, '' '', case when addr.street is null then '''' else addr.street end) as address
from customer c
inner join groups tg on c.custtype = tg.id
  left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = ''custtype'' and mst.lang = (select value from fieldvalue where fieldname = ''default_lang'')
left join (select * from address
  where id in(select min(id) fid from address a
    where a.deleted=0 and a.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'')
    group by a.ref_id)) addr on c.id = addr.ref_id
where c.deleted=0 and c.id not in(select customer.id from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') @where_str '
WHERE viewname='CustomerView';

update ui_viewfields set 
sqlstr=' CONCAT(case when addr.city is null then '''' else addr.city end, '' '', case when addr.street is null then '''' else addr.street end)' 
where viewname='CustomerView' and fieldname='address';

UPDATE ui_applview SET sqlstr='select c.id, c.custnumber, c.custname, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end as number_value,
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
left join customer rf_customer on fv.value = cast(rf_customer.id as char)
left join tool rf_tool on fv.value = cast(rf_tool.id as char)
left join trans rf_trans on fv.value = cast(rf_trans.id as char)
left join product rf_product on fv.value = cast(rf_product.id as char)
left join project rf_project on fv.value = cast(rf_project.id as char)
left join employee rf_employee on fv.value = cast(rf_employee.id as char)
left join place rf_place on fv.value = cast(rf_place.id as char)
where fv.deleted = 0 and c.deleted=0 and c.id not in(select customer.id from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') @where_str'
WHERE viewname='CustomerFieldsView';

update ui_viewfields set 
sqlstr=' cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS decimal)' 
where viewname='CustomerFieldsView' and fieldname='number_value';

UPDATE ui_applview SET sqlstr='select e.id, c.custnumber, c.custname, e.calnumber, eg.groupvalue as eventgroup, 
  cast(e.fromdate as date) as fromdate, cast(cast(e.fromdate as time) as char) as fromtime, 
  cast(e.todate as date) as todate, cast(cast(e.todate as time) as char) as totime,
  e.subject, e.place, e.description
from event e
inner join customer c on e.ref_id = c.id
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and c.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') 
  and c.id not in(select customer.id from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') @where_str'
WHERE viewname='CustomerEvents';

update ui_viewfields set 
sqlstr=' cast(cast(e.fromdate as time) as char)' 
where viewname='CustomerEvents' and fieldname='fromtime';

update ui_viewfields set 
sqlstr=' cast(cast(e.todate as time) as char)' 
where viewname='CustomerEvents' and fieldname='totime';

UPDATE ui_applview SET sqlstr='select p.id, p.partnumber, p.description, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end as number_value,
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
left join customer rf_customer on fv.value = cast(rf_customer.id as char)
left join tool rf_tool on fv.value = cast(rf_tool.id as char)
left join trans rf_trans on fv.value = cast(rf_trans.id as char)
left join product rf_product on fv.value = cast(rf_product.id as char)
left join project rf_project on fv.value = cast(rf_project.id as char)
left join employee rf_employee on fv.value = cast(rf_employee.id as char)
left join place rf_place on fv.value = cast(rf_place.id as char)
where fv.deleted = 0 and p.deleted=0  @where_str'
WHERE viewname='ProductFieldsView';

update ui_viewfields set 
sqlstr=' cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS decimal)' 
where viewname='ProductFieldsView' and fieldname='number_value';

UPDATE ui_applview SET sqlstr='select e.id, p.partnumber, p.description as partname, e.calnumber, eg.groupvalue as eventgroup, 
  cast(e.fromdate as date) as fromdate, cast(cast(e.fromdate as time) as char) as fromtime, 
  cast(e.todate as date) as todate, cast(cast(e.todate as time) as char) as totime,
  e.subject, e.place, e.description
from event e
inner join product p on e.ref_id = p.id
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and p.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''product'') @where_str'
WHERE viewname='ProductEvents';

update ui_viewfields set 
sqlstr=' cast(cast(e.fromdate as time) as char)' 
where viewname='ProductEvents' and fieldname='fromtime';

update ui_viewfields set 
sqlstr=' cast(cast(e.todate as time) as char)' 
where viewname='ProductEvents' and fieldname='totime';

UPDATE ui_applview SET sqlstr='select e.id, e.empnumber, c.firstname, c.surname, e.username, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end as number_value,
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
left join customer rf_customer on fv.value = cast(rf_customer.id as char)
left join tool rf_tool on fv.value = cast(rf_tool.id as char)
left join trans rf_trans on fv.value = cast(rf_trans.id as char)
left join product rf_product on fv.value = cast(rf_product.id as char)
left join project rf_project on fv.value = cast(rf_project.id as char)
left join employee rf_employee on fv.value = cast(rf_employee.id as char)
left join place rf_place on fv.value = cast(rf_place.id as char)
where fv.deleted = 0 and e.deleted=0 @where_str'
WHERE viewname='EmployeeFieldsView';

update ui_viewfields set 
sqlstr=' cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS decimal)' 
where viewname='EmployeeFieldsView' and fieldname='number_value';

UPDATE ui_applview SET sqlstr='select e.id, em.empnumber, c.firstname, c.surname, em.username, e.calnumber, eg.groupvalue as eventgroup, 
  cast(e.fromdate as date) as fromdate, cast(cast(e.fromdate as time) as char) as fromtime, 
  cast(e.todate as date) as todate, cast(cast(e.todate as time) as char) as totime,
  e.subject, e.place, e.description
from event e
inner join employee em on e.ref_id = em.id
left join contact c on em.id = c.ref_id and c.nervatype = (select id from groups where groupname = ''nervatype'' and groupvalue = ''employee'')
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and em.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''employee'') @where_str'
WHERE viewname='EmployeeEvents';

update ui_viewfields set 
sqlstr=' cast(cast(e.fromdate as time) as char)' 
where viewname='EmployeeEvents' and fieldname='fromtime';

update ui_viewfields set 
sqlstr=' cast(cast(e.todate as time) as char)' 
where viewname='EmployeeEvents' and fieldname='totime';

UPDATE ui_applview SET sqlstr='select t.id, t.serial, t.description, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end as number_value,
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
left join customer rf_customer on fv.value = cast(rf_customer.id as char)
left join tool rf_tool on fv.value = cast(rf_tool.id as char)
left join trans rf_trans on fv.value = cast(rf_trans.id as char)
left join product rf_product on fv.value = cast(rf_product.id as char)
left join project rf_project on fv.value = cast(rf_project.id as char)
left join employee rf_employee on fv.value = cast(rf_employee.id as char)
left join place rf_place on fv.value = cast(rf_place.id as char)
where fv.deleted = 0 and t.deleted=0 and (t.toolgroup not in(select id from groups where groupname=''toolgroup'' and groupvalue=''printer'') or t.toolgroup is null) @where_str'
WHERE viewname='ToolFieldsView';

update ui_viewfields set 
sqlstr=' cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS decimal)' 
where viewname='ToolFieldsView' and fieldname='number_value';

UPDATE ui_applview SET sqlstr='select e.id, t.serial, t.description as pdescription, e.calnumber, eg.groupvalue as eventgroup, 
  cast(e.fromdate as date) as fromdate, cast(cast(e.fromdate as time) as char) as fromtime, 
  cast(e.todate as date) as todate, cast(cast(e.todate as time) as char) as totime,
  e.subject, e.place, e.description
from event e
inner join tool t on e.ref_id = t.id
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and t.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''tool'') 
  and (t.toolgroup not in(select id from groups where groupname=''toolgroup'' and groupvalue=''printer'') or t.toolgroup is null) @where_str'
WHERE viewname='ToolEvents';

update ui_viewfields set 
sqlstr=' cast(cast(e.fromdate as time) as char)' 
where viewname='ToolEvents' and fieldname='fromtime';

update ui_viewfields set 
sqlstr=' cast(cast(e.todate as time) as char)' 
where viewname='ToolEvents' and fieldname='totime';

UPDATE ui_applview SET sqlstr='select CONCAT(t.id, ''_'', tg.groupvalue, ''_'', dg.groupvalue) as id, t.transnumber, t.crdate, case when msd.msg is null then dg.groupvalue else msd.msg end as direction
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

UPDATE ui_applview SET sqlstr='select CONCAT(cast(t.id as char), ''_'', tg.groupvalue, ''_'', dg.groupvalue) as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when msd.msg is null then dg.groupvalue else msd.msg end as direction,
  case when msc.msg is null then fv.value else msc.msg end as transcast, 
  t.transnumber, t.ref_transnumber, t.crdate, t.transdate, t.duedate, c.custname, e.empnumber, deg.groupvalue as department, p.pronumber, 
  case when msp.msg is null then ptg.groupvalue else msp.msg end as paidtype,
  t.curr, irow.netamount, irow.vatamount, irow.amount,
  t.notax, t.paid,t.acrate, t.notes, t.intnotes, t.fnote,  
  case when mss.msg is null then sg.groupvalue else mss.msg end as transtate,
  t.closed, t.deleted,
  reholiday.value as reholiday, rebadtool.value as rebadtool, reother.value as reother, rentnote.value as rentnote,
  wsdistance.value as wsdistance, wsrepair.value as wsrepair, wstotal.value as wstotal, wsnote.value as wsnote
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

update ui_viewfields set 
sqlstr=' cast(reholiday.value as decimal)' 
where viewname='TransItemHeadView' and fieldname='reholiday';

update ui_viewfields set 
sqlstr=' cast(rebadtool.value as decimal)' 
where viewname='TransItemHeadView' and fieldname='rebadtool';

update ui_viewfields set 
sqlstr=' cast(reother.value as decimal)' 
where viewname='TransItemHeadView' and fieldname='reother';

update ui_viewfields set 
sqlstr=' cast(wsdistance.value as decimal)' 
where viewname='TransItemHeadView' and fieldname='wsdistance';

update ui_viewfields set 
sqlstr=' cast(wsrepair.value as decimal)' 
where viewname='TransItemHeadView' and fieldname='wsrepair';

update ui_viewfields set 
sqlstr=' cast(wstotal.value as decimal)' 
where viewname='TransItemHeadView' and fieldname='wstotal';

UPDATE ui_applview SET sqlstr='select CONCAT(cast(t.id as char), ''_'', tg.groupvalue, ''_'', dg.groupvalue) as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when msd.msg is null then dg.groupvalue else msd.msg end as direction, t.transnumber, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end as number_value,
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
left join customer rf_customer on fv.value = cast(rf_customer.id as char)
left join tool rf_tool on fv.value = cast(rf_tool.id as char)
left join trans rf_trans on fv.value = cast(rf_trans.id as char)
left join product rf_product on fv.value = cast(rf_product.id as char)
left join project rf_project on fv.value = cast(rf_project.id as char)
left join employee rf_employee on fv.value = cast(rf_employee.id as char)
left join place rf_place on fv.value = cast(rf_place.id as char)
where fv.deleted = 0 and (t.deleted=0 or (tg.groupvalue=''invoice'' and dg.groupvalue=''out'') or (tg.groupvalue=''receipt'' and dg.groupvalue=''out''))  
  @where_str'
WHERE viewname='TransItemFieldsView';

update ui_viewfields set 
sqlstr=' cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS decimal)' 
where viewname='TransItemFieldsView' and fieldname='number_value';

UPDATE ui_applview SET sqlstr='select CONCAT(cast(t.id as char), ''_'', tg.groupvalue, ''_'', dg.groupvalue) as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
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

UPDATE ui_applview SET sqlstr='select CONCAT(cast(t.id as char), ''_'', tg.groupvalue, ''_'', dg.groupvalue) as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
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

UPDATE ui_applview SET sqlstr='select CONCAT(cast(t.id as char),''_'', tg.groupvalue, ''_'', dg.groupvalue) as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
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

UPDATE ui_applview SET sqlstr='select CONCAT(cast(t.id as char),''_'', tg.groupvalue, ''_'', dg.groupvalue) as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when tg.groupvalue=''bank'' then '''' else case when msd.msg is null then dg.groupvalue else msd.msg end end as direction, 
  t.transnumber, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end as number_value,
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
left join customer rf_customer on fv.value = cast(rf_customer.id as char)
left join tool rf_tool on fv.value = cast(rf_tool.id as char)
left join trans rf_trans on fv.value = cast(rf_trans.id as char)
left join product rf_product on fv.value = cast(rf_product.id as char)
left join project rf_project on fv.value = cast(rf_project.id as char)
left join employee rf_employee on fv.value = cast(rf_employee.id as char)
left join place rf_place on fv.value = cast(rf_place.id as char)
where fv.deleted = 0 and (t.deleted=0 or (tg.groupvalue=''char''))  
  and fv.ref_id in (select trans_id from payment) @where_str'
WHERE viewname='PaymentFieldsView';

update ui_viewfields set 
sqlstr=' cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS decimal)' 
where viewname='PaymentFieldsView' and fieldname='number_value';

UPDATE ui_applview SET sqlstr='select CONCAT(cast(t.id as char),''_'', tg.groupvalue, ''_'', dg.groupvalue) as id, 
  case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when tg.groupvalue=''bank'' then '''' else case when msd.msg is null then dg.groupvalue else msd.msg end end as direction, 
  p.paiddate, pa.description as place,
  t.transnumber as paidnumber, pa.curr as pcurr, af.value as paidamount, rf.value as prate,
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

update ui_viewfields set sqlstr=' cast(af.value as decimal)' 
where viewname='PaymentInvoiceView' and fieldname='paidamount';

update ui_viewfields set sqlstr=' cast(rf.value as decimal)' 
where viewname='PaymentInvoiceView' and fieldname='prate';

UPDATE ui_applview SET sqlstr='select CONCAT(cast(t.id as char),''_'', tg.groupvalue, ''_'', dg.groupvalue) as id, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
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

UPDATE ui_applview SET sqlstr='select CONCAT(tg.groupvalue, ''_'', dg.groupvalue, ''_'', (case when it.id is null then cast(t.id as char) else cast(it.id as char) end)) as id, 
  case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when msd.msg is null then dg.groupvalue else msd.msg end as direction,
  t.transnumber, cast(mt.shippingdate as date) as shippingdate, pt.description as warehouse, 
  p.partnumber, p.description, p.unit, mt.notes as pgroup, mt.qty, 
  case when it.transnumber is null then  case when vt1.transnumber is null then case when vt2.transnumber is null then tl.transnumber end
    else vt1.transnumber end else it.transnumber end as refnumber, 
    case when c1.custname is null then c2.custname else c1.custname end as refcustomer
  from movement mt
  inner join trans t on mt.trans_id = t.id
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

UPDATE ui_applview SET sqlstr='select CONCAT(tg.groupvalue, ''_'', dg.groupvalue, ''_'', (case when delt.ref_id is null then cast(t.id as char) else cast(delt.ref_id as char) end)) as id, 
  case when mst.msg is null then tg.groupvalue else mst.msg end as transtype, 
  case when msd.msg is null then dg.groupvalue else msd.msg end as direction, t.transnumber, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end as number_value,
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
left join customer rf_customer on fv.value = cast(rf_customer.id as char)
left join tool rf_tool on fv.value = cast(rf_tool.id as char)
left join trans rf_trans on fv.value = cast(rf_trans.id as char)
left join product rf_product on fv.value = cast(rf_product.id as char)
left join project rf_project on fv.value = cast(rf_project.id as char)
left join employee rf_employee on fv.value = cast(rf_employee.id as char)
left join place rf_place on fv.value = cast(rf_place.id as char)
left join (select mt.trans_id, min(it.id) as ref_id from movement mt
  inner join link iln on iln.nervatype_1 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''movement'')
    and iln.ref_id_1 = mt.id and iln.nervatype_2 = (select id from groups where groupname = ''nervatype'' and groupvalue = ''item'')
    inner join item i on iln.ref_id_2 = i.id left join trans it on i.trans_id = it.id group by mt.trans_id) delt on fv.ref_id = delt.trans_id
where fv.deleted = 0 and t.deleted=0  
  and t.transtype in (select id from groups where groupname = ''transtype'' and groupvalue in(''delivery'',''inventory'',''waybill'',''production'')) @where_str'
WHERE viewname='MovementFieldsView';

update ui_viewfields set 
sqlstr=' cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS decimal)' 
where viewname='MovementFieldsView' and fieldname='number_value';

UPDATE ui_applview SET sqlstr='select CONCAT(tg.groupvalue, ''_'', dg.groupvalue, ''_'', (case when delt.ref_id is null then cast(t.id as char) else cast(delt.ref_id as char) end)) as id, 
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

UPDATE ui_applview SET sqlstr='select p.id, p.pronumber, p.description, df.description as fielddef,
case when fg.groupvalue in (''notes'', ''string'', ''valuelist'', ''urlink'') then fv.value else null end as text_value,
case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end as number_value,
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
left join customer rf_customer on fv.value = cast(rf_customer.id as char)
left join tool rf_tool on fv.value = cast(rf_tool.id as char)
left join trans rf_trans on fv.value = cast(rf_trans.id as char)
left join product rf_product on fv.value = cast(rf_product.id as char)
left join project rf_project on fv.value = cast(rf_project.id as char)
left join employee rf_employee on fv.value = cast(rf_employee.id as char)
left join place rf_place on fv.value = cast(rf_place.id as char)
where fv.deleted = 0 and p.deleted=0 @where_str'
WHERE viewname='ProjectFieldsView';

update ui_viewfields set 
sqlstr=' cast(case when fg.groupvalue in (''float'', ''integer'') then fv.value else null end AS decimal)' 
where viewname='ProjectFieldsView' and fieldname='number_value';

UPDATE ui_applview SET sqlstr='select e.id, p.pronumber, p.description as pdescription, e.calnumber, eg.groupvalue as eventgroup, 
  cast(e.fromdate as date) as fromdate, cast(cast(e.fromdate as time) as char) as fromtime, 
  cast(e.todate as date) as todate, cast(cast(e.todate as time) as char) as totime,
  e.subject, e.place, e.description
from event e
inner join project p on e.ref_id = p.id
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and p.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''project'') @where_str'
WHERE viewname='ProjectEvents';

update ui_viewfields set 
sqlstr=' cast(cast(e.fromdate as time) as char)' 
where viewname='ProjectEvents' and fieldname='fromtime';

update ui_viewfields set 
sqlstr=' cast(cast(e.todate as time) as char)' 
where viewname='ProjectEvents' and fieldname='totime';
