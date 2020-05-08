# coding=utf-8
"""
Space War Alpha 5
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
from game_shapes import *

#N = sys.argv[1]

class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.disparando = False
        self.reloj = 0

controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return

    if key == glfw.KEY_ESCAPE:
        sys.exit()

    if key == glfw.KEY_SPACE:
        controller.disparando = True

    if key == glfw.KEY_0:
        controller.fillPolygon = not controller.fillPolygon


def moverPlayer(player_pos, velocidad, dt):

    # Configurar modificador de velocidad según si la nave va en diagonal o no
    if ((glfw.get_key(window, glfw.KEY_A) == glfw.PRESS) and (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS)) \
    or ((glfw.get_key(window, glfw.KEY_A) == glfw.PRESS) and (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS)) \
    or ((glfw.get_key(window, glfw.KEY_D) == glfw.PRESS) and (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS)) \
    or ((glfw.get_key(window, glfw.KEY_D) == glfw.PRESS) and (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS)):
        modificador = 0.707
    else:
        modificador = 1

    limite = 0.1

    # Cambiar la posición del jugador (dentro de los límites de la pantalla) según la tecla presionada
    if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS) and (player_pos[0] > (-1 + limite)):
        player_pos[0] -= velocidad * modificador * dt

    if (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS) and (player_pos[0] < (1 - limite)):
        player_pos[0] += velocidad * modificador * dt

    if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS) and (player_pos[1] > (-1 + limite)):
        player_pos[1] -= velocidad * modificador * dt * 3/4

    if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS) and (player_pos[1] < (1 - limite)):
        player_pos[1] += velocidad * modificador * dt * 3/4

    return player_pos    


def moverEnemigos(rojos_vars, velocidad, dt):
    for r in range(len(rojos_vars)):
        if (rojos_vars[r][0][0] < -1.3) or (rojos_vars[r][0][0] > 1.3) \
           or ((rojos_vars[r][0][1] < -1.3) and (rojos_vars[r][0][1] > -2)):
               
            posX = random()*2 -1
            amplitud = 0.75 # Rango de direcciones posibles. Valor entre 0 y 1
            angulo = np.pi * (random()*amplitud + (1 - amplitud)/2)
            dirX = np.cos(angulo)
            dirY = np.sin(angulo)*-3/4

            rojos_vars[r] = [[posX, 1.1], [dirX, dirY]]

        else:
            dirX = rojos_vars[r][1][0]
            dirY = rojos_vars[r][1][1]
            rojos_vars[r][0][0] += dt * dirX * velocidad
            rojos_vars[r][0][1] += dt * dirY * velocidad
               
    return rojos_vars


def moverLasers(lasers_vars, player_pos, rojos_vars, dt, rojosEnPantalla):
    global controller

    # LASERS DEL JUGADOR
    for i in range(1,6): # Cada laser del jugador
        if lasers_vars[0][i][1] < 2:
            lasers_vars[0][i][1] += 4 * dt
    if (controller.disparando == True):
        laserADisparar = lasers_vars[0][0] +1
        # El laser tomará la posición del jugador
        posX = player_pos[0]
        posY = player_pos[1]
        lasers_vars[0][laserADisparar] = [posX,posY]
        # Se prepara el siguiente laser del jugador
        lasers_vars[0][0] = laserADisparar % 5
        # Se modifica el controlador
        controller.disparando = False

    # LASERS DE LOS ENEMIGOS
    for i in range(1,rojosEnPantalla+1): # Set de datos de cada enemigo
        for j in range(1,4): # Cada laser del enemigo "i"
            if lasers_vars[i][j][1] > -2:
                lasers_vars[i][j][1] -= 2 * dt
        if controller.reloj >= lasers_vars[i][0][1]: # Momento de disparar
            laserADisparar = lasers_vars[i][0][0] +1
            # El laser tomará la posición del enemigo "i"
            posX = rojos_vars[i-1][0][0]
            posY = rojos_vars[i-1][0][1]
            lasers_vars[i][laserADisparar] = [posX,posY]
            # Se prepara el siguiente laser de "i"
            lasers_vars[i][0][0] = laserADisparar % 3
            # Se define el momento del siguiente disparo
            lasers_vars[i][0][1] += 0.8 # Intervalo de disparo

    return lasers_vars


# Inicio del programa --------------------------------------------------------

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()
        
    width = 450
    height = 600

    window = glfw.create_window(width, height, "Space War Alpha 5", None, None)

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
    ## Naves
    playerNave = sg.SceneGraphNode("playerNave")
    playerNave.childs += [crearNave(0.2, 0.6, 1)]

    rojosEnPantalla = 3 # Máximo de enemigos simultáneamente en pantalla
    navesEnemigas = variosEnemigos(rojosEnPantalla)

    ## Escenario
    densidadFondo = 3 # Determina la cantidad de planetas (x2) y estrellas (x6)
    detalleFondo = 10 # Determina los lados de los planetas (x2) y las estrellas (x1)
    
    planetasA = variosPlanetas(densidadFondo, detalleFondo*2)
    planetasB = variosPlanetas(densidadFondo, detalleFondo*2)

    estrellasA = variasEstrellas(densidadFondo*3, detalleFondo)
    estrellasB = variasEstrellas(densidadFondo*3, detalleFondo)

    ## Disparos
    lasers = variosLasers(rojosEnPantalla)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Variables iniciales
    t0 = glfw.get_time()
    abc = ["A","B","C","D","E","F","G"]
    velocidadA = 1.55 # Afecta al jugador y al fondo
    velocidadB = 1.3 # Afecta a los enemigos
    
    player_pos = [0,-0.6] # Posición del jugador
    planA_posY = 0 # Posición vertical del grupo de planetas A
    planB_posY = 6 # Posición vertical del grupo de planetas B
    estrA_posY = 0 # Posición vertical del grupo de estrellas A
    estrB_posY = 6 # Posición vertical del grupo de estrellas B

    # Lista de 3 dimensiones que indica posición y dirección de los enemigos
    ##          [[posX,posY],[dirX,dirY]]
    rojos_vars = [[[0, -1.5], [0, 0]]] # Valores para el primer enemigo
    for r in range(rojosEnPantalla-1):
        #               [[posX,posY],[dirX,dirY]]
        rojos_vars.append([[0, -1.5], [0, 0]])

    # Lista de 3 dimensiones que indica laser en uso y posición de los lasers
    ##    [laserEnUso,posLaserA,posLaserB,posLaserC,posLaserD,posLaserE]
    lasers_vars = [[0, [0, 2.5], [0, 2.5], [0, 2.5], [0, 2.5], [0, 2.5]]]
    for i in range(rojosEnPantalla): # Lasers enemigos
        clock = random()
        #       [[laserEnUso,sgteMomento],posLaserA,posLaserB,posLaserC]
        lasers_vars.append([[0, clock], [0, -2.5], [0, -2.5], [0, -2.5]])


    # Ciclo principal ------------------------------------------------------
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        controller.reloj = t1
        dt = t1 - t0
        t0 = t1

        # Modificando variables de posiciones:
        player_pos = moverPlayer(player_pos, velocidadA, dt)
        rojos_vars = moverEnemigos(rojos_vars, velocidadB, dt)
        lasers_vars = moverLasers(lasers_vars, player_pos, rojos_vars, dt, rojosEnPantalla)

        planA_posY -= dt * velocidadA * 1.3
        if planA_posY <= -6:
            planA_posY = 6
        planB_posY -= dt * velocidadA * 1.3
        if planB_posY <= -6:
            planB_posY = 6

        estrA_posY -= dt * velocidadA * 0.45
        if estrA_posY <= -6:
            estrA_posY = 6
        estrB_posY -= dt * velocidadA * 0.45
        if estrB_posY <= -6:
            estrB_posY = 6

        # Modificando transformadas de traslación:
        playerNave.transform = tr.translate(player_pos[0], player_pos[1], 0)
        planetasA.transform = tr.translate(0, planA_posY, 0)
        planetasB.transform = tr.translate(0, planB_posY, 0)
        estrellasA.transform = tr.translate(0, estrA_posY, 0)
        estrellasB.transform = tr.translate(0, estrB_posY, 0)

        for r in range(rojosEnPantalla):
            enemigo = sg.findNode(navesEnemigas, "enemigo"+str(r))
            enemigo.transform = tr.translate(rojos_vars[r][0][0], rojos_vars[r][0][1], 0)

        for i in range(1,6):
            laserPlayer = sg.findNode(lasers, "laserPlayer"+abc[i-1])
            laserPlayer.transform = tr.translate(lasers_vars[0][i][0], lasers_vars[0][i][1], 0)

        for i in range(1,rojosEnPantalla+1):
            for j in range(1,4):
                laserEnemigo = sg.findNode(lasers, "laserEnemigo"+str(i-1)+abc[j-1])
                laserEnemigo.transform = tr.translate(lasers_vars[i][j][0], lasers_vars[i][j][1], 0)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Dibujando los nodos
        sg.drawSceneGraphNode(estrellasA, pipeline, "transform")
        sg.drawSceneGraphNode(estrellasB, pipeline, "transform")
        sg.drawSceneGraphNode(planetasA, pipeline, "transform")
        sg.drawSceneGraphNode(planetasB, pipeline, "transform")
        sg.drawSceneGraphNode(lasers, pipeline, "transform")
        sg.drawSceneGraphNode(navesEnemigas, pipeline, "transform")
        sg.drawSceneGraphNode(playerNave, pipeline, "transform")

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)


    glfw.terminate()
