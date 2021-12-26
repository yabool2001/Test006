from contextlib import nullcontext
import datetime
import json
from os import error, system
import time
import serial
import struct
import sys
# sys.setdefaultencoding('utf-8')

################################################################
######################## DEFINITIONS ###########################
################################################################

global                  chirp_cfg
global                  log_file , data_file
global                  conf_com , data_com
raws                    = bytes(1)
log_file_name           = 'log.txt'
data_file_name          = 'data.txt'
conf_file_name          = 'chirp_cfg/mmw_pplcount_demo_default.cfg'
# conf_file_name = 'chirp_cfg/sense_and_direct_68xx.cfg'
# conf_file_name = 'chirp_cfg/long_range_people_counting.cfg'
conf_com                = serial.Serial ()
data_com                = serial.Serial ()
conf_com.port           = 'COM10' # Choose: Silicon Labs Dual CP2105 USB to UART Bridge: Enhanced COM Port from Device manager on MS GO3
data_com.port           = 'COM11' # Choose: Silicon Labs Dual CP2105 USB to UART Bridge: Standard COM Port from Device manager on MS GO3
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

hello = "\n\n#########################################\n########## serials3.py started ##########\n#########################################\n"

################################################################
############ OPEN LOG, DATA AND CHIRP CONF FILE ################
################################################################

# Open log file
try:
    log_file = open ( log_file_name , 'a' , encoding='utf-8' )
    if log_file.writable() :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {hello}' )
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

