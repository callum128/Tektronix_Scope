import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import integrate, signal
from scipy.interpolate import PchipInterpolator 

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
sample3P03H4_4886 = 'Outputs/(3P0)1D2-3H4_488.65_emission_scopeTEST_14_07_2026_10_53_14_237.toml'
sample3P03H4_4882 = 'Outputs/(3P0)1D2-3H4_488.25_emission_scope_14_07_2026_12_33_52_765.toml'
sample3P03H5_test = 'Outputs/3P0-3H5_488.3_emission_scopeTEST_14_07_2026_14_23_30_846.toml'
sample3P03H5 = 'Outputs/3P0-3H5_488.3_emission_scope_14_07_2026_14_40_44_075.toml'
sample3P03H6_test = 'Outputs/3P0-3H6_488.35_emission_scope_ampTEST_15_07_2026_09_31_30_422.toml'
sample3P03H6_test2 = 'Outputs/3P0-3H6_488.35_emission_scope_ampTEST2_15_07_2026_09_54_00_531.toml'
sample3P03H6 = 'Outputs/3P0-3H6_488.35_emission_scope_amp_15_07_2026_10_12_10_468.toml'
sample3P03F2 = 'Outputs/3P0-3F2_488.35_emission_scope_amp_15_07_2026_13_43_32_484.toml'
sample3P03F3_test = 'Outputs/3P0-3F33F4_488.7_emission_scope_ampTEST_21_07_2026_09_48_14_527.toml'
sample3P03F3_4884test = 'Outputs/3P0-3F33F4_488.4_emission_scope_ampTEST2_21_07_2026_10_17_40_310.toml'
sample3P03F3 = 'Outputs/3P0-3F33F4_488.7_emission_scope_amp_21_07_2026_10_38_53_510.toml'
sample3P03H6_dgates_test= 'Outputs/3P0-3H6_488.7_emission_scope_amp_dgatesTEST_21_07_2026_14_47_25_888.toml'
sample3P03H6_dgates = 'Outputs/3P0-3H6_488.7_emission_scope_amp_dgates_21_07_2026_15_00_39_175.toml'
sample3P03H5_test2 = 'Outputs/3P0-3H5_488.75_emission_scope_amp_longTEST_22_07_2026_09_10_14_338.toml'
sample3P03H6_sgates = 'Outputs/3P0-3H6_488.7_emission_scope_amp_sgates_quick_21_07_2026_16_57_04_816.toml'

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
        shifted_wavenumbers = np.ones_like(wavenumbers) *start_laser-wavenumbers+off #need to change this to do the offset on the wavelengths, then convert to wavenumbers
        norm_areas = (areas-min(areas))/max(areas) +(y_offset_multiplier-1.0)*y_offset
        ax.plot(shifted_wavenumbers, norm_areas, label=name, color=color)

        area_peaks, _ = signal.find_peaks(norm_areas, prominence=prominence, distance=distance) #adjust height as needed based on expected peak amplitudes
        for i in area_peaks:
                ax.annotate(f'{shifted_wavenumbers[i]:.1f}', xy=(shifted_wavenumbers[i], norm_areas[i]), xytext=(5, 10), textcoords='offset points', color=color, fontsize=7)


title = 'Emission Spectra'
fig, ax = plt.subplots()
start_laser = 16524 #the lowest top multiplet from the monitored transition, ideally the laser wavelength

#wavenumbers, areas = loader(sample3H6_test)
#shifted_wavenumbers = np.ones_like(wavenumbers) *start_laser-wavenumbers-0.0  #shift so the first point is at 0 cm^-1 for 3H4, adjust as needed based on expected peak positions
#ax.plot(wavenumbers, areas, label='Spectra')

# wavenumbers, areas = loader(sample3P03H6)
# areas = (areas-min(areas))/max(areas)
# ax.plot(wavenumbers, areas, label='3P0-3H6 Spectra small gates')

# wavenumbers, areas = loader(sample3H4_580)
# areas = (areas-min(areas))/max(areas)
# ax.plot(wavenumbers, areas, label='1D2-3H4 Spectra')

# wavenumbers, areas = loader(sample3P03F2)
# areas = (areas-min(areas))/max(areas)
# ax.plot(wavenumbers, areas, label='3P0-3F2 Spectra')

# wavenumbers, areas = loader(Indirect_3H4)
# areas = (areas-min(areas))/max(areas)
# ax.plot(wavenumbers+65, areas, label='Test(3P0)1D2-3H4 Spectra')

# wavenumbers, areas = loader(sample3P03H4_4882)
# areas = (areas-min(areas))/max(areas)
# ax.plot(wavenumbers, areas, label='(3P0)1D2-3H4 Spectra')

