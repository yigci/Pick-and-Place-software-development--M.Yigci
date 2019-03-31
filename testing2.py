import numpy as np
import imutils
import cv2
import pandas as pd
import time
from enum import Enum
import serial
from serial.tools.list_ports import comports
import subprocess


s = None
CAMERA_POSITION = [10, 0]  # Predefined constants.
FEEDER_POSITION = [50, 0]
DEFINED_CENTER = [240, 240]


class State(Enum):  # To make the program easier to understand, some of the processes assigned to numbers.
    GO_TO_FEEDER = 0
    PICK_UP = 1
    PLACE = 2
    GO_TO_CAMERA = 3
    CAMERA_ADJUST = 4
    PLACEMENT_LOC = 5
    SET_RELATIVE_OFFSET = 6  # This option changes machine's current position to given coordinates.(only x and y axis)
    ANGLE_CORRECTION = 7


def send_gcode(gcode):
    s.flushInput()  # Flush startup text in serial input
    code = gcode.splitlines()  # Strip all EOL characters for streaming

    for line in code:

        # check = 1
        print('Sending: ' + line)
        s.write((line + "\n").encode())  # Send g-code block to grbl
        grbl_out = s.readline()  # Wait for grbl response with carriage return
        ret = grbl_out.strip().decode()
        if ret is not 'Sent':
            print(ret)

        # while check is 1:
        #     s.write(("?" + "\n").encode())
        #     grbl_out = s.readline()  # Wait for grbl response with carriage return
        #     ret = grbl_out.strip().decode()
        #     time.sleep(0.1)
        #     if 'Idle' in ret:
        #         check = 0

    time.sleep(1)
    print("Transmission finished.")


def gcode_generate(x, y, angle, statement):

    if statement == State.GO_TO_FEEDER:  # Move to feeder position
        gcode = "X%s Y%s" % (str(FEEDER_POSITION[0]), str(FEEDER_POSITION[1]))
        send_gcode(gcode)  # Send gcode to the controller.

    elif statement == State.PICK_UP:  # pick up
        gcode = "Z50 \nM08 \nZ0 \n"
        send_gcode(gcode)

    elif statement == State.PLACE:  # place
        gcode = "M9 \nZ50 \nM10 \nZ0 \n"
        send_gcode(gcode)

    elif statement == State.GO_TO_CAMERA:  # GO TO CAMERA
        gcode = "X%s Y%s \nM7\n" % (str(CAMERA_POSITION[0]), str(CAMERA_POSITION[1]))
        send_gcode(gcode)

    elif statement == State.CAMERA_ADJUST:  # Camera position adjustments
        gcode = "G91 \nX%s Y%s \nG90" % (str(x), str(y))
        send_gcode(gcode)

    elif statement == State.PLACEMENT_LOC:
        gcode = "X%s Y%s \n" % (str(x), str(y))
        send_gcode(gcode)
    elif statement == State.SET_RELATIVE_OFFSET:
        gcode = "G10 L20 P1 X%s Y%s" % (str(x), str(y))
        send_gcode(gcode)
    elif statement == State.ANGLE_CORRECTION:
        gcode = "A%s" % str(angle)
        send_gcode(gcode)


def visual():
    cv2.namedWindow("Output")
    cap = cv2.VideoCapture(0)
    while 1:
        ret, image = cap.read()
        cv2.waitKey(1)
        res_y = int(len(image[0]))
        res_x = int(len(image))
        starty = int((res_y - res_x) / 2)
        image = image[:, starty:starty + res_x]
        origin = int(res_x / 2)
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

        cv2.circle(image, (origin, origin), 1, (255, 255, 255), -1)
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
                return data

        image[origin, origin - 5:origin + 5] = (255, 0, 0)
        image[origin - 5:origin + 5, origin] = (255, 0, 0)
        cv2.imshow("Output", image)


