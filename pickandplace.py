import numpy as np
import imutils
import cv2
import pandas as pd
import time
from enum import Enum
import serial


s = None
CAMERA_POSITION = [10, 0]   # Predefined constants.
FEEDER_POSITION = [50, 0]
DEFINED_CENTER = [360, 360]


class State(Enum):      # To make the program easier to understand, some of the processes assigned to numbers.
    GO_TO_FEEDER = 0
    PICK_UP = 1
    PLACE = 2
    GO_TO_CAMERA = 3
    CAMERA_ADJUST = 4
    PLACEMENT_LOC = 5


def act_serial():

    global s
    serial_address = input("Enter connection port of the GRBL controller.\nIn format of 'COM+number': ")
    baudrate = input("Enter Baudrate. If not configured otherwise it is (115200): ")
    try:
        s = serial.Serial(serial_address, baudrate)   # connect to controller
    except serial.serialutil.SerialException:
        print("Connection failed.")
        return 0

    print("Connection established.")
    s.write("\r\n\r\n".encode())        # Wake up grbl
    time.sleep(2)                       # A few seconds is necessary for grbl until it accepts commands.


def send_gcode(gcode_address):

    f = open(gcode_address, 'r')
    s.flushInput()  # Flush startup text in serial input

    for line in f:
        code = line.strip()  # Strip all EOL characters for streaming
        if code is not '?':
            print('Sending: ' + code)
        s.write((code + "\n").encode())  # Send g-code block to grbl
        grbl_out = s.readline()  # Wait for grbl response with carriage return
        ret = grbl_out.strip().decode()

        if 'Sent' in ret:
            print("Sent.")

        if 'Run' in ret:
            f.close()
            return 1

    f.close()
    time.sleep(1)
    print("Transmission finished.")


def visual():

    # cv2.namedWindow("Output")
    # address = "http://192.168.1.23:4747/video?1280x720"
    address = input("Select system camera(0) or Camera server(url)")
    cap = cv2.VideoCapture(address)
    # address = "http://192.168.1.23:4747/cam/1/led_toggle"
    # urllib.request.urlopen(address)
    while 1:
        ret, image = cap.read()
        cv2.waitKey(1)
        # image = image[280:1000, 0:720]
        # image[180, 175:185] = (255, 0, 0)
        # image[175:185, 180] = (255, 0, 0)
        # image[180, 180] = (255, 255, 255)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 16)
        edged = cv2.Canny(gray, 50, 100)
        kernel = np.ones((9, 9), np.uint8)
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
        cnts = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        mycnts = []
        for cnt in cnts:
            if 7000 < cv2.contourArea(cnt) < 20000:
                perimeter = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.12 * perimeter, True)
                if len(approx) == 4:
                    mycnts.append(cnt)

        cv2.circle(image, (180, 180), 1, (255, 255, 255), -1)
        for cnt in mycnts:
            data = []
            if 6500 < cv2.contourArea(cnt) < 21000:
                rect = cv2.minAreaRect(cnt)
#               box = cv2.boxPoints(rect)
#               box = np.int0(box)
#               cv2.drawContours(image, [box], 0, (0, 0, 255), 2)
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
                cv2.destroyAllWindows()
                return data
        cv2.imshow("Output", image)


def gcode_generate(x, y, angle, statement):
    path = input("Enter the path of GCode generation file: ")
    if angle > 0:
        print("Angle is received. \nAngle correction is not available right now.\nProceeding to next step.")
    with open(path, "r") as f:      # Code between line 26-28 is to clear the gcode.txt file.
        f.read()
    command_file = open(path, "w")

    if statement == State.GO_TO_FEEDER:    # Move to feeder position
        command_file.write("X%s Y%s \n" % (str(FEEDER_POSITION[0]), str(FEEDER_POSITION[1])))  # write gcode to the file
        command_file.close()                     # close file for next step.
        send_gcode(path)            # Send gcode to the controller.

    elif statement == State.PICK_UP:       # pick up
        command_file.write("Z10 \nM08 \nZ20. \n")
        command_file.close()
        send_gcode(path)

    elif statement == State.PLACE:         # place
        command_file.write("Z10 \nM09 \nZ20. \n")
        command_file.close()
        send_gcode(path)

    elif statement == State.GO_TO_CAMERA:  # GO TO CAMERA
        command_file.write("X%s Y%s \n" % (str(CAMERA_POSITION[0]), str(CAMERA_POSITION[1])))
        command_file.close()
        send_gcode(path)

    elif statement == State.CAMERA_ADJUST:  # Camera position adjustments
        command_file.write("G91 \nX%s Y%s \n" % (str(x), str(y)))  # incremental mode should be used.
        command_file.close()
        send_gcode(path)

    elif statement == State.PLACEMENT_LOC:
        command_file.write("G90 \nX%s Y%s \n" % (str(x), str(y)))  # absolute movement to placement location
        command_file.close()
        send_gcode(path)
    elif statement == '?':
        command_file.write("?")
        command_file.close()
        check = send_gcode(path)
        return check


