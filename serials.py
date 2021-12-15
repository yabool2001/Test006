import datetime
import json
from os import system
import time
import serial
import struct
import sys

# import sys
# sys.setdefaultencoding('utf-8')

log_file_name = 'serials.log'
data_file_name = 'data.txt'
conf_file_name = 'chirp_cfg/mmw_pplcount_demo_default.cfg'
# conf_file_name = 'chirp_cfg/sense_and_direct_68xx.cfg'
# conf_file_name = 'chirp_cfg/long_range_people_counting.cfg'
data_com_delta_seconds = 1

hvac_control = 506660481457717506
frame_header_struct = 'Q10I2H'
frame_header_length = struct.calcsize ( frame_header_struct )
tlv_header_struct = '2I'
tlv_header_length = struct.calcsize ( tlv_header_struct )
point_cloud_unit_struct = '4f'
point_cloud_unit_length = struct.calcsize ( point_cloud_unit_struct )
point_struct = '2B2h'
point_length = struct.calcsize ( point_struct )

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
# Otwórz port danych
try: 
    data_com.open ()
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port opened' )
except serial.SerialException as e:
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port error opening: {str(e)}' )
# Odczytaj, rozpakuj i zapisz dane z portu COM danych
if data_com.is_open:
    data_com.reset_output_buffer ()
    data_com.reset_input_buffer ()
    time_up = datetime.datetime.utcnow () + datetime.timedelta ( seconds = data_com_delta_seconds )
    while datetime.datetime.utcnow () < time_up :
        # Rozpakuj i zapisz dane z nagłówka pakietu
        data_frame = data_com.read ( 4666 )
        try:
            sync , version , platform , timestamp , packet_length , frame_number , subframe_number , chirp_margin , frame_margin , uart_sent_time , track_process_time , num_tlvs , checksum = struct.unpack ( frame_header_struct , data_frame[:frame_header_length] )
            data_frame_ok = True
        except struct.error as e :
            data_file.write ( f'\nFrame header parse failed! {e}' )
            data_frame_ok = False
        if data_frame_ok and sync == hvac_control :
            # Zapisz frame header
            data_frame_header = dict ( sync = sync , version = version , platform = platform , timestamp = timestamp , packet_length = packet_length , frame_number = frame_number , subframe_number = subframe_number , chirp_margin = chirp_margin , frame_margin = frame_margin , uart_sent_time = uart_sent_time , track_process_time = track_process_time , num_tlvs = num_tlvs , checksum = checksum )
            data_file.write ( f'\n{data_frame_header}' )
            data_frame = data_frame[frame_header_length:]
            # Rozpakuj i zapisz dane z nagłówka tlv
            if num_tlvs > 0 :
                for i in range ( num_tlvs ) :
                    try:
                        tlv_type, tlv_length = struct.unpack ( tlv_header_struct , data_frame[:tlv_header_length] )
                        tlv_frame_ok = True
                    except struct.error as e :
                        data_file.write ( f'\nTlv header parse failed! {e}' )
                        tlv_frame_ok = False
                    if tlv_frame_ok :
                        # Zapisz TLV header
                        tlv_frame_header = dict ( tlv_type = tlv_type , tlv_length = tlv_length )
                        data_file.write ( f'\n{tlv_frame_header}' )
                        data_frame = data_frame[tlv_header_length:]
                        if tlv_type == 6 :
                            print ('continue here')
                            try :
                                azimuth_unit , doppler_unit , range_unit , snr_unit = struct.unpack ( point_cloud_unit_struct , data_frame[:point_cloud_unit_length] )
                                point_cloud_unit_ok = True
                            except struct.error as e :
                                data_file.write ( f'\nPoint cloud unit parse failed! {e}' )
                                point_cloud_unit_ok = False
                            if point_cloud_unit_ok :
                                # Zapisz Point Cloud Unit
                                point_cloud_unit = dict ( azimuth_unit = azimuth_unit , doppler_unit = doppler_unit , range_unit = range_unit, snr_unit = snr_unit )
                                data_file.write ( f'\n{point_cloud_unit}' )
                                data_frame = data_frame[point_cloud_unit_length:]
            else :
                data_file.write ( f'\nNo TLV!' )

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