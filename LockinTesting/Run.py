import sys
from pymeasure.display.Qt import QtWidgets
from LockinTesting.ExperimentResistanceFrequency import ExperimentResistanceFrequency
from LockinTesting.ExperimentNoiseFrequency import ExperimentNoiseFrequency

app = QtWidgets.QApplication(sys.argv)
#window = RandomExperiment()
#window = ExperimentResistanceFrequency()
window = ExperimentNoiseFrequency()
window.show()
sys.exit(app.exec())