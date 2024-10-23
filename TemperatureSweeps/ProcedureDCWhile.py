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
from pymeasure.instruments.oxfordinstruments import Triton


class ProcedureDCWhile(Procedure):
    source = None
    lakeshore = None
    voltage_range = FloatParameter('Voltage Range', units='mV', default=20)
    current = FloatParameter('Source Current', units='uA', default=.25)
    delay = FloatParameter('Delay Time', units='ms', default=200)
    compliance_voltage = FloatParameter('Compliance Voltage', units='mV', default=500)
    #charge_delay = FloatParameter('Charge Delay', units='s',default=1)

    DATA_COLUMNS = ['Voltage (V)', 'Voltage STD (V)', 'Resistance (ohm)','Resistance STD (ohm)', 'Temperature 5 (K)','Temperature 8 (K)']

    def startup(self):
        log.debug("Setting up instruments")

        #self.lakeshore = LakeShore331(12)
        self.triton = Triton()
        self.triton.connect(edsIP = "138.67.20.104")

        self.source = Keithley2400("GPIB::24")
        self.source.reset()
        self.source.wires = 2
        self.source.apply_current()
        self.source.measure_voltage()
        self.source.compliance_voltage = self.compliance_voltage*1e-3
        self.source.voltage_range = self.voltage_range*1e-3
        self.source.enable_source()
        sleep(2)

    def execute(self):
        temperature = self.triton.get_temp_T8();
        while(temperature<1):
            temp_voltages = []
            self.source.source_current = 0.0
            sleep(self.delay * 1e-3)
            for i in range(100):
                temp_voltages.append(self.source.voltage)
                sleep(1e-3)
            sleep(1)
            zero_voltage = np.mean(temp_voltages)
            zero_voltageSTD = np.std(temp_voltages)
            log.info('Voltage at zero current: {} +/- {} mV'.format(zero_voltage*1e3, zero_voltageSTD*1e3))
            temp_voltages=[]
            self.source.source_current = self.current*1e-6           
            sleep(self.delay * 1e-3)
            for j in range(20):
                temp_voltages.append(self.source.voltage-zero_voltage)
                sleep(100e-3)
            self.source.source_current = 0.0
            data = {
                #'Temperature (K)': self.lakeshore.input_A.kelvin,
                'Voltage (V)': np.mean(temp_voltages),
                'Voltage STD (V)': np.std(temp_voltages),
                'Resistance (ohm)': np.mean(temp_voltages)/(self.current*1e-6),
                'Resistance STD (ohm)': np.std(temp_voltages)/(self.current*1e-6),
                'Temperature 5 (K)': self.triton.get_temp_T5(),
                'Temperature 8 (K)': self.triton.get_temp_T8()
            }
            temperature = self.triton.get_temp_T8()
            self.emit('results', data)
            self.emit('progress', 0)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break
            sleep(70)

    def shutdown(self):
        if(self.source is not None):
            self.source.shutdown()
        log.info("Finished")