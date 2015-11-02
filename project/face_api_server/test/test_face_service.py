from PIL import Image
from face_api_server.face_service import FaceService
import numpy as np

face_service = FaceService("asdf")

def load_img(path):
    image = Image.open(path)

    buf = np.fliplr(np.asarray(image))
    rgbFrame = np.zeros((image.height, image.width, 3), dtype=np.uint8)
    rgbFrame[:, :, 0] = buf[:, :, 2]
    rgbFrame[:, :, 1] = buf[:, :, 1]
    rgbFrame[:, :, 2] = buf[:, :, 0]

    return rgbFrame

print 'j training'
images = [load_img('./data/j1.jpg'),
          load_img('./data/j2.png'),
          load_img('./data/j3.png'),
          load_img('./data/j4.png'),
          load_img('./data/j5.png'),
          load_img('./data/j6.png'),
          load_img('./data/j7.png'),
          load_img('./data/j8.png'),
          load_img('./data/j9.png'),
          load_img('./data/j10.png'),
          load_img('./data/j11.png'),
          load_img('./data/j12.png'),
          load_img('./data/j13.png'),
          load_img('./data/j14.png'),
          ]
face_service.training("jung", images)

print 'c training'
images = [load_img('./data/c1.png'),
          load_img('./data/c2.png'),
          load_img('./data/c3.png'),
          load_img('./data/c4.png'),
          load_img('./data/c5.png')
          ]
face_service.training("choi", images)


print 'm training'
images = [load_img('./data/m1.png'),
          load_img('./data/m2.png'),
          load_img('./data/m3.png'),
          load_img('./data/m4.png')
          ]
face_service.training("min", images)

print 'predict training'

test_image = load_img('./data/t2.png')

users = face_service.predict(test_image)
if users is None:
    print 'not found'
