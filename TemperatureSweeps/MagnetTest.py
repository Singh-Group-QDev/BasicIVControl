from pymeasure.instruments.oxfordinstruments import Triton
import numpy as np
myTriton = Triton()
myTriton.connect(edsIP = "138.67.20.104")
myTriton.get_Bfield()
myTriton.get_temp_T8()