import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate, signal

from pathlib import Path
from rex_utils import load_rex_data

def trigger_dependent_custom_integration(time_axis, voltages, start_time, end_time):
    """Integrate the waveform in a window defined relative to the trigger. NOPE, THE TIME AXIS IS ALREADY RELATIVE TO THE TRIGGER, SO JUST USE THE OFFSETS AS ABSOLUTE TIMES"""
    
    print(f"Integrating from {start_time:.3e} s to {end_time:.3e} s relative to trigger at zero seconds")

    start_index = np.searchsorted(time_axis, start_time, side="left")
    end_index = np.searchsorted(time_axis, end_time, side="right")
    plt.vlines(time_axis[start_index], ymin=min(voltages), ymax=max(voltages), colors='g', linestyles='--', label="Calculated Start Index")
    plt.vlines(time_axis[end_index], ymin=min(voltages), ymax=max(voltages), colors='c', linestyles='--', label="Calculated End Index")

    #Savgol filter
    sav_voltages = np.array(signal.savgol_filter(voltages, 41, 3)) # window length 31, polynomial order 3
    plt.plot(time_axis, sav_voltages, 'k', label="Smoothed Voltages")
    plt.hlines(sav_voltages[start_index], xmin=min(time_axis), xmax=max(time_axis), colors='g', linestyles='--', label="Smoothed Start Level")
    plt.hlines(sav_voltages[end_index], xmin=min(time_axis), xmax=max(time_axis), colors='c', linestyles='--', label="Smoothed End Level")
    
    if start_index < 0 or end_index > len(voltages) or start_index >= end_index:
        raise ValueError("Integration bounds are out of range of the data")

    # if START_OFFSET_S < 0:
    #     print("!!!Warning: Start offset is negative. This breaks the comparison with the scope's gated area measurement, which uses the actual time axis for integration. The calculated area may differ from the scope's measurement due to this offset.")
    #     shifted_time_axis = time_axis + 1e-5 #shift time axis to avoid negative times for integration, doesn't change the relative positions of the points, just makes it easier to interpret the integration window
    #     shifted_voltages = voltages
    #     print(f"Start index for integration: {start_index}, shifted time at start index: {shifted_time_axis[start_index]:.3e} s")
    #     integrated_value = integrate.trapezoid(
    #         shifted_voltages[start_index:end_index], shifted_time_axis[start_index:end_index]
    #     )
    else:
        #print(f"Start index for integration: {start_index}, time at start index: {time_axis[start_index]:.3e} s")
        integrated_value = integrate.trapezoid(
            sav_voltages[start_index:end_index], time_axis[start_index:end_index] #doesn't match the scope's gated area measurement if negative offset
        ) #trapezoid is worse, but more inline with what the scope area calculates

    summed_value = np.sum(sav_voltages[start_index:end_index])

    return integrated_value, summed_value

unlicpped = "Outputs/Test_Scope_Driver_27_05_2026_16_40_22_296.toml"
bad_clipping = "Outputs/Test_Scope_Driver_27_05_2026_16_39_26_673.toml"
moving_mecrury_lamp = "Outputs/Test_Scope_Driver_28_05_2026_16_04_05_248.toml" #manually moving the spectrometer, off, mixed, on
moving_mecrury_lamp_2 = "Outputs/Test_Scope_Driver_28_05_2026_15_52_08_770.toml" #manually moving the spectrometer, on, off, off, on, on
test_stop = "Outputs/Test_Scope_Driver_28_05_2026_16_40_47_022.toml"
moving_mecrury_lamp_3 = "Outputs/Test_Scope_Driver_28_05_2026_16_45_22_142.toml" #manually moving the spectrometer, 543.1, 543.2, 543.3(on), 543.4 nm
trigger = "Outputs/Test_Scope_Driver_29_05_2026_11_44_57_966.toml"
blank = 'Outputs/Test_Scope_Driver_29_05_2026_15_22_32_054.toml'
test = 'Outputs/Test_Scope_Driver_29_05_2026_15_41_52_436.toml'

pospos = 'Outputs/Pos_Pos_bounds_29_05_2026_15_50_14_959.toml'
negpos = 'Outputs/Neg_Pos_far_bounds_29_05_2026_16_14_14_339.toml'
negneg = 'Outputs/Neg_Neg_bounds_29_05_2026_16_18_42_839.toml'

data_path = Path(__file__).parent / negneg

# Read in the rex toml data format, reads in only the .data layer, ignoring configurations etc.This handles importing nested data

# load a polars dataframe (recomended)
data = load_rex_data(data_path, "polars")
# load a pandas dataframe
#data = load_rex_data(data_path, "pandas")
# if you want to read in a full validated data session, the seesion flag will do this
#data = load_rex_data(data_path, "session")

# raw dictionary
#data = load_rex_data(data_path, "dict")

#print(data.head())

sample_number = 0 #each times the experiment loops is a 'sample'

waveforms = np.array(data['DPO7104_TekTronix_scope_waveform'][sample_number])
times = np.array(data['DPO7104_TekTronix_scope_time_from_trigger'][sample_number])
area = np.array(data['DPO7104_TekTronix_scope_area'][sample_number])
print(f'Area from the scope: {area:.4e}')


fig, ax = plt.subplots()
start, stop = -9e-4, -1e-4 #match the toml

computed_area, summed_area = trigger_dependent_custom_integration(times, waveforms, start, stop)
computed_area = -computed_area #negate to match the scope's convention of negative area for downward pulses, adjust as needed based on your specific waveform and expected pulse polarity
print(f"Computed area from the waveform: {computed_area:.4e}")
print(f'Difference compared to scope area: {computed_area / area:.2f} times the scope area')

box_area =-1* (8e-4) * (abs(max(waveforms)) - abs(min(waveforms)))
print(f"Area of the bounding box defined by the integration window and waveform amplitude: {box_area:.4e}")
print(f"Box - Computed: {box_area - computed_area:.4e}")


ax.plot(times, waveforms, '.', label=f"Sample {sample_number}\n Area {area:.4e}")  
plt.vlines(start, ymin=min(waveforms), ymax=max(waveforms), colors='r', linestyles='--', label="Start")
plt.vlines(stop, ymin=min(waveforms), ymax=max(waveforms), colors='m', linestyles='--', label="Stop")
plt.title("Oscilloscope Waveform")
plt.xlabel("Time from Trigger (s)")
plt.ylabel("Voltage (V)")
plt.legend()
plt.show()

# samples = range(4)
# fig, ax = plt.subplots(len(samples), sharey=True, figsize=(10, 6))
# ax[0].set_ylim(-0.12, 0.02) #adjust as needed based on expected PMT pulse amplitude
# for i, sample in enumerate(samples):
#     waveforms = np.array(data['DPO7104_TekTronix_scope_waveform'][i])
#     times = np.array(data['DPO7104_TekTronix_scope_time_from_trigger'][i])
#     area = np.array(data['DPO7104_TekTronix_scope_area'][i])
#     ax[i].plot(times, waveforms, 'k.', label=f"Sample {sample}\n Area {area:.4e}")  
#     ax[i].set_xlabel("Time from Trigger (s)")
#     ax[i].set_ylabel("Voltage (V)")
#     ax[i].legend(loc='lower right')
# plt.show()
