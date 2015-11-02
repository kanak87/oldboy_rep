import json
import os
import pickle

from flask import Flask, request, send_from_directory
from flask.ext.cors import cross_origin

from werkzeug.utils import secure_filename

from face_api_server.proxy.face_database import FaceDatabase
from face_service import FaceService
from util import *

app = Flask(__name__)


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
        print e.message
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
        print e.message
        result = {"result": "-1",
                  "message": e.message}

    return json.dumps(result)


@app.route('/thumbnails/<filename>')
@cross_origin()
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/request_face_detection')
@cross_origin()
def request_face_detection():
    try:
        result = {"result": "0"}
        data = json.loads(request.form['data'])
        device_id = data['device_id']
        image = string_to_image(data['img'])

        detected_faces = faceService.predict(image)

        result['detected_faces'] = []
        for face in detected_faces:
            user = faceDatabase.find_user_by_index(face[0])
            detected_entity = {
                "id": user.identity,
                "name": user.name,
                "probability": face[2],
                "boundingbox": face[1],
                "thumbnail": user.thumbnail
            }
            result['detected_faces'].append(detected_entity)

    except Exception as e:
        print e.message
        result = {"result": "-1",
                  "message": e.message}

    return json.dumps(result)


if __name__ == "__main__":
    print "## init websocket"
    # detectStreamService = DetectionWebSocket()

    print "## face database"
    faceDatabase = FaceDatabase()

    print "## init face service"
    faceService = FaceService()

    print "## server start"
    app.run(host="0.0.0.0", port=20100, debug=True)
