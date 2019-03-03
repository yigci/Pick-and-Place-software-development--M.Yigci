import pandas as pd
import numpy as np
import camera
import serial_grbl
import time
from serial_grbl import send_gcode, act_serial

CAMERA_POSITION = [100, 200]
FEEDER_POSITION = [100, 100]
DEFINED_CENTER = [360, 360]


def gcode_generate(x, y, angle, statement):

    with open('gcode.txt', "r") as f:
        f.read()
    myfile = open('gcode.txt', "w")

    if statement == 0:  # Move to feeder position
        myfile.write("G01 X%s Y%s F5000\n" % (str(FEEDER_POSITION[0]), str(FEEDER_POSITION[1])))
        myfile.close()
        send_gcode('gcode.txt')

    elif statement == 1:    # pick or place sequence
        myfile.write("G17 G21 G90 \nG00 Z10 \nM08 \nG00 Z20.\n")
        myfile.close()
        serial_grbl.send_gcode('gcode.txt')

    elif statement == 2:    # move to camera position
        myfile.write("G01 X%s Y%s F5000\n" % (str(CAMERA_POSITION[0]), str(CAMERA_POSITION[1])))
        myfile.close()
        serial_grbl.send_gcode('gcode.txt')

    elif statement == 3:    # Camera position adjustments
        myfile.write("G00 X%s Y%s \n" % (str(x), str(y)))  # incremental mode should be used.
        myfile.close()
        serial_grbl.send_gcode('gcode.txt')

    elif statement == 4:    # Camera position adjustments
        myfile.write("G01 X%s Y%s F5000\n" % (str(x), str(y)))  # absolute movement to placement location
        myfile.close()
        serial_grbl.send_gcode('gcode.txt')


def component_handle(feeder, indx, angle, x_coordinates, y_coordinates):

    for i in range(len(feeder)):
        locations = indx[i]
        print("Picking: %s" % feeder[i])
        for k in range(len(locations)):
            center_x, center_y, change_x, change_y = 0, 0, 0, 0
            position_x = (float(x_coordinates[locations[k]]) / 100)
            position_y = (float(y_coordinates[locations[k]]) / 100)
            gcode_generate(0, 0, 0, 0)
            time.sleep(10)
            gcode_generate(0, 0, 0, 1)  # PICKUP THE COMPONENT
            time.sleep(10)
            gcode_generate(0, 0, 0, 2)  # GO TO CAMERA POSITION
            time.sleep(10)
            while ((60 < center_x < 7000) and (35 < center_y < 4500)) is False:
                data = None
                while data is None:
                    data = camera.visual()
                center_x = data[0]
                center_y = data[1]
                # current_angle = data[2]

                print(center_x, center_y)
                gcode_generate((DEFINED_CENTER[0]-center_x), (DEFINED_CENTER[1]-center_y), 0, 3)
                time.sleep(10)
                change_x += (DEFINED_CENTER[0]-float(center_x))
                change_y += (DEFINED_CENTER[1]-float(center_y))

            gcode_generate(position_x, position_y, 0, 4)
            time.sleep(10)
            gcode_generate(0, 0, 0, 1)
            time.sleep(10)


def read_gerber():

    loc = "C:/Users/muham/Desktop/XY-coordinates.htm"
    table = pd.read_html(loc)
    table = table[0]
##
#   X-coordinates are in column 5
#   Y-coordinates are in column 6
#   Angles are in column 7
#   Mirror in colum 8
#   names are in column 1
##
    dimension = np.shape(table)
#   column = dimension[1]
    row = (dimension[0]-1)
    x_coordinates = table[5]
    y_coordinates = table[6]
    angles = table[7]
    components = table[1]
    components = list(components)
    del components[0]
    type_names = []
    type_names = list(type_names)

    for i in range(row):
        is_new = 1
        if i is 0:
            type_names.append(components[i])
        else:
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
                indx.append(r+1)
        indx_list.append(indx)
#   for i in range(len(type_names)):
#      locations = indx_list[i]
#      print("Picking: %s" % type_names[i])
#     for k in range(len(locations)):
#     print("Coordinates: %4d-%4d \t Angle: %3d" % (int(float(x_coordinates[locations[k]])),
#                                                   int(float(y_coordinates[locations[k]])),
#                                                   int(float(angles[locations[k]]))))

    component_handle(type_names, indx_list, angles, x_coordinates, y_coordinates)
    return type_names, indx_list, angles, x_coordinates, y_coordinates


act_serial()
read_gerber()
