from imutils import face_utils
import dlib
import cv2
import numpy as numpy

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
prevBox = (float('-inf'), float('+inf'))
while True:
  # grabbing images from the webcam and converting it into grayscale
    _, image = cap.read()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # show the gray image
    face = face_cascade.detectMultiScale(gray, 1.3, 6)

    if(len(face) > 0):
      x = face[0][0]
      y = face[0][1]
      w = face[0][2]
      h = face[0][3]

      cv2.rectangle(image, (x,y), (x+w, y+h), (255,0,0),2)
      roi_gray = gray[y:y+h, x:x+w]
      roi_color = image[y:y+h, x:x+w]

    cv2.imshow("Output", image)

    # close app with esc key
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
    prevBox = (w, h)

cv2.destroyAllWindows()
cap.release()