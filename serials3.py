import datetime
from os import error, system
import time
import serial
import struct
import sys


log_file_name = 'serials3_log.txt'
data_file_name = 'serials3_data.txt'
conf_file_name = 'chirp_cfg/mmw_pplcount_demo_default.cfg'
# conf_file_name = 'chirp_cfg/sense_and_direct_68xx.cfg'
# conf_file_name = 'chirp_cfg/long_range_people_counting.cfg'

frame_list = []
tlv_list = []
point_list = []
#frame_header = ""
#tlv_header = ""
#tlvs = ""
#point_cloud_unit = ""

hvac_control = 506660481457717506
frame_header_struct = 'Q10I2H'
frame_header_length = struct.calcsize ( frame_header_struct )
tlv_header_struct = '2I'
tlv_header_length = struct.calcsize ( tlv_header_struct )
pointcloud_unit_struct = '4f'
pointcloud_unit_length = struct.calcsize ( pointcloud_unit_struct )
point_struct = '2B2h'
point_length = struct.calcsize ( point_struct )
tlv_type_pointcloud_2d = 6

conf_com = serial.Serial ()
data_com = serial.Serial ()
#conf_com.port = 'COM4' # Choose: Silicon Labs Dual CP2105 USB to UART Bridge: Enhanced COM Port from Device manager on Wacom
#data_com.port = 'COM3' # Choose: Silicon Labs Dual CP2105 USB to UART Bridge: Standard COM Port from Device manager on Wacom
conf_com.port = 'COM10' # Choose: Silicon Labs Dual CP2105 USB to UART Bridge: Enhanced COM Port from Device manager on MS GO3
data_com.port = 'COM11' # Choose: Silicon Labs Dual CP2105 USB to UART Bridge: Standard COM Port from Device manager on MS GO3
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

data_com_delta_seconds = 1

data_frame_bytes = bytes (1)
frame_time = []
data_frame_size = []

data = ""

hello = "\n\n#########################################\n########## serials3.py started ##########\n#########################################\n"

################################################################
######################## DEFINITIONS ###########################
################################################################

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
####################### START PROGRAM ##########################
################################################################

print ( hello )

# Open log file
try:
    log_file = open ( log_file_name , 'a' , encoding='utf-8' )
    if log_file.writable() :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {hello}' )
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file is writable.' )
except IOError as e :
    print ( f'{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file opening problem... {str(e)}' )

# Open Chirp file and read configuration  
try:
    with open ( f'{conf_file_name}' , 'r' , encoding='utf-8' ) as conf_file:
        if conf_file.readable () :
            log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_file.name} file is readable.' )
            chirp_cfg = conf_file.readlines()
except IOError as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_file.name} file opening problem... {str(e)}' )

# Open data file
try:
    data_file = open ( data_file_name , 'a' , encoding='utf-8' )
    if data_file.writable() :
        log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file.name} file is writable.' )
except IOError as e :
    print ( f'{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {data_file.name} file opening problem... {str(e)}' )

# Chirp configuration
open_COM ( conf_com )
#chirp_conf () # Odblokować tylko przy pierwszym uruchomieniu
close_COM ( conf_com )

