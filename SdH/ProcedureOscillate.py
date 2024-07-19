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

class ProcedureOscillate(Procedure):
    # awg = None
    # lockin = None
    source = None
    gate = None
    triton = None
    nvm = None

    DATA_COLUMNS = ['Time (s)', 'Field (T)', 'Resistance (ohm)', 'Resistance STD (ohm)', 'Resistance XY (ohm)', 'Resistance XY STD (ohm)', 'Temperature 5 (K)', 'Temperature 8 (K)']

    gate_voltage = FloatParameter('Gate Voltage', units = 'V', default = 3)
    min_current = FloatParameter('Minimum Current', units = 'uA', default = 10e-3)
    max_current = FloatParameter('Maximum Current', units = 'uA', default = 30e-3)
    current_step = FloatParameter('Current Step', units = 'uA', default = 1e-3)
    hysteresis = BooleanParameter('Hysteresis', default = False)
    # offset = FloatParameter('DC Offset', units = 'V', default = 1)
    # amplitude = FloatParameter('Amplitude', units = 'V', default = 0.1)
    # frequency = FloatParameter('Frequency', units = 'hz', default = 8)
    delay = FloatParameter('Delay', units = 'ms', default = 200)
    voltage_range = FloatParameter('Measured Voltage Range', units = 'V', default = 20)
    four_wire = BooleanParameter('4 Wire', default = False)
    source_compliance = FloatParameter('Source Compliance Voltage', units = 'V', default = 5)
    gate_compliance = FloatParameter('Gate Compliance Current', units = 'mA', default = 1)

    min_B = FloatParameter('Minimum Magnetic Field', units = 'T', default = 0)
    max_B = FloatParameter('Maximum Magnetic Field', units = 'T', default = 2)
    B_sweep = FloatParameter('Magnetic Field Sweep Rate', units = 'T/min', default = 0.02)
    rxy = BooleanParameter('Rxy ?', default = True)

    def startup(self):
        if self.rxy:
            self.nvm = Keithley2182(15)
            self.nvm.reset()
            self.nvm.ch_1.setup_voltage()
            self.nvm.active_channel = 1

        self.triton = Triton()
        self.triton.connect(edsIP = "138.67.20.104")
        # self.lockin = SR830(12)
        # self.awg = Agilent33220A("USB0::0x0957::0x5707::MY53803283::INSTR")
        self.source = Keithley2400(24)
        self.gate = Keithley2400(19)
        if(self.four_wire):
            self.source.wires = 4
        else:
            self.source.wires = 2
        self.source.apply_current(compliance_voltage = self.source_compliance)
        self.source.measure_voltage(voltage = self.voltage_range)

        # self.awg.amplitude_unit = 'VRMS' # Change from Vpp
        # self.awg.frequency = self.frequency
        # self.awg.amplitude = self.amplitude #phantom keyshight factor of 2
        # self.awg.offset = self.offset
        # self.awg.output = 1

        # self.lockin.time_constant = 10/self.frequency

        self.gate.apply_voltage(voltage_range = 20, compliance_current = self.gate_compliance*1e-3)
        self.gate.measure_current() # auto range

        sleep(2)
        self.source.enable_source()
        self.gate.enable_source()

    def execute(self):

        if(self.hysteresis):
            current_up1 = np.arange(0, self.max_current*1e-6, self.current_step*1e-6)
            current_down = np.arange(self.max_current*1e-6,self.min_current*1e-6,-self.current_step*1e-6)
            current_up2 = np.arange(self.min_current*1e-6,0,self.current_step*1e-6)
            currents = np.concatenate((current_up1,current_down,current_up2))
            currents = np.append(currents,0)
        else:
            currents = np.arange(self.min_current*1e-6,self.max_current*1e-6,self.current_step*1e-6)

        self.gate.source_voltage = self.gate_voltage
        sleep(5)

        self.triton.goto_bfield(self.min_B, wait = True, log = log)
        self.triton.goto_bfield(self.max_B, sweeprate = self.B_sweep, wait = False, log = log)

        zero_time = time()
        while(not self.triton.is_idle()):
            zero_voltages = []
            zero_voltages_xy = []
            self.source.source_current = 0
            sleep(self.delay*1e-3)
            for i in range(10):
                sleep(self.delay*1e-3)
                zero_voltages.append(self.source.voltage)
                if(self.nvm is not None):
                    zero_voltages_xy.append(self.nvm.voltage)
                else:
                    zero_voltages_xy.append(0)
                

            zero_voltage = np.mean(zero_voltages)
            zero_voltage_STD = np.std(zero_voltage)
            zero_voltage_xy = np.mean(zero_voltages_xy)
            log.info('Voltage at zero current: {} +/- {}'.format(zero_voltage, zero_voltage_STD))
            log.info('XY Voltage at zero current: {}'.format(zero_voltage_xy))
            
            bfield = self.triton.get_Bfield()
            actual_voltages = []
            actual_voltages_xy = []
            actual_voltages_std = []
            for i, current in enumerate(currents):
                #voltages = []
                self.source.source_current = current
                sleep(self.delay*1e-3)
                #for j in range(10):
                #    voltages.append(self.source.voltage - zero_voltage)
                voltage = self.source.voltage - zero_voltage#np.mean(voltages)
                voltage_std = 0#np.std(voltages)
                actual_voltages.append(voltage)
                actual_voltages_std.append(voltage_std)
                actual_voltages_xy.append(self.nvm.voltage-zero_voltage_xy)

            fit, c = np.polyfit(np.asarray(currents), np.asarray(actual_voltages), 1, cov='unscaled', w=np.full(len(currents),np.sqrt(len(currents))))#, w=1/np.asarray(actual_voltages_std))
            error = np.sqrt(np.diag(c))

            fit_xy, c_xy = np.polyfit(np.asarray(currents), np.asarray(actual_voltages_xy), 1, cov='unscaled', w=np.full(len(currents),np.sqrt(len(currents))))#, w=1/np.asarray(actual_voltages_std))
            error_xy = np.sqrt(np.diag(c_xy))

            data = {
                'Time (s)': time() - zero_time,
                'Field (T)': bfield,
                'Resistance (ohm)': fit[0],
                'Resistance STD (ohm)': error[0],
                'Resistance XY (ohm)': fit_xy[0],
                'Resistance XY STD (ohm)': error_xy[0],
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
        log.info("Finished")