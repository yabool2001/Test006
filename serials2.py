import datetime
import json
from os import error, system
import time
import serial
import struct
import sys
# sys.setdefaultencoding('utf-8')

global                  chirp_cfg
global                  log_file , data_file
global                  conf_com , data_com
raw_frame_bytes               = b"\x02\x01\x04\x03\x06\x05\x08\x07\x04\x00\x05\x03B\x16\n\x00\xe6\xees;\xc6\x01\x00\x00:\x00\x00\x00\x00\x00\x00\x00K\x00\x00\x00\x11J\x00\x00\xa4\x06\x00\x00\xa3\x14\x00\x00\x01\x00\x98D\x06\x00\x00\x00\x92\x01\x00\x00\x01\x00\xf0?\r\x87\xd2=\xa7\x85b=\x00\x00\x00>\x1c\x00g\x00R\x00\x1a\x00f\x00G\x00\x19\x00\x04\x00\xc1\x00\x19\x00@\x00\x9a\x01\x19\x00T\x00_\x00\x18\x00<\x00-\x00\x18\x00=\x00\x0f\x01\x18\x00>\x00\x9b\x08\x18\x00?\x00^\x0b\x18\x00U\x00\x87\x00\x17\x00V\x00b\x00\x15\x009\x00*\x00\x14\x00:\x002\x00\x12\x00N\x00\xba\x02\x12\x00O\x00N\x07\x12\x00P\x00\xf3\x03\x11\x00Q\x00P\x06\x11\x00R\x00%\x06\x11\x00S\x00S\x01\x0c\x00T\x00\x8c\x00\x0c\x00U\x00o\x00\x0c\x00V\x00+\x00\x0b\x00 \x00m\x00\x0b\x00!\x00q\x00\x08\x00M\x00\x96\x00\x07\x00A\x000\x00\x06\x00H\x00\xff\x01\x06\x00I\x00\x07\x01\x04\x00J\x00\xb8\x00\x02\x00C\x00\xdb\x00\x01\x00D\x00\x84\x1a\x00\x00E\x00\xc5\x93\x00\x00F\x00B\xe7\x00\x00o\x00\x93\x00\x00\x00p\x00\x06\x01\x00\x00G\x00\xf0\x1e\x00\x00q\x00=\x00\xfe\x00H\x00b\x02\xfc\x00#\x00\xc9\x00\xfc\x00$\x005\x01\xfc\x00%\x00s\x00\xfc\x00'\x00?\x00\xfb\x00&\x00V\x00\xfa\x00\x1a\x00\xbe\x00\xf9\x00\x18\x009\x03\xf9\x00\x19\x00x\x05\xf8\x00\x1b\x00F\x01\xf8\x00\x1c\x00?\x01\xf5\x00Q\x00\x88\x04\xf5\x00R\x00\x86\x07\xf5\x00q\x00)\x00\xf4\x00S\x00\xc0\x02\xf0\x00\x11\x00\xbf\x00\xf0\x00\x12\x00d\x00\xf0\x00W\x00*\x00\xef\x00X\x00+\x00\xee\x00\x13\x00)\x00\xeb\x00\x1d\x00V\x00\xeb\x00K\x00+\x00\xea\x00\x0c\x00B\x00\xe8\x00\x0b\x00T\x00\xe8\x00\x1e\x006\x00\xe6\x00\n\x006\x00"
raw_frame_bytes2              = b'\x02\x01\x04\x03\x06\x05\x08\x07\x04\x00\x05\x03B\x16\n\x00\x08\xde4\xc1\xf0\x01\x00\x00?E\x01\x00\x00\x00\x00\x00K\x00\x00\x00\x0bJ\x00\x00\x7f\x08\x00\x00;\x16\x00\x00\x01\x00\x17\x87\x06\x00\x00\x00\xbc\x01\x00\x00\x01\x00\xf0?\r\x87\xd2=\xa7\x85b=\x00\x00\x00>\x1c\x00R\x00\x00\x03\x1c\x00S\x00T\x01\x1a\x00c\x005\x00\x19\x00\x04\x00\xd3\x00\x18\x00d\x006\x00\x17\x00?\x00\x8b\x17\x17\x00@\x00\xb6\x05\x17\x00A\x00K\x00\x16\x00<\x002\x00\x16\x00=\x00\xff\x01\x16\x00>\x00\x87\x1a\x15\x00Z\x00/\x00\x14\x00W\x001\x00\x14\x00X\x00*\x00\x10\x001\x00:\x00\x10\x002\x00n\x00\x10\x003\x005\x00\x10\x00N\x00t\x02\x10\x00O\x00O\x04\x10\x00P\x00H\x03\x0f\x00Q\x00\xcf\x06\x0e\x00R\x00Q\x05\x0e\x00T\x00\x81\x00\r\x00S\x00p\x01\x0c\x00U\x00E\x00\x0c\x00e\x00V\x00\t\x00 \x00p\x00\t\x00!\x00\x99\x00\x04\x00I\x00\x08\x01\x03\x00H\x00~\x04\x03\x00J\x00d\x00\x01\x00C\x00F\x00\x00\x00D\x00\xab\x0c\x00\x00E\x00\x94\xfc\xff\x00F\x00\x1d\xff\xff\x00o\x00D\x00\xff\x00p\x00\x1f\x01\xfe\x00G\x00..\xfe\x00q\x00{\x00\xfd\x00H\x00\x90\x06\xfc\x00I\x00E\x01\xfb\x00\'\x006\x00\xfa\x00#\x00\xa7\x00\xfa\x00$\x00A\x01\xfa\x00%\x00\x8d\x00\xfa\x00&\x00b\x00\xf8\x00\x1a\x00\xe4\x00\xf8\x00W\x00V\x00\xf8\x00X\x00\x92\x00\xf7\x00\x18\x00\xec\x02\xf7\x00\x19\x00\xb6\x05\xf7\x00\x1b\x00\xb2\x01\xf7\x00\x1c\x00\x97\x01\xf6\x00Y\x002\x00\xf3\x00Q\x00\xb3\x03\xf3\x00R\x00\x95\x06\xf3\x00S\x00"\x03\xf3\x00o\x00+\x00\xf3\x00p\x00[\x00\xf2\x00T\x00\\\x00\xef\x00\x11\x00\xac\x01\xef\x00\x12\x00\xd2\x00\xee\x00\x10\x000\x00\xee\x00\x13\x00D\x00\xee\x00$\x00V\x05\xee\x00%\x00\t\x02\xeb\x00Y\x00F\x00\xea\x00W\x00C\x00\xea\x00X\x00s\x00\xe7\x00\\\x00,\x00'
raws                    = bytes(1)
log_file_name           = 'log.txt'
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

