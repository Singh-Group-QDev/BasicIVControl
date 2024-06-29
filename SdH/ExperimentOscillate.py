import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from SdH.ProcedureOscillate import ProcedureOscillate


class ExperimentOscillate(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureOscillate,
            inputs=['min_current', 'max_current', 'current_step', 'delay', 'source_compliance', 'voltage_range', 'gate_compliance', 'hysteresis', 'min_B', 'max_B', 'B_sweep'],
            displays=['min_current', 'max_current', 'current_step', 'delay', 'voltage_range', 'hysteresis','min_B', 'max_B', 'B_sweep'],
            x_axis='Voltage (V)',
            y_axis='Current (A)'
        )
        self.setWindowTitle('Transistor 4-Wire IV with B Field')
 
    def queue(self):

        directory = "./Data"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='OSC')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)