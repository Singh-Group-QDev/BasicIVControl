import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep, time
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from LockinTesting.ProcedureTimeDependence import ProcedureTimeDependence   


class ExperimentTimeDependence(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureTimeDependence,
            inputs=['delay', 'voltage_range'],
            displays=['voltage_range'],
            x_axis='Time (s)',
            y_axis='Lockin R (V)'
        )
        self.setWindowTitle('Lockin Measured Current Time Dependence')
 
    def queue(self):

        directory = "./Data/Lockin_Testing"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='noise_jan25')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)