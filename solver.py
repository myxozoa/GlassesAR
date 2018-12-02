from imutils import face_utils
import dlib
import cv2
import numpy as np
from webcam import Webcam
from loaders import loadobj
from constants import *

class Solver:
  def __init__(self):
    self.K = np.array(DEFAULT_K, dtype = "double")

    # this is assuming zero lens distortion, unrealistic but good enough for now
    self.D = np.zeros((5, 1))

    self.cam_matrix = np.array(self.K).reshape(3, 3).astype(np.float32)
    self.dist_coeffs = np.array(self.D).reshape(5, 1).astype(np.float32)

    # head points estimation
    self.object_pts = np.float32(HEAD_PTS)

    self.obj_data = loadobj(MODEL)

    self.reprojectsrc = np.float32(self.obj_data[0])

    self.line_pairs = self.obj_data[1]

    self.detector = dlib.get_frontal_face_detector()

    self.predictor = dlib.shape_predictor(SHAPE_PREDICTOR)

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

  # def calculate_optical_flow(self, prev_frame, gray, prev_reprojection):
  #   current_flow, status, _ = cv2.calcOpticalFlowPyrLK(prev_frame, gray, prev_reprojection, np.array([]))
  #   prev_reprojection, current_flow = map(lambda flows: flows[status.ravel().astype(bool)], [prev_reprojection, current_flow])
  #   transform = cv2.estimateRigidTransform(prev_reprojection, current_flow, True)

  #   if transform is not None:
  #     transform = np.append(transform, [[0, 0, 1]], axis=0)

  #   return transform

  def reproject(self, image):
    height, width, channels = image.shape

    # converting image to grayscale as required by algs
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # blank image for debug
    blank_image = np.zeros((height,width,3), np.uint8)
    blank_image[:,0:width] = (255,255,255)

    # face detection
    rect = self.detector(gray, 0)

    # if face detected
    if (len(rect) > 0):
      shape_pred = self.predictor(gray, rect[0])

      # convert face landmarks to 2-tuple of (x, y) coords
      shape = face_utils.shape_to_np(shape_pred)

      reprojectdst, euler_angle = self.head_pose(shape)
      return reprojectdst, euler_angle, shape

    return None, None, None