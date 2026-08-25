import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import integrate, signal
from scipy.interpolate import PchipInterpolator 

from pathlib import Path
from rex_utils import load_rex_data


s1_1D2 = 'Outputs/Excitation/S1/EX_S1_1D2_from_1D2-1G4_excitationTEST_25_08_2026_14_04_17_027.toml'

def ex_loader(filename):
        data_path = Path(__file__).parent / filename
        data = load_rex_data(data_path, "polars")

        areas = np.array(data['DPO7104_TekTronix_scope_area'])
        print(f'First 10 areas from the scope: {areas[:5]}')


        inital_wavelength = 570
        final_wavelength = 610
        step_size = 0.02
        wavelengths = np.arange(inital_wavelength, final_wavelength + 2*step_size, step_size)
        print(f'Laser wavelength range: {wavelengths[0]} - {wavelengths[-1]}')

        wavenumbers = 1e7 / wavelengths

        return wavelengths, areas

w,a = ex_loader(s1_1D2)
plt.plot(w, a)
plt.title('Excitation Spectrum')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Scope Area (V*s)')
plt.show()