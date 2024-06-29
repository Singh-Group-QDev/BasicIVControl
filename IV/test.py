from pymeasure.instruments.keithley import Keithley2400

source = Keithley2400(24)
source.measure_concurent_functions = True
source.apply_voltage()
source.measure_current()
source.current_range = 1e-6
source.wires = 2


