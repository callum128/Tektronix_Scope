import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pathlib import Path
from rex_utils import load_rex_data

def single_exponential(t, A, tau, y0):
    return A * np.exp(-t / tau) + y0

def double_exponential(t, A1, tau1, A2, tau2, y0):
    return A1 * np.exp(-t / tau1) + A2 * np.exp(-t / tau2) + y0

def no_rise(v_all, t_all):
    #cut to find slope from trigger start
    #v_start = np.searchsorted(t_all, 0.0)
    v_all = -v_all
    v_start = np.argmax(v_all) -0 #fit start at the clean top
    v_end = -1 #np.argmax(v_all)+30
    
    v = v_all[v_start:v_end]
    t = t_all[v_start:v_end]
    
    # 3. Provide initial guesses (Crucial for curve_fit)
    # Guess A as max voltage, tau as reasonable time, y0 as baseline/end value
    initial_guesses = [max(v), (t[-1] - t[0])/10, min(v)]
    print(initial_guesses)
    
    # 4. Fit the curve
    popt, pcov = curve_fit(single_exponential, t, v, p0=initial_guesses)
    print(popt)
    
    # Extract fitted parameters
    A_fit, tau_fit, y0_fit = popt
    print(f"Fitted Lifetime (tau): {tau_fit:.5e} seconds")
    
    # 5. Calculate Fits and Residuals for plotting
    v_fit = single_exponential(t, A_fit, tau_fit, y0_fit)
    residuals = v - v_fit
    
    # 6. Plotting
    ax.set_xlabel('Time from Trigger (s)', fontsize=20, labelpad=3)
    ax.set_ylabel('Voltage (V)', fontsize=20, labelpad=3)
    ax.plot(t_all, v_all, 'k.')
    ax.vlines(t[0], min(v_all), max(v_all), linestyle='dashed', label='fit start')
    
    ax.plot(t, v_fit, 'r', label=f'Tau={tau_fit:.3e} s')
    title = (f'Lifetime')
    ax.set_title(title, fontsize=20)
    plt.legend(loc='center right', fontsize=20)
    plt.tight_layout()

def risetime(v_all, t_all):
    v_all = -v_all
    v_start = np.argmax(v_all) -27 #fit start at inital rise
    v_end = -1 #np.argmax(v_all)+500
    
    v = v_all[v_start:v_end]
    t = t_all[v_start:v_end]
    
    # 3. Provide initial guesses (Crucial for curve_fit)
    # Guess A as max voltage, tau as reasonable time, y0 as baseline/end value
    initial_guesses = [-max(v), (t[-1] - t[0])/100, max(v)/10, (t[-1] - t[0])/10, min(v)]
    #initial_guesses = [-1.0e-2, 1.0e-5, 1.0e-4, 1.5e-4, min(v)]
    print(initial_guesses)
    
    # 4. Fit the curve
    popt, pcov = curve_fit(double_exponential, t, v, p0=initial_guesses)
    print(popt)
    
    # Extract fitted parameters
    A_fit, tau_fit, A2_fit, tau2_fit, y0_fit = popt
    print(f"Fitted Rise Time (tau2): {tau2_fit:.6e} seconds")
    
    # 5. Calculate Fits and Residuals for plotting
    v_fit = double_exponential(t, A_fit, tau_fit, A2_fit, tau2_fit, y0_fit)
    residuals = v - v_fit
    
    # 6. Plotting
    ax.set_xlabel('Time from Trigger (s)', fontsize=20, labelpad=3)
    ax.set_ylabel('Voltage (V)', fontsize=20, labelpad=3)
    ax.plot(t_all, v_all, 'k.')
    ax.vlines(t[0], min(v_all), max(v_fit), linestyle='dashed', label='fit end')
    
    ax.plot(t, v_fit, 'r', label=f'Tau1={tau_fit:.3e} s\nTau2={tau2_fit:.3e} s')
    title = (f'Rise Time')
    ax.set_title(title, fontsize=20)
    plt.legend(loc='center right', fontsize=20)
    plt.tight_layout()


