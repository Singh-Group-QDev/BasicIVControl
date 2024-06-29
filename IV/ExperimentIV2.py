import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from IV.ProcedureIV2 import ProcedureIV2

class ExperimentIV2(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureIV2,
            inputs=['min_current', 'max_current', 'current_step', 'delay', 'voltage_range', 'compliance_voltage_range', 'temp_below', 'hysteresis', 'concurrent'],
            displays=['min_current', 'max_current', 'current_step', 'delay', 'temp_below', 'hysteresis', 'concurrent'],
            x_axis='Measure Voltage (V)',
            y_axis='Source Current (A)'
        )
        self.setWindowTitle('DC Probe While Cooling (2 Keithleys)')
 
    def queue(self):

        directory = "./Data/CISS"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='IV2')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)