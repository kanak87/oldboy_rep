import os
import sys

fileDir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(fileDir, ".."))

import base64
import json
import StringIO
from flask import Flask, request
import argparse
import cv2
import imagehash
import json
from PIL import Image
import numpy as np
import os
import StringIO
import urllib
import base64

from sklearn.decomposition import PCA
from sklearn.grid_search import GridSearchCV
from sklearn.manifold import TSNE
from sklearn.svm import SVC

import matplotlib.pyplot as plt
import matplotlib.cm as cm

modelDir = os.path.join(fileDir, "..", 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')
sys.path.append(openfaceModelDir)

os.path.expanduser("~/src/dlib-18.16/python_examples")

import dlib
import openface
from openface.alignment import NaiveDlib

app = Flask(__name__)



class Face:

    def __init__(self, rep, identity):
        self.rep = rep
        self.identity = identity

    def __repr__(self):
        return "{{id: {}, rep[0:5]: {}}}".format(
            str(self.identity),
            self.rep[0:5]
        )


class FaceService(object):
    def __init__(self):
        self.align = NaiveDlib(os.path.join(dlibModelDir, "mean.csv"),
                               os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
        self.net = openface.TorchWrap(os.path.join(openfaceModelDir, 'nn4.v1.t7'),
                                      imgDim=96, cuda=False)
        self.images = { }
        self.people = []
        self.svm = None

    def get_face_id(self, string_img, width, height):
        head = "data:image/jpeg;base64,"
        assert (string_img.startswith(head))

        imgdata = base64.b64decode(string_img[len(head):])
        imgF = StringIO.StringIO()
        imgF.write(imgdata)
        imgF.seek(0)
        img = Image.open(imgF)

        buf = np.fliplr(np.asarray(img))
        rgbFrame = np.zeros((height, width, 3), dtype=np.uint8)
        rgbFrame[:, :, 0] = buf[:, :, 2]
        rgbFrame[:, :, 1] = buf[:, :, 1]
        rgbFrame[:, :, 2] = buf[:, :, 0]

        identities = []
        bbs = self.align.getAllFaceBoundingBoxes(rgbFrame)


faceService = FaceService()


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/request_face_dectection", methods=['POST'])
def request_face_detection():
    try:
        if request.form['data']:
            print request.form['data']

        data = json.loads(request.form['data'])
        print data
.''
        face_id = faceSe=-wertyzxcvbnm,