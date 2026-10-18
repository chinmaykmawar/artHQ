select * from product_image pi 
join product_image_marketplaces pim on pi.id =pim.imagedata_id
join marketplace m on pim.marketplace_id=m.id

where product_id=86;
--pi.public_id,pi.display_order, m.code