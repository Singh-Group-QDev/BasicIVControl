import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from SdH.ProcedureInverseB import ProcedureInverse


class ExperimentInverse(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureInverse,
            inputs=['gate_voltage','voltage_offset', 'voltage_amplitude', 'frequency', 'delay', 'voltage_range', 'gate_compliance', 'min_invB', 'max_invB', 'step', 'resistance'],
            displays=['gate_voltage','voltage_offset', 'voltage_amplitude', 'frequency', 'min_invB', 'max_invB'],
            x_axis='Inverse Field (1/T)',
            y_axis='Lockin X (V)'
        )
        self.setWindowTitle('SdH Sweep with even 1/T spacing')
 
    def queue(self):

        directory = "./Data"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='OSC_INV')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)