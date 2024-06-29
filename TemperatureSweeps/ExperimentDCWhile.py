import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import tempfile
import sys
from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from TemperatureSweeps.ProcedureDCWhile import ProcedureDCWhile

class ExperimentDCWhile(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureDCWhile,
            inputs=['min_voltage', 'max_voltage', 'voltage_step', 'delay', 'current_range', 'compliance_current_range'],
            displays=['min_voltage', 'max_voltage', 'voltage_step'],
            x_axis='Voltage (V)',
            y_axis='Current (A)'
        )
        self.setWindowTitle('DC 4 Probe While Cooling')
 
    def queue(self):

        directory = "./Data/CISS"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='DCW')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)