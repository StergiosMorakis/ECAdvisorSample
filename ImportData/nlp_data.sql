        Select 
            p.id AS productId
            , ISNULL(p.name,'') AS name
            , ISNULL(p.shortDescription,'') AS shortDescription
            , ISNULL(p.FullDescription, '') AS fullDescription
            , ISNULL(ugc.Categories, '') AS Categories
            , ISNULL(ugc.Manufacturers, '') AS Manufacturers
            , ISNULL(ugc.Taggs, '') AS Taggs
            , ISNULL(psm.specs, '') AS specs
            , CAST(TTT.published AS INT) AS published
            , TTT.ordered AS ordered
        from (
            Select 
                isnull(T.id,TT.id) as productId
                , isnull(T.Published,1) as published
                , isnull(T.Ordered,0) as ordered 
            from ( 
                select distinct p.id as id, p.Published, 1 as Ordered from orderitem oi left join product p on oi.ProductId=p.id
            ) T full outer join (
                select id from product where Published=1
            ) TT 
            on T.id=TT.id
        ) TTT
            left join product p on p.id=TTT.productId
            left join Unique_Group_Combination ugc on ugc.ProductId=p.id
            left join Product_Specs_Mapping psm on psm.productid=p.id