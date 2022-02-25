import threading
import time
import random
from ECG_to_LSL import ECG_to_LSL
#from EEG_to_LSL import EEG_to_LSL
from GSR_to_LSL import GSR_to_LSL
import sys


def thread_function(name, sleep_time):
    print(f"Thhread starting {name}")
    time.sleep(random.randint(1, 50))
    print(f"Thhread done lol {name}")

def main():

    print("Heiheihiei")
    comX = sys.argv[1]          
    comY = sys.argv[2]

    x = threading.Thread(target=ECG_to_LSL, args=(comY,))
    y = threading.Thread(target=GSR_to_LSL, args=(comX, ))
    
    x.start()
    y.start()



if __name__ == "__main__":
    print("asd")
    main()
