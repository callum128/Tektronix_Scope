import time
import matplotlib.pyplot as plt
import numpy as np
import pyvisa
from scipy import integrate

SCOPE_ADDRESS = 'GPIB0::1::INSTR'
RESOURCE_MANAGER = "@ivi"

rm = pyvisa.ResourceManager(RESOURCE_MANAGER)
scope = None
channel = 1

print("Connecting to oscilloscope...")
#print(rm.list_resources())

try:
    scope = rm.open_resource(SCOPE_ADDRESS)
    scope.timeout = 25000 

    print(scope.query("*IDN?").strip())

    scope.write(f"DATa:SOUrce CH{channel}")
    scope.write("DATa:ENCdg RIBINARY")
    scope.write("DATa:WIDth 2") #1, 2, 3, 4 don't work
    scope.write("DATa:STARt 1")
    scope.write("DATa:STOP 100000") 

    # Query scaling parameters from the preamble
    y_mult = float(scope.query("WFMOutpre:YMUlt?"))
    y_off  = float(scope.query("WFMOutpre:YOFf?"))
    y_zero = float(scope.query("WFMOutpre:YZEro?"))
    x_incr = float(scope.query("WFMOutpre:XINcr?"))
    x_zero = float(scope.query("WFMOutpre:XZEro?"))
    trigger_position = float(scope.query("HORizontal:MAIn:SCAle?"))

    print("Stopping acquisition and reading waveform data...")

    scope.write("ACQuire:STOPAfter SEQuence")

    # Read binary block data directly into a numpy array
    adc_samples = np.array(scope.query_binary_values("CURVe?", datatype='h', is_big_endian=True)) #b, h, d, f all don't work

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
    plt.ylabel("Voltage (V)")
    plt.legend()
    plt.show()


except pyvisa.VisaIOError as exc:
    print("VISA error:", exc)
except Exception as exc:
    print("Error:", exc)
finally:
    if scope is not None:
        scope.close()