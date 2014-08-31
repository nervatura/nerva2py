INSERT INTO ui_report(reportkey, nervatype, transtype, direction, repname, description, filetype, report)
  VALUES ('fpdf_invoice_hu', 
      (select id from groups where groupname='nervatype' and groupvalue='trans'), 
      (select id from groups where groupname='transtype' and groupvalue='invoice'), 
      (select id from groups where groupname='direction' and groupvalue='out'), 
      'Számla HU', 'Vevőszámla', (select id from groups where groupname='filetype' and groupvalue='fpdf'), null);--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='fpdf_invoice_hu'), 'head', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='fpdf_invoice_hu'), 'items', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
VALUES((select id from ui_report where reportkey='fpdf_invoice_hu'), 'taxgroup', '');--

INSERT INTO ui_message(secname, fieldname, msg) 
VALUES ('fpdf_invoice_hu_items', 'lb_deposit', 'Előleg');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_head', 'lb_ref_invoice', 'Hiv.számla');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_head', 'lb_copy', 'MÁSOLAT');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_head', 'lb_original_issue', 'EREDETI');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_head', 'lb_cancelling_invoice', 'SZTORNÓ SZÁMLA');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_head', 'lb_amending_invoice', 'HELYESBÍTŐ BIZONYLAT');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_head', 'lb_deleted', 'Törölt');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_head', 'lb_address', 'Cím');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_head', 'lb_tax_no', 'Adószám');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_head', 'lb_account_no', 'Számlaszám');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'logo_file', 'icon24_ntura_white.png');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'logo_link', 'http://www.nervatura.com');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'web_page', 'www.nervatura.com');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'web_link', 'http://nervatura.com');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_invoice', 'SZÁMLA');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_supplier', 'Szállító');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_customer', 'Vevő');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_delivery_date', 'Telj. időpont');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_due_date', 'Esedékesség');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_creation_date', 'Számla kelte');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_currency', 'Deviza');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_payment', 'Fiz. mód');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_source_ref_no', 'Hiv. bizonylat');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_comments', 'Egyéb adatok');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_no', 'Sz.');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_description', 'Megnevezés');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_unit', 'ME');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_qty', 'M.ség');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_price', 'Egységár');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_disc', 'Kedv.');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_vat', 'ÁFA');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_vat_value', 'ÁFA érték');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_netamount', 'Nettó');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_amount', 'Bruttó');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_invoice_hu_report', 'lb_total', 'Össz.');--

update ui_reportsources set sqlstr = 'select tax.taxcode as taxcode, sum(ti.netamount) as netamount, sum(ti.vatamount) as vatamount, sum(ti.amount) as amount 
from item ti inner join product p on p.id = ti.product_id inner join tax on tax.id = ti.tax_id 
where ti.trans_id = @id 
group by tax.rate, tax.taxcode order by tax.rate'
where report_id = (select id from ui_report where reportkey='fpdf_invoice_hu') and dataset='taxgroup';--

update ui_reportsources set sqlstr = 'select concat(case when ti.deposit=1 then ''={{lb_deposit}}: '' else '''' end, case when pf.value is null then '''' else concat(pf.value,'' '') end, ti.description) as description
, pf.value as vtsz, p.partnumber, ti.unit, ti.qty as qty, tax.taxcode
, ti.fxprice, ti.netamount, ti.discount, ti.vatamount, ti.amount, ti.deposit 
from item ti inner join product p on p.id = ti.product_id inner join tax on tax.id = ti.tax_id 
left join fieldvalue pf on pf.ref_id = p.id and fieldname = ''szj_vtsz'' 
where ti.deleted=0 and ti.trans_id = @id 
order by ti.id'
where report_id = (select id from ui_report where reportkey='fpdf_invoice_hu') and dataset='items';--

