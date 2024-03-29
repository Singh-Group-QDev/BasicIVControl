import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from TemperatureSweeps.ProcedureLockinResistivity import ProcedureLockinResistivity

class ExperimentLockinResistivity(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureLockinResistivity,
            inputs=['amplitude', 'resistance', 'frequency', 'tempmin'],
            displays=['amplitude', 'resistance', 'frequency', 'tempmin'],
            x_axis='Temperature (K)',
            y_axis='Resistance (ohm)'
        )
        self.setWindowTitle('GUI Example')
 
    def queue(self):

        directory = "./"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='RT')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)