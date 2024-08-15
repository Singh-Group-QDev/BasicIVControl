import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from SdH.ProcedureACDC import ProcedureACDC


class ExperimentACDC(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureACDC,
            inputs=['gate_voltage','current', 'voltage_range', 'gate_compliance', 'Rxx', 'voltage_offset', 'voltage_amplitude', 'frequency', 'voltage_lockin', 'min_B', 'max_B', 'hysteresis', 'from_zero', 'B_step', 'B_sweep', "sweep_rate", 'resistance'],
            displays=['gate_voltage','current', 'min_B', 'max_B', 'B_step'],
            x_axis='Field (T)',
            y_axis='Resistance XY (ohm)'
        )
        self.setWindowTitle('Transistor 4-Wire IV with B Field')
 
    def queue(self):

        directory = "./Data"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='ACDC')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)