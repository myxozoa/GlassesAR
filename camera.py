from scipy import linalg

class Camera(object):
  # using the pin-hole camera model

  def __init__(self, P):
    # P = K[R|T]
    self.P = P
    self.K = None # Camera Calibration Matrix
    self.R = None # Rotation Matrix
    self.T = None # Translation Matrix
    self.C = None # Camera Center

  def project(self, X):
    # Project points in X ($*n array) and normalize coords

    x = dot(self.P, X)
    for i in range(3):
      x[i] /= x[2]

    return x
