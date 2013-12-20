# -*- coding: utf-8 -*-

"""
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2013, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
"""
  
def insert_nflex_rows(db):
  nflex = db.nflex

#--------------------------------------------------
# fMain
#--------------------------------------------------
  nflex.insert(sqlkey = 'fMain_setPassword', engine = 'all', section = 'fMain', 
  sqlstr = 'update employee set password=@password where username=@username;')


#--------------------------------------------------
# fSetting
#--------------------------------------------------
  nflex.insert(sqlkey = 'fSetting_getDeffieldProp', engine = 'all', section = 'fSetting', 
  sqlstr = 'select \'customer_\'||c.id as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'||t.id as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'||p.id as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'||p.id as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'||e.id as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'||p.id as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))' )
  
  nflex.insert(sqlkey = 'fSetting_getDeffieldProp', engine = 'mysql', section = 'fSetting', 
  sqlstr = 'select CONCAT(\'customer_\',cast(c.id as char)) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select CONCAT(\'tool_\',cast(t.id as char)) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select CONCAT(\'trans_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select CONCAT(\'transitem_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select CONCAT(\'transmovement_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select CONCAT(\'transpayment_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select CONCAT(\'product_\',cast(p.id as char)) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select CONCAT(\'project_\',cast(p.id as char)) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select CONCAT(\'employee_\',cast(e.id as char)) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select CONCAT(\'place_\',cast(p.id as char)) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))' )
  
  nflex.insert(sqlkey = 'fSetting_getDeffieldProp', engine = 'mssql', section = 'fSetting', 
  sqlstr = 'select \'customer_\'+cast(c.id as varchar) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'+cast(t.id as varchar) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'+cast(p.id as varchar) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'+cast(p.id as varchar) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'+cast(e.id as varchar) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'+cast(p.id as varchar) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname  \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'setting\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))' )
  
  nflex.insert(sqlkey = 'fSettings_getEnabled_currency', engine = 'all', section = 'fSettings', 
  sqlstr = 'select c.curr, case when sct.ct is not null then cast(0 as boolean) \
    else case when pct.ct is not null then cast(0 as boolean) \
      else case when rct.ct is not null then cast(0 as boolean) \
        else cast(1 as boolean) end \
      end \
    end as enabled \
  from currency c \
  left join (select distinct curr as ct from trans) sct on curr = sct.ct \
  left join (select distinct curr as ct from place) pct on curr = pct.ct \
  left join (select distinct curr as ct from rate) rct on curr = rct.ct')
  
  nflex.insert(sqlkey = 'fSettings_getEnabled_currency', engine = 'mysql', section = 'fSettings', 
  sqlstr = 'select c.curr, case when sct.ct is not null then false \
    else case when pct.ct is not null then false \
      else case when rct.ct is not null then false \
        else true end \
      end \
    end as enabled \
  from currency c \
  left join (select distinct curr as ct from trans) sct on curr = sct.ct \
  left join (select distinct curr as ct from place) pct on curr = pct.ct \
  left join (select distinct curr as ct from rate) rct on curr = rct.ct')
  
  nflex.insert(sqlkey = 'fSettings_getEnabled_currency', engine = 'mssql', section = 'fSettings', 
  sqlstr = 'select c.curr, case when sct.ct is not null then cast(0 as bit) \
    else case when pct.ct is not null then cast(0 as bit) \
      else case when rct.ct is not null then cast(0 as bit) \
        else cast(1 as bit) end \
      end \
    end as enabled \
  from currency c \
  left join (select distinct curr as ct from trans) sct on curr = sct.ct \
  left join (select distinct curr as ct from place) pct on curr = pct.ct \
  left join (select distinct curr as ct from rate) rct on curr = rct.ct')
  
  nflex.insert(sqlkey = 'fRate_getGroupsLang', engine = 'all', section = 'fSettings', 
  sqlstr = 'select g.id, g.groupvalue, ms.msg as langvalue from groups g \
  left join ui_message ms on ms.secname = g.groupname and ms.fieldname = g.groupvalue  \
  and ms.lang = (select value from fieldvalue where fieldname = \'default_lang\') \
  where g.groupname in (\'ratetype\');')
  
  nflex.insert(sqlkey = 'dbsFunctions_getPriceValue_1', engine = 'all', section = 'dbsFunctions', 
  sqlstr = "select :row_id as row_id, p.*, 0 as fxprice, 0 as discount, 0 as actionprice, :qty as qty, \
      (select max(fv.notes) from fieldvalue fv where ref_id = p.id and fieldname = 'product_custpartnumber' and \
        cast(fv.value as integer) = :customer_id) as partscustomer \
      from product p where id in (@product_id)")

  nflex.insert(sqlkey = 'dbsFunctions_getPriceValue_1', engine = 'mysql', section = 'dbsFunctions', 
  sqlstr = "select :row_id as row_id, p.*, 0 as fxprice, 0 as discount, 0 as actionprice, :qty as qty, \
      (select max(fv.notes) from fieldvalue fv where ref_id = p.id and fieldname = 'product_custpartnumber' and \
        cast(fv.value as signed) = :customer_id) as partscustomer \
      from product p where id in (@product_id)")

  nflex.insert(sqlkey = 'dbsFunctions_getPriceValue_2', engine = 'all', section = 'dbsFunctions', 
  sqlstr = "select min(pr.pricevalue) as pricevalue from price pr \
        left join link ln0 on ln0.nervatype_1 = (select id from groups where groupname='nervatype' and groupvalue='price') and ln0.ref_id_1 = pr.id \
          and ln0.nervatype_2 = (select id from groups where groupname='nervatype' and groupvalue='customer') and ln0.ref_id_2 = :customer_id \
        left join link ln1 on ln1.nervatype_1 = (select id from groups where groupname='nervatype' and groupvalue='price') and ln1.ref_id_1 = pr.id \
          and ln1.nervatype_2 = (select id from groups where groupname='nervatype' and groupvalue='groups') \
        left join groups gc on ln1.ref_id_2 = gc.id and gc.deleted=0 and gc.id in(select l.ref_id_2 as groups_id from link l \
          where l.nervatype_1 = (select id from groups where groupname='nervatype' and groupvalue='customer') \
          and l.nervatype_2 = (select id from groups where groupname='nervatype' and groupvalue='groups') \
          and l.deleted=0 and l.ref_id_1 = :customer_id) \
        where pr.deleted = 0 and pr.discount is null and pr.vendorprice = :vendorprice and pr.pricevalue<>0 and pr.product_id = :product_id \
        and pr.validfrom <= :posdate and (pr.validto>= :posdate or pr.validto is null) and pr.curr = :curr and pr.qty <= :qty")

  nflex.insert(sqlkey = 'dbsFunctions_getPriceValue_3', engine = 'all', section = 'dbsFunctions', 
  sqlstr = "select gca.groupvalue as calcmode, pr.discount, pr.pricevalue as lmt from price pr \
          inner join groups gca on pr.calcmode = gca.id \
          left join link ln0 on ln0.nervatype_1 = (select id from groups where groupname='nervatype' and groupvalue='price') and ln0.ref_id_1 = pr.id \
            and ln0.nervatype_2 = (select id from groups where groupname='nervatype' and groupvalue='customer') and ln0.ref_id_2 = :customer_id \
          left join link ln1 on ln1.nervatype_1 = (select id from groups where groupname='nervatype' and groupvalue='price') and ln1.ref_id_1 = pr.id \
            and ln1.nervatype_2 = (select id from groups where groupname='nervatype' and groupvalue='groups') \
          left join groups gc on ln1.ref_id_2 = gc.id and gc.deleted=0 and gc.id in(select l.ref_id_2 as groups_id from link l \
            where l.nervatype_1 = (select id from groups where groupname='nervatype' and groupvalue='customer') \
            and l.nervatype_2 = (select id from groups where groupname='nervatype' and groupvalue='groups') \
            and l.deleted=0 and l.ref_id_1 = :customer_id) \
          where pr.deleted = 0 and pr.discount is not null and pr.vendorprice = :vendorprice and pr.product_id = :product_id \
          and pr.validfrom <= :posdate and (pr.validto>= :posdate or pr.validto is null) and pr.curr = :curr and pr.qty <= :qty")
  
#--------------------------------------------------
# fDeffield
#--------------------------------------------------
  nflex.insert(sqlkey = 'fDeffield_getGroupsLang', engine = 'all', section = 'fDeffield', 
  sqlstr = 'select g.id, g.groupvalue, case when ms.msg is null then g.groupvalue else ms.msg end as langvalue from groups g \
  left join ui_message ms on ms.secname = g.groupname and ms.fieldname = g.groupvalue \
  and ms.lang = (select value from fieldvalue where fieldname = \'default_lang\') \
  where g.groupname in (\'fieldtype\', \'transtype\', \'placetype\');')
  
