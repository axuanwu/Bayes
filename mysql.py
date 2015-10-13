# coding=utf-8
import pyodbc
import numpy as np
import os

con=pyodbc.connect("DSN=axuanwusqlsever;UID=sa;pwd=2008123456")
curser = con.cursor()
sql = "select  a.*,b.userid  into [baoxian].[dbo].[test_items2]" +\
      "from  [baoxian].[dbo].[test_items] a left join "+\
      "[baoxian].[dbo].[user_bought_history] b on a.itemid=b.itemid"
print sql
try:
    curser.execute(sql)
except:
    pass
w_stream = open("E:\\gitshell\\tianchi\\test_items.txt",'w')
curser.execute("select itemid,userid from [baoxian].[dbo].[test_items2] group by itemid,userid order by itemid,userid")
for i in curser:
    w_stream.writelines(str(i[0])+'\t'+str(i[1])+'\n')
w_stream.close()
curser.close()
con.close()