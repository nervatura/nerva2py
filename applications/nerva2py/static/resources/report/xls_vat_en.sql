INSERT INTO ui_report(reportkey, nervatype, transtype, direction, repname, description, filetype, report, label)
    VALUES ('xls_vat_en', (select id from groups where groupname='nervatype' and groupvalue='report'), 
      null, null, 'VAT Summary - MS Excel', 'Recoverable and payable VAT summary grouped by currency. MS Excel sample.'
      , (select id from groups where groupname='filetype' and groupvalue='xls'), null, 'Example');--

INSERT INTO ui_reportfields(report_id, fieldname, fieldtype, wheretype, description, orderby, sqlstr, parameter, dataset,defvalue)
    VALUES ((select id from ui_report where reportkey='xls_vat_en'), 'date_from', (select id from groups where groupname='fieldtype' and groupvalue='date')
    , (select id from groups where groupname='wheretype' and groupvalue='in'), 'From date', 0, '', 0, null,'-360');--

INSERT INTO ui_reportfields(report_id, fieldname, fieldtype, wheretype, description, orderby, sqlstr, parameter, dataset)
    VALUES ((select id from ui_report where reportkey='xls_vat_en'), 'date_to', (select id from groups where groupname='fieldtype' and groupvalue='date')
    , (select id from groups where groupname='wheretype' and groupvalue='in'), 'To date', 1, '', 0, null);--

INSERT INTO ui_reportfields(report_id, fieldname, fieldtype, wheretype, description, orderby, sqlstr, parameter, dataset)
    VALUES ((select id from ui_report where reportkey='xls_vat_en'), 'curr', (select id from groups where groupname='fieldtype' and groupvalue='string')
    , (select id from groups where groupname='wheretype' and groupvalue='where'), 'Currency', 2, '', 0, null);--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='xls_vat_en'), 'total', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='xls_vat_en'), 'ds', '');--

update ui_reportsources set sqlstr = 'select t.curr as curr, case when t.notax=1 then ''AAM'' else tx.taxcode end as taxcode
, sum(case when dg.groupvalue=''out'' then netamount else 0 end) as netamount_out
, sum(case when dg.groupvalue=''in'' then netamount else 0 end) as netamount_in
, sum(case when dg.groupvalue=''out'' then vatamount else 0 end) as vatamount_out
, sum(case when dg.groupvalue=''in'' then vatamount else 0 end) as vatamount_in
, sum(case when dg.groupvalue=''out'' then amount else 0 end) as amount_out
, sum(case when dg.groupvalue=''in'' then amount else 0 end) as amount_in
,sum(case when dg.groupvalue=''in'' then vatamount else 0 end-case when dg.groupvalue=''out'' then vatamount else 0 end) as vatamount_diff 
from trans t 
inner join groups tg on t.transtype = tg.id and tg.groupvalue=''invoice'' 
inner join groups dg on t.direction = dg.id 
inner join item ti on t.id=ti.trans_id and ti.deleted=0 
inner join tax tx on ti.tax_id=tx.id 
where t.deleted=0 and t.transdate >= @date_from and t.transdate <= @date_to @where_str 
group by t.curr, case when t.notax=1 then ''AAM'' else tx.taxcode end 
order by t.curr DESC, case when t.notax=1 then ''AAM'' else tx.taxcode end DESC'
where report_id = (select id from ui_report where reportkey='xls_vat_en') and dataset='total';--

