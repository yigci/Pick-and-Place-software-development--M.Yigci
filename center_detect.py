import cv2
import numpy as np


address = "http://192.168.1.23:4747/video?1280x720/"
cap = cv2.VideoCapture(0)
while 1:
    ret, image = cap.read()
    cv2.waitKey(10)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#   blurred = cv2.bilateralFilter(image, 9, 120, 120)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 6)
    edged = cv2.Canny(gray, 32, 55)
    kernel = np.ones((9, 9), np.uint8)
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
    cnts = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0]

    cv2.drawContours(image, cnts, -1, (0, 255, 0), 1)
    for cnt in cnts:
        if 7000 < cv2.contourArea(cnt) < 20000:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(image, [box], 0, (0, 0, 255), 2)
            rect = list(rect)
            angle = list(np.float_(rect[2:3]))
            angle = float(angle[0])
            coor = list(np.float_(rect[0:1]))
            coor = coor[0]
            cX = int(coor[0])
            cY = int(coor[1])
            cv2.circle(image, (cX, cY), 1, (255, 255, 255), -1)
            cv2.putText(image, "center: %f-%f  Angle: %f" % (coor[0], coor[1], angle), (15, 15),
                        cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 1)
            cv2.imshow("asdads", image)
