# coding=utf-8

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import sys

# Cargar la matriz "u"
archivoNPY = input("Archivo .npy a cargar: ")
with open(archivoNPY, "rb") as file:
    u = np.load(file)

x = []
y = []
z = []
cu = []

for i in range(u.shape[0]):
    for j in range(u.shape[1]):
        for k in range(u.shape[2]):
            cu += [u[i,j,k]]
            x += [i]
            y += [j]
            z += [k]

fig = plt.figure()
ax = plt.axes(projection="3d")
ax.scatter(x, y, z, c=cu, cmap="viridis", linewidth=0.5);
plt.show()
