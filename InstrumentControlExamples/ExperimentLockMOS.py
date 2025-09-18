import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from InstrumentControlExamples.ProcedureLockMOS import ProcedureLockMOS

class ExperimentLockMOS(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureLockMOS,
            inputs=['amplitude', 'frequency', 'gateVoltageMin', 'gateVoltageMax', 'gateVoltageStep'],
            displays=['amplitude', 'frequency', 'gateVoltageMin', 'gateVoltageMax', 'gateVoltageStep'],
            x_axis='Gate Voltage (V)',
            y_axis='R (A)'
        )
        self.setWindowTitle('Lockin MOSFET Example')
 
    def queue(self):

        directory = "./Data/Lockin_Testing"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='LOCKMOS')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)