Driver and example code to use the DPO7104 Tektronix oscilloscope for experiments, such as emission and lifetimes. Should work better than the current C8835 photon counter as a detector for short lifetimes. Uses a GPIB-USB knockoff Keysight Technologies cable to physically connect to the lab computer and pyvisa.
Uses Jamin Martin's Rex (https://github.com/JaminMartin/rex) to integrate into the current workflow. Should be adaptable for the boxcar integrator. Now included with https://github.com/JaminMartin/spcs_instruments.

For our specific GPIB-USB adapter, this requires Keysight Technologies IOLS, and may require changing the registory HKEY_LOCAL_MACHINE\SOFTWARE\National Instruments\NI-VISA\ni488.dll to path to the agvisa.dll, and making sure Keysight VISA is prefered over the NI for GPIB, so that pyvisa can see it. 

Run using the command: rex run .\measurement.py -o .\Outputs\
