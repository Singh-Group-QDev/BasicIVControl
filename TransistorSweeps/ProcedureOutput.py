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

class ProcedureOutput(Procedure):

    max_voltage = FloatParameter('Maximum S/D Voltage', units='V', default=1)
    min_voltage = FloatParameter('Minimum S/D Voltage', units='V', default=0)
    voltage_step = FloatParameter('S/D Voltage Step', units='V', default=0.01)
    compliance_current = FloatParameter('Compliance Current', units='mA', default=1)
    delay = FloatParameter('Delay Time', units='ms', default=20)
    current_range = FloatParameter('Expected Current Range', units='mA', default=1)
    gate_voltage = FloatParameter('Gate Voltage', units='V', default=0)


    DATA_COLUMNS = ['SD Current (A)', 'GS Current (A)', 'SD Voltage (V)', 'Source-Drain Resistance (ohm)', 'Field Oxide Resistance (ohm)']

    def startup(self):
        log.debug("Setting up instruments")
        # SD Voltage
        self.source1 = Keithley2400("GPIB::24")
        self.source1.reset()
        self.source1.apply_voltage()
        self.source1.compliance_current = self.compliance_current * 1e-3
        self.source1.measure_current()
        self.source1.current_range = self.current_range * 1e-3
        self.source1.enable_source()

        # Gate Voltage
        self.source2 = Keithley2400("GPIB::19")
        self.source2.reset()
        self.source2.apply_voltage()
        self.source2.compliance_current = self.compliance_current * 1e-3
        self.source2.measure_current()
        self.source2.current_range = self.current_range * 1e-3
        self.source2.enable_source()
        sleep(2)

    def execute(self):
        #Zero the keithleys
        zero_array1 = []
        zero_array2 = []
        self.source1.source_voltage = 0.0
        self.source2.source_voltage = 0.0
        for i in range(10):
            zero_array1.append(self.source1.current)
            zero_array2.append(self.source2.current)
            sleep(100*1e-3)
        GZero = np.mean(zero_array2)
        SDZero = np.mean(zero_array1)
        log.info('Gate zero: {} uA'.format(GZero*1e6))
        log.info('Drain zero: {} uA'.format(SDZero*1e6))

        voltages = np.arange(self.min_voltage, self.max_voltage, self.voltage_step)
        steps = len(voltages)

        log.info('Setting Gate Voltage to: %g V', self.gate_voltage)
        self.source2.source_voltage = self.gate_voltage

        log.info("Starting to sweep through S/D voltages")
        for i, voltage in enumerate(voltages):
            log.debug("Applying S/D voltage: %g V" % voltage)
            self.source1.source_voltage = voltage
            sleep(self.delay * 1e-3)
            SDCurrent = self.source1.current-SDZero
            GSCurrent = self.source2.current-GZero
            if abs(SDCurrent) <= 1e-10:
                SDresistance = np.nan
            else:
                SDresistance = voltage / SDCurrent

            if abs(GSCurrent) <= 1e-10:
                GSresistance = np.nan
            else:
                GSresistance = self.gate_voltage / GSCurrent
            data = {
                'SD Current (A)': SDCurrent,
                'GS Current (A)': GSCurrent,
                'SD Voltage (V)': voltage,
                'Source-Drain Resistance (ohm)': SDresistance,
                'Field Oxide Resistance (ohm)': GSresistance
            }
            
            self.emit('results', data)
            self.emit('progress', 100. * i / steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        self.source1.shutdown()
        self.source2.shutdown()
        log.info("Finished")