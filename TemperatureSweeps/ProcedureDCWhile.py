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
from pymeasure.instruments.lakeshore import LakeShore331


class ProcedureDCWhile(Procedure):
    source = None
    lakeshore = None
    max_voltage = FloatParameter('Maximum Voltage', units='V', default=0.2)
    min_voltage = FloatParameter('Minimum Voltage', units='V', default=-0.2)
    voltage_step = FloatParameter('Voltage Step', units='V', default=0.05)
    delay = FloatParameter('Delay Time', units='ms', default=20)
    current_range = FloatParameter('Current Range', units='uA', default=1)
    compliance_current_range = FloatParameter('Compliance Current Range', units='uA', default=10)
    #charge_delay = FloatParameter('Charge Delay', units='s',default=1)

    DATA_COLUMNS = ['Temperature (K)', 'Voltage (V)', 'Current (A)', 'Current STD (A)']

    def startup(self):
        log.debug("Setting up instruments")

        self.lakeshore = LakeShore331(12)

        self.source = Keithley2400("GPIB::24")
        self.source.reset()
        self.source.wires = 2
        self.source.measure_concurent_functions = True
        self.source.apply_voltage()
        self.source.measure_current()
        self.source.source_voltage_range = self.max_voltage
        self.source.current_range = self.current_range * 1e-6  # A
        self.source.compliance_current = self.compliance_current_range
        self.source.measure_voltage()
        self.source.voltage_range = self.max_voltage
        self.source.enable_source()
        sleep(2)

    def execute(self):
        #voltage_up1 = np.arange(0, self.max_voltage, self.voltage_step)
        #voltage_down = np.arange(self.max_voltage,self.min_voltage,-self.voltage_step)
        #voltage_up2 = np.arange(self.min_voltage,0,self.voltage_step)
        voltages = np.arange(self.min_voltage,self.max_voltage,self.voltage_step)
        #currents_down = np.arange(self.max_current, self.min_current, -self.current_step)
        #currents = np.concatenate((currents_up, currents_down))  # Include the reverse
        #voltages = np.concatenate((voltage_up1,voltage_down,voltage_up2))
        steps = len(voltages)
        while True:
            temp_currents = []
            self.source.source_voltage = 0.0
            sleep(self.delay * 1e-3)
            for i in range(100):
                temp_currents.append(self.source.current)
                sleep(1e-3)
            sleep(1)
            zero_current = np.mean(temp_currents)
            zero_currentSTD = np.std(temp_currents)
            log.info('Current at zero voltage: {} +/- {}'.format(zero_current, zero_currentSTD))
            log.info("Starting to sweep through voltages")

            for i, voltage in enumerate(voltages):
                temp_currents = []
                self.source.source_voltage = voltage           
                # Or use self.source.ramp_to_current(current, delay=0.1)
                sleep(self.delay * 1e-3)
                for j in range(20):
                    temp_currents.append(self.source.current-zero_current)
                data = {
                    'Temperature (K)': self.lakeshore.input_A.kelvin,
                    'Voltage (V)': voltage,
                    'Current (A)': np.mean(temp_currents),
                    'Current STD (A)': np.std(temp_currents)
                }
            
                self.emit('results', data)
                self.emit('progress', 100. * i / steps)
                if self.should_stop():
                    log.warning("Catch stop command in procedure")
                    break
                self.source.source_voltage = 0.0
            sleep(30)

    def shutdown(self):
        if(self.source is not None):
            self.source.shutdown()
        log.info("Finished")