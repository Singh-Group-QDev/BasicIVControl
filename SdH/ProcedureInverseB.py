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
from pymeasure.instruments.signalrecovery import DSP7265

class ProcedureInverse(Procedure):
    awg = None
    lockin = None
    lockin2 = None
    source = None
    gate = None
    triton = None

    DATA_COLUMNS = ['Time (s)', 'Field (T)', 'Inverse Field (1/T)', 'Lockin X (V)', 'Lockin Y (V)', 'Lockin X STD (V)', 'Lockin Y STD (V)', 'Resistance (ohm)', 'Resistance STD (ohm)', 'Temperature 5 (K)', 'Temperature 8 (K)']

    gate_voltage = FloatParameter('Gate Voltage', units = 'V', default = 6)
    voltage_offset = FloatParameter('Offset Voltage', units = 'V', default = 5)
    voltage_amplitude = FloatParameter('Amplitude', units = 'V', default = 3)
    frequency = FloatParameter('Frequency', units = 'hz', default = 9)
    delay = FloatParameter('Delay', units = 'ms', default = 200)
    voltage_range = FloatParameter('Measured Voltage Range', units = 'mV', default = .2)
    gate_compliance = FloatParameter('Gate Compliance Current', units = 'mA', default = 1)

    min_invB = FloatParameter('Minimum Magnetic Field', units = '1/T', default = 1/7.5)
    max_invB = FloatParameter('Maximum Magnetic Field', units = '1/T', default = 1/2)
    step = FloatParameter('Step', units='1/T', default=0.001)
    resistance = FloatParameter('Reference Resistor', units = 'Mohm', default = 0.967)

    def startup(self):
        self.triton = Triton()
        self.triton.connect(edsIP = "138.67.20.104")
        self.triton.set_poc_off()
        self.lockin = SR830(8)
        # self.lockin2 = DSP7265(12)
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
        Bfields = np.insert(1/np.arange(self.max_invB,self.min_invB,-self.step),0,0)
        self.gate.source_voltage = self.gate_voltage   
        self.triton.goto_bfield(0, wait = True, log = log)  
        self.lockin.set_scaling('X',0)
        for i in range(int(10*80/self.frequency)):
            sleep(100e-3)
            self.lockin.x
        #self.lockin.auto_offset('X')
        for i in range(int(10*80/self.frequency)):
            sleep(100e-3)
            self.lockin.x
        self.lockin.auto_offset('X')
        scaled = self.lockin.output_conversion('X')
        zero_time = time()
        for f, field in enumerate(Bfields):
            self.triton.goto_bfield(field, wait = True, log = log)
            for i in range(int(10*4*self.lockin.time_constant)):
                sleep(100e-3)
                self.lockin.x
            lockinx = []
            lockiny = []
            for i in range(20):
                lockinx.append(scaled(self.lockin.x))
                lockiny.append(self.lockin.y)
                # lockin2x.append(self.lockin2.x)
                # lockin2y.append(self.lockin2.y)
                sleep(60*1e-3)
            
            bfield = self.triton.get_Bfield()

            data = {
                'Time (s)': time() - zero_time,
                'Field (T)': bfield,
                'Inverse Field (1/T)': np.nan if abs(bfield) < 0.0001 else 1/bfield,
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
            self.emit('progress', 100. * (f/len(Bfields)))
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