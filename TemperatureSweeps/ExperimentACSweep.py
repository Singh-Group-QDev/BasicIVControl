import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from TemperatureSweeps.ProcedureACSweep import ProcedureACSweep

class ExperimentACSweep(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureACSweep,
            inputs=['amplitude', 'resistance', 'frequency', 'sensitivity','set_temp', 'ramp_rate', 'heater_range'],
            displays=['amplitude', 'resistance', 'frequency', 'sensitivity', 'set_temp', 'ramp_rate', 'heater_range'],
            x_axis='Temperature (K)',
            y_axis='SRSX (V)'
        )
        self.setWindowTitle('Lockin resistivity while temperature PID')
 
    def queue(self):

        directory = "./Data/"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='AC_PID')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)