def component_handle(feeder, indx, angle, x_coordinates, y_coordinates):
    print("Do you want to load user defined GCode settings? (y/n)\n=> ")
    choice = input()
    choice.lower()
    if choice == "y":
        initial = input("Enter initial settings path: ")
        send_gcode(initial)
    else:
        initial = "G90"  # absolute distance mode
        if choice != "n":
            print("Error. Default settings will be used.")
        send_gcode(initial)

    # print("Angle of the component is not included to the program yet.(%f)", angle[0])
    # angle adjustments should be included to the program. Either servo or step motor can be used.
    for i in range(len(feeder)):
        locations = indx[i]
        print("Picking: %s" % feeder[i])
        for k in range(len(locations)):
            center_x, center_y, change_x, change_y, check_x, check_y = 0, 0, 0, 0, 0, 0
            position_x = (float(x_coordinates[locations[k]]) / 100)
            position_y = (float(y_coordinates[locations[k]]) / 100)
            comp_angle = float(angle[locations[k]])
            if comp_angle == 270:
                comp_angle = -90

            gcode_generate(None, None, None, State.GO_TO_FEEDER)  # GO TO FEEDER POSITION
            gcode_generate(None, None, None, State.PICK_UP)  # PICKUP THE COMPONENT
            gcode_generate(None, None, None, State.GO_TO_CAMERA)  # GO TO CAMERA POSITION
            gcode_generate(None, None, comp_angle, State.ANGLE_CORRECTION)
            # this is not actually a correction. Initially set component angle to its necessary value.

            is_center_ready = 0
            is_angle_ready = 0
            while 1:
                data = None
                while data is None:
                    data = visual()

                center_x = data[0]
                center_y = data[1]
                current_angle = float(data[2])
                if (220 < center_x < 260) and (220 < center_y < 260):
                    is_center_ready = 1
                if abs(current_angle) < 1 or 44 < abs(current_angle) < 46:
                    is_angle_ready = 1

                pixel2mm = 15
                # this value must be calculated during laboratory tests. It is the definition of the ratio
                # of the conversion between pixel values and milimeter. It depends on the Z-axis height.
                if is_center_ready is not 1:
                    correction_x = (DEFINED_CENTER[0] - float(center_x)) / pixel2mm
                    correction_y = (DEFINED_CENTER[1] - float(center_y)) / pixel2mm
                    gcode_generate(correction_x, correction_y, 0, State.CAMERA_ADJUST)
                    change_x += correction_x
                    change_y += correction_y
                if is_angle_ready is not 1:
                    correction_angle = comp_angle - current_angle
                    gcode_generate(None, None, correction_angle, State.ANGLE_CORRECTION)  # angle correction
                if is_center_ready and is_angle_ready:
                    break

            gcode_generate(position_x + change_x, position_y + change_y, None, State.PLACEMENT_LOC)  # go placement loc.
            gcode_generate(None, None, None, State.PLACE)  # PLACE THE COMPONENT


def read_gerber_htm(loc):
    # loc = input("Enter full path of gerber file: ")
    offset_x, offset_y = input("Enter board reference point:").split()
    gcode_generate(offset_x, offset_y, 0, State.SET_RELATIVE_OFFSET)
    gcode_generate(0, 0, 0, State.PLACEMENT_LOC)  # nothing to place. go to reference point.(WPos = '0,0,0')
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
    del angles[0]   # angles read from gerber file
    type_names = []
    type_names = list(type_names)
    type_names.append(components[0])    # add first component to type list.

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


def read_gerber(loc):

    offset_x, offset_y = input("Enter board reference point:").split()
    gcode_generate(offset_x, offset_y, 0, State.SET_RELATIVE_OFFSET)
    gcode_generate(0, 0, 0, State.PLACEMENT_LOC)  # nothing to place. go to reference point.(WPos = '0,0,0')
    f = open(loc, "r")
    count = 0
    foundat = 0

    x_coordinates, y_coordinates, angles, components, mylist = [], [], [], [], []

    for lines in f.readlines():
        mylist.append(lines)
        count += 1
        if "REFDES" in lines:
            foundat = count
    f.close()
    for i in range(foundat):
        del mylist[0]

    for lines in mylist:
        comp = lines.split(',')
        x_coordinates.append(comp[len(comp) - 4])
        y_coordinates.append(comp[len(comp) - 3])
        angles.append(comp[len(comp) - 2])
        components.append(comp[1])
    row = len(components)
    type_names = []
    type_names = list(type_names)
    type_names.append(components[0])    # add first component to type list.

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


def act_serial(port):
    global s
    select = input("Select device: ")
    serial_address = port[int(select)-1]
    baudrate = 115200
    baud_change = input("Enter Baudrate. Default is (115200). Do you want to change?(y/n) : ")
    if baud_change.lower() == 'y':
        baudrate = input("New baudrate: ")
    try:
        s = serial.Serial(serial_address, baudrate)  # connect to controller
    except serial.serialutil.SerialException:
        print("Connection failed.")
        return 0

    print("Connection established.")
    s.write("\r\n\r\n".encode())  # Wake up grbl
    time.sleep(2)  # A few seconds is necessary for grbl until it accepts commands.


def start():
    ports = []
    iterator = comports(include_links='s')
    print("Device(s) found at port(s):")
    count = 0
    for n, (port, desc, hwid) in enumerate(iterator):
        count += 1
        string = 'wmic path CIM_LogicalDevice where \"Caption like \'%'+port+"%\'\" get caption"
        x = subprocess.check_output(string, shell=True)
        x = str(x)
        x = x.split('\\r\\r\\n')
        print("%d: %s" % (count, x[1]))
        ports.append(port)

    while act_serial(ports) == 0:
        print("Check your device path.")

    loc = input("Enter the centroid file path: ")
    if ".htm" in loc:
        read_gerber_htm(loc)
    else:
        read_gerber(loc)


start()
