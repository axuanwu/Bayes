import numpy as np
__author__ = '01053185'
a= np.array([[1,2,3,4],[2,3,4,5]])
b = np.argsort(-a[:,2])
print a[b,:]