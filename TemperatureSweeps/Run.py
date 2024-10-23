import sys
from pymeasure.display.Qt import QtWidgets
from TemperatureSweeps.ExperimentLockinResistivity import ExperimentLockinResistivity
from TemperatureSweeps.ExperimentIVB import ExperimentIVB
from TemperatureSweeps.ExperimentIVBNano import ExperimentIVBNano
from TemperatureSweeps.ExperimentCooling import ExperimentCooling
from TemperatureSweeps.ExperimentCoolingDC import ExperimentCoolingDC
from TemperatureSweeps.ExperimentDCWhile import ExperimentDCWhile
from TemperatureSweeps.ExperimentACSweep import ExperimentACSweep

app = QtWidgets.QApplication(sys.argv)
#window = RandomExperiment()
#window = ExperimentLockinResistivity()
#window = ExperimentIVB()
#window = ExperimentCoolingDC()
window = ExperimentCooling()
#window = ExperimentDCWhile()
#window = ExperimentACSweep()

window.show()
sys.exit(app.exec())