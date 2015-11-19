# -*- coding: utf-8 -*-

import base64
import StringIO
import cStringIO
import json
from time import sleep
import urllib

import cv2
import datetime
import netifaces
import numpy as np
from PIL import Image
import requests
from proxy.face_database import FaceKind


def save_array(image_array, filename):
    im = Image.fromarray(image_array)
    im.save(filename)


def image_to_nparray(image):
    buf = np.asarray(image)
    rgbFrame = np.zeros((image.height, image.width, 3), dtype=np.uint8)
    rgbFrame[:, :, 0] = buf[:, :, 0]
    rgbFrame[:, :, 1] = buf[:, :, 1]
    rgbFrame[:, :, 2] = buf[:, :, 2]

    sleep(1)
    return rgbFrame


def stream_to_image(file):
    image = Image.open(cStringIO.StringIO(file.read()))
    return image_to_nparray(image)


def file_to_image(path):
    image = Image.open(path)
    return image_to_nparray(image)


def string_to_image(image_string, head="data:image/jpeg;base64,"):
    assert (image_string.startswith(head))

    imgdata = base64.b64decode(image_string[len(head):])
    imgF = StringIO.StringIO()
    imgF.write(imgdata)
    imgF.seek(0)
    image = Image.open(imgF)

    return image_to_nparray(image)


def annotate_face_info(image, detected_faces, faceDatabase):
    annotated_frame = np.copy(image)

    if detected_faces is None:
        return annotated_frame

    for detected_face in detected_faces:
        bb = detected_face[1]
        bl = (bb.left(), bb.bottom())
        tr = (bb.right(), bb.top())

        identity = detected_face[0]
        if identity == -1:
            name = "Unknown"
            color = (152, 255, 204)
        else:
            user = faceDatabase.find_user_by_index(identity)
            name = user.name
            if user.kind is FaceKind.Normal:
                color = (64, 255, 92)
            elif user.kind is FaceKind.Missing:
                color = (156, 117, 235)
            elif user.kind is FaceKind.Wanted:
                color = (240, 96, 93)
            else:
                color = (152, 255, 204)

        probability = detected_face[2] * 100

        cv2.rectangle(annotated_frame, bl, tr, color=color,
                      thickness=3)
        cv2.putText(annotated_frame, name + '[' + str(round(probability, 1)) + '%]', (bb.left(), bb.top() - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.75,
                    color=color, thickness=2)

    return annotated_frame


def image_to_url(image):
    img = Image.fromarray(image)

    imgdata = StringIO.StringIO(img._repr_png_())
    imgdata.seek(0)
    content = 'data:image/png;base64,' + urllib.quote(base64.b64encode(imgdata.buf))

    return content


def now_datetime_to_filename(ext):
    now_time = datetime.datetime.now()
    filename = '%02d%02d%02d%02d%02d%02d%04d.%s' % (
        now_time.year % 100, now_time.month, now_time.day, now_time.hour, now_time.minute, now_time.second,
        now_time.microsecond / 100, ext)

    return filename


def get_inet_addr():
    interfaces = netifaces.interfaces()
    for i in interfaces:
        if i == 'lo':
            continue
        iface = netifaces.ifaddresses(i).get(netifaces.AF_INET)
        if iface != None:
            for j in iface:
                return j['addr']


def send_sms(device_id, name, probability):
    appid = ''
    apikey = ''
    sender = ''
    receivers = []
    device_text = u'%s기기' % (str(device_id))
    if int(device_id) is 999:
        device_text = u'Web'
    elif int(device_id) is 1010:
        device_text = u'씨앗방'
    elif int(device_id) is 1011:
        device_text = u'폴리스캠'
    elif int(device_id) is 1:
        devicetext = u'스마트폰'

    content = u'[Oldboy] "%s"(이)가 "%s"에서 발견되었습니다. 유사도 %s' % (name, device_text, str(round(probability, 1)))

    url = 'https://api.bluehouselab.com/smscenter/v1.0/sendsms'
    params = {
        'sender': sender,
        'receivers': receivers,
        'content': content,
    }
    headers = {'Content-type': 'application/json; charset=utf-8', }
    r = requests.post(url, data=json.dumps(params),
                      auth=(appid, apikey), headers=headers)

    print r.status_code, r.reason
    if r.status_code == 200:
        print r.json()