[engine sqlite] update ui_reportsources set sqlstr = 'select case when ti.deposit=1 then ''={{lb_deposit}}: '' else '''' end || case when pf.value is null then '''' else pf.value||'' '' end || ti.description as description
, pf.value as vtsz, p.partnumber as partnumber, ti.unit as unit, ti.qty as qty, tax.taxcode as taxcode
, ti.fxprice as fxprice, ti.netamount as netamount, ti.discount as discount, ti.vatamount as vatamount, ti.amount as amount, ti.deposit as deposit 
from item ti inner join product p on p.id = ti.product_id inner join tax on tax.id = ti.tax_id 
left join fieldvalue pf on pf.ref_id = p.id and fieldname = ''szj_vtsz'' 
where ti.deleted=0 and ti.trans_id = @id 
order by ti.id'
where report_id = (select id from ui_report where reportkey='fpdf_invoice_hu') and dataset='items';--

[engine mssql] update ui_reportsources set sqlstr = 'select case when ti.deposit=1 then ''={{lb_deposit}}: '' else '''' end + case when pf.value is null then '''' else pf.value+'' '' end + ti.description as description
, pf.value as vtsz, p.partnumber, ti.unit, ti.qty as qty, tax.taxcode
, ti.fxprice, ti.netamount, ti.discount, ti.vatamount, ti.amount, ti.deposit 
from item ti inner join product p on p.id = ti.product_id inner join tax on tax.id = ti.tax_id 
left join fieldvalue pf on pf.ref_id = p.id and fieldname = ''szj_vtsz'' 
where ti.deleted=0 and ti.trans_id = @id 
order by ti.id'
where report_id = (select id from ui_report where reportkey='fpdf_invoice_hu') and dataset='items';--

update ui_reportsources set sqlstr = 'function|convertNumberToText_hu|lang=>HU|numvalue=>select sum(ti.amount) as value 
  from item ti where ti.deleted=0 and ti.trans_id = @id'
where report_id = (select id from ui_report where reportkey='fpdf_invoice_hu') and dataset='isumamount';--

update ui_reportsources set sqlstr = 'select t.transnumber, t.transdate, t.crdate
, case when t.notes is null then '''' else t.notes end as notes
, case when t.fnote is null then '''' else t.fnote end as fnote
, case when (tcast.value != ''normal'' ) then 
    case when t.ref_transnumber is null then '''' else concat(''={{lb_ref_invoice}}: '', t.ref_transnumber) end 
  else '''' end as ref_transnumber_1
, case when (tcast.value = ''normal'' ) then
  case when t.ref_transnumber is null then '''' else t.ref_transnumber end
  else '''' end as ref_transnumber_2, t.deleted
