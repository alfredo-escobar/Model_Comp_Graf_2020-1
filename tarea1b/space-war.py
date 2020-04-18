# coding=utf-8
"""
Basado en scene_graph2.py
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

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
    centro.transform = tr.identity()
    centro.childs += [gpuGrayRombo]
    
    nave = sg.SceneGraphNode("nave")
    nave.childs += [centro]
    nave.childs += [alaIzq]
    nave.childs += [alaDer]

    return nave


def demoNaves(N):

    naveEscalada = sg.SceneGraphNode("naveEscalada")
    naveEscalada.transform = tr.uniformScale(0.15)
    naveEscalada.childs += [crearNave()] # Re-using the previous function

    naves = sg.SceneGraphNode("nave")

    baseName = "naveEscalada"
    for i in range(N):
        # A new node is only locating a naveEscalada in the scene depending on index i
        newNode = sg.SceneGraphNode(baseName + str(i))
        newNode.transform = tr.translate(0.7 * i - 0.7, 0, 0)
        newNode.childs += [naveEscalada]
        naves.childs += [newNode]

    return naves


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


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 450
    height = 600

    window = glfw.create_window(width, height, "Space War Alpha 2", None, None)

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
    playerNave.transform = tr.uniformScale(0.15)
    playerNave.childs += [crearNave(0.2, 0.6, 1)]

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    t0 = glfw.get_time()
    player_pos = [0,0]
    velocidad = 700

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        player_pos = moverPlayer(player_pos, velocidad, dt, width, height)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Modificando la nave del jugador:
        playerNave.transform = np.matmul(tr.translate(player_pos[0]/width,player_pos[1]/height,0),
                                         tr.uniformScale(0.15))

        # Dibujar las naves
        sg.drawSceneGraphNode(playerNave, pipeline, "transform")

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    
    glfw.terminate()
