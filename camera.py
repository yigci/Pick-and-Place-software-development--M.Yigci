# import the necessary packages
import numpy as np
import imutils
import cv2
import urllib.request
import time

# import sys
# import pickle


def visual():

    address = "http://192.168.1.23:4747/video?1280x720/"
    cap = cv2.VideoCapture(address)
    address = "http://192.168.1.23:4747/cam/1/led_toggle"
    urllib.request.urlopen(address)
    time.sleep(2)
    while 1:
        ret, image = cap.read()
        cv2.waitKey(1)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 16)
        edged = cv2.Canny(gray, 50, 100)
        cv2.namedWindow("Output")
        kernel = np.ones((9, 9), np.uint8)
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
        cnts = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
#       cv2.drawContours(image, cnts, -1, (0, 255, 0), 1)
        cv2.waitKey(5)
        for cnt in cnts:
            if 2000 < cv2.contourArea(cnt) < 200000:
                rect = cv2.minAreaRect(cnt)
#               box = cv2.boxPoints(rect)
#               box = np.int0(box)
#               cv2.drawContours(image, [box], 0, (0, 0, 255), 2)
#               cv2.waitKey(5)
                rect = list(rect)
                angle = list(np.float_(rect[2:3]))
                angle = float(angle[0])
                coor = list(np.float_(rect[0:1]))
                coor = coor[0]
                cx = int(coor[0])
                cy = int(coor[1])
                cv2.circle(image, (cx, cy), 1, (255, 255, 255), -1)
                cv2.putText(image, "center: %f-%f  Angle: %f" % (coor[0], coor[1], angle), (15, 15),
                            cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 1)
#               cv2.waitKey(50)
                cv2.imshow("Output", image)
                open('center_info.txt', 'w').close()
                myfile = open('center_info.txt', 'a')
                data = []

                data.append((coor[0]))
                data.append((coor[1]))
                data.append(angle)
#               if write_to_file is 1:
                myfile.write(str(data))
#               write_to_file = 0
                return data
        cv2.imshow("Output", image)
