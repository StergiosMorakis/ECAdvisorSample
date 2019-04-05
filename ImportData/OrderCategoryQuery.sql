	select
		TTT.DividerId,
		TTT.ItemId,
		1 Quantity
	from(
		select 
			oi.OrderId [DividerId],
			'C'+cast(pcm.CategoryId as varchar) [ItemId],
           	year(o.createdonutc) [Year],
           	month(o.createdonutc) [Month]
		from orderitem oi
		join [Order] o on o.id = oi.OrderId
		join Product_Category_Mapping pcm on pcm.ProductId = oi.ProductId
		where o.createdonutc>'2018-10-01'
	)TTT 
	group by TTT.DividerId,TTT.ItemId