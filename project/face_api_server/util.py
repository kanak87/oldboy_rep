import base64
import StringIO
import cStringIO
import numpy as np
from PIL import Image


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

    return rgbFrame