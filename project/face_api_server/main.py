import json
import os
import pickle
import sys
import traceback

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource
from flask import Flask, request, send_from_directory, render_template
from flask.ext.cors import cross_origin
from werkzeug.utils import secure_filename

from proxy.redis_function import RedisProxy
from proxy.face_database import FaceDatabase
from face_service import FaceService
from util import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['IMAGE_STORE'] = True
app.config['UPLOAD_FOLDER'] = './thumbnails/'
app.config['IMAGE_FOLDER'] = './images/'

faceDetectSocketList = []

inet_addr = get_inet_addr();

@app.route('/')
@cross_origin()
def show_index():
    # Used ajax, because already exist data in javascript
    global inet_addr
    templateData = {'title': 'Face Detector',
                    'inet_addr': inet_addr
                    }
    return render_template('index.html', **templateData)


@app.route('/regit')
@cross_origin()
def registration():
    templateData = {'title': 'Face Detector',
                    'inet_addr': inet_addr
                    }
    return render_template('registration.html', **templateData)


@app.route('/findToFile')
@cross_origin()
def findToFile():
    templateData = {'title': 'Face Detector',
                    'inet_addr': inet_addr
                    }
    return render_template('findToFile.html', **templateData)


@app.route('/state')
@cross_origin()
def state():
    templateData = {'title': 'Face Detector',
                    'inet_addr': inet_addr
                    }
    return render_template('state.html', **templateData)


@app.route('/cameraStream')
@cross_origin()
def cameraStream():
    templateData = {'title': 'Face Detector',
                    'inet_addr': inet_addr
                    }
    return render_template('cameraStream.html', **templateData)


@app.route('/immediateLearn')
@cross_origin()
def immediateLearn():
    templateData = {'title': 'Face Detector',
                    'inet_addr': inet_addr
                    }
    return render_template('immediateLearn.html', **templateData)


class FaceDetectReceiveSocket(WebSocketServerProtocol):
    def onConnect(self, request):
        faceDetectSocketList.append(self)

    def onClose(self, wasClean, code, reason):
        faceDetectSocketList.remove(self)

    def onMessage(self, payload, isBinary):
        print payload


