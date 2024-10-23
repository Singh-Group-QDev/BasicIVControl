''' 
This routine preforms a four point lockin measurement followed by a
two point DC measurement. The DC measurement is intended to be the
across the terminals the AWG is connected to.

This script is designed such that sufficient time is given to the
oxford software to stabilize the temperature after each new B field
is reached.

This is important at present (10/2024) as the fridge is at reduced
cooling power and it is difficult to keep the magnet from influencing
the sample temperature.

This script is designed the the IISc STO sample that is highly temperature
sensitive.

BL
'''

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from IISc.ProcedureTempSensitive import ProcedureTempSensitive


class ExperimentTempSensitive(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureTempSensitive,
            inputs=['gate_voltage','voltage_offset', 'voltage_amplitude', 'frequency', 'delay', 'voltage_range', 'gate_compliance', 'min_B', 'max_B', 'B_sweep', 'resistance', 'current', 'voltage_range_2', 'compliance_voltage'],
            displays=['gate_voltage','voltage_offset', 'voltage_amplitude', 'frequency', 'min_B', 'max_B', 'B_sweep', 'current'],
            x_axis='Field (T)',
            y_axis='AC Resistance (ohm)'
        )
        self.setWindowTitle('RvH')
 
    def queue(self):

        directory = "./Data"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='RvH')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)