#--------------------------------------------------
# fGroups
#--------------------------------------------------
  nflex.insert(sqlkey = 'fGroups_getPrintqueueProp', engine = 'all', section = 'fGroups', 
  sqlstr = 'select pq.id, ntg.groupvalue as typename, \
    case when ntg.groupvalue=\'trans\' then \
    case when mst.msg is null then tg.groupvalue else mst.msg end \
    else case when msg.msg is null then ntg.groupvalue else msg.msg end end as stypename, \
    case when ntg.groupvalue=\'trans\' then tg.groupvalue else null end as transtype, \
    case when ntg.groupvalue in (\'customer\') then rf_customer.custnumber \
          when ntg.groupvalue in (\'tool\') then rf_tool.serial \
          when ntg.groupvalue in (\'trans\', \'transitem\', \'transmovement\', \'transpayment\') then rf_trans.transnumber \
          when ntg.groupvalue in (\'product\') then rf_product.partnumber \
          when ntg.groupvalue in (\'project\') then rf_project.pronumber \
          when ntg.groupvalue in (\'employee\') then rf_employee.empnumber \
          when ntg.groupvalue in (\'place\') then rf_place.planumber \
          else null end as refnumber, \
    case when ntg.groupvalue=\'trans\' then dg.groupvalue else null end as direction, \
    e.empnumber, r.repname \
  from ui_printqueue pq \
  inner join groups ntg on pq.nervatype = ntg.id \
    left join ui_message msg on msg.fieldname = ntg.groupvalue and  msg.secname = \'nervatype\' and msg.lang = (select value from fieldvalue where fieldname = \'default_lang\') \
  left join customer rf_customer on pq.ref_id = rf_customer.id \
  left join tool rf_tool on pq.ref_id = rf_tool.id \
  left join trans rf_trans on pq.ref_id = rf_trans.id \
    left join groups dg on rf_trans.direction = dg.id \
    left join groups tg on rf_trans.transtype = tg.id \
    left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = \'transtype\' and mst.lang = (select value from fieldvalue where fieldname = \'default_lang\') \
  left join product rf_product on pq.ref_id = rf_product.id \
  left join project rf_project on pq.ref_id = rf_project.id \
  left join employee rf_employee on pq.ref_id = rf_employee.id \
  left join place rf_place on pq.ref_id = rf_place.id \
  inner join employee e on pq.employee_id = e.id \
  left join ui_report r on pq.report_id = r.id \
  where 1=1 @where_str')
  
  nflex.insert(sqlkey = 'fGroups_getEnabled_eventgroup', engine = 'all', section = 'fGroups', 
  sqlstr = 'select g.id, case when scg.cg is not null then 0 else 1 end as enabled \
  from groups g  \
  left join (select distinct eventgroup as cg from event) scg on id = scg.cg \
  where groupname=@groupname')
  
  nflex.insert(sqlkey = 'fGroups_getEnabled_rategroup', engine = 'all', section = 'fGroups', 
  sqlstr = 'select g.id, case when scg.cg is not null then 0 else 1 end as enabled \
  from groups g  \
  left join (select distinct rategroup as cg from rate) scg on id = scg.cg \
  where groupname=@groupname')
  
  nflex.insert(sqlkey = 'fGroups_getEnabled_toolgroup', engine = 'all', section = 'fGroups', 
  sqlstr = 'select g.id, case when scg.cg is not null then 0 else 1 end as enabled \
  from groups g  \
  left join (select distinct toolgroup as cg from tool) scg on id = scg.cg \
  where groupname=@groupname')
  
  nflex.insert(sqlkey = 'fGroups_getEnabled_link', engine = 'all', section = 'fGroups', 
  sqlstr = 'select g.id, case when scg2.cg is not null then 0 else \
    case when scg1.cg is not null then 0 else 1 end  \
    end as enabled \
  from groups g  \
  left join (select distinct ref_id_2 as cg from link where nervatype_2 = (select id from groups where groupname = \'nervatype\'  \
    and groupvalue = \'groups\')) scg2 on id = scg2.cg \
  left join (select distinct ref_id_1 as cg from link where nervatype_1 = (select id from groups where groupname = \'nervatype\'  \
    and groupvalue = \'groups\')) scg1 on id = scg1.cg \
  where groupname=@groupname')
  
  nflex.insert(sqlkey = 'fGroups_getEnabled_usergroup', engine = 'all', section = 'fGroups', 
  sqlstr = 'select g.id, case when scg.cg is not null then 0 else 1 end as enabled \
  from groups g  \
  left join (select distinct usergroup as cg from employee) scg on id = scg.cg \
  where groupname=@groupname')
  
  nflex.insert(sqlkey = 'fGroups_getGroupsLang_usergroup', engine = 'all', section = 'fGroups', 
  sqlstr = 'select g.id, g.groupvalue, case when ms.msg is null then g.groupvalue else ms.msg end as langvalue from groups g \
  left join ui_message ms on ms.secname = g.groupname and ms.fieldname = g.groupvalue  \
  and ms.lang = (select value from fieldvalue where fieldname = \'default_lang\') \
  where g.groupname in (\'nervatype\', \'transtype\', \'inputfilter\', \'transfilter\');')
  
  nflex.insert(sqlkey = 'fGroups_getReports', engine = 'all', section = 'fGroups', 
              sqlstr = 'select id, repname from ui_report order by repname;')
  
  nflex.insert(sqlkey = 'fGroups_getReports2', engine = 'all', section = 'fGroups', 
  sqlstr = 'select r.id, r.repname, r.description \
  ,  case when gi.groups_id is null then 0 else 1 end as usereports \
  , nt.groupvalue as nervatype, tt.groupvalue as transtype, dg.groupvalue as direction \
  from ui_report r \
  inner join groups fg on r.filetype = fg.id \
  inner join groups nt on r.nervatype = nt.id \
  left join groups tt on r.transtype = tt.id \
  left join groups dg on r.direction = dg.id \
  left join ui_groupinput gi on gi.groups_id = @usergroup \
    and gi.formname = r.reportkey and gi.contname = r.reportkey \
  where fg.groupvalue in(@filetype) and r.repname is not null \
  order by r.repname;')

#--------------------------------------------------
# dsReports
#--------------------------------------------------
  nflex.insert(sqlkey = 'dsReports_getReportFields', engine = 'all', section = 'dsReports', 
  sqlstr = 'select rf.report_id, rf.fieldname, fg.groupvalue as fieldtype, wg.groupvalue as wheretype, rf.description, rf.orderby, rf.sqlstr, \
    rf.parameter, rf.dataset, rf.defvalue, rf.valuelist \
    from ui_reportfields rf \
    inner join groups fg on rf.fieldtype = fg.id \
    inner join groups wg on rf.wheretype = wg.id \
    inner join ui_report r on rf.report_id = r.id \
    inner join groups ffg on r.filetype = ffg.id and ffg.groupvalue in(@filetype) \
    where r.nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=@nervatype) \
      and r.repname is not null @where_str')
  
  nflex.insert(sqlkey = 'dsReports_getReports', engine = 'all', section = 'dsReports', 
  sqlstr = "select r.id, r.reportkey, r.repname, r.description, r.label, fg.groupvalue as filetype, \
    case when ig.groupvalue='disabled' then 0 else 1 end as usereports, r.nervatype \
    from ui_report r inner join groups fg on r.filetype = fg.id \
    left join ui_audit au on r.id = au.subtype and au.usergroup = @usergroup \
    and au.nervatype = (select id from groups where groupname='nervatype' and groupvalue='report') \
    left join groups ig on au.inputfilter = ig.id \
    where r.nervatype = (select id from groups where groupname='nervatype' and groupvalue=@nervatype) \
       and fg.groupvalue in(@filetype) and r.repname is not null @where_str order by r.repname;")
  
  nflex.insert(sqlkey = 'dsReports_getReportsFile', engine = 'all', section = 'dsReports', sqlstr = 'select report from ui_report where id=@id')
  
  nflex.insert(sqlkey = 'dsReports_getReportsSources', engine = 'all', section = 'dsReports', 
  sqlstr = 'select rs.* from ui_reportsources rs \
    inner join ui_report r on rs.report_id = r.id \
    inner join groups ffg on r.filetype = ffg.id and ffg.groupvalue in(@filetype) \
    where r.nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=@nervatype) \
      and r.repname is not null @where_str')
  
  nflex.insert(sqlkey = 'dsReports_insertPrintQueue', engine = 'all', section = 'dsReports', 
  sqlstr = 'insert into ui_printqueue(nervatype, ref_id, qty, employee_id, report_id, crdate) \
    values(@nervatype, @ref_id, @qty, @employee_id, @reports_id,  @crdate);')
  
#--------------------------------------------------
# fBrowser
#--------------------------------------------------
  nflex.insert(sqlkey = 'fBrowser_getApplViews', engine = 'all', section = 'fBrowser', 
  sqlstr = 'select v.*, m.msg as langname from ui_applview v \
    inner join ui_message m on m.secname=\'view\' and m.fieldname=v.viewname and lang=@lang \
    where parentview=@parent @where_str order by v.orderby;')
  
  nflex.insert(sqlkey = 'fBrowser_getViewFields', engine = 'all', section = 'fBrowser', 
  sqlstr = 'select f.viewname, f.fieldname, fg.groupvalue as fieldtype, wg.groupvalue as  wheretype, f.orderby, \
    f.sqlstr, ag.groupvalue as aggretype, m.msg as langname from ui_viewfields f \
    inner join ui_applview vp on f.viewname=vp.viewname \
    inner join groups fg on f.fieldtype = fg.id \
    inner join groups wg on f.wheretype = wg.id \
    inner join groups ag on f.aggretype = ag.id \
    left join ui_message m on m.secname=f.viewname and m.fieldname=f.fieldname and lang=@lang \
    where parentview=@parent order by f.orderby;')

#--------------------------------------------------
# fPlace
#--------------------------------------------------
  nflex.insert(sqlkey = 'fPlace_getGroupsLang', engine = 'all', section = 'fPlace', 
  sqlstr = 'select g.id, g.groupvalue, ms.msg as langvalue from groups g \
  left join ui_message ms on ms.secname = g.groupname and ms.fieldname = g.groupvalue  \
  and ms.lang = (select value from fieldvalue where fieldname = \'default_lang\') \
  where g.groupname in (\'placetype\');')
  
  nflex.insert(sqlkey = 'fPlace_getDeffieldProp', engine = 'all', section = 'fPlace', 
  sqlstr = 'select \'customer_\'||c.id as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'||t.id as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'||p.id as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'||p.id as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'||e.id as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'||p.id as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fPlace_getDeffieldProp', engine = 'mysql', section = 'fPlace', 
  sqlstr = 'select CONCAT(\'customer_\',cast(c.id as char)) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select CONCAT(\'tool_\',cast(t.id as char)) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select CONCAT(\'trans_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select CONCAT(\'transitem_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select CONCAT(\'transmovement_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select CONCAT(\'transpayment_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select CONCAT(\'product_\',cast(p.id as char)) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select CONCAT(\'project_\',cast(p.id as char)) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select CONCAT(\'employee_\',cast(e.id as char)) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select CONCAT(\'place_\',cast(p.id as char)) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fPlace_getDeffieldProp', engine = 'mssql', section = 'fPlace', 
  sqlstr = 'select \'customer_\'+cast(c.id as varchar) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'+cast(t.id as varchar) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'+cast(p.id as varchar) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'+cast(p.id as varchar) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'+cast(e.id as varchar) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'+cast(p.id as varchar) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @place_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'place\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fPlace_getDeleteState', engine = 'all', section = 'fPlace', 
  sqlstr = 'select cast(sum(co) as integer) as sco \
  from (select count(*) as co from trans where place_id=@place_id \
  union select count(*) as co from place where place_id=@place_id \
  union select count(*) as co from rate where place_id=@place_id \
  union select count(*) as co from movement where place_id=@place_id \
  union select count(*) as co from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'place\')  \
    and ref_id_2=@place_id \
  union select count(*) as co from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))  \
    and value = cast(@place_id as text)) foo')
  
  nflex.insert(sqlkey = 'fPlace_getDeleteSql_update', engine = 'all', section = 'fPlace', sqlstr = 'update place set deleted = 1 where id=@place_id;')
  
  nflex.insert(sqlkey = 'fPlace_getDeleteSql_delete', engine = 'all', section = 'fPlace', 
  sqlstr = 'delete from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'place\')  \
    and ref_id_2=@place_id \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))  \
    and value = cast(@place_id as text) \
    delete from place where id=@place_id ')

