import json

import cv2
import imutils as imutils
import requests

video_capture = cv2.VideoCapture(0)
# video_capture.set(3, 1024)
# video_capture.set(4, 768)
# video_capture.set(15, -8.0)

params = list()
params.append(cv2.IMWRITE_PNG_COMPRESSION)
params.append(9)
firstFrame = None

while True:
    (grabbed, frame) = video_capture.read()

    if not grabbed:
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0) \
 \
    if firstFrame is None:
        firstFrame = gray
        continue

    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)

    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) > 500:
            cv2.imwrite('img.png', frame, params)

            json_data = {"device_id": 1010}

            try:
                requests.post('http://127.0.0.1:20100/request_face_detection_from_webcam',
                              data={"data": json.dumps(json_data)},
                              files={"file[]": open('img.png', 'rb')})
            except Exception as e:
                print 'error'

                # print 'not send'
                # sleep(0.3)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
