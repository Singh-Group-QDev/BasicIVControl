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

    max_current = FloatParameter('Maximum Current', units='mA', default=11)
    min_current = FloatParameter('Minimum Current', units='mA', default=-11)
    current_step = FloatParameter('Current Step', units='mA', default=0.1)
    delay = FloatParameter('Delay Time', units='ms', default=20)
    voltage_range = FloatParameter('Voltage Range', units='V', default=10)

    amplitude = FloatParameter('Input Signal Amplitude', units='V', default=1)
    resistance = FloatParameter('Reference Resistance', units='ohm', default=1000)
    frequency = FloatParameter("Reference Frequency", units='hz', default=1000)

    tempstep = FloatParameter('Tenoerature Step', units='mK', default=5)
    tempmin = FloatParameter('Minimum Temperature', units='K', default = 0.010)
    tempmax = FloatParameter('Maximum Temperature', units='K', default=2)

    runs = IntegerParameter('Averaging Cycles', default=1000)

    DATA_COLUMNS = ['Temperature (K)', 'Temperature STD (K)', 'Resistance (ohm)', 'Resistance STD (ohm)']

    def startup(self):
        triton = Triton()
        triton.set_ramp_on()
        
        self.wfg = Agilent33220A("USB0::2391::22279::MY53803283::0::INSTR")
        self.wfg.amplitude_unit = 'VRRMS' # Change from Vpp
        self.wfg.frequency = self.frequency
        self.wfg.amplitude = self.amplitude
        self.wfg.output = 1

        self.lockin = SR830(9)
        log.debug("Setting up instruments")
        self.meter = Keithley2400("GPIB::21")
        self.meter.reset()
        self.meter.measure_voltage()
        self.meter.voltage_range = self.voltage_range
        self.meter.voltage_nplc = 1  # Integration constant to Medium
        self.meter.enable_source()

        self.source = Keithley2400("GPIB::23")
        self.source.reset()
        self.source.apply_current()
        self.source.source_current_range = self.max_current * 1e-3  # A
        self.source.compliance_voltage = self.voltage_range
        self.source.enable_source()
        sleep(2)

    def execute(self):
        currents_up = np.arange(self.min_current, self.max_current, self.current_step)
        currents_down = np.arange(self.max_current, self.min_current, -self.current_step)
        currents = np.concatenate((currents_up, currents_down))  # Include the reverse
        currents *= 1e-3  # to mA from A
        steps = len(currents)

        log.info("Starting to sweep through current")
        for i, current in enumerate(currents):
            log.info("Measuring current: %g mA" % current)

            self.source.source_current = current
            
            # Or use self.source.ramp_to_current(current, delay=0.1)
            sleep(self.delay * 1e-3)
            
            voltage = self.meter.voltage
            
            if abs(current) <= 1e-10:
                resistance = np.nan
            else:
                resistance = voltage / current
            data = {
                'Current (A)': current,
                'Voltage (V)': voltage,
                'Resistance (ohm)': resistance
            }
            
            self.emit('results', data)
            self.emit('progress', 100. * i / steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        self.source.shutdown()
        self.meter.shutdown()
        log.info("Finished")