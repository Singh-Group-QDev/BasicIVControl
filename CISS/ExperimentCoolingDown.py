import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from CISS.ProcedureCoolingDown import ProcedureCoolingDown

class ExperimentCoolingDown(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureCoolingDown,
            inputs=['min_current', 'max_current', 'current_step', 'delay', 'source_compliance', 'voltage_range', 'hysteresis', 'from_zero', 'target_temp'],
            displays=['min_current', 'max_current', 'current_step', 'delay', 'hysteresis', 'target_temp'],
            x_axis='Current (A)',
            y_axis='Voltage L (V)',
            sequencer = True,
            sequencer_inputs=['target_temp']
        )
        self.setWindowTitle('IV Curves While Cooling')
 
    def queue(self, procedure=None):

        directory = "./Data/CISS"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='CD')
        if(procedure == None):
            procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)