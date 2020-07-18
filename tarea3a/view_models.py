# coding=utf-8
"""
Daniel Calderon, CC3501, 2019-2
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from PIL import Image
import sys

import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es
import lighting_shaders as ls
import local_shapes as locs

print("Cargar archivo de textura:")
texPez = input(">> texturas/")

LIGHT_FLAT    = 0
LIGHT_GOURAUD = 1
LIGHT_PHONG   = 2

SHAPE_CUERPO    = 0
SHAPE_COLA      = 1
SHAPE_PEZ       = 2


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = False
        self.lightingModel = LIGHT_GOURAUD
        self.shape = SHAPE_PEZ


# We will use the global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_LEFT_CONTROL:
        controller.showAxis = not controller.showAxis

    elif key == glfw.KEY_Q:
        controller.lightingModel = LIGHT_FLAT

    elif key == glfw.KEY_W:
        controller.lightingModel = LIGHT_GOURAUD

    elif key == glfw.KEY_E:
        controller.lightingModel = LIGHT_PHONG

    elif key == glfw.KEY_1:
        controller.shape = SHAPE_PEZ

    elif key == glfw.KEY_2:
        controller.shape = SHAPE_CUERPO

    elif key == glfw.KEY_3:
        controller.shape = SHAPE_COLA

    elif key == glfw.KEY_ESCAPE:
        sys.exit()
        

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Visualizador de Modelos 3D", None, None)

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

    # This shader program does not consider lighting
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    texture = Image.open("texturas/" + texPez)
    gpuAxis = es.toGPUShape(bs.createAxis(4))
    gpuFishBody = es.toGPUShape(locs.fishBody(texture), GL_REPEAT, GL_LINEAR)
    gpuCola = es.toGPUShape(locs.cola(texture), GL_REPEAT, GL_LINEAR)
    sgnPez = locs.crearPez(texture)

    pez_theta = 0
    cola_theta = 0

    t0 = glfw.get_time()
    camera_theta = -2
    camera_gamma = 1

    lightX = 0
    lightY = 0
    lightZ = 4
    lightSpeed = 10

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

        # Movimiento de la luz
        if (glfw.get_key(window, glfw.KEY_Z) == glfw.PRESS):
            lightX -= lightSpeed * dt

        if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
            lightX += lightSpeed * dt

        if (glfw.get_key(window, glfw.KEY_X) == glfw.PRESS):
            lightY -= lightSpeed * dt

        if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
            lightY += lightSpeed * dt

        if (glfw.get_key(window, glfw.KEY_C) == glfw.PRESS):
            lightZ -= lightSpeed * dt

        if (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
            lightZ += lightSpeed * dt
        
        #projection = tr.ortho(-3, 3, -3, 3, 0.1, 100)
        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

        camX = 3 * np.cos(camera_theta) * np.sin(camera_gamma)
        camY = 3 * np.sin(camera_theta) * np.sin(camera_gamma)
        camZ = 3 * np.cos(camera_gamma)

        viewPos = np.array([camX,camY,camZ])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        axis = np.array([1,-1,1])
        axis = axis / np.linalg.norm(axis)
        #model = tr.rotationA(rotation_theta, axis)
        model = tr.identity()

        # Movimientos del pez
        cola_theta += dt * 2.5
        pez_theta = cola_theta - 3.7
        rot1 = np.sin(cola_theta) * 0.5
        rot2 = np.sin(pez_theta) * 0.2

        sgnCola = sg.findNode(sgnPez, "cola")
        sgnCola.transform = tr.matmul([tr.translate(0,-0.8,0),tr.rotationZ(rot1)])
        sgnPez.transform = tr.rotationZ(rot2)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # The axis is drawn without lighting effects
        if controller.showAxis:
            glUseProgram(mvpPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            mvpPipeline.drawShape(gpuAxis, GL_LINES)

        # Selecting the shape to display
        if controller.shape == SHAPE_CUERPO:
            gpuShape = gpuFishBody
        elif controller.shape == SHAPE_COLA:
            gpuShape = gpuCola
        elif controller.shape == SHAPE_PEZ:
            gpuShape = gpuCola
        else:
            raise Exception()

        # Selecting the lighting shader program
        if controller.lightingModel == LIGHT_FLAT:
            textureLightingPipeline = textureFlatPipeline
        elif controller.lightingModel == LIGHT_GOURAUD:
            textureLightingPipeline = textureGouraudPipeline
        elif controller.lightingModel == LIGHT_PHONG:
            textureLightingPipeline = texturePhongPipeline
        else:
            raise Exception()


        # Texture Lighting Pipeline Drawing ---------------------------------------------------------------------------

        glUseProgram(textureLightingPipeline.shaderProgram)

        # Setting all uniform shader variables

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Kd"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # TO DO: Explore different parameter combinations to understand their effect!

        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "lightPosition"), lightX, lightY, lightZ)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "viewPosition"), 0, 0, 0)
        glUniform1ui(glGetUniformLocation(textureLightingPipeline.shaderProgram, "shininess"), 100)
        
        glUniform1f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(textureLightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureLightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureLightingPipeline.shaderProgram, "model"), 1, GL_TRUE, model)

        # Drawing
        if controller.shape == SHAPE_PEZ:
            sg.drawSceneGraphNode(sgnPez, textureLightingPipeline, "model")
        else:
            textureLightingPipeline.drawShape(gpuShape)
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