data_com_delta_seconds = 0.5

################################################################
############ OPEN LOG, DATA AND CHIRP CONF FILE ################
################################################################

# Open log file
try:
    log_file = open ( log_file_name , 'a' , encoding='utf-8' )
    if log_file.writable() :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file is writable.' )
except IOError as e :
    print ( f'{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file opening problem... {str(e)}' )

# Open data file
try:
    data_file = open ( data_file_name , 'a' , encoding='utf-8' )
    if data_file.writable() :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file.name} file is writable.' )
except IOError as e :
    print ( f'{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file.name} file opening problem... {str(e)}' )

# Open Chirp configuration file and read configuration to chirp_cfg
try:
    with open ( f'{conf_file_name}' , 'r' , encoding='utf-8' ) as conf_file:
        if conf_file.readable () :
            log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_file.name} file is readable.' )
        chirp_cfg = conf_file.readlines()
except IOError as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_file.name} file opening problem... {str(e)}' )

################################################################
################ OPEN CONF AND DATA COM PORTS ##################
################################################################

# Open CONF COM port
try: 
    conf_com.open ()
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port opened.' )
except serial.SerialException as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port error opening: {str(e)}' )

# Open DATA COM port
try: 
    data_com.open ()
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port opened' )
except serial.SerialException as e:
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port error opening: {str(e)}' )

