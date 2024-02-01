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

class ProcedureTransfer(Procedure):

    max_voltage = FloatParameter('Maximum Gate Voltage', units='V', default=1)
    min_voltage = FloatParameter('Minimum Gate Voltage', units='V', default=0)
    voltage_step = FloatParameter('Gate Voltage Step', units='V', default=0.05)
    compliance_current = FloatParameter('Gate Compliance Current', units='mA', default=1)
    delay = FloatParameter('Delay Time', units='ms', default=20)
    current_range = FloatParameter('Expected SD Current Range', units='mA', default=1)
    SD_Voltage = FloatParameter('Source-Drain Voltage', units='V', default=1)

    DATA_COLUMNS = ['SD Current (A)', 'GS Current (A)','Gate Voltage (V)', 'Field Oxide Resistance (ohm)']

    def startup(self):
        log.debug("Setting up instruments")
        # Gate Voltage
        self.source1 = Keithley2400("GPIB::19")
        self.source1.reset()
        self.source1.apply_voltage()
        self.source1.compliance_current = self.compliance_current * 1e-3
        self.source1.measure_current()
        self.source1.current_range = self.current_range * 1e-3
        self.source1.enable_source()

        # SD Voltage
        self.source2 = Keithley2400("GPIB::24")
        self.source2.reset()
        self.source2.apply_voltage()
        self.source2.compliance_current = self.compliance_current * 1e-3
        self.source2.measure_current()
        self.source2.current_range = self.current_range * 1e-3
        self.source2.enable_source()
        sleep(2)

    def execute(self):
        voltages = np.arange(self.min_voltage, self.max_voltage, self.voltage_step)
        steps = len(voltages)

        log.info('Setting SD Voltage to: %g V', self.SD_Voltage)
        self.source2.source_voltage = self.SD_Voltage

        log.info("Starting to sweep through gate voltages")
        for i, voltage in enumerate(voltages):
            log.debug("Applying gate voltage: %g V" % voltage)
            self.source1.source_voltage = voltage
            sleep(self.delay * 1e-3)
            SDCurrent = self.source2.current
            GSCurrent = self.source1.current
            if abs(GSCurrent) <= 1e-10:
                resistance = np.nan
            else:
                resistance = voltage / GSCurrent
            data = {
                'SD Current (A)': SDCurrent,
                'GS Current (A)': GSCurrent,
                'Gate Voltage (V)': voltage,
                'Field Oxide Resistance (ohm)': resistance
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