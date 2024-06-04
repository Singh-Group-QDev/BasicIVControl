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
from pymeasure.instruments.oxfordinstruments import Triton
from Helpers import waitForTempBelow

class Procedure4Probe(Procedure):
    source = None
    triton = None
    max_voltage = FloatParameter('Maximum Voltage', units='V', default=1)
    min_voltage = FloatParameter('Minimum Voltage', units='V', default=0)
    voltage_step = FloatParameter('Voltage Step', units='V', default=0.01)
    delay = FloatParameter('Delay Time', units='ms', default=20)
    current_range = FloatParameter('Current Range', units='uA', default=1)
    compliance_current_range = FloatParameter('Compliance Current Range', units='uA', default=10)

    DATA_COLUMNS = ['Current (A)', 'Voltage (V)', 'Voltage STD (V)']

    def startup(self):
        log.debug("Setting up instruments")
        
        self.source = Keithley2400("GPIB::24")
        self.source.reset()
        self.source.wires = 4
        self.source.apply_voltage()
        self.source.measure_current()
        self.source.source_voltage_range = self.max_voltage
        self.source.current_range = self.current_range * 1e-6  # A
        self.source.compliance_current = self.compliance_current_range
        self.source.enable_source()
        sleep(2)

    def execute(self):
        voltage_up = np.arange(self.min_voltage, self.max_voltage, self.voltage_step)
        #currents_down = np.arange(self.max_current, self.min_current, -self.current_step)
        #currents = np.concatenate((currents_up, currents_down))  # Include the reverse
        voltages = voltage_up
        steps = len(voltages)

        temp_currents = []
        self.source.source_voltage = 0.0
        sleep(self.delay * 1e-3)
        for i in range(20):
            temp_currents.append(self.source.current)

        zero_current = np.mean(temp_currents)
        zero_currentSTD = np.std(temp_currents)
        log.info('Current at zero voltage: {} +/- {}'.format(zero_current, zero_currentSTD))
        log.info("Starting to sweep through voltages")

        for i, voltage in enumerate(voltages):
            temp_currents = []
            log.info("Measuring at voltage: %g A" % voltage)
            #waitForTempBelow(self.triton, self.source, self.stay_below * 1e-3)
            self.source.source_voltage = voltage
            
            # Or use self.source.ramp_to_current(current, delay=0.1)
            sleep(self.delay * 1e-3)
            for j in range(20):
                temp_currents.append(self.source.current)
            current = np.mean(temp_currents)
            current_std = np.std(temp_currents)

            data = {
                'Current (A)': current,
                'Voltage (V)': voltage,
                'Current STD (A)': current_std
            }
            
            self.emit('results', data)
            self.emit('progress', 100. * i / steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        if(self.source is not None):
            self.source.shutdown()
        log.info("Finished")