import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pathlib import Path
from rex_utils import load_rex_data

def single_exponential(t, A, tau, y0):
    return A * np.exp(-t / tau) + y0

def double_exponential(t, A1, tau1, A2, tau2, y0):
    return A1 * np.exp(-t / tau1) + A2 * np.exp(-t / tau2) + y

odd_1D2_3H4_lifetime = 'Outputs/(3P0)1D2-3H4_488.35nm_Test_Lifetime_Experiment_16_06_2026_11_41_23_899.toml'
lifetime_3P0_3H5 = 'Outputs/3P0-3H5_488.35nm_Lifetime_16_06_2026_14_03_58_850.toml'
lifetime_3P0_3F3 = 'Outputs/3P0-3F3_488.35nm_Lifetime_16_06_2026_16_04_14_279.toml'

data_path = Path(__file__).parent / lifetime_3P0_3H5
data = load_rex_data(data_path, "polars")

waveforms = np.array(data['DPO7104_TekTronix_scope_waveform'][0])
time_params = np.array(data['DPO7104_TekTronix_scope_time_from_trigger_parameters'][0])
spec_wavelength = np.array(data['iHR550_wavelength (nm)'][0])

print(time_params)

times = np.arange(0, time_params[0], step=time_params[1]) * time_params[2] + time_params[3] - time_params[4]
fig, ax = plt.subplots(figsize=(14,8))
def no_rise(v_all, t_all):
    #cut to find slope from trigger start
    #v_start = np.searchsorted(t_all, 0.0)
    v_all = -v_all
    v_start = np.argmax(v_all) +0 #fit start at the clean top
    
    v = v_all[v_start:-1]
    t = t_all[v_start:-1]
    
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
    
    ax.plot(t, v_fit, 'r', label=f'Tau={tau_fit:.5e} s')
    title = (f'Lifetime')
    ax.set_title(title, fontsize=20)
    plt.legend(loc='center right', fontsize=20)
    plt.tight_layout()

no_rise(waveforms, times)

#ax.plot(times, waveforms)
plt.show()