'''
This script connects to the Cyton board from OpenBCI through brainflow. 
8 EEG channels, and 3 accelerometer channels are then forwarded to lsl.
'''

import argparse
import time
import numpy as np

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

from pylsl import StreamInfo, StreamOutlet
#from queue import Queue

BoardShim.enable_dev_board_logger()

params = BrainFlowInputParams()
params.serial_port = 'COM3'

board = BoardShim(BoardIds.CYTON_BOARD.value, params) # added cyton board id here
srate = board.get_sampling_rate(BoardIds.CYTON_BOARD.value)
board.prepare_session()

board.start_stream()
#board.config_board('/2')  # enable analog mode only for Cyton Based Boards!    # added from example in docs


eeg_chan = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD.value)
aux_chan = BoardShim.get_accel_channels(BoardIds.CYTON_BOARD.value)
print('EEG channels:')
print(eeg_chan)
print('Accelerometer channels')
print(aux_chan)

# define lsl streams
# Defining stream info:
name = 'OpenBCIEEG'
ID = 'OpenBCIEEG'
channels = 8
sample_rate = 250
datatype = 'float32'
streamType = 'EEG'
print(f"Creating LSL stream for EEG. \nName: {name}\nID: {ID}\n")

info_eeg = StreamInfo(name, streamType, channels, sample_rate, datatype, ID)
chns = info_eeg.desc().append_child("channels")
for label in ["AFp1", "AFp2", "C3", "C4", "P7", "P8", "O1", "O2"]:
    ch = chns.append_child("channel")
    ch.append_child_value("label", label)

info_aux = StreamInfo('OpenBCIAUX', 'AUX', 3, 250, 'float32', 'OpenBCItestAUX')
chns = info_aux.desc().append_child("channels")
for label in ["X", "Y", "Z"]:
    ch = chns.append_child("channel")
    ch.append_child_value("label", label)

outlet_aux = StreamOutlet(info_aux)
outlet_eeg = StreamOutlet(info_eeg)

# construct a numpy array that contains only eeg channels and aux channels with correct scaling
# this streams to lsl
while True:
    data = board.get_board_data() # this gets data continiously

    # don't send empty data
    if len(data[0]) < 1 : continue
       
    eeg_data = data[eeg_chan]
    aux_data = data[aux_chan]
    #print(scaled_eeg_data)
    #print(scaled_aux_data)
    #print('------------------------------------------------------------------------------------------')
    eegchunk = []
    for i in range(len(eeg_data[0])):
        eegchunk.append((eeg_data[:,i]).tolist())
    outlet_eeg.push_chunk(eegchunk)
    auxchunk = []
    for i in range(len(aux_data[0])):
        auxchunk.append((aux_data[:,i]).tolist())
    outlet_aux.push_chunk(auxchunk)    