import pandas as pd
import numpy as np
import camera
import serial_grbl
import time

CAMERA_POSITION = [100, 200]
FEEDER_POSITION = [100, 100]


def gcode_generate(x, y, angle, statement):
    with open('gcode.txt', "r") as f:
        f.read()
    myfile = open('gcode.txt', "w")

    if statement == 0:
        myfile.write("G00 X%s Y%s \n" % (str(FEEDER_POSITION[0]), str(FEEDER_POSITION[1])))
        myfile.close()
        serial_grbl.send_gcode('gcode.txt')  # pick up the component. Code is not real. Needs to be created properly.

    elif statement == 1:
        myfile.write("G17 G21 G90 \nG00 Z10 \nM08 \nG00 Z20.\n")
        myfile.close()
        serial_grbl.send_gcode('gcode.txt')  # pick up the component. Code is not real. Needs to be created properly.

    elif statement == 2:
        myfile.write("G00 X%s Y%s \n" % (str(CAMERA_POSITION[0]), str(CAMERA_POSITION[1])))
        myfile.close()
        serial_grbl.send_gcode('gcode.txt')  # pick up the component. Code is not real. Needs to be created properly.

    elif statement == 3:
        myfile.write("G00 X%s Y%s \n" % (str(x), str(y)))
        myfile.close()
        serial_grbl.send_gcode('gcode.txt')  # pick up the component. Code is not real. Needs to be created properly.


def component_handle(feeder, indx, angle, x_coordinates, y_coordinates):
    data = None
    while data is None:
        data = camera.visual()
    center_x = data[0]
    center_y = data[1]
    current_angle = data[2]
    # ----------------------------------------------------------------------------------------------------
    check = serial_grbl.send_gcode('feeder_loc.txt')

    if check is not 1:
        print("An error occured in GCode sending script.")

    position_x = FEEDER_POSITION[0]
    position_y = FEEDER_POSITION[1]

    for i in range(len(feeder)):
        # gcode_generate(0, 0, 0, 0)
        locations = indx[i]
        print("Picking: %s" % feeder[i])
        # ******      # gcode_generate(0, 0, 0, 1)
        # with open('gcode.txt', "r") as f:
        #     f.read()
        #
        # myfile = open('gcode.txt', "w")
        # myfile.write("G17 G21 G90 \nG00 Z10 \nM08 \nG00 Z20.\n")
        # myfile.close()
        # serial_grbl.send_gcode('gcode.txt')  # pick up the component. Code is not real. Needs to be created properly.
        #       =======> Go to camera position and make necessary corrections.(add each correction move. Total value will be
        #       added to placement location.)
        for k in range(len(locations)):
            with open('gcode.txt', "r") as f:
                f.read()

            myfile = open('gcode.txt', "w")
            position_x = (float(x_coordinates[locations[k]]) / 100)
            position_y = (float(y_coordinates[locations[k]]) / 100)
            myfile.write("G00 X%s Y%s \n" % (str(position_x), str(position_y)))
            myfile.close()
            serial_grbl.send_gcode('gcode.txt')
            with open('gcode.txt', "r") as f:
                f.read()
            time.sleep(1)
            myfile = open('gcode.txt', "w")
            myfile.write("G00 Z10 M08 \nG00 Z0.\n")
            myfile.close()
            serial_grbl.send_gcode('gcode.txt')


#           ======> Go to placement location.
#           ======> Place the component.


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
    row = (dimension[0] - 1)
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
                indx.append(r + 1)
        indx_list.append(indx)
    # for i in range(len(type_names)):
    #    locations = indx_list[i]
    # print("Picking: %s" % type_names[i])
    #    for k in range(len(locations)):
    #  print("Coordinates: %4d-%4d \t Angle: %3d" % (int(float(x_coordinates[locations[k]])),
    #                          int(float(y_coordinates[locations[k]])),
    #                                                          int(float(angles[locations[k]]))))

    component_handle(type_names, indx_list, angles, x_coordinates, y_coordinates)
    return type_names, indx_list, angles, x_coordinates, y_coordinates


read_gerber()
