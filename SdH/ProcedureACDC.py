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
from pymeasure.instruments.srs import SR830
from pymeasure.instruments.agilent import Agilent33220A

class ProcedureACDC(Procedure):
    # awg = None
    # lockin = None
    source = None
    lockin = None
    awg = None
    gate = None
    triton = None
    nvm = None

    DATA_COLUMNS = ['Time (s)', 'Field (T)', 'Lockin X (V)', 'Lockin Y (V)', 'Lockin X STD (V)', 'Lockin Y STD (V)', 'Resistance XX (ohm)', 'Resistance XX STD (ohm)', 'Positive Hall Voltage (V)', 'Negative Hall Voltage (V)', 'Positive Hall Voltage STD (V)', 'Negative Hall Voltage STD (V)','Resistance XY (ohm)', 'Resistance XY STD (ohm)', 'Temperature 5 (K)', 'Temperature 8 (K)']

    gate_voltage = FloatParameter('Gate Voltage', units = 'V', default = 6)
    current = FloatParameter('Current', units = 'uA', default = 30)

    delay = FloatParameter('Delay', units = 's', default = 5)
    voltage_range = FloatParameter('Measured Voltage Range', units = 'V', default = 20)
    source_compliance = FloatParameter('Source Compliance Voltage', units = 'V', default = 5)
    gate_compliance = FloatParameter('Gate Compliance Current', units = 'mA', default = 1)
    Rxx = BooleanParameter('Rxx?', default = True)
    voltage_offset = FloatParameter('Offset Voltage', units = 'V', default = 5)
    voltage_amplitude = FloatParameter('Amplitude', units = 'V', default = 2.5)
    frequency = FloatParameter('AWG frequency', units = 'hz', default = 5)
    voltage_lockin = FloatParameter('Lockin Voltage Range', units = 'mV', default = 100)

    min_B = FloatParameter('Minimum Magnetic Field', units = 'T', default = 0)
    max_B = FloatParameter('Maximum Magnetic Field', units = 'T', default = 7.5)
    hysteresis = BooleanParameter('Hysteresis?', default = False)
    from_zero = BooleanParameter('Hysteresis from Zero?', default = False)
    B_step = FloatParameter('Magnetic Field Step', units = 'T', default = 0.025)
    B_sweep = BooleanParameter('Enforce sweep rate?', default = False)
    sweep_rate = FloatParameter('Sweep Rate', units = 'T/min', default = 0.01)

    resistance = FloatParameter('Reference Resistor', units = 'Mohm', default = 0.967)

    def startup(self):
        self.nvm = Keithley2182(15)
        self.nvm.reset()
        self.nvm.ch_1.setup_voltage()
        self.nvm.active_channel = 1
        self.nvm.sample_continuously()

        self.awg = Agilent33220A("USB0::0x0957::0x5707::MY53803283::INSTR")
        self.awg.amplitude_unit = 'VRMS' # Change from Vpp
        self.awg.frequency = self.frequency
        self.awg.amplitude = self.voltage_amplitude #phantom keyshight factor of 2
        self.awg.offset = self.voltage_offset
        
        self.lockin = SR830(8)
        self.lockin.time_constant = 10/self.frequency
        self.lockin.sensitivity = self.voltage_lockin * 1e-3

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
        self.awg.output = 0
        self.source.enable_source()
        self.gate.enable_source()

    def execute(self):
        if(not self.hysteresis):
           log.info('Preparing B field values, no hysteresis')
           Bfields = np.arange(self.min_B, self.max_B, self.B_step)
        elif(self.hysteresis and self.from_zero):
            log.info('Preparing B field values, hysteresis from zero')
            B_up1 = np.arange(0, self.max_B, self.B_step)
            B_down = np.arange(self.max_B,self.min_B,-self.B_step)
            B_up2 = np.arange(self.min_B,0,self.B_step)
            Bfields = np.concatenate((B_up1,B_down,B_up2))
        else:
            log.info('Preparing B field values, hysteresis from min')
            B_up1 = np.arange(self.min_B, self.max_B, self.B_step)
            B_down = np.arange(self.max_B,self.min_B,-self.B_step)
            Bfields = np.concatenate((B_up1,B_down))
        
        self.gate.source_voltage = self.gate_voltage
        self.triton.goto_bfield(Bfields[0], wait = True, log = log)
        zero_time = time()

        for B in Bfields:
            self.triton.goto_bfield(B, sweeprate = (self.sweep_rate if self.B_sweep else None), wait = True, log = log)
            bfield = self.triton.get_Bfield()

            v_h_p, v_h_p_std = self.measure(self.current*1e-6)
            v_h_n, v_h_n_std = self.measure(-self.current*1e-6)
            self.source.source_current = 0
            if(self.Rxx):
                self.awg.output = 1
                for i in range(int(10*160/self.frequency)):
                    sleep(100e-3)
                    self.lockin.x
                lockinx = []
                lockiny = []
                for i in range(16):
                    sleep(100e-3)
                    lockinx.append(self.lockin.x)
                    lockiny.append(self.lockin.y)
                lockX = np.mean(lockinx)
                lockY = np.mean(lockiny)

                self.awg.output = 0
            else:
                lockX = np.nan
                lockY = np.nan


            log.info("vhp:{}, vhn:{}".format(v_h_p, v_h_n))

            data = {
                'Time (s)': time() - zero_time,
                'Field (T)': bfield,
                'Lockin X (V)': lockX,
                'Lockin Y (V)': lockY,
                'Lockin X STD (V)': np.std(lockinx) if self.Rxx else np.nan,
                'Lockin Y STD (V)': np.std(lockiny) if self.Rxx else np.nan,
                'Resistance XX (ohm)': (self.resistance*1e6*lockX)/(self.voltage_amplitude) if self.Rxx else np.nan,
                'Resistance XX STD (ohm)': (self.resistance*1e6*np.std(lockinx))/(self.voltage_amplitude) if self.Rxx else np.nan,
                'Positive Hall Voltage (V)': v_h_p,
                'Negative Hall Voltage (V)': v_h_n,
                'Positive Hall Voltage STD (V)': v_h_p_std,
                'Negative Hall Voltage STD (V)': v_h_n_std,
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
    
    def measure(self, current):
        self.source.source_current = current
        sleep(100e-3)
        self.nvm.config_buffer(points=64)
        self.nvm.start_buffer()
        self.nvm.wait_for_buffer()
        actual_voltages_xy = self.nvm.buffer_data[-20:]

        return  np.mean(actual_voltages_xy), np.std(actual_voltages_xy)
    
    def shutdown(self):
        if(self.source is not None):
            self.source.shutdown()
        if(self.gate is not None):
            self.gate.shutdown()
        if(self.triton is not None):
            self.triton.disconnect()
        if(self.awg is not None):
            self.awg.output = 0
        log.info("Finished")

    