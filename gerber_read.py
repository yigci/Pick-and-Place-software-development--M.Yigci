import pandas as pd
import numpy as np

def read_gerber():

    loc = "C:/Users/muham/Desktop/XY-coordinates.htm"
#    loc = input("Enter full path of gerber file: ")

    table = pd.read_html(loc)
    table = table[0]

    dimension = np.shape(table)
#   column = dimension[1]
    row = dimension[0]-1
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

    for i in range(len(type_names)):
        locations = indx_list[i]
        print("Picking: %s" % type_names[i])
        for k in range(len(locations)):
            print("Coordinates: %4d-%4d \t Angle: %3d" % (int(float(x_coordinates[locations[k]])),
                                                  int(float(y_coordinates[locations[k]])),
                                                  int(float(angles[locations[k]]))))

read_gerber()