import time
import numpy as np
import pyvisa
from pyvisa.resources import MessageBasedResource
from typing import Optional, cast

from rex_utils import Measurement, RexSupport


class DPO7104_TekTronix_scope(RexSupport):
    """Class for controlling the DPO7104 TekTronix oscilloscope via GPIB-USB pyvisa.
    
    Attributes:
    
    Methods:
        set_config(): Configures.
        set_cursors(): Sets the cursors on the scope for channel 1, relative to the trigger.
        measure_area(): Pulls the area between the cursors.
        measure_waveform(channel=1): Pull the entire waveform, channel 1 for the data, channel 2 form the trigger. Slow.
        full_autoset(): Full autosetup, only done at the start. Very slow.
        quick_autoset(): Quick autosetup of the vertical bounds. Use to keep the waveform filling the screen. Fast.
        check_clipping(): Checks if the waveform if off the screen. 
        check_small(): Checks if the waveform is too small for good signal.
        reset(): Return the scope to the default settings.
        close(): Close the connection to the scope. 
        test_connection(): Check pyvisa resourse manager, address and then checks a basic ID query to the scope.
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
            "time_from_trigger" : {"_value": False, "_description": "Pulls time axis data, subtracting the trigger position, both channels should be the same"}
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
                        TRUE_NAME = 'TEKTRONIX'  # Note: *IDN? usually returns a longer string like 'TEKTRONIX,DPO7104,...'
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

        self.full_autoset()

        self.scope.write("TRIGger:A:TYPe EDGE")
        self.scope.write("TRIGger:A:EDGE:SOUrce CH2")
        self.scope.write("TRIGger:A:EDGE:SLOPe FALL") 
        self.scope.write("TRIGger:A SETLevel")

        self.scope.write(f"ACQuire:MODe AVErage")
        self.scope.write(f"ACQuire:NUMAVg {self.averages}") 

        self.scope.write("*CLS")
        self.scope.write(f'CH1:POSition -3.5')

    def set_cursors(self): 
        self.scope.write('CURSor:STATE ON') 
        self.scope.write('CURSor:FUNCtion VBARS')
        self.scope.write(f'CURSor:VBARS:POS1 {self.start_bound}')
        self.scope.write(f'CURSor:VBARS:POS2 {self.end_bound}')
 
        self.scope.write('MEASUrement:GATing ON')
        self.scope.write('MEASUrement:IMMed:TYPE AREA')
        self.scope.write(f'MEASUrement:IMMed:SOUrce CH1')
        time.sleep(0.1)

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

    def quick_autoset(self):
        """Only works for signals that are strictly positive or negative, like PMT pulses. May need to run multiple times if the initial scale is very far off, but much faster than full autoset."""
        self.check_clipping()
        current_scale = float(self.scope.query(f'CH1:SCAle?'))
        # We want the peak to reach ~7 divisions high (leaving 1 div headroom)
        target_scale = self.v_peak / 7.0 
        
        # 4. Update if change is > 10%
        if abs(target_scale - current_scale) / current_scale > 0.10:
            # Enforce a minimum scale to avoid chasing noise
            final_scale = max(target_scale, 0.001) 
            self.scope.write(f'CH1:SCAle {final_scale:.4f}') #may need more decimals

    def check_clipping(self):
        self.scope.write(f'MEASUrement:IMMed:TYPE MINimum')
        self.scope.write(f'MEASUrement:IMMed:SOUrce CH1')
        
        self.v_peak = abs(float(self.scope.query('MEASUrement:IMMed:VALue?')))
        
    def close(self):
        if self.scope:
            self.scope.close()

    
