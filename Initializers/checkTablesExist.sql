-- comma sensitive
select count(1)
from information_schema.tables
where table_name in ('CategoryTree'
					, 'Product_Category_Mapping'
					, 'Product_Category_Mapping_Desc'
					, 'Product_Specs_Mapping'
					, 'Product_Group_Mapping'
					, 'Unique_Group_Combination'
					, 'Ratings')
