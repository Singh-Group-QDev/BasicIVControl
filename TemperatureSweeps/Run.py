import sys
from pymeasure.display.Qt import QtWidgets
from TemperatureSweeps.ExperimentLockinResistivity import ExperimentLockinResistivity
from TemperatureSweeps.ExperimentIVB import ExperimentIVB
from TemperatureSweeps.ExperimentIVBNano import ExperimentIVBNano

app = QtWidgets.QApplication(sys.argv)
#window = RandomExperiment()
#window = ExperimentLockinResistivity()
window = ExperimentIVBNano()
window.show()
sys.exit(app.exec())