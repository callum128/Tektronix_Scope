import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import integrate, signal

from pathlib import Path
from rex_utils import load_rex_data

sample = 'Outputs/Zoomed_out_quick_600_645_Test_Emission_Experiment_05_06_2026_16_31_54_372.toml'
ten_avg_sample = 'Outputs/Avg_quick_600_645_Test_Emission_Experiment_05_06_2026_17_42_57_278.toml'
big_gates = 'Outputs/Emission_(3P0)1D2_3H4_big_gate_488.35_experiment_16_06_2026_12_24_23_976.toml'
small_gates = 'Outputs/Emission_(3P0)1D2_3H4_small_gate_488.35_experiment_16_06_2026_13_18_35_617.toml'
sample = 'Outputs/Emission_3P0_3H5_488.35_experiment_TEST_16_06_2026_14_35_24_778.toml'
sample = 'Outputs/Emission_3P0_3H5_488.35_experiment_16_06_2026_14_48_36_780.toml'
sample = 'Outputs/Emission_3P0_3F3_488.35_experiment_TEST_16_06_2026_16_12_33_447.toml'
sample = 'Outputs/Emission_3P0_3F2_488.35_experiment_16_06_2026_16_31_54_403.toml'
sample = 'Outputs/1D2-3H5_606.35_emission_scope_TEST_22_06_2026_13_32_58_466.toml'
sample = 'Outputs/1D2-3H5_606.35_emission_scopeAMP_TEST_22_06_2026_13_54_10_344.toml'
sample3H5 = 'Outputs/1D2-3H5_606.35_emission_scope_amp_22_06_2026_14_10_14_891.toml'
sample ='Outputs/1D2-3H6_606.50_emission_scope_amp_TEST_23_06_2026_10_23_53_723.toml'
sample = 'Outputs/1D2-3F2_606.50_emission_scope_amp_23_06_2026_14_56_44_370.toml'
sample3H6 = 'Outputs/1D2-3H6_606.50_emission_scope_amp_23_06_2026_10_46_40_147.toml'
sample3H5end = 'Outputs/1D2-3H5_end_606.50_emission_scope_amp_29_06_2026_11_12_59_398.toml'
sample3H4 = 'Outputs/1D2-3H4_576.90_emission_scope_ampTEST2_29_06_2026_12_50_00_417.toml'
sample = 'Outputs/1D2-3H4_576.90_emission_scope_ampTEST3_29_06_2026_15_44_28_791.toml'
sample = 'Outputs/1D2-1G4_emission_scopeTEST_30_06_2026_10_23_45_257.toml'
Indirect_3H4 = 'Outputs/Emission_(3P0)1D2_3H4_big_gate_488.35_experiment_16_06_2026_12_24_23_976.toml'
Direct_3H4 = 'Outputs/1D2-3H4_576.90_emission_scope_amp_2_29_06_2026_15_54_39_353.toml'
sample = 'Outputs/1D2-1G4_emission_scope_30_06_2026_11_26_28_142.toml'
sample3H4_580_amp = 'Outputs/1D2-3H4_580.2_emission_scope_ampTEST_13_07_2026_10_57_27_635.toml'
sample3H4_580_no_amp = 'Outputs/1D2-3H4_580.2_emission_scope_no_ampTEST_13_07_2026_11_28_14_950.toml'
sample3H4_580 = 'Outputs/1D2-3H4_580.2_emission_scope_amp_13_07_2026_12_03_47_480.toml'
sample3H6_test = 'Outputs/1D2-3H6_606.45_emission_scope_ampTEST_13_07_2026_14_40_34_165.toml'
sample3H6_full = 'Outputs/1D2-3H6_606.45_emission_scope_amp_13_07_2026_14_53_02_724.toml'
sample3P03H4_4882 = 'Outputs/(3P0)1D2-3H4_488.2_emission_scopeTEST_14_07_2026_09_55_22_863.toml'

def loader(filename):

        data_path = Path(__file__).parent / filename

        # Read in the rex toml data format, reads in only the .data layer, ignoring configurations etc.This handles importing nested data

        # load a polars dataframe (recomended)
        data = load_rex_data(data_path, "polars")

        areas = np.array(data['DPO7104_TekTronix_scope_area'])
        print(f'First 10 areas from the scope: {areas[:10]}')
        spec_wavelengths = np.array(data['iHR550_wavelength (nm)'])
        print(f'Spec wavelength range: {spec_wavelengths[0]} - {spec_wavelengths[-1]}')

        wavenumbers = 1e7 / spec_wavelengths

        return wavenumbers, areas


