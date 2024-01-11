import sys
from pymeasure.display.Qt import QtWidgets
from TransistorSweeps.ExperimentTurnOn import ExperimentTurnOn
from TransistorSweeps.ExperimentTransfer import ExperimentTransfer

app = QtWidgets.QApplication(sys.argv)
#window = ExperimentTurnOn()
window = ExperimentTransfer()
window.show()
sys.exit(app.exec())