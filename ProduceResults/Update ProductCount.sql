--ALTER TABLE O_C_Rules
--add AntecedentsProductCount int not null default 0

--ALTER TABLE O_C_Rules
--add consequentsProductCount int not null default 0
--GO


UPDATE RR
SET RR.AntecedentsProductCount = TCalc.AntecedentsProductCount
FROM O_C_Rules RR 
JOIN (
	SELECT 
		RuleId, 
		COUNT(1) as AntecedentsProductCount
	FROM (
		SELECT R.Id as RuleId, 
				R.confidence,
				pgm.id as ProductId,
				R.[antecedents length],
				Count(1) as matchCount
		FROM product_group_mapping pgm	
		left join O_C_Rules_antecedents oa 
			on oa.antecedents = pgm.groupId
		JOIN O_C_Rules R 
			on oa.ruleId = R.id
		group by R.Id, R.confidence, pgm.Id, R.[antecedents length]
	)TT
	WHERE matchCount = [antecedents length]
	GROUP BY RuleId, confidence
) Tcalc
on Tcalc.RuleId = RR.Id

UPDATE RR
SET RR.ConsequentsProductCount = TCalc.consequentsProductCount
FROM O_C_Rules RR 
JOIN (
	SELECT 
		RuleId, 
		COUNT(1) as consequentsProductCount
	FROM (
		SELECT R.Id as RuleId, 
				R.confidence,
				pgm.id as ProductId,
				R.[consequents length],
				Count(1) as matchCount
		FROM product_group_mapping pgm	
		left join O_C_Rules_consequents oa on oa.consequents = pgm.groupId
		JOIN O_C_Rules R on oa.ruleId = R.id
		group by R.Id, R.confidence, pgm.Id, R.[consequents length]
	)TT
	WHERE matchCount = [consequents length]
	GROUP BY RuleId, confidence
) Tcalc
on Tcalc.RuleId = RR.Id


