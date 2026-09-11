import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import integrate, signal
from scipy.interpolate import PchipInterpolator 

from pathlib import Path
from rex_utils import load_rex_data


s1_1D2 = 'Outputs/Excitation/S1/EX_S1_1D2_from_1D2-1G4_excitationTEST_25_08_2026_14_04_17_027.toml'
s1_1D2_test ='Outputs/Excitation/S1/EX_S1_1D2_from_1D2-1G4_excitation_ampTEST_26_08_2026_13_08_16_351.toml'
s2_1D2_test = 'Outputs/Excitation/S2/EX_S2_1D2_from_1D2-1G4_excitation_ampTEST_25_08_2026_17_06_27_481.toml'
s2_1D2 = 'Outputs/Excitation/S2/EX_S2_1D2_from_1D2-1G4_excitation_amp_26_08_2026_09_35_06_735.toml'
s2_1D2_end = 'Outputs/Excitation/S2/EX_S2_1D2_from_1D2-1G4_excitation_amp_end_26_08_2026_12_29_14_384.toml'
s2_1D2_R610_test = 'Outputs/Excitation/S2/EX_S2_1D2_from_1D2-1G4_excitation_R610dyeTEST_26_08_2026_14_24_10_151.toml'
s2_1D2_R610 = 'Outputs/Excitation/S2/EX_S2_1D2_from_1D2-1G4_excitation_R610dye_26_08_2026_15_05_25_131.toml'
s1_1D2_R610_test = 'Outputs/Excitation/S1/EX_S1_1D2_from_1D2-1G4_excitation_R610dyeTEST_26_08_2026_16_20_38_769.toml'
s1_1D2_R610 = 'Outputs/Excitation/S1/EX_S1_1D2_from_1D2-1G4_excitation_R610dye_27_08_2026_09_19_18_610.toml'
s2_3P0_test = 'Outputs/Excitation/S2/EX_S2_3P0_from_1D2-1G4_excitation_C481dyeTEST_27_08_2026_10_43_41_699.toml'
s2_3P0 = 'Outputs/Excitation/S2/EX_S2_3P0_from_1D2-1G4_excitation_C481_27_08_2026_11_36_09_371.toml'
s1_3P0_test = 'Outputs/Excitation/S1/EX_S1_3P0_from_1D2-1G4_excitation_C481TEST_27_08_2026_14_22_30_681.toml'
s1_3P0 = 'Outputs/Excitation/S1/EX_S1_3P0_from_1D2-1G4_excitation_C481_27_08_2026_15_04_57_328.toml'
s2_3P0_C460_test = 'Outputs/Excitation/S2/EX_S2_3P2_from_1D2-1G4_excitation_C460TEST_02_09_2026_10_06_07_429.toml'
s2_1I6_C460_test = 'Outputs/Excitation/S2/EX_S2_1I6_from_1D2-1G4_excitation_C460TEST_07_09_2026_10_42_42_152.toml'
s2_1I6 = 'Outputs/Excitation/S2/EX_S2_1I6_from_1D2-1G4_excitation_C460_07_09_2026_11_15_51_423.toml'
s1_1I6_test = 'Outputs/Excitation/S1/EX_S1_1I6_from_1D2-1G4_excitation_C460TEST_07_09_2026_13_18_27_785.toml'
s1_1I6 = 'Outputs/Excitation/S1/EX_S1_1I6_from_1D2-1G4_excitation_C460_07_09_2026_13_45_43_970.toml'
s2_3P2_C440_test = 'Outputs/Excitation/S2/EX_S2_3P2_from_1D2-1G4_excitation_C440TEST_07_09_2026_16_06_14_032.toml'
s2_3P2_C440_test2 = 'Outputs/Excitation/S2/EX_S2_3P2_from_1D2-1G4_excitation_C440TEST2_11_09_2026_09_19_28_165.toml'
s2_3P2_C440 = 'Outputs/Excitation/S2/EX_S2_3P2_from_1D2-1G4_excitation_C440_11_09_2026_09_43_01_266.toml'
s1_3P2_C440_test = 'Outputs/Excitation/S1/EX_S1_3P2_from_1D2-1G4_excitation_C440_TEST_11_09_2026_12_19_44_539.toml'
s1_3P2_C440 = 'Outputs/Excitation/S1/EX_S1_3P2_from_1D2-1G4_excitation_C440_11_09_2026_12_46_42_025.toml'
s2_3P0_C500_test = 'Outputs/Excitation/S2/EX_S2_3P0_from_1D2-1G4_excitation_C500_TEST_11_09_2026_14_55_38_686.toml'

def ex_loader(filename, initial_wavelength, final_wavelength):
        data_path = Path(__file__).parent / filename
        data = load_rex_data(data_path, "polars")

        areas = np.array(data['DPO7104_TekTronix_scope_area'])
        print(f'First 10 areas from the scope: {areas[:5]}')


        #wavelengths = np.arange(initial_wavelength, final_wavelength + n*step_size, step_size)
        wavelengths = np.linspace(initial_wavelength, final_wavelength, len(areas))
        print(f'Laser wavelength range: {wavelengths[0]} - {wavelengths[-1]}')

        wavenumbers = 1e7 / wavelengths

        return wavelengths, areas

y2 = 0.0001
# w,a = ex_loader(s2_3P0_test, 470, 505)
# plt.plot(w, a+y2, label='s2_3P0_test')
   
w,a = ex_loader(s2_3P0, 460, 500)
plt.plot(w, a+y2, label='s2_3P0')

# w,a = ex_loader(s1_3P0_test, 460, 505)
# plt.plot(w, a, label='s1_3P0_test')
        
w,a = ex_loader(s1_3P0, 465, 495)
plt.plot(w, a, label='s1_3P0')

w,a = ex_loader(s2_1I6, 435, 480)
plt.plot(w, a+y2, label='s2_1I6')

w,a = ex_loader(s1_1I6, 435, 480)
plt.plot(w, a, label='s1_1I6')

w,a = ex_loader(s2_3P2_C440, 420, 460)
plt.plot(w, a+y2, label='s2_3P2_C440')

w,a = ex_loader(s1_3P2_C440, 425, 455)
plt.plot(w, a, label='s1_3P2_C440')

w,a = ex_loader(s2_3P0_C500_test, 475, 510)
plt.plot(w, a+2*y2, label='s2_3P0_C500_test')

plt.title('Excitation Spectrum')
plt.xlabel('Laser Wavelength (nm)')
plt.ylabel('Intensity (V*s)')
plt.legend()
plt.show()