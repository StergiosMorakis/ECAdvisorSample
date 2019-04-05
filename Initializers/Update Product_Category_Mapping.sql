drop table if exists #TEMP_ProductCategoryMapping
drop table if exists Product_Category_Mapping
select productId,
	categoryId,
	C2.Id as parent2,
	C3.Id as parent3,
	C4.Id as parent4
INTO #TEMP_ProductCategoryMapping
FROM Product_Category_Mapping as l1
LEFT JOIN Category c1 on c1.id = l1.CategoryId
LEFT JOIN Category c2 on c2.id = c1.ParentCategoryId
LEFT JOIN Category c3 on c3.id = c2.ParentCategoryId
LEFT JOIN Category c4 on c4.id = c3.ParentCategoryId

select distinct productid, categoryid 
INTO Product_Category_Mapping
FROM(
select productid, categoryId as categoryid
FROM #TEMP_ProductCategoryMapping
UNION ALL 
select productid, parent2 as categoryid
FROM #TEMP_ProductCategoryMapping
UNION ALL 
select productid, parent3 as categoryid
FROM #TEMP_ProductCategoryMapping
UNION ALL 
select productid, parent4 as categoryid
FROM #TEMP_ProductCategoryMapping
) T
where  categoryid is not null