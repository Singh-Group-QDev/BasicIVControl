import sys
import tempfile
import random
from time import sleep, time
import numpy as np
from pymeasure.instruments.keithley import Keithley2600

source = Keithley2600(16)
source.reset()
current = 12e-5
source.write("SOUR:DELT:HIGH %f" % current)
source.write("SOUR:DELT:DELay 10e-3")
source.write("SOUR:DELT:COUN 64")
source.write("SOUR:DELT:CAB ON")
source.write("TRAC:POIN 64")
source.write("SOUR:DELT:ARM ")
source.write("INIT:IMM")
source.write("SOUR:SWE:ABOR")
source.ask("TRACe:DATA?")
