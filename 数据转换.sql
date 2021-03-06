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
 ----------------------------------------------------------------
  --类别关系统计
  -----找到搭配商品对 
  select a.item_id item_id1,b.item_id item_id2 
  into [tianchi].[dbo].[dim_fashion_matchsets3]
  from [tianchi].[dbo].[dim_fashion_matchsets2] a left join 
   [tianchi].[dbo].[dim_fashion_matchsets2] b on a.id1=b.id1 and a.id2 != b.id2;
  ----找到类别的关系
  select a.*,b.class_id class_id1,b.word_str word_str1,c.class_id class_id2,c.word_str word_str2  
  into [tianchi].[dbo].[dim_fashion_matchsets4]
  from [tianchi].[dbo].[dim_fashion_matchsets3] a 
  left join [tianchi].dbo.dim_items_new b on(a.item_id1=b.item_id)
  left join [tianchi].dbo.dim_items_new c on(a.item_id2=c.item_id);
  
  -- 统计 类别关系
  select class_id1,class_id2,COUNT(distinct item_id1+0.0001*item_id2), COUNT(*) num2
  from [tianchi].[dbo].[dim_fashion_matchsets4] a 
  group by class_id1,class_id2 order by class_id1,class_id2
  select * from [tianchi].[dbo].[dim_fashion_matchsets4]
  -- 词组 
  select word_str1,word_str2, COUNT(*) num2
  from [tianchi].[dbo].[dim_fashion_matchsets4] a 
  group by word_str1,word_str2 order by num2 desc