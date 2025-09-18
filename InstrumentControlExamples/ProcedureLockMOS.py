import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
import numpy as np
from pymeasure.log import console_log
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter
from pymeasure.instruments.keithley import Keithley2000, Keithley2400
from pymeasure.instruments.agilent import Agilent33220A
from pymeasure.instruments.srs import SR830

class ProcedureLockMOS(Procedure):

    amplitude = FloatParameter('Input Signal Amplitude (RMS)', units='V', default=0.5)
    frequency = FloatParameter("Min Frequency", units='hz', default=109)
    gateVoltageMin = FloatParameter('Gate Voltage Start', units='V', default=0)
    gateVoltageMax = FloatParameter('Gate Voltage End', units='V', default=1.5)
    gateVoltageStep = FloatParameter('Gate Voltage Step', units='V', default = 0.05)

    DATA_COLUMNS = ['Gate Voltage (V)', 'R (A)', 'Theta (degree)']

    def startup(self):
        
        # self.wfg = Agilent33220A("USB0::0x0957::0x5707::MY53803283::INSTR")
        # self.wfg.amplitude_unit = 'VRMS' # Change from Vpp
        # self.wfg.frequency = self.frequencyMin
        # self.wfg.amplitude = self.amplitude #phantom keyshight factor of 2
        # self.wfg.output = 1

        self.lockin = SR830(8)
        self.lockin.x # Test it here first, not strictly necessary
        self.lockin.frequency = self.frequency
        self.lockin.time_constant = 10/self.frequency #pymeasure will round up to the next time constant
        self.lockin.sine_voltage = self.amplitude
        self.lockin.aux_out_2 = 0
        log.debug("Set up instruments")
        sleep(1)

    def execute(self):
        voltages = np.arange(self.gateVoltageMin, self.gateVoltageMax, self.gateVoltageStep)
        steps = len(voltages)
        for i, voltage in enumerate(voltages):
            self.lockin.aux_out_1 = voltage
            temp_lockin_r = []
            temp_lockin_theta = []
            sleep(5*self.lockin.time_constant) #wait for data to stabilize
            for i in range(20):
                temp_lockin_r.append(self.lockin.magnitude)
                temp_lockin_theta.append(self.lockin.theta)
                sleep(0.01)

            srsR = np.mean(temp_lockin_r)
            srsT = np.mean(temp_lockin_theta)

            data = {
                'Gate Voltage (V)': voltage,
                'R (A)': srsR,
                'Theta (degree)': srsT
            }
            
            self.emit('results', data)
            self.emit('progress', 100. * i / steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        log.info("Finished")