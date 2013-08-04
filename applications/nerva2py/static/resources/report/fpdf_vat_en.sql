INSERT INTO ui_report(reportkey, nervatype, transtype, direction, repname, description, filetype, report, label)
    VALUES ('fpdf_vat_en', (select id from groups where groupname='nervatype' and groupvalue='report'), 
      null, null, 'VAT Summary - Nervatura Report', 'Recoverable and payable VAT summary grouped by currency. Nervatura Report sample.'
      , (select id from groups where groupname='filetype' and groupvalue='fpdf'), null, 'Example');--

INSERT INTO ui_reportfields(report_id, fieldname, fieldtype, wheretype, description, orderby, sqlstr, parameter, dataset,defvalue)
    VALUES ((select id from ui_report where reportkey='fpdf_vat_en'), 'date_from', (select id from groups where groupname='fieldtype' and groupvalue='date')
    , (select id from groups where groupname='wheretype' and groupvalue='in'), 'From date', 0, '', 0, null,'-360');--

INSERT INTO ui_reportfields(report_id, fieldname, fieldtype, wheretype, description, orderby, sqlstr, parameter, dataset)
    VALUES ((select id from ui_report where reportkey='fpdf_vat_en'), 'date_to', (select id from groups where groupname='fieldtype' and groupvalue='date')
    , (select id from groups where groupname='wheretype' and groupvalue='in'), 'To date', 1, '', 0, null);--

INSERT INTO ui_reportfields(report_id, fieldname, fieldtype, wheretype, description, orderby, sqlstr, parameter, dataset)
    VALUES ((select id from ui_report where reportkey='fpdf_vat_en'), 'curr', (select id from groups where groupname='fieldtype' and groupvalue='string')
    , (select id from groups where groupname='wheretype' and groupvalue='where'), 'Currency', 2, '', 0, null);--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='fpdf_vat_en'), 'total', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='fpdf_vat_en'), 'ds', '');--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='fpdf_vat_en'), 'total_bycur', '');--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='fpdf_vat_en'), 'company', '');--

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
where report_id = (select id from ui_report where reportkey='fpdf_vat_en') and dataset='total';--

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
where report_id = (select id from ui_report where reportkey='fpdf_vat_en') and dataset='ds';--

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
where report_id = (select id from ui_report where reportkey='fpdf_vat_en') and dataset='ds';--

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
where report_id = (select id from ui_report where reportkey='fpdf_vat_en') and dataset='total_bycur';--

update ui_reportsources set sqlstr = 'select c.custname as custname, c.taxnumber as taxnumber, c.account as account, addr.country as country, addr.state as state, addr.zipcode as zipcode, addr.city as city, addr.street as street 
from customer c 
left join (select * from address 
  where id in(select min(id) fid from address a 
    where a.deleted=0 and a.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') 
    group by a.ref_id)) addr on c.id = addr.ref_id 
where c.id=1'
where report_id = (select id from ui_report where reportkey='fpdf_vat_en') and dataset='company';--

update ui_report set report='
<template>
  <report title="VAT summary" font-family="helvetica" font-size="11" left-margin="15" top-margin="15" right-margin="15" decode="utf-8" encode="latin_1" />
  <header>
    <row height="10">
      <cell name="custname" value="={{company.0.custname}}" align="L" font-style="B" font-size="12" width="100"/>
      <cell name="label" value="VAT summary" font-style="BI" font-size="26" align="R" color="14212058"/>
    </row>
    <vgap height="2"/>
    <hline border-color="14212058" gap="1"/>
    <vgap height="3"/>
    <row hgap="2" height="1">
      <cell name="label" value="Report date:" font-style="B" font-size="10" align="L" />
      <cell name="date_from" value="={{ds.0.date_from}}" align="L" font-style="B" font-size="10" />
      <cell name="label" value="-" font-style="B" font-size="10" align="L" width="5"/>
      <cell name="date_to" value="={{ds.0.date_to}}" align="L" font-style="B" font-size="10"/>
      <cell name="crdate" value="Create date: ={{crtime}}" align="R" font-style="I" font-size="9"/>
    </row>
  </header>
  <details>
    <vgap height="3"/>
    <datagrid name="items" databind="ds" border="1" border-color="14212058" font-size="8">
      <header background-color="16119285" />
      <columns>
        <column width="4%" fieldname="counter" align="R" label="No." footer=" "/>
        <column width="6%" fieldname="curr" label="Curr" footer=" "/>
        <column width="20%" fieldname="transnumber" label="Invoice No." footer="Total"/>
        <column width="11%" fieldname="duedate" align="C" label="Due Date" footer=" "/>
        <column width="20%" fieldname="custname" label="Customer" footer=" "/>
        <column width="5%" fieldname="taxcode" align="R" label="VAT%" footer=" " />
        <column width="12%" fieldname="netamount" align="R" thousands=" " digit="2" label="Net" footer="={{total_bycur.0.netamount}}"/>
        <column width="11%" fieldname="vatamount" align="R" thousands=" " digit="2" label="VAT" footer="={{total_bycur.0.vatamount}}"/>
        <column width="12%" fieldname="amount" align="R" thousands=" " digit="2" label="Gross" footer="={{total_bycur.0.amount}}"/>
      </columns>  
    </datagrid>
    <vgap height="3"/>
    <datagrid name="total" databind="total" border="1" border-color="14212058" font-size="8">
      <header background-color="16119285" />
      <columns>
        <column width="10%" fieldname="curr" label="Curr" />
        <column width="8%" fieldname="taxcode" align="R" label="VAT%" />
        <column width="17%" fieldname="netamount_out" label="Net income" align="R" thousands=" " digit="2" />
        <column width="16%" fieldname="vatamount_out" label="VAT(+)" align="R" thousands=" " digit="2" />
        <column width="17%" fieldname="netamount_in" align="R" thousands=" " digit="2" label="Net payment" />
        <column width="16%" fieldname="vatamount_in" align="R" thousands=" " digit="2" label="VAT(-)" />
        <column width="17%" fieldname="vatamount_diff" align="R" thousands=" " digit="2" label="VAT Diff." />
      </columns>  
    </datagrid>
  </details>
  <footer>
    <vgap height="2"/>
    <hline border-color="14212058"/>
    <row height="10">
      <cell value="www.nervatura.com" link="http://nervatura.com" font-style="BI" color="2162943"/>
      <cell value="{{pages}}/{{page}}" align="R" font-style="B"/>
    </row>
  </footer>
</template>
' 
where reportkey ='fpdf_vat_en';--
