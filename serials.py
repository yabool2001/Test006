import datetime
import time
import serial

ser = serial.Serial ()
ser.port = 'COM3'
# Chose from Device manager: Silicon Labs Dual CP2105 USB to UART Bridge: Standard COM Port 
ser.baudrate = 921600
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.timeout = 1
ser.write_timeout = 1

try: 
    ser.open ()
except serial.SerialException as e:
    print ( "error open serial port: " + str ( e ) )
if ser.is_open:
    print ( f'{ser.name} opened' )
    try:
        ser.write ( str.encode ( f'UTC {time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec}\r\n' ) ) 
    except serial.SerialTimeoutException as e:
        print ( f'error write {ser.name}: {str(e)}' )

time_up = datetime.datetime.utcnow () + datetime.timedelta ( seconds = 600 )
while datetime.datetime.utcnow () < time_up :
    com7_line = ser.readline ()
    print ( com7_line )

try:
    ser.close ()
except serial.SerialException as e:
    print ( f'error close {ser.name}: {str(e)}' )
if not ser.is_open:
    print ( f'{ser.name} closed' )
