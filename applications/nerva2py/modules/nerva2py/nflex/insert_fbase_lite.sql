UPDATE ui_applview SET sqlstr='select e.id, c.custnumber, c.custname, e.calnumber, eg.groupvalue as eventgroup, 
  case when e.fromdate is null then null else substr(e.fromdate,1,10) end as fromdate, 
  case when e.fromdate is null then null else substr(e.fromdate,11,6) end as fromtime,
  case when e.todate is null then null else substr(e.todate,1,10) end as todate, 
  case when e.todate is null then null else substr(e.todate,11,6) end as totime,
  e.subject, e.place, e.description
from event e
inner join customer c on e.ref_id = c.id
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and c.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') 
  and c.id not in(select customer.id from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') @where_str'
WHERE viewname='CustomerEvents';

update ui_viewfields set 
sqlstr=' case when e.fromdate is null then null else substr(e.fromdate,1,10) end' 
where viewname='CustomerEvents' and fieldname='fromdate';
update ui_viewfields set 
sqlstr=' case when e.fromdate is null then null else substr(e.fromdate,11,6) end' 
where viewname='CustomerEvents' and fieldname='fromtime';

update ui_viewfields set 
sqlstr=' case when e.todate is null then null else substr(e.todate,1,10) end' 
where viewname='CustomerEvents' and fieldname='todate';
update ui_viewfields set 
sqlstr=' case when e.todate is null then null else substr(e.todate,11,6) end' 
where viewname='CustomerEvents' and fieldname='totime';

UPDATE ui_applview SET sqlstr='select e.id, p.partnumber, p.description as partname, e.calnumber, eg.groupvalue as eventgroup, 
  case when e.fromdate is null then null else substr(e.fromdate,1,10) end as fromdate, 
  case when e.fromdate is null then null else substr(e.fromdate,11,6) end as fromtime,
  case when e.todate is null then null else substr(e.todate,1,10) end as todate, 
  case when e.todate is null then null else substr(e.todate,11,6) end as totime,
  e.subject, e.place, e.description
from event e
inner join product p on e.ref_id = p.id
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and p.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''product'') @where_str'
WHERE viewname='ProductEvents';

update ui_viewfields set 
sqlstr=' case when e.fromdate is null then null else substr(e.fromdate,1,10) end' 
where viewname='ProductEvents' and fieldname='fromdate';
update ui_viewfields set 
sqlstr=' case when e.fromdate is null then null else substr(e.fromdate,11,6) end' 
where viewname='ProductEvents' and fieldname='fromtime';

update ui_viewfields set 
sqlstr=' case when e.todate is null then null else substr(e.todate,1,10) end' 
where viewname='ProductEvents' and fieldname='todate';
update ui_viewfields set 
sqlstr=' case when e.todate is null then null else substr(e.todate,11,6) end' 
where viewname='ProductEvents' and fieldname='totime';

UPDATE ui_applview SET sqlstr='select e.id, em.empnumber, c.firstname, c.surname, em.username, e.calnumber, eg.groupvalue as eventgroup, 
  case when e.fromdate is null then null else substr(e.fromdate,1,10) end as fromdate, 
  case when e.fromdate is null then null else substr(e.fromdate,11,6) end as fromtime,
  case when e.todate is null then null else substr(e.todate,1,10) end as todate, 
  case when e.todate is null then null else substr(e.todate,11,6) end as totime,
  e.subject, e.place, e.description
from event e
inner join employee em on e.ref_id = em.id
left join contact c on em.id = c.ref_id and c.nervatype = (select id from groups where groupname = ''nervatype'' and groupvalue = ''employee'')
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and em.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''employee'') @where_str'
WHERE viewname='EmployeeEvents';

update ui_viewfields set 
sqlstr=' case when e.fromdate is null then null else substr(e.fromdate,1,10) end' 
where viewname='EmployeeEvents' and fieldname='fromdate';
update ui_viewfields set 
sqlstr=' case when e.fromdate is null then null else substr(e.fromdate,11,6) end' 
where viewname='EmployeeEvents' and fieldname='fromtime';

