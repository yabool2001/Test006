import datetime
import time
import serial

conf_file_name = 'mmw_pplcount_demo_default.cfg'

conf_com = serial.Serial ()
data_com = serial.Serial ()
conf_com.port = 'COM4'
data_com.port = 'COM3'
# Chose from Device manager: Silicon Labs Dual CP2105 USB to UART Bridge: Standard COM Port 
conf_com.baudrate = 115200
data_com.baudrate = 921600
conf_com.bytesize = serial.EIGHTBITS
data_com.bytesize = serial.EIGHTBITS
conf_com.parity = serial.PARITY_NONE
data_com.parity = serial.PARITY_NONE
conf_com.stopbits = serial.STOPBITS_ONE
data_com.stopbits = serial.STOPBITS_ONE
conf_com.timeout = 0.3
data_com.timeout = 0.025
conf_com.write_timeout = 1

try: 
    conf_com.open ()
except serial.SerialException as e:
    print ( f'error opening {conf_com.name}: {str(e)}' )
if conf_com.is_open:
    print ( f'{conf_com.name} opened' )
    conf_com.reset_output_buffer()
try:
    conf_com.close ()
except serial.SerialException as e:
    print ( f'error closing {conf_com.name}: {str(e)}' )
if not conf_com.is_open:
    print ( f'{conf_com.name} closed' )

#### Otwórz CONF COM i wyślij konfigurację ####

# Otwórz plik z konfiguracją #
with open ( f'{conf_file_name}' , 'r' , encoding='utf-8' ) as conf_file:
    cfg = conf_file.readlines()

try: 
    data_com.open ()
except serial.SerialException as e:
    print ( "error open serial port: " + str ( e ) )
if data_com.is_open:
    print ( f'{data_com.name} opened' )
    data_com.reset_output_buffer()
    try:
        data_com.write ( str.encode ( f'UTC {time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec}\r\n' ) ) 
    except serial.SerialTimeoutException as e:
        print ( f'error write {data_com.name}: {str(e)}' )

time_up = datetime.datetime.utcnow () + datetime.timedelta ( seconds = 10 )
while datetime.datetime.utcnow () < time_up :
    com7_line = data_com.readline ()
    print ( com7_line )

try:
    data_com.close ()
except serial.SerialException as e:
    print ( f'error close {data_com.name}: {str(e)}' )
if not data_com.is_open:
    print ( f'{data_com.name} closed' )
