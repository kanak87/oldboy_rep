import os
import sys
from time import sleep
import cv2

fileDir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(fileDir, "..", "./project"))

import openface
from openface.alignment import NaiveDlib

from PIL import Image
import numpy as np

params = list()
params.append(cv2.IMWRITE_PNG_COMPRESSION)
params.append(9)

modelDir = os.path.join(fileDir, "../project", 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')
sys.path.append(openfaceModelDir)

align = NaiveDlib(os.path.join(dlibModelDir, "mean.csv"),
                  os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))

video_capture = cv2.VideoCapture(0)

ret, frame = video_capture.read()
sleep(1)
ret, frame = video_capture.read()

image = frame

cv2.imwrite('img.png', frame, params)
bbs = align.getAllFaceBoundingBoxes(image)

print len(bbs)

bb = bbs[0]
alignedFace = align.alignImg("affine", 96, image, bb)
cv2.imwrite('img2.png', alignedFace, params)