################################################################
##################### CHIRP CONFIGURATION ######################
################################################################
def chirp_conf () :
    for line in chirp_cfg :
        time.sleep(.1)
        conf_com.write ( line.encode () )
        ack = conf_com.readline ()
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
        ack = conf_com.readline ()
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
        time.sleep ( 3 )
        conf_com.reset_input_buffer ()

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
        #self.frame_header_data = dict ()

    # Zdekodowanie wszystkich punktów z ramki zaczynającej się od Punktów
    # Zapisanie punktów do dict, zapisanie słownika do pliku i skasowanie słownika
    # Usunięcie Punktu z ramki w każdej iteracji
    def get_points_data ( self ) :
        print (self.data["tlv_header_data"]["tlv_length"])
        print (self.tlv_header_length)
        print (self.pointcloud_unit_length)
        print (self.point_length)
        points_number = int ( ( self.data["tlv_header_data"]["tlv_length"] - self.tlv_header_length - self.pointcloud_unit_length ) / self.point_length ) # 
        for j in range ( points_number ) :
            try :
                azimuth_point , doppler_point , range_point , snr_point = struct.unpack ( self.point_struct , self.frame_data[:self.point_length] )
                try_result = True
            except struct.error as e :
                data_file.write ( f'\nPoint parse failed! {e}' )
                try_result = False
            if try_result :
                # Zapisz punkt
                point = { "point" : { "azimuth_point" : azimuth_point , "doppler_point" : doppler_point , "range_point" : range_point , "snr_point" : snr_point } }
                self.data.update ( point )
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
            pointcloud_unit = { "pointcloud_unit" : { "azimuth_unit" : azimuth_unit , "doppler_unit" : doppler_unit , "range_unit" : range_unit, "snr_unit" : snr_unit } }
            self.data.update ( pointcloud_unit )
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
                tlv_header_data = { "tlv_header_data" : { "tlv_type" : tlv_type , "tlv_length" : tlv_length } }
                self.data.update ( tlv_header_data )
                del tlv_header_data
                self.frame_data = self.frame_data[self.tlv_header_length:]
    
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
            frame_header_data = { "frame_header_data" : { "sync" : sync , "version" : version , "platform" : platform , "timestamp" : timestamp , "packet_length" : packet_length , "frame_number" : frame_number , "subframe_number" : subframe_number , "chirp_margin" : chirp_margin , "frame_margin" : frame_margin , "uart_sent_time" : uart_sent_time , "track_process_time" : track_process_time , "num_tlvs" : num_tlvs , "checksum" : checksum } }
            self.data.update ( frame_header_data )
            del frame_header_data
            self.frame_data = self.frame_data[self.frame_header_length:]
        else :
            log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} Check it out! Frame no. {frame_number} contain alter sync {sync}' )
    
    # Get frame data from frame_data to self dict
    def get_frame_data ( self ) :
        self.get_frame_header_data ()
        if self.data["frame_header_data"]["num_tlvs"] :
            self.get_tlv_header_data ()
            if self.data["tlv_header_data"]["tlv_type"] == 6 :
                self.get_pointcloud_unit_data ()
                self.get_points_data ()
            else :
                log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} Check it out! Frame no. {self.data["frame_header_data"]["frame_number"]} contain alter TLV type {self.data["tlv_header_data"]["tlv_type"]}' )
            data_file.write ( f'\n{self.data}' )
        else :
            data_file.write ( f'\n{self.data["frame_header_data"]["num_tlvs"]} TLVs in frame no. {self.data["frame_header_data"]["frame_number"]}' )

# Configure chirp 
conf_com.reset_input_buffer()
conf_com.reset_output_buffer()
chirp_conf ()
# Read data
data_com.reset_input_buffer ()
time_up = datetime.datetime.utcnow () + datetime.timedelta ( seconds = data_com_delta_seconds )
while datetime.datetime.utcnow () < time_up :
    # Rozpakuj i zapisz dane z nagłówka pakietu
    frame_data = data_com.read ( 4666 )
    print ( frame_data )
    if frame_data :
        hvac = Sense_and_detect_hvac_control_frame_data ( frame_data )
        #hvac = Sense_and_detect_hvac_control_frame_data ( raw_frame_bytes )
        hvac.get_frame_data ()
        del hvac
    else :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} Frame is empty!' )
        time.sleep(.2)
        data_com.reset_input_buffer ()
    break

################################################################
##################### CLOSE DATA COM PORT ######################
################################################################
try:
    data_com.close ()
except serial.SerialException as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port error closing: {str(e)}' )
if not data_com.is_open :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_com.name} port closed.' )

################################################################
############# STOP SENSOR AND CLOSE CONF COM PORT ##############
################################################################
# Stop sensor (freez until know how to start it properly)
# conf_com.write ( 'sensorStop\n'.encode () )
# ack = conf_com.readline ()
# log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
# ack = conf_com.readline ()
# log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
# time.sleep ( 3 )
# conf_com.reset_input_buffer ()
# Close CONF COM Port
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
################## CLOSE LOG AND DATA FILE #####################
################################################################
# Close data file
try:
    data_file.close ()
    if data_file.closed :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file.name} file is closed.' )
except IOError as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file.name} file closing problem... {str(e)}' )
# Close log file (must be at the end of the program)
log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file closing...' )
try:
    log_file.close ()
    if log_file.closed :
        print ( f'{log_file.name} file is closed.' )
except IOError as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file closing problem... {str(e)}' )
    print ( f'{log_file.name} file closing problem... {str(e)}' )