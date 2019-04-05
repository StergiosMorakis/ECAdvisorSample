drop table if exists Product_Specs_Mapping
select T.id productId
	,  STRING_AGG ( T.attr, ' ') Specs 
into Product_Specs_Mapping
from (
	select p.id
	, REPLACE(isnull('S'+convert(varchar, s.id ) + 'SO'+convert(varchar, so.id ),''), ' ', '') as attr
	from product p 
	left join Product_SpecificationAttribute_Mapping psm 
		on psm.ProductId=p.id
	left join SpecificationAttributeOption so 
		on so.id=psm.SpecificationAttributeOptionId
	left join SpecificationAttribute s 
		on s.Id=so.SpecificationAttributeId
) T group by T.id