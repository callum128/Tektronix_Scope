Driver and example code to use the DPO7104 Tektronix oscilloscope for automated experiments, such as emission. Should work better than the current C8835 photon counter as a detector for short lifetimes. Uses a GPIB-USB knockoff Keysight Technologies cable to physically connect to the lab computer and pyvisa.
Uses Jamin Martin's Rex and Rex_utils (https://github.com/JaminMartin/rex) to integrate into the current workflow. Should be adaptable for the boxcar integrator. 
Run using the command: rex run .\measurement.py -o .\Outputs\