@app.route("/request_data", methods=['POST'])
@cross_origin()
def request_data():
    if request.form['data']:
        # print request.form['data']
        pass
    try:
        device_datas = redisProxy.get_device_datas()

        faces = []

        for user in faceDatabase.users:
            if user.identity == -1:
                continue

            user_face = {
                "id": user.identity,
                "name": user.name,
                "kind": user.kind,
                "thumbnail": user.thumbnail
            }
            faces.append(user_face)

        result = {"reuslt": "0",
                  "device_datas": device_datas,
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


app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


@app.route("/request_register_face", methods=['POST'])
@cross_origin()
def request_register_face():
    try:
        data = json.loads(request.form['data'])
        name = data['name']
        kind = data['kind']

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

            identity = faceDatabase.add_new_user(name, thumbnail_path, kind)

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
                i += 1

        result = {
            "result": "0",
            "face": {
                "id": identity,
                "name": name,
                "kind": kind,
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


@app.route("/request_register_face_from_webcam", methods=['POST'])
@cross_origin()
def request_register_face_from_webcam():
    try:
        data = json.loads(request.form['data'])
        name = data['name']
        kind = data['kind']

        images = []
        for imageUrl in data['images']:
            image = string_to_image(imageUrl, "")
            images.append(image)

            if app.config['IMAGE_STORE'] is True:
                filename = now_datetime_to_filename('png')
                save_path = os.path.join(app.config['IMAGE_FOLDER'], filename)
                save_array(image, save_path)

        if len(images) < 1:
            raise Exception('empty images array')

        if faceDatabase.is_exist(name) is False:
            thumbnail_path = name + "png"
            thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], thumbnail_path)
            save_array(images[0], thumbnail_path)

            identity = faceDatabase.add_new_user(name, thumbnail_path, kind)
        else:
            user = faceDatabase.find_user_by_name(name)
            identity = user.identity
            thumbnail_path = user.thumbnail

        training_result = faceService.training(identity, images)

        file_training_result = []
        i = 0
        for image in images:
            file_training_result.append({
                "filename": str(i),
                "result": training_result[i]
            })
            i += 1

        result = {
            "result": "0",
            "face": {
                "id": identity,
                "name": name,
                "kind": kind,
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


@app.route("/request_unregister_face", methods=['POST'])
@cross_origin()
def request_unregister_face():
    try:
        data = json.loads(request.form['data'])
        name = data['name']

        identity = faceDatabase.remove_user(name)
        faceService.remove_face(identity)

        result = {
            "result": "0",
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

        if app.config['IMAGE_STORE'] is True:
            filename = now_datetime_to_filename('png')
            save_path = os.path.join(app.config['IMAGE_FOLDER'], filename)
            save_array(image, save_path)

        send_image = True

        try:
            if data['debug'] == 1:
                send_image = False
        except Exception:
            send_image = True

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
                        "kind": user.kind,
                        "probability": face[2],
                        "boundingbox": [face[1].left(), face[1].top(), face[1].right(), face[1].bottom()],
                        "thumbnail": user.thumbnail
                    }
                else:
                    detected_entity = {
                        "id": -1,
                        "name": 'unknown',
                        "kind": FaceKind.Unknown,
                        "probability": 0.0,
                        "boundingbox": [face[1].left(), face[1].top(), face[1].right(), face[1].bottom()],
                        "thumbnail": ""
                    }
                detected_faces_result.append(detected_entity)

        annotated_image = annotate_face_info(image, detected_faces, faceDatabase)
        annotated_url_image = image_to_url(annotated_image)

        websocket_send_data = {
            'device_id': device_id,
            'image': annotated_url_image,
            'detected_faces': detected_faces_result
        }

        msg = {
            "type": "image",
            "content": websocket_send_data
        }

        redisProxy.update_device(device_id, websocket_send_data)

        for protocol in faceDetectSocketList:
            protocol.sendMessage(json.dumps(msg))
        result['detected_faces'] = detected_faces_result

        if send_image is True:
            result['image'] = annotated_url_image

    except Exception as e:
        print "-" * 60
        print e.message
        print " "
        print traceback.print_exc(file=sys.stdout)
        print "-" * 60
        result = {"result": "-1",
                  "message": e.message}

    return json.dumps(result)


@app.route('/request_face_detection_from_webcam', methods=['POST'])
@cross_origin()
def request_face_detection_from_webcam():
    try:
        result = {"result": "0"}
        data = json.loads(request.form['data'])
        device_id = data['device_id']

        uploaded_files = request.files.getlist("file[]")
        if len(uploaded_files) < 1:
            uploaded_files = request.files.getlist("files")
            if len(uploaded_files) < 1:
                raise Exception("upload file error")

        images = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                images.append(stream_to_image(file))

        image = images[0]
        detected_faces = faceService.predict(image)

        # results.append((identity, bb, result_proba_list[identity]))
        faceDetected = False
        detected_faces_result = []
        if detected_faces is not None:
            for face in detected_faces:
                faceDetected  = True
                if face[0] is not -1:
                    user = faceDatabase.find_user_by_index(face[0])
                    detected_entity = {
                        "id": user.identity,
                        "name": user.name,
                        "kind": user.kind,
                        "probability": face[2],
                        "boundingbox": [face[1].left(), face[1].top(), face[1].right(), face[1].bottom()],
                        "thumbnail": user.thumbnail
                    }
                else:
                    detected_entity = {
                        "id": -1,
                        "name": 'unknown',
                        "kind": FaceKind.Unknown,
                        "probability": 0.0,
                        "boundingbox": [face[1].left(), face[1].top(), face[1].right(), face[1].bottom()],
                        "thumbnail": ""
                    }
                detected_faces_result.append(detected_entity)

        annotated_image = annotate_face_info(image, detected_faces, faceDatabase)
        annotated_url_image = image_to_url(annotated_image)

        websocket_send_data = {
            'device_id': device_id,
            'image': annotated_url_image,
            'detected_faces': detected_faces_result
        }

        msg = {
            "type": "image",
            "content": websocket_send_data
        }

        redisProxy.update_device(device_id, websocket_send_data)

        for protocol in faceDetectSocketList:
            protocol.sendMessage(json.dumps(msg))

        if faceDetected is True and app.config['IMAGE_STORE'] is True:
            filename = now_datetime_to_filename('png')
            save_path = os.path.join(app.config['IMAGE_FOLDER'], filename)
            save_array(image, save_path)

    except Exception as e:
        print "-" * 60
        print e.message
        print " "
        print traceback.print_exc(file=sys.stdout)
        print "-" * 60
        result = {"result": "-1",
                  "message": e.message}

    return json.dumps(result)


@app.route('/request_face_detection_by_file', methods=['POST'])
@cross_origin()
def request_face_detection_by_file():
    try:
        result = {"result": "0"}
        data = json.loads(request.form['data'])
        device_id = data['device_id']

        send_image = True

        try:
            if data['debug'] == 1:
                send_image = False
        except Exception:
            send_image = True

        uploaded_files = request.files.getlist("file[]")
        if len(uploaded_files) < 1:
            uploaded_files = request.files.getlist("files")
            if len(uploaded_files) < 1:
                raise Exception("upload file error")

        images = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                images.append(stream_to_image(file))

                if app.config['IMAGE_STORE'] is True:
                    save_path = os.path.join(app.config['IMAGE_FOLDER'], file.filename)
                    save_array(images[len(images) - 1], save_path)

        image = images[0]

        detected_faces = faceService.predict(image)

        detected_faces_result = []
        if detected_faces is not None:
            for face in detected_faces:
                if face[0] is not -1:
                    user = faceDatabase.find_user_by_index(face[0])
                    detected_entity = {
                        "id": user.identity,
                        "name": user.name,
                        "kind": user.kind,
                        "probability": face[2],
                        "boundingbox": [face[1].left(), face[1].top(), face[1].right(), face[1].bottom()],
                        "thumbnail": user.thumbnail
                    }
                else:
                    detected_entity = {
                        "id": -1,
                        "name": 'unknown',
                        "kind": FaceKind.Unknown,
                        "probability": 0.0,
                        "boundingbox": [face[1].left(), face[1].top(), face[1].right(), face[1].bottom()],
                        "thumbnail": ""
                    }
                detected_faces_result.append(detected_entity)

        annotated_image = annotate_face_info(image, detected_faces, faceDatabase)
        annotated_url_image = image_to_url(annotated_image)

        websocket_send_data = {
            'device_id': device_id,
            'image': annotated_url_image,
            'detected_faces': detected_faces_result
        }

        msg = {
            "type": "image",
            "content": websocket_send_data
        }

        redisProxy.update_device(device_id, websocket_send_data)

        for protocol in faceDetectSocketList:
            protocol.sendMessage(json.dumps(msg))
        result['detected_faces'] = detected_faces_result

        if send_image is True:
            result['image'] = annotated_url_image

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
    # create thumbnail directory
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    if not os.path.exists(app.config['IMAGE_FOLDER']):
        os.makedirs(app.config['IMAGE_FOLDER'])

    print "## face database"
    faceDatabase = FaceDatabase()

    print "## redis"
    redisProxy = RedisProxy()

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

    while True:
        try:
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
        except Exception as e:
            print "#" * 60
            print e.message
            print " "
            print traceback.print_exc(file=sys.stdout)
            print "#" * 60
