# import the necessary packages
import numpy as np
import imutils
import cv2
# import urllib.request
# import time


def visual():

    # cv2.namedWindow("Output")
    address = "http://172.20.10.12:4747/video?1280x720"
    cap = cv2.VideoCapture(0)
    # address = "http://192.168.1.23:4747/cam/1/led_toggle"
    # urllib.request.urlopen(address)
    while 1:
        ret, image = cap.read()
        cv2.waitKey(1)
        res_y = int(len(image[0]))
        res_x = int(len(image))
        starty = int((res_y-res_x)/2)
        image = image[:, starty:starty+res_x]
        origin = int(res_x/2)
        image[origin, origin-5:origin+5] = (255, 0, 0)
        image[origin-5:origin+5, origin] = (255, 0, 0)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # gray = cv2.GaussianBlur(gray, (3, 3), 40)
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 16)
        cv2.imshow("threshold", gray)
        edged = cv2.Canny(gray, 50, 100)
        kernel = np.ones((5, 5), np.uint8)

        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
        cnts = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        mycnts = []
        for cnt in cnts:
            if 1000 < cv2.contourArea(cnt) < 20000:
                perimeter = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.12 * perimeter, True)
                if len(approx) == 4:
                    mycnts.append(cnt)
        print(type(mycnts))
        cv2.circle(image, (origin, origin), 1, (255, 255, 255), -1)
        for cnt in mycnts:
            data = []
            if 1500 < cv2.contourArea(cnt) < 21000:
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
                # cv2.destroyAllWindows()
                # return data
        cv2.imshow("Output", image)

visual()
