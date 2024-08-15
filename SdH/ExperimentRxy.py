import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from SdH.ProcedureRxy import ProcedureRxy


class ExperimentRxy(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureRxy,
            inputs=['gate_voltage','current', 'delay', 'source_compliance', 'voltage_range', 'gate_compliance', 'min_B', 'max_B', 'B_step', 'B_sweep', "sweep_rate"],
            displays=['gate_voltage','current', 'delay', 'voltage_range', 'min_B', 'max_B', 'B_step'],
            x_axis='Field (T)',
            y_axis='Resistance XY (ohm)'
        )
        self.setWindowTitle('Transistor 4-Wire IV with B Field')
 
    def queue(self):

        directory = "./Data"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='Rxy')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)