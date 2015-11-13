import json

import cv2
import requests

video_capture = cv2.VideoCapture(0)
#video_capture.set(3, 1024)
#video_capture.set(4, 768)
#video_capture.set(15, -8.0)

params = list()
params.append(cv2.IMWRITE_PNG_COMPRESSION)
params.append(9)


while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    #cv2.imshow('Video', frame)
    cv2.imwrite('img.png', frame, params)

    json_data = { "device_id" : 1010 }

    try:
        requests.post('http://127.0.0.1:20100/request_face_detection_from_webcam',
                      data = {"data" : json.dumps(json_data)},
                      files= {"file[]" : open('img.png', 'rb')})
    except Exception as e:
        print 'error'
    #sleep(0.3)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()