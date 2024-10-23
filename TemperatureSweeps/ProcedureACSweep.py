import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
import numpy as np
from pymeasure.log import console_log
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter
from pymeasure.instruments.keithley import Keithley2000, Keithley2400, Keithley2182
from pymeasure.instruments.oxfordinstruments import Triton
from pymeasure.instruments.agilent import Agilent33220A
from pymeasure.instruments.srs import SR830

class ProcedureACSweep(Procedure):

    amplitude = FloatParameter('Input Signal Amplitude (RMS)', units='V', default=0.25)
    resistance = FloatParameter('Reference Resistance', units='Mohm', default=0.967)
    frequency = FloatParameter("Reference Frequency", units='hz', default=17)
    sensitivity = FloatParameter("Lock in Sensitivity", units='mV', default=2)
    set_temp = FloatParameter('Set Temperature', units='K', default=1)
    ramp_rate = FloatParameter('Ramp Rate', units='mK/min', default = 5)
    heater_range = FloatParameter('Heater Range', units='mW', default = 10)

    DATA_COLUMNS = ['SRSX (V)', 'SRSX STD (V)', 'SRSY (V)', 'SRSY STD (V)', 'Preliminary Resistance (ohm)', 'Temperature (K)', 'Temperature Cernox (K)']

    def startup(self):
        # self.nvm = Keithley2182(15)
        # self.nvm.reset()
        # self.nvm.ch_1.setup_voltage()
        # self.nvm.active_channel = 1
        # self.nvm.sample_continuously()
        self.triton = Triton()
        self.triton.connect(edsIP = "138.67.20.104")
        
        self.wfg = Agilent33220A("USB0::0x0957::0x5707::MY53803283::INSTR")
        self.wfg.amplitude_unit = 'VRMS' # Change from Vpp
        self.wfg.frequency = self.frequency
        self.wfg.amplitude = self.amplitude
        self.wfg.output = 1

        self.lockin = SR830(8)
        self.lockin.time_constant = 10/self.frequency #make sure 2f harmonic is attenuated
        self.lockin.sensitivity = self.sensitivity*1e-3

        log.debug("Setting up instruments")
        sleep(2)

    def execute(self):
        self.lockin.set_scaling('X',0)
        # for i in range(int(10*80/self.frequency)):
        #         sleep(100e-3)
        #         self.lockin.x
        # self.lockin.auto_offset('X')
        scaled = self.lockin.output_conversion('X')
        temperature = self.triton.get_temp_T8()
        self.triton.goto_temp(self.set_temp,self.ramp_rate*1e-3,self.heater_range)
        while(not self.triton.isWithin(temperature, self.set_temp, .001)):
            # Collect temperature over 40 seconds
            temp_lockinX = []
            temp_lockinY = []
            for i in range(50):
                temp_lockinX.append(scaled(self.lockin.x))
                temp_lockinY.append(self.lockin.y)
                #temp_phase.append(np.arctan2(self.lockin.y,self.lockin.x)*180/np.pi)
                sleep(160*1e-3)

            temperature = self.triton.get_temp_T8()
            temperatureC = self.triton.get_temp_T5()
            srsx = np.mean(temp_lockinX)
            srsx_std = np.std(temp_lockinX)
            srsy = np.mean(temp_lockinY)
            srsy_std = np.std(temp_lockinY)
            log.info("Temperature: {}K (cernox: {} K), Lockin X: {} +/- {} mV".format(temperature, temperatureC, srsx*1000, srsx_std*1000))

            data = {
                'SRSX (V)': srsx,
                'SRSX STD (V)': srsx_std,
                'SRSY (V)': srsy,
                'SRSY STD (V)': srsy_std,
                'Preliminary Resistance (ohm)': self.resistance*(10**6)*(srsx/self.amplitude),
                'Temperature (K)': temperature,
                'Temperature Cernox (K)': temperatureC
            }
            
            self.emit('results', data)
            #self.emit('progress', 100. * i / steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break
            sleep(90)

    def measure(self):
        sleep(100e-3)
        self.nvm.config_buffer(points=128)
        self.nvm.start_buffer()
        self.nvm.wait_for_buffer()
        actual_voltages_xx = self.nvm.buffer_data
        return np.mean(actual_voltages_xx), np.std(actual_voltages_xx)

    def shutdown(self):
        self.wfg.shutdown()
        self.triton.goto_base()
        self.triton.disconnect()
        log.info("Finished")