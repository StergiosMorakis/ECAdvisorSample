select
	TTT.DividerId,
	TTT.ItemId,
	1 Quantity
from(
	select 
		oi.OrderId [DividerId],
		pgm.groupId [ItemId],
        year(o.createdonutc) [Year],
        month(o.createdonutc) [Month]
	from orderitem oi
	join [Order] o on o.id = oi.OrderId
	join Product_Group_Mapping pgm on pgm.id = oi.ProductId
)TTT
where TTT.itemid is not null
group by TTT.DividerId, TTT.ItemId
order by TTT.DividerId, TTT.ItemId