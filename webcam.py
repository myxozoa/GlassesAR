import cv2
import numpy as np
from threading import Thread
from constants import *

class Webcam:
  def __init__(self, width=640, height=480):
    self.feed = cv2.VideoCapture(0)
    self.feed.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    self.feed.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    self.current_frame = self.feed.read()[1]

    with np.load(WEBCAM_CALIB) as calib:
      self.camera_matrix, self.dist_coeffs = [calib[i] for i in ('mtx','dist')]

  def start(self):
    t = Thread(target=self.update_frame, args=())
    t.setDaemon(True)
    t.start()

  def update_frame(self):
    while(True):
      self.current_frame = self.feed.read()[1]

  def get_current_frame(self):
    return self.current_frame

  def release(self):
    self.feed.release()