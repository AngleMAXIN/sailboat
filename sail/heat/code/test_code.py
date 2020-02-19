import numpy as np

# a = np.linspace(1,10,6).reshape((2,3))
# print(a)

# a = np.array([4,5,6],dtype=np.float32)
# print(a,a.dtype)

# a = np.array([
#     [4,5,6],
#     [65,65,78.656565],
#     [[87.8,67,767,[67,76,76,[78,3,99,]]]],
#     7
# ])
# a
# print(a[2][0][4])

# a = np.arange(4,78,2)
# v = np.array([[1,2],[4,5]])
# b = np.arange(4).reshape(2,2)
# print(v)
# print(b)
#
# print(b*v)
# print(np.dot(b,v))
# print(v.dot(b))


# a = np.linspace(1, 10,6).reshape((2, 3))
a = np.array([10,23,2])
b = np.arange(3)

print(np.dot(a,b))
