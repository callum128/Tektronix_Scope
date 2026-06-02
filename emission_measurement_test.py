import os
import sys
import time

from rex_utils import Session #if Experiment doesn't work

from DPO7104_TekTronix_scope_driver import DPO7104_TekTronix_scope

from spcs_instruments import HoribaiHR550, Experiment #should work if the spcs_instruments path is added to rex config

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_emission_experiment():
    def a_measurement(config) -> dict:
        spec = HoribaiHR550(config)
        tektronix = DPO7104_TekTronix_scope(config)
        
        tektronix.set_cursors()
        spec.set_wavelength(spec.initial_wavelength)
        steps = int((spec.final_wavelength - spec.initial_wavelength) / spec.step_size)
        for i in range(steps):
            tektronix.measure()
            spec.spectrometer_step()
            spec.measure()
            time.sleep(0.1)
        tektronix.close()

        return

    dir_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(dir_path, "emission_config.toml")
    config_path = os.path.abspath(config_path)

    experiment = Experiment(a_measurement, config_path) #may need to be Session
    experiment.start()


if __name__ == "__main__":
    test_emission_experiment()
    print("experiment complete!")