# coding=utf-8
"""
Space War Beta 2.1
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

if len(sys.argv) == 1:
    N = int(input("Cantidad de enemigos: "))
else:
    N = int(sys.argv[1])

class Controller:
    def __init__(self):
        self.disparando = False
        self.reloj = 0
        self.vidas = 3
        self.playerHit = False
        self.enemigosTotal = N

controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return

    if key == glfw.KEY_ESCAPE:
        sys.exit()

    if key == glfw.KEY_SPACE:
        controller.disparando = True


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

            rojos_vars[r] = [[posX, 1.05], [dirX, dirY]]

        elif (rojos_vars[r][0][1] > -2):
            dirX = rojos_vars[r][1][0]
            dirY = rojos_vars[r][1][1]
            rojos_vars[r][0][0] += dt * dirX * velocidad
            rojos_vars[r][0][1] += dt * dirY * velocidad

            # Colisión enemigo-jugador
            if (((rojos_vars[r][0][1] - player_pos[1]) < 0.2) \
               and ((rojos_vars[r][0][1] - player_pos[1]) >= 0.05) \
               and (abs(rojos_vars[r][0][0] - player_pos[0]) < 0.14)) \
               or (((rojos_vars[r][0][1] - player_pos[1]) < 0.05) \
               and ((player_pos[1] - rojos_vars[r][0][1]) < 0.205) \
               and (abs(rojos_vars[r][0][0] - player_pos[0]) < 0.24)):
                rojos_vars[r][0][1] = -1.5
                controller.playerHit = True
               
    return rojos_vars


def moverLasers(lasers_vars, player_pos, rojos_vars, dt, rojosEnPantalla):

    # Avance de los láseres del jugador
    for i in range(1,6): # Cada láser del jugador
        if lasers_vars[0][i][1] < 2:
            lasers_vars[0][i][1] += 4 * dt
            # Colisión láser-enemigo
            for j in range(rojosEnPantalla):
                if (rojos_vars[j][0][1] < 0.95) \
                   and (abs(rojos_vars[j][0][0] - lasers_vars[0][i][0]) < 0.18) \
                   and (abs(rojos_vars[j][0][1] - lasers_vars[0][i][1]) < 0.165):
                    controller.enemigosTotal -= 1
                    lasers_vars[0][i][1] = 2.5
                    if (controller.enemigosTotal < rojosEnPantalla):
                        rojos_vars[j][0][1] = -2.5
                    else:
                        rojos_vars[j][0][1] = -1.5
                        
    # Disparo del láser preparado del jugador
    if (controller.disparando == True):
        laserADisparar = lasers_vars[0][0] +1
        # El láser tomará la posición del jugador
        posX = player_pos[0]
        posY = player_pos[1]
        lasers_vars[0][laserADisparar] = [posX,posY]
        # Se prepara el siguiente láser del jugador
        lasers_vars[0][0] = laserADisparar % 5
        # Se modifica el controlador
        controller.disparando = False

    for i in range(1,rojosEnPantalla+1): # Set de datos de cada enemigo
        
        # Avance de los láseres del enemigo "i"
        for j in range(1,4): # Cada láser del enemigo "i"
            if lasers_vars[i][j][1] > -2:
                lasers_vars[i][j][1] -= 2 * dt
                # Colisión láser-jugador
                if (((lasers_vars[i][j][1] - player_pos[1]) < 0.165) \
                   and ((lasers_vars[i][j][1] - player_pos[1]) >= 0.025) \
                   and (abs(lasers_vars[i][j][0] - player_pos[0]) < 0.06)) \
                   or (((lasers_vars[i][j][1] - player_pos[1]) < 0.025) \
                   and ((player_pos[1] - lasers_vars[i][j][1]) < 0.17) \
                   and (abs(lasers_vars[i][j][0] - player_pos[0]) < 0.17)):
                    lasers_vars[i][j][1] = -2.5
                    controller.playerHit = True
        
        # Disparo del láser preparado del enemigo "i"
        if controller.reloj >= lasers_vars[i][0][1]: # Momento de disparar
            laserADisparar = lasers_vars[i][0][0] +1
            # El láser tomará la posición del enemigo "i"
            posX = rojos_vars[i-1][0][0]
            posY = rojos_vars[i-1][0][1]
            lasers_vars[i][laserADisparar] = [posX,posY]
            # Se prepara el siguiente láser de "i"
            lasers_vars[i][0][0] = laserADisparar % 3
            # Se define el momento del siguiente disparo
            lasers_vars[i][0][1] += 0.8 # Intervalo de disparo

    return lasers_vars


def gameProgress(barraHP, tex_Y, dt):
    if (controller.playerHit == True) and (controller.vidas > 0):
        controller.vidas -= 1
        cuadroHP = sg.findNode(barraHP, "cuadroHP"+str(controller.vidas))
        cuadroHP.transform = tr.translate(0, 1.1, 0)
        controller.playerHit = False

    if controller.vidas <= 0:
        if tex_Y < 0:
            tex_Y += 2*dt

    elif controller.enemigosTotal <= 0:
        if tex_Y < 0:
            tex_Y += 2*dt

    return tex_Y


# Inicio del programa --------------------------------------------------------

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()
        
    width = 450
    height = 600

    window = glfw.create_window(width, height, "Space War", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline = es.SimpleTransformShaderProgram()
    pipeline2 = es.SimpleTextureTransformShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.0, 0.0, 0.1, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Creating shapes on GPU memory
    ## Naves
    azulNave = sg.SceneGraphNode("azulNave")
    azulNave.childs += [crearNave(0.2, 0.6, 1)]

    playerNave = sg.SceneGraphNode("playerNave")
    playerNave.childs += [azulNave]

    playerIcon = sg.SceneGraphNode("playerIcon")
    playerIcon.transform = np.matmul(tr.translate(-0.9,0.9,0),tr.uniformScale(0.4))
    playerIcon.childs += [azulNave]

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

    ## Otros (UI)
    barraHP = barraVida(0.2, 0.6, 1)
    gpuWin = es.toGPUShape(bs.createTextureQuad("sprite1.png"), GL_REPEAT, GL_NEAREST)
    gpuLose = es.toGPUShape(bs.createTextureQuad("sprite2.png"), GL_REPEAT, GL_NEAREST)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Variables iniciales
    t0 = glfw.get_time()
    abc = ["A","B","C","D","E","F","G"]
    velocidadA = 1.55 # Afecta al jugador y al fondo
    velocidadB = 1.3 # Afecta a los enemigos
    tex_Y = -1.2 # Posición en Y de las texturas
    
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
        rojos_vars.append([[0, -2.5], [0, 0]])

    # Controlador de aparición de enemigos ([sgteEnemigo, momentoDeAparicion]
    rojos_spawn = [1, 5] 
    
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

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        controller.reloj = t1
        dt = t1 - t0
        t0 = t1
        
        # Aparición de más enemigos en pantalla
        if (rojos_spawn[0] < min(rojosEnPantalla, controller.enemigosTotal)) \
            and (controller.reloj >= rojos_spawn[1]) and (controller.enemigosTotal > 0):
            rojos_vars[rojos_spawn[0]][0][1] = -1.5
            rojos_spawn[0] += 1
            rojos_spawn[1] += 5 # Intervalo de aparición
        
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

        tex_Y = gameProgress(barraHP, tex_Y, dt)

        # Dibujando los nodos
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(estrellasA, pipeline, "transform")
        sg.drawSceneGraphNode(estrellasB, pipeline, "transform")
        sg.drawSceneGraphNode(planetasA, pipeline, "transform")
        sg.drawSceneGraphNode(planetasB, pipeline, "transform")
        sg.drawSceneGraphNode(lasers, pipeline, "transform")
        sg.drawSceneGraphNode(navesEnemigas, pipeline, "transform")
        sg.drawSceneGraphNode(playerNave, pipeline, "transform")
        sg.drawSceneGraphNode(playerIcon, pipeline, "transform")
        sg.drawSceneGraphNode(barraHP, pipeline, "transform")
        
        # Dibujando las texturas
        if controller.vidas <= 0:
            glUseProgram(pipeline2.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
                    tr.translate(0, tex_Y, 0),
                    tr.scale(1.0, 0.141, 1.0)]))
            pipeline2.drawShape(gpuLose)
            
        elif controller.enemigosTotal <= 0:
            glUseProgram(pipeline2.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
                    tr.translate(0, tex_Y, 0),
                    tr.scale(1.0, 0.149, 1.0)]))
            pipeline2.drawShape(gpuWin)
        

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)


    glfw.terminate()
