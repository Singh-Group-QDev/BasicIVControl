import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
import numpy as np
from pymeasure.log import console_log
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter
from pymeasure.instruments.keithley import Keithley2000, Keithley2400
from pymeasure.instruments.oxfordinstruments import Triton
from pymeasure.instruments.agilent import Agilent33220A
from pymeasure.instruments.srs import SR830

class ProcedureLockinResistivity(Procedure):

    amplitude = FloatParameter('Input Signal Amplitude (RMS)', units='V', default=0.5)
    resistance = FloatParameter('Reference Resistance', units='Mohm', default=0.967)
    frequency = FloatParameter("Reference Frequency", units='Khz', default=1)

    tempmin = FloatParameter('Minimum Temperature', units='K', default = 1)

    DATA_COLUMNS = ['Temperature (K)', 'Temperature STD (K)', 'Resistance (ohm)', 'Resistance STD (ohm)', 'Theta (degree)']

    def startup(self):
        self.triton = Triton()
        self.triton.connect(edsIP = "138.67.20.104")
        
        self.wfg = Agilent33220A("USB0::0x0957::0x5707::MY53803283::INSTR")
        self.wfg.amplitude_unit = 'VRMS' # Change from Vpp
        self.wfg.frequency = self.frequency * 1000
        self.wfg.amplitude = self.amplitude/2
        self.wfg.output = 1

        self.lockin = SR830(8)
        self.lockin.x # Test it here first, not strictly necessary
        log.debug("Setting up instruments")
        sleep(2)

    def execute(self):

        temperature = self.triton.get_temp_T8()
        while(temperature > 0.01):
            # Collect temperature over 40 seconds
            temp_temperatures = []
            temp_lockin = []
            temp_phase = []
            for i in range(5):
                temp_temperatures.append(self.triton.get_temp_T8())
                temp_lockin.append(np.sqrt(self.lockin.x**2+self.lockin.y**2))
                temp_phase.append(np.arctan2(self.lockin.y,self.lockin.x)*180/np.pi)
                sleep(60)

            temperature = np.mean(temp_temperatures)
            temperature_std = np.std(temp_temperatures)
            srsx = np.mean(temp_lockin)
            srsx_std = np.std(temp_lockin)
            phase = np.mean(temp_phase)

            log.info("Temperature: {} +/- {}K, Lockin X: {} +/- {} mV".format(temperature, temperature_std, srsx*1000, srsx_std*1000))

            data = {
                'Temperature (K)': temperature,
                'Temperature STD (K)': temperature_std, 
                'Resistance (ohm)': self.resistance*(10**6)*(srsx/self.amplitude),
                'Resistance STD (ohm)': self.resistance*(10**6)*(srsx_std/self.amplitude),
                'Theta (degree)': phase
            }
            
            self.emit('results', data)
            #self.emit('progress', 100. * i / steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        self.wfg.shutdown()
        log.info("Finished")