from numpy import random
import matplotlib.pyplot as plt
from collections import Counter

# Instrucciones
result = random.binomial(n=2, p=0.6, size=1000)
c = Counter(result)
plt.xticks([0, 1, 2], ["read", "calc", "write"])
plt.title("Distribución de instrucciones generadas")
plt.xlabel("Dirección de memoria")
plt.ylabel("Cantidad de apariciones")

# Direcciones de memoria
# result = random.binomial(n=7, p=0.5, size=1000)
# c = Counter(result)
# plt.title("Distribución de direcciones de memoria")
# plt.xlabel("Dirección de memoria")
# plt.ylabel("Cantidad de apariciones")

plt.bar(c.keys(), c.values())
plt.show()
