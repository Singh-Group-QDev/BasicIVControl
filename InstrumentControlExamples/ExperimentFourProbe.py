import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import tempfile
import sys
from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from InstrumentControlExamples.ProcedureFourProbe import ProcedureFourProbe

class ExperimentFourProbe(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureFourProbe,
            inputs=['min_voltage', 'max_voltage', 'voltage_step', 'delay', 'current_range', 'compliance_current_range'],
            displays=['min_voltage', 'max_voltage', 'voltage_step'],
            x_axis='Voltage (V)',
            y_axis='Current (A)'
        )
        self.setWindowTitle('Voltage 4 Probe')
 
    def queue(self):

        directory = "./Data/IVB"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='V4P')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)