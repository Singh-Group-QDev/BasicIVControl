import sys
from pymeasure.display.Qt import QtWidgets
from TransistorSweeps.ExperimentTransfer import ExperimentTransfer
from TransistorSweeps.ExperimentOutput import ExperimentOutput

app = QtWidgets.QApplication(sys.argv)
window = ExperimentTransfer()
#window = ExperimentOutput()
window.show()
sys.exit(app.exec())