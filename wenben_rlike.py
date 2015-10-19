# coding=utf-8
__author__ = '01053185'
import numpy as np
import os
from yewu_jingyan import exp_of_people


class most_like():
    def __init__(self):
        self.data_dir = 'E:\\gitshell\\tianchi'
        # 词组
        self.word_num = 0
        self.dict_word = {}
        self.word_M = np.zeros((3000000, 2))  # 第一列 记录word_id  第二列 记录 次数
        # 商品
        self.dict_item = {}
        self.item_M = np.zeros((3000000, 2))
        self.item_word_array = [""] * 3000000
        self.item_num = 0
        # 类别
        self.class_M = np.zeros((3000000, 2))
        self.dict_class = {}
        self.class_num = 0
        pass

    def read_txt(self, filename="dim_items.txt"):
        r_path = os.path.join(self.data_dir, filename)
        r_stream = open(r_path, 'r')
        self.item_num = 0
        for line_i in r_stream:
            # 录入商品
            my_str = line_i.strip().split(" ")
            self.dict_item[int(my_str[0])] = self.item_num
            self.item_M[self.item_num] = [my_str[0], my_str[1]]
            self.item_word_array[self.item_num] = my_str[2]
            self.item_num += 1
            # 录入不同的词组
            my_str2 = my_str[2].split(',')
            for x_word in my_str2:
                word_id = int(x_word)
                word_ind = self.dict_word.get(word_id, -1)
                if word_ind == -1:
                    self.dict_word[word_id] = self.word_num
                    self.word_M[self.word_num, :] = [word_id, 1]
                    self.word_num += 1
                else:
                    self.word_M[word_ind, 1] += 1
            # 录入分类信息
            class_id = int(my_str[1])
            class_ind = self.dict_class.get(class_id, -1)
            if class_ind == -1:
                self.dict_class[class_ind] = self.class_num
                self.class_M[self.class_num, :] = [class_id, 1]
                self.class_num += 1
            else:
                self.class_M[class_ind, 1] = 1
        self.class_M = self.class_M[0:self.class_num, ]
        self.word_M = self.class_M[0:self.word_num, ]
        self.item_M = self.item_M[0:self.item_num, ]

    # 统计词词
    def my_tongji(self):
        pass


if __name__ == "__main__":
    a = most_like()
    a.read_txt()
    print 1