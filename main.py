from numpy import random


zero = False
seven = False
max = False

for i in range(0, 1000):
    x = random.binomial(n=7, p=0.5, size=1)[0]

    if x == 0:
        zero = True

    if x > 7:
        max = True

    if x == 7:
        seven = True

print("zero " + str(zero))
print("seven " + str(seven))
print("max " + str(max))
