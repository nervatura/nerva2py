INSERT INTO ui_report(reportkey, nervatype, transtype, direction, repname, description, filetype, report)
    VALUES ('fpdf_customer_sheet_en', (select id from groups where groupname='nervatype' and groupvalue='customer'), 
      null, null, 'Customer Sheet', 'Customer Information Sheet', (select id from groups where groupname='filetype' and groupvalue='fpdf'), null);--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
    VALUES ((select id from ui_report where reportkey='fpdf_customer_sheet_en'), 'head', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
    VALUES ((select id from ui_report where reportkey='fpdf_customer_sheet_en'), 'fieldvalue', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
    VALUES ((select id from ui_report where reportkey='fpdf_customer_sheet_en'), 'address', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
    VALUES ((select id from ui_report where reportkey='fpdf_customer_sheet_en'), 'contact', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
    VALUES ((select id from ui_report where reportkey='fpdf_customer_sheet_en'), 'groups', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
    VALUES ((select id from ui_report where reportkey='fpdf_customer_sheet_en'), 'event', '');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_head', 'lb_yes', 'YES');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_head', 'lb_no', 'NO');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_fieldvalue', 'lb_yes', 'YES');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_fieldvalue', 'lb_no', 'NO');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'logo_file', 'icon24_ntura_white.png');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'logo_link', 'http://www.nervatura.com');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'web_page', 'www.nervatura.com');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'web_link', 'http://nervatura.com');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_customer_datasheet', 'CUSTOMER DATASHEET');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_customer_no', 'Customer No.');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_name', 'Name');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_customer_type', 'Customer type');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_taxnumber', 'Taxnumber');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_tax_free', 'Tax free');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_inactive', 'Inactive');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_account', 'Account');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_due_date', 'Due Date (day)');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_discount', 'Discount');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_credit_limit', 'Credit limit');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_additional_data', 'Additional data');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_no', 'No.');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_description', 'Description');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_value', 'Value');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_comment', 'Comment');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_address_details', 'Address details');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_zipcode', 'Zipcode');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_city', 'City');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_street', 'Street');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_firstname', 'Firstname');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_surname', 'Surname');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_status', 'Status');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_phone', 'Phone');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_mobil', 'Mobil');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_email', 'Email');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_events', 'Events');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_event_no', 'Event No.');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_group', 'Group');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_fromdate', 'Date From');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_todate', 'Date To');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_subject', 'Subject');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_customer_sheet_en_report', 'lb_place', 'Place');--

update ui_reportsources set sqlstr='select c.id as id, c.custnumber as custnumber, c.custname as custname, ctype.groupvalue as custtype, c.taxnumber as taxnumber, c.account as account, 
  case when c.notax =1 then ''={{lb_yes}}'' else ''={{lb_no}}'' end as notax, c.terms as terms, c.creditlimit as creditlimit,
  c.discount as discount, c.notes as notes,  case when c.inactive=1 then ''={{lb_yes}}'' else ''={{lb_no}}'' end as inactive 
from customer c 
inner join groups as ctype on c.custtype=ctype.id 
where c.deleted=0 and c.id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_customer_sheet_en') and dataset = 'head';--

update ui_reportsources set sqlstr='select df.description as fielddef,
case when fg.groupvalue in (''bool'') and fv.value = ''true'' then ''={{lb_yes}}''
        when fg.groupvalue in (''bool'') and fv.value = ''false'' then ''={{lb_no}}''
        when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''transitem'',''transmovement'',''transpayment'') then rf_trans.transnumber
        when fg.groupvalue in (''product'') then rf_product.partnumber
        when fg.groupvalue in (''project'') then rf_project.pronumber
        when fg.groupvalue in (''employee'') then rf_employee.empnumber
        when fg.groupvalue in (''place'') then rf_place.planumber
        else fv.value end as value,
fv.notes as notes 
from fieldvalue fv 
inner join deffield df on fv.fieldname = df.fieldname and df.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') 
inner join groups fg on df.fieldtype = fg.id 
left join customer rf_customer on fv.value = cast(rf_customer.id as char(150)) 
left join tool rf_tool on fv.value = cast(rf_tool.id as char(150)) 
left join trans rf_trans on fv.value = cast(rf_trans.id as char(150)) 
left join product rf_product on fv.value = cast(rf_product.id as char(150)) 
left join project rf_project on fv.value = cast(rf_project.id as char(150)) 
left join employee rf_employee on fv.value = cast(rf_employee.id as char(150)) 
left join place rf_place on fv.value = cast(rf_place.id as char(150)) 
where fv.deleted = 0 and df.visible=1 and fv.ref_id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_customer_sheet_en') and dataset = 'fieldvalue';--

