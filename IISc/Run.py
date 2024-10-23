import sys
from pymeasure.display.Qt import QtWidgets
from IISc.ExperimentTempSensitive import ExperimentTempSensitive

app = QtWidgets.QApplication(sys.argv)
window = ExperimentTempSensitive()
window.show()
sys.exit(app.exec())

