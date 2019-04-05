	select
        t.DividerId,
        t.ItemId,
        t.Quantity
    from (
        select 
            year(o.createdonutc) [Year],
            month(o.createdonutc) [Month], 
            o.id [DividerId], 
            oi.productid [ItemId], 
            count(oi.id) over(partition by o.id) [Quantity]
        from 
            [orderitem] as oi 
        join [order] o 
            on oi.orderid=o.id
        join product p
            on p.id=oi.productid
        where
            p.deleted=0
    ) T where t.quantity>1