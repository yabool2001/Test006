import datetime
import time
import serial

log_file_name = 'serials.log'
data_file_name = 'data.txt'
conf_file_name = 'mmw_pplcount_demo_default.cfg'
data_com_delta_seconds = 2

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

#### Otwieranie pliku z logami i pliku z danymi ####
try:
    log_file = open ( log_file_name , 'a' , encoding='utf-8' )
    if log_file.writable() :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file_name} file is writable.' )
except IOError as e:
    print ( f'{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file_name} file opening problem... {str(e)}' )
try:
    data_file = open ( data_file_name , 'a' , encoding='utf-8' )
    if data_file.writable() :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file_name} file is writable.' )
except IOError as e:
    print ( f'{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file_name} file opening problem... {str(e)}' )

################################################################
###################### KONFIGURACJA CHIRP ######################
################################################################

#### Otwieranie pliku z konfiguracją chirp
try:
    with open ( f'{conf_file_name}' , 'r' , encoding='utf-8' ) as conf_file:
        if conf_file.readable () :
            log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_file_name} file is readable.' )
        cfg = conf_file.readlines()
except IOError as e:
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_file_name} file opening problem... {str(e)}' )

#### Otwieranie portu CONF COM do konfiguracji
try: 
    conf_com.open ()
    if conf_com.is_open:
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port opened.' )
        conf_com.reset_output_buffer()
    #### Wysyłanie konfiguracji chirp do portu CONF COM
    for line in cfg:
        time.sleep(.1)
        conf_com.write ( line.encode () )
        ack = conf_com.readline ()
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
        ack = conf_com.readline ()
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
        time.sleep ( 3 )
        conf_com.reset_input_buffer ()
except serial.SerialException as e:
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port error opening: {str(e)}' )

#### Zamykanie portu CONF COM do konfiguracji
if conf_com.is_open:
    try:
        conf_com.close ()
        if not conf_com.is_open:
            log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port closed.' )
    except serial.SerialException as e:
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port error closing: {str(e)}' )
else:
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port closed.' )

################################################################
################################################################
################################################################

################################################################
######################## ODBIÓR DANYCH #########################
################################################################
try: 
    data_com.open ()
except serial.SerialException as e:
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port error opening: {str(e)}' )
if data_com.is_open:
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port opened' )
    #data_com.reset_output_buffer()
    #try:
    #    data_com.write ( str.encode ( f'UTC {time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec}\r\n' ) ) 
    #except serial.SerialTimeoutException as e:
    #    print ( f'error write {data_com.name}: {str(e)}' )

time_up = datetime.datetime.utcnow () + datetime.timedelta ( seconds = data_com_delta_seconds )
while datetime.datetime.utcnow () < time_up :
    com7_line = data_com.readline ()
    data_file.write ( com7_line.decode () )
    #print ( com7_line )

try:
    data_com.close ()
except serial.SerialException as e:
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port error closing: {str(e)}' )
if not data_com.is_open:
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port closed.' )


#### Zamykanie pliku z logami i pliku z danymi ####
log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file_name} file closing...' )
try:
    log_file.close ()
except IOError as e:
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file_name} file closing problem... {str(e)}' )
    print ( f'{log_file_name} file closing problem... {str(e)}' )
if log_file.closed :
    print ( f'{log_file_name} file is closed.' )

log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file_name} file closing...' )
try:
    data_file.close ()
except IOError as e:
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file_name} file closing problem... {str(e)}' )
    print ( f'{data_file_name} file closing problem... {str(e)}' )
if data_file.closed :
    print ( f'{data_file_name} file is closed.' )