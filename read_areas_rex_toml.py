import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate, signal

from pathlib import Path
from rex_utils import load_rex_data

sample = 'Outputs/Zoomed_out_quick_600_645_Test_Emission_Experiment_05_06_2026_16_31_54_372.toml'
ten_avg_sample = 'Outputs/Avg_quick_600_645_Test_Emission_Experiment_05_06_2026_17_42_57_278.toml'

data_path = Path(__file__).parent / ten_avg_sample

# Read in the rex toml data format, reads in only the .data layer, ignoring configurations etc.This handles importing nested data

# load a polars dataframe (recomended)
data = load_rex_data(data_path, "polars")

areas = np.array(data['DPO7104_TekTronix_scope_area'])
print(f'First 10 areas from the scope: {areas[:10]}')
spec_wavelengths = np.array(data['iHR550_wavelength (nm)'])
print(f'First 10 spectrometer wavelengths: {spec_wavelengths[:10]}')

wavenumbers = 1e7 / spec_wavelengths

fig, ax = plt.subplots()

shifted_wavenumbers = -(wavenumbers - 16504-24.65) #shift so the first point is at 0 cm^-1 for 3H4, adjust as needed based on expected peak positions

ax.plot(shifted_wavenumbers, areas)

area_peaks, _ = signal.find_peaks(areas, height=0.001) #adjust height as needed based on expected peak amplitudes
ax.plot(shifted_wavenumbers[area_peaks], areas[area_peaks], 'rx', label='Peaks')
for i in area_peaks:
    ax.annotate(f'{shifted_wavenumbers[i]:.2f} cm$^{{-1}}$', xy=(shifted_wavenumbers[i], areas[i]), xytext=(10, 10), textcoords='offset points', color='red', fontsize=7)

def cmnminvert(x):
        """ 
        returns 1/x with special treatment of x == 0
        used to plot two axes - see below. 
        """
        #print('x:', x)
        x = np.array(x).astype(float)
        near_zero = np.isclose(x, 0)
        x[near_zero] = np.inf
        x[~near_zero] = 1.0e7 / x[~near_zero]
        return x

ax.set_xlabel('Wavenumber (cm$^{-1}$)')
secax = ax.secondary_xaxis('top', functions=(cmnminvert, cmnminvert))  #to put wavelength on top
secax.set_xlabel('Wavelength (nm)')
secax.tick_params(axis = 'x')
# note the double backslash: \\alpha
ax.set_ylabel('Intensity (mV*s)')
ax.tick_params(axis = 'x')
ax.tick_params(axis = 'y')
ax.set_title('Emission Areas')
plt.show()