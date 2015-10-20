# coding=utf-8
import numpy as np
import time
import math

__author__ = 'axuanwu'
# 2015年 9 月 25 日
class XMatrix():
    def __init__(self, m=1000, n=100, step=4):
        self.zero_like = 0.01  # 伪零： 差异小于该值认为无差异
        self.step = int(step)  # 数据块的切分方法
        self.m = m  # 原矩阵行数
        self.n = n  # 原矩阵列数
        self.splits = int(math.ceil(1.0 * self.n / self.step))  # 每行记录的分块数
        self.res = self.n % self.step
        self.Memory = []  # 存储数据块的实体
        self.dict_rowid = {}  # 记录数据块的位置字典
        self.Memory_max_rowid = -1
        self.base_line = np.array([0.0] * 10)

    def set_data(self, tezhenshu):
        self.base_line = tezhenshu * np.array([1.0] * self.n)

    def intoMatrix(self, i, j, data):
        # 矩阵赋值
        if (self.base_line[j] != 0) and abs(data / self.base_line[j] - 1) < 0.1:
            pass
        else:
            row_id = (int(j / self.step) + i * self.splits)
            i_temp = self.dict_rowid.get(row_id, -1)
            if i_temp == -1:
                self.Memory_max_rowid += 1
                i_temp = self.Memory_max_rowid
                self.dict_rowid[row_id] = i_temp
                self.Memory.append(np.array([-1.0] * self.step))  # 增加一块 数据块
            self.Memory[i_temp][j % self.step] = data

    def getitem(self, i, j=-1):
        # 读取稀疏矩阵
        if j == -1:
            # 返回一行数据
            temp_array = self.base_line
            for j in xrange(0, self.splits):
                i_temp = self.dict_rowid.get(int(j + i * self.splits), -1)
                if i_temp == -1:
                    continue
                else:
                    for x in xrange(0, len(self.Memory[i_temp])):
                        if self.Memory[i_temp][x] == -1:
                            continue
                        temp_array[x + j * self.step] = self.Memory[i_temp][x]
            return temp_array
        else:
            # 返回元素
            i_temp = self.dict_rowid.get((int(j / self.step) + i * self.splits), -1)
            if i_temp == -1:
                return self.base_line[j]
            return self.Memory[i_temp][j % self.step]


if __name__ == "__main__":
    m = 10  # 需要分解的矩阵行数
    n = 8  # 需要分解的矩阵列数
    a = np.zeros((m, n))
    aaa = XMatrix(m, n, 2)
    aaa.set_data(np.arange(0, n))  # 3 个主要成分
    for i in xrange(0, m):
        for j in xrange(0, n):
            a[i, j] = j
            aaa.intoMatrix(i, j, a[i, j])
    print aaa.getitem(1)
    print aaa.getitem(6, 6)
    aaa.intoMatrix(4, 5, aaa.getitem(4, 5) + 6)
    print aaa.getitem(4, 5)