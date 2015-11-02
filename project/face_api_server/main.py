import json
import os

from flask import Flask, request, send_from_directory
from werkzeug.utils import secure_filename

from face_service import FaceService
from detect_stream_service import DetectionWebSocket
from util import *

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/request_data", methods=['POST'])
def request_data():
    if request.form['data']:
        print request.form['data']
    try:
        device_ids = [1, 2, 3]

        result = {"reuslt": "0",
                  "device_ids": device_ids,
                  "faces": faces}

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
def request_register_face():
    try:
        data = json.loads(request.form['data'])
        name = data['name']

        uploaded_files = request.files.getlist("file[]")
        if len(uploaded_files) < 1:
            raise Exception("upload file error")

        images = []

        is_first_file = True
        save_file_name = ""
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                images.append(stream_to_image(file))

                if is_first_file is True:
                    file.seek(0)
                    filename = secure_filename(file.filename)
                    save_file_name = name + filename[-4:]
                    save_file_name = os.path.join(app.config['UPLOAD_FOLDER'], save_file_name)
                    file.save(save_file_name)
                    is_first_file = False

        identity = faceService.training(name, images)

        result = {
            "result": "0",
            "face": {
                "id": identity,
                "name": name,
                "thumbnail": save_file_name
            }
        }

    except Exception as e:
        print e.message
        result = {"result": "-1",
                  "message": e.message}

    return json.dumps(result)


@app.route('/thumbnails/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/request_face_detection')
def request_face_detection():
    try:
        result = {"result": "0"}
        data = json.loads(request.form['data'])
        device_id = data['device_id']
        image = string_to_image(data['img'])

        detected_faces = faceService.predict(image)

        # results.append((self.faces[identity], bb, result_proba_list[max_index]))

        result['detected_faces'] = []
        for face in detected_faces:
            detected_entity = {
                "id": face[0],
                "name": faceService.people[face[0]],
                "probability" : face[2],
                "boundingbox" : face[1],
                "thumbnail": "/thumbnails/jung.png"
            }
            result['detected_faces'].append(detected_entity)

    except Exception as e:
        print e.message
        result = {"result": "-1",
                  "message": e.message}

    return json.dumps(result)


if __name__ == "__main__":
    print "## init websocket"
    detectStreamService = DetectionWebSocket()

    print "## init face service"
    faceService = FaceService(detectStreamService)

    print "## server start"
    app.run(host="0.0.0.0", port=20100, debug=True)
