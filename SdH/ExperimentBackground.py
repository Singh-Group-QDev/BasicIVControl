import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from SdH.ProcedureBackground import ProcedureBackground


class ExperimentBackground(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureBackground,
            inputs=['gate_voltage','min_current', 'max_current', 'current_step', 'delay', 'source_compliance', 'voltage_range', 'gate_compliance', 'hysteresis', 'min_B', 'four_wire', 'duration'],
            displays=['gate_voltage', 'min_current', 'max_current', 'current_step', 'delay', 'voltage_range', 'hysteresis','min_B'],
            x_axis='Time (s)',
            y_axis='Resistance (ohm)'
        )
        self.setWindowTitle('Transistor 4-Wire IV Background')
 
    def queue(self):

        directory = "./Data"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='OSC_b')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)