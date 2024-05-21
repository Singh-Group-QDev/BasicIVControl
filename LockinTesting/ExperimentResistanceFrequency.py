import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from LockinTesting.ProcedureResistanceFrequency import ProcedureResistanceFrequency

class ExperimentResistanceFrequency(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureResistanceFrequency,
            inputs=['amplitude', 'resistance', 'frequencyMin', 'frequencyMax', 'frequencyStep'],
            displays=['amplitude', 'resistance', 'frequencyMin', 'frequencyMax', 'frequencyStep'],
            x_axis='Frequency (Hz)',
            y_axis='Resistance from Lockin R (ohm)'
        )
        self.setWindowTitle('GUI Example')
 
    def queue(self):

        directory = "./Data/Lockin_Testing"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='RF')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)