# coding=utf-8
import os
import numpy as np

__author__ = '01053185'
# 该部分的主要指是直接使用达人的匹配数据进行关联结果
class exp_of_people():
    def __init__(self):
        self.matrix_item = np.zeros((90000, 3), int)
        self.item_dict = {}
        self.ind1_dict = {}
        pass

    def read_jingyan(self):
        def my_ShangPinGuanLian():
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

        my_ShangPinGuanLian()
        opath = "E:\\gitshell\\tianchi2\\dim_fashion_matchsets2.txt"
        Read_stream = open(opath, "r")
        i_record = 0
        pre_ind1 = -1
        for line_i in Read_stream:
            my_str = line_i.split("\t")
            # 商品 主序号  次序号
            self.matrix_item[i_record, :] = [int(my_str[2]), int(my_str[0]), int(my_str[1])]
            ind_str = self.item_dict.get(int(my_str[2]), '-1')
            #  商品字典
            if ind_str == '-1':
                self.item_dict[int(my_str[2])] = str(i_record)
            else:
                self.item_dict[int(my_str[2])] = ind_str + ',' + str(i_record)
            i_record += 1
            #  ind1 字典
            if i_record == 1:
                self.ind1_dict[int(my_str[0])] = 0
                pre_ind1 = int(my_str[0])
            elif pre_ind1 != int(my_str[0]):
                self.ind1_dict[int(my_str[0])] = i_record - 1
                pre_ind1 = int(my_str[0])

    def associated_items(self, item_id):
        ind_str = self.item_dict.get(item_id, '')
        if len(ind_str) == 0:
            return []
        else:
            asso_array = []
            ind_str = ind_str.split(',')
            for ind in ind_str:
                ind2 = int(ind)
                temp_item = self.matrix_item[ind2, :]
                if temp_item[0] != item_id:
                    print
                id1 = temp_item[1]
                id2 = temp_item[2]
                start_i = self.ind1_dict[id1]
                while (self.matrix_item[start_i, 1] == id1):
                    if self.matrix_item[start_i, 2] != id2:
                        asso_array.append(self.matrix_item[start_i, 0])
                    start_i += 1
            return set(asso_array)  # 去重


if __name__ == "__main__":
    b = exp_of_people()
    b.read_jingyan()
    print b.associated_items(893028)
