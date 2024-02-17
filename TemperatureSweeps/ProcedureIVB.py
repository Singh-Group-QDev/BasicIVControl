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

class ProcedureIVB(Procedure):
    source = None
    meter = None
    triton = None
    max_current = FloatParameter('Maximum Current', units='uA', default=50)
    min_current = FloatParameter('Minimum Current', units='uA', default=0)
    current_step = FloatParameter('Current Step', units='uA', default=0.5)
    delay = FloatParameter('Delay Time', units='ms', default=20)
    voltage_range = FloatParameter('Voltage Range', units='mV', default=200)
    compliance_voltage_range = FloatParameter('Compliance Voltage Range', units='V', default=10)
    bfield = FloatParameter('Magnetic Field Strength', units='mT', default=0)
    stay_below = FloatParameter('Stay Below Temperature', units='mK', default=500)

    DATA_COLUMNS = ['Current (A)', 'Voltage (V)', 'Voltage STD (V)', 'B Field (T)', 'Temperature (K)']

    def startup(self):
        log.debug("Setting up instruments")

        self.triton = Triton()
        self.triton.connect(edsIP = "138.67.20.104")
        self.triton.goto_bfield(self.bfield*1e-3, wait=True, log=log)
        log.info('Set B field to {} mT. Measured B field: {} mT'.format(self.bfield, self.triton.get_Bfield()*10**3))

        self.meter = Keithley2400("GPIB::23")
        self.meter.reset()
        self.meter.apply_current()
        self.meter.source_current = 0
        self.meter.measure_voltage()
        self.meter.voltage_range = self.voltage_range * 1e-3
        self.meter.compliance_voltage = self.voltage_range * 1e-3
        self.meter.voltage_nplc = 1  # Integration constant to Medium
        self.meter.enable_source()
        
        self.source = Keithley2400("GPIB::21")
        self.source.reset()
        self.source.apply_current()
        self.source.source_current_range = self.max_current * 1e-6  # A
        self.source.compliance_voltage = self.compliance_voltage_range
        self.source.enable_source()
        sleep(2)

    def execute(self):
        currents_up = np.arange(self.min_current, self.max_current, self.current_step)
        #currents_down = np.arange(self.max_current, self.min_current, -self.current_step)
        #currents = np.concatenate((currents_up, currents_down))  # Include the reverse
        currents = currents_up
        currents *= 1e-6  # to uA from A
        steps = len(currents)

        temp_voltages = []
        self.source.source_current = 0.0
        sleep(self.delay * 1e-3)
        for i in range(20):
            temp_voltages.append(self.meter.voltage)

        zero_voltage = np.mean(temp_voltages)
        zero_voltageSTD = np.std(temp_voltages)
        log.info('Voltage at zero current: {} +/- {}'.format(zero_voltage, zero_voltageSTD))
        log.info("Starting to sweep through current")

        for i, current in enumerate(currents):
            temp_voltages = []
            log.info("Measuring current: %g A" % current)
            waitForTempBelow(self.triton, self.source, self.stay_below * 1e-3)
            self.source.source_current = current
            
            # Or use self.source.ramp_to_current(current, delay=0.1)
            sleep(self.delay * 1e-3)
            if(i <= 4):
                sleep(10)
            for j in range(20):
                temp_voltages.append(self.meter.voltage)
            voltage = np.mean(temp_voltages)
            voltage_std = np.std(temp_voltages)

            data = {
                'Current (A)': current,
                'Voltage (V)': voltage,
                'Voltage STD (V)': voltage_std,
                'B field (T)': self.triton.get_Bfield(),
                'Temperature (K)': self.triton.get_temp_T8()
            }
            
            self.emit('results', data)
            self.emit('progress', 100. * i / steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        if(self.source is not None):
            self.source.shutdown()
        if(self.meter is not None):
            self.meter.shutdown()
        if(self.triton is not None):
            self.triton.disconnect()
        log.info("Finished")