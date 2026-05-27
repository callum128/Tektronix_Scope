import time
from tkinter import NONE
from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np
import pyvisa
from scipy import integrate

# --- Configuration ---
SCOPE_ADDRESS = 'GPIB0::1::INSTR'
RESOURCE_MANAGER = "@ivi"
DEFAULT_AVERAGES = 1032
TRIGGER_LEVEL_V = None   # None to auto-set based on signal, or set manually to a value just at the tip of the trigger pulse
START_OFFSET_S = 1e-6 #time from trigger to start of integration window, adjust based on expected delay of PMT pulse after trigger
END_OFFSET_S = 13e-6
PLOT_VISIBLE = True


def trigger_dependent_custom_integration(
    trigger_time: float,
    start_offset: float,
    end_offset: float,
    time_axis: np.ndarray,
    voltages: np.ndarray,
) -> float:
    """Integrate the waveform in a window defined relative to the trigger. NOPE, THE TIME AXIS IS ALREADY RELATIVE TO THE TRIGGER, SO JUST USE THE OFFSETS AS ABSOLUTE TIMES"""
    start_time = start_offset
    end_time = end_offset
    print(f"Integrating from {start_time:.3e} s to {end_time:.3e} s relative to trigger at {trigger_time:.3e} s")

    start_index = np.searchsorted(time_axis, start_time, side="left")
    end_index = np.searchsorted(time_axis, end_time, side="right")

    if start_index < 0 or end_index > len(voltages) or start_index >= end_index:
        raise ValueError("Integration bounds are out of range of the data")

    if START_OFFSET_S < 0:
        print("!!!Warning: Start offset is negative. This breaks the comparison with the scope's gated area measurement, which uses the actual time axis for integration. The calculated area may differ from the scope's measurement due to this offset.")
        shifted_time_axis = time_axis + 1e-5 #shift time axis to avoid negative times for integration, doesn't change the relative positions of the points, just makes it easier to interpret the integration window
        shifted_voltages = voltages
        print(f"Start index for integration: {start_index}, shifted time at start index: {shifted_time_axis[start_index]:.3e} s")
        integrated_value = integrate.trapezoid(
            shifted_voltages[start_index:end_index], shifted_time_axis[start_index:end_index]
        )
    else:
        print(f"Start index for integration: {start_index}, time at start index: {time_axis[start_index]:.3e} s")
        integrated_value = integrate.trapezoid(
            voltages[start_index:end_index], time_axis[start_index:end_index] #doesn't match the scope's gated area measurement if negative offset
        ) #trapezoid is worse, but more inline with what the scope area calculates

    summed_value = np.sum(voltages[start_index:end_index]) #* (time_axis[1] - time_axis[0]) #do I need the time axis? what best approximated the intensity

    return integrated_value, summed_value


def lifetime_from_exponential_fit(time_axis: np.ndarray, voltages: np.ndarray, trigger_time=0.0) -> float:
    """Fits an exponential decay to the data and extracts the lifetime."""
    from scipy.optimize import curve_fit

    start_index = np.searchsorted(time_axis, trigger_time + START_OFFSET_S, side="left")
    end_index = np.searchsorted(time_axis, trigger_time + END_OFFSET_S, side="right")

    time_axis_cut = time_axis[start_index:end_index] + 3e-6
    voltages_cut = voltages[start_index:end_index]

    def exp_decay(t, A, tau, C):
        return A * np.exp(-t / tau) + C

    # Initial guess: A = max-min, tau = (max time - min time)/5, C = min
    A_guess = np.max(voltages_cut) - np.min(voltages_cut)
    tau_guess = (time_axis_cut[-1] - time_axis_cut[0]) / 5
    C_guess = np.min(voltages_cut)

    popt, _ = curve_fit(exp_decay, time_axis_cut, voltages_cut, p0=[A_guess, tau_guess, C_guess])
    _, tau_fit, _ = popt

    if PLOT_VISIBLE:
        plt.figure()
        plt.plot(time_axis_cut, voltages_cut, "k.", label="Data")
        plt.plot(time_axis_cut, exp_decay(time_axis_cut, *popt), "r-", label=f"Exp Fit (tau={tau_fit:.3e} s)")
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (V)")
        plt.title("Exponential Decay Fit")
        plt.legend()
        plt.show()

    return tau_fit


