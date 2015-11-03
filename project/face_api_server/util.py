import base64
import StringIO
import cStringIO
import urllib
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


def stream_to_image(file):
    image = Image.open(cStringIO.StringIO(file.read()))

    buf = np.fliplr(np.asarray(image))
    rgbFrame = np.zeros((image.height, image.width, 3), dtype=np.uint8)
    rgbFrame[:, :, 0] = buf[:, :, 2]
    rgbFrame[:, :, 1] = buf[:, :, 1]
    rgbFrame[:, :, 2] = buf[:, :, 0]

    return rgbFrame


def file_to_image(path):
    image = Image.open(path)

    buf = np.fliplr(np.asarray(image))
    rgbFrame = np.zeros((image.height, image.width, 3), dtype=np.uint8)
    rgbFrame[:, :, 0] = buf[:, :, 2]
    rgbFrame[:, :, 1] = buf[:, :, 1]
    rgbFrame[:, :, 2] = buf[:, :, 0]

    plt.figure()
    plt.imshow(rgbFrame)
    plt.xticks([])
    plt.yticks([])

    return rgbFrame


def string_to_image(image_string):
    head = "data:image/jpeg;base64,"
    assert (image_string.startswith(head))

    imgdata = base64.b64decode(image_string[len(head):])
    imgF = StringIO.StringIO()
    imgF.write(imgdata)
    imgF.seek(0)
    img = Image.open(imgF)
    buf = np.fliplr(np.asarray(img))

    rgbFrame = np.zeros((img.height, img.width, 3), dtype=np.uint8)
    rgbFrame[:, :, 0] = buf[:, :, 2]
    rgbFrame[:, :, 1] = buf[:, :, 1]
    rgbFrame[:, :, 2] = buf[:, :, 0]

    plt.figure()
    plt.imshow(rgbFrame)
    plt.xticks([])
    plt.yticks([])

    return rgbFrame


def annotate_face_info(image, detected_faces, faceDatabase):
    annotated_frame = np.copy(image)

    for detected_face in detected_faces:
        bb = detected_face[1]
        bl = (bb.left(), bb.bottom())
        tr = (bb.right(), bb.top())

        cv2.rectangle(annotated_frame, bl, tr, color=(153, 255, 204),
                      thickness=3)
        identity = detected_face[0]
        if identity == -1:
            name = "Unknown"
        else:
            name = faceDatabase.find_user_by_index(identity).name

        probability = detected_face[2] * 100
        cv2.putText(annotated_frame, name + '[' + str(round(probability, 1)) + '%]', (bb.left(), bb.top() - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.75,
                    color=(152, 255, 204), thickness=2)

    return annotated_frame


def image_to_url(image):
    plt.figure()
    plt.imshow(image)
    plt.xticks([])
    plt.yticks([])

    imgdata = StringIO.StringIO()
    plt.savefig(imgdata, format='png')
    imgdata.seek(0)
    content = 'data:image/png;base64,' + \
              urllib.quote(base64.b64encode(imgdata.buf))

    return content
