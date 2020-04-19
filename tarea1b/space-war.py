# coding=utf-8
"""
Space War Alpha 3
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

#N = sys.argv[1]

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return

    if key == glfw.KEY_ESCAPE:
        sys.exit()


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


def demoNaves(N):

    naveEscalada = sg.SceneGraphNode("naveEscalada")
    naveEscalada.childs += [crearNave(0, 1, 0)] # Re-using the previous function

    naves = sg.SceneGraphNode("nave")

    baseName = "naveEscalada"
    for i in range(N):
        newNode = sg.SceneGraphNode(baseName + str(i))
        newNode.transform = tr.translate(0.7 * i - 0.7, 0, 0)
        newNode.childs += [naveEscalada]
        naves.childs += [newNode]

    return naves


def crearEnemigos(N):

    naveRotada = sg.SceneGraphNode("naveRotada")
    naveRotada.transform = tr.rotationZ(np.pi)
    naveRotada.childs += [crearNave(1, 0, 0)]

    navesEnemigas = sg.SceneGraphNode("navesEnemigas")

    baseName = "enemigo"
    for i in range(N):
        newNode = sg.SceneGraphNode(baseName + str(i))
        newNode.transform = tr.translate(0.7 * i - 0.7, 0.7, 0)
##        newNode.transform = tr.translate(0, 1.2, 0) # Se crean fuera de la pantalla
        newNode.childs += [naveRotada]
        navesEnemigas.childs += [newNode]

    return navesEnemigas


def crearPlaneta(r, g, b):
    
    sombra = 0.3
    lados = 20
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


def variosPlanetas(N = 5):

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
        newNode.childs += [crearPlaneta(r, g, b)]
        planetas.childs += [newNode]

    return planetas


def variasEstrellas(N = 15):

    lados = 15
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


def moverPlayer(player_pos, velocidad, dt, width, height):

    # Configurar modificador de velocidad según si la nave va en diagonal o no
    if ((glfw.get_key(window, glfw.KEY_A) == glfw.PRESS) and (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS)) \
    or ((glfw.get_key(window, glfw.KEY_A) == glfw.PRESS) and (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS)) \
    or ((glfw.get_key(window, glfw.KEY_D) == glfw.PRESS) and (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS)) \
    or ((glfw.get_key(window, glfw.KEY_D) == glfw.PRESS) and (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS)):
        modificador = 0.707
    else:
        modificador = 1

    limite = 50

    # Cambiar la posición del jugador (dentro de los límites de la pantalla) según la tecla presionada
    if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS) and (player_pos[0] > (-width + limite)):
        player_pos[0] -= velocidad * modificador * dt

    if (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS) and (player_pos[0] < (width - limite)):
        player_pos[0] += velocidad * modificador * dt

    if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS) and (player_pos[1] > (-height + limite)):
        player_pos[1] -= velocidad * modificador * dt

    if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS) and (player_pos[1] < (height - limite)):
        player_pos[1] += velocidad * modificador * dt

    return player_pos    


def moverEnemigo():
    return


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 450
    height = 600

    window = glfw.create_window(width, height, "Space War Alpha 3", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline = es.SimpleTransformShaderProgram()
    
    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.0, 0.0, 0.1, 1.0)

    # Creating shapes on GPU memory
    playerNave = sg.SceneGraphNode("playerNave")
    playerNave.childs += [crearNave(0.2, 0.6, 1)]

    navesEnemigas = crearEnemigos(3)

    planetasA = variosPlanetas()
    planetasB = variosPlanetas()

    estrellasA = variasEstrellas()
    estrellasB = variasEstrellas()

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Variables iniciales
    t0 = glfw.get_time()
    velocidad = 700
    player_pos = [0,-400] # Posición del jugador
    planA_posY = 0 # Posición vertical del grupo de planetas A
    planB_posY = 6 # Posición vertical del grupo de planetas B
    estrA_posY = 0 # Posición vertical del grupo de estrellas A
    estrB_posY = 6 # Posición vertical del grupo de estrellas B

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Modificando variables de posiciones:
        player_pos = moverPlayer(player_pos, velocidad, dt, width, height)

        planA_posY -= dt * velocidad/350
        if planA_posY <= -6:
            planA_posY = 6
        planB_posY -= dt * velocidad/350
        if planB_posY <= -6:
            planB_posY = 6

        estrA_posY -= dt * velocidad/1000
        if estrA_posY <= -6:
            estrA_posY = 6
        estrB_posY -= dt * velocidad/1000
        if estrB_posY <= -6:
            estrB_posY = 6

        # Modificando transformadas de traslación:
        playerNave.transform = tr.translate(player_pos[0]/width, player_pos[1]/height, 0)
        planetasA.transform = tr.translate(0, planA_posY, 0)
        planetasB.transform = tr.translate(0, planB_posY, 0)
        estrellasA.transform = tr.translate(0, estrA_posY, 0)
        estrellasB.transform = tr.translate(0, estrB_posY, 0)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Dibujando los nodos
        sg.drawSceneGraphNode(estrellasA, pipeline, "transform")
        sg.drawSceneGraphNode(estrellasB, pipeline, "transform")
        sg.drawSceneGraphNode(planetasA, pipeline, "transform")
        sg.drawSceneGraphNode(planetasB, pipeline, "transform")
        sg.drawSceneGraphNode(navesEnemigas, pipeline, "transform")
        sg.drawSceneGraphNode(playerNave, pipeline, "transform")


        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    
    glfw.terminate()
