string = 'wmic path CIM_LogicalDevice where \"Caption like \'%' + "asd" + "%\'\" get caption"
print(string)