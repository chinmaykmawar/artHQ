select mf.name, STRING_AGG(mvv.value, ', 'ORDER BY mvv.value) AS valid_values, mf.description
from marketplace_field mf
join marketplace_valid_value mvv on mf.id=mvv.marketplace_field_id
where mf.name in ('Style','Theme')
group by mf.name,mf.description
order by mf.name