update ui_reportsources set sqlstr = 'select @date_from as date_from, @date_to as date_to, t.transnumber as transnumber, t.crdate as crdate, t.transdate as transdate, substr(cast(t.duedate as char(10)), 1, 10) as  duedate, c.custname as custname, t.curr as curr, dg.groupvalue as direction
, case when t.notax=1 then ''AAM'' else tx.taxcode end as taxcode
, case when dg.groupvalue=''in'' then 0-sum(netamount) else sum(netamount) end as netamount
, case when dg.groupvalue=''in'' then 0-sum(vatamount) else sum(vatamount) end as vatamount
, case when dg.groupvalue=''in'' then 0-sum(amount) else sum(amount) end as amount 
from trans t 
inner join groups tg on t.transtype = tg.id and tg.groupvalue=''invoice'' 
inner join groups dg on t.direction = dg.id 
inner join item ti on t.id=ti.trans_id and ti.deleted=0 
inner join customer c on t.customer_id = c.id 
inner join tax tx on ti.tax_id=tx.id 
where t.deleted=0 and t.transdate >= @date_from and t.transdate <= @date_to @where_str 
group by t.transnumber, t.crdate, t.transdate, substr(cast(t.duedate as char(10)), 1, 10), c.custname, t.curr, dg.groupvalue, case when t.notax=1 then ''AAM'' else tx.taxcode end 
order by t.curr DESC, dg.groupvalue, t.transdate, case when t.notax=1 then ''AAM'' else tx.taxcode end DESC'
where report_id = (select id from ui_report where reportkey='xls_vat_en') and dataset='ds';--

[engine mssql]update ui_reportsources set sqlstr = 'select @date_from as date_from, @date_to as date_to, t.transnumber as transnumber, t.crdate as crdate, t.transdate as transdate, CONVERT(VARCHAR(10), t.duedate, 120) as duedate, c.custname as custname, t.curr as curr, dg.groupvalue as direction
, case when t.notax=1 then ''AAM'' else tx.taxcode end as taxcode
, case when dg.groupvalue=''in'' then 0-sum(netamount) else sum(netamount) end as netamount
, case when dg.groupvalue=''in'' then 0-sum(vatamount) else sum(vatamount) end as vatamount
, case when dg.groupvalue=''in'' then 0-sum(amount) else sum(amount) end as amount 
from trans t 
inner join groups tg on t.transtype = tg.id and tg.groupvalue=''invoice'' 
inner join groups dg on t.direction = dg.id 
inner join item ti on t.id=ti.trans_id and ti.deleted=0 
inner join customer c on t.customer_id = c.id 
inner join tax tx on ti.tax_id=tx.id 
where t.deleted=0 and t.transdate >= @date_from and t.transdate <= @date_to @where_str 
group by t.transnumber, t.crdate, t.transdate, CONVERT(VARCHAR(10), t.duedate, 120), c.custname, t.curr, dg.groupvalue, case when t.notax=1 then ''AAM'' else tx.taxcode end 
order by t.curr DESC, dg.groupvalue, t.transdate, case when t.notax=1 then ''AAM'' else tx.taxcode end DESC'
where report_id = (select id from ui_report where reportkey='xls_vat_en') and dataset='ds';--

update ui_report set report='{
  "total":{"sheetName":"tax_total",
        "columns":[{"name":"curr","label":"Currency","type":"string"},
                   {"name":"taxcode","label":"VAT%","type":"string"},                   
                   {"name":"netamount_out","label":"Net income","type":"float"},
                   {"name":"vatamount_out","label":"VAT(+)","type":"float"},
                   {"name":"netamount_in","label":"Net payment","type":"float"},
                   {"name":"vatamount_in","label":"VAT(-)","type":"float"},
                   {"name":"vatamount_diff","label":"VAT Diff.","type":"float"}
                  ]
       },
  "ds":{"sheetName":"items",
        "columns":[{"name":"curr","label":"Currency","type":"string"},
                   {"name":"transnumber","label":"Invoice No.","type":"string"},
                   {"name":"duedate","label":"Due Date","type":"string"},
                   {"name":"custname","label":"Customer","type":"string"},
                   {"name":"taxcode","label":"VAT%","type":"string"},
                   {"name":"netamount","label":"Net","type":"float"},
                   {"name":"vatamount","label":"VAT amount","type":"float"},
                   {"name":"amount","label":"Gross","type":"float"}
                  ]
       }
}' 
where reportkey ='xls_vat_en';--
