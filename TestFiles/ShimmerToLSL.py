#!/usr/bin/python
import sys, struct, serial
from pylsl import StreamInfo, StreamOutlet


def wait_for_ack():
   ddata = ""
   ack = struct.pack('B', 0xff)
   while ddata != ack:
      ddata = ser.read(1)	  
   return

#print(sys.argv.index.__getattribute__)
if len(sys.argv) < 2:
   print( "no device specified")
   print( "You need to specify the serial port of the device you wish to connect to")
   print( "example:")
   print( "   aAccel5Hz.py Com12")
   print( "or")
   print( "   aAccel5Hz.py /dev/rfcomm0")
else:
   ser = serial.Serial(sys.argv[1], 115200)
   ser.flushInput()
   print( "port opening, done.")

# send the set sensors command
   ser.write(struct.pack('BBBB', 0x08 , 0x04, 0x01, 0x00))  #GSR and PPG
   wait_for_ack()   
   print( "sensor setting, done.")

# Enable the internal expansion board power
   ser.write(struct.pack('BB', 0x5E, 0x01))
   wait_for_ack()
   print( "enable internal expansion board power, done.")

# send the set sampling rate command

   '''
    sampling_freq = 32768 / clock_wait = X Hz
   '''
   sampling_freq = 50
   clock_wait = (2 << 14) / sampling_freq

   ser.write(struct.pack('<BH', 0x05, int(clock_wait)))
   wait_for_ack()

# send start streaming command
   ser.write(struct.pack('B', 0x07))
   wait_for_ack()
   print( "start command sending, done.")

   # define lsl streams
   # Defining stream info:
   name = 'Shimmer_GSR'
   ID = 'Shimmer_GSR'
   channels = 1
   sample_rate = 50
   datatype = 'float32'
   streamType = 'GSR'
   print("Creating LSL stream for GSR. \nName: %s\nID: %s\n" %(name, ID))

   info_gsr = StreamInfo(name, streamType, channels, sample_rate, datatype, ID)
   #print(info_gsr)
   chns = info_gsr.desc().append_child("channels")
   #print('chns: ', chns)
   for label in ["CH1", "CH"]:
      ch = chns.append_child("channel")
      ch.append_child_value("label", label)
      
   
   outlet_gsr = StreamOutlet(info_gsr)
   #print(outlet_gsr.do_push_chunk)

# read incoming data
   ddata = ""
   numbytes = 0
   framesize = 8 # 1byte packet type + 3byte timestamp + 2 byte GSR + 2 byte PPG(Int A13)

   print( "Packet Type\tTimestamp\tGSR\tPPG")
   try:
      while True:
         while numbytes < framesize:
            ddata = ser.read(framesize)
            numbytes = len(ddata)
         
         #print('ddata', ddata)
         data = ddata[0:framesize]
         ddata = ddata[framesize:]
         numbytes = len(ddata)

         """ print('struckt size: ', str(struct.calcsize('P')))

         for i in range(framesize):
            print(data[i])
            print(struct.unpack('P', data[i]))
          """

         # read basic packet information
         (packettype) = struct.unpack('B', data[0:1])
         (timestamp0, timestamp1, timestamp2) = struct.unpack('BBB', data[1:4])
         # print('packettype', packettype)

         # read packet payload
         (PPG_raw, GSR_raw) = struct.unpack('HH', data[4:framesize])

         # get current GSR range resistor value
         Range = ((GSR_raw >> 14) & 0xff)  # upper two bits
         if(Range == 0):
            Rf = 40.2   # kohm
         elif(Range == 1):
            Rf = 287.0  # kohm
         elif(Range == 2):
            Rf = 1000.0 # kohm
         elif(Range == 3):
            Rf = 3300.0 # kohm

         # convert GSR to kohm value
         gsr_to_volts = (GSR_raw & 0x3fff) * (3.0/4095.0)
         GSR_ohm = Rf/( (gsr_to_volts /0.5) - 1.0)

         # convert PPG to milliVolt value
         PPG_mv = PPG_raw * (3000.0/4095.0)

         timestamp = timestamp0 + timestamp1*256 + timestamp2*65536

         print( "0x%02x\t\t%5d,\t%4d,\t%4d" % (packettype[0], timestamp, GSR_ohm, PPG_mv))
         
         gsr_data = GSR_ohm
         print('gsr_data: ', gsr_data)
         gsr_chunk = []
         gsr_chunk.append(gsr_data)
         outlet_gsr.push_chunk(gsr_chunk)



   except KeyboardInterrupt:
#send stop streaming command
      ser.write(struct.pack('B', 0x20))
      print( "stop command sent, waiting for ACK_COMMAND")
      wait_for_ack()
      print( "ACK_COMMAND received.")
#close serial port
      ser.close()
      print( "All done")