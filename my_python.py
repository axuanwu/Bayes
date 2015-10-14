# coding=utf-8
__author__ = '01053185'
import os
import numpy as np
import time
import datetime
from pro_estimate import Pro_estimate

class READ_Bought_History():
    def __init__(self):
        self.data_dir = 'E:\\gitshell\\tianchi'
        self.user_dict = {}
        self.user_num = -1
        self.record_num = -1  # 记录最大编号 +1 为购买记录数
        self.user_array = np.zeros((2000000, 2), int)
        self.user_item_array = np.zeros((20000000, 2), int)
        # 商品热度统计数据
        self.item_num = -1  # 记录最大编号 +1为商品数
        self.item_dict = {}
        self.item_array = np.zeros((2000000,2),int)
        self.item_user_list = []
        # 商品分类信息
        self.item_class = np.zeros([0] * 20)
        self.class_dict = {}
        self.class_num = -1  # 记录最大编号 +1为分类数
        # 热度排行初过滤参数  只对最畅销的 n 个商品进行精细计算
        self.top_k = 20000
        self.simple = True
        # 分类别关联性 商品热度统计
        self.num_k = 5  # 邻近的num_k个自身算第一个 被认为有关联
        self.like_matrix = np.zeros((10, 10), int)  # 存储不同分类下的
        # self.matrix = np.zeros((self.top_k+1,self.class_num+1), int)
        # 需要测试的数据组
        self.test_list = []
        # 关联商品的热度分布
        self.temp_item_array_hot=np.array([0]*10)
        # 结果输出相关参数
        self.r_top_num = 200  # 取前200个商品

    def read_history(self):
        # 将购买物品
        read_path = os.path.join(self.data_dir, 'user_bought_history1.txt')
        read_stream = open(read_path, 'r')
        user_id_p = 0
        start_date = datetime.datetime(2012, 1, 1)
        i_line = 0
        for line_i in read_stream:
            i_line += 1
            if i_line % 100000 == 0:
                print i_line, time.time()
            self.record_num += 1
            a = line_i.strip().split(',')
            item_id = int(a[1])
            user_id = int(a[0])
            t0 = a[2].split('-')
            date_now = datetime.datetime(int(t0[0]), int(t0[1]), int(t0[2]))
            if user_id_p != user_id:
                # diyici
                if self.record_num != 1:
                    self.user_array[self.user_num, 1] = self.record_num  # 记录上一个词的末尾位置
                start_date = date_now
                user_id_p = user_id
                self.user_num += 1
                self.user_dict[user_id] = self.user_num
                self.user_array[self.user_num, 0] = self.record_num
                self.user_item_array[self.record_num, :] = np.array([item_id, 0])
            else:
                dt = (date_now - start_date).days
                self.user_item_array[self.record_num, :] = np.array([item_id, dt])
        self.user_array[self.user_num, 1] = self.record_num + 1
        self.user_array = self.user_array[0:(self.user_num + 1), ]
        self.user_item_array = self.user_item_array[0:(self.record_num + 1), ]
        read_stream.close()

    def item_hot(self):
        # 商品热度统计
        item_dict = {}
        for i_record in xrange(0, self.record_num + 1):
            item_id = self.user_item_array[i_record, 0]
            item_index = item_dict.get(item_id, -1)
            if item_index == -1:
                self.item_num += 1  # 商品数+1
                item_index = self.item_num  # 商品分配的存储位置
                item_dict[item_id] = item_index  # 记录商品存储的未知
                self.item_array[item_index,0] = item_id
                # self.item_array[item_index,1] = 1  # 统计次数
            self.item_array[item_index,1] += 1  # 统计次数
        self.item_array = self.item_array[0:(self.item_num + 1), ]  # 截取
        item_array_order = np.argsort(-self.item_array[:, 1])  # 降序排序
        # 根据商品热度 重新排序存储  对前top_k商品hash索引
        self.item_array = self.item_array[item_array_order,:]
        for x in xrange(0, self.item_num + 1):
            self.item_dict[self.item_array[x,0]] = x

    def read_class_id(self):
        self.item_class = np.array([0]*(self.item_num + 1))
        read_path = os.path.join(self.data_dir, 'dim_items.txt')
        read_stream = open(read_path, 'r')
        for line_i in read_stream:
            aa = line_i.strip().split(' ')
            item_index = self.item_dict.get(int(aa[0]), -1)
            # 购买记录中存在该商品
            if item_index != -1:
                self.item_class[item_index] = int(aa[1])
                # 记录商品类别数目
                if self.class_dict.get(int(aa[1]), -1) == -1:
                    self.class_num += 1
                    self.class_dict[int(aa[1])] = self.class_num  # 给类别分配编号
        read_stream.close()

    def set_top_k(self, a=20000):
        # 设置top_k
        self.top_k = a

    def add_circle(self, index, a=1):
        return (index + a + self.num_k) % self.num_k

    def class_item_hot(self):
        # 各类商品 关联商品热度 统计结果为购买某一类商品后 其他各个商品出现其后的概率
        self.like_matrix = np.zeros((self.top_k + 1, self.class_num + 1), int)  # 最后一行记录残余项
        # 关联数
        temp_array = np.array([-1] * self.num_k)  #
        index_temp = 0
        for i_record in xrange(0, self.record_num + 1):
            temp = self.user_item_array[i_record,] #  商品  时间差
            # 某用户的第一个商品
            if temp[1] == 0:
                temp_array = np.array([-1] * self.num_k)
                index_temp = 0
            item_index = self.item_dict.get(temp[0], 0)  # 最后一行为残余项求和
            class_id = self.item_class[item_index]
            class_index = self.class_dict[class_id]  # 商品类别列编号
            temp_array[index_temp] = class_index
            item_index = min(item_index, self.top_k)
            # 前top_k个类别在的此商品上+1
            for x in xrange(0, self.num_k):
                class_id0 = self.add_circle(index_temp, -x)
                class_index0 = temp_array[class_id0]
                if class_index0 == -1:
                    break
                self.like_matrix[item_index, class_index0] += 1
            index_temp = self.add_circle(index_temp, 1)  # 下一个位置

    # 读取需要计算的商品
    def my_test(self):
        read_stream = open(os.path.join(self.data_dir, "test_items.txt"), 'r')
        item_id = 0
        temp_str = ''
        first = True
        for line_i in read_stream:
            a = line_i.strip().split('\t')
            # 增加 未有购买记录的商品处理方式
            if a[1] == 'None':
                a[1] = -1
            temp_item = [int(a[0]), int(a[1])]
            if item_id != temp_item[0]:
                if first == True:
                    first = False
                else:
                    self.test_list.append(temp_str)
                temp_str = str(temp_item[0]) + '\t' + str(temp_item[1])
            temp_str += ',' + str(temp_item[1])
        self.test_list.append(temp_str)

    # 利用全局热度 扩展到 某一个分类的热度分布
    def all_2_class(self,class_index):
        # 尾数重分布 : 前top_k个商品使用统计分布， 残余的冷门商品利用总次数按照全局统计的结果进行分布
        # self.temp_item_array_hot = np.array([0.0]*(self.item_num + 1))
        zhi_shu = 1.0 * self.like_matrix[self.top_k,class_index] / sum(self.item_array[self.top_k:,1])  # 某类别的残余项统计与全局残余项对比
        self.temp_item_array_hot = zhi_shu * self.item_array[:,1]
        self.temp_item_array_hot[0:self.top_k] = self.like_matrix[0:self.top_k,class_index]
        num_total = sum(self.like_matrix[:,class_index])
        # 残余项 概率计算比例
        bi_li = 1.0*zhi_shu/num_total*(self.record_num+1)
        # 概率优化
        pes = Pro_estimate()
        # 前top_k个
        p_pre0 = 0
        num_total = sum(self.like_matrix[:,class_index])
        for i_item in xrange(0,self.item_num + 1):
            if self.simple and i_item>self.top_k:
                self.temp_item_array_hot[i_item] = bi_li * self.item_array[i_item,1] / (self.record_num+1)
            p_pre = 1.0 * self.item_array[i_item,1]/(self.record_num+1)
            if p_pre != p_pre0:
                p_pre0 = p_pre
                pes.solve_function(p_pre)
                pes.set_array()
            self.temp_item_array_hot[i_item] = pes.get_pro(self.temp_item_array_hot[i_item],num_total)

    # 后邻的n个商品意见组合方式 目前 简单求和
    def union_pro(self,temp_result):
        k = 1.0
        for x in xrange(0,len(temp_result)):
            k *= (1-temp_result[x])
        return 1-k

    #   统计该商品的关联商品分布 并返回序列
    def count_items(self,item_id,user_str):
        """

        :type item_id: 商品id 整数
        :type user_str: item_id 的购买者列表 字符串，不同用户逗号间隔
        """
        # 空的 user 列表
        if user_str == '-1':
            my_orders = np.argsort(-self.temp_item_array_hot)
            result_str = item_id + ' ' + str(self.item_array[my_orders[0], 0])
            for i_order in xrange(1, self.r_top_num):
                result_str += ',' + str(self.item_array[my_orders[i_order], 0])
            return result_str
        k_step = self.num_k  # 认为紧接前K个商品之间有匹配关系
        result_matrix = np.zeros((self.item_num+1,self.num_k))
        user_list = user_str.split(',')
        for user in user_list:
            user_index = self.user_dict[int(user)]
            i_record = self.user_array[user_index, 0] # 用户开始的记录
            start = False  #  统计开始的标志
            k = 0
            while i_record < self.user_array[user_index, 1]:
                if self.user_item_array[i_record,0] == item_id:
                    start = True
                    k = 0  # 统计的个数  1开始计数
                elif start & k <= k_step:
                    temp_item = self.user_item_array[i_record, 0]
                    item_index = self.item_dict[temp_item]
                    result_matrix[item_index,k] += 1 # 对应位置+1
                    k += 1
        #  计算统计 该商品的关联性质
        col_sum = result_matrix.sum(0)  # 按照列 求和
        row_sum = result_matrix.sum(1)  # 按照行 求和
        temp_result_array = np.zeros((20000, 2))  # 存储 计算结果
        temp_result = np.array([0.0]*len(col_sum))
        my_orders = np.argsort(-self.temp_item_array_hot)  # 概率 降序 取序号
        i_temp_result = 0
        pes = Pro_estimate()
        for i_order in xrange(0,self.item_num+1):
            temp_item_index = my_orders[i_order]  # 商品的下标
            # 优化原假设 self.temp_item_array_hot
            if (i_order < self.r_top_num)|(row_sum[temp_item_index]>0):
                pes.solve_function(self.temp_item_array_hot[temp_item_index])
                pes.set_array()
                for i in xrange(0,len(col_sum)):
                    temp_result[i] = pes.get_pro(result_matrix[temp_item_index,i],col_sum[i])
                temp_pro = self.union_pro(temp_result)
                temp_result_array[i_temp_result] = [self.item_array[temp_item_index,0], temp_pro] # 记录商品 其概率结果
                i_temp_result += 1
                if i_temp_result == 20000:  # 超出记录空间 断出
                    break
        temp_result_array = temp_result_array[0:i_temp_result, :]
        temp_order = np.argsort(-temp_result_array[:, 1]) # 按照概率降序排列
        result_str = str(item_id)+' '+str(temp_result_array[temp_order[0], 0])
        for i in xrange(1,self.r_top_num):
            result_str += ',' + str(temp_result_array[temp_order[i], 0])
        return result_str
    
    # 计算某一个商品的的搭配商品结果
    def calculate_item_list(self, item_user_str):
        aaa = item_user_str.split('\t')
        item_id = int(aaa[0])  # 商品编号
        item_index = self.item_dict.get(item_id, 0) # 商品存储位置编号
        class_id = self.item_class[item_index]
        class_index = self.class_dict[class_id]
        self.all_2_class(item_id)  # 取得该商品类别的 经验分布
        return self.count_items(item_id, aaa[1])

    # 计算所有的商品列表
    def calculate_all(self):
        w_stream = open(os.path.join(self.data_dir, 'my_result.txt'), 'w')
        for item_user_str in self.test_list:
            string0 = self.calculate_item_list(item_user_str)
            w_stream.writelines(string0 + '\n')
        w_stream.close()
if __name__ == "__main__":
    a = READ_Bought_History()
    a.read_history()
    a.set_top_k()  # 关注主要热度商品参数设置
    a.item_hot()
    a.read_class_id()
    a.class_item_hot()
    a.my_test()