def plot_areas(wavenumbers, areas, name, ax, off=0.0, color='k', prominence=0.01, distance=20, y_offset_multiplier=1.0):
        shifted_wavenumbers = np.ones_like(wavenumbers) *start_laser-wavenumbers+off
        norm_areas = (areas-min(areas))/max(areas) +(y_offset_multiplier-1.0)*y_offset
        ax.plot(shifted_wavenumbers, norm_areas, label=name, color=color)
        area_peaks, _ = signal.find_peaks(norm_areas, prominence=prominence, distance=distance) #adjust height as needed based on expected peak amplitudes
        for i in area_peaks:
                ax.annotate(f'{shifted_wavenumbers[i]:.1f}', xy=(shifted_wavenumbers[i], norm_areas[i]), xytext=(5, 10), textcoords='offset points', color=color, fontsize=7)



fig, ax = plt.subplots()
start_laser = 16524 #the lowest top multiplet from the monitored transition, ideally the laser wavelength

#wavenumbers, areas = loader(sample3H6_test)
#shifted_wavenumbers = np.ones_like(wavenumbers) *start_laser-wavenumbers-0.0  #shift so the first point is at 0 cm^-1 for 3H4, adjust as needed based on expected peak positions
#ax.plot(wavenumbers, areas, label='Spectra')

# wavenumbers, areas = loader(sample3P03H4_4882)
# ax.plot(wavenumbers, areas, label='3P0 Spectra')

# wavenumbers, areas = loader(sample3H4_580)
# ax.plot(wavenumbers, areas, label='580 Spectra')

# wavenumbers, areas = loader(Direct_3H4)
# ax.plot(wavenumbers, areas, label='576 Spectra')

# ax.invert_xaxis()


y_offset = 0.1
off1 = 72.7
off2 = -2.17
off3 = 58.65

wavenumbers, areas = loader(sample3P03H4_4882)
step_size = np.mean(np.diff(1e7/wavenumbers))
name = f'Indirect (3P0) Data\n{step_size:.2f} step, 15 avg, 0.2 slits'
color = 'm'
plot_areas(wavenumbers, areas, name, ax, off=off1, color=color, prominence=0.01, distance=20, y_offset_multiplier=2.0)

wavenumbers, areas = loader(Direct_3H4)
step_size = np.mean(np.diff(1e7/wavenumbers))
name = f'Direct 576 (1D2) Data\n{step_size:.2f} step, 4 avg, 0.1 slits, amplified'
color = 'r'
plot_areas(wavenumbers, areas, name, ax, off=off2, color=color, prominence=0.01, distance=20, y_offset_multiplier=3.0)

wavenumbers, areas = loader(sample3H4_580)
step_size = np.mean(np.diff(1e7/wavenumbers))
name = f'Direct 580 (1D2) Data\n{step_size:.2f} step, 8 avg, 0.1 slits, amplified'
color = 'b'
plot_areas(wavenumbers, areas, name, ax, off=70.5, color=color, prominence=0.01, distance=20, y_offset_multiplier=4.0)

jon_data = np.loadtxt('Outputs/600nm-650nm 0.01nm step D2 to H4 (2).dat', skiprows=1)
wavelnumbers_jon = 1e7/jon_data[:,0]
areas_jon = jon_data[:,1]
name = 'Jon\'s Data'
color = 'g'
plot_areas(wavelnumbers_jon, areas_jon, name, ax, off=off3, color=color, prominence=0.01, distance=20, y_offset_multiplier=1.0)

ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())

# area_peaks, _ = signal.find_peaks(norm_areas, height=0.00001, distance=80) #adjust height as needed based on expected peak amplitudes
# ax.plot(shifted_wavenumbers[area_peaks], norm_areas[area_peaks], 'rx', label='Peaks')
# for i in area_peaks:
#    ax.annotate(f'{shifted_wavenumbers[i]:.2f} cm$^{{-1}}$', xy=(shifted_wavenumbers[i], norm_areas[i]), xytext=(10, 10), textcoords='offset points', color='red', fontsize=7)



def cmnminvert(x):
        x = np.array(x).astype(float)
        near_zero = np.isclose(x, 0)
        x[near_zero] = np.inf
        x[~near_zero] = 1.0e7 / x[~near_zero]
        return x

ax.set_xlabel('Wavenumber (cm$^{-1}$)')
secax = ax.secondary_xaxis('top', functions=(cmnminvert, cmnminvert))  #to put wavelength on top
secax.set_xlabel('Wavelength (nm)')
secax.tick_params(axis = 'x')
ax.set_ylabel('Intensity')
ax.tick_params(axis = 'x')
ax.tick_params(axis = 'y')
ax.set_title('Emission Spectra')
plt.legend()
plt.show()