import sys
from pymeasure.display.Qt import QtWidgets
from LockinTesting.ExperimentResistanceFrequency import ExperimentResistanceFrequency
from LockinTesting.ExperimentNoiseFrequency import ExperimentNoiseFrequency
from LockinTesting.ExperimentTimeDependence import ExperimentTimeDependence

app = QtWidgets.QApplication(sys.argv)
#window = RandomExperiment()
#window = ExperimentResistanceFrequency()
#window = ExperimentNoiseFrequency()
window = ExperimentTimeDependence()
window.show()
sys.exit(app.exec())