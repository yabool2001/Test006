import datetime
from os import system
import time
import serial

# import sys
# sys.setdefaultencoding('utf-8')

log_file_name = 'serials.log'
data_file_name = 'data.txt'
conf_file_name = 'mmw_pplcount_demo_default.cfg'
data_com_delta_seconds = 10

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
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file is writable.' )
except IOError as e :
    print ( f'{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file opening problem... {str(e)}' )
try:
    data_file = open ( data_file_name , 'a' , encoding='utf-8' )
    if data_file.writable() :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file.name} file is writable.' )
except IOError as e :
    print ( f'{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file.name} file opening problem... {str(e)}' )

################################################################
###################### KONFIGURACJA CHIRP ######################
################################################################

#### Otwieranie pliku z konfiguracją chirp
try:
    with open ( f'{conf_file_name}' , 'r' , encoding='utf-8' ) as conf_file:
        if conf_file.readable () :
            log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_file.name} file is readable.' )
        cfg = conf_file.readlines()
except IOError as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_file.name} file opening problem... {str(e)}' )

#### Otwieranie portu CONF COM do konfiguracji
try: 
    conf_com.open ()
    if conf_com.is_open :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port opened.' )
        conf_com.reset_output_buffer()
    #### Wysyłanie konfiguracji chirp do portu CONF COM
    for line in cfg :
        time.sleep(.1)
        conf_com.write ( line.encode () )
        ack = conf_com.readline ()
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
        ack = conf_com.readline ()
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
        time.sleep ( 3 )
        conf_com.reset_input_buffer ()
except serial.SerialException as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port error opening: {str(e)}' )

#### Zamykanie portu CONF COM do konfiguracji
if conf_com.is_open :
    try:
        conf_com.close ()
        if not conf_com.is_open :
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

#time_up = datetime.datetime.utcnow () + datetime.timedelta ( seconds = data_com_delta_seconds )
#while datetime.datetime.utcnow () < time_up :
    # data_line = data_com.readline ()[:-1] # [:-1] czyli bez znaku końca linii z powodu, któego by nie działał decode()
    # data_file.write ( data_line.decode () )
    
    # Jedna z wersji odczytująca dane ale generująca błędy podczas decode()
    # data_line = data_com.readline ()
    # data_file.write ( str ( data_line ) )
    
    # Wersja alternatywna odczytująca dane ale nie po linii tylko po jednym bajcie, zeby sprawdzić czy zadziała funkcja decode()
data_byte = data_com.read ( 4666 )
data_file.write ( str ( data_byte ) )
    #data_file.write ( data_byte.decode() )


try:
    data_com.close ()
except serial.SerialException as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port error closing: {str(e)}' )
if not data_com.is_open :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port closed.' )


#### Zamykanie pliku z logami i pliku z danymi ####
try:
    data_file.close ()
    if data_file.closed :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file.name} file is closed.' )
except IOError as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file.name} file closing problem... {str(e)}' )


# Zamykanie plików z logami powinno być zawsze na samym końcu programu
log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file closing...' )
try:
    log_file.close ()
    if log_file.closed :
        print ( f'{log_file.name} file is closed.' )
except IOError as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file closing problem... {str(e)}' )
    print ( f'{log_file.name} file closing problem... {str(e)}' )