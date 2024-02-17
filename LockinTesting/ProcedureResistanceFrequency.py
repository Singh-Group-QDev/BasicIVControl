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

class ProcedureResistanceFrequency(Procedure):

    amplitude = FloatParameter('Input Signal Amplitude (RMS)', units='V', default=0.5)
    resistance = FloatParameter('Reference Resistance', units='Mohm', default=0.967)
    frequencyMin = FloatParameter("Min Frequency", units='hz', default=1)
    frequencyMax = FloatParameter('Max Frequency', units='hz', default=1000)
    frequencyStep = FloatParameter('Frequency Step', units='hz', default=10)

    DATA_COLUMNS = ['Resistance from Lockin R (ohm)', 'Resistance STD (ohm)', 'Frequency (Hz)', 'Phase (degree)', 'Phase STD (degree)']

    def startup(self):
        
        self.wfg = Agilent33220A("USB0::0x0957::0x5707::MY53803283::INSTR")
        self.wfg.amplitude_unit = 'VRMS' # Change from Vpp
        self.wfg.frequency = self.frequencyMin
        self.wfg.amplitude = self.amplitude / 2 #phantom keyshight factor of 2
        self.wfg.output = 1

        self.lockin = SR830(8)
        self.lockin.x # Test it here first, not strictly necessary
        log.debug("Set up instruments")
        sleep(1)

    def execute(self):
        frequencies = np.arange(self.frequencyMin, self.frequencyMax, self.frequencyStep)
        for i, frequency in enumerate(frequencies):
            self.wfg.frequency = frequency
            temp_lockin = []
            temp_lockin_phase = []
            for i in range(20):
                temp_lockin.append(np.sqrt(self.lockin.x**2+self.lockin.y**2))
                temp_lockin_phase.append(np.arctan2(self.lockin.y, self.lockin.x)*180/np.pi)
                sleep(0.01)

            srsR = np.mean(temp_lockin)
            srsP = np.mean(temp_lockin_phase)
            srsR_std = np.std(temp_lockin)
            srsP_std = np.std(temp_lockin_phase)

            data = {
                'Resistance from Lockin R (ohm)': self.resistance*(10**6)*(srsR/self.amplitude),
                'Resistance STD (ohm)': self.resistance*(10**6)*(srsR_std/self.amplitude),
                'Frequency (Hz)': frequency,
                'Phase (degree)': srsP,
                'Phase STD (degree)': srsP_std

            }
            
            self.emit('results', data)
            #self.emit('progress', 100. * i / steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        self.wfg.shutdown()
        log.info("Finished")