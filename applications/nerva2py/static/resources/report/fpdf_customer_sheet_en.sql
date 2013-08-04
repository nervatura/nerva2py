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

update ui_reportsources set sqlstr='select c.id as id, c.custnumber as custnumber, c.custname as custname, ctype.groupvalue as custtype, c.taxnumber as taxnumber, c.account as account, 
  case when c.notax =1 then ''YES'' else ''NO'' end as notax, c.terms as terms, c.creditlimit as creditlimit,
  c.discount as discount, c.notes as notes,  case when c.inactive=1 then ''YES'' else ''NO'' end as inactive 
from customer c 
inner join groups as ctype on c.custtype=ctype.id 
where c.deleted=0 and c.id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_customer_sheet_en') and dataset = 'head';--

update ui_reportsources set sqlstr='select df.description as fielddef,
case when fg.groupvalue in (''bool'') and fv.value = ''true'' then ''YES''
        when fg.groupvalue in (''bool'') and fv.value = ''false'' then ''NO''
        when fg.groupvalue in (''customer'') then rf_customer.custnumber
        when fg.groupvalue in (''tool'') then rf_tool.serial
        when fg.groupvalue in (''trans'') then rf_trans.transnumber
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
      <image file="icon24_ntura_white.png" link="http://www.nervatura.com"/>
      <cell value="CUSTOMER DATASHEET" font-style="BI" font-size="26" color="14212058"/>
      <cell value="={{head.0.custnumber}}" align="R" font-style="B" />
    </row>
    <hline border-color="14212058"/>
    <vgap height="2"/>
  </header>
  <details>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="Customer No." font-style="B" background-color="14212058"/>
      <cell name="custnumber" value="={{head.0.custnumber}}" border="1" border-color="14212058"/>
      <cell name="label" value="Name" font-style="B" background-color="14212058"/>
      <cell name="custname" value="={{head.0.custname}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="Customer type" font-style="B" background-color="14212058"/>
      <cell name="custtype" value="={{head.0.custtype}}" border="1" border-color="14212058"/>
      <cell name="label" value="Taxnumber" font-style="B" background-color="14212058"/>
      <cell name="taxnumber" value="={{head.0.taxnumber}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="Tax free" font-style="B" background-color="14212058"/>
      <cell name="notax" value="={{head.0.notax}}" border="1" border-color="14212058"/>
      <cell name="label" value="Inactive" font-style="B" background-color="14212058"/>
      <cell name="inactive" value="={{head.0.inactive}}" border="1" border-color="14212058"/>
      <cell name="label" value="Account" font-style="B" background-color="14212058"/>
      <cell name="account" value="={{head.0.account}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="Due Date (day)" font-style="B" background-color="14212058"/>
      <cell name="terms" align="R" value="={{head.0.terms}}" border="1" border-color="14212058"/>
      <cell name="label" value="Discount(%)" font-style="B" background-color="14212058"/>
      <cell name="discount" align="R" value="={{head.0.discount}}" border="1" border-color="14212058"/>
      <cell name="label" value="Credit limit" font-style="B" background-color="14212058"/>
      <cell name="creditlimit" align="R" value="={{head.0.creditlimit}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="Notes" font-style="B" background-color="14212058"/>
      <cell name="notes" multiline="true" value="={{head.0.notes}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <hline border-color="14212058"/>
    <vgap height="2"/>
    <row>
      <cell name="label" value="Additional data" align="C" font-style="B" background-color="14212058"/>
    </row>
    <datagrid name="fieldvalue" databind="fieldvalue" border="1" border-color="14212058">
      <header background-color="14212058"/>
      <columns>
        <column width="4%" fieldname="counter" align="R" label="No."/>
        <column width="25%" fieldname="fielddef" label="Description"/>
        <column width="32%" fieldname="value" label="Value"/>
        <column width="40%" fieldname="notes" label="Comment"/>
      </columns>  
    </datagrid>
    <vgap height="5"/>
    <row>
      <cell name="label" value="Address details" align="C" font-style="B" background-color="14212058"/>
    </row>
    <datagrid name="address" databind="address" border="1" border-color="14212058">
      <header background-color="14212058"/>
      <columns>
        <column width="4%" fieldname="counter" align="R" label="No."/>
        <column width="10%" fieldname="zipcode" label="Zipcode"/>
        <column width="20%" fieldname="city" label="City"/>
        <column width="27%" fieldname="street" label="Street"/>
        <column width="40%" fieldname="notes" label="Notes"/>
      </columns>  
    </datagrid>
    <vgap height="5"/>
    <row>
      <cell name="label" value="Contact details" align="C" font-style="B" background-color="14212058"/>
    </row>
    <datagrid name="contact" databind="contact" border="1" border-color="14212058">
      <header background-color="14212058"/>
      <columns>
        <column width="4%" fieldname="counter" align="R" label="No."/>
        <column width="12%" fieldname="firstname" label="Firstname"/>
        <column width="13%" fieldname="surname" label="Surname"/>
        <column width="11%" fieldname="status" label="Status"/>
        <column width="11%" fieldname="phone" label="Phone"/>
        <column width="11%" fieldname="mobil" label="Mobil"/>
        <column width="25%" fieldname="email" label="Email"/>
        <column width="14%" fieldname="cont_notes" label="Notes"/>
      </columns>  
    </datagrid>
    <vgap height="5"/>
    <row>
      <cell name="label" value="Events" align="C" font-style="B" background-color="14212058"/>
    </row>
    <datagrid name="event" databind="event" border="1" border-color="14212058">
      <header background-color="14212058"/>
      <columns>
        <column width="4%" fieldname="counter" align="R" label="No."/>
        <column width="20%" fieldname="calnumber" label="Event No."/>
        <column width="13%" fieldname="eventgroup" label="Group"/>
        <column width="13%" align="C" fieldname="fromdate" label="Date From"/>
        <column width="13%" align="C" fieldname="todate" label="Date To"/>
        <column width="19%" fieldname="subject" label="Subject"/>
        <column width="19%" fieldname="place" label="Place"/>
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
</template>'
where reportkey = 'fpdf_customer_sheet_en';--
