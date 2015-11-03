import json
import os
import pickle
import sys, traceback

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource

from flask import Flask, request, send_from_directory
from flask.ext.cors import cross_origin

from werkzeug.utils import secure_filename

from proxy.face_database import FaceDatabase
from face_service import FaceService
from util import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

faceDetectSocketList = []


class FaceDetectReceiveSocket(WebSocketServerProtocol):
    def onConnect(self, request):
        faceDetectSocketList.append(self)

    def onClose(self, wasClean, code, reason):
        faceDetectSocketList.remove(self)

    def onMessage(self, payload, isBinary):
        print payload


@app.route("/")
@cross_origin()
def hello():
    return "Hello World!"


@app.route("/request_data", methods=['POST'])
@cross_origin()
def request_data():
    if request.form['data']:
        print request.form['data']
    try:
        device_ids = [1, 2, 3]

        faces = []

        for user in faceDatabase.users:
            user_face = {
                "id": user.identity,
                "name": user.name,
                "thumbnail": user.thumbnail
            }
            faces.append(user_face)

        result = {"reuslt": "0",
                  "device_ids": device_ids,
                  "faces": faces
                  }

    except Exception as e:
        print "-" * 60
        print e.message
        print " "
        print traceback.print_exc(file=sys.stdout)
        print "-" * 60
        result = {"result": "-1",
                  "message": e.message}

    return json.dumps(result)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


app.config['UPLOAD_FOLDER'] = './thumbnails/'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


@app.route("/request_register_face", methods=['POST'])
@cross_origin()
def request_register_face():
    try:
        data = json.loads(request.form['data'])
        name = data['name']

        uploaded_files = request.files.getlist("file[]")
        if len(uploaded_files) < 1:
            uploaded_files = request.files.getlist("files")
            if len(uploaded_files) < 1:
                raise Exception("upload file error")

        images = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                images.append(stream_to_image(file))

        if faceDatabase.is_exist(name) is False:
            thumbnailFile = uploaded_files[0]
            thumbnailFile.seek(0)
            filename, file_extension = os.path.splitext(secure_filename(thumbnailFile.filename))
            thumbnail_path = name + file_extension
            thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], thumbnail_path)
            thumbnailFile.save(thumbnail_path)

            identity = faceDatabase.add_new_user(name, thumbnail_path)

        else:
            user = faceDatabase.find_user_by_name(name)
            identity = user.identity
            thumbnail_path = user.thumbnail

        training_result = faceService.training(identity, images)

        file_training_result = []
        i = 0
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                file_training_result.append({
                    "filename": file.filename,
                    "result": training_result[i]
                })
                ++i

        result = {
            "result": "0",
            "face": {
                "id": identity,
                "name": name,
                "thumbnail": thumbnail_path
            },
            "training_result": file_training_result
        }

        pickle.dump(faceDatabase.users, open('user.pickle', 'wb'), -1)
        pickle.dump(faceService.svm, open('svm.pickle', 'wb'), -1)
        pickle.dump(faceService.trained_images, open('trained_images.pickle', 'wb'), -1)

    except Exception as e:
        print "-" * 60
        print e.message
        print " "
        print traceback.print_exc(file=sys.stdout)
        print "-" * 60
        result = {"result": "-1",
                  "message": e.message}

    return json.dumps(result)


@app.route('/thumbnails/<filename>')
@cross_origin()
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/request_face_detection', methods=['POST'])
@cross_origin()
def request_face_detection():
    try:
        result = {"result": "0"}
        data = json.loads(request.form['data'])
        device_id = data['device_id']
        image = string_to_image(data['img'])

        detected_faces = faceService.predict(image)

        # results.append((identity, bb, result_proba_list[identity]))
        detected_faces_result = []
        if detected_faces is not None:
            for face in detected_faces:
                if face[0] is not -1:
                    user = faceDatabase.find_user_by_index(face[0])
                    detected_entity = {
                        "id": user.identity,
                        "name": user.name,
                        "probability": face[2],
                        "boundingbox": [face[1].left(), face[1].top(), face[1].right(), face[1].bottom()],
                        "thumbnail": user.thumbnail
                    }
                else:
                    detected_entity = {
                        "id": -1,
                        "name": 'unknown',
                        "probability": 0.0,
                        "boundingbox": face[1],
                        "thumbnail": ""
                    }
                detected_faces_result.append(detected_entity)

        annotated_image = annotate_face_info(image, detected_faces, faceDatabase)

        msg = {
            "type": "image",
            "content": {
                'device_id': device_id,
                'image': image_to_url(annotated_image),
                'detected_faces': detected_faces_result
            }
        }

        for protocol in faceDetectSocketList:
            protocol.sendMessage(json.dumps(msg))
        result['detected_faces'] = detected_faces_result

    except Exception as e:
        print "-" * 60
        print e.message
        print " "
        print traceback.print_exc(file=sys.stdout)
        print "-" * 60
        result = {"result": "-1",
                  "message": e.message}

    return json.dumps(result)


if __name__ == "__main__":
    print "## face database"
    faceDatabase = FaceDatabase()

    print "## init face service"
    faceService = FaceService()

    print "## server start"
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False

    app.debug = debug
    if debug:
        log.startLogging(sys.stdout)

    wsFactory = WebSocketServerFactory(u"ws://127.0.0.1:20100",
                                       debug=debug,
                                       debugCodePaths=debug)

    wsFactory.protocol = FaceDetectReceiveSocket
    wsResource = WebSocketResource(wsFactory)
    wsgiResource = WSGIResource(reactor, reactor.getThreadPool(), app)
    rootResource = WSGIRootResource(wsgiResource, {'ws': wsResource})

    site = Site(rootResource)

    reactor.listenTCP(20100, site)
    reactor.run()
