import datetime
import json
from os import error, system
import time
import serial
import struct
import sys

# import sys
# sys.setdefaultencoding('utf-8')

log_file_name           = 'serials.log'
data_file_name          = 'data.txt'
conf_file_name          = 'chirp_cfg/mmw_pplcount_demo_default.cfg'
# conf_file_name = 'chirp_cfg/sense_and_direct_68xx.cfg'
# conf_file_name = 'chirp_cfg/long_range_people_counting.cfg'
conf_com                = serial.Serial ()
data_com                = serial.Serial ()
conf_com.port           = 'COM4'
data_com.port           = 'COM3'
# Chose from Device manager: Silicon Labs Dual CP2105 USB to UART Bridge: Standard COM Port 
conf_com.baudrate       = 115200
data_com.baudrate       = 921600
conf_com.bytesize       = serial.EIGHTBITS
data_com.bytesize       = serial.EIGHTBITS
conf_com.parity         = serial.PARITY_NONE
data_com.parity         = serial.PARITY_NONE
conf_com.stopbits       = serial.STOPBITS_ONE
data_com.stopbits       = serial.STOPBITS_ONE
conf_com.timeout        = 0.3
data_com.timeout        = 0.025
conf_com.write_timeout  = 1

data_com_delta_seconds = 10

