import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from SdH.ProcedureOscillateAC import ProcedureOscillateAC


class ExperimentOscillateAC(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureOscillateAC,
            inputs=['gate_voltage','voltage_offset', 'voltage_amplitude', 'frequency', 'delay', 'voltage_range', 'voltage_range_2', 'gate_compliance', 'min_B', 'max_B', 'B_sweep', 'resistance'],
            displays=['gate_voltage','voltage_offset', 'voltage_amplitude', 'frequency', 'min_B', 'max_B', 'B_sweep', 'resistance'],
            x_axis='Field (T)',
            y_axis='Resistance (ohm)'
        )
        self.setWindowTitle('Transistor AC 4-Wire IV with B Field')
 
    def queue(self):

        directory = "./Data"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='OSC_AC')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)