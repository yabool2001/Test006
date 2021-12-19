import datetime
import json
from os import error, system
import time
import serial
import struct
import sys

# sys.setdefaultencoding('utf-8')

hello = "\n\n#########################################\n########## serials2.py started ##########\n#########################################\n"
print ( hello )

log_file_name = 'log.txt'
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

data_frame_time = []
data_frame_size = []

data = dict ()

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

# Open Chirp file and read configuration  
try:
    with open ( f'{conf_file_name}' , 'r' , encoding='utf-8' ) as conf_file:
        if conf_file.readable () :
            log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_file.name} file is readable.' )
            chirp_cfg = conf_file.readlines()
except IOError as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_file.name} file opening problem... {str(e)}' )

#### Chirp configuration
def chirp_conf () :
    conf_com.reset_output_buffer()
    for line in chirp_cfg :
        time.sleep(.1)
        conf_com.write ( line.encode () )
        ack = conf_com.readline ()
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
        ack = conf_com.readline ()
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
        time.sleep ( 3 )
        conf_com.reset_input_buffer ()

#### Open COM port
def open_COM ( port ) :
    try: 
        port.open ()
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {port.name} port opened' )
    except serial.SerialException as e:
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {port.name} port error opening: {str(e)}' )

#### Close COM port
def close_COM ( port ) :
    if port.is_open :
        try:
            port.close ()
            if not port.is_open :
                log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {port.name} port closed.' )
        except serial.SerialException as e:
            log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {port.name} port error closing: {str(e)}' )
    else:
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {port.name} port closed.' )
#### Create time report
def time_report ( a ) :
    time_total = 0
    for i in a :
        time_total += i
    if len ( a ) > 0 :
        print ( f'Average time: {time_total / len ( a )}   Number of frames: {len ( a )}' )
    else :
        print ( f'No data for time report.' )

#### Create size report
def size_report ( a ) :
    size_total = 0
    for i in a :
        size_total += i
    if len ( a ) > 0 :
        print ( f'Average size: {size_total / len ( a )}   Total size: {size_total}   number of frames: {len ( a )}' )
    else :
        print ( f'No data for size report.' )
#### Create global report
def report ( size , time ) :
    size_total = 0
    time_total = 0
    for i in size :
        size_total += i
    if len ( size ) > 0 :
        print ( f'Average size: {int ( size_total / len ( size ) )}   Total size: {size_total}' )
    else :
        print ( f'No data for size report.' )
    for i in time :
        time_total += i
    if len ( time ) > 0 :
        print ( f'Average time: {int ( time_total / len ( time ) )}   Number of frames: {len ( time )}' )
    else :
        print ( f'No data for time report.' )
    if len ( size ) > 0 and len ( time ) > 0 :
        print ( f'Time total / number of frames: {int ( time_total / len ( time ) )}.  Time total: {time_total}, number of frames: {len ( time )}' )

################################################################
######################## CONF CHIRP ############################
################################################################

open_COM ( conf_com )
# chirp_conf () # Odblokować tylko przy pierwszym uruchomieniu
close_COM ( conf_com )
 
################################################################
######################## DATA OPERATIONS #######################
################################################################

