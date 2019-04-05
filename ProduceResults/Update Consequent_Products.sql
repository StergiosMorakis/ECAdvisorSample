drop table if exists Consequent_Products
SELECT 
	CaRuleId as RuleId,
	ProductId, 
	score * (CASE WHEN isnull(AntecedentsProductCount,1) < isnull(ConsequentsProductCount,1) then 0.5 else 1.0 END ) Score
INTO Consequent_Products
FROM (
	SELECT  *
		, confidence / ( isnull(rrules.AntecedentsProductCount,1) + isnull(rrules.ConsequentsProductCount,1))  as score
	FROM (
		SELECT ProductId, 
			CARuleId, 
			count(1) as matchCount
		FROM (
			SELECT pgm.id as ProductId,
					groupId,
					RA.RuleId as CARuleId
			FROM O_C_Rules_consequents RA
			JOIN product_group_mapping pgm on pgm.groupId = RA.consequents		
		)TT
		where CARuleId is not null
		group by ProductId,  CARuleId
	) AS TRules
	JOIN O_C_Rules RRules on TRules.CARuleId = RRules.id
	where matchCount / RRules.[consequents length] >= 1
)TTT