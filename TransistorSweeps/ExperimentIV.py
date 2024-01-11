import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import tempfile
import sys
from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from InstrumentControlExamples.ProcedureIV import ProcedureIV

class ExperimentIV(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureIV,
            inputs=['max_current', 'min_current', 'current_step', 'delay', 'voltage_range'],
            displays=['max_current', 'min_current', 'current_step', 'delay', 'voltage_range'],
            x_axis='Current (A)',
            y_axis='Voltage (V)'
        )
        self.setWindowTitle('GUI Example')
 
    def queue(self):

        directory = "./"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='IV')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)
    


    