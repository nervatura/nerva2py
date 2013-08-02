INSERT INTO ui_report(reportkey, nervatype, transtype, direction, repname, description, filetype, report, label)
    VALUES ('html_vat', (select id from groups where groupname='nervatype' and groupvalue='report'), 
      null, null, 'VAT Summary - Web2Py HTML', 'Recoverable and payable VAT summary grouped by currency. Web2Py HTML sample.'
      , (select id from groups where groupname='filetype' and groupvalue='html'), null, 'Example');--

INSERT INTO ui_reportfields(report_id, fieldname, fieldtype, wheretype, description, orderby, sqlstr, parameter, dataset, defvalue)
    VALUES ((select id from ui_report where reportkey='html_vat'), 'date_from', (select id from groups where groupname='fieldtype' and groupvalue='date')
    , (select id from groups where groupname='wheretype' and groupvalue='in'), 'From date', 0, '', 0, null,'-360');--

INSERT INTO ui_reportfields(report_id, fieldname, fieldtype, wheretype, description, orderby, sqlstr, parameter, dataset)
    VALUES ((select id from ui_report where reportkey='html_vat'), 'date_to', (select id from groups where groupname='fieldtype' and groupvalue='date')
    , (select id from groups where groupname='wheretype' and groupvalue='in'), 'To date', 1, '', 0, null);--

INSERT INTO ui_reportfields(report_id, fieldname, fieldtype, wheretype, description, orderby, sqlstr, parameter, dataset)
    VALUES ((select id from ui_report where reportkey='html_vat'), 'curr', (select id from groups where groupname='fieldtype' and groupvalue='string')
    , (select id from groups where groupname='wheretype' and groupvalue='where'), 'Currency', 2, '', 0, null);--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='html_vat'), 'total', '');--

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
group by t.curr, case when t.notax=1 then ''AAM'' else tx.taxcode end, tx.rate 
order by t.curr, tx.rate'
where report_id = (select id from ui_report where reportkey='html_vat') and dataset='total';--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='html_vat'), 'ds', '');--

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
order by t.curr, t.transdate, c.custname'
where report_id = (select id from ui_report where reportkey='html_vat') and dataset='ds';--

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
order by t.curr, t.transdate, c.custname'
where report_id = (select id from ui_report where reportkey='html_vat') and dataset='ds';--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='html_vat'), 'total_bycur', '');--

update ui_reportsources set sqlstr = 'select t.curr as curr
, sum(case when dg.groupvalue=''in'' then 0-netamount else netamount end) as netamount
, sum(case when dg.groupvalue=''in'' then 0-vatamount else vatamount end) as vatamount
, sum(case when dg.groupvalue=''in'' then 0-amount else amount end) as amount 
from trans t 
inner join groups tg on t.transtype = tg.id and tg.groupvalue=''invoice'' 
inner join groups dg on t.direction = dg.id 
inner join item ti on t.id=ti.trans_id and ti.deleted=0 
where t.deleted=0 and t.transdate >= @date_from and t.transdate <= @date_to @where_str 
group by t.curr 
order by t.curr DESC'
where report_id = (select id from ui_report where reportkey='html_vat') and dataset='total_bycur';--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='html_vat'), 'company', '');--

update ui_reportsources set sqlstr = 'select c.custname as custname, c.taxnumber as taxnumber, c.account as account, addr.country as country, addr.state as state, addr.zipcode as zipcode, addr.city as city, addr.street as street 
from customer c 
left join (select * from address 
  where id in(select min(id) fid from address a 
    where a.deleted=0 and a.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') 
    group by a.ref_id)) addr on c.id = addr.ref_id 
where c.id=1'
where report_id = (select id from ui_report where reportkey='html_vat') and dataset='company';--

update ui_report set report='
{{=STYLE(XML(
    "body {margin: 10px;}"
    ))
}}
{{=TABLE(
        TR(
          TD(company[0]["custname"], _style="width:50%;font-weight:bold;vertical-align:bottom;"),
          TD(T("VAT summary"), _style="width:50%;text-align:right;font-size:30px;font-weight:bold;font-style:italic;")
        ),
        TR(
          TD(HR(_style="margin-top:5px;margin-bottom:5px;border-width:2px;"), _style="width:100%;vertical-align:middle;", _colspan="2")
        ),
        TR(
          TD(T("Report date")+": "+ds[0]["date_from"]+" - "+ds[0]["date_to"], _style="width:50%;font-weight:bold;font-size:20px;"),
          TD(T("Create date")+": "+crtime, _style="width:50%;text-align:right;font-style:italic;")
        ),
      _style="width:100%")
}}
{{=P()}}
{{=TABLE(
      THEAD(
      TR(
        TH(T("Currency")),
        TH(T("Invoice No.")),
        TH(T("Due Date")),
        TH(T("Customer")),
        TH(T("VAT%"),_style="text-align: right;"),
        TH(T("Net"),_style="text-align: right;"),
        TH(T("VAT"),_style="text-align: right;"),
        TH(T("Gross"),_style="text-align: right;"))),
      TFOOT(
      TR(
        TH(T("Total")),
        TH(T("")),
        TH(T("")),
        TH(T("")),
        TH(T(""),_style="text-align: right;"),
        TH(total_bycur[0]["netamount"],_style="text-align: right;"),
        TH(total_bycur[0]["vatamount"],_style="text-align: right;"),
        TH(total_bycur[0]["amount"],_style="text-align: right;")),
      _style="border:1px solid;"),
      *[TR(
              TD(row["curr"]),
              TD(row["transnumber"]),
              TD(row["duedate"]),
              TD(row["custname"]),
              TD(row["taxcode"],_style="text-align: right;"),
              TD(row["netamount"],_style="text-align: right;"),
              TD(row["vatamount"],_style="text-align: right;"),
              TD(row["amount"],_style="text-align: right;")
              ) for row in ds],
      _style="width:100%;border:1px solid;")
}}
{{=P(_style="margin:0px;")}}
{{=TABLE(
      THEAD(
      TR(
        TH(T("Currency")),
        TH(T("VAT%")),
        TH(T("Net income"),_style="text-align: right;"),
        TH(T("VAT(+)"),_style="text-align: right;"),
        TH(T("Net payment"),_style="text-align: right;"),
        TH(T("VAT(-)"),_style="text-align: right;"),
        TH(T("VAT Diff."),_style="text-align: right;"))),
      *[TR(
              TD(row["curr"]),
              TD(row["taxcode"]),
              TD(row["netamount_out"],_style="text-align: right;"),
              TD(row["vatamount_out"],_style="text-align: right;"),
              TD(row["netamount_in"],_style="text-align: right;"),
              TD(row["vatamount_in"],_style="text-align: right;"),
              TD(row["vatamount_diff"],_style="text-align: right;")
              ) for row in total],
      _style="width:100%;border:1px solid;")
}}
' 
where reportkey ='html_vat';--
