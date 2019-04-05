select
	'O_' + Convert(nvarchar(10),T.DividerId) as DividerId,
	T.ItemId,
	1 Quantity
from(
	select
		oi.OrderId [DividerId],
		kc.Cluster [ItemId],
		dense_rank() over (partition by  oi.OrderId order by kc.Cluster)+  dense_rank() over (partition by oi.OrderId order by kc.Cluster desc) - 1 as ItemsInOrder
	from orderitem oi
	join [Order] o on o.id = oi.OrderId
	join [dbo].[Kmeans_withManufacturer_Clustering] kc on kc.ProductId = oi.ProductId
	WHERE O.CreatedOnUtc > DATEADD(year,-2,GETDATE()) AND oi.OrderId % 10 != 0
)T
WHERE ItemsInOrder >1
group by T.DividerId,T.ItemId
UNION ALL
select 'CS_' + Convert(nvarchar(10),Id) as DividerId,
	kc.Cluster as ItemId,
	1 Quantity
from CrossSellProduct
join [dbo].[Kmeans_withManufacturer_Clustering] kc on kc.ProductId = CrossSellProduct.ProductId1
UNION ALL
select 'CS_' + Convert(nvarchar(10),Id) as DividerId,
	kc.Cluster as ItemId,
	1 Quantity
from CrossSellProduct
join [dbo].[Kmeans_withManufacturer_Clustering] kc on kc.ProductId = CrossSellProduct.ProductId2
UNION ALL

  select 'R_' + Convert(nvarchar(10),OrderId) as DividerId,
	kc.Cluster as ItemId,
	1 Quantity
  from [Ratings] R
  JOIN OrderItem OI ON R.sourceId = OI.OrderId
	join [dbo].[Kmeans_withManufacturer_Clustering] kc on kc.ProductId = OI.ProductId
	WHERE R.rating = 3
UNION ALL
select 'R_' + Convert(nvarchar(10),sourceId) as DividerId,
	kc.Cluster as ItemId,
	1 Quantity
  from [Ratings] R
	join [dbo].[Kmeans_withManufacturer_Clustering] kc on kc.ProductId = R.ProductSuggestedId
	WHERE R.rating = 3

UNION ALL

	SELECT DividerId, ItemId, Quantity FROM(
	 SELECT DividerId, ItemId, Quantity, COUNT(1) OVER (partition by DividerId) as items
	 FROM(
	  select 'SC_' + Convert(nvarchar(10),CustomerId) as DividerId,
		kc.Cluster as ItemId,
		SUM(Quantity) Quantity
	  from [ShoppingCartItem] SCI
		join [dbo].[Kmeans_withManufacturer_Clustering] kc on kc.ProductId = SCI.ProductId
		GROUP BY CustomerId, kc.Cluster
		)T 
	)TT WHERE items > 1


order by DividerId