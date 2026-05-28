import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from rex_utils import load_rex_data

unlicpped = "Outputs/Test_Scope_Driver_27_05_2026_16_40_22_296.toml"
bad_clipping = "Outputs/Test_Scope_Driver_27_05_2026_16_39_26_673.toml"
moving_mecrury_lamp = "Outputs/Test_Scope_Driver_28_05_2026_16_04_05_248.toml" #manually moving the spectrometer, off, mixed, on
moving_mecrury_lamp_2 = "Outputs/Test_Scope_Driver_28_05_2026_15_52_08_770.toml" #manually moving the spectrometer, on, off, off, on, on
test_stop = "Outputs/Test_Scope_Driver_28_05_2026_16_40_47_022.toml"
moving_mecrury_lamp_3 = "Outputs/Test_Scope_Driver_28_05_2026_16_45_22_142.toml" #manually moving the spectrometer, 543.1, 543.2, 543.3, 543.4nm

data_path = Path(__file__).parent / moving_mecrury_lamp_3

# Read in the rex toml data format, reads in only the .data layer, ignoring configurations etc.This handles importing nested data

# load a polars dataframe (recomended)
#data = load_rex_data(data_path, "polars")
# load a pandas dataframe
#data = load_rex_data(data_path, "pandas")
# if you want to read in a full validated data session, the seesion flag will do this
#data = load_rex_data(data_path, "session")

# raw dictionary
data = load_rex_data(data_path, "dict")

#ample_number = 0 #each times the experiment loops is a 'sample'

#waveforms = np.array(data['DPO7104_TekTronix_scope']['waveform'][sample_number])
#times = np.array(data['DPO7104_TekTronix_scope']['time_from_trigger'][sample_number])
#area = np.array(data['DPO7104_TekTronix_scope']['area'][sample_number])
#print(area)

# fig, ax = plt.subplots()
# ax.plot(times, waveforms, '.', label=f"Sample {sample_number}\n Area {area}")  
# plt.title("Oscilloscope Waveform")
# plt.xlabel("Time from Trigger (s)")
# plt.ylabel("Voltage (V)")
# plt.legend()
# plt.show()
samples = range(4)
fig, ax = plt.subplots(len(samples), sharey=True, figsize=(10, 6))
ax[0].set_ylim(-0.12, 0.02) #adjust as needed based on expected PMT pulse amplitude
for i, sample in enumerate(samples):
    waveforms = np.array(data['DPO7104_TekTronix_scope']['waveform'][i])
    times = np.array(data['DPO7104_TekTronix_scope']['time_from_trigger'][i])
    area = np.array(data['DPO7104_TekTronix_scope']['area'][i])
    ax[i].plot(times, waveforms, 'k.', label=f"Sample {sample}\n Area {area:.4e}")  
    ax[i].set_xlabel("Time from Trigger (s)")
    ax[i].set_ylabel("Voltage (V)")
    ax[i].legend(loc='lower right')
plt.show()
