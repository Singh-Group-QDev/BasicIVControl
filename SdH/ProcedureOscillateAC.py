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
from pymeasure.instruments.keithley import Keithley2000, Keithley2400
from pymeasure.instruments.srs import SR830
from pymeasure.instruments.agilent import Agilent33220A
from pymeasure.instruments.oxfordinstruments import Triton

class ProcedureOscillateAC(Procedure):
    awg = None
    lockin = None
    source = None
    gate = None
    triton = None

    DATA_COLUMNS = ['Time (s)', 'Field (T)', 'Lockin X (V)', 'Lockin Y (V)', 'Resistance (ohm)', 'Resistance STD (ohm)', 'Temperature 5 (K)', 'Temperature 8 (K)']

    gate_voltage = FloatParameter('Gate Voltage', units = 'V', default = 6)
    voltage_offset = FloatParameter('Offset Voltage', units = 'V', default = 8)
    voltage_amplitude = FloatParameter('Amplitude', units = 'V', default = 1.414)
    frequency = FloatParameter('Frequency', units = 'hz', default = 20)
    delay = FloatParameter('Delay', units = 'ms', default = 200)
    voltage_range = FloatParameter('Measured Voltage Range', units = 'mV', default = 100)
    gate_compliance = FloatParameter('Gate Compliance Current', units = 'mA', default = 1)

    min_B = FloatParameter('Minimum Magnetic Field', units = 'T', default = 1)
    max_B = FloatParameter('Maximum Magnetic Field', units = 'T', default = 8)
    B_sweep = FloatParameter('Magnetic Field Sweep Rate', units = 'T/min', default = 0.1)
    resistance = FloatParameter('Reference Resistor', units = 'Mohm', default = 0.967)

    def startup(self):
        self.triton = Triton()
        self.triton.connect(edsIP = "138.67.20.104")
        self.lockin = SR830(8)
        self.awg = Agilent33220A("USB0::0x0957::0x5707::MY53803283::INSTR")
        self.gate = Keithley2400(19)

        self.awg.amplitude_unit = 'VRMS' # Change from Vpp
        self.awg.frequency = self.frequency
        self.awg.amplitude = self.voltage_amplitude #phantom keyshight factor of 2
        self.awg.offset = self.voltage_offset
        self.awg.output = 1
        self.lockin.time_constant = 10/self.frequency
        self.lockin.sensitivity = self.voltage_range * 1e-3

        self.gate.apply_voltage(voltage_range = 20, compliance_current = self.gate_compliance*1e-3)
        self.gate.measure_current() # auto range

        sleep(2)
        self.gate.enable_source()

    def execute(self):
        self.gate.source_voltage = self.gate_voltage
        sleep(160/self.frequency)
        self.triton.goto_bfield(self.min_B, wait = True, log = log)
        self.triton.goto_bfield(self.max_B, sweeprate = self.B_sweep, wait = False, log = log)
        zero_time = time()

        while(not self.triton.is_idle()):
            sleep(self.delay*1e-3)
            lockinx = []
            lockiny = []
            for i in range(10):
                lockinx.append(self.lockin.x)
                lockiny.append(self.lockin.y)
                sleep(40*1e-3)
            
            bfield = self.triton.get_Bfield()

            data = {
                'Time (s)': time() - zero_time,
                'Field (T)': bfield,
                'Lockin X (V)': np.mean(lockinx),
                'Lockin Y (V)': np.mean(lockiny),
                'Lockin X STD (V)': np.std(lockinx),
                'Lockin Y STD (V)': np.std(lockiny),
                'Resistance (ohm)': self.resistance*1e6*(np.mean(lockinx)/self.voltage_amplitude),
                'Resistance STD (ohm)': self.resistance*1e6*(np.std(lockinx)/self.voltage_amplitude),
                'Temperature 5 (K)': self.triton.get_temp_T5(),
                'Temperature 8 (K)': self.triton.get_temp_T8()
            }

            self.emit('results', data)
            self.emit('progress', 100. * (bfield-self.min_B) / (self.max_B-self.min_B))
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

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