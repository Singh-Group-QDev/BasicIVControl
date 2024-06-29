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
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter, BooleanParameter
from pymeasure.instruments.keithley import Keithley2000, Keithley2400
from pymeasure.instruments.lakeshore import LakeShore331
from Helpers import waitForTempBelow

class ProcedureCurrent(Procedure):
    source = None
    lakeshore = None
    max_current = FloatParameter('Maximum Current', units='nA', default=.2)
    min_current = FloatParameter('Minimum Current', units='nA', default=-.2)
    current_step = FloatParameter('Current Step', units='nA', default=0.025)
    delay = FloatParameter('Delay Time', units='ms', default=200)
    voltage_range = FloatParameter('Voltage Range', units='mV', default=1000)
    compliance_voltage_range = FloatParameter('Compliance Voltage Range', units='V', default=2)
    temp_below = FloatParameter('Temperature', units='K', default=300)
    hysteresis = BooleanParameter('Hysteresis',default=True)
    fourwire = BooleanParameter('Four Wire',default=False)
    concurrent = BooleanParameter('Concurrent', default=True)
    #charge_delay = FloatParameter('Charge Delay', units='s',default=1)

    DATA_COLUMNS = ['Current (A)', 'Current STD (A)', 'Voltage (V)', 'Voltage STD (V)', 'Temperature A (K)', 'Temperature B (K)']

    def startup(self):
        log.debug("Setting up instruments")
        self.wires = 2
        if self.fourwire:
            self.wires = 4
        self.lakeshore = LakeShore331(12)
        self.source = Keithley2400("GPIB::24")
        self.source.reset()
        self.source.wires = self.wires
        self.source.measure_concurent_functions = self.concurrent
        self.source.apply_current()

        if not self.concurrent:
            self.source.measure_voltage()
        else:
            self.source.write("SENS:FUNC:ON 'VOLT', 'CURR'")
            self.source.voltage_nplc = 1
            self.source.current_nplc = 1
            self.current_range = self.max_current * 1e-9

        self.source.source_current_range = self.max_current * 1e-9
        self.source.voltage_range = self.voltage_range * 1e-3  # V
        self.source.compliance_voltage = self.compliance_voltage_range
        self.source.enable_source()
        sleep(2)

    def execute(self):
        currents = []

        if(self.hysteresis):
            current_up1 = np.arange(0, self.max_current, self.current_step)
            current_down = np.arange(self.max_current,self.min_current,-self.current_step)
            current_up2 = np.arange(self.min_current,0,self.current_step)
            currents = np.concatenate((current_up1,current_down,current_up2))
            currents = np.append(currents,0)
        else:
            currents = np.arange(self.min_current,self.max_current,self.current_step)
        currents *= 1e-9 # nA
        steps = len(currents)
        temp_voltages = []
        self.source.source_current = 0.0
        sleep(self.delay * 5 * 1e-3)
        for i in range(100):
            if self.concurrent:
                data = self.source.values(":READ?")
                temp_voltages.append(data[0])
            else:
                temp_voltages.append(self.source.voltage)
            sleep(1e-3)

        zero_voltage = np.mean(temp_voltages)
        zero_voltageSTD = np.std(temp_voltages)
        log.info('Voltage at zero current: {} +/- {}'.format(zero_voltage, zero_voltageSTD))
        log.info("Starting to sweep through voltages")

        for i, current in enumerate(currents):
            # self.source.source_voltage = 0
            # sleep(self.charge_delay)
            temp_voltages = []
            temp_currents = []
            log.info("Measuring at current: %g A" % current)
            #waitForTempBelow(self.triton, self.source, self.stay_below * 1e-3)
            self.source.source_current = current
            self.source.voltage # Make the display show voltage
            # Or use self.source.ramp_to_current(current, delay=0.1)
            sleep(self.delay * 1e-3)
            for j in range(20):
                if not self.concurrent:
                    temp_voltages.append(self.source.voltage)
                else: 
                    data = self.source.values(":READ?")
                    temp_voltages.append(data[0])
                    temp_currents.append(data[1])

            voltage = np.mean(temp_voltages)
            voltage_std = np.std(temp_voltages)
            currentdata = current if not self.concurrent else np.mean(temp_currents)
            currentSTD = np.nan if not self.concurrent else np.std(temp_currents)
            data = {
                'Current (A)': currentdata,
                'Current STD (A)': currentSTD,
                'Voltage (V)': voltage-zero_voltage,
                'Voltage STD (V)': voltage_std,
                'Temperature A (K)': self.lakeshore.input_A.kelvin,
                'Temperature B (K)': self.lakeshore.input_B.kelvin
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