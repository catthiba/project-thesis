import sys, struct, serial
import os
import platform
import threading
import datetime
import csv
import math
import struct
from typing import List, Optional

def wait_for_ack():
   ddata = ""
   ack = struct.pack('B', 0xff)
   while ddata != ack:
      ddata = ser.read(1)
   return

sampling_rate = 128

if len(sys.argv) < 2:
   print ("no device specified")
   print ("You need to specify the serial port of the device you wish to connect to")
   print ("A second argument can be specified to change sampling rate to new value")
   print ("If no second argument the current sampling rate is read and displayed")
   print ("example (setting sampling rate to 51.2Hz):")
   print ("   samplingRate.py Com12")
   print ("or")
   print ("   samplingRate.py Com12 0x0280")

else:
   if len(sys.argv) == 2:
    ser = serial.Serial(sys.argv[1], 115200)
    ser.flushInput()
    print("port opening, done.")
    # send the set sensors command
    # 4 bytes command:
    #     0x08 is SET_SENSORS_COMMAND
    #     Each bit in the three following bytes are one sensor.
    ser.write(struct.pack(
        'BBBB', 0x08, 0x84, 0x01, 0x00))  # GSR and PPG
    wait_for_ack()
    print("sensor setting, done.")

    # Enable the internal expansion board power
    ser.write(struct.pack('BB', 0x5E, 0x01))
    wait_for_ack()
    print("enable internal expansion board power, done.")

    # send the set sampling rate command

    '''
    sampling_freq = 32768 / clock_wait = X Hz
    2 << 14 = 32768
    '''
    clock_wait = math.ceil((2 << 14) / sampling_rate)

    ser.write(struct.pack('<BH', 0x05, clock_wait))
    wait_for_ack()

    # Inquiry configurations (For finding channels order)
    # Page 16 of This PDF:
    # http://www.shimmersensing.com/images/uploads/docs/LogAndStream_for_Shimmer3_Firmware_User_Manual_rev0.11a.pdf

    ser.write(struct.pack('B', 0x01))
    wait_for_ack()
    inquiery_response = bytes("", 'utf-8')
    # response_size is 1 packet_type + 2 Sampling rate + 4 Config Bytes +
    # 1 Num Channels + 1 Buffer size
    response_size = 9
    numbytes = 0
    while numbytes < response_size:
        inquiery_response += ser.read(response_size)
        numbytes = len(inquiery_response)

    num_channels = inquiery_response[7]
    print("Number of Channels:", num_channels)
    print("Buffer size:", inquiery_response[8])

    # There's one byte for each channel
    # For the meaning of each byte, refer to the above PDF
    channels = bytes("", "utf-8")
    numbytes = 0
    while numbytes < num_channels:
        channels += ser.read(num_channels)
        numbytes = len(channels)

    print("Channel 1:", channels[0])
    print("Channel 2:", channels[1])
    print("Channel 3:", channels[2])
    print("Channel 4:", channels[3])
    print("Channel 5:", channels[4])

    # send start streaming command
    ser.write(struct.pack('B', 0x07))
    wait_for_ack()
    print("start command sending, done.")


    '''
    Reads incoming data
    '''
    ddata = bytes("", 'utf-8')
    numbytes = 0
    # 1byte packet type + 3byte timestamp + 2 byte X + 2 byte Y +
    # 2 byte Z + 2 byte PPG + 2 byte GSR
    framesize = 14

    try:
        while True:
            while numbytes < framesize:
                ddata += ser.read(framesize)
                numbytes = len(ddata)

            data = ddata[0:framesize]
            ddata = ddata[framesize:]
            numbytes = len(ddata)

            # read basic packet information
            (packettype) = struct.unpack('B', data[0:1])
            (timestamp0, timestamp1, timestamp2) = \
                struct.unpack('BBB', data[1:4])

            # read packet payload
            (x, y, z, PPG_raw, GSR_raw) = \
                struct.unpack('HHHHH', data[4:framesize])
            record_time = datetime.datetime.now()

            # get current GSR range resistor value
            data_range = ((GSR_raw >> 14) & 0xff)  # upper two bits
            if data_range == 0:
                rf = 40.2   # kohm
            elif data_range == 1:
                rf = 287.0  # kohm
            elif data_range == 2:
                rf = 1000.0  # kohm
            elif data_range == 3:
                rf = 3300.0  # kohm

            # convert GSR to kohm value
            gsr_to_volts = (GSR_raw & 0x3fff) * (3.0/4095.0)
            GSR_ohm = rf/((gsr_to_volts / 0.5) - 1.0)

            # convert PPG to milliVolt value
            PPG_mv = PPG_raw * (3000.0/4095.0)

            timestamp = timestamp0 + timestamp1*256 + timestamp2*65536

            #print([packettype[0], timestamp, GSR_ohm, PPG_mv] + _trigger)


            row = [packettype[0],
                    timestamp,
                    x, y, z,
                    GSR_ohm,
                    PPG_mv,
                    record_time]

    
    except KeyboardInterrupt:
        # send stop streaming command
        ser.write(struct.pack('B', 0x20))

        print("stop command sent, waiting for ACK_COMMAND")
        wait_for_ack()
        print("ACK_COMMAND received.")
        ser.close()
        print("All done")



"""    if not os.path.exists(file_name):
        csv_file = open(file_name, 'a')
        header = ["type", "time stamp", "Acc_x", "Acc_y", "Acc_z",
                    "GSR_ohm",
                    "PPG_mv",
                    "time",
                    "trigger"]
        writer = csv.writer(csv_file)
        writer.writerow(header)
        csv_file.flush()
        csv_file.close()

    with open(file_name, 'a') as csv_file:
        writer = csv.writer(csv_file)
        for row in _stream_data:
            writer.writerow(row)
            csv_file.flush()
 def _get_monitoring_data(:
    '''Returns latest collected data for monitoring/visualizing purposes.'''
    # Last three seconds
    return _stream_data[-1 * 3 * _sampling_rate:]

def get_saving_mode(:
    '''
    Return saving mode
    
    Returns
    -----------
    int
        The way of saving data: saving continiously in a file or save data related to
        each stimulus in a separate file. 
        SavingModeEnum: CONTINIOUS_SAVING_MODE = 0
                        SEPARATED_SAVING_MODE = 1
    '''
    return _saving_mode

def get_output_path(:
    '''
    Return the path that use for data recording

    Returns
    -----------
    str
        The output path that use for data recording
    '''
    return output_path """