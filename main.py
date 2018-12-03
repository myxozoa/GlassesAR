from OpenGL.GL import *
from OpenGL.GLUT import *
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
    self.webcam = Webcam()
    self.solver = None
    self.webcam_background = None
    self.rotate_y = 0.0
    self.rotate_x = 0.0
    self.scale = 1.0
    self.prev_position = None

  def print_text(self, x, y, font, text, r, g , b):
    # set text color
    glColor3d(r,g,b)
    glWindowPos2f(x,y)

    for ch in text :
      glutBitmapCharacter(font, ctypes.c_int(ord(ch)))

    # reset draw color for further rendering
    glColor3d(1,1,1)

  def setupWindow(self):
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(SIZE[1], SIZE[0])
    glutInitWindowPosition(100, 100)
    glutCreateWindow(APP_NAME)

  def setup_gl(self):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(33.7, 1.3, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    # start webcam thread
    self.webcam.start()

    # initializing solver after opengl context is created
    self.solver = Solver()

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
    glTranslatef(0.0, 0.0, -10.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-4.0, -3.0, 0.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( 4.0, -3.0, 0.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( 4.0, 3.0, 0.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-4.0, 3.0, 0.0)
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

  def scale_range(self, input, min, max):
    input += 0 #min
    input /= 10 / (max - min) #10 is max
    input += min
    return input

  def draw(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    image = self.webcam.get_current_frame()

    self.draw_webcam(image)

    translation_vec, euler_angle, shape, obj_data = self.solver.reproject(image)

    if euler_angle is not None:
      # print(shape[34])
      self.print_text(30, 40, GLUT_BITMAP_HELVETICA_18, "X: " + "{:7.2f}".format(euler_angle[0, 0]), 0.0, 0.0, 0.0)
      self.print_text(30, 70, GLUT_BITMAP_HELVETICA_18, "Y: " + "{:7.2f}".format(euler_angle[1, 0]), 0.0, 0.0, 0.0)
      self.print_text(30, 100, GLUT_BITMAP_HELVETICA_18, "Z: " + "{:7.2f}".format(euler_angle[2, 0]), 0.0, 0.0, 0.0)

      glLoadIdentity()

      # left -2.0, right 2.0
      # down -1.5, up 1.5
      glScalef(self.scale, self.scale, self.scale)

      # translation hack, figure out more scalable solution
      new_x = self.scale_range(-translation_vec[0], -2, 2)[0]
      new_y = self.scale_range(-translation_vec[1], -1.5, 1.5)[0]
      # print((new_x, new_y))
      glTranslatef(new_x * 0.2, (-new_y - 4) * 0.2, -5.0)

      glTranslatef(0.05, 0.5, -1.0)

      # glTranslatef(0.0, 0.0, -5.0)

      # rotate with arrow keys
      # glRotatef(self.rotate_x, 1.0, 0.0, 0.0)
      # glRotatef(self.rotate_y, 0.0, 1.0, 0.0)

      glRotatef(euler_angle[0, 0], 1.0, 0.0, 0.0) # x rotate
      glRotatef(-euler_angle[1, 0], 0.0, 1.0, 0.0) # y rotate
      glRotatef(-euler_angle[2, 0], 0.0, 0.0, 1.0) # z rotate
      
      # debug cube
      glColor3d(1, 0, 1)
      glutSolidCube(1.0)

      # glCallList(obj_data.gl_list)

      # reset draw color for further rendering
      glColor3d(1,1,1)

      # self.prev_position = shape[34]

    glutSwapBuffers()

  def main(self):
    self.setupWindow()
    glutDisplayFunc(self.draw)
    glutIdleFunc(self.draw)
    # The callback function for keyboard controls
    glutSpecialFunc(self.special)
    self.setup_gl()
    glutMainLoop()
    
    # # main loop
    # while True:
      # # grabbing images from the webcam and converting it into grayscale
        # image = self.webcam.get_current_frame()

        # reprojectdst, euler_angle, shape = self.solver.reproject(image)

        # if reprojectdst is not None and euler_angle is not None:
        #   # draw face landmark points
        #   for (x, y) in shape:
        #     cv2.circle(image, (x, y), 2, (255, 0, 0), -1)

        #   # draw edges of object one line at a time
        #   for start, end in self.solver.line_pairs:
        #     cv2.line(image, reprojectdst[start], reprojectdst[end], (0, 255, 0))

        #   # print debug info about the euler angle to the opencv window
          # self.text(cv2, image, "X: " + "{:7.2f}".format(euler_angle[0, 0]), (20, 20))
          # self.text(cv2, image, "Y: " + "{:7.2f}".format(euler_angle[1, 0]), (20, 50))
          # self.text(cv2, image, "Z: " + "{:7.2f}".format(euler_angle[2, 0]), (20, 80))

        # # output image to opencv window
        # cv2.imshow(APP_NAME, image)

        # # write frame to output file
        # self.webcam.write_output(image)

        # # close app with esc key
        # k = cv2.waitKey(5) & 0xFF
        # if k == 27:
        #     break

        # # close app if window is closed with the x button
        # if cv2.getWindowProperty(APP_NAME, 0) < 0:
        #   break

    # # breaking out of the loop constitutes quitting, cleanup
    # cv2.destroyAllWindows()
    # self.webcam.release()
    # sys.exit()

def main():
  prog = Glasses()
  prog.main()

if __name__ == '__main__':
  main()