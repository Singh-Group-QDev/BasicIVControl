import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import tempfile
import sys
from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from TransistorSweeps.ProcedureOutput import ProcedureOutput

class ExperimentOutput(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureOutput,
            inputs=['max_voltage', 'min_voltage', 'voltage_step', 'compliance_current', 'delay', 'current_range', 'gate_voltage'],
            displays=['max_voltage', 'min_voltage', 'voltage_step', 'compliance_current', 'delay', 'current_range', 'gate_voltage'],
            x_axis='SD Voltage (V)',
            y_axis='SD Current (A)'
        )
        self.setWindowTitle('Transistor Output Characteristics')
 
    def queue(self):

        directory = "./"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='TTO')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)
    


    