import sys, struct, serial

def wait_for_ack():
	ddata = ""
	ack = struct.pack('B', 0xff)
	print(ack)
	while ddata != ack:
		ddata = ser.read(1)
		print("read: ", struct.unpack('B',ddata))
	return

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
try:
    inq_command = ser.write(struct.pack('B', 0x01))
    inq_response = list(ser.read(10))
    print(inq_response)

    #get the daughter card ID byte (SR number)
    print("Requesting Daughter Card ID and Revision number...")
    #print(struct.pack('BBB', 0x66, 0x02,0x00))
    ser.write(struct.pack('BBB', 0x66, 0x02,0x00))
    wait_for_ack()

    #print(ser.write(struct.pack('B', 0x01)))
    ddata = list(struct.unpack(4*'B', ser.read(4)))
    #print(len(ddata)) #length here is 4
    print("here")
    srNumber = ddata[2]
    srRev = ddata[3]
    print(ddata)
    #[101, 2, 47, 1]
    print("data: %d, %d, %d, %d" % (ddata[0], ddata[1], ddata[2], ddata[3]))
    print ("Device: SR%d-%d" % (srNumber, srRev))

    #sending inquiry response 
    inq_command = ser.write(struct.pack('B', 0x01))
    wait_for_ack()
    #ville ikke lese mer en 15 
    #reading the inquiry response 
    inq_response = list(struct.unpack(15*'B',ser.read(15)))
    print(inq_response)
    # first byte is the packet type
    #[2, 64, 0, 112, 14, 56, 9, 6, 1, 29, 35, 36, 32, 37, 38] ecg response 

    #sending GET_SAMPLING_RATE_COMMAND 0x03
    sample_rate_command = ser.write(struct.pack('B', 0x03))
    #wait for respone
    wait_for_ack()
    #SAMPLING_RATE_RESPONSE recieves sampling rate 
    samplerate = list(struct.unpack('BBB',ser.read(3)))
    print(samplerate)
    #[4, 64, 0] (ecg) 4 is which command/packet it is while 64, 0 are the samplerate values

    #send the set sensors command
    ser.write(struct.pack('BBBB', 0x08, 0x18, 0x00, 0x00))  #exg1 and exg2
    wait_for_ack()
    print ("Sensor Enabling done...")

    inq_command = ser.write(struct.pack('B', 0x01))
    wait_for_ack()
    #ville ikke lese mer en 15 
    #reading the inquiry response 
    inq_response = list(struct.unpack(15*'B',ser.read(15)))
    print("inq_respone: "+ inq_response)

except KeyboardInterrupt:
    #send stop streaming command
    ser.write(struct.pack('B', 0x20))
    wait_for_ack()
    #close serial port
    ser.close()
    print
    print ("All done!")
