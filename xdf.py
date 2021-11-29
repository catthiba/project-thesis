
import pyxdf
import matplotlib.pyplot as plt
import numpy as np

data, header = pyxdf.load_xdf('gsr_test2.xdf')

for stream in data:
    y = np.array(stream['time_series'])

    if isinstance(y, list):
        print('her isinstance')

        # list of strings, draw one vertical line for each marker
        for timestamp, marker in zip(np.array(stream['time_stamps']), y):
            plt.axvline(x=timestamp)
            print(f'Marker "{marker[0]}" @ {timestamp:.2f}s')
    elif isinstance(y, np.ndarray):
        # numeric data, draw as lines
        # print('x: ', np.array(stream['time_stamps']), 'y: ', y)
        plt.plot(np.array(stream['time_stamps']), y)
    else:
        raise RuntimeError('Unknown stream format')

plt.show()