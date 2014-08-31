INSERT INTO ui_report(reportkey, nervatype, transtype, direction, repname, description, filetype, report)
    VALUES ('fpdf_employee_sheet_en', (select id from groups where groupname='nervatype' and groupvalue='employee'), 
      null, null, 'Employee Sheet', 'Employee Information Sheet', (select id from groups where groupname='filetype' and groupvalue='fpdf'), null);--

INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
    VALUES ((select id from ui_report where reportkey='fpdf_employee_sheet_en'), 'head', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
    VALUES ((select id from ui_report where reportkey='fpdf_employee_sheet_en'), 'fieldvalue', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
    VALUES ((select id from ui_report where reportkey='fpdf_employee_sheet_en'), 'address', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
    VALUES ((select id from ui_report where reportkey='fpdf_employee_sheet_en'), 'contact', '');--
INSERT INTO ui_reportsources(report_id, dataset, sqlstr)
    VALUES ((select id from ui_report where reportkey='fpdf_employee_sheet_en'), 'event', '');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_head', 'lb_yes', 'YES');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_head', 'lb_no', 'NO');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_fieldvalue', 'lb_yes', 'YES');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_fieldvalue', 'lb_no', 'NO');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'logo_file', 'icon24_ntura_white.png');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'logo_link', 'http://www.nervatura.com');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'web_page', 'www.nervatura.com');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'web_link', 'http://nervatura.com');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_employee_datasheet', 'EMPLOYEE DATASHEET');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_employee_no', 'Employee No.');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_firstname', 'Firstname');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_surname', 'Surname');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_status', 'Status');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_phone', 'Phone');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_mobil', 'Mobil');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_email', 'Email');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_start_date', 'Start Date');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_end_date', 'End Date');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_zipcode', 'Zipcode');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_city', 'City');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_street', 'Street');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_inactive', 'Inactive');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_usergroup', 'Usergroup');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_department', 'Department');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_username', 'Username');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_comment', 'Comment');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_additional_data', 'Additional data');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_no', 'No.');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_description', 'Description');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_value', 'Value');--

INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_events', 'Events');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_event_no', 'Event No.');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_group', 'Group');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_fromdate', 'Date From');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_todate', 'Date To');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_subject', 'Subject');--
INSERT INTO ui_message(secname, fieldname,  msg) 
VALUES ('fpdf_employee_sheet_en_report', 'lb_place', 'Place');--

update ui_reportsources set sqlstr='select e.id as id, e.empnumber as empnumber, e.username as username, ugroup.groupvalue as usergroup, e.startdate as startdate, e.enddate as enddate, dep.groupvalue as department,
  case when e.inactive=1 then ''={{lb_yes}}'' else ''={{lb_no}}'' end as inactive 
from employee e 
inner join groups as ugroup on e.usergroup=ugroup.id 
left join groups as dep on e.department=dep.id 
where e.deleted=0 and e.id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_employee_sheet_en') and dataset = 'head';--

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
inner join deffield df on fv.fieldname = df.fieldname and df.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''employee'') 
inner join groups fg on df.fieldtype = fg.id 
left join customer rf_customer on fv.value = cast(rf_customer.id as char(150)) 
left join tool rf_tool on fv.value = cast(rf_tool.id as char(150)) 
left join trans rf_trans on fv.value = cast(rf_trans.id as char(150)) 
left join product rf_product on fv.value = cast(rf_product.id as char(150)) 
left join project rf_project on fv.value = cast(rf_project.id as char(150)) 
left join employee rf_employee on fv.value = cast(rf_employee.id as char(150)) 
left join place rf_place on fv.value = cast(rf_place.id as char(150)) 
where fv.deleted = 0 and df.visible=1 and fv.ref_id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_employee_sheet_en') and dataset = 'fieldvalue';--

update ui_reportsources set sqlstr='select a.country as country, a.state as state, a.zipcode as zipcode, a.city as city, a.street as street, a.notes as notes 
from address a 
where a.deleted=0 and a.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''employee'') and a.ref_id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_employee_sheet_en') and dataset = 'address';--

update ui_reportsources set sqlstr='select co.firstname as firstname, co.surname as surname, co.status as status, co.phone as phone, co.fax as fax, co.mobil as mobil, co.email as email, co.notes as notes 
from contact co  
where co.deleted=0 and co.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''employee'') and co.ref_id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_employee_sheet_en') and dataset = 'contact';--

