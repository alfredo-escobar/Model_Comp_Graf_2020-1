# coding=utf-8
"""
Daniel Calderon, CC3501, 2019-2
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import transformations as tr
import basic_shapes as bs
import easy_shaders as es
import lighting_shaders as ls
import local_shapes as locs


LIGHT_FLAT    = 0
LIGHT_GOURAUD = 1
LIGHT_PHONG   = 2


SHAPE_CUERPO    = 0
SHAPE_ALA_BASE  = 1
SHAPE_ALA_MEDIO = 2
SHAPE_ALA_PUNTA = 3
SHAPE_COLA      = 4
SHAPE_CABEZA    = 5
SHAPE_PICO      = 6


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.lightingModel = LIGHT_PHONG
        self.shape = SHAPE_CUERPO


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
        controller.shape = SHAPE_CUERPO

    elif key == glfw.KEY_2:
        controller.shape = SHAPE_ALA_BASE

    elif key == glfw.KEY_3:
        controller.shape = SHAPE_ALA_MEDIO

    elif key == glfw.KEY_4:
        controller.shape = SHAPE_ALA_PUNTA

    elif key == glfw.KEY_5:
        controller.shape = SHAPE_COLA

    elif key == glfw.KEY_6:
        controller.shape = SHAPE_CABEZA

    elif key == glfw.KEY_7:
        controller.shape = SHAPE_PICO

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

    # Different shader programs for different lighting strategies
    flatPipeline = ls.SimpleFlatShaderProgram()
    gouraudPipeline = ls.SimpleGouraudShaderProgram()
    phongPipeline = ls.SimplePhongShaderProgram()

    # This shader program does not consider lighting
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = es.toGPUShape(bs.createAxis(4))
    gpuBirdBody = es.toGPUShape(locs.birdBody([0.1,0.6,1]))
    gpuAlaBase = es.toGPUShape(locs.alaBase([0.1,0.6,1]))
    gpuAlaMedio = es.toGPUShape(locs.alaMedio([0.1,0.6,1]))
    gpuAlaPunta = es.toGPUShape(locs.alaPunta([0.1,0.6,1]))
    gpuCola = es.toGPUShape(locs.cola([0.1,0.6,1]))
    gpuCabeza = es.toGPUShape(locs.generateSphereShape([0.1,0.6,1]))
    gpuPico = es.toGPUShape(locs.pico([0.1,0.6,1]))

    t0 = glfw.get_time()
    camera_theta = -2
    camera_gamma = 1

    lightX = -5
    lightY = -5
    lightZ = 5
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
        
        projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)
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

        rotation_theta = glfw.get_time()

        axis = np.array([1,-1,1])
        #axis = np.array([0,0,1])
        axis = axis / np.linalg.norm(axis)
        model = tr.rotationA(rotation_theta, axis)
        model = tr.identity()

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
            gpuShape = gpuBirdBody
        elif controller.shape == SHAPE_ALA_BASE:
            gpuShape = gpuAlaBase
        elif controller.shape == SHAPE_ALA_MEDIO:
            gpuShape = gpuAlaMedio
        elif controller.shape == SHAPE_ALA_PUNTA:
            gpuShape = gpuAlaPunta
        elif controller.shape == SHAPE_COLA:
            gpuShape = gpuCola
        elif controller.shape == SHAPE_CABEZA:
            gpuShape = gpuCabeza
        elif controller.shape == SHAPE_PICO:
            gpuShape = gpuPico
        else:
            raise Exception()

        # Selecting the lighting shader program
        if controller.lightingModel == LIGHT_FLAT:
            lightingPipeline = flatPipeline
        elif controller.lightingModel == LIGHT_GOURAUD:
            lightingPipeline = gouraudPipeline
        elif controller.lightingModel == LIGHT_PHONG:
            lightingPipeline = phongPipeline
        else:
            raise Exception()
        
        glUseProgram(lightingPipeline.shaderProgram)

        # Setting all uniform shader variables

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # TO DO: Explore different parameter combinations to understand their effect!

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), lightX, lightY, lightZ)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)
        
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, model)

        # Drawing
        lightingPipeline.drawShape(gpuShape)
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
