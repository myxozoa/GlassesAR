from imutils import face_utils
import dlib
import cv2
import numpy as np
from webcam import Webcam
from loaders import loadobj
from constants import *
import sys

class Glasses:
  def __init__(self):
    self.K = np.array(DEFAULT_K, dtype = "double")

    # this is assuming zero lens distortion, unrealistic but good enough for now
    self.D = np.zeros((5, 1))

    self.cam_matrix = np.array(self.K).reshape(3, 3).astype(np.float32)
    self.dist_coeffs = np.array(self.D).reshape(5, 1).astype(np.float32)

    # head points estimation
    self.object_pts = np.float32(HEAD_PTS)

    self.obj_data = loadobj("teddy.obj")

    self.reprojectsrc = np.float32(self.obj_data[0])

    self.line_pairs = self.obj_data[1]

    self.webcam = Webcam()

  def head_pose(self, shape):
    image_pts = np.float32([shape[17], shape[21], shape[22], shape[26], shape[36],
                            shape[39], shape[42], shape[45], shape[31], shape[35],
                            shape[48], shape[54], shape[57], shape[8]])

    _, rotation_vec, translation_vec = cv2.solvePnP(self.object_pts, image_pts, self.cam_matrix, self.dist_coeffs)

    reprojectdst, _ = cv2.projectPoints(self.reprojectsrc, rotation_vec, translation_vec, self.cam_matrix,
                                        self.dist_coeffs)

    reprojectdst = tuple(map(tuple, reprojectdst.reshape(-1, 2)))

    # calc euler angle
    rotation_mat, _ = cv2.Rodrigues(rotation_vec)
    pose_mat = cv2.hconcat((rotation_mat, translation_vec))
    _, _, _, _, _, _, euler_angle = cv2.decomposeProjectionMatrix(pose_mat)

    return reprojectdst, euler_angle

  def text(self, cv, image, txt, pos):
    cv.putText(image, txt, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), thickness=2)

  def main(self):
    self.webcam.start()
    detector = dlib.get_frontal_face_detector()

    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

    while True:
      # grabbing images from the webcam and converting it into grayscale
        image = self.webcam.get_current_frame()
        height, width, channels = image.shape

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blank_image = np.zeros((height,width,3), np.uint8)

        blank_image[:,0:width] = (255,255,255)

        # show the gray image

        rect = detector(gray, 0)

        if (len(rect) > 0):
          shape_pred = predictor(gray, rect[0])

          # convert face landmarks to 2-tuple of (x, y) coords
          shape = face_utils.shape_to_np(shape_pred)

          reprojectdst, euler_angle = self.head_pose(shape)


          # print(len(reprojectdst))

          # for (x, y) in shape:
          #   cv2.circle(image, (x, y), 2, (255, 0, 0), -1)

          for start, end in self.line_pairs:
            # print(start, end)
            cv2.line(image, reprojectdst[start], reprojectdst[end], (0, 255, 0))

          # self.text(cv2, image, "X: " + "{:7.2f}".format(euler_angle[0, 0]), (20, 20))
          # self.text(cv2, image, "Y: " + "{:7.2f}".format(euler_angle[1, 0]), (20, 50))
          # self.text(cv2, image, "Z: " + "{:7.2f}".format(euler_angle[2, 0]), (20, 80))


        cv2.imshow("Output", image)

        # close app with esc key
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break

    cv2.destroyAllWindows()
    self.webcam.release()
    sys.exit()

def main():
  prog = Glasses()
  prog.main()

if __name__ == '__main__':
  main()