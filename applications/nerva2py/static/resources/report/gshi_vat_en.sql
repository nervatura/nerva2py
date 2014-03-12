INSERT INTO ui_report(reportkey, nervatype, transtype, direction, repname, description, filetype, report, label)
    VALUES ('gshi_vat_en', (select id from groups where groupname='nervatype' and groupvalue='report'), 
      null, null, 'VAT Summary - Genshi HTML', 'Recoverable and payable VAT summary grouped by currency. Genshi template sample.'
      , (select id from groups where groupname='filetype' and groupvalue='gshi'), null, 'Example');--

INSERT INTO ui_reportfields(report_id, fieldname, fieldtype, wheretype, description, orderby, sqlstr, parameter, dataset,defvalue)
    VALUES ((select id from ui_report where reportkey='gshi_vat_en'), 'date_from', (select id from groups where groupname='fieldtype' and groupvalue='date')
    , (select id from groups where groupname='wheretype' and groupvalue='in'), 'From date', 0, '', 0, null,'-360');--

INSERT INTO ui_reportfields(report_id, fieldname, fieldtype, wheretype, description, orderby, sqlstr, parameter, dataset)
    VALUES ((select id from ui_report where reportkey='gshi_vat_en'), 'date_to', (select id from groups where groupname='fieldtype' and groupvalue='date')
    , (select id from groups where groupname='wheretype' and groupvalue='in'), 'To date', 1, '', 0, null);--

INSERT INTO ui_reportfields(report_id, fieldname, fieldtype, wheretype, description, orderby, sqlstr, parameter, dataset)
    VALUES ((select id from ui_report where reportkey='gshi_vat_en'), 'curr', (select id from groups where groupname='fieldtype' and groupvalue='string')
    , (select id from groups where groupname='wheretype' and groupvalue='where'), 'Currency', 2, '', 0, null);--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='gshi_vat_en'), 'total', '');--

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
where report_id = (select id from ui_report where reportkey='gshi_vat_en') and dataset='total';--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='gshi_vat_en'), 'ds', '');--

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
where report_id = (select id from ui_report where reportkey='gshi_vat_en') and dataset='ds';--

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
where report_id = (select id from ui_report where reportkey='gshi_vat_en') and dataset='ds';--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='gshi_vat_en'), 'total_bycur', '');--

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
where report_id = (select id from ui_report where reportkey='gshi_vat_en') and dataset='total_bycur';--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='gshi_vat_en'), 'company', '');--

update ui_reportsources set sqlstr = 'select c.custname as custname, c.taxnumber as taxnumber, c.account as account, addr.country as country, addr.state as state, addr.zipcode as zipcode, addr.city as city, addr.street as street 
from customer c 
left join (select * from address 
  where id in(select min(id) fid from address a 
    where a.deleted=0 and a.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') 
    group by a.ref_id)) addr on c.id = addr.ref_id 
where c.id in(select min(customer.id) from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'')'
where report_id = (select id from ui_report where reportkey='gshi_vat_en') and dataset='company';--

update ui_report set report='
<?python
    def splitThousands(s, tSep=" ", dSep="."): 
      if s == None:
        retval = 0
      else:
        if not isinstance( s, str ):
          s = str( s )
        cnt=0
        numChars=dSep+"0123456789"
        ls=len(s)
        while cnt < ls and s[cnt] not in numChars: cnt += 1
        lhs = s[ 0:cnt ]
        s = s[ cnt: ]
        if dSep == "":
          cnt = -1
        else:
          cnt = s.rfind( dSep )
        if cnt > 0:
          rhs = dSep + s[ cnt+1: ]
          s = s[ :cnt ]
        else:
          rhs = ""
        splt=""
        while s != "":
          splt= s[ -3: ] + tSep + splt
          s = s[ :-3 ]
        retval = lhs + splt[ :-1 ] + rhs
      return retval
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
    "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://genshi.edgewall.org/"
      xmlns:xi="http://www.w3.org/2001/XInclude"
      lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <title>VAT summary</title>
    <link rel="shortcut icon" href="/nerva2py/static/favicon.ico" type="image/x-icon"/>
  </head>
  <body>
  
  <table width="100%" border="0">
    <tr>
      <td width="50%"><b><i>${company[0].custname}</i></b></td>
      <td width="50%" align="right" style="font-size:26px;">
        <b><i>VAT summary</i></b>
      </td>
    </tr>
  </table>
    <hr />
    <table width="100%" border="0">
    <tr>
      <td width="80%"><b>Report date: ${ds[0].date_from} - ${ds[0].date_to}</b></td>
      <td width="20%" rowspan="2" align="right">
        <i>Create date: ${crtime}</i>
      </td>
    </tr>
  </table>
    <p></p>
    <table id="gridbox1" width="96%" height= "100%" cellpadding="4" style="border: 1px solid #000000; border-collapse: collapse;" border="1" repeat="1">
      <th style="background-color:#CCCCCC">Currency</th>
      <th style="background-color:#CCCCCC">Invoice No.</th>
      <th style="background-color:#CCCCCC">Due Date</th>
      <th style="background-color:#CCCCCC">Customer</th>
      <th style="background-color:#CCCCCC">VAT %</th>
      <th style="background-color:#CCCCCC">Net</th>
      <th style="background-color:#CCCCCC">VAT amount</th>
      <th style="background-color:#CCCCCC">Gross</th>
        <tr py:for="item in ds">
            <td align="center">${item.curr}</td>
            <td>${item.transnumber}</td>
            <td align="center">${item.transdate}</td>
            <td>${item.custname}</td>
            <td align="right" style="padding-right:30px;">${item.taxcode}</td>
            <td align="right">${splitThousands(item.netamount)}</td>
            <td align="right">${splitThousands(item.vatamount)}</td>
            <td align="right">${splitThousands(item.amount)}</td>
        </tr>
        <tr py:for="item in total_bycur">
            <td colspan="5"><b>Total</b></td>
            <td align="right"><b>${splitThousands(item.netamount)}</b></td>
            <td align="right"><b>${splitThousands(item.vatamount)}</b></td>
            <td align="right"><b>${splitThousands(item.amount)}</b></td>
        </tr>
    </table>
    <p></p>
    <table id="gridbox2" width="96%" height="100%" cellpadding="4" style="border: 1px solid #000000; border-collapse: collapse;" border="1" repeat="1">
      <th style="background-color:#CCCCCC">Currency</th>
      <th style="background-color:#CCCCCC">VAT %</th>
      <th style="background-color:#CCCCCC">Net income</th>
      <th style="background-color:#CCCCCC">VAT(+)</th>
      <th style="background-color:#CCCCCC">Net payment</th>
      <th style="background-color:#CCCCCC">VAT(-)</th>
      <th style="background-color:#CCCCCC">TAX diff.</th>
        <tr py:for="item in total">
            <td align="center">${item.curr}</td>
            <td align="right" style="padding-right:30px;">${item.taxcode}</td>
            <td align="right">${splitThousands(item.netamount_out)}</td>
            <td align="right">${splitThousands(item.vatamount_out)}</td>
            <td align="right">${splitThousands(item.netamount_in)}</td>
            <td align="right">${splitThousands(item.vatamount_in)}</td>
            <td align="right">${splitThousands(item.vatamount_in-item.vatamount_out)}</td>
        </tr>
    </table>
  </body>
</html>' 
where reportkey ='gshi_vat_en';--
