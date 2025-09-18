import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import tempfile
import random
from time import sleep, time
import numpy as np
from pymeasure.log import console_log
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter, BooleanParameter
from pymeasure.instruments.srs import SR830

class ProcedureTimeDependence(Procedure):
    lockin = None
    
    DATA_COLUMNS = ['Lockin X (V)', 'Lockin Y (V)', 'Lockin R (V)', 'Time (s)']

    delay = FloatParameter('Delay', units = 'ms', default = 200)
    voltage_range = FloatParameter('Measured Current Range', units = 'uA', default = 1)

    def startup(self):

        """Initialize the lock-in amplifier."""
        log.info("Initializing lock-in amplifier")
        self.lockin = SR830(8)  # Update address as necessary
       # self.lockin.sensitivity = self.voltage_range * 1e-3
        log.info("Lock-in amplifier initialized")

    def execute(self):
        """Run the measurement procedure."""
        log.info("Starting measurement procedure")
        lockinx = []
        lockiny = []
        lockinr = []
        start_time = time()
        for _ in range(20000):  # Collect 1000 samples
            lockinx.append(self.lockin.x)
            lockiny.append(self.lockin.y)
            lockinr.append(self.lockin.magnitude)
            elapsed_time = time() - start_time
            data = {
            'Lockin X (V)': self.lockin.x,
            'Lockin Y (V)': self.lockin.y,
            'Lockin R (V)' : self.lockin.magnitude,
            'Time (s)': elapsed_time,
            }
            sleep(self.delay*1e-3)  # Convert delay to miliseconds
            log.info(f"Emitting results: {data}")
            self.emit('results', data)

            if self.should_stop():
                log.warning("Stop command received during measurement")
                return

    def shutdown(self):
        """Clean up resources."""
        log.info("Shutting down procedure")
        # if self.lockin:
        #     del self.lockin 
        log.info("Procedure finished")