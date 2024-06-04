import sys
from pymeasure.display.Qt import QtWidgets
from InstrumentControlExamples.ExperimentRandom import RandomExperiment
from InstrumentControlExamples.ExperimentIV import ExperimentIV
from InstrumentControlExamples.Experiment4Probe import Experiment4Probe

app = QtWidgets.QApplication(sys.argv)
#window = RandomExperiment()
#window = ExperimentIV()
window = Experiment4Probe()
window.show()
sys.exit(app.exec())