# Odczytaj, rozpakuj i zapisz dane z portu COM danych
open_COM ( data_com )
if data_com.is_open:
    time_up = datetime.datetime.utcnow () + datetime.timedelta ( seconds = data_com_delta_seconds )
    while datetime.datetime.utcnow () < time_up :
        # Rozpakuj i zapisz dane z nagłówka pakietu
        data_com.reset_output_buffer ()
        data_com.reset_input_buffer ()
        data_frame = data_com.read ( 4666 )
        if sys.getsizeof ( data_frame ) > 52 :
            time_0 = time.perf_counter_ns ()
            try:
                sync , version , platform , timestamp , packet_length , frame_number , subframe_number , chirp_margin , frame_margin , uart_sent_time , track_process_time , num_tlvs , checksum = struct.unpack ( frame_header_struct , data_frame[:frame_header_length] )
                data_frame_ok = True
            except struct.error as e :
                data_file.write ( f'\nFrame header parse failed! {e}. data_frame size: {sys.getsizeof ( data_frame )}' )
                data_frame_ok = False
            if data_frame_ok and sync == hvac_control :
                data.clear ()
                # Zapisz frame header
                data_frame_header = { 'sync' : sync , 'version' : version , 'platform' : platform , 'timestamp' : timestamp , 'packet_length' : packet_length , 'frame_number' : frame_number , 'subframe_number' : subframe_number , 'chirp_margin' : chirp_margin , 'frame_margin' : frame_margin , 'uart_sent_time' : uart_sent_time , 'track_process_time' : track_process_time , 'num_tlvs' : num_tlvs , 'checksum' : checksum }
                #data_file.write ( f'\n{data_frame_header}' )
                data["data_frame_header"] = data_frame_header
                #del data_frame_header
                #data_frame_size.append ( sys.getsizeof ( data_frame ) )
                data_frame = data_frame[frame_header_length:][:packet_length]
                time_d = time.perf_counter_ns() - time_0
                data_frame_time.append (time_d)
                # Rozpakuj i zapisz dane z nagłówka tlv
                if num_tlvs > 0 :
                    tlv = dict ()
                    for i in range ( num_tlvs ) :
                        try:
                            tlv_type, tlv_length = struct.unpack ( tlv_header_struct , data_frame[:tlv_header_length] )
                            tlv_frame_ok = True
                        except struct.error as e :
                            data_file.write ( f'\nTlv header parse failed! {e}. data_frame size: {sys.getsizeof ( data_frame )}' )
                            tlv_frame_ok = False
                        if tlv_frame_ok :
                            # Zapisz TLV header
                            tlv_frame_header = { 'tlv_type' : tlv_type , 'tlv_length' : tlv_length }
                            #data_file.write ( f'\n{tlv_frame_header}' )
                            #del tlv_frame_header
                            if tlv_type == 6 :
                                tlv[i] = tlv_frame_header
                                #data_frame = data_frame[tlv_header_length:]
                                try :
                                    azimuth_unit , doppler_unit , range_unit , snr_unit = struct.unpack ( point_cloud_unit_struct , data_frame[tlv_header_length:][:point_cloud_unit_length] )
                                    point_cloud_unit_ok = True
                                except struct.error as e :
                                    data_file.write ( f'\nPoint cloud unit parse failed! {e}. data_frame size: {sys.getsizeof ( data_frame )}' )
                                    point_cloud_unit_ok = False
                                if point_cloud_unit_ok :
                                    # Zapisz Point Cloud Unit
                                    point_cloud_unit = { 'azimuth_unit' : azimuth_unit , 'doppler_unit' : doppler_unit , 'range_unit' : range_unit, 'snr_unit' : snr_unit }
                                    data_file.write ( f'\n{point_cloud_unit}' )
                                    tlv[i] = point_cloud_unit
                                    #data_frame = data_frame[point_cloud_unit_length:]
                                    points_number = int ( ( tlv_length - tlv_header_length - point_cloud_unit_length ) / point_length )
                                    # print ( points_number )
                                    points = dict ()
                                    for j in range ( points_number ) :
                                        try :
                                            azimuth_point , doppler_point , range_point , snr_point = struct.unpack ( point_struct , data_frame[(tlv_header_length+point_cloud_unit_length)+(j*point_length):][:point_length] )
                                            point = { 'azimuth_point' : azimuth_point , 'doppler_point' : doppler_point , 'range_point' : range_point , 'snr_point' : snr_point }
                                            # point = dict ( azimuth_point = azimuth_point , doppler_point = doppler_point , range_point = range_point , snr_point = snr_point )
                                            points[j] = point
                                            del point
                                            #data_file.write ( f'\n{point}' )
                                        except struct.error as e :
                                            data_file.write ( f'\nPoint parse failed! {e}. data_frame size: {sys.getsizeof ( data_frame )}' )
                                            break
                                    data_file.write ( f'\n{points}' )
                                    tlv[i] = points
                                    del points
                                    data_frame = data_frame[tlv_length:]
                            else :
                                data_frame = data_frame[tlv_length:]
                        data["tlv"] = tlv
                else :
                    data_file.write ( f'\nNo TLV ' )
                data_file.write ( f'\n\n{data}' )

close_COM ( data_com ) 
 
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

#size_report ( data_frame_size )
time_report ( data_frame_time )
#report ( data_frame_size , data_frame_time )

#test = "1234512345"
#print (test[2:][:3])
#test = test[5:]
#print (test[2:][:3])
