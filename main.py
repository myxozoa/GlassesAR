from imutils import face_utils
import dlib
import cv2
import numpy as np
from webcam import Webcam
from solver import Solver
from loaders import loadobj
from constants import *
import sys

class Glasses:
  def __init__(self):
    self.webcam = Webcam()
    self.solver = Solver()

  def text(self, cv, image, txt, pos):
    cv.putText(image, txt, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), thickness=2)

  def main(self):
    self.webcam.start()

    # main loop
    while True:
      # grabbing images from the webcam and converting it into grayscale
        image = self.webcam.get_current_frame()

        reprojectdst, euler_angle, shape = self.solver.reproject(image)

        if reprojectdst is not None and euler_angle is not None:
          # draw face landmark points
          for (x, y) in shape:
            cv2.circle(image, (x, y), 2, (255, 0, 0), -1)

          # draw edges of object one line at a time
          for start, end in self.solver.line_pairs:
            cv2.line(image, reprojectdst[start], reprojectdst[end], (0, 255, 0))

          # print debug info about the euler angle to the opencv window
          self.text(cv2, image, "X: " + "{:7.2f}".format(euler_angle[0, 0]), (20, 20))
          self.text(cv2, image, "Y: " + "{:7.2f}".format(euler_angle[1, 0]), (20, 50))
          self.text(cv2, image, "Z: " + "{:7.2f}".format(euler_angle[2, 0]), (20, 80))

        # output image to opencv window
        cv2.imshow(APP_NAME, image)

        # write frame to output file
        self.webcam.write_output(image)

        # close app with esc key
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break

        # close app if window is closed with the x button
        if cv2.getWindowProperty(APP_NAME, 0) < 0:
          break

    # breaking out of the loop constitutes quitting, cleanup
    cv2.destroyAllWindows()
    self.webcam.release()
    sys.exit()

def main():
  prog = Glasses()
  prog.main()

if __name__ == '__main__':
  main()