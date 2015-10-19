# coding=utf-8
"""
商品搭配在购物记录中的特征统计与发现
"""
import pyodbc
import numpy as np
import os

con=pyodbc.connect("DSN=axuanwusqlsever;UID=sa;pwd=2008123456")
curser = con.cursor()
if False:
    # 对需要测试的的商品列表找出其关联的所有用户，病按照用户排序后输出文本，方便后续计算
    sql = "select  a.*,b.userid  into [baoxian].[dbo].[test_items2]" + \
          "from  [baoxian].[dbo].[test_items] a left join " + \
          "[baoxian].[dbo].[user_bought_history] b on a.itemid=b.itemid"
    print sql
    try:
        curser.execute(sql)
    except:
        pass
    w_stream = open("E:\\gitshell\\tianchi\\test_items.txt", 'w')
    curser.execute(
        "select itemid,userid from [baoxian].[dbo].[test_items2] group by itemid,userid order by itemid,userid")
    for i in curser:
        w_stream.writelines(str(i[0]) + '\t' + str(i[1]) + '\n')
    w_stream.close()


# 统计 所有的的搭配数据 计算 搭配的产品主要的购买距离上的关系
# 商品搭配数据
def my_ShangPinGuanLian(curser):
    path = "E:\\gitshell\\tianchi2\\dim_fashion_matchsets.txt"
    opath = "E:\\gitshell\\tianchi2\\dim_fashion_matchsets2.txt"
    read_stream = open(path, 'r')
    write_stream = open(opath, 'w')
    for line in read_stream:
        aaa = line.rstrip().split(' ')
        key = int(aaa[0])
        item_list = aaa[1].rstrip().split(';')
        for i in xrange(0, len(item_list)):
            temp_str = str(key) + '\t' + str(i) + '\t'
            item_list2 = item_list[i].split(',')
            for temp_item in item_list2:
                write_stream.writelines(temp_str + temp_item + '\n')
    read_stream.close()
    write_stream.close()
    # jianbiao
    table_name = "[baoxian].[dbo].[dim_fashion_matchsets]"
    curser.execute("drop table " + table_name)
    sql = "create table " + table_name + "(id1 int,id2 int,item int)"
    print sql
    curser.execute(sql)
    sql = "     BULK INSERT " + table_name + "   FROM '" + opath \
          + "' WITH (FIELDTERMINATOR = '\t', ROWTERMINATOR = '\n')"
    print sql
    curser.execute(sql)
    table_name2 = "[baoxian].[dbo].[dim_fashion_matchsets2]"
    curser.execute("drop table " + table_name2)
    sql = "select a.item item1, b.item item2 into " + table_name2 + " from " + table_name + " a left join " + table_name \
          + " b on (a.id1=b.id1 and a.id2!=b.id2)"
    print sql
    curser.execute(sql)
    curser.execute("commit")


# my_ShangPinGuanLian(curser)

# 统计商品搭配之间的区别距离
def my_tongJi(curser):
    table_name1 = "[baoxian].[dbo].[dim_fashion_matchsets]"  # 记录商品搭配的表格
    table_name2 = "[baoxian].[dbo].[user_bought_history]"  # 记录购买记录的数据
    table_name3 = "[baoxian].[dbo].[user_bought_history_ex]"
    sql = "select a.*,b.id1,b.id2 into " + table_name3 + " from " + table_name2 \
          + " a left join " + table_name1 + " b on a.itemid=b.item "
    try:
        curser.execute(sql)
    except:
        print sql

    table_name4 = "[baoxian].[dbo].[user_bought_history_ex2]"  # 记录数
    sql = "select a.*,row_number()over(partition by userid order by [buy_date]) order_num into " \
          + table_name4 + " from " + table_name3 + " a"
    try:
        curser.execute(sql)
    except:
        print sql  # [userid] ,[itemid],[buy_date],id1,id2,order_num
    table_name5 = "[baoxian].[dbo].[user_bought_history_ex3]"  # 记录数
    sql = "select * into " + table_name5 + "from " + table_name4 + " where id1 is not null "
    try:
        curser.execute(sql)
        curser.execute("commit")
    except:
        print sql

    # 关联
    table_name6 = "[baoxian].[dbo].[user_bought_history_ex4]"  # 记录数
    sql = "select a.*,b.itemid itemid2,b.buy_date buy_date2,b.id1 id11," \
          + "b.id2 id22,b.order_num order_num2,datediff(DAY,a.buy_date,b.buy_date) day_diff," \
          + "b.order_num-a.order_num order_diff into " + table_name6 \
          + " from " + table_name5 + " a left join " + table_name4 + " b on a.userid = b.userid and ABS(b.order_num-a.order_num)<=100 and ABS(datediff(DAY,a.buy_date,b.buy_date))<=30"
    try:
        curser.execute(sql)
        curser.execute("commit")
    except:
        print sql



# my_tongJi(curser)

def tongji3(curser):
    sql = """select c.[class_id],isnull(sum(c.num),0)num1,COUNT(*) num2 from (SELECT a.[item_id]
            ,a.[class_id]
            ,b.num,b.[ranknum]
            FROM [axuanwu].[dbo].[dim_items2] a left join [baoxian].[dbo].[item_hot] b
            on a.item_id =b.itemid) c group by c.[class_id] order by num2 desc """
    w_stream = open("E:\\gitshell\\tianchi\\class_hot.txt", 'w')
    print sql
    curser.execute(sql)
    for i in curser:
        w_stream.writelines(str(i[0]) + '\t' + str(i[1]) + '\t' + str(i[2]) + '\n')
    w_stream.close()


# tongji3(curser)

# 统计数据库中相关搭配 与 购买顺序的的关系
def my_tongji2():
    table_name6 = "[baoxian].[dbo].[user_bought_history_ex4]"  # 记录数
    sql = "select order_diff,count(*) all_num,sum(case when id1=id11 and id2!=id22 then 1 else 0 end) good_num" \
          + ",1.0*sum(case when id1=id11 and id2!=id22 then 1 else 0 end)/count(*) abc from " + table_name6 \
          + " where order_diff !=0 group by order_diff order by order_diff "
    print sql
    sql = "select day_diff,count(*) all_num,sum(case when id1=id11 and id2!=id22 then 1 else 0 end) good_num" \
          + ",1.0*sum(case when id1=id11 and id2!=id22 then 1 else 0 end)/count(*) abc from " + table_name6 \
          + " where order_diff !=0 group by day_diff order by day_diff "
    print sql


my_tongji2()
curser.close()

con.close()