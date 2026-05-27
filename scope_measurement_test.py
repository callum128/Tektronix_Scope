import time
from pathlib import Path

from DPO7104_TekTronix_scope_driver import DPO7104_TekTronix_scope

from rex_utils import Session

def test_scope_experiment():
    def scope_measurement(config) -> None:
        # connect to a device, inherit its config & loop through its functions. ideally, all devices should have some "measure" like
        # function that handles sending the data over the socket.
        tektronix = DPO7104_TekTronix_scope(config, connect_to_rex=True)
        tektronix.set_cursors()
        for i in range(5):
            tektronix.quick_autoset()
            tektronix.measure()
            time.sleep(0.1)
        tektronix.close()

        return

    # This may soon be deprecated, instead passing in the config via rex exlusively.
    base_path = Path(__file__).parent

    config_path = base_path / "scope_config.toml"
    print(config_path)

    session = Session(scope_measurement, config_path)
    session.start()


if __name__ == "__main__":
    test_scope_experiment()
