import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import tempfile
from time import sleep
from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results
from InstrumentControlExamples.ProcedureRandom import RandomProcedure

class RandomExperiment(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class = RandomProcedure,
            inputs=['iterations', 'delay', 'seed'],
            displays=['iterations', 'delay', 'seed'],
            x_axis='Iteration',
            y_axis='Random Number'
        )
        self.setWindowTitle('GUI Example')

    def queue(self):
        filename = tempfile.mktemp()

        #procedure = RandomProcedure()
        #procedure.seed = str(self.inputs.seed.text())
        #procedure.iterations = self.inputs.iterations.value()
        #procedure.delay = self.inputs.delay.value()

        procedure = self.make_procedure()

        results = Results(procedure, filename)

        experiment = self.new_experiment(results)

        self.manager.queue(experiment)