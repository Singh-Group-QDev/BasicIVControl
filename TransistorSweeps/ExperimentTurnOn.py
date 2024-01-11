import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import tempfile
import sys
from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from TransistorSweeps.ProcedureTurnOn import ProcedureTurnOn

class ExperimentTurnOn(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class = ProcedureTurnOn,
            inputs=['max_voltage', 'min_voltage', 'voltage_step', 'compliance_current', 'delay', 'current_range', 'SD_Voltage'],
            displays=['max_voltage', 'min_voltage', 'voltage_step', 'compliance_current', 'delay', 'current_range', 'SD_Voltage'],
            x_axis='Gate Voltage (V)',
            y_axis='SD Current (A)'
        )
        self.setWindowTitle('Transistor Turn-On')
 
    def queue(self):

        directory = "./"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='TTO')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)
    


    