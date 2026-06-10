import time
import matplotlib.pyplot as plt
import numpy as np
import pyvisa
from scipy import integrate

SCOPE_ADDRESS = 'GPIB0::1::INSTR'
#RESOURCE_MANAGER = "@ivi"

rm = pyvisa.ResourceManager()
scope = None
channel = 1

print(rm.list_resources())
print("Connecting to oscilloscope...")

def step_data_puller(scope, channel=1):
    """Pulls a few points of the waveform data, then step further and pulls again, to try to avoid overwhelming the scope's 
    CPU and causing it to crash. This is a bit of a hack, but it will probably work."""
    scope.write(f"DATa:SOUrce CH{channel}")
    scope.write("DATa:ENCdg RIBINARY")
    scope.write("DATa:WIDth 2") #1 byte, 2 byte, 4 byte, 8 byte data width. 2 byte is typical for Tektronix scopes, but check your scope's documentation to be sure. Using the wrong width can lead to incorrect data scaling and interpretation.
    scope.write("DATa:STARt 1")
    total_points = int(scope.query("HORizontal:RECOrdlength?")) 
    print(f"Record length: {total_points} points")
    smaller_size = 5000
    step_size = int(total_points / smaller_size) #adjust as needed based on the performance of your specific scope and computer, and the total number of points. This is the number of points to pull in each step.
    adc_samples = [] 
    for start in range(1, total_points+1, step_size):
        stop = min(start + step_size - 1, total_points)
        scope.write(f"DATa:STARt {start}")
        scope.write(f"DATa:STOP {stop}")
        adc_samples.extend(scope.query_binary_values("CURVe?", datatype='h', is_big_endian=True)) #need to make a faster, safer np array thing
        #time.sleep(0.1)
    return np.array(adc_samples)


try:
    scope = rm.open_resource(SCOPE_ADDRESS)
    scope.timeout = 25000 

    print(scope.query("*IDN?").strip())

    #breakpoint()

    scope.write(f"ACQuire:MODe SAMple") #set to sample

    # scope.write(f"DATa:SOUrce CH{channel}")
    # scope.write("DATa:ENCdg RIBINARY")
    # scope.write("DATa:WIDth 2") #1 byte, 2 byte, 4 byte, 8 byte data width. 2 byte is typical for Tektronix scopes, but check your scope's documentation to be sure. Using the wrong width can lead to incorrect data scaling and interpretation.
    # scope.write("DATa:STARt 1")
    # scope.write("DATa:STOP 100000") #try 2500 as the command for all
    # #try WAVFrm? for waveform preamble


    # Query scaling parameters from the preamble
    y_mult = float(scope.query("WFMOutpre:YMUlt?"))
    y_off  = float(scope.query("WFMOutpre:YOFf?")) #24400 is real
    y_zero = float(scope.query("WFMOutpre:YZEro?"))
    x_incr = float(scope.query("WFMOutpre:XINcr?"))
    x_zero = float(scope.query("WFMOutpre:XZEro?"))
    trigger_position = float(scope.query("HORizontal:MAIn:SCAle?"))
    #print(f"Queried scaling parameters: Y_Mult={y_mult}, Y_Off={y_off}, Y_Zero={y_zero}, X_Incr={x_incr}, X_Zero={x_zero}, Trigger_Position={trigger_position}")
    
    record_length = int(scope.query("HORizontal:RECOrdlength?"))
    print(f"Record length: {record_length} points")

    time.sleep(0.5) #wait a bit to ensure the scope has time to process the queries and is ready for the next commands, adjust as needed based on the performance of your specific scope and computer
    acq = int(scope.query("ACQUIRE:NUMACQ?"))
    print(f"Initial acquisition count: {acq}")

    print("Stopping acquisition and reading waveform data...")

    scope.write("ACQuire:STOPAfter SEQuence")

    # # Read binary block data directly into a numpy array
    # adc_samples = np.array(scope.query_binary_values("CURVe?", datatype='h', is_big_endian=True)) #b, h, d, f depending on the data width set above. 'h' is 2 byte signed integer, which is common for Tektronix scopes. Adjust as needed based on your scope's data format and the width you set. The is_big_endian flag may also need to be adjusted based on your scope's data format. Check your scope's documentation for details on the binary data format it uses.

    adc_samples = step_data_puller(scope, channel=channel)

    print(f"Read {adc_samples.size} ADC samples from scope")
    scope.write("ACQuire:STOPAfter RUNSTOP")
    scope.write("ACQuire:STATE RUN")


    print(f"Scaling parameters: Y_Mult={y_mult}, Y_Off={y_off}, Y_Zero={y_zero}, X_Incr={x_incr}, X_Zero={x_zero}, Trigger_Position={trigger_position}")
    print(f"First 100 ADC samples: {adc_samples[:100]}")

    # Apply Tektronix scaling formula: Voltage = (ADC - Y_Offset) * Y_Multiplier + Y_Zero
    voltages = (adc_samples - y_off) * y_mult + y_zero
    print(f"First 100 voltages: {voltages[:100]}")

    # Time axis: Time = Index * X_Increment + X_Zero - trigger_position (to align with trigger)
    time_axis = np.arange(adc_samples.size) * x_incr + x_zero - trigger_position #relative to trigger, adjust as needed based on expected delay of PMT pulse after trigger

    fig, ax = plt.subplots()
    ax.plot(time_axis, voltages, '.', label=f"Channel {channel}")  
    plt.title("Oscilloscope Waveform")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (mV)")
    plt.legend()
    plt.show()


except pyvisa.VisaIOError as exc:
    print("VISA error:", exc)
except Exception as exc:
    print("Error:", exc)
finally:
    if scope is not None:
        scope.close()