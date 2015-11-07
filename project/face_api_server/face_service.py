import os
import pickle
import sys

import imagehash
from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVC
from Queue import PriorityQueue

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

        self.identities = []

        if os.path.exists("trained_images.pickle"):
            self.trained_images = pickle.load(open('trained_images.pickle', 'rb'))
            identities_set = set()
            for trained_image in self.trained_images.values():
                identities_set.add(trained_image.identity)

            self.identities = list(identities_set)
            self.identities.sort()
        else:
            self.trained_images = {}

        if os.path.exists("svm.pickle"):
            self.svm = pickle.load(open('svm.pickle', 'rb'))
        else:
            self.svm = None

    def training(self, identity, images):
        X = []
        y = []

        training_result = []
        identities_set = set()

        for img in self.trained_images.values():
            X.append(img.rep)
            y.append(img.identity)
            identities_set.add(img.identity)

        identities_set.add(identity)
        self.identities = list(identities_set)
        self.identities.sort()

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

            # save_array(alignedFace, "train.png")

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

        if len(self.identities) > 1:
            X = np.vstack(X)
            y = np.array(y)

            param_grid = [
                {'C': [1, 10, 100, 1000],
                 'kernel': ['linear']},
                {'C': [1, 10, 100, 1000],
                 'gamma': [0.001, 0.0001],
                 'kernel': ['rbf']}
            ]
            print "*" * 60
            print X
            print y
            self.svm = GridSearchCV(SVC(C=1, probability=True), param_grid, cv=5).fit(X, y)

        return training_result

    def remove_face(self, identity):
        X = []
        y = []

        remove_faces = []
        identities_set = set()

        for key, value in self.trained_images.items():
            if value.identity == identity:
                remove_faces.append(key)
            else:
                X.append(value.rep)
                y.append(value.identity)
                identities_set.add(value.identity)

        self.identities = list(identities_set)
        self.identities.sort()

        for key in remove_faces:
            del self.trained_images[key]

        if len(self.identities) > 1:
            X = np.vstack(X)
            y = np.array(y)

            param_grid = [
                {'C': [1, 10, 100, 1000],
                 'kernel': ['linear']},
                {'C': [1, 10, 100, 1000],
                 'gamma': [0.001, 0.0001],
                 'kernel': ['rbf']}
            ]
            print "*" * 60
            print X
            print y
            self.svm = GridSearchCV(SVC(C=1, probability=True), param_grid, cv=5).fit(X, y)
        else:
            self.svm = None

    def predict(self, image):
        result_priority_queue = PriorityQueue()
        results = []

        bbs = self.align.getAllFaceBoundingBoxes(image)
        print "-" * 60
        for bb_index, bb in enumerate(bbs):
            alignedFace = self.align.alignImg("affine", 96, image, bb)
            if alignedFace is None:
                continue

            phash = str(imagehash.phash(Image.fromarray(alignedFace)))
            if phash in self.trained_images:
                identity = self.trained_images[phash].identity
                result_priority_queue.put_nowait((-1.0, identity, bb_index))
            else:
                rep = self.net.forwardImage(alignedFace)
                if self.svm is not None:
                    result_proba_list = self.svm.predict_proba(rep)
                    identity = np.argmax(result_proba_list[0])
                    print str(result_proba_list[0]) + " " + str(bb)
                    for index, prob in enumerate(result_proba_list[0]):
                        result_priority_queue.put_nowait((prob * -1.0, self.identities[index], bb_index))
                else:
                    result_priority_queue.put_nowait((0.0, -1, bb_index))

        matched_identities = []
        matched_bb_indices = []
        threshold = 0.6

        while len(matched_identities) != len(bbs) and result_priority_queue.empty() is False:
            detectedFaceInfo = result_priority_queue.get_nowait()

            identity = detectedFaceInfo[1]
            probability = detectedFaceInfo[0] * -1.0
            bb_index = detectedFaceInfo[2]
            # print detectedFaceInfo

            if identity in matched_identities:
                # print "matched_bbs : " + str(matched_identities)
                continue

            matched_bb_indices.append(bb_index)
            matched_identities.append(identity)

            if probability < threshold:
                results.append((-1, bbs[bb_index], 0.0))
            else:
                results.append((identity, bbs[bb_index], probability))

                # print '+' + str(results[len(results) - 1])

        for bb_index, bb in enumerate(bbs):
            if bb_index in matched_bb_indices:
                continue

            results.append((-1, bb, 0.0))

        return results
