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

    DATA_COLUMNS = ['Frequency (Hz)','Resistance from Lockin R (ohm)', 'Resistance STD (ohm)', 'Lock in X (V)','Lock in X STD (V)', 'Lock in Y (V)','Lock in Y STD (V)', 'Lock in Phase (degree)']

    def startup(self):
        
        self.wfg = Agilent33220A("USB0::0x0957::0x5707::MY53803283::INSTR")
        self.wfg.amplitude_unit = 'VRMS' # Change from Vpp
        self.wfg.frequency = self.frequencyMin
        self.wfg.amplitude = self.amplitude #phantom keyshight factor of 2
        self.wfg.output = 1

        self.lockin = SR830(8)
        self.lockin.x # Test it here first, not strictly necessary
        log.debug("Set up instruments")
        sleep(1)

    def execute(self):
        frequencies = np.arange(self.frequencyMin, self.frequencyMax, self.frequencyStep)
        for i, frequency in enumerate(frequencies):
            self.wfg.frequency = frequency
            new_const = 10/frequency
            if(i==0 or self.lockin.time_constant != new_const):
                log.info("changing time constant to {}".format(new_const))
            self.lockin.time_constant = 10/frequency #pymeasure will round up to the next time constant
            temp_lockin_x = []
            temp_lockin_y = []
            sleep(5*self.lockin.time_constant) #wait for data to stabilize
            for i in range(20):
                temp_lockin_x.append(self.lockin.x)
                temp_lockin_y.append(self.lockin.y)
                sleep(0.01)

            srsX = np.mean(temp_lockin_x)
            srsX_std = np.std(temp_lockin_x)
            srsY = np.mean(temp_lockin_y)
            srsY_std = np.std(temp_lockin_y)
            srsP = np.arctan2(srsY,srsX)


            data = {
                'Frequency (Hz)': frequency,
                'Resistance from Lockin R (ohm)': self.resistance*(10**6)*(srsX/self.amplitude),
                'Resistance STD (ohm)': self.resistance*(10**6)*(srsX_std/self.amplitude),
                'Lock in X (V)': srsX,
                'Lock in X STD (V)': srsX_std, 
                'Lock in Y (V)': srsY,
                'Lock in Y STD (V)': srsY_std,
                'Lock in Phase (degree)': srsP*180/np.pi
            }
            
            self.emit('results', data)
            #self.emit('progress', 100. * i / steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        self.wfg.shutdown()
        log.info("Finished")