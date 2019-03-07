import pandas as pd
import numpy as np
import camera
import time
from serial_grbl import send_gcode, act_serial
from enum import Enum


class State(Enum):      # To make the program easier to understand, some of the processes assigned to numbers.
    GO_TO_FEEDER = 0
    PICK_UP = 1
    PLACE = 2
    GO_TO_CAMERA = 3
    CAMERA_ADJUST = 4
    PLACEMENT_LOC = 5


CAMERA_POSITION = [10, 0]   # Predefined constants.
FEEDER_POSITION = [50, 0]
DEFINED_CENTER = [360, 360]


def gcode_generate(x, y, angle, statement):

    with open('gcode.txt', "r") as f:      # Code between line 26-28 is to clear the gcode.txt file.
        f.read()
    command_file = open('gcode.txt', "w")

    if statement == State.GO_TO_FEEDER:    # Move to feeder position
        command_file.write("X%s Y%s \n" % (str(FEEDER_POSITION[0]), str(FEEDER_POSITION[1])))  # write new gcode to the file.
        command_file.close()                     # close file for next step.
        send_gcode('gcode.txt')            # Send gcode to the controller.

    elif statement == State.PICK_UP:       # pick up
        command_file.write("Z10 \nM08 \nZ20. \n")
        command_file.close()
        send_gcode('gcode.txt')

    elif statement == State.PLACE:         # place
        command_file.write("Z10 \nM09 \nZ20. \n")
        command_file.close()
        send_gcode('gcode.txt')

    elif statement == State.GO_TO_CAMERA:  # GO TO CAMERA
        command_file.write("X%s Y%s \n" % (str(CAMERA_POSITION[0]), str(CAMERA_POSITION[1])))
        command_file.close()
        send_gcode('gcode.txt')

    elif statement == State.CAMERA_ADJUST:  # Camera position adjustments
        command_file.write("G91 \nX%s Y%s \n" % (str(x), str(y)))  # incremental mode should be used.
        command_file.close()
        send_gcode('gcode.txt')

    elif statement == State.PLACEMENT_LOC:
        command_file.write("G90 \nX%s Y%s \n" % (str(x), str(y)))  # absolute movement to placement location
        command_file.close()
        send_gcode('gcode.txt')


def component_handle(feeder, indx, angle, x_coordinates, y_coordinates):
    send_gcode('initial.txt')
    for i in range(len(feeder)):
        locations = indx[i]
        print("Picking: %s" % feeder[i])
        for k in range(len(locations)):
            center_x, center_y, change_x, change_y ,check_x, check_y = 0, 0, 0, 0, 0, 0
            position_x = (float(x_coordinates[locations[k]]) / 100)
            position_y = (float(y_coordinates[locations[k]]) / 100)
            gcode_generate(0, 0, 0, State.GO_TO_FEEDER)  # GO TO FEEDER POSITION
            gcode_generate(0, 0, 0, State.PICK_UP)       # PICKUP THE COMPONENT
            gcode_generate(0, 0, 0, State.GO_TO_CAMERA)  # GO TO CAMERA POSITION
            time.sleep(1)
            while (check_x and check_y) is 0:
                data = None
                while data is None:
                    check_x = 0
                    check_y = 0
                    data = camera.visual()
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

    loc = "C:/Users/muham/Desktop/XY-coordinates.htm"
#    loc = input("Enter full path of gerber file: ")

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
 #   return type_names, indx_list, angles, x_coordinates, y_coordinates


act_serial()
read_gerber()
