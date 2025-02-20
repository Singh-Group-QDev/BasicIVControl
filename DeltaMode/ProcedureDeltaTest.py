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
from pymeasure.instruments.keithley import Keithley2000, Keithley2400, Keithley2182, Keithley6221
from pymeasure.instruments.srs import SR830
from pymeasure.instruments.agilent import Agilent33220A
from pymeasure.instruments.oxfordinstruments import Triton

class ProcedureDeltaTest(Procedure):
    # awg = None
    # lockin = None
    source = None
    nvm = None

    DATA_COLUMNS = ['Time (s)', 'Field (T)', 'Applied Current (A)', 'Measured Voltage (V)']

    gate_voltage = FloatParameter('Gate Voltage', units = 'V', default = 5)
    delay = FloatParameter('Delay', units = 's', default = .005)
    delta_count = IntegerParameter('Delta Counts', default = 16)
    voltage_range = FloatParameter('Measured Voltage Range', units = 'V', default = .1)
    source_compliance = FloatParameter('Source Compliance Voltage', units = 'V', default = 1)
    max_current = FloatParameter('Maximum Current', units='uA', default=100)
    min_current = FloatParameter('Minimum Current', units='uA', default=0)
    current_step = FloatParameter('Current Step', units='uA', default=2)
    hysteresis = BooleanParameter('Hysteresis', default=False)

    def startup(self):

        # self.nvm = Keithley2182(15)
        # self.nvm.reset()
        # self.nvm.ch_1.setup_voltage()
        # self.nvm.active_channel = 1
        # self.nvm.sample_continuously()

        self.source = Keithley6221(16)
        self.source.reset()
        self.source.source_compliance = self.source_compliance

        sleep(2)

    def execute(self):

        if(self.hysteresis):
            current_up1 = np.arange(0, self.max_current, self.current_step)
            current_down = np.arange(self.max_current,self.min_current,-self.current_step)
            current_up2 = np.arange(self.min_current,0,self.current_step)
            currents = np.concatenate((current_up1,current_down,current_up2))
            currents = np.append(currents,0)
        else:
            currents = np.arange(self.min_current,self.max_current,self.current_step)
        currents*=1e-6

        zero_time = time()
        for i,current in enumerate(currents):
            voltage = np.mean(self.measure(current))
            #zero_voltage_xy = np.mean(zero_voltages_xy)
            #log.info('XY Voltage at zero current: {}'.format(zero_voltage_xy))

            data = {
                'Time (s)': time() - zero_time,
                'Applied Current (A)': current,
                'Measured Voltage (V)': float(voltage)
            }

            self.emit('results', data)
            self.emit('progress', 100. * (i/len(currents)))
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break
    
    def measure(self, current):
        self.source.write("SOUR:DELT:HIGH %f" % current)
        self.source.write("SOUR:DELT:DELay %f" % self.delay)
        self.source.write("SOUR:DELT:COUN %f" % self.delta_count)
        self.source.write("SOUR:DELT:CAB ON")
        self.source.config_buffer(points=self.delta_count)
        self.source.write("SOUR:DELT:ARM")
        self.source.write("INIT:IMM")
        self.source.wait_for_buffer()
        self.source.write("SOUR:SWE:ABOR")
        self.source.write("FORMAT:ELEMENTS READING")
        numbers = self.source.ask("TRACe:DATA?")
        return np.fromstring(numbers,dtype=np.float32,sep=",")
    
    def shutdown(self):
        if(self.source is not None):
            self.source.shutdown()
        log.info("Finished")