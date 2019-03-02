import pandas as pd
import numpy as np

CAMERA_POSITION = [100, 200]
FEEDER_POSITION = [100, 100]


def create_gcode(feeder, indx, angle, x_coordinates, y_coordinates):

    reading = open("center_info.txt", "r+")
    #   (Acquire information from camera. Coordinates should be written into this file by camera script)
    data_file = reading.read()
    print(data_file)
    data_file = data_file.replace('[', '')
    data_file = data_file.replace(']', '')
    temp = data_file.split(",")
    input_data = []

    for i in range(len(temp)):
        input_data.append(int(float(temp[i])))
    center_x = input_data[0]
    center_y = input_data[1]
    current_angle = input_data[2]
    print(center_x, center_y, current_angle)
########################################################################################################################

    for i in range(len(feeder)):
        locations = indx[i]
#       =======> go to feeder location. If many, make gcode creation properly.
        # test #
        with open('feeder_loc.txt', "r") as f:
            f.read()
        myfile = open('feeder_loc.txt', "w")
        myfile.write("G17 G21 G90 G94\nG00 X%s Y%s" % (str(FEEDER_POSITION[0]), str(FEEDER_POSITION[1])))
        # Send created Gcode via Serial connection
        # test #
        print("Picking: %s" % feeder[i])
#       =======> Gcode for picking up the element.
#       =======> Go to camera position and make necessary corrections.(add each correction move. Total value will be
#       added to placement location.)
        for k in range(len(locations)):
            with open('gcode.txt', "r") as f:
                f.read()
            myfile = open('gcode.txt', "w")
            myfile.write("G17 G21 G90 G94\nG01 X%s Y%s" % (str(int(float(x_coordinates[locations[k]]))),
                                                           str(int(float(y_coordinates[locations[k]])))))
            myfile.close()
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
    for i in range(len(type_names)):
        locations = indx_list[i]
        print("Picking: %s" % type_names[i])
        for k in range(len(locations)):
            print("Coordinates: %4d-%4d \t Angle: %3d" % (int(float(x_coordinates[locations[k]])),
                                                          int(float(y_coordinates[locations[k]])),
                                                          int(float(angles[locations[k]]))))

    create_gcode(type_names, indx_list, angles, x_coordinates, y_coordinates)
    return type_names, indx_list, angles, x_coordinates, y_coordinates


read_gerber()
