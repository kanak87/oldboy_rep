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
    def __init__(self):
        self.align = NaiveDlib(os.path.join(dlibModelDir, "mean.csv"),
                               os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
        self.net = openface.TorchWrap(os.path.join(openfaceModelDir, 'nn4.v1.t7'),
                                      imgDim=96, cuda=False)

        if os.path.exists("trained_images.pickle"):
            self.trained_images = pickle.load(open('trained_images.pickle', 'rb'))
        else:
            self.trained_images = {}

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

    def training(self, identity, images):
        X = []
        y = []

        training_result = []

        for img in self.trained_images.values():
            X.append(img.rep)
            y.append(img.identity)

        for image in images:
            bbs = self.align.getAllFaceBoundingBoxes(image)

            if len(bbs) is not 1:
                training_result.append('0 or many people in image')
                continue
                # raise Exception('0 or many people in image')

            bb = bbs[0]
            alignedFace = self.align.alignImg("affine", 96, image, bb)
            if alignedFace is None:
                training_result.append('not exist face in image')
                continue

            phash = str(imagehash.phash(Image.fromarray(alignedFace)))
            if phash in self.trained_images:
                rep = self.trained_images[phash].rep
                training_result.append('already trained')
            else:
                rep = self.net.forwardImage(alignedFace)
                self.trained_images[phash] = Face(rep, identity)

                X.append(rep)
                y.append(identity)

                training_result.append(0)

        if identity > 0:
            param_grid = [
                {'C': [1, 10, 100, 1000],
                 'kernel': ['linear']},
                {'C': [1, 10, 100, 1000],
                 'gamma': [0.001, 0.0001],
                 'kernel': ['rbf']}
            ]
            self.svm = GridSearchCV(SVC(C=1, probability=True), param_grid, cv=5).fit(X, y)

        return training_result

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
            if phash in self.trained_images:
                identity = self.trained_images[phash].identity
                results.append(identity, bb, 1)
            else:
                rep = self.net.forwardImage(alignedFace)
                if self.svm is not None:
                    # self.svm.predict(rep)
                    result_proba_list = self.svm.predict_proba(rep)
                    identity = np.argmax(result_proba_list[0])
                    # threshold = 0.8
                    threshold = 0.3
                    if result_proba_list[0][identity] > threshold:
                        results.append((identity, bb, result_proba_list[0][identity]))
                    else:
                        results.append((-1, bb, 0.0))

        return results
