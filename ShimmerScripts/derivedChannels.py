#!/usr/bin/python
import sys, struct, serial

def wait_for_ack():
   ddata = ""
   ack = struct.pack('B', 0xff)
   while ddata != ack:
      ddata = ser.read(1)
   return


if len(sys.argv) < 2:
   print ("no device specified")
   print ("You need to specify the serial port of the device you wish to connect to")
   print ("A second argument can be specified to change sampling rate to new value")
   print ("If no second argument the current sampling rate is read and displayed")
   print ("example (setting sampling rate to 51.2Hz):")
   print ("   samplingRate.py Com12")
   print ("or")
   print ("   samplingRate.py Com12 0x0280")
   print ("or")
   print ("   samplingRate.py /dev/rfcomm0")
   print ("or")
   print ("   samplingRate.py /dev/rfcomm0 640")
else:
   if len(sys.argv) == 2:
      ser = serial.Serial(sys.argv[1], 115200)
      ser.flushInput()
# send get sampling rate command
      ser.write(struct.pack('B', 0x6F))
      wait_for_ack()

# read incoming data
      ddata = ""
      numbytes = 0
      framesize = 4
      print(framesize)
      while numbytes < framesize:
         ddata = ser.read(framesize)
         numbytes = len(ddata)
         
      data = ddata[0:framesize]
      ddata = ddata[framesize:]
      numbytes = len(ddata)

      (dc0, dc1, dc2) = struct.unpack('BBB', data[1:4])
      print ("Current derived channel bytes: 0x%02x 0x%02x 0x%02x, %d " % (dc0, dc1, dc2, dc0+dc1*256+dc2*65536))
   elif len(sys.argv) == 3:
      newval = int(sys.argv[2])
      if 1 <= newval <= 16777216:
         ser = serial.Serial(sys.argv[1], 115200)
         ser.flushInput()
# send get sampling rate command
         ser.write(struct.pack('BBBB', 0x06d, (newval&0xFF), ((newval&0xFF00)>>8), ((newval&0xFF0000)>>16))) #need to be done this way due to alignment issues
         wait_for_ack()
         print ("derived channel bytes: 0x%02x 0x%02x 0x%02x, %d " % ((newval&0xFF), ((newval&0xFF00)>>8), ((newval&0xFF0000)>>16), newval))
      else:
         print ("%d is not a valid sampling rate\nMust be between 1 and 16777216" % newval)
#close serial port
   ser.close()
   print ("All done")