, case when t.closed = 1 then ''={{lb_copy}}'' else ''={{lb_original_issue}}'' end as state
, case when (tcast.value = ''cancellation'' ) then ''={{lb_cancelling_invoice}}'' when (tcast.value = ''amendment'') then ''={{lb_amending_invoice}}'' else '''' end as transcast
, case when (t.deleted = 1 and tcast.value <> ''cancellation'' ) then ''={{lb_deleted}}'' else '''' end as status
, substr(cast(t.duedate as char(10)), 1, 10) as duedate
, t.curr, cu.description as currname, case when msp.msg is null then ptg.groupvalue else msp.msg end as paidtypedesc, t.acrate
, compname.value as comp_name
, concat(''={{lb_address}}: '',case when compaddress.value is null then '''' else compaddress.value end) as comp_address
, concat(''={{lb_tax_no}}: '',case when comptax.value is null then '''' else comptax.value end) as comp_taxnumber
, custname.value as cust_name
, concat(''={{lb_address}}: '',case when custaddress.value is null then '''' else custaddress.value end) as cust_address
, concat(''={{lb_tax_no}}: '',case when custtax.value is null then '''' else custtax.value end) as cust_taxnumber
, concat(''={{lb_account_no}}: '',case when c.account is null then '''' else c.account end) as custaccount
, concat(''={{lb_account_no}}: '',case when comp.account is null then '''' else comp.account end) as compaccount
, tsum.sum_netamount, tsum.sum_vatamount, tsum.sum_amount 
from trans t 
inner join currency cu on t.curr = cu.curr 
inner join fieldvalue tcast on t.id = tcast.ref_id and tcast.fieldname=''trans_transcast'' 
inner join groups ptg on t.paidtype = ptg.id 
  left join ui_message msp on msp.fieldname = ptg.groupvalue and  msp.secname = ''paidtype'' and msp.lang = ''en'' 
left join fieldvalue compname on t.id = compname.ref_id and compname.fieldname=''trans_custinvoice_compname'' 
left join fieldvalue compaddress on t.id = compaddress.ref_id and compaddress.fieldname=''trans_custinvoice_compaddress'' 
left join fieldvalue comptax on t.id = comptax.ref_id and comptax.fieldname=''trans_custinvoice_comptax'' 
left join fieldvalue custname on t.id = custname.ref_id and custname.fieldname=''trans_custinvoice_custname'' 
left join fieldvalue custaddress on t.id = custaddress.ref_id and custaddress.fieldname=''trans_custinvoice_custaddress'' 
left join fieldvalue custtax on t.id = custtax.ref_id and custtax.fieldname=''trans_custinvoice_custtax'' 
inner join customer c on t.customer_id = c.id 
left join customer comp on comp.id in (select min(customer.id) from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') 
left join (select ti.trans_id as id, sum(ti.netamount) as sum_netamount, sum(ti.vatamount) as sum_vatamount, sum(ti.amount) as sum_amount 
  from item ti where ti.deleted=0 group by ti.trans_id ) as tsum on tsum.id = t.id  
where t.id = @id'
where report_id = (select id from ui_report where reportkey='fpdf_invoice_hu') and dataset='head';--

[engine sqlite]update ui_reportsources set sqlstr = 'select t.transnumber as transnumber, t.transdate as transdate, t.crdate as crdate
, case when t.notes is null then '''' else t.notes end as notes
, case when t.fnote is null then '''' else t.fnote end as fnote
, case when (tcast.value != ''normal'' ) then 
    case when t.ref_transnumber is null then '''' else ''={{lb_ref_invoice}}: '' || t.ref_transnumber end 
  else '''' end as ref_transnumber_1
, case when (tcast.value = ''normal'' ) then
  case when t.ref_transnumber is null then '''' else t.ref_transnumber end
  else '''' end as ref_transnumber_2, t.deleted
, case when t.closed = 1 then ''={{lb_copy}}'' else ''={{lb_original_issue}}'' end as state
, case when (tcast.value = ''cancellation'' ) then ''={{lb_cancelling_invoice}}'' when (tcast.value = ''amendment'') then ''={{lb_amending_invoice}}'' else '''' end as transcast
, case when (t.deleted = 1 and tcast.value <> ''cancellation'' ) then ''={{lb_deleted}}'' else '''' end as status
, substr(cast(t.duedate as char(10)), 1, 10) as duedate
, t.curr as curr, cu.description as currname, case when msp.msg is null then ptg.groupvalue else msp.msg end as paidtypedesc, t.acrate as acrate
, compname.value as comp_name
, ''={{lb_address}}: ''||case when compaddress.value is null then '''' else compaddress.value end as comp_address
, ''={{lb_tax_no}}: ''||case when comptax.value is null then '''' else comptax.value end as comp_taxnumber
, custname.value as cust_name
, ''={{lb_address}}: ''||case when custaddress.value is null then '''' else custaddress.value end as cust_address
, ''={{lb_tax_no}}: ''||case when custtax.value is null then '''' else custtax.value end as cust_taxnumber
, ''={{lb_account_no}}: ''||case when c.account is null then '''' else c.account end as custaccount, ''={{lb_account_no}}: ''||case when comp.account is null then '''' else comp.account end as compaccount
, tsum.sum_netamount as sum_netamount, tsum.sum_vatamount as sum_vatamount, tsum.sum_amount as sum_amount 
from trans t 
inner join currency cu on t.curr = cu.curr 
inner join fieldvalue tcast on t.id = tcast.ref_id and tcast.fieldname=''trans_transcast'' 
inner join groups ptg on t.paidtype = ptg.id 
  left join ui_message msp on msp.fieldname = ptg.groupvalue and  msp.secname = ''paidtype'' and msp.lang = ''en'' 
left join fieldvalue compname on t.id = compname.ref_id and compname.fieldname=''trans_custinvoice_compname'' 
left join fieldvalue compaddress on t.id = compaddress.ref_id and compaddress.fieldname=''trans_custinvoice_compaddress'' 
left join fieldvalue comptax on t.id = comptax.ref_id and comptax.fieldname=''trans_custinvoice_comptax'' 
left join fieldvalue custname on t.id = custname.ref_id and custname.fieldname=''trans_custinvoice_custname'' 
left join fieldvalue custaddress on t.id = custaddress.ref_id and custaddress.fieldname=''trans_custinvoice_custaddress'' 
left join fieldvalue custtax on t.id = custtax.ref_id and custtax.fieldname=''trans_custinvoice_custtax'' 
inner join customer c on t.customer_id = c.id 
left join customer comp on comp.id in (select min(customer.id) from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') 
left join (select ti.trans_id as id, sum(ti.netamount) as sum_netamount, sum(ti.vatamount) as sum_vatamount, sum(ti.amount) as sum_amount 
  from item ti where ti.deleted=0 group by ti.trans_id ) as tsum on tsum.id = t.id  
where t.id = @id'
where report_id = (select id from ui_report where reportkey='fpdf_invoice_hu') and dataset='head';--

[engine mssql]update ui_reportsources set sqlstr = 'select t.transnumber, t.transdate, t.crdate
, case when t.notes is null then '''' else t.notes end as notes
, case when t.fnote is null then '''' else t.fnote end as fnote
, case when (tcast.value != ''normal'' ) then 
    case when t.ref_transnumber is null then '''' else ''={{lb_ref_invoice}}: '' + t.ref_transnumber end 
  else '''' end as ref_transnumber_1
, case when (tcast.value = ''normal'' ) then
  case when t.ref_transnumber is null then '''' else t.ref_transnumber end
  else '''' end as ref_transnumber_2, t.deleted
, case when t.closed = 1 then ''={{lb_copy}}'' else ''={{lb_original_issue}}'' end as state
, case when (tcast.value = ''cancellation'' ) then ''={{lb_cancelling_invoice}}'' when (tcast.value = ''amendment'') then ''={{lb_amending_invoice}}'' else '''' end as transcast
, case when (t.deleted = 1 and tcast.value <> ''cancellation'' ) then ''={{lb_deleted}}'' else '''' end as status
, CONVERT(VARCHAR(10), t.duedate, 120) as duedate
, t.curr, cu.description as currname, case when msp.msg is null then ptg.groupvalue else msp.msg end as paidtypedesc, t.acrate
, compname.value as comp_name
, ''={{lb_address}}: ''+case when compaddress.value is null then '''' else compaddress.value end as comp_address
, ''={{lb_tax_no}}: ''+case when comptax.value is null then '''' else comptax.value end as comp_taxnumber
, custname.value as cust_name
, ''={{lb_address}}: ''+case when custaddress.value is null then '''' else custaddress.value end as cust_address
, ''={{lb_tax_no}}: ''+case when custtax.value is null then '''' else custtax.value end as cust_taxnumber
, ''={{lb_account_no}}: ''+case when c.account is null then '''' else c.account end as custaccount, ''={{lb_account_no}}: ''+case when comp.account is null then '''' else comp.account end as compaccount
, tsum.sum_netamount, tsum.sum_vatamount, tsum.sum_amount 
from trans t 
inner join currency cu on t.curr = cu.curr 
inner join fieldvalue tcast on t.id = tcast.ref_id and tcast.fieldname=''trans_transcast'' 
inner join groups ptg on t.paidtype = ptg.id 
  left join ui_message msp on msp.fieldname = ptg.groupvalue and  msp.secname = ''paidtype'' and msp.lang = ''en'' 
left join fieldvalue compname on t.id = compname.ref_id and compname.fieldname=''trans_custinvoice_compname'' 
left join fieldvalue compaddress on t.id = compaddress.ref_id and compaddress.fieldname=''trans_custinvoice_compaddress'' 
left join fieldvalue comptax on t.id = comptax.ref_id and comptax.fieldname=''trans_custinvoice_comptax'' 
left join fieldvalue custname on t.id = custname.ref_id and custname.fieldname=''trans_custinvoice_custname'' 
left join fieldvalue custaddress on t.id = custaddress.ref_id and custaddress.fieldname=''trans_custinvoice_custaddress'' 
left join fieldvalue custtax on t.id = custtax.ref_id and custtax.fieldname=''trans_custinvoice_custtax'' 
inner join customer c on t.customer_id = c.id 
left join customer comp on comp.id in (select min(customer.id) from customer inner join groups on customer.custtype=groups.id and groups.groupvalue=''own'') 
left join (select ti.trans_id as id, sum(ti.netamount) as sum_netamount, sum(ti.vatamount) as sum_vatamount, sum(ti.amount) as sum_amount 
  from item ti where ti.deleted=0 group by ti.trans_id ) as tsum on tsum.id = t.id  
where t.id = @id'
where report_id = (select id from ui_report where reportkey='fpdf_invoice_hu') and dataset='head';--

update ui_report set report = '<template>
  <report title="SZÁMLA" font-family="helvetica" font-size="11" left-margin="15" top-margin="15" right-margin="15" decode="utf-8" encode="iso8859_2" />
  <header>
    <row height="10">
      <image file="={{labels.logo_file}}" link="={{labels.logo_link}}"/>
      <cell name="label" value="={{labels.lb_invoice}}" font-style="BI" font-size="26" color="14212058"/>
      <cell name="transnumber" value="={{head.0.transnumber}}" align="R" font-style="B" font-size="20"/>
    </row>
    <row hgap="2" height="1">
      <hgap width="8" />
      <cell name="status" value="={{head.0.status}}" align="L" font-style="B" color="16711680" font-size="10"/>
      <cell name="state" value="={{head.0.state}}" align="R" font-style="B" font-size="10"/>
    </row>
    <row >
      <cell name="transcast" value="={{head.0.transcast}}" align="L" font-style="B" font-size="10"/>
      <cell name="ref_transnumber_1" value="={{head.0.ref_transnumber_1}}" align="R" font-style="B" font-size="10"/>
    </row>
    <hline border-color="14212058"/>
    <vgap height="2"/>
  </header>
  <details>
    <row>
      <cell name="label" width="50%" value="={{labels.lb_supplier}}" font-style="B" background-color="16119285" border="LT" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_customer}}" font-style="B" background-color="16119285"  border="LRT" border-color="14212058"/>
    </row>
    <row>
      <cell name="company_name" width="50%" font-style="B" value="={{head.0.comp_name}}" border="L" border-color="14212058"/>
      <cell name="customer_name" font-style="B" value="={{head.0.cust_name}}" border="LR" border-color="14212058"/>
    </row>
    <row>
      <cell name="company_address" width="50%" value="={{head.0.comp_address}}" border="L" border-color="14212058"/>
      <cell name="customer_address" value="={{head.0.cust_address}}" border="LR" border-color="14212058"/>
    </row>
    <row>
      <cell name="company_taxnumber" width="50%" value="={{head.0.comp_taxnumber}}" border="L" border-color="14212058"/>
      <cell name="customer_taxnumber" value="={{head.0.cust_taxnumber}}" border="LR" border-color="14212058"/>
    </row>
    <row>
      <cell name="company_account" width="50%" value="={{head.0.compaccount}}" border="L" border-color="14212058"/>
      <cell name="customer_account" value="={{head.0.custaccount}}" border="LR" border-color="14212058"/>
    </row>
    <row>
      <cell name="label" align="C" width="30" font-style="B" value="={{labels.lb_delivery_date}}" background-color="16119285" border="LBT" border-color="14212058"/>
      <cell name="label" align="C" width="30" font-style="B" value="={{labels.lb_due_date}}" background-color="16119285" border="LBT" border-color="14212058"/>
      <cell name="label" align="C" width="30" font-style="B" value="={{labels.lb_creation_date}}" background-color="16119285" border="LBT" border-color="14212058"/>
      <cell name="label" align="C" width="20" font-style="B" value="={{labels.lb_currency}}" background-color="16119285" border="LBT" border-color="14212058"/>
      <cell name="label" align="C" width="30" font-style="B" value="={{labels.lb_payment}}" background-color="16119285" border="LBT" border-color="14212058"/>
      <cell name="label" align="C" font-style="B" value="={{labels.lb_source_ref_no}}" background-color="16119285" border="LBTR" border-color="14212058"/>
    </row>
    <row>
      <cell name="transdate" align="C" width="30" value="={{head.0.transdate}}" border="LB" border-color="14212058"/>
      <cell name="duedate" align="C" width="30" value="={{head.0.duedate}}" border="LB" border-color="14212058"/>
      <cell name="crdate" align="C" width="30" value="={{head.0.crdate}}" border="LB" border-color="14212058"/>
      <cell name="curr" align="C" width="20" value="={{head.0.curr}}" border="LB" border-color="14212058"/>
      <cell name="payment" align="C" width="30" value="={{head.0.paidtypedesc}}" border="LB" border-color="14212058"/>
      <cell name="source_transnumber" align="C" value="={{head.0.ref_transnumber_2}}" border="LBR" border-color="14212058"/>
    </row>
    <row>
      <cell name="label" width="30" font-style="B" value="={{labels.lb_comments}}" background-color="16119285" border="LB" border-color="14212058"/>
      <cell name="comment" multiline="true" value="={{head.0.notes}}" border="LBR" border-color="14212058"/>
    </row>
    <datagrid name="items" databind="items" border="1" border-color="14212058" font-size="10">
      <header background-color="16119285" />
      <columns>
        <column width="4%" fieldname="counter" align="R" label="={{labels.lb_no}}"/>
        <column width="25%" fieldname="description" label="={{labels.lb_description}}"/>
        <column width="8%" fieldname="unit" label="={{labels.lb_unit}}"/>
        <column width="7%" fieldname="qty" align="R" thousands=" " digit="2" label="={{labels.lb_qty}}"/>
        <column width="10%" fieldname="fxprice" align="R" thousands=" " digit="2" label="={{labels.lb_price}}"/>
        <column width="7%" fieldname="discount" align="R" thousands=" " digit="2" label="={{labels.lb_disc}}%"/>
        <column width="8%" fieldname="taxcode" align="R" label="={{labels.lb_vat}}%"/>
        <column width="11%" fieldname="netamount" align="R" thousands=" " digit="2" label="={{labels.lb_netamount}}"/>
        <column width="9%" fieldname="vatamount" align="R" thousands=" " digit="2" label="={{labels.lb_vat_value}}"/>
        <column width="12%" fieldname="amount" align="R" thousands=" " digit="2" label="={{labels.lb_amount}}"/>
      </columns>  
    </datagrid>
    <vgap height="2"/>
    <datagrid width="50%" name="taxgroup" databind="taxgroup" border="1" border-color="14212058" font-size="10">
      <header background-color="16119285"/>
      <columns>
        <column width="19%" fieldname="taxcode" align="R" label="={{labels.lb_vat}}%" footer="={{labels.lb_total}}"/>
        <column width="27%" fieldname="netamount" align="R" thousands=" " digit="2" label="={{labels.lb_netamount}}" footer="={{head.0.sum_netamount}}"/>
        <column width="27%" fieldname="vatamount" align="R" thousands=" " digit="2" label="={{labels.lb_vat_value}}" footer="={{head.0.sum_vatamount}}"/>
        <column width="27%" fieldname="amount" align="R" thousands=" " digit="2" label="={{labels.lb_amount}}" footer="={{head.0.sum_amount}}"/>
      </columns>  
    </datagrid>
    <vgap height="4"/>
    <row>
      <cell name="label" value="azaz "  align="R" />
      <cell width="0" name="label" align="L" font-style="B" value="={{isumamount}} forint"/>
    </row>
    <row>
      <cell name="hu_vat" value="={{head.0.huvat}}"/>
    </row>
    <html fieldname="notes">={{head.0.fnote}}</html>
  </details>
  <footer>
    <vgap height="2"/>
    <hline border-color="14212058"/>
    <row height="10">
      <cell value="={{labels.web_page}}" link="={{labels.web_link}}" font-style="BI" color="2162943"/>
      <cell value="{{pages}}/{{page}}" align="R" font-style="B"/>
    </row>
  </footer>
</template>'
where reportkey = 'fpdf_invoice_hu';--
