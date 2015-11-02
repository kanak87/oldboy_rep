import os
import pickle
import sys

import imagehash
from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVC

fileDir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(fileDir, ".."))

import openface
from openface.alignment import NaiveDlib

from PIL import Image
import numpy as np

modelDir = os.path.join(fileDir, "..", 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')
sys.path.append(openfaceModelDir)


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
    def __init__(self, detectStreamService):
        self.align = NaiveDlib(os.path.join(dlibModelDir, "mean.csv"),
                               os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
        self.net = openface.TorchWrap(os.path.join(openfaceModelDir, 'nn4.v1.t7'),
                                      imgDim=96, cuda=False)

        if os.path.exists("trained_images.pickle"):
            self.trained_images = pickle.load(open('trained_images.pickle', 'rb'))
        else:
            self.trained_images = {}

        if os.path.exists("people.pickle"):
            self.people = pickle.load(open('people.pickle', 'rb'))
        else:
            self.people = []

        if os.path.exists("svm.pickle"):
            self.svm = pickle.load(open('svm.pickle', 'rb'))
        else:
            param_grid = [
                {'C': [1, 10, 100, 1000],
                 'kernel': ['linear']},
                {'C': [1, 10, 100, 1000],
                 'gamma': [0.001, 0.0001],
                 'kernel': ['rbf']}
            ]
            self.svm = GridSearchCV(SVC(C=1, probability=True), param_grid, cv=5)

    def training(self, name, images):
        X = []
        y = []

        try:
            identity = self.people.index(name)
        except Exception as e:
            identity = len(self.people)

        for img in self.trained_images.values():
            X.append(img.rep)
            y.append(img.identity)

        for image in images:
            bbs = self.align.getAllFaceBoundingBoxes(image)

            if len(bbs) is not 1:
                continue
                #raise Exception('0 or many people in image')

            bb = bbs[0]
            alignedFace = self.align.alignImg("affine", 96, image, bb)
            if alignedFace is None:
                continue
                #raise Exception('not exist face in image')

            phash = str(imagehash.phash(Image.fromarray(alignedFace)))
            if phash in self.trained_images:
                rep = self.trained_images[phash].rep
            else:
                rep = self.net.forwardImage(alignedFace)
                self.trained_images[phash] = Face(rep, identity)

                X.append(rep)
                y.append(identity)

        self.people.append(name)

        param_grid = [
            {'C': [1, 10, 100, 1000],
             'kernel': ['linear']},
            {'C': [1, 10, 100, 1000],
             'gamma': [0.001, 0.0001],
             'kernel': ['rbf']}
        ]

        if len(self.people) > 1:
            self.svm = GridSearchCV(SVC(C=1, probability=True), param_grid, cv=5).fit(X, y)

            pickle.dump(self.svm, open('svm.pickle', 'wb'), -1)
            pickle.dump(self.trained_images, open('trained_images.pickle', 'wb'), -1)
            pickle.dump(self.people, open('people.pickle', 'wb'), -1)

        return identity

    def predict(self, image):
        if len(self.trained_images) < 2:
            return None

        results = []
        bbs = self.align.getAllFaceBoundingBoxes(image)

        for bb in bbs:
            # print(len(bbs))
            alignedFace = self.align.alignImg("affine", 96, image, bb)
            if alignedFace is None:
                continue

            phash = str(imagehash.phash(Image.fromarray(alignedFace)))
            identity = None
            if phash in self.trained_images:
                identity = self.trained_images[phash].identity
                results.append((self.faces[identity], bb, 1))
            else:
                rep = self.net.forwardImage(alignedFace)
                if self.svm:
                    #self.svm.predict(rep)
                    result_proba_list = self.svm.predict_proba(rep)
                    max_index = np.argmax(result_proba_list[0])
                    #threshold = 0.8
                    threshold = 0.6
                    if result_proba_list[0][max_index] > threshold:
                        results.append((self.faces[identity], bb, result_proba_list[max_index]))

        return results