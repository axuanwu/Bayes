# coding=utf-8
import math

__author__ = '01053185'
import numpy as np
import os
from yewu_jingyan import exp_of_people
import time
from pro_estimate2 import Pro_estimate


class most_like():
    def __init__(self):
        self.data_dir = 'E:\\gitshell\\tianchi2'
        # 词组
        self.word_num = 0
        self.dict_word = {}
        self.top_k_word = 20000  # 详细计算前20000的词组
        self.word_M = np.zeros((1000000, 2))  # 第一列 记录word_id  第二列 记录 概率
        self.word_item_array = [""] * 1000000  # 每个词被哪些商品使用
        # 需要预测的词组
        self.r_word_num = 0
        self.r_dict_word = {}
        self.r_word_M = np.zeros((80000, 2))
        self.test_item = []
        # 商品
        self.dict_item = {}
        self.item_M = np.zeros((600000, 2), int)
        self.item_word_array = [""] * 600000
        self.item_num = 0
        # 类别
        self.class_M = np.zeros((3000000, 2))  # 类别id  类别商品计数
        self.dict_class = {}
        self.class_num = 0
        self.class_class = np.zeros((2, 2))
        # 原始人工经验
        self.exp_peo = exp_of_people()
        self.exp_peo.read_jingyan()
        # self.matrix_item = np.zeros((10000000,3))
        # 概率优化模块
        self.pro_guji = Pro_estimate()

        pass

    def read_txt(self, filename="dim_items.txt"):
        r_path = os.path.join(self.data_dir, filename)
        r_stream = open(r_path, 'r')
        self.item_num = 0
        for line_i in r_stream:
            if self.item_num % 100000 == 0:
                print self.item_num, time.time()
            # 录入商品
            my_str = line_i.strip('\n').split(" ")
            self.dict_item[int(my_str[0])] = self.item_num
            self.item_M[self.item_num, :] = [my_str[0], int(my_str[1])]
            self.item_word_array[self.item_num] = my_str[2]
            self.item_num += 1
            # 录入不同的词组
            my_str2 = my_str[2].split(',')
            for x_word in my_str2:
                try:
                    word_id = int(x_word)
                except:
                    continue
                word_ind = self.dict_word.get(word_id, -1)
                if word_ind == -1:
                    self.dict_word[word_id] = self.word_num
                    self.word_M[self.word_num, :] = [word_id, 1]
                    self.word_item_array[self.word_num] = my_str[0]  # 商品                    
                    self.word_num += 1
                else:
                    self.word_M[word_ind, 1] += 1
                    self.word_item_array[word_ind] += ',' + my_str[0]  # 商品
            # 录入分类信息
            class_id = int(my_str[1])
            class_ind = self.dict_class.get(class_id, -1)
            if class_ind == -1:
                self.dict_class[class_id] = self.class_num
                self.class_M[self.class_num, :] = [class_id, 1]
                self.class_num += 1
            else:
                self.class_M[class_ind, 1] += 1
        self.class_M = self.class_M[0:self.class_num, :]
        self.word_M = self.word_M[0:self.word_num, :]
        self.item_M = self.item_M[0:self.item_num, :]
        self.item_word_array = self.item_word_array[0:self.item_num]
        self.word_item_array = self.word_item_array[0:self.word_num]
        # 根据热度排行对词进行重新排序
        order = np.argsort(-self.word_M[:, 1])
        self.word_M = self.word_M[order, :]
        temp_a = self.word_item_array
        for x in xrange(0, len(order)):
            self.word_item_array[x] = temp_a[order[x]]
        for x in xrange(0, self.word_num):
            self.dict_word[int(self.word_M[x, 0])] = x
        r_stream.close()
        # 转化word_M 第2 列 为概率：
        sum_word_num = sum(self.word_M[:, 1])
        self.word_M[:, 1] = self.word_M[:, 1] / sum_word_num

    def result_word(self, file_name='test_items2.txt'):
        file_name = os.path.join(self.data_dir, file_name)
        r_stream = open(file_name, 'r')
        for line_i in r_stream:
            item_id = int(line_i.strip())
            self.test_item.append(item_id)
            item_ind = self.dict_item.get(item_id, -1)
            if item_ind == -1:
                continue
            word_array = self.item_word_array[item_ind].split(',')
            for word_id in word_array:
                word_id = int(word_id)
                word_ind = self.r_dict_word.get(word_id, -1)
                if word_ind == -1:
                    self.r_dict_word[word_id] = self.r_word_num
                    self.r_word_M[self.r_word_num, :] = [word_id, 1]
                    self.r_word_num += 1
                else:
                    self.r_word_M[word_ind, 1] += 1
        r_stream.close()
        order = np.argsort(-self.r_word_M[0:self.r_word_num, 1])
        self.r_word_M = self.r_word_M[order, :]
        i_record = self.r_word_num
        for i in xrange(0, self.r_word_num):
            if self.r_word_M[i, 1] == 1:
                i_record = i
                break
        self.r_word_num = i_record
        self.r_word_M = self.r_word_M[0:i_record, :]

    # 返回一个词的所有 商品
    def get_item_array(self, word_id):
        word_ind = self.dict_word.get(word_id, -1)
        item_array = []
        if word_ind == -1:
            return item_array
        else:
            item_str = self.word_item_array[word_ind].split(',')
            for item in item_str:
                item_array.append(int(item))
        return item_array

    # 统计词词关系
    def my_tongji1(self):
        split_ss = self.r_word_num
        temp_array = np.zeros((split_ss, self.top_k_word + 1))
        p_remain = sum(self.word_M[self.top_k_word:, 1])  # 残余项原始概率
        i_file = 0
        file_name = "word_word_pro"
        # word_ind = 0
        for word_ind in xrange(0, self.r_word_num):
            word_id = int(self.r_word_M[word_ind, 0])
            item_array = self.get_item_array(word_id)
            for item_id in item_array:
                item_array2 = self.exp_peo.associated_items(int(item_id))  # 关联商品
                if len(item_array2) == 0:
                    continue
                for item_id2 in item_array2:
                    item_ind = self.dict_item.get(item_id2, -1)
                    if item_ind != -1:
                        word_str = self.item_word_array[item_ind]  # 所关联商品的分词组
                        if word_str == '':
                            continue
                        word_array = word_str.split(',')
                        for word_id2 in word_array:
                            word_ind2 = min(self.dict_word[int(word_id2)], self.top_k_word)
                            temp_array[word_ind, word_ind2] += 1  # word_ind 指示的词发生后其关联商品 为 含word_ind2的词 次数+1
            if word_ind > 0 and ((word_ind % split_ss == 0) | (word_ind == self.r_word_num - 1)):
                temp_array_sum = temp_array.sum(1)  # 按照行进行求和
                (row_num, col_num) = temp_array.shape
                for i_col in xrange(0, col_num):
                    if i_col % 200 == 0:
                        print i_col, time.time()
                    if i_col == self.top_k_word:
                        p_pre = p_remain
                    else:
                        p_pre = self.word_M[i_col, 1]
                    for i_row in xrange(0, row_num):
                        temp_array[i_row, i_col] = \
                            self.pro_guji.get_pro_r(p_pre,
                                                    temp_array[i_row, i_col],
                                                    temp_array_sum[i_row])  # p n m
                # 静态存储
                i_file = math.floor(word_ind / split_ss)
                w_file = os.path.join(self.data_dir, file_name + str(i_file) + '.txt')
                w_stream = open(w_file, 'w')
                for i_row in xrange(0, row_num):
                    my_str = ''
                    for i_col in xrange(0, col_num - 1):
                        my_str += str(math.log(temp_array[i_row, i_col])) + ','
                    my_str += str(math.log(temp_array[i_row, col_num - 1])) + '\n'
                    w_stream.writelines(my_str)
                w_stream.close()
        pass

    # 统计 类类 关系
    def my_tongji2(self):
        # 统计结果由 sql sever 完成后存为txt 这里直接读取
        r_path = os.path.join(self.data_dir, "class_class.txt")
        r_stream = open(r_path, 'r')
        self.class_class = np.zeros(())
        for line in r_stream:
            my_str = line.strip().split('\t')
            class_ind1 = self.dict_class[int(my_str[0])]
            class_ind2 = self.dict_class[int(my_str[1])]
            num = self.dict_class[int(my_str[2])]
            self.class_class[class_ind1, class_ind2] += num
        r_stream.close()
        row_sum = self.class_class.sum(1)  # 按照行求和
        all_num = sum(self.class_M[:, 1])
        # self.class_class[class_ind1, class_ind2] 存储 id1 类别 后面搭配 id2 类别的概率
        for ind2 in xrange(0, self.class_num):
            p_pre = 1.0 * self.class_M[ind2, 1] / all_num  # ind2 发生的概率
            for ind1 in xrange(0, self.class_num):
                self.class_class[ind1, ind2] = self.pro_guji.get_pro_r(p_pre,
                                                                       self.class_class[ind1, ind2],
                                                                       row_sum[ind1])
        pass

    # 统计词词关系 new 基于sql sever 处理过的文件开始统计 简化代码
    def my_tongji3(self):
        split_ss = self.r_word_num
        temp_array = np.zeros((self.r_word_num + 1, self.top_k_word + 1))
        p_remain = sum(self.word_M[self.top_k_word:, 1])  # 残余项原始概率
        i_file = 0
        file_name = "word_word_pro"
        r_path = os.path.join(self.data_dir, "wordstr_wordstr.txt")
        r_stream = open(r_path, 'r')
        for wor_str in r_stream:
            my_str = wor_str.strip().split('\t')
            if my_str[0] == '' or my_str[1] == '':
                continue
            word_p = my_str[0].split(',')
            word_s = my_str[1].split(',')
            num = int(my_str[2])
            for word_id1 in word_p:
                word_ind1 = self.r_dict_word.get(int(word_id1), -1)  # 行号
                if word_ind1 == -1:
                    continue  # 非统计对象
                word_ind1 = min(word_ind1, self.r_word_num)
                for word_id2 in word_s:
                    word_ind2 = self.dict_word.get(int(word_id2), -1)
                    if word_ind2 == -1:
                        continue  # 非录入词
                    word_ind2 = min(word_ind2, self.top_k_word)
                    temp_array[word_ind1, word_ind2] += num  # word_ind 指示的词发生后其关联商品 为 含word_ind2的词 次数+1
        r_stream.close()
        # 求概率
        temp_array_sum = temp_array.sum(1)  # 按照行进行求和
        (row_num, col_num) = temp_array.shape
        for i_col in xrange(0, col_num):
            if i_col % 200 == 0:
                print i_col, time.time()
            if i_col == self.top_k_word:
                p_pre = p_remain
            else:
                p_pre = self.word_M[i_col, 1]
            for i_row in xrange(0, row_num):
                temp_array[i_row, i_col] = \
                    self.pro_guji.get_pro_r(p_pre,
                                            temp_array[i_row, i_col],
                                            temp_array_sum[i_row])  # p n m
        # 静态存储
        w_file = os.path.join(self.data_dir, file_name + str(i_file) + '.txt')
        w_stream = open(w_file, 'w')
        for i_row in xrange(0, row_num):
            my_str = ''
            for i_col in xrange(0, col_num - 1):
                my_str += str(math.log(temp_array[i_row, i_col])) + ','
            my_str += str(math.log(temp_array[i_row, col_num - 1])) + '\n'
            w_stream.writelines(my_str)
        w_stream.close()
        self.word_word = temp_array


if __name__ == "__main__":
    a = most_like()
    a.read_txt()
    a.result_word()
    print 1
    a.my_tongji3()  # 统计 词词 关系
    print 2
    a.my_tongji2()  # 统计 类类 关系
    print 3
    # a.get_item_array(171811)
    print a.r_word_num, a.r_word_M[a.r_word_num - 1, 1]