#--------------------------------------------------
# fFilter
#--------------------------------------------------
  nflex.insert(sqlkey = 'CustomerFilter_getResult', engine = 'all', section = 'fFilter', 
  sqlstr = 'select c.id, c.custnumber, c.custname,  \
  case when a.city is null then \'\' else a.city end ||\' \'|| case when a.street is null then \'\' else a.street end as address, \
    c.taxnumber, c.terms, c.discount, c.notax  \
  from customer c \
  left join (select * from address \
    where id in(select min(id) fid from address a \
      where a.deleted=0 and a.nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\') \
      group by a.ref_id)) a on c.id = a.ref_id \
  where c.deleted=0 and c.id>1 @where_str order by c.custname')
  
  nflex.insert(sqlkey = 'CustomerFilter_getResult', engine = 'mysql', section = 'fFilter', 
  sqlstr = 'select c.id, c.custnumber, c.custname,  \
  CONCAT(case when a.city is null then \'\' else a.city end, \' \', case when a.street is null then \'\' else a.street end) as address, \
    c.taxnumber, c.terms, c.discount, c.notax  \
  from customer c \
  left join (select * from address \
    where id in(select min(id) fid from address a \
      where a.deleted=0 and a.nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\') \
      group by a.ref_id)) a on c.id = a.ref_id \
  where c.deleted=0 and c.id>1 @where_str order by c.custname')
  
  nflex.insert(sqlkey = 'CustomerFilter_getResult', engine = 'mssql', section = 'fFilter', 
  sqlstr = 'select c.id, c.custnumber, c.custname,  \
  case when a.city is null then \'\' else a.city end +\' \'+ case when a.street is null then \'\' else a.street end as address, \
    c.taxnumber, c.terms, c.discount, c.notax  \
  from customer c \
  left join (select * from address \
    where id in(select min(id) fid from address a \
      where a.deleted=0 and a.nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\') \
      group by a.ref_id)) a on c.id = a.ref_id \
  where c.deleted=0 and c.id>1 @where_str order by c.custname')
  
  nflex.insert(sqlkey = 'PlaceFilter_getResult', engine = 'all', section = 'fFilter', 
  sqlstr = 'select p.id, p.planumber, case when mst.msg is null then tg.groupvalue else mst.msg end as placetype, p.description \
  from place p inner join groups tg on p.placetype = tg.id \
    left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = \'placetype\' \
    and mst.lang = (select value from fieldvalue where fieldname = \'default_lang\') \
  where p.deleted = 0 and tg.groupvalue<>\'store\' @where_str order by p.description')
  
  nflex.insert(sqlkey = 'EmployeeFilter_getResult', engine = 'all', section = 'fFilter', 
  sqlstr = 'select e.id, e.empnumber, c.firstname, c.surname, e.username, ug.groupvalue as usergroup, dg.groupvalue as department \
  from employee e \
  left join contact c on e.id = c.ref_id and c.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
  inner join groups ug on e.usergroup = ug.id \
  left join groups dg on e.department = dg.id \
  where e.deleted=0 @where_str')
  
  nflex.insert(sqlkey = 'ToolFilter_getResult', engine = 'all', section = 'fFilter', 
  sqlstr = 'select t.id, t.serial, t.description, tg.groupvalue as tgroup, case when ssel.state is null then \'***************\' else ssel.state end  as state \
  from tool t left join groups tg on t.toolgroup = tg.id \
  left join (select mv.tool_id,  case when t.direction = (select id from groups where groupname = \'direction\' and groupvalue = \'in\') then (select custname from customer where id=1) \
    when c.custname is not null then c.custname \
    when e.empnumber is not null then e.empnumber \
    else ltc.custname end as state \
  from movement mv inner join trans t on mv.trans_id=t.id \
  left join customer c on t.customer_id=c.id left join employee e on t.employee_id=e.id \
  left join link lnk on t.id = lnk.ref_id_1 and lnk.deleted=0 and lnk.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
       and lnk.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
       left join trans lt on lnk.ref_id_2 = lt.id left join customer ltc on lt.customer_id=ltc.id \
  where mv.id in(select max(id) from movement mv \
    inner join (select tool_id, max(shippingdate) as ldate from movement mv \
      inner join trans t on mv.trans_id=t.id \
      where mv.deleted=0 and tool_id is not null and t.deleted=0 and cast(shippingdate as date) <= current_date \
      group by tool_id) lst_date on mv.tool_id=lst_date.tool_id and mv.shippingdate=lst_date.ldate group by mv.tool_id)) ssel on t.id = ssel.tool_id \
  where t.deleted = 0 @where_str')
  
  nflex.insert(sqlkey = 'ToolFilter_getResult', engine = 'mssql', section = 'fFilter', 
  sqlstr = 'select t.id, t.serial, t.description, tg.groupvalue as tgroup, case when ssel.state is null then \'***************\' else ssel.state end  as state \
  from tool t left join groups tg on t.toolgroup = tg.id \
  left join (select mv.tool_id,  case when t.direction = (select id from groups where groupname = \'direction\' and groupvalue = \'in\') then (select custname from customer where id=1) \
    when c.custname is not null then c.custname \
    when e.empnumber is not null then e.empnumber \
    else ltc.custname end as state \
  from movement mv inner join trans t on mv.trans_id=t.id \
  left join customer c on t.customer_id=c.id left join employee e on t.employee_id=e.id \
  left join link lnk on t.id = lnk.ref_id_1 and lnk.deleted=0 and lnk.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
       and lnk.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
       left join trans lt on lnk.ref_id_2 = lt.id left join customer ltc on lt.customer_id=ltc.id \
  where mv.id in(select max(id) from movement mv \
    inner join (select tool_id, max(shippingdate) as ldate from movement mv \
      inner join trans t on mv.trans_id=t.id \
      where mv.deleted=0 and tool_id is not null and t.deleted=0 and cast(shippingdate as date) <= cast(GETDATE() as DATE) \
      group by tool_id) lst_date on mv.tool_id=lst_date.tool_id and mv.shippingdate=lst_date.ldate group by mv.tool_id)) ssel on t.id = ssel.tool_id \
  where t.deleted = 0 @where_str')
  
  nflex.insert(sqlkey = 'MovementFilter_getResult', engine = 'all', section = 'fFilter', 
  sqlstr = 'select t.id, t.transnumber, tg.groupvalue as transtype, dg.groupvalue as direction, t.transdate \
  from trans t \
  inner join groups tg on tg.id=t.transtype and tg.groupvalue in(\'delivery\',\'inventory\',\'waybill\') \
  inner join groups dg on dg.id=t.direction \
  where t.deleted=0 @where_str')
  
  nflex.insert(sqlkey = 'PaymentFilter_getResult', engine = 'all', section = 'fFilter', 
  sqlstr = 'select t.id, 0 as selected, tg.groupvalue as transtype, dg.groupvalue as direction, t.transnumber, i.paiddate, p.description as place, p.curr,  \
    case when dg.groupvalue=\'out\' then -i.amount else i.amount end as amount \
  from trans t \
  inner join groups tg on t.transtype = tg.id \
  inner join groups dg on t.direction = dg.id \
  inner join place p on t.place_id = p.id \
  inner join payment i on t.id = i.trans_id and i.deleted=0 \
  where (t.deleted=0 or tg.groupvalue=\'cash\') @where_str \
  order by t.transdate;')
  
  nflex.insert(sqlkey = 'ProductFilter_getResult', engine = 'all', section = 'fFilter', 
  sqlstr = 'select p.id, 0 as selected, p.partnumber, p.description, p.unit, p.tax_id \
    ,case when trkeszl.qty is null then 0 else trkeszl.qty end as i2qty \
    ,case when szkeszl.qty is null then 0 else -szkeszl.qty end as i3qty  \
  from product p \
  left join (select i.product_id, sum(qty) as qty  \
    from item i \
    inner join trans t on i.trans_id = i.id and t.deleted = 0 \
    inner join groups g on t.transtype = g.id and g.groupvalue in (\'inv_ct\', \'inv_vd\', \'ivt_iv\') \
    inner join product p on i.product_id = p.id and p.deleted = 0 \
    inner join groups pg on p.protype = pg.id and pg.groupvalue = \'item\' \
    where i.deleted = 0 and i.deposit = 0 \
    group by i.product_id) as szkeszl on p.id = szkeszl.product_id \
  left join ( \
    select m.product_id, sum(qty) as qty  \
    from movement m \
    inner join groups g on m.movetype = g.id and g.groupvalue = \'inventory\' \
    inner join product p on m.product_id = p.id and p.deleted = 0 \
    inner join groups pg on p.protype = pg.id and pg.groupvalue = \'item\' \
    where m.deleted = 0 \
    group by m.product_id) as trkeszl on p.id = trkeszl.product_id \
  where p.deleted = 0 @where_str order by p.partnumber;')
  
  nflex.insert(sqlkey = 'ProjectFilter_getResult', engine = 'all', section = 'fFilter', 
  sqlstr = 'select p.id, p.pronumber, p.description, p.startdate, p.enddate, c.custname \
  from project p \
  left join customer c on p.customer_id = c.id \
  where p.deleted=0 @where_str \
  order by p.pronumber;')
  
  nflex.insert(sqlkey = 'TransItemFilter_getResult', engine = 'all', section = 'fFilter', 
  sqlstr = 'select t.id, 0 as selected, tg.groupvalue as transtype, dg.groupvalue as direction, t.transnumber, t.transdate, c.custname,  \
    t.curr, sum(i.amount) as amount \
  from trans t \
  inner join groups tg on t.transtype = tg.id and tg.groupvalue in(\'invoice\',\'receipt\',\'order\',\'offer\',\'worksheet\',\'rent\') \
  inner join groups dg on t.direction = dg.id \
  left join customer c on t.customer_id = c.id \
  left join item i on t.id = i.trans_id and i.deleted=0 \
  where (t.deleted=0 or (tg.groupvalue=\'invoice\' and dg.groupvalue=\'out\') or (tg.groupvalue=\'receipt\' and dg.groupvalue=\'out\')) @where_str \
  group by t.id, tg.groupvalue, dg.groupvalue, t.transnumber, t.transdate, c.custname, t.curr \
  order by t.transnumber;')

#--------------------------------------------------
# fCustomer
#--------------------------------------------------
  nflex.insert(sqlkey = 'fCustomer_getCalendarView', engine = 'all', section = 'fCustomer', 
  sqlstr = 'select e.*, g.groupvalue as vf_groups from event e left join groups g on e.eventgroup = g.id \
    where e.deleted = 0 and  e.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
    and e.ref_id = @customer_id order by e.id;')
  
  nflex.insert(sqlkey = 'fCustomer_getDeffieldProp', engine = 'all', section = 'fCustomer', 
  sqlstr = 'select \'customer_\'||c.id as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'||t.id as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'||p.id as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'||p.id as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'||e.id as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'||p.id as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fCustomer_getDeffieldProp', engine = 'mysql', section = 'fCustomer', 
  sqlstr = 'select CONCAT(\'customer_\',cast(c.id as char)) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select CONCAT(\'tool_\',cast(t.id as char)) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select CONCAT(\'trans_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select CONCAT(\'transitem_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select CONCAT(\'transmovement_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select CONCAT(\'transpayment_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select CONCAT(\'product_\',cast(p.id as char)) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select CONCAT(\'project_\',cast(p.id as char)) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select CONCAT(\'employee_\',cast(e.id as char)) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select CONCAT(\'place_\',cast(p.id as char)) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fCustomer_getDeffieldProp', engine = 'mssql', section = 'fCustomer', 
  sqlstr = 'select \'customer_\'+cast(c.id as varchar) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'+cast(t.id as varchar) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'+cast(p.id as varchar) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'+cast(p.id as varchar) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'+cast(e.id as varchar) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'+cast(p.id as varchar) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @customer_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fCustomer_getDeleteSql_delete', engine = 'all', section = 'fCustomer', 
  sqlstr = 'delete from event where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') and ref_id=@customer_id; \
  delete from link where nervatype_1=(select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') and ref_id_1=@customer_id; \
  delete from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') and ref_id_2=@customer_id; \
  delete from address where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') and ref_id=@customer_id; \
  delete from contact where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\') and ref_id=@customer_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\'))  \
    and ref_id = @customer_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\'))  \
    and value = cast(@customer_id as text); \
  delete from customer where id=@customer_id;')
  
  nflex.insert(sqlkey = 'fCustomer_getDeleteSql_update', engine = 'all', section = 'fCustomer', sqlstr = 'update customer set deleted = 1 where id=@customer_id;')
  
  nflex.insert(sqlkey = 'fCustomer_getDeleteState', engine = 'all', section = 'fCustomer', 
  sqlstr = 'select cast(sum(co) as integer) as sco \
  from (select count(*) as co from trans where customer_id=@customer_id \
  union select count(*) as co from project where customer_id=@customer_id \
  union select count(*) as co from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'customer\')  \
    and ref_id_2=@customer_id \
  union select count(*) as co from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\'))  \
    and value = cast(@customer_id as text)) foo')

#--------------------------------------------------
# fEmployee
#--------------------------------------------------
  nflex.insert(sqlkey = 'fEmployee_getCalendarView', engine = 'all', section = 'fEmployee', 
  sqlstr = 'select e.*, g.groupvalue as vf_groups \
  from event e left join groups g on e.eventgroup = g.id \
  where e.deleted = 0 and  e.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\')  \
    and e.ref_id = @employee_id order by e.id;')
  
  nflex.insert(sqlkey = 'fEmployee_getDeffieldProp', engine = 'all', section = 'fEmployee', 
  sqlstr = 'select \'customer_\'||c.id as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'||t.id as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'||p.id as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'||p.id as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'||e.id as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'||p.id as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fEmployee_getDeffieldProp', engine = 'mysql', section = 'fEmployee', 
  sqlstr = 'select CONCAT(\'customer_\',cast(c.id as char)) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select CONCAT(\'tool_\',cast(t.id as char)) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select CONCAT(\'trans_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select CONCAT(\'transitem_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select CONCAT(\'transmovement_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select CONCAT(\'transpayment_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select CONCAT(\'product_\',cast(p.id as char)) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select CONCAT(\'project_\',cast(p.id as char)) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select CONCAT(\'employee_\',cast(e.id as char)) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select CONCAT(\'place_\',cast(p.id as char)) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fEmployee_getDeffieldProp', engine = 'mssql', section = 'fEmployee', 
  sqlstr = 'select \'customer_\'+cast(c.id as varchar) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'+cast(t.id as varchar) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'+cast(p.id as varchar) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'+cast(p.id as varchar) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'+cast(e.id as varchar) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'+cast(p.id as varchar) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @employee_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fEmployee_getDeleteSql_delete', engine = 'all', section = 'fEmployee', 
  sqlstr = 'delete from event where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') and ref_id=@employee_id; \
  delete from link where nervatype_1=(select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') and ref_id_1=@employee_id; \
  delete from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') and ref_id_2=@employee_id; \
  delete from address where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') and ref_id=@employee_id; \
  delete from contact where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\') and ref_id=@employee_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\'))  \
    and ref_id = @employee_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\'))  \
    and value = cast(@employee_id as text); \
  delete from employee where id=@employee_id;')
  
  nflex.insert(sqlkey = 'fEmployee_getDeleteSql_update', engine = 'all', section = 'fEmployee', sqlstr = 'update employee set deleted = 1 where id=@employee_id;')
  
  nflex.insert(sqlkey = 'fEmployee_getDeleteState', engine = 'all', section = 'fEmployee', 
  sqlstr = 'select cast(sum(co) as integer) as sco \
  from (select count(*) as co from trans where employee_id=@employee_id \
  union select count(*) as co from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'employee\')  \
    and ref_id_2=@employee_id \
  union select count(*) as co from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\'))  \
    and value = cast(@employee_id as text)) foo')
  
