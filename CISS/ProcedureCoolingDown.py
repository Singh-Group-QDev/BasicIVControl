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
from pymeasure.instruments.oxfordinstruments import Triton

class ProcedureCoolingDown(Procedure):
    source = None
    triton = None
    nvm1 = None
    nvm2 = None

    DATA_COLUMNS = ['Time (s)', 'Temperature 5 (K)', 'Temperature 8 (K)', 'Current (A)', 'Voltage L (V)', 'Voltage L STD (V)', 'Voltage T (V)', 'Voltage T STD (V)', 'Voltage 2Pt (V)']

    min_current = FloatParameter('Min Current', units = 'uA', default = -150)
    max_current = FloatParameter('Max Current', units = 'uA', default = 150)
    current_step = FloatParameter('Current Step', units = 'uA', default = 10)
    delay = FloatParameter('Delay', units = 's', default = 2)
    source_compliance = FloatParameter('Source Compliance Voltage', units = 'V', default = 5)
    voltage_range = FloatParameter('2Pt Voltage Range', units = 'V', default = 2)
    hysteresis = BooleanParameter('Hysteresis?', default = True)
    from_zero = BooleanParameter('Hysteresis from Zero?', default = True)
    target_temp = FloatParameter('Temperature', units = 'K', default = 298)

    def startup(self):
        self.nvm1 = Keithley2182(15)
        self.nvm1.reset()
        self.nvm1.ch_1.setup_voltage()
        self.nvm1.active_channel = 1
        self.nvm1.sample_continuously()

        self.nvm2 = Keithley2182(7)
        self.nvm2.reset()
        self.nvm2.ch_1.setup_voltage()
        self.nvm2.active_channel = 1
        self.nvm2.sample_continuously()

        self.triton = Triton()
        self.triton.connect(edsIP = "138.67.20.104")

        self.source = Keithley2400(19)
        self.source.apply_current(compliance_voltage = self.source_compliance)
        self.source.measure_voltage(voltage = self.voltage_range)

        sleep(2)
        self.source.enable_source()

    def execute(self):
        if(not self.hysteresis):
           log.info('Preparing B field values, no hysteresis')
           currents = np.arange(self.min_current, self.max_current, self.current_step)
        elif(self.hysteresis and self.from_zero):
            log.info('Preparing B field values, hysteresis from zero')
            B_up1 = np.arange(0, self.max_current, self.current_step)
            B_down = np.arange(self.max_current,self.min_current,-self.current_step)
            B_up2 = np.arange(self.min_current,0,self.current_step)
            currents = np.concatenate((B_up1,B_down,B_up2))
        else:
            log.info('Preparing B field values, hysteresis from min')
            B_up1 = np.arange(self.min_current, self.max_current, self.current_step)
            B_down = np.arange(self.max_current,self.min_current,-self.current_step)
            currents = np.concatenate((B_up1,B_down))
        self.source.source_current = 0
        self.nvm1.ch_1.acquire_voltage_reference()
        self.nvm1.ch_1.voltage_offset_enabled = True
        self.nvm2.ch_1.acquire_voltage_reference()
        self.nvm2.ch_1.voltage_offset_enabled = True
        currents *= 1e-6
        zero_time = time()
        while(self.triton.get_temp_T5() > self.target_temp):
            sleep(60)
        for i, current in enumerate(currents):
            vxx, vxx_std, v_h_p, v_h_p_std = self.measure(current,16)
            log.info("vhp:{}".format(v_h_p))
            data = {
                'Time (s)': time() - zero_time,
                'Temperature 5 (K)': self.triton.get_temp_T5(),
                'Temperature 8 (K)': self.triton.get_temp_T8(),
                'Current (A)': current,
                'Voltage L (V)': vxx,
                'Voltage L STD (V)': vxx_std,
                'Voltage T (V)': v_h_p,
                'Voltage T STD (V)': v_h_p_std,
                'Voltage 2Pt (V)': self.source.voltage
            }

            self.emit('results', data)
            self.emit('progress', 100. * (i/len(currents)))
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break
    
    def measure(self, current, points):
        self.source.source_current = current
        sleep(self.delay)
        self.nvm1.config_buffer(points=points)
        self.nvm1.start_buffer()
        self.nvm2.config_buffer(points=points)
        self.nvm2.start_buffer()
        self.nvm2.wait_for_buffer(timeout = 2*points/3)
        actual_voltages_xx = self.nvm1.buffer_data
        actual_voltages_xy = self.nvm2.buffer_data
        return  np.mean(actual_voltages_xx), np.std(actual_voltages_xx), np.mean(actual_voltages_xy), np.std(actual_voltages_xy)
    
    def shutdown(self):
        if(self.source is not None):
            self.source.shutdown()
        if(self.triton is not None):
            self.triton.disconnect()
        log.info("Finished")

    