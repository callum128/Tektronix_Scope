import time
import numpy as np
import pyvisa
from pyvisa.resources import MessageBasedResource
from typing import Optional, cast

from rex_utils import Measurement, RexSupport


class DPO7104_TekTronix_scope(RexSupport):
    """Class for controlling a Tektronix DPO7104 oscilloscope via GPIB-USB using PyVISA.
    
    This driver handles device connection, baseline configuration, and iterative vertical 
    scaling adjustment to prevent signal clipping and optimize dynamic range for negative 
    transient signals (e.g., PMT pulses).

    Attributes:
        state (int): A counter that increments with every successful measurement cycle.
        connect_to_rex (bool): Flag indicating whether to forward data payloads to a Rex server link.
        sock (socket or None): The TCP socket connection used when connect_to_rex is enabled.
        scope (MessageBasedResource or None): The PyVISA message-based resource pointer for the physical scope.
        measurements (dict): Container for compiled measurement results. Holds 'area', 'waveform', 
            'trigger', and 'time_from_trigger' as Measurement objects.
        averages (int): The number of hardware waveform acquisitions to average over.
        start_bound (float): The left position boundary for the gated measurement relative to the trigger.
        end_bound (float): The right position boundary for the gated measurement relative to the trigger.
        area_enabled (bool): Boolean flag stating whether area integrations should be captured.
        waveform_enabled (bool): Boolean flag stating whether Channel 1 waveforms should be pulled.
        trigger_enabled (bool): Boolean flag stating whether Channel 2 trigger waveforms should be pulled.
        v_peak (float): The absolute peak negative voltage captured during clipping checks.

    Methods:
        test_connection(): Establishes the PyVISA connection and validates the instrument identity string.
        set_config(): Imports active configuration values, executes a full autoset, and binds 
            acquisition and trigger criteria (Edge, Fall, Channel 2 Source).
        set_cursors(): Enables and positions vertical bars on the scope for gated Channel 1 area calculations.
        measure_area(): Queries the scope's gated area calculation and transforms it to account for negative PMT polarity.
        measure_waveform(channel=1): Downloads raw binary ADC curves from the specified channel, scales them 
            into true voltages using preamble multipliers, and builds a time-axis relative to the trigger.
        measure(): Orchestrates the enabled acquisition routines (area and/or waveforms) and pushes payloads to Rex.
        full_autoset(): Commands the scope hardware to execute its slow native autoset sequence (*OPC? blocking).
        quick_autoset(max_iterations=5): Iteratively steps the vertical Volts/Div scale up or down over multiple 
            loops to ensure negative transients fill ~7 divisions of the screen without clipping.
        check_clipping(): Measures the absolute peak minimum voltage on Channel 1 and caches it to self.v_peak.
        close(): Safely closes the PyVISA session to free up the GPIB resource interface.
    """

    #pyvisa settings
    RESOURCE_MANAGER = "@ivi"
    SCOPE_ADDRESS = "GPIB0::1::INSTR"

    __toml_config__ = {
        "device.DPO7104_TekTronix_scope": {
            "_section_description": "DPO7104_TekTronix_scope configuration",
            "averages": {"_value": 512, "_description": "Number of averages"},
            "start_bound": {"_value": 0.0, "_description": "Starting bound, the position of the first cursor relative to the trigger"},
            "end_bound": {"_value": 1.0e-6, "_description": "Ending bound, the position of the second cursor relative to the trigger"},
            "area": {"_value": True, "_description": "Pulls area data"},
            "waveform": {"_value": False, "_description": "Pulls wavefrom data, channel 1"},
            "trigger": {"_value": False, "_description": "Pulls trigger waveform data, channel 2"},
        }
    }

    def __init__(self, config, name="DPO7104_TekTronix_scope", connect_to_rex=True):
        self.state = 0
        self.connect_to_rex = connect_to_rex
        super().__init__(name=name)
        self.bind_config(config)
        self.logger.debug(f"{self.name} connected with this config {self.config}")

        if self.connect_to_rex:
            self.sock = self.tcp_connect()

        self.scope: Optional[MessageBasedResource] = None

        self.test_connection()
        self.set_config()

        self.measurements = {
            "area": Measurement(data=[], unit="V*s"), 
            "waveform": Measurement(data=[], unit="V"),
            "trigger": Measurement(data=[], unit="V"),
            "time_from_trigger": Measurement(data=[], unit="s")
        }

        self.validate_measurements()

    def test_connection(self) -> None:
            """Opens the resource manager and connects to the scope, saving it to self.scope."""
            try:
                rm = pyvisa.ResourceManager(self.RESOURCE_MANAGER)
                if self.SCOPE_ADDRESS not in rm.list_resources():
                    raise Exception(f'{self.SCOPE_ADDRESS} not in {rm.list_resources()}')
                else:
                    # 1. Bind the opened resource to self.scope
                    self.scope = cast(MessageBasedResource, rm.open_resource(self.SCOPE_ADDRESS))
                    self.scope.timeout = 25000 
                    
                    try:
                        TRUE_NAME = 'TEKTRONIX,DPO7104,B069280,CF:91.1CT FV:5.3.5 Build 22'  
                        idn = self.scope.query("*IDN?").strip()
                        if TRUE_NAME not in idn:  # Using 'in' is safer than '==' for *IDN?
                            raise Exception(f"Unexpected Scope ID: {idn} is not {TRUE_NAME}")
                    except Exception as e:
                        print(f"Scope did not accept ID query: {e}")

            except Exception as e:
                print(f"pyvisa.ResourceManager did not work: {e}")

    def set_config(self):
        self.averages = self.require_config("averages")
        self.start_bound = self.require_config("start_bound")
        self.end_bound = self.require_config("end_bound")
        self.area_enabled = self.require_config("area")
        self.waveform_enabled = self.require_config("waveform")
        self.trigger_enabled = self.require_config("trigger")

        if not self.scope:
            raise RuntimeError("Scope connection is not open. Call test_connection first.")

        #self.full_autoset()

        self.scope.write("TRIGger:A:TYPe EDGE")
        self.scope.write("TRIGger:A:EDGE:SOUrce CH2") 
        self.scope.write("TRIGger:A:EDGE:SLOPe FALL") 
        self.scope.write("TRIGger:A SETLevel")

        self.scope.write(f"ACQuire:MODe AVErage")
        self.scope.write(f"ACQuire:NUMAVg {self.averages}") 

        v_position = 0 #3.5 for actaul PMT data

        self.scope.write("*CLS")
        self.scope.write(f'CH1:POSition {v_position}')

    def set_cursors(self): 
        self.scope.write('CURSor:STATE ON') 
        self.scope.write('CURSor:FUNCtion VBARS')
        self.scope.write(f'CURSor:VBARS:POS1 {self.start_bound}')
        self.scope.write(f'CURSor:VBARS:POS2 {self.end_bound}')
 
        self.scope.write('MEASUrement:GATing ON')
        self.scope.write('MEASUrement:IMMed:TYPE AREA')
        self.scope.write(f'MEASUrement:IMMed:SOUrce CH1')
        time.sleep(0.5)

    def measure_area(self):
        self.scope.write('MEASUrement:IMMEd:STATE ON')
        area = float(self.scope.query('MEASUrement:IMMEd:VALue?'))

        data = -1*area #PMT is negative voltage

        self.measurements["area"] = Measurement(
                data=[data],
                unit="V*s",
            )
        
    def measure_waveform(self, channel=1):
        """Pulls the waveform data, and data to make the time axis. Channel 2 for trigger."""
        self.scope.write(f"DATa:SOUrce CH{channel}")
        self.scope.write("DATa:ENCdg RIBINARY")
        self.scope.write("DATa:WIDth 2") 
        self.scope.write("DATa:STARt 1")
        self.scope.write("DATa:STOP 100000") #will take ~1.5s

        # Query scaling parameters from the preamble
        y_mult = float(self.scope.query("WFMOutpre:YMUlt?"))
        y_off  = float(self.scope.query("WFMOutpre:YOFf?"))
        y_zero = float(self.scope.query("WFMOutpre:YZEro?"))
        x_incr = float(self.scope.query("WFMOutpre:XINcr?"))
        x_zero = float(self.scope.query("WFMOutpre:XZEro?"))
        trigger_pos = float(self.scope.query("HORizontal:MAIn:SCAle?"))

        adc_samples = np.array(self.scope.query_binary_values("CURVe?", datatype='h', is_big_endian=True))
        voltages = (adc_samples - y_off) * y_mult + y_zero
        time_axis = np.arange(adc_samples.size) * x_incr + x_zero - trigger_pos #relative to trigger

        data = voltages.tolist()
        times = time_axis.tolist()

        self.measurements["time_from_trigger"] = Measurement(
                data=[times],
                unit="s",
            )

        if channel == 1:
            self.measurements["waveform"] = Measurement(
                data=[data],
                unit="V",
            )
        elif channel == 2:
            self.measurements["trigger"] = Measurement(
                data=[data],
                unit="V",
            )
        
    def measure(self):
        if self.area_enabled:
            self.measure_area()
        if self.waveform_enabled:
            self.measure_waveform()
        if self.trigger_enabled:
            self.measure_waveform(2)

        self.state += 1

        if self.connect_to_rex:
            payload = self.create_payload()
            self.tcp_send(payload, self.sock)

        return self.measurements
    
    def full_autoset(self):
        self.scope.query("*OPC?")
        self.scope.write("AUToset EXECute")

    def quick_autoset(self, max_iterations=5): #doesn't work yet, at least not for function generator tests
        """Only works for signals that are strictly negative, like PMT pulses. 
        Loops and adjusts the vertical scale until the scale changes by less than 10%,
        or until max_iterations is reached. Much faster than full autoset.
        """
        for iteration in range(max_iterations):
            self.check_clipping()
            current_scale = float(self.scope.query(f'CH1:SCAle?'))

            if self.v_peak < 1e-4: 
                self.logger.warning("Signal too small or flatlined. Dropping scale to look for transient.")
                # Aggressively drop the scale to search for the small transient
                self.scope.write(f'CH1:SCAle {current_scale / 2.0:.4f}') #probaly need to adjust this bit
                time.sleep(0.2)
                continue
            
            # We want the peak to reach ~7 divisions high (leaving 1 div headroom)
            target_scale = self.v_peak / 7.0
            
            # Check if the change is greater than 10%
            scale_change = abs(target_scale - current_scale) / current_scale
            if scale_change > 0.10:
                # Enforce a minimum scale to avoid chasing noise
                final_scale = max(target_scale, 0.001) #probaly need to adjust this noise floor a bit
                self.scope.write(f'CH1:SCAle {final_scale:.4f}') #may need more decimals
                
                # Small delay to let the scope hardware/autoset settle before checking again
                time.sleep(0.2)
            else:
                # The scale is stable (change is <= 10%), we can stop looping
                self.logger.debug(f"Quick autoset converged after {iteration + 1} iterations.")
                break
        else:
            self.logger.warning("Quick autoset reached max iterations without perfectly settling.")

    def check_clipping(self):
        self.scope.write(f'MEASUrement:IMMed:TYPE MINimum')
        self.scope.write(f'MEASUrement:IMMed:SOUrce CH1')
        
        self.v_peak = abs(float(self.scope.query('MEASUrement:IMMed:VALue?')))
        
    def close(self):
        if self.scope:
            self.scope.close()

    