#--------------------------------------------------
# fEvent
#--------------------------------------------------
  nflex.insert(sqlkey = 'fEvent_getDeffieldProp', engine = 'all', section = 'fEvent', 
  sqlstr = 'select \'customer_\'||c.id as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'||t.id as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'||p.id as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'||p.id as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'||e.id as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'||p.id as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fEvent_getDeffieldProp', engine = 'mysql', section = 'fEvent', 
  sqlstr = 'select CONCAT(\'customer_\',cast(c.id as char)) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select CONCAT(\'tool_\',cast(t.id as char)) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select CONCAT(\'trans_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select CONCAT(\'transitem_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select CONCAT(\'transmovement_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select CONCAT(\'transpayment_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select CONCAT(\'product_\',cast(p.id as char)) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select CONCAT(\'project_\',cast(p.id as char)) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select CONCAT(\'employee_\',cast(e.id as char)) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select CONCAT(\'place_\',cast(p.id as char)) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fEvent_getDeffieldProp', engine = 'mssql', section = 'fEvent', 
  sqlstr = 'select \'customer_\'+cast(c.id as varchar) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'+cast(t.id as varchar) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'+cast(p.id as varchar) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'+cast(p.id as varchar) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'+cast(e.id as varchar) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'+cast(p.id as varchar) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @event_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fEvent_getDeleteSql_delete', engine = 'all', section = 'fEvent', 
  sqlstr = 'delete from link where nervatype_1=(select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') and ref_id_1=@event_id; \
  delete from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'event\') and ref_id_2=@event_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'event\')) and ref_id = @event_id; \
  delete from event where id=@event_id;')
  
  nflex.insert(sqlkey = 'fEvent_getDeleteSql_update', engine = 'all', section = 'fEvent', sqlstr = 'update event set deleted = 1 where id=@event_id;')

#--------------------------------------------------
# fProduct
#--------------------------------------------------
  nflex.insert(sqlkey = 'fProduct_getDeffieldProp', engine = 'all', section = 'fProduct', 
  sqlstr = 'select \'customer_\'||c.id as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'||t.id as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'||p.id as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'||p.id as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'||e.id as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'||p.id as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))' )
  
  nflex.insert(sqlkey = 'fProduct_getDeffieldProp', engine = 'mysql', section = 'fProduct', 
  sqlstr = 'select CONCAT(\'customer_\',cast(c.id as char)) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select CONCAT(\'tool_\',cast(t.id as char)) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select CONCAT(\'trans_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select CONCAT(\'transitem_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select CONCAT(\'transmovement_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select CONCAT(\'transpayment_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select CONCAT(\'product_\',cast(p.id as char)) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select CONCAT(\'project_\',cast(p.id as char)) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select CONCAT(\'employee_\',cast(e.id as char)) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select CONCAT(\'place_\',cast(p.id as char)) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))' )
  
  nflex.insert(sqlkey = 'fProduct_getDeffieldProp', engine = 'mssql', section = 'fProduct', 
  sqlstr = 'select \'customer_\'+cast(c.id as varchar) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'+cast(t.id as varchar) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'+cast(p.id as varchar) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'+cast(p.id as varchar) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'+cast(e.id as varchar) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'+cast(p.id as varchar) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @product_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))' )
  
  nflex.insert(sqlkey = 'fProduct_getDeleteSql_delete', engine = 'all', section = 'fProduct', 
  sqlstr = 'delete from event where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') and ref_id=@product_id; \
  delete from link where nervatype_1=(select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') and ref_id_1=@product_id; \
  delete from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') and ref_id_2=@product_id; \
  delete from movement where product_id=@product_id; \
  delete from tool where product_id=@product_id; \
  delete from item where product_id=@product_id; \
  delete from price where product_id=@product_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'product\'))  \
    and ref_id = @product_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\'))  \
    and value = cast(@product_id as text); \
  delete from product where id=@product_id;')
  
  nflex.insert(sqlkey = 'fProduct_getDeleteSql_update', engine = 'all', section = 'fProduct', sqlstr = 'update product set deleted = 1 where id=@product_id;')
  
  nflex.insert(sqlkey = 'fProduct_getDeleteState', engine = 'all', section = 'fProduct', 
  sqlstr = 'select cast(sum(co) as integer) as sco \
  from ( \
  select count(*) as co from movement where product_id=@product_id \
  union select count(*) as co from tool where product_id=@product_id \
  union select count(*) as co from item where product_id=@product_id \
  union select count(*) as co from price where product_id=@product_id \
  union select count(*) as co from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'product\')  \
    and ref_id_2=@product_id \
  union select count(*) as co from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\'))  \
    and value = cast(@product_id as text)) foo')
  
  nflex.insert(sqlkey = 'fProduct_getEventView', engine = 'all', section = 'fProduct', 
  sqlstr = 'select e.*, g.groupvalue as vf_groups  \
  from event e left join groups g on e.eventgroup = g.id \
  where e.deleted = 0 and  e.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'product\') and e.ref_id = @product_id \
  order by e.id;')
  
  nflex.insert(sqlkey = 'fProduct_getGroupsLang', engine = 'all', section = 'fProduct', 
  sqlstr = 'select g.id, g.groupvalue, ms.msg as langvalue from groups g \
  left join ui_message ms on ms.secname = g.groupname and ms.fieldname = g.groupvalue  \
  and ms.lang = (select value from fieldvalue where fieldname = \'default_lang\') \
  where g.groupname in (\'protype\', \'calcmode\');')
  
  nflex.insert(sqlkey = 'fProduct_getPriceProp', engine = 'all', section = 'fProduct', 
  sqlstr = 'select pp.id, c.id as customer_id, c.custname as description \
  from price pp \
  inner join link ln0 on ln0.nervatype_1 = (select id from groups where groupname=\'nervatype\' and groupvalue=\'price\') and ln0.ref_id_1 = pp.id \
  inner join customer c on ln0.nervatype_2 = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\')  \
    and ln0.ref_id_2 = c.id and c.deleted=0 \
  where pp.product_id = @product_id')
  
  nflex.insert(sqlkey = 'fProduct_getValidBarcode', engine = 'all', section = 'fProduct', sqlstr = 'select case when count(*)>0 then 0 else 1 end as valid, @barcode as barcode  \
        from barcode where code like @barcode')

