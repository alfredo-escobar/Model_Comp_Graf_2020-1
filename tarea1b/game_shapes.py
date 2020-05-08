# coding=utf-8
"""
Space War Alpha 5
Funciones de creación de Shapes e Instancing
Alfredo Escobar
CC3501-1
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
from random import *

import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es


# FUNCIONES DE CREACIÓN DE OBJETOS CON SCENE GRAPH NODE -----------------------

def crearNave(R=0.5, G=0.5, B=0.5):

    gpuGrayRombo = es.toGPUShape(bs.createColorRombo(0.7,0.7,0.7, -0.3))
    gpuColorRombo = es.toGPUShape(bs.createColorRombo(R,G,B))

    # Creando un ala
    alaGris = sg.SceneGraphNode("alaGris")
    alaGris.transform = np.matmul(np.matmul(tr.uniformScale(0.6),tr.translate(-0.6,-0.2,0)),
                                  tr.rotationZ(5*np.pi/8))
    alaGris.childs += [gpuGrayRombo]

    alaColor = sg.SceneGraphNode("alaColor")
    alaColor.transform = tr.uniformScale(0.5)
    alaColor.childs += [gpuColorRombo]

    # Instanciating de las dos alas de la nave
    alaIzq = sg.SceneGraphNode("alaIzq")
    alaIzq.transform = tr.translate(-0.3,-0.3,0)
    alaIzq.childs += [alaGris]
    alaIzq.childs += [alaColor]

    alaDer = sg.SceneGraphNode("alaDer")
    alaDer.transform = np.matmul(tr.translate(0.3,-0.3,0), tr.scale(-1,1,1))
    alaDer.childs += [alaGris]
    alaDer.childs += [alaColor]
    
    # Creando el centro de la nave
    centro = sg.SceneGraphNode("centro")
    centro.childs += [gpuGrayRombo]

    # Ensamblando la nave completa
    nave = sg.SceneGraphNode("nave")
    nave.transform = tr.uniformScale(0.15)
    nave.childs += [centro]
    nave.childs += [alaIzq]
    nave.childs += [alaDer]

    return nave


def crearEnemigo(R=1, G=0, B=0):

    gpuGrayTriangulo = es.toGPUShape(bs.createColorTriangle(0.4,0.4,0.4,[0.3,0.7]))
    gpuColorTriangulo = es.toGPUShape(bs.createColorTriangle(R,G,B,[0.3,0.7]))
    gpuGrayRombo = es.toGPUShape(bs.createColorRombo(0.4,0.4,0.4,-0.3))
    gpuColorQuad = es.toGPUShape(bs.createColorQuad(R,G,B))

    # Creando un ala
    alaGris = sg.SceneGraphNode("alaGris")
    alaGris.childs += [gpuGrayTriangulo]

    alaColor = sg.SceneGraphNode("alaColor")
    alaColor.transform = tr.translate(-0.1,0,0)
    alaColor.childs += [gpuColorTriangulo]

    # Instanciating de las dos alas de la nave
    alaIzq = sg.SceneGraphNode("alaIzq")
    alaIzq.transform = tr.translate(-0.7,0,0)
    alaIzq.childs += [alaColor]
    alaIzq.childs += [alaGris]

    alaDer = sg.SceneGraphNode("alaDer")
    alaDer.transform = np.matmul(tr.translate(0.7,0,0), tr.scale(-1,1,1))
    alaDer.childs += [alaColor]
    alaDer.childs += [alaGris]

    # Creando el centro de la nave
    barra = sg.SceneGraphNode("barra")
    barra.transform = np.matmul(tr.translate(0,-0.3,0), tr.scale(1,0.5,1))
    barra.childs += [gpuColorQuad]
    
    centro = sg.SceneGraphNode("centro")
    centro.transform = tr.translate(0,0,0)
    centro.childs += [gpuGrayRombo]

    # Ensamblando la nave completa
    nave = sg.SceneGraphNode("nave")
    nave.transform = tr.uniformScale(0.15)
    nave.childs += [barra]
    nave.childs += [centro]
    nave.childs += [alaIzq]
    nave.childs += [alaDer]

    return nave


def crearPlaneta(r, g, b, lados=20):
    
    sombra = 0.3
    gpuColorCirculo1 = es.toGPUShape(bs.createColorPoligono(r-sombra, g-sombra, b-sombra, lados))
    gpuColorCirculo2 = es.toGPUShape(bs.createColorPoligono(r, g, b, lados))

    circuloOscuro = sg.SceneGraphNode("circuloOscuro")
    circuloOscuro.transform = tr.scale(1, 0.75, 1)
    circuloOscuro.childs += [gpuColorCirculo1]

    circuloClaro = sg.SceneGraphNode("circuloClaro")
    circuloClaro.transform = np.matmul(tr.scale(0.8, 0.6, 0.8), tr.translate(-0.1,0.2,1))
    circuloClaro.childs += [gpuColorCirculo2]
    
    planeta = sg.SceneGraphNode("planeta")
    planeta.childs += [circuloOscuro]
    planeta.childs += [circuloClaro]

    return planeta


# FUNCIONES DE INSTANCING --------------------------------------------------------

def variosEnemigos(N):

    naveRotada = sg.SceneGraphNode("naveRotada")
    naveRotada.transform = tr.rotationZ(np.pi)
    naveRotada.childs += [crearEnemigo(1, 0, 0)]

    navesEnemigas = sg.SceneGraphNode("navesEnemigas")

    baseName = "enemigo"
    for i in range(N):
        newNode = sg.SceneGraphNode(baseName + str(i))
        newNode.childs += [naveRotada]
        navesEnemigas.childs += [newNode]

    return navesEnemigas


def variosPlanetas(N = 5, lados = 20):

    planetas = sg.SceneGraphNode("planetas")

    baseName = "planeta"
    for i in range(N):
        r = random()/2
        g = random()/2
        b = random()/2
        posX = random()*2 -1
        posY = random()*6 -3
        scale = randint(5,30)/100
        
        newNode = sg.SceneGraphNode(baseName + str(i))
        newNode.transform = np.matmul(tr.translate(posX,posY,0),tr.uniformScale(scale))
        newNode.childs += [crearPlaneta(r, g, b, lados)]
        planetas.childs += [newNode]

    return planetas


def variasEstrellas(N = 15, lados = 10):

    gpuBlancoCirculo = es.toGPUShape(bs.createColorPoligono(1, 1, 1, lados))

    estrellas = sg.SceneGraphNode("estrellas")

    baseName = "estrella"
    for i in range(N):
        posX = random()*2 -1
        posY = random()*6 -3
        scale = randint(5,25)/1000
        
        newNode = sg.SceneGraphNode(baseName + str(i))
        newNode.transform = np.matmul(tr.translate(posX,posY,0),tr.scale(scale, scale*3/4, scale))
        newNode.childs += [gpuBlancoCirculo]
        estrellas.childs += [newNode]

    return estrellas


def variosLasers(N):

    gpuVerdeQuad = es.toGPUShape(bs.createColorQuad(0, 1, 0))
    gpuRosadoQuad = es.toGPUShape(bs.createColorQuad(1, 0.12, 0.31))

    scaledVerdeQuad = sg.SceneGraphNode("scaledVerdeQuad")
    scaledVerdeQuad.transform = tr.scale(0.04, 0.13, 1)
    scaledVerdeQuad.childs += [gpuVerdeQuad]
    
    scaledRosadoQuad = sg.SceneGraphNode("scaledRosadoQuad")
    scaledRosadoQuad.transform = tr.scale(0.04, 0.13, 1)
    scaledRosadoQuad.childs += [gpuRosadoQuad]

    abc = ["A","B","C","D","E","F","G"]

    lasers = sg.SceneGraphNode("lasers")

    baseName = "laserPlayer"
    for i in range(5):
        newNode = sg.SceneGraphNode(baseName + abc[i])
        newNode.childs += [scaledVerdeQuad]
        lasers.childs += [newNode]

    baseName = "laserEnemigo"
    for i in range(N):
        for j in range(3):
            newNode = sg.SceneGraphNode(baseName + str(i) + abc[j])
            newNode.childs += [scaledRosadoQuad]
            lasers.childs += [newNode]

    return lasers
