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

  # def print_text(self, x, y, font, text, r, g , b):
  #   # set text color
  #   glColor3d(r,g,b)
  #   glWindowPos2f(x,y)

  #   for ch in text :
  #     glutBitmapCharacter(font, ctypes.c_int(ord(ch)))

  #   # reset draw color for further rendering
  #   glColor3d(1,1,1)

  def setupWindow(self):
    # glutInit()
    # glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    # glutInitWindowSize(SIZE[1], SIZE[0])
    # glutInitWindowPosition(100, 100)
    # glutCreateWindow(APP_NAME)

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

  def special(self, key, x, y):
    # Rotate cube according to keys pressed
    if key == GLUT_KEY_RIGHT:
        self.rotate_y += 5
    if key == GLUT_KEY_LEFT:
        self.rotate_y -= 5
    if key == GLUT_KEY_UP:
        self.rotate_x += 5
    if key == GLUT_KEY_DOWN:
        self.rotate_x -= 5
    glutPostRedisplay()

  def draw(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    image = self.webcam.get_current_frame()

    self.draw_webcam(image)

    translation_vec, euler_angle, obj_data, rotation_vec = self.solver.reproject(image)

    if translation_vec is not None:
      # self.print_text(30, 40, GLUT_BITMAP_HELVETICA_18, "X: " + "{:7.2f}".format(euler_angle[0, 0]), 0.0, 0.0, 0.0)
      # self.print_text(30, 70, GLUT_BITMAP_HELVETICA_18, "Y: " + "{:7.2f}".format(euler_angle[1, 0]), 0.0, 0.0, 0.0)
      # self.print_text(30, 100, GLUT_BITMAP_HELVETICA_18, "Z: " + "{:7.2f}".format(euler_angle[2, 0]), 0.0, 0.0, 0.0)

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

    # glutSwapBuffers()
    glfw.swap_buffers(self.window)
    glfw.poll_events()


  def main(self):
    self.setupWindow()
    # glutDisplayFunc(self.draw)
    # glutIdleFunc(self.draw)
    # The callback function for keyboard controls
    # glutSpecialFunc(self.special)
    self.setup_gl()

    while not glfw.window_should_close(self.window):
      self.draw()
    # glutMainLoop()

    glfw.terminate()

def main():
  prog = Glasses()
  prog.main()

if __name__ == '__main__':
  main()