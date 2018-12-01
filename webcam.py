import cv2
from threading import Thread

class Webcam:
  def __init__(self, width=640, height=480):
    self.feed = cv2.VideoCapture(0)
    self.video_capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)
    self.video_capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height)
    self.current_frame = self.feed.read()[1]

  def start(self):
    Thread(target=self.update_frame, args=()).start()

  def update_frame(self):
    while(True):
      self.current_frame = self.feed.read()[1]

  def get_current_frame(self):
    return self.current_frame