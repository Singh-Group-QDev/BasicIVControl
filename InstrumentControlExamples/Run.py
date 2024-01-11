import sys
from pymeasure.display.Qt import QtWidgets
from InstrumentControlExamples.ExperimentRandom import RandomExperiment
from InstrumentControlExamples.ExperimentIV import ExperimentIV

app = QtWidgets.QApplication(sys.argv)
#window = RandomExperiment()
window = ExperimentIV()
window.show()
sys.exit(app.exec())