import math

a = 0.0000003480061091
b = 250.
c = 0.000003091619094
d = 0.0000682775184551527
e = -0.0301431777

happy = 5000
bonus = 0.15
gymdot = 7.3

alpha = (a * math.log(happy + b) + c) * (1 + bonus) * gymdot
beta = (d * (happy + b) + e) * (1 + bonus) * gymdot

sc = 50000000
ec = math.log(alpha * sc / beta + 1.) / alpha

print(f"alpha = {alpha:.10f}")
print(f"beta = {beta:.10f}")
print(f"ec = {ec:.10f}")