update ui_viewfields set 
sqlstr=' case when e.todate is null then null else substr(e.todate,1,10) end' 
where viewname='EmployeeEvents' and fieldname='todate';
update ui_viewfields set 
sqlstr=' case when e.todate is null then null else substr(e.todate,11,6) end' 
where viewname='EmployeeEvents' and fieldname='totime';

UPDATE ui_applview SET sqlstr='select e.id, t.serial, t.description as pdescription, e.calnumber, eg.groupvalue as eventgroup, 
  case when e.fromdate is null then null else substr(e.fromdate,1,10) end as fromdate, 
  case when e.fromdate is null then null else substr(e.fromdate,11,6) end as fromtime,
  case when e.todate is null then null else substr(e.todate,1,10) end as todate, 
  case when e.todate is null then null else substr(e.todate,11,6) end as totime,
  e.subject, e.place, e.description
from event e
inner join tool t on e.ref_id = t.id
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and t.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''tool'') 
  and (t.toolgroup not in(select id from groups where groupname=''toolgroup'' and groupvalue=''printer'') or t.toolgroup is null) @where_str'
WHERE viewname='ToolEvents';

update ui_viewfields set 
sqlstr=' case when e.fromdate is null then null else substr(e.fromdate,1,10) end' 
where viewname='ToolEvents' and fieldname='fromdate';
update ui_viewfields set 
sqlstr=' case when e.fromdate is null then null else substr(e.fromdate,11,6) end' 
where viewname='ToolEvents' and fieldname='fromtime';

update ui_viewfields set 
sqlstr=' case when e.todate is null then null else substr(e.todate,1,10) end' 
where viewname='ToolEvents' and fieldname='todate';
update ui_viewfields set 
sqlstr=' case when e.todate is null then null else substr(e.todate,11,6) end' 
where viewname='ToolEvents' and fieldname='totime';

UPDATE ui_applview SET sqlstr='select p.id, p.pronumber, p.description, c.custname as customer, 
  case when p.startdate is null then null else substr(p.startdate,1,10) end as startdate, 
  case when p.enddate is null then null else substr(p.enddate,1,10) end as enddate, p.inactive, p.notes
from project p
left join customer c on p.customer_id = c.id
where p.deleted=0 @where_str '
WHERE viewname='ProjectView';

update ui_viewfields set 
sqlstr=' case when p.startdate is null then null else substr(p.startdate,1,10) end' 
where viewname='ProjectView' and fieldname='startdate';
update ui_viewfields set 
sqlstr=' case when p.enddate is null then null else substr(p.enddate,1,10) end' 
where viewname='ProjectView' and fieldname='enddate';

UPDATE ui_applview SET sqlstr='select e.id, p.pronumber, p.description as pdescription, e.calnumber, eg.groupvalue as eventgroup, 
  case when e.fromdate is null then null else substr(e.fromdate,1,10) end as fromdate, 
  case when e.fromdate is null then null else substr(e.fromdate,11,6) end as fromtime,
  case when e.todate is null then null else substr(e.todate,1,10) end as todate, 
  case when e.todate is null then null else substr(e.todate,11,6) end as totime,
  e.subject, e.place, e.description
from event e
inner join project p on e.ref_id = p.id
left join groups eg on e.eventgroup = eg.id
where e.deleted=0 and p.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''project'') @where_str'
WHERE viewname='ProjectEvents';

update ui_viewfields set 
sqlstr=' case when e.fromdate is null then null else substr(e.fromdate,1,10) end' 
where viewname='ProjectEvents' and fieldname='fromdate';
update ui_viewfields set 
sqlstr=' case when e.fromdate is null then null else substr(e.fromdate,11,6) end' 
where viewname='ProjectEvents' and fieldname='fromtime';

update ui_viewfields set 
sqlstr=' case when e.todate is null then null else substr(e.todate,1,10) end' 
where viewname='ProjectEvents' and fieldname='todate';
update ui_viewfields set 
sqlstr=' case when e.todate is null then null else substr(e.todate,11,6) end' 
where viewname='ProjectEvents' and fieldname='totime';