def _plot_waveform(
    time_axis: np.ndarray,
    voltages: np.ndarray,
    start_time: float,
    end_time: float,
    integral: float,
    sum_value: float,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(time_axis, voltages, "k.", label="Waveform")
    ax.axvline(start_time, color="r", linestyle="--", label="Integration start")
    ax.axvline(end_time, color="m", linestyle="--", label="Integration end")
    ax.set_xlabel("Time from Trigger (s)")
    ax.set_ylabel("Voltage (V)")
    ax.set_title(f"Integration window: {integral:.3e} V·s (Voltage Sum: {sum_value:.3e} V)")
    fig.tight_layout()
    return ax


def pull_data_from_scope(scope, channel=1) -> Tuple[np.ndarray, np.ndarray, float]:
    """Extracts waveform data using Tektronix WFMOutpre headers and binary transfer."""
    # Target Channel 1
    scope.write(f"DATa:SOUrce CH{channel}")
    # Set encoding to signed integer, big-endian (standard for Tek)
    scope.write("DATa:ENCdg RIBINARY")
    # 1 byte per point is standard for 8-bit ADC acquisition, 2 bytes for 16-bit ADCs
    scope.write("DATa:WIDth 2")
    
    # Query scaling parameters from the preamble
    y_mult = float(scope.query("WFMOutpre:YMUlt?"))
    y_off  = float(scope.query("WFMOutpre:YOFf?"))
    y_zero = float(scope.query("WFMOutpre:YZEro?"))
    x_incr = float(scope.query("WFMOutpre:XINcr?"))
    x_zero = float(scope.query("WFMOutpre:XZEro?"))
    
    # The DPO zero reference for the trigger is 0.0 unless delayed
    trdl = float(scope.query("HORizontal:MAIn:DELay:TIMe?")) if scope.query("HORizontal:MAIn:DELay:MODe?").strip() == "ON" else 0.0
    trigger_position = float(scope.query("HORizontal:MAIn:SCAle?")) 
    print(f"Trigger position (relative to first sample): {trigger_position} s, starts at 1 div + {trdl:.3e} s delay")

    # Read binary block data directly into a numpy array, datatype h for 16-bit ADCs, b for 8-bit ADCs
    adc_samples = np.array(scope.query_binary_values("CURVe?", datatype='h', is_big_endian=True))
    print(f"Read {adc_samples.size} ADC samples from scope")
    print(f"Scaling parameters: Y_Mult={y_mult}, Y_Off={y_off}, Y_Zero={y_zero}, X_Incr={x_incr}, X_Zero={x_zero}, Trigger_Delay={trdl}")


    if adc_samples.size == 0:
        raise RuntimeError("No ADC samples found in scope payload")

    # Apply Tektronix scaling formula: Voltage = (ADC - Y_Offset) * Y_Multiplier + Y_Zero
    voltages = (adc_samples - y_off) * y_mult + y_zero
    
    # Time axis: Time = Index * X_Increment + X_Zero + trigger_position (to align with trigger)
    time_axis = np.arange(adc_samples.size) * x_incr + x_zero -trigger_position #CHECK THIS!!!!

    return time_axis, voltages, trigger_position


def calculate_photon_count(area_under: float) -> float:
    """Calculates photon count. PMT pulses are usually negative, so area is negative."""
    resistance = 50.0  # 50 Ohms is crucial for fast PMT signals!
    gain = 1e6         # PMT Gain
    elementary_charge = 1.602176634e-19
    quantum_efficiency = 0.8 
    
    # Take absolute area because PMT voltage pulses are negative
    total_charge = abs(area_under) / resistance
    return total_charge / (quantum_efficiency * gain * elementary_charge)


def configure_scope(scope) -> None:
    """Configures the Tektronix scope for averaging and trigger setup."""
    # Turn off command headers in responses so we just get raw values back
    scope.write("HEADer OFF")
    print("Connected to:", scope.query("*IDN?").strip())
    scope.query("*OPC?")  # Ensure all previous commands are complete before proceeding
    
    print("Performing custom auto-setup...")
    #scope.write("AUToset EXECute") #takes ~1.5s
    #fast_unipolar_autoscale(scope, channel=1, direction="negative")  # Much faster than full autoset, but may require multiple iterations if the initial scale is very far off
    robust_autoscale(scope, channel=1)  # Can catch bigger (not all) scale errors and then fine-tune, but takes ~0.1s
    time.sleep(0.1)

    timebase = float(scope.query("HORizontal:MAIn:SCAle?"))
    print(f"Current timebase: {timebase:.3e} s/div")

    # Setup Acquisition
    scope.write(f"ACQuire:MODe AVErage")
    scope.write(f"ACQuire:NUMAVg {DEFAULT_AVERAGES}")
    
    # Setup Trigger (assuming Laser sync is on CH2)
    scope.write("TRIGger:A:TYPe EDGE")
    scope.write("TRIGger:A:EDGE:SOUrce CH2")
    scope.write("TRIGger:A:EDGE:SLOPe FALL")  # PMT pulses are negative, so trigger on falling edge

    if TRIGGER_LEVEL_V is None:
        # Auto measure trigger, requires the laser to be on
        # Command the scope to evaluate the signal and set the level to 50%
        scope.write("TRIGger:A SETLevel")
        
        # Query the level back so you know what the scope decided to use
        chosen_level = float(scope.query("TRIGger:A:LEVel:CH2?"))
        print(f"Trigger level auto-set to {chosen_level:.3f} V on Channel 2")
    
    else:
        # Manually set trigger level
        scope.write(f"TRIGger:A:LEVel:CH2 {TRIGGER_LEVEL_V}")
        print(f"Trigger level set to {TRIGGER_LEVEL_V} V on Channel 2")

    # Clear status
    scope.write("*CLS")


def fast_unipolar_autoscale(scope, channel=1, direction="positive"):
    """only works for signals that are strictly positive or negative, like PMT pulses. May need to run multiple times if the initial scale is very far off, but much faster than full autoset."""
    # 1. Position the baseline at the bottom (-3.5 div) or top (+3.5 div)
    # Most Tektronix screens are 8 divisions tall (-4 to +4)
    pos = -3.5 if direction == "positive" else 3.5
    scope.write(f'CH{channel}:POSition {pos}')
    
    # 2. Get the Peak (Max) or Base (Min) for unipolar scaling
    # We use 'Maximum' for positive-going spectra
    meas_type = 'MAXimum' if direction == "positive" else 'MINimum'
    scope.write(f'MEASUrement:IMMed:TYPE {meas_type}')
    scope.write(f'MEASUrement:IMMed:SOUrce CH{channel}')
    
    v_peak = abs(float(scope.query('MEASUrement:IMMed:VALue?')))
    current_scale = float(scope.query(f'CH{channel}:SCAle?'))

    # 3. Calculate target scale
    # We want the peak to reach ~7 divisions high (leaving 1 div headroom)
    target_scale = v_peak / 7.0 
    
    # 4. Update if change is > 10%
    if abs(target_scale - current_scale) / current_scale > 0.10:
        # Enforce a minimum scale to avoid chasing noise
        final_scale = max(target_scale, 0.001) 
        scope.write(f'CH{channel}:SCAle {final_scale:.4f}')
        print(f"Adjusted Scale to: {final_scale:.4f} V/div for unipolar {direction} signal")

def robust_autoscale(scope, channel=1):
    # 1. Check for Clipping / Off-screen
    # If the measurement is "clipping," the peak value will be very close 
    # to (Scale * 4) + Offset.
    
    current_scale = float(scope.query(f'CH{channel}:SCAle?'))
    v_max = float(scope.query(f'MEASUrement:IMMed:TYPE MAXimum;VALue?'))
    v_min = float(scope.query(f'MEASUrement:IMMed:TYPE MINimum;VALue?'))

    # Determine if we are off-screen (clipping)
    # Most DPO7000s report a specific status or a capped value.
    # A safe bet: if signal is within 5% of the screen edge, zoom out 5x immediately.
    screen_edge_high = current_scale * 4
    screen_edge_low = current_scale * -4
    
    if v_max > (screen_edge_high * 0.95) or v_min < (screen_edge_low * 0.95):
        # BLIND SEARCH: Zoom out significantly to find the signal in one jump
        new_scale = current_scale * 5 
        scope.write(f'CH{channel}:SCAle {new_scale}')
        time.sleep(0.1) # Short wait for hardware to settle
        # Re-run the measurement once after zooming out
        v_max = float(scope.query(f'MEASUrement:IMMed:TYPE MAXimum;VALue?'))
        v_min = float(scope.query(f'MEASUrement:IMMed:TYPE MINimum;VALue?'))
        current_scale = new_scale

    # 2. Precise Scaling (Unipolar logic for Emission Spectra)
    # Move baseline to top to maximize resolution
    #baseline_pos = 3.5 
    baseline_pos = 0 #for function generator testing
    scope.write(f'CH{channel}:POSition {str(baseline_pos)}') 
    
    v_pp = v_max - v_min
    target_scale = v_pp / 7.0
    
    if target_scale > 0:
        scope.write(f'CH{channel}:SCAle {target_scale:.4f}')
        print(f"Robust Autoscale set to: {target_scale:.4f} V/div")


def measure_gated_area(scope, start_time=NONE, end_time=NONE, channel=1):
    # 3. Setup Cursors
    scope.write('CURSor:STATE ON')
    scope.write('CURSor:FUNCtion VBARS')
    if start_time is not None and end_time is not None:
        scope.write(f'CURSor:VBARS:POS1 {start_time}')
        scope.write(f'CURSor:VBARS:POS2 {end_time}')
        
    # 4. Use the specific DPO7000 gating command
    # Try 'VBARS' if 'CURSOR' failed
    scope.write('MEASUrement:GATing ON')
    scope.write('MEASUrement:IMMed:TYPE AREA')
    scope.write(f'MEASUrement:IMMed:SOUrce CH{channel}')
    #scope.write('MEASUrement:IMMed:AREA')
    
    # 5. Enable the measurement and wait for a fresh acquisition
    scope.write('MEASUrement:IMMEd:STATE ON')
    time.sleep(0.5) # Longer wait for the first run
    
    # 6. Fetch and check
    try:
        val = scope.query('MEASUrement:IMMEd:VALue?')
        area_val = float(val)
        #print(f"Measured gated area: {area_val:.3e} V·s")
        
        if area_val > 1e30:
            # Check if signal is too small for the scope to 'see'
            print("Scope reporting invalid. Try increasing vertical scale.")
            return 0.0
        return area_val
    except Exception as e:
        print(f"Query error: {e}")
        return 0.0

# Usage: 
# area = measure_gated_area_final(scope, -10e-6, 10e-6)
# print(f"Area: {area:.6e}")



def main() -> None:
    rm = pyvisa.ResourceManager(RESOURCE_MANAGER)
    scope = None

    try:
        scope = rm.open_resource(SCOPE_ADDRESS)
        # Extend timeout for averaging acquisition to finish
        scope.timeout = 25000 

        #print(scope.query("*IDN?").strip())
        
        configure_scope(scope)

        # Wait for auto-setup to complete if used

        print(f"Starting {DEFAULT_AVERAGES} averaged acquisitions...")
        # StopAfter SEQuence tells the scope to stop after one full averaging cycle completes
        scope.write("ACQuire:STOPAfter SEQuence")
        #print("Waiting for acquisition to complete...")
        scope.write("ACQuire:STATE RUN")
        #print("Acquisition started. Scope is averaging...")
        # *OPC? blocks execution until the previous commands (the sequence) are entirely finished
        #scope.query("*OPC?") 
        time.sleep(0.1)  # Additional wait to ensure acquisition is complete, adjust as needed
        print("Acquisition complete. Capturing data...")

        time_axis, voltages, trigger_position = pull_data_from_scope(scope, 1)
        print(f"Trigger position (time from trigger to first sample): {trigger_position :.3e} s")
        time_axis2, trigger_voltages, _ = pull_data_from_scope(scope, 2) #just to check trigger signal

        print("Re-arming scope to continuous run...")
        scope.write("ACQuire:STOPAfter RUNSTOP")
        scope.write("ACQuire:STATE RUN")

        area_under, summed_voltages = trigger_dependent_custom_integration(
            trigger_position,
            START_OFFSET_S,
            END_OFFSET_S,
            time_axis,
            voltages,
        )

        area = measure_gated_area(scope, START_OFFSET_S, END_OFFSET_S, channel=1)
        print(f"Gated Area: {area:.6e} V*s")

        if PLOT_VISIBLE:
            ax = _plot_waveform(time_axis, voltages, START_OFFSET_S, END_OFFSET_S, area_under, summed_voltages)
            ax.plot(time_axis2, trigger_voltages-1.5*max(voltages), "c-", label="Trigger Signal (CH2),\noffset for visibility") #offset trigger down for visibility
            plt.legend()
            plt.show()

        print(f"Calculated area under curve: {area_under:.3e} V·s")
        print(f"Summed voltages in integration window: {summed_voltages:.3e} V")

        # coupling = scope.query("CH1:COUPling?").strip()
        # print(f"Channel 1 coupling: {coupling} (Ensure this says 'DC50' or 'AC50' for a PMT!)")
        
        # photon_count = calculate_photon_count(area_under)
        # print(f"Estimated photon count in integration window: {photon_count:.3e} photons")

        #tau_fit = lifetime_from_exponential_fit(time_axis, voltages)
        #print(f"Estimated lifetime from exponential fit: {tau_fit:.3e} s")

    except pyvisa.VisaIOError as exc:
        print("VISA error:", exc)
    except Exception as exc:
        print("Error:", exc)
    finally:
        if scope is not None:
            scope.close()


if __name__ == "__main__":
    main()