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

