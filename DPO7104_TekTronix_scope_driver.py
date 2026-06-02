import time
import numpy as np
import pyvisa
from pyvisa.resources import MessageBasedResource
from typing import Optional, cast

from rex_utils import Measurement, RexSupport


class DPO7104_TekTronix_scope(RexSupport):
    """Class for controlling a Tektronix DPO7104 oscilloscope via Keysight Technologies GPIB-USB using PyVISA.
    
    This driver handles device connection, baseline configuration, gated area measurements, waveform acquisition, 
    and optional data forwarding to a Rex server link.

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
        open_connection(): Establishes the PyVISA connection and validates the instrument identity string.
        set_config(): Imports active configuration values, executes a full autoset, and binds 
            acquisition and trigger criteria (Edge, Fall, Channel 2 Source).
        set_cursors(): Enables and positions vertical bars on the scope for gated Channel 1 area calculations.
        measure_area(): Queries the scope's gated area calculation and transforms it to account for negative PMT polarity.
        measure_waveform(channel=1): Downloads raw binary ADC curves from the specified channel, scales them 
            into true voltages using preamble multipliers, and builds a time-axis relative to the trigger.
        measure(): Orchestrates the enabled acquisition routines (area and/or waveforms) and pushes payloads to Rex.
        full_autoset(): Commands the scope hardware to execute its slow native autoset sequence (*OPC? blocking).
        check_clipping(): Measures the absolute peak minimum voltage on Channel 1 and caches it to self.v_peak.
        close(): Safely closes the PyVISA session to free up the GPIB resource interface.
    """

    #pyvisa settings
    RESOURCE_MANAGER = '' #default to pyvisa's default backend, but can be set to "@ivi" or other backends if needed for compatibility with specific GPIB-USB adapters or drivers. Check pyvisa documentation for details on available backends and their compatibility with your hardware setup.
    SCOPE_ADDRESS = "GPIB0::1::INSTR"

    __toml_config__ = {
        "device.DPO7104_TekTronix_scope": {
            "_section_description": "DPO7104_TekTronix_scope configuration",
            "averages": {"_value": 1, "_description": "Number of averages"}, #set to 1 for non-averaged data, set to >1 for averaged data, but be aware this will slow down your acquisition loop significantly as the scope needs to acquire and process multiple waveforms for each measurement cycle
            "start_bound": {"_value": 0.0, "_description": "Starting bound, the position of the first cursor relative to the trigger"},
            "end_bound": {"_value": 1.0e-4, "_description": "Ending bound, the position of the second cursor relative to the trigger"},
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

        self.open_connection()
        self.set_config()

        self.measurements = {
            "area": Measurement(data=[], unit="V*s"), 
            "waveform": Measurement(data=[], unit="V"),
            "trigger": Measurement(data=[], unit="V"),
            "time_from_trigger": Measurement(data=[], unit="s")
        }

        self.validate_measurements()

    def open_connection(self):
            """Opens the resource manager and connects to the scope, saving it to self.scope."""
            try:
                rm = pyvisa.ResourceManager(self.RESOURCE_MANAGER)
                if self.SCOPE_ADDRESS not in rm.list_resources():
                    self.logger.error(f"Scope address {self.SCOPE_ADDRESS} not found in available resources: {rm.list_resources()}")
                    raise Exception(f'{self.SCOPE_ADDRESS} not in {rm.list_resources()}')
                else:
                    # 1. Bind the opened resource to self.scope
                    self.scope = cast(MessageBasedResource, rm.open_resource(self.SCOPE_ADDRESS))
                    self.scope.timeout = 25000 
                    
                    try:
                        TRUE_NAME = 'TEKTRONIX,DPO7104,B069280,CF:91.1CT FV:5.3.5 Build 22'  
                        idn = self.scope.query("*IDN?").strip()
                        if TRUE_NAME not in idn:  # Using 'in' is safer than '==' for *IDN?
                            self.logger.error(f"Unexpected Scope ID: {idn} does not contain expected identifier {TRUE_NAME}")
                            raise Exception(f"Unexpected Scope ID: {idn} is not {TRUE_NAME}")
                    except Exception as e:
                        self.logger.error(f"Scope did not accept ID query: {e}")

            except Exception as e:
                self.logger.error(f"pyvisa.ResourceManager did not work: {e}")

    def set_config(self):
        self.averages = self.require_config("averages")
        self.start_bound = self.require_config("start_bound")
        self.end_bound = self.require_config("end_bound")
        self.area_enabled = self.require_config("area")
        self.waveform_enabled = self.require_config("waveform")
        self.trigger_enabled = self.require_config("trigger")

        if not self.scope:
            raise RuntimeError("Oscilloscope connection is not open. Check the cable connections.")

        #self.full_autoset()

        self.scope.write("TRIGger:A:TYPe EDGE")
        self.scope.write("TRIGger:A:EDGE:SOUrce CH2") 
        self.scope.write("TRIGger:A:EDGE:SLOPe FALL") 
        self.scope.write("TRIGger:A SETLevel")

        if self.averages == 1:
            self.scope.write(f"ACQuire:MODe SAMple")
        else:
            self.scope.write(f"ACQuire:MODe AVErage")
            self.scope.write(f"ACQuire:NUMAVg {self.averages}") 

        v_position = 3.5 #3.5 for actaul PMT data
        self.scope.write(f'CH1:POSition {v_position}')

        self.scope.write("*CLS") #may need to move for each measurement loop if scope gets backed up with data

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
        self.scope.write("DATa:STOP 100000") #will take ~2s

        # Query scaling parameters from the preamble
        y_mult = float(self.scope.query("WFMOutpre:YMUlt?"))
        y_off  = float(self.scope.query("WFMOutpre:YOFf?"))
        y_zero = float(self.scope.query("WFMOutpre:YZEro?"))
        x_incr = float(self.scope.query("WFMOutpre:XINcr?"))
        x_zero = float(self.scope.query("WFMOutpre:XZEro?"))
        trigger_pos = float(self.scope.query("HORizontal:MAIn:SCAle?"))

        self.scope.write("ACQuire:STOPAfter SEQuence") #stop the acquisition to prevent overwriting the buffer while we're reading it, will need to start it again after

        adc_samples = np.array(self.scope.query_binary_values("CURVe?", datatype='h', is_big_endian=True))

        self.scope.write("ACQuire:STOPAfter RUNSTOP")
        self.scope.write("ACQuire:STATE RUN") #restart the acquisition for the next loop, may need to move this if we find scope gets backed up with data

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
        self.scope.write("*CLS") #clear the status to prevent overflow

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

    def check_clipping(self):
        self.scope.write(f'MEASUrement:IMMed:TYPE MINimum')
        self.scope.write(f'MEASUrement:IMMed:SOUrce CH1')
        
        self.v_peak = abs(float(self.scope.query('MEASUrement:IMMed:VALue?')))
        
    def close(self):
        if self.scope:
            self.scope.close()

    
