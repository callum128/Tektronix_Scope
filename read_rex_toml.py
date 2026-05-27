from pathlib import Path

from rex_utils import load_rex_data

data_path = Path(__file__).parent / "Outputs\Test_Scope_Driver_27_05_2026_15_59_20_509.toml"

# Read in the rex toml data format, reads in only the .data layer, ignoring configurations etc.This handles importing nested data
# e.g data in the form of a series of traces from an osciliscope, but you will have to handle those "slices" directly.

# load a polars dataframe (recomended)
#data = load_rex_data(data_path, "polars")
#print(data)

# load a pandas dataframe
#data = load_rex_data(data_path, "pandas")
#print(data)


# raw dictionary
data = load_rex_data(data_path, "dict")
print(data['DPO7104_TekTronix_scope']['waveform'][0]) #seems to dupe the waveform and trigger and time data when all requested


# if you want to read in a full validated data session, the seesion flag will do this
#data = load_rex_data(data_path, "session")
#print(data)