class Sense_and_detect_hvac_control_frame_data :
    def __init__ ( self , frame_data ) :
        self.frame_data = frame_data
        self.control = 506660481457717506
        self.frame_header_struct = 'Q10I2H'
        self.frame_header_length = struct.calcsize ( self.frame_header_struct )
        self.tlv_header_struct = '2I'
        self.tlv_header_length = struct.calcsize ( self.tlv_header_struct )
        self.pointcloud_unit_struct = '4f'
        self.pointcloud_unit_length = struct.calcsize ( self.pointcloud_unit_struct )
        self.point_struct = '2B2h'
        self.point_length = struct.calcsize ( self.point_struct )
        self.data = dict ()

    # Zdekodowanie wszystkich punktów z ramki zaczynającej się od Punktów
    # Zapisanie punktów do dict, zapisanie słownika do pliku i skasowanie słownika
    # Usunięcie Punktu z ramki w każdej iteracji
    def get_points_data ( self ) :
        points_number = int ( ( self.tlv_length - self.pointcloud_unit_length ) / self.point_length ) # 
        for j in range ( points_number ) :
            try :
                azimuth_point , doppler_point , range_point , snr_point = struct.unpack ( self.point_struct , self.frame_data[:self.point_length] )
                point_ok = True
            except struct.error as e :
                data_file.write ( f'\nPoint parse failed! {e}' )
                point_ok = False
            if point_ok :
                # Zapisz punkt
                point = dict ( azimuth_point = azimuth_point , doppler_point = doppler_point , range_point = range_point , snr_point = snr_point )
                data_file.write ( f'\n{point}' )
                del point
                self.frame_data = self.frame_data[self.point_length:]
                # Tutaj skońzyłem i coś nie działa z ostatnim punktem

    # Zdekodowanie chmury punktów z ramki zaczynającej się od chmury punktów
    # Zapisanie chmury punktów do dict, zapisanie słownika do pliku i skasowanie słownika
    # Usunięcie chmury punktów z ramki
    def get_pointcloud_unit_data ( self ) :
        try :
            azimuth_unit , doppler_unit , range_unit , snr_unit = struct.unpack ( self.pointcloud_unit_struct , self.frame_data[:self.pointcloud_unit_length] )
            try_result = True
        except struct.error as e :
            data_file.write ( f'\nPoint cloud unit parsing failed in frame no. {self.data["frame_header_data"]["frame_number"]}! {e}' )
            try_result = False
        if try_result :
            # Zapisz Point Cloud Unit
            pointcloud_unit = dict ( azimuth_unit = azimuth_unit , doppler_unit = doppler_unit , range_unit = range_unit, snr_unit = snr_unit )
            self.data ["pointcloud_unit"] = pointcloud_unit
            del pointcloud_unit
            self.frame_data = self.frame_data[self.pointcloud_unit_length:]
            # self.get_points ()

    # Rozpakuj i zapisz dane z nagłówka TLV Header
    def get_tlv_header_data ( self ) :
        for i in range ( self.data["frame_header_data"]["num_tlvs"] ) :
            try:
                tlv_type, tlv_length = struct.unpack ( self.tlv_header_struct , self.frame_data[:self.tlv_header_length] )
                try_result = True
            except struct.error as e :
                data_file.write ( f'\nTLV header parsing failed! {e}' )
                try_result = False
            if try_result :
                # Zapisz TLV header
                tlv_header = dict ( tlv_type = tlv_type , tlv_length = tlv_length )
                self.data ["tlv_header"] = tlv_header
                del tlv_header
                self.frame_data = self.frame_data[self.tlv_header_length:]
                if self.data["tlv_header"]["tlv_type"] == 6 :
                    self.get_pointcloud_unit_data ()
                    pass
                else :
                    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} Check it out! Frame no. {self.data["frame_header_data"]["frame_number"]} contain alter TLV type {tlv_type}' )
    
    # Rozpakuj i zapisz dane z Frame header
    def get_frame_header_data ( self ) :
        try:
            sync , version , platform , timestamp , packet_length , frame_number , subframe_number , chirp_margin , frame_margin , uart_sent_time , track_process_time , num_tlvs , checksum = struct.unpack ( self.frame_header_struct , self.frame_data[:self.frame_header_length] )
            try_result = True
        except struct.error as e :
            data_file.write ( f'\nFrame header parse failed! {e}' )
            try_result = False
        if try_result and sync == self.control :
            # Zapisz frame header
            frame_header_data = dict ( sync = sync , version = version , platform = platform , timestamp = timestamp , packet_length = packet_length , frame_number = frame_number , subframe_number = subframe_number , chirp_margin = chirp_margin , frame_margin = frame_margin , uart_sent_time = uart_sent_time , track_process_time = track_process_time , num_tlvs = num_tlvs , checksum = checksum )
            self.data ["frame_header_data"] = frame_header_data
            del frame_header_data
            self.frame_data = self.frame_data[self.frame_header_length:]
        else :
            log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} Check it out! Frame no. {frame_number} contain alter sync {sync}' )
    
    # Get frame data from frame_data to self dict
    def get_frame_data ( self ) :
        self.get_frame_header_data ()
        if self.data["frame_header_data"]["num_tlvs"] :
            self.get_tlv_header_data ()
            data_file.write ( f'\n{self.data}' )
        else :
            data_file.write ( f'\n{self.data["frame_header_data"]["num_tlvs"]} TLVs in frame no. {self.data["frame_header_data"]["frame_number"]}' )
                        
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
        frame_data = data_com.read ( 4666 )
        if frame_data :
            hvac = Sense_and_detect_hvac_control_frame_data ( frame_data )
            hvac.get_frame_data ()
        else :
            log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} Frame is empty!' )
            time.sleep(.2)
            data_com.reset_output_buffer ()
            data_com.reset_input_buffer ()
            
try:
    data_com.close ()
except serial.SerialException as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port error closing: {str(e)}' )
if not data_com.is_open :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port closed.' )


#### Zamykanie pliku z danymi ####
try:
    data_file.close ()
    if data_file.closed :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file.name} file is closed.' )
except IOError as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file.name} file closing problem... {str(e)}' )

#### Zatrzymanie pracy radaru i zamykanie portu CONF COM do konfiguracji
# Zatrzymanie pracy sensora
# conf_com.write ( 'sensorStop\n'.encode () )
# ack = conf_com.readline ()
# log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
# ack = conf_com.readline ()
# log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
# time.sleep ( 3 )
# conf_com.reset_input_buffer ()
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

# Zamykanie plików z logami powinno być zawsze na samym końcu programu
log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file closing...' )
try:
    log_file.close ()
    if log_file.closed :
        print ( f'{log_file.name} file is closed.' )
except IOError as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file closing problem... {str(e)}' )
    print ( f'{log_file.name} file closing problem... {str(e)}' )