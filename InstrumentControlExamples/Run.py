import sys
from pymeasure.display.Qt import QtWidgets
from InstrumentControlExamples.ExperimentRandom import RandomExperiment
from InstrumentControlExamples.ExperimentIV import ExperimentIV
from InstrumentControlExamples.ExperimentFourProbe import ExperimentFourProbe
from InstrumentControlExamples.ExperimentLockMOS import ExperimentLockMOS

app = QtWidgets.QApplication(sys.argv)
#window = RandomExperiment()
#window = ExperimentIV()
window = ExperimentLockMOS()
window.show()
sys.exit(app.exec())