def component_handle(feeder, indx, angle, x_coordinates, y_coordinates):
    path = input("Enter the initial settings file path: ")
    send_gcode(path)
    print("Angle of the component is not included to the processes yet.(%f)", angle[0])
    for i in range(len(feeder)):
        locations = indx[i]
        print("Picking: %s" % feeder[i])
        for k in range(len(locations)):
            center_x, center_y, change_x, change_y, check_x, check_y = 0, 0, 0, 0, 0, 0
            position_x = (float(x_coordinates[locations[k]]) / 100)
            position_y = (float(y_coordinates[locations[k]]) / 100)
            gcode_generate(0, 0, 0, State.GO_TO_FEEDER)  # GO TO FEEDER POSITION
            gcode_generate(0, 0, 0, State.PICK_UP)       # PICKUP THE COMPONENT
            gcode_generate(0, 0, 0, State.GO_TO_CAMERA)  # GO TO CAMERA POSITION
            time.sleep(1)

            while (check_x and check_y) is 0:
                data = None
                check_if_running = 0

                while gcode_generate(0, 0, 0, '?'):  # Continuously check if any of the axis is running.
                    if check_if_running == 0:
                        print("Already performing process. Waiting process to end.")
                        check_if_running += 1
                    time.sleep(0.1)
                if check_if_running is not 0:
                    print("Process have ended. Camera adjustment process started.")

                while data is None:
                    check_x = 0
                    check_y = 0
                    data = visual()
                center_x = data[0]
                center_y = data[1]
                # current_angle = data[2]
                if 150 < center_x < 200:
                    check_x = 1
                if 150 < center_y < 200:    # Camera sensitivity settings. These if statements defines that how many
                                            # pixels can center point vary from the exact origin.
                    check_y = 1
                print(center_x, center_y)
                gcode_generate((DEFINED_CENTER[0]-center_x), (DEFINED_CENTER[1]-center_y), 0, State.CAMERA_ADJUST)
                change_x += (DEFINED_CENTER[0]-float(center_x))
                change_y += (DEFINED_CENTER[1]-float(center_y))

            gcode_generate(position_x, position_y, 0, State.PLACEMENT_LOC)    # GO TO PLACEMENT POINT

            gcode_generate(0, 0, 0, State.PLACE)  # PLACE THE COMPONENT


def read_gerber():

    loc = input("Enter full path of gerber file: ")
    # loc = "C:/Users/muham/Desktop/XY-coordinates.htm"
    table = pd.read_html(loc)
    table = table[0]
    dimension = np.shape(table)
    row = dimension[0] - 1
    components = table[1]
    x_coordinates = table[5]
    y_coordinates = table[6]
    angles = table[7]
    x_coordinates = list(x_coordinates)
    y_coordinates = list(y_coordinates)
    components = list(components)
    angles = list(angles)
    del x_coordinates[0]
    del y_coordinates[0]
    del components[0]
    del angles[0]
    type_names = []
    type_names = list(type_names)
    type_names.append(components[0])

    for i in range(row):
        is_new = 1
        for k in range(len(type_names)):
            if type_names[k] == components[i]:
                is_new = 0
        if is_new is 1:
            type_names.append(components[i])

    indx_list = []

    for t in range(len(type_names)):
        indx = []
        for r in range(row):
            if components[r] == type_names[t]:
                indx.append(r)
        indx_list.append(indx)

    component_handle(type_names, indx_list, angles, x_coordinates, y_coordinates)


def start():

    while act_serial() == 0:
        print("Check your device path.")
    read_gerber()


start()
