select
	T.DividerId,
	T.ItemId,
	1 Quantity
from(
	select 
		oi.OrderId [DividerId],
		'C'+cast(pcm.CategoryId as varchar) [ItemId]
	from [Order] o
	join orderitem oi on o.id = oi.OrderId
	join Product_Category_Mapping_Desc pcm on pcm.productid=oi.productid
)T
group by T.DividerId,T.ItemId