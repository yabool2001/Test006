import serial

ser = serial.Serial (
    port = 'COM4', \
    baudrate = 9600, \
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0 )
