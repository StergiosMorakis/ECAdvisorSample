drop table if exists Product_Category_Mapping_Desc
select productId, categoryId, lvl, isFeaturedProduct
into Product_Category_Mapping_Desc
from (
	select distinct
		pcm.ProductId productId,
		c.id categoryId,		
		c.name [ItemId],
		ct.level lvl,
		max(ct.level)over(partition by pcm.ProductId) maxlvl,
		pcm.IsFeaturedProduct
	from Product_Category_Mapping pcm
	join category c on pcm.categoryid=c.id
	join CategoryTree ct on ct.Id=pcm.categoryid
) t where lvl=maxlvl