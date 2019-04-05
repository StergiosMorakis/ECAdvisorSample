DROP TABLE IF EXISTS dbo.E0009_Suggestions
CREATE TABLE [dbo].[E0009_Suggestions](
  [Id] [int] IDENTITY(1,1) NOT NULL,
  [ProductId] [int] NOT NULL,
  [SuggestionProductId] [int] NOT NULL,
  [score] [float] NOT NULL,
  [Reason] [nvarchar](124) NOT NULL
) ON [PRIMARY]
INSERT INTO dbo.E0009_Suggestions 
(ProductId, SuggestionProductId, score, Reason)
select *
from (
  SELECT kcA.ProductId as ProductId 
    , kcC.ProductId as SuggestionProductId 
    , MAX(R.confidence) 
      * (CASE WHEN SourceProduct.Price >= TargetProduct.Price THEN 1.0 ELSE ROUND(1 - (TargetProduct.Price - SourceProduct.Price ) / (TargetProduct.Price + SourceProduct.Price), 2) END )
       as score
    , 'Present Rule' as Reason
  FROM [E0009_Cl2] R
  left join E0009_Cl2_Ant A on R.id = A.RuleId  
  left join E0009_Cl2_Con C on R.id = C.RuleId
  left join [dbo].[Kmeans_withManufacturer_Clustering] kcA on kcA.Cluster = A.antecedents
  left join Product SourceProduct  ON kcA.productId = SourceProduct.Id
  left join [dbo].[Kmeans_withManufacturer_Clustering] kcC on kcC.Cluster = C.consequents
  left join Product TargetProduct  ON kcC.productId = TargetProduct.Id  
  WHERE TargetProduct.Published = 1 and TargetProduct.Deleted = 0
  GROUP BY kcA.ProductId,kcC.ProductId, SourceProduct.Price, TargetProduct.Price
UNION ALL
  SELECT kcA.ProductId as ProductId 
    , nearCluster.ProductId as SuggestionProductId 
    , MAX(R.confidence) 
      * (CASE WHEN SourceProduct.Price >= TargetProduct.Price THEN 1.0 ELSE ROUND(1 - (TargetProduct.Price - SourceProduct.Price ) / (TargetProduct.Price + SourceProduct.Price),2) END )
      * (1.0 - kcC.Distance)
	  as score
    , 'Consequent-Nearest Rule'  as Reason
  FROM [E0009_Cl2] R
  left join E0009_Cl2_Ant A on R.id = A.RuleId  
  left join E0009_Cl2_Con C on R.id = C.RuleId
  left join [dbo].[Kmeans_withManufacturer_Clustering] kcA on kcA.Cluster = A.antecedents
  left join Product SourceProduct  ON kcA.productId = SourceProduct.Id
  left join [dbo].[Kmeans_withManufacturer_Clustering] kcC on kcC.Cluster = C.consequents
  left join [dbo].[Kmeans_withManufacturer_Clustering] nearCluster on nearCluster.Cluster = kcC.nearCluster  
  left join Product TargetProduct  ON nearCluster.productId = TargetProduct.Id  
  WHERE TargetProduct.Published = 1 and TargetProduct.Deleted = 0
  GROUP BY kcA.ProductId,nearCluster.ProductId, SourceProduct.Price, TargetProduct.Price , kcC.Distance
UNION ALL
  SELECT nearCluster.ProductId as ProductId 
    , kcC.ProductId as SuggestionProductId 
    , MAX(R.confidence) 
      * (CASE WHEN SourceProduct.Price >= TargetProduct.Price THEN 1.0 ELSE ROUND(1 - (TargetProduct.Price - SourceProduct.Price ) / (TargetProduct.Price + SourceProduct.Price),2) END )
      * (1.0 - kcA.Distance)
	  as score      
    , 'Andecedent-Nearest Rule'  as Reason
  FROM [E0009_Cl2] R
  left join E0009_Cl2_Ant A on R.id = A.RuleId  
  left join E0009_Cl2_Con C on R.id = C.RuleId
  left join [dbo].[Kmeans_withManufacturer_Clustering] kcA on kcA.Cluster = A.antecedents
  left join [dbo].[Kmeans_withManufacturer_Clustering] nearCluster on nearCluster.Cluster = kcA.nearCluster
  left join Product SourceProduct  ON nearCluster.productId = SourceProduct.Id
  left join [dbo].[Kmeans_withManufacturer_Clustering] kcC on kcC.Cluster = C.consequents  
  left join Product TargetProduct  ON kcC.productId = TargetProduct.Id
  WHERE TargetProduct.Published = 1 and TargetProduct.Deleted = 0
  GROUP BY nearCluster.ProductId, kcC.ProductId, SourceProduct.Price, TargetProduct.Price, kcA.Distance
)T