drop table if exists [DATABASE_NAME].dbo.Suggestions
SELECT 
	ProductId,
	SuggestedProductId as SuggestionProductId,
	score
INTO [DATABASE_NAME].dbo.Suggestions
FROM (
	SELECT 
		ProductId,
		P.Name PName,
		SuggestedProductId,
		SP.Name SPName,
		1000 * score AS score,
		MatchingRules,	
		Rank() over(partition by ProductId order by score desc) as rank
	FROM (
		SELECT 
			TMatchingRules.ProductId, 
			MatchingC.ProductId as SuggestedProductId,			
			--SUM(MatchingC.score * (CASE WHEN IsFeaturedProduct >0 THEN 1.2 ELSE 1.0 END)) as score
			--AVG(MatchingC.score * (CASE WHEN IsFeaturedProduct >0 THEN 1.2 ELSE 1.0 END)) as score
			(AVG(MatchingC.score * (CASE WHEN IsFeaturedProduct >0 THEN 1.2 ELSE 1.0 END)) + MAX(MatchingC.score)) * (CASE WHEN SourceProduct.Price >= TargetProduct.Price THEN 1.0 ELSE ROUND(1 - (TargetProduct.Price - SourceProduct.Price ) / (TargetProduct.Price + SourceProduct.Price),2) END ) as score,
			COUNT(1) as MatchingRules
		FROM (
			SELECT *
			FROM (
				SELECT ProductId, 
					CARuleId, 
					count(1) as matchCount,
					SUM(IsFeaturedProduct) IsFeaturedProduct
				FROM (
					SELECT pgm.id as ProductId,
						groupId,
						RA.RuleId as CARuleId,
						IsFeaturedProduct
					FROM O_C_Rules_Antecedents RA
					JOIN product_group_mapping pgm on pgm.groupId = RA.antecedents
				)TT
				group by ProductId, CARuleId
			)TRules
			JOIN O_C_Rules RRules on TRules.CARuleId = RRules.id
			where matchCount / RRules.[antecedents length] >= 1
		) TMatchingRules
		JOIN Consequent_Products MatchingC on TMatchingRules.CARuleId = MatchingC.RuleId
		JOIN Product SourceProduct on SourceProduct.Id = TMatchingRules.ProductId
		JOIN Product TargetProduct on TargetProduct.Id = MatchingC.ProductId
		GROUP BY TMatchingRules.ProductId, MatchingC.ProductId, SourceProduct.Price, TargetProduct.Price
	) T
	JOIN Product P on p.id = T.productId
	JOIN Product SP on SP.id = T.SuggestedProductId
	WHERE SP.Published = 1 and SP.Deleted = 0
)TGPD
where TGPD.rank <= 50