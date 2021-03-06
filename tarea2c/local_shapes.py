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


def createColorTriangleIndexation(start_index, a, b, c, color):
    # Defining locations and colors for each vertex of the shape    
    vertices = [
    #        positions               colors             
        a[0], a[1], a[2], color[0], color[1], color[2],
        b[0], b[1], b[2], color[0], color[1], color[2],
        c[0], c[1], c[2], color[0], color[1], color[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         start_index, start_index+1, start_index+2
        ]

    return (vertices, indices)


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


def createColorQuadIndexation(start_index, a, b, c, d, color):
    # Defining locations and colors for each vertex of the shape    
    vertices = [
    #        positions               colors
        a[0], a[1], a[2], color[0], color[1], color[2],
        b[0], b[1], b[2], color[0], color[1], color[2],
        c[0], c[1], c[2], color[0], color[1], color[2],
        d[0], d[1], d[2], color[0], color[1], color[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         start_index, start_index+1, start_index+2,
         start_index+2, start_index+3, start_index
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


# CREACI??N DE GPU SHAPES

def birdBody(color):

    vertices = []
    indices = []
    start_index = 0

    a = np.array([0, 1, 0])
    b = np.array([-0.4, 0, 0])
    c = np.array([0, 0, 0.3])
    d = np.array([0.4, 0, 0])
    e = np.array([0, 0, -0.3])
    f = np.array([-0.2, -0.8, 0.05])
    g = np.array([0.2, -0.8, 0.05])
    h = np.array([0.2, -0.8, -0.05])
    i = np.array([-0.2, -0.8, -0.05])
    
    triangulos = [[a,b,c], [a,c,d], [a,d,e], [a,e,b],
                  [c,b,f], [c,f,g], [c,g,d], [e,d,h],
                  [e,h,i], [e,i,b], [b,i,f], [d,g,h]]

    for tri in triangulos:
        _vertex, _indices = createColorNormalsTriangleIndexation(start_index, tri[0], tri[1], tri[2], color)

        vertices += _vertex
        indices  += _indices
        start_index += 3

    _vertex, _indices = createColorNormalsQuadIndexation(start_index, i, h, g, f, color)
    vertices += _vertex
    indices  += _indices

    return bs.Shape(vertices, indices)


def alaBase(color):

    vertices = []
    indices = []
    start_index = 0

    a = np.array([0, 0.4, 0.1])
    b = np.array([-0.7, 0.4, 0.1])
    c = np.array([-0.7, -0.2, 0.1])
    d = np.array([0, -0.4, 0.1])
    e = np.array([0, 0.4, -0.1])
    f = np.array([-0.7, 0.4, -0.04])
    g = np.array([-0.7, -0.2, -0.04])
    h = np.array([0, -0.4, -0.1])

    cuadrilateros = [[a,b,c,d], [a,e,f,b], [b,f,g,c],
                     [c,g,h,d], [d,h,e,a], [e,h,g,f]]

    for quad in cuadrilateros:
        _vertex, _indices = createColorNormalsQuadIndexation(start_index, quad[0], quad[1], quad[2], quad[3], color)
        
        vertices += _vertex
        indices  += _indices
        start_index += 4

    return bs.Shape(vertices, indices)
        
        
def alaMedio(color):

    vertices = []
    indices = []
    start_index = 0

    a = np.array([0, 0.4, 0.07])
    b = np.array([-0.7, 0.4, 0.07])
    c = np.array([-0.7, 0.05, 0.07])
    d = np.array([0, -0.2, 0.07])
    e = np.array([0, 0.4, -0.07])
    f = np.array([-0.7, 0.4, -0.02])
    g = np.array([-0.7, 0.05, -0.02])
    h = np.array([0, -0.2, -0.07])

    cuadrilateros = [[a,b,c,d], [a,e,f,b], [b,f,g,c],
                     [c,g,h,d], [d,h,e,a], [e,h,g,f]]

    for quad in cuadrilateros:
        _vertex, _indices = createColorNormalsQuadIndexation(start_index, quad[0], quad[1], quad[2], quad[3], color)
        
        vertices += _vertex
        indices  += _indices
        start_index += 4

    return bs.Shape(vertices, indices)


def alaPunta(color):

    vertices = []
    indices = []
    start_index = 0

    a = np.array([0, 0.4, 0.045])
    b = np.array([-0.7, 0.4, 0.045])
    c = np.array([0, 0.05, 0.045])
    d = np.array([0, 0.4, -0.045])
    e = np.array([0, 0.05, -0.045])

    triangulos = [[a,b,c], [c,b,e], [e,b,d], [d,b,a]]

    for tri in triangulos:
        _vertex, _indices = createColorNormalsTriangleIndexation(start_index, tri[0], tri[1], tri[2], color)

        vertices += _vertex
        indices  += _indices
        start_index += 3

    _vertex, _indices = createColorNormalsQuadIndexation(start_index, a, c, e, d, color)
    vertices += _vertex
    indices  += _indices

    return bs.Shape(vertices, indices)


def cola(color):

    vertices = []
    indices = []
    start_index = 0

    a = np.array([0.2, 0.05, 0.05])
    b = np.array([-0.2, 0.05, 0.05])
    c = np.array([-0.3,-0.5,0])
    d = np.array([0.3,-0.5,0])
    e = np.array([0.2, 0.05, -0.05])
    f = np.array([-0.2, 0.05, -0.05])

    cuadrilateros = [[a,b,c,d], [b,a,e,f], [f,e,d,c]]
    triangulos = [[a,d,e], [b,f,c]]

    for quad in cuadrilateros:
        _vertex, _indices = createColorNormalsQuadIndexation(start_index, quad[0], quad[1], quad[2], quad[3], color)
        
        vertices += _vertex
        indices  += _indices
        start_index += 4

    for tri in triangulos:
        _vertex, _indices = createColorNormalsTriangleIndexation(start_index, tri[0], tri[1], tri[2], color)

        vertices += _vertex
        indices  += _indices
        start_index += 3

    return bs.Shape(vertices, indices)


def generateSphereShape(color):
    nTheta = 5
    nPhi = 5
    vertices = []
    indices = []

    theta_angs = np.linspace(0, np.pi, nTheta, endpoint=True)
    phi_angs = np.linspace(0, 2 * np.pi, nPhi, endpoint=True)

    start_index = 0

    for theta_ind in range(len(theta_angs)-1): # vertical
        cos_theta = np.cos(theta_angs[theta_ind]) # z_top
        cos_theta_next = np.cos(theta_angs[theta_ind + 1]) # z_bottom

        sin_theta = np.sin(theta_angs[theta_ind])
        sin_theta_next = np.sin(theta_angs[theta_ind + 1])

        # d === c <---- z_top
        # |     |
        # |     |
        # a === b  <--- z_bottom
        # ^     ^
        # phi   phi + dphi
        for phi_ind in range(len(phi_angs)-1): # horizontal
            cos_phi = np.cos(phi_angs[phi_ind])
            cos_phi_next = np.cos(phi_angs[phi_ind + 1])
            sin_phi = np.sin(phi_angs[phi_ind])
            sin_phi_next = np.sin(phi_angs[phi_ind + 1])
            # we will asume radius = 1, so scaling should be enough.
            # x = cos?? sin??
            # y = sin?? sin??
            # z = cos??

            #                     X                             Y                          Z
            a = np.array([cos_phi      * sin_theta_next, sin_phi * sin_theta_next     , cos_theta_next])
            b = np.array([cos_phi_next * sin_theta_next, sin_phi_next * sin_theta_next, cos_theta_next])
            c = np.array([cos_phi_next * sin_theta     , sin_phi_next * sin_theta     , cos_theta])
            d = np.array([cos_phi * sin_theta          , sin_phi * sin_theta          , cos_theta])

            _vertex, _indices = createColorNormalsQuadIndexation(start_index, a, b, c, d, color)

            vertices += _vertex
            indices  += _indices
            start_index += 4

    return bs.Shape(vertices, indices)


def pico(color):

    vertices = []
    indices = []
    start_index = 0

    a = np.array([0.07, -0.1, 0.07])
    b = np.array([0, 0.2, 0])
    c = np.array([-0.07, -0.1, 0.07])
    d = np.array([0.07, -0.1, -0.07])
    e = np.array([-0.07, -0.1, -0.07])

    triangulos = [[a,b,c], [c,b,e], [e,b,d], [d,b,a]]

    for tri in triangulos:
        _vertex, _indices = createColorNormalsTriangleIndexation(start_index, tri[0], tri[1], tri[2], color)

        vertices += _vertex
        indices  += _indices
        start_index += 3

    _vertex, _indices = createColorNormalsQuadIndexation(start_index, a, c, e, d, color)
    vertices += _vertex
    indices  += _indices

    return bs.Shape(vertices, indices)


def createTextureCubeMap(image_filename):

    # Defining locations and texture coordinates for each vertex of the shape  
    vertices = [
    #   positions         tex coords
    # Z+:
        -0.5, -0.5,  0.5, 1/4,   0,
         0.5, -0.5,  0.5, 1/2,   0,
         0.5,  0.5,  0.5, 1/2, 1/3,
        -0.5,  0.5,  0.5, 1/4, 1/3,

    # Z-:
        -0.5, -0.5, -0.5, 1/4,   1,
         0.5, -0.5, -0.5, 1/2,   1,
         0.5,  0.5, -0.5, 1/2, 2/3,
        -0.5,  0.5, -0.5, 1/4, 2/3,
        
    # X+:
         0.5, -0.5, -0.5, 3/4, 2/3,
         0.5,  0.5, -0.5, 1/2, 2/3,
         0.5,  0.5,  0.5, 1/2, 1/3,
         0.5, -0.5,  0.5, 3/4, 1/3,
 
    # X-:
        -0.5, -0.5, -0.5,   0, 2/3,
        -0.5,  0.5, -0.5, 1/4, 2/3,
        -0.5,  0.5,  0.5, 1/4, 1/3,
        -0.5, -0.5,  0.5,   0, 1/3,

    # Y+:
        -0.5,  0.5, -0.5, 1/4, 2/3,
         0.5,  0.5, -0.5, 1/2, 2/3,
         0.5,  0.5,  0.5, 1/2, 1/3,
        -0.5,  0.5,  0.5, 1/4, 1/3,

    # Y-:
        -0.5, -0.5, -0.5,   1, 2/3,
         0.5, -0.5, -0.5, 3/4, 2/3,
         0.5, -0.5,  0.5, 3/4, 1/3,
        -0.5, -0.5,  0.5,   1, 1/3
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15, # X-
         19,18,17,17,16,19, # Y+
         20,21,22,22,23,20] # Y-

    return bs.Shape(vertices, indices, image_filename)


def createTextureInnerNormalsCubeMap(image_filename):

    # Defining locations and texture coordinates for each vertex of the shape  
    vertices = [
    #   positions         tex coords   normals
    # Z+:
        -0.5, -0.5,  0.5, 1/4,   0,   0,0,-1,
         0.5, -0.5,  0.5, 1/2,   0,   0,0,-1,
         0.5,  0.5,  0.5, 1/2, 1/3,   0,0,-1,
        -0.5,  0.5,  0.5, 1/4, 1/3,   0,0,-1,

    # Z-:
        -0.5, -0.5, -0.5, 1/4,   1,    0,0,1,
         0.5, -0.5, -0.5, 1/2,   1,    0,0,1,
         0.5,  0.5, -0.5, 1/2, 2/3,    0,0,1,
        -0.5,  0.5, -0.5, 1/4, 2/3,    0,0,1,
        
    # X+:
         0.5, -0.5, -0.5, 3/4, 2/3,   -1,0,0,
         0.5,  0.5, -0.5, 1/2, 2/3,   -1,0,0,
         0.5,  0.5,  0.5, 1/2, 1/3,   -1,0,0,
         0.5, -0.5,  0.5, 3/4, 1/3,   -1,0,0,
 
    # X-:
        -0.5, -0.5, -0.5,   0, 2/3,    1,0,0,
        -0.5,  0.5, -0.5, 1/4, 2/3,    1,0,0,
        -0.5,  0.5,  0.5, 1/4, 1/3,    1,0,0,
        -0.5, -0.5,  0.5,   0, 1/3,    1,0,0,

    # Y+:
        -0.5,  0.5, -0.5, 1/4, 2/3,   0,-1,0,
         0.5,  0.5, -0.5, 1/2, 2/3,   0,-1,0,
         0.5,  0.5,  0.5, 1/2, 1/3,   0,-1,0,
        -0.5,  0.5,  0.5, 1/4, 1/3,   0,-1,0,

    # Y-:
        -0.5, -0.5, -0.5,   1, 2/3,    0,1,0,
         0.5, -0.5, -0.5, 3/4, 2/3,    0,1,0,
         0.5, -0.5,  0.5, 3/4, 1/3,    0,1,0,
        -0.5, -0.5,  0.5,   1, 1/3,    0,1,0
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15, # X-
         19,18,17,17,16,19, # Y+
         20,21,22,22,23,20] # Y-

    return bs.Shape(vertices, indices, image_filename)


def createTextureOuterNormalsCubeMap(image_filename):

    # Defining locations and texture coordinates for each vertex of the shape  
    vertices = [
    #   positions         tex coords   normals
    # Z+:
        -0.5, -0.5,  0.5, 1/4,   0,    0,0,1,
         0.5, -0.5,  0.5, 1/2,   0,    0,0,1,
         0.5,  0.5,  0.5, 1/2, 1/3,    0,0,1,
        -0.5,  0.5,  0.5, 1/4, 1/3,    0,0,1,

    # Z-:
        -0.5, -0.5, -0.5, 1/4,   1,   0,0,-1,
         0.5, -0.5, -0.5, 1/2,   1,   0,0,-1,
         0.5,  0.5, -0.5, 1/2, 2/3,   0,0,-1,
        -0.5,  0.5, -0.5, 1/4, 2/3,   0,0,-1,
        
    # X+:
         0.5, -0.5, -0.5, 3/4, 2/3,    1,0,0,
         0.5,  0.5, -0.5, 1/2, 2/3,    1,0,0,
         0.5,  0.5,  0.5, 1/2, 1/3,    1,0,0,
         0.5, -0.5,  0.5, 3/4, 1/3,    1,0,0,
 
    # X-:
        -0.5, -0.5, -0.5,   0, 2/3,   -1,0,0,
        -0.5,  0.5, -0.5, 1/4, 2/3,   -1,0,0,
        -0.5,  0.5,  0.5, 1/4, 1/3,   -1,0,0,
        -0.5, -0.5,  0.5,   0, 1/3,   -1,0,0,

    # Y+:
        -0.5,  0.5, -0.5, 1/4, 2/3,    0,1,0,
         0.5,  0.5, -0.5, 1/2, 2/3,    0,1,0,
         0.5,  0.5,  0.5, 1/2, 1/3,    0,1,0,
        -0.5,  0.5,  0.5, 1/4, 1/3,    0,1,0,

    # Y-:
        -0.5, -0.5, -0.5,   1, 2/3,   0,-1,0,
         0.5, -0.5, -0.5, 3/4, 2/3,   0,-1,0,
         0.5, -0.5,  0.5, 3/4, 1/3,   0,-1,0,
        -0.5, -0.5,  0.5,   1, 1/3,   0,-1,0
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15, # X-
         19,18,17,17,16,19, # Y+
         20,21,22,22,23,20] # Y-

    return bs.Shape(vertices, indices, image_filename)


# MODELACI??N DEL AVE CON SCENE GRAPH NODES

def crearAve(escala = 1):

    color1 = [70/255, 205/255, 195/255]
    color2 = [50/255, 185/255, 175/255]
    color3 = [30/255, 165/255, 155/255]
    gris = [0.2, 0.2, 0.2]

    # GPU Shapes
    gpuBirdBody = es.toGPUShape(birdBody(color1))
    gpuAlaBase = es.toGPUShape(alaBase(color2))
    gpuAlaMedio = es.toGPUShape(alaMedio(color3))
    gpuAlaPunta = es.toGPUShape(alaPunta(gris))
    gpuCola = es.toGPUShape(cola(gris))
    gpuCabeza = es.toGPUShape(generateSphereShape(color1))
    gpuPico = es.toGPUShape(pico([0.1,0.1,0.1]))

    # Scene Graph Nodes
    sgnBirdBody = sg.SceneGraphNode("birdBody")
    sgnBirdBody.childs += [gpuBirdBody]

    sgnAlaPunta = sg.SceneGraphNode("alaPunta")
    sgnAlaPunta.transform = tr.matmul([tr.translate(-0.7,-0.001,0.024),tr.rotationY(0)])#<-rot1
    sgnAlaPunta.childs += [gpuAlaPunta]

    sgnAlaMedio = sg.SceneGraphNode("alaMedio")
    sgnAlaMedio.childs += [gpuAlaMedio]

    sgnAlaBase = sg.SceneGraphNode("alaBase")
    sgnAlaBase.childs += [gpuAlaBase]

    sgnCola = sg.SceneGraphNode("cola")
    sgnCola.transform = tr.translate(0,-0.8,0)
    sgnCola.childs += [gpuCola]

    sgnCabeza = sg.SceneGraphNode("cabeza")
    sgnCabeza.transform = tr.matmul([tr.translate(0,0.7,0),tr.uniformScale(0.3)])
    sgnCabeza.childs += [gpuCabeza]

    sgnPico = sg.SceneGraphNode("pico")
    sgnPico.transform = tr.translate(0,1,0)
    sgnPico.childs += [gpuPico]

    sgnAlaExt = sg.SceneGraphNode("alaExt")
    sgnAlaExt.transform = tr.matmul([tr.translate(-0.7,-0.001,0.029),tr.rotationY(0)])#<-rot2
    sgnAlaExt.childs += [sgnAlaPunta]
    sgnAlaExt.childs += [sgnAlaMedio]

    sgnAlaCompleta = sg.SceneGraphNode("alaCompleta")
    sgnAlaCompleta.transform = tr.rotationY(0)#<-rot3
    sgnAlaCompleta.childs += [sgnAlaExt]
    sgnAlaCompleta.childs += [sgnAlaBase]

    sgnAlaIzq = sg.SceneGraphNode("alaIzq")
    sgnAlaIzq.transform = tr.translate(-0.1,0,0)
    sgnAlaIzq.childs += [sgnAlaCompleta]

    sgnAlaDer = sg.SceneGraphNode("alaDer")
    sgnAlaDer.transform = tr.matmul([tr.translate(0.1,0,0),tr.scale(-1,1,1)])
    sgnAlaDer.childs += [sgnAlaCompleta]

    sgnAve =  sg.SceneGraphNode("ave")
    sgnAve.transform = tr.uniformScale(escala)
    sgnAve.childs += [sgnBirdBody]
    sgnAve.childs += [sgnAlaIzq]
    sgnAve.childs += [sgnAlaDer]
    sgnAve.childs += [sgnCola]
    sgnAve.childs += [sgnCabeza]
    sgnAve.childs += [sgnPico]

    return sgnAve


# FUNCIONES DE INSTANCING

def variasAves(n):
    aves = sg.SceneGraphNode("aves")

    baseName = "ave"
    for i in range(n):
        posY = (-i//2) * 0.4
        posX = posY * ((-1)**(i%2)) * 0.7
        centro = (n//2) * 0.2
        
        newNode = sg.SceneGraphNode(baseName + str(i))
        newNode.transform = tr.translate(posX,posY+centro,0)
        newNode.childs += [crearAve(0.1)]
        aves.childs += [newNode]

    return aves


def palos():
    palo = es.toGPUShape(createTextureOuterNormalsCubeMap("palo.png"), GL_REPEAT, GL_LINEAR)
    
    paloEscalado = sg.SceneGraphNode("paloEscalado")
    paloEscalado.transform = tr.scale(0.09, 0.09, 0.404)
    paloEscalado.childs += [palo]

    palos = sg.SceneGraphNode("palos")

    baseName = "palo"
    for i in range(5):
        if i == 4:
            posX = -0.075
            posY = -0.445
        else:
            posX = 0.445 * ((-1)**(i%2))
            posY = 0.445 * ((-1)**(i//2))
        
        newNode = sg.SceneGraphNode(baseName + str(i))
        newNode.transform = tr.translate(posX,posY,-0.298)
        newNode.childs += [paloEscalado]
        palos.childs += [newNode]

    return palos
