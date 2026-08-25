import os
import time
import sys

from spcs_instruments import Gl100, DPO7104_TekTronix_scope, Experiment

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def excitation_experiment():
    def scope_las_measurement(config):
        tektronix = DPO7104_TekTronix_scope(config)
        las = Gl100(config, connect_to_rex=True)
        total_positions = len(las.scan_data)

        las.measure()
        time.sleep(0.1)
        tektronix.measure() #set in config toml to record area after after a few averages

        for i in range(total_positions):
            las.move_to_next_position()
            time.sleep(0.1)
            tektronix.measure()

        time.sleep(1)
        tektronix.close()

        return

    dir_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(dir_path,"..", "templates", "scope_excitation.toml")
    config_path = os.path.abspath(config_path)

    experiment = Experiment(scope_las_measurement, config_path)
    experiment.start()

if __name__ == "__main__":
    excitation_experiment()

#set spec using spectrometer_gui first
#run: rex run .\Scripts\scope_excitation.py -o .\Outputs\