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
import lighting_shaders as ls
import local_shapes as locs


LIGHT_FLAT    = 0
LIGHT_GOURAUD = 1
LIGHT_PHONG   = 2


# A class to store the application control
class Controller:
    def __init__(self):
        self.lightingModel = LIGHT_PHONG


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

    elif key == glfw.KEY_ESCAPE:
        sys.exit()
        

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 1120
    height = 630

    window = glfw.create_window(width, height, "Bird Herd", None, None)

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

    # Different shader programs for different texture lighting strategies
    textureFlatPipeline = ls.SimpleTextureFlatShaderProgram()
    textureGouraudPipeline = ls.SimpleTextureGouraudShaderProgram()
    #texturePhongPipeline = ls.SimpleTexturePhongShaderProgram()

    # This shader program does not consider lighting
    texturemvpPipeline = es.SimpleTextureModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Creating shapes on GPU memory
    cantAves = 5
    aves = locs.variasAves(cantAves)
    aves.transform = tr.translate(0,1.5,0.5)

    cubeMap1 = es.toGPUShape(locs.createTextureInnerNormalsCubeMap("cubemap1.png"), GL_REPEAT, GL_LINEAR)
    cubeMap2 = es.toGPUShape(locs.createTextureCubeMap("cubemap2.png"), GL_REPEAT, GL_LINEAR)
    palos = locs.palos()

    # Valores de rotación
    rot1 = 0 # Punta del ala
    rot2 = 0 # Mitad del ala
    rot3 = 0 # Ala completa
    alas_theta = 0

    sun = np.array([7.75, 2.86, 5.62])

    t0 = glfw.get_time()
    camera_theta = np.pi/2
    camera_gamma = np.pi/2

    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Obteniendo la posición del mouse
        [mouseX, mouseY] = glfw.get_cursor_pos(window)
        mouseX = 2*mouseX/width - 1
        mouseY = -2*mouseY/height + 1

        # Movimiento de la cámara
        if (mouseX < 1) and (mouseX > -1) and (mouseY < 1) and (mouseY > -1):
            camera_theta = np.pi/2 - np.pi*mouseX
            camera_gamma = (np.pi/2 - np.pi*mouseY/2) * 0.99
        
        projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)
        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

        camX = 5 * np.cos(camera_theta) * np.sin(camera_gamma)
        camY = 5 * np.sin(camera_theta) * np.sin(camera_gamma)
        camZ = 5 * np.cos(camera_gamma)

        viewPos = np.array([camX,camY,camZ])

        view = tr.lookAt(
            np.array([0,0,0]),
            viewPos,
            np.array([0,0,1])
        )

        rotation_theta = glfw.get_time()

        axis = np.array([1,-1,1])
        axis = axis / np.linalg.norm(axis)
        model = tr.identity()

        # Movimiento de las alas del ave
        alas_theta += dt * 1.5
        rot1 += (rot2*0.67 - rot1) * dt * 2
        rot2 += (rot3*0.75 - rot2) * dt * 2
        rot3 = np.sin(alas_theta) * 0.65
        
        sgnAlaPunta = sg.findNode(aves, "alaPunta")
        sgnAlaPunta.transform = tr.matmul([tr.translate(-0.7,-0.001,-0.001),tr.rotationY(rot1)])

        sgnAlaExt = sg.findNode(aves, "alaExt")
        sgnAlaExt.transform = tr.matmul([tr.translate(-0.7,-0.001,-0.001),tr.rotationY(rot2)])
        
        sgnAlaCompleta = sg.findNode(aves, "alaCompleta")
        sgnAlaCompleta.transform = tr.rotationY(rot3)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Selecting the lighting shader programs
        if controller.lightingModel == LIGHT_FLAT:
            lightingPipeline = flatPipeline
            textureLightingPipeline = textureFlatPipeline
        elif controller.lightingModel == LIGHT_GOURAUD:
            lightingPipeline = gouraudPipeline
            textureLightingPipeline = textureGouraudPipeline
        elif controller.lightingModel == LIGHT_PHONG:
            lightingPipeline = phongPipeline
            textureLightingPipeline = textureGouraudPipeline
            #textureLightingPipeline = texturePhongPipeline
        else:
            raise Exception()

        # Lighting Pipeline Drawing --------------------------------------------------------------------------------
        
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

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), sun[0], sun[1], sun[2])
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), 0, 0, 0)
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)
        
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, model)

        # Drawing
        sg.drawSceneGraphNode(aves, lightingPipeline, "model")

        # Texture MVP Pipeline Drawing --------------------------------------------------------------------------------

        glUseProgram(texturemvpPipeline.shaderProgram)
        
        glUniformMatrix4fv(glGetUniformLocation(texturemvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(texturemvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(texturemvpPipeline.shaderProgram, "model"), 1, GL_TRUE, model)
        
        glUniformMatrix4fv(glGetUniformLocation(texturemvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(20))
        texturemvpPipeline.drawShape(cubeMap2)

        # Texture Lighting Pipeline Drawing ---------------------------------------------------------------------------

        glUseProgram(textureLightingPipeline.shaderProgram)

        # Setting all uniform shader variables

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(textureLightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # TO DO: Explore different parameter combinations to understand their effect!

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
        glUniformMatrix4fv(glGetUniformLocation(textureLightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        textureLightingPipeline.drawShape(cubeMap1)

        sg.drawSceneGraphNode(palos, textureLightingPipeline, "model")

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
