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
from pymeasure.instruments.signalrecovery import DSP7265

class ProcedureNoiseFrequency(Procedure):
    awg = None
    lockin = None
    lockin2 = None
    source = None
    gate = None
    triton = None

    DATA_COLUMNS = ['Frequency (Hz)', 'Lockin X (V)', 'Lockin Y (V)', 'Lockin X STD (V)', 'Lockin Y STD (V)', 'Temperature 5 (K)', 'Temperature 8 (K)']

    gate_voltage = FloatParameter('Gate Voltage', units = 'V', default = 6)
    voltage_offset = FloatParameter('Offset Voltage', units = 'V', default = .25)
    voltage_amplitude = FloatParameter('Amplitude', units = 'V', default = .1)
    min_frequency = FloatParameter('Min Frequency', units = 'hz', default = 7)
    max_frequency = FloatParameter('Max Frequency', units = 'hz', default = 60)
    frequency_step = FloatParameter("Step", units = 'hz', default = 1)
    delay = FloatParameter('Delay', units = 'ms', default = 200)
    voltage_range = FloatParameter('Measured Voltage Range', units = 'mV', default = .5)
    gate_compliance = FloatParameter('Gate Compliance Current', units = 'mA', default = 1)

    B = FloatParameter('Magnetic Field', units = 'T', default = 0)

    def startup(self):

    
        self.triton = Triton()
        self.triton.connect(edsIP = "138.67.20.104")
        self.triton.set_poc_off()
        self.lockin = SR830(8)
        # self.lockin2 = DSP7265(12)
        self.awg = Agilent33220A("USB0::0x0957::0x5707::MY53803283::INSTR")
        self.gate = Keithley2400(19)

        self.awg.amplitude_unit = 'VRMS' # Change from Vpp
        self.awg.amplitude = self.voltage_amplitude #phantom keyshight factor of 2
        self.awg.offset = self.voltage_offset

        self.lockin.sensitivity = self.voltage_range * 1e-3

        self.gate.apply_voltage(voltage_range = 20, compliance_current = self.gate_compliance*1e-3)
        self.gate.measure_current() # auto range

        sleep(2)
        self.gate.enable_source()

    def execute(self):
        self.triton.goto_bfield(self.B, wait = True, log = log)  
        self.gate.source_voltage = self.gate_voltage
        frequencies = np.arange(self.min_frequency, self.max_frequency, self.frequency_step)
        for frequency in frequencies:
            self.awg.frequency = frequency
            self.awg.output = 1
            self.lockin.time_constant = 10/frequency
            self.lockin.set_scaling('X',0)
            if frequency==frequencies[0]:
                sleep(10)
            for i in range(int(10*80/frequency)):
                sleep(100e-3)
                self.lockin.x
            self.lockin.auto_offset('X')
            scaled = self.lockin.output_conversion('X')
            sleep(4*self.lockin.time_constant)

            lockinx = []
            lockiny = []
            for i in range(40):
                lockinx.append(scaled(self.lockin.x))
                lockiny.append(self.lockin.y)
                # lockin2x.append(self.lockin2.x)
                # lockin2y.append(self.lockin2.y)
                sleep(160*1e-3)

            data = {
                'Frequency (Hz)': frequency,
                'Lockin X (V)': np.mean(lockinx),
                'Lockin Y (V)': np.mean(lockiny),
                'Lockin X STD (V)': np.std(lockinx),
                'Lockin Y STD (V)': np.std(lockiny),
                'Temperature 5 (K)': self.triton.get_temp_T5(),
                'Temperature 8 (K)': self.triton.get_temp_T8()
            }

            self.emit('results', data)
            self.emit('progress', 100. * (frequency-self.min_frequency) / (self.max_frequency-self.min_frequency))
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        if(self.source is not None):
            self.source.shutdown()
        if(self.gate is not None):
            self.gate.shutdown()
        if(self.triton is not None):
            self.triton.set_poc_on()
            self.triton.disconnect()
        if(self.awg is not None):
            self.awg.output = 0
        if(self.lockin2 is not None):
            self.lockin2.shutdown()
        log.info("Finished")