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

frame_header = ""
tlv_header = ""
tlvs = ""
point_cloud_unit = ""
syn = 0


hvac_control = 506660481457717506
frame_header_struct = 'Q10I2H'
frame_header_length = struct.calcsize ( frame_header_struct )
tlv_header_struct = '2I'
tlv_header_length = struct.calcsize ( tlv_header_struct )
point_cloud_unit_struct = '4f'
point_cloud_unit_length = struct.calcsize ( point_cloud_unit_struct )
point_struct = '2B2h'
point_length = struct.calcsize ( point_struct )
tlv_type_pointcloud_2d = 6

conf_com = serial.Serial ()
data_com = serial.Serial ()
conf_com.port = 'COM4' # Choose: Silicon Labs Dual CP2105 USB to UART Bridge: Enhanced COM Port from Device manager
data_com.port = 'COM3' # Choose: Silicon Labs Dual CP2105 USB to UART Bridge: Standard COM Port from Device manager
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
        time_frame_header_0 = time.perf_counter_ns ()
        sync = 0
        try:
            sync , version , platform , timestamp , packet_length , frame_number , subframe_number , chirp_margin , frame_margin , uart_sent_time , track_process_time , num_tlvs , checksum = struct.unpack ( frame_header_struct , frame[:frame_header_length] )
        except struct.error as e :
            data_file.write ( f'\nError: Frame header unpack failed! {e}. Frame size: {sys.getsizeof ( frame )}. Sync: {sync}' )
        if sync == hvac_control :
            # Store frame header
            #frame_header = f"'sync':{sync},'version':{version},'platform':{platform},'timestamp':{timestamp},'packet_length':{packet_length},'frame_number':{frame_number},'subframe_number':{subframe_number},'chirp_margin':{chirp_margin},'frame_margin':{frame_margin},'uart_sent_time':{uart_sent_time},'track_process_time':{track_process_time},'num_tlvs':{num_tlvs},'checksum':{checksum}"
            frame_header = "{frame_header:{'sync':" + str ( sync ) + ",'version':" + str ( version ) + ",'platform':" + str ( platform ) + ",'timestamp':" + str ( timestamp ) + ",'packet_length':" + str ( packet_length ) + ",'frame_number':" + str ( frame_number ) + ",'subframe_number':" + str ( subframe_number ) + ",'chirp_margin':" + str ( chirp_margin ) + ",'frame_margin':" + str ( frame_margin ) + ",'uart_sent_time':" + str ( uart_sent_time ) + ",'track_process_time':" + str ( track_process_time ) + ",'num_tlvs':" + str ( num_tlvs ) + ",'checksum':" + str ( checksum ) + "}}"
            # Remove frame header to simplify next TLVs calculations
            frame = frame[frame_header_length:]
            time_frame_header_d = time.perf_counter_ns() - time_frame_header_0
            frame_time.append (time_frame_header_d)

            # Unpack tlv header
            time_tlv_header_0 = time.perf_counter_ns ()
            for i in range ( num_tlvs ) :
                try:
                    tlv_type, tlv_length = struct.unpack ( tlv_header_struct , frame[:tlv_header_length] )
                except struct.error as e :
                    data_file.write ( f'\nError: Tlv header parse failed! {e}. Exiting frame because not now how to get next TLV!' )
                    break
                if tlv_type == tlv_type_pointcloud_2d :
                    #tlv_header = f"'tlv_type':{tlv_type},'tlv_length':{tlv_length}"
                    tlv_header = "{" + "'tlv_header:{'tlv_type':" + str(tlv_type) + ",'tlv_length':" + str(tlv_length) + "}}},"
                    time_tlv_header_d = time.perf_counter_ns() - time_tlv_header_0
                    frame_time.append (time_tlv_header_d)

                    # Unpack point_cloud_unit
                    time_point_cloud_unit_0 = time.perf_counter_ns ()
                    try :
                        azimuth_unit , doppler_unit , range_unit , snr_unit = struct.unpack ( point_cloud_unit_struct , frame[tlv_header_length:][:point_cloud_unit_length] )
                        try_result = True
                    except struct.error as e :
                        data_file.write ( f'\npoint_cloud_unit parse failed! {e}.' )
                        try_result = False
                    if try_result :
                        point_cloud_unit = f"'azimuth_unit':{azimuth_unit},'doppler_unit':{doppler_unit},'range_unit':{range_unit},'snr_unit':{snr_unit}"
                        time_point_cloud_unit_d = time.perf_counter_ns() - time_point_cloud_unit_0
                        frame_time.append (time_point_cloud_unit_d)
                    # Next line here
                    # Sprawdzić czy:
                    # 1. Kasują sie zmienne tlv_type i tlv_length
                    # 2. Czy są sytuacje, że nie znam tlv_length i nie wiem jak obciąć ramkę tvl, żeby poprawnie rozpakować następną
                
                    frame = frame[tlv_length:]
                    # Create JSON comprises all frame component
                else :
                    data_file.write ( f'\nInfo: Tlv type {tlv_type} not {tlv_type_pointcloud_2d}!' )
                    tlv = f""
        data = "\n{'frame':[" + frame_header + "]}"
        # Write JSON frame to the file 
        data_file.write ( data )

close_COM ( data_com )
time_report ( frame_time )
frame_time.clear ()

# Zamykanie plików z logami powinno być zawsze na samym końcu programu
log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file closing...' )
try:
    log_file.close ()
    if log_file.closed :
        print ( f'{log_file.name} file is closed.' )
except IOError as e :
    log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {log_file.name} file closing problem... {str(e)}' )
    print ( f'{log_file.name} file closing problem... {str(e)}' )
