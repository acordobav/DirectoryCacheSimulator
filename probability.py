from numpy import random
import matplotlib.pyplot as plt
from collections import Counter

# Instrucciones
# result = random.binomial(n=2, p=0.6, size=1000)

# Direcciones de memoria
result = random.binomial(n=7, p=0.5, size=1000)
c = Counter(result)

plt.bar(c.keys(), c.values())
plt.show()
