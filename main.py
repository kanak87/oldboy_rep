import cv2
import datetime
import os

originalDirName = 'original'
detectDirName = 'detect'

if not os.path.exists(originalDirName):
    os.mkdir(originalDirName)

if not os.path.exists(detectDirName):
    os.mkdir(detectDirName)

dateDirName = ""

faceCascade = cv2.CascadeClassifier('face.xml')

video_capture = cv2.VideoCapture(0)

params = list()
params.append(cv2.IMWRITE_PNG_COMPRESSION)
params.append(9)


while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )

    filename = ""
    if len(faces) > 0:
        nowTime = datetime.datetime.now()
        currentDateDirName = '%04d-%02d-%02d' % (nowTime.year, nowTime.month, nowTime.day)

        if currentDateDirName != dateDirName:
            dateDirName = currentDateDirName
            newDir = os.path.join(originalDirName, dateDirName)
            if not os.path.exists(newDir):
                os.mkdir(newDir)

            newDir = os.path.join(detectDirName, dateDirName)
            if not os.path.exists(newDir):
                os.mkdir(newDir)

        filename = '%02d%02d%02d%02d%02d%02d%04d.png' % (nowTime.year%100, nowTime.month, nowTime.day, nowTime.hour, nowTime.minute, nowTime.second, nowTime.microsecond/100)
        cv2.imwrite(os.path.join(originalDirName, dateDirName, filename), frame, params)

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    if len(faces) > 0:
        cv2.imwrite(os.path.join(detectDirName, dateDirName, filename), frame, params)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()