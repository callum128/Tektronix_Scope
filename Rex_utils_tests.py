from rex_utils import RexSupport

class tester(RexSupport):
    __toml_config__ = {
            "device.DPO7104_TekTronix_scope": {
                "_section_description": "DPO7104_TekTronix_scope configuration",
                "averages": {"_value": 512, "_description": "Number of averages"},
                "start_bound": {"_value": 0.0, "_description": "Starting bound, the position of the first cursor relative to the trigger"},
                "end_bound": {"_value": 1.0e-6, "_description": "Ending bound, the position of the second cursor relative to the trigger"},
                "measure_type": {"_value": "area", "_description": "Type of measurement to pull, area, waveform, or trigger_waveform"}
            }
        }
    
    def __init__(self) -> None:
            pass
    
    def config(self):
          print(self.require_config("averages"))

config = 1
tester.config(config)