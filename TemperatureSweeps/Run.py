import sys
from pymeasure.display.Qt import QtWidgets
from TemperatureSweeps.ExperimentLockinResistivity import ExperimentLockinResistivity
from TemperatureSweeps.ExperimentIVB import ExperimentIVB
from TemperatureSweeps.ExperimentIVBNano import ExperimentIVBNano
from TemperatureSweeps.ExperimentCooling import ExperimentCooling

app = QtWidgets.QApplication(sys.argv)
#window = RandomExperiment()
#window = ExperimentLockinResistivity()
window = ExperimentIVB()
#window = ExperimentCooling()
window.show()
sys.exit(app.exec())