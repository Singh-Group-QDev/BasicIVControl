import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import tempfile
import random
from time import sleep
import numpy as np
from pymeasure.log import console_log
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter
from pymeasure.instruments.keithley import Keithley2000, Keithley2400

class ProcedureIV(Procedure):

    max_current = FloatParameter('Maximum Current', units='mA', default=11)
    min_current = FloatParameter('Minimum Current', units='mA', default=-11)
    current_step = FloatParameter('Current Step', units='mA', default=0.1)
    delay = FloatParameter('Delay Time', units='ms', default=20)
    voltage_range = FloatParameter('Voltage Range', units='V', default=10)

    DATA_COLUMNS = ['Current (A)', 'Voltage (V)', 'Resistance (ohm)']

    def startup(self):
        log.debug("Setting up instruments")
        self.meter = Keithley2400("GPIB::21")
        self.meter.reset()
        self.meter.measure_voltage()
        self.meter.voltage_range = self.voltage_range
        self.meter.voltage_nplc = 1  # Integration constant to Medium
        self.meter.enable_source()

        self.source = Keithley2400("GPIB::23")
        self.source.reset()
        self.source.apply_current()
        self.source.source_current_range = self.max_current * 1e-3  # A
        self.source.compliance_voltage = self.voltage_range
        self.source.enable_source()
        sleep(2)

    def execute(self):
        currents_up = np.arange(self.min_current, self.max_current, self.current_step)
        currents_down = np.arange(self.max_current, self.min_current, -self.current_step)
        currents = np.concatenate((currents_up, currents_down))  # Include the reverse
        currents *= 1e-3  # to mA from A
        steps = len(currents)

        log.info("Starting to sweep through current")
        for i, current in enumerate(currents):
            log.info("Measuring current: %g mA" % current)

            self.source.source_current = current
            
            # Or use self.source.ramp_to_current(current, delay=0.1)
            sleep(self.delay * 1e-3)
            
            voltage = self.meter.voltage
            
            if abs(current) <= 1e-10:
                resistance = np.nan
            else:
                resistance = voltage / current
            data = {
                'Current (A)': current,
                'Voltage (V)': voltage,
                'Resistance (ohm)': resistance
            }
            
            self.emit('results', data)
            self.emit('progress', 100. * i / steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        self.source.shutdown()
        self.meter.shutdown()
        log.info("Finished")