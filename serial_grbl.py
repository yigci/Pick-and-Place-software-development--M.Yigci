import serial
import time


def send_gcode(address):
    s = serial.Serial('COM4', 115200)
    f = open(address, 'r')

    # Wake up grbl
    s.write("\r\n\r\n".encode())
    time.sleep(2)  # Wait for grbl to initialize
    s.flushInput()  # Flush startup text in serial input

    for line in f:
        code = line.strip()  # Strip all EOL characters for streaming
        print('Sending: ' + code)
        s.write((code + "\n").encode())  # Send g-code block to grbl
        grbl_out = s.readline()  # Wait for grbl response with carriage return
        print(' : ' + grbl_out.strip().decode())

    print("Transmission finished.")
    f.close()

    return 1
