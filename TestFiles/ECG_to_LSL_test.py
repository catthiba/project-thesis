#!/usr/bin/python
import sys, struct, serial, time
from pylsl import StreamInfo, StreamOutlet 

# ExG configuration parameters
exgconfigGain = {	#decimal
    'GAIN_1':  0x15, #21
    'GAIN_2':  0x25, #37
    'GAIN_3':  0x35, #53
    'GAIN_4':  0x45, #69
    'GAIN_6':  0x05, #5
    'GAIN_8':  0x55, #55
    'GAIN_12': 0x65  #101
}

exgGain = {
    'GAIN_1':  1, #used
    'GAIN_2':  2,
    'GAIN_3':  3,
    'GAIN_4':  4, #Recommended 
    'GAIN_6':  6, #Default
    'GAIN_8':  8,
    'GAIN_12': 12
}

exg_24bit = [0x18, 0x00, 0x00]
exg_16bit = [0x00, 0x00, 0x18]

'''
***************************
* User settable variables *
***************************
'''
samplingFrequency 	= 512 						# frequency in Hz
exgRes_24bit 		= False						# 24bit if True, else 16bit
exgGainValue 		= exgconfigGain['GAIN_1'] 	# sets a gain of 1


# The internal sampling rate of the ADS1292R chips needs to be set based on the Shimmers sampling rate
if (samplingFrequency<=125):
    exgSamplingRate = 0x00 # 125Hz
elif (samplingFrequency<=250):
    exgSamplingRate = 0x01 # 250Hz
elif (samplingFrequency<=500):
    exgSamplingRate = 0x02 # 500Hz
elif (samplingFrequency<=1000):
    exgSamplingRate = 0x03 # 1000Hz
elif (samplingFrequency<=2000):
    exgSamplingRate = 0x04 # 2000Hz
elif (samplingFrequency<=4000):
    exgSamplingRate = 0x05 # 4000Hz
else:
    exgSamplingRate = 0x02 # 500Hz

'''
Example configuration for exg test signal square wave:
Configure both ADS1292R (ExG) chips: 
- enable internal voltage reference
- 500 samples per second (internal sampling rate)
- square-wave test signal
write:
SET_EXG_REGS_COMMAND
chip identifier ('0' for chip1, '1' for chip2)
starting byte
number of bytes to write
followed by the exgtestsignalconfiguration bytes
where: 
exgtestsignalconfiguration = ["CONFIG1" = 2, "CONFIG2" = 163, "LOFF" = 16,
"CH1SET" = 5, "CH2SET" = 5, "RLD_SENS" = 0, "LOFF_SENS" = 0, "LOFF_STAT" = 0,
"RESP1" = 2, "RESP2" = 1]
'''
# Chip 1 configuration
chip1Config = [exgSamplingRate, 0xA3, 0x10, exgGainValue, exgGainValue, 0x00, 0x00, 0x00, 0x02, 0x01]

# Chip 2 configuration
chip2Config = [exgSamplingRate, 0xA3, 0x10, exgGainValue, exgGainValue, 0x00, 0x00, 0x00, 0x02, 0x01]


'''
************************
* Function definitions *
************************
'''
def wait_for_ack():
    ddata = ""
    ack = struct.pack('B', 0xff)
    #print(ack)
    while ddata != ack:
        ddata = ser.read(1)
        #print("read: ", struct.unpack('B',ddata))
    return

def setSamplingRateHz(rate=512):
    # send the set sampling rate command
    sampling_freq = rate #Hz
    clock_wait = (2 << 14) / sampling_freq
    ser.write(struct.pack('<BH', 0x05, int(clock_wait)))
    wait_for_ack()

'''
**************************************************
* Connect to Shimmer and send configuraion bytes *
**************************************************
'''

if len(sys.argv) < 2:
    print ("No device specified.")
    print ("Specify the serial port of the device you wish to connect to.")
    print ("Example:")
    print ("   exgSquareWave512Hz.py Com12")
    print ("or")
    print ("   exgSquareWave512Hz.py /dev/rfcomm0")
