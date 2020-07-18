# coding=utf-8

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from PIL import Image
from random import *
import json
import sys

import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es
import lighting_shaders as ls
import local_shapes as locs

#archivoJSON = sys.argv[1]
archivoJSON = "view-setup.json"
setup = json.load(open(archivoJSON))

# Cargar la matriz "u"
with open(setup["filename"], "rb") as file:
    u = np.load(file)

LIGHT_FLAT    = 0
LIGHT_GOURAUD = 1
LIGHT_PHONG   = 2

VOXELS_NONE = 0
VOXELS_A    = 1
VOXELS_B    = 2
VOXELS_C    = 3


# A class to store the application control
class Controller:
    def __init__(self):
        self.lightingModel = LIGHT_GOURAUD
        self.voxels = VOXELS_NONE


# We will use the global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_Q:
        controller.lightingModel = LIGHT_FLAT

    elif key == glfw.KEY_W:
        controller.lightingModel = LIGHT_GOURAUD

    elif key == glfw.KEY_E:
        controller.lightingModel = LIGHT_PHONG

    elif key == glfw.KEY_0:
        controller.voxels = VOXELS_NONE

    elif key == glfw.KEY_A:
        controller.voxels = VOXELS_A

    elif key == glfw.KEY_B:
        controller.voxels = VOXELS_B

    elif key == glfw.KEY_C:
        controller.voxels = VOXELS_C

    elif key == glfw.KEY_ESCAPE:
        sys.exit()
        

def zonasAptas():
    global u, setup
    aptas_A = []
    aptas_B = []
    aptas_C = []
    
    for i in range(1, u.shape[0]-1):
        for j in range(1, u.shape[1]-1):
            for k in range(1, u.shape[2]-1):
                if (u[i,j,k] >= setup["t_a"]-2) and (u[i,j,k] <= setup["t_a"]+2):
                    aptas_A += [[i,j,k]]
                if (u[i,j,k] >= setup["t_b"]-2) and (u[i,j,k] <= setup["t_b"]+2):
                    aptas_B += [[i,j,k]]
                if (u[i,j,k] >= setup["t_c"]-2) and (u[i,j,k] <= setup["t_c"]+2):
                    aptas_C += [[i,j,k]]
                    
    return aptas_A, aptas_B, aptas_C


def LWH(h):
    global u
    return (u.shape[0]-1)*h, (u.shape[1]-1)*h, (u.shape[2]-1)*h                


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 1056
    height = 594

    window = glfw.create_window(width, height, "Aquarium View", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Different shader programs for different texture lighting strategies
    textureFlatPipeline = ls.SimpleTextureFlatShaderProgram()
    textureGouraudPipeline = ls.SimpleTextureGouraudShaderProgram()
    texturePhongPipeline = ls.SimpleTexturePhongShaderProgram()

    # This shader programs do not consider lighting
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()
    texturemvpPipeline = es.SimpleTextureModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Dimensiones del acuario
    h = 0.25
    [L,W,H] = LWH(h)

    # Creating shapes on GPU memory
    acuarioTex = Image.open("texturas/acuario.png")
    acuario = locs.crearAcuario(L,W,H, acuarioTex)
    acuarioBorde = es.toGPUShape(locs.bordeAcuario(L, W, H))
    
    naranjoTex = Image.open("texturas/naranjo.jpg")
    azulTex = Image.open("texturas/azul.jpg")
    negroTex = Image.open("texturas/negro.jpg")
    
    peces_A = locs.variosPeces(setup["n_a"],naranjoTex)
    peces_B = locs.variosPeces(setup["n_b"],azulTex)
    peces_C = locs.variosPeces(setup["n_c"],negroTex)

    pez_theta = 0
    cola_theta = 0

    # Posiciones para peces y voxeles
    [aptas_A, aptas_B, aptas_C] = zonasAptas()
    ocupadas = []

    for p in range(setup["n_a"]):
        while True:
            r = randint(0, len(aptas_A)-1)
            if aptas_A[r] not in ocupadas:
                ocupadas.append(aptas_A[r])
                [rx,ry,rz] = aptas_A[r]
                ang = uniform(0, 2*np.pi)
                pez_p = sg.findNode(peces_A, "pez"+str(p))
                pez_p.transform = tr.matmul([tr.translate(rx*h-L/2, ry*h-W/2, rz*h-H/2), tr.rotationZ(ang)])
                break
            
    for p in range(setup["n_b"]):
        while True:
            r = randint(0, len(aptas_B)-1)
            if aptas_B[r] not in ocupadas:
                ocupadas.append(aptas_B[r])
                [rx,ry,rz] = aptas_B[r]
                ang = uniform(0, 2*np.pi)
                pez_p = sg.findNode(peces_B, "pez"+str(p))
                pez_p.transform = tr.matmul([tr.translate(rx*h-L/2, ry*h-W/2, rz*h-H/2), tr.rotationZ(ang)])
                break
            
    for p in range(setup["n_c"]):
        while True:
            r = randint(0, len(aptas_C)-1)
            if aptas_C[r] not in ocupadas:
                ocupadas.append(aptas_C[r])
                [rx,ry,rz] = aptas_C[r]
                ang = uniform(0, 2*np.pi)
                pez_p = sg.findNode(peces_C, "pez"+str(p))
                pez_p.transform = tr.matmul([tr.translate(rx*h-L/2, ry*h-W/2, rz*h-H/2), tr.rotationZ(ang)])
                break

    # Posición de la fuente de luz
    sun = np.array([0, 0, 5])

    t0 = glfw.get_time()
    camera_theta = -np.pi/2
    camera_gamma = np.pi/2
    camera_zoom = 7

    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Movimiento de la cámara
        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt

        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS) and (camera_gamma > 0.05):
            camera_gamma -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS) and (camera_gamma < np.pi-0.05):
            camera_gamma += 2 * dt

        if (glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS) and (camera_zoom > 2):
            camera_zoom -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS) and (camera_zoom < 10):
            camera_zoom += 2 * dt
        
        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

        camX = camera_zoom * np.cos(camera_theta) * np.sin(camera_gamma)
        camY = camera_zoom * np.sin(camera_theta) * np.sin(camera_gamma)
        camZ = camera_zoom * np.cos(camera_gamma)

        viewPos = np.array([camX,camY,camZ])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        model = tr.identity()

        # Movimientos del pez
        cola_theta += dt * 2.5
        pez_theta = cola_theta - 3.7
        rot1 = np.sin(cola_theta) * 0.5
        rot2 = np.sin(pez_theta) * 0.2

        sgnCola = sg.findNode(peces_A, "cola")
        sgnCola.transform = tr.matmul([tr.translate(0,-0.8,0),tr.rotationZ(rot1)])
        sgnPez = sg.findNode(peces_A, "pez")
        sgnPez.transform = tr.rotationZ(rot2)
        sgnCola = sg.findNode(peces_B, "cola")
        sgnCola.transform = tr.matmul([tr.translate(0,-0.8,0),tr.rotationZ(rot1)])
        sgnPez = sg.findNode(peces_B, "pez")
        sgnPez.transform = tr.rotationZ(rot2)
        sgnCola = sg.findNode(peces_C, "cola")
        sgnCola.transform = tr.matmul([tr.translate(0,-0.8,0),tr.rotationZ(rot1)])
        sgnPez = sg.findNode(peces_C, "pez")
        sgnPez.transform = tr.rotationZ(rot2)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Selecting the shape to display
