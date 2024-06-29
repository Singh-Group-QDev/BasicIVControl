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

class ProcedureIV2(Procedure):
    source = None
    meter = None
    lakeshore = None
    max_current = FloatParameter('Maximum Current', units='nA', default=.3)
    min_current = FloatParameter('Minimum Current', units='nA', default=-.3)
    current_step = FloatParameter('Current Step', units='nA', default=0.025)
    delay = FloatParameter('Delay Time', units='ms', default=200)
    voltage_range = FloatParameter('Voltage Range', units='mV', default=1000)
    compliance_voltage_range = FloatParameter('Compliance Voltage Range', units='V', default=2)
    temp_below = FloatParameter('Temperature', units='K', default=300)
    hysteresis = BooleanParameter('Hysteresis',default=True)
    concurrent = BooleanParameter('Concurrent', default=False)
    #charge_delay = FloatParameter('Charge Delay', units='s',default=1)

    DATA_COLUMNS = ['Source Current (A)', 'Source Current STD (A)', 'Source Voltage (V)', 'Source Voltage STD (V)', 'Measure Voltage (V)', 'Measure Voltage STD (V)', 'Temperature A (K)', 'Temperature B (K)']

    def startup(self):
        log.debug("Setting up instruments")
        self.lakeshore = LakeShore331(12)

        self.source = Keithley2400(19)
        self.source.reset()
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
        
        self.meter = Keithley2400(24)
        self.meter.reset()
        self.meter.apply_current()
        self.meter.measure_voltage()
        self.meter.voltage_range = self.voltage_range * 1e-3
        self.meter.compliance_voltage = self.compliance_voltage_range
        sleep(2)
        self.source.enable_source()
        self.meter.enable_source()
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
        temp_voltages_meas = []
        self.source.source_current = 0.0
        sleep(self.delay * 5 * 1e-3)
        for i in range(100):
            if self.concurrent:
                data = self.source.values(":READ?")
                temp_voltages.append(data[0])
            else:
                temp_voltages.append(self.source.voltage)
            temp_voltages_meas.append(self.meter.voltage)
            sleep(1e-3)
        zero_voltage = np.mean(temp_voltages)
        zero_voltage_meas = np.mean(temp_voltages_meas)
        zero_voltage_meas_STD = np.std(temp_voltages_meas)
        log.info('Voltage at zero current: {} +/- {}'.format(zero_voltage_meas, zero_voltage_meas_STD))
        log.info("Starting to sweep through voltages")

        for i, current in enumerate(currents):
            # self.source.source_voltage = 0
            # sleep(self.charge_delay)
            temp_meas_voltages = []
            temp_voltages = []
            temp_currents = []
            log.info("Measuring at current: %g A" % current)
            #waitForTempBelow(self.triton, self.source, self.stay_below * 1e-3)
            self.source.source_current = current
            self.source.voltage # Make the display show voltage
            # Or use self.source.ramp_to_current(current, delay=0.1)
            sleep(self.delay * 1e-3)
            for j in range(20):
                temp_meas_voltages.append(self.meter.voltage)
                if not self.concurrent:
                    temp_voltages.append(self.source.voltage)
                else: 
                    data = self.source.values(":READ?")
                    temp_voltages.append(data[0])
                    temp_currents.append(data[1])

            voltage = np.mean(temp_voltages)
            voltage_std = np.std(temp_voltages)
            voltage_meas = np.mean(temp_meas_voltages)
            voltage_meas_std = np.std(temp_meas_voltages)
            currentdata = current if not self.concurrent else np.mean(temp_currents)
            currentSTD = np.nan if not self.concurrent else np.std(temp_currents)
            data = {
                'Source Current (A)': currentdata,
                'Source Current STD (A)': currentSTD,
                'Source Voltage (V)': voltage-zero_voltage,
                'Source Voltage STD (V)': voltage_std,
                'Measure Voltage (V)':voltage_meas-zero_voltage_meas,
                'Measure Voltage STD (V)':voltage_meas_std,
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
        if(self.meter is not None):
            self.meter.shutdown()
        log.info("Finished")