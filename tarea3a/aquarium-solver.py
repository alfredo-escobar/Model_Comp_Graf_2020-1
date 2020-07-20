# coding=utf-8

import numpy as np
from scipy.sparse import csc_matrix, lil_matrix
from scipy.sparse.linalg import spsolve
import json
import sys

if len(sys.argv) == 1:
    archivoJSON = input("Archivo .json a cargar: ")
else:
    archivoJSON = sys.argv[1]
setup = json.load(open(archivoJSON))

H = setup["height"]
W = setup["width"]
L = setup["lenght"]
h = 0.25

# Boundary Dirichlet Conditions:
TOP = setup["ambient_temperature"]
HEAT_A = setup["heater_a"]
HEAT_B = setup["heater_b"]

# Condición Neumann
F = setup["window_loss"]

# Number of unknowns
# top side is known (Dirichlet condition)
ni = int(L / h) + 1
nj = int(W / h) + 1
nk = int(H / h)

# El dominio es un cubo
N = ni * nj * nk

# Funciones para convertir índices:

def getP(i,j,k):
    return k * nj * ni + j * ni + i

def getIJK(p):
    i = p % ni
    j = (p // ni) % nj
    k = p // (nj * ni)
    return (i, j, k)

# In this matrix we will write all the coefficients of the unknowns
A = lil_matrix((N, N))

# In this vector we will write all the right side of the equations
b = lil_matrix((N,1))

# We iterate over each point inside the domain
# Each point has an equation associated
# The equation is different depending on the point location inside the domain
for i in range(ni):
    for j in range(nj):
        for k in range(nk):

            p = getP(i,j,k)

            p_up    = getP(i,j,k+1)
            p_down  = getP(i,j,k-1)
            p_left  = getP(i-1,j,k)
            p_right = getP(i+1,j,k)
            p_front = getP(i,j+1,k)
            p_back  = getP(i,j-1,k)

            # Interior
            if i >= 1 and i <= ni-2 and j >= 1 and j <= nj-2 and\
               k >= 1 and k <= nk-2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_front] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = 0

            # Heater A
            elif i >= L/(5*h) and i <= 2*L/(5*h) and j >= W/(3*h) and j <= 2*W/(3*h) and\
               k == 0:
                A[p, p] = 1
                b[p] = HEAT_A

            # Heater B
            elif i >= 3*L/(5*h) and i <= 4*L/(5*h) and j >= W/(3*h) and j <= 2*W/(3*h) and\
               k == 0:
                A[p, p] = 1
                b[p] = HEAT_B

            # CARAS --------------------------------------------------

            # Top
            elif i >= 1 and i <= ni-2 and j >= 1 and j <= nj-2 and\
               k == nk-1:
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_front] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = -TOP

            # Bottom (excepto heaters)
            elif i >= 1 and i <= ni-2 and j >= 1 and j <= nj-2 and\
               k == 0:
                A[p, p_up] = 2
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_front] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = 0

            # Left
            elif i == 0 and j >= 1 and j <= nj-2 and\
               k >= 1 and k <= nk-2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_front] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = -2 * h * F

            # Right
            elif i == ni-1 and j >= 1 and j <= nj-2 and\
               k >= 1 and k <= nk-2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_front] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = -2 * h * F

            # Front
            elif i >= 1 and i <= ni-2 and j == nj-1 and\
               k >= 1 and k <= nk-2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -2 * h * F

            # Back
            elif i >= 1 and i <= ni-2 and j == 0 and\
               k >= 1 and k <= nk-2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -2 * h * F

            # ARISTAS ------------------------------------------------

            # Arista Left Back
            elif i == 0 and j == 0 and\
                 k >= 1 and k <= nk-2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -4 * h * F

            # Arista Left Front
            elif i == 0 and j == nj-1 and\
                 k >= 1 and k <= nk-2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -4 * h * F

            # Arista Left Bottom
            elif i == 0 and j >= 1 and j <= nj-2 and\
                 k == 0:
                A[p, p_up] = 2
                A[p, p_right] = 2
                A[p, p_front] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = -2 * h * F

            # Arista Left Top
            elif i == 0 and j >= 1 and j <= nj-2 and\
                 k == nk-1:
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_front] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = -2 * h * F -TOP

            # Arista Right Back
            elif i == ni-1 and j == 0 and\
                 k >= 1 and k <= nk-2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -4 * h * F

            # Arista Right Front
            elif i == ni-1 and j == nj-1 and\
                 k >= 1 and k <= nk-2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -4 * h * F

            # Arista Right Bottom
            elif i == ni-1 and j >= 1 and j <= nj-2 and\
                 k == 0:
                A[p, p_up] = 2
                A[p, p_left] = 2
                A[p, p_front] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = -2 * h * F

            # Arista Right Top
            elif i == ni-1 and j >= 1 and j <= nj-2 and\
                 k == nk-1:
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_front] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = -2 * h * F -TOP

            # Arista Back Bottom
            elif i >= 1 and i <= ni-2 and j == 0 and\
               k == 0:
                A[p, p_up] = 2
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -2 * h * F

            # Arista Front Bottom
            elif i >= 1 and i <= ni-2 and j == nj-1 and\
               k == 0:
                A[p, p_up] = 2
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -2 * h * F

            # Arista Back Top
            elif i >= 1 and i <= ni-2 and j == 0 and\
               k == nk-1:
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -2 * h * F -TOP

            # Arista Front Top
            elif i >= 1 and i <= ni-2 and j == nj-1 and\
               k == nk-1:
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -2 * h * F -TOP

            # VÉRTICES -----------------------------------------------

            # Esquina Left Back Top
            elif (i,j,k) == (0, 0, nk-1):
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -4 * h * F -TOP
                
            # Esquina Left Back Bottom
            elif (i,j,k) == (0, 0, 0):
                A[p, p_up] = 2
                A[p, p_right] = 2
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -4 * h * F
                
            # Esquina Left Front Top
            elif (i,j,k) == (0, nj-1, nk-1):
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -4 * h * F -TOP
                
            # Esquina Left Front Bottom
            elif (i,j,k) == (0, nj-1, 0):
                A[p, p_up] = 2
                A[p, p_right] = 2
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -4 * h * F
                
            # Esquina Right Back Top
            elif (i,j,k) == (ni-1, 0, nk-1):
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -4 * h * F -TOP
                
            # Esquina Right Back Bottom
            elif (i,j,k) == (ni-1, 0, 0):
                A[p, p_up] = 2
                A[p, p_left] = 2
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -4 * h * F
                
            # Esquina Right Front Top
            elif (i,j,k) == (ni-1, nj-1, nk-1):
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -4 * h * F -TOP
                
            # Esquina Right Front Bottom
            elif (i,j,k) == (ni-1, nj-1, 0):
                A[p, p_up] = 2
                A[p, p_left] = 2
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -4 * h * F

            else:
                print("Point (" + str(i) + ", " + str(j) + ") missed!")
                print("Associated point index is " + str(k))
                raise Exception()


# Solving our system
A = A.tocsc()
b = b.tocsc()
x = spsolve(A, b)

# Now we return our solution to the 3D discrete domain
# In this matrix we will store the solution in the 3D domain
u = np.zeros((ni,nj,nk+1))

for p in range(0, N):
    i,j,k = getIJK(p)
    u[i,j,k] = x[p]

# Parte superior, a temperatura ambiente
for i in range(ni):
    for j in range(nj):
        u[i, j, nk] = TOP

# Guardar la matriz "u"
with open(setup["filename"], "wb") as file:
    np.save(file, u)
