select p.product_id, m.code, pm.* from product p
join product_marketplace pm on p.id=pm.product_id
join marketplace m on pm.marketplace_id=m.id
--where pm.price=400
where p.product_id='JBR30007PiW'
