--DROP TABLE #TEMP_ConsWithScore
				SELECT 
					R.id AS RuleId,
					Spcm.ProductId as SuggestionProductId,					
						SourceCategory.Level + 
						confidence * (CASE WHEN SourceCategory.TopLevelId = TargetCategory.TopLevelId THEN 0.8 else 1.0 end )
								* (CASE WHEN SourceCategory.TopLevelId = TargetCategory.TopLevelId AND SourceCategory.Level > TargetCategory.Level THEN 0.1 else 1.0 end  )
								* (CASE WHEN SourceCategory.Level <= TargetCategory.Level THEN 1.0 else 0.5 end ) 
							as score,
					'Order_Category' as [SuggestionType],
					10 as SuggestionLevel
INTO #TEMP_ConsWithScore
				FROM O_C_Rules_single R 
				JOIN O_C_Rules_single_antecedents AR on AR.ruleid=R.id 
				JOIN CategoryTree SourceCategory on SourceCategory.id = AR.itemid
				JOIN O_C_Rules_single_consequents CR on R.id = CR.ruleid
				JOIN Product_Category_Mapping Spcm on Spcm.CategoryId = CR.itemid
				JOIN CategoryTree TargetCategory on TargetCategory.id = spcm.categoryid
				JOIN Product P On Spcm.ProductId = P.id		   
				WHERE p.Published = 1 and p.Deleted = 0


TRUNCATE TABLE [DATABASE_NAME].dbo.Suggestions_Single

INSERT INTO [DATABASE_NAME].dbo.Suggestions_Single
SELECT 
	ProductId,
	SuggestionProductId,
	score

FROM (

	SELECT ProductId,
		SuggestionProductId,
		Score
	FROM (
		SELECT *,
				Rank() over(partition by ProductId order by Score desc) as rank
		FROM(
			select 


			PCM.productid ProductId,
							TCWS.SuggestionProductId,
							MAX(TCWS.Score) as Score
			FROM Product_Category_Mapping PCM				
			JOIN O_C_Rules_single_antecedents AR on PCM.CategoryId = AR.itemid
			JOIN #TEMP_ConsWithScore TCWS ON TCWS.RuleId = AR.ruleId
			GROUP BY PCM.productid, TCWS.SuggestionProductId
		)TOC
	)TOCWITHRANK

	WHERE rank <= 5
--AND productid = 3704
UNION ALL

	SELECT 
		AR.itemid as ProductId,
		CR.itemid as SuggestionProductId,
		[confidence] + 1000 as score

	FROM O_P_Rules_Single R
	join O_P_Rules_Single_Antecedents AR on R.Id=AR.[Ruleid]
	join O_P_Rules_Single_Consequents CR on R.Id=CR.[Ruleid]
	JOIN Product P On AR.itemid = P.id
	WHERE p.Published = 1 and p.Deleted = 0
)T


DROP TABLE #TEMP_ConsWithScore