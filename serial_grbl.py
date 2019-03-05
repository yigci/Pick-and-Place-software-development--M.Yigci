import serial
import time

s = None


def act_serial():
    global s
    s = serial.Serial('COM4', 115200)   # connect to controller
    print("Connection established.")
    s.write("\r\n\r\n".encode())        # Wake up grbl
    time.sleep(2)                       # A few seconds is necessary for grbl until it accepts commands.

def send_gcode(address):

    f = open(address, 'r')
    s.flushInput()  # Flush startup text in serial input

    for line in f:
        code = line.strip()  # Strip all EOL characters for streaming
        print('Sending: ' + code)
        s.write((code + "\n").encode())  # Send g-code block to grbl
        grbl_out = s.readline()  # Wait for grbl response with carriage return
        print(' : ' + grbl_out.strip().decode())
        ret = grbl_out.strip().decode()
        if ret != "Sent":
            print("GCode is not sent. An error occurred. Terminating program")
            return 0
    time.sleep(1)
    print("Transmission finished.")
    f.close()

    return 1
