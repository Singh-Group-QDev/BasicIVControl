import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from DeltaMode.ProcedureDeltaTest import ProcedureDeltaTest


class ExperimentDeltaTest(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureDeltaTest,
            inputs=['delay', 'delta_count', 'voltage_range','source_compliance','max_current','min_current','current_step','hysteresis'],
            displays=['voltage_range','max_current','min_current','current_step','hysteresis'],
            x_axis='Applied Current (A)',
            y_axis='Measured Voltage (V)'
        )
        self.setWindowTitle('Delta Mode Test')
 
    def queue(self):

        directory = "./Data/DeltaModeTest"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='DMT')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)