else:
    ser = serial.Serial(sys.argv[1], 115200)
    ser.flushInput()
    print ("Port open...")

    #get the daughter card ID byte (SR number)
    print("Requesting Daughter Card ID and Revision number...")
    print(struct.pack('BBB', 0x66, 0x02,0x00))
    ser.write(struct.pack('BBB', 0x66, 0x02,0x00))
    wait_for_ack()

    #print(ser.write(struct.pack('B', 0x01)))

    ddata = list(struct.unpack(4*'B', ser.read(4)))
    #print(len(ddata)) #length here is 4
    srNumber = ddata[2]
    srRev = ddata[3]

    print ("Device: SR%d-%d" % (srNumber, srRev))
    #print("data: %d, %d" % (ddata[0],ddata[1]))

    #send the set sensors command
    ser.write(struct.pack('BBBB', 0x08, 0x18, 0x00, 0x00))  #exg1 and exg2
    wait_for_ack()
    print ("Sensor Enabling done...")

    # send the set sampling rate command
    setSamplingRateHz(samplingFrequency)
    print ("Freq sent...")


    ''' 
    *************************
    * Send ExG config bytes *
    *************************
    '''
    # firstly - send the set sensors command - disable all
    if exgRes_24bit:
        sensors = [0x08] + exg_24bit
    else:
        sensors = [0x08] + exg_16bit
    ser.write(sensors)
    wait_for_ack()
    time.sleep(2)


    if exgRes_24bit:
        exgCalFactor = (((2.42*1000)/exgGain['GAIN_1'])/(pow(2,23)-1))
    else:
        exgCalFactor = (((2.42*1000)/(exgGain['GAIN_1']*2))/(pow(2,15)-1))

    if(srNumber == 47 and srRev >= 4):
        chip1Config[1] |= 8 # Config byte for CHIP1 in SR47-4


    #	 write:
    # 	SET_EXG_REGS_COMMAND (0x61)
    # 	chip identifier ('0' for chip1, '1' for chip2)
    # 	starting byte
    # 	number of bytes to write
    # 	followed by the exgtestsignalconfiguration bytes

    # Configure Chip 1
    #wirites set_EXG_regs_command for chip1, starting at byte 0 ad writes 0x0a (10) bytes 
    chip1Config = [0x61, 0x00, 0x00, 0x0A] + chip1Config
    ser.write(chip1Config)
    wait_for_ack()

    # Configure Chip 2 
    chip2Config = [0x61, 0x01, 0x00, 0x0A] + chip2Config
    ser.write(chip2Config)
    wait_for_ack()
    print ("Configuration sent...")


    # send start streaming command
    ser.write(struct.pack('B', 0x07))
    wait_for_ack()
    print ("Start sent...")


    # define lsl streams
    # Defining stream info:
    name = 'Shimmer_ECG'
    ID = 'Shimmer_Ecg'
    channels = 4
    sample_rate = samplingFrequency
    datatype = 'float32'
    streamType = 'ECG'
    print("Creating LSL stream for ECG. \nName: %s\nID: %s\n" %(name, ID))

    info_ecg = StreamInfo(name, streamType, channels, sample_rate, datatype, ID)
    #print(info_gsr)
    chns = info_ecg.desc().append_child("channels")
    #print('chns: ', chns)
    for label in ["C1CH1", "C1CH2", "C2CH1", "C2CH2"]:
        ch = chns.append_child("channel")
        ch.append_child_value("label", label)
        

    outlet_ecg = StreamOutlet(info_ecg)
    #print(outlet_gsr.do_push_chunk)

    # read incoming data
    ddata = ""
    numbytes = 0
    framesize = (18 if exgRes_24bit else 14) # 1byte packet type + 3byte timestamp + 14byte ExG data

    print ("Packet Type,\tTimestamp, \tChip1 Status, \tChip1 Channel 1,2 (mv), \tChip2 Status, \tChip2 Channel 1,2 (mV)")
    try:
        while True:
            while numbytes < framesize:
                ddata = ser.read(framesize)
                numbytes = len(ddata)
            
            data = ddata[0:framesize]
            ddata = ddata[framesize:]
            numbytes = len(ddata)

            (packettype,) = struct.unpack('B', data[0:1])
            
            #print(struct.unpack('B', data[1:2]))
            # (timestamp, c1status) = struct.unpack('HB', data[1:4])
            (ts0, ts1, ts2, c1status) = struct.unpack('BBBB', data[1:5])
            
            timestamp = ts0 + ts1*256 + ts2*65536
            # 24-bit signed values MSB values are tricky, as struct only supports 16-bit or 32-bit
            # pad with zeroes at LSB end and then shift the result
            
            if exgRes_24bit:
                # chip 1
                c1ch1 = struct.unpack('>i', (data[5:8]))[0] >> 8
                c1ch2 = struct.unpack('>i', (data[8:11] + '\0'))[0] >> 8

                # status byte
                (c2status,) = struct.unpack('B', data[11:12])

                # chip 2
                c2ch1 = struct.unpack('>i', (data[12:15] + '\0'))[0] >> 8
                c2ch2 = struct.unpack('>i', (data[15:framesize] + '\0'))[0] >> 8
            else:
                # chip 1
                c1ch1 = struct.unpack('>h', data[5:7])[0]
                c1ch2 = struct.unpack('>h', data[7:9])[0]

                # status byte
                (c2status,) = struct.unpack('B', data[9:10])

                # chip 2
                c2ch1 = struct.unpack('>h', data[10:12])[0]
                c2ch2 = struct.unpack('>h', data[12:framesize])[0]

            # Calibrate exg channels:
            c1ch1 *= exgCalFactor
            c1ch2 *= exgCalFactor
            c2ch1 *= exgCalFactor
            c2ch2 *= exgCalFactor

            print ("0x%02x,\t\t%5d,\t0x%02x,\t\t%2.4f,%2.4f,\t\t%s0x%02x,\t\t%2.4f,%2.4f" % \
            (packettype, timestamp, c1status, c1ch1, c1ch2, "\t" if c1ch1>0 else "", c2status, c2ch1, c2ch2))

            ecg_data = [c1ch1, c1ch2, c2ch1, c2ch2]
            print('ecg_data: ', ecg_data)
            ecg_chunk = []
            ecg_chunk.append(ecg_data)
            outlet_ecg.push_chunk(ecg_chunk)

    except KeyboardInterrupt:
        #send stop streaming command
        ser.write(struct.pack('B', 0x20))
        wait_for_ack()
        #close serial port
        ser.close()
        print
        print ("All done!")