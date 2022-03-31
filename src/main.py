import threading
import time
import random
from ECG_to_LSL import ECG_to_LSL
from EEG_to_LSL import EEG_to_LSL
from GSR_to_LSL import GSR_to_LSL
import sys



def main():
    comX = sys.argv[1]          
    comY = sys.argv[2]
    comUSB = 'Com3' #/dev/tty2'

    gsr = threading.Thread(target=GSR_to_LSL, args=(comX, ))
    ecg = threading.Thread(target=ECG_to_LSL, args=(comY,))
    eeg = threading.Thread(target=EEG_to_LSL, args=(comUSB,))
    
    gsr.start()
    ecg.start()
    eeg.start()



if __name__ == "__main__":
    main()
