/****** Script for SelectTopNRows command from SSMS  ******/
-- 获得每个类别的热度
select a.*,b.class_id into  dbo.user_bought_history_new3
from dbo.user_bought_history_new2 
a left join dbo.dim_items_new b on a.item_id = b.item_id

select class_id,COUNT(*) num1,count(distinct item_id) num2
 from dbo.user_bought_history_new3 group by class_id order by num2 desc
 
 -- 测试集商品被哪些用户使用
 
 select a.item_id,isnull(b.user_id,-1) from dbo.test_items_new a left join dbo.user_bought_history_new3 b 
 on a.item_id=b.item_id order by a.item_id