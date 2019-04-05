drop table if exists Product_Group_Mapping
SELECT *
into Product_Group_Mapping
FROM(

		select p.id, 'C' + Convert(nvarchar(10),cm.CategoryId) as groupId, ISNULL(cm.IsFeaturedProduct,0) IsFeaturedProduct
		from Product p
		join Product_Category_Mapping_Desc cm on cm.ProductId = p.Id 							
	UNION ALL 
		select p.id,  'M' + Convert(nvarchar(10), mm.ManufacturerId) as groupId , ISNULL(IsFeaturedProduct,0) IsFeaturedProduct
		from Product p
		join Product_Manufacturer_Mapping mm on mm.ProductId = p.Id
	UNION ALL 
		select p.id,  'T' + Convert(nvarchar(10), ptm.ProductTag_Id) as groupId , 0 as IsFeaturedProduct
		from Product p
		join Product_ProductTag_Mapping ptm on ptm.Product_Id = p.Id
)T