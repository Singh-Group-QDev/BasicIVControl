import sys
from pymeasure.display.Qt import QtWidgets
from CISS.ExperimentCoolingDown import ExperimentCoolingDown

app = QtWidgets.QApplication(sys.argv)
window = ExperimentCoolingDown()
window.show()
sys.exit(app.exec())