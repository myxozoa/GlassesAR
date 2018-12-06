from OpenGL.GL import *
# from OpenGL.GLUT import *
import glfw
from OpenGL.GLU import *
import cv2
import numpy as np
from webcam import Webcam
from solver import Solver
from PIL import Image
from constants import *
import sys

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

  def setupWindow(self):
    if not glfw.init():
      return
    
    self.window = glfw.create_window(SIZE[1], SIZE[0], APP_NAME, None, None)
    if not self.window:
      glfw.terminate()
      return

    glfw.make_context_current(self.window)

  def setup_gl(self):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(33.7, 1.3, 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)

    # start webcam thread
    self.webcam.start()

    # initializing solver after opengl context is created
    self.solver = Solver(self.webcam.camera_matrix, self.webcam.dist_coeffs)

    # assign texture
    glEnable(GL_TEXTURE_2D)
    self.webcam_background = glGenTextures(1)

  def draw_webcam(self, image):
    glEnable(GL_TEXTURE_2D)

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

    # draw bg
    glBindTexture(GL_TEXTURE_2D, self.webcam_background)
    glPushMatrix()
    glTranslatef(0.0, 0.0, -100.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-40.0, -30.0, 0.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( 40.0, -30.0, 0.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( 40.0, 30.0, 0.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-40.0, 30.0, 0.0)
    glEnd()
    glPopMatrix()

    glDisable(GL_TEXTURE_2D)

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


  def main(self):
    self.setupWindow()
    self.setup_gl()
    glfw.set_key_callback(self.window, self.handle_keys)
  
    while not glfw.window_should_close(self.window):
      self.draw()

    glfw.terminate()

def main():
  prog = Glasses()
  prog.main()

if __name__ == '__main__':
  main()