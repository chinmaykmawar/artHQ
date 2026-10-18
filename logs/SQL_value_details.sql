select mf.name,mf.description, mfm.value_type, mfm.value, msf.column_order
from marketplace_field mf
join marketplace_subcategory_field msf on mf.id=msf.marketplace_field_id
join marketplace_field_mapping mfm on msf.id=mfm.marketplace_subcategory_field_id
where mf.name like '%Browse%'