update ui_reportsources set sqlstr='select c.id as id, c.custnumber as custnumber, c.custname as custname, a.country as country, a.state as state, a.zipcode as zipcode, a.city as city, a.street as street, a.notes as notes 
from address a inner join customer c on a.ref_id = c.id 
where a.deleted=0 and c.deleted=0 and a.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') and c.id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_customer_sheet_en') and dataset = 'address';--

update ui_reportsources set sqlstr='select c.id as id, c.custnumber as custnumber, c.custname as custname, co.firstname as firstname, co.surname as surname, co.status as status, co.phone as phone, co.fax as fax, co.mobil as mobil, co.email as email, co.notes as cont_notes 
from contact co inner join customer c on co.ref_id = c.id 
where co.deleted=0 and c.deleted=0 and co.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') and c.id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_customer_sheet_en') and dataset = 'contact';--

update ui_reportsources set sqlstr='select c.id as id, c.custnumber as custnumber, c.custname as custname, g.groupvalue as groupvalue, g.description as description 
from customer c 
inner join link l on c.id = l.ref_id_1 and l.nervatype_1 = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') 
inner join groups g on l.ref_id_2 = g.id and l.nervatype_2 = (select id from groups where groupname=''nervatype'' and groupvalue=''groups'') 
where c.deleted = 0 and c.id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_customer_sheet_en') and dataset = 'groups';--

update ui_reportsources set sqlstr='select e.calnumber as calnumber, eg.groupvalue as eventgroup, 
  substr(cast(e.fromdate as char(10)), 1, 10) as fromdate, substr(cast(e.fromdate as char(16)), 12, 5) as fromtime, 
  substr(cast(e.todate as char(10)), 1, 10) as todate, substr(cast(e.todate as char(16)), 12, 5) as totime,
  e.subject as subject, e.place as place, e.description as description 
from event e 
left join groups eg on e.eventgroup = eg.id 
where e.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') and e.ref_id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_customer_sheet_en') and dataset = 'event';--

[engine mssql]update ui_reportsources set sqlstr='select e.calnumber as calnumber, eg.groupvalue as eventgroup, 
  CONVERT(VARCHAR(10), e.fromdate, 120) as fromdate, CONVERT(VARCHAR(5), e.fromdate, 108) as fromtime,
  CONVERT(VARCHAR(10), e.todate, 120) as todate, CONVERT(VARCHAR(5), e.todate, 108) as totime,
  e.subject as subject, e.place as place, e.description as description 
from event e 
left join groups eg on e.eventgroup = eg.id 
where e.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''customer'') and e.ref_id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_customer_sheet_en') and dataset = 'event';--