update ui_reportsources set sqlstr='select e.calnumber as calnumber, eg.groupvalue as eventgroup, 
  substr(cast(e.fromdate as char(10)), 1, 10) as fromdate, substr(cast(e.fromdate as char(16)), 12, 5) as fromtime, 
  substr(cast(e.todate as char(10)), 1, 10) as todate, substr(cast(e.todate as char(16)), 12, 5) as totime,
  e.subject as subject, e.place as place, e.description as description 
from event e 
left join groups eg on e.eventgroup = eg.id 
where e.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''employee'') and e.ref_id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_employee_sheet_en') and dataset = 'event';--

[engine mssql]update ui_reportsources set sqlstr='select e.calnumber as calnumber, eg.groupvalue as eventgroup, 
  CONVERT(VARCHAR(10), e.fromdate, 120) as fromdate, CONVERT(VARCHAR(5), e.fromdate, 108) as fromtime,
  CONVERT(VARCHAR(10), e.todate, 120) as todate, CONVERT(VARCHAR(5), e.todate, 108) as totime,
  e.subject as subject, e.place as place, e.description as description 
from event e 
left join groups eg on e.eventgroup = eg.id 
where e.deleted=0 and e.nervatype = (select id from groups where groupname=''nervatype'' and groupvalue=''employee'') and e.ref_id = @id '
where report_id = (select id from ui_report where reportkey='fpdf_employee_sheet_en') and dataset = 'event';--

update ui_report set report = '<template>
  <report title="EMPLOYEE DATASHEET" left-margin="15" top-margin="15" right-margin="15" decode="utf-8" encode="latin_1" />
  <header>
    <row height="10">
      <image file="={{labels.logo_file}}" link="={{labels.logo_link}}"/>
      <cell value="={{labels.lb_employee_datasheet}}" font-style="BI" font-size="26" color="14212058"/>
      <cell value="={{head.0.empnumber}}" align="R" font-style="B" font-size="20" />
    </row>
    <hline border-color="14212058"/>
    <vgap height="2"/>
  </header>
  <details>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="={{labels.lb_employee_no}}" font-style="B" background-color="14212058"/>
      <cell name="empnumber" value="={{head.0.empnumber}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_firstname}}" font-style="B" background-color="14212058"/>
      <cell name="firstname" value="={{contact.0.firstname}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_surname}}" font-style="B" background-color="14212058"/>
      <cell name="surname" value="={{contact.0.surname}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="={{labels.lb_status}}" font-style="B" background-color="14212058"/>
      <cell name="status" value="={{contact.0.status}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_phone}}" font-style="B" background-color="14212058"/>
      <cell name="phone" width="35" value="={{contact.0.phone}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_mobil}}" font-style="B" background-color="14212058"/>
      <cell name="mobil" value="={{contact.0.mobil}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="={{labels.lb_start_date}}" font-style="B" background-color="14212058"/>
      <cell name="startdate" value="={{head.0.startdate}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_end_date}}" font-style="B" background-color="14212058"/>
      <cell name="enddate" value="={{head.0.enddate}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_email}}" font-style="B" background-color="14212058"/>
      <cell name="email" value="={{contact.0.email}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <hline border-color="14212058"/>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="={{labels.lb_zipcode}}" font-style="B" background-color="14212058"/>
      <cell name="zipcode" value="={{address.0.zipcode}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_city}}" font-style="B" background-color="14212058"/>
      <cell name="city" value="={{address.0.city}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="={{labels.lb_street}}" font-style="B" background-color="14212058"/>
      <cell name="street" multiline="true" value="={{address.0.street}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <hline border-color="14212058"/>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="={{labels.lb_inactive}}" font-style="B" background-color="14212058"/>
      <cell name="inactive" value="={{head.0.inactive}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_usergroup}}" font-style="B" background-color="14212058"/>
      <cell name="usergroup" value="={{head.0.usergroup}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_department}}" font-style="B" background-color="14212058"/>
      <cell name="department" value="={{head.0.department}}" border="1" border-color="14212058"/>
      <cell name="label" value="={{labels.lb_username}}" font-style="B" background-color="14212058"/>
      <cell name="username" value="={{head.0.username}}" border="1" border-color="14212058"/>
    </row>
    <vgap height="2"/>
    <row hgap="2">
      <cell name="label" value="={{labels.lb_comment}}" font-style="B" background-color="14212058"/>
      <cell name="notes" multiline="true" value="={{contact.0.notes}}" border="1" border-color="14212058"/>
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
where reportkey = 'fpdf_employee_sheet_en';--


