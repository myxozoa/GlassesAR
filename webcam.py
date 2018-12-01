import cv2
from threading import Thread

class Webcam:
  def __init__(self, width=640, height=480, output=False):
    self.feed = cv2.VideoCapture(0)
    self.feed.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    self.feed.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    self.current_frame = self.feed.read()[1]

    if output:
      self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
      self.out = cv2.VideoWriter('output.avi', self.fourcc, 20.0, (width,height))

  def start(self):
    t = Thread(target=self.update_frame, args=())
    t.setDaemon(True)
    t.start()

  def update_frame(self):
    while(True):
      self.current_frame = self.feed.read()[1]

  def get_current_frame(self):
    return self.current_frame

  def write_output(image):
    self.out.write(image)

  def release(self):
    self.feed.release();