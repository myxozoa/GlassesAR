from OpenGL.GL import *
# from OpenGL.GLUT import *
import glfw
from OpenGL.GLU import *
import cv2
import numpy as np
from webcam import Webcam
from solver import Solver
from loaders import load_shaders, load_OBJ
from PIL import Image
from constants import *
import sys
import ctypes
import glm
import math

lightPositions = [
    glm.vec3(-5.0,  5.0, 5.0),
    glm.vec3( 5.0,  5.0, 5.0),
    # glm.vec3(-5.0, -5.0, 5.0),
    # glm.vec3( 5.0, -5.0, 5.0)
]

lightColors = [
    glm.vec3(300.0, 300.0, 300.0),
    glm.vec3(300.0, 300.0, 300.0),
    # glm.vec3(300.0, 300.0, 300.0),
    # glm.vec3(300.0, 300.0, 300.0)
]

# webcam_verts = np.array([
#   # tex coords   # vert coords
#   0.0, 1.0,    -400, -400, 0.0,
#   1.0, 1.0,     400, -400, 0.0,
#   1.0, 0.0,     400, 400, 0.0,
#   0.0, 0.0,    -400, 400, 0.0
# ], dtype=np.float32)

webcam_verts = np.array([
  # tex coords   # vert coords
  1.0, 1.0,     0.0, 0.0, 0.0,
  0.0, 1.0,     SIZE[0], 0.0, 0.0,
  0.0, 0.0,     SIZE[0], SIZE[1], 0.0,
  1.0, 0.0,    0.0, SIZE[1], 0.0,
], dtype=np.float32)

