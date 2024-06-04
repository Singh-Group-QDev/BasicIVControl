import sys
from pymeasure.display.Qt import QtWidgets
from InstrumentControlExamples.ExperimentRandom import RandomExperiment
from InstrumentControlExamples.ExperimentIV import ExperimentIV
from InstrumentControlExamples.ExperimentFourProbe import ExperimentFourProbe

app = QtWidgets.QApplication(sys.argv)
#window = RandomExperiment()
#window = ExperimentIV()
window = ExperimentFourProbe()
window.show()
sys.exit(app.exec())