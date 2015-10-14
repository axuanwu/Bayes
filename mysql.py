# coding=utf-8
import pyodbc
import numpy as np
import os

con=pyodbc.connect("DSN=axuanwusqlsever;UID=sa;pwd=2008123456")
curser = con.cursor()
if True:
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
path = "E:\\gitshell\\tianchi\\dim_fashion_matchsets.txt"
opath = "E:\\gitshell\\tianchi\\dim_fashion_matchsets2.txt"
read_stream = open(path, 'r')
write_stream = open(opath, 'w')
for line in read_stream:
    aaa = line.rstrip().split(' ')
    key = int(aaa[0])
    item_list = aaa[1].rstrip().split(';')
    for i in xrange(0, len(item_list)):
        temp_str = key + '\t' + str(i) + '\t'
        item_list2 = item_list[i].split(',')
        for temp_item in item_list2:
            write_stream.writelines(temp_str + temp_item + '\n')
    pass

curser.close()

con.close()