import pyvisa as pv
import numpy as np
import time




# HM8118
# rm = pv.ResourceManager()
# rm.list_resources()

# lcr = rm.open_resource("ASRL3::INSTR")
# lcr.read_termination = '\r'
# lcr.query("*IDN?")
# lcr.write("RNGH 0")
# lcr.write("PMOD 4")
# lcr.write("BIAS 1")
# lcr.write("AVGM 2")
# lcr.write("MMOD 1")
# lcr.write("FREQ 30")


# # The following will clear the Event Status Register (ESR), start a measurement that should take a long time, ask the ESR to
# # set bit 0 to 1 after the measurement is done, then wait for bit 0 to be 1, then query the result.
# # Apparently, the *OPC? command does not get the value of bit 0!!!! It places a 1 into the output queue so that we can wait
# # for a 1 to know that the measurements are done, but this is not ideal with pyVisa which will time us out.
# def lcr_measure(timeout = 60):
#     lcr.write("*CLS")
#     lcr.query("*ESR?")
#     lcr.write("*TRG")
#     lcr.write("*OPC")
#     zero_time = time.time()
#     while(not(int(lcr.query("*ESR?"))&1)):
#         print("Busy")
#         time.sleep(.1)
#         if(time.time()-zero_time > timeout):
#             break
#     ret = float(lcr.query("XMAJ?")) if int(lcr.query("*ESR?"))&1 else np.nan
#     lcr.write("*CLS")
#     return ret
