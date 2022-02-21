from ECG_to_LSL import ECG_to_LSL
from EEG_to_LSL import EEG_to_LSL
from GSR_to_LSL import GSR_to_LSL

import sys

class RunExperiment:
    
    def __init__(self):
        comX = sys.argv[1]
        comY = sys.argv[2]

        gsr = GSR_to_LSL(comX)
        gsr.GSR_setup()
        ecg = ECG_to_LSL(comY)
        ecg.ECG_setup()
        #eeg = EEG_to_LSL()
        #eeg.EEG_setup()

RunExperiment()