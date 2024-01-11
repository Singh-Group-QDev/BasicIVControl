import sys
from pymeasure.display.Qt import QtWidgets
from InstrumentControlExamples.ExperimentRandom import RandomExperiment

app = QtWidgets.QApplication(sys.argv)
window = RandomExperiment()
#window = IVExperiment()
window.show()
sys.exit(app.exec())

from pymeasure.adapters import VXI11Adapter
from pymeasure.instruments import Instrument
string = "TCPIP::169.254.192.76::inst0::INSTR"
adapter = VXI11Adapter(host = string)
laskeShore = Instrument(adapter, "my_instr")