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
from pymeasure.instruments.keithley import Keithley2000, Keithley2400, Keithley2182
from pymeasure.instruments.srs import SR830
from pymeasure.instruments.agilent import Agilent33220A
from pymeasure.instruments.oxfordinstruments import Triton

class ProcedureRxy(Procedure):
    # awg = None
    # lockin = None
    source = None
    gate = None
    triton = None
    nvm = None

    DATA_COLUMNS = ['Time (s)', 'Field (T)', 'Resistance (ohm)', 'Resistance STD (ohm)', 'Resistance XX (ohm)', 'Resistance XX STD (ohm)', 'Resistance XY (ohm)', 'Resistance XY STD (ohm)', 'Temperature 5 (K)', 'Temperature 8 (K)']

    gate_voltage = FloatParameter('Gate Voltage', units = 'V', default = 5)
    current = FloatParameter('Current', units = 'uA', default = 20)

    delay = FloatParameter('Delay', units = 's', default = 5)
    voltage_range = FloatParameter('Measured Voltage Range', units = 'V', default = 20)
    source_compliance = FloatParameter('Source Compliance Voltage', units = 'V', default = 5)
    gate_compliance = FloatParameter('Gate Compliance Current', units = 'mA', default = 1)

    min_B = FloatParameter('Minimum Magnetic Field', units = 'T', default = 0)
    max_B = FloatParameter('Maximum Magnetic Field', units = 'T', default = 2)
    B_step = FloatParameter('Magnetic Field Step', units = 'T', default = 0.1)
    B_sweep = BooleanParameter('Enforce sweep rate?', default = False)
    sweep_rate = FloatParameter('Sweep Rate', units = 'T/min', default = 0.01)

    def startup(self):

        self.nvm = Keithley2182(15)
        self.nvm.reset()
        self.nvm.ch_1.setup_voltage()
        self.nvm.active_channel = 1
        self.nvm.sample_continuously()

        self.nvmxx = Keithley2182(7)
        self.nvmxx.reset()
        self.nvmxx.ch_1.setup_voltage(auto_range = False)
        self.nvmxx.ch_1.voltage_range = 1
        self.nvmxx.active_channel = 1
        self.nvmxx.sample_continuously()

        self.triton = Triton()
        self.triton.connect(edsIP = "138.67.20.104")
        self.triton.set_poc_off()


        self.source = Keithley2400(24)
        self.gate = Keithley2400(19)

        self.source.apply_current(compliance_voltage = self.source_compliance)
        self.source.measure_voltage(voltage = self.voltage_range)

        self.gate.apply_voltage(voltage_range = 20, compliance_current = self.gate_compliance*1e-3)
        self.gate.measure_current() # auto range

        sleep(2)
        self.source.enable_source()
        self.gate.enable_source()

    def execute(self):
        Bfields = np.arange(self.min_B, self.max_B, self.B_step)
        self.gate.source_voltage = self.gate_voltage
        self.triton.goto_bfield(self.min_B, wait = True, log = log)
        zero_time = time()
        for B in Bfields:
            if(self.B_sweep):
                self.triton.goto_bfield(B, sweeprate = self.sweep_rate, wait = True, log = log)
            else:
                self.triton.goto_bfield(B, wait = True, log = log)
            zero_voltages = []
           # zero_voltages_xy = []
            self.source.source_current = 0
            sleep(100e-3)
            for i in range(10):
                sleep(100e-3)
                zero_voltages.append(self.source.voltage)
                #zero_voltages_xy.append(self.nvm.voltage)

            zero_voltage = np.mean(zero_voltages)
            zero_voltage_STD = np.std(zero_voltage)
            #zero_voltage_xy = np.mean(zero_voltages_xy)
            log.info('Voltage at zero current: {} +/- {}'.format(zero_voltage, zero_voltage_STD))
            #log.info('XY Voltage at zero current: {}'.format(zero_voltage_xy))
            
            bfield = self.triton.get_Bfield()

            v_p, v_p_std, v_xx_p, v_xx_p_std, v_h_p, v_h_p_std = self.measure(self.current*1e-6, zero_voltage)
            v_n, v_n_std, v_xx_n, v_xx_n_std, v_h_n, v_h_n_std = self.measure(-self.current*1e-6, zero_voltage)

            log.info("vp: {}, vn: {}, vhp:{}, vhn:{}".format(v_p,v_n, v_h_p, v_h_n))

            data = {
                'Time (s)': time() - zero_time,
                'Field (T)': bfield,
                'Resistance (ohm)': (v_p-v_n)/(self.current*1e-6),
                'Resistance STD (ohm)': (v_p_std+v_n_std)/(self.current*1e-6),
                'Resistance XX (ohm)': (v_xx_p-v_xx_n)/(self.current*1e-6),
                'Resistance XX STD (ohm)': (v_xx_p_std+v_xx_n_std)/(self.current*1e-6),
                'Resistance XY (ohm)': -(v_h_p-v_h_n)/(self.current*1e-6),
                'Resistance XY STD (ohm)': (v_h_p_std+v_h_n_std)/(self.current*1e-6),
                'Temperature 5 (K)': self.triton.get_temp_T5(),
                'Temperature 8 (K)': self.triton.get_temp_T8()
            }

            self.emit('results', data)
            self.emit('progress', 100. * (bfield-self.min_B) / (self.max_B-self.min_B))
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break
    
    def measure(self, current, zero_voltage):
        actual_voltages = []

        self.source.source_current = current
        sleep(100e-3)
        self.nvm.config_buffer(points=64)
        self.nvmxx.config_buffer(points=64)
        self.nvm.start_buffer()
        self.nvmxx.start_buffer()
        for j in range(10):
            sleep(50e-3)
            actual_voltages.append(self.source.voltage - zero_voltage)
        self.nvm.wait_for_buffer()
        actual_voltages_xy = self.nvm.buffer_data[-20:]
        actual_voltages_xx = self.nvmxx.buffer_data[-20:]
        return np.mean(actual_voltages), np.std(actual_voltages), np.mean(actual_voltages_xx), np.std(actual_voltages_xx), np.mean(actual_voltages_xy), np.std(actual_voltages_xy)
    
    def shutdown(self):
        if(self.source is not None):
            self.source.shutdown()
        if(self.gate is not None):
            self.gate.shutdown()
        if(self.triton is not None):
            self.triton.disconnect()
        log.info("Finished")

    