# Read data
open_COM ( data_com )
if data_com.is_open:
    time_up = datetime.datetime.utcnow () + datetime.timedelta ( seconds = data_com_delta_seconds )
    while datetime.datetime.utcnow () < time_up :
        
        # Read data from data_com
        data_com.reset_output_buffer ()
        data_com.reset_input_buffer ()
        frame = data_com.read ( 4666 )

        # Unpack frame header
        # sync = 0 check if it's local and deleting itself
        try:
            sync , version , platform , timestamp , packet_length , frame_number , subframe_number , chirp_margin , frame_margin , uart_sent_time , track_process_time , num_tlvs , checksum = struct.unpack ( frame_header_struct , frame[:frame_header_length] )
        except struct.error as e :
            #data_file.write ( f"\n\nError: Frame header unpack failed! {e}. Frame size: {sys.getsizeof ( frame )}.\n\n" )
            continue
        if sync == hvac_control :
            # Store frame header
            frame_header = f"{{frame_header:{{'sync':{sync},'version':{version},'platform':{platform},'timestamp':{timestamp},'packet_length':{packet_length},'frame_number':{frame_number},'subframe_number':{subframe_number},'chirp_margin':{chirp_margin},'frame_margin':{frame_margin},'uart_sent_time':{uart_sent_time},'track_process_time':{track_process_time},'num_tlvs':{num_tlvs},'checksum':{checksum}}}}}"
            # Remove frame header to simplify next TLVs calculations
            frame = frame[frame_header_length:]
            # Unpack tlv header
            for i in range ( num_tlvs ) :
                try:
                    tlv_type, tlv_length = struct.unpack ( tlv_header_struct , frame[:tlv_header_length] )
                    tlv_header = f"{{tlv_header:{{'tlv_type':{tlv_type},'tlv_length':{tlv_length}}}}}"
                except struct.error as e :
                    data_file.write ( f"\n\nError: Tlv header parse failed! {e}.!\n\n" )
                    continue
                if tlv_type == tlv_type_pointcloud_2d :
                    # Unpack point_cloud_unit
                    try :
                        azimuth_unit , doppler_unit , range_unit , snr_unit = struct.unpack ( pointcloud_unit_struct , frame[tlv_header_length:][:pointcloud_unit_length] )
                        point_cloud_unit = f"'point_cloud_unit':{{'azimuth_unit':{azimuth_unit},'doppler_unit':{doppler_unit},'range_unit':{range_unit},'snr_unit':{snr_unit}}}"
                    except struct.error as e :
                        data_file.write ( f"\n\nPoint_cloud_unit parse failed! {e}.\n\n" )
                        continue
                    points_number = int ( ( tlv_length - tlv_header_length - pointcloud_unit_length ) / point_length )
                    for k in range ( points_number ) :
                        try :
                            azimuth_point , doppler_point , range_point , snr_point = struct.unpack ( point_struct , frame[(tlv_header_length+pointcloud_unit_length)+(k*point_length):][:point_length] )
                            # Zapisz punkt
                            point_list.append ( f"{{'point':{{'azimuth_point':{azimuth_point},'doppler_point':{doppler_point}, 'range_point':{range_point},'snr_point':{snr_point}}}}}" )
                        except struct.error as e :
                            data_file.write ( f'\nPoint parse failed! {e}' )
                    l = len ( point_list )
                    points = "'points':["
                    for k in range ( len ( point_list ) ) :
                        points = points + str ( point_list[i] )
                        if i < ( l - 1 ) :
                            points = points + ","
                    points = points + "]"
                    tlv_list.append ( f"{{tlv:{tlv_header},{point_cloud_unit},{points}}}" )
                    del points
                    point_list.clear ()
                    # Next line here
                    # Sprawdzić czy:
                    # 1. Kasują sie zmienne tlv_type i tlv_length
                    # 2. Czy są sytuacje, że nie znam tlv_length i nie wiem jak obciąć ramkę tvl, żeby poprawnie rozpakować następną
                    frame = frame[tlv_length:]
                else :
                    tlv_list.append ( f"{{tlv:{tlv_header}}}" )
                    frame = frame[tlv_length:]
            l = len ( tlv_list )
            tlvs = "'tlvs':["
            for i in range ( len ( tlv_list ) ) :
                tlvs = tlvs + str ( tlv_list[i] )
                if i < ( l - 1 ) :
                    tlvs = tlvs + ","
            tlvs = tlvs + "]"
            tlv_list.clear ()
            frame_list.append ( f"{{frame:{frame_header},{tlvs}}}" )
        # Write JSON frame to the file 
        for i in frame_list :
            data_file.write ( str ( i ) )
        frame_list.clear ()

close_COM ( data_com )

# Zamykanie plików z logami powinno być zawsze na samym końcu programu
log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file closing...' )
try:
    log_file.close ()
    if log_file.closed :
        print ( f'{log_file.name} file is closed.' )
except IOError as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file closing problem... {str(e)}' )
    print ( f'{log_file.name} file closing problem... {str(e)}' )
