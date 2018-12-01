from imutils import face_utils
import dlib
import cv2
import numpy as np
import camera

obj = open("teddy.obj", "r")
vertex_array = []
triangle_sections = []


for line in obj:
  line_split = line.split(" ")

  if line_split[0] == "v":
    vertex_array.append([ float(x) for x in line_split[1:] ])

  if line_split[0] == "f":
    # fix since obj files seem to have 1-indexed verticies
    temp = [ max(int(x) - 1, 0) for x in line_split[1:] ]

    triangle_sections.append(temp[0:2])
    triangle_sections.append(temp[1:3])

vertex_array.append([0, 0, 0])

# hardcoded webcam image size for now
size = (480, 640)

focal_length = size[1]
center = (size[1]/2, size[0]/2)
K = np.array(
                         [[focal_length, 0, center[0]],
                         [0, focal_length, center[1]],
                         [0, 0, 1]], dtype = "double"
                         )

# this is assuming zero lens distortion, unrealistic but good enough for now
D = np.zeros((5, 1))

cam_matrix = np.array(K).reshape(3, 3).astype(np.float32)
dist_coeffs = np.array(D).reshape(5, 1).astype(np.float32)

object_pts = np.float32([[6.825897, 6.760612, 4.402142],
                         [1.330353, 7.122144, 6.903745],
                         [-1.330353, 7.122144, 6.903745],
                         [-6.825897, 6.760612, 4.402142],
                         [5.311432, 5.485328, 3.987654],
                         [1.789930, 5.393625, 4.413414],
                         [-1.789930, 5.393625, 4.413414],
                         [-5.311432, 5.485328, 3.987654],
                         [2.005628, 1.409845, 6.165652],
                         [-2.005628, 1.409845, 6.165652],
                         [2.774015, -2.080775, 5.048531],
                         [-2.774015, -2.080775, 5.048531],
                         [0.000000, -3.116408, 6.097667],
                         [0.000000, -7.415691, 4.070434]])

# reprojectsrc = np.float32([[10.0, 10.0, 10.0],
#                            [10.0, 10.0, -10.0],
#                            [10.0, -10.0, -10.0],
#                            [10.0, -10.0, 10.0],
#                            [-10.0, 10.0, 10.0],
#                            [-10.0, 10.0, -10.0],
#                            [-10.0, -10.0, -10.0],
#                            [-10.0, -10.0, 10.0]
#                            ])

# line_pairs = [[0, 1], [1, 2], [2, 3], [3, 0],
#               [4, 5], [5, 6], [6, 7], [7, 4],
#               [0, 4], [1, 5], [2, 6], [3, 7]
#               ]

# reprojectsrc = np.float32([[0.0, 10.0, 10.0],
#               [0.0, 10.0, -10.0]])

# line_pairs = [[0, 1]]

reprojectsrc = np.float32(vertex_array)

line_pairs = triangle_sections

# print(line_pairs)
def head_pose(shape):
  image_pts = np.float32([shape[17], shape[21], shape[22], shape[26], shape[36],
                          shape[39], shape[42], shape[45], shape[31], shape[35],
                          shape[48], shape[54], shape[57], shape[8]])

  _, rotation_vec, translation_vec = cv2.solvePnP(object_pts, image_pts, cam_matrix, dist_coeffs)

  reprojectdst, _ = cv2.projectPoints(reprojectsrc, rotation_vec, translation_vec, cam_matrix,
                                      dist_coeffs)

  reprojectdst = tuple(map(tuple, reprojectdst.reshape(-1, 2)))

  # calc euler angle
  rotation_mat, _ = cv2.Rodrigues(rotation_vec)
  pose_mat = cv2.hconcat((rotation_mat, translation_vec))
  _, _, _, _, _, _, euler_angle = cv2.decomposeProjectionMatrix(pose_mat)

  return reprojectdst, euler_angle

def text(cv, image, txt, pos):
  cv.putText(image, txt, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), thickness=2)

def main():
  detector = dlib.get_frontal_face_detector()

  predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

  cap = cv2.VideoCapture(0)

  cap.set(3, size[1])
  cap.set(4, size[0])

  fourcc = cv2.VideoWriter_fourcc(*'XVID')
  out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
  while True:
    # grabbing images from the webcam and converting it into grayscale
      _, image = cap.read()
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

        reprojectdst, euler_angle = head_pose(shape)


        # print(len(reprojectdst))

        # for (x, y) in shape:
        #   cv2.circle(image, (x, y), 2, (255, 0, 0), -1)

        for start, end in line_pairs:
          # print(start, end)
          cv2.line(image, reprojectdst[start], reprojectdst[end], (0, 255, 0))

        # text(cv2, image, "X: " + "{:7.2f}".format(euler_angle[0, 0]), (20, 20))
        # text(cv2, image, "Y: " + "{:7.2f}".format(euler_angle[1, 0]), (20, 50))
        # text(cv2, image, "Z: " + "{:7.2f}".format(euler_angle[2, 0]), (20, 80))

      out.write(image)
      cv2.imshow("Output", image)

      # close app with esc key
      k = cv2.waitKey(5) & 0xFF
      if k == 27:
          break

  cv2.destroyAllWindows()
  cap.release()

if __name__ == '__main__':
  main()