update ui_report set report = '<template>
  <report title="CUSTOMER DATASHEET" left-margin="15" top-margin="15" right-margin="15" decode="utf-8" encode="latin_1" />
  <header>
    <row height="10">
      <image file="={{labels.logo_file}}" link="={{labels.logo_link}}"/>
      <cell value="={{labels.lb_customer_datasheet}}" font-style="BI" font-size="26" color="14212058"/>
      <cell value="={{head.0.custnumber}}" align="R" font-style="B" font-size="20" />
    </row>
    <hline border-color="14212058"/>
    <vgap height="2"/>
  </header>
  <details>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="={{labels.lb_customer_no}}" font-style="B" background-color="14212058"/>
      <cell name="custnumber" value="={{head.0.custnumber}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_name}}" font-style="B" background-color="14212058"/>
      <cell name="custname" value="={{head.0.custname}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="={{labels.lb_customer_type}}" font-style="B" background-color="14212058"/>
      <cell name="custtype" value="={{head.0.custtype}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_taxnumber}}" font-style="B" background-color="14212058"/>
      <cell name="taxnumber" value="={{head.0.taxnumber}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="={{labels.lb_tax_free}}" font-style="B" background-color="14212058"/>
      <cell name="notax" value="={{head.0.notax}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_inactive}}" font-style="B" background-color="14212058"/>
      <cell name="inactive" value="={{head.0.inactive}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_account}}" font-style="B" background-color="14212058"/>
      <cell name="account" value="={{head.0.account}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="={{labels.lb_due_date}}" font-style="B" background-color="14212058"/>
      <cell name="terms" align="R" value="={{head.0.terms}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_discount}}(%)" font-style="B" background-color="14212058"/>
      <cell name="discount" align="R" value="={{head.0.discount}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_credit_limit}}" font-style="B" background-color="14212058"/>
      <cell name="creditlimit" align="R" value="={{head.0.creditlimit}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="={{labels.lb_comment}}" font-style="B" background-color="14212058"/>
      <cell name="notes" multiline="true" value="={{head.0.notes}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <hline border-color="14212058"/>
    <vgap height="2"/>
    <row visible="fieldvalue">
      <cell name="label" value="={{labels.lb_additional_data}}" align="C" font-style="B" background-color="14212058"/>
    </row>
    <datagrid name="fieldvalue" databind="fieldvalue" border="1" border-color="14212058">
      <header background-color="14212058"/>
      <columns>
        <column width="4%" fieldname="counter" align="R" label="={{labels.lb_no}}"/>
        <column width="25%" fieldname="fielddef" label="={{labels.lb_description}}"/>
        <column width="32%" fieldname="value" label="={{labels.lb_value}}"/>
        <column width="40%" fieldname="notes" label="={{labels.lb_comment}}"/>
      </columns>  
    </datagrid>
    <vgap height="5"/>
    <row visible="address">
      <cell name="label" value="={{labels.lb_address_details}}" align="C" font-style="B" background-color="14212058"/>
    </row>
    <datagrid name="address" databind="address" border="1" border-color="14212058">
      <header background-color="14212058"/>
      <columns>
        <column width="4%" fieldname="counter" align="R" label="={{labels.lb_no}}"/>
        <column width="10%" fieldname="zipcode" label="={{labels.lb_zipcode}}"/>
        <column width="20%" fieldname="city" label="={{labels.lb_city}}"/>
        <column width="27%" fieldname="street" label="={{labels.lb_street}}"/>
        <column width="40%" fieldname="notes" label="={{labels.lb_comment}}"/>
      </columns>  
    </datagrid>
    <vgap height="5"/>
    <row visible="contact">
      <cell name="label" value="Contact details" align="C" font-style="B" background-color="14212058"/>
    </row>
    <datagrid name="contact" databind="contact" border="1" border-color="14212058">
      <header background-color="14212058"/>
      <columns>
        <column width="4%" fieldname="counter" align="R" label="={{labels.lb_no}}"/>
        <column width="12%" fieldname="firstname" label="={{labels.lb_firstname}}"/>
        <column width="13%" fieldname="surname" label="={{labels.lb_surname}}"/>
        <column width="11%" fieldname="status" label="={{labels.lb_status}}"/>
        <column width="11%" fieldname="phone" label="={{labels.lb_phone}}"/>
        <column width="11%" fieldname="mobil" label="={{labels.lb_mobil}}"/>
        <column width="25%" fieldname="email" label="={{labels.lb_email}}"/>
        <column width="14%" fieldname="cont_notes" label="={{labels.lb_comment}}"/>
      </columns>  
    </datagrid>
    <vgap height="5"/>
    <row visible="event">
      <cell name="label" value="={{labels.lb_events}}" align="C" font-style="B" background-color="14212058"/>
    </row>
    <datagrid name="event" databind="event" border="1" border-color="14212058">
      <header background-color="14212058"/>
      <columns>
        <column width="4%" fieldname="counter" align="R" label="={{labels.lb_no}}"/>
        <column width="20%" fieldname="calnumber" label="={{labels.lb_event_no}}"/>
        <column width="13%" fieldname="eventgroup" label="={{labels.lb_group}}"/>
        <column width="13%" align="C" fieldname="fromdate" label="={{labels.lb_fromdate}}"/>
        <column width="13%" align="C" fieldname="todate" label="={{labels.lb_todate}}"/>
        <column width="19%" fieldname="subject" label="={{labels.lb_subject}}"/>
        <column width="19%" fieldname="place" label="={{labels.lb_place}}"/>
      </columns>  
    </datagrid>
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
where reportkey = 'fpdf_customer_sheet_en';--