##        if controller.voxels == VOXELS_NONE:
##            gpuShape = 
##        elif controller.voxels == VOXELS_A:
##            gpuShape = 
##        elif controller.voxels == VOXELS_B:
##            gpuShape = 
##        elif controller.voxels == VOXELS_C:
##            gpuShape = 
##        else:
##            raise Exception()

        # Selecting the lighting shader program
        if controller.lightingModel == LIGHT_FLAT:
            textureLightingPipeline = textureFlatPipeline
        elif controller.lightingModel == LIGHT_GOURAUD:
            textureLightingPipeline = textureGouraudPipeline
        elif controller.lightingModel == LIGHT_PHONG:
            #textureLightingPipeline = textureGouraudPipeline
            textureLightingPipeline = texturePhongPipeline
        else:
            raise Exception()


        # MVP Pipeline Drawing ----------------------------------------------------------------------------------------
        glUseProgram(mvpPipeline.shaderProgram)

        # Setting all uniform shader variables
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        # Drawing
        mvpPipeline.drawShape(acuarioBorde, GL_LINES)

        # Texture Lighting Pipeline Drawing ---------------------------------------------------------------------------
        glUseProgram(textureLightingPipeline.shaderProgram)

        # Setting all uniform shader variables
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Kd"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "lightPosition"), sun[0], sun[1], sun[2])
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "viewPosition"), 0, 0, 0)
        glUniform1ui(glGetUniformLocation(textureLightingPipeline.shaderProgram, "shininess"), 100)
        
        glUniform1f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(textureLightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureLightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureLightingPipeline.shaderProgram, "model"), 1, GL_TRUE, model)

        # Drawing
        sg.drawSceneGraphNode(peces_A, textureLightingPipeline, "model")
        sg.drawSceneGraphNode(peces_B, textureLightingPipeline, "model")
        sg.drawSceneGraphNode(peces_C, textureLightingPipeline, "model")

        # Texture MVP Pipeline Drawing --------------------------------------------------------------------------------
        glUseProgram(texturemvpPipeline.shaderProgram)

        # Setting all uniform shader variables
        glUniformMatrix4fv(glGetUniformLocation(texturemvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(texturemvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(texturemvpPipeline.shaderProgram, "model"), 1, GL_TRUE, model)

        # Drawing
        sg.drawSceneGraphNode(acuario, texturemvpPipeline, "model")

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
