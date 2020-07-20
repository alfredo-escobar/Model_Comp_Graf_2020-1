# coding=utf-8

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es


def createColorNormalsTriangleIndexation(start_index, a, b, c, color):
    # Computing normal from a b c
    v1 = np.array([a_v - b_v for a_v, b_v in zip(a, b)])
    v2 = np.array([b_v - c_v for b_v, c_v in zip(b, c)])
    v1xv2 = np.cross(v1, v2)

    # Defining locations and colors for each vertex of the shape    
    vertices = [
    #        positions               colors                        normals
        a[0], a[1], a[2], color[0], color[1], color[2], v1xv2[0], v1xv2[1], v1xv2[2],
        b[0], b[1], b[2], color[0], color[1], color[2], v1xv2[0], v1xv2[1], v1xv2[2],
        c[0], c[1], c[2], color[0], color[1], color[2], v1xv2[0], v1xv2[1], v1xv2[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         start_index, start_index+1, start_index+2
        ]

    return (vertices, indices)


def createColorNormalsQuadIndexation(start_index, a, b, c, d, color):

    # Computing normal from a b c
    v1 = np.array(a-b)
    v2 = np.array(b-c)
    v1xv2 = np.cross(v1, v2)

    # Defining locations and colors for each vertex of the shape    
    vertices = [
    #        positions               colors                 normals
        a[0], a[1], a[2], color[0], color[1], color[2],  v1xv2[0], v1xv2[1], v1xv2[2],
        b[0], b[1], b[2], color[0], color[1], color[2],  v1xv2[0], v1xv2[1], v1xv2[2],
        c[0], c[1], c[2], color[0], color[1], color[2],  v1xv2[0], v1xv2[1], v1xv2[2],
        d[0], d[1], d[2], color[0], color[1], color[2],  v1xv2[0], v1xv2[1], v1xv2[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         start_index, start_index+1, start_index+2,
         start_index+2, start_index+3, start_index
        ]
    
    return (vertices, indices)


def createTextureNormalsTriangleIndexation(start_index, p1, p2, p3):
    a, t1 = p1
    b, t2 = p2
    c, t3 = p3
    
    # Computing normal from a b c
    v1 = np.array([a_v - b_v for a_v, b_v in zip(a, b)])
    v2 = np.array([b_v - c_v for b_v, c_v in zip(b, c)])
    v1xv2 = np.cross(v1, v2)

    # Defining locations and colors for each vertex of the shape    
    vertices = [
    #        positions      texture       normals
        a[0], a[1], a[2], t1[0], t1[1], v1xv2[0], v1xv2[1], v1xv2[2],
        b[0], b[1], b[2], t2[0], t2[1], v1xv2[0], v1xv2[1], v1xv2[2],
        c[0], c[1], c[2], t3[0], t3[1], v1xv2[0], v1xv2[1], v1xv2[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         start_index, start_index+1, start_index+2
        ]

    return (vertices, indices)


def createTextureNormalsQuadIndexation(start_index, p1, p2, p3, p4):
    a, t1 = p1
    b, t2 = p2
    c, t3 = p3
    d, t4 = p4

    # Computing normal from a b c
    v1 = np.array(a-b)
    v2 = np.array(b-c)
    v1xv2 = np.cross(v1, v2)

    # Defining locations and colors for each vertex of the shape    
    vertices = [
    #        positions      texture                 normals
        a[0], a[1], a[2], t1[0], t1[1],  v1xv2[0], v1xv2[1], v1xv2[2],
        b[0], b[1], b[2], t2[0], t2[1],  v1xv2[0], v1xv2[1], v1xv2[2],
        c[0], c[1], c[2], t3[0], t3[1],  v1xv2[0], v1xv2[1], v1xv2[2],
        d[0], d[1], d[2], t4[0], t4[1],  v1xv2[0], v1xv2[1], v1xv2[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         start_index, start_index+1, start_index+2,
         start_index+2, start_index+3, start_index
        ]
    
    return (vertices, indices)


# CREACIÓN DE GPU SHAPES

def fishBody(image_filename):

    vertices = []
    indices = []
    start_index = 0

    #              positions            texture
    a = np.array([[    0,    1,    0], [    1,  5/10, 0]])
    b = np.array([[ -0.2,    0,    0], [13/23,  5/10, 0]])
    c = np.array([[    0,    0,  0.5], [13/23,     0, 0]])
    d = np.array([[  0.2,    0,    0], [13/23,  5/10, 0]])
    e = np.array([[    0,    0, -0.5], [13/23, 10/10, 0]])
    f = np.array([[-0.05, -0.8,  0.2], [ 5/23,  3/10, 0]])
    g = np.array([[    0, -0.8,  0.2], [ 5/23,  2/10, 0]])
    h = np.array([[ 0.05, -0.8,  0.2], [ 5/23,  3/10, 0]])
    i = np.array([[ 0.05, -0.8, -0.2], [ 5/23,  7/10, 0]])
    j = np.array([[    0, -0.8, -0.2], [ 5/23,  8/10, 0]])
    k = np.array([[-0.05, -0.8, -0.2], [ 5/23,  7/10, 0]])
    
    triangulos = [[a,b,c], [a,c,d], [a,d,e], [a,e,b],
                  [c,b,f], [c,f,g], [c,g,h], [c,h,d],
                  [e,d,i], [e,i,j], [e,j,k], [e,k,b],
                  [b,k,f], [d,h,i]]

    for tri in triangulos:
        _vertex, _indices = createTextureNormalsTriangleIndexation(start_index, tri[0], tri[1], tri[2])

        vertices += _vertex
        indices  += _indices
        start_index += 3

    _vertex, _indices = createTextureNormalsQuadIndexation(start_index, k, i, h, f)
    vertices += _vertex
    indices  += _indices

    return bs.Shape(vertices, indices, image_filename)


def cola(image_filename):

    vertices = []
    indices = []
    start_index = 0
    
    #              positions            texture
    a = np.array([[-0.05,    0,  0.2], [5/23, 3/10, 0]])
    b = np.array([[    0,    0,  0.2], [5/23, 2/10, 0]])
    c = np.array([[ 0.05,    0,  0.2], [5/23, 3/10, 0]])
    d = np.array([[ 0.05,    0, -0.2], [5/23, 7/10, 0]])
    e = np.array([[    0,    0, -0.2], [5/23, 8/10, 0]])
    f = np.array([[-0.05,    0, -0.2], [5/23, 7/10, 0]])
    g = np.array([[    0, -0.5,  0.5], [   0,    0, 0]])
    h = np.array([[    0, -0.5, -0.5], [   0,    1, 0]])

    cuadrilateros = [[a,c,d,f], [c,g,h,d], [a,f,h,g]]
    triangulos = [[a,g,b], [b,g,c], [d,h,e], [e,h,f]]

    for quad in cuadrilateros:
        _vertex, _indices = createTextureNormalsQuadIndexation(start_index, quad[0], quad[1], quad[2], quad[3])
        
        vertices += _vertex
        indices  += _indices
        start_index += 4

    for tri in triangulos:
        _vertex, _indices = createTextureNormalsTriangleIndexation(start_index, tri[0], tri[1], tri[2])

        vertices += _vertex
        indices  += _indices
        start_index += 3

    return bs.Shape(vertices, indices, image_filename)


# MODELACIÓN DEL PEZ CON SCENE GRAPH NODES

def crearPez(image_filename):

    # GPU Shapes
    gpuFishBody = es.toGPUShape(fishBody(image_filename), GL_REPEAT, GL_LINEAR)
    gpuCola = es.toGPUShape(cola(image_filename), GL_REPEAT, GL_LINEAR)

    # Scene Graph Nodes
    sgnFishBody = sg.SceneGraphNode("fishBody")
    sgnFishBody.childs += [gpuFishBody]

    sgnCola = sg.SceneGraphNode("cola")
    sgnCola.transform = tr.matmul([tr.translate(0,-0.8,0),tr.rotationZ(0)])
    sgnCola.childs += [gpuCola]

    sgnPez =  sg.SceneGraphNode("pez")
    sgnPez.transform = tr.rotationZ(0)
    sgnPez.childs += [sgnFishBody]
    sgnPez.childs += [sgnCola]

    return sgnPez


def variosPeces(n, image_filename):
    
    pezEscalado = sg.SceneGraphNode("pezEscalado")
    pezEscalado.transform = tr.uniformScale(0.17)
    pezEscalado.childs += [crearPez(image_filename)]

    peces = sg.SceneGraphNode("peces")

    baseName = "pez"
    for i in range(n):        
        newNode = sg.SceneGraphNode(baseName + str(i))
        newNode.childs += [pezEscalado]
        peces.childs += [newNode]

    return peces


def createTextureVoxel(i, j, k, h, image_filename):
    l_x = i - h/2
    r_x = i + h/2
    b_y = j - h/2
    f_y = j + h/2
    b_z = k - h/2
    t_z = k + h/2
    #   positions      texturePos
    vertices = [
    # Z+: number 1
        l_x, b_y, t_z, 0,1,
        r_x, b_y, t_z, 1,1,
        r_x, f_y, t_z, 1,0,
        l_x, f_y, t_z, 0,0,
    # Z-: number 6
        l_x, b_y, b_z, 0,1,
        r_x, b_y, b_z, 1,1,
        r_x, f_y, b_z, 1,0,
        l_x, f_y, b_z, 0,0,
    # X+: number 5
        r_x, b_y, b_z, 0,1,
        r_x, f_y, b_z, 1,1,
        r_x, f_y, t_z, 1,0,
        r_x, b_y, t_z, 0,0,
    # X-: number 2
        l_x, b_y, b_z, 0,1,
        l_x, f_y, b_z, 1,1,
        l_x, f_y, t_z, 1,0,
        l_x, b_y, t_z, 0,0,
    # Y+: number 4
        l_x, f_y, b_z, 0,1,
        r_x, f_y, b_z, 1,1,
        r_x, f_y, t_z, 1,0,
        l_x, f_y, t_z, 0,0,
    # Y-: number 3
        l_x, b_y, b_z, 0,1,
        r_x, b_y, b_z, 1,1,
        r_x, b_y, t_z, 1,0,
        l_x, b_y, t_z, 0,0
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2, 2, 3, 0,
        4, 5, 6, 6, 7, 4,
        4, 5, 1, 1, 0, 4,
        6, 7, 3, 3, 2, 6,
        5, 6, 2, 2, 1, 5,
        7, 4, 0, 0, 3, 7]

    return bs.Shape(vertices, indices, image_filename)


def crearAcuario(L, W, H, image_filename):
    
    gpuAcuario = es.toGPUShape(bs.createTextureCube(image_filename), GL_REPEAT, GL_LINEAR)
    
    sgnAcuario = sg.SceneGraphNode("sgnAcuario")
    sgnAcuario.transform = tr.scale(L,W,H)
    sgnAcuario.childs += [gpuAcuario]

    return sgnAcuario

    
def bordeAcuario(L, W, H):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #    positions           colors
         -L/2,  -W/2,  -H/2, 0.428, 0.753, 1.0,
         -L/2,  -W/2,   H/2, 0.428, 0.753, 1.0,
         -L/2,   W/2,  -H/2, 0.428, 0.753, 1.0,
         -L/2,   W/2,   H/2, 0.428, 0.753, 1.0,
          L/2,  -W/2,  -H/2, 0.428, 0.753, 1.0,
          L/2,  -W/2,   H/2, 0.428, 0.753, 1.0,
          L/2,   W/2,  -H/2, 0.428, 0.753, 1.0,
          L/2,   W/2,   H/2, 0.428, 0.753, 1.0]

    # This shape is meant to be drawn with GL_LINES,
    # i.e. every 2 indices, we have 1 line.
    indices = [0,4, 4,6, 6,2, 2,0,
               1,5, 5,7, 7,3, 3,1,
               0,1, 4,5, 6,7, 2,3]

    return bs.Shape(vertices, indices)


def heaters(L,W,H):
    gpuHeater = es.toGPUShape(bs.createColorCube(0.428, 0.753, 1.0))

    sgnHeater = sg.SceneGraphNode("sgnHeater")
    sgnHeater.transform = tr.scale(L/5, W/3, 0.01)
    sgnHeater.childs += [gpuHeater]

    sgnHeaterA = sg.SceneGraphNode("sgnHeaterA")
    sgnHeaterA.transform = tr.translate(-L/5, 0, -H/2 +0.01)
    sgnHeaterA.childs += [sgnHeater]

    sgnHeaterB = sg.SceneGraphNode("sgnHeaterB")
    sgnHeaterB.transform = tr.translate(L/5, 0, -H/2 +0.01)
    sgnHeaterB.childs += [sgnHeater]

    sgnAmbosHeaters = sg.SceneGraphNode("AmbosHeaters")
    sgnAmbosHeaters.childs += [sgnHeaterA]
    sgnAmbosHeaters.childs += [sgnHeaterB]

    return sgnAmbosHeaters
