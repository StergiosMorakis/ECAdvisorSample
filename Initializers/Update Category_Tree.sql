drop table if exists CategoryTree;
;WITH [CategoryTree] AS (
	SELECT [Category].[Id] AS [Id], 
		[Category].Name,
		1 as [Level],
		Convert(nvarchar(max),[Category].Name ) as FullName,
		[Category].[Id]  as [TopLevelId]
    FROM [Category] WHERE [Category].[ParentCategoryId] = 0
    UNION ALL
    SELECT [Category].[Id] AS [Id], 
		[Category].Name,
		[CategoryTree].[Level] + 1 as [Level],
		[CategoryTree].FullName + ' > ' + [Category].Name as FullName,
		[CategoryTree].[TopLevelId] as [TopLevelId]
    FROM [Category]
        INNER JOIN [CategoryTree] ON [CategoryTree].[Id] = [Category].[ParentCategoryId]
)
select * 
INTO CategoryTree
from [CategoryTree]