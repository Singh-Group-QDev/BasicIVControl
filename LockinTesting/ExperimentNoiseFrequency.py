import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from LockinTesting.ProcedureNoiseFrequency import ProcedureNoiseFrequency


class ExperimentNoiseFrequency(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureNoiseFrequency,
            inputs=['gate_voltage','voltage_offset', 'voltage_amplitude', 'min_frequency', 'max_frequency', 'frequency_step', 'delay', 'voltage_range',  'gate_compliance', 'B'],
            displays=['gate_voltage','voltage_offset', 'voltage_amplitude', 'min_frequency', 'max_frequency', 'B'],
            x_axis='Frequency (Hz)',
            y_axis='Lockin X STD (V)'
        )
        self.setWindowTitle('Lockin Noise Frequency Sweep')
 
    def queue(self):

        directory = "./Data"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='LCK_NS')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)