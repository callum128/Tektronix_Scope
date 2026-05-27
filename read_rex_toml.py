import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from rex_utils import load_rex_data

unlicpped = "Outputs/Test_Scope_Driver_27_05_2026_16_40_22_296.toml"
bad_clipping = "Outputs/Test_Scope_Driver_27_05_2026_16_39_26_673.toml"

data_path = Path(__file__).parent / unlicpped

# Read in the rex toml data format, reads in only the .data layer, ignoring configurations etc.This handles importing nested data

# load a polars dataframe (recomended)
#data = load_rex_data(data_path, "polars")
# load a pandas dataframe
#data = load_rex_data(data_path, "pandas")
# if you want to read in a full validated data session, the seesion flag will do this
#data = load_rex_data(data_path, "session")

# raw dictionary
data = load_rex_data(data_path, "dict")

sample_number = 0 #each times the experiment loops is a 'sample'

waveforms = np.array(data['DPO7104_TekTronix_scope']['waveform'][sample_number])
times = np.array(data['DPO7104_TekTronix_scope']['time_from_trigger'][sample_number])
area = np.array(data['DPO7104_TekTronix_scope']['area'][sample_number])
print(area)

fig, ax = plt.subplots()
ax.plot(times, waveforms, '.', label=f"Sample {sample_number}\n Area {area}")  
plt.title("Oscilloscope Waveform")
plt.xlabel("Time from Trigger (s)")
plt.ylabel("Voltage (V)")
plt.legend()
plt.show()
