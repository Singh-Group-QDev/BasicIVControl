import sys
from pymeasure.display.Qt import QtWidgets
from LockinTesting.ExperimentResistanceFrequency import ExperimentResistanceFrequency

app = QtWidgets.QApplication(sys.argv)
#window = RandomExperiment()
window = ExperimentResistanceFrequency()
window.show()
sys.exit(app.exec())