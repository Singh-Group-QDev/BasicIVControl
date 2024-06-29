import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from TemperatureSweeps.ProcedureCoolingDC import ProcedureCoolingDC

class ExperimentCoolingDC(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureCoolingDC,
            inputs=['min_voltage', 'max_voltage', 'voltage_step', 'delay', 'current_range', 'compliance_current_range', 'temp_below', 'hysteresis', 'fourwire'],
            displays=['min_voltage', 'max_voltage', 'voltage_step', 'delay', 'temp_below', 'hysteresis', 'fourwire'],
            x_axis='Voltage (V)',
            y_axis='Current (A)'
        )
        self.setWindowTitle('DC Probe While Cooling (Source V Measure I)')
 
    def queue(self):

        directory = "./Data/CISS"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='V4P')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)