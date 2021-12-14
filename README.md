# Project Thesis

This repository is part of our prosject thesis, where the goal is to connect Shimmer sensor units to the LSL network.

In our research to decode the Shimmer units, we have copied and played around with the scripts from ShimmerReserch's GitHub repository for SHimmer3 units. The scripts can be found [here](https://github.com/ShimmerResearch/shimmer3/tree/master/LogAndStream/python_scripts).

The scripts worth noticing are ShimmmerCommands, GSR_to_LSL.py, and ECG_to_LSL.py. Togheter these scripts creates an output stream which is collected by the LSL network.

## Table of content

- [Installation](#installation)
  - [Conda](#conda)
  - [PIP](#pip)
  - [LabRecorder](#labrecorder)
- [Usage](#usage)
  - [Linux](#linux)
  - [Windows](#windows)
  - [Run Experiment](#run-experiment)

## Installation

In order to run this repository, and use LSL follow these steps. The setup is tested on both linux and windows operative system.

It is good practice to use virtual environments, in order to have control of the installed packages and libraries. You can eighter use Anaconda and the conda environment, or install virtualenvironment. Both guides are given below.

### Conda

If you dont have Anaconda already installed, you can follow [the Windows guide](https://www.datacamp.com/community/tutorials/installing-anaconda-windows) for installation. Or if you have linux you can follw [the Linux guide](https://www.datacamp.com/community/tutorials/installing-anaconda-windows). Open your terminal or Anaconda prompt and follow the steps:

Create and activate Anaconda environment:

```
conda create --name your_environment
```

Windows activation:

```
conda activate your_environment
```

Linux activation:

```
source conda activate your_environment
```

Install LSL:

```
conda install -c tstenner pylsl
```

Install Serial Port:

```
conda install pyserial
```

Type y when conda asks you to proceed

### PIP

If you dont have PyPI already installed, you can follow [the Windows guide](https://phoenixnap.com/kb/install-pip-windows) for installation. Or if you have linux, follow [the Linux guide](https://www.geeksforgeeks.org/how-to-install-pip-in-linux/).

Create and activate virtual environment with virtualenv package

```
pip install virtualenv  && virtualenv your_environment
```

Windows activation:

```
your_environment\Scripts\activate
```

Linux activation:

```
source your_environment/bin/activate
```

Install LSL

```
pip install pylsl
```

Install Serial Port

```
pip install pyserial
```

### LabRecorder

The program can be downloaded through LSL's own [GitHub repository](https://github.com/labstreaminglayer/App-LabRecorder/releases). The program is cross-platform, supported by the popular operative system such as Windows, OSX, Android, and Linux. The dependencies of the program must be downloaded and installed if the program is running on Linux Ubuntu. 

## Usage

LabRecorder has a user-friendly interface, making it easy to start the recording session. The interface consists of three sections. A Recording control section where the user can start and stop the recording. A Record from Streams section where all available device streams are displayed, and lastly a Saving to section, where the location of the file is displayed, in addition to configuration settings of the file. 

If only specific streams are wanted they can be selected as needed. LabRecorder must be updated if a device is turned on after initiating the program. When the setup is ready, the user can start recording the measurements.

First you have to connect to the Shimmer sensor units. This is done differently on Windows and Linux.

### Linux

To run the scripts and connect to the sensor units, you need admin priveleges.

First you need to find the MAC-address, by running:

```
hcitool scan
```

The output will look something like this:

```
00:06:66:D7:C6:F2	Shimmer3-C6F2
```

Check that there are no other serial connections running.

```
sudo killall rfcomm
```

Connect to the Shimmer with:

```
sudo rfcomm connect /dev/rfcomm0 <MAC-adress> 1 &
```

When connecting to the sensors for the first time a window will pop up on the screen and ask you to type in a pin code. This pin code is:

```
1234
```

### Windows

Connect to the Shimmer sensor units through the Bluetooth UI. This is found under bluetooth setting. Click on "Add Bluetooth or other device", then on "Bluetooth". Find the shimmer device you want to connect and doubble click on it. It will ask you for a pin, type in the pin "1234" => connect => done

To check which comport it is using the device is using, click on "More Bluetooth options" => "Com Ports". Here you will see overview of COM ports, the direction and name of device. If the device do not have an outgoing COM port already you have to add on by clicking "Add...", check of for outgoing, find the device in the dropdown list and click "Ok". Note which COM port the device have, because when you are running the scripts you need to know which comport to use.

### Run Experiment

1. Open LabRecorder.
2. To conduct the experiment with the Shimmer sensors and LabRecorder you have to run the scripts ECG_to_LSL.py and GSR_to_LSL.py in seperate terminals/command prompts. 

  Linux:

    ```
    sudo python3 ECG_to_LSL.py /dev/rfcomm0
    ```
    ```
    sudo python3 GSR_to_LSL.py /dev/rfcomm0
    ```
  Windows:

   ```
   python ECG_to_LSL.py <COMPORT>
   ```

   ```
   python GSR_to_LSL.py <COMPORT>
   ```

<!-- ... RunExperiment.py. The sensors are now available to the LSL network.
   Linux:

   ```
   sudo python3 RunExperiment.py /dev/rfcomm0
   ```

   Windows:

   ```
   python RunExperiment.py <COMPORT>
   ```-->

3. Update LabRecorder and select the sensors you want.
4. Start experiment. Both RunExperiment.py and LabRecorder must run simultaniously in order to collect data.
5. Stop experiment. The data will be saved to an xdf file.
6. View the data by running xdf.py, before running the script, it have to be modifed to have the correct file path. 

  ```
  data, header = pyxdf.load_xdf('file_path')
  ```
