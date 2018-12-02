from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from imutils import face_utils
import dlib
import cv2
import numpy as np
from webcam import Webcam
from solver import Solver
from loaders import loadobj
from PIL import Image
from constants import *
import sys

class Glasses:
  def __init__(self):
    self.webcam = Webcam()
    self.solver = Solver()
    self.webcam_background = None

  def text(self, cv, image, txt, pos):
    cv.putText(image, txt, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), thickness=2)

  def setupWindow(self):
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 480)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(APP_NAME)

  def setup_gl(self):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(33.7, 1.3, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    # start webcam thread
    self.webcam.start()

    # assign texture
    glEnable(GL_TEXTURE_2D)
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

    # draw bg
    glBindTexture(GL_TEXTURE_2D, self.webcam_background)
    glPushMatrix()
    glTranslatef(0.0,0.0,-10.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0); glVertex3f(-4.0, -3.0, 0.0)
    glTexCoord2f(1.0, 1.0); glVertex3f( 4.0, -3.0, 0.0)
    glTexCoord2f(1.0, 0.0); glVertex3f( 4.0,  3.0, 0.0)
    glTexCoord2f(0.0, 0.0); glVertex3f(-4.0,  3.0, 0.0)
    glEnd( )
    glPopMatrix()

  def draw(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    image = self.webcam.get_current_frame()

    self.draw_webcam(image)

    glutSwapBuffers()


  def main(self):
    self.setupWindow()
    glutDisplayFunc(self.draw)
    glutIdleFunc(self.draw)
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
        #   self.text(cv2, image, "X: " + "{:7.2f}".format(euler_angle[0, 0]), (20, 20))
        #   self.text(cv2, image, "Y: " + "{:7.2f}".format(euler_angle[1, 0]), (20, 50))
        #   self.text(cv2, image, "Z: " + "{:7.2f}".format(euler_angle[2, 0]), (20, 80))

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