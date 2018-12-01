from scipy import linalg
import numpy as np

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

  def rotation_matrix(self, a):
    # 3d rotation matrix around axis vector and
    R = np.eye(4)
    R[:3, :3] = linalg.expm([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return R

  def factor(self):
    # factorize camera matrix into K, R, T, as P = K[R|T]

    K, R = linalg.rq(self.P[:, :3])

    T = np.diag(np.sign(np.diag(K)))

    if linalg.det(T) < 0:
      T[1,1] *= -1

    self.K = dot(K, T)
    self.R = dot(T, R)
    self.T = dot(linalg.inv(self.K), self.P[:, 3])

    return self.K, self.R, self.T

  def center(self):
    # compute camera center

    if self.C is not None:
      return self.C

    self.factor()
    self.C = -dot(self.R.T, self.T)
    return self.C
