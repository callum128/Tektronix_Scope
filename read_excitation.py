import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate, signal
import toml
import tomllib

# Load a TOML file
with open("Outputs/694.94_excitation_22_06_2026_16_52_18_261.toml", "rb") as f:
    data = tomllib.load(f)

# The data is parsed directly into a standard Python dictionary
wavelengths = np.array(data['device']['GL100_Dye_Laser']['data']["desired wavelength (nm)"]['data'])
