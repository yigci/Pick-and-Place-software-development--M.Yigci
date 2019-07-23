import numpy as np
import imutils
import cv2
import pandas as pd
import time
from enum import Enum
import serial
from serial.tools.list_ports import comports
import subprocess
from PIL import Image


CAMERA_POSITION = []  # Predefined constants.
FEEDER_POSITION = []
DEFINED_CENTER = []


def visual():
    camera = input("camera number")
    cap = cv2.VideoCapture(int(camera))
    ret, image = cap.read()
    res_y = int(len(image[0]))
    res_x = int(len(image))
    starty = int((res_y - res_x) / 2)
    origin = int(res_x / 2)
    DEFINED_CENTER.append(origin)
    DEFINED_CENTER.append(origin)
    while 1:
        ret, image = cap.read()
        cv2.waitKey(1)
        cv2.imshow("orig", image)
        image = image[:, 0:480]
        cv2.imshow("Crop", image)
        cv2.waitKey()
        image = imutils.rotate(image, 90)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 15)
       #  gray = ~gray

        edged = cv2.Canny(gray, 50, 200)
        kernel = np.ones((5, 5), np.uint8)
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
        cnts = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        mycnts = []
        for cnt in cnts:
            if 7000 < cv2.contourArea(cnt) < 75000:
                perimeter = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.03 * perimeter, True)
                # if len(approx) > 4:
                print("%d: press" % len(approx))
                mycnts.append(cnt)


        cv2.circle(image, (origin, origin), 1, (255, 255, 255), -1)
        for cnt in mycnts:
            data = []
            if 6500 < cv2.contourArea(cnt) < 65000:
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(image, [box], -1, (0, 0, 255), 1)
                rect = list(rect)
                angle = list(np.float_(rect[2:3]))
                angle = float(angle[0])
                coor = list(np.float_(rect[0:1]))
                coor = coor[0]
                cx = int(coor[0])
                cy = int(coor[1])
                cv2.circle(image, (cx, cy), 1, (0, 0, 255), -1)
                cv2.putText(image, "center: %f-%f  Angle: %f" % (coor[0], coor[1], angle), (15, 125),
                            cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)

                data.append((coor[0]))
                data.append((coor[1]))
                data.append(angle)
                cv2.imwrite("img.jpg", image)
                cv2.drawContours(image, mycnts, -1, (0, 255, 0), 1)
                cv2.imshow("contour", image)

                image[origin, origin - 5:origin + 5] = (255, 0, 0)
                image[origin - 5:origin + 5, origin] = (255, 0, 0)
                cv2.imshow("Output", image)
                # return data

        image[origin, origin - 5:origin + 5] = (255, 0, 0)
        image[origin - 5:origin + 5, origin] = (255, 0, 0)
        cv2.imshow("Output", image)


visual()
