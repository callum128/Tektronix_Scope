import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from rex_utils import load_rex_data

data_path = Path(__file__).parent / "Outputs/Test_Scope_Driver_27_05_2026_16_24_03_779.toml"

# Read in the rex toml data format, reads in only the .data layer, ignoring configurations etc.This handles importing nested data

# load a polars dataframe (recomended)
#data = load_rex_data(data_path, "polars")
# load a pandas dataframe
#data = load_rex_data(data_path, "pandas")
# if you want to read in a full validated data session, the seesion flag will do this
#data = load_rex_data(data_path, "session")

# raw dictionary
data = load_rex_data(data_path, "dict")

sample_number = 0

waveforms = np.array(data['DPO7104_TekTronix_scope']['waveform'][sample_number])
times = np.array(data['DPO7104_TekTronix_scope']['time_from_trigger'][sample_number])

fig, ax = plt.subplots()
ax.plot(times, waveforms, '.', label=f"Sample {sample_number}")  
plt.title("Oscilloscope Waveform")
plt.xlabel("Time from Trigger (s)")
plt.ylabel("Voltage (V)")
plt.legend()
plt.show()