#--------------------------------------------------
# fTool
#--------------------------------------------------
  nflex.insert(sqlkey = 'fTool_getCalendarView', engine = 'all', section = 'fTool', 
  sqlstr = 'select e.*, g.groupvalue as vf_groups \
  from event e left join groups g on e.eventgroup = g.id \
  where e.deleted = 0 and  e.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\')  \
    and e.ref_id = @tool_id order by e.id;')
  
  nflex.insert(sqlkey = 'fTool_getTransView', engine = 'all', section = 'fTool', 
  sqlstr = 'select t.id, tg.groupvalue as transtype, dg.groupvalue as direction, t.transnumber, cast(mv.shippingdate as date) as shippingdate \
    , case when msd.msg is null then dg.groupvalue else msd.msg end as direction_lang \
    , lt.transnumber as refnumber, e.empnumber, t.employee_id, t.customer_id, c.custnumber, c.custname, lt.id as refnumber_id \
    , t.closed, mv.notes \
  from trans t \
  inner join movement mv on t.id = mv.trans_id \
  inner join tool tl on mv.tool_id = tl.id \
  inner join groups tg on t.transtype = tg.id and tg.groupvalue = \'waybill\' \
  inner join groups dg on t.direction = dg.id \
    left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = \'direction\' \
      and msd.lang = (select value from fieldvalue where fieldname = \'default_lang\') \
  left join link lnk on t.id = lnk.ref_id_1 and lnk.deleted=0 and lnk.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
       and lnk.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
       left join trans lt on lnk.ref_id_2 = lt.id \
  left join employee e on t.employee_id = e.id \
  left join customer c on t.customer_id = c.id \
  where t.deleted = 0 and mv.deleted=0 and mv.tool_id = @tool_id \
  order by shippingdate;')
  
  nflex.insert(sqlkey = 'fTool_getDeffieldProp', engine = 'all', section = 'fTool', 
  sqlstr = 'select \'customer_\'||c.id as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'||t.id as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'||p.id as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'||p.id as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'||e.id as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'||p.id as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fTool_getDeffieldProp', engine = 'mysql', section = 'fTool', 
  sqlstr = 'select CONCAT(\'customer_\',cast(c.id as char)) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select CONCAT(\'tool_\',cast(t.id as char)) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select CONCAT(\'trans_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed) \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select CONCAT(\'transitem_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select CONCAT(\'transmovement_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select CONCAT(\'transpayment_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select CONCAT(\'product_\',cast(p.id as char)) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select CONCAT(\'project_\',cast(p.id as char)) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select CONCAT(\'employee_\',cast(e.id as char)) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select CONCAT(\'place_\',cast(p.id as char)) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fTool_getDeffieldProp', engine = 'mssql', section = 'fTool', 
  sqlstr = 'select \'customer_\'+cast(c.id as varchar) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'+cast(t.id as varchar) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'+cast(p.id as varchar) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'+cast(p.id as varchar) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'+cast(e.id as varchar) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'+cast(p.id as varchar) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @tool_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fTool_getDeleteSql_delete', engine = 'all', section = 'fTool', 
  sqlstr = 'delete from event where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') and ref_id=@tool_id; \
  delete from link where nervatype_1=(select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') and ref_id_1=@tool_id; \
  delete from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\') and ref_id_2=@tool_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\'))  \
    and ref_id = @tool_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\'))  \
    and value = cast(@tool_id as text); \
  delete from tool where id=@tool_id;')
  
  nflex.insert(sqlkey = 'fTool_getDeleteSql_update', engine = 'all', section = 'fTool', sqlstr = 'update tool set deleted = 1 where id=@tool_id;')
  
  nflex.insert(sqlkey = 'fTool_getDeleteState', engine = 'all', section = 'fTool', 
  sqlstr = 'select cast(sum(co) as integer) as sco \
  from (select count(*) as co from movement mv inner join trans t on mv.trans_id = t.id and t.deleted=0 where tool_id=@tool_id \
  union select count(*) as co from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'tool\')  \
    and ref_id_2=@tool_id \
  union select count(*) as co from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\'))  \
    and value = cast(@tool_id as text)) foo')

#--------------------------------------------------
# fProject
#--------------------------------------------------
  nflex.insert(sqlkey = 'fProject_getCustProp', engine = 'all', section = 'fProject', 
  sqlstr = 'select c.id as id, c.custnumber as custnumber, c.custname as cname \
        from project p \
        left join customer c on p.customer_id = c.id \
        where p.id = @project_id')
  
  nflex.insert(sqlkey = 'fProject_getCalendarView', engine = 'all', section = 'fProject', 
  sqlstr = 'select e.*, g.groupvalue as vf_groups from event e left join groups g on e.eventgroup = g.id \
    where e.deleted = 0 and  e.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
    and e.ref_id = @project_id order by e.id;')
  
  nflex.insert(sqlkey = 'fProject_getTransView', engine = 'all', section = 'fProject', 
  sqlstr = 'select t.id, 0 as selected, tg.groupvalue as transtype, case when mst.msg is null then tg.groupvalue else mst.msg end as transtype_ms, \
    dg.groupvalue as direction, t.transnumber, t.transdate, c.custname,  t.curr, sum(i.amount) as amount \
  from trans t \
  inner join groups tg on t.transtype = tg.id \
    left join ui_message mst on mst.fieldname = tg.groupvalue and  mst.secname = \'transtype\' \
    and mst.lang = (select value from fieldvalue where fieldname = \'default_lang\') \
  inner join groups dg on t.direction = dg.id left join customer c on t.customer_id = c.id \
  inner join item i on t.id = i.trans_id and i.deleted=0 inner join project p on t.project_id = p.id \
  where (t.deleted=0 or (tg.groupvalue=\'invoice\' and dg.groupvalue=\'out\') or (tg.groupvalue=\'receipt\' and dg.groupvalue=\'out\')) and p.id = @project_id \
  group by t.id, tg.groupvalue, dg.groupvalue, mst.msg, t.transnumber, t.transdate, c.custname, t.curr \
  order by t.transdate;')
  
  nflex.insert(sqlkey = 'fProject_getDeffieldProp', engine = 'all', section = 'fProject', 
  sqlstr = 'select \'customer_\'||c.id as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'||t.id as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'||p.id as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'||p.id as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'||e.id as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'||p.id as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))' )
  
  nflex.insert(sqlkey = 'fProject_getDeffieldProp', engine = 'mysql', section = 'fProject', 
  sqlstr = 'select CONCAT(\'customer_\',cast(c.id as char)) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select CONCAT(\'tool_\',cast(t.id as char)) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select CONCAT(\'trans_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select CONCAT(\'transitem_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select CONCAT(\'transmovement_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select CONCAT(\'transpayment_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select CONCAT(\'product_\',cast(p.id as char)) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select CONCAT(\'project_\',cast(p.id as char)) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select CONCAT(\'employee_\',cast(e.id as char)) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select CONCAT(\'place_\',cast(p.id as char)) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))' )
  
  nflex.insert(sqlkey = 'fProject_getDeffieldProp', engine = 'mssql', section = 'fProject', 
  sqlstr = 'select \'customer_\'+cast(c.id as varchar) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'+cast(t.id as varchar) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'+cast(p.id as varchar) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'+cast(p.id as varchar) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'+cast(e.id as varchar) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'+cast(p.id as varchar) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @project_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))' )
  
  nflex.insert(sqlkey = 'fProject_getDeleteSql_delete', engine = 'all', section = 'fProject', 
  sqlstr = 'delete from event where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') and ref_id=@project_id; \
  delete from link where nervatype_1=(select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') and ref_id_1=@project_id; \
  delete from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') and ref_id_2=@project_id; \
  delete from address where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') and ref_id=@project_id; \
  delete from contact where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'project\') and ref_id=@project_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'project\'))  \
    and ref_id = @project_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\'))  \
    and value = cast(@project_id as text); \
  delete from project where id=@project_id;')
  
  nflex.insert(sqlkey = 'fProject_getDeleteSql_update', engine = 'all', section = 'fProject', sqlstr = 'update project set deleted = 1 where id=@project_id;')
  
  nflex.insert(sqlkey = 'fProject_getDeleteState', engine = 'all', section = 'fProject', 
  sqlstr = 'select cast(sum(co) as integer) as sco \
  from (select count(*) as co from trans where project_id=@project_id \
  union select count(*) as co from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'project\')  \
    and ref_id_2=@project_id \
  union select count(*) as co from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\'))  \
    and value = cast(@project_id as text)) foo')