# jon_data = np.loadtxt('Outputs/598nm-683nm 0.1nm step P0 to H6.dat', skiprows=1)
# wavelnumbers_jon = 1e7/(jon_data[:,0][-500:-1])
# areas_jon = jon_data[:,1][-500:-1]
# areas_jon = (areas_jon-min(areas_jon))/max(areas_jon)
# ax.plot(wavelnumbers_jon+10, areas_jon, label='Jon\'s Data 3P0-3F2')

wavenumbers1, areas1 = loader(sample3P03H6)
#areas = (areas-min(areas))/max(areas)
ax.plot(wavenumbers1, areas1*1.45, label='Old Spectra, intensity multiplied by 1.45', linestyle='dotted', color='k')

wavenumbers2, areas2 = loader(sample3P03H6_dgates)
#areas = (areas-min(areas))/max(areas)
ax.plot(wavenumbers2, areas2, label='34us time gates Spectra')

wavenumbers3, areas3 = loader(sample3P03H6_sgates)
#areas = (areas-min(areas))/max(areas)
ax.plot(wavenumbers3, areas3, label='17us time gates Spectra (0.08 stepsize)')

areas3_resized = PchipInterpolator(1e7/wavenumbers3, areas3)(1e7/wavenumbers2)
endclip = 100
ax.plot(wavenumbers2[:-endclip], areas3_resized[:-endclip], label='17us time gates Spectra resized', linestyle='dashed')

fixed_areas = areas3_resized*2 - areas2 #Not sure if this is the way Jon meant
ax.plot(wavenumbers2[:-endclip], fixed_areas[:-endclip], label='Fixed Spectra with 1D2 subtracted out')

fixed_areas2 = areas1*1.45*2 - areas2 #Not sure if this is the way Jon meant
ax.plot(wavenumbers2[:-endclip], fixed_areas2[:-endclip], label='Fixed Spectra with 1D2 subtracted out (Old Spectra)')

title = '3P0-3H6 Emission Spectra with Different Time Gates'

# wavenumbers, areas = loader(sample3P03H5)
# #areas = (areas-min(areas))/max(areas)
# ax.plot(wavenumbers, areas, label='Spectra')

# wavenumbers, areas = loader(sample3P03H5_test2)
# #areas = (areas-min(areas))/max(areas)
# ax.plot(wavenumbers, areas, label='Spectra')

ax.invert_xaxis()


# y_offset = 0.05
# off1 = 72.15
# off2 = -2.17
# off3 = 58.65

# wavenumbers, areas = loader(sample3P03H4_4882)
# step_size = np.mean(np.diff(1e7/wavenumbers))
# name = f'Indirect 488.20 (3P0) Data\n{step_size:.2f} step, 7 avg, 0.1 slits'
# color = 'orange'
# plot_areas(wavenumbers, areas, name, ax, off=off1, color=color, prominence=0.01, distance=20, y_offset_multiplier=2.0)

# # wavenumbers, areas = loader(sample3P03H4_4886)
# # step_size = np.mean(np.diff(1e7/wavenumbers))
# # name = f'Indirect 488.65(3P0) Data\n{step_size:.2f} step, 2 avg, 0.1 slits'
# # color = 'hotpink'
# # plot_areas(wavenumbers, areas, name, ax, off=off1+0.54, color=color, prominence=0.01, distance=20, y_offset_multiplier=3.0)

# wavenumbers, areas = loader(Direct_3H4)
# step_size = np.mean(np.diff(1e7/wavenumbers))
# name = f'Site 1 Direct 576.90 (1D2) Data\n{step_size:.2f} step, 4 avg, 0.1 slits, amplified'
# color = 'r'
# plot_areas(wavenumbers, areas, name, ax, off=off2, color=color, prominence=0.01, distance=20, y_offset_multiplier=4.0)

# wavenumbers, areas = loader(sample3H4_580)
# step_size = np.mean(np.diff(1e7/wavenumbers))
# name = f'Direct 580.00 (1D2) Data\n{step_size:.2f} step, 8 avg, 0.1 slits, amplified'
# color = 'b'
# plot_areas(wavenumbers, areas, name, ax, off=70.5, color=color, prominence=0.01, distance=20, y_offset_multiplier=3.0)

# jon_data = np.loadtxt('Outputs/600nm-650nm 0.01nm step D2 to H4 (2).dat', skiprows=1)
# wavelnumbers_jon = 1e7/jon_data[:,0]
# areas_jon = jon_data[:,1]
# name = 'Jon\'s Data'
# color = 'g'
# plot_areas(wavelnumbers_jon, areas_jon, name, ax, off=off3, color=color, prominence=0.01, distance=20, y_offset_multiplier=1.0)


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
secax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
ax.grid()
ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
ax.set_ylabel('Intensity')
ax.tick_params(axis = 'x')
ax.tick_params(axis = 'y')
ax.set_title(title)
plt.legend()
plt.show()