odd_1D2_3H4_lifetime = 'Outputs/(3P0)1D2-3H4_488.35nm_Test_Lifetime_Experiment_16_06_2026_11_41_23_899.toml'
lifetime_3P0_3H5 = 'Outputs/3P0-3H5_488.35nm_Lifetime_16_06_2026_14_03_58_850.toml'
lifetime_3P0_3F3 = 'Outputs/3P0-3F3_488.35nm_Lifetime_16_06_2026_16_04_14_279.toml'
lifetime_3P0_PC = 'Outputs/3P0_544.36_488.35_lifetime_scope_test_17_06_2026_16_28_03_077.toml'
lifetime_3P0_PC_sparse = 'Outputs/3P0_544.36_488.35_lifetime_scope_test_sparse_17_06_2026_16_32_38_246.toml'
#=======
life3H4_site1 = 'Outputs/1D2-3H4_577.0_50ohm_lifetime_scope_605.33_30_06_2026_09_12_27_582.toml'
life3H4_site1_other = 'Outputs/1D2-3H4_577.0_50ohm_lifetime_scope_611.93_30_06_2026_09_37_11_570.toml'
life1G4 = 'Outputs/1D2-1G4_606.50_50ohm_lifetime_scope_30_06_2026_11_00_29_600.toml'
life3H4_bigslit = 'Outputs/1D2-3H4_580.2_50ohm_lifetime_scope_13_07_2026_16_47_16_368.toml' #0.2 slits, need to redo for 0.1
life3H5 = 'Outputs/1D2-3H5_606.35_50ohm_lifetime_scope_22_06_2026_12_33_45_333.toml'
life3P0_1D2_3H4 = 'Outputs/(3P0)1D2-3H4_488.2_50ohm_lifetime_scope_14_07_2026_10_34_31_169.toml'
life3P0_1D2_3H4_bigslits = 'Outputs/(3P0)1D2-3H4_488.2_50ohm_lifetime_scope_bigslits_14_07_2026_10_22_02_048.toml'
life3P0_1D2_3H4_unknown = 'Outputs/(3P0)1D2-3H4_488.65_50ohm_lifetime_scope_14_07_2026_11_35_41_178.toml'
life3P0_3H5 = 'Outputs/3P0-3H5_488.3_50ohm_lifetime_scope_14_07_2026_16_20_14_217.toml'
life3P0_3H6_616 = 'Outputs/3P0-3H6_488.35_50ohm_lifetime_scope_15_07_2026_12_18_35_756.toml'
life3P0_3H6_615 = 'Outputs/3P0-3H6_488.35_50ohm_lifetime_scope_615_15_07_2026_12_37_08_674.toml'
life3P0_3H6_607 = 'Outputs/3P0-3H6_488.35_50ohm_lifetime_scope_607_15_07_2026_12_56_00_366.toml'
life3P0_3H6_621 = 'Outputs/3P0-3H6_488.35_50ohm_lifetime_scope_621_15_07_2026_17_34_27_687.toml'
life3P0_3F3 = 'Outputs/3P0-3F3_488.7_50ohm_lifetime_scope_21_07_2026_14_20_47_002.toml'

life3P0_3F2_647 = 'Outputs/3P0-3F2_488.35_50ohm_lifetime_scope_647_15_07_2026_16_37_12_584.toml'
life3P0_3F2_648 = 'Outputs/3P0-3F2_488.35_50ohm_lifetime_scope_648_15_07_2026_16_51_27_487.toml'
life3P0_3F2_649 = 'Outputs/3P0-3F2_488.35_50ohm_lifetime_scope_649_15_07_2026_17_02_51_812.toml'
life3P0_3F2_650 = 'Outputs/3P0-3F2_488.35_50ohm_lifetime_scope_650_15_07_2026_17_13_01_161.toml'
life3P0_3F2_653 = 'Outputs/3P0-3F2_488.35_50ohm_lifetime_scope_653_15_07_2026_17_23_00_868.toml'
life3P0_3F2_657 = 'Outputs/3P0-3F2_488.35_50ohm_lifetime_scope_657_15_07_2026_17_28_44_365.toml'

data_path = Path(__file__).parent / life3P0_3F3
title = '1D2-3H5 Lifetime'
data = load_rex_data(data_path, "polars")

waveforms = np.array(data['DPO7104_TekTronix_scope_waveform'][0])
time_params = np.array(data['DPO7104_TekTronix_scope_time_from_trigger_parameters'][0])
#spec_wavelength = np.array(data['iHR550_wavelength (nm)'][0])

print(time_params)

times = np.arange(0, time_params[0], step=time_params[1]) * time_params[2] + time_params[3] - time_params[4]
fig, ax = plt.subplots(figsize=(9,5))

no_rise(waveforms, times)
#risetime(waveforms, times)

#ax.plot(times, waveforms)
plt.title(title)
plt.show()