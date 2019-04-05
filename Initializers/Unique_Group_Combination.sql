drop table if exists Unique_Group_Combination
select 
	p.id as ProductId	
	, STRING_AGG (GM.groupid,'|') 
		WITHIN GROUP ( ORDER BY GM.groupid ASC )
		as allgroups
	, STRING_AGG (Case when gm.groupId like 'c%' then gm.groupId else null end,'|') 
		WITHIN GROUP ( ORDER BY GM.groupid ASC )
		as Categories
	, STRING_AGG (Case when gm.groupId like 'm%' then gm.groupId else null end,'|') 
		WITHIN GROUP ( ORDER BY GM.groupid ASC )
		as Manufacturers
	, STRING_AGG (Case when gm.groupId like 't%' then gm.groupId else null end,'|') 
		WITHIN GROUP ( ORDER BY GM.groupid ASC )
		as Taggs
	, MAX(ISNULL(IsFeaturedProduct,0)) AS IsFeaturedProduct
into Unique_Group_Combination
from product p
	JOIN Product_Group_Mapping GM on GM.id = p.id
group by p.id