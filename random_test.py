import numpy as np
import imutils
import cv2
import pandas as pd
import time
from enum import Enum
import serial
from serial.tools.list_ports import comports
import subprocess


def visual():

    # cap = cv2.VideoCapture(1)
    # ret, image = cap.read()
    image = cv2.imread("C:/Users/Muham/Desktop/foto1.jpeg")
    cv2.imshow("adasd", image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 1)
    for i in range(3, 29, 2):
        for k in range(3, 29, 2):

            cv2.imshow("a1", cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, i, k))
            cv2.waitKey(5)
            cv2.Scale
    edged = cv2.Canny(gray, 120, 130)
    cv2.imshow("adasd", edged)

    kernel = np.ones((9, 9), np.uint8)
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
    cv2.imwrite("a2.jpg", closed)
    cnts = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    mycnts = []
    for cnt in cnts:
        if 7000 < cv2.contourArea(cnt) < 20000:
            perimeter = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.08 * perimeter, True)
            if len(approx) == 4:
                mycnts.append(cnt)

    for cnt in mycnts:
        data = []
        if 6500 < cv2.contourArea(cnt) < 21000:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(image, [box], 0, (0, 0, 255), 2)
            rect = list(rect)
            angle = list(np.float_(rect[2:3]))
            angle = float(angle[0])
            coor = list(np.float_(rect[0:1]))
            coor = coor[0]
            cx = int(coor[0])
            cy = int(coor[1])
            cv2.circle(image, (cx, cy), 1, (0, 0, 255), -1)
            cv2.putText(image, "center: %f-%f  Angle: %f" % (coor[0], coor[1], angle), (15, 15),
                        cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 1)

            data.append((coor[0]))
            data.append((coor[1]))
            data.append(angle)
            cv2.drawContours(image, mycnts, -1, (0, 255, 0), 1)
            # return data

        cv2.imshow("Output", image)


visual()