class Glasses:
  def __init__(self):
    self.INVERSE_MATRIX = np.array(INVERSE_MATRIX)
    self.window = None
    self.webcam = Webcam()
    self.solver = None
    self.webcam_background = None
    self.rotate_y = 0.0
    self.rotate_x = 0.0
    self.scale = 8.0
    self.model_shader = None
    self.webcam_program = None
    self.vbo = None
    self.vao = None

  def setupWindow(self):
    if not glfw.init():
      return

    self.window = glfw.create_window(SIZE[1], SIZE[0], APP_NAME, None, None)
    if not self.window:
      glfw.terminate()
      return

    glfw.make_context_current(self.window)

  def setup_gl_objects(self):
    # setup model data
    self.vao = glGenVertexArrays(1)
    glBindVertexArray(self.vao)

    self.vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
    glBufferData(GL_ARRAY_BUFFER, self.VERTICES.nbytes, self.VERTICES, GL_STATIC_DRAW)

    # Contains the vertex format (string) such as "T2F_N3F_V3F"
    # texcoord_index = glGetAttribLocation(self.model_shader, 'texcoord')
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, ctypes.sizeof(GLfloat) * 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # normal_index = glGetAttribLocation(self.model_shader, 'normal')
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, ctypes.sizeof(GLfloat) * 8, ctypes.c_void_p(2 * ctypes.sizeof(GLfloat)))
    glEnableVertexAttribArray(1)

    # vpos_index = glGetAttribLocation(self.model_shader, 'vposition')
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, ctypes.sizeof(GLfloat) * 8, ctypes.c_void_p(5 * ctypes.sizeof(GLfloat)))
    glEnableVertexAttribArray(2)

    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER,0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)

    # setup webcam data
    self.webcam_vao = glGenVertexArrays(1)
    glBindVertexArray(self.webcam_vao)

    self.webcam_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, self.webcam_vbo)
    glBufferData(GL_ARRAY_BUFFER, webcam_verts.nbytes, webcam_verts, GL_STATIC_DRAW)

    glVertexAttribPointer(4, 2, GL_FLOAT, GL_FALSE, ctypes.sizeof(GLfloat) * 5, ctypes.c_void_p(0))
    glEnableVertexAttribArray(4)
    glVertexAttribPointer(5, 3, GL_FLOAT, GL_FALSE, ctypes.sizeof(GLfloat) * 5, ctypes.c_void_p(2 * ctypes.sizeof(GLfloat)))
    glEnableVertexAttribArray(5)

    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER,0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)

  def set_textures(self):
    print(self.obj.mtl)

  def setup_gl(self):
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClearDepth(1.0)
    # glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
    # glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    # glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    # glLightfv(GL_LIGHT0, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))
    # glEnable(GL_LIGHT0)
    # glEnable(GL_LIGHTING)
    # glEnable(GL_COLOR_MATERIAL)
    # glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    # glShadeModel(GL_SMOOTH)
    # glMatrixMode(GL_PROJECTION)
    # glLoadIdentity()
    # gluPerspective(33.7, 1.3, 0.1, 1000.0)
    # glMatrixMode(GL_MODELVIEW)
    self.model_shader = load_shaders("./shaders/model/vert.glsl", "./shaders/model/frag.glsl")
    self.webcam_shader = load_shaders("./shaders/webcam_feed/vert.glsl", "./shaders/webcam_feed/frag.glsl")

    self.obj = load_OBJ(MODEL)

    self.VERTICES = np.array(self.obj.buffer_data, dtype=np.float32)

    # start webcam thread
    self.webcam.start()

    # initializing solver after opengl context is created
    # self.solver = Solver(self.webcam.camera_matrix, self.webcam.dist_coeffs)

    # assign texture
    self.webcam_background = glGenTextures(1)


  def draw_webcam(self, image):
    # convert image to opengl tex format
    bg_image = cv2.flip(image, 0)
    bg_image = Image.fromarray(bg_image)
    ix = bg_image.size[0]
    iy = bg_image.size[1]
    bg_image = bg_image.tobytes('raw', 'BGRX', 0, -1)

    # create bg texture
    glBindTexture(GL_TEXTURE_2D, self.webcam_background)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, bg_image)

    glBindTexture(GL_TEXTURE_2D, 0)

    # draw bg
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, self.webcam_background)

    glUseProgram(self.webcam_shader)

    projection = glm.ortho(0.0, SIZE[0], 0.0, SIZE[1], 0.1, 100.0)
    glUniformMatrix4fv(glGetUniformLocation(self.webcam_shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

    view = glm.mat4(1.0)
    view = glm.translate(view, glm.vec3(0.0, 0.0, -3.0))
    glUniformMatrix4fv(glGetUniformLocation(self.webcam_shader, "view"), 1, GL_FALSE, glm.value_ptr(view))

    model = glm.mat4(1.0)
    # model = glm.translate(model, glm.vec3(0.0, 0.0, -3.0))
    # model = glm.rotate(model, float(glfw.get_time()) * glm.radians(30.0), glm.vec3(1.0, 1.0, 0.0))
    # model = glm.scale(model, glm.vec3(0.05))
    glUniformMatrix4fv(glGetUniformLocation(self.webcam_shader, "model"), 1, GL_FALSE, glm.value_ptr(model))

    glBindVertexArray(self.webcam_vao)
    glDrawArrays(GL_QUADS, 0, len(webcam_verts)//5)

  def handle_keys(self, window, key, scancode, action, mods):
    # Rotate cube according to keys pressed
    if key == glfw.KEY_RIGHT:
        self.rotate_y -= 5
    if key == glfw.KEY_LEFT:
        self.rotate_y += 5
    if key == glfw.KEY_UP:
        self.rotate_x -= 5
    if key == glfw.KEY_DOWN:
        self.rotate_x += 5

  def draw(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    image = self.webcam.get_current_frame()

    self.draw_webcam(image)

    translation_vec, euler_angle, obj_data, rotation_vec = self.solver.reproject(image)

    if translation_vec is not None:
      # calculate view matrix
      rmtx = cv2.Rodrigues(rotation_vec)[0]

      view_matrix = np.array([[-rmtx[0][0], -rmtx[0][1], -rmtx[0][2], -translation_vec[0]],
                              [-rmtx[1][0], -rmtx[1][1], -rmtx[1][2], -translation_vec[1]],
                              [-rmtx[2][0], -rmtx[2][1], -rmtx[2][2], -translation_vec[2]],
                              [0.0, 0.0, 0.0, 1.0]])

      view_matrix *= self.INVERSE_MATRIX
      transp_view_matrix = np.transpose(view_matrix)

      glPushMatrix()
      glLoadMatrixf(transp_view_matrix)

      glScalef(self.scale, self.scale, self.scale)

      # rotate with arrow keys
      glRotatef(self.rotate_x, 1.0, 0.0, 0.0)
      glRotatef(self.rotate_y, 0.0, 1.0, 0.0)

      # debug cube
      # glColor3d(1, 0, 1)

      # move to bridge of nose
      # glTranslatef(0.0, 1.0, 1.5)

      glTranslatef(0.0, 0.2 , 0.0)

      # render obj
      glCallList(obj_data.gl_list)

      # reset draw color for further rendering
      glColor3d(1,1,1)
      glPopMatrix()
    else:
      print('face not found')

    glfw.swap_buffers(self.window)
    glfw.poll_events()

  def test_draw(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    image = self.webcam.get_current_frame()

    self.draw_webcam(image)

    # glUseProgram(self.model_shader)

    # projection = glm.perspective(glm.radians(45.0), SIZE[1] / SIZE[0], 0.1, 1000.0)
    # glUniformMatrix4fv(glGetUniformLocation(self.model_shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

    # view = glm.mat4(1.0)
    # view = glm.translate(view, glm.vec3(0.0, 0.0, -3.0))
    # glUniformMatrix4fv(glGetUniformLocation(self.model_shader, "view"), 1, GL_FALSE, glm.value_ptr(view))

    # model = glm.mat4(1.0)
    # model = glm.translate(model, glm.vec3(0.0, 0.0, -3.0))
    # # model = glm.rotate(model, float(glfw.get_time()) * glm.radians(30.0), glm.vec3(1.0, 1.0, 0.0))
    # # model = glm.scale(model, glm.vec3(0.05))
    # glUniformMatrix4fv(glGetUniformLocation(self.model_shader, "model"), 1, GL_FALSE, glm.value_ptr(model))

    # for i in range(len(lightPositions)):
    #   glUniform3fv(glGetUniformLocation(self.model_shader, "lightPositions[" + str(i) + "]"), 1, glm.value_ptr(lightPositions[i]))
    #   glUniform3fv(glGetUniformLocation(self.model_shader, "lightColors[" + str(i) + "]"), 1, glm.value_ptr(lightColors[i]))


    # glBindVertexArray(self.vao)
    # glDrawArrays(GL_TRIANGLES, 0, len(self.VERTICES)//8)

    glfw.swap_buffers(self.window)
    glfw.poll_events()

  def main(self):
    self.setupWindow()
    self.setup_gl()
    self.setup_gl_objects()
    # self.set_textures()

    glfw.set_key_callback(self.window, self.handle_keys)

    while not glfw.window_should_close(self.window):
      self.test_draw()

    print('its terminating normally for some reason')
    glfw.terminate()
    sys.exit()

def main():
  prog = Glasses()
  prog.main()

if __name__ == '__main__':
  main()