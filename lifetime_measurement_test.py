import os
import sys
import time

from rex_utils import Session

from DPO7104_TekTronix_scope_driver import DPO7104_TekTronix_scope

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def lifetime_experiment_test():
    def scope_measurement(config) -> dict:
        tektronix = DPO7104_TekTronix_scope(config) #note that the cursor bounds are irrelevant for lifetime measurements 
        waveform = tektronix.measure() #set to pull waveform only in the config toml
        tektronix.close()

        return

    dir_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(dir_path, "lifetime_config.toml") #will need to adjust the path to the config file as needed
    config_path = os.path.abspath(config_path)

    experiment = Session(scope_measurement, config_path)
    experiment.start()


if __name__ == "__main__":
    lifetime_experiment_test()

#run: rex run .\lifetime_measurement_test.py -o .\Outputs\  