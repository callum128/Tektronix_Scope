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

def step_data_puller(scope, new_size=50):
    """Pulls one point of the waveform data, then steps further and pulls again, to try to avoid overwhelming the scope's 
    CPU and saving massive data files. This is a bit of a hack, but you cannot change the scope's sampling rate (and thus 
    record length) without also changing the horizontal scale. If new_size is too big it will be very slow, but won't
    create massive data files."""
    total_points = int(scope.query("HORizontal:RECOrdlength?"))  #likely to be 100000 for real data
    step_size = total_points // new_size
    adc_samples = np.zeros(new_size)
    pull_log = 0
    for start in range(1, total_points+1, step_size):
        stop = min(start, total_points) #pulls 1 point every step
        scope.write(f"DATa:STARt {start}")
        scope.write(f"DATa:STOP {stop}")
        adc_samples[start//step_size] = (scope.query_binary_values("CURVe?", datatype='h', is_big_endian=True, container=np.ndarray))[0]
        pull_log += 1
    #print(f'Made: {pull_log} CURve? pulls')
    return np.array(adc_samples)


try:
    scope = rm.open_resource(SCOPE_ADDRESS)
    scope.timeout = 25000 

    print(scope.query("*IDN?").strip())

    scope.write(f"ACQuire:MODe SAMple")


    # print("Testing HORizontal:RECOrdlength...")
    # # Read original value first
    # orig_length = scope.query("HORizontal:RECOrdlength?").strip()
    # print(f"  Current Record Length: {orig_length} points")
    
    # Try setting to a smaller size (e.g., 5000 or 2500 depending on valid steps)
    # target_length = 10000
    # scope.write(f"HORizontal:RECOrdlength {target_length}")

    # # scale =  100E-6
    # # scope.write(f"HORizontal:MAIn:SCAle {scale}")

    # time.sleep(0.1)
    
    # Query back to verify change
    new_length = scope.query("HORizontal:RECOrdlength?").strip()
    print(f"  New Record Length Verified: {new_length} points")




    scope.write(f"DATa:SOUrce CH{channel}")
    scope.write("DATa:ENCdg RIBINARY")
    scope.write("DATa:WIDth 2") #1 byte, 2 byte, 4 byte, 8 byte data width. 2 byte is typical for Tektronix scopes, but check your scope's documentation to be sure. Using the wrong width can lead to incorrect data scaling and interpretation.
    
    # scope.write("DATa:STARt 1")
    # scope.write(f"DATa:STOP {new_length}")
    #try WAVFrm? for waveform preamble

    # sample_interval = 6.400E-6
    # scope.write(f"WFMPre:XINcr {sample_interval}")
    # print(scope.query("WFMPre?").strip())
    # print(scope.query(f"WFMPre:XINcr?"))


    # Query scaling parameters from the preamble
    y_mult = float(scope.query("WFMOutpre:YMUlt?"))
    y_off  = float(scope.query("WFMOutpre:YOFf?")) #24400 is real
    y_zero = float(scope.query("WFMOutpre:YZEro?"))
    x_incr = float(scope.query("WFMOutpre:XINcr?"))
    x_zero = float(scope.query("WFMOutpre:XZEro?"))
    trigger_position = float(scope.query("HORizontal:MAIn:SCAle?"))
    print(f"Queried scaling parameters: Y_Mult={y_mult}, Y_Off={y_off}, Y_Zero={y_zero}, X_Incr={x_incr}, X_Zero={x_zero}, Trigger_Position={trigger_position}")
    
    y_unit = scope.query("WFMOutpre:YUnit?").strip()
    x_unit = scope.query("WFMOutpre:XUnit?").strip()
    print(f'Y unit:{y_unit}')
    print(f'X unit:{x_unit}')

    record_length = int(scope.query("HORizontal:RECOrdlength?"))
    print(f"Record length: {record_length} points")

    time.sleep(0.5) #wait a bit to ensure the scope has time to process the queries and is ready for the next commands, adjust as needed based on the performance of your specific scope and computer
    acq = int(scope.query("ACQUIRE:NUMACQ?"))
    #print(f"Initial acquisition count: {acq}")

    # #scope.write('MEASUrement:GATing ON')
    # scope.write('MEASUrement:IMMed:TYPE AREA')
    # scope.write(f'MEASUrement:IMMed:SOUrce CH1')
    # scope.write('MEASUrement:IMMEd:STATE ON')
    # area = float(scope.query('MEASUrement:IMMEd:VALue?'))
    # print(area)
    # print(scope.query('MEASUrement:IMMEd:UNits?').strip())

    print("Stopping acquisition and reading waveform data...")

    scope.write("ACQuire:STOPAfter SEQuence")

    # # Read binary block data directly into a numpy array
    #adc_samples = np.array(scope.query_binary_values("CURVe?", datatype='h', is_big_endian=True)) #b, h, d, f depending on the data width set above. 'h' is 2 byte signed integer, which is common for Tektronix scopes. Adjust as needed based on your scope's data format and the width you set. The is_big_endian flag may also need to be adjusted based on your scope's data format. Check your scope's documentation for details on the binary data format it uses.

    adc_samples = step_data_puller(scope)

    print(f"Read {adc_samples.size} ADC samples from scope")
    scope.write("ACQuire:STOPAfter RUNSTOP")
    scope.write("ACQuire:STATE RUN")



    #print(f"Scaling parameters: Y_Mult={y_mult}, Y_Off={y_off}, Y_Zero={y_zero}, X_Incr={x_incr}, X_Zero={x_zero}, Trigger_Position={trigger_position}")
    #print(f"First 100 ADC samples: {adc_samples[:100]}")

    # Apply Tektronix scaling formula: Voltage = (ADC - Y_Offset) * Y_Multiplier + Y_Zero
    voltages = (adc_samples - y_off) * y_mult + y_zero
   # print(f"First 100 voltages: {voltages[:100]}")

    # Time axis: Time = Index * X_Increment + X_Zero - trigger_position (to align with trigger)
    time_axis = np.arange(0, int(new_length), step=int(new_length)//voltages.size) * x_incr + x_zero - trigger_position #relative to trigger, adjust as needed based on expected delay of PMT pulse after trigger

    fig, ax = plt.subplots()
    ax.plot(time_axis, voltages, 'k', label=f"Channel {channel}")  
    plt.title("Oscilloscope Waveform")
    plt.xlabel(f"Time ({x_unit})")
    plt.ylabel(f"Voltage ({y_unit})")
    plt.legend()
    plt.show()


except pyvisa.VisaIOError as exc:
    print("VISA error:", exc)
except Exception as exc:
    print("Error:", exc)
finally:
    if scope is not None:
        scope.close()