class Sense_and_detect_hvac_control_raw_data :
    def __init__ ( self , raw_data ) :
        self.raw_data = raw_data
        self.control = 506660481457717506
        self.tlv_type_pointcloud_2d = 6
        self.frame_header_struct = 'Q10I2H'
        self.frame_header_length = struct.calcsize ( self.frame_header_struct )
        self.tlv_header_struct = '2I'
        self.tlv_header_length = struct.calcsize ( self.tlv_header_struct )
        self.pointcloud_unit_struct = '4f'
        self.pointcloud_unit_length = struct.calcsize ( self.pointcloud_unit_struct )
        self.point_struct = '2B2h'
        self.point_length = struct.calcsize ( self.point_struct )
        self.frame_header = None
        self.tlvs = None
        self.num_tlvs = None
        self.frame_header = None
        self.tlv_header = None
        self.pointcloud_unit = None
        self.points = None
        self.tlv_list = []
        self.point_list = []
        #self.frame_header_data = dict ()

    def write_data ( self , file ) :
        file.write ( f"\n\n{{frame:{self.frame_header},{self.tlvs}}}" )

    # Zdekodowanie wszystkich punktów z ramki zaczynającej się od Punktów
    # Zapisanie punktów do dict, zapisanie słownika do pliku i skasowanie słownika
    # Usunięcie Punktu z ramki w każdej iteracji
    def get_points ( self , tlv_length ) :
        points_number = int ( ( tlv_length - self.tlv_header_length - self.pointcloud_unit_length ) / self.point_length )
        for i in range ( points_number ) :
            try :
                azimuth_point , doppler_point , range_point , snr_point = struct.unpack (self. point_struct , self.raw_data[(self.tlv_header_length + self.pointcloud_unit_length ) + ( i * self.point_length ):][:self.point_length] )
                # Zapisz punkt
                self.point_list.append ( f"{{'azimuth_point':{azimuth_point},'doppler_point':{doppler_point}, 'range_point':{range_point},'snr_point':{snr_point}}}" )
            except struct.error as e :
                self.point_list.append ( f"{{'error':'{e}'}}" )
        l = len ( self.point_list )
        self.points = "'points':["
        for i in range ( len ( self.point_list ) ) :
            self.points += str ( self.point_list[i] ) #self.points = self.points + str ( self.point_list[i] )
            if i < ( l - 1 ) :
                self.points = self.points + ","
        self.points = self.points + "]"


    # Zdekodowanie chmury punktów z ramki zaczynającej się od chmury punktów
    # Zapisanie chmury punktów do dict, zapisanie słownika do pliku i skasowanie słownika
    # Usunięcie chmury punktów z ramki
    def get_pointcloud2d_unit ( self ) :
        try :
            azimuth_unit , doppler_unit , range_unit , snr_unit = struct.unpack ( self.pointcloud_unit_struct , self.raw_data[self.tlv_header_length:][:self.pointcloud_unit_length] )
            self.pointcloud_unit = f"'point_cloud_unit':{{'azimuth_unit':{azimuth_unit},'doppler_unit':{doppler_unit},'range_unit':{range_unit},'snr_unit':{snr_unit}}}"
            return True
        except struct.error as e :
            self.pointcloud_unit = f"{{'point_cloud_unit':{{'error':'{e}'}}}}"
            return False

    def get_tlv ( self ) :
        try:
            tlv_type, tlv_length = struct.unpack ( self.tlv_header_struct , self.raw_data[:self.tlv_header_length] )
            self.tlv_header = f"'tlv_header':{{'tlv_type':{tlv_type},'tlv_length':{tlv_length}}}"
            if tlv_type == self.tlv_type_pointcloud_2d :
                if self.get_pointcloud2d_unit () :
                    self.get_points ( tlv_length )
                    self.tlv_list.append ( f"{{tlv:{{{self.tlv_header},{self.pointcloud_unit},{self.points}}}}}" )
                else :
                    self.tlv_list.append ( f"{{tlv:{{{self.tlv_header},{self.pointcloud_unit}}}}}" )
            elif tlv_type > self.tlv_type_pointcloud_2d :
                self.tlv_list.append ( f"{{tlv:{{{self.tlv_header}}}}}" )
            self.raw_data = self.raw_data[tlv_length:]
            return True
        except struct.error as e :
            self.tlv_header = f"'tlv_header':{{'error':{e}}}"
            return False

    def get_tlvs ( self ) :
        for i in range ( self.num_tlvs ) :
            if not self.get_tlv () :
                break
        l = len ( self.tlv_list )
        self.tlvs = "'tlvs':["
        for i in range ( l ) :
            self.tlvs = self.tlvs + str ( self.tlv_list[i] )
            if i < ( l - 1 ) :
                self.tlvs = self.tlvs + ","
        self.tlvs = self.tlvs + "]"
        self.tlv_list.clear ()
            
    # Rozpakuj i zapisz dane z Frame header
    def get_frame_header ( self ) :
        try:
            sync , version , platform , timestamp , packet_length , frame_number , subframe_number , chirp_margin , frame_margin , uart_sent_time , track_process_time , num_tlvs , checksum = struct.unpack ( self.frame_header_struct , self.raw_data[:self.frame_header_length] )
            self.num_tlvs = num_tlvs
            if sync == self.control :
                self.frame_header = f"{{'frame_header':{{'sync':{sync},'version':{version},'platform':{platform},'timestamp':{timestamp},'packet_length':{packet_length},'frame_number':{frame_number},'subframe_number':{subframe_number},'chirp_margin':{chirp_margin},'frame_margin':{frame_margin},'uart_sent_time':{uart_sent_time},'track_process_time':{track_process_time},'num_tlvs':{num_tlvs},'checksum':{checksum}}}}}"
            else :
                self.frame_header = f"{{'frame_header':{{'error':'control = {sync}'}}}}"
        except struct.error as e :
            self.frame_header = f"{{'frame_header':{{'error':'{e}'}}}}"

################################################################
####################### START PROGRAM ##########################
################################################################

print ( hello )

# Configure chirp 
conf_com.reset_input_buffer()
conf_com.reset_output_buffer()
#chirp_conf ()

# Read data
data_com.reset_output_buffer()
data_com.reset_input_buffer ()
frame_read_time_up = datetime.datetime.utcnow () + datetime.timedelta ( seconds = data_com_delta_seconds )
while datetime.datetime.utcnow () < frame_read_time_up :
    raw_data = data_com.read ( 4666 )
    hvac = Sense_and_detect_hvac_control_raw_data ( raw_data )
    hvac.get_frame_header ()
    if hvac.num_tlvs :
        hvac.raw_data = hvac.raw_data[hvac.frame_header_length:]
        hvac.get_tlvs ()
    hvac.write_data ( data_file )
    del hvac

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