#--------------------------------------------------
# fTrans
#--------------------------------------------------
  nflex.insert(sqlkey = 'fTrans_getCustProp', engine = 'all', section = 'fTrans', 
  sqlstr = 'select c.id as id, c.custnumber as custnumber, c.custname as name, case when address is null then \'\' else address end as address,  \
        c.taxnumber as taxnumber, c.terms as terms, dd.defterm, c.discount as discount, c.notax as notax \
        from trans t \
        left join customer c on t.customer_id = c.id \
        left join (select ref_id as customer_id,  \
  case when zipcode is null then \'\' else zipcode end || \' \' || case when city is null then \'\' else city end || \' \' || \
    case when street is null then \'\' else street end as address from address  \
  where id in(select min(id) from address \
    where nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\') and deleted = 0 \
    group by ref_id)) adr on c.id=adr.customer_id \
        , (select cast(value as integer) as defterm from fieldvalue where fieldname = \'default_deadline\') dd   \
        where t.id = @trans_id')
  
  nflex.insert(sqlkey = 'fTrans_getCustProp', engine = 'mssql', section = 'fTrans', 
  sqlstr = 'select c.id as id, c.custnumber as custnumber, c.custname as name, case when address is null then \'\' else address end as address,  \
        c.taxnumber as taxnumber, c.terms as terms, dd.defterm, c.discount as discount, c.notax as notax \
        from trans t \
        left join customer c on t.customer_id = c.id \
        left join (select ref_id as customer_id,  \
  case when zipcode is null then \'\' else zipcode end + \' \' + case when city is null then \'\' else city end + \' \' + \
    case when street is null then \'\' else street end as address from address  \
  where id in(select min(id) from address \
    where nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\') and deleted = 0 \
    group by ref_id)) adr on c.id=adr.customer_id \
        , (select cast(value as integer) as defterm from fieldvalue where fieldname = \'default_deadline\') dd   \
        where t.id = @trans_id')
  
  nflex.insert(sqlkey = 'fTrans_getCustProp', engine = 'mysql', section = 'fTrans', 
  sqlstr = 'select c.id as id, c.custnumber as custnumber, c.custname as name, case when address is null then \'\' else address end as address,  \
        c.taxnumber as taxnumber, c.terms as terms, dd.defterm, c.discount as discount, c.notax as notax \
        from trans t \
        left join customer c on t.customer_id = c.id \
        left join (select ref_id as customer_id,  \
  CONCAT(case when zipcode is null then \'\' else zipcode end, \' \', case when city is null then \'\' else city end, \' \', \
    case when street is null then \'\' else street end) as address from address  \
  where id in(select min(id) from address \
    where nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\') and deleted = 0 \
    group by ref_id)) adr on c.id=adr.customer_id \
        , (select cast(value as signed) as defterm from fieldvalue where fieldname = \'default_deadline\') dd   \
        where t.id = @trans_id')
  
  nflex.insert(sqlkey = 'fTrans_getDeffieldProp', engine = 'all', section = 'fTrans', 
  sqlstr = 'select \'customer_\'||c.id as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'||t.id as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'||p.id as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'||p.id as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'||e.id as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'||p.id as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fTrans_getDeffieldProp', engine = 'mysql', section = 'fTrans', 
  sqlstr = 'select CONCAT(\'customer_\',cast(c.id as char)) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select CONCAT(\'tool_\',cast(t.id as char)) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select CONCAT(\'trans_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select CONCAT(\'transitem_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select CONCAT(\'transmovement_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select CONCAT(\'transpayment_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select CONCAT(\'product_\',cast(p.id as char)) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select CONCAT(\'project_\',cast(p.id as char)) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select CONCAT(\'employee_\',cast(e.id as char)) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select CONCAT(\'place_\',cast(p.id as char)) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fTrans_getDeffieldProp', engine = 'mssql', section = 'fTrans', 
  sqlstr = 'select \'customer_\'+cast(c.id as varchar) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'+cast(t.id as varchar) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'+cast(p.id as varchar) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'+cast(p.id as varchar) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'+cast(e.id as varchar) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'+cast(p.id as varchar) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id = @trans_id \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fTrans_getDeffieldPropShip', engine = 'all', section = 'fTrans', 
  sqlstr = 'select \'customer_\'||c.id as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id  \
    from movement mt inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'||t.id as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'||t.id as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'||p.id as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'||p.id as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'||e.id as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'||p.id as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as integer)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fTrans_getDeffieldPropShip', engine = 'mysql', section = 'fTrans', 
  sqlstr = 'select CONCAT(\'customer_\',cast(c.id as char)) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id  \
    from movement mt inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select CONCAT(\'tool_\',cast(t.id as char)) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select CONCAT(\'trans_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select CONCAT(\'transitem_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select CONCAT(\'transmovement_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select CONCAT(\'transpayment_\',cast(t.id as char)) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select CONCAT(\'product_\',cast(p.id as char)) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select CONCAT(\'project_\',cast(p.id as char)) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select CONCAT(\'employee_\',cast(e.id as char)) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select CONCAT(\'place_\',cast(p.id as char)) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select cast(fv.value as signed)  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fTrans_getDeffieldPropShip', engine = 'mssql', section = 'fTrans', 
  sqlstr = 'select \'customer_\'+cast(c.id as varchar) as id, c.custname as description \
  from customer c \
  where c.deleted=0 and c.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id  \
    from movement mt inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'customer\')) \
  union select \'tool_\'+cast(t.id as varchar) as id, t.serial as description \
  from tool t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'tool\')) \
  union select \'trans_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\')) \
  union select \'transitem_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transitem\')) \
  union select \'transmovement_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transmovement\')) \
  union select \'transpayment_\'+cast(t.id as varchar) as id, t.transnumber as description \
  from trans t \
  where t.deleted=0 and t.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'transpayment\')) \
  union select \'product_\'+cast(p.id as varchar) as id, p.partnumber as description \
  from product p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'product\')) \
  union select \'project_\'+cast(p.id as varchar) as id, p.pronumber as description \
  from project p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'project\')) \
  union select \'employee_\'+cast(e.id as varchar) as id, e.empnumber as description \
  from employee e \
  where e.deleted=0 and e.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'employee\')) \
  union select \'place_\'+cast(p.id as varchar) as id, p.planumber as description \
  from place p \
  where p.deleted=0 and p.id in (select case when ISNUMERIC(fv.value)=1 then cast(fv.value as integer) else 0 end  \
    from deffield df \
    inner join fieldvalue fv on df.fieldname = fv.fieldname and fv.ref_id in(select distinct mt.trans_id from movement mt  \
    inner join trans t on mt.trans_id = t.id  \
      inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\')  \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\')  \
      inner join item i on ln.ref_id_2 = i.id where mt.deleted = 0 and i.trans_id = @trans_id) \
    where fv.deleted = 0 and df.nervatype = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
      and df.fieldtype = (select id from groups where groupname = \'fieldtype\' and groupvalue = \'place\'))')
  
  nflex.insert(sqlkey = 'fTrans_getDeleteLinkSql_delete', engine = 'all', section = 'fTrans', sqlstr = 'delete link from id = @link_id;')
  
  nflex.insert(sqlkey = 'fTrans_getDeleteLinkSql_update', engine = 'all', section = 'fTrans', sqlstr = 'update link set deleted=1 where id = @link_id;')
  
  nflex.insert(sqlkey = 'fTrans_getDeleteSql_delete', engine = 'all', section = 'fTrans', 
  sqlstr = 'delete from link where nervatype_1=(select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') and ref_id_1=@trans_id; \
  delete from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') and ref_id_2=@trans_id; \
  delete from movement where trans_id=@trans_id; \
  delete from payment where trans_id=@trans_id; \
  delete from item where trans_id=@trans_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where nervatype=(select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\'))  \
    and ref_id = @trans_id; \
  delete from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\'))  \
    and value = cast(@trans_id as text); \
  delete from trans where id=@trans_id;')
  
  nflex.insert(sqlkey = 'fTrans_getDeleteSql_update', engine = 'all', section = 'fTrans', sqlstr = 'update trans set deleted = 1 where id=@trans_id;')
  
  nflex.insert(sqlkey = 'fTrans_getDeleteState', engine = 'all', section = 'fTrans', 
  sqlstr = 'select cast(sum(co) as integer) as sco \
  from ( \
  select count(*) as co from link where nervatype_2=(select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') and ref_id_2=@trans_id \
  union select count(*) as co from fieldvalue where fieldname in( \
    select fieldname from deffield where fieldtype=(select id from groups where groupname = \'fieldtype\' and groupvalue = \'trans\'))  \
    and value = cast(@trans_id as text);) foo')
  
  nflex.insert(sqlkey = 'fTrans_getDeliveryInventoryView', engine = 'all', section = 'fTrans', 
  sqlstr = 'select mt.product_id, mt.place_id, pl.planumber, pl.description, mt.notes, sum(mt.qty) as sqty \
  from movement mt \
  inner join groups g on mt.movetype = g.id and g.groupvalue = \'inventory\' \
  inner join place pl on mt.place_id = pl.id \
  where mt.deleted = 0 and mt.product_id in (select distinct case when fv.value is null then i.product_id else cast(fv.value as integer) end as product_id \
    from item i  \
    left join fieldvalue fv on fv.ref_id = i.product_id and fv.fieldname = \'product_element\' \
    inner join product p on i.product_id = p.id \
    inner join groups pg on p.protype = pg.id and pg.groupvalue = \'item\' \
    where i.deleted=0 and i.trans_id = @trans_id) \
  group by mt.product_id, mt.place_id, pl.planumber, pl.description, mt.notes')
  
  nflex.insert(sqlkey = 'fTrans_getDeliveryInventoryView', engine = 'mysql', section = 'fTrans', 
  sqlstr = 'select mt.product_id, mt.place_id, pl.planumber, pl.description, mt.notes, sum(mt.qty) as sqty \
  from movement mt \
  inner join groups g on mt.movetype = g.id and g.groupvalue = \'inventory\' \
  inner join place pl on mt.place_id = pl.id \
  where mt.deleted = 0 and mt.product_id in (select distinct case when fv.value is null then i.product_id else cast(fv.value as signed) end as product_id \
    from item i  \
    left join fieldvalue fv on fv.ref_id = i.product_id and fv.fieldname = \'product_element\' \
    inner join product p on i.product_id = p.id \
    inner join groups pg on p.protype = pg.id and pg.groupvalue = \'item\' \
    where i.deleted=0 and i.trans_id = @trans_id) \
  group by mt.product_id, mt.place_id, pl.planumber, pl.description, mt.notes')
  
  nflex.insert(sqlkey = 'fTrans_getDeliveryItemView', engine = 'postgres', section = 'fTrans', 
  sqlstr = 'select foo.*, p.partnumber, case when foo.pgroup=true then p.description||\' (\'||foo.description||\')\' else foo.description end as itemname, \
    cfv.notes as cust_partnumber,  case when mov.tqty is null then 0 else mov.tqty end tqty \
  from (select i.id as item_id, i.description, t.customer_id, case when fv.value is null then i.product_id else cast(fv.value as integer) end as product_id, \
      case when fv.value is null then false else true end as pgroup,  \
      sum(case when length (translate (trim (fv.notes),\' +-.0123456789\',\' \'))=0 then cast(fv.notes as real) else 1 end*i.qty) as pqty \
    from trans t \
    inner join item i on t.id = i.trans_id \
    left join fieldvalue fv on fv.ref_id = i.product_id and fv.fieldname = \'product_element\' \
    inner join product p on i.product_id = p.id \
    where i.deleted=0 and t.id = @trans_id \
    group by i.id, i.description, t.customer_id, p.partnumber, p.description, case when fv.value is null then i.product_id else cast(fv.value as integer) end, \
    case when fv.value is null then false else true end) foo \
  inner join product p on foo.product_id = p.id \
  inner join groups pg on p.protype = pg.id and pg.groupvalue = \'item\' \
  left join fieldvalue cfv on cfv.ref_id = foo.product_id and cfv.fieldname = \'product_custpartnumber\' and cast(cfv.value as integer) = foo.customer_id \
  left join (select i.id as item_id, mt.product_id, sum(case when dg.groupvalue=\'out\' then -mt.qty else mt.qty end) as tqty \
    from movement mt \
    inner join trans t on mt.trans_id = t.id \
    inner join groups dg on t.direction = dg.id \
    inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\') \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\') \
    inner join item i on ln.ref_id_2 = i.id  \
    where mt.deleted = 0 and i.trans_id = @trans_id \
    group by i.id, mt.product_id) mov on foo.item_id = mov.item_id and foo.product_id = mov.product_id \
  order by foo.item_id;')
  
  nflex.insert(sqlkey = 'fTrans_getDeliveryItemView', engine = 'sqlite', section = 'fTrans', 
  sqlstr = 'select foo.*, p.partnumber, case when foo.pgroup=1 then p.description||\' (\'||foo.description||\')\' else foo.description end as itemname, \
    cfv.notes as cust_partnumber,  case when mov.tqty is null then 0 else mov.tqty end tqty \
  from (select i.id as item_id, i.description, t.customer_id, case when fv.value is null then i.product_id else cast(fv.value as integer) end as product_id, \
      case when fv.value is null then 0 else 1 end as pgroup,  \
      sum(case when cast(fv.notes as real)!=0 then cast(fv.notes as real) else 1 end*i.qty) as pqty \
    from trans t \
    inner join item i on t.id = i.trans_id \
    left join fieldvalue fv on fv.ref_id = i.product_id and fv.fieldname = \'product_element\' \
    inner join product p on i.product_id = p.id \
    where i.deleted=0 and t.id = @trans_id \
    group by i.id, i.description, t.customer_id, p.partnumber, p.description, case when fv.value is null then i.product_id else cast(fv.value as integer) end, \
    case when fv.value is null then 0 else 1 end) foo \
  inner join product p on foo.product_id = p.id \
  inner join groups pg on p.protype = pg.id and pg.groupvalue = \'item\' \
  left join fieldvalue cfv on cfv.ref_id = foo.product_id and cfv.fieldname = \'product_custpartnumber\' and cast(cfv.value as integer) = foo.customer_id \
  left join (select i.id as item_id, mt.product_id, sum(case when dg.groupvalue=\'out\' then -mt.qty else mt.qty end) as tqty \
    from movement mt \
    inner join trans t on mt.trans_id = t.id \
    inner join groups dg on t.direction = dg.id \
    inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\') \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\') \
    inner join item i on ln.ref_id_2 = i.id  \
    where mt.deleted = 0 and i.trans_id = @trans_id \
    group by i.id, mt.product_id) mov on foo.item_id = mov.item_id and foo.product_id = mov.product_id \
  order by foo.item_id;')
  
  nflex.insert(sqlkey = 'fTrans_getDeliveryItemView', engine = 'mysql', section = 'fTrans', 
  sqlstr = 'select foo.*, p.partnumber, case when foo.pgroup=true then CONCAT(p.description,\' (\', foo.description, \')\') else foo.description end as itemname, \
    cfv.notes as cust_partnumber,  case when mov.tqty is null then 0 else mov.tqty end tqty \
  from (select i.id as item_id, i.description, t.customer_id, case when fv.value is null then i.product_id else cast(fv.value as signed) end as product_id, \
      case when fv.value is null then false else true end as pgroup,  \
      sum(case when ISNUMERIC(ltrim(rtrim(fv.notes)))=1 then cast(ltrim(rtrim(fv.notes)) as decimal) else 1 end*i.qty) as pqty \
    from trans t \
    inner join item i on t.id = i.trans_id \
    left join fieldvalue fv on fv.ref_id = i.product_id and fv.fieldname = \'product_element\' \
    inner join product p on i.product_id = p.id \
    where i.deleted=0 and t.id = @trans_id \
    group by i.id, i.description, t.customer_id, p.partnumber, p.description, case when fv.value is null then i.product_id else cast(fv.value as signed) end, \
    case when fv.value is null then false else true end) foo \
  inner join product p on foo.product_id = p.id \
  inner join groups pg on p.protype = pg.id and pg.groupvalue = \'item\' \
  left join fieldvalue cfv on cfv.ref_id = foo.product_id and cfv.fieldname = \'product_custpartnumber\' and cast(cfv.value as signed) = foo.customer_id \
  left join (select i.id as item_id, mt.product_id, sum(case when dg.groupvalue=\'out\' then -mt.qty else mt.qty end) as tqty \
    from movement mt \
    inner join trans t on mt.trans_id = t.id \
    inner join groups dg on t.direction = dg.id \
    inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\') \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\') \
    inner join item i on ln.ref_id_2 = i.id  \
    where mt.deleted = 0 and i.trans_id = @trans_id \
    group by i.id, mt.product_id) mov on foo.item_id = mov.item_id and foo.product_id = mov.product_id \
  order by foo.item_id;')
  
  nflex.insert(sqlkey = 'fTrans_getDeliveryItemView', engine = 'mssql', section = 'fTrans', 
  sqlstr = 'select foo.*, p.partnumber, case when foo.pgroup=1 then p.description+\' (\'+foo.description+\')\' else foo.description end as itemname, \
    cfv.notes as cust_partnumber,  case when mov.tqty is null then 0 else mov.tqty end tqty \
  from (select i.id as item_id, i.description, t.customer_id, case when fv.value is null then i.product_id else cast(fv.value as integer) end as product_id, \
      case when fv.value is null then 0 else 1 end as pgroup,  \
      sum(case when isnumeric(fv.notes)=1 then cast(fv.notes as real) else 1 end*i.qty) as pqty \
    from trans t \
    inner join item i on t.id = i.trans_id \
    left join fieldvalue fv on fv.ref_id = i.product_id and fv.fieldname = \'product_element\' \
    inner join product p on i.product_id = p.id \
    where i.deleted=0 and t.id = @trans_id \
    group by i.id, i.description, t.customer_id, p.partnumber, p.description, case when fv.value is null then i.product_id else cast(fv.value as integer) end, \
    case when fv.value is null then 0 else 1 end) foo \
  inner join product p on foo.product_id = p.id \
  inner join groups pg on p.protype = pg.id and pg.groupvalue = \'item\' \
  left join fieldvalue cfv on cfv.ref_id = foo.product_id and cfv.fieldname = \'product_custpartnumber\' and cast(cfv.value as integer) = foo.customer_id \
  left join (select i.id as item_id, mt.product_id, sum(case when dg.groupvalue=\'out\' then -mt.qty else mt.qty end) as tqty \
    from movement mt \
    inner join trans t on mt.trans_id = t.id \
    inner join groups dg on t.direction = dg.id \
    inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\') \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\') \
    inner join item i on ln.ref_id_2 = i.id  \
    where mt.deleted = 0 and i.trans_id = @trans_id \
    group by i.id, mt.product_id) mov on foo.item_id = mov.item_id and foo.product_id = mov.product_id \
  order by foo.item_id;')
  
  nflex.insert(sqlkey = 'fTrans_getDeliveryShippingView', engine = 'all', section = 'fTrans', 
  sqlstr = 'select mt.trans_id, t.transnumber, dg.groupvalue as ditection, substr(mt.shippingdate,1,10) as shippingdate, pt.description as place,  \
    p.partnumber, i.description, mt.qty, mt.notes, mt.product_id, i.id as item_id, mt.place_id \
    from movement mt \
    inner join trans t on mt.trans_id = t.id \
    inner join groups dg on t.direction = dg.id \
    inner join product p on mt.product_id = p.id \
    inner join place pt on mt.place_id = pt.id \
    inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\') \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\') \
    inner join item i on ln.ref_id_2 = i.id \
    where mt.deleted = 0 and i.trans_id = @trans_id \
    order by mt.trans_id;')
  
  nflex.insert(sqlkey = 'fTrans_getGroupsLang', engine = 'all', section = 'fTrans', 
  sqlstr = 'select g.id, g.groupvalue, ms.msg as langvalue from groups g \
  left join ui_message ms on ms.secname = g.groupname and ms.fieldname = g.groupvalue  \
  and ms.lang = (select value from fieldvalue where fieldname = \'default_lang\') \
  where g.groupname in (\'paidtype\', \'transtate\', \'storetype\', \'direction\');')
  
  nflex.insert(sqlkey = 'fTrans_getIniField', engine = 'all', section = 'fTrans', sqlstr = 'select value as inivalue from inifields where fieldname=@inifield')
  
  nflex.insert(sqlkey = 'fTrans_getInvoiceView', engine = 'all', section = 'fTrans', 
  sqlstr = 'select t1.id as id, t1dir.groupvalue as direction, ti.deposit, t1.transnumber, t1.transdate, t1.curr, ti.product_id, \
  ti.description, ti.unit, ti.qty, ti.netamount, ti.vatamount, ti.amount, ti.fxprice, ti.discount, ti.tax_id, p.partnumber, p.description as partname \
  from link ln  \
  inner join trans t1 on ln.ref_id_1 = t1.id and t1.deleted=0 \
    inner join groups t1type on t1.transtype = t1type.id and (t1type.groupvalue=\'invoice\' or t1type.groupvalue=\'receipt\') \
    inner join groups t1dir on t1.direction = t1dir.id \
  inner join item ti on t1.id = ti.trans_id and ti.deleted=0 \
  inner join product p on ti.product_id = p.id \
  inner join trans t2 on ln.ref_id_2 = t2.id \
  where ln.deleted=0 and ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\')  \
    and t1.direction = t2.direction and ln.ref_id_2 = @trans_id \
  order by ti.id;')
  
  nflex.insert(sqlkey = 'fTrans_getItemDeliveryView', engine = 'all', section = 'fTrans', 
  sqlstr = 'select foo.*, p.partnumber, case when foo.pgroup=true then p.description||\' (\'||foo.description||\')\' else foo.description end as itemname, \
    case when mov.tqty is null then 0 else mov.tqty end tqty \
  from (select i.id as item_id, i.description, case when fv.value is null then i.product_id else cast(fv.value as integer) end as product_id, \
      case when fv.value is null then false else true end as pgroup,  \
      sum(case when length (translate (trim (fv.notes),\' +-.0123456789\',\' \'))=0 then cast(fv.notes as real) else 1 end*i.qty) as pqty \
    from trans t \
    inner join item i on t.id = i.trans_id \
    left join fieldvalue fv on fv.ref_id = i.product_id and fv.fieldname = \'product_element\' \
    inner join product p on i.product_id = p.id \
    where i.deleted=0 and t.id = @trans_id \
    group by i.id, i.description, p.partnumber, p.description, case when fv.value is null then i.product_id else cast(fv.value as integer) end, \
    case when fv.value is null then false else true end) foo \
  inner join product p on foo.product_id = p.id \
  inner join groups pg on p.protype = pg.id and pg.groupvalue = \'item\' \
  left join (select i.id as item_id, mt.product_id, sum(case when dg.groupvalue=\'out\' then -mt.qty else mt.qty end) as tqty \
    from movement mt \
    inner join trans t on mt.trans_id = t.id \
    inner join groups dg on t.direction = dg.id \
    inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\') \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\') \
    inner join item i on ln.ref_id_2 = i.id  \
    where mt.deleted = 0 and i.trans_id = @trans_id \
    group by i.id, mt.product_id) mov on foo.item_id = mov.item_id and foo.product_id = mov.product_id \
  order by foo.item_id;')
  
  nflex.insert(sqlkey = 'fTrans_getItemDeliveryView', engine = 'sqlite', section = 'fTrans', 
  sqlstr = 'select foo.*, p.partnumber, case when foo.pgroup=1 then p.description||\' (\'||foo.description||\')\' else foo.description end as itemname, \
    case when mov.tqty is null then 0 else mov.tqty end tqty \
  from (select i.id as item_id, i.description, case when fv.value is null then i.product_id else cast(fv.value as integer) end as product_id, \
      case when fv.value is null then 0 else 1 end as pgroup,  \
      sum(case when cast(fv.notes as real)!=0 then cast(fv.notes as real) else 1 end*i.qty) as pqty \
    from trans t \
    inner join item i on t.id = i.trans_id \
    left join fieldvalue fv on fv.ref_id = i.product_id and fv.fieldname = \'product_element\' \
    inner join product p on i.product_id = p.id \
    where i.deleted=0 and t.id = @trans_id \
    group by i.id, i.description, p.partnumber, p.description, case when fv.value is null then i.product_id else cast(fv.value as integer) end, \
    case when fv.value is null then 0 else 1 end) foo \
  inner join product p on foo.product_id = p.id \
  inner join groups pg on p.protype = pg.id and pg.groupvalue = \'item\' \
  left join (select i.id as item_id, mt.product_id, sum(case when dg.groupvalue=\'out\' then -mt.qty else mt.qty end) as tqty \
    from movement mt \
    inner join trans t on mt.trans_id = t.id \
    inner join groups dg on t.direction = dg.id \
    inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\') \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\') \
    inner join item i on ln.ref_id_2 = i.id  \
    where mt.deleted = 0 and i.trans_id = @trans_id \
    group by i.id, mt.product_id) mov on foo.item_id = mov.item_id and foo.product_id = mov.product_id \
  order by foo.item_id;')
  
  nflex.insert(sqlkey = 'fTrans_getItemDeliveryView', engine = 'mysql', section = 'fTrans', 
  sqlstr = 'select foo.*, p.partnumber, case when foo.pgroup=true then CONCAT(p.description, \' (\', foo.description, \')\') else foo.description end as itemname, \
    case when mov.tqty is null then 0 else mov.tqty end tqty \
  from (select i.id as item_id, i.description, case when fv.value is null then i.product_id else cast(fv.value as signed) end as product_id, \
      case when fv.value is null then false else true end as pgroup,  \
      sum(case when ISNUMERIC(ltrim(rtrim(fv.notes)))=1 then cast(ltrim(rtrim(fv.notes)) as decimal) else 1 end*i.qty) as pqty \
    from trans t \
    inner join item i on t.id = i.trans_id \
    left join fieldvalue fv on fv.ref_id = i.product_id and fv.fieldname = \'product_element\' \
    inner join product p on i.product_id = p.id \
    where i.deleted=0 and t.id = @trans_id \
    group by i.id, i.description, p.partnumber, p.description, case when fv.value is null then i.product_id else cast(fv.value as signed) end, \
    case when fv.value is null then false else true end) foo \
  inner join product p on foo.product_id = p.id \
  inner join groups pg on p.protype = pg.id and pg.groupvalue = \'item\' \
  left join (select i.id as item_id, mt.product_id, sum(case when dg.groupvalue=\'out\' then -mt.qty else mt.qty end) as tqty \
    from movement mt \
    inner join trans t on mt.trans_id = t.id \
    inner join groups dg on t.direction = dg.id \
    inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\') \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\') \
    inner join item i on ln.ref_id_2 = i.id  \
    where mt.deleted = 0 and i.trans_id = @trans_id \
    group by i.id, mt.product_id) mov on foo.item_id = mov.item_id and foo.product_id = mov.product_id \
  order by foo.item_id;')
  
  nflex.insert(sqlkey = 'fTrans_getItemDeliveryView', engine = 'mssql', section = 'fTrans', 
  sqlstr = 'select foo.*, p.partnumber, case when foo.pgroup=1 then p.description+\' (\'+foo.description+\')\' else foo.description end as itemname, \
    case when mov.tqty is null then 0 else mov.tqty end tqty \
  from (select i.id as item_id, i.description, case when fv.value is null then i.product_id else cast(fv.value as integer) end as product_id, \
      case when fv.value is null then 0 else 1 end as pgroup,  \
      sum(case when isnumeric(fv.notes)=1 then cast(fv.notes as real) else 1 end*i.qty) as pqty \
    from trans t \
    inner join item i on t.id = i.trans_id \
    left join fieldvalue fv on fv.ref_id = i.product_id and fv.fieldname = \'product_element\' \
    inner join product p on i.product_id = p.id \
    where i.deleted=0 and t.id = @trans_id \
    group by i.id, i.description, p.partnumber, p.description, case when fv.value is null then i.product_id else cast(fv.value as integer) end, \
    case when fv.value is null then 0 else 1 end) foo \
  inner join product p on foo.product_id = p.id \
  inner join groups pg on p.protype = pg.id and pg.groupvalue = \'item\' \
  left join (select i.id as item_id, mt.product_id, sum(case when dg.groupvalue=\'out\' then -mt.qty else mt.qty end) as tqty \
    from movement mt \
    inner join trans t on mt.trans_id = t.id \
    inner join groups dg on t.direction = dg.id \
    inner join link ln on ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'movement\') \
      and ln.ref_id_1 = mt.id and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'item\') \
    inner join item i on ln.ref_id_2 = i.id  \
    where mt.deleted = 0 and i.trans_id = @trans_id \
    group by i.id, mt.product_id) mov on foo.item_id = mov.item_id and foo.product_id = mov.product_id \
  order by foo.item_id;')
  
  nflex.insert(sqlkey = 'fTrans_getItemToolsView', engine = 'all', section = 'fTrans', 
  sqlstr = 'select t.id, tg.groupvalue as transtype, dg.groupvalue as direction, t.transnumber, cast(mv.shippingdate as date) as shippingdate \
    , case when msd.msg is null then dg.groupvalue else msd.msg end as direction_lang \
    , tl.serial, tl.description, tl.id as tool_id \
    , t.closed, mv.notes \
  from trans t \
  inner join movement mv on t.id = mv.trans_id \
  inner join tool tl on mv.tool_id = tl.id \
  inner join groups tg on t.transtype = tg.id and tg.groupvalue = \'waybill\' \
  inner join groups dg on t.direction = dg.id \
    left join ui_message msd on msd.fieldname = dg.groupvalue and  msd.secname = \'direction\' \
      and msd.lang = (select value from fieldvalue where fieldname = \'default_lang\') \
  left join link lnk on t.id = lnk.ref_id_1 and lnk.deleted=0 and lnk.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
       and lnk.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\') \
       left join trans lt on lnk.ref_id_2 = lt.id \
  where t.deleted = 0 and mv.deleted=0 and lt.id = @trans_id \
  order by shippingdate;')
  
  nflex.insert(sqlkey = 'fTrans_getItemsProp', engine = 'all', section = 'fTrans', 
  sqlstr = 'select ti.id as id, p.partnumber as partnumber, p.description as description, fv.notes as partcustomer \
        from item ti \
        inner join product p on ti.product_id = p.id \
        inner join trans t on ti.trans_id = t.id \
        left join fieldvalue fv on ref_id = p.id and fieldname = \'product_custpartnumber\' and cast(fv.value as integer) = t.customer_id \
        where t.id = @trans_id')
  
  nflex.insert(sqlkey = 'fTrans_getItemsProp', engine = 'mysql', section = 'fTrans', 
  sqlstr = 'select ti.id as id, p.partnumber as partnumber, p.description as description, fv.notes as partcustomer \
        from item ti \
        inner join product p on ti.product_id = p.id \
        inner join trans t on ti.trans_id = t.id \
        left join fieldvalue fv on ref_id = p.id and fieldname = \'product_custpartnumber\' and cast(fv.value as signed) = t.customer_id \
        where t.id = @trans_id')
  
  nflex.insert(sqlkey = 'fTrans_getMovementProp', engine = 'all', section = 'fTrans', 
  sqlstr = 'select mv.id as id, p.partnumber as partnumber, p.description as description \
        from movement mv \
        inner join product p on mv.product_id = p.id \
        where mv.trans_id = @trans_id')
  
  nflex.insert(sqlkey = 'fTrans_getMovementPropTool', engine = 'all', section = 'fTrans', 
  sqlstr = 'select mv.id as id, t.serial as partnumber, t.description as description \
        from movement mv \
        inner join tool t on mv.tool_id = t.id \
        where mv.trans_id = @trans_id')
  
  nflex.insert(sqlkey = 'fTrans_getNextNumber', engine = 'all', section = 'fTrans', 
  sqlstr = 'select min(id) as id from trans where transtype=@transtype and id > @id @where_str')
  
  nflex.insert(sqlkey = 'fTrans_getPaymentProp', engine = 'all', section = 'fTrans', 
  sqlstr = 'select ln.id, t.transnumber, g.groupvalue as direction \
  from link ln inner join trans t on ln.ref_id_2 = t.id inner join groups g on t.direction = g.id \
  where ln.deleted=0 and ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'payment\')  \
  and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\')  \
  and ln.ref_id_1 in (select id from payment where trans_id= @trans_id);')
  
  nflex.insert(sqlkey = 'fTrans_getPaymentView', engine = 'all', section = 'fTrans', 
  sqlstr = 'select t.id as id, tg.groupvalue as transtype, dg.groupvalue as direction, p.paiddate, pa.description, \
    t.transnumber, cast(af.value as real)*cast(rf.value as real) as amount, ln.id as link_id \
  from link ln  \
  inner join payment p on ln.ref_id_1 = p.id \
  inner join trans t on p.trans_id = t.id  \
  inner join groups tg on t.transtype = tg.id \
  inner join groups dg on t.direction = dg.id \
  inner join place pa on t.place_id = pa.id \
  inner join fieldvalue af on ln.id = af.ref_id and af.fieldname=\'link_qty\' \
  inner join fieldvalue rf on ln.id = rf.ref_id and rf.fieldname=\'link_rate\' \
  where ln.deleted=0 and ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'payment\')  \
  and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\')  \
  and ln.ref_id_2 = @trans_id  \
  order by p.paiddate;')
  
  nflex.insert(sqlkey = 'fTrans_getPaymentView', engine = 'mysql', section = 'fTrans', 
  sqlstr = 'select t.id as id, tg.groupvalue as transtype, dg.groupvalue as direction, p.paiddate, pa.description, \
    t.transnumber, cast(af.value as decimal)*cast(rf.value as decimal) as amount, ln.id as link_id \
  from link ln  \
  inner join payment p on ln.ref_id_1 = p.id \
  inner join trans t on p.trans_id = t.id  \
  inner join groups tg on t.transtype = tg.id \
  inner join groups dg on t.direction = dg.id \
  inner join place pa on t.place_id = pa.id \
  inner join fieldvalue af on ln.id = af.ref_id and af.fieldname=\'link_qty\' \
  inner join fieldvalue rf on ln.id = rf.ref_id and rf.fieldname=\'link_rate\' \
  where ln.deleted=0 and ln.nervatype_1 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'payment\')  \
  and ln.nervatype_2 = (select id from groups where groupname = \'nervatype\' and groupvalue = \'trans\')  \
  and ln.ref_id_2 = @trans_id  \
  order by p.paiddate;')
  
  nflex.insert(sqlkey = 'fTrans_getPrevNumber', engine = 'all', section = 'fTrans', sqlstr = 'select max(id) as id from trans where transtype=@transtype @where_str')
  
  nflex.insert(sqlkey = 'fTrans_getTransArch', engine = 'all', section = 'fTrans', 
  sqlstr = 'select @trans_id as trans_id,  \
    comp.custname as comp_name, comp.zipcode||\' \'||comp.city||\' \'||comp.street as comp_address,  \
    comp.taxnumber as comp_taxnumber, \
    cust.custname as cust_name, cust.zipcode||\' \'||cust.city||\' \'||cust.street as cust_address,  \
    cust.taxnumber as cust_taxnumber \
  from \
  (select c.custname, adr.zipcode, adr.city, adr.street, c.taxnumber \
  from customer c \
  left join (select ref_id as customer_id, case when zipcode is null then \'\' else zipcode end as zipcode, \
   case when city is null then \'\' else city end as city, \
    case when street is null then \'\' else street end as street from address  \
  where id in(select min(id) from address \
    where nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\') and deleted = 0 \
    group by ref_id)) adr on c.id=adr.customer_id \
  where c.id=1) comp, \
  (select c.custname, adr.zipcode, adr.city, adr.street, c.taxnumber \
  from customer c \
  left join (select ref_id as customer_id, case when zipcode is null then \'\' else zipcode end as zipcode, \
   case when city is null then \'\' else city end as city, \
    case when street is null then \'\' else street end as street from address  \
  where id in(select min(id) from address \
    where nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\') and deleted = 0 \
    group by ref_id)) adr on c.id=adr.customer_id \
  where c.id= @cust_id) cust')
  
  nflex.insert(sqlkey = 'fTrans_getTransArch', engine = 'mysql', section = 'fTrans', 
  sqlstr = 'select @trans_id as trans_id,  \
    comp.custname as comp_name, CONCAT(comp.zipcode, \' \', comp.city, \' \', comp.street) as comp_address,  \
    comp.taxnumber as comp_taxnumber, \
    cust.custname as cust_name, CONCAT(cust.zipcode, \' \', cust.city, \' \', cust.street) as cust_address,  \
    cust.taxnumber as cust_taxnumber \
  from \
  (select c.custname, adr.zipcode, adr.city, adr.street, c.taxnumber \
  from customer c \
  left join (select ref_id as customer_id, case when zipcode is null then \'\' else zipcode end as zipcode, \
   case when city is null then \'\' else city end as city, \
    case when street is null then \'\' else street end as street from address  \
  where id in(select min(id) from address \
    where nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\') and deleted = 0 \
    group by ref_id)) adr on c.id=adr.customer_id \
  where c.id=1) comp, \
  (select c.custname, adr.zipcode, adr.city, adr.street, c.taxnumber \
  from customer c \
  left join (select ref_id as customer_id, case when zipcode is null then \'\' else zipcode end as zipcode, \
   case when city is null then \'\' else city end as city, \
    case when street is null then \'\' else street end as street from address  \
  where id in(select min(id) from address \
    where nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\') and deleted = 0 \
    group by ref_id)) adr on c.id=adr.customer_id \
  where c.id= @cust_id) cust')
  
  nflex.insert(sqlkey = 'fTrans_getTransArch', engine = 'mssql', section = 'fTrans', 
  sqlstr = 'select @trans_id as trans_id,  \
    comp.custname as comp_name, comp.zipcode+\' \'+comp.city+\' \'+comp.street as comp_address,  \
    comp.taxnumber as comp_taxnumber, \
    cust.custname as cust_name, cust.zipcode+\' \'+cust.city+\' \'+cust.street as cust_address,  \
    cust.taxnumber as cust_taxnumber \
  from \
  (select c.custname, adr.zipcode, adr.city, adr.street, c.taxnumber \
  from customer c \
  left join (select ref_id as customer_id, case when zipcode is null then \'\' else zipcode end as zipcode, \
   case when city is null then \'\' else city end as city, \
    case when street is null then \'\' else street end as street from address  \
  where id in(select min(id) from address \
    where nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\') and deleted = 0 \
    group by ref_id)) adr on c.id=adr.customer_id \
  where c.id=1) comp, \
  (select c.custname, adr.zipcode, adr.city, adr.street, c.taxnumber \
  from customer c \
  left join (select ref_id as customer_id, case when zipcode is null then \'\' else zipcode end as zipcode, \
   case when city is null then \'\' else city end as city, \
    case when street is null then \'\' else street end as street from address  \
  where id in(select min(id) from address \
    where nervatype = (select id from groups where groupname=\'nervatype\' and groupvalue=\'customer\') and deleted = 0 \
    group by ref_id)) adr on c.id=adr.customer_id \
  where c.id= @cust_id) cust')
  
  nflex.insert(sqlkey = 'fTrans_getTransaudit', engine = 'all', section = 'fTrans', 
  sqlstr = "select au.supervisor from employee e \
    inner join ui_audit au on e.usergroup = au.usergroup \
    inner join groups nt on (au.nervatype=nt.id and nt.groupvalue='trans') \
    inner join groups st on (au.subtype=st.id and st.groupvalue=@transtype) \
    where e.id=@employee_id")
  
  nflex.insert(sqlkey = 'fTrans_getTransProp', engine = 'all', section = 'fTrans', 
  sqlstr = 'select t.id, p.pronumber, e.empnumber from trans t \
  left join project p on t.project_id = p.id left join employee e on t.employee_id = e.id \
  where t.id = @trans_id')
  
  nflex.insert(sqlkey = 'fTrans_getOrderFromShip', engine = 'all', section = 'fTrans', 
  sqlstr = "select max(i.trans_id) as id from movement mt \
    left join link iln on iln.nervatype_1 = (select id from groups where groupname = 'nervatype' and groupvalue = 'movement') \
    and iln.ref_id_1 = mt.id and iln.nervatype_2 = (select id from groups where groupname = 'nervatype' and groupvalue = 'item') \
    left join item i on iln.ref_id_2 = i.id and i.deleted=0 \
    where mt.deleted=0 and mt.trans_id= @trans_id")
  
  nflex.insert(sqlkey = 'fTrans_setClosed', engine = 'all', section = 'fTrans', sqlstr = 'update trans set closed=1 where id=@trans_id;')
  
  nflex.insert(sqlkey = 'TransDeliveryFilter_getResult', engine = 'all', section = 'fTrans', 
  sqlstr = 'select t.id, 0 as selected, tg.groupvalue as transtype, dg.groupvalue as direction, t.transnumber, t.transdate, c.custname,  \
    t.curr, sum(i.amount) as amount \
  from trans t \
  inner join groups tg on t.transtype = tg.id \
  inner join groups dg on t.direction = dg.id \
  left join customer c on t.customer_id = c.id \
  inner join item i on t.id = i.trans_id and i.deleted=0 \
  where t.deleted=0 and tg.groupvalue in(\'order\',\'worksheet\',\'rent\') @where_str \
  group by t.id, tg.groupvalue, dg.groupvalue, t.transnumber, t.transdate, c.custname, t.curr